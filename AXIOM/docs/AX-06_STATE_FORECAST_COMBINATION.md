# AX-06 — State, Forecasting and Combination

**Status:** Normative.
**Upstream:** AX-05 (features), AX-03 (time/units).
**Downstream:** AX-07 (portfolio), AX-08 (cost gate), AX-10 (promotion), AX-11 (simulator).

This document defines (a) the **prediction target**, (b) the **forecast object**, (c) the **baseline
models**, (d) the **combination and shrinkage law**, and (e) the **regime/state layer**. It fixes the
mathematics so that implementation requires no interpretive choices.

---

## 1. Pipeline (`AX-06:§1`)

```
TapeCursor(as_of) → FeatureVector (AX-05) → per-model raw score s_m(i,H,t)
   → per-model calibrated net-return forecast (μ_m, σ_m, p_m)          [§3, §4]
   → reliability-weighted combination + shrinkage → (μ_net, σ_net)     [§5]
   → regime conditioning (multiplier ∈ [0,1])                          [§6]
   → trade/no-trade decision (cost hurdle)                             [§7, AX-08 §3.4]
   → Forecast object → Portfolio plane                                  [AX-07]
```

Nothing in this pipeline may look at the account, the position, or the mode; those enter at AX-07.

---

## 2. The prediction target (`AX-06:§2`)

### 2.1 Net-return label (`AX-06:§2.1`)

For instrument `i`, horizon `H` bars, decision at bar-close `t`:

```
y_net(i,t,H) = ln( c(i,t+H) / c(i,t) ) · d
             − d · ( fee_entry + slip_entry + fee_exit + slip_exit )/1e4   [in log-return units]
             − funding_paid(i, t, t+H) · d
```
where `d = +1` for a long position and `−1` for a short (so `y_net` is the return *of the position*),
fees and slippage are in basis points converted to log-return units, and `funding_paid` is the sum of
settled funding rates over the holding window with the correct sign (a long pays a positive rate).
Details:
- `c` is the **final** close (AX-03 §3.3), never a provisional value.
- Fee rates come from `commissionRate` at the time of the label (`[V-PROBE]`); slippage uses the
  measured distribution (AX-08 §3.3), not an assumption.
- Funding uses settled values (`FundingSettlement`) for historical labels; the *current* rate is used
  only for the forward-looking cost gate, never for training labels.
- The horizon set is `H ∈ {1, 4, 16}` bars of the canonical 15 m interval (≈15 m, 1 h, 4 h).

`AX-06:§2.1-R1` — labels are computed **once**, in the learning plane, with the cost model version
recorded; changing the cost model invalidates labels and forces re-derivation (T-LAB-001).

### 2.2 Triple-barrier labels for meta-labelling (`AX-06:§2.2`)

For the trade/no-trade model (§7):
- upper barrier `+a·σ̂_H`, lower barrier `−b·σ̂_H`, time barrier `H`, with `a = b = P-FCT-001`
  (default 1.0, `[C]`, calibrated by `CAL-LBL-01` to maximize the separation between "tradeable" and
  "noise" outcomes **after** costs).
- label `+1` if the upper barrier is hit first, `−1` if the lower is hit first, `0` if the time barrier
  is reached; barrier-touch precedence within a bar follows the conservative rule "worst case first"
  (AX-11 §4.2).
- Sample weights use the **uniqueness** weight `w_u = 1/ (number of labels spanning the same bar)` to
  counter overlapping-label inflation (`AX-05:§4.7`); the weight is recorded per sample.

---

## 3. The forecast object and its calibration (`AX-06:§3`)

### 3.1 Definitions (`AX-06:§3.1`)

For each `(instrument, horizon, decision bar)` the system produces:

| Field | Meaning | Estimator |
|---|---|---|
| `μ_raw` | expected net log return, uncalibrated | model output (§4) |
| `μ_net` | calibrated expected net log return | §3.3 + §5 |
| `σ_model` | standard error of `μ_net` | block-bootstrap / analytic (§3.2) |
| `σ_market` | forecast of the return's own dispersion over the horizon | HAR-RV (§3.2, AX-05) |
| `p_net` | calibrated probability that the realised net return is positive | §3.3 |
| `n_eff` | effective sample size behind the estimate | §3.2 |

### 3.2 Uncertainty (`AX-06:§3.2`)

- `σ_market` = `√(F-HAR-RV · H)` with the HAR parameters of the instrument's current model version.
- `σ_model` is estimated by a **stationary block bootstrap** over training residuals with block length
  `P-FCT-002` bars, `P-FCT-003` replications, refitting the model on each replication at a reduced
  cost (`P-FCT-004` replications may reuse the design matrix). The standard deviation of the
  bootstrap `μ` distribution is `σ_model`.
- `n_eff` uses the number of *uniquely* labelled bars in the fitting window: `n_eff = Σ w_u`
  (weights from §2.2). This is what makes shrinkage honest (§5.2).
- Total predictive dispersion used for probabilities: `σ_pred² = σ_market² + σ_model²`
  (`[D]`: the two sources are treated as independent because model error and market noise have
  different generating mechanisms; the assumption is tested by the calibration diagnostics of §3.4).

### 3.3 Calibration (`AX-06:§3.3`)

Raw scores are not probabilities. Two calibrations are applied, both **cross-fitted** (fitted on a
fold and applied to the held-out fold) to avoid optimistic in-sample calibration:

1. **Magnitude calibration (regression):** fit `y_net = α + β·s_raw + ε` on the fold; the calibrated
   magnitude is `μ_net = α̂ + β̂·s_raw`. `β̂` is the *shrinkage built into the data*: if the raw score
   overstates the effect, `β̂ < 1` automatically.
2. **Probability calibration (isotonic):** fit a monotonically increasing step function mapping the
   standardised score `z = μ_net/σ_pred` to the empirical frequency of `y_net > 0`, with a minimum bin
   size of `P-CAL-001` samples and isotonic regression (PAVA). Monotonicity is required so that the
   trading rule remains monotone in the forecast.

**Calibration diagnostics (blocking for promotion, AX-10 §4.3):**
- reliability curve in `P-CAL-002` bins with a bootstrap band;
- **Brier skill score** versus the base rate: `BSS = 1 − BS/B S_ref` must exceed `P-CAL-003`;
- **sharpness**: the distribution of `p_net` must not collapse to the base rate (a model that always
  predicts 0.5 has no information);
- **monotone degradation**: at least `P-CAL-004` of the bins must lie on the correct side of the
  diagonal within band.

### 3.4 What "calibrated" means here (`AX-06:§3.4`)

A forecast is calibrated when, conditional on the forecast value, the realised frequency matches within
the declared band. This is a *testable empirical claim* about our own model, re-tested every
`P-CAL-005` days (AX-10 §6). Failure triggers demotion or re-calibration, not a narrative.

---

## 4. Models (`AX-06:§4`)

### 4.1 Baseline model `M1` (Tier `T1`) — regularised linear (`AX-06:§4.1`)

- Design matrix `X` = scaled `T1`(+) features (§AX-05 §4.6), plus a constant.
- Objective: weighted ridge `min_β Σ_s w_u,s (y_s − x_s'β)² + λ Σ_{j≠0} β_j²`, with `λ` chosen on a
  purged, embargoed validation fold (AX-10 §3.3) by minimising mean squared error *of the net return*;
  `λ` is a `[C]` parameter per horizon and is stored with the model artifact.
- Reported inference: HAC (Newey–West) standard errors with lag `P-FCT-005`, plus the block-bootstrap
  errors of §3.2; the more conservative of the two is used for `σ_model`.
- Rationale for a linear baseline `[D]`: (a) the parameter count is honest relative to `n_eff`
  (A3), (b) coefficients are interpretable and monitorable per feature (§AX-05 §5), (c) a nonlinear
  model must *earn* its place by the same admission test, not by default.

### 4.2 Model `M2` (Tier `T2`) — shallow gradient boosting (`AX-06:§4.2`)

- Hyperparameters are bounded by design: depth ≤ `P-FCT-010`, trees ≤ `P-FCT-011`, learning rate
  `P-FCT-012`, minimum child samples `P-FCT-013`; all are `[C]` and selected on the purged fold.
- It is admitted only if, against `M1` on the *same* folds, the incremental net objective (§AX-05 §2.3)
  is positive with a bootstrap CI excluding zero and the cost-stress condition holds.
- Monotonicity constraints are imposed on the features whose mechanism implies a monotone effect
  (e.g. `F-TAKER` may be non-monotone; `F-SPR`'s effect on *net* return is monotone negative) — this
  reduces over-fitting and preserves interpretability. The constraint list is part of the artifact.

### 4.3 Models `M3` (Tier `T3`) — research (`AX-06:§4.3`)

Anything else (nonlinear state-space models, HMM-conditioned regressions, kernel methods, sequence
models). They live in `lnp`, are compared under identical folds and the same admission test, and may
enter the live path **only** by passing it and being recorded in the model registry with an ADR.

### 4.4 Missing inputs (`AX-06:§4.4`)

- If any `T1` feature returns `insufficient_data` for an instrument, the instrument produces **no
  forecast** that cycle (`reason = FEATURE_UNAVAILABLE`); no imputation, no partial model.
- If a `T2` feature is unavailable, it is replaced by its training-window median *and* the model's
  confidence is reduced: `σ_model ← σ_model · P-FCT-020` (default 1.5, `[O]`). The substitution is
  recorded in the forecast metadata.

---

## 5. Combination and shrinkage law (`AX-06:§5`)

Given `M` models with forecasts `μ_m` and standard errors `σ_m`:

1. **Precision weighting:** `w_m ∝ 1/σ_m²`, normalised to sum to 1, and clipped below by 0 and above by
   `P-FCT-030` (default 0.6) so that no single model dominates (`[D]`: the variance proportional to
   inverse-precision is the minimum-variance combination under independence; the clip bounds the
   damage of an underestimated `σ_m`, which is the realistic failure mode).
2. **Correlation adjustment:** models are not independent. The effective number of models is
   `M_eff = 1/Σ_m w_m²`; if `M_eff < 1.2`, the combination is no better than the best single model and
   the simpler model is used directly (`[D]`: the variance of a nearly degenerate combination exceeds
   the single-model variance; A7 prefers the simpler object).
3. **Shrinkage toward zero (Bayesian, honest):** apply
   `μ_net = μ_comb · max(0, 1 − P_eff/n_eff)` where `P_eff` is the number of *effective* parameters
   (the ridge's effective degrees of freedom `tr(X(X'X+λI)⁻¹X')`) and `n_eff` from §3.2.
   Derivation `[D]`: the adjusted R² of a regression shrinks by approximately `P/n`; with few
   independent observations this factor is material and prevents the system from trading the
   in-sample component of its estimate.
4. **Final dispersion:** `σ_net = √(σ_market² + σ_model²)` where `σ_model` accounts for the
   combination weights (`σ_model² = Σ w_m² σ_m²` plus the covariance terms estimated by the bootstrap).
5. **Horizon selection:** each horizon is forecast independently; the *portfolio* layer (AX-07 §6)
   chooses the horizon whose net edge, after the round-trip cost of the position it implies, is
   largest. The forecast layer never blends horizons into a single number (blending destroys the
   cost/horizon relationship, which is the main economic trade-off).

---

## 6. Regime and state layer (`AX-06:§6`)

### 6.1 Purpose (`AX-06:§6.1`)

The regime layer **conditions** forecasts and risk; it is never a standalone alpha. Its outputs are
multipliers in `[0,1]` and category labels for monitoring.

### 6.2 Hidden Markov state model (`AX-06:§6.2`)

- Observation vector per bar: `[z(F-RV), F-ER{16}, F-ABSORB, F-DISP]` (scaled, winsorised per AX-05 §4.6).
- `K ∈ {2,3,4}` states, Gaussian emissions with diagonal covariance (diagonal is deliberate: full
  covariance with `K·4·5/2` parameters is not affordable at the available sample size — A3).
- Fitted by EM with `P-REG-001` restarts (different seeds), selecting the restart with the highest
  log-likelihood *on held-out data* (not in-sample) to reduce local optima and over-fitting.
- **Label-switching** resolution: states are ordered by their expected volatility (ascending) and
  re-mapped after each fit so that state numbering is stable across fits.
- **Online use:** the live forecast consumes the **filtered** probability `P(state_t | data_{≤t})`
  (forward pass only). Smoothed probabilities are a research tool and are **forbidden** in the live
  path (`T-REG-001`).
- **State uncertainty:** `H_t = −Σ_k P_k ln P_k / ln K`. If `H_t > P-REG-002`, the regime is treated as
  unknown: all regime multipliers are set to `P-REG-003` (default 0.8, `[O]`) rather than to the
  arg-max state (`[D]`: acting on an uncertain state is over-fitting to noise).

### 6.3 Change-point monitors (`AX-06:§6.3`)

- **CUSUM on standardised forecast errors** `e_t = (y_real − μ_net)/σ_net`:
  `S⁺_t = max(0, S⁺_{t−1} + e_t − k)`, `S⁻_t = max(0, S⁻_{t−1} − e_t − k)` with drift `k = P-REG-010`
  (default 0.5) and alarm at `h = P-REG-011` (default 5). Alarm ⇒ `EV-FCT-CUSUM` and a mandatory
  review; two alarms within `P-REG-012` days demote the affected model version.
- **Volatility regime break:** the `F-VOLPCT` series is monitored with the same CUSUM machinery in log
  space.

### 6.4 Regime multipliers (`AX-06:§6.4`)

| Condition | Multiplier on `μ_net` | Multiplier on the risk budget (passed to AX-07) |
|---|---|---|
| high-vol state and the model was trained mostly in low vol (state-conditional `n_eff < P-REG-020`) | `P-REG-021` (default 0.7) | `P-REG-022` (default 0.8) |
| trend state, trend-following features dominant | 1.0 | 1.0 |
| choppy state (low `F-ER`) | `P-REG-023` (default 0.8) | 1.0 |
| turbulence above `P-REG-024` | `P-REG-025` (default 0.5) | `P-REG-026` (default 0.6) |
| absorption ratio above `P-REG-027` (fragility) | 1.0 | `P-REG-028` (default 0.7) |

All multipliers are `[C]`-class and are re-estimated at each model promotion; multiplying them without
evidence is prohibited (C5).

---

## 7. Trade/no-trade decision (`AX-06:§7`)

A forecast becomes a *tradeable* signal only when **all** hold (the algebra of the cost hurdle lives in
AX-08 §3.4; the *decision* is stated here because it determines what the portfolio layer receives):

1. `μ_net > 0` and `p_net ≥ P-FCT-040` (default 0.55, `[O]`; a lower value is allowed only with
   correspondingly higher cost margin — the two are coupled, see AX-08 §3.4).
2. The **lower confidence bound** `μ_net − z_{P-FCT-041}·σ_model > c_roundtrip + m·σ_c`, where
   `c_roundtrip` is the modelled round-trip cost and `m·σ_c` its uncertainty margin (AX-08 §3.3–3.4).
3. The meta-model (Tier `T2`, when enabled) returns `p_trade ≥ P-FCT-042`, where the meta-model is
   trained on triple-barrier labels (§2.2) using the *same* features plus the primary model's output —
   i.e. it learns *when the primary model's signals pay*, which is a different question from direction
   (`[D]`: meta-labelling separates the "when" from the "which way", and reduces the cost of
   false-positive signals).
4. Regime multiplier and data-health multiplier are applied (`≠ 0`); a zero multiplier suppresses the
   signal entirely.

If any condition fails, the system emits a `Refusal` with the failing condition id (AX-09 §6.3). This
is deliberate: **most bars should produce refusals** — a system that trades most of the time is
almost certainly ignoring cost.
