# AX-04 — Data Plane: Acquisition, Quality, Storage, Universe

**Status:** Normative.
**Upstream:** AX-02 (venue facts), AX-03 (objects, time, identity).
**Downstream:** AX-05, AX-06, AX-11, AX-12, AX-15, `contracts/sql`.

The data plane (`mdp`) owns everything between "a byte arrived from the venue" and "a decision may read
a value". It is the only plane that touches the network for market data, the only plane that writes L0,
and the only plane that may declare a series *unusable*.

---

## 1. Responsibilities and boundaries (`AX-04:§1`)

**Owns:** WS connections for market data; REST polling for the market-data and reference endpoints in
AX-02 §3.1; L0 tape; L1 curated store; quality gates; gap detection & repair; universe construction;
snapshot materialisation; retention and compaction; data-health signals.

**Does not own:** order/position/account queries (that is `exp`/`rg`, though they are journaled through
the same store); feature computation (`sfp`); any decision.

**Hard rules**
- `AX-04:§1-R1` — Nothing is interpreted before it is stored. The raw payload and its receive metadata
  are appended to L0 first; parsers run afterwards and may fail without losing the raw record.
- `AX-04:§1-R2` — All writes to L1 are idempotent upserts keyed by natural keys (AX-03 §1.2) so that a
  crash mid-write-and-restart converges.
- `AX-04:§1-R3` — Derived data (L2/L3) is never mixed with L1: a rebuild must be able to delete L2/L3
  entirely without losing truth.
- `AX-04:§1-R4` — The store is single-writer (one process); readers are concurrent. Cross-process
  writers are forbidden (SQLite WAL + an advisory lock file).

---

## 2. Collection plan and derived request budget (`AX-04:§2`)

### 2.1 Three collection tiers (`AX-04:§2.1`)

Because the device's storage and the venue's request budget are both finite, instruments are assigned
to a collection tier. The tier is recomputed daily with the universe, and whenever the hot set changes.

| Tier | Instruments | Collected | Purpose |
|---|---|---|---|
| `HOT` | instruments with an open position, a working order, or a target this cycle; plus the top `P-DATA-010` by liquidity or forecast activity | full `trade` tape, `bookTicker`, `depth` snapshot every `P-DATA-011` s, `diffDepth`, all canonical `kline` intervals, `markPrice`, plus REST polls | decisions, execution, microstructure features |
| `WARM` | universe instruments not in `HOT` | `bookTicker`, `kline` (canonical intervals), `trade` aggregated to `P-DATA-012` s buckets (count, volume, taker-buy volume if available, VWAP) | signals that do not need the raw tape; cheap breadth |
| `COLD` | watchlist (not tradeable this cycle) | `kline` daily + `fundingRate` + `openInterest` | research, universe stability, new listing evaluation |

`AX-04:§2.1-R1` — A position in an instrument **forces** `HOT` at the next tick; the transition is
journaled. `AX-04:§2.1-R2` — Tier changes never delete raw data already collected.

### 2.2 Request budget (derivation `[D]`)

Let `N_H`, `N_W` be the counts per tier, and let the canonical intervals be `I = {15m, 1h, 4h}`.

| Source | Cadence | Requests/min | Weight/min |
|---|---|---|---|
| `exchangeInfo` | 1×/start + 1×/day | ~0 | 0 |
| `riskLimits` | 1×/day per instrument | `N_H/1440` | `N_H/1440` |
| `fundingRate` | every `P-DATA-013` (default 60 s) per instrument in `HOT`+`WARM` | `(N_H+N_W)` | same |
| `openInterest` | every `P-DATA-014` (default 300 s) per instrument in `HOT`+`WARM` | `(N_H+N_W)/5` | same |
| `historyFundingRate` | 1×/hour per instrument | `(N_H+N_W)/60` | same |
| `ticker/24hr` (screen) | 1×/day per instrument + 1×/day for the venue-wide universe if a bulk call is permitted | ~0 | 0 |
| `markPrice` (bulk, no symbol) | only if the WS stream is down | ≤ 1/5 s | ≤ 12 |
| `klines` backfill | on gap, per affected `(instrument, interval)` | bursty | ≤ `P-DATA-015` per repair |
| `commissionRate` | 1×/day | ~0 | 0 |

With `N_H = 10`, `N_W = 30` `[O]` (AX-15 `P-DATA-020`, `P-DATA-021`), the steady-state cost is
`≈ 40 + 8 + 0.7 ≈ 49` weight/min against an internal ceiling of 1500 (AX-02 §7.2) — i.e. **~3 %**.
The binding constraint is therefore not REST weight but (a) **storage** (§7) and (b) the **ORDERS**
bucket during active trading (orders, not data). Plan revision trigger: if a daily average exceeds
`P-DATA-022` (default 30 %) of the internal ceiling, the cadence table must be re-derived and the change
signed off (AX-12 §8).

### 2.3 WS subscription set (`AX-04:§2.3`)

Per `HOT` instrument: `trade`, `bookTicker`, `depth`, `diffDepth`, `markPrice`, and
`kline_{15m,1h,4h}`. Per `WARM`: `bookTicker`, `kline_{15m,1h,4h}`. Plus one venue-wide
`wholeBookTicker` subscription (breadth/monitoring). `wholeRealTime` is **not** subscribed by default
(it is spot-weighted and voluminous); the daily screen uses REST instead (`AX-04:§2.3-R1`).

### 2.4 Poller discipline (`AX-04:§2.4`)

- Every poller declares `(endpoint, weight_per_call, cadence, priority_class)` and is driven by one
  scheduler that respects the class shares in AX-02 §7.2.
- A poller that misses `P-DATA-016` consecutive deadlines emits `EV-COLLECT-LAGGING` and, if the
  affected series is decision-critical, degrades the instrument to `no-new-risk` (INV-1).
- All pollers are idempotent and record `(endpoint, params_hash, request_ts, response_hash)` to allow
  exact replay of the request side of any incident.

---

## 3. Quality gates (`AX-04:§3`)

A **gate** is a pure function from an incoming record (and its recent context) to one of:
`ACCEPT`, `ACCEPT_WITH_FLAG(flag)`, `DROP(reason)`, `QUARANTINE_SERIES(reason, duration)`,
`EXCLUDE_INSTRUMENT(reason)`, `HALT_DATA(reason)`. Every gate firing is counted per
`(instrument, gate, day)` and exported as a metric; a gate whose firing rate exceeds its budget
(`P-DATA-030`) raises an incident.

| ID | Gate | Rule (with units) | Action on violation |
|---|---|---|---|
| `QC-01` | Schema/parse | payload → object conforms to the current parser contract | `DROP` + count |
| `QC-02` | Timestamp sanity | `event_ts ≤ ingest_ts + P-DATA-031` and `event_ts ≥ ingest_ts − P-DATA-032` | `ACCEPT_WITH_FLAG(ts_out_of_range)`; if persistent, `QUARANTINE` |
| `QC-03` | Monotonic receive | `recv_seq` strictly increasing; wall clock non-regressing | `HALT_DATA` on regression (clock/GPU/OS problem) |
| `QC-04` | Bar integrity | `l ≤ min(o,c) ≤ max(o,c) ≤ h`, all prices `> 0`, `volume ≥ 0`, `trade_count ≥ 0` for REST bars | `DROP` (WS) / `QUARANTINE` (REST bar) |
| `QC-05` | Bar uniqueness | one final revision per `(instrument, interval, open_time)`; later revisions replace and are recorded | replace + flag `revised` |
| `QC-06` | Bar continuity | for each `(instrument, interval)`, the set of `open_time` values has no hole beyond `P-DATA-033` consecutive missing bars during trading | `QUARANTINE_SERIES` + schedule repair (§9) |
| `QC-07` | Staleness | `server_now − last_ingest > max(P-DATA-034, k·p99_inter_arrival)` per series (k default 5) | `QUARANTINE_SERIES`; instrument ⇒ `no-new-risk` |
| `QC-08` | Cross-source bar agreement | for a closed bar, `|WS − REST|/REST ≤ P-DATA-035` on `c` and volume | use REST; flag `ws_rest_divergence`; recurring ⇒ incident |
| `QC-09` | Quote sanity | `bid < ask`, both `> 0`, quantities `> 0`; `spread/ mid ≤ P-DATA-036` | `DROP`; if the ratio persists above the ceiling, `EXCLUDE_INSTRUMENT` from new risk (illiquid) |
| `QC-10` | Quote jump | `|ln(mid_t/mid_{t−1})| > P-DATA-037 · σ̂_1m` | flag `price_jump`; block new entries on that instrument until `P-DATA-038` bars pass without recurrence |
| `QC-11` | Trade sanity | `qty > 0`, `price` within `P-DATA-039` of the current quote band | `DROP` + count |
| `QC-12` | Trade-id regression | when `venue_trade_id` integrity is verified (`VCH-13`), the per-symbol id must not regress within a stream session | `HALT_DATA` for that stream + resync |
| `QC-13` | Trade tape gap | id discontinuity larger than `P-DATA-040` | mark tape `incomplete` for the interval; trade-derived features are disabled for that interval (§4.3 of AX-05) |
| `QC-14` | Book coherence | reconstructed book has `best_bid < best_ask`, no negative quantities, level count ≥ `P-DATA-041` | `QUARANTINE` book state; re-snapshot |
| `QC-15` | Funding sanity | `|rate| ≤ cap + ε` and `next_funding_time` in the future | `DROP` observation; keep last good |
| `QC-16` | Open-interest sanity | `size ≥ 0`; `|Δ ln OI| ≤ P-DATA-042` between consecutive polls | flag `oi_outlier`; the observation is marked unusable for features |
| `QC-17` | Reference drift | `exchangeInfo`/`riskLimits`/`commissionRate` hash changed unexpectedly | `EV-VENUE-DRIFT` → re-run affected probes (AX-02 §1.3) |
| `QC-18` | Symbol membership | an incoming stream for a symbol not in the current universe | store (L0) but exclude from features; alert if it persists (subscription leak) |
| `QC-19` | Instrument status | venue `status ≠ TRADING`, or `API_TRADE_FORBIDDEN`, or `OPEN_FORBIDDEN` | `EXCLUDE_INSTRUMENT` from new risk immediately; existing positions get the reduce-only path (AX-09 §5.2) |
| `QC-20` | Storage write health | append failure, fsync error, hash-chain write failure, or free space < `P-DATA-043` | `HALT_DATA` for non-journal writes; journal failure halts all risk-increasing activity (INV-1, INV-10) |

**Quarantine semantics:** a quarantined series is *not* deleted and *not* silently filled; it is marked
and any feature depending on it returns `insufficient_data` until repaired. Filling (interpolation) is
permitted **only** for non-decision-critical series and only where a document explicitly authorises it
(none currently does). `AX-04:§3-R1` — *Never interpolate a price series used by a decision.*

---

## 4. Universe construction (`AX-04:§4`)

The universe is a **deterministic function** of stored data plus venue metadata, recomputed once per
day at 00:10 UTC and frozen for the day (`universe_id = hash(rule_version, inputs_digest, date)`).
Intraday changes are limited to *removals* (safety) and are journaled; additions wait for the next day.
Rationale `[D]`: additions mid-day create selection bias and complicate attribution; removals protect
capital and must be instant.

### 4.1 Algorithm (`AX-04:§4.1`)

1. Fetch/refresh `exchangeInfo`; select `contracts[]` with `margin_token = USDT` and `inverse = false`
   (the venue's own sample includes an inverse contract `BTC-SWAP` with `marginToken=BTC` — a trap the
   selector must exclude explicitly) `[V-DOC]`; require `status = TRADING` and no API restriction.
2. Compute, over the last `P-UNI-001` days (default 14) of stored data, per candidate:
   - `median_daily_quote_volume` (`QDV`), `median_spread_bps` (`S`), `median_minute_quote_volume`
     (`MQV`), `book_depth_at_touch` (`D1`, notional within `P-UNI-002` bps of mid),
     `days_since_listing` (`DSL`), `bar_completeness` (`BC`, fraction of expected final bars present).
3. Apply admission filters (all must hold; each threshold is `[O]`/`[C]` per AX-15):
   - `BC ≥ P-UNI-003`, `DSL ≥ P-UNI-004`, `QDV ≥ P-UNI-005`, `S ≤ P-UNI-006`,
     `data_health = OK` for the last `P-UNI-007` days.
   - **Participation feasibility (the binding, account-size-derived rule):** let
     `MPN = max_position_notional` for this instrument permitted by the risk budget (AX-07 §7) and let
     `MQV` be the median minute quote volume. Require
     `MPN ≤ P-UNI-008 · MQV` (default `P-UNI-008 = 0.05`, i.e. our maximum position must be at most 5 %
     of a typical minute's traded notional) and `MPN ≤ P-UNI-009 · D1`. Instruments that fail are
     excluded **regardless of their signal quality** — the constraint is reality, not preference (A3).
4. Rank survivors by a liquidity score `LS = ln(QDV) − P-UNI-010 · S` and keep the top `P-UNI-011`
   (default 20, `[O]`), subject to cluster caps (`P-UNI-012` instruments per correlation cluster,
   AX-07 §5) so the universe is not one asset in twenty costumes.
5. Emit the `UniverseRecord` (immutable, hashed) with per-instrument tier, thresholds applied, the
   measured values, and the rule version.

### 4.2 Frozen-day rule and exceptions (`AX-04:§4.2`)

- For the day `D`, decisions use `universe(D)` only.
- A removal may occur intraday when: `QC-19` fires, data health drops below OK for `P-UNI-013`
  consecutive cycles, or the instrument loses its position-relevant streaming health. Removals are
  journaled with cause and take effect for new risk immediately; positions in a removed instrument
  continue to be managed (protection/exit remain available).
- A previously excluded instrument never re-enters before a new daily computation.

### 4.3 Survivorship and research integrity (`AX-04:§4.3`)

Research datasets must include instruments that were in the universe on the relevant date **and**
instruments later removed or delisted; the dataset builder therefore reconstructs the historical
universe from the daily `UniverseRecord`s, not from today's list. Backtests that use today's universe
over past dates are a defect (`T-DATA-004`) because they inflate performance via survivorship.

---

## 5. Snapshot materialisation (`AX-04:§5`)

At each decision tick, `mdp` produces the `Snapshot` object (AX-03 §1.4) for `as_of = decision_ts`:

1. Determine the instrument set = current universe ∩ instruments with `data_health ≥ WARN`.
2. For each instrument, resolve the cursor-visible values: last final bars per interval, latest quote,
   latest mark/index, latest funding, latest OI observation, latest `RiskTierObs`, plus the current
   `Position`/`AccountState` snapshots (from `exp`/`rg`, journaled).
3. Compute `snapshot_id` over the partition digests (AX-03 §5.2) and persist the snapshot's *digest
   manifest* (not a copy of the data — the data is immutable, so digests suffice for reproduction).
4. `T-SNAP-001`: two snapshots with the same manifest must produce identical decisions (tested by
   replay with `T-PARITY-002`).

Cost note `[D]`: the manifest approach keeps a snapshot's marginal storage at a few hundred bytes per
instrument rather than duplicating the store; reproduction happens via the immutable L1 partitions.

---

## 6. Storage architecture (`AX-04:§6`)

### 6.1 Layers (`AX-04:§6.1`)

| Layer | Content | Format | Mutability | Rebuildable |
|---|---|---|---|---|
| **L0** | raw payloads as received (WS messages, REST bodies), with receive metadata | length-prefixed JSONL segments + SHA-256 per segment, index rows in SQLite | append-only | n/a (source of truth) |
| **L1** | curated objects of AX-03 §1.2/§1.3 (bars, trades, quotes, depth, funding, OI, orders, fills, positions, journal) | SQLite (hot, WAL) + Parquet (cold) | insert + upsert on natural key | yes, from L0 |
| **L2** | features, forecasts, targets, decisions, health samples | SQLite + Parquet | replace-by-partition, versioned | yes, from L1 + code + params |
| **L3** | research copies, datasets, reports, simulator outputs | Parquet/CSV | disposable | yes |

Hot/cold split rule (`AX-04:§6.1-R1`): rows newer than `P-DATA-050` days live in SQLite; older rows are
exported to Parquet partitions `dt=YYYY-MM-DD/instrument=<id>/kind=<...>` and pruned from SQLite.
Export is verified by row count + a digest per partition before pruning (never prune without verify).

### 6.2 Journal (`AX-04:§6.2`)

The journal (AX-03 §5.3) lives in its own append-only table with `seq UNIQUE`, `prev_hash`, `hash`, and
database triggers that reject `UPDATE`/`DELETE`. It is *never* compacted or exported-and-pruned: it is
small (one row per event, canonical JSON) and it is the audit spine. Its growth is monitored
(`P-DATA-051` bytes/day) and if the projected horizon exceeds the device capacity, the response is to
reduce verbose payloads (store hashes of large bodies in L0 and reference them), never to prune the
chain.

### 6.3 Write path (`AX-04:§6.3`)

`L0 append (fsync per segment flush) → L1 upsert (transaction per batch) → journal append (fsync per
event batch) → metrics`. Failure of the journal write blocks *risk-increasing* actions (INV-1) but not
the collection loop; failure of L0 blocks everything (nothing may be interpreted un-stored, §1-R1).

### 6.4 Rebuild procedure (`AX-04:§6.4`)

`rebuild(kind, range)`: L1 → replay L0 segments of the range through the same parsers and gates →
compare digests to the existing rows → report diffs → replace only on `--apply` with a journaled
change record. Performance budget: rebuild of one day for `N_H+N_W = 40` instruments must finish within
`P-DATA-052` (default 30 min single-threaded on the reference device, measured by `BENCH-04`). If the
budget cannot be met on the owner's device, the design's response is to keep *more* raw data cold
(L0 retained longer) and rebuild in windows, not to skip verification.

---

## 7. Retention and capacity model (`AX-04:§7`)

Assumptions are explicit and `[D]`/`[C]`; they are re-measured by the benchmarks in AX-12 §2 and the
retention parameters are re-derived from the measurements (never hardcoded from this table).

Per `HOT` instrument, per day, with trade rate `r_t` trades/s and `bookTicker` rate `r_b` updates/s:

| Series | Rows/day | Bytes/row (canonical, est.) | Bytes/day |
|---|---|---|---|
| trades | `86 400 · r_t` | ~110 | `9.5 · r_t` MB |
| bookTicker | `86 400 · r_b` | ~120 | `10.4 · r_b` MB |
| depth snapshots (every `P-DATA-011` s, 10 levels) | `86 400 / P-DATA-011` | ~900 | ~`0.9 · 86 400 / P-DATA-011` MB |
| klines (3 intervals) | 96 + 24 + 6 | ~140 | negligible |
| other polls | ≤ 2 000 | ~120 | negligible |

With `r_t = 3`, `r_b = 4`, `P-DATA-011 = 30` `[C]` (measurement-derived; these are *placeholders to be
re-measured*, marked `[V-PROVISIONAL]`), one `HOT` instrument costs `≈ 28 + 42 + 2.6 ≈ 73 MB/day`;
ten such instruments ≈ `0.7 GB/day`. **This is the binding capacity constraint of the design.**

**Tiered retention (`AX-04:§7-R1`), all deterministic:**

| Age | Trades | Quotes | Depth | Bars |
|---|---|---|---|---|
| 0–`P-DATA-053` days (default 30) | raw | raw | snapshots kept | final bars |
| `P-DATA-053`–`P-DATA-054` days (default 365) | aggregated to `P-DATA-055` s buckets (count, volume, VWAP, min/max, taker-buy volume if verified) | aggregated to `P-DATA-055` s (OHLC of mid, mean spread, mean depth) | dropped except daily snapshots at fixed times | final bars |
| `>` `P-DATA-054` | dropped (bars and funding/OI retain the long history) | dropped | dropped | final bars |

Aggregation is a *derived* transformation: it is recomputed from L0 during compaction, and its
definition is versioned (`aggregation_version`) so that research can tell which statistic changed.
`AX-04:§7-R2` — retention never applies to the journal, to fills/orders/positions, to
`UniverseRecord`s, or to calibration artifacts.

**Capacity guard:** before compaction, the free-space projection over `P-DATA-056` days is computed; if
it falls below `P-DATA-057`, the system (a) drops `COLD`-tier streaming, (b) reduces `P-DATA-011` (depth
cadence) and `P-DATA-012`, (c) stops `WARM` trade aggregation, in that order, and journals each
degradation. Reduction of the **journal or fills** is never an option (INV-10).

---

## 8. Gap detection and repair (`AX-04:§8`)

Detection: `QC-06` (bar continuity), `QC-13` (trade-id discontinuity), WS session boundaries, and a
daily full-coverage audit that recomputes the expected key set per `(instrument, interval, day)`.

Repair procedures (`mdp.repair`), in precedence order:

1. **Bars:** REST `klines` with `startTime`/`endTime` windows ≤ `P-DATA-060` bars per call, respecting
   weights; write as `revision+1` with `source=REST`; then re-run `QC-04/06` on the range.
2. **Trades:** REST `trades` returns only the last 60 `[V-DOC]`, so historical trade gaps **cannot** be
   repaired: the interval is marked `tape_incomplete` permanently, and trade-derived features are
   flagged unavailable for it (§3 `QC-13`). This is a designed consequence, not an oversight.
3. **Book/quote gaps:** unfixable retroactively; the affected windows are marked
   `book_unavailable`, and any feature using book data over those windows returns `insufficient_data`.
4. **Funding/OI/reference:** re-poll (idempotent upsert). OI history holes cannot be filled — they are
   permanent by construction `[V-DOC]`; the feature layer must tolerate them (AX-05 §3.4).

Every repair writes a `RepairRecord(scope, method, rows, digests, started_ts, finished_ts)` to the
journal. Repair never overwrites a *final* bar with lower-quality data: REST supersedes WS only
(AX-03 §3.3), and a repair that would reduce data quality is rejected with an incident.

---

## 9. Boot and readiness sequence (`AX-04:§9`)

The system may only leave `OFF` when **all** of the following hold (each is a readiness check emitting
`HealthSample`s):

1. Store integrity: SQLite `PRAGMA integrity_check` OK on the required schemas; journal chain verified.
2. Schema compatibility: `schema_version` within the supported range (`T-MIG-001`).
3. Clock: `abs(server_offset_ms) ≤ P-VEN-001` and the last 8 offset samples consistent.
4. Venue profile: a `VenueProfile` exists, is not `STALE` per AX-02 §1.3, and all *blocking* probes for
   the target environment are `PASSED`.
5. Reference data: `exchangeInfo`, `riskLimits`, `commissionRate` fetched within `P-DATA-070` hours.
6. Universe: today's `UniverseRecord` exists and is hashed.
7. Data: for every universe instrument, bars are final through the last closed canonical interval, and
   the series health is `OK` or `WARN` (not `FAIL`).
8. Streams: WS connected and heart-beating for all `HOT` instruments; `HOT` set consistent with the
   positions/orders read from the venue.
9. Account: positions, working orders and balance fetched; reconciliation complete per AX-08 §7.
10. Governor: state is `NORMAL` or `CAUTION` (a `REDUCED`+ state requires an explicit re-arm).
11. Owner inputs: all mandatory `[O]` entries present (AX-15 §9); otherwise the system stays `OFF`
    (designed fail-closed, not an error).

Readiness is re-evaluated continuously, not only at boot; a failure at any time moves the system to the
governor state implied by the mapping in AX-09 §4.

---

## 10. Data-health states and their meaning (`AX-04:§10`)

| State | Condition | Consequence |
|---|---|---|
| `OK` | all decision-critical series fresh and gate-clean | full operation |
| `WARN` | a non-critical series is stale/gapped, or a critical series has isolated flags | new entries permitted in the instrument only if the *decision-critical* subset is `OK`; size haircut `P-DATA-080` (default 20 %) applies |
| `FAIL` | any decision-critical series violates `QC-07` staleness, or book state is quarantined, or `QC-19` fired | **no new risk** in that instrument (INV-1); protective/exit paths remain |
| `HALT` | `QC-03`, `QC-20`, or store-integrity failure | all risk-increasing activity in the whole system stops (AX-09 §5.3) |

The mapping from states to governor transitions is defined once, in AX-09 §4.3, and this document must
not duplicate it.

---

## 11. Test obligations (`AX-04:§11`)

| Area | Tests |
|---|---|
| Identity & keys | `T-ID-001`, `T-ID-002` |
| Gates | `T-QC-001`…`T-QC-020` (one per gate + a synthetic dataset exercising all firing paths) |
| Point-in-time | `T-PIT-001`, `T-PIT-002` (shared with AX-03) |
| Bars | `T-BAR-001` (no provisional bar reaches a decision), `T-BAR-002` (revision never changes a past decision) |
| Store | `T-SNAP-001`, `T-REBUILD-001` (L1 from L0 is byte-reproducible), `T-REBUILD-002` (aggregation version pinning), `T-JRN-001`, `T-JRN-002` |
| Universe | `T-DATA-004` (historical universe reconstruction; no survivorship), `T-UNI-001` (deterministic given inputs), `T-UNI-002` (participation rule rejects an illiquid instrument regardless of rank) |
| Repair | `T-REPAIR-001` (idempotent re-repair), `T-REPAIR-002` (never downgrade quality) |
| Capacity | `T-CAP-001` (guard triggers and journal is never dropped), `T-CAP-002` (compaction preserves row counts & digests) |
| Readiness | `T-READY-001`…`T-READY-011` — one test per readiness check, each asserting the system **stays OFF** when the check fails |
