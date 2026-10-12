#!/usr/bin/env python3
"""AXIOM — single source of truth for the configuration contract.

This script generates, from one table:
  * contracts/config.default.yaml   (human/operator-facing configuration)
  * contracts/registry.json         (machine-readable registry, consumed by the loader)

Rules (AX-13 §6, AX-15 §0-R1):
  * every key maps to exactly one AX-15 parameter id;
  * class V values are NEVER written into the config (they live in venue_profile.json);
  * class C values carry a calibration_ref;
  * class O values default to null and must be supplied by the owner (OI-* ids);
  * the loader refuses unknown keys, missing classes, out-of-range values,
    C-values without a calibration_ref, and O-values without an owner_input id.

Run:  python contracts/build_registry.py            # writes both artifacts
      python contracts/build_registry.py --check    # fails if the files drift
"""
from __future__ import annotations

import json
import sys
from collections import OrderedDict
from pathlib import Path

HERE = Path(__file__).resolve().parent

# (path, id, class, unit, default, lo, hi, calibration_ref, owner_input, note)
ENTRIES: list[tuple] = [
    # --- meta -------------------------------------------------------------
    ("meta.schema_version", "P-META-000", "D", "int", 1, 1, 1, None, None, "contract schema version"),
    ("meta.env", "P-META-001", "D", "enum", "PAPER", None, None, None, None, "RESEARCH|BACKTEST|SHADOW|PAPER|PROBE|MICRO_LIVE|LIVE (AX-01 §6.1)"),
    ("meta.profile", "P-META-002", "D", "str", "default", None, None, None, None, "selects the VenueProfile artifact"),

    # --- venue ------------------------------------------------------------
    ("venue.base_url", "P-VEN-004", "D", "url", "https://api.toobit.com", None, None, None, None, "structural API entry point; measurable venue facts live in venue_profile.json"),
    ("venue.ws_url", "P-VEN-005", "D", "url", "wss://stream.toobit.com/quote/ws/v1", None, None, None, None, "market-data stream entry point (AX-02 §4)"),
    ("venue.profile_path", "P-VEN-006", "D", "path", "runtime/venue_profile.json", None, None, None, None, "produced by the conformance harness (AX-02 §10)"),
    ("venue.profile_max_age_hours", "P-VEN-007", "C", "h", 24, 1, 168, "CAL-DATA-01", None, "older profile ⇒ RK-08 refuses"),
    ("venue.f_safe", "P-VEN-002", "D", "fraction", 0.5, 0.1, 0.9, None, None, "fraction of the venue rate limit the system may use (AX-02 §7.1)"),
    ("venue.max_offset_ms", "P-VEN-001", "C", "ms", 500, 100, 2000, "CAL-EXE-01", None, "clock offset beyond ⇒ RK-06 refuses (AX-02 §2.3)"),
    ("venue.recv_window_ms", "P-VEN-003", "D", "ms", 5000, 1000, 60000, None, None, "recvWindow actually sent; venue default documented as 5000 [V-DOC]"),
    ("venue.backoff_schedule_s", "P-VEN-008", "D", "list[s]", [1, 2, 4, 8, 15, 30], None, None, None, None, "reconnect/retry backoff, capped (P-DATA-006)"),

    # --- data -------------------------------------------------------------
    ("data.hot_depth_snapshot_s", "P-DATA-001", "C", "s", 60, 30, 300, "CAL-DATA-01", None, "HOT tier book cadence (AX-04 §2.1)"),
    ("data.warm_agg_s", "P-DATA-002", "C", "s", 60, 30, 300, "CAL-DATA-01", None, "WARM tier aggregate cadence"),
    ("data.bar_close_grace_s", "P-DATA-003", "C", "s", 5, 2, 30, "CAL-DATA-01", None, "provisional→final grace (AX-03 §3.3)"),
    ("data.staleness_k", "P-DATA-004", "C", "multiple", 2, 1.5, 4, "CAL-DATA-01", None, "stale if age > k·bar interval"),
    ("data.ws_heartbeat_s", "P-DATA-005", "D", "s", 20, 5, 120, None, None, "client ping cadence (venue ping documented [V-DOC])"),
    ("data.reconnect_backoff_s", "P-DATA-006", "D", "list[s]", [1, 2, 4, 8, 15, 30], None, None, None, None, "WS reconnect backoff"),
    ("data.l0_segment_mb", "P-DATA-009", "D", "MB", 256, 64, 1024, None, None, "L0 segment rotation"),
    ("data.journal_fsync", "P-DATA-010", "D", "enum", "per_event", None, None, None, None, "per_event|per_batch (durability of INV-3)"),
    ("data.retention_days_hot", "P-DATA-011", "O", "d", None, 7, 180, None, "OI-CAP-02", "hot-tier retention"),
    ("data.retention_days_warm", "P-DATA-013", "O", "d", None, 180, 3650, None, "OI-CAP-02", "warm-tier retention"),
    ("data.capacity_free_floor_pct", "P-DATA-014", "O", "%", None, 5, 40, None, "OI-CAP-02", "free-space floor before degradation (AX-04 §7)"),
    ("data.repair_trade_history_bars", "P-DATA-007", "D", "bars", 60, 1, 1000, None, None, "REST trades are limited to 60 records [V-DOC]"),
    ("data.kline_page_max", "P-DATA-008", "D", "records", 1000, 100, 1500, None, None, "venue page size [V-DOC]"),
    ("data.universe_refresh_utc", "P-UNI-008", "D", "hh:mm", "00:05", None, None, None, None, "deterministic daily universe freeze (AX-04 §4)"),
    ("data.health_gate_ids", "P-DATA-021", "D", "list", ["QC-01", "QC-07", "QC-09", "QC-12"], None, None, None, None, "gates that can move an instrument to FAIL"),

    # --- universe ---------------------------------------------------------
    ("universe.max_instruments", "P-UNI-001", "O", "count", None, 1, 200, None, "OI-CAP-01", "candidate set is always the full eligible venue set; this caps what may be traded"),
    ("universe.min_bars_complete", "P-UNI-002", "C", "bars", 500, 200, 5000, "CAL-DATA-01", None, "minimum completed history"),
    ("universe.min_listing_days", "P-UNI-003", "C", "d", 30, 7, 180, "CAL-DATA-01", None, "minimum age"),
    ("universe.min_qv_median_usdt", "P-UNI-004", "C", "USDT", 5_000_000, 100_000, 100_000_000, "CAL-DATA-01", None, "median daily quote volume"),
    ("universe.max_spread_bps", "P-UNI-005", "C", "bps", 8, 1, 50, "CAL-DATA-01", None, "median spread"),
    ("universe.participation_cap_mqv", "P-UNI-006", "C", "fraction", 0.05, 0.005, 0.1, "CAL-CST-01", None, "MPN ≤ c·MQV"),
    ("universe.cluster_max", "P-UNI-007", "C", "fraction", 0.40, 0.1, 0.6, "CAL-RSK-01", None, "cluster concentration cap"),

    # --- features ---------------------------------------------------------
    ("features.enabled_t1", "P-FEAT-010", "D", "list[str]", ["F-TS-SLOPE", "F-RV", "F-EWMA", "F-SPR", "F-D1", "F-MICRO", "F-TAKER", "F-OI-QUAD", "F-FUND"], None, None, None, None, "T1 family (AX-05 §3)"),
    ("features.enabled_t2", "P-FEAT-011", "D", "list[str]", ["F-DONJ", "F-ER", "F-HAR-RV", "F-Y-Z", "F-QIMB", "F-KYLE", "F-SLIP-MEAS", "F-CASCADE", "F-BASIS", "F-XS-MOM", "F-BETA-KF", "F-ABSORB", "F-TURB", "F-VOLPCT"], None, None, None, None, "T2 family"),
    ("features.enabled_t3", "P-FEAT-012", "D", "list[str]", ["F-LSR"], None, None, None, None, "T3 / research-only"),
    ("features.scaling_window", "P-FEAT-001", "D", "bars", 500, 100, 5000, None, None, "z-scaling lookback"),
    ("features.clip_sigma", "P-FEAT-002", "D", "sigma", 5, 2, 10, None, None, "clipping bound"),
    ("features.winsor_fraction", "P-FEAT-003", "D", "fraction", 0.005, 0.0, 0.05, None, None, "winsorization"),
    ("features.availability_floor", "P-MON-003", "C", "fraction", 0.90, 0.5, 1.0, "CAL-GOV-01", None, "below ⇒ feature demoted to zero weight"),
    ("features.psi_window_days", "P-MON-001", "C", "d", 30, 7, 365, "CAL-GOV-01", None, "PSI window"),
    ("features.psi_breach", "P-MON-004", "C", "index", 0.25, 0.05, 1.0, "CAL-GOV-01", None, "PSI breach level"),

    # --- admission / research --------------------------------------------
    ("admission.fdr_q", "P-ADM-001", "O", "fraction", None, 0.01, 0.25, None, "OI-RISK-03", "Benjamini–Hochberg level for feature families"),
    ("admission.min_ic", "P-ADM-002", "C", "corr", 0.02, 0.005, 0.1, "CAL-LBL-01", None, "minimum absolute out-of-sample IC"),
    ("admission.cost_stress", "P-ADM-003", "D", "list[multiple]", [1.5, 1.5], None, None, None, None, "cost stress: fee×1.5 and slippage×1.5 (AX-05 §2.3)"),
    ("admission.min_regime_subsets", "P-ADM-004", "D", "count", 3, 1, 4, None, None, "same-sign regime subsets"),
    ("admission.min_sample_ratio", "P-ADM-005", "C", "ratio", 1.0, 0.5, 5.0, "CAL-LBL-01", None, "n_eff ≥ ratio · required sample (Fisher-z power)"),

    # --- forecast ---------------------------------------------------------
    ("forecast.horizons_bars", "P-FCT-001", "O", "list[bars]", None, None, None, None, "OI-RISK-03", "admissible horizons: subset of {1,4,16} ⇒ ≥15 min (AX-01 §2.3)"),
    ("forecast.ridge_lambda", "P-FCT-002", "C", "float", 1.0, 0.001, 1000.0, "CAL-LBL-01", None, "regularisation"),
    ("forecast.hac_lag_multiplier", "P-FCT-003", "D", "multiple", 1.5, 1.0, 4.0, None, None, "HAC lags ≈ multiplier·H"),
    ("forecast.bootstrap_reps", "P-FCT-004", "D", "count", 2000, 200, 20000, None, None, "block bootstrap replications"),
    ("forecast.bootstrap_block_mult", "P-FCT-005", "D", "multiple", 2.0, 1.0, 5.0, None, None, "block length ≈ multiplier·H"),
    ("forecast.p_net_min", "P-FCT-006", "O", "probability", None, 0.5, 0.9, None, "OI-RISK-03", "minimum calibrated probability of positive net return"),
    ("forecast.m_eff_floor", "P-FCT-007", "D", "effective models", 1.2, 1.0, 3.0, None, None, "below ⇒ no trade (AX-06 §5)"),
    ("forecast.weight_clip", "P-FCT-008", "D", "fraction", 0.6, 0.2, 1.0, None, None, "max weight of one model in the combination"),
    ("forecast.edge_z", "P-FCT-009", "O", "sigma", None, 0.0, 2.0, None, "OI-RISK-03", "z for the lower bound of the edge"),
    ("forecast.isotonic_min_sample", "P-FCT-010", "C", "count", 500, 100, 5000, "CAL-LBL-01", None, "minimum calibration sample"),
    ("forecast.brier_skill_floor", "P-CAL-002", "C", "skill", 0.02, 0.0, 0.1, "CAL-LBL-01", None, "below ⇒ horizon suspended"),
    ("forecast.refit_days", "P-CAL-001", "D", "d", 7, 1, 30, None, None, "calibration refit cadence"),

    # --- regime -----------------------------------------------------------
    ("regime.hmm_states_max", "P-REG-001", "D", "count", 4, 2, 6, None, None, "K of the filtered HMM"),
    ("regime.entropy_gate", "P-REG-002", "C", "index", 0.80, 0.5, 1.0, "CAL-REG-01", None, "above ⇒ multiplier→state floor"),
    ("regime.cusum_threshold_q", "P-REG-004", "C", "quantile", 0.99, 0.95, 0.999, "CAL-GOV-01", None, "CUSUM alarm level"),
    ("regime.multiplier_floor", "P-REG-005", "D", "fraction", 0.4, 0.0, 1.0, None, None, "lowest regime risk multiplier"),

    # --- risk -------------------------------------------------------------
    ("risk.risk_fraction", "P-RSK-001", "O", "fraction", None, 0.001, 0.02, None, "OI-RISK-01", "R per trade as a fraction of equity"),
    ("risk.d_max", "P-RSK-002", "O", "fraction", None, 0.03, 0.30, None, "OI-RISK-02", "drawdown at which the system hard de-risks"),
    ("risk.k_d", "P-RSK-003", "D", "multiple", 1.5, 1.0, 3.0, None, None, "drawdown→risk conversion"),
    ("risk.n_bets_per_day", "P-RSK-004", "C", "count", 6, 1, 50, "CAL-RSK-01", None, "expected trades/day; recomputed monthly (AX-15 §6)"),
    ("risk.daily_loss_cap", "P-RSK-006", "O", "fraction", None, 0.01, 0.10, None, "OI-RISK-04", "stop new risk for the UTC day"),
    ("risk.sigma_target_annual", "P-RSK-007", "O", "fraction", None, 0.05, 0.60, None, "OI-RISK-03", "annualised volatility target"),
    ("risk.g_max", "P-RSK-008", "O", "multiple", None, 1.0, 5.0, None, "OI-RISK-03", "maximum gross exposure"),
    ("risk.gamma", "P-RSK-009", "D", "float", 2.0, 0.5, 10.0, None, None, "risk aversion"),
    ("risk.cov_half_life_days", "P-RSK-010", "C", "d", 60, 10, 250, "CAL-RSK-01", None, "EWMA covariance half-life"),
    ("risk.mp_denoise", "P-RSK-012", "D", "bool", True, None, None, None, None, "Marchenko–Pastur eigenvalue denoising"),
    ("risk.hrp_beta", "P-RSK-014", "C", "fraction", 0.5, 0.0, 1.0, "CAL-RSK-01", None, "shrinkage toward inverse-variance"),
    ("risk.no_trade_band_mult", "P-RSK-020", "C", "multiple", 1.0, 0.5, 3.0, "CAL-CST-01", None, "cost-aware rebalancing band"),
    ("risk.turnover_cap_x_gross", "P-RSK-021", "O", "multiple", None, 0.1, 3.0, None, "OI-RISK-03", "daily turnover cap"),
    ("risk.gross_cap", "P-RSK-030", "O", "multiple", None, 1.0, 5.0, None, "OI-RISK-03", "Σ|notional|/equity"),
    ("risk.net_cap", "P-RSK-031", "O", "multiple", None, 0.2, 3.0, None, "OI-RISK-03", "|Σ signed notional|/equity"),
    ("risk.per_instrument_cap", "P-RSK-032", "C", "fraction", 0.25, 0.05, 0.5, "CAL-RSK-01", None, "single instrument share of gross"),
    ("risk.portfolio_beta_cap", "P-RSK-034", "O", "beta", None, 0.0, 1.5, None, "OI-RISK-03", "index-beta cap"),
    ("risk.participation_cap_d1", "P-RSK-042", "C", "fraction", 0.10, 0.01, 0.2, "CAL-CST-01", None, "≤ c·D1 of daily volume"),
    ("risk.max_exit_minutes", "P-RSK-043", "C", "min", 2.0, 0.5, 15.0, "CAL-CST-01", None, "time to exit the position at MQV"),
    ("risk.kelly_fraction", "P-RSK-050", "O", "fraction", None, 0.05, 0.5, None, "OI-RISK-05", "fraction of the LCB-Kelly size"),
    ("risk.kelly_lcb_factor", "P-RSK-051", "C", "fraction", 0.6, 0.3, 0.9, "CAL-MRG-01", None, "lower confidence bound on the Kelly size"),
    ("risk.k_safe", "P-RSK-060", "C", "multiple", 3.0, 1.5, 8.0, "CAL-MRG-01", None, "liquidation distance ≥ k_safe·s_stop"),
    ("risk.c_sigma", "P-RSK-061", "C", "multiple", 2.5, 1.5, 5.0, "CAL-STP-01", None, "stop σ multiple"),
    ("risk.c_cost", "P-RSK-062", "C", "multiple", 3.0, 1.5, 6.0, "CAL-STP-01", None, "stop cost multiple"),
    ("risk.q_tail", "P-RSK-063", "C", "quantile", 0.995, 0.99, 0.9999, "CAL-STP-01", None, "tail quantile for the gap term"),
    ("risk.tail_multiplier_cap", "P-RSK-064", "O", "multiple", None, 1.0, 5.0, None, "OI-RISK-05", "maximum gap loss as a multiple of R"),
    ("risk.max_open_positions", "P-RSK-070", "O", "count", None, 1, 30, None, "OI-CAP-01", "attention and margin bound"),
    ("risk.margin_util_cap", "P-MRG-001", "O", "fraction", None, 0.1, 0.9, None, "OI-RISK-02", "Σ margin + reservations ≤ cap·equity"),
    ("risk.pretrade_check_order", "P-RSK-080", "D", "list[str]", ["RK-01", "RK-02", "RK-03", "RK-04", "RK-05", "RK-06", "RK-07", "RK-08", "RK-09", "RK-10", "RK-11", "RK-12", "RK-13", "RK-14", "RK-15", "RK-16", "RK-17", "RK-18", "RK-19", "RK-20", "RK-21", "RK-22", "RK-23", "RK-24", "RK-25"], None, None, None, None, "normative order (AX-09 §2)"),

    # --- execution --------------------------------------------------------
    ("execution.taker_only", "P-EXE-070", "D", "bool", True, None, None, None, None, "ADR-009: post-only disabled by policy"),
    ("execution.allow_post_only", "P-EXE-071", "D", "bool", False, None, None, None, None, "enabling requires a Class-3 ADR"),
    ("execution.k_cross", "P-EXE-001", "C", "multiple", 0.25, 0.0, 2.0, "CAL-EXE-02", None, "cross price = mid ± k·spread"),
    ("execution.tick_slack", "P-EXE-002", "D", "ticks", 2, 0, 10, None, None, "ticks beyond the touch when crossing"),
    ("execution.protection_bound_s", "P-EXE-003", "C", "s", 10, 5, 60, "CAL-EXE-01", None, "unprotected window bound (AX-08 §6.4)"),
    ("execution.max_attempts", "P-EXE-005", "D", "count", 2, 1, 5, None, None, "attempts per intent"),
    ("execution.resolve_attempts", "P-EXE-010", "D", "count", 5, 1, 10, None, None, "ambiguity-ladder queries"),
    ("execution.resolve_window_s", "P-EXE-011", "D", "s", 60, 10, 300, None, None, "total resolution window"),
    ("execution.slice_threshold_mqv", "P-EXE-020", "C", "fraction", 0.05, 0.01, 0.2, "CAL-EXE-03", None, "above ⇒ sliced execution"),
    ("execution.slice_spacing_s", "P-EXE-021", "C", "s", 15, 5, 120, "CAL-EXE-03", None, "delay between slices"),
    ("execution.order_deadline_min", "P-EXE-022", "D", "min", 5, 1, 30, None, None, "residual abandoned after this"),
    ("execution.max_working_orders", "P-EXE-040", "D", "count", 3, 1, 8, None, None, "per instrument"),
    ("execution.max_new_positions_per_min", "P-EXE-041", "O", "count", None, 1, 20, None, "OI-OPS-03", "operational pace cap"),
    ("execution.unprotected_escalate_s", "P-EXE-031", "D", "s", 60, 15, 300, None, None, "SEV-2 threshold"),
    ("execution.unprotected_flatten_r", "P-EXE-032", "D", "R", 2.0, 1.0, 5.0, None, None, "flatten if unprotected and notional > this"),
    ("execution.adverse_window_s", "P-EXE-050", "D", "s", 120, 10, 900, None, None, "adverse-selection measurement window"),
    ("execution.opportunity_cost_allowance", "P-EXE-051", "O", "fraction", None, 0.05, 0.5, None, "OI-RISK-03", "max share of gross edge lost to non-execution"),
    ("execution.emergency_offset_spreads", "P-EXE-060", "D", "multiples", 5, 2, 50, None, None, "emergency IOC offset when market orders are forbidden"),
    ("execution.flatten_budget_s", "P-EXE-061", "D", "s", 30, 10, 180, None, None, "flatten must complete within this"),

    # --- cost -------------------------------------------------------------
    ("cost.upper_quantile", "P-COST-010", "C", "quantile", 0.75, 0.5, 0.99, "CAL-CST-01", None, "cost upper estimator"),
    ("cost.uncertainty_m", "P-COST-021", "O", "multiple", None, 0.0, 3.0, None, "OI-RISK-03", "m_c on σ_cost in the gate"),
    ("cost.edge_z", "P-COST-020", "O", "sigma", None, 0.0, 2.0, None, "OI-RISK-03", "z_g on σ_model in the gate"),
    ("cost.min_samples_refit", "P-COST-011", "D", "count", 100, 30, 1000, None, None, "fills needed for a refit"),
    ("cost.sessions_above_band", "P-COST-030", "D", "count", 5, 2, 20, None, None, "K5 after this many consecutive sessions"),
    ("cost.funding_defer_ratio", "P-COST-001", "C", "fraction", 0.25, 0.05, 0.5, "CAL-CST-01", None, "defer entry if funding > this share of edge"),
    ("cost.slip_buckets_mqv", "P-COST-012", "D", "list[fraction]", [0.001, 0.005, 0.01, 0.05], None, None, None, None, "slippage bucket boundaries"),

    # --- governor ---------------------------------------------------------
    ("governor.caution_q", "P-GOV-100", "C", "quantile", 0.95, 0.8, 0.99, "CAL-GOV-01", None, "CAUTION trigger quantile"),
    ("governor.reduced_q", "P-GOV-101", "C", "quantile", 0.99, 0.9, 0.999, "CAL-GOV-01", None, "REDUCED trigger quantile"),
    ("governor.defensive_q", "P-GOV-102", "C", "quantile", 0.995, 0.95, 0.9999, "CAL-GOV-01", None, "DEFENSIVE trigger quantile"),
    ("governor.dwell_hours_performance", "P-GOV-040", "D", "h", 24, 1, 168, None, None, "clean evaluations before recovery"),
    ("governor.dwell_hours_health", "P-GOV-041", "D", "h", 1, 0.25, 24, None, None, "for health/venue triggers"),
    ("governor.multipliers", "P-GOV-103", "D", "map", {"NORMAL": 1.0, "CAUTION": 0.7, "REDUCED": 0.4, "DEFENSIVE": 0.15, "FLATTEN": 0.0, "HALT": 0.0}, 0.0, 1.0, None, None, "m_gov by state (AX-09 §3)"),
    ("governor.journal_verify_minutes", "P-GOV-001", "D", "min", 10, 1, 120, None, None, "RK-07 cadence"),
    ("governor.reconcile_freshness_s", "P-GOV-002", "D", "s", 60, 10, 900, None, None, "RK-09 freshness"),
    ("governor.api_fail_k2", "P-GOV-060", "D", "count", 5, 2, 20, None, None, "consecutive failures ⇒ K2"),
    ("governor.heartbeat_expiry_h", "P-GOV-091", "O", "h", None, 1, 168, None, "OI-OPS-03", "operator heartbeat; expiry ⇒ stricter state"),
    ("governor.escalation_minutes", "P-GOV-081", "D", "list[min]", [5, 15, 30], None, None, None, None, "SEV-1 repeat / SEV-2 ack / SEV-2 action"),
    ("governor.ladder_incidents_month", "P-LRN-021", "O", "count", None, 0, 10, None, "OI-OPS-03", "SEV-2 budget per month"),

    # --- learning (offline) ------------------------------------------------
    ("learning.embargo_bars", "P-LRN-001", "D", "bars", "max(H, 50)", None, None, None, None, "purge/embargo (AX-10 §3.2)"),
    ("learning.folds", "P-LRN-008", "D", "count", 5, 3, 20, None, None, "purged K-fold count"),
    ("learning.psr_floor", "P-LRN-005", "O", "probability", None, 0.9, 0.999, None, "OI-RISK-05", "PSR(DSR) required for promotion"),
    ("learning.pbo_max", "P-LRN-007", "O", "probability", None, 0.1, 0.7, None, "OI-RISK-05", "PBO ceiling (CSCV)"),
    ("learning.spa_reps", "P-LRN-004", "D", "count", 5000, 1000, 50000, None, None, "stationary bootstrap replications"),
    ("learning.cscv_blocks", "P-LRN-006", "D", "count", 16, 4, 64, None, None, "CSCV blocks"),
    ("learning.hypothesis_cap_month", "P-LRN-060", "O", "count", None, 1, 50, None, "OI-RISK-05", "pre-registered hypotheses per month"),
    ("learning.shadow_days", "P-LRN-011", "O", "d", None, 7, 90, None, "OI-OPS-03", "L3 duration"),
    ("learning.paper_days", "P-LRN-012", "O", "d", None, 14, 120, None, "OI-OPS-03", "L4 duration"),
    ("learning.micro_live_fraction", "P-LRN-016", "O", "fraction", None, 0.02, 0.5, None, "OI-RISK-01", "L5 risk fraction"),
    ("learning.sim_haircut", "P-SIM-010", "C", "fraction", 0.8, 0.3, 1.0, "CAL-SIM-01", None, "fill-fraction haircut"),
    ("learning.intrabar_rule", "P-SIM-011", "D", "enum", "adverse_first", None, None, None, None, "changing this requires an ADR (AX-11 §4.3)"),

    # --- operations -------------------------------------------------------
    ("ops.tick_s", "P-OPS-031", "C", "s", 15, 5, 60, "CAL-DATA-01", None, "decision cadence (bar-aligned); equals the smallest horizon bar length"),
    ("ops.backup_interval_min", "P-OPS-040", "O", "min", None, 5, 1440, None, "OI-CAP-02", "journal backup RPO"),
    ("ops.backup_locations", "P-OPS-043", "O", "list[path]", None, None, None, None, "OI-CAP-02", "at least one off-device"),
    ("ops.log_level", "P-OPS-110", "D", "enum", "INFO", None, None, None, None, "DEBUG|INFO|WARN|ERROR"),
    ("ops.telemetry_retention_days", "P-OPS-080", "D", "d", 90, 7, 3650, None, None, "metrics/log retention"),
    ("ops.notify_channel", "P-OPS-120", "O", "enum", None, None, None, None, "OI-OPS-02", "telegram|console|email|none"),
    ("ops.notify_destination_ref", "P-OPS-121", "O", "secret-ref", None, None, None, None, "OI-OPS-02", "identifier resolved from the secret store; never a literal in this file"),
    ("ops.topology", "P-OPS-130", "O", "enum", None, None, None, None, "OI-OPS-01", "A single-node | B edge+compute | C server"),
    ("ops.single_writer_lock", "P-OPS-131", "D", "path", "runtime/axiom.lock", None, None, None, None, "prevents a second live instance"),
    ("ops.restart_backoff_s", "P-OPS-020", "D", "list[s]", [1, 5, 15, 60, 300], None, None, None, None, "supervisor restart backoff"),
    ("ops.crash_loop_restarts", "P-OPS-021", "D", "count", 5, 2, 50, None, None, "restarts within the window that force OFF"),
    ("ops.crash_loop_window_min", "P-OPS-022", "D", "min", 30, 5, 240, None, None, "crash-loop window"),
    ("ops.heartbeat_s", "P-OPS-023", "D", "s", 30, 5, 300, None, None, "watchdog heartbeat"),
    ("ops.param_cooloff_minutes", "P-OPS-070", "O", "min", None, 5, 1440, None, "OI-OPS-03", "cooling-off before a risk-parameter change applies"),
    ("ops.max_manual_actions_per_hour", "P-OPS-101", "O", "count", None, 1, 50, None, "OI-OPS-03", "friction against impulsive intervention"),
    ("ops.max_manual_change_r", "P-OPS-102", "O", "R", None, 0.5, 5.0, None, "OI-RISK-01", "a manual action may not exceed this risk"),

    # --- security ---------------------------------------------------------
    ("security.key_rotation_days", "P-SEC-001", "O", "d", None, 30, 365, None, "OI-OPS-03", "key rotation interval"),
    ("security.require_ip_whitelist", "P-SEC-010", "D", "bool", True, None, None, None, None, "venue rejects unbound keys (-1023) [V-DOC]"),
    ("security.forbidden_permissions", "P-SEC-011", "D", "list[str]", ["WITHDRAW", "TRANSFER"], None, None, None, None, "must be impossible on the API key"),

    # --- tests ------------------------------------------------------------
    ("tests.coverage_floor_pct", "P-TST-003", "O", "%", None, 50, 100, None, "OI-OPS-03", "branch coverage floor on decision-critical packages"),
    ("tests.mutation_per_module", "P-TST-004", "D", "count", 1, 1, 20, None, None, "surviving mutants per module fail the build"),
    ("tests.conformance_evidence_days", "P-TST-001", "D", "d", 30, 1, 365, None, None, "G5 evidence expiry"),
    ("tests.statistical_evidence_months", "P-TST-002", "D", "months", 3, 1, 24, None, None, "G3 evidence expiry"),
]

# --- additional ids tabulated in AX-15 §3–§8 (appendix §12 completes the mapping) ---
ADDITIONAL: list[tuple] = [
    ("forecast.sharpness_floor", "P-CAL-003", "C", "index", 0.0, 0.0, 1.0, "CAL-LBL-01", None, "sharpness is measured; the floor is set by calibration (AX-06 §3.3)"),
    ("data.qc_thresholds", "P-DATA-020", "C", "map", {"QC-09_spread_mult": 4.0, "QC-12_gap_bars": 3, "QC-13_burst_mult": 5.0, "QC-15_zero_vol_bars": 20}, None, None, "CAL-DATA-01", None, "per-gate thresholds (AX-04 §3)"),
    ("features.taker_window_bars", "P-FLOW-001", "D", "bars", 1, 1, 5, None, None, "window for the taker split (AX-05 §3.4)"),
    ("features.oi_quad_deciles", "P-FLOW-002", "C", "list[quantile]", [0.1,0.25,0.5,0.75,0.9], None, None, "CAL-FLOW-01", None, "OI-change quadrant boundaries"),
    ("features.funding_stress_q", "P-FLOW-003", "C", "quantile", 0.99, 0.95, 0.9999, "CAL-GOV-01", None, "funding-stress trigger"),
    ("features.depth_levels", "P-LIQ-001", "D", "levels", 5, 1, 20, None, None, "levels used by F-D1 / F-MICRO"),
    ("features.spread_ewma_half_life", "P-LIQ-002", "C", "bars", 50, 10, 200, "CAL-CST-01", None, "spread EWMA"),
    ("features.kyle_window_trades", "P-LIQ-003", "C", "trades", 200, 50, 2000, "CAL-CST-01", None, "Kyle-lambda window (used by the cost model too)"),
    ("features.vol_half_life_bars", "P-VOL-001", "C", "bars", 30, 10, 120, "CAL-VOL-01", None, "EWMA vol half-life"),
    ("features.har_windows", "P-VOL-002", "D", "list[bars]", [1,5,22], None, None, None, None, "HAR-RV windows"),
    ("features.vol_percentile_lookback", "P-VOL-003", "C", "bars", 500, 200, 2000, "CAL-VOL-01", None, "volatility percentile lookback"),
    ("features.xs_ranking_window", "P-XS-001", "C", "bars", 20, 5, 200, "CAL-LBL-01", None, "cross-sectional ranking window (AX-05 §3.5)"),
    ("features.xs_min_breadth", "P-XS-002", "D", "count", 5, 3, 50, None, None, "minimum cross-sectional breadth for any XS feature"),
    ("regime.cusum_drift", "P-REG-003", "C", "sigma", 0.5, 0.1, 1.5, "CAL-REG-01", None, "CUSUM drift parameter k"),
    ("risk.r_floor_rule", "P-RSK-005", "D", "enum", "min_notional_feasibility", None, None, None, None, "R is floored so that one step of the smallest tradable size is a legal position (AX-07 §3.2)"),
    ("risk.lw_shrinkage", "P-RSK-011", "D", "enum", "analytic", None, None, None, None, "Ledoit-Wolf analytic intensity (ADR-014)"),
    ("risk.cluster_count_rule", "P-RSK-013", "D", "enum", "sqrt(N/2)", None, None, None, None, "number of correlation clusters (AX-07 §5.3)"),
    ("risk.surplus_tolerance", "P-RSK-022", "D", "fraction", 1e-06, 0.0, 0.001, None, None, "ties in the surplus ranking (deterministic order)"),
    ("risk.cluster_cap", "P-RSK-033", "C", "fraction", 0.40, 0.1, 0.6, "CAL-RSK-01", None, "portfolio cluster cap (allocation stage; distinct from the universe breadth rule P-UNI-007)"),
    ("risk.participation_cap_mqv", "P-RSK-041", "C", "fraction", 0.05, 0.005, 0.1, "CAL-CST-01", None, "same estimator as P-UNI-006, applied at sizing time"),
    ("risk.per_position_risk_share", "P-RSK-071", "D", "fraction", 0.5, 0.1, 1.0, None, None, "one position may not consume more than this share of the daily risk budget"),
    ("risk.margin_health_warn", "P-MRG-002", "D", "fraction", 0.30, 0.1, 0.6, None, None, "margin-health warning level (venue-reported)"),
    ("risk.margin_health_critical", "P-MRG-004", "D", "fraction", 0.15, 0.05, 0.3, None, None, "margin-health critical level"),
    ("risk.leverage_readback_required", "P-MRG-003", "D", "bool", True, None, None, None, None, "leverage is set and then read back before any entry (AX-07 §8.4)"),
    ("governor.stop_tighten_caution_pct", "P-GOV-010", "D", "%", 20, 5, 50, None, None, "stop tightening in CAUTION"),
    ("governor.reduced_min_p_net", "P-GOV-011", "C", "probability", 0.65, 0.5, 0.95, "CAL-GOV-01", None, "new positions in REDUCED require a higher calibrated probability"),
    ("governor.reduced_max_horizon", "P-GOV-012", "D", "bars", 4, 1, 16, None, None, "longest horizon allowed in REDUCED"),
    ("governor.defensive_close_pct", "P-GOV-013", "D", "%", 50, 10, 100, None, None, "share of gross closed in DEFENSIVE"),
    ("governor.health_fail_reduced", "P-GOV-020", "D", "count", 3, 1, 20, None, None, "instruments in FAIL before REDUCED"),
    ("governor.health_fail_defensive", "P-GOV-021", "D", "count", 5, 2, 30, None, None, "instruments in FAIL before DEFENSIVE"),
    ("governor.funding_stress_instruments", "P-GOV-030", "D", "count", 5, 1, 50, None, None, "instruments above the funding-stress quantile"),
    ("governor.exec_multiplier_warn", "P-GOV-050", "D", "fraction", 0.7, 0.1, 1.0, None, None, "m_exec when realised cost is above the band"),
    ("governor.exec_multiplier_stale", "P-GOV-051", "D", "fraction", 0.5, 0.05, 1.0, None, None, "m_exec when the cost model is stale"),
    ("governor.k6_trigger_fraction", "P-GOV-070", "D", "fraction", 0.5, 0.1, 0.9, None, None, "liquidation distance below this share of the safe requirement triggers K6"),
    ("governor.status_refusals", "P-GOV-080", "D", "count", 20, 5, 200, None, None, "refusals shown in the status view"),
    ("governor.gap_loss_multiplier", "P-GOV-090", "O", "multiple", None, 1.0, 5.0, None, "OI-RISK-05", "gap-only loss tolerated by the tail budget (same policy as P-RSK-064)"),
    ("monitoring.min_ic_posterior", "P-MON-002", "C", "quantile", 0.05, 0.01, 0.3, "CAL-GOV-01", None, "rolling IC posterior below which a feature is demoted"),
    ("learning.min_embargo_bars", "P-LRN-002", "D", "bars", 50, 1, 500, None, None, "floor for the embargo width"),
    ("learning.walk_forward_step", "P-LRN-003", "C", "bars", 500, 50, 5000, "CAL-LBL-01", None, "re-fit step"),
    ("learning.regime_subsets_same_sign", "P-LRN-010", "D", "count", 3, 1, 6, None, None, "pre-declared regime subsets that must agree"),
    ("learning.max_sim_model_cost_gap", "P-LRN-013", "C", "fraction", 0.3, 0.1, 1.0, "CAL-SIM-01", None, "allowed simulator-vs-model cost gap"),
    ("learning.min_sim_round_trips", "P-LRN-014", "C", "count", 30, 10, 500, "CAL-SIM-01", None, "paper-mode round trips"),
    ("learning.max_cost_gate_refusal_rate", "P-LRN-015", "C", "fraction", 0.98, 0.5, 1.0, "CAL-CST-01", None, "above this the candidate is not tradable, not promotable"),
    ("learning.clean_days_micro_live", "P-LRN-017", "O", "d", None, 3, 30, None, "OI-OPS-03", "clean reconciliation days before micro-live"),
    ("learning.min_trades_l5", "P-LRN-018", "C", "count", 20, 5, 500, "CAL-LBL-01", None, "trades required at L5"),
    ("learning.min_trades_l6", "P-LRN-019", "C", "count", 60, 20, 2000, "CAL-LBL-01", None, "trades required at L6"),
    ("learning.live_dsr_floor", "P-LRN-020", "O", "probability", None, 0.9, 0.999, None, "OI-RISK-05", "live DSR required to scale"),
    ("learning.demotion_psr_floor", "P-LRN-030", "O", "probability", None, 0.8, 0.99, None, "OI-RISK-05", "PSR floor before a one-rung demotion"),
    ("learning.max_unresolved_sev1_days", "P-LRN-031", "O", "d", None, 1, 30, None, "OI-OPS-03", "unresolved SEV-1 older than this moves the system to paper"),
    ("learning.champion_review_days", "P-LRN-040", "O", "d", None, 7, 365, None, "OI-OPS-03", "scheduled champion/challenger review"),
    ("learning.n_bets_tolerance", "P-LRN-050", "C", "fraction", 0.5, 0.2, 1.0, "CAL-RSK-01", None, "turnover deviation that forces recomputing R"),
    ("learning.post_retirement_days", "P-LRN-070", "D", "d", 90, 7, 730, None, None, "monitoring after retirement (the autopsy)"),
    ("learning.warmup_rule", "P-SIM-001", "D", "enum", "max_min_history_plus_10pct", None, None, None, None, "replay warm-up (AX-11 §2)"),
    ("learning.mark_penalty_ticks", "P-SIM-020", "D", "ticks", 2, 0, 10, None, None, "mark-price proxy penalty"),
    ("learning.maker_through_ticks", "P-SIM-021", "D", "ticks", 1, 1, 5, None, None, "maker fill requires trade-through"),
    ("learning.replay_cadence_days", "P-SIM-030", "D", "d", 14, 7, 90, None, None, "live-tape replay test cadence"),
    ("learning.illiq_spread_multiple", "P-SIM-040", "D", "multiple", 5, 2, 50, None, None, "illiquidity scenario"),
    ("learning.outage_minutes", "P-SIM-041", "D", "min", 30, 5, 480, None, None, "outage scenario duration"),
    ("ops.standalone_days", "P-OPS-001", "O", "d", None, 7, 365, None, "OI-OPS-01", "days the live loop must operate without a second machine"),
    ("ops.decision_p99_s", "P-OPS-010", "C", "s", 5, 0.5, 30, "CAL-DATA-01", None, "BENCH-01 criterion"),
    ("ops.tick_lateness_s", "P-OPS-030", "D", "s", 5, 1, 60, None, None, "late cycle ⇒ skip, never back-fill"),
    ("ops.status_refusals", "P-OPS-050", "D", "count", 20, 5, 200, None, None, "refusals listed by the status command"),
    ("ops.paper_soak_days", "P-OPS-060", "O", "d", None, 3, 60, None, "OI-OPS-03", "observation window before a live deploy"),
    ("ops.live_verify_hours", "P-OPS-061", "O", "h", None, 24, 720, None, "OI-OPS-03", "post-deploy live verification window"),
    ("ops.postmortem_deadline_days", "P-OPS-090", "O", "d", None, 1, 14, None, "OI-OPS-03", "deadline for an incident postmortem"),
    ("ops.notify_max_per_hour", "P-OPS-100", "O", "count", None, 1, 200, None, "OI-OPS-03", "SEV-3/4 notification budget"),
]

OWNER_INPUTS = [
    ("OI-RISK-01", "risk appetite per trade (R_fraction; also sets the micro-live fraction)", "AX-15 §9"),
    ("OI-RISK-02", "drawdown at which the system must hard de-risk (D_max) and the margin-utilisation cap", "AX-15 §9"),
    ("OI-RISK-03", "volatility target, admissible horizons, gross/net/beta caps, turnover cap, edge/cost margins", "AX-15 §9"),
    ("OI-RISK-04", "daily loss cap", "AX-15 §9"),
    ("OI-RISK-05", "tail multiplier, Kelly fraction, statistical-promotion strictness (PSR/PBO), experiment budget", "AX-15 §9"),
    ("OI-CAP-01", "maximum universe size and maximum open positions", "AX-15 §9"),
    ("OI-CAP-02", "retention, storage budget, backup interval and locations", "AX-15 §9"),
    ("OI-OPS-01", "deployment topology (A/B/C) and the machine that runs the live loop", "AX-15 §9"),
    ("OI-OPS-02", "notification channel and destination for SEV-1/2 and digests", "AX-15 §9"),
    ("OI-OPS-03", "review cadence, operator heartbeat, cooling-off, manual-action limits, durations of the ladder rungs", "AX-15 §9"),
    ("OI-GOV-01", "who may arm, promote, and issue the hard kill (and whether a second person exists)", "AX-15 §9"),
]

HEADER = """# AXIOM — default configuration contract (v1)
#
# GENERATED by contracts/build_registry.py from the single parameter table.
# Do not hand-edit: edit the table and re-run the generator.
#
# Rules:
#  * every key maps to exactly one AX-15 parameter id (see contracts/registry.json);
#  * class V values are NEVER stored here — they come from venue_profile.json (AX-02 §10);
#  * class C values carry a calibration_ref; the loader refuses a C value without one;
#  * class O values are owner inputs: they are null here on purpose, the system stays OFF
#    until the owner supplies them (AX-15 §9), and it never substitutes a default;
#  * a key present with value null is *missing*, not zero. The loader records the source
#    of every resolved value (default | calibration | owner | profile).
"""


def emit_yaml(entries) -> str:
    groups: "OrderedDict[str, list]" = OrderedDict()
    for path, *rest in entries:
        groups.setdefault(path.split(".")[0], []).append((path, rest))
    out = [HEADER]
    for group, rows in groups.items():
        out.append(f"{group}:")
        for path, rest in rows:
            pid, cls, unit, default, lo, hi, cal, owner, note = rest
            key = path.split(".", 1)[1]
            if default is None:
                value = "null"
            elif isinstance(default, bool):
                value = "true" if default else "false"
            elif isinstance(default, list):
                value = "[" + ", ".join(json.dumps(v) for v in default) + "]"
            elif isinstance(default, dict):
                value = "{" + ", ".join(f"{k}: {json.dumps(v)}" for k, v in default.items()) + "}"
            elif isinstance(default, str):
                value = json.dumps(default)
            else:
                value = json.dumps(default)
            meta = f"# {pid} [{cls}] {unit}"
            if cal:
                meta += f" cal:{cal}"
            if owner:
                meta += f" owner:{owner}"
            out.append(f"  {key}: {value}  {meta}  # {note}")
        out.append("")
    out.append("owner_inputs:")
    out.append("  # Required decisions (AX-15 §9). Until every one is supplied the system remains OFF.")
    for oid, desc, ref in OWNER_INPUTS:
        out.append(f"  {oid}: null  # {desc}  ({ref})")
    out.append("")
    return "\n".join(out) + "\n"


def emit_registry(entries) -> str:
    reg = {
        "$comment": "AXIOM parameter registry — generated by contracts/build_registry.py; consumed by the config loader (AX-13 §6).",
        "schema_version": 1,
        "parameters": {
            path: {
                "id": pid,
                "class": cls,
                "unit": unit,
                "default": default,
                "range": [lo, hi] if lo is not None or hi is not None else None,
                "calibration_ref": cal,
                "owner_input": owner,
                "note": note,
            }
            for path, pid, cls, unit, default, lo, hi, cal, owner, note in entries
        },
        "owner_inputs": {
            oid: {"description": desc, "authority": ref} for oid, desc, ref in OWNER_INPUTS
        },
    }
    return json.dumps(reg, indent=2, ensure_ascii=False) + "\n"


ENTRIES_ALL = ENTRIES + ADDITIONAL


def main() -> int:
    entries = ENTRIES_ALL

    yaml_text = emit_yaml(entries)
    reg_text = emit_registry(entries)
    cfg = HERE / "config.default.yaml"
    reg = HERE / "registry.json"
    check = "--check" in sys.argv
    if check:
        ok = True
        if not cfg.exists() or cfg.read_text(encoding="utf-8") != yaml_text:
            print(f"DRIFT: {cfg} is not what the table produces", file=sys.stderr)
            ok = False
        if not reg.exists() or reg.read_text(encoding="utf-8") != reg_text:
            print(f"DRIFT: {reg} is not what the table produces", file=sys.stderr)
            ok = False
        ids = [e[1] for e in entries]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            print(f"DUPLICATE ids: {sorted(dupes)}", file=sys.stderr)
            ok = False
        for path, pid, cls, *_ in entries:
            if cls == "V":
                print(f"VIOLATION: class V parameter {pid} ({path}) must not be in the config", file=sys.stderr)
                ok = False
        print("registry check:", "OK" if ok else "FAILED")
        return 0 if ok else 1
    cfg.write_text(yaml_text, encoding="utf-8")
    reg.write_text(reg_text, encoding="utf-8")
    print(f"wrote {cfg} ({len(entries)} parameters) and {reg}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
