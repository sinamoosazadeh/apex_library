# AX-01 — Charter, Law and Architecture

**Status:** Normative. Clauses in this document are binding on every other AX document and on the
implementation.
**Upstream:** AX-00 (constraints C1–C8, axioms A1–A10, provenance law).
**Downstream:** all AX documents; the traceability matrix (AX-17) cites clause IDs from this file.

Clause IDs in this document are of the form `AX-01:§n.m` and are referenced verbatim by tests
(AX-14) and by the traceability matrix (AX-17). An implementation may not weaken a clause; it may only
satisfy it more strongly.

---

## 1. Identity of the system

**AXIOM** is a single-venue, single-operator systematic futures trading system for Toobit USDT-M
perpetuals. It ingests the venue's public market data, maintains its own point-in-time record of that
data, computes calibrated forecasts of *net* (after-cost) returns, converts forecasts into target
positions under hard risk limits, executes those targets through a fail-closed execution state
machine, and continuously measures whether its own forecasts and executions are behaving as modelled —
demoting or shutting itself down when they are not.

### 1.1 One-sentence definition

> AXIOM is an *evidence machine* attached to an exchange account: it converts market data into
> calibrated, cost-adjusted forecasts; forecasts into bounded positions; positions into reconcilable
> orders; and all of the above into auditable evidence that decides how much, if any, capital it may
> deploy.

### 1.2 What AXIOM is not (non-goals — binding)

| Non-goal | Reason |
|---|---|
| High-frequency trading, market making, queue-position optimisation, latency arbitrage | A6: the execution path (public REST + consumer network) cannot compete on latency; attempting it converts a data problem into an infrastructure arms race AXIOM cannot win. |
| Multi-venue routing, cross-exchange arbitrage, spot–perp basis trading on other venues | C1: single venue. Cross-venue data may be used **only** as an optional research input if the owner enables it (AX-04 §9), never as a trading leg. |
| Spot, options, structured products, DeFi, copy-trading | C1: scope lock. Adding instruments expands the test matrix without adding evidence. |
| Autonomous capital allocation, autonomous parameter/risk changes, "self-learning live" behaviour | A9 + INV-7: without frozen parameters, no result is attributable; changes to risk or model behaviour require the promotion pipeline (AX-10 §4). |
| A user-facing conversational product or signal-distribution service | C7: AXIOM serves exactly one account and one operator. |
| Prediction of prices as an end in itself | A1: uncalibrated and un-costed prediction is not tradeable information. |
| Guaranteed profitability, or any claim of expected return level | C3 is about *quality of process and evidence*, not about promised outcomes. |

---

## 2. Scope (`AX-01:§2`)

**§2.1 Venue.** Toobit (`https://api.toobit.com`, streams `wss://stream.toobit.com`), USDT-M
perpetual futures (`category` = default; USDC-M is out of scope). One account (the owner's), one
sub-account set at most. `[V-DOC]`

**§2.2 Instrument universe.** A deterministic function of measured liquidity and venue metadata,
recomputed once per day, frozen within the day (AX-04 §4). Universe size is an *output* of the
liquidity screen, not a fixed constant; the design supports 1…N instruments with N bounded by the
measured data budget (AX-04 §8).

**§2.3 Horizons.** Decision cadence and horizons are constrained by A6 and by the statistical power
requirement (AX-10 §3). Canonical decision timeframes: `15m`, `1h`, `4h` (all three are supported by
the venue's WebSocket kline stream `[V-DOC]`), with bar-close evaluation only — never intra-bar
decision-making on incomplete candles.

**§2.4 Account model.** Isolated margin per position; one-way position mode; leverage is an *output*
of sizing (AX-07 §8), not an input knob. Cross-margin and hedge mode are out of scope (they multiply
the state space; A7).

**§2.5 Environments.** `RESEARCH` → `BACKTEST` → `SHADOW` → `PAPER` → `MICRO-LIVE` → `LIVE`. The
environment is a property of the *run*, recorded on every artifact; no artifact may exist without one
(AX-03 §7). Only `LIVE` sends signed orders to the venue. `PAPER` uses a simulator, not the venue
(AX-11 §2). `SHADOW` is live data with zero orders.

**§2.6 Operator.** The owner, one person, non-professional availability. All human-facing flows must
assume the operator is asleep, travelling, or offline for hours at a time; the system's safety may
never depend on timely human action (A8).

---

## 3. Architecture: planes and dependency law (`AX-01:§3`)

### 3.1 Planes

| Plane | Code prefix | Responsibility (owns) | Doc |
|---|---|---|---|
| Venue Access | `vap` | Transport, signing, clock offset, rate governor, error taxonomy, outcome classification, conformance harness | AX-02 |
| Market Data | `mdp` | Collection, normalisation, quality gates, L0 tape, L1 curated store, gap repair, snapshot construction | AX-04 |
| State & Features | `sfp` | Deterministic feature/state computation from L1 only, with declared availability lag | AX-05 |
| Forecast | `fcp` | Registered forecasters, calibration, combination, uncertainty | AX-06 |
| Portfolio | `pfp` | Risk model, covariance, target weights, trade list, no-trade band | AX-07 |
| Execution | `exp` | Order planning, order FSM, idempotency, protective orders, reconciliation, cost ledger | AX-08 |
| Risk Governor | `rg` | Health/performance state machine, risk budget multiplication, pre-trade kernel, kill switches | AX-09 |
| Learning | `lnp` | Dataset builders, simulator/backtester, experiments, promotion/demotion, drift monitors | AX-10, AX-11 |
| Control & Observability | `cop` | Config/provenance loader, journal, metrics, alerts, operator interface, backup | AX-12 |

### 3.2 Dependency law (`AX-01:§3.2`)

1. Runtime data flow is **acyclic** and strictly downward:
   `vap → mdp → (L0,L1) → sfp → fcp → pfp → rg(pre-trade gate) → exp → vap(venue) → journal → L1`.
2. `rg` may **veto or reduce** any action from any plane at any time; no plane may veto `rg`
   (INV-7).
3. `lnp` is **offline**: it may read L0/L1 and write only to the model/parameter registry. No runtime
   plane may read from `lnp` processes; they read *frozen artifacts* from the registry by version.
4. `cop` observes everything and may change nothing except configuration, which is applied through
   the config loader's validation and the change-control procedure (AX-12 §8).
5. **Import rule:** a module may import only from its own plane and from the planes above it in the
   flow, plus the shared `axiom.core` types. Violations are caught by a static import test
   (`T-ARCH-001`, AX-14 §4).

### 3.3 Single decision kernel (`AX-01:§3.3`)

There is exactly one implementation of the decision path: `kernel(snapshot, params, models) → actions`.
Live, paper, shadow, and backtest differ **only** in (a) the source of the tape, (b) the execution
adapter, (c) the clock. Any code path that exists only in live or only in backtest is a defect.

---

## 4. Authority model (`AX-01:§4`)

| Actor | May | May not |
|---|---|---|
| Decision kernel | propose target positions and orders | bypass `rg`; write to L0/L1; know whether it is live or simulated |
| Risk Governor | veto, reduce, flatten, halt, arm/disarm | increase risk above what `pfp` proposed; generate alpha |
| Execution plane | choose *how* to execute an approved action within its price/time budget | change the approved size, symbol, direction, or risk parameters |
| Learning plane | propose model/parameter versions into the registry | write to the registry without passing the promotion gates; run in the live path |
| Operator (owner) | set owner-policy inputs, approve promotions, arm/disarm, kill, pause | modify historical tape/journal; alter risk limits without a recorded decision (AX-18) |
| Implementer/agent | write code satisfying clauses, add tests, raise `[ISSUE]` records | invent parameters, thresholds, defaults, or behaviour not covered by a clause (C5) |

**Conflict resolution.** If two documents appear to conflict, the stricter interpretation wins and an
`[ISSUE]` record must be filed; the conflict is resolved by an ADR, not by implementation choice
(AX-17 §4).

---

## 5. The Law (`AX-01:§5`)

### 5.1 Provenance law (implements C5)

**L1.** Every constant that appears in code, config, or a document must carry exactly one provenance
class:

| Class | Meaning | Where the value comes from | Verification |
|---|---|---|---|
| `[V]` | Venue fact | live official venue source or venue response at runtime | fetched, never hardcoded; re-verified per AX-02 §7.6 |
| `[D]` | Derived | a formula in the docs from other quantities | unit test recomputes the formula (AX-14 §4) |
| `[C]` | Calibrated | a named calibration procedure on named data | procedure recorded; calibration artifact hashed; acceptance metric recorded |
| `[O]` | Owner policy | a bounded input from the Owner Input Register (AX-15 §9) | validated against its allowed range; fail-closed if unset where required |

**L2.** A value without a class is a **defect**, detected by a lint test that scans the parameter
registry of the built configuration (`T-PROV-001`). The same lint fails if a `[C]` parameter is used
with a calibration artifact older than its re-calibration period.

**L3.** Thresholds should preferentially be *derived from data* (quantiles of an empirically
estimated null distribution, cost multiples, uncertainty bounds) rather than chosen; when a threshold
must be a policy choice, it is `[O]` and bounded.

**L4.** Any formula in the documents uses explicit units and a stated estimator with known failure
modes; no formula may be presented without its assumptions.

### 5.2 Engineering law — invariants (INV-series)

| ID | Invariant | Enforced by |
|---|---|---|
| INV-1 | **Fail-closed.** If a precondition cannot be *verified*, no risk-increasing action occurs. Risk-reducing paths remain available. | `T-GOV-*`, `T-PRETRADE-*` |
| INV-2 | **Two authorities.** The journal is authoritative for intent; the venue is authoritative for reality. Divergence triggers reconciliation; never a silent overwrite. | `T-RECON-001`, `T-JRN-002` |
| INV-3 | **Exactly-once effects.** Every state-changing venue call is preceded by a write-ahead intent record carrying a unique idempotency key; retries reuse the key or are resolved by query; blind resubmission is forbidden. | `T-AMB-*` |
| INV-4 | **Point-in-time.** A decision at wall-clock `t` may use only records with `ingest_ts ≤ t` and may not use a revision published after `t`. | `T-PIT-*` |
| INV-5 | **Determinism / parity.** The kernel is a pure function of (snapshot, param-set version, model-artifact hashes, code version). Replay reproduces the decision stream bit-for-bit. | `T-PARITY-*`, `T-DET-*` |
| INV-6 | **Provenance.** §5.1. | `T-PROV-001` |
| INV-7 | **Separation of authority.** Alpha cannot modify risk limits; risk cannot create alpha; the governor only reduces. | code review + `T-ARCH-002` |
| INV-8 | **Least privilege.** The API key has trading permission only, never withdrawal; secrets never appear in the repository, logs, journals, notifications, or chat. | `T-SEC-*` |
| INV-9 | **Asymmetry.** De-risking is automatic and immediate; re-risking is slow, evidence-gated, and never automatic. | `T-GOV-*`, AX-10 §4 |
| INV-10 | **Rebuildability.** L0 is append-only and immutable; every derived artifact records the code, parameter, and model versions that produced it and can be rebuilt to a byte-identical result. | `T-REBUILD-*` |
| INV-11 | **Observability.** Every decision, refusal, transition, and error is journaled with cause and input references; there is no silent code path. | `T-OBS-*` |
| INV-12 | **Bounded blast radius.** Global daily-loss budget, per-cluster caps, and per-trade caps bound the worst-case outcome under simultaneous, correlated failures. | `T-RISK-*` |

### 5.3 Change law (`AX-01:§5.3`)

1. A normative clause changes only via an ADR (AX-18) + version bump + traceability update + re-run of
   affected tests.
2. Parameters of class `[C]` change only by re-running their calibration procedure; parameters of
   class `[O]` change only by an operator action that is journaled with the previous and new value and
   the operator's stated reason.
3. Risk-limit parameters are **dual-control**: a change requires a journaled operator action *and* a
   subsequent, separate confirmation step (AX-12 §8) — deliberate friction, by design (A5).
4. Deleting a test is forbidden; a test may be superseded by a stricter test with an ADR.

---

## 6. Complexity admission (`AX-01:§6`, implements A7)

Every component, factor, model, filter, and branch is assigned a tier:

| Tier | Meaning | Admission requirement | Removal rule |
|---|---|---|---|
| `T1` | Core, always on in the live path | Required by an INV or by an A-series axiom; cannot be removed without breaking the system | none |
| `T2` | Conditional | Must pass the marginal-information test (`T-ADM-002`, AX-05 §2.3): adds out-of-sample, cost-adjusted, multiple-testing-corrected value *and* its data requirement is met and its sample-size requirement is satisfied | removed automatically if it fails the test in two consecutive quarterly reviews |
| `T3` | Research-only | Exists in `lnp` only; never imported by runtime planes | graduation to `T2` only through AX-10 §4 gates |

**Prohibited:** introducing a component because it is "standard", "impressive", or appears in the
prior project. A component without an admission record is a defect.

---

## 7. Risk philosophy (`AX-01:§7`)

AXIOM manages four budgets. Each has an owner, a unit, and a hard floor.

| Budget | Unit | Hard rule |
|---|---|---|
| Capital-at-risk | quote currency, per trade / per cluster / per day | Never exceeded even if all limits fire simultaneously (INV-12); daily-loss budget is a *stop*, not a warning. |
| Data integrity | number of unusable records / staleness seconds | Any instrument whose data fails its gate is *excluded from new risk* until repaired (INV-1). |
| Execution quality | realized cost vs modelled cost (bps) | If realized cost exceeds the model's upper bound, the system de-risks and the affected strategy's promotion is suspended until the cost model is re-fitted (AX-08 §3.5). |
| Operational | error/incident budget | Above a threshold rate of `SEV-1/SEV-2` incidents, the system returns to the previous rung of the ladder (AX-10 §4.4). |

**Loss definition.** All risk math is expressed in *R* units (R = the account's risk unit, see AX-07
§3) and in volatility-scaled drawdown, never in raw percentages alone, so that thresholds are
comparable across regimes (A2, L3).

---

## 8. Document map and reading order (`AX-01:§8`)

| # | Document | Purpose | Normative? |
|---|---|---|---|
| AX-00 | Design Checkpoint | constraints, axioms, evidence boundary, non-inheritance | yes |
| AX-01 | Charter, Law and Architecture | scope, invariants, authority, complexity admission | yes |
| AX-02 | Venue Truth & Conformance | everything about Toobit that the system depends on, plus the probes that verify it | yes |
| AX-03 | Domain Model, Time and Identity | objects, IDs, clocks, point-in-time, schemas, quantization | yes |
| AX-04 | Data Plane | acquisition, quality gates, storage, rebuild, universe construction | yes |
| AX-05 | Signal Library | estimators and features with exact math and admission tests | yes |
| AX-06 | State, Forecast and Combination | regime detection, calibrated forecasts, ensembling | yes |
| AX-07 | Risk Model, Portfolio and Sizing | covariance, limits, sizing, leverage, stops | yes |
| AX-08 | Execution and Cost | order lifecycle, cost model, ambiguity protocol, reconciliation | yes |
| AX-09 | Governor and Fail-Safe | health/performance state machine, kill switches, escalation | yes |
| AX-10 | Research, Learning and Promotion | experiments, statistics, ladder, drift, decommission | yes |
| AX-11 | Simulator and Backtest | fill/cost/funding models, parity requirements | yes |
| AX-12 | Operations, Security, Observability | deployment, benchmarks, secrets, runbooks, operator UX | yes |
| AX-13 | Interface Contracts | module APIs, event schemas, config schema | yes |
| AX-14 | Tests and Acceptance | test taxonomy, IDs, gates G0–G6 | yes |
| AX-15 | Parameter Registry | every parameter with unit, default, class, procedure | yes |
| AX-16 | Work Breakdown and Roadmap | phases, deliverables, definitions of done, estimates | yes |
| AX-17 | Traceability and Gap Audit | requirement→clause→test matrix, no-gap checklist | yes |
| AX-18 | Decision Records | ADRs, including all owner decisions | yes |
| `contracts/` | machine-readable artifacts | config YAML, SQL DDL, JSON Schemas | yes |

**Reading order for an implementer:** AX-00 → AX-01 → AX-02 → AX-03 → *the document of your module*
→ AX-13 → AX-14 → AX-15. **Reading order for a reviewer:** AX-17 → AX-01 → AX-02 → AX-03 → the rest.

---

## 9. Canonical glossary (`AX-01:§9`)

Terms are fixed here; documents may not redefine them.

- **Tape (L0):** append-only, immutable record of every received datum with its ingest metadata.
- **L1 (curated):** deduplicated, ordered, validated time series derived from L0, rebuildable.
- **Snapshot:** the immutable, hashed set of L1 facts visible to a decision at a given instant, with
  `as_of` = the decision time. Decisions reference a `snapshot_id`, never a "current value".
- **Availability lag:** the time between an event's occurrence and the earliest moment a correct
  decision could have used it; declared per source and per feature.
- **Feature:** a deterministic function of L1 restricted to `ingest_ts ≤ as_of`, with a version and a
  declared lag.
- **Forecast:** a calibrated distribution (not a point) of future *net* return for an instrument and
  horizon, plus model/version/uncertainty metadata.
- **Target:** desired position (quantity, or weight) after portfolio construction and caps.
- **Intent:** a write-ahead journal record of an action the system is about to attempt at the venue,
  carrying the idempotency key.
- **Plan:** the execution-level decomposition of an approved action (orders, prices, times, budgets).
- **Fill:** an exchange-reported execution; unique by `fill_id`; appended, never edited.
- **Position (truth):** derived by reconciling journal intent with venue state; disagreements are
  incidents, not averages.
- **Risk unit (R):** the money value the system is willing to lose if a single trade's stop is hit
  under modelled slippage (AX-07 §3).
- **Mode:** operating mode (OFF/ARMED/SHADOW/PAPER/MICRO-LIVE/LIVE) — what the system is permitted to
  do.
- **Governor state:** health/performance risk multiplier (NORMAL/CAUTION/REDUCED/DEFENSIVE/FLATTEN/HALT).
- **Rung:** a stage of the capital ladder (AX-10 §4).
- **Gate:** a binary acceptance checkpoint (G0–G6) with required evidence (AX-14 §6).
- **Provenance class:** `[V] [D] [C] [O]` (§5.1).
- **Evidence class:** `[MEASURED]` (produced by our own instrumented run), `[SIMULATED]` (produced by
  the simulator), `[CLAIM]` (stated by a source, not reproduced), `[DESIGN]` (true by construction).
