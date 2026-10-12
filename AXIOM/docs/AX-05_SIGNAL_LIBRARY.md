# AX-05 — Signal Library: Estimators, Features and Admission

**Status:** Normative.
**Upstream:** AX-02 (data availability), AX-03 (time/units), AX-04 (quality).
**Downstream:** AX-06 (forecasts), AX-10 (promotion), AX-14 (tests), AX-15 (parameters).

This document defines **every** quantity the forecasting plane is allowed to consume. A quantity that
is not defined here does not exist: features cannot be invented in code (`AX-01:§6`). Each definition
carries its inputs, its declared availability lag, its minimum history, its tier, and its kill rule.

---

## 1. Conventions (`AX-05:§1`)

### 1.1 Notation (`AX-05:§1.1`)

| Symbol | Meaning |
|---|---|
| `i`, `j` | instruments (venue symbols) or market/index series |
| `t` | bar index on a chosen interval; `o,h,l,c,v` the bar fields |
| `r_t` | log return, `r_t = ln(c_t / c_{t−1})` |
| `σ̂_t` | per-bar volatility estimate, unit = per-bar log return |
| `mid_t` | `(bid+ask)/2` from `Quote` |
| `s_t` | quoted spread, `s_t = (ask − bid)/mid_t` (fraction, reported in bps where stated) |
| `τ` | half-life in bars |
| `z(x)` | robust z-score, `z = (x − median)/ (1.4826 · MAD)` over the declared window |
| `E[·]` | sample mean over the declared window (documented per feature) |

### 1.2 Unit law (`AX-05:§1.2`)

Every feature declaration states its unit. Return-like quantities are per-bar log returns on the
declared interval; volatility-like quantities are per-bar standard deviations of log returns;
cost-like quantities are fractions of notional (bps in commentary only); counts are integers per bar.
**A feature whose unit cannot be stated is not admissible.**

### 1.3 Availability law (`AX-05:§1.3`)

A feature computed at `as_of = T` may use only records with `ingest_ts ≤ T` (AX-03 §3.2) and only
**final** bars (AX-03 §3.3). Each feature declares `lag_declared` = the maximum over its inputs of
`L_source` (AX-03 §3.4). The simulator enforces the same lag in backtests (AX-11 §5.3), which is what
makes a backtest admissible evidence rather than a story.

---

## 2. Admission framework (`AX-05:§2`)

### 2.1 Tiers (`AX-05:§2.1`)

| Tier | Meaning | Requirement |
|---|---|---|
| `T1` | **Core.** Always on; used by the baseline forecaster. | Its inputs exist in the venue data (AX-02 §5) with sufficient history; a small number of parameters; a documented mechanism for *why* the regularity should exist. |
| `T2` | **Conditional.** Enabled only when its data gate and sample gate are satisfied. | Passes the marginal-information test (§2.3) on an out-of-sample window; its data requirement is met (e.g. verified taker-side semantics for flow features, verified book reconstruction for book features). |
| `T3` | **Research only.** Never in the live path. | Exists in `lnp`; may graduate to `T2` only through AX-10 §4 gates. |

### 2.2 Mechanism requirement (`AX-05:§2.2`)

Every feature must state a *mechanism* — an economic or structural reason the regularity should exist
and persist, and the condition under which it should fail. Examples: "funding carry exists because
perpetual buyers pay for leverage when longs crowd"; "liquidation-cascade reversal exists because
forced sellers transact at prices beyond fundamental value"; "time-series momentum exists because of
slow information diffusion and risk-management constraints". A feature whose only justification is
"it backtests well" is **rejected** (A7, L6).

### 2.3 Marginal-information test (`AX-05:§2.3`, `T-ADM-002`)

A candidate feature (or feature group) is admitted to `T2` only if **all** hold:

1. **Incremental, not decorative.** Fit the baseline forecaster (AX-06 §4.1) with and without the
   candidate on identical folds. Require a positive out-of-sample, cost-adjusted improvement of the
   forecast's *net* objective (AX-06 §3.3) with a block-bootstrap 90 % confidence interval that
   excludes zero (block length = `P-ADM-001` bars; `P-ADM-002` bootstrap replications).
2. **Multiple-testing control.** The family of candidates tested in a review window is corrected with
   the Benjamini–Hochberg procedure at `P-ADM-003` false-discovery rate; only candidates whose
   p-value passes the corrected threshold are admitted (AX-10 §3.5).
3. **Cost survival.** The improvement must remain positive under a cost stress of `P-ADM-004`
   (default: +50 % on fees and spread, ×1.5 on slippage) — an edge that dies under a plausible cost
   increase is not an edge (A1).
4. **Stability.** The sign of the feature's contribution must not flip across the two halves of the
   out-of-sample window, and its rolling information coefficient (IC) must have
   `P-ADM-005`-fraction of its mass on the expected side.
5. **Data validity.** Inputs verified: e.g. `taker_is_buy` verified by `VCH-11` for flow features;
   book state verified by `VCH-31` for book features (AX-02 §11).

Failure at review time demotes the feature to `T3` and removes it from the live path; two consecutive
failures delete it (`AX-01:§6`).

### 2.4 Sample-size gate (`AX-05:§2.4`)

Before any feature is *tested*, its minimum sample is computed and recorded (pre-registration,
AX-10 §3.1): for a per-bar IC of magnitude `ρ`, the number of independent bars required for a test at
`(α = 0.05, power = 0.80)` is approximately `n ≈ ( (z_{1−α/2} + z_{1−β}) / atanh(ρ) )²` `[D]`
(Fisher-z approximation), divided by the estimated autocorrelation inflation factor
`1 + 2Σ_k ρ_k` of the labelled outcome. **If `n` exceeds the data available, the test is not run** —
this prevents the classic "test everything on 300 bars" failure.

---

## 3. Feature families (`AX-05:§3`)

### 3.1 Price structure and trend (`AX-05:§3.1`)

| ID | Definition | Inputs / lag | Tier | Notes |
|---|---|---|---|---|
| `F-TS-MOM{K}` | `Σ_{u=1..K} r_{t−u}` for `K ∈ {4, 16, 96}` bars (≈1 h, 4 h, 1 d on 15 m bars) | final bars; lag = 1 bar + `L_bar` | `T1`/`T2` | canonical time-series momentum; overlapping windows are intentional and are handled by the label-overlap correction in testing |
| `F-SLOPE{K}` | OLS slope of `ln c` on time over the last `K` bars, divided by `σ̂√K` ⇒ a t-statistic-like scale-free slope | final bars | `T2` | invariant to price level; complements raw momentum |
| `F-DONJ{K}` | `(c_t − min(l_{t−K..t}))/(max(h_{t−K..t}) − min(l_{t−K..t})) ∈ [0,1]` | final bars | `T2` | position within the range; monotone transform of momentum only in trending regimes |
| `F-ER{K}` | Kaufman efficiency ratio: `|c_t − c_{t−K}| / Σ_{u} |c_{t−u+1} − c_{t−u}|` | final bars | `T2` | trend *quality*; high values = directional, low = choppy |
| `F-VR{K}` | Lo–MacKinlay variance ratio: `Var(r^{K}) / (K · Var(r^{1}))` minus 1, computed with overlapping windows and a heteroskedasticity-robust standard error | final bars | `T3` | statistical test for mean reversion vs trending; overlaps hurt power, so only research |

### 3.2 Volatility and distribution (`AX-05:§3.2`)

| ID | Definition | Tier | Notes |
|---|---|---|---|
| `F-RV{K}` | realised variance `Σ_{u=1..K} r_{t−u}²` (per-bar returns), and `σ̂ = √F-RV` | `T1` | base scale for stops, sizing, and normalisation |
| `F-EWMA-VOL` | `σ̂²_t = λ σ̂²_{t−1} + (1−λ) r_t²`, `λ = P-VOL-001` (default 0.94; `[D]`: standard decay for daily-equivalent horizons, re-fitted by `CAL-VOL-01`) | `T1` | fast-reacting scale |
| `F-PARK` | Parkinson: `σ̂² = (1/(4 ln 2)) · (ln(h/l))²` | `T2` | uses the range; efficient for OHLC bars |
| `F-GK` | Garman–Klass estimator using `o,h,l,c` | `T2` | lower variance than close-to-close under continuity assumptions |
| `F-YZ{K}` | Yang–Zhang estimator (drift- and gap-robust combination of overnight and intraday components) | `T2` | the default “benchmark” vol for reporting |
| `F-RS-JUMP` | realised semivariance split (`Σ r²·1{r>0}`, `Σ r²·1{r<0}`) and their ratio | `T2` | asymmetry; feeds the conditional-skew feature |
| `F-SKEW{K}`, `F-KURT{K}` | realised skewness/kurtosis of per-bar returns (risk-neutral-free, sample estimates with bias note) | `T2` | tail awareness; small-sample instability flagged |
| `F-HAR-RV` | HAR forecast: `RV_{t+1} = β0 + β_d RV_t + β_w mean(RV_{t−5..t}) + β_m mean(RV_{t−22..t})` with non-negativity constraints on `β` (NNLS) | `T1` | the baseline daily-horizon vol forecast; the label-overlap issue is handled by HAC standard errors |
| `F-VOV{K}` | volatility-of-volatility: `std(σ̂_{t−K..t}) / mean(σ̂_{t−K..t})` | `T2` | regime fragility |
| `F-VOLPCT{K}` | `z(F-RV{K})` over a long window (`K_long = P-VOL-002` bars) | `T1` | regime input: is today's vol high or low *relative to its own history* |

### 3.3 Liquidity, cost and microstructure (`AX-05:§3.3`)

| ID | Definition | Tier | Notes / gate |
|---|---|---|---|
| `F-SPR` | time-weighted mean `s_t` (bps) over the bar, from `bookTicker` | `T1` | direct cost input to AX-08 §3 |
| `F-D1` | notional resting within `P-UNI-002` bps of mid on each side (from `depth`) | `T1` for sizing, `T2` as a feature | requires `VCH-31` |
| `F-QIMB` | top-of-book imbalance `(bq − aq)/(bq + aq)` | `T2` | short-horizon pressure; needs verified quote stream |
| `F-MICRO` | microprice `= (bid·aq + ask·bq)/(aq + bq)`; feature = `(micro − mid)/mid` | `T2` | standard microstructure predictor of short-horizon drift |
| `F-AMIHUD` | `mean_{u} |r_u| / (quote_volume_u / 1e6)` over `K` bars | `T2` | price impact proxy; scale differs across assets ⇒ used cross-sectionally only |
| `F-ROLL` | Roll implied spread from the first-order autocovariance of intra-bar (or trade-to-trade) price changes: `2√max(0, −Cov(Δp_u, Δp_{u−1}))` | `T3` | the estimator is undefined when autocovariance ≥ 0; the max(0,·) form is used and the undefined cases are marked missing, never imputed |
| `F-CS` | Corwin–Schultz high–low spread estimator | `T3` | works from bars alone but is noisy and biased in trends; research-only |
| `F-KYLE` | Kyle's λ from the per-bar regression `r_t = λ · signed_volume_t + ε` where `signed_volume` uses the verified taker flag (bucket size `P-LIQ-001`) | `T2` (gate: `VCH-11`) | impact per unit flow; the regression uses HAC errors |
| `F-TIM` | trade intensity: `trades_t / median(trades)` over `P-LIQ-002` bars | `T2` | activity anomaly |
| `F-LARGE` | share of volume in trades whose size exceeds the `P-LIQ-003` quantile of the trailing size distribution | `T2` (gate: trade tape complete) | "whale" proxy, deliberately crude (no size-class inference is possible) |
| `F-SLIP-MEAS` | **self-measured** execution cost: `E[ (fill_price − decision_mid)/decision_mid ]` per side, from our own fills (AX-08 §3.3) | `T1` (feedback) | this is not a market feature but the empirical calibration of the cost model; it is listed here because it shares the pipeline |

### 3.4 Flow, positioning and carry (`AX-05:§3.4`)

| ID | Definition | Tier | Notes |
|---|---|---|---|
| `F-TAKER` | taker-buy share of volume: `taker_buy_quote / quote_volume` per bar (from REST klines, which provide the split `[V-DOC]`) minus 0.5, smoothed by EWMA(`P-FLOW-001`) | `T1` | the cheapest reliable flow signal: no dependence on the WS `m` flag |
| `F-FLOW-Z` | `z(F-TAKER)` over `P-FLOW-002` bars | `T1` | normalised pressure |
| `F-OI-QUAD` | quadrant classification of `(Δ ln price, Δ ln OI)` over `K` bars: `{price↑ OI↑: new longs; price↑ OI↓: short covering; price↓ OI↑: new shorts; price↓ OI↓: long liquidation}`, encoded as a 4-state categorical, plus the continuous pair `(Δln price, Δln OI)` normalised by their own rolling scales | `T2` | our own OI series (AX-02 §5.2); mechanism: forced/voluntary positioning changes have different forward dynamics |
| `F-CASCADE` | cascade score: `z(trade_intensity) + z(|r|) + max(0, −z(Δ ln OI)) + max(0, −z(funding change))`, then `z(·)` of the sum | `T2` | a *constructed* composite with a stated mechanism (forced deleveraging); all four components are separately monitored so the composite can be attributed |
| `F-FUND` | current funding rate (per settlement period, from `fundingRate`), and `F-FUND-ANN` = annualised cost of the *current* rate assuming the venue's stated period | `T1` | a direct cash-flow input to the net-return calculation, not a directional signal |
| `F-FUND-Z` | `z` of the funding rate over `P-FLOW-003` settlements using `historyFundingRate` | `T1` | carry regime |
| `F-BASIS` | `(last − mark)/mark` and `(index − mark)/mark` (the venue even exposes `change = (index − mark)/mark` in index-bar responses `[V-DOC]`), each `z`-scored | `T1` | premium/discount of the perp versus its composite index; a structural carry/positioning signal available *only* because the venue publishes both |
| `F-LSR` | long/short **account-count** ratio change, 30-day window only `[V-DOC]` | `T3` | retail-crowding proxy; count-weighted, so weak; research until proven |
| `F-FUNDDISP` | cross-sectional dispersion of `F-FUND` across the universe | `T2` | carry opportunities are relative |

### 3.5 Cross-sectional structure (`AX-05:§3.5`)

| ID | Definition | Tier | Notes |
|---|---|---|---|
| `F-XS-MOM` | cross-sectional rank of `F-TS-MOM{K}` within the universe, centred to `[−1,1]` | `T1` | long-short relative momentum; removes the common market factor |
| `F-BETA-KF` | Kalman-filtered dynamic beta of `i` on the market series (`BTC-SWAP-USDT`), state `[β]` with random-walk transition `σ_β = P-XS-001`, observation `r_i,t = α + β_t r_m,t + ε` | `T2` | betas drift; OLS betas over fixed windows are the rejected alternative |
| `F-RES-MOM` | residual momentum: `Σ (r_{i,u} − β̂_t r_{m,u})` over `K` bars, then `z` | `T2` | standard cross-sectional residual momentum |
| `F-CORR-DIST` | correlation distance `d_{ij} = √(0.5(1 − ρ_{ij}))` from EWMA correlations over `P-XS-002` bars | `T1` (for clustering) | input to HRP/NCO allocation (AX-07 §5) |
| `F-DISP` | cross-sectional standard deviation of `K`-bar returns | `T2` | regime: dispersion = stock-picker's or cluster-rotation regimes |
| `F-BREADTH` | fraction of universe with positive `K`-bar return | `T2` | regime breadth |
| `F-ABSORB` | absorption ratio: share of total variance explained by the top `k = P-XS-003` principal components of the universe return matrix | `T2` | systemic-fragility indicator (Kritzman-style); computed with a rolling window |
| `F-TURB` | turbulence: Mahalanobis distance of the latest universe return vector from its rolling mean/covariance (shrunk) | `T2` | a single-number "unusual day" measure used by the governor |

### 3.6 Calendar and session structure (`AX-05:§3.6`)

| ID | Definition | Tier | Notes |
|---|---|---|---|
| `F-SESS` | categorical: hour-of-day/day-of-week bucket (UTC) | `T3` | crypto trades 24/7, so calendar seasonality is weak and highly susceptible to false discovery; only research until `T-ADM-002` passes with FDR control |
| `F-FUNDWIN` | time to next settlement as a fraction of the period, plus the expected payment if the position is held through it | `T1` | operational: never hold a position through a settlement whose expected cost exceeds the expected remaining edge (AX-08 §3.2) |
| `F-LIQDOD` | intraday liquidity profile (mean spread/depth by hour bucket) | `T2` | used to schedule entries in the cheapest windows (execution, not alpha) |

### 3.7 Deliberately excluded (`AX-05:§3.7`)

With reasons, so that nobody re-adds them without an ADR:

1. **Order-book-history features beyond top-of-book moments** (e.g. queue imbalance time series): the
   venue gives no historical L2, and our own recording is too young for training (A3).
2. **Liquidation-data features** (true liquidation prints): not available as a stream; the
   `F-CASCADE` composite is the designed substitute, and it is labelled as a proxy.
3. **Cross-venue features** (other exchanges' prices/order books): excluded by C1 for trading; as
   *research-only* inputs they require an explicit owner decision and a data-licensing check
   (AX-04 §9 → `ADR-011`), and even then they may not feed the live kernel without a promotion.
4. **Sentiment/news/social features**: no reliable, reproducible, licensed source; unverifiable
   timestamping; violates L1/L4.
5. **Deep-learning sequence models**: they multiply parameters by orders of magnitude against a
   sample-size budget of thousands of bars, and they destroy interpretability of the *mechanism*
   (A3, A7). Reconsidered only if a `T3` study shows incremental value at equal or lower variance,
   which the admission test then decides.
6. **Every indicator that is a monotone transform of another** (e.g. RSI vs price position): admitted
   only if its transform demonstrably changes the *forecast* (test §2.3), because collinear duplicates
   inflate the apparent evidence.

---

## 4. Engineering rules for features (`AX-05:§4`)

1. **Declaration-first**: each feature lives in a registry entry (`feature_id`, `version`, `tier`,
   `family`, `formula_ref`, `inputs[]`, `lag_declared`, `min_history`, `parameters[]` with provenance,
   `monitor`, `kill_rule`) — code that computes a feature absent from the registry cannot load
   (`T-FEAT-001`).
2. **Pure functions**: `f(cursor, params) → value | insufficient_data`. No I/O, no wall clock, no
   randomness, no global state (`T-FEAT-002`).
3. **Determinism**: same cursor + same params ⇒ byte-identical output across runs and platforms;
   floating-point results are hashed and compared (`T-DET-002`).
4. **Missing data**: features return `insufficient_data` rather than a fabricated value; the forecaster
   must have a defined behaviour for missing inputs (AX-06 §4.4), never a silent zero.
5. **Warm-up**: `min_history` is declared and enforced; the system cannot trade an instrument until all
   `T1` features have passed their warm-up (AX-04 §9).
6. **Scaling**: any feature used in a linear model must be scaled by its own trailing robust scale
   (median/MAD over `P-FEAT-001` bars) rather than a fixed constant, so that regime shifts do not
   silently change a feature's effective weight; scaled values are clipped at `±P-FEAT-002` robust
   deviations with the clipping fraction monitored.
7. **No leakage**: overlapping-window features and overlapping labels are the main leakage vector;
   the leak tests (`T-LEAK-001`: future-shuffle invariance; `T-LEAK-002`: label-overlap inflation
   check) are mandatory for every `T1`/`T2` feature.

---

## 5. Monitoring and kill rules (`AX-05:§5`)

For every `T2`+ feature, the system maintains rolling statistics over `P-MON-001` bars:

- **Information coefficient** (Spearman rank correlation between the feature and the forward net
  return over its natural horizon), with a block-bootstrap confidence interval.
- **Contribution stability**: sign and magnitude of the model coefficient in the live model version.
- **Distribution drift**: population-stability-index-like measure `PSI = Σ (p̂_live − p̂_train) ·
  ln(p̂_live / p̂_train)` on decile bins, with the training distribution frozen at promotion time.
- **Availability**: fraction of bars with `insufficient_data`.

Kill rules (`AX-05:§5-R1`, all automatic, all journaled as `EV-FEAT-DEMOTE`):

| Condition | Action |
|---|---|
| `IC`'s posterior probability of being positive falls below `P-MON-002` for `P-MON-003` consecutive windows | demote to `T3`, remove from the live model, keep recording |
| `PSI > P-MON-004` | treat the feature as uncalibrated: shrink its effective weight to zero (AX-06 §5.2) until re-calibration |
| availability `< P-MON-005` | treat as unavailable; the forecaster's missing-data path handles it |
| two demotions within `P-MON-006` days | delete from the registry; a re-addition requires a new pre-registration |

Demotion is **safe by construction** because the forecaster's combination weights are functions of
estimated reliability (AX-06 §5.2): a demoted feature shrinks to zero weight automatically before any
human notices.
