# AX-09 — Risk Governor, Kill Switches and Escalation

**Status:** Normative.
**Upstream:** AX-04 (health), AX-07 (limits), AX-08 (execution states).
**Downstream:** AX-10 (demotion), AX-12 (operator interface, runbooks), AX-14 (tests).

The governor (`rg`) is the **only** component allowed to override a decision downward, and it is the
only component that may keep the system alive when models, data or the venue misbehave. Its authority is
asymmetric by design (INV-9): it can always reduce risk, immediately and without evidence; it can never
increase it, no matter how convincing a signal looks.

---

## 1. Two layers (`AX-09:§1`)

| Layer | Cadence | Purpose | Failure mode addressed |
|---|---|---|---|
| **Risk kernel** (`RK`) | every candidate order, in-process, < 10 ms | hard, deterministic, fail-closed pre-trade checks | bad sizes, stale data, limit breaches, margin/liquidation risk, duplicate intents |
| **Governor** (`GOV`) | every decision tick + event-driven | slower-state machine over performance, health and quality; sets the risk multiplier and the system mode | regime change, model decay, venue degradation, drawdown, operational stress |

Both are **independent of alpha code** (INV-7): they cannot import forecast models, and the alpha code
cannot alter their parameters at runtime.

---

## 2. Risk kernel (`AX-09:§2`)

Evaluated **in order**; the first failure stops the order with a `Refusal` carrying the check id.

| # | Check | Condition to pass | On failure |
|---|---|---|---|
| `RK-01` | System mode | mode ∈ {`PAPER`, `MICRO_LIVE`, `LIVE`} and armed | refuse `MODE_BLOCKED` |
| `RK-02` | Kill state | no active `K1..K8` | refuse `KILL_ACTIVE` |
| `RK-03` | Governor state | state ∉ {`FLATTEN`, `HALT`} | refuse `GOV_BLOCKED` |
| `RK-04` | Instrument eligibility | in today's universe, `status = TRADING`, not API-forbidden, not removal-flagged | refuse `INSTRUMENT_INELIGIBLE` |
| `RK-05` | Data health | instrument health ∈ {`OK`, `WARN`} and all decision-critical series fresh | refuse `DATA_STALE` |
| `RK-06` | Clock | `abs(server_offset_ms) ≤ P-VEN-001` | refuse `CLOCK_SKEW` |
| `RK-07` | Journal integrity | hash chain verified within `P-GOV-001` minutes | refuse `JOURNAL_UNVERIFIED` |
| `RK-08` | Venue profile | blocking probes `PASSED`, profile not `STALE` | refuse `PROFILE_STALE` |
| `RK-09` | Reconciliation | last reconciliation clean within `P-GOV-002` seconds (and after all activity) | refuse `RECON_REQUIRED` |
| `RK-10` | Duplicate intent | the candidate key is unused | refuse `DUPLICATE_INTENT` |
| `RK-11` | Open positions cap | `open_positions < P-RSK-070` | refuse `POSITION_LIMIT` |
| `RK-12` | Per-trade risk | `qty·f·price·s_stop ≤ R·m_risk·P-RSK-071` | reduce size, else `RISK_CAP` |
| `RK-13` | Daily loss budget | realized + unrealized loss `< L_day` | refuse `DAILY_LOSS` (and the governor tightens) |
| `RK-14` | Gross/net exposure | within `G`, `N_net` | reduce, else `EXPOSURE_CAP` |
| `RK-15` | Cluster cap | cluster exposure within `C_c` | reduce, else `CLUSTER_CAP` |
| `RK-16` | Correlation cap | projected worst-case simultaneous loss (portfolio) within the tail budget | reduce, else `CORR_CAP` |
| `RK-17` | Margin utilisation | post-trade `Σ margin + reservations ≤ P-MRG-001·equity` | reduce, else `MARGIN_CAP` |
| `RK-18` | Leverage | `L` within the interval of AX-07 §8.4 and equal to the venue's reported value | set/repair, else `LEVERAGE_MISMATCH` |
| `RK-19` | Liquidation distance | `d_liq ≥ k_safe·s_stop` with live mark | reduce, else `LIQ_TOO_CLOSE` |
| `RK-20` | Liquidity/participation | `notional ≤ P-RSK-041·MQV` and `≤ P-RSK-042·D1`, and `T_exit ≤ P-RSK-043` | reduce, else `LIQUIDITY_CAP` |
| `RK-21` | Price band and filters | tick/step/min-notional/band per AX-02 §6.4/§6.7 | refuse `VENUE_FILTER` |
| `RK-22` | Economic gate | AX-08 §3.4 holds with the *final* quantized size | refuse `COST_GATE` |
| `RK-23` | Order-rate budget | P1 token available and policy cap `P-EXE-041` not exceeded | queue with deadline, else `RATE_DEFERRED` |
| `RK-24` | Protection feasibility | a protection construct is available for this instrument/position (AX-08 §6) | refuse `NO_PROTECTION` — **a position that cannot be protected is not opened** |
| `RK-25` | Universe freeze & drift | no `EV-VENUE-DRIFT` pending for this instrument | refuse `DRIFT_PENDING` |

`AX-09:§2-R1` — The kernel takes the **conservative** branch when a check cannot be evaluated (e.g. a
required query fails): an unevaluable check is a failed check (INV-1).
`AX-09:§2-R2` — Every kernel evaluation is journaled with the candidate order, the check set version,
and the outcome; the refusal ledger (§6.3) is a first-class product.

---

## 3. Governor states (`AX-09:§3`)

| State | Risk multiplier `m_gov` | New positions | Leverage factor | Exit posture |
|---|---|---|---|---|
| `NORMAL` | 1.00 | allowed | 1.0 | stops as planned |
| `CAUTION` | 0.70 | allowed | 0.8 | stops tightened by `P-GOV-010` |
| `REDUCED` | 0.40 | allowed only for instruments with `p_net ≥ P-GOV-011` | 0.6 | stops tightened; no new horizon ≥ `P-GOV-012` |
| `DEFENSIVE` | 0.15 | **no** | — | close the riskiest `P-GOV-013` % of gross by cost-adjusted edge; tighten all stops |
| `FLATTEN` | 0.00 | no | — | close everything (bounded, orderly) |
| `HALT` | 0.00 | no | — | no new venue traffic except the read queries needed to protect/close |

Transitions are event-driven; the multiplier is applied as `m_gov × m_data × m_regime` (AX-07 §2-R1)
and may only decrease it.

---

## 4. Triggers and thresholds (`AX-09:§4`)

### 4.1 Threshold derivation law (`AX-09:§4.1`)

Every governor threshold is either (a) `[O]` owner policy (drawdown limits, risk appetite) or (b) `[C]`
**calibrated from the null distribution of the monitored statistic during verified normal operation**.
The calibration procedure (`CAL-GOV-01`) is fixed:

1. Collect the statistic over the longest available clean period (paper/shadow or historical replay
   with the current code and parameters).
2. Estimate its distribution's quantiles `q_{90}, q_{95}, q_{99}` (block bootstrap for dependence).
3. Set: `CAUTION` = `q_{95}`, `REDUCED` = `q_{99}`, `DEFENSIVE` = `q_{99.5}`, and additionally cap
   `DEFENSIVE` at the owner's `D_max` (AX-07 §3.2).
4. Re-calibrate quarterly or at model promotion; a threshold change is an ADR-tracked parameter change
   (AX-12 §8).

Rationale `[D]`: thresholds tied to the statistic's own distribution have a *stated* false-alarm rate;
hand-picked thresholds do not, and their false-alarm rate is unknowable (L3, L6).

### 4.2 Trigger table (`AX-09:§4.2`)

| Group | Statistic | `CAUTION` | `REDUCED` | `DEFENSIVE` | Immediate action |
|---|---|---|---|---|---|
| Performance | drawdown in `R` units from the equity peak | `q95` | `q99` | `q99.5` & `D_max` | scale down; no new risk in `DEFENSIVE` |
| Performance | vol-scaled drawdown (`DD / σ̂_p·√t`) | `q95` | `q99` | `q99.5` | same, but regime-robust |
| Performance | daily loss vs `L_day` | 60 % | 80 % | 100 % | stop new risk for the UTC day at 100 % |
| Health | instruments in `FAIL` data state | 1 | `P-GOV-020` | `P-GOV-021` | exclude affected instruments; portfolio-level at scale |
| Health | WS session instability (`reconnects/hour`) | `q95` | `q99` | `q99.5` | drop streaming-dependent features |
| Venue | API error rate (non-success / total) | `q95` | `q99` | `q99.5` | reduce cadence, prefer cancels over new entries |
| Venue | `-1006/-1007/-114x` count in the window | ≥1 | ≥2 | ≥3 | ambiguity protocol + governor tightening |
| Execution | realised cost − modelled cost | `+q95(σ_c)` | `+q99` | `+q99.5` | de-risk; refit cost model before promotion |
| Execution | adverse selection (post-fill drift) | `q95` | `q99` | `q99.5` | shorten horizons / reduce sizes |
| Operations | open `SEV-2` incidents | 1 | 2 | 3 | ladder demotion (AX-10 §4.4) |
| Model | CUSUM alarm on standardised forecast errors | 1 alarm | 2 alarms | 3 alarms | demote model version; re-calibrate |
| Model | calibration failure (Brier skill below floor) | marginal | fail | fail + 2 consecutive | suspend the affected horizon |
| Market | funding stress: `|F-FUND|` above `q99` across `P-GOV-030` instruments | — | ×1 | ×2 | cut carry exposures, raise the funding term in cost |
| Market | absorption-ratio spike above `q99` | ×1 | ×2 | ×3 | de-risk (systemic fragility) |
| Margin | worst-case simultaneous loss (AX-09 `RK-16` metric) | 60 % of tail budget | 80 % | 100 % | reduce gross |

### 4.3 Recovery (`AX-09:§4.3`) — ratchet, dwell, evidence

- **Ratchet:** while in a stricter state, the effective risk multiplier may only be the minimum of the
  observed values; it never "bounces" upward within a cycle.
- **Dwell:** a state may be exited only after `P-GOV-040` consecutive clean evaluations of *all*
  statistics that triggered it (default 24 h for performance triggers, 1 h for health/venue triggers),
  and never within `P-GOV-041` of the triggering event.
- **Evidence:** `REDUCED` → `CAUTION` requires the triggering statistics to be inside their `q90`
  bands; `DEFENSIVE` → `REDUCED` requires either a new model promotion or an explicit operator
  re-arm with a recorded reason; `FLATTEN`/`HALT` → anything requires an operator re-arm plus a
  successful full readiness pass (AX-04 §9).
- **Never automatic upward:** no automated process may move the governor to a *less* restrictive state
  after `FLATTEN` or `HALT` (`AX-09:§4.3-R1`).

### 4.4 Portfolio quality multipliers (`AX-09:§4.4`)

Independent of the state machine, three continuous multipliers feed AX-07:
`m_data` (data health per instrument, §4.2 health rows), `m_regime` (AX-06 §6.4), and `m_exec`
(1.0 when realised cost is inside the model band; `P-GOV-050` when it is above the `q95` band; and
`P-GOV-051` when the cost model is stale beyond `P-COST-011`). All three are ≤ 1.

---

## 5. Kill switches (`AX-09:§5`)

Each switch has: detection, scope, exact actions, recovery requirement, and notification class.
Kills are **idempotent**: re-triggering an active kill leaves the state unchanged and adds a journal
record.

| ID | Trigger | Scope | Actions (exact) | Recovery |
|---|---|---|---|---|
| `K1` | Journal chain break, store write failure, or disk-space breach (`QC-20`) | system | block all new risk; keep protection/exit paths; alarm `SEV-1` | operator + integrity verification |
| `K2` | API unavailable (`P-GOV-060` consecutive failures) or a 403/WAF event | system | stop new risk; if positions exist, monitor; retry the *minimum* read set | operator re-arm after a successful readiness pass |
| `K3` | Reconciliation divergence `DIV-QTY`/`DIV-FILL`, or 3 consecutive `UNKNOWN` events | instrument or system | stop new risk; run the ambiguity protocol; place/repair protection | clean reconciliation |
| `K4` | Daily loss budget reached, or drawdown `DEFENSIVE` threshold crossed | system | stop new risk until the next UTC day (loss) or until re-arm (drawdown) | automatic (time) or operator |
| `K5` | Realised cost above the `q99` band for `P-COST-030` sessions | system | reduce sizes by `P-GOV-051`; suspend promotions | cost-model refit + verification |
| `K6` | Liquidation distance on any position below `P-GOV-070` of `k_safe·s_stop` | instrument | reduce the position until the constraint is restored, or close it | automatic upon restoration |
| `K7` | `-1022` (signature) or `-1021` persisting after re-estimation | system | halt all signed traffic | operator + signing/clock verification |
| `K8` | Operator kill (CLI/Telegram command, or a missed heartbeat from the operator-facing control channel — see §6.4) | configurable: soft (stop new risk) or hard (flatten) | as configured, journaled with the issuer | operator |

**Priority order when several fire (`AX-09:§5-R1`):** protection and closure of existing positions
always take precedence over the mechanisms that block new risk; the system prefers a closed position to
a comfortable state machine.

---

## 6. Observability, refusal telemetry and escalation (`AX-09:§6`)

### 6.1 Operator surface (`AX-09:§6.1`)

A single status view (CLI and Telegram message schema fixed in AX-12 §7.3) containing: mode, governor
state and its trigger, risk multiplier decomposition, open positions with `R` consumed and protection
state, today's loss versus `L_day`, last reconciliation result, data health summary, kill states,
pending operator decisions (e.g. re-arm requests), and the last `P-GOV-080` refusals with reasons.

### 6.2 Escalation matrix (`AX-09:§6.2`)

| Severity | Examples | Notification | Ack required | Auto-action if unacknowledged within |
|---|---|---|---|---|
| `SEV-1` | kill `K1`, flatten failure, journal break | immediate, repeated every `P-GOV-081` min, distinct channel | yes | `P-GOV-082` ⇒ system stays in the strictest safe state and keeps retrying closure |
| `SEV-2` | divergence, protection failure, 3 `UNKNOWN`s | immediate | yes | `P-GOV-083` ⇒ governor to `DEFENSIVE` |
| `SEV-3` | unprotected window, single `UNKNOWN`, data `FAIL` on a non-held instrument | batched hourly | no | — |
| `SEV-4` | informational (refusals, schedule drift) | daily digest | no | — |

Notification throttling must never suppress a `SEV-1/2`; it may only coalesce `SEV-3/4`
(`AX-09:§6.2-R1`).

### 6.3 Refusal ledger (`AX-09:§6.3`)

Every refusal is stored with: instrument, horizon, stage, check id, parameter values involved, the
forecast that was rejected, and the market state. Aggregate refusal statistics are part of the
promotion evidence (a model that is refused 99 % of the time by the cost gate is a *finding*, not a
failure).

### 6.4 Dead-man behaviour (`AX-09:§6.4`)

**Design rule: the safety of an open position must never depend on our process being alive.** Therefore:
(a) protection is always placed at the venue (AX-08 §6), (b) positions are sized so that the venue-side
protection alone bounds the loss to `R` per position under normal conditions and to
`P-GOV-090 × R` under gap scenarios (AX-07 §9.1 tail term), (c) if the process dies, the venue keeps
the stops, and the recovery path is the boot reconciliation (AX-04 §9), not an emergency.

The operator-facing control channel carries a **heartbeat**; if the operator's confirmation of a
critical re-arm request is missing beyond `P-GOV-091`, the system defaults to the stricter state
(never to the looser one).

---

## 7. Fail-safe doctrine (`AX-09:§7`)

1. **Prefer a refused trade to a doubtful one.** Refusals are cheap; unknown states are expensive.
2. **Prefer a closed position to an unprotected one.**
3. **Prefer a smaller position to a larger one** when any estimate is uncertain.
4. **Never widen a stop to avoid a stop-out**; widen only with a simultaneous, equal-or-greater size
   reduction (AX-07 §9.2).
5. **Never bypass a gate "just this once".** No override path exists in code; overrides are *parameter
   changes* with change control (AX-12 §8) or *mode changes* with the operator's recorded approval.
6. **Every automatic action must be explainable by a named trigger.** If an action cannot be traced to a
   trigger id, it is a defect (INV-11).

---

## 8. Test obligations (`AX-09:§8`)

| Area | Tests |
|---|---|
| Kernel | `T-PRETRADE-001`…`T-PRETRADE-025` — one per `RK` check, each asserting refusal and the correct reason code; `T-PRETRADE-026` — unevaluable check ⇒ refusal |
| Governor | `T-GOV-001` (each trigger), `T-GOV-002` (ratchet: no upward move without evidence), `T-GOV-003` (dwell enforcement), `T-GOV-004` (threshold calibration reproducibility) |
| Kills | `T-KILL-001`…`T-KILL-008`, plus `T-KILL-009` (idempotency) and `T-KILL-010` (priority order) |
| Telemetry | `T-OBS-001` (refusal ledger completeness), `T-OBS-002` (escalation throttling never suppresses `SEV-1/2`), `T-OBS-003` (heartbeat expiry ⇒ stricter state) |
| Dead-man | `T-DEADMAN-001` (simulated process death with open positions ⇒ venue stops remain, recovery reconciles) |
