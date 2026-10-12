# AX-07 — Risk Model, Portfolio Construction and Sizing

**Status:** Normative.
**Upstream:** AX-06 (forecasts), AX-02 (§6.4–6.6 venue constraints), AX-03 (numeric law).
**Downstream:** AX-08 (what to execute and how), AX-09 (what can veto), AX-11 (simulator), AX-15.

This document converts forecasts into **bounded positions**. It owns the capital-risk budget. Every
formula here is deterministic given its inputs; there are no discretionary overrides.

---

## 1. Authority (`AX-07:§1`)

- `pfp` proposes targets. `rg` (AX-09) may **reduce or veto**; it may never increase. `exp` may choose
  *how* to reach a target within a price/time budget; it may never change size, direction, or symbol.
- All limits in this document are expressed as parameters (AX-15) with a provenance class. A limit that
  is not in the registry cannot be applied (`AX-03:§1.5-R1`).

---

## 2. The four budgets (`AX-07:§2`)

| Budget | Owner doc | Binding quantity |
|---|---|---|
| Capital at risk | this document | `R` (risk unit), per-trade loss cap, daily loss cap, cluster caps, margin utilisation |
| Data integrity | AX-04 | health states ⇒ `no-new-risk` per instrument |
| Execution quality | AX-08 | realized-vs-modelled cost; if breached ⇒ de-risk |
| Operational | AX-09/AX-12 | incident rate ⇒ ladder demotion |

`AX-07:§2-R1` — The capital budget is **multiplicative** with the other three: the effective risk at
any instant is `R × (governor multiplier) × (data-health multiplier) × (regime multiplier)`, and every
factor is ≤ 1 by construction. No component can increase risk.

---

## 3. The risk unit `R` (`AX-07:§3`)

### 3.1 Definition (`AX-07:§3.1`)

`R` is the money value the account is willing to lose if a single trade's protective stop is hit at the
modelled slippage. All position sizes derive from `R`; all risk statistics are reported in multiples of
`R` (`R`-multiples), making them comparable across instruments and regimes.

### 3.2 Derivation from owner policy (`AX-07:§3.2`) — no magic number

Let the owner declare (Owner Input Register, AX-15 §9):

| Input | Symbol | Meaning |
|---|---|---|
| `OI-RISK-01` | `D_max` | the monthly drawdown the owner is willing to tolerate in the *normal* course of business (e.g. 0.15) |
| `OI-RISK-02` | `N_bets` | the expected number of *independent* risk events per month (from the strategy's turnover; re-estimated monthly from the journal) |
| `OI-RISK-03` | `k_D` | the drawdown multiple to protect against (default 2, `[O]`, allowed 1.5–3) |

Then:
```
R_fraction = D_max / ( k_D · sqrt(N_bets) )        [fraction of equity per trade]
R = R_fraction · equity
```
Derivation `[D]`: under the standard model where each risk event contributes an independent `±1 R`
outcome, the accumulated P&L after `N` events has standard deviation `√N · R`; requiring the *k_D σ*
drawdown to stay inside `D_max` gives the formula. Consequences that are made explicit:
- `N_bets` must come from *measured* turnover, not hope: if the strategy trades more than assumed, the
  monthly risk of a `D_max` breach rises with `√N_bets`; therefore the estimator of `N_bets` (rolling
  30-day count of new positions) is a monitored quantity (`AX-09 §4.4`).
- `R_fraction` is capped by `P-RSK-001` (default 0.01 = 1 % of equity, absolute hard cap `[O]`) and
  floored by feasibility: if `R < min_notional · stop_fraction` for the *most liquid* instrument, the
  system reports "capital too small for the configured risk policy" rather than silently oversizing
  (`AX-07:§3.2-R1`).

### 3.3 Daily loss budget (`AX-07:§3.3`)

`L_day = min( P-RSK-002 · equity ,  (Σ_i risk_i of open positions) + (Σ pending intents risk) )` with
default `P-RSK-002 = 0.04` (`[O]`). The governor tracks realized + unrealized loss against `L_day`; on
breach it enters `DEFENSIVE` and stops new risk for the rest of the UTC day (AX-09 §4.2). The daily
budget is **not** a target to be used up; it is a circuit breaker.

---

## 4. Portfolio volatility target (`AX-07:§4`)

- `σ_target` (annualised) is `[O]` (`OI-RISK-04`, default 0.20, allowed 0.05–0.50).
- The instantaneous portfolio volatility estimate is `σ̂_p = √(w' Σ w) · √(bars_per_year)` where `Σ` is
  the per-bar covariance of log returns from §5 and `w` the target weights.
- The global scale is `g = clamp(σ_target / σ̂_p, 0, g_max)` with `g_max = P-RSK-003` (default 2,
  `[D]`: doubling exposure is the largest step that cannot be confused with a modelling error; larger
  scales are addressed by adding capital, not leverage).
- `w_final = g · w_proposed`. If `g < P-RSK-004` (default 0.25), the system reports "vol target
  unreachable at the current opportunity set" instead of forcing trades (`AX-07:§4-R1`).

---

## 5. Covariance model (`AX-07:§5`)

### 5.1 Estimator chain (`AX-07:§5.1`)

1. **EWMA covariance** with decay `λ_c = P-RSK-010` (default 0.97 on 15 m bars ⇒ ≈ 1 day half-life;
   `[D]`, re-fitted by `CAL-RSK-01` against realized out-of-sample portfolio variance).
2. **Shrinkage:** Ledoit–Wolf toward the single-index (market) target:
   `Σ_shrunk = (1 − δ) Σ_EWMA + δ F`, with `F` the constant-correlation/single-factor target and `δ`
   estimated by the standard LW formula `[D]` (the estimator of the optimal shrinkage intensity is the
   ratio of the mean squared deviation between sample and target covariance to the mean squared
   deviation of the sample covariance; computed in code per the LW paper, cited in AX-18 ADR-014).
3. **Denoising (Marchenko–Pastur):** with `q = T/N` the ratio of observations to instruments, the
   noise-edge eigenvalues lie in `[σ²(1−√q)², σ²(1+√q)²]`. Eigenvalues inside the band are replaced by
   their average (clipping); those below the band are set to zero. `[D]`: this prevents the
   optimiser from trading on noise directions, which is the dominant failure of unscaled mean-variance
   optimisation at our `N/T` ratio.
4. **Positive-definiteness:** if the result is not positive definite (possible after clipping), add
   `P-RSK-011 · I` and log the event (`T-RISK-001` asserts PD in all fixtures).

### 5.2 Correlation structure, clusters and capital allocation (`AX-07:§5.2`)

1. Correlation matrix from `Σ` (fall back to `F-CORR-DIST`).
2. Distance `d_ij = √(0.5(1 − ρ_ij))`; hierarchical clustering (average linkage) to `P-RSK-012`
   clusters **or** a distance cut `P-RSK-013`, whichever yields the more balanced partition.
3. **Within-cluster allocation:** inverse-variance weights, shrunk toward equal weight by
   `P-RSK-014` (default 0.5) — equal weight is the robust default when the covariance estimate is
   noisy (`[D]`: shrinkage toward 1/N is the standard answer to estimation error).
4. **Across-cluster allocation:** equal *risk* contribution by default; option `OI-RISK-05` allows
   cluster weights proportional to shrunk cluster-level `μ`, in which case the cluster `μ` uses the
   same reliability shrinkage as AX-06 §5 unless the sample-size gate is met for the cluster level.
5. Outcome: a **prior weight vector** `w_prior` used as the starting point of §6.

---

## 6. Portfolio construction (`AX-07:§6`)

### 6.1 Objective (`AX-07:§6.1`)

```
maximise_w   μ' w − (γ/2) w' Σ w − Σ_i C_i(|w_i − w_i^prev|)
subject to   Σ_i |w_i| ≤ G                       (gross exposure cap)      [P-RSK-020]
             |Σ_i w_i| ≤ N_net                   (net exposure cap)        [P-RSK-021]
             |w_i| ≤ w_max                        (per-instrument cap)      [P-RSK-022]
             Σ_{i∈cluster c} |w_i| ≤ C_c          (cluster cap)             [P-RSK-023]
             |β' w| ≤ B                          (market-beta neutrality)  [P-RSK-024]
             f_i · w_i ≤ liquidity cap_i          (§7.4)
```
where `μ` is the reliability-shrunk net forecast (AX-06 §5), `γ` is the risk-aversion parameter
`P-RSK-030` (`[D]`: `γ` is chosen so that, in the absence of costs and limits, the unconstrained
solution would use the full risk budget: `γ = √(σ_target⁻² · μ'Σ⁻¹μ / (1'))` evaluated on the training
window — i.e. it is *fitted to the owner's risk target*, not chosen by taste), `C_i(·)` are
proportional round-trip costs (AX-08 §3), and `f_i` the contract multiplier.

### 6.2 Solver requirement (`AX-07:§6.2`)

- Determinism is mandatory (INV-5): the solver is a **projected-gradient / proximal method with a fixed
  iteration count and fixed tolerances**, or an open QP solver run with a fixed configuration; the
  chosen method and its version are recorded in the artifact. Iterative solvers that can return
  different answers on different runs are non-compliant.
- The solution is validated post-hoc: constraint violation ≤ `P-RSK-031`; otherwise the previous
  portfolio is retained (fail-safe) and an incident is raised (`T-OPT-001`).

### 6.3 No-trade band (cost-aware inertia, derived) (`AX-07:§6.3`)

Trade instrument `i` from `w_i^prev` toward `w_i*` only if
```
|w_i* − w_i^prev| · E_i   >   c_i · |w_i* − w_i^prev| + F_i / equity + S_i
```
where `E_i` = the marginal expected net return of the position difference (that is `μ_i` net of the
risk penalty `γ (Σw)_i`), `c_i` = proportional round-trip cost (fees + spread + slippage), `F_i` = the
part of the cost that is fixed per order (its expected minimum-notional size effect, modelled in
AX-08 §3.5), and `S_i` = a **safety margin** equal to `z_s · σ_cost` with `z_s = P-RSK-032`
(default 1.0) and `σ_cost` the standard error of the cost estimate for that instrument (AX-08 §3.3).
Derivation `[D]`: the inequality is the discrete optimal-trading band condition — trade when the
expected benefit of the rebalancing trade exceeds its expected total cost plus the uncertainty of that
cost. Setting `S_i = 0` reproduces the classic band result; the safety margin is what prevents
"trading on a cost estimate that happens to be wrong today".

### 6.4 Turnover cap (`AX-07:§6.4`)

`Σ_i |w_i* − w_i^prev| ≤ TO_max` per day (`P-RSK-033`, default derived from `N_bets × 2`). If the
unconstrained solution exceeds it, the trades are ranked by the §6.3 surplus (benefit minus cost) and
executed in that order until the cap is reached — the residual becomes next cycle's demand, which
naturally reduces turnover under stress.

---

## 7. Sizing a single trade (`AX-07:§7`)

All caps are computed and the **minimum** is taken; each cap that binds is recorded in
`Target.binding_constraints` (observability, INV-11).

### 7.1 Risk-based cap (`AX-07:§7.1`)

```
qty_risk = ( R · m_risk ) / ( |entry_ref − stop_price| · f )
```
with `f` = contract multiplier (`[V-PROBE]`), `entry_ref` the price the decision assumes (the current
`F-MICRO`-adjusted mid, recorded for later slippage measurement), `stop_price` from §9, and `m_risk`
the effective risk multiplier `= governor × data-health × regime` (all ≤ 1).

### 7.2 Volatility-target cap (`AX-07:§7.2`)

```
qty_vol = ( g · w_i* · equity ) / ( entry_ref · f )
```
i.e. the notional implied by the portfolio solution after the global scale `g` of §4.

### 7.3 Kelly lower-bound cap (`AX-07:§7.3`)

Continuous log-optimal fraction `f* = μ / σ²` (per trade, in return units). AXIOM uses the
**lower confidence bound** formulation:
```
f_used = f_kelly · max(0, (μ_net − z_k · σ_model) / μ_net)      with f_kelly = P-RSK-040
qty_kelly = ( f_used · equity ) / ( entry_ref · f )
```
`P-RSK-040` (default 0.25, `[O]`, allowed 0.05–0.5) is the fraction of full Kelly used, justified `[D]`
by three facts: (i) `μ` is estimated, not known (the LCB term addresses this directly),
(ii) returns are not Gaussian (fat tails make full Kelly ruinous at the same `σ`),
(iii) models decay (AX-05 §5), so the realised `μ` is lower than the fitted one.

### 7.4 Liquidity cap (`AX-07:§7.4`)

```
qty_liq = min( P-RSK-041 · MQV_traded , P-RSK-042 · D1 ) / ( entry_ref · f )
```
with `MQV_traded` the median minute traded notional and `D1` the notional resting at the touch
(AX-05 §3.3). Defaults `P-RSK-041 = 0.05`, `P-RSK-042 = 0.10` (`[O]`; the *range* is bounded to
0.01–0.20 and 0.02–0.30). Additionally the **time-to-exit** estimate
`T_exit = position_notional / (P-RSK-041 · MQV_traded)` must satisfy `T_exit ≤ P-RSK-043` (default
2 minutes) at the *maximum* position; otherwise the position cap is reduced to satisfy it. This is what
guarantees the kill switch can actually flatten the book (A5).

### 7.5 Margin cap (`AX-07:§7.5`)

```
qty_margin = ( M_avail · L_i ) / ( entry_ref · f )
```
with `M_avail` the free margin after §8's utilisation cap and `L_i` the leverage for the instrument
from §8.

### 7.6 Final size (`AX-07:§7.6`)

```
qty = round_down_to_step( min(qty_risk, qty_vol, qty_kelly, qty_liq, qty_margin) )
```
then the min-notional rule of AX-03 §4.2. If the result is zero or below the venue minimum with no
permission to raise: `Refusal(reason = SIZE_BELOW_MINIMUM)`.

### 7.7 Horizon selection at execution time (`AX-07:§7.7`)

When more than one horizon produces a target for the same instrument, the executed horizon is the one
maximising `net_edge(h) = |μ_net(h)| − c_roundtrip(h) − funding_cost(h)`, with `c_roundtrip(h)` scaled
by the expected number of round trips implied by the decay of the signal at that horizon
(`≈ 1/half_life`). Ties are broken by the longer horizon (fewer trades, lower cost variance) —
deterministic tie-breaking is mandatory.

---

## 8. Leverage and margin policy (`AX-07:§8`)

### 8.1 Definitions (`AX-07:§8.1`)

- `f_i` contract multiplier `[V-PROBE]`; `notional_i = qty_i · price · f_i`.
- Tier: from `RiskTierObs` (AX-02 §6.6) for the current `notional_i`: `initial_margin_rate mm_i`,
  `maintenance_margin_rate mnt_i`, `max_leverage L_tier`.
- `L_i` = leverage set for the symbol via the venue (integer).

### 8.2 Liquidation-distance constraint (derived) (`AX-07:§8.2`)

For an isolated-margin position, ignoring fees and funding, the distance from entry to liquidation is
approximately `d_liq ≈ 1/L − mnt` (fraction of price, for a long: `p_liq ≈ entry·(1 − 1/L + mnt)`).
Require the stop to trigger long before liquidation with a gap allowance:
```
1/L_i − mnt_i  ≥  k_safe · s_stop_i          (safety constraint, gives the maximum usable L)
⇒       L_i     ≤  1 / ( mnt_i + k_safe · s_stop_i )
```
with `k_safe = P-RSK-050` (default 3, `[O]`, allowed 2–6) and `s_stop` the relative stop distance from
§9.1. Rationale `[D]`: the venue liquidates on mark price with its own slippage; a `3×` buffer between
the stop and the liquidation band survives normal gaps and mark-price dislocations without demanding
absurd margin.

### 8.3 Margin-utilisation constraint (`AX-07:§8.3`)

`L_i ≥ notional_i / M_avail_i`; and `Σ_i (notional_i / L_i) + Σ working orders (marginLocked_i) ≤
P-MRG-001 · equity` with default `P-MRG-001 = 0.5` (`[O]`, allowed 0.2–0.7). Rationale `[D]`: at 50 %
utilisation, a simultaneous adverse move of ~2× the portfolio's daily σ leaves the account above its
maintenance requirement; the exact value is re-derived from measured σ and the venue's maintenance
rates at each model promotion (`CAL-MRG-01`).

### 8.4 Setting and verifying leverage (`AX-07:§8.4`)

```
L_i = clamp( floor( 1 / (mnt_i + k_safe · s_stop_i) ) , ceil(notional_i / M_avail_i) , L_tier )
```
- If the interval is empty ⇒ the trade is refused (`Refusal(reason = MARGIN_INFEASIBLE)`) and the size
  is re-derived downward once (not iteratively, to avoid unbounded loops); if still infeasible, the
  instrument is flagged for the day.
- `L_i` is set via the venue **before** the entry order, then read back (`accountLeverage`); a mismatch
  is a hard stop for that instrument (`T-STATE-002`).
- Leverage is never set above `L_tier` and never "for margin efficiency" beyond this formula.

---

## 9. Stops, tails and liquidation (`AX-07:§9`)

### 9.1 Stop distance (`AX-07:§9.1`)

```
s_stop = max( c_σ · σ̂_H ,  c_c · (s_spread + fee_rt) ,  q_tail )
```
- `σ̂_H = σ̂_market · √H` (per-AX-06 §3.2), `c_σ = P-RSK-060` (default 2.5, `[C]`, `CAL-STP-01`
  selects `c_σ` on the training window as the smallest value for which the realised stop-out rate does
  not exceed the modelled rate by more than `P-RSK-061`).
- `c_c = P-RSK-062` (default 3): a stop inside three cost units is noise, not protection.
- `q_tail` = the `P-RSK-063` quantile (default 0.995) of the *holding-period* return distribution
  estimated by a peaks-over-threshold GPD fit on losses exceeding the `P-RSK-064` quantile of the
  trailing `P-RSK-065` bars; if the tail fit fails its diagnostics (Hill-plot stability,
  `T-TAIL-001`), `q_tail = c_tail · σ̂_H` with `c_tail = P-RSK-066` (default 3.5) and the fallback is
  journaled.
- The stop is placed **on mark price** (`triggerBy = MARK_PRICE`) to avoid wick-triggered exits and
  because the venue's own liquidation uses mark price (AX-02 §6.5).

### 9.2 Stop revision (`AX-07:§9.2`)

- Stops may be **tightened** when (i) vol falls materially (`σ̂` down by `P-RSK-070`), or (ii) the
  position reaches `P-RSK-071 R` of unrealised profit, in which case the stop may be moved to at most
  `P-RSK-072 R` of locked profit.
- Stops may be **loosened** only by reducing size simultaneously so that `qty · s_stop` is
  non-increasing. This invariant (`qty · s_stop = R · m_risk` never increases) is enforced by the risk
  kernel (`T-RISK-002`).
- Stop revisions are journaled with the triggering condition; no revision may occur more often than
  `P-RSK-073` per position per day (rate-limit on risk-state churn).

### 9.3 Trailing (`AX-07:§9.3`)

The venue's trailing-stop primitive is **not** used (AX-02 §6.2); trailing is implemented as our own
revision rule in §9.2, so that the trigger logic and its timing are observable and testable.

### 9.4 Pre-trade liquidation check (`AX-07:§9.4`)

Immediately before submitting an entry, the kernel recomputes `d_liq` with the **live** mark price, the
actual `L_i`, and the tier's `mnt_i`; the condition `d_liq ≥ k_safe · s_stop` must hold with the live
numbers (a stale tier or a drifted mark can otherwise turn a safe plan into a thin one). Failure ⇒
refuse (`Refusal(reason = LIQ_TOO_CLOSE)`).

---

## 10. Worked example (`AX-07:§10`) — reference numbers for implementers

**Inputs.** Equity `10 000 USDT`; owner policy gives `R_fraction = 0.005` ⇒ `R = 50 USDT`. Instrument
`X-SWAP-USDT`: `f = contractMultiplier = 0.001`, `tick = 0.01`, `step = 1`, `minNotional = 10 USDT`,
`entry_ref = 2.500`, `mnt = 0.005`, `L_tier = 20`. Forecast: `σ̂ = 0.004` per 15 m bar, horizon
`H = 4` bars ⇒ `σ̂_H = 0.004·√4 = 0.008`. Costs: spread `6 bps`, round-trip fees `4 bps`.
Stop: `σ̂`-component `= c_σ · σ̂_H = 2.5 · 0.008 = 0.02`; cost component `= c_c · (s + fees) = 3 · 10
bps = 0.03`; **the cost component binds** ⇒ `s_stop = 0.03`.

| Cap | Formula | Value (contracts) | Notional |
|---|---|---|---|
| `qty_risk` | `R / (f · price · s_stop) = 50 / (0.001 · 2.5 · 0.03)` | `666 666` | `1 666.7 USDT` |
| `qty_vol` | `g · w* · equity / (f · price) = 1.0 · 0.15 · 10 000 / (0.001 · 2.5)` | `600 000` | `1 500 USDT` |
| `qty_kelly` | `f_used · equity / (f · price)`, `f* = μ/σ² = 0.006/0.05² = 2.4`, `f_used = 0.25 · 2.4 · 0.6 = 0.36` | `1 440 000` | `3 600 USDT` |
| `qty_liq` | `0.05 · MQV / (f · price) = 0.05 · 40 000 / 0.0025` | `800 000` | `2 000 USDT` |
| `qty_margin` | `M_avail · L / (f · price) = 5 000 · 10 / 0.0025` | `20 000 000` | `50 000 USDT` |

**Result.** `qty = min(...) = 600 000` contracts (`1 500 USDT` notional), binding constraint
`VOL_TARGET`. Risk consumed `= qty · f · price · s_stop = 600 000 · 0.001 · 2.5 · 0.03 = 45 USDT ≤ R`.
Margin used `= notional/L = 150 USDT` at `L = 10`. Stop price `= 2.500 · (1 − 0.03) = 2.425`.
Liquidation-distance check: `1/L − mnt = 0.1 − 0.005 = 0.095` versus `k_safe · s_stop = 3 · 0.03 =
0.09` ⇒ passes with `0.005` of margin, i.e. **tight**; the system must display this headroom rather than
hide it (the governor's `CAUTION` state is triggered by such thinness at the portfolio level, AX-09 §4).

`T-RISK-003` reproduces this table exactly; any deviation is a defect in either the code or this
document — and the resolution is an ADR, never a silent edit.
