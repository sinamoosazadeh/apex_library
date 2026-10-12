# AX-00 — Independent Design Checkpoint (CP-0)

**Status:** Normative preamble to the AXIOM design suite. Read before any other AX document.
**Date of record:** 2026-10-12 (UTC).
**Author:** AXIOM design session (single designer of record).
**Purpose:** Record *how* AXIOM's requirements were derived, *from what* they were derived, and *what is deliberately not inherited* from any earlier project. Every later document cites this checkpoint's axioms (A1–A10) and owner constraints (C1–C8) rather than restating them.

---

## 0. Why this document exists

A design suite that cannot state where its constraints came from cannot be audited, and a design that
borrows structure without reasons cannot be trusted. This checkpoint therefore fixes, in order:

1. the **hard constraints** imposed by the owner (C-series);
2. the **design axioms** derived from first principles by this designer (A-series);
3. the **evidence boundary**: what has been verified (live official sources, dated), what is a
   *claim* made by third-party or historical material, and what is unknown;
4. the **non-inheritance clause**: the explicit statement that AXIOM is not a revision, successor,
   upgrade, or repair of the earlier `apex_gen5` project, and the list of ideas that were
   *deliberately rejected* as well as the few that were *adopted as transferable knowledge*.

Everything after this file is engineering. This file is law about provenance.

---

## 1. Owner constraints — C-series (non-negotiable, from the owner's instruction)

| ID | Constraint (as understood) | Design consequence |
|---|---|---|
| C1 | Trading target is **crypto futures** on **Toobit only**. No spot, no other venue in the baseline. | Venue layer is single-venue by design; no smart order routing, no cross-venue arbitrage, no spot hedge leg. |
| C2 | The owner **has an account** there and will trade it. | Real capital is in scope *eventually*; therefore safety, idempotency, and recovery are first-class, and promotion gates are mandatory (see AX-10). |
| C3 | Required quality level is "institutional / Tier-A hedge-fund grade, above". | Statistical validity, cost realism, evidence discipline, and operational rigor are required, **not** decorative architecture; complexity must be justified (A7). |
| C4 | The design must be **complete**: an execution team must be able to code it with **zero guesswork**, with no clause that returns to the designer for missing data, and no clause deferred "to the future". | Every parameter carries a provenance class (AX-15); every unknown about the *world* carries a specified resolution procedure with acceptance criteria (AX-02 §7, AX-14). |
| C5 | **Not one character** enters the design without a valid reason/document/logic. | Provenance law: `[V]` venue-verified, `[D]` derived with formula shown, `[C]` calibrated by a named procedure, `[O]` owner policy. Nothing else is permitted to exist (AX-01 §5). |
| C6 | The previous project's repository is a **knowledge source only**; its architecture, philosophy, decomposition, data flow and logic are explicitly **not endorsed**. | Non-inheritance clause (§5). Where a prior lesson is used, it is cited as an external lesson and re-derived, never copied as structure. |
| C7 | The system must be usable by its owner in practice (single owner-operator). | Operator is treated as a *component* with latency and failure modes (A8); alerting, approvals, runbooks and a one-command "arm/disarm/kill" surface are normative, not optional (AX-12). |
| C8 | Unspecified-but-required policy values (risk appetite, capital, notification destination, and similar) must not be guessed by implementers. | A bounded **Owner Input Register** (AX-15 §9) with safe defaults and defined fail-closed behaviour when unset. The design does not leave gaps; it defines an input interface. |

**Interpretation discipline.** C4 vs C8: "no gaps" means *no unspecified design decision and no path that
requires improvisation*. It does **not** mean the designer must invent facts about the world that only
measurement can produce (device performance, venue error codes, cost distributions). For those, the
design specifies a **measurement procedure, acceptance criteria, and a fail-closed fallback**, so the
implementer never has to guess either.

---

## 2. Design axioms — A-series (derived first, before reading any prior-project material)

These were derived from the physics and economics of the problem, not from any earlier design.

**A1 — Trading is inference under cost.** The system's output is never "a signal"; it is a *distribution
of net outcomes* (after fees, spread, slippage, funding, and financing) for an action. Only the
lower-confidence bound of that distribution may authorise risk. Consequence: a calibrated *cost model*
is not an add-on module; it is the gate through which every idea must pass (AX-08 §3).

**A2 — Every edge decays.** Any statistical regularity is an asset with a half-life, a capacity limit,
and a monitoring requirement. Consequence: monitoring, drift detection, and decommissioning are
designed at the same time as the alpha itself (AX-10 §6), not later.

**A3 — The binding constraints are data, cost, and sample size — not compute or model class.** With
single-venue retail-feed data, the achievable information rate is the limit. Consequence: model
families are admitted only when their *data* exists and their *sample-size* requirement is satisfiable
(A7, AX-05 §2).

**A4 — Measurement beats assumption.** Any statement about the venue, the device, or the cost of
trading is either (a) read from a pinned official source, (b) measured by a named probe, or (c) marked
as an assumption with a probe that will replace it. Consequence: the design begins with a **Venue
Conformance Harness** and a **device/resource benchmark gate**, not with hardcoded beliefs (AX-02 §7,
AX-12 §2).

**A5 — Survival dominates return.** The events that end accounts are rare, discrete and expensive:
gaps, halts, partial fills, duplicated orders, unknown outcomes, liquidations, stale data, key misuse.
Consequence: idempotency, reconciliation, kill paths, and fail-closed defaults are *core*, and the
worst-case path gets more design attention than the expected path (AX-08 §5, AX-09).

**A6 — Latency defines the admissible alpha class.** With a public REST execution path and
consumer-grade network, round-trip decision latency is on the order of 10²–10³ ms. Therefore every
admissible strategy must have an economic horizon where that latency is immaterial — i.e. holding
periods of minutes to weeks. Consequence: high-frequency market making, queue-position gaming, and
latency arbitrage are **out of scope by construction**, and this is stated as a non-goal rather than
silently attempted (AX-01 §3).

**A7 — Complexity must earn admission.** Every component, factor, indicator, and branch consumes
sample size and introduces failure modes. Consequence: a tiered admission system (`T1` always-on core,
`T2` conditional, `T3` research-only) with an evidence test for promotion and a rule for removal
(AX-05 §2, AX-10 §5).

**A8 — The operator is a component.** The owner-operator has latency (minutes to hours), availability
(not 24/7), and failure modes (fatigue, misreading, acting on stale context). Consequence: the human
interface is specified with the same rigor as the machine interface: bounded decisions, safe defaults,
one-tap kill, and no requirement for the operator to act quickly to remain safe (AX-12 §7).

**A9 — Reproducibility precedes learning.** Without deterministic replay of decisions from a recorded
tape, no result can be attributed to skill rather than luck, environment, or drift. Consequence: an
append-only raw tape, point-in-time semantics, and a *single decision kernel* shared by live, paper,
and backtest are architectural invariants (AX-03 §6, AX-11 §5).

**A10 — Capital deployment is a ladder, not a switch.** Each rung (research → shadow → paper →
micro-live → scaled) costs evidence and can be lost. Consequence: explicit promotion and demotion
criteria, with statistical (not narrative) gates (AX-10 §4).

### 2.1 Axiom → structure map

| Axiom | Primary documents | Enforced by (tests) |
|---|---|---|
| A1 | AX-06 (forecasts), AX-08 (cost) | T-NET-*, T-COST-* |
| A2 | AX-10 §6 | T-DRIFT-* |
| A3 | AX-05 §2 (admission), AX-10 §3 | T-ADM-*, T-POWER-* |
| A4 | AX-02 §7, AX-12 §2 | T-VCH-*, T-BENCH-* |
| A5 | AX-08 §5, AX-09 | T-AMB-*, T-RECON-*, T-KILL-* |
| A6 | AX-01 §3 (non-goals) | design-review gate (no HFT paths exist) |
| A7 | AX-05 §2, AX-10 §5 | T-ADM-*, T-DECOMM-* |
| A8 | AX-12 §7 | T-OPS-*, runbook drills |
| A9 | AX-03 §6, AX-11 §5 | T-PARITY-*, T-DET-* |
| A10 | AX-10 §4 | gate checklists G2–G6 |

---

## 3. Evidence boundary — what is verified, what is claimed, what is unknown

The design team must never confuse these three classes. They are used consistently across the suite.

**Class 1 — Verified against live official sources (dated 2026-10-12, UTC).**
- `api-docs.toobit.com` — Toobit's official API documentation (basic information, USDT-M market data,
  USDT-M account/trading, USDT-M WebSocket streams). Facts drawn from it are tagged `[V-DOC]`.
- `github.com/toobit-docs/agent-kit` at commit `2ee2d6b54617974c789a407f74c0bbf15cbb99f7`
  (2026-03-15), the exchange's own toolkit: endpoint list, per-endpoint rate limits, parameter
  semantics, error-code behaviour table. Facts drawn from it are tagged `[V-KIT]`.
- Both are **point-in-time**. Venue facts rot; every `[V-*]` fact is therefore re-verified by the
  Venue Conformance Harness before first live use and re-verified on a schedule (AX-02 §7.6).

**Class 2 — Claims from third-party/historical material (the `apex_library` repository).**
Material reviewed for this checkpoint, and the *only* material cited:
`APEX_GEN6_LEARNING_BRIEF.md`, `APEX_GEN5_TO_GEN6_SOURCE_MATERIALS_REGISTER_2026-10-06.md.md`,
`APEX_GEN5_POSTFREEZE_DISCOVERY_DELTA_INDEX_2026-10-06.md`,
`APEX_GEN5_v1.0_TO_v1.1_FREEZE_HANDOFF_CHECKLIST_4.md`, `APEX-GEN5-DATAFLOW-PROFESSIONAL.md`,
`MEGA_ENCYCLOPEDIA_L1_L2_L3_DATA.md`, `MEGA_ENCYCLOPEDIA_QUANT_METHODS.md`,
`25_NEW_PROJECT_IDEAS.md`, `8_AGENTS_PROMPTS_FOR_CODING_&_IMPLEMENTING.md`, `TELEGRAM_CHECK_LIST.md`,
and structural inspection (headings, sizes, index files) of `APEX_GEN5.md` (20,983 lines) and the
88,322-line dossier patch.
- These are treated as **claims by their authors**, not as verified facts about the cryptomarket, the
  venue, the device, or performance. Where such a claim is used, it is labelled `[L-CLAIM]`.
- The 88k-line dossier, the 21k-line blueprint, all PRs, audits and probe reports were **not**
  exhaustively read. No claim is made here about the prior project's completeness or correctness
  beyond what the above files state about themselves.

**Class 3 — Unknowns that only measurement can close.**
Owner's device performance envelope; realized execution cost distribution on the owner's account;
venue behaviour for untested parameter combinations; sustainable data throughput on the owner's
network. Each is assigned a probe in AX-02 §7 or a benchmark in AX-12 §2, with an acceptance
criterion and a fail-closed fallback. **No design decision depends on an unmeasured value.**

**Lessons adopted as transferable knowledge (re-derived, not copied).** The following principles appear
in the reviewed material in some form; each is restated here as *this design's* principle with its own
mechanism, and none is imported as structure:

| # | Principle (as adopted) | Where it acts in AXIOM |
|---|---|---|
| L1 | A written requirement, an existing code path, an exercised caller, and an accepted operational result are four different things. | AX-14 §6 (evidence classes per gate), AX-17 §4 |
| L2 | Identity, time, provenance, corrections, and point-in-time availability decide whether downstream conclusions are valid. | AX-03 (whole document) |
| L3 | Trade outcomes can be partially observed; persistence, idempotency, interruption, retry, recovery, and reconciliation must be designed explicitly. | AX-08 §5–§7 |
| L4 | A local or synthetic test proves only its own scope; environment/venue/long-run acceptance are separate gates. | AX-14 §2, AX-10 §4 |
| L5 | Resource constraints must be measured at the boundary that matters (full workload, persistence, restart, sustained operation). | AX-12 §2 |
| L6 | Complexity and numeric rules need reasons, units, and a validation method. | AX-01 §5, AX-15 |
| L7 | Operations and human control are part of system quality; refusals and failures must be observable. | AX-12 §7, AX-09 §6 |
| L8 | Historical records can disagree or be incomplete; keep snapshot identity and evidence type explicit. | §3 above, AX-17 §5 |

**Explicitly rejected as structure (with reasons).** Not carried into AXIOM:

1. **Scale-by-engine-count.** A fixed roster of a dozen-plus "engines", each mandatory, each producing
   a first-class object. Reason for rejection: violates A3 and A7 — the number of sub-systems is an
   output of data availability and evidence, never an input.
2. **One monolithic blueprint as the single normative document.** Reason: makes clause-level
   traceability, review, and change control impossible; AXIOM is a set of numbered documents with a
   traceability matrix (AX-17) and per-clause IDs.
3. **Numbers introduced as "governed defaults" without a derivation or a calibration path.** Reason:
   violates C5 directly; superseded by the provenance classes in AX-15.
4. **Architecture in which the same monolith computes features, state, decisions and execution.**
   Reason: makes point-in-time correctness and deterministic parity unverifiable; superseded by the
   plane separation of AX-01 §6 with a single decision kernel (A9).
5. **Live self-modification of risk or model parameters.** Reason: violates the separation of
   authorities (INV-7) and makes attribution impossible; superseded by the promotion pipeline
   (AX-10 §4) and dual-control parameter changes (AX-12 §8).
6. **Interface/notification channels carrying credentials or account secrets.** Reason: violation of
   least privilege; superseded by AX-12 §5.
7. **Any reliance on a "Trading Universe" or taxonomy inherited from an earlier specification.** The
   AXIOM universe is constructed from measured liquidity and venue metadata (AX-04 §4).

**No-inheritance clause.** AXIOM is an independent system. It shares no architecture, module boundary,
data flow, object model, parameter set, naming convention, or document structure with any earlier
project. Every element in this suite must be justifiable by reference to C1–C8, A1–A10, an official
venue source (`[V-*]`), a derivation, a calibration procedure, or an explicit owner policy. If an
element cannot be justified that way, it must be deleted.

---

## 4. Feasibility envelope recorded at CP-0 (design consequence of C3 + A6)

This design is only coherent if it is honest about what is *not* possible on a single-venue retail
API. Recorded here so that no later document drifts:

- **Horizon floor.** Any strategy whose expected holding period is below ~10 minutes is rejected by
  construction (A6). The admissible set is intraday-to-multi-week, with an explicit cost hurdle
  (AX-08 §3) that is larger for shorter horizons.
- **Information floor.** The data available is: venue candles, trades (with taker side flag and a
  globally increasing trade id), partial/diff book via WebSocket, best-bid/ask stream, mark price,
  venue index price (a disclosed cross-exchange weighted composite), funding rate + funding history
  (8-hour settlement in the observed sample), open interest (current only — history must be
  constructed by our own polling), long/short account ratio (30-day window), insurance fund, risk-limit
  tiers, and the owner's own orders/fills/positions. **No options data, no L3 queue data, no
  order-book history beyond what we record ourselves.** Every alpha family must be expressible from
  this list; anything requiring more is out of scope (AX-05 §2).
- **Capital scale honesty.** Per-trade notional is bounded by participation caps derived from measured
  depth (AX-07 §7) — the design governs *risk*, not vanity size; the binding constant is venue
  liquidity, recomputed continuously.
- **Evidence floor.** The owner's decision to deploy capital will, at best, rest on months — not years
  — of live evidence. The design compensates with (a) strict out-of-sample discipline, (b)
  multiple-testing control, (c) conservative priors and shrinkage, and (d) a promotion ladder whose
  first rungs require no capital at all (AX-10 §4).

---

## 5. What this checkpoint does *not* do

It does not specify modules, schemas, formulas, thresholds, or code. It fixes constraints, axioms,
provenance law and non-inheritance. All engineering decisions live in AX-01 … AX-18 and are traceable
back to this file.

**Change control.** This document may be amended only by an explicit owner decision recorded in
AX-18 (Decision Records) with the amendment text; silent edits are a design defect and are caught by
the hash check in AX-17 §6.
