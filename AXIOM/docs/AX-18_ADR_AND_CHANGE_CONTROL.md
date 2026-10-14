# AX-18 — Architecture Decision Records and Change Control

**Status:** Normative. This document is the **only** legal way to change the design.
**Upstream:** AX-01 §5 (the Law), AX-14 §6 (gates).
**Downstream:** every future revision of AX-00…AX-17 and the code.

---

## 1. Purpose (`AX-18:§1`)

A design of this size dies in two ways: silently drifting away from its own text (the documents stop
describing the system), or being amended casually by whoever is under pressure at the time (the
constraints erode). The ADR mechanism exists to make every change *deliberate, recorded, and
reversible*.

---

## 2. Change classes (`AX-18:§2`)

| Class | Example | Required |
|---|---|---|
| **Class-1 editorial** | typo, formatting, a clarification that cannot change behaviour | commit + note; no ADR |
| **Class-2 additive** | a new test id, a new parameter that is not used in a decision path, a new runbook | ADR (short form) + registry/schema update |
| **Class-3 behavioural** | a new feature, a changed threshold class, a changed order construct, a new data source | full ADR + gate impact analysis + tests + re-run of the affected gates |
| **Class-4 constitutional** | axioms (AX-00 §2), invariants (AX-01 §5), the authority model, the risk envelope's *shape*, the venue (ADR-001) | full ADR + the owner's written approval + a re-audit (AX-17) |

`AX-18:§2-R1` — A change that touches a number in a decision path is never Class-1, no matter how small
it looks. `AX-18:§2-R2` — A change that *weakens* a safety threshold, gate, or the ambiguity protocol
is at least Class-3, and in the case of gates/ambiguity/kills is Class-4.

---

## 3. ADR format (`AX-18:§3`)

```
ADR-nnn: title                     Status: Proposed | Accepted | Superseded-by ADR-mmm | Rejected
Date, Decider (owner/architect), Class (1–4)

Context        the forces at play, in one paragraph
Decision       the choice, stated as an instruction to the system
Rationale      why, with the mechanism (not "it backtests better")
Alternatives   each rejected option and the specific reason for rejection
Consequences   what becomes possible/impossible; what must be re-tested; cost
Evidence       citations, measurements, or the gate record that supports it
Supersedes     (if any)
```

An ADR without a stated mechanism in `Rationale` is rejected: "the numbers looked better" is not a
mechanism, it is a memory of one sample (A9).

---

## 4. The register (`AX-18:§4`)

### ADR-001 — Single venue: Toobit USDT-M futures (`Accepted`, Class-4)

**Context.** The owner holds a Toobit account; multi-venue adds reconciliation, latency and regulatory
complexity for a system that has not yet proven one venue.
**Decision.** All execution goes to Toobit futures. External venues may be used only as *research data*
(ADR-011, ADR-018 conditions).
**Rationale.** Mechanism: cost-of-complexity. Every additional venue multiplies the ambiguity surface
(A5) and the reconciliation state space, while the marginal edge from a second venue, at this capital
size, is negative after fees and slippage.
**Alternatives rejected.** (a) Two venues for arbitrage — the design's non-goals forbid latency-class
strategies (AX-01 §2); (b) multi-venue for redundancy — redundancy of *venue* does not reduce the risk
that dominates (liquidation, ambiguity, data), and doubles the operational load.
**Consequences.** Single point of failure accepted and mitigated by venue-side protection (ADR-010),
drift detection (AX-02 §10), and the kill set (AX-09 §5).

### ADR-002 — One language: Python (≥3.11) for runtime and research (`Accepted`, Class-3)

**Decision.** Python everywhere; heavy numerical work via NumPy/SciPy/pandas (with optional numba for
hot loops if benchmarks require it).
**Rationale.** Mechanism: the decision kernel must exist once (A10/INV-5). Two languages guarantee two
implementations and therefore a permanent parity bug. Python's latency overhead is ~10³ times smaller
than the design's latency budget (AX-08 §2).
**Alternatives rejected.** C++/Rust core (no measurable benefit at 15-minute horizons, large cost to
maintain by a single owner); C# (better client exists, ADR-001 keeps us off it for control reasons).

### ADR-003 — One decision kernel, three seams (`Accepted`, Class-4)

**Decision.** A single kernel object decides; the tape source, the execution adapter and the clock are
injected (AX-01 §3.3, AX-11 §1).
**Rationale.** Mechanism: eliminates the class of bugs where the backtest and live disagree for reasons
that cannot be located. Decision parity becomes *testable* (`T-PARITY-002`).
**Alternatives rejected.** Separate backtest engine — the industry-standard source of inflated results;
"shared library, different wrappers" — still two decision paths.

### ADR-004 — Journal-first, append-only, hash-chained (`Accepted`, Class-4)

**Decision.** Every intent is journaled before transmission; the journal is append-only with a hash
chain; corrections are new events (AX-03 §5.3, AX-08 §7-R1).
**Rationale.** Mechanism: after an `UNKNOWN`, only the journal can tell us what we *intended*; without
it, duplicate orders and untracked positions are inevitable.
**Alternatives rejected.** Mutable state table (loss of evidence exactly when it matters); relying on the
venue's order history (no intent context, retention unknown).

### ADR-005 — SQLite (WAL) as the local store (`Accepted`, Class-2)

**Decision.** L1/L2 and the journal index live in SQLite in WAL mode, single writer, with L0 as ordered
segment files.
**Rationale.** Mechanism: transactional durability with zero administration on a phone-class device;
WAL gives readers without blocking the writer.
**Alternatives rejected.** PostgreSQL (resource cost on the target device, ADR: topology A); Parquet-only
(no transactional updates for the hot path); an in-memory store (weaker durability, not crash-only).

### ADR-006 — v1 canonical wire; v2 evaluated but not adopted (`Accepted`, Class-3)

**Decision.** Trade on the v1 routes with the documented signing law (parameter order = signature
order; `recvWindow` default 5 000 ms; header `X-BB-APIKEY`). v2 remains available for evaluation only.
**Rationale.** Mechanism: one wire, one signing implementation, one error map. The v2 JSON-body signing
is a second code path with its own byte-identity failure mode; adopting both doubles the surface with no
functional gain for this design.
**Alternatives rejected.** v2 (no required capability is missing in v1; the extra path adds risk);
"whichever responds faster" (non-determinism in the execution path).
**Note.** If a required capability appears only in v2, the change is Class-3 and must be an ADR with its
own conformance probes.

### ADR-007 — Bars as the decision substrate; minimum horizon 15 minutes (`Accepted`, Class-3)

**Decision.** Decisions are made on completed bars (provisional bars are never used, AX-03 §3.3), with
a minimum horizon of one 15-minute bar.
**Rationale.** Mechanism: the venue's own data offers 1 m as the finest reliable granularity for
history (REST trades limited to 60 records, no L2 history, no liquidation prints). Building decisions on
a substrate we cannot reconstruct after the fact makes research and live disagree. The latency budget
(AX-08 §2) shows the 15 m horizon is ~10³ above the achievable latency, so the choice costs nothing in
edge.
**Alternatives rejected.** 1 m decisions (fragile to data gaps, latency budget becomes ~1 % of the
horizon, and all features would need the unavailable microstructure); tick/event-driven (no historical
substrate).

### ADR-008 — Refusals are first-class products (`Accepted`, Class-3)

**Decision.** The system's primary output is a decision record containing *refusals with reasons*;
orders are the exception.
**Rationale.** Mechanism: an unknown number of correctly-refused trades is the evidence that the cost
gate and risk kernel are working (A7). Without the refusal ledger, "why isn't it trading" would be
answered by loosening a threshold — the exact failure mode this design exists to prevent.
**Alternatives rejected.** Silent refusal (indistinguishable from a crash); logging only errors (refusals
are not errors).

### ADR-009 — Maker-only / post-only strategies are not admitted (`Accepted`, Class-3)

**Decision.** Entry and exit constructs are taker. `POST_ONLY` exists in the venue, is therefore in the
capability matrix, and is **disabled** by policy; enabling it is Class-3.
**Rationale.** Mechanism: queue position is unobservable with the available data (no L2 history), so
maker fill probability cannot be estimated except from our own fills, which do not exist yet. A strategy
whose edge depends on maker fills cannot be honestly validated (AX-11 §4.5).
**Alternatives rejected.** "Try it and see" — that is a live experiment with capital on a property that
cannot be measured from history.

### ADR-010 — Protection lives at the venue, always (`Accepted`, Class-4)

**Decision.** Every position carries a venue-side protective order (MARK_PRICE `STOP`, or the venue's
trading-stop route) placed immediately after the fill and confirmed by query; our process is never part
of the protection path.
**Rationale.** Mechanism: the process can die, the network can fail, and the operator can be asleep; the
venue cannot (A5, dead-man design AX-09 §6.4).
**Alternatives rejected.** Local stop monitoring (single point of failure); trailing stops at the venue
(behaviour not verifiable, loosens risk control, AX-07 §9.2).

### ADR-011 — Cross-venue and other external data: research context only (`Accepted`, Class-3)

**Context.** Broader market context (e.g. BTC/ETH prices and funding from other venues available as
public data) can inform regime classification and beta estimation. The owner's envelope restricts
*trading* to Toobit.
**Decision.** External data may be used **only** for: (a) regime context (AX-06 §6), (b) cross-sectional
beta estimation when the local index is insufficient, (c) research robustness checks. It may **not**
originate an order, may not define a signal that could be executed without Toobit price agreement, and
must be stored in the same L0/L1 pipeline with the same gates and the same PIT timestamps (an external
series is as untrustworthy as any other). The features derived from it are marked `EXT` and are
T3 until admitted.
**Rationale.** Mechanism: information asymmetry cannot be traded where it cannot be executed; using
external prices to *time* local trades is a latency-class strategy (forbidden) wearing a research
costume. Regime context, by contrast, is a slow, robust input that does not require execution
elsewhere.
**Alternatives rejected.** Pure Toobit-only data (loses genuinely useful context at zero execution
risk); no restriction at all (would import an entire second venue's data-quality surface and legal
questions the owner did not authorise).
**Owner note.** If the owner prefers maximal strictness, disabling the `EXT` features is a parameter
change with no effect on any other component (AX-17 §4.3 `EXT-04`).

### ADR-012 — Parameter registry with provenance classes; no numeric literals in decision paths (`Accepted`, Class-3)

**Decision.** Every tunable number lives in AX-15 with a class (`V`/`D`/`C`/`O`); `[V]` values come only
from the harness; `[C]` values require a calibration reference; `[O]` values are the owner's.
**Rationale.** Mechanism: an unregistered number is an undocumented assumption; assumptions in decision
paths are precisely what makes a system unexplainable after a loss.

### ADR-013 — Risk allocation via HRP-clustered shrinkage, not full mean-variance (`Accepted`, Class-3)

**Decision.** The covariance chain is EWMA → Ledoit–Wolf single-index shrinkage → Marchenko–Pastur
denoising → PD repair; allocation is cluster-aware inverse-variance (HRP-style) inside a constrained QP.
**Rationale.** Mechanism: with `N` up to `P-UNI-001` and short histories, the sample covariance is
near-singular; unconstrained mean-variance amplifies estimation error into the largest positions —
exactly backwards. Shrinkage and clustering move weight toward the best-estimated directions and cap
concentration.
**Alternatives rejected.** Equal weight (ignores vol differences); raw sample covariance (unstable);
full Black–Litterman (requires prior machinery unjustified by our information set).

### ADR-014 — Covariance shrinkage: Ledoit–Wolf (`Accepted`, Class-3)

**Decision.** The shrinkage target is the single-index (market-model) covariance; intensity is estimated
by the Ledoit–Wolf analytic formula rather than cross-validated.
**Citation / evidence.** O. Ledoit and M. Wolf, *Honey, I Shrunk the Sample Covariance Matrix*,
Journal of Portfolio Management 30(4), 2004; and their later single-index formulation (Ledoit & Wolf,
*Improved estimation of the covariance matrix of stock returns with an application to portfolio
selection*, Journal of Empirical Finance 10(5), 2003). The analytic intensity estimator is
closed-form, deterministic, and requires no tuning — a property this design requires (`T-DET-*`).
**Rationale.** Mechanism: shrinkage trades a known small bias for a large variance reduction in the
inverse; the analytic formula removes a free parameter (which would otherwise be another thing to
overfit).
**Alternatives rejected.** Cross-validated shrinkage (a second parameter, and the CV objective is not
the portfolio objective); factor models fitted on our short history (over-parameterised); no shrinkage
(see ADR-013).

### ADR-015 — Statistical protocol: purged/embargoed folds, DSR, PBO/CSCV, SPA, MinTRL (`Accepted`, Class-3)

**Decision.** A promotion requires: purged K-fold + embargo, PSR(DSR) ≥ `P-LRN-005`, PBO ≤ `P-LRN-007`,
SPA significance over the surviving candidate set, `n_eff` from label uniqueness, and MinTRL satisfied.
**Citations.** M. López de Prado, *Advances in Financial Machine Learning* (2018) — purging, embargo,
uniqueness, triple barrier; D. Bailey & M. López de Prado, *The Deflated Sharpe Ratio* (Journal of
Portfolio Management, 2014); D. Bailey, J. Borwein, M. López de Prado & Q. J. Zhu, *The Probability of
Backtest Overfitting* (Notices of the AMS, 2014, CSCV) and their *Pseudo-Mathematics and Financial
Charlatanism* (Notices of the AMS, 2015); H. White, *A Reality Check for Data Snooping* (Econometrica,
2000); P. Hansen, *A Test for Superior Predictive Ability* (JBES, 2005); D. Politis & J. Romano,
*The Stationary Bootstrap* (JASA, 1994).
**Rationale.** Mechanism: with a finite search budget, the *maximum* observed Sharpe is a biased
estimator of skill; DSR/PBO/SPA convert the number of trials into an explicit correction, which is the
only way a single-operator project can avoid paying tuition to randomness.
**Alternatives rejected.** Plain t-statistics with a Bonferroni bound (overly conservative, ignores
dependence); "out-of-sample period is enough" (it is not: CSCV shows the in-sample winner need not
generalise).

### ADR-016 — Governor thresholds calibrated from null distributions (`Accepted`, Class-3)

**Decision.** Thresholds are quantiles of each statistic's own distribution during verified normal
operation (`CAL-GOV-01`), not hand-picked values (AX-09 §4.1).
**Rationale.** Mechanism: a threshold that is a quantile has a *stated* false-alarm rate; a hand-picked
number has an unknown one. Without this, the governor either fires constantly (and gets ignored) or
never fires (and is decoration).
**Alternatives rejected.** Industry-style fixed values ("5 % drawdown") — no relation to this system's
vol, turnover or sample.

### ADR-017 — Tiered collection (HOT/WARM/COLD), not exhaustive capture (`Accepted`, Class-3)

**Decision.** Depth snapshots at the HOT cadence for the active set, aggregates for the wider set, and
no attempt to record every tick.
**Rationale.** Mechanism: the binding constraint is storage and write bandwidth on the target device
(AX-12 §1), while the features that matter integrate over minutes (AX-05). Exhaustive capture would
consume the device's budget for information the system does not use.
**Alternatives rejected.** Full-depth L2 recorder (impossible on the target device, and unused);
liquidation/print capture (not available historically, so it would create research/live asymmetry).

### ADR-018 — Every feature must state a mechanism (`Accepted`, Class-3)

**Decision.** Admission to the signal library requires a stated economic/behavioural mechanism
(AX-05 §2.2) in addition to statistical evidence.
**Rationale.** Mechanism: with ~100 candidate features tested on limited data, some will pass by chance;
the mechanism requirement is an orthogonal filter that survives the data (it can be falsified later,
which is what makes retirement honest: AX-10 §8).

### ADR-019 — Purged K-fold with embargo as the default validation scheme (`Accepted`, Class-3)

See ADR-015 for the citation; this ADR fixes the *default* in `lnp`: purge width = horizon, embargo ≥
`P-LRN-002`. Walk-forward is the final arbiter for promotion; the CV is used for selection and
diagnostics only.

### ADR-020 — Labels: net-return with triple-barrier outcomes (`Accepted`, Class-3)

**Decision.** The primary label is the net return over horizon `H` after fees/slippage/funding; the
secondary label is the triple-barrier outcome (profit target, stop, time) with uniqueness weighting.
**Rationale.** Mechanism: a classifier that predicts "direction" without the path cannot be combined
with a stop-based risk process; the barrier label matches the actual exit logic, so calibration is
meaningful.

### ADR-021 — No online learning in the trading path (`Accepted`, Class-4)

**Decision.** Models are trained offline, versioned, and promoted through gates. In live, parameters may
only be *tightened* automatically (governor multipliers, feature demotion to zero weight); nothing is
re-fitted from live data in the decision path.
**Rationale.** Mechanism: online adaptation destroys attribution (a loss could be the market or the
adaptation) and creates a feedback loop between our own executions and our own model. Demotion is safe
because it is a *reduction* of exposure, which is always admissible (INV-9).
**Alternatives rejected.** Incremental learning (unmeasurable); daily re-train with auto-promotion (a
re-labelled search under live conditions — the definition of multiple testing in production).

### ADR-022 — Operator surface: CLI for control, Telegram for notification (`Accepted`, Class-2)

**Decision.** Control commands are CLI (local, authenticated by file permissions and an explicit
confirmation for destructive actions); notifications go to the owner's chosen channel (`OI-OPS-02`),
default Telegram, structured and rate-limited per severity.
**Rationale.** Mechanism: a chat channel is not an authenticated control plane and must never be able to
start trading by a mis-click; notifications must reach a phone (the owner's reality).
**Alternatives rejected.** Full chat control (authorisation and replay hazards); email-only (latency);
web UI (an unnecessary attack surface and a second code path).

### ADR-023 — Gates are monotone and evidence-class bound (`Accepted`, Class-4)

**Decision.** `G0…G6` are cumulative; passing a gate requires evidence of the matching class; any change
invalidates dependent gates; waivers require an ADR that changes the requirement (AX-14 §6).
**Rationale.** Mechanism: gate erosion is the standard path from a working system to a broken one; the
only defence is that weakening a gate costs more than passing it.

### ADR-024 — Simulator conservatism: adverse-first intrabar rules (`Accepted`, Class-3)

**Decision.** Within a bar, ambiguous sequences resolve against us; stops in gaps fill at the gap price
plus a slippage draw; maker orders require trade-through (AX-11 §4.3–§4.5).
**Rationale.** Mechanism: the simulator's job is to *falsify* strategies cheaply. An optimistic tie-break
converts "unknown" into "profitable", which is how simulated edges are born.
**Alternatives rejected.** Best-case tie-break (unusable); "random tie-break" (adds noise without
removing bias).

### ADR-025 — Local-first storage with explicit capacity degradation (`Accepted`, Class-2)

**Decision.** All authoritative artifacts are local; the capacity guard degrades in a documented order
and never silently deletes L0 or the journal (AX-04 §7).
**Rationale.** Mechanism: an unattended system running out of disk is a crash at an unknown time;
making degradation explicit converts a failure into a decision.

### ADR-026 — Non-normative research layer under `research/` (`Accepted`, Class-2)

**Context.** The owner maintains a literature encyclopedia (papers, books, regulation, venue/technical
documentation) around the concepts used by the system and by comparable institutional systems. Without a
declared status, such material would either be (wrongly) treated as design input or live outside the
documents entirely — both violate `AX-01:§5.4` (no undeclared influence on the decision function).

**Decision.** A directory `research/` exists with non-normative artifacts (`CONCEPT_ATLAS.md`,
`build_index.py`, `concept_index.json`, `search_queries.txt`). It is **outside** the design suite:
no clause of `AX-00…AX-17` references it, no gate (`G0…G6`) consumes it, and `T-DOC-001`'s
scope is `docs/`. Its index is a *search-vector* registry, not evidence: a source found through it is
graded (primary paper / replication / regulation / industry claim) before it may be cited by any design
clause, and a concept enters the system only through the normal path — `AX-05 §2` (mechanism +
marginal-information test + FDR) → `AX-10 §2–§4` (pre-registration, ladder) → `AX-15` (parameter id and
class) → this register (if behaviour changes).

**Rationale.** Mechanism: separating *knowledge collection* from *design authority*. The design must be
able to say "every line here is justified and testable"; a research collection by nature contains
unverified claims. Declaring the boundary explicitly keeps both honest — and it is falsifiable: the
moment anything in `research/` is cited by a clause, this ADR is broken (`T-DOC-002` audits that no clause outside these two ADRs cites `research/`
as a source of requirements).

**Alternatives rejected.** (a) Putting the atlas inside `docs/` — it would inherit normative force it
cannot support; (b) keeping it outside the repository entirely — the owner's collection would lose its
index, its ids, and its reproducibility; (c) banning literature review — absurd, since `AX-00 §3`
already fixes how external claims (`L-CLAIM`) are treated.

**Consequences.** `research/` may be edited freely (Class-1); moving anything from it into the design
requires the full procedure of §5. The generator `research/build_index.py --check` keeps the index and
the query pack consistent, in the same spirit as `contracts/build_registry.py --check`.

### ADR-027 — Governed build of the literature encyclopedia (`Accepted`, Class-2)

**Decision.** The encyclopedia is built as a set of graded entries with the fixed schema of
`research/CONCEPT_ATLAS.md` §E1 (`id, title_fa, title_en, aliases, family, engine, status, evidence,
sources[], axiom_refs[], notes`) and the status legend `CORE | ADJACENT | SPECULATIVE`. Three-entry
test per concept (§D3): primary source, second-degree interpretation, independent replication or
refutation; a concept lacking an independent replication is filed as *un-replicated*, never as
established.

**Rationale.** Mechanism: the industry failure mode is not too little reading but too little grading —
a collection that mixes a refereed paper, a vendor white paper and a YouTube strategy becomes unusable
for decisions. Status + grading make the collection *queryable by evidentiary strength*, which is the
same discipline `AX-00 §3` imposes on the design itself.

**Consequences.** Concept ids (`A01…A12`, `B01…B12`, and future families) are stable and referenced by
every collected artifact, so the encyclopedia can be indexed, deduplicated and searched by concept,
family, or evidentiary status. Adding a concept is a data change in `research/build_index.py`, not a
design change.

---

## 5. Amendment procedure (`AX-18:§5`)

1. Draft the ADR (§3) and record it as `Proposed`; assign its class.
2. Identify every clause affected; produce the diff to the design documents **before** the code change.
3. Identify the gate impact: which `G0…G6` evidence is invalidated (`T-GATE-001` computes this from the
   dependency map).
4. For Class-3/4: write or update the tests first; the ADR is `Accepted` only when the tests exist
   (for Class-4, additionally after the owner's approval and a re-audit of AX-17).
5. Apply the change in one atomic set: documents + registry/schema + tests (+ code, when the code
   exists). A partially applied ADR is a blocking defect.
6. Supersede, never delete: the old ADR stays in the register with `Superseded-by`.
7. Update AX-17's traceability tables and, if a number changed, AX-15's `cited by` lists.

**Prohibited without an ADR (`AX-18:§5-R1`):** adding/removing a gate; changing the ambiguity protocol;
changing a risk cap's *class*; adding a venue, a data source, or an order type; disabling a test;
changing the direction-aware rounding law; changing the journal's append-only property; enabling
`POST_ONLY`, online learning, or a second venue.

---

## 6. Register maintenance (`AX-18:§6`)

- Ids are append-only and never reused; ADRs are dated and attributed.
- A quarterly review (AX-12 §7.5 `RB-20`) reads the register and asks of each ADR: does the context
  still hold? An ADR whose context has died is superseded — the register is a living record of *why*,
  and its value is precisely that the reasoning is not reconstructed from memory afterwards.
- The register's length is not a problem; duplicated reasoning is. Every ADR must be reachable from the
  clause it governs (`cited by` in AX-15; clause footnotes elsewhere would be Class-1 edits).
