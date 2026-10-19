//@version=6
// UCE v2 — Unified Composite Engine (sina). Primary range: 5m–1h.
// Linear, quote-margined perpetuals only; the contract type cannot be verified
// reliably from ticker metadata. Check multiplier, lot size and venue rules.
// Signals/state commit only at chart-bar close. Default HTF inputs use [1] with
// lookahead_on. Developing HTF mode CAN change historical signals after reload;
// it disables the simulator, outcome ledger and P3. Live plots are previews.
// Data-feed revisions, dataset changes and input changes can alter all history.
// Entries use the next bar's open and an immutable signal-time snapshot.
// OHLC path assumption: adverse extreme first in conservative mode, favorable
// first otherwise. Opening gaps execute first. BE/trailing changes take effect
// next bar; an already-crossed new stop becomes a next-open market exit.
// Fees/slippage are proportional cost proxies, not simulated execution prices.
// Partial exits are fractions of original size, not venue-rounded child orders.
// MAE/MFE follow the assumed path and stop at exit; DD is CLOSE-to-close MTM.
// P3 is an in-sample diagnostic on completed, entry-ordered base candidates,
// not proof of an edge. Missing ledger entries force P3 back to static.
// Scores, delta/CVD, price-level R/S Hurst and GBM bands are heuristic proxies.
// Funding, liquidation execution, spread, latency and order-book depth are not
// modeled. The approximate liquidation level is advisory, not a guarantee.
indicator("UCE — Unified Composite Engine v2 (sina)",
     overlay = true, max_lines_count = 120, max_labels_count = 120,
     max_boxes_count = 120, max_bars_back = 1000)
// === MODULE 1: INPUTS ===
g01 = "1 · MASTER"
showDash    = input.bool(true,  "Dashboard", group = g01, tooltip = "On-chart dashboard table. Off frees its budget.")
dashMode    = input.string("Full", "Dashboard mode", options = ["Full", "Compact"], group = g01, tooltip = "Compact = essentials for phone screens.")
showDiag    = input.bool(true,  "Diagnostics rows (P1/P2/P3 + ledger)", group = g01, tooltip = "Adaptive gates, sample sizes, expectancy Δ vs static, MAE/MFE p50, ledger overflow/invalid counters. Full mode only.")
showSignals = input.bool(true,  "Signal markers + plan labels", group = g01, tooltip = "Triangles + per-signal trade-plan label. Created once at signal close; never move. Display only — does NOT affect signal calculation.")
showZones   = input.bool(true,  "Order blocks + FVG boxes", group = g01, tooltip = "Active zones only; drawn on last bar to save budget. Display only.")
showPools   = input.bool(true,  "Liquidity pool lines", group = g01, tooltip = "Dotted lines at clustered unswept pivot pools (top N/side) + prev HTF bar H/L (2 heavier lines). Display only.")
showEmas    = input.bool(true,  "EMAs (fast/mid/slow)", group = g01, tooltip = "The three regime EMAs.")
showKalman  = input.bool(false, "Kalman line", group = g01, tooltip = "Kalman-smoothed price from the quant layer.")
showProj    = input.bool(true,  "GBM projection cone", group = g01, tooltip = "Dashed lines from last bar: median ±1.645σ (≈90%) lognormal quantiles. Analytic formula — NOT Monte Carlo.")
regimeBg    = input.bool(true,  "Regime background tint", group = g01, tooltip = "Faint tint: teal=trend up, red=trend down, amber=range.")
g02 = "2 · MODE / PRESET / HTF"
presetMode = input.string("Auto (by timeframe)", "Preset", options = ["Auto (by timeframe)", "Scalp (<5m)", "Intraday (5m–1h · primary)", "Swing (>1h–12h)", "Position (>12h)", "Manual"], group = g02, tooltip = "Auto bands: <5m Scalp · 5m–1h Intraday (the PRIMARY design/validation range) · >1h–12h Swing · >12h Position. Manual uses group 8 verbatim on EVERY chart TF (v1 bug B6 fixed).")
htfMode    = input.string("Auto (ratio band)", "HTF selection", options = ["Auto (ratio band)", "Manual override"], group = g02, tooltip = "Auto targets ≈12× the chart TF on a snapped grid — a design HYPOTHESIS re-centered on the 5m–1h primary range, NOT a measured optimum. Primary maps: 5m→1h, 15m→3h, 30m→6h, 1h→12h. Secondary: 1m→15m, 2h→1D, 4h→2D. Seconds/D/W/M get minimal valid mappings. Accept band 6–32×; out-of-band → HTF influence disabled + DEG flag. Overrides are validated against the same band; invalid → auto + warning.")
htfManual  = input.timeframe("240", "HTF override", group = g02, tooltip = "Used only in Manual override; must be 6–32× chart TF or it falls back to Auto with a warning.")
htfDevelop = input.bool(false, "Use developing HTF bar — REPAINTS", group = g02, tooltip = "ON = unshifted request with lookahead_off: HTF values move while the HTF bar forms (repaint, labeled). OFF (default) = last closed HTF bar, non-repainting.")
g03 = "3 · LAYERS"
useRegime    = input.bool(true, "L1 Regime (direction-aware)", group = g03, tooltip = "EMA stack/slope, DMI, trend correlation, HTF bias → symmetric UP/DOWN/RANGE/CHOP with evidence-agreement confidence.")
useLiquidity = input.bool(true, "L2 Liquidity (pools + sweeps)", group = g03, tooltip = "Pivot pools via 1-D density clustering (eps·ATR); symmetric pierce-&-reclaim sweeps with consumption + cooldown.")
useStructure = input.bool(true, "L3 Structure (BOS/CHoCH/MSS)", group = g03, tooltip = "Event-driven; levels consumed on break, re-armed on new pivot; MSS = CHoCH + HTF bias agreement.")
useShadows   = input.bool(true, "L3b Shadow candles (3)", group = g03, tooltip = "Doji-rejection, stop-hunt, fakeout. Symmetric.")
useHarmonic  = input.bool(true, "L3c Harmonics (4 canonical)", group = g03, tooltip = "Gartley/Bat/Butterfly/Crab on an alternation-enforced zigzag with canonical ratios (AB/XA, BC/AB, CD/BC, AD/XA) ± tolerance.")
useOrderflow = input.bool(true, "L4 Order flow (OB/FVG/Δ-proxy)", group = g03, tooltip = "OB lifecycle active→mitigated→breaker (correct semantics), FVG fill tracking, delta/CVD proxies (labeled).")
useMomentum  = input.bool(true, "L5 Momentum", group = g03, tooltip = "WaveTrend, Volume-Flow-Balance (windowed, bounded), AO, true double-smoothed STC, RSI, squeeze release.")
useRange     = input.bool(true, "L5b Range events", group = g03, tooltip = "Honest Wyckoff-style events: spring/upthrust (vol-confirmed), SOS/SOW (follow-through). No fake probabilities.")
useQuant     = input.bool(true, "L6 Quant (Kalman + z)", group = g03, tooltip = "Kalman slope + z-score extremes. Heuristic score, labeled.")
usePlaybook  = input.bool(true, "L6b Playbooks (4, symmetric)", group = g03, tooltip = "Sweep-reversal, spring/upthrust, OB+FVG confluence, squeeze breakout. Best one boosts its side.")
g04 = "4 · SIGNAL GATES & RATE GUARD"
thrLong  = input.float(86.0, "Long threshold", minval = 30, maxval = 90, group = g04, tooltip = "Min long score 0–100. Higher = fewer, stricter signals. Rec 58–70 (quality-over-quantity default 62; v1 parity 55).")
thrShort = input.float(86.0, "Short threshold", minval = 30, maxval = 90, group = g04, tooltip = "As above for shorts. v1 parity 55.")
thrDiff  = input.float(12.0, "Score gap", minval = 2, maxval = 30, group = g04, tooltip = "Required long/short score separation. Divided by 1.5 in trend regimes (v1 parity). Rec 8–15; v1=10.")
regRelax = input.float(6.0, "Trend-aligned relax", minval = 0, maxval = 15, group = g04, tooltip = "Threshold reduction for the regime-aligned side only. v1 parity 8.")
regBoost = input.float(0.15, "Regime boost ×conf", minval = 0, maxval = 0.5, step = 0.05, group = g04, tooltip = "Aligned side += confidence × this. v1 parity 0.15.")
pbBoost  = input.float(0.25, "Playbook boost ×score", minval = 0, maxval = 0.5, step = 0.05, group = g04, tooltip = "Playbook side += playbook score × this. v1 parity 0.25.")
minBars  = input.int(10, "Min bars between signals", minval = 0, maxval = 100, group = g04, tooltip = "Cooldown in bars (both directions). v1 parity 5.")
maxHr    = input.int(3, "Max signals / rolling hour (0=off)", minval = 0, maxval = 50, group = g04, tooltip = "Rolling-hour signal cap. On the primary 5m–1h range it rarely binds; it mainly matters if you drop to 1m–5m. 0 disables.")
maxDay   = input.int(12, "Max signals / rolling 24h (0=off)", minval = 0, maxval = 200, group = g04, tooltip = "Rolling 24h cap. 0 disables.")
lateAtr  = input.float(0.75, "Late after (×ATR)", minval = 0.1, maxval = 3, step = 0.05, group = g04, tooltip = "Plan marked LATE once |close − entry ref| exceeds this ×ATR. Shown on the dashboard (mobile: no hover needed).")
expireBars = input.int(20, "Plan expires after (bars)", minval = 1, maxval = 500, group = g04, tooltip = "Plan marked EXPIRED after this many bars.")
g05 = "5 · RISK & TRADE PLAN (manual LINEAR-perp entry)"
accEquity = input.float(200.0, "Account equity (quote)", minval = 10, group = g05, tooltip = "Equity used for position sizing on labels/dashboard and as sim start balance.")
riskPct   = input.float(2, "Risk % per trade", minval = 0.05, maxval = 5, step = 0.05, group = g05, tooltip = "Equity % lost if SL hits (before fees). Rec 0.25–1% for 5m–1h perps.")
levIn     = input.float(10.0, "Leverage ×", minval = 1, maxval = 125, group = g05, tooltip = "Used for margin estimate, notional cap and ≈liq display — does NOT change risk-based size.")
mmrPct    = input.float(0.5, "Maintenance margin % (≈)", minval = 0.1, maxval = 5, step = 0.1, group = g05, tooltip = "Exchange MMR for the APPROXIMATE isolated liq price: long ≈ entry×(1−1/lev+MMR). Venue tiers are NOT modeled.")
feeTaker  = input.float(0.02, "Taker fee % per fill", minval = 0, maxval = 0.5, step = 0.005, group = g05, tooltip = "Market-entry fee per fill; sim charges a round trip per closed fraction.")
slipPct   = input.float(0.02, "Slippage % per fill", minval = 0, maxval = 0.5, step = 0.005, group = g05, tooltip = "Manual market-order slippage per fill; charged like the fee.")
ctrMult   = input.float(1.0, "Contract multiplier (LINEAR)", minval = 0.000001, group = g05, tooltip = "Quote value of 1 qty unit per 1.0 of price. LINEAR (USDT/USDC-margined) contracts only; most linear perps use 1.0 (1 contract = 1 coin). INVERSE/coin-margined contracts are NOT modeled — qty/PnL math would be wrong for them. Check your venue's contract spec.")
qtyStep   = input.float(0.0, "Qty step (0 = off)", minval = 0.0, group = g05, tooltip = "Venue lot-size step; displayed qty is rounded DOWN to this step. 0 = no rounding. Min order size / min notional of the venue are NOT validated by the script — check them yourself.")
capNotional = input.bool(true, "Cap qty by equity × leverage", group = g05, tooltip = "Caps displayed qty so notional ≤ equity × leverage (margin ≤ equity). When the cap binds, the label shows CAP and your actual risk at SL is LESS than the configured risk %.")
useSwingSL = input.bool(true, "Swing-based SL", group = g05, tooltip = "SL at last confirmed structure pivot, clamped to the ATR min/max below. Off = pure ATR stop.")
slAtrMin  = input.float(1.5, "SL min distance ×ATR", minval = 0.3, maxval = 5, step = 0.1, group = g05, tooltip = "Floor for stop distance.")
slAtrMax  = input.float(3.5, "SL max distance ×ATR", minval = 1, maxval = 10, step = 0.1, group = g05, tooltip = "Cap for stop distance (fat-tail protection on perps).")
tp1R = input.float(1.0, "TP1 (R)", minval = 0.3, maxval = 5, step = 0.1, group = g05, tooltip = "First target in R (R = stop distance). Raising it lowers hit rate, raises payoff.")
tp2R = input.float(2.0, "TP2 (R)", minval = 0.5, maxval = 8, step = 0.1, group = g05, tooltip = "Second target; activates the trail.")
tp3R = input.float(3.5, "TP3 (R)", minval = 1, maxval = 12, step = 0.1, group = g05, tooltip = "Runner target.")
tp1Pct = input.float(40.0, "TP1 close % of ORIGINAL", minval = 5, maxval = 90, group = g05, tooltip = "Percent of the ORIGINAL position closed at TP1 (v1 ambiguity C12 fixed). TP1%+TP2% is clamped to ≤90 at runtime.")
tp2Pct = input.float(30.0, "TP2 close % of ORIGINAL", minval = 5, maxval = 90, group = g05, tooltip = "Percent of ORIGINAL closed at TP2; remainder runs to TP3/trail/SL.")
beAfterTp1 = input.bool(true, "Breakeven after TP1", group = g05, tooltip = "Move SL to entry after TP1 (exit ≈ −fees on that fraction; honest).")
trailAtr = input.float(1.0, "Trail ×ATR after TP2", minval = 0.3, maxval = 5, step = 0.1, group = g05, tooltip = "Chandelier-style ratchet from bar extreme once TP2 fills.")
hurstTp  = input.bool(false, "Scale TPs by Hurst PROXY", group = g05, tooltip = "TP multiple ×(0.75+0.5·Hurst-proxy). Hurst here is a biased single-window R/S proxy — off by default.")
g06 = "6 · SIMULATOR"
simOn   = input.bool(true, "Enable simulator", group = g06, tooltip = "Indicative sim: entry next bar open, exits from entry bar onward, fees+slippage on every closed fraction, whole-trade R accounting. Disabled on non-standard charts. NOT exchange-accurate.")
simComp = input.bool(false, "Compound", group = g06, tooltip = "Risk % of current sim equity instead of fixed start equity.")
conserv = input.bool(true, "Conservative same-bar (SL first)", group = g06, tooltip = "If SL and TP are both inside one bar, assume SL filled first. OFF = optimistic (TP first, like v1 — biased).")
killN    = input.int(5, "Kill switch: consecutive losses", minval = 2, maxval = 10, group = g06, tooltip = "Whole-trade R < 0 streak that halts new entries.")
killCool = input.int(30, "Kill cooldown (bars)", minval = 5, maxval = 200, group = g06, tooltip = "Bars to stay halted.")
onePos   = input.bool(true, "One position at a time", group = g06, tooltip = "Block new signals while the sim position is open (matches manual trading).")
g07 = "7 · ADAPTIVE (normalization + ledger)"
p1On  = input.bool(true, "P1 sweep-gate NORMALIZATION", group = g07, tooltip = "Gate = blend of static default and the rolling q-quantile of ALL detected sweep scores (recorded BEFORE gating — no censoring). Keeps acceptance rate stable across vol regimes. This is normalization, not optimization.")
p1Q   = input.float(0.70, "P1 quantile", minval = 0.4, maxval = 0.95, step = 0.05, group = g07, tooltip = "Higher = stricter gate.")
p1N   = input.int(50, "P1 window (events)", minval = 20, maxval = 200, group = g07, tooltip = "Rolling event count; also full-confidence blend size.")
p1Min = input.int(20, "P1 min events", minval = 5, maxval = 100, group = g07, tooltip = "Below this the static default is used.")
p1Hyst = input.float(3.0, "P1 hysteresis (pts)", minval = 0, maxval = 10, group = g07, tooltip = "Gate moves only if the candidate differs by ≥ this (min dwell 10 bars). Bounds 40–90 fixed.")
p1Freeze = input.bool(false, "P1 freeze", group = g07, tooltip = "Hold the current gate; stop updating.")
swGateStatic = input.float(55.0, "Sweep gate static default", minval = 40, maxval = 90, group = g07, tooltip = "Used when P1 is off/insufficient; blend anchor otherwise.")
p2On  = input.bool(true, "P2 OB-displacement NORMALIZATION", group = g07, tooltip = "OB creation gate = blend of preset static and rolling q-quantile of range/ATR over the window (ALL bars, pre-gate). Keeps zone-creation selectivity stable. Normalization, not optimization.")
p2Q   = input.float(0.80, "P2 quantile", minval = 0.5, maxval = 0.95, step = 0.05, group = g07, tooltip = "Higher = rarer OBs.")
p2N   = input.int(200, "P2 window (bars)", minval = 50, maxval = 500, group = g07, tooltip = "Rolling bar count.")
p2Min = input.int(50, "P2 min bars", minval = 20, maxval = 200, group = g07, tooltip = "Below this the static preset is used.")
p2Refresh = input.int(10, "P2 refresh (bars)", minval = 1, maxval = 50, group = g07, tooltip = "Quantile recompute cadence (dwell = 2× this). Bounds 1.1–3.0 fixed.")
p2Hyst = input.float(0.05, "P2 hysteresis", minval = 0, maxval = 0.5, step = 0.01, group = g07, tooltip = "Min gate change to apply.")
p2Freeze = input.bool(false, "P2 freeze", group = g07, tooltip = "Hold current gate.")
p3On  = input.bool(false, "P3 outcome threshold step (diagnostics always on)", group = g07, tooltip = "DEFAULT OFF. Steps the entry threshold +2/+4/+6 only when the ledger shows the current stream losing (≤ −margin, n≥min) AND the higher step beating it by ≥ margin on the SAME uncensored stream. Step-ups are BLOCKED while any ledger overflow drop exists (see LEDGER row). Auto-reverts to static when adaptive fails to beat static by the revert margin. The dashboard shows what P3 WOULD do while it is off (genuine parallel diagnostics, not a zero-by-construction delta).")
p3MinN = input.int(30, "P3 min resolved signals", minval = 10, maxval = 100, group = g07, tooltip = "Per candidate, before it may act.")
p3Margin = input.float(0.10, "P3 step margin (R)", minval = 0.02, maxval = 0.5, step = 0.01, group = g07, tooltip = "Required superiority / loss margin.")
p3Rev = input.float(0.05, "P3 revert margin (R)", minval = 0.0, maxval = 0.5, step = 0.01, group = g07, tooltip = "Adaptive must beat static by ≥ this or it reverts.")
g08 = "8 · ENGINE (advanced; Manual preset uses these)"
swingLiqIn = input.int(5, "Liquidity pivot L/R", minval = 2, maxval = 50, group = g08, tooltip = "Pivot wing for liquidity pools. Confirmation lags this many bars (causal).")
swingStrIn = input.int(4, "Structure pivot L/R", minval = 2, maxval = 30, group = g08, tooltip = "Pivot wing for BOS/CHoCH/zigzag.")
atrLenIn   = input.int(14, "ATR length", minval = 5, maxval = 100, group = g08, tooltip = "Risk/normalization ATR.")
obThrIn    = input.float(1.5, "OB displacement static ×ATR", minval = 1, maxval = 5, step = 0.1, group = g08, tooltip = "Static OB gate (P2 anchor).")
wt1In = input.int(9, "WaveTrend ch.", minval = 5, maxval = 50, group = g08, tooltip = "WT channel EMA.")
wt2In = input.int(18, "WaveTrend avg.", minval = 5, maxval = 100, group = g08, tooltip = "WT average length.")
vfiLenIn = input.int(60, "Flow window (VFB)", minval = 10, maxval = 500, group = g08, tooltip = "Volume-Flow-Balance window (windowed & bounded; v1 VFI drift B5 fixed).")
stcF = input.int(23, "STC fast", minval = 5, maxval = 100, group = g08, tooltip = "STC MACD fast EMA.")
stcS = input.int(50, "STC slow", minval = 10, maxval = 200, group = g08, tooltip = "STC MACD slow EMA.")
stcC = input.int(10, "STC cycle", minval = 3, maxval = 50, group = g08, tooltip = "Stochastic window (true double-smoothed STC).")
kalQ = input.float(0.05, "Kalman q", minval = 0.001, maxval = 1, step = 0.005, group = g08, tooltip = "Process noise; higher = faster.")
kalR = input.float(1.0, "Kalman r", minval = 0.01, maxval = 10, step = 0.01, group = g08, tooltip = "Measurement noise; higher = smoother.")
zLen = input.int(50, "Z-score length", minval = 10, maxval = 200, group = g08, tooltip = "Mean/σ window for z.")
regLen = input.int(50, "Regime corr length", minval = 20, maxval = 200, group = g08, tooltip = "close↔time correlation window (trend quality vote).")
adxLen = input.int(14, "DMI length", minval = 5, maxval = 50, group = g08, tooltip = "DI/ADX length.")
adxTrend = input.float(20.0, "ADX trend floor", minval = 10, maxval = 40, group = g08, tooltip = "ADX ≥ this counts as trending evidence.")
rangeLen = input.int(20, "Range window", minval = 10, maxval = 100, group = g08, tooltip = "Prior-window H/L for spring/upthrust/SOS/SOW.")
volSpike = input.float(1.3, "Volume spike ×avg", minval = 1, maxval = 3, step = 0.1, group = g08, tooltip = "Volume confirmation multiple.")
clustEps = input.float(0.30, "Pool cluster eps ×ATR", minval = 0.05, maxval = 1, step = 0.05, group = g08, tooltip = "Pivot grouping distance for pools (1-D density clustering).")
sweepCool = input.int(8, "Sweep cooldown (bars/side)", minval = 0, maxval = 50, group = g08, tooltip = "Per-side lockout after an accepted sweep (B2 fix).")
sweepTgtPen = input.float(0.35, "Sweep target penetration ×ATR", minval = 0.1, maxval = 1, step = 0.05, group = g08, tooltip = "Ideal pierce depth (score peak).")
sweepMaxPen = input.float(1.25, "Sweep max penetration ×ATR", minval = 0.5, maxval = 3, step = 0.05, group = g08, tooltip = "Deeper than this = breakdown, not sweep.")
fvgMin = input.float(0.15, "FVG min size ×ATR", minval = 0.05, maxval = 1, step = 0.05, group = g08, tooltip = "Minimum 3-candle gap.")
fvgFill = input.float(0.5, "FVG mitigation fill", minval = 0.1, maxval = 1, step = 0.1, group = g08, tooltip = "Fraction filled that mitigates the gap.")
obLook = input.int(10, "OB scan depth", minval = 3, maxval = 30, group = g08, tooltip = "Bars back to find the opposite candle.")
htfEmaLen = input.int(50, "HTF EMA length", minval = 10, maxval = 200, group = g08, tooltip = "Bias EMA computed on the HTF.")
projLen  = input.int(20, "Projection stats window", minval = 10, maxval = 200, group = g08, tooltip = "Log-return μ/σ window for GBM cone.")
projBars = input.int(8, "Projection horizon (bars)", minval = 2, maxval = 50, group = g08, tooltip = "Cone length.")
emaFastL = input.int(21, "EMA fast", minval = 5, maxval = 500, group = g08, tooltip = "Regime EMA stack.")
emaMidL  = input.int(50, "EMA mid", minval = 5, maxval = 500, group = g08, tooltip = "Regime EMA stack.")
emaSlowL = input.int(200, "EMA slow", minval = 5, maxval = 500, group = g08, tooltip = "Regime EMA stack; dominates warm-up.")
harmTol = input.float(0.06, "Harmonic ratio tolerance", minval = 0.01, maxval = 0.2, step = 0.01, group = g08, tooltip = "±fraction around canonical bands.")
decayPts = input.float(4.0, "Memory decay (pts/bar)", minval = 0.5, maxval = 20, step = 0.5, group = g08, tooltip = "Event-memory cooling, scaled ×(ATR/ATR50) clamped 0.5–2; neutral ×1 while ATR warms up (F-01). Decays to 0 (B4 fix).")
g09 = "9 · FUSION WEIGHTS (neutral regime)"
wStructIn = input.float(0.20, "w structure", minval = 0, maxval = 1, step = 0.05, group = g09, tooltip = "Neutral-regime weight. Trend/range profiles use v1 parity constants (see tooltip of the switch).")
wLiqIn    = input.float(0.20, "w liquidity", minval = 0, maxval = 1, step = 0.05, group = g09, tooltip = "Neutral weight.")
wMomIn    = input.float(0.15, "w momentum", minval = 0, maxval = 1, step = 0.05, group = g09, tooltip = "Neutral weight.")
wImbIn    = input.float(0.15, "w order flow", minval = 0, maxval = 1, step = 0.05, group = g09, tooltip = "Neutral weight.")
wRangeIn  = input.float(0.10, "w range events", minval = 0, maxval = 1, step = 0.05, group = g09, tooltip = "Neutral weight.")
wQuantIn  = input.float(0.10, "w quant", minval = 0, maxval = 1, step = 0.05, group = g09, tooltip = "Neutral weight.")
wHarmIn   = input.float(0.05, "w harmonic", minval = 0, maxval = 1, step = 0.05, group = g09, tooltip = "Neutral weight.")
wShadIn   = input.float(0.05, "w shadow", minval = 0, maxval = 1, step = 0.05, group = g09, tooltip = "Neutral weight.")
profShift = input.bool(true, "Regime weight profiles (v1 parity)", group = g09, tooltip = "Trend: S.25 L.15 M.20 I.15 R.10 Q.10 H.05 D.05 · Range: S.15 L.30 M.10 I.15 R.20 Q.10 H.05 D.05. Off = neutral weights always.")
g10 = "10 · LEGACY PARITY (A/B)"
legacyAll = input.bool(false, "Legacy parity master (v1 signal logic)", group = g10, tooltip = "Forces the three switches below ON. For full numeric parity also set: thresholds 55/55/10, relax 8, min-bars 5, rate guards 0, P1/P2/P3 off. Parity scope is documented — fills are NOT reproduced (v1 fills were lookahead-biased).")
legAsymIn  = input.bool(false, "Legacy #2: UP-only regime boost/relax", group = g10, tooltip = "Reproduces v1 defect A5's EFFECT: shorts get no regime boost/relax. The old directionless classifier itself is NOT reproduced.")
legSweepIn = input.bool(false, "Legacy #3: v1 sweep rules", group = g10, tooltip = "Most-recent-pivot only, bull side without reclaim, no consumption/cooldown/gate (B1/B2 behavior).")
legStructIn = input.bool(false, "Legacy #4: v1 structure persistence", group = g10, tooltip = "Break levels not consumed (re-fire) + memory floor 50 on the trend side (B3/B4 behavior).")
g11 = "11 · OPTIONAL TIME FILTER"
sessOn = input.bool(false, "Restrict signals to UTC window", group = g11, tooltip = "Crypto trades 24/7 — this is an optional liquidity-window filter, not an FX session. Default OFF.")
sessWin = input.session("1200-2000", "UTC window", group = g11, tooltip = "HHMM-HHMM, UTC, all days.")
g12 = "12 · STYLE"
colBull = input.color(color.new(#26a69a, 0), "Bull color", group = g12, tooltip = "Teal — CVD-safe pair with the red.")
colBear = input.color(color.new(#ef5350, 0), "Bear color", group = g12, tooltip = "Red.")
colWarn = input.color(color.new(#ff9800, 0), "Warn/accent", group = g12, tooltip = "Amber accents.")
colNeut = input.color(color.new(#9598a1, 0), "Neutral text", group = g12, tooltip = "Dim gray.")
dashPos = input.string("top_right", "Dashboard anchor", options = ["top_right", "bottom_right", "top_left", "bottom_left"], group = g12, tooltip = "Corner anchor; pick the one that does not cover price on your phone.")
dashSize = input.string("tiny", "Dashboard text", options = ["tiny", "small", "normal"], group = g12, tooltip = "tiny recommended on mobile.")
dashBg  = input.color(color.new(#131722, 15), "Dashboard bg", group = g12, tooltip = "Table background.")
lblSize = input.string("tiny", "Label text", options = ["tiny", "small", "normal"], group = g12, tooltip = "Plan label size; small recommended on phones.")
lblMax  = input.int(30, "Max plan labels", minval = 2, maxval = 100, group = g12, tooltip = "Oldest labels are deleted beyond this. Presentation only — the latest plan always stays visible on the dashboard; signal calculation is unaffected.")
maxZoneDraw = input.int(6, "Max zones drawn / type", minval = 2, maxval = 20, group = g12, tooltip = "Active OBs and FVGs drawn, newest first. Drawing cap only — zone state/logic is unaffected.")
poolShow = input.int(5, "Pool lines / side", minval = 1, maxval = 10, group = g12, tooltip = "Strongest pools drawn per side. Drawing cap only.")
emaFc = input.color(color.new(#ffd600, 0), "EMA fast color", group = g12, tooltip = "Line color.")
emaMc = input.color(color.new(#ff9800, 0), "EMA mid color", group = g12, tooltip = "Line color.")
emaSc = input.color(color.new(#2962ff, 0), "EMA slow color", group = g12, tooltip = "Line color.")
emaFw = input.int(1, "EMA fast width", minval = 1, maxval = 5, group = g12, tooltip = "Line width.")
emaMw = input.int(1, "EMA mid width", minval = 1, maxval = 5, group = g12, tooltip = "Line width.")
emaSw = input.int(2, "EMA slow width", minval = 1, maxval = 5, group = g12, tooltip = "Line width.")
obBullCol = input.color(color.new(#26a69a, 85), "Bull OB fill", group = g12, tooltip = "Includes transparency.")
obBearCol = input.color(color.new(#ef5350, 85), "Bear OB fill", group = g12, tooltip = "Includes transparency.")
fvgBullCol = input.color(color.new(#26a69a, 92), "Bull FVG fill", group = g12, tooltip = "Includes transparency.")
fvgBearCol = input.color(color.new(#ef5350, 92), "Bear FVG fill", group = g12, tooltip = "Includes transparency.")
// === MODULE 2: PRESET + HTF RESOLUTION ===
// Primary design range 5m–1h → band 2 (Intraday). 5m is PRIMARY, not scalp (F-07).
tfSec = timeframe.in_seconds(timeframe.period)
band = presetMode == "Manual" ? 0 :
     presetMode == "Scalp (<5m)" ? 1 :
     presetMode == "Intraday (5m–1h · primary)" ? 2 :
     presetMode == "Swing (>1h–12h)" ? 3 :
     presetMode == "Position (>12h)" ? 4 :
     tfSec < 300 ? 1 : tfSec <= 3600 ? 2 : tfSec <= 43200 ? 3 : 4
pivLiqLen = band == 1 ? 4 : band == 2 ? 6 : band == 3 ? 9 : band == 4 ? 12 : swingLiqIn
pivStrLen = band == 1 ? 3 : band == 2 ? 5 : band == 3 ? 7 : band == 4 ? 9 : swingStrIn
atrLen    = band == 1 ? 12 : band == 2 ? 14 : band == 3 ? 14 : band == 4 ? 20 : atrLenIn
wtL1      = band == 1 ? 8 : band == 2 ? 10 : band == 3 ? 12 : band == 4 ? 14 : wt1In
wtL2      = band == 1 ? 16 : band == 2 ? 21 : band == 3 ? 26 : band == 4 ? 28 : wt2In
vfiLen    = band == 1 ? 50 : band == 2 ? 60 : band == 3 ? 80 : band == 4 ? 100 : vfiLenIn
obStatic  = band == 1 ? 1.3 : band == 2 ? 1.5 : band == 3 ? 1.6 : band == 4 ? 1.8 : obThrIn
// HTF ratio ladder re-centered to ≈12× across the grid (F-06). Design HYPOTHESIS,
// not a measured optimum. Primary: 5m→60, 15m→180, 30m→360, 1h→720 (all 12×).
// Secondary: 1m→15 (15×), 2h→D (12×), 4h→2D (12×). Robustness: 6h/12h→5D, D→2W, W→3M, M→12M.
htfAuto = tfSec <= 25 ? "3" :
     tfSec <= 90 ? "15" :
     tfSec <= 180 ? "30" :
     tfSec <= 450 ? "60" :
     tfSec <= 720 ? "120" :
     tfSec <= 1080 ? "180" :
     tfSec <= 2100 ? "360" :
     tfSec <= 3900 ? "720" :
     tfSec <= 7200 ? "D" :
     tfSec <= 21600 ? "2D" :
     tfSec <= 43200 ? "5D" :
     tfSec <= 86400 ? "2W" :
     tfSec <= 604800 ? "3M" : "12M"
ovSec = timeframe.in_seconds(htfManual)
ovRatio = ovSec / math.max(tfSec, 1)
ovValid = ovRatio >= 6 and ovRatio <= 32
htfUsed = htfMode == "Manual override" and ovValid ? htfManual : htfAuto
htfRatio = timeframe.in_seconds(htfUsed) / math.max(tfSec, 1)
htfDegraded = htfRatio < 6 or htfRatio > 32
htfOvWarn = htfMode == "Manual override" and not ovValid
// === MODULE 3: TYPES + UTILITIES ===
type Zone
    bool  isBull
    float top
    float bot
    int   born
    int   state // 0 active · 1 mitigated · 2 breaker (polarity flipped)
type Trade
    int   dir
    float en
    float sl
    float rd
    float t1
    float t2
    float t3
    float rem
    float banked
    bool  h1
    bool  h2
    bool  trailOn
    float mae
    float mfe
    bool  closed
    float rFin
    float margin
    int   bEn
    float rm
f_clamp(float v, float lo, float hi) => math.max(lo, math.min(hi, v))
f_fmt(float v) => str.tostring(v, format.mintick)
f_pushCap(array<float> a, float v, int cap) =>
    array.push(a, v)
    if array.size(a) > cap
        array.shift(a)
f_quantA(array<float> a, float q) =>
    s = array.size(a)
    if s == 0
        float(na)
    else
        t = array.copy(a)
        array.sort(t, order.ascending)
        idx = int(math.floor(q * (s - 1) + 0.5))
        array.get(t, int(f_clamp(idx, 0, s - 1)))
f_pools(array<float> src, float eps) =>
    c = array.new_float()
    n = array.new_int()
    sz = array.size(src)
    if sz > 0 and eps > 0
        t = array.copy(src)
        array.sort(t, order.ascending)
        runS = array.get(t, 0)
        runN = 1
        if sz > 1
            for i = 1 to sz - 1
                v = array.get(t, i)
                if v - array.get(t, i - 1) <= eps
                    runS += v
                    runN += 1
                else
                    array.push(c, runS / runN)
                    array.push(n, runN)
                    runS := v
                    runN := 1
        array.push(c, runS / runN)
        array.push(n, runN)
    [c, n]
f_stoch(float s, simple int len) =>
    lo = ta.lowest(s, len)
    hi = ta.highest(s, len)
    (s - lo) / math.max(hi - lo, 1e-10) * 100.0
f_in(float x, float lo, float hi) => x >= lo * (1 - harmTol) and x <= hi * (1 + harmTol)
// === MODULE 4: CORE SERIES (all ta.* unconditional) ===
atrVal = ta.atr(atrLen)
atrSlow = ta.atr(50)
atrOk = not na(atrVal) and not na(atrSlow) and atrSlow > 0
// F-01 ROOT-CAUSE FIX: na-safe, finite, NEUTRAL volatility scale. In the Stage-2
// source, na ATR during warm-up made volScale na → dk na → persistent memories
// poisoned permanently (math.max(0, na) = na) → Score L/S = NaN forever.
volScale = atrOk ? f_clamp(atrVal / atrSlow, 0.5, 2.0) : 1.0
emaF = ta.ema(close, emaFastL)
emaM = ta.ema(close, emaMidL)
emaSlo = ta.ema(close, emaSlowL)
rsiV = ta.rsi(close, 14)
[diP, diM, adxV] = ta.dmi(adxLen, adxLen)
volOk = not na(volume)
vol = nz(volume, 0.0)
volSma = ta.sma(vol, 20)
volUsable = volOk and volSma > 0 // F-08: all-zero volume is NOT healthy flow
volR = volUsable ? vol / volSma : 1.0
corrV = ta.correlation(close, bar_index, regLen)
// squeeze
bbBasis = ta.sma(close, 20)
bbDev = 2.0 * ta.stdev(close, 20)
kcRng = 1.5 * ta.sma(ta.tr, 20)
sqzOn = (bbBasis - bbDev > bbBasis - kcRng) and (bbBasis + bbDev < bbBasis + kcRng)
sqzRel = sqzOn[1] and not sqzOn
momH = ta.linreg(close - (ta.highest(high, 20) + ta.lowest(low, 20)) / 2.0, 20, 0)
// WaveTrend
wtEsa = ta.ema(hlc3, wtL1)
wtDe = ta.ema(math.abs(hlc3 - wtEsa), wtL1)
wtCi = (hlc3 - wtEsa) / math.max(0.015 * wtDe, 1e-10)
wt1 = ta.ema(wtCi, wtL2)
wt2 = ta.sma(wt1, 4)
// Volume Flow Balance (windowed, bounded — replaces v1 VFI drift)
vfbCut = 0.2 * ta.atr(30)
vfbMf = hlc3 - hlc3[1]
vfbDir = vfbMf > vfbCut ? 1.0 : vfbMf < -vfbCut ? -1.0 : 0.0
vfb = 100.0 * math.sum(vfbDir * vol, vfiLen) / math.max(math.sum(vol, vfiLen), 1e-10)
vfbSig = ta.ema(vfb, 10)
// AO
ao = ta.sma(hl2, 5) - ta.sma(hl2, 34)
aoSig = ta.sma(ao, 9)
// True double-smoothed STC
stcMacd = ta.ema(close, stcF) - ta.ema(close, stcS)
stcK1 = f_stoch(stcMacd, stcC)
stcD1 = ta.ema(stcK1, 3)
stcK2 = f_stoch(stcD1, stcC)
stcV = ta.ema(stcK2, 3)
// z, hurst proxy, delta proxies
zV = (close - ta.sma(close, zLen)) / math.max(ta.stdev(close, zLen), 1e-10)
hMean = ta.sma(close, 50)
hSd = ta.stdev(close, 50)
f_hurst() =>
    if na(hSd) or na(hMean) // F-16: warm-up guard, neutral 0.5
        0.5
    else
        sdE = math.max(hSd, 1e-10)
        cum = 0.0
        mx = 0.0
        mn = 0.0
        for i = 0 to 49
            cum += close[i] - hMean
            mx := math.max(mx, cum)
            mn := math.min(mn, cum)
        rs = (mx - mn) / sdE
        h = rs > 0 ? math.log(rs) / math.log(50) : 0.5
        f_clamp(h, 0.0, 1.0)
hurstV = f_hurst() // PROXY: single-window R/S, biased; display + optional TP scale only
rngBar = high - low
deltaRaw = rngBar > 0 and volUsable ? vol * (close - open) / rngBar : 0.0 // intrabar PROXY
deltaSm = ta.ema(deltaRaw, 14)
cvdW = math.sum(deltaRaw, 50) // windowed CVD PROXY (bounded, no drift)
cvdSig = ta.ema(cvdW, 20)
// pivots (confirm with wing-length lag — causal)
phL = ta.pivothigh(high, pivLiqLen, pivLiqLen)
plL = ta.pivotlow(low, pivLiqLen, pivLiqLen)
phS = ta.pivothigh(high, pivStrLen, pivStrLen)
plS = ta.pivotlow(low, pivStrLen, pivStrLen)
hh20 = ta.highest(high, 20)
ll20 = ta.lowest(low, 20)
// GBM analytic quantiles (NOT Monte Carlo)
logRet = close > 0 and close[1] > 0 ? math.log(close / close[1]) : 0.0
gMu = ta.sma(logRet, projLen)
gSd = ta.stdev(logRet, projLen)
gDrift = gMu - 0.5 * gSd * gSd
projUp = close * math.exp(gDrift * projBars + gSd * math.sqrt(projBars) * 1.645)
projDn = close * math.exp(gDrift * projBars - gSd * math.sqrt(projBars) * 1.645)
projMid = close * math.exp(gDrift * projBars)
// === MODULE 5: HTF CONTEXT (documented pattern) ===
// Confirmed (non-repainting): every field expr[1] WITH lookahead_on.
[cC, cE, cEp, cH, cL] = request.security(syminfo.tickerid, htfUsed,
     [close[1], ta.ema(close, htfEmaLen)[1], ta.ema(close, htfEmaLen)[2], high[1], low[1]],
     lookahead = barmerge.lookahead_on)
// Developing (REPAINTS while HTF bar forms): unshifted expr with lookahead_off.
[dC, dE, dEp, dH, dL] = request.security(syminfo.tickerid, htfUsed,
     [close, ta.ema(close, htfEmaLen), ta.ema(close, htfEmaLen)[1], high, low],
     lookahead = barmerge.lookahead_off)
htfC = htfDevelop ? dC : cC
htfE = htfDevelop ? dE : cE
htfEp = htfDevelop ? dEp : cEp
htfH = htfDevelop ? dH : cH
htfL = htfDevelop ? dL : cL
htfWarm = htfDevelop ? (na(dC) or na(dE) or na(dEp)) : (na(cC) or na(cE) or na(cEp)) // F-15: HTF warm-up ≠ ratio-degraded
htfOk = not htfWarm and not htfDegraded
htfBias = not htfOk ? 0 : htfC > htfE and htfE > htfEp ? 1 : htfC < htfE and htfE < htfEp ? -1 : htfC > htfE ? 1 : htfC < htfE ? -1 : 0
// === MODULE 6: REGIME (direction-aware, honest confidence) ===
vStack = emaF > emaM and emaM > emaSlo ? 1 : emaF < emaM and emaM < emaSlo ? -1 : 0
vSlope = emaM > emaM[3] ? 1 : emaM < emaM[3] ? -1 : 0
vDmi = diP > diM + 2 ? 1 : diM > diP + 2 ? -1 : 0
vCorr = corrV > 0.3 ? 1 : corrV < -0.3 ? -1 : 0
vHtf = htfBias
vPx = close > emaSlo ? 1 : close < emaSlo ? -1 : 0
dirSum = vStack + vSlope + vDmi + vCorr + vHtf + vPx
regDir = useRegime ? (dirSum >= 2 and adxV >= adxTrend ? 1 : dirSum <= -2 and adxV >= adxTrend ? -1 : 0) : 0
regTrend = regDir != 0
regStrong = regTrend and adxV >= adxTrend * 1.5 and math.abs(dirSum) >= 4
atrRatio = atrVal / math.max(atrSlow, 1e-10)
regRange = not regTrend and adxV < adxTrend
regName = regDir == 1 ? (regStrong ? "T↑S" : "T↑") : regDir == -1 ? (regStrong ? "T↓S" : "T↓") : regRange and (sqzOn or atrRatio < 0.8) ? "R·C" : regRange and atrRatio > 1.2 ? "R·E" : regRange ? "R" : "CHOP"
regConf = f_clamp(math.abs(dirSum) / 6.0 * 100.0, 0, 100) // evidence agreement, not probability
legAsym = legacyAll or legAsymIn
legSweep = legacyAll or legSweepIn
legStruct = legacyAll or legStructIn
// === MODULE 7: STATE DECLARATIONS ===
var array<float> loPx = array.new_float()
var array<int> loBar = array.new<int>()
var array<float> hiPx = array.new_float()
var array<int> hiBar = array.new<int>()
var array<float> poolLoC = array.new_float()
var array<int> poolLoN = array.new<int>()
var array<float> poolHiC = array.new_float()
var array<int> poolHiN = array.new<int>()
var array<float> p1Buf = array.new_float()
var array<float> p2Buf = array.new_float()
var float p1Gate = swGateStatic
var int p1Last = 0
var float p2Gate = na
var int p2Last = 0
if na(p2Gate)
    p2Gate := obStatic
var int coolLo = 0
var int coolHi = 0
var float memSwB = 0.0
var float memSwS = 0.0
var float memStB = 0.0
var float memStS = 0.0
var float memShB = 0.0
var float memShS = 0.0
var float memHaB = 0.0
var float memHaS = 0.0
var float memRgB = 0.0
var float memRgS = 0.0
var float armHi = na
var bool armHiOn = false
var float armLo = na
var bool armLoOn = false
var int sDir = 0
var string lastEvt = "—"
var string lastSweepTxt = "—"
var float lastPivHi = na
var float lastPivLo = na
var array<float> zzP = array.new_float()
var array<int> zzB = array.new<int>()
var array<int> zzT = array.new<int>()
var string lastHarm = "—"
var array<Zone> obs = array.new<Zone>()
var array<Zone> fvgs = array.new<Zone>()
var string lastRgEvt = "—"
var float kfV = na
var float kfP = 1.0
var Trade pos = na
var int pendDir = 0
var float pendMargin = 0.0
var int pendLedDir = 0
var float pendLedMargin = 0.0
var array<Trade> ledOpen = array.new<Trade>()
var array<float> ledR = array.new_float()
var array<float> ledM = array.new_float()
var array<float> ledMae = array.new_float()
var array<float> ledMfe = array.new_float()
var int ledDrop = 0  // F-09: explicit ledger overflow counter (no silent censoring)
var int invCnt = 0   // F-04: bars with non-finite scores (defensive; should stay 0)
var array<float> simR = array.new_float()
var float eq = accEquity
var float eqPeak = accEquity
var float maxDd = 0.0
var int nT = 0
var int nW = 0
var float sumW = 0.0
var float sumL = 0.0
var int lossStreak = 0
var bool killActive = false
var int killUntil = 0
var int lastSigBar = -99999
var int lastLedBar = -99999
var array<int> sigT = array.new<int>()
var int p3Off = 0        // F-10: would-be state, maintained ALWAYS; applied only when p3On
var int p3ChgBar = 0
var float longSc = 0.0
var float shortSc = 0.0
var float effLv = 0.0
var float effSv = 0.0
var bool scoreValidG = true
var int planDir = 0
var int planBar = 0
var float planRef = na
var float planSl = na
var float planT1 = na
var float planT2 = na
var float planT3 = na
var float planQty = na
var float planMarg = na
var bool planCapped = false
var float planLiq = na
var bool planLiqWarn = false
var string planGrade = "—"
var float planScore = 0.0
var string planPb = "—"
var bool markL = false
var bool markS = false
var array<label> sigLbls = array.new<label>()
stdChart = chart.is_standard
simActive = simOn and stdChart
// F-14: warm gate covers every length family actually used by the active config
reqBars = math.max(math.max(math.max(emaSlowL, vfiLen + 5), math.max(regLen + 5, zLen + 5)), math.max(stcS + stcC + 8, 60)) + math.max(pivLiqLen, pivStrLen) + 5
warmOk = bar_index >= reqBars and atrOk and not na(emaSlo)
warmPct = math.min(100.0, bar_index / math.max(reqBars, 1) * 100.0)
volZeroFlag = warmOk and volOk and not volUsable
sessOk = not sessOn or not na(time(timeframe.period, sessWin + ":1234567", "UTC"))
// === MODULE 8: FLOW/ZONE SCANS (pure reads, series) ===
obBullNear = false
obBearNear = false
brkBearNear = false
brkBullNear = false
nObAct = 0
if array.size(obs) > 0
    for i = 0 to array.size(obs) - 1
        z = array.get(obs, i)
        if z.state == 0
            nObAct += 1
            if z.isBull and close >= z.bot and close - z.top <= 1.0 * atrVal
                obBullNear := true
            if not z.isBull and close <= z.top and z.bot - close <= 1.0 * atrVal
                obBearNear := true
        if z.state == 2
            if z.isBull and close <= z.top and z.bot - close <= 1.0 * atrVal
                brkBearNear := true
            if not z.isBull and close >= z.bot and close - z.top <= 1.0 * atrVal
                brkBullNear := true
fvgBullNear = false
fvgBearNear = false
nFvgAct = 0
if array.size(fvgs) > 0
    for i = 0 to array.size(fvgs) - 1
        z = array.get(fvgs, i)
        if z.state == 0
            nFvgAct += 1
            if z.isBull and close >= z.bot and close - z.top <= 1.0 * atrVal
                fvgBullNear := true
            if not z.isBull and close <= z.top and z.bot - close <= 1.0 * atrVal
                fvgBearNear := true
absorb = volUsable and volR > 1.5 and rngBar < 0.5 * atrVal
imbB = f_clamp(50.0 + (obBullNear ? 20 : 0) + (fvgBullNear ? 15 : 0) + (brkBullNear ? 12 : 0) + (volUsable and deltaSm > 0 ? 8 : 0) + (volUsable and cvdW > cvdSig ? 7 : 0) + (absorb ? 5 : 0) - (obBearNear ? 10 : 0), 0, 100)
imbS = f_clamp(50.0 + (obBearNear ? 20 : 0) + (fvgBearNear ? 15 : 0) + (brkBearNear ? 12 : 0) + (volUsable and deltaSm < 0 ? 8 : 0) + (volUsable and cvdW < cvdSig ? 7 : 0) + (absorb ? 5 : 0) - (obBullNear ? 10 : 0), 0, 100)
// === MODULE 9: MOMENTUM SCORE (series, symmetric) ===
wtXu = ta.crossover(wt1, wt2)
wtXd = ta.crossunder(wt1, wt2)
aoXu = ta.crossover(ao, aoSig)
aoXd = ta.crossunder(ao, aoSig)
stcUp = stcV > stcV[1]
stcDn = stcV < stcV[1] // F-05: flat STC is neutral for BOTH sides (was short-biased)
momB = math.min(100.0, (wtXu and wt1 <= -40 ? 20 : wt1 > wt2 ? 8 : 0) + (volUsable and vfb > vfbSig ? (vfb > 20 ? 18 : 12) : 0) + (aoXu ? 12 : ao > aoSig and ao > 0 ? 8 : 0) + (stcUp and stcV[1] < 25 ? 15 : stcUp ? 8 : 0) + (rsiV > 55 ? 8 : 0) + (sqzRel and momH > momH[1] ? 19 : 0))
momS = math.min(100.0, (wtXd and wt1 >= 40 ? 20 : wt1 < wt2 ? 8 : 0) + (volUsable and vfb < vfbSig ? (vfb < -20 ? 18 : 12) : 0) + (aoXd ? 12 : ao < aoSig and ao < 0 ? 8 : 0) + (stcDn and stcV[1] > 75 ? 15 : stcDn ? 8 : 0) + (rsiV < 45 ? 8 : 0) + (sqzRel and momH < momH[1] ? 19 : 0))
// === MODULE 10: RANGE WINDOW + QUANT (series) ===
rHi = ta.highest(high, rangeLen)[1]
rLo = ta.lowest(low, rangeLen)[1]
rWidthOk = rHi - rLo >= 1.5 * atrVal
// === MODULE 11: SHARED SIM/PLAN FUNCTIONS ===
f_planLevels(int dirI, float en, float atrE, float swLo, float swHi) =>
    minD = slAtrMin * atrE
    maxD = slAtrMax * atrE
    rawD = dirI == 1 ? (useSwingSL and not na(swLo) ? en - swLo : minD) : (useSwingSL and not na(swHi) ? swHi - en : minD)
    d = math.min(math.max(rawD, minD), maxD)
    hM = hurstTp ? 0.75 + nz(hurstV, 0.5) * 0.5 : 1.0
    sl = dirI == 1 ? en - d : en + d
    [sl, en + dirI * d * tp1R * hM, en + dirI * d * tp2R * hM, en + dirI * d * tp3R * hM, d]
f_mkTrade(int dirI, float en, float atrE, float swLo, float swHi, float marginV, float rmV) =>
    [sl, t1, t2, t3, d] = f_planLevels(dirI, en, atrE, swLo, swHi)
    Trade.new(dirI, en, sl, d, t1, t2, t3, 1.0, 0.0, false, false, false, 0.0, 0.0, false, 0.0, marginV, bar_index, rmV)
f_step(Trade t) =>
    if not t.closed
        cRT = t.rd > 0 ? (t.en * 2.0 * (feeTaker + slipPct) / 100.0) / t.rd : 0.0
        t.mfe := math.max(t.mfe, (t.dir == 1 ? high - t.en : t.en - low) / t.rd)
        t.mae := math.max(t.mae, (t.dir == 1 ? t.en - low : high - t.en) / t.rd)
        slHit = t.dir == 1 ? low <= t.sl : high >= t.sl
        q1 = t.dir == 1 ? high >= t.t1 : low <= t.t1
        q2 = t.dir == 1 ? high >= t.t2 : low <= t.t2
        q3 = t.dir == 1 ? high >= t.t3 : low <= t.t3
        f1c = math.min(tp1Pct, 90.0) / 100.0
        f2c = math.min(tp2Pct, 90.0 - math.min(tp1Pct, 90.0)) / 100.0
        if conserv and slHit
            t.banked += t.rem * ((t.sl - t.en) * t.dir / t.rd - cRT)
            t.rem := 0.0
        else
            if q1 and not t.h1 and t.rem > 0
                f1 = math.min(f1c, t.rem)
                t.banked += f1 * ((t.t1 - t.en) * t.dir / t.rd - cRT)
                t.rem -= f1
                t.h1 := true
                if beAfterTp1
                    t.sl := t.dir == 1 ? math.max(t.sl, t.en) : math.min(t.sl, t.en)
            if q2 and t.h1 and not t.h2 and t.rem > 0
                f2 = math.min(f2c, t.rem)
                t.banked += f2 * ((t.t2 - t.en) * t.dir / t.rd - cRT)
                t.rem -= f2
                t.h2 := true
                t.trailOn := true
            if t.trailOn and t.rem > 0
                t.sl := t.dir == 1 ? math.max(t.sl, high - trailAtr * atrVal) : math.min(t.sl, low + trailAtr * atrVal)
            if q3 and t.rem > 0
                t.banked += t.rem * ((t.t3 - t.en) * t.dir / t.rd - cRT)
                t.rem := 0.0
            else if slHit and t.rem > 0
                t.banked += t.rem * ((t.sl - t.en) * t.dir / t.rd - cRT)
                t.rem := 0.0
        if t.rem <= 0.0001
            t.closed := true
            t.rFin := t.banked
f_ledStats(float off) =>
    n = 0
    s = 0.0
    sz = array.size(ledR)
    if sz > 0
        for i = 0 to sz - 1
            if array.get(ledM, i) >= off
                n += 1
                s += array.get(ledR, i)
    [n, n > 0 ? s / n : float(na)]
f_sweepScore(float pen, float reclaim, float wick, bool bodyOk, float vR, float poolW, float ctx) =>
    pS = pen <= sweepTgtPen ? pen / math.max(sweepTgtPen, 1e-6) : math.max(0.0, 1.0 - (pen - sweepTgtPen) / math.max(sweepMaxPen - sweepTgtPen, 1e-6))
    rS = f_clamp(reclaim, 0, 1)
    wS = f_clamp(wick / 0.6, 0, 1)
    bS = bodyOk ? 1.0 : 0.4
    vS = f_clamp(vR / math.max(volSpike * 1.5, 0.1), 0, 1)
    qS = f_clamp(poolW / 3.0, 0, 1)
    100.0 * (0.18 * pS + 0.20 * rS + 0.14 * wS + 0.08 * bS + 0.18 * vS + 0.12 * qS + 0.10 * ctx)
// === MODULE 12: CONFIRMED-BAR STATE ENGINE ===
if barstate.isconfirmed
    // -- 12a kill reset, sim creation (consumes pend set LAST bar → next-bar-open fill)
    if killActive and bar_index >= killUntil
        killActive := false
        lossStreak := 0
    atrE = nz(atrVal[1], nz(atrVal, 0.0))
    if pendDir != 0
        if simActive and not killActive and (na(pos) or pos.closed) and atrE > 0 // F-19: no rd=0 trades
            rm = (simComp ? eq : accEquity) * riskPct / 100.0
            pos := f_mkTrade(pendDir, open, atrE, lastPivLo, lastPivHi, pendMargin, rm)
        pendDir := 0
    if pendLedDir != 0
        if array.size(ledOpen) < 24 and atrE > 0 // F-09: cap 8→24 + explicit overflow count
            array.unshift(ledOpen, f_mkTrade(pendLedDir, open, atrE, lastPivLo, lastPivHi, pendLedMargin, 0.0))
        else
            ledDrop += 1
        pendLedDir := 0
    // -- 12b step real position, book on close
    if not na(pos) and not pos.closed
        f_step(pos)
        if pos.closed
            nT += 1
            f_pushCap(simR, pos.rFin, 200)
            if pos.rFin > 0
                nW += 1
                sumW += pos.rFin
                lossStreak := 0
            else if pos.rFin < 0
                sumL += -pos.rFin
                lossStreak += 1
                if lossStreak >= killN
                    killActive := true
                    killUntil := bar_index + killCool
            eq += pos.rFin * pos.rm
    // -- 12c step ledger (same execution model as the sim; explicit overflow, F-12 while-loop)
    if array.size(ledOpen) > 0
        li = array.size(ledOpen) - 1
        while li >= 0
            t = array.get(ledOpen, li)
            f_step(t)
            if t.closed
                f_pushCap(ledR, t.rFin, 120)
                f_pushCap(ledM, t.margin, 120)
                f_pushCap(ledMae, t.mae, 120)
                f_pushCap(ledMfe, t.mfe, 120)
                array.remove(ledOpen, li)
            li -= 1
    // -- 12d MTM equity + drawdown (open excursion included)
    eqM = eq
    if not na(pos) and not pos.closed
        cRTm = pos.rd > 0 ? (pos.en * 2.0 * (feeTaker + slipPct) / 100.0) / pos.rd : 0.0
        eqM += (pos.banked + pos.rem * ((close - pos.en) * pos.dir / pos.rd - cRTm)) * pos.rm
    eqPeak := math.max(eqPeak, eqM)
    if eqPeak > 0
        maxDd := math.max(maxDd, (eqPeak - eqM) / eqPeak * 100.0)
    // -- 12e memory decay FIRST (B4 fix: cools to 0), events re-arm below
    // F-02: nz() self-heals any historically poisoned memory within one bar
    // (recovery policy: invalid memory → 0, which fails toward NO signal).
    dk = decayPts * volScale
    memSwB := math.max(0.0, nz(memSwB) - dk)
    memSwS := math.max(0.0, nz(memSwS) - dk)
    memStB := math.max(0.0, nz(memStB) - dk)
    memStS := math.max(0.0, nz(memStS) - dk)
    memShB := math.max(0.0, nz(memShB) - dk)
    memShS := math.max(0.0, nz(memShS) - dk)
    memHaB := math.max(0.0, nz(memHaB) - dk)
    memHaS := math.max(0.0, nz(memHaS) - dk)
    memRgB := math.max(0.0, nz(memRgB) - dk)
    memRgS := math.max(0.0, nz(memRgS) - dk)
    // -- 12f pivots → pools
    poolsDirty = false
    if not na(phL)
        array.unshift(hiPx, phL)
        array.unshift(hiBar, bar_index - pivLiqLen)
        poolsDirty := true
        if array.size(hiPx) > 25
            array.pop(hiPx)
            array.pop(hiBar)
    if not na(plL)
        array.unshift(loPx, plL)
        array.unshift(loBar, bar_index - pivLiqLen)
        poolsDirty := true
        if array.size(loPx) > 25
            array.pop(loPx)
            array.pop(loBar)
    if not na(phS)
        lastPivHi := phS
    if not na(plS)
        lastPivLo := plS
    eps = clustEps * atrVal
    if poolsDirty and atrOk
        [pc1, pn1] = f_pools(loPx, eps)
        poolLoC := pc1
        poolLoN := pn1
        [pc2, pn2] = f_pools(hiPx, eps)
        poolHiC := pc2
        poolHiN := pn2
    // -- 12g sweeps (symmetric pierce-&-reclaim; F-03: gated on valid ATR so na can
    //    never enter scores or the P1 buffer; legacy switch reproduces v1)
    swBullEvt = false
    swBearEvt = false
    swBullScore = 0.0
    swBearScore = 0.0
    if useLiquidity and atrOk
        if legSweep
            if array.size(loPx) > 0 and low < array.get(loPx, 0)
                c = array.get(loPx, 0)
                pen = (c - low) / math.max(atrVal, 1e-10)
                rec = (close - c) / math.max(rngBar, 1e-10)
                wick = (math.min(open, close) - low) / math.max(rngBar, 1e-10)
                sLeg = f_sweepScore(pen, rec, wick, close > open, volR, 1.0, regRange or regDir == 1 ? 1.0 : 0.5)
                if not na(sLeg)
                    swBullScore := sLeg
                    swBullEvt := true
                    f_pushCap(p1Buf, swBullScore, p1N)
            if array.size(hiPx) > 0 and high > array.get(hiPx, 0) and close < array.get(hiPx, 0)
                c = array.get(hiPx, 0)
                pen = (high - c) / math.max(atrVal, 1e-10)
                rec = (c - close) / math.max(rngBar, 1e-10)
                wick = (high - math.max(open, close)) / math.max(rngBar, 1e-10)
                sLeg2 = f_sweepScore(pen, rec, wick, close < open, volR, 1.0, regRange or regDir == -1 ? 1.0 : 0.5)
                if not na(sLeg2)
                    swBearScore := sLeg2
                    swBearEvt := true
                    f_pushCap(p1Buf, swBearScore, p1N)
        else
            // bull: pierce pool below + RECLAIM (B1 fix) + consumption + cooldown (B2 fix)
            if bar_index >= coolLo
                bestS = 0.0
                bestC = float(na)
                nCand = array.size(poolLoC)
                for i = 0 to (nCand > 0 ? nCand - 1 : 0)
                    if nCand > 0
                        c = array.get(poolLoC, i)
                        w = float(array.get(poolLoN, i))
                        pen = (c - low) / math.max(atrVal, 1e-10)
                        if low < c and close > c and pen <= sweepMaxPen
                            rec = (close - c) / math.max(rngBar, 1e-10)
                            wick = (math.min(open, close) - low) / math.max(rngBar, 1e-10)
                            s = f_sweepScore(pen, rec, wick, close > open, volR, w, regRange or regDir == 1 ? 1.0 : 0.5)
                            if s > bestS
                                bestS := s
                                bestC := c
                if htfOk and not na(htfL)
                    penH = (htfL - low) / math.max(atrVal, 1e-10)
                    if low < htfL and close > htfL and penH <= sweepMaxPen
                        recH = (close - htfL) / math.max(rngBar, 1e-10)
                        wickH = (math.min(open, close) - low) / math.max(rngBar, 1e-10)
                        sH = f_sweepScore(penH, recH, wickH, close > open, volR, 2.0, regRange or regDir == 1 ? 1.0 : 0.5)
                        if sH > bestS
                            bestS := sH
                            bestC := htfL
                if bestS > 0
                    f_pushCap(p1Buf, bestS, p1N) // recorded PRE-gate (no censoring)
                    if bestS >= (p1On ? p1Gate : swGateStatic)
                        swBullEvt := true
                        swBullScore := bestS
                        coolLo := bar_index + sweepCool
                        if not na(bestC)
                            i2 = array.size(loPx) - 1
                            while i2 >= 0
                                if math.abs(array.get(loPx, i2) - bestC) <= eps
                                    array.remove(loPx, i2)
                                    array.remove(loBar, i2)
                                i2 -= 1
                            [pc3, pn3] = f_pools(loPx, eps)
                            poolLoC := pc3
                            poolLoN := pn3
            // bear mirror
            if bar_index >= coolHi
                bestS = 0.0
                bestC = float(na)
                nCand = array.size(poolHiC)
                for i = 0 to (nCand > 0 ? nCand - 1 : 0)
                    if nCand > 0
                        c = array.get(poolHiC, i)
                        w = float(array.get(poolHiN, i))
                        pen = (high - c) / math.max(atrVal, 1e-10)
                        if high > c and close < c and pen <= sweepMaxPen
                            rec = (c - close) / math.max(rngBar, 1e-10)
                            wick = (high - math.max(open, close)) / math.max(rngBar, 1e-10)
                            s = f_sweepScore(pen, rec, wick, close < open, volR, w, regRange or regDir == -1 ? 1.0 : 0.5)
                            if s > bestS
                                bestS := s
                                bestC := c
                if htfOk and not na(htfH)
                    penH = (high - htfH) / math.max(atrVal, 1e-10)
                    if high > htfH and close < htfH and penH <= sweepMaxPen
                        recH = (htfH - close) / math.max(rngBar, 1e-10)
                        wickH = (high - math.max(open, close)) / math.max(rngBar, 1e-10)
                        sH = f_sweepScore(penH, recH, wickH, close < open, volR, 2.0, regRange or regDir == -1 ? 1.0 : 0.5)
                        if sH > bestS
                            bestS := sH
                            bestC := htfH
                if bestS > 0
                    f_pushCap(p1Buf, bestS, p1N)
                    if bestS >= (p1On ? p1Gate : swGateStatic)
                        swBearEvt := true
                        swBearScore := bestS
                        coolHi := bar_index + sweepCool
                        if not na(bestC)
                            i2 = array.size(hiPx) - 1
                            while i2 >= 0
                                if math.abs(array.get(hiPx, i2) - bestC) <= eps
                                    array.remove(hiPx, i2)
                                    array.remove(hiBar, i2)
                                i2 -= 1
                            [pc4, pn4] = f_pools(hiPx, eps)
                            poolHiC := pc4
                            poolHiN := pn4
    if swBullEvt
        memSwB := math.max(memSwB, swBullScore)
        lastSweepTxt := "SW↑ " + str.tostring(math.round(swBullScore))
    if swBearEvt
        memSwS := math.max(memSwS, swBearScore)
        lastSweepTxt := "SW↓ " + str.tostring(math.round(swBearScore))
    // P1 gate update (normalization; hysteresis + dwell + bounds + freeze)
    if p1On and not p1Freeze and array.size(p1Buf) >= p1Min
        qv = f_quantA(p1Buf, p1Q)
        if not na(qv)
            wq = math.min(1.0, array.size(p1Buf) / float(p1N))
            cand = f_clamp(swGateStatic * (1 - wq) + qv * wq, 40, 90)
            if math.abs(cand - p1Gate) >= p1Hyst and bar_index - p1Last >= 10
                p1Gate := cand
                p1Last := bar_index
    // -- 12h structure (consumed levels; legacy switch = v1 persistence)
    if not na(phS)
        armHi := phS
        armHiOn := true
    if not na(plS)
        armLo := plS
        armLoOn := true
    if useStructure
        if armHiOn and not na(armHi) and close > armHi
            chochB = sDir == -1
            mssB = chochB and htfOk and htfBias == 1
            if not legStruct
                armHiOn := false
            sDir := 1
            memStB := math.max(memStB, mssB ? 100 : chochB ? 85 : 70)
            memStS := math.max(0.0, memStS - 15.0)
            lastEvt := mssB ? "MSS↑" : chochB ? "CHoCH↑" : "BOS↑"
        if armLoOn and not na(armLo) and close < armLo
            chochS = sDir == 1
            mssS = chochS and htfOk and htfBias == -1
            if not legStruct
                armLoOn := false
            sDir := -1
            memStS := math.max(memStS, mssS ? 100 : chochS ? 85 : 70)
            memStB := math.max(0.0, memStB - 15.0)
            lastEvt := mssS ? "MSS↓" : chochS ? "CHoCH↓" : "BOS↓"
        if legStruct
            if sDir == 1
                memStB := math.max(memStB, 50.0)
            if sDir == -1
                memStS := math.max(memStS, 50.0)
    // -- 12i shadows (3, symmetric; na-ATR conditions simply stay false pre-warm-up)
    if useShadows and rngBar > 0
        bodyC = math.abs(close - open)
        upW = high - math.max(open, close)
        dnW = math.min(open, close) - low
        if bodyC / rngBar <= 0.25 and dnW >= 1.5 * upW and dnW >= 0.4 * atrVal
            memShB := math.max(memShB, 40.0)
        if bodyC / rngBar <= 0.25 and upW >= 1.5 * dnW and upW >= 0.4 * atrVal
            memShS := math.max(memShS, 40.0)
        pBodLo = math.min(open[1], close[1])
        pBodHi = math.max(open[1], close[1])
        if low < pBodLo and dnW >= 0.2 * atrVal and close >= pBodLo
            memShB := math.max(memShB, 60.0)
        if high > pBodHi and upW >= 0.2 * atrVal and close <= pBodHi
            memShS := math.max(memShS, 60.0)
        if high[1] >= hh20[2] + 0.1 * atrVal and close[1] < hh20[2] and close < close[1]
            memShS := math.max(memShS, 70.0)
        if low[1] <= ll20[2] - 0.1 * atrVal and close[1] > ll20[2] and close > close[1]
            memShB := math.max(memShB, 70.0)
    // -- 12j zigzag + harmonics (alternation enforced, canonical ratios)
    if useHarmonic
        zzNew = 0
        if not na(phS)
            if array.size(zzT) > 0 and array.get(zzT, 0) == 1
                if phS > array.get(zzP, 0)
                    array.set(zzP, 0, phS)
                    array.set(zzB, 0, bar_index - pivStrLen)
            else
                array.unshift(zzP, phS)
                array.unshift(zzB, bar_index - pivStrLen)
                array.unshift(zzT, 1)
                zzNew := 1
        if not na(plS)
            if array.size(zzT) > 0 and array.get(zzT, 0) == -1
                if plS < array.get(zzP, 0)
                    array.set(zzP, 0, plS)
                    array.set(zzB, 0, bar_index - pivStrLen)
            else
                array.unshift(zzP, plS)
                array.unshift(zzB, bar_index - pivStrLen)
                array.unshift(zzT, -1)
                zzNew := -1
        while array.size(zzP) > 12
            array.pop(zzP)
            array.pop(zzB)
            array.pop(zzT)
        if zzNew != 0 and array.size(zzP) >= 5
            dP = array.get(zzP, 0)
            cP = array.get(zzP, 1)
            bP = array.get(zzP, 2)
            aP = array.get(zzP, 3)
            xP = array.get(zzP, 4)
            tD = array.get(zzT, 0)
            XA = math.abs(aP - xP)
            AB = math.abs(bP - aP)
            BC = math.abs(cP - bP)
            CD = math.abs(dP - cP)
            if XA > 1e-10 and AB > 1e-10 and BC > 1e-10
                rAB = AB / XA
                rBC = BC / AB
                rCD = CD / BC
                rAD = math.abs(aP - dP) / XA
                gart = f_in(rAB, 0.618, 0.618) and f_in(rBC, 0.382, 0.886) and f_in(rCD, 1.13, 1.618) and f_in(rAD, 0.786, 0.786)
                batP = f_in(rAB, 0.382, 0.50) and f_in(rBC, 0.382, 0.886) and f_in(rCD, 1.618, 2.618) and f_in(rAD, 0.886, 0.886)
                bfly = f_in(rAB, 0.786, 0.786) and f_in(rBC, 0.382, 0.886) and f_in(rCD, 1.618, 2.24) and f_in(rAD, 1.27, 1.618)
                crab = f_in(rAB, 0.382, 0.618) and f_in(rBC, 0.382, 0.886) and f_in(rCD, 2.24, 3.618) and f_in(rAD, 1.618, 1.618)
                anyH = gart or batP or bfly or crab
                hN = gart ? "Gartley" : batP ? "Bat" : bfly ? "Butterfly" : crab ? "Crab" : ""
                if anyH and tD == -1
                    memHaB := math.max(memHaB, 75.0)
                    lastHarm := hN + "↑"
                if anyH and tD == 1
                    memHaS := math.max(memHaS, 75.0)
                    lastHarm := hN + "↓"
    // -- 12k zones: OB creation (P2 gate) + lifecycle (breaker fixed), FVG
    if atrOk and atrVal > 0 // F-03: buffer only receives valid ratios
        f_pushCap(p2Buf, rngBar / atrVal, p2N)
    if p2On and not p2Freeze and bar_index % p2Refresh == 0 and array.size(p2Buf) >= p2Min
        qv2 = f_quantA(p2Buf, p2Q)
        if not na(qv2)
            wq2 = math.min(1.0, array.size(p2Buf) / float(p2N))
            cand2 = f_clamp(obStatic * (1 - wq2) + qv2 * wq2, 1.1, 3.0)
            if math.abs(cand2 - p2Gate) >= p2Hyst and bar_index - p2Last >= p2Refresh * 2
                p2Gate := cand2
                p2Last := bar_index
    obGate = p2On ? p2Gate : obStatic
    if useOrderflow and atrOk
        bodyR = math.abs(close - open) / math.max(rngBar, 1e-10)
        disp = atrVal > 0 ? rngBar / atrVal : 0.0
        if close > open and bodyR >= 0.6 and disp >= obGate and bar_index > obLook
            for i = 1 to obLook
                if close[i] < open[i]
                    array.unshift(obs, Zone.new(true, math.max(open[i], close[i]), math.min(open[i], close[i]), bar_index - i, 0))
                    break
        if close < open and bodyR >= 0.6 and disp >= obGate and bar_index > obLook
            for i = 1 to obLook
                if close[i] > open[i]
                    array.unshift(obs, Zone.new(false, math.max(open[i], close[i]), math.min(open[i], close[i]), bar_index - i, 0))
                    break
        if array.size(obs) > 0
            for i = 0 to array.size(obs) - 1
                z = array.get(obs, i)
                if z.state == 0
                    if z.isBull
                        if close < z.bot
                            z.state := 2 // breaker: mitigated-through + close beyond (B7 fix)
                        else if low <= z.bot
                            z.state := 1
                    else
                        if close > z.top
                            z.state := 2
                        else if high >= z.top
                            z.state := 1
        while array.size(obs) > 16
            array.pop(obs)
        if low > high[2] and low - high[2] >= fvgMin * atrVal
            array.unshift(fvgs, Zone.new(true, low, high[2], bar_index - 1, 0))
        if high < low[2] and low[2] - high >= fvgMin * atrVal
            array.unshift(fvgs, Zone.new(false, low[2], high, bar_index - 1, 0))
        if array.size(fvgs) > 0
            for i = 0 to array.size(fvgs) - 1
                z = array.get(fvgs, i)
                if z.state == 0
                    if z.isBull and low <= z.top - (z.top - z.bot) * fvgFill
                        z.state := 1
                    if not z.isBull and high >= z.bot + (z.top - z.bot) * fvgFill
                        z.state := 1
        while array.size(fvgs) > 16
            array.pop(fvgs)
    // -- 12l range events (honest Wyckoff-style)
    springEvt = false
    upthrEvt = false
    if useRange and rWidthOk and not na(rHi) and not na(rLo)
        if low < rLo and close > rLo and volR > volSpike
            springEvt := true
            memRgB := math.max(memRgB, 80.0)
            lastRgEvt := "Spring"
        if high > rHi and close < rHi and volR > volSpike
            upthrEvt := true
            memRgS := math.max(memRgS, 80.0)
            lastRgEvt := "Upthrust"
        if close > rHi and close[1] > rHi[1] and volR > 1.0
            memRgB := math.max(memRgB, 65.0)
            lastRgEvt := "SOS"
        if close < rLo and close[1] < rLo[1] and volR > 1.0
            memRgS := math.max(memRgS, 65.0)
            lastRgEvt := "SOW"
    // -- 12m Kalman (confirmed-bar update only → non-repainting)
    if na(kfV)
        kfV := close
    pPred = kfP + kalQ
    kG = pPred / (pPred + kalR)
    kfV := kfV + kG * (close - kfV)
    kfP := (1 - kG) * pPred
    kSl = kfV - nz(kfV[1], kfV)
    qB = f_clamp(50.0 + (kSl > 0 ? 15 : -15) + (zV < -2 ? 25 : 0) - (zV > 2 ? 25 : 0), 0, 100)
    qS = f_clamp(50.0 + (kSl < 0 ? 15 : -15) + (zV > 2 ? 25 : 0) - (zV < -2 ? 25 : 0), 0, 100)
    // -- 12n playbooks (symmetric)
    pbDir = 0
    pbScore = 0.0
    pbName = "—"
    if usePlaybook
        if swBullEvt and (regRange or sDir == 1) and swBullScore > pbScore
            pbDir := 1
            pbScore := swBullScore
            pbName := "SWEEP↑"
        if swBearEvt and (regRange or sDir == -1) and swBearScore > pbScore
            pbDir := -1
            pbScore := swBearScore
            pbName := "SWEEP↓"
        if springEvt and 80 > pbScore
            pbDir := 1
            pbScore := 80
            pbName := "SPRING"
        if upthrEvt and 80 > pbScore
            pbDir := -1
            pbScore := 80
            pbName := "UPTHR"
        if imbB >= 60 and fvgBullNear and obBullNear and 75 > pbScore
            pbDir := 1
            pbScore := 75
            pbName := "OB+FVG↑"
        if imbS >= 60 and fvgBearNear and obBearNear and 75 > pbScore
            pbDir := -1
            pbScore := 75
            pbName := "OB+FVG↓"
        if sqzRel and regDir != 0 and (regDir == 1 ? momB : momS) > pbScore
            pbDir := regDir
            pbScore := regDir == 1 ? momB : momS
            pbName := "SQZ-BRK"
    // -- 12o fusion (renormalized over enabled layers; v1 parity profiles)
    pT = profShift and regTrend
    pR = profShift and regRange
    wS2 = pT ? 0.25 : pR ? 0.15 : wStructIn
    wL2 = pT ? 0.15 : pR ? 0.30 : wLiqIn
    wM2 = pT ? 0.20 : pR ? 0.10 : wMomIn
    wI2 = pT ? 0.15 : pR ? 0.15 : wImbIn
    wR2 = pT ? 0.10 : pR ? 0.20 : wRangeIn
    wQ2 = pT ? 0.10 : pR ? 0.10 : wQuantIn
    wH2 = pT ? 0.05 : pR ? 0.05 : wHarmIn
    wD2 = pT ? 0.05 : pR ? 0.05 : wShadIn
    den = (useStructure ? wS2 : 0) + (useLiquidity ? wL2 : 0) + (useMomentum ? wM2 : 0) + (useOrderflow ? wI2 : 0) + (useRange ? wR2 : 0) + (useQuant ? wQ2 : 0) + (useHarmonic ? wH2 : 0) + (useShadows ? wD2 : 0)
    den := den > 0 ? den : 1.0
    lS = ((useStructure ? wS2 * memStB : 0) + (useLiquidity ? wL2 * memSwB : 0) + (useMomentum ? wM2 * momB : 0) + (useOrderflow ? wI2 * imbB : 0) + (useRange ? wR2 * memRgB : 0) + (useQuant ? wQ2 * qB : 0) + (useHarmonic ? wH2 * memHaB : 0) + (useShadows ? wD2 * memShB : 0)) / den
    sS = ((useStructure ? wS2 * memStS : 0) + (useLiquidity ? wL2 * memSwS : 0) + (useMomentum ? wM2 * momS : 0) + (useOrderflow ? wI2 * imbS : 0) + (useRange ? wR2 * memRgS : 0) + (useQuant ? wQ2 * qS : 0) + (useHarmonic ? wH2 * memHaS : 0) + (useShadows ? wD2 * memShS : 0)) / den
    if regTrend
        if regDir == 1
            lS := f_clamp(lS + regConf * regBoost, 0, 100)
        else if not legAsym
            sS := f_clamp(sS + regConf * regBoost, 0, 100)
    if pbDir == 1
        lS := f_clamp(lS + pbScore * pbBoost, 0, 100)
    if pbDir == -1
        sS := f_clamp(sS + pbScore * pbBoost, 0, 100)
    longSc := lS
    shortSc := sS
    // -- 12p P3 state machine — F-10: runs ALWAYS (would-be diagnostics while OFF);
    //    the offset is APPLIED only when p3On. F-09: step-ups blocked after any drop.
    [n0, e0] = f_ledStats(0.0)
    p3Cur = float(p3Off)
    [nC, eC] = f_ledStats(p3Cur)
    [nN, eN] = f_ledStats(math.min(p3Cur + 2.0, 6.0))
    canStep = ledDrop == 0
    if canStep and nC >= p3MinN and not na(eC) and eC < -p3Margin and p3Off < 6 and nN >= p3MinN and not na(eN) and eN > eC + p3Margin
        p3Off += 2
        p3ChgBar := bar_index
    else if p3Off > 0
        if n0 >= p3MinN and nC >= p3MinN and not na(eC) and not na(e0) and eC - e0 < p3Rev
            p3Off := 0
            p3ChgBar := bar_index
        else if bar_index - p3ChgBar > 100 and not na(eC) and eC >= -p3Rev
            p3Off := math.max(0, p3Off - 2)
            p3ChgBar := bar_index
    p3Eff = p3On ? float(p3Off) : 0.0
    // -- 12q thresholds, guards, firing (confirmed close only; FAIL-CLOSED on invalid scores)
    relaxL = regTrend and regDir == 1 ? regRelax : 0.0
    relaxS = regTrend and regDir == -1 and not legAsym ? regRelax : 0.0
    effDiff = regTrend ? thrDiff / 1.5 : thrDiff
    effL0 = thrLong - relaxL
    effS0 = thrShort - relaxS
    effL = effL0 + p3Eff
    effS = effS0 + p3Eff
    effLv := effL
    effSv := effS
    while array.size(sigT) > 0 and time - array.get(sigT, 0) > 86400000
        array.shift(sigT)
    cntD = array.size(sigT)
    cntH = 0
    if cntD > 0
        for i = 0 to cntD - 1
            if time - array.get(sigT, i) <= 3600000
                cntH += 1
    rateOk = (maxDay == 0 or cntD < maxDay) and (maxHr == 0 or cntH < maxHr)
    coolOk = bar_index - lastSigBar >= minBars
    posFlat = na(pos) or pos.closed
    scoreValid = not na(longSc) and not na(shortSc) // F-04 defensive invariant
    scoreValidG := scoreValid
    if warmOk and not scoreValid
        invCnt += 1
    rawL = scoreValid and longSc >= effL and longSc > shortSc + effDiff
    rawS = scoreValid and shortSc >= effS and shortSc > longSc + effDiff
    fireL = rawL and warmOk and coolOk and rateOk and sessOk and not killActive and (not onePos or posFlat or not simActive)
    fireS = rawS and warmOk and coolOk and rateOk and sessOk and not killActive and (not onePos or posFlat or not simActive)
    // uncensored ledger stream: base threshold (offset 0), cooldown only
    ledL = scoreValid and longSc >= effL0 and longSc > shortSc + effDiff and warmOk and bar_index - lastLedBar >= minBars
    ledS = scoreValid and shortSc >= effS0 and shortSc > longSc + effDiff and warmOk and bar_index - lastLedBar >= minBars
    markL := false
    markS := false
    if fireL or fireS
        dirI = fireL ? 1 : -1
        scI = fireL ? longSc : shortSc
        mI = fireL ? longSc - effL : shortSc - effS
        [slP, t1P, t2P, t3P, dP2] = f_planLevels(dirI, close, atrVal, lastPivLo, lastPivHi)
        // F-11: LINEAR-contract sizing with multiplier, lot step and notional cap
        riskM = accEquity * riskPct / 100.0
        qtyRaw = dP2 > 0 and ctrMult > 0 ? riskM / (dP2 * ctrMult) : 0.0
        qtyCap = capNotional and close > 0 and ctrMult > 0 ? (accEquity * levIn) / (close * ctrMult) : qtyRaw
        sizeCapped = capNotional and qtyCap < qtyRaw
        qtyP = sizeCapped ? qtyCap : qtyRaw
        if qtyStep > 0
            qtyP := math.floor(qtyP / qtyStep) * qtyStep
        notP = qtyP * close * ctrMult
        margP = levIn > 0 ? notP / levIn : notP
        costR = dP2 > 0 ? (close * 2.0 * (feeTaker + slipPct) / 100.0) / dP2 : 0.0
        liqP = dirI == 1 ? close * (1 - 1.0 / levIn + mmrPct / 100.0) : close * (1 + 1.0 / levIn - mmrPct / 100.0)
        liqD = math.abs(close - liqP)
        liqWarn = dP2 > 0.5 * liqD
        planDir := dirI
        planBar := bar_index
        planRef := close
        planSl := slP
        planT1 := t1P
        planT2 := t2P
        planT3 := t3P
        planQty := qtyP
        planMarg := margP
        planCapped := sizeCapped
        planLiq := liqP
        planLiqWarn := liqWarn
        planScore := scI
        planGrade := mI >= 10 ? "A" : mI >= 5 ? "B" : "C"
        planPb := pbName
        lastSigBar := bar_index
        array.push(sigT, time)
        pendDir := dirI
        pendMargin := mI
        markL := fireL
        markS := fireS
        if showSignals
            rrTxt = dP2 > 0 ? str.tostring((math.abs(t3P - close)) / dP2, "#.#") : "—"
            txt = (dirI == 1 ? "LONG " : "SHORT ") + planGrade + " " + str.tostring(math.round(scI)) + "\nref " + f_fmt(close) + " · SL " + f_fmt(slP) + "\nT1 " + f_fmt(t1P) + " T2 " + f_fmt(t2P) + " T3 " + f_fmt(t3P) + "\nqty " + str.tostring(qtyP, "#.####") + (sizeCapped ? " CAP" : "") + " · " + str.tostring(levIn, "#.#") + "x · R:R " + rrTxt + "\nrisk $" + str.tostring(riskM, "#.##") + " · marg $" + str.tostring(margP, "#.#") + " · cost≈" + str.tostring(costR, "#.##") + "R" + "\nliq≈ " + f_fmt(liqP) + (liqWarn ? " ⚠SL>50%liq" : " ✓") + "\n" + pbName + " · " + regName + " · fills next open"
            lb = label.new(bar_index, dirI == 1 ? low - atrVal * 0.6 : high + atrVal * 0.6, txt, style = dirI == 1 ? label.style_label_up : label.style_label_down, color = dirI == 1 ? color.new(colBull, 15) : color.new(colBear, 15), textcolor = color.white, size = lblSize == "tiny" ? size.tiny : lblSize == "small" ? size.small : size.normal)
            array.push(sigLbls, lb)
            while array.size(sigLbls) > lblMax
                label.delete(array.shift(sigLbls))
    if ledL or ledS
        pendLedDir := ledL ? 1 : -1
        pendLedMargin := ledL ? longSc - effL0 : shortSc - effS0
        lastLedBar := bar_index
// === MODULE 13: PLAN STATUS (mobile: on dashboard, no hover) ===
planAge = planDir != 0 ? bar_index - planBar : 0
planMove = planDir != 0 and atrVal > 0 and not na(planRef) ? math.abs(close - planRef) / atrVal : 0.0
planStatus = planDir == 0 ? "—" : planAge > expireBars ? "EXPIRED" : planMove > lateAtr ? "LATE" : "VALID"
// === MODULE 14: PLOTS (global, unconditional) ===
plot(showEmas ? emaF : na, "EMA fast", emaFc, emaFw)
plot(showEmas ? emaM : na, "EMA mid", emaMc, emaMw)
plot(showEmas ? emaSlo : na, "EMA slow", emaSc, emaSw)
plot(showKalman ? kfV : na, "Kalman", colWarn, 1)
plotshape(markL and barstate.isconfirmed and showSignals, "LONG", shape.triangleup, location.belowbar, colBull, size = size.small)
plotshape(markS and barstate.isconfirmed and showSignals, "SHORT", shape.triangledown, location.abovebar, colBear, size = size.small)
bgcolor(regimeBg and useRegime ? (regDir == 1 ? color.new(colBull, 94) : regDir == -1 ? color.new(colBear, 94) : regRange ? color.new(colWarn, 96) : na) : na, title = "Regime tint")
// === MODULE 15: LAST-BAR DRAWINGS ===
var line prjU = na
var line prjM = na
var line prjD = na
var array<line> poolLn = array.new<line>()
var array<box> zBx = array.new<box>()
if barstate.islast
    line.delete(prjU)
    line.delete(prjM)
    line.delete(prjD)
    if showProj
        prjU := line.new(bar_index, close, bar_index + projBars, projUp, color = color.new(colBull, 40), style = line.style_dashed)
        prjM := line.new(bar_index, close, bar_index + projBars, projMid, color = color.new(colNeut, 40), style = line.style_dotted)
        prjD := line.new(bar_index, close, bar_index + projBars, projDn, color = color.new(colBear, 40), style = line.style_dashed)
    while array.size(poolLn) > 0
        line.delete(array.pop(poolLn))
    if showPools
        nLo = math.min(array.size(poolLoC), poolShow)
        if nLo > 0
            for i = 0 to nLo - 1
                array.push(poolLn, line.new(bar_index - 20, array.get(poolLoC, i), bar_index + 3, array.get(poolLoC, i), color = color.new(colBull, 35), style = line.style_dotted, width = 1))
        nHi = math.min(array.size(poolHiC), poolShow)
        if nHi > 0
            for i = 0 to nHi - 1
                array.push(poolLn, line.new(bar_index - 20, array.get(poolHiC, i), bar_index + 3, array.get(poolHiC, i), color = color.new(colBear, 35), style = line.style_dotted, width = 1))
        if not na(htfH)
            array.push(poolLn, line.new(bar_index - 20, htfH, bar_index + 3, htfH, color = color.new(colBear, 20), width = 2))
        if not na(htfL)
            array.push(poolLn, line.new(bar_index - 20, htfL, bar_index + 3, htfL, color = color.new(colBull, 20), width = 2))
    while array.size(zBx) > 0
        box.delete(array.pop(zBx))
    if showZones
        drawn = 0
        if array.size(obs) > 0
            for i = 0 to array.size(obs) - 1
                z = array.get(obs, i)
                if z.state == 0 and drawn < maxZoneDraw
                    array.push(zBx, box.new(z.born, z.top, bar_index, z.bot, bgcolor = z.isBull ? obBullCol : obBearCol, border_color = color.new(z.isBull ? colBull : colBear, 55), border_style = line.style_dashed))
                    drawn += 1
        drawn2 = 0
        if array.size(fvgs) > 0
            for i = 0 to array.size(fvgs) - 1
                z = array.get(fvgs, i)
                if z.state == 0 and drawn2 < maxZoneDraw
                    array.push(zBx, box.new(z.born, z.top, bar_index, z.bot, bgcolor = z.isBull ? fvgBullCol : fvgBearCol, border_color = color.new(z.isBull ? colBull : colBear, 70), border_style = line.style_dotted))
                    drawn2 += 1
// === MODULE 16: DASHBOARD (F-13: static layout decided by inputs; table built once,
//     merges at init only, every cell rewritten in place each update) ===
fullDash = dashMode == "Full"
diagRows = fullDash and showDiag
legAny = legacyAll or legAsymIn or legSweepIn or legStructIn
rowRegime = 1
rowScores = 2
rowLiq = fullDash ? 3 : -1
rowFlow = fullDash ? 4 : -1
rowRng = fullDash ? 5 : -1
rowSig = fullDash ? 6 : 3
rowPlan = rowSig + 1
rowSize = rowPlan + 1
rowSim = rowSize + 1
rowAdapt = diagRows ? rowSim + 1 : -1
rowLed = diagRows ? rowSim + 2 : -1
rowLeg = legAny ? (diagRows ? rowSim + 3 : rowSim + 1) : -1
dashRowsN = (legAny ? rowLeg : diagRows ? rowLed : rowSim) + 1
var table dash = na
if showDash and barstate.islast
    if na(dash)
        dash := table.new(dashPos == "top_right" ? position.top_right : dashPos == "bottom_right" ? position.bottom_right : dashPos == "top_left" ? position.top_left : position.bottom_left, 4, dashRowsN, bgcolor = dashBg, border_color = color.new(colNeut, 70), border_width = 1)
        table.merge_cells(dash, 0, 0, 3, 0)
        if legAny
            table.merge_cells(dash, 0, rowLeg, 3, rowLeg)
    ts = dashSize == "tiny" ? size.tiny : dashSize == "small" ? size.small : size.normal
    cTx = color.new(#d1d4dc, 0)
    anyWarnB = not warmOk or not stdChart or not volOk or volZeroFlag or htfWarm or htfOvWarn or htfDegraded
    stTxt = "UCE v2 " + (scoreValidG ? "" : "SCORE INVALID · ") + (warmOk ? "" : "WARM-UP " + str.tostring(math.round(warmPct)) + "% · ") + (stdChart ? "" : "CHART≠STD · SIM OFF · ") + (not volOk ? "NO VOLUME · " : volZeroFlag ? "VOL ZERO · " : "") + (htfWarm ? "HTF WARM-UP · " : "") + (htfOvWarn ? "HTF OVR→AUTO · " : "") + (htfDegraded ? "HTF RATIO DEG · " : "") + (killActive ? "KILL " + str.tostring(killUntil - bar_index) + "b" : "ACTIVE")
    table.cell(dash, 0, 0, stTxt, text_color = not scoreValidG or killActive ? colBear : anyWarnB ? colWarn : cTx, text_size = ts, bgcolor = color.new(#1c2a5c, 20))
    table.cell(dash, 0, rowRegime, "REGIME", text_color = colNeut, text_size = ts)
    table.cell(dash, 1, rowRegime, regName, text_color = regDir == 1 ? colBull : regDir == -1 ? colBear : colWarn, text_size = ts)
    table.cell(dash, 2, rowRegime, "agree " + str.tostring(math.round(regConf)) + "%", text_color = cTx, text_size = ts)
    table.cell(dash, 3, rowRegime, "HTF " + htfUsed + " " + str.tostring(htfRatio, "#.#") + "× " + (htfDegraded ? "DEG" : htfOvWarn ? "OVR→AUTO" : htfWarm ? "WARM" : htfDevelop ? "RP!" : "✓"), text_color = htfDegraded or htfOvWarn or htfWarm ? colWarn : colNeut, text_size = ts)
    table.cell(dash, 0, rowScores, "SCORES", text_color = colNeut, text_size = ts)
    table.cell(dash, 1, rowScores, "L " + str.tostring(math.round(longSc)) + "/" + str.tostring(math.round(effLv)), text_color = longSc >= effLv ? colBull : cTx, text_size = ts, bgcolor = longSc >= effLv ? color.new(colBull, 85) : na)
    table.cell(dash, 2, rowScores, "S " + str.tostring(math.round(shortSc)) + "/" + str.tostring(math.round(effSv)), text_color = shortSc >= effSv ? colBear : cTx, text_size = ts, bgcolor = shortSc >= effSv ? color.new(colBear, 85) : na)
    table.cell(dash, 3, rowScores, lastSweepTxt + " · " + lastEvt, text_color = cTx, text_size = ts)
    if fullDash
        table.cell(dash, 0, rowLiq, "LIQ/STRUCT", text_color = colNeut, text_size = ts)
        table.cell(dash, 1, rowLiq, "pools " + str.tostring(array.size(poolLoC)) + "↓/" + str.tostring(array.size(poolHiC)) + "↑", text_color = cTx, text_size = ts)
        table.cell(dash, 2, rowLiq, "memB " + str.tostring(math.round(memSwB)) + "/" + str.tostring(math.round(memStB)), text_color = colBull, text_size = ts)
        table.cell(dash, 3, rowLiq, "memS " + str.tostring(math.round(memSwS)) + "/" + str.tostring(math.round(memStS)), text_color = colBear, text_size = ts)
        table.cell(dash, 0, rowFlow, "FLOW/MOM", text_color = colNeut, text_size = ts)
        table.cell(dash, 1, rowFlow, "OB " + str.tostring(nObAct) + " FVG " + str.tostring(nFvgAct), text_color = cTx, text_size = ts)
        table.cell(dash, 2, rowFlow, "imb " + str.tostring(math.round(imbB)) + "/" + str.tostring(math.round(imbS)), text_color = cTx, text_size = ts)
        table.cell(dash, 3, rowFlow, "mom " + str.tostring(math.round(momB)) + "/" + str.tostring(math.round(momS)), text_color = cTx, text_size = ts)
        table.cell(dash, 0, rowRng, "RANGE/QNT", text_color = colNeut, text_size = ts)
        table.cell(dash, 1, rowRng, lastRgEvt, text_color = colWarn, text_size = ts)
        table.cell(dash, 2, rowRng, "z " + str.tostring(zV, "#.##"), text_color = zV > 0 ? colBull : colBear, text_size = ts)
        table.cell(dash, 3, rowRng, lastHarm + " · H~" + str.tostring(hurstV, "#.##"), text_color = cTx, text_size = ts)
    table.cell(dash, 0, rowSig, "SIGNAL", text_color = colNeut, text_size = ts)
    table.cell(dash, 1, rowSig, planDir == 0 ? "—" : (planDir == 1 ? "LONG " : "SHORT ") + planGrade + " (" + str.tostring(planAge) + "b)", text_color = planDir == 1 ? colBull : planDir == -1 ? colBear : colNeut, text_size = ts)
    table.cell(dash, 2, rowSig, planStatus, text_color = planStatus == "VALID" ? colBull : planStatus == "LATE" ? colWarn : colNeut, text_size = ts, bgcolor = planStatus == "LATE" ? color.new(colWarn, 85) : na)
    table.cell(dash, 3, rowSig, "cd " + str.tostring(math.max(0, minBars - (bar_index - lastSigBar))) + " · " + str.tostring(array.size(sigT)) + "/24h", text_color = colNeut, text_size = ts)
    table.cell(dash, 0, rowPlan, "PLAN", text_color = colNeut, text_size = ts)
    table.cell(dash, 1, rowPlan, planDir == 0 ? "—" : "ref " + f_fmt(planRef), text_color = cTx, text_size = ts)
    table.cell(dash, 2, rowPlan, planDir == 0 ? "—" : "SL " + f_fmt(planSl), text_color = colBear, text_size = ts)
    table.cell(dash, 3, rowPlan, planDir == 0 ? "—" : "T " + f_fmt(planT1) + "/" + f_fmt(planT2) + "/" + f_fmt(planT3), text_color = colBull, text_size = ts)
    table.cell(dash, 0, rowSize, "SIZE", text_color = colNeut, text_size = ts)
    table.cell(dash, 1, rowSize, planDir == 0 ? "—" : "qty " + str.tostring(planQty, "#.####") + (planCapped ? " CAP" : ""), text_color = planCapped ? colWarn : cTx, text_size = ts)
    table.cell(dash, 2, rowSize, str.tostring(levIn, "#.#") + "x · " + str.tostring(riskPct, "#.##") + "% · m$" + (na(planMarg) ? "—" : str.tostring(planMarg, "#")), text_color = cTx, text_size = ts)
    table.cell(dash, 3, rowSize, planDir == 0 ? "—" : "liq≈" + f_fmt(planLiq) + (planLiqWarn ? " ⚠" : " ✓"), text_color = planLiqWarn ? colWarn : cTx, text_size = ts)
    winRate = nT > 0 ? nW / float(nT) * 100.0 : 0.0
    pfV = sumL > 0 ? sumW / sumL : na
    nR = array.size(simR)
    muR = 0.0
    if nR > 0
        for i = 0 to nR - 1
            muR += array.get(simR, i)
        muR /= nR
    sdR = 0.0
    if nR > 1
        for i = 0 to nR - 1
            sdR += math.pow(array.get(simR, i) - muR, 2)
        sdR := math.sqrt(sdR / (nR - 1))
    sqnV = sdR > 0 and nR > 0 ? muR / sdR * math.sqrt(nR) : na
    table.cell(dash, 0, rowSim, simActive ? (not na(pos) and not pos.closed ? "SIM·" + (pos.dir == 1 ? "L@" : "S@") + f_fmt(pos.en) : "SIM") : "SIM OFF", text_color = colNeut, text_size = ts)
    table.cell(dash, 1, rowSim, str.tostring(nT) + "t · " + str.tostring(math.round(winRate)) + "% · PF " + (na(pfV) ? "—" : str.tostring(pfV, "#.##")), text_color = cTx, text_size = ts)
    table.cell(dash, 2, rowSim, "exp " + str.tostring(muR, "#.##") + "R · SQN(R) " + (na(sqnV) ? "—" : str.tostring(sqnV, "#.#")), text_color = muR > 0 ? colBull : colBear, text_size = ts)
    table.cell(dash, 3, rowSim, "DD " + str.tostring(maxDd, "#.#") + "% · eq " + str.tostring(math.round(eq)), text_color = cTx, text_size = ts)
    if diagRows
        [dn0, de0] = f_ledStats(0.0)
        [dnA, deA] = f_ledStats(float(p3Off))
        mae50 = f_quantA(ledMae, 0.5)
        mfe50 = f_quantA(ledMfe, 0.5)
        table.cell(dash, 0, rowAdapt, "ADAPT", text_color = colNeut, text_size = ts)
        table.cell(dash, 1, rowAdapt, "P1 " + str.tostring(math.round(p1On ? p1Gate : swGateStatic)) + " (n" + str.tostring(array.size(p1Buf)) + ")" + (p1Freeze ? "❄" : ""), text_color = cTx, text_size = ts)
        table.cell(dash, 2, rowAdapt, "P2 " + str.tostring(p2On ? p2Gate : obStatic, "#.##") + " (n" + str.tostring(array.size(p2Buf)) + ")" + (p2Freeze ? "❄" : ""), text_color = cTx, text_size = ts)
        table.cell(dash, 3, rowAdapt, "P3 " + (p3On ? "+" + str.tostring(p3Off) : "OFF·wld+" + str.tostring(p3Off)) + " ΔE " + (na(deA) or na(de0) ? "—" : str.tostring(deA - de0, "#.##")) + "R n" + str.tostring(dnA) + "/" + str.tostring(dn0), text_color = p3On ? colWarn : colNeut, text_size = ts)
        table.cell(dash, 0, rowLed, "LEDGER", text_color = colNeut, text_size = ts)
        table.cell(dash, 1, rowLed, "open " + str.tostring(array.size(ledOpen)) + "/24 · done " + str.tostring(array.size(ledR)) + (ledDrop > 0 ? " ⚠drop " + str.tostring(ledDrop) : "") + (invCnt > 0 ? " ⚠inv " + str.tostring(invCnt) : ""), text_color = ledDrop > 0 or invCnt > 0 ? colWarn : cTx, text_size = ts)
        table.cell(dash, 2, rowLed, "MAE50 " + (na(mae50) ? "—" : str.tostring(mae50, "#.##") + "R"), text_color = cTx, text_size = ts)
        table.cell(dash, 3, rowLed, "MFE50 " + (na(mfe50) ? "—" : str.tostring(mfe50, "#.##") + "R"), text_color = cTx, text_size = ts)
    if legAny
        table.cell(dash, 0, rowLeg, "⚠ LEGACY PARITY: " + (legAsym ? "regime-asym " : "") + (legSweep ? "v1-sweep " : "") + (legStruct ? "v1-struct" : ""), text_color = colWarn, text_size = ts)