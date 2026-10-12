# AX-13 — Interface Contracts (Module APIs, Events, Configuration)

**Status:** Normative. Signatures here are binding; implementations may add private helpers but must not
change public names, argument order, or semantics.
**Upstream:** AX-03 (objects), AX-04, AX-06, AX-07, AX-08, AX-09, AX-10, AX-11, AX-12.
**Downstream:** the code; AX-14 (tests reference these names).

---

## 1. Conventions (`AX-13:§1`)

- **Language/runtime:** Python ≥ 3.11, single language for runtime and research (one language means one
  implementation of the kernel, INV-5). Typing is mandatory on public interfaces; `mypy --strict` is a
  gate (`T-ARCH-003`).
- **Data types:** frozen `dataclass`es or pydantic models with `extra="forbid"`; monetary/price
  quantities are `Decimal` at the wire boundary and `float` in computation (AX-03 §4.1).
- **Errors:** every public function either returns a result object or raises an exception from the
  fixed taxonomy (§7). No bare `except Exception` in a code path that touches orders
  (`T-ARCH-004`).
- **Purity:** functions in `sfp`, `fcp`, `pfp` are pure: no I/O, no clock, no randomness
  (`T-FEAT-002`). All external inputs arrive as arguments.
- **Determinism:** no `set` iteration order dependence in decision paths; all loops over ordered
  sequences; all randomness from an injected `rng: random.Random` seeded explicitly.
- **Time:** never `time.time()` inside logic; a `Clock` object is injected (`now_utc_ms()`,
  `monotonic_ms()`, `server_offset_ms()`).

---

## 2. Package layout (`AX-13:§2`)

```
axiom/
  core/        types.py, ids.py, hashing.py, clock.py, errors.py, params.py, config.py
  vap/         client.py, signer.py, governor_rl.py, clock_sync.py, classify.py, conformance.py
  mdp/         collectors.py, gates.py, store_l0.py, store_l1.py, universe.py, snapshot.py, health.py, repair.py
  sfp/         cursor.py, registry.py, features_*.py, scaling.py
  fcp/         models.py, pipeline.py, calibrate.py, regime.py, combine.py
  pfp/         cov.py, cluster.py, optimize.py, size.py, stops.py, targets.py
  rg/          kernel.py, governor.py, kills.py, escalation.py
  exp/         planner.py, order_manager.py, protection.py, reconcile.py, cost_ledger.py, quality.py
  lnp/         dataset.py, replay.py, sim_venue.py, experiments.py, stats.py, promotion.py, drift.py
  cop/         journal.py, metrics.py, notifier.py, cli.py, backup.py, redaction.py
tests/         unit/, property/, integration/, parity/, fault/, conformance/, statistical/, soak/
contracts/     config.default.yaml, sql/, schemas/
```

The import linter enforces these edges only:
`cop ← (all)`, `vap ← mdp ← sfp ← fcp ← pfp ← rg ← exp`, with `lnp` importing anything *except* a
running process, and nothing importing `lnp` except `cop` (for reports). Violations fail the build
(`T-ARCH-001`).

---

## 3. Core types (`AX-13:§3`)

```python
# core/types.py
Env            = Literal["RESEARCH","BACKTEST","SHADOW","PAPER","PROBE","MICRO_LIVE","LIVE"]
IntentPurpose  = Literal["ENTRY","PROTECT","EXIT","FLATTEN","CANCEL","MODIFY","LEVERAGE","MARGIN_TYPE"]
SideSemantic   = Literal["OPEN_LONG","OPEN_SHORT","CLOSE_LONG","CLOSE_SHORT"]
OrderState     = Literal["WRITTEN","SENT","ACKED","PARTIAL","FILLED","REJECTED","UNKNOWN",
                         "RESOLVED_FILLED","RESOLVED_WORKING","RESOLVED_ABSENT","RESOLVED_ESCALATED","ABANDONED"]
GovState       = Literal["NORMAL","CAUTION","REDUCED","DEFENSIVE","FLATTEN","HALT"]
DataHealth     = Literal["OK","WARN","FAIL","HALT"]
Verdict        = Literal["ALLOW","REDUCE","REFUSE"]

@dataclass(frozen=True) class Instrument:      # AX-03 §1.1
    instrument_id: str; index_symbol: str; contract_multiplier: Decimal
    tick: Decimal; step: Decimal; min_notional: Decimal
    status: str; inverse: bool; factors_hash: str

@dataclass(frozen=True) class Bar:             # AX-03 §1.2
    instrument_id: str; interval: str; open_time: int; close_time: int
    o: float; h: float; l: float; c: float; v: float; qv: float
    trades: int; taker_buy_qv: float; is_final: bool; revision: int
    source: Literal["WS","REST"]; first_ingest_ts: int; last_update_ts: int

@dataclass(frozen=True) class Snapshot:        # AX-03 §1.4
    snapshot_id: str; as_of: int; instruments: tuple[str, ...]
    manifest: tuple[tuple[str, str], ...]      # (partition, digest)
    param_set_hash: str; code_commit: str; model_hashes: tuple[str, ...]; profile_hash: str

@dataclass(frozen=True) class Forecast
@dataclass(frozen=True) class Target
@dataclass(frozen=True) class OrderIntent
@dataclass(frozen=True) class VerdictResult     # from the risk kernel
@dataclass(frozen=True) class Refusal
```

Field sets are exactly those of AX-03; the dataclasses add no fields without an ADR.

---

## 4. Module interfaces (`AX-13:§4`)

### 4.1 `vap` (`AX-13:§4.1`)

```python
class RateGovernor:
    def acquire(self, req: RequestSpec, deadline_ms: int | None = None) -> Token | None: ...
    def observe(self, headers: Mapping[str,str]) -> None: ...        # X-Api-Limit-* feedback

@dataclass(frozen=True) class RequestSpec:
    method: Literal["GET","POST","PUT","DELETE"]; path: str
    params: tuple[tuple[str,str], ...]        # ORDERED – signing law AX-02 §2.2-R1
    body: tuple[tuple[str,str], ...] | None = None
    json_body: bytes | None = None            # v2 only; byte-identical to what is sent
    signed: bool; priority: Literal["P0","P1","P2","P3"]; weight: int

@dataclass(frozen=True) class Outcome:
    kind: Literal["KNOWN_SUCCESS","KNOWN_FAILURE","UNKNOWN"]
    http_status: int | None; code: int | None; msg: str | None
    raw: bytes; received_ts: int; latency_ms: int

class VenueClient:
    def execute(self, req: RequestSpec, timeout_ms: int) -> Outcome: ...
    def classify(self, outcome: Outcome, route_class: RouteClass) -> Outcome: ...   # AX-02 §9.1

class ClockSync:
    def estimate(self) -> int            # server_offset_ms, min-RTT filter, AX-02 §2.3
    @property def offset_ms(self) -> int
    @property def rtt_p95_ms(self) -> int

class ConformanceHarness:              # AX-02 §10
    def run(self, probes: Sequence[str], env: Env) -> VenueProfile: ...
```

`VenueClient.execute` performs exactly one attempt and **never retries**; retries are a policy of the
caller (`exp`), which knows the intent's semantics. This is deliberate: a generic retry inside the
transport is how duplicate orders are born.

### 4.2 `mdp` (`AX-13:§4.2`)

```python
class StoreL0:
    def append(self, stream: str, payload: bytes, meta: RawMeta) -> None: ...
    def read_range(self, stream: str, t0: int, t1: int) -> Iterator[RawRecord]: ...

class StoreL1:
    def upsert_bar(self, bar: Bar) -> None: ...
    def upsert_trade(self, trade: Trade) -> None: ...
    def upsert_quote(self, q: Quote) -> None: ...
    def upsert_book(self, snap: BookSnapshot) -> None: ...
    def upsert_funding(self, obs: FundingRateObs) -> None: ...
    def upsert_oi(self, obs: OpenInterestObs) -> None: ...
    def upsert_position_snapshot(self, p: Position) -> None: ...
    def cursor(self, as_of: int) -> "TapeCursor": ...

class Gatekeeper:
    def check(self, rec: RawRecord) -> GateResult: ...       # AX-04 §3, returns action + flags

class UniverseBuilder:
    def build(self, day: str, day_start_ts: int | None = None) -> UniverseRecord: ...

class SnapshotBuilder:
    def build(self, as_of: int, universe: UniverseRecord) -> Snapshot: ...

class HealthMonitor:
    def state(self, instrument_id: str) -> DataHealth: ...
```

### 4.3 `sfp` (`AX-13:§4.3`)

```python
class TapeCursor:                       # the ONLY data access allowed to features
    as_of: int
    def bar(self, instrument_id: str, interval: str, k_back: int = 0) -> Bar | None: ...
    def bars(self, instrument_id: str, interval: str, n: int) -> Sequence[Bar]: ...
    def quotes(self, instrument_id: str, n: int) -> Sequence[Quote]: ...
    def trades(self, instrument_id: str, n: int) -> Sequence[Trade]: ...
    def book(self, instrument_id: str) -> BookState | None: ...
    def mark(self, instrument_id: str) -> MarkPriceObs | None: ...
    def index(self, instrument_id: str) -> IndexPriceObs | None: ...
    def funding(self, instrument_id: str) -> FundingRateObs | None: ...
    def oi_series(self, instrument_id: str, n: int) -> Sequence[OpenInterestObs]: ...

class FeatureRegistry:
    def get(self, feature_id: str, version: str) -> FeatureSpec: ...
    def compute(self, feature_id: str, version: str, cursor: TapeCursor,
                instrument_id: str, params: ParamSet) -> float | NotAvailable: ...
```

`NotAvailable` is a distinct sentinel type (never `None`, never `NaN`) so that a missing value cannot be
confused with a value (`T-FEAT-003`).

### 4.4 `fcp` (`AX-13:§4.4`)

```python
class Forecaster(Protocol):
    model_id: str; version: str
    def fit(self, ds: Dataset, params: ParamSet) -> "FittedModel": ...
    def predict(self, fm: "FittedModel", cursor: TapeCursor, instrument_id: str,
                horizon_bars: int) -> RawScore: ...

class ForecastPipeline:
    def run(self, snapshot: Snapshot, cursor: TapeCursor, universe: UniverseRecord,
            params: ParamSet) -> list[Forecast]: ...

class Calibrator:
    def transform_score(self, raw: float, artifact: "ModelArtifact") -> tuple[float, float]: ...  # (mu, sigma)

class RegimeModel:
    def filtered_probs(self, cursor: TapeCursor) -> tuple[float, ...]: ...
    def multipliers(self, probs: tuple[float, ...], params: ParamSet) -> RegimeMultipliers: ...
```

### 4.5 `pfp` (`AX-13:§4.5`)

```python
class RiskModel:
    def covariance(self, cursor: TapeCursor, instruments: Sequence[str]) -> np.ndarray: ...   # AX-07 §5
    def clusters(self, corr: np.ndarray, instruments: Sequence[str], params: ParamSet) -> list[list[int]]: ...

class PortfolioOptimizer:
    def solve(self, mu: np.ndarray, sigma: np.ndarray, w_prev: np.ndarray,
              caps: Caps, costs: CostVector, params: ParamSet) -> OptimalWeights: ...

class Sizer:
    def size(self, target: ProposedTarget, ctx: RiskContext, params: ParamSet) -> SizedTarget: ...

class Stops:
    def initial(self, instrument_id: str, entry_ref: float, horizon_bars: int,
                cursor: TapeCursor, params: ParamSet) -> StopPlan: ...
    def revise(self, pos: PositionView, cursor: TapeCursor, params: ParamSet) -> StopPlan | None: ...
```

### 4.6 `rg` (`AX-13:§4.6`)

```python
@dataclass(frozen=True) class Candidate:      # an order about to be sent
    instrument_id: str; side: SideSemantic; qty: Decimal; limit_price: Decimal | None
    purpose: IntentPurpose; intent: OrderIntent; target_ref: str; snapshot_id: str

class RiskKernel:
    def evaluate(self, c: Candidate, ctx: RiskContext) -> VerdictResult: ...   # AX-09 §2, ordered checks

class Governor:
    def step(self, metrics: GovernorMetrics) -> GovState: ...                  # event-driven, idempotent
    def multiplier(self) -> float: ...
    def state(self) -> GovState: ...
    def rearm(self, reason: str, actor: str) -> None: ...                      # operator-only, journaled
```

### 4.7 `exp` (`AX-13:§4.7`)

```python
class Planner:
    def plan(self, target: SizedTarget, cursor: TapeCursor, params: ParamSet) -> OrderPlan: ...

class OrderManager:
    def submit(self, intent: OrderIntent) -> IntentState: ...          # writes journal first (INV-3)
    def resolve(self, intent_id: str) -> IntentState: ...              # AX-08 §5.2 ladder
    def cancel(self, intent_id: str) -> IntentState: ...
    def state(self, intent_id: str) -> IntentState: ...

class ProtectionManager:
    def ensure(self, instrument_id: str) -> ProtectionState: ...
    def revise(self, instrument_id: str, stop: StopPlan) -> ProtectionState: ...

class Reconciler:
    def full(self, reason: str) -> ReconciliationResult: ...

class CostLedger:
    def record_fill(self, fill: Fill, decision_mid: float, arrival_mid: float) -> None: ...
    def cost(self, instrument_id: str, notional: float) -> CostEstimate: ...   # upper estimator AX-08 §3.3-R1
```

### 4.8 `lnp` (`AX-13:§4.8`)

```python
class DatasetBuilder:
    def build(self, spec: DatasetSpec) -> Dataset: ...            # survivorship-free, versioned
class ReplayEngine:
    def run(self, tape: TapeRef, versions: VersionStamp) -> ReplayResult: ...
class SimulatedVenue:
    def submit_order(self, req: SubmitRequest) -> SubmitResult: ...
    def cancel_order(self, req: CancelRequest) -> CancelResult: ...
    def query_order_state(self, req: QueryOrder) -> OrderView: ...
    def query_open_positions(self) -> tuple[PositionView, ...]: ...
    def query_account_margin_health(self) -> MarginHealth: ...
class Stats:                        # DSR, PBO, SPA, MinTRL, bootstrap CIs (AX-10 §3.4)
    def dsr(self, returns: Sequence[float], trials: int, **kw) -> float: ...
class PromotionGate:
    def evaluate(self, rung_from: str, rung_to: str, evidence: EvidenceBundle) -> GateRecord: ...
class DriftMonitor:
    def daily(self, window_days: int) -> DriftReport: ...
```

### 4.9 `cop` (`AX-13:§4.9`)

```python
class Journal:
    def append(self, event_type: str, payload: Mapping[str, Any]) -> JournalEntry: ...  # chain + fsync
    def verify_chain(self, limit: int | None = None) -> ChainStatus: ...
    def range(self, t0: int, t1: int) -> Iterator[JournalEntry]: ...
class ConfigLoader:
    def load(self, path: str) -> ParamSet: ...      # validates provenance classes (INV-6)
class Notifier:
    def send(self, severity: str, event_type: str, payload: Mapping[str, Any]) -> None: ...
class OperatorCLI: ...                              # AX-12 §7.2 command surface only
```

---

## 5. Journal event catalogue (`AX-13:§5`)

| `event_type` | Payload (required keys) |
|---|---|
| `EV-BOOT` | `env, code_commit, param_set_hash, profile_hash, schema_version` |
| `EV-READY` | `checks[] (id, status, value, threshold_ref)` |
| `EV-SNAPSHOT` | `snapshot_id, as_of, manifest_digest` |
| `EV-DECISION` | `decision_id, snapshot_id, targets[], refusals[], gov_state` |
| `EV-REFUSAL` | `instrument_id, stage, check_id, reason_code, detail` |
| `EV-INTENT` | `intent_id, idempotency_key, purpose, params_digest` |
| `EV-VENUE-REQUEST` | `intent_id, request_digest, sent_ts, priority, weight` |
| `EV-VENUE-RESPONSE` | `intent_id, outcome_kind, http_status, code, latency_ms, raw_hash` |
| `EV-ORDER-STATE` | `intent_id, order_id, client_order_id, status, executed_qty, avg_price` |
| `EV-FILL` | `fill_id, intent_id, order_id, qty, price, fee, is_maker, event_ts` |
| `EV-PROTECTION` | `instrument_id, state, stop_price, trigger_by, order_id, unprotected_ms` |
| `EV-RECONCILE` | `reason, result, divergences[] (class, detail)` |
| `EV-CORRECTION` | `object, adopted_value, evidence_refs[], cause` |
| `EV-GOV-STATE` | `from, to, trigger_ids[], multipliers{}, dwell_until` |
| `EV-KILL` | `kill_id, scope, actions[], operator|null` |
| `EV-INCIDENT` | `incident_id, severity, trigger_codes[], evidence_refs[]` |
| `EV-PARAM-CHANGE` | `param_id, old, new, class, actor, reason, calibration_ref?` |
| `EV-MODEL-PROMOTE` / `EV-MODEL-DEMOTE` | `model_id, version, rung_from, rung_to, gate_record_id` |
| `EV-FEAT-DEMOTE` | `feature_id, version, reason, metric_values` |
| `EV-DATA-HEALTH` | `instrument_id, from, to, gate_id, value, threshold_ref` |
| `EV-REPAIR` | `scope, method, rows, digests, started_ts, finished_ts` |
| `EV-VENUE-DRIFT` | `field, old_hash, new_hash, affected_probes[]` |
| `EV-CLOCK` | `offset_ms, rtt_p95_ms, samples` |
| `EV-OPERATOR` | `command, args_digest, actor, confirmed_by?, result` |

Every payload is canonical-JSON-hashed into the chain (AX-03 §5.3).

---

## 6. Configuration schema (`AX-13:§6`)

**The normative structure is the pair `contracts/config.default.yaml` + `contracts/registry.json`,
generated together from one table by `contracts/build_registry.py`** (whose `--check` mode fails the
build on any drift). Every key maps to exactly one AX-15 parameter id with a provenance class. The
loader rejects: unknown keys, keys absent from the registry, `[C]` parameters without a calibration
reference, values outside their registry range, `[O]` parameters supplied without an owner
`EV-PARAM-CHANGE` record, and any `[V]` value supplied as a literal (`T-CFG-001`, `T-PROV-002`).
The section list below is illustrative of the *shape* (the generated file is the authority and adds
`admission`, `regime`, `learning`, `security` and `tests` sections); every leaf in it carries a trailing
comment with its parameter id, class, unit and calibration/owner reference:

```yaml
meta:        { env: LIVE, profile: default }         # env ∈ Env
venue:       { base_url: "https://api.toobit.com", ws_url: "wss://stream.toobit.com/quote/ws/v1",
               recv_window_ms: null, offset_max_ms: null, safety_fraction: null }
universe:    { max_instruments: null, min_bars_complete: null, min_listing_days: null,
               min_qy_volume: null, max_spread_bps: null, participation_cap: null, cluster_max: null }
data:        { hot_depth_snapshot_s: null, warm_agg_s: null, retention_days_hot: null,
               retention_days_warm: null, bar_close_grace_s: null, staleness_k: null }
features:    { enabled_t1: [...], enabled_t2: [...], scaling_window: null, clip_sigma: null }
forecast:    { horizons: [1,4,16], ridge_lambda: null, lcb_z: null, p_min: null, m_eff_floor: null }
risk:        { risk_fraction: null, d_max: null, n_bets: null, k_d: null, daily_loss_cap: null,
               sigma_target: null, g_max: null, gamma: null, kelly_fraction: null,
               gross_cap: null, net_cap: null, per_instrument_cap: null, cluster_cap: null,
               beta_cap: null, margin_util_cap: null, k_safe: null, c_sigma: null, c_cost: null,
               q_tail: null, kelly_lcb_z: null }
execution:   { k_cross: null, max_attempts: null, slice_threshold: null, slice_spacing_s: null,
               deadline_min: null, protection_bound_s: null, max_positions_per_min: null,
               taker_only: true, allow_post_only: false }
cost:        { upper_quantile: null, uncertainty_m: null, refit_days: null, funding_defer_ratio: null }
governor:    { caution_q: null, reduced_q: null, defensive_q: null, dwell_h_perf: null,
               dwell_h_health: null, rearm_requires_operator: true }
ops:         { tick_s: null, reconcile_s: null, backup_interval_min: null, log_level: INFO,
               notify: { channel: "telegram", chat_id_ref: "secret:telegram_chat" } }
owner_inputs: { OI-RISK-01: null, OI-RISK-02: null, ..., OI-CAP-01: null }
```

`null` means "must be supplied by the registry default or by the owner input"; the loader resolves it
and records the resolved value's source. **No key may be absent** (`T-CFG-001`).

---

## 7. Error taxonomy in code (`AX-13:§7`)

```
AxiomError
├── ConfigError            (bad/missing/invalid configuration, provenance violation)
├── VenueError             (transport/venue)  → subclassified by Outcome.kind
│   ├── VenueRejected      (definitive business rejection; carries code/msg)
│   └── VenueUnknown       (UNKNOWN outcome; must be resolved, never retried blindly)
├── DataError              (gate/quarantine/staleness; carries gate id)
├── RiskError              (kernel refusal; carries check id)  — not an exception in the normal flow
├── ExecutionError         (order FSM violation; always an incident)
├── IntegrityError         (journal chain, hashing, schema mismatch)  — SEV-1
└── InternalError          (a bug; always an incident with an evidence bundle)
```

`RiskError` is returned as a value (`VerdictResult`), not raised: refusals are normal operation
(AX-09 §6.3).

---

## 8. Interface versioning (`AX-13:§8`)

Interfaces carry a `contract_version`; additive changes bump the minor version, and any change to a
public signature, event payload, or the config schema requires an ADR + a migration note + updated
tests. The runtime records all contract versions in `EV-BOOT` so a journal can always be interpreted.
