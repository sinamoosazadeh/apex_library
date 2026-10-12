# AX-08 — Execution, Cost Model and Outcome Uncertainty

**Status:** Normative.
**Upstream:** AX-02 (§6–§9 venue semantics, error taxonomy), AX-03 (objects), AX-07 (sizes/limits).
**Downstream:** AX-09 (kill paths), AX-11 (simulator fidelity), AX-12 (runbooks), AX-14 (tests).

The execution plane turns an approved `Target` into venue state. Its governing principle is A5: the
rare, expensive events (unknown outcomes, duplicate orders, unprotected positions, failed cancels)
dominate survival, so every interaction with the venue is a *transaction with a documented state
machine*, never a fire-and-forget call.

---

## 1. Authority and scope (`AX-08:§1`)

`exp` may choose **how** to reach a target: which order construct, at which price bound, in how many
slices, with what timing, and with what retry policy. It may not change: symbol, direction, size,
leverage, stop level, or the risk budget. Those come from AX-07 and may only be reduced (by `rg`).

---

## 2. Timing model and latency budget (`AX-08:§2`)

Stages, with their sources (all measured by `VCH-16` and re-measured continuously in the journal):

| Stage | Symbol | Typical (measured) | Consequence |
|---|---|---|---|
| decision tick to plan | `t_plan` | ≤ 200 ms in-process | no network |
| plan to request written | `t_write` | ≤ 20 ms (journal fsync) | INV-3 cost |
| request to venue ack | `t_ack` | 100–600 ms `[V-PROBE]` | network + venue |
| ack to fill observation | `t_fill` | ≤ 1 s (query) | reconciliation |
| fill to protection acknowledged | `t_prot` | `VCH-23` measures it | the unprotected window |

**Budget (`AX-08:§2-R1`):** the *economic* latency budget is dominated by `t_plan + t_ack ≈ 0.5–1 s`.
The minimum admissible horizon (AX-01 §2.3) is 15 minutes = 900 s, so latency consumes ≤ 0.11 % of the
holding period; the design's margin is a factor of ~1000. **This is why A6 forbids shorter horizons:**
not ideology, but the measured relationship between latency and edge.

**Protection bound (`AX-08:§2-R2`):** `t_prot ≤ P-EXE-003` (default 10 s, `[C]`: `CAL-EXE-01` sets it
at the p99 of measured `t_prot` plus a margin, floor 5 s). Every second beyond the bound is an incident
(§6.4).

---

## 3. Cost model (`AX-08:§3`)

Total expected cost of a round trip, per instrument and size, in return units:

```
c_total(q) = c_fee + c_spread(q) + c_slip(q) + c_impact(q) + c_funding(H)
```

### 3.1 Fees (`AX-08:§3.1`)

`c_fee = fee_open + fee_close`, both read at run time from `commissionRate` `[V-PROBE]` (never guessed;
`-1111`/`-1131`-class surprises are exactly what happens when fees are assumed). Maker/taker selection:
the entry construct in §4 is a taker (IOC); the exit is a taker by default; if the `POST_ONLY` policy
is ever enabled (AX-02 §6.2) the model uses the venue-reported maker rate and the measured fill rate,
and the *expected* cost includes the missed-fill cost (AX-07 §6.3's `F_i`/opportunity term).

### 3.2 Funding (`AX-08:§3.2`)

`c_funding(H) = Σ_{settlements in holding window} sign(position) · rate_k · (1 + adjust)`, where the
`rate_k` are the *settled* rates when known (training/labels, AX-06 §2.1) and the *current* rate
extrapolated when future (decision), with:
- the sign convention derived from the venue behaviour, verified by `VCH-25` (a long pays when the
  rate is positive);
- the settlement schedule from `FundingRateObs.nextFundingTime` + `period` `[V-DOC]` (samples show
  `8H`); **never assumed to be 8 hours for a specific instrument** — it is read;
- the **settlement-window rule** (`AX-08:§3.2-R1`): if a settlement falls inside the expected holding
  window and the expected payment exceeds `P-COST-001` of the expected remaining edge, the entry is
  deferred until after the settlement (or the position is closed before it). This rule is applied at
  decision time using `F-FUNDWIN`.

### 3.3 Spread, slippage and impact (`AX-08:§3.3`) — measured, not assumed

For a taker order of notional `n`:
```
c_spread(n) = s_eff/2            (half of the *effective* spread at execution; s_eff measured from our fills)
c_slip(n)   = E[ slip | n, instrument ]   (from the ledger, bucketed by n/MQV ∈ {<0.1%, <0.5%, <1%, <5%, ≥5%})
c_impact(n) = λ̂ · n / (f · MQV)   (Kyle-λ from AX-05 §3.3, applied with the same bucketing to avoid double counting)
```
**Estimator and conservatism (`AX-08:§3.3-R1`):** the cost gate uses the **upper** estimator
`c_hat = quantile_{P-COST-010}(samples) + m·SE` (default `P-COST-010 = 0.75`, `m = 1`), not the mean,
because the failure mode of underestimating cost is taking trades that do not exist (A1). The mean is
used only for reporting and for the ledger's analytics.

**Self-measurement loop (`AX-08:§3.3-R2`):** for every fill the system records
`slip = (fill_price − decision_mid)/decision_mid · sign` and
`delay_cost = (decision_mid − arrival_mid)/decision_mid · sign` where `arrival_mid` is the mid at the
moment the request was written. These feed `F-SLIP-MEAS` and the cost model's refit
(`CAL-COST-01`, weekly, with a minimum sample `P-COST-011`; if the sample is insufficient, the model
keeps its previous parameters *and* the cost gate uses the wider uncertainty band, so the system trades
less rather than optimistically).

### 3.4 The trade gate (`AX-08:§3.4`) — the single economic admission rule

A candidate trade on instrument `i`, horizon `H`, size `q` is executed only if

```
μ_net(i,H) − z_g · σ_model(i,H)   >   c_total(q) + m_c · σ_c(i,q) + F_i(q)/equity
        edge lower bound                     expected cost      cost uncertainty   fixed-cost term
```
with `z_g = P-COST-020` (default 1.0), `m_c = P-COST-021` (default 1.0), and
`F_i(q) = max(0, minNotional_i · c_prop_i − q · price · f · c_prop_i)` capturing the discrete-size
effect when the *optimal* size is below the venue minimum but the minimum must be traded.
`AX-08:§3.4-R1` — This inequality (together with AX-06 §7) is the only place where a trade becomes
legal. Any code path that submits an order without passing through it is a defect (`T-COST-001`
asserts the call graph).

### 3.5 Cost model versioning (`AX-08:§3.5`)

The cost model is an artifact (AX-03 §1.1 `ModelArtifact`, `kind = COST_MODEL`) with a version and a
hash. Labels (AX-06 §2.1) and simulator runs (AX-11) record the version they used. If measured cost
exceeds the model's `p95` band for `P-COST-030` consecutive sessions, the governor de-risks (AX-09 §4.4)
and the model is re-fitted before new promotions.

---

## 4. Order planning (`AX-08:§4`)

### 4.1 Price construction (`AX-08:§4.1`)

Let `p_ref = F-MICRO` (microprice) at decision time, `s` the current quoted spread (fraction), `μ_net`
the forecast, `c_rest` the cost components other than the entry's own slippage.

- **Economic bound (indifference price).** The worst entry price that still leaves the required
  surplus: for a buy, `p_bound = p_ref · exp( μ_net − c_rest − m_c·σ_c )`; for a sell,
  `p_bound = p_ref · exp( −(μ_net − c_rest − m_c·σ_c) )`. Beyond this price, the trade is refused
  (`Refusal(reason = COST_DRIFT)`), never "chased" (`AX-08:§4.1-R1`).
- **Aggressive cross price.** For a taker IOC: buys at `ask + k_x·s` (cross, plus one to two ticks),
  sells at `bid − k_x·s`; `k_x = P-EXE-001` (default 0.25, `[C]`: `CAL-EXE-02` fits `k_x` to maximize
  fill probability subject to the slippage distribution).
- **Submitted price** = the price that is *aggressive enough to fill* while remaining inside the bound,
  quantized **toward risk reduction** (AX-03 §4.2): `p_submit = min(p_cross, p_bound)` for buys
  (max for sells). If `p_cross > p_bound` ⇒ refuse; the market has moved beyond the edge.
- Additionally validate: tick alignment, price band (AX-02 §6.7), `maxPrice`/`minPrice` filters, and
  `price > 0`.

### 4.2 Slicing (`AX-08:§4.2`)

- If `notional ≤ P-EXE-020 · MQV` (default 0.05): **single order**, no scheduling. Rationale `[D]`:
  below this size the measured impact is inside the cost model's noise band and scheduling only adds
  non-execution risk.
- Above it: split into `N = ceil(notional / (P-EXE-020 · MQV))` slices, spaced by `P-EXE-021` seconds
  (default 15 s, `[C]`, `CAL-EXE-03` minimizes expected cost net of non-execution risk on the recorded
  data), each slice re-evaluating its own `p_bound`, with an overall deadline
  `T_deadline = P-EXE-022` minutes after which the residual is abandoned (and the target becomes a
  *new* decision next cycle). The deterministic schedule is mandatory (INV-5); Almgren–Chriss-style
  continuous optimisation is `T3` and may only replace it after an admission test showing a lower
  realised cost on our own fills.

### 4.3 Attempts and abandonment (`AX-08:§4.3`)

- Maximum `P-EXE-005` attempts (default 2) per intent; each attempt requires a fresh snapshot and a
  re-evaluated gate (§3.4). Attempts are recorded with their price bounds.
- **Never chase**: an attempt may not raise its price bound; the bound is recomputed from the *new*
  forecast, which may be smaller (or zero, in which case the residual is cancelled).
- Partial fills: the residual is re-sized (`target − filled`), re-gated, and either attempted again
  within the limits of §4.3 or abandoned with a `Refusal(reason = PARTIAL_INSUFFICIENT)`
  (`AX-08:§4.3-R1`).

### 4.4 Open-order discipline (`AX-08:§4.4`)

- At most `P-EXE-040` working orders per instrument (venue rejects beyond a cap with `-1193`/`-1207`
  `[V-DOC]`; our own cap is much lower, derived from `1 entry + 1 protection + slack`).
- Before any new entry, working non-protective orders for that instrument are cancelled (avoid
  self-crossing and margin contention); the cancel is confirmed by query, never assumed.
- Order-rate budget: submissions are counted against the `ORDERS` bucket by the request governor
  (AX-02 §7.2, class P1). With a 30 order/2 s internal cap, the system can open up to ~10 positions per
  second in theory; the *policy* cap `P-EXE-041` (default 4 new positions per minute) is far tighter and
  is the one that matters for operational safety.

---

## 5. Outcome-uncertainty protocol (`AX-08:§5`)

### 5.1 States of a venue transaction (`AX-08:§5.1`)

```
WRITTEN ──send──▶ SENT ──2xx+success──▶ ACKED ──fills──▶ FILLED
   │               │                      │
   │               └──definitive 4xx──▶ REJECTED
   │               └──timeout/5xx/-1006/-1007/-114x──▶ UNKNOWN
   └──(pre-send abort: journaled)──▶ ABANDONED
                                        │
                            resolution ladder (§5.2)
                                        ▼
                    RESOLVED_FILLED / RESOLVED_WORKING / RESOLVED_ABSENT / RESOLVED_ESCALATED
```

Rules:
1. `SENT` is journaled before the socket write; `ACKED` requires both HTTP 2xx **and** a business
   success code (v1: the route's documented success code; v2: `200`) `[V-DOC]`.
2. `REJECTED` requires a *definitive* rejection code (AX-02 §8). Everything else is `UNKNOWN`
   (explicitly including HTTP 5XX, whose execution status the venue documents as unknown `[V-DOC]`).
3. On `UNKNOWN`: no new risk-increasing intent for that instrument until resolution; risk-reducing
   actions (protection, exit) remain permitted *only* through the conservative branch of §5.3.

### 5.2 Resolution ladder (`AX-08:§5.2`)

1. `GET /api/v1/futures/order?origClientOrderId=<id>` (weight 1) up to `P-EXE-010` times with backoff
   (1 s, 2 s, 4 s, capped), total window `P-EXE-011` s.
2. If found ⇒ adopt the venue's state. If the venue reports `FILLED`/`PARTIALLY_FILLED` ⇒ proceed to
   protection (§6) using the **actual** filled quantity.
3. If not found, query `openOrders` for the instrument (weight 1) and the current `positions`.
4. Decision table:

| Query results | Adopted state | Action |
|---|---|---|
| order exists, working | `RESOLVED_WORKING` | if the intent was an entry, either keep (if still valid under §3.4) or cancel; protection is placed only after fill |
| order exists, filled (any part) | `RESOLVED_FILLED` | protect immediately, reconcile, journal |
| not found, position unchanged, working orders unchanged | `RESOLVED_ABSENT` | re-derive the decision from a fresh snapshot (a **new** intent with a **new** key) or abandon |
| not found, but position/orders changed vs the pre-send snapshot | `RESOLVED_ESCALATED` | treat as executed; adopt the position; protection; `SEV-2` incident with full evidence |
| queries fail entirely (venue unreachable) | `UNKNOWN` | retry the ladder; meanwhile place **no** new risk; if positions are open and unprotected, enter the emergency protection path (§9) when connectivity returns |

5. Every resolution writes a `ResolutionRecord(intent_id, attempts, evidence_refs, adopted_state)` into
   the journal.

### 5.3 Conservative branch by intent class (`AX-08:§5.3`)

| Intent class | If unresolved |
|---|---|
| Entry (risk-increasing) | assume *possibly filled*: adopt the position, place protection sized to the venue-reported position, do not re-enter |
| Protection (risk-reducing) | re-place protection; duplicates are harmless (a second stop on a reduced position is capped by the venue's own position logic; we prefer redundancy here to a naked position) — and the duplicate is journaled |
| Exit/flatten | verify the position before repeating; if the position persists, repeat with a bounded aggressive-but-limited order; never send more exits than the position size |
| Cancel | repeat the cancel; `-1142`/`-1143`/`-2013` mean success in practice, and the state is confirmed by `openOrders` |
| Modify (stop revision) | treat as a fresh placement of the new stop and cancel the old one after confirming the new exists |

---

## 6. Protection management (`AX-08:§6`)

### 6.1 Placement (`AX-08:§6.1`)

After any fill that increases exposure:
1. Immediately (same cycle, no waiting for the next decision tick) issue the protective order:
   `POST /api/v1/futures/position/trading-stop` when the venue route supports the needed stop, else a
   `type=STOP` order with `triggerBy=MARK_PRICE` and `side` = the closing side (AX-02 §6.2).
2. Confirm by query (`GET /futures/order` for stop orders, or the position's TP/SL fields).
3. Journal `protection_state` ∈ {`NONE`, `PENDING`, `ACTIVE`, `FAILED`} with timestamps.

### 6.2 Quantity (`AX-08:§6.2`)

The protection quantity is always derived from the **venue-reported position**, never from our
arithmetic: partial fills, funding-induced adjustments, or a missed fill event would otherwise leave a
mismatch. If the venue position is larger than our intended size (ambiguity adoption), the protection
covers the full venue position and the excess is flagged for immediate review.

### 6.3 Updates (`AX-08:§6.3`)

On every stop revision (AX-07 §9.2): place the new stop, confirm it, cancel the old one, confirm the
cancel. If the new stop cannot be confirmed and the old one still exists, the old stop is retained and
the revision is abandoned (never a gap in protection).

### 6.4 Unprotected window (`AX-08:§6.4`)

The system maintains a gauge `unprotected_seconds` per position and a portfolio-level alert
`EV-EXEC-UNPROTECTED` when:
- `unprotected_seconds > P-EXE-003` (default 10 s) ⇒ `SEV-3`, continue with elevated monitoring;
- `> P-EXE-031` (default 60 s) ⇒ `SEV-2`; if the position notional exceeds
  `P-EXE-032` (default 2 R) ⇒ immediate flatten (the position is not considered insurable);
- protection placement fails with a definitive error (`-1165`, `-1194`, etc.) ⇒ treat as
  *protection impossible*: flatten immediately, do not retry the same construct
  (`AX-08:§6.4-R1`).

---

## 7. Reconciliation (`AX-08:§7`)

**Inputs:** journal-derived state (intents, adopts, fills) vs venue state (`positions`, `openOrders`,
`userTrades`, `balance`).

**Trigger points:** at boot; after every `UNKNOWN`; every `P-EXE-040` seconds (default 60); immediately
before the first new entry for an instrument that had any activity since the last reconciliation;
after any governor transition to a stricter state.

**Comparisons and tolerances:**

| Object | Comparison | Tolerance | Divergence class |
|---|---|---|---|
| Position quantity | exact equality after quantization | 0 | `DIV-QTY` (`SEV-2`) |
| Position entry price | absolute difference | `P-REC-001` ticks | `DIV-PRICE` (`SEV-3`) |
| Working orders | set equality by `client_order_id` | 0 | `DIV-ORDERS` (`SEV-2`) |
| Fills | every venue fill present in the journal (by `fill_id`) | 0 missing | `DIV-FILL` (`SEV-2`) |
| Balance/margin | our margin model vs venue's available/used margin | `P-REC-002` % of equity | `DIV-MARGIN` (`SEV-3`) |
| Leverage | `accountLeverage` vs intended | 0 | `DIV-LEV` (`SEV-2`) |
| Instrument status | universe rule vs venue status | 0 | `DIV-STATUS` (`SEV-2`) |

**Resolution law (`AX-08:§7-R1`):** the journal is never edited. A divergence produces an appended
`CorrectionEvent` citing the venue evidence (raw payload hash), the adopted value, and the cause if
known. Any `SEV-2` divergence stops new risk-increasing actions until the next full reconciliation
passes cleanly.

---

## 8. Execution-quality measurement (`AX-08:§8`)

For every order, the journal stores a decomposition (implementation shortfall):

```
IS = delay_cost + execution_cost + opportunity_cost
delay_cost       = (arrival_mid − decision_mid)/decision_mid · sign
execution_cost   = (fill_price − arrival_mid)/arrival_mid · sign
opportunity_cost = unfilled_fraction · (future_mid − decision_mid)/decision_mid · sign
```
Reported per instrument, size bucket, hour-of-day and model version (the standard "TCA" table).
Adverse selection is measured as the mid's move in the `P-EXE-050` seconds after each fill, signed
against our direction; a persistently negative value means we are paying for toxic flow and is treated
as a *model* problem (the forecast's horizon is too short for the market impact being paid).

**Promotion gate coupling:** a model version may not be promoted if its realised `execution_cost`
exceeds the cost model's `p75` band, or if its opportunity cost exceeds `P-EXE-051` of its gross edge
(AX-10 §4.3).

---

## 9. Emergency procedures (`AX-08:§9`)

**Flatten sequence (normative order):**
1. Freeze new risk (set an in-process flag; the journal records the trigger).
2. Cancel protective orders for the instrument (confirmed by query) — a stop firing during a flatten
   can otherwise double-close.
3. Cancel remaining working orders (confirmed).
4. Submit a bounded taker order for the **exact** venue position quantity, closing side, using the
   venue's taker construct (`type=LIMIT`, `priceType=MARKET`; if the instrument forbids it (`-1194`),
   a wide-but-bounded IOC limit at `P-EXE-060 · s` from mid).
5. Verify the position is flat; if a residual remains above the step size, repeat once (maximum two
   attempts) with the residual; if residual remains, escalate to the operator with the exact numbers.
6. Journal every step with raw payload hashes; raise `SEV-2` (or `SEV-1` if flatten failed).

**Bounded by design:** the whole sequence must complete within `P-EXE-061` seconds under normal venue
conditions; the simulator's `S-SCN-EMERG` scenario (AX-11 §7) verifies the timing and the idempotency.

**Cancellation sweep:** `DELETE /api/v1/futures/batchOrders` (symbol+side) is used for cleanliness
only, never as a substitute for confirmed cancels — because its scope with respect to protective orders
is an open question until `VCH-22` (AX-02 §11 `AMB-08`).

---

## 10. Identifiers and duplicate prevention (`AX-08:§10`)

- Key format and namespace: AX-03 §2.2. The key is bound to the *intent*, stored in the journal, and
  reused only for retries of the same unresolved intent.
- `-1141 ORDER_DUPLICATED` `[V-DOC]` is the venue-side guard; AXIOM treats it as *evidence the original
  exists* and resolves by query (§5.2), never by generating a new key.
- A new decision always produces a new key; key reuse across different intents is a defect detected at
  load time by a uniqueness check on the journal (`T-ID-002`).

---

## 11. Test obligations (`AX-08:§11`)

| Area | Tests |
|---|---|
| Order construction | `T-EXE-001` (price bound never exceeded), `T-EXE-002` (quantization direction), `T-EXE-003` (band/precision validators make venue rejections unreachable) |
| Cost | `T-COST-001` (call-graph: no submission without the gate), `T-COST-002` (upper estimator used), `T-COST-003` (funding sign/timing), `T-COST-004` (cost refit staleness widens the band) |
| Uncertainty | `T-AMB-001`…`T-AMB-006` — one per row of §5.2's decision table, each driven by a fault-injected transport (timeout, 5XX, reset, duplicate, lost ack) |
| Protection | `T-PROT-001` (placement within bound), `T-PROT-002` (quantity from venue), `T-PROT-003` (revision never gaps), `T-PROT-004` (protection-impossible ⇒ flatten) |
| Reconciliation | `T-RECON-001`…`T-RECON-007` — one per divergence class, asserting the absence of journal edits and the presence of a correction event |
| Emergency | `T-EMER-001` (sequence order), `T-EMER-002` (bounded retries), `T-EMER-003` (no double-close) |
| Quality metrics | `T-TCA-001` (decomposition identity holds), `T-TCA-002` (adverse-selection sign) |
