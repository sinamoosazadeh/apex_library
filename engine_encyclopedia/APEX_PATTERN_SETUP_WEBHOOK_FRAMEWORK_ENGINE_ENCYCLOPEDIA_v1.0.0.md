# APEX — Pattern, Setup, Webhook & Framework Engine Encyclopedia & Institutional Engineering Specification v1.0.0

**Document class:** Research + quantitative engineering master specification  
**Date:** 2026-08-13  
**Scope:** APEX / Crypto Futures / Toobit / L1-first

**Engine mission:** Formal pattern grammar, setup composition, event transport and extensible engine framework.

## Table of Contents

1. Document Control & Purpose
2. Table of Contents
3. Architecture Contract
4. Domain Ontology
5. Input Contract
6. Core Algorithms
7. State Machine & Lifecycle
8. Multi-Timeframe Architecture
9. Feature Registry
10. Event / Zone Model
11. Probability, Confidence & Calibration
12. Failure Modes & Edge Cases
13. No-Lookahead / Repainting Controls
14. Research & Statistical Validation
15. Synthetic & Historical Test Design
16. Performance & Resource Engineering
17. Observability & Monitoring
18. Explainability & Provenance
19. Configuration & Parameter Governance
20. API / Python Interfaces
21. Storage & Serialization
22. Dependency Contract with Other APEX Engines
23. Acceptance Criteria & Release Gate
24. Maintenance, Drift & Evolution
25. Limitations / Epistemic Boundaries
26. Reference Implementations / Pseudocode
27. Reference & Source Registry

---

## 1. Document Control & Purpose

# APEX ENGINE ENCYCLOPEDIA — COMMON ENGINE CONTRACT

## Purpose
APEX analytical engines are deterministic, point-in-time-safe research and intelligence components. They transform canonical market observations into explicit measurements, evidence, inferred states, events, zones, scenarios, and confidence-bearing outputs. They do not place orders and may not bypass independent risk controls.

## APEX scope
- Exchange: Toobit only.
- Market: Crypto futures only.
- Baseline data: L1 OHLCV + Open Interest.
- Timeframes: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 12h, 1d, 3d, 1w, 1mo.
- Runtime target: Python / Termux / resource-aware execution.
- Determinism and no-future-leak are non-negotiable.

## Data availability contract
A feature at time t can use only information that was published and available by t. Closed-bar semantics must be explicit. Higher-timeframe candles may be used only after their data is actually available. Every object carries `as_of`, `source_timestamp`, `data_revision`, `engine_version`, and `config_version`.

## Canonical input contract
`MarketSnapshot` contains symbol, exchange, contract, timeframe, timestamp, OHLCV, OI, session metadata, quality flags, source revisions, and approved upstream feature references.

## Canonical output contract
`EngineOutput` contains engine name/version, run id, as-of timestamp, symbol/timeframe, features, evidence items, events, states, zones, scores, calibrated probabilities where applicable, confidence, invalidation, contradictions, quality flags, provenance, and explanation graph.

## Universal state machine
`CANDIDATE -> ACTIVE -> TESTED -> CONFIRMED | WEAKENED | INVALIDATED -> ARCHIVED`.

## Feature taxonomy
1. Atomic measurements.
2. Relational measurements.
3. Structural features.
4. Temporal features.
5. Contextual features.
6. Probabilistic/calibrated features.
7. Data-quality features.
8. Explanatory/provenance features.

## Universal anti-error controls
- No look-ahead.
- No repainting.
- No hidden future normalization.
- No silent imputation.
- No double counting of highly correlated evidence.
- No retrospective pattern relabeling in the live state.
- No mixing of incompatible definitions without a versioned definition registry.
- No production promotion from in-sample performance alone.

## Quant research validation
Research must preserve separate development, validation, and true out-of-sample periods. For overlapping labels and serial dependence, use leakage-aware validation such as purging and embargo. Record all tried configurations and use explicit overfitting diagnostics; the probability of backtest overfitting is itself a research concern. [Bailey et al., 2015; López de Prado, 2018].

## Governance
Every production release requires semantic versioning, change log, regression report, schema compatibility check, rollback artifact, and reproducibility manifest.

## Recommended Python boundaries
```text
apex_engine/
  domain/
  schemas/
  config/
  ingestion/
  features/
  detectors/
  state/
  inference/
  calibration/
  persistence/
  explainability/
  validation/
  monitoring/
  api/
  tests/
```


### Engine-specific inputs
All approved analytical engine outputs, configuration, event schema registry.

### Engine-specific outputs
Pattern objects, setup candidates, scenario objects, event envelopes, webhook payloads, plugin metadata and explanation graphs.

## 2. Table of Contents

1. Document Control & Purpose
2. Table of Contents
3. Architecture Contract
4. Domain Ontology
5. Input Contract
6. Core Algorithms
7. State Machine & Lifecycle
8. Multi-Timeframe Architecture
9. Feature Registry
10. Event / Zone Model
11. Probability, Confidence & Calibration
12. Failure Modes & Edge Cases
13. No-Lookahead / Repainting Controls
14. Research & Statistical Validation
15. Synthetic & Historical Test Design
16. Performance & Resource Engineering
17. Observability & Monitoring
18. Explainability & Provenance
19. Configuration & Parameter Governance
20. API / Python Interfaces
21. Storage & Serialization
22. Dependency Contract with Other APEX Engines
23. Acceptance Criteria & Release Gate
24. Maintenance, Drift & Evolution
25. Limitations / Epistemic Boundaries
26. Reference Implementations / Pseudocode
27. Reference & Source Registry

## 3. Architecture Contract

The engine is a pure analytical boundary. It can consume approved upstream data, emit immutable outputs, and maintain engine-local state, but it cannot mutate upstream truth, place an order, bypass the Risk Veto, or call execution directly.

## 4. Domain Ontology

The ontology must distinguish observation, measurement, evidence, event, state, hypothesis, confidence and invalidation. Every domain term that has multiple competing meanings receives a definition ID and semantic version. The engine never silently merges terms from Wyckoff, RTM, ICT, SMC or generic price action.

## 5. Input Contract

**Required:** All approved analytical engine outputs, configuration, event schema registry.

**Input validation:** schema validation, monotonic timestamps, duplicate detection, missing-bar classification, nonnegative volume, OHLC consistency, OI sanity, exchange/contract identity, and source revision checks.

**Availability rule:** all values are point-in-time safe. Incomplete higher-timeframe bars are never treated as closed observations.

## 6. Core Algorithms

All algorithmic modules must expose deterministic inputs, parameters, intermediate evidence, and outputs. Research mode and production mode share the same semantic definitions; only approved execution optimizations may differ. The implementation should support both vectorized historical evaluation and incremental live updates.

### Engine-specific algorithmic specification


### 5. Pattern grammar
Primitive predicates become composite graphs. A pattern definition contains required evidence, optional evidence, exclusion rules, temporal order, thresholds, invalidation and expiry.

### 6. Setup lifecycle
`CONTEXTUALIZED -> ELIGIBLE -> TRIGGERED -> CONFIRMING -> QUALIFIED | REJECTED -> EXPIRED`.

### 7. Evidence lineage
Every setup component references its source engine, source object ID, timestamp and definition version. Duplicate evidence families are discounted or explicitly flagged.

### 8. Webhook contract
At minimum: `event_id`, `schema_version`, `event_type`, `created_at`, `as_of`, `symbol`, `timeframe`, `engine_versions`, `evidence_ids`, `state`, `confidence`, `quality_flags`, `idempotency_key`, signature metadata.

### 9. Delivery architecture
At-least-once delivery, idempotent consumer design, retries, dead-letter path, replay support, rate limits, signed payloads, secret rotation and complete audit logs.

### 10. Plugin framework
Engine registry, dependency declarations, feature registry, configuration registry, health checks, capability discovery, lifecycle hooks, graceful degradation and schema compatibility.

### 11. Safety
Webhook events cannot directly execute trades. Downstream risk/portfolio/execution components remain independent.


## 7. State Machine & Lifecycle

Persistent objects require unique IDs and immutable creation facts. State transitions append events rather than rewriting history. Expiry and invalidation rules are explicit. A state may be uncertain and may revert only through a formally defined transition, never by silent relabeling.

## 8. Multi-Timeframe Architecture

Every timeframe is an autonomous observation domain. Cross-timeframe relationships use explicit availability timestamps, parent-child links, alignment matrices and conflict states. A higher-timeframe event can become a context constraint without overwriting lower-timeframe measurements.

## 9. Feature Registry

Each feature has: `feature_id`, definition, mathematical formula or algorithm, units, normalization, lookback, availability delay, upstream dependencies, missing-data behavior, version, and validation status. Features are categorized as atomic, relational, structural, temporal, contextual, probabilistic, quality, or explanatory.

## 10. Event / Zone Model

Events are instantaneous or interval objects with creation, confirmation, invalidation and expiry. Zones are spatial-temporal objects with boundaries, age, freshness, tests, mitigation, reactions and invalidation. Event and zone definitions must be serializable and replayable.

## 11. Probability, Confidence & Calibration

A score is not automatically a probability. If the output is called probability, empirical calibration is required. Track calibration by symbol, timeframe, regime and event quality when sample size permits. Preserve raw evidence and calibrated estimate separately.

## 12. Failure Modes & Edge Cases

Mandatory cases include flat markets, extreme volatility, one-bar shocks, equal highs/lows, sparse volume, OI discontinuity, timestamp anomalies, exchange maintenance, partial candles, data revision, nested patterns, conflicting MTF states, and parameter boundary instability.

## 13. No-Lookahead / Repainting Controls

Every detector requires a replay test proving that outputs at t are unchanged by bars after t, except for explicitly documented state updates after t. Swing confirmation latency must be recorded. Retrospective schematic labels cannot be used as live-state evidence.

## 14. Research & Statistical Validation

Use walk-forward and out-of-sample validation. When labels overlap or observations are serially dependent, use purging/embargo or another leakage-aware approach. Track the number of configurations tried and maintain research lineage. Backtest overfitting is a first-class failure condition.

## 15. Synthetic & Historical Test Design

Create synthetic fixtures for idealized trends, ranges, shocks, gaps/imbalance, false breakouts, nested structures, and pathological data. Historical replay must compare exact event timing, state transitions, output hashes, and performance metrics.

## 16. Performance & Resource Engineering

Historical mode may use vectorization and batch processing; live mode should update incrementally. Caches are bounded. Repeated MTF calculations are memoized. Memory and CPU use are observable. The Termux target requires degradation strategies when resources are constrained.

## 17. Observability & Monitoring

Monitor data freshness, processing latency, error rate, state/event frequency, feature distribution, confidence calibration, output completeness, dependency health, resource consumption, and drift. Material anomalies generate structured diagnostic events.

## 18. Explainability & Provenance

Each output carries an explanation graph linking it to source bars, features, upstream events, configuration, thresholds, contradictory evidence, and state transitions. A historical output must be reconstructible from its provenance manifest.

## 19. Configuration & Parameter Governance

All thresholds and definitions live in versioned configuration. Research optimization writes candidates into a repository; production uses only approved versions. Symbol/timeframe/regime overrides are explicit. Parameter defaults are conservative and validated.

## 20. API / Python Interfaces

Use typed models and narrow interfaces. Recommended classes: `EngineConfig`, `MarketSnapshot`, `FeatureVector`, `EvidenceItem`, `Event`, `Zone`, `StateSnapshot`, `Confidence`, `EngineOutput`, `ProvenanceRecord`. Public methods should include `validate_input`, `compute_features`, `detect`, `update_state`, `publish`, and `explain` where relevant.

## 21. Storage & Serialization

Use append-only event persistence for state changes. Store compact feature snapshots, event objects, zone objects, and provenance manifests. Every serialized object includes schema version and engine version. Historical values are immutable.

## 22. Dependency Contract with Other APEX Engines

Declare hard and soft dependencies. Hard dependency failure blocks publication or marks output degraded. Soft dependency failure reduces confidence. The dependency graph must be acyclic.

## 23. Acceptance Criteria & Release Gate

Production readiness requires schema compliance, deterministic replay, no known future leak, unit/property/adversarial tests, historical replay consistency, documented limitations, resource budget compliance, monitoring hooks, and a signed research validation artifact.

## 24. Maintenance, Drift & Evolution

Track concept drift, data drift, performance drift, event-frequency drift and calibration drift. New versions run in shadow mode before promotion. Historical comparisons are mandatory for material changes.

## 25. Limitations / Epistemic Boundaries

The engine measures and infers from available data. It cannot directly observe hidden orders, trader identity, intent, manipulation, or true market-maker inventory from L1 OHLCV/OI alone. Any such concept is a latent hypothesis.

## 26. Reference Implementations / Pseudocode

```python
class Engine:
    def validate_input(self, snapshot): ...
    def compute_features(self, snapshot, upstream): ...
    def detect(self, features): ...
    def update_state(self, events, prior_state): ...
    def publish(self, state, provenance): ...
    def explain(self, output): ...
```

Recommended invariant: `output(t)` must be identical when replayed with the same point-in-time snapshot, dependency versions and configuration.

## 30. Reference and Source Registry

### Wyckoff
- Hank Pruden, *The Three Skills of Top Trading: Behavioral Systems Building, Pattern Recognition, and Mental State Management*, Wiley. The book explicitly covers systems building, behavioral finance, charting, the Wyckoff method, and trade anatomy. https://onlinelibrary.wiley.com/doi/book/10.1002/9781119196822
- Hank Pruden, “The Wyckoff Method of Technical Analysis and Speculation,” Wiley chapter. It describes the method through price/volume, supply/demand, and cause/effect. https://onlinelibrary.wiley.com/doi/10.1002/9781119196822.ch6
- Hank Pruden, “The Basic Elements of Charting for the Wyckoff Method,” Wiley. https://onlinelibrary.wiley.com/doi/abs/10.1002/9781119196822.ch5
- David H. Weis, *Trades About to Happen: A Modern Adaptation of the Wyckoff Method*, Wiley. https://onlinelibrary.wiley.com/doi/book/10.1002/9781118656389
- Wyckoff Analytics, Hank Pruden archive and Wyckoff materials. https://www.wyckoffanalytics.com/hank-pruden/
- Hank Pruden / Max von Lichtenstein, *Wyckoff Schematics: Visual Templates for Market Timing Decisions*. https://www.wyckoffanalytics.com/wp-content/uploads/2019/09/WyckoffSchematics-VisualTemplatesForMarketTimingDecisions.pdf

### Quant research / validation
- Bailey, Borwein, López de Prado, Zhu, “The Probability of Backtest Overfitting.” SSRN / Journal of Computational Finance. https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
- Marcos López de Prado, *Advances in Financial Machine Learning*, Wiley. Includes finance-specific cross-validation, purging and embargo, and feature-importance considerations.

### Market microstructure / quantitative foundations
- Joel Hasbrouck, *Empirical Market Microstructure*, Oxford University Press.
- Maureen O'Hara, *Market Microstructure Theory*, Wiley-Blackwell.
- Charles-Albert Lehalle and Jean-Philippe Bouchaud, work on market microstructure, optimal execution, and price formation.

### Technical analysis / charting
- Edwards, Magee, Bassetti, *Technical Analysis of Stock Trends*.
- John J. Murphy, *Technical Analysis of the Financial Markets*.
- Welles Wilder, *New Concepts in Technical Trading Systems*.

### ICT / SMC / price-action terminology
Public ICT/SMC terminology is used as a secondary vocabulary source only. APEX does not treat community terminology as empirical fact. Definitions are operationalized and independently tested. Public terminology cross-checks include contemporary SMC glossaries, while proprietary claims are not assumed to be authoritative.

### RTM
The RTM family of terminology is treated as a separate ontology. Public RTM materials are used to identify vocabulary and source claims, while operational definitions are versioned and independently testable. Proprietary/community interpretations must not be presented as scientifically established facts.


## 27. Detailed Quantitative Specification

### 27.1 Parameter classes
Parameters must be classified into:
- semantic parameters: definition choices;
- detection parameters: thresholds/windows;
- normalization parameters;
- lifecycle parameters;
- confidence parameters;
- calibration parameters;
- performance parameters.

Semantic parameters may alter what the event means and therefore require a new definition version, not merely a numeric configuration change.

### 27.2 Parameter sensitivity
For critical thresholds, run local perturbation tests around the selected value. A concept that exists only in a narrow parameter island is considered unstable. Report sensitivity surfaces, not only the selected point.

### 27.3 Invariance testing
Where theoretically appropriate, test invariance to:
- price scale;
- volatility scale;
- bar aggregation;
- small timestamp shifts;
- symbol nominal price differences;
- equivalent normalization windows.

### 27.4 Information decomposition
Every output should expose a decomposition:
`observation -> measurement -> transformed feature -> evidence -> inference -> confidence`.
This is necessary to determine where a failure originated.

### 27.5 Evidence independence
The engine should tag evidence families so a downstream combiner can distinguish, for example, four structure-derived conditions from four genuinely different information sources. Correlated evidence must not be naively added.

### 27.6 Missing-data semantics
Missing means unknown. The engine must distinguish:
- unavailable;
- invalid;
- not applicable;
- zero;
- stale;
- imputed under an explicitly approved policy.

### 27.7 Numerical stability
Use robust division, explicit epsilon policy, bounded transforms, NaN propagation rules, integer-safe timestamps, and deterministic floating-point handling where possible.

### 27.8 Reproducibility bundle
For each research artifact store:
- code commit;
- config hash;
- schema version;
- feature manifest;
- data revision;
- experiment ID;
- dependency versions;
- random seeds;
- output hash.

## 28. Test Matrix

| Test class | Minimum objective |
|---|---|
| Unit | Each critical rule and formula |
| Property-based | Invariants under generated inputs |
| Metamorphic | Expected output relation under controlled transformations |
| Replay | Identical historical reconstruction |
| Anti-lookahead | Future bars cannot alter past output |
| Boundary | Threshold edges, equal highs/lows, zero denominators |
| Missing data | Explicit degradation, no silent corruption |
| Adversarial | Extreme shocks, sparse data, malformed candles |
| Contract | Upstream/downstream schema compatibility |
| Resource | CPU/RAM budget and graceful degradation |
| Calibration | Probability reliability and drift |
| Regression | Version-to-version output comparison |

## 29. Research Label Discipline

Labels are definitions, not truths. Every label used to train or evaluate an engine must specify its horizon, outcome rule, event overlap, stopping conditions, and whether the label was knowable at the prediction timestamp. Label generation is versioned independently from feature generation.

## 30. Release Gate

A candidate version must answer:
1. What changed?
2. Which definitions changed?
3. Which historical outputs changed?
4. Did detection latency change?
5. Did calibration change?
6. Did false-positive rates change?
7. Did resource usage change?
8. Which downstream engines are affected?
9. Can the previous version be reproduced and restored?
10. What evidence supports promotion?

## 31. Framework-Specific Deep Blueprint

### Pattern DSL
A future implementation can use a declarative pattern DSL:
```yaml
pattern_id: example
requirements:
  - event: structural_break
  - relation: liquidity_sweep_before_break
  - relation: zone_return_after_break
invalidations:
  - close_beyond_origin
expiry: 40bars
```
The DSL compiler must output a deterministic predicate graph.

### Event bus guarantees
At-least-once delivery, idempotency, replayability, signed payloads, dead-letter handling and auditability are mandatory.
