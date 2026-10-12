# AX-11 — Simulator, Paper Trading and Backtest Fidelity

**Status:** Normative.
**Upstream:** AX-02 (venue semantics), AX-03 (time/identity), AX-08 (cost, order constructs), AX-10 (protocol).
**Downstream:** AX-14 (gates), AX-16 (roadmap).

The simulator has exactly one job: **to be the same decision-maker as live, on a different execution
substrate**, and to be *conservative* wherever the truth is unknown. It is not a forecasting tool, and
its output is not evidence about the future (AX-00 §3, L4).

---

## 1. Two modes, one kernel (`AX-11:§1`)

| Mode | Data | Execution | Purpose |
|---|---|---|---|
| **Backtest** (`BACKTEST`) | historical L0/L1 replay | simulated venue | research, gate `L2` |
| **Paper** (`PAPER`) | live streams | simulated venue, *identical code path* | gate `L4`, operation rehearsals |
| **Shadow** (`SHADOW`) | live streams | none (no orders at all) | gate `L3`, decision logging |

The **decision kernel is the same object** in all three and in live (INV-5). Differences are injected
only through three seams (AX-01 §3.3): the tape source, the execution adapter, and the clock. A code
path that exists only in live or only in backtest is a defect (`T-PARITY-001`).

---

## 2. Market replay (`AX-11:§2`)

- **Ordering:** records are delivered in `(ingest_ts, ingest_seq)` order — the order in which they were
  *available*, not the order in which they happened (`event_ts` may be out of order; the kernel must be
  robust to that, exactly as it must be live).
- **Determinism:** the replay is single-threaded over a deterministic priority queue; ties break on
  `ingest_seq`. Repeating a replay must reproduce byte-identical decisions (`T-DET-001`).
- **Availability lags** (AX-03 §3.4) are enforced, so a backtest cannot use a bar that live could not
  have used at that moment. `T-PIT-003` asserts this by injecting a deliberately delayed record.
- **Warm-up:** the replay starts `P-SIM-001` bars before the evaluation window so that every `T1`
  feature has its declared `min_history` before the first decision; the warm-up window is excluded from
  performance statistics.

---

## 3. Execution substrate (`AX-11:§3`)

### 3.1 The five operations (`AX-11:§3.1`)

The simulated venue implements **the same five operations** the live adapter exposes:
`submit_order`, `cancel_order`, `query_order_state`, `query_open_positions`, `query_account_margin_health`.
Nothing else exists; the kernel cannot tell which implementation it holds (a *seam* assertion in the
type system, `T-SIM-001`).

### 3.2 Latency injection (`AX-11:§3.2`)

Each simulated call samples a latency from the measured distribution (`VCH-16`, refreshed by
`BENCH-06`), decomposed into `t_write`, `t_ack`, `t_fill_observe` (AX-08 §2). The sampled latencies are
recorded per simulated order so that the *decision latency* in the paper run matches live statistics;
without this, paper results systematically flatter the strategy.

### 3.3 Failure injection (`AX-11:§3.3`)

The substrate can emit the venue's failure vocabulary per a scenario profile: `-1006`, `-1007`, `-1021`,
`-1022`, `-1131`, `-1141`, `-1146`, `-1147`, HTTP 5XX, timeouts, connection resets, duplicate responses
and lost acknowledgements. **The ambiguity protocol (AX-08 §5) must run unchanged** in these scenarios;
that is the point of the injection (`T-AMB-SIM-*`).

---

## 4. Fill model (`AX-11:§4`)

### 4.1 Price basis (`AX-11:§4.1`)

Fills are computed against a **conservative path**, built from the finest available data:
trades and quotes when recorded (`HOT` tier), otherwise bars. The model is explicit that it cannot see
the queue, so it must not assume favourable queue position (A4).

### 4.2 Taker fills (`AX-11:§4.2`) — IOC (`LIMIT`+`IOC`, or `priceType=MARKET`)

Let the order be a buy at limit `p_l`, size `q`, submitted at replay time `t0` with injected latency
`Δ`. The order is evaluated against the price path in `[t0+Δ, t0+Δ+τ_order]` where `τ_order` is the
venue's order lifetime for IOC (treated as "immediate" and modelled as the next observable event):

1. **Cross test:** if the path's best ask (or trade price) ≤ `p_l`, the order crosses.
2. **Fill quantity:** the fill fraction is
   `φ = min(1, P-SIM-010 · D(p_l) / (q · price · f))`, where `D(p_l)` is the observed depth available at
   or better than `p_l` from the recorded book (or, without book data, the median `D1` from
   `F-D1`), and `P-SIM-010 ≤ 1` is a haircut (`[C]`, `CAL-SIM-01`, fitted so that simulated fill
   fractions do not exceed realised ones on our own live fills — *never* fitted the other way).
3. **Slippage:** the fill price is the worse of (a) the path price and (b) `p_l`, plus a slippage
   draw from the measured per-bucket distribution (AX-08 §3.3), capped so the fill never improves
   beyond the bucket's observed best.
4. **No fill:** if the cross test fails, the order is unfilled, which is a *result* (opportunity cost is
   recorded, AX-08 §8), not an error.

### 4.3 Intrabar path rule (`AX-11:§4.3`) — the conservative convention

When a bar contains both a stop and a target level, the simulator assumes the **adverse level is
reached first** (for a long: the stop before the target). When a bar contains a limit entry and a stop
level, the entry is assumed filled and then the stop is evaluated on the *same* bar's remaining range
(the conservative direction). This convention is versioned; changing it requires an ADR because it
changes every historical result (`AX-11:§4.3-R1`).
When only one level is inside the bar, no ambiguity exists. When the bar's open is beyond a stop level
(a gap-through), the stop fills at the bar's open plus the measured gap-slippage distribution — never at
the stop price (`[D]`: the common backtest bug of filling stops at their level in a gap is precisely
what makes simulated strategies untradeable).

### 4.4 Stop-trigger basis (`AX-11:§4.4`)

Stops are triggered by the same reference as live (`MARK_PRICE`, AX-07 §9.1). Because mark-price
history is coarser than last-price history, the simulator uses the recorded mark-price series when
available and, when unavailable, the bar's last price **minus** a penalty of `P-SIM-020` ticks, so that
the simulation is pessimistically biased rather than optimistically biased about stop timing.

### 4.5 Maker orders (`AX-11:§4.5`)

`POST_ONLY` orders cannot be simulated with acceptable fidelity: queue position is unknown, and our own
data records no order-book microstructure. The simulator models a maker order as *filled only if the
market trades through its price by at least `P-SIM-021` ticks*, and always reports
`maker_fidelity = LOW`. **Consequence:** no strategy whose edge depends on maker fills may be promoted
from backtest alone; its `L2` gate additionally requires paper-mode (`L4`) agreement before `L5`.

### 4.6 Fees, funding and other cash flows (`AX-11:§4.6`)

- Fees come from the recorded `commissionRate` **in force at the time** (the daily snapshots); if the
  history is missing, the simulation uses the *maximum* observed rate, never the current (optimistic)
  one.
- Funding is applied at the settled times and rates (`FundingSettlement`), with the sign convention
  verified by `VCH-25`; if a settlement's rate is missing, the current rate is used and the affected
  window is flagged `funding_imputed`.
- The margin/liquidation model mirrors AX-07 §8.2 with the tier in force; liquidation events are
  simulated at the venue's approximate rule, and a liquidation is always treated as a `SEV-1`-class
  event in the report (it means the risk model failed, not that the market moved).
- Open-order margin reservation uses the venue's `marginLocked` convention (AX-02 §6.3) when recorded.

---

## 5. Parity requirements (`AX-11:§5`)

### 5.1 Decision parity (`AX-11:§5.1`)

Given the same tape and the same artifact versions, the kernel must emit the *identical* decision stream
in replay and in live (`T-PARITY-002`): identical targets, identical refusals, identical reason codes.
Any difference is investigated as a defect before any result from that run is used.

### 5.2 Live-tape replay test (`AX-11:§5.2`)

Every `P-SIM-030` days, a recorded live window (including its actual venue responses and observed
latencies) is replayed and the decision stream is diffed against what live actually decided. This is
the mechanism behind gate `L3` (AX-10 §4) and the strongest available evidence that the simulator and
live agree about *decisions*.

### 5.3 Execution-parity caveat (`AX-11:§5.3`)

Execution cannot be replayed identically (fills depend on the real market). Therefore the design
separates: **decision parity is exact and testable; execution fidelity is statistical and measured**.
Reports must state both, never conflate them (`AX-11:§5.3-R1`).

---

## 6. Scenario suite (`AX-11:§6`)

Scenarios are versioned fixtures, each with an acceptance criterion; they are part of gate `G3`
(AX-14 §6):

| ID | Scenario | What it proves |
|---|---|---|
| `S-SCN-GAP` | a bar gaps through the stop with slippage | the loss model and the tail budget (AX-07 §9.1) survive |
| `S-SCN-CASCADE` | burst of trades + OI drop + funding spike | cascade features behave; stops and flatten path work under stress |
| `S-SCN-ILLIQ` | spread widens `P-SIM-040`×, depth collapses | the cost gate refuses; no size is forced into a dead book |
| `S-SCN-OUTAGE` | venue down for `P-SIM-041` minutes during an open position | protection remains venue-side; recovery reconciles |
| `S-SCN-STALE` | a data series stops updating | `QC-07` fires; `no-new-risk`; refusal ledger shows why |
| `S-SCN-RATESTORM` | 429/`-1003` storm | backoff and priority classes behave; P0 never starves |
| `S-SCN-CLOCK` | clock skew beyond `P-VEN-001` | `RK-06` refuses; `-1021` handled without order loss |
| `S-SCN-KILLDRILL` | operator kill, then `K1`, then `K3` | kill idempotency, priority order, escalation, recovery |
| `S-SCN-DEADMAN` | process killed with open positions | venue stops remain; boot reconciliation correct |

---

## 7. Reporting (`AX-11:§7`)

Every backtest/paper report contains: the version stamp (AX-03 §6), evidence class, the trial ledger
context (AX-10 §7), the cost decomposition (fees/spread/slippage/funding), turnover and `N_bets`,
drawdown distribution and its `q95/q99`, the DSR/PSR/PBO inputs, the strategy's capacity curve
(performance versus notional, computed by re-running with scaled sizes and the measured impact model),
the scenario-suite results, and an explicit **limitations** section listing §4.5, §5.3 and any injected
simplification. A report missing any of these is not evidence (`T-SIM-002`).

**Over-claiming is a defect**: a report that describes simulated results in language suggesting live
performance violates `AX-11:§7-R1` and is rejected at gate review.
