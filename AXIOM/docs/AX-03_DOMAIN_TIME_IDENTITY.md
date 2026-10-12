# AX-03 — Domain Model, Time, Identity and Numeric Law

**Status:** Normative.
**Upstream:** AX-01 (§5 law, §9 glossary), AX-02 (venue semantics).
**Downstream:** AX-04 (storage), AX-05, AX-06, AX-07, AX-08, AX-11, AX-13 (interfaces), `contracts/sql`,
`contracts/schemas`.

This document fixes the **objects**, their **identities**, the **time model**, the **numeric and
rounding law**, and the **serialisation/hashing law**. Every later document refers to these names; no
document may invent a parallel vocabulary.

---

## 1. Object catalogue (`AX-03:§1`)

Each object below is specified by: purpose → identity → fields → source → immutability/retention.
Field types use `dec` for decimal-string-preserved values, `f64` for computed floating-point values,
`i64` for integers, `ts` for UTC epoch milliseconds, `enum` for closed value sets. "Immutable" means
insert-only (no update, no delete before retention expiry); "derived" means rebuildable from
immutables and therefore not part of the truth of record.

### 1.1 Reference objects

**`InstrumentSpec`** — the venue's contract description, snapshotted.
Identity: `(instrument_id, observed_ts)`. Immutable.
Fields: `instrument_id` (venue symbol, e.g. `BTC-SWAP-USDT`), `status` enum, `base_asset`,
`quote_asset`, `margin_token`, `inverse` bool, `contract_multiplier` dec, `price_precision` dec,
`qty_precision` dec, `index_symbol` (e.g. `BTCUSDT`), `categories[]`, `filters[]` (raw JSON),
`risk_tiers[]` (raw JSON), `raw_hash`, `schema_version`.
Rule: **`instrument_id` is the venue symbol string, and it is the only identifier used anywhere in
AXIOM** (models, tables, logs, notifications). No internal aliases, no normalisation, no display
re-mapping. The index symbol of the underlying spot pair is a *separate field*, never an alias
(`AX-03:§1.1-R1`, test `T-ID-001`).

**`VenueProfile`** — the frozen output of the conformance harness (AX-02 §10), versioned and hashed.
Identity: `(profile_version, content_hash)`. Immutable.

**`ParamSet`** — the complete configuration for a run.
Identity: `param_set_version` (monotonic integer) and `param_set_hash` (see §6).
Fields: every registry entry from AX-15 with its value, unit, provenance class, and source reference.
Rule: a run may only load a `ParamSet` whose entries all carry a provenance class (INV-6) and whose
`[C]` entries reference calibration artifacts that are within their validity window
(`AX-03:§1.1-R2`, test `T-PROV-001`).

**`ModelArtifact`** — a frozen model/calibration object produced by the learning plane.
Identity: `(model_id, version, artifact_hash)`. Fields: `kind` enum (`FORECASTER`, `CALIBRATOR`,
`RISK_MODEL`, `UNIVERSE_RULE`, `COST_MODEL`), `training_window` `[start,end]`, `feature_versions[]`,
`code_commit`, `artifact_hash`, `promotion_state` enum (`RESEARCH`, `SHADOW`, `PAPER`, `MICRO_LIVE`,
`LIVE`, `RETIRED`), `evidence_ref` (experiment ids), `created_ts`.
Rule: runtime planes load artifacts **by hash**, never by name or by "latest"
(`AX-03:§1.1-R3`).

### 1.2 Market data objects (L0/L1)

| Object | Identity | Key fields | Source | Notes |
|---|---|---|---|---|
| `Bar` | `(instrument_id, interval, open_time)` + `revision` | `open_time`, `close_time`, `o,h,l,c` dec, `volume_base` dec, `quote_volume` dec, `trade_count` i64, `taker_buy_base` dec, `taker_buy_quote` dec, `is_final` bool, `source` enum (`WS`, `REST`), `revision` i32, `first_ingest_ts`, `last_update_ts`, `quality_flags` | WS kline, REST klines | both sources recorded; `is_final` set only by the close-detection procedure (§4.3) |
| `Trade` | `(instrument_id, venue_trade_id)` when `venue_trade_id` integrity is verified; otherwise `(instrument_id, ingest_seq)` | `event_ts`, `price` dec, `qty` dec, `taker_is_buy` bool nullable, `venue_trade_id` (the `v` field) nullable, `ingest_ts`, `ingest_seq` | WS `trade` | `taker_is_buy` stays `NULL` while `AMB-02` is unresolved (AX-02 §11) |
| `Quote` | `(instrument_id, ingest_seq)` | `bid`,`bid_qty`,`ask`,`ask_qty` dec, `event_ts`, `tx_ts`, `ingest_ts` | WS `bookTicker` | top-of-book only; the cheapest source of spread |
| `BookSnapshot` | `(instrument_id, snapshot_seq)` | `bids[]`,`asks[]` (each `[price,qty]`), `level_count`, `venue_version` text, `event_ts`, `ingest_ts` | WS `depth` / REST `depth` | used to (re)initialise book state; the venue version is diagnostic only (AX-02 §4) |
| `BookDelta` | `(instrument_id, ingest_seq)` | `bids[]`,`asks[]`, `venue_version`, `event_ts` | WS `diffDepth` | `qty=0` deletes a level |
| `MarkPriceObs` | `(instrument_id, event_ts, ingest_seq)` | `price` dec | WS `markPrice`, REST `markPrice` | liquidation-distance and trigger reference |
| `IndexPriceObs` | `(index_symbol, event_ts, ingest_seq)` | `index` dec, `edp` dec (10-min average), `formula_ref` | WS `index`, REST `index` | venue composite across disclosed exchanges (AX-02 §3.1) |
| `FundingRateObs` | `(instrument_id, ingest_ts)` | `rate` dec, `period` text (`8H`), `next_funding_time`, `interest`, `cap`, `floor` | REST `fundingRate` | polled; see collection cadence in AX-04 §2 |
| `FundingSettlement` | `(instrument_id, settle_time)` | `settle_rate` dec, `period` text | REST `historyFundingRate` | the only correct basis for carry accounting |
| `OpenInterestObs` | `(instrument_id, ingest_ts)` | `size_base` dec, `unit` text | REST `openInterest` | history is ours (AX-02 §5.2) |
| `LongShortRatioObs` | `(instrument_id, bucket_start, period)` | `long_short_ratio`, `long_account`, `short_account` | REST | T3 input |
| `RiskTierObs` | `(instrument_id, observed_ts, level)` | `quantity`, `maintain_margin`, `initial_margin`, `max_leverage` | REST `riskLimits` | drives leverage caps and liquidation distance |
| `InsuranceFundObs` | `(instrument_id, update_time)` | `value` dec | REST | context only |

### 1.3 Account and trading objects (truth of intent vs truth of reality)

**`OrderIntent`** (ours, immutable once written) — the write-ahead record required by INV-3.
Identity: `intent_id` (ULID-like, §3.1). Fields: `created_ts`, `purpose` enum
(`ENTRY`, `PROTECT`, `EXIT`, `FLATTEN`, `CANCEL`, `MODIFY`, `LEVERAGE`, `MARGIN_TYPE`),
`instrument_id`, `side_semantic` enum (`OPEN_LONG`, `OPEN_SHORT`, `CLOSE_LONG`, `CLOSE_SHORT`),
`qty` dec nullable, `value_qty` dec nullable, `limit_price` dec nullable, `trigger_price` dec nullable,
`trigger_by` enum nullable, `price_type` enum, `tif` enum, `idempotency_key` text (unique),
`decision_id` nullable, `snapshot_id` nullable, `risk_R` f64 nullable,
`price_budget` dec nullable (worst acceptable price), `expires_ts` nullable, `state` enum
(`WRITTEN`, `SENT`, `ACKED`, `PARTIAL`, `FILLED`, `REJECTED`, `UNKNOWN`, `RESOLVED_*`, `ABANDONED`),
`resolution_ref` text nullable.
Rules: written **before** transmission; never modified except for `state` transitions and
`resolution_ref`, each of which is itself journaled as an event (`AX-03:§1.3-R1`).

**`VenueOrder`** (observed reality) — Identity `(order_id, observed_ts)`; snapshot-style rows carrying
the raw venue payload plus `client_order_id`, `status`, `orig_qty`, `executed_qty`, `avg_price`,
`price`, `type`, `side`, `update_ts`, `raw_hash`. Immutable snapshots; the "current" view is derived.

**`Fill`** — Identity `fill_id` (venue-provided when available; otherwise
`hash(order_id, price, qty, event_ts, seq)`); fields: `order_id`, `client_order_id`, `instrument_id`,
`qty`, `price`, `fee`, `fee_asset`, `is_maker` nullable, `event_ts`, `ingest_ts`.
Immutable; `fill_id` is the deduplication key (INV-3).

**`Position`** (venue truth, snapshot) — Identity `(instrument_id, observed_ts)`; fields: `side`,
`qty`, `entry_price`, `mark_price`, `unrealized_pnl`, `margin`, `liquidation_price`, `leverage`,
`raw_hash`. The system's *own* position view is derived by replaying the journal and is compared to
this object; disagreement is an incident, never an average (`AX-03:§1.3-R2`, INV-2).

**`AccountState`** — Identity `(observed_ts)`; fields: equity, available margin, used margin,
open-order margin reservation (`marginLocked` of working orders, per AX-02 §6.3), unrealized PnL,
day PnL, commission rate (with `observed_ts`).

### 1.4 Decision objects

| Object | Identity | Content | Rule |
|---|---|---|---|
| `Snapshot` | `snapshot_id` (content hash) | `as_of` ts, instrument set, per-partition digests of L1 content visible, `param_set_hash`, `code_commit`, `model_hashes[]`, `profile_hash` | one decision references exactly one snapshot; a snapshot is immutable and reproducible |
| `FeatureVector` | `(feature_set_version, instrument_id, as_of)` | values + `inputs_hash` | computed only through the tape cursor (§5.1) |
| `Forecast` | `(forecast_id)` = hash(model_id, version, instrument, horizon, as_of) | `mu_net` f64 (expected net return), `sigma` f64, `p_net_positive` f64, `horizon`, `model_id`, `features_hash` | calibrated distribution objects, not point signals |
| `Target` | `target_id` | `instrument_id`, `target_qty` dec, `target_notional` dec, `stop_price` dec nullable, `risk_R` f64, `binding_constraints[]`, `reason_code` enum, `forecast_refs[]` | the only object the execution plane treats as an order of business |
| `OrderPlan` | `plan_id` | `target_id`, ordered `steps[]` (each with its `OrderIntent` template and a trigger condition), budgets | produced by the execution planner (AX-08 §4) |
| `Decision` | `decision_id` | `snapshot_id`, `targets[]`, `refusals[]` (with reason codes), `governor_state` at decision time, `mode` | the journaled output of the kernel (INV-5) |
| `Refusal` | part of `Decision` | `instrument_id`, `stage` enum, `reason_code` enum, `detail` | refusals are first-class evidence (AX-09 §6.3): "no trade" must be as observable as a trade |

### 1.5 Operational objects

**`JournalEvent`** — Identity `seq` i64 monotonic; fields: `ts`, `type`, `payload`, `prev_hash`,
`hash` (§6.3). **The journal is the spine of INV-2/INV-11**: intents, venue responses, state
transitions, decisions, refusals, governor transitions, incidents, parameter changes, operator actions.

**`Incident`** — Identity `incident_id`; fields: `severity` (`SEV-1..SEV-4`), `opened_ts`,
`closed_ts`, `trigger_codes[]`, `observed_metrics`, `actions_taken[]`, `evidence_refs[]`,
`postmortem_ref`.

**`HealthSample`** — Identity `(component, metric, ts)`; fields: `value`, `unit`, `status`
(`OK`, `WARN`, `FAIL`), `threshold_ref` (the parameter id of the threshold used).
Rule: a threshold without an id in AX-15 cannot be applied (`AX-03:§1.5-R1`).

**`Experiment`** (research) — Identity `experiment_id`; fields: `hypothesis_id`,
`preregistration_hash`, `dataset_refs[]`, `config_hash`, `metrics`, `result` enum, `created_ts`,
`evidence_class` (`[SIMULATED]`, `[MEASURED]`). Immutable once recorded; corrections are new records
(AX-10 §3).

---

## 2. Identity rules (`AX-03:§2`)

1. **ULIDs for locally created ids** (`intent_id`, `decision_id`, `target_id`, `plan_id`,
   `incident_id`, `experiment_id`): 26-char Crockford base32, 48-bit ms timestamp + 80-bit randomness
   from a CSPRNG. Rationale `[D]`: lexicographic order = time order (useful for journal scans),
   collision probability negligible, no coordination required, and no dependency on a UUID library
   (`AX-03:§2.1`).
2. **Idempotency keys** are a distinct namespace from ULIDs: format
   `ax<env0><purpose2><instrument_code10><epoch_base36><counter2>` — total ≤ 32 chars, characters
   restricted to `[A-Za-z0-9_-]` (the venue's toolkit strips other characters; restricting at source is
   safer than sanitising later) `[V-KIT]`. The key is stored in the journal *before* sending
   (INV-3) and is unique per (intent, attempt-class): a genuine retry after a *resolved* failure reuses
   the key, a *new decision* gets a new key (`AX-03:§2.2`, test `T-ID-002`).
3. **Content hashes** for immutable objects: `sha256(canonical_bytes)` (§6).
4. **No natural-language keys**: a symbol, timestamp, or order id is never used as a primary key alone;
   composite keys are explicit in the DDL (`contracts/sql`).
5. **Identifier immutability**: an id, once assigned, is never reused, even after deletion of the
   underlying record.

---

## 3. Time model (`AX-03:§3`)

### 3.1 The five clocks (`AX-03:§3.1`)

| Clock | Definition | Source | Use |
|---|---|---|---|
| `event_ts` | when the event happened at the venue | payload field (`t`, `E`, `time`, bar `open_time`) | ordering *within* a venue stream, feature computation |
| `ingest_ts` | when AXIOM's process received it | local wall clock + `server_offset_ms` correction, monotonic guard | **availability / point-in-time** (INV-4) |
| `decision_ts` (`as_of`) | the instant a decision is declared to have been made | scheduler tick, wall clock corrected | snapshot scoping, latency accounting |
| `intent_ts` | when a write-ahead intent was journaled | same clock as `ingest_ts` | latency accounting, audit |
| `venue_ack_ts` | when the venue answered | local receive time of the response | execution-quality analytics |

All are stored as UTC epoch milliseconds (`i64`). `ingest_ts` must be monotonic non-decreasing per
process; the writer enforces this by `max(prev_ingest, now)` and flags any wall-clock regression
(`EV-CLOCK-REGRESSION`).

### 3.2 Availability rule (`AX-03:§3.2`) — the point-in-time law

> A decision with `as_of = T` may read only records with `ingest_ts ≤ T`, and for any record that has
> later revisions, only the revision whose `first_ingest_ts ≤ T`.

Enforcement is structural, not disciplinary:

- Feature/forecast code receives a `TapeCursor(as_of)` handle and **has no other data access**: the
  import linter forbids `mdp.store` reads from `sfp`/`fcp`/`pfp` code (`T-PIT-001` static check).
- `TapeCursor` yields, for each instrument and series, the value as of `as_of`.
- The replay engine (AX-11 §5) drives the same cursor over recorded data; therefore live and backtest
  cannot diverge in their view of "what was known" (INV-5).
- `T-PIT-002` (runtime canary): a test tape contains a "future" record; any decision whose inputs
  change when that record is added is a **release blocker**.

### 3.3 Bar semantics and close detection (`AX-03:§3.3`)

- Bar intervals: `15m`, `1h`, `4h` are canonical decision intervals (AX-01 §2.3). All intervals
  available at the venue remain recordable for research.
- `open_time` alignment: Unix-epoch multiples of the interval (the venue's own convention as observed
  in responses `[V-DOC]`); `close_time = open_time + interval − 1 ms` where the venue supplies it.
- A bar becomes **provisional** at `open_time` (WS updates flow in) and **final** only when *all* hold:
  (a) `server_now ≥ close_time + P-DATA-003 (bar_close_grace)`, (b) a REST `klines` re-fetch for the
  closed bar succeeds and matches the WS values within `P-DATA-004` tolerance, or (c) the venue's REST
  bar is the *only* source available and the grace period has passed.
  `bar_close_grace` is `[C]`, calibrated as `max(P-DATA-005, p99(WS delivery delay) + 1 s)` with a
  floor of 3 s (AX-15 `P-DATA-003`); until calibrated, the floor applies.
- **Decisions never use provisional bars** (they may use *current* book/quote/trade state and the last
  final bars). A decision cycle that finds a canonical bar not yet final by its deadline is skipped for
  the affected instrument with a `Refusal(reason = BAR_NOT_FINAL)` (`AX-03:§3.3-R1`).
- Revisions: if the REST re-fetch differs from the WS bar, both are stored, `revision` increments, and
  the REST value is authoritative for closed bars (`bar_authority = REST_CLOSED`, mandatory; see
  `VCH-32`). A revision arriving after a decision **never** changes that decision; it changes future
  computations only (`AX-03:§3.3-R2`).

### 3.4 Declared availability lag (`AX-03:§3.4`)

Every series carries a declared lag `L_source`: the minimum time between `event_ts` and the earliest
correct `as_of` at which a decision could use it. The lag table (values recorded in
`venue_profile.json` after `VCH-16`/`VCH-33`; defaults in AX-15) is used by the simulator to enforce
the same availability in backtests as in live (AX-11 §5.3). Features must declare
`lag = max(L_sources)`; a feature whose declaration is missing is rejected at load time.

---

## 4. Numeric domain and rounding law (`AX-03:§4`)

### 4.1 Representations (`AX-03:§4.1`)

| Layer | Representation | Reason |
|---|---|---|
| Wire (parse/serialise) | `Decimal` (arbitrary precision) with the **exact original string retained** | the signed message is a byte string; re-formatting a float can change the signature (AX-02 §2.2-R2) |
| Storage of venue-sourced numbers | both: `dec_text` (original) and `f64` (for computation) | exactness for audit; speed for math |
| Internal computation | `float64` | performance; the precision limit is documented and bounded by the quantization policy below |
| Hashed payloads | decimal **strings only**, never floats (§6.2) | hash stability across platforms |

### 4.2 Quantization and rounding (`AX-03:§4.2`) — direction-aware, risk-reducing

Let `tick = PRICE_FILTER.tickSize`, `step = LOT_SIZE.stepSize`, `min_notional = MIN_NOTIONAL.minNotional`
(all `[V-PROBE]`).

- **Prices** are rounded toward the *risk-reducing* side: for a buy, **down** to the tick; for a sell,
  **up** to the tick; for a stop trigger of a long position, up; for a stop trigger of a short, down.
  Rationale `[D]`: rounding toward the side that makes the order less aggressive can only reduce
  slippage and can never increase risk; the cost is a bounded chance of non-execution, which is a
  *known* state rather than an unknown one (A1, A5).
- **Quantities** are always rounded **down** to the step (less size = less risk), except in the
  emergency-flatten path where the quantity is taken exactly from the venue position and rounded
  **down** as well, with a second corrective order if residual position remains above the minimum
  step.
- **Minimum-size rule:** if the rounded quantity has notional `< min_notional`, the order is normally
  **skipped** with `Refusal(reason = BELOW_MIN_NOTIONAL)`. It is raised to the minimum **only if**
  (a) the resulting `risk_R` stays within the per-trade cap, (b) the resulting expected net edge still
  clears the cost hurdle (AX-08 §3.4), and (c) the raised notional stays inside the liquidity cap.
  This rule prevents the classic "minimum size forces oversized risk" failure (`AX-03:§4.2-R1`).
- **Order of operations:** quantize → validate against filters (`minQty`, `maxQty`, `minNotional`,
  `maxPrice`, price band via §6.7 of AX-02) → compute margin requirement → risk-kernel checks →
  submit. Reversing this order is a defect (`T-VALID-001`).
- **Unit chain:** every notional computation uses `contract_multiplier` and the probe-verified
  quantity semantics (`VCH-09`); while `AMB-01` is open, the fallback is: size from
  `risk_R / stop_distance` in *price* terms, then convert with the venue's own reported `marginLocked`
  for verification after acknowledgement (`AX-03:§4.2-R2`).

### 4.3 Numerical hygiene (`AX-03:§4.3`)

- Returns are computed in **log space** (`r = ln(p_t/p_{t-1})`) to keep cross-instrument comparisons
  and compounding additive; PnL accounting remains in price space.
- Volatility/scale estimates use the same unit consistently (per-bar log-return standard deviation);
  every document declares its unit (AX-05 §1.3).
- Cancellation-prone forms (e.g. `E[x²] − E[x]²`) are forbidden where a stable form exists;
  variance uses Welford or an explicit two-pass formula (`AX-03:§4.3-R1`).
- Division guards: any denominator below `P-NUM-001` (default `1e-12`, class `[D]`, unitless) yields
  `NaN` **and** a `QualityFlag`, never a silently large number.
- `NaN`/`inf` never propagate into a decision: the pre-trade kernel rejects any target whose inputs
  contain a non-finite value (`AX-03:§4.3-R2`, test `T-NUM-001`).

---

## 5. Serialisation and hashing law (`AX-03:§5`)

### 5.1 Canonical bytes (`AX-03:§5.1`)

For hashing and for equivalence checks, an object is serialised as canonical JSON:

1. UTF-8, no BOM; 2. object keys sorted by Unicode code point; 3. no insignificant whitespace
(`{"a":1,"b":[2,3]}`); 4. numbers that originated at the venue or in a parameter registry are emitted
as **strings**; 5. integers are emitted as integers; 6. `null` is explicit; 7. arrays preserve order;
8. the resulting bytes are hashed with SHA-256 and rendered lowercase hex.
Test vectors live in `contracts/schemas/canonical_json_vectors.json` (`T-HASH-001`).

### 5.2 What must be hashed (`AX-03:§5.2`)

| Object | Hash of |
|---|---|
| `Snapshot` | the ordered list of `(partition, digest)` pairs + `param_set_hash` + `code_commit` + `model_hashes[]` + `profile_hash` |
| `Decision` | canonical bytes of the entire decision payload |
| `VenueOrder`/`Fill` raw records | the raw response body as received (bytes), so that any later negotiation is detectable |
| `ParamSet` | canonical bytes of the registry entries (id → value) |
| `ModelArtifact` | canonical bytes of the model file(s) + metadata |
| journal | chain: `hash_i = sha256(hash_{i-1} ‖ canonical_bytes(event_i))`, `hash_0 = 0^64` |

### 5.3 Journal chain semantics (`AX-03:§5.3`)

- The chain is verified on every boot and once per hour; a break is `SEV-1` (INV-10, INV-11).
- A chain break does **not** stop risk-reducing actions, but blocks all risk-increasing actions until
  the cause is identified (fail-closed with asymmetric availability, INV-1/INV-9).
- The journal is stored in an append-only table with `seq`, `hash`, `prev_hash`; the database enforces
  `UNIQUE(seq)` and a trigger rejects `UPDATE`/`DELETE` on it (`T-JRN-001`).

### 5.4 Schema versioning (`AX-03:§5.4`)

- Every table and every event carries `schema_version` (semver-like `MAJOR.MINOR`).
- **Additive** changes bump `MINOR`; readers must ignore unknown fields.
- **Breaking** changes bump `MAJOR` and require: new table/type + dual-write period +
  backfill + a migration test + an ADR. Migrations are files under `contracts/sql/migrations/` and are
  forward-only; rolling back means restoring a backup (AX-12 §6).
- The system refuses to start if the database `schema_version` is newer than the code's supported
  version (`T-MIG-001`).

---

## 6. Environments and artifact stamping (`AX-03:§6`)

Environment enum: `RESEARCH`, `BACKTEST`, `SHADOW`, `PAPER`, `PROBE`, `MICRO_LIVE`, `LIVE`.

Rules:
1. Every artifact (bar, forecast, intent, fill, experiment, report) carries `environment`.
2. `PROBE` is reserved for the conformance harness's minimal real orders; its records are excluded
   from performance statistics and from model training (`AX-03:§6-R1`).
3. `LIVE` and `MICRO_LIVE` differ only in the risk budget passed to the governor (AX-10 §4), never in
   code paths (`AX-03:§6-R2`).
4. A run's identity stamp = `(environment, code_commit, param_set_hash, profile_hash, model_hashes,
   schema_version)`; every decision and every report carries it. Two runs with different stamps may not
   be compared without recording the difference (`AX-03:§6-R3`).

---

## 7. Invariants introduced by this document (`AX-03:§7`)

| ID | Invariant | Test |
|---|---|---|
| `AX-03:I1` | One instrument identifier everywhere; no aliases. | `T-ID-001` |
| `AX-03:I2` | Intents are written before transmission, with a unique key. | `T-JRN-003` |
| `AX-03:I3` | No decision reads data with `ingest_ts > as_of`. | `T-PIT-001`, `T-PIT-002` |
| `AX-03:I4` | Decisions use only final bars for bar-based features. | `T-BAR-001` |
| `AX-03:I5` | All rounding is direction-aware and risk-reducing. | `T-ROUND-001` |
| `AX-03:I6` | Non-finite values never reach an order. | `T-NUM-001` |
| `AX-03:I7` | Journal is append-only and hash-chained; break ⇒ no new risk. | `T-JRN-001`, `T-JRN-002` |
| `AX-03:I8` | Every artifact is stamped with its environment and versions. | `T-STAMP-001` |
