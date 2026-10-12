# AX-15 — Parameter Registry, Calibration Map and Owner Inputs

**Status:** Normative. This document is the **single authority** for every tunable number in the system.
**Upstream:** every document that uses a parameter.
**Downstream:** `contracts/config.default.yaml`, the calibration jobs, gate `G0` (`T-CFG-001`, `T-PROV-002`).

**Rule (`AX-15:§0-R1`):** a number that appears in code, config or a document without an entry here is a
defect. The loader refuses unknown keys; the linter greps the codebase for numeric literals in
decision paths and requires a registry id (`T-ARCH-005`).

---

## 1. Parameter record schema (`AX-15:§1`)

Every entry has:

| Field | Meaning |
|---|---|
| `id` | stable id (`P-<FAMILY>-<nnn>`) |
| `family` | owning plane |
| `meaning` | one sentence |
| `unit` | unit and sign convention |
| `class` | `V` venue truth · `D` derived · `C` calibrated · `O` owner policy |
| `default_or_source` | a default for `D`/`C` (and the calibration id), or `OI-*` for `O` |
| `range` | admissible range enforced by the loader |
| `change control` | AX-12 §8 class |
| `cited by` | documents/clauses that use it |

`[V]` entries do not appear in the config file at all: they live in `venue_profile.json`, produced by the
conformance harness (AX-02 §10). `[D]` entries are derived constants (usually dimensionless); changing
one is a design change (ADR). `[C]` entries carry a `calibration_ref`; without it the loader refuses.
`[O]` entries come from §9.

---

## 2. Venue-truth parameters (`AX-15:§2`)

Produced by the harness, never configured by hand: `V-TICK`, `V-STEP`, `V-MINN`, `V-FEE`, `V-FUNDPER`,
`V-LEVG`, `V-BAND`, `V-PRICE-FILTER`, `V-RATE-HEADERS`, `V-WS-HEARTBEAT`, `V-DEPTH-VERSION`,
`V-RATELIMIT`, plus every `VCH` probe result and the `AMB` status flags. Their *use* is governed by
AX-02 §1 (source-tag precedence). Any document referencing `[V-PROBE]` means "the harness's latest
value, within its validity window".

---

## 3. Data-plane parameters (`AX-15:§3`)

| id | meaning | unit | class | default / source | range | change control |
|---|---|---|---|---|---|---|
| `P-DATA-001` | hot-tier depth snapshot cadence | s | C → `CAL-DATA-01` | 60 | 30–300 | `[C]` |
| `P-DATA-002` | warm-tier aggregate cadence | s | C | 60 | 30–300 | `[C]` |
| `P-DATA-003` | bar-close grace (also `P-DATA-012`) | s | C | 5 | 2–30 | `[C]` |
| `P-DATA-004` | staleness multiplier `k` (acceptance `≤ k·bar`) | – | C | 2 | 1.5–4 | `[C]` |
| `P-DATA-005` | WS heartbeat interval | s | V-adjacent `[V-DOC]` | 20 | — | `[V]` |
| `P-DATA-006` | reconnect backoff schedule | s | D | 1,2,4,8,15,30 cap | — | ADR |
| `P-DATA-007` | gap-repair history horizon for trades | bars | V-limited `[V-DOC]` | 60 | — | `[V]` |
| `P-DATA-008` | kline page size for repair | – | V `[V-DOC]` | 1000 | — | `[V]` |
| `P-DATA-009` | L0 segment rotation size | MB | D | 256 | 64–1024 | ADR |
| `P-DATA-010` | journal `fsync` policy | – | D | per-event | — | ADR |
| `P-DATA-011` | retention: hot | days | O → `OI-CAP-02` | 30 | 7–180 | `[O]` |
| `P-DATA-013` | retention: warm | days | O → `OI-CAP-02` | 730 | 180–3650 | `[O]` |
| `P-DATA-014` | capacity guard free-space floor | % | O | 15 | 5–40 | `[O]` |
| `P-DATA-020`… | per-gate thresholds `QC-01`…`QC-20` | mixed | C | see AX-04 §3 table | — | `[C]` |
| `P-UNI-001` | max instruments in the universe | – | O → `OI-CAP-01` | 30 | 1–200 | `[O]` |
| `P-UNI-002` | minimum completed bars before eligibility | bars | C | 500 | 200–5000 | `[C]` |
| `P-UNI-003` | minimum days since listing | days | C | 30 | 7–180 | `[C]` |
| `P-UNI-004` | minimum median daily quote volume | USDT | C | 5 000 000 | 1e5–1e8 | `[C]` |
| `P-UNI-005` | maximum median spread | bps | C | 8 | 1–50 | `[C]` |
| `P-UNI-006` | participation cap (`MPN ≤ c·MQV`) | fraction | C | 0.05 | 0.005–0.1 | `[C]` |
| `P-UNI-007` | cluster concentration cap | fraction | C | 0.40 | 0.1–0.6 | `[C]` |
| `P-UNI-008` | universe refresh time (UTC) | hh:mm | D | 00:05 | — | ADR |

---

## 4. Signal and admission parameters (`AX-15:§4`)

| id | meaning | class | default | range |
|---|---|---|---|---|
| `P-ADM-001` | maximum FDR (Benjamini–Hochberg) for the feature family | O | 0.10 | 0.01–0.25 |
| `P-ADM-002` | minimum out-of-sample IC (absolute) for admission | C | 0.02 | 0.005–0.1 |
| `P-ADM-003` | cost-stress multipliers applied to the cost model | D | {+50 %, ×1.5} | — |
| `P-ADM-004` | minimum regime subsets with the same sign | D | 3 of 4 | — |
| `P-ADM-005` | Fisher-z sample-size gate | C | see AX-05 §2.4 | — |
| `P-VOL-001` | EWMA half-life (returns vol) | C → `CAL-VOL-01` | 30 bars | 10–120 |
| `P-VOL-002` | HAR-RV window set | D | {1, 5, 22} | — |
| `P-VOL-003` | volatility percentile lookback | C | 500 bars | 200–2000 |
| `P-LIQ-001` | depth window for `F-D1` | D | top 5 levels | — |
| `P-LIQ-002` | spread EWMA half-life | C → `CAL-CST?` | 50 | 10–200 |
| `P-LIQ-003` | Kyle-λ estimation window | C → `CAL-CST-01` | 200 trades | 50–2000 |
| `P-FLOW-001` | taker-imbalance window | D | 1 bar | — |
| `P-FLOW-002` | OI quad classification thresholds | C | deciles | — |
| `P-FLOW-003` | funding-stress percentile | C → `CAL-GOV-01` | q99 | — |
| `P-XS-001` | cross-sectional ranking window | C | 20 bars | 5–200 |
| `P-XS-002` | minimum cross-sectional breadth | D | 5 instruments | — |
| `P-MON-001` | PSI window and breach threshold | C | 30 d / 0.25 | — |
| `P-MON-002` | minimum rolling IC posterior for retention | C → `CAL-GOV-01` | q5 | — |
| `P-MON-003` | feature availability floor | C | 0.90 | 0.5–1.0 |
| `P-FEAT-001` | scaling window | D | 500 bars | — |
| `P-FEAT-002` | clipping sigma | D | 5 | — |
| `P-FEAT-003` | winsorization fraction | D | 0.005 | — |

---

## 5. Forecast and model parameters (`AX-15:§5`)

| id | meaning | class | default | range |
|---|---|---|---|---|
| `P-FCT-001` | horizons (bars) | O → `OI-RISK-03` | {1, 4, 16} | ≥ 1 |
| `P-FCT-002` | ridge `λ` | C → `CAL-LBL-01` | 1.0 | 1e-3–1e3 |
| `P-FCT-003` | HAC lag length | D | `≈ 1.5·H` | — |
| `P-FCT-004` | bootstrap replications (block) | D | 2000 | — |
| `P-FCT-005` | block length for bootstrap | D | `2·H` | — |
| `P-FCT-006` | `p_net` floor for a trade | O | 0.55 | 0.5–0.9 |
| `P-FCT-007` | `M_eff` floor | D | 1.2 | — |
| `P-FCT-008` | weight clip (combination) | D | 0.6 | — |
| `P-FCT-009` | `z` for the edge lower bound | O | 1.0 | 0–2 |
| `P-FCT-010` | isotonic calibration minimum sample | C | 500 | — |
| `P-CAL-001` | calibration refit cadence | D | weekly | — |
| `P-CAL-002` | Brier skill floor | C → `CAL-LBL-01` | 0.02 | 0–0.1 |
| `P-CAL-003` | sharpness floor | C | reported | — |
| `P-REG-001` | HMM states `K` | D | ≤ 4 | — |
| `P-REG-002` | regime entropy gate | C → `CAL-REG-01` | 0.8 | 0.5–1.0 |
| `P-REG-003` | CUSUM drift parameter | C | see AX-06 §6.3 | — |
| `P-REG-004` | CUSUM threshold | C → `CAL-GOV-01` | q99 | — |
| `P-REG-005` | regime multiplier floor | D | 0.4 | — |

---

## 6. Risk and sizing parameters (`AX-15:§6`)

| id | meaning | class | default / source | range |
|---|---|---|---|---|
| `P-RSK-001` | `R_fraction` (risk per trade) | O → `OI-RISK-01` | 0.005 | 0.001–0.02 |
| `P-RSK-002` | `D_max` (max drawdown before hard de-risk) | O → `OI-RISK-02` | 0.15 | 0.03–0.30 |
| `P-RSK-003` | `k_D` (drawdown-to-risk conversion) | D | 1.5 | — |
| `P-RSK-004` | `N_bets` estimate (trades/day) | C → `CAL-RSK-01` | 6 | 1–50 |
| `P-RSK-005` | `R` floor (min-notional feasibility) | D | see AX-07 §3.2 | — |
| `P-RSK-006` | daily loss cap | O → `OI-RISK-04` | 0.04 | 0.01–0.10 |
| `P-RSK-007` | volatility target (annualised) | O → `OI-RISK-03` | 0.20 | 0.05–0.60 |
| `P-RSK-008` | `g_max` (max gross) | O | 2.0 | 1–5 |
| `P-RSK-009` | risk-aversion `γ` | D | 2.0 | — |
| `P-RSK-010` | covariance EWMA half-life | C → `CAL-RSK-01` | 60 d | 10–250 |
| `P-RSK-011` | Ledoit–Wolf shrinkage intensity | D (computed) | data-driven | — |
| `P-RSK-012` | MP denoising eigenvalue floor | D | `q` from `T/N` | — |
| `P-RSK-013` | cluster count rule | D | `√(N/2)` | — |
| `P-RSK-014` | `1/N` shrinkage toward inverse-variance | C | 0.5 | 0–1 |
| `P-RSK-020` | no-trade band width (× cost) | C → `CAL-CST-01` | 1.0 | 0.5–3 |
| `P-RSK-021` | turnover cap per day | O | 1.0× gross | 0.1–3 |
| `P-RSK-022` | surplus ranking tolerance | D | 1e-6 | — |
| `P-RSK-030` | `gross_cap` `G` | O | 2.0 | 1–5 |
| `P-RSK-031` | `net_cap` `N_net` | O | 1.0 | 0.2–3 |
| `P-RSK-032` | per-instrument cap | C | 0.25 | 0.05–0.5 |
| `P-RSK-033` | cluster cap | C | 0.40 | 0.1–0.6 |
| `P-RSK-034` | portfolio beta cap | O | 0.5 | 0–1.5 |
| `P-RSK-041` | participation cap (`MQV`) | C | 0.05 | 0.005–0.1 |
| `P-RSK-042` | participation cap (`D1`) | C | 0.10 | 0.01–0.2 |
| `P-RSK-043` | maximum exit time | min | C | 2 | 0.5–15 |
| `P-RSK-050` | Kelly fraction | O | 0.25 | 0.05–0.5 |
| `P-RSK-051` | Kelly LCB confidence factor | C → `CAL-MRG-01` | 0.6 | 0.3–0.9 |
| `P-RSK-060` | `k_safe` (liquidation-distance multiple) | C → `CAL-MRG-01` | 3.0 | 1.5–8 |
| `P-RSK-061` | `c_sigma` (stop σ multiple) | C → `CAL-STP-01` | 2.5 | 1.5–5 |
| `P-RSK-062` | `c_cost` (stop cost multiple) | C → `CAL-STP-01` | 3.0 | 1.5–6 |
| `P-RSK-063` | tail quantile `q_tail` | C → `CAL-STP-01` | 0.995 | 0.99–0.9999 |
| `P-RSK-064` | tail multiplier cap (gap term) | O → `OI-RISK-05` | 2.0 | 1–5 |
| `P-RSK-070` | max open positions | O | 8 | 1–30 |
| `P-RSK-071` | per-position risk share cap | D | 0.5 | — |
| `P-MRG-001` | margin utilisation cap | O | 0.50 | 0.1–0.9 |
| `P-MRG-002` | margin health warn/critical levels | D | 0.30 / 0.15 | — |
| `P-MRG-003` | leverage readback required | D | true | — |

---

## 7. Execution, cost and governor parameters (`AX-15:§7`)

| id | meaning | class | default / source | range |
|---|---|---|---|---|
| `P-COST-001` | funding-deferral decision fraction | C → `CAL-CST-01` | 0.25 | 0.05–0.5 |
| `P-COST-010` | cost upper-estimator quantile | C → `CAL-CST-01` | 0.75 | 0.5–0.99 |
| `P-COST-011` | minimum cost sample for refit | D | 100 fills | 30–1000 |
| `P-COST-020` | `z_g` (gate margin on the edge) | O | 1.0 | 0–2 |
| `P-COST-021` | `m_c` (cost uncertainty multiple) | O | 1.0 | 0–3 |
| `P-COST-030` | consecutive sessions above the band before `K5` | D | 5 | 2–20 |
| `P-EXE-001` | cross factor `k_x` | C → `CAL-EXE-02` | 0.25 | 0–2 |
| `P-EXE-002` | tick slack on crossing | D | 2 ticks | — |
| `P-EXE-003` | protection bound | C → `CAL-EXE-01` | 10 s | 5–60 |
| `P-EXE-005` | maximum attempts per intent | D | 2 | 1–5 |
| `P-EXE-010` | resolution query attempts | D | 5 | 1–10 |
| `P-EXE-011` | resolution window | s | D | 60 | 10–300 |
| `P-EXE-020` | slicing threshold (× MQV) | C → `CAL-EXE-03` | 0.05 | 0.01–0.2 |
| `P-EXE-021` | slice spacing | s | C → `CAL-EXE-03` | 15 | 5–120 |
| `P-EXE-022` | order deadline | min | D | 5 | 1–30 |
| `P-EXE-031` | unprotected escalation | s | D | 60 | 15–300 |
| `P-EXE-032` | unprotected flatten threshold | × R | D | 2 | 1–5 |
| `P-EXE-040` | max working orders per instrument | D | 3 | 1–8 |
| `P-EXE-041` | max new positions per minute | O | 4 | 1–20 |
| `P-EXE-050` | adverse-selection measurement window | s | D | 120 | 10–900 |
| `P-EXE-051` | opportunity-cost allowance | O | 0.25 | 0.05–0.5 |
| `P-EXE-060` | emergency limit offset | × spread | D | 5 | 2–50 |
| `P-EXE-061` | flatten time budget | s | D | 30 | 10–180 |
| `P-VEN-001` | maximum tolerated clock offset | ms | V/C | 500 | 100–2000 |
| `P-GOV-001` | journal verification cadence | min | D | 10 | 1–120 |
| `P-GOV-002` | reconciliation freshness | s | D | 60 | 10–900 |
| `P-GOV-010` | stop tightening in `CAUTION` | % | D | 20 | 5–50 |
| `P-GOV-011` | min `p_net` for new positions in `REDUCED` | C | see §3.4 | — |
| `P-GOV-012` | max horizon in `REDUCED` | bars | D | 4 | 1–16 |
| `P-GOV-013` | % of gross closed in `DEFENSIVE` | D | 50 | 10–100 |
| `P-GOV-020`/`021` | health-driven instrument counts | D | 3 / 5 | — |
| `P-GOV-030` | funding-stress instrument count | D | 5 | — |
| `P-GOV-040` | dwell per state class | h | D | 24 / 1 | 1–168 |
| `P-GOV-041` | minimum time before any recovery | min | D | 30 | 5–240 |
| `P-GOV-050`/`051` | execution-quality multipliers | D | 0.7 / 0.5 | — |
| `P-GOV-060` | consecutive API failures for `K2` | D | 5 | 2–20 |
| `P-GOV-070` | `K6` trigger fraction | D | 0.5 | 0.1–0.9 |
| `P-GOV-080` | refusals in the status view | – | D | 20 | — |
| `P-GOV-081`–`083` | escalation timers | min | D | 5 / 15 / 30 | — |
| `P-GOV-090` | gap-loss multiple allowed by the tail budget | O | 2.0 | 1–5 |
| `P-GOV-091` | operator heartbeat expiry | h | O | 24 | 1–168 |

---

## 8. Learning, simulation and operations parameters (`AX-15:§8`)

| id | meaning | class | default | range |
|---|---|---|---|---|
| `P-LRN-001` | embargo width | bars | D | `max(H, P-LRN-002)` | — |
| `P-LRN-002` | minimum embargo | bars | D | 50 | — |
| `P-LRN-003` | walk-forward step | bars | C | 500 | — |
| `P-LRN-004` | SPA bootstrap replications | D | 5000 | — |
| `P-LRN-005` | required `PSR(SR*)` | O | 0.95 | 0.9–0.999 |
| `P-LRN-006` | CSCV blocks | D | 16 | — |
| `P-LRN-007` | maximum `PBO` | O | 0.5 | 0.1–0.7 |
| `P-LRN-010` | minimum regime subsets with the same sign | D | 3 of 4 | — |
| `P-LRN-011` | shadow duration | O | 14 d | 7–90 |
| `P-LRN-012` | paper duration | O | 21 d | 14–120 |
| `P-LRN-013` | allowed simulator-vs-model cost gap | C | 0.3 | 0.1–1.0 |
| `P-LRN-014` | minimum simulated round trips (paper) | C | 30 | 10–500 |
| `P-LRN-015` | maximum cost-gate refusal rate to stay promoted | C | 0.98 | — |
| `P-LRN-016` | micro-live fraction | O | 0.10 | 0.02–0.5 |
| `P-LRN-017` | clean-reconciliation days before micro-live | O | 5 | 3–30 |
| `P-LRN-018`/`019` | minimum trades at `L5`/`L6` | C | 20 / 60 | — |
| `P-LRN-020` | live DSR floor for scaling | O | 0.95 | — |
| `P-LRN-021` | monthly `SEV-2` budget | O | 2 | 0–10 |
| `P-LRN-030` | demotion `PSR` floor | O | 0.90 | — |
| `P-LRN-031` | max unresolved `SEV-1` age | O | 7 d | 1–30 |
| `P-LRN-040` | champion review cadence | O | monthly | — |
| `P-LRN-050` | `N_bets` deviation tolerance | C | 0.5 | 0.2–1.0 |
| `P-LRN-060` | monthly hypothesis cap | O | 12 | 1–50 |
| `P-LRN-070` | post-retirement monitoring | D | 90 d | — |
| `P-SIM-001` | warm-up bars | D | max feature `min_history` + 10 % | — |
| `P-SIM-010` | fill-fraction haircut | C → `CAL-SIM-01` | 0.8 | 0.3–1.0 |
| `P-SIM-020` | mark-price proxy penalty | ticks | D | 2 | 0–10 |
| `P-SIM-021` | maker trade-through requirement | ticks | D | 1 | 1–5 |
| `P-SIM-030` | live-tape replay cadence | d | D | 14 | 7–90 |
| `P-SIM-040` | illiquidity scenario spread multiple | – | D | 5 | — |
| `P-SIM-041` | outage scenario duration | min | D | 30 | — |
| `P-OPS-001` | days the live loop must work standalone | d | O | 30 | 7–365 |
| `P-OPS-010`…`014` | benchmark criteria `BENCH-01`…`07` | mixed | O/C | see AX-12 §2 | — |
| `P-OPS-020`–`023` | supervisor backoff/restart/heartbeat | mixed | D | — | — |
| `P-OPS-030` | maximum lateness before a cycle is skipped | s | D | 5 | — |
| `P-OPS-040`–`043` | RPO/RTO and backup locations | mixed | O | — | — |
| `P-OPS-050` | refusals in the status view | – | D | 20 | — |
| `P-OPS-060`/`061` | paper-soak days / live-verify hours | mixed | O | 7 / 72 | — |
| `P-OPS-070` | parameter cooling-off delay | h | O | 1 | 0–24 |
| `P-OPS-080` | telemetry retention | d | D | 90 | — |
| `P-OPS-090` | postmortem deadline | d | O | 3 | 1–14 |
| `P-OPS-100`–`102` | notification/manual-action limits | mixed | O | see AX-12 §11 | — |
| `P-SEC-001` | key rotation interval | d | O | 90 | 30–365 |
| `P-TST-001`/`002`/`003`/`004` | evidence expiry and coverage/mutation floors | mixed | O/D | 30 d / 3 mo / 85 % / 1 per module | — |

---

## 9. Owner inputs (`AX-15:§9`) — the only numbers the owner must supply

Each is a **decision**, not a preference; the system cannot invent them and must stay `OFF` without
them (AX-00 §6). For each: what it is, why it cannot be derived, the admissible range, and what breaks
if it is wrong.

| id | input | why the system cannot decide it | range | effect of a wrong value |
|---|---|---|---|---|
| `OI-RISK-01` | `R_fraction` (fraction of equity risked per trade; drives `R`) | it is the owner's risk appetite; the mathematics can only say what follows | 0.001–0.02 | too high ⇒ ruin risk rises as `R²`-ish through the drawdown path; too low ⇒ the min-notional floor makes trading impossible and the system will (correctly) refuse everything |
| `OI-RISK-02` | `D_max` (drawdown at which the system must hard de-risk) | a preference about pain, not a measurable fact | 0.03–0.30 | too high ⇒ survivable capital loss; too low ⇒ the system de-risks during normal noise and never compounds |
| `OI-RISK-03` | volatility target and horizons (annualised vol budget; which horizons are admissible) | maps to the owner's tolerance of equity swings and to the effort of monitoring | vol 0.05–0.60; horizons from {1,4,16} bars (≥15 min) | inconsistent with `D_max` ⇒ permanent `CAUTION` (the governor will say so explicitly) |
| `OI-RISK-04` | `daily_loss_cap` | an operational pain threshold; also bounds how often the owner must look | 0.01–0.10 | too high ⇒ large single days; too low ⇒ the day stops after one normal loss |
| `OI-RISK-05` | tail multiplier (how much worse than `R` a gap-only loss may be without changing the design) | a statement about acceptable worst cases | 1–5 | too low ⇒ the tail budget refuses most instruments (correctly, but maybe not what the owner wants) |
| `OI-CAP-01` | maximum universe size (how many instruments may be traded simultaneously) | depends on the owner's capital and attention | 1–200 | with a large universe and small capital, the min-notional floor binds and the system refuses most signals |
| `OI-CAP-02` | retention and storage budget (how much history to keep; where) | a resource decision outside the system's knowledge | as §3 | too small ⇒ repair becomes impossible and research is limited |
| `OI-OPS-01` | the deployment topology (A/B/C of AX-12 §1) and the machine that will run the live loop | facts about the owner's life and hardware | A/B/C | choosing A without passing the benchmarks forces the system to disable capabilities and say so |
| `OI-OPS-02` | the notification destination (channel + address) for `SEV-1/2` and daily digests | private information | — | without it, no `LIVE` (an unattended live system cannot notify anyone) |
| `OI-OPS-03` | the review cadence the owner commits to (daily/weekly/monthly obligations) | a commitment, not a parameter | — | the monitoring design assumes a daily glance and a weekly read; if unmet, the system's automatic protections still hold, but demotion/promotion decisions stall |
| `OI-GOV-01` | who may issue `arm`, promotions and `kill hard` (and whether a second person exists for dual control) | an authority question | — | with one person, dual control is unavailable and the design's friction (cooling-off, two-step confirms) is the only substitute — this must be recorded, not assumed |

`OI-*` values are recorded in the journal (`EV-PARAM-CHANGE`, class `O`) with the owner's identifier and
a reason string. A change to `OI-RISK-*` requires the two-step confirmation of AX-12 §8.

---

## 10. Calibration jobs (`AX-15:§10`)

| id | job | inputs | outputs | cadence | gate |
|---|---|---|---|---|---|
| `CAL-DATA-01` | sampling/threshold calibration for `QC` gates | recorded archive + clean-operation baseline | `P-DATA-020…`, `P-DATA-004` | quarterly | `G1` |
| `CAL-VOL-01` | vol-model half-lives and percentile windows | archive | `P-VOL-001/003` | quarterly | `G1` |
| `CAL-LBL-01` | label/calibration parameters (ridge `λ`, Brier floor) | dataset + OOS folds | `P-FCT-002`, `P-CAL-002` | per promotion | `G3` |
| `CAL-RSK-01` | `N_bets`, covariance half-life, caps | paper/live ledger | `P-RSK-004`, `P-RSK-010` | monthly | `G4` |
| `CAL-MRG-01` | Kelly LCB factor, `k_safe` | fill/vol/liq data | `P-RSK-051`, `P-RSK-060` | quarterly | `G4` |
| `CAL-STP-01` | stop multiples and tail quantile | fills + tail fits | `P-RSK-061…063` | quarterly | `G4` |
| `CAL-CST-01` | cost model + slippage buckets + Kyle-λ | own fills ledger | `P-COST-*`, `P-RSK-020`, `P-LIQ-003` | weekly | `G4`/`G5` |
| `CAL-EXE-01` | protection bound from measured `t_prot` | venue timings | `P-EXE-003` | monthly | `G5` |
| `CAL-EXE-02` | cross factor `k_x` | fills | `P-EXE-001` | monthly | `G4` |
| `CAL-EXE-03` | slicing threshold/spacing | fills + impact model | `P-EXE-020/021` | quarterly | `G4` |
| `CAL-GOV-01` | all governor thresholds | null distributions (§AX-09 §4.1) | `P-GOV-*`, `P-MON-002`, `P-REG-004`, `P-FLOW-003` | quarterly | `G4` |
| `CAL-REG-01` | regime-model parameters (entropy gate, CUSUM drift) | archive replay + filtered-state diagnostics | `P-REG-002`, `P-REG-003` | quarterly | `G3`/`G4` |
| `CAL-FLOW-01` | flow-feature normalisation (OI-change quadrant boundaries) | archive | `P-FLOW-002` | quarterly | `G1` |
| `CAL-SIM-01` | simulation haircut, fill fractions | live vs simulated | `P-SIM-010`, `P-LRN-013/014` | per promotion | `G2` |

Each calibration writes a `CalibrationRecord(job_id, inputs_hash, method_version, outputs, metrics,
ts)` and its results are applied only through the parameter change process of AX-12 §8.

---

## 11. Registry maintenance (`AX-15:§11`)

1. **Adding** a parameter: requires an ADR if it changes behaviour; the entry must specify all §1
   fields; the config schema and the loader are updated in the same change (`T-CFG-001`).
2. **Removing**: only when the citing clause is removed by an ADR; the id is never reused
   (append-only namespace).
3. **Deprecation**: mark `deprecated`, keep the value in the deployment ledger of past runs so old
   results remain interpretable.
4. **Audit**: monthly, the registry is diffed against the code's numeric literals and the config
   schema; drift is a blocking defect (`T-ARCH-005`).

---

## 12. Contract-level appendix (`AX-15:§12`)

Sections 3–8 group the parameters by plane for human reading. The **complete, authoritative** list is
`contracts/registry.json`, generated by `contracts/build_registry.py` from a single table (the generator
also emits `contracts/config.default.yaml`; `python3 contracts/build_registry.py --check` fails if the
two artifacts drift from the table, and the same check rejects a class-`V` value in the config).

The ids below are the ones introduced directly by the contract layer (operational, structural, or
granular splits of a parameter that the plane tables describe as a single row). Each is a first-class
registry entry with a class, a range and a change-control path; none of them may appear as a literal in
code (AX-15 §0-R1, `T-ARCH-005`).

| id | config path | class | unit | meaning |
|---|---|---|---|---|
| `P-COST-012` | `cost.slip_buckets_mqv` | D | list[fraction] | slippage bucket boundaries |
| `P-DATA-021` | `data.health_gate_ids` | D | list | gates that can move an instrument to FAIL |
| `P-EXE-070` | `execution.taker_only` | D | bool | ADR-009: post-only disabled by policy |
| `P-EXE-071` | `execution.allow_post_only` | D | bool | enabling requires a Class-3 ADR |
| `P-FEAT-010` | `features.enabled_t1` | D | list[str] | T1 family (AX-05 §3) |
| `P-FEAT-011` | `features.enabled_t2` | D | list[str] | T2 family |
| `P-FEAT-012` | `features.enabled_t3` | D | list[str] | T3 / research-only |
| `P-GOV-021` | `governor.health_fail_defensive` | D | count | instruments in FAIL before DEFENSIVE |
| `P-GOV-051` | `governor.exec_multiplier_stale` | D | fraction | m_exec when the cost model is stale |
| `P-GOV-100` | `governor.caution_q` | C | quantile | CAUTION trigger quantile |
| `P-GOV-101` | `governor.reduced_q` | C | quantile | REDUCED trigger quantile |
| `P-GOV-102` | `governor.defensive_q` | C | quantile | DEFENSIVE trigger quantile |
| `P-GOV-103` | `governor.multipliers` | D | map | m_gov by state (AX-09 §3) |
| `P-LRN-008` | `learning.folds` | D | count | purged K-fold count |
| `P-LRN-019` | `learning.min_trades_l6` | C | count | trades required at L6 |
| `P-META-000` | `meta.schema_version` | D | int | contract schema version |
| `P-META-001` | `meta.env` | D | enum | RESEARCH|BACKTEST|SHADOW|PAPER|PROBE|MICRO_LIVE|LIVE (AX-01 §6.1) |
| `P-META-002` | `meta.profile` | D | str | selects the VenueProfile artifact |
| `P-MON-004` | `features.psi_breach` | C | index | PSI breach level |
| `P-MRG-004` | `risk.margin_health_critical` | D | fraction | margin-health critical level |
| `P-OPS-021` | `ops.crash_loop_restarts` | D | count | restarts within the window that force OFF |
| `P-OPS-022` | `ops.crash_loop_window_min` | D | min | crash-loop window |
| `P-OPS-023` | `ops.heartbeat_s` | D | s | watchdog heartbeat |
| `P-OPS-031` | `ops.tick_s` | C | s | decision cadence (bar-aligned); equals the smallest horizon bar length |
| `P-OPS-043` | `ops.backup_locations` | O | list[path] | at least one off-device |
| `P-OPS-061` | `ops.live_verify_hours` | O | h | post-deploy live verification window |
| `P-OPS-101` | `ops.max_manual_actions_per_hour` | O | count | friction against impulsive intervention |
| `P-OPS-102` | `ops.max_manual_change_r` | O | R | a manual action may not exceed this risk |
| `P-OPS-110` | `ops.log_level` | D | enum | DEBUG|INFO|WARN|ERROR |
| `P-OPS-120` | `ops.notify_channel` | O | enum | telegram|console|email|none |
| `P-OPS-121` | `ops.notify_destination_ref` | O | secret-ref | identifier resolved from the secret store; never a literal in this file |
| `P-OPS-130` | `ops.topology` | O | enum | A single-node | B edge+compute | C server |
| `P-OPS-131` | `ops.single_writer_lock` | D | path | prevents a second live instance |
| `P-RSK-080` | `risk.pretrade_check_order` | D | list[str] | normative order (AX-09 §2) |
| `P-SEC-010` | `security.require_ip_whitelist` | D | bool | venue rejects unbound keys (-1023) [V-DOC] |
| `P-SEC-011` | `security.forbidden_permissions` | D | list[str] | must be impossible on the API key |
| `P-SIM-011` | `learning.intrabar_rule` | D | enum | changing this requires an ADR (AX-11 §4.3) |
| `P-TST-002` | `tests.statistical_evidence_months` | D | months | G3 evidence expiry |
| `P-TST-003` | `tests.coverage_floor_pct` | O | % | branch coverage floor on decision-critical packages |
| `P-TST-004` | `tests.mutation_per_module` | D | count | surviving mutants per module fail the build |
| `P-VEN-002` | `venue.f_safe` | D | fraction | fraction of the venue rate limit the system may use (AX-02 §7.1) |
| `P-VEN-003` | `venue.recv_window_ms` | D | ms | recvWindow actually sent; venue default documented as 5000 [V-DOC] |
| `P-VEN-004` | `venue.base_url` | D | url | structural API entry point; measurable venue facts live in venue_profile.json |
| `P-VEN-005` | `venue.ws_url` | D | url | market-data stream entry point (AX-02 §4) |
| `P-VEN-006` | `venue.profile_path` | D | path | produced by the conformance harness (AX-02 §10) |
| `P-VEN-007` | `venue.profile_max_age_hours` | C | h | older profile ⇒ RK-08 refuses |
| `P-VEN-008` | `venue.backoff_schedule_s` | D | list[s] | reconnect/retry backoff, capped (P-DATA-006) |

**Aliases and splits (`AX-15:§12-R1`):**

* `P-DATA-012` is a deprecated alias of `P-DATA-003` (bar-close grace); it exists only so that AX-04 §3's
  text remains readable. It must not appear in the config.
* `P-MRG-002` (margin-health warning) and `P-MRG-004` (margin-health critical) split the single row of §6
  because a registry entry maps one-to-one to one config key.
* `P-GOV-020`/`P-GOV-021`, `P-GOV-050`/`P-GOV-051`, `P-LRN-018`/`P-LRN-019`, `P-OPS-040`–`P-OPS-043` and
  `P-OPS-100`–`P-OPS-102` follow the same rule: one id per key, never a compound value.
* `P-UNI-007` (universe breadth, used at the daily freeze) and `P-RSK-033` (portfolio cluster cap, used at
  allocation) are deliberately distinct: the first decides what may be *eligible*, the second how much
  correlated risk may be *held*. Both must hold simultaneously.

**Verification (`AX-15:§12-R2`):** `T-CFG-001` asserts that the set of config paths equals the registry
map, that every class-`C` key has a resolvable `calibration_ref`, that every class-`O` key is either null
(system OFF) or accompanied by an `EV-PARAM-CHANGE` record, and that no class-`V` value is present.
