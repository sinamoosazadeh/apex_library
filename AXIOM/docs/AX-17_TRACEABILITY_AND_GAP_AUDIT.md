# AX-17 — Traceability, Coverage and Gap Audit

**Status:** Normative audit artifact. It is *evidence about the design*, not a new design.
**Upstream:** all documents. **Downstream:** the owner's acceptance decision.

Purpose: prove that (a) every owner constraint and axiom is discharged by named clauses, (b) every
clause is discharged by named tests, (c) nothing in the suite is decoration, and (d) every remaining
unknown is enumerated, owned, and has a defined behaviour that is safe while it stays unknown.

---

## 1. Owner constraints → clauses (`AX-17:§1`)

| Constraint (AX-00 §1) | Discharged by |
|---|---|
| C1 independence from the prior project | AX-00 no-inheritance clause; §6 below audits that nothing was imported as a template |
| C2 maximum achievable level | AX-01 §2 (capability ambition) with AX-01 §2.3 (admissible horizon), AX-16 §8 (honest limits); the design maximises *within stated physics* rather than promising beyond them |
| C3 use any method/tool/resource | AX-05 mechanism-based families; AX-10 protocol; AX-11 simulators; the design imports standard literature (ADR-014, ADR-015) rather than inventing privately |
| C4 no limitation of any kind | AX-00 §4 feasibility envelope: "no limitation" is implemented as *no self-imposed limitation* — physical, legal and venue limits remain, and are stated |
| C5 every character justified | AX-01 §1 authority model + AX-15 §0-R1 (no unregistered numbers) + AX-16 §6-R1 (no open questions in a started package) |
| C6 independent of the prior audit | AX-00 §3 evidence classes; AX-02 re-derives venue truth; §6 below |
| C7 zero gaps | §4 of this document (gap register) + AX-16 §6-R1 |
| C8 Toobit futures | AX-02 (venue truth, one venue), ADR-001, ADR-011 (research-only external data) |

---

## 2. Axioms → clauses → tests (`AX-17:§2`)

| Axiom (AX-00 §2) | Primary clauses | Primary tests |
|---|---|---|
| A1 No free lunch / cost-first | AX-08 §3, §3.4; AX-06 §2.1 | `T-COST-001`…`004`, `T-LAB-001` |
| A2 Truth is sampled, not declared | AX-04 §3, §8; AX-02 §10 | `T-QC-001`…`020`, `T-CONF-001`…`040`, `T-REPAIR-001/002` |
| A3 Time is an instrument | AX-03 §3; AX-11 §2 | `T-PIT-003`, `T-BAR-002`, `T-CLOCK-*` |
| A4 Uncertainty is the raw material | AX-06 §3; AX-08 §3.3 | `T-MDL-001`, `T-COST-002`, `T-STAT-*` |
| A5 Rare events dominate | AX-08 §5, §6, §9; AX-09 §5 | `T-AMB-001`…`006`, `T-PROT-*`, `T-EMER-*`, `T-KILL-*` |
| A6 Horizon–latency coupling | AX-08 §2 (budget numbers); AX-01 §2.3 | `T-BENCH-05`, `T-VEN-*` |
| A7 Refusal is a position | AX-06 §7; AX-09 §6.3 | `T-PRETRADE-*`, `T-OBS-001` |
| A8 Operations are design | AX-12 (whole) | `T-OPS-*`, `T-BACKUP-*`, `T-BENCH-01…10` |
| A9 Statistical honesty | AX-10 §3; AX-14 §6 | `T-STAT-001…008`, `T-LEAK-001/002`, `T-LRN-005…008` |
| A10 One kernel, many substrates | AX-11 §1/§5; AX-13 §4.8 | `T-PARITY-001/002`, `T-SIM-001`, `T-DET-001/002` |

Any axiom without a passing test in the current artifact set means the artifact set is not accepted
(`AX-14:§8`).

---

## 3. Document → obligation → verification (`AX-17:§3`)

| Document | Owns | Verified by |
|---|---|---|
| AX-00 | constraints, axioms, evidence classes, feasibility | this document + the owner's acceptance |
| AX-01 | authority, planes, invariants | `T-ARCH-001…004`, `T-PROV-002` |
| AX-02 | venue truth, conformance | `T-CONF-*`, `T-VEN-*`, `T-CLOCK-*` |
| AX-03 | objects, ids, time, numeric law | `T-ID-*`, `T-PIT-*`, `T-DET-*`, `T-KERNEL-MONO` |
| AX-04 | data plane | `T-QC-*`, `T-READY-*`, `T-REBUILD-*`, `T-CAP-*`, `T-UNI-*`, `T-SNAP-001`, `T-REPAIR-*` |
| AX-05 | signals | `T-FEAT-*`, `T-ADM-002`, `T-LEAK-*`, `T-MON-*` |
| AX-06 | forecast/state/combination | `T-MDL-*`, `T-COMB-001`, `T-REG-001`, `T-CAL-*` |
| AX-07 | risk/sizing | `T-RISK-001/002/003`, `T-OPT-001`, `T-TAIL-001`, `T-MRG-*` |
| AX-08 | execution/cost | `T-EXE-*`, `T-COST-*`, `T-AMB-*`, `T-PROT-*`, `T-RECON-*`, `T-TCA-*` |
| AX-09 | governor/kills | `T-PRETRADE-*`, `T-GOV-*`, `T-KILL-*`, `T-DEADMAN-001` |
| AX-10 | learning/promotion | `T-LRN-*`, `T-STAT-*` |
| AX-11 | simulator/parity | `T-SIM-*`, `T-PARITY-*`, `T-DET-*`, `T-SCN-*` |
| AX-12 | ops/security | `T-OPS-*`, `T-SEC-*`, `T-BACKUP-*`, `T-BENCH-*` |
| AX-13 | interfaces/events/config | `T-CFG-001`, `T-ARCH-005`, schema tests |
| AX-14 | gates | `T-GATE-001…003` |
| AX-15 | parameters | `T-PROV-002`, `T-CFG-001`, `T-ARCH-005` |
| AX-16 | plan | DoD records per package |
| AX-18 | change law | ADR presence checks |

---

## 4. Gap register (`AX-17:§4`)

Two kinds of "gap" exist and they are treated differently.

### 4.1 Closed gaps (`AX-17:§4.1`)

Design questions that were open during authoring and are now decided *in the documents*: the venue's
wire version (ADR-006), the bar substrate (ADR-007), maker strategies (ADR-009), venue-side protection
(ADR-010), the covariance estimator (ADR-014), the statistical protocol (ADR-015), governor threshold
derivation (ADR-016), the tiered collection model (ADR-017), and the owner-input set (AX-15 §9).
No clause in the suite contains "TBD", "to be decided later", or "implementer's choice"; the audit
grep is `T-DOC-001` (a lint that greps the documents for forbidden phrases and fails the build).

### 4.2 Open venue unknowns (`AX-17:§4.2`) — the `AMB` register

These are facts about Toobit that public documentation does not settle. Each has a **safe behaviour**,
so none of them blocks the build; each is resolved by the conformance harness before `LIVE`.

| Id | Unknown | Safe behaviour while unknown | Resolved by | Blocks |
|---|---|---|---|---|
| `AMB-01` | tick/step/min-notional precision edge cases and quantization rules | fail-closed: refuse any order whose quantization is ambiguous; direction-aware rounding (AX-03 §4.2) | `VCH-05/06` | live order placement |
| `AMB-02` | whether WS push flags (taker side in kline pushes) are reliable | AX-05 `F-TAKER` derives the taker split from **REST klines** only; WS flags are unused | `VCH-31` | nothing (feature is designed around it) |
| `AMB-03` | exact liquidation-fee and maintenance-margin formula per tier | use the published table if available, else the conservative `mnt + fee` upper bound; the tail budget absorbs the difference | `VCH-24` | full-size live |
| `AMB-04` | behaviour of protective-order replacement semantics | always place new → confirm → cancel old (AX-08 §6.3) | `VCH-22` | nothing |
| `AMB-05` | whether a user-data/listenKey stream exists | REST reconciliation only; no dependency on user WS | `VCH-33` | nothing |
| `AMB-06` | exact scope of `DELETE /batchOrders` with respect to protective orders | never rely on it; confirmed cancels only | `VCH-22` | nothing |
| `AMB-07` | rate-limit interaction between weight and request-count limits under bursts | the P0–P3 prioritisation and `f_safe = 0.5` (AX-02 §7) | `VCH-15` | nothing |
| `AMB-08` | whether STOP orders trigger on MARK or LAST by default when `triggerBy` is omitted | **always send `triggerBy` explicitly** | `VCH-23` | nothing |
| `AMB-09` | index-composition changes (`edp` list) and their effect on basis features | basis features are T2 and shrink to zero when composition changes are detected | `VCH-35` | basis sizing |
| `AMB-10` | funding-rate settlement exact timestamps | read `nextFundingTime`; if inconsistent with realised cash flows, treat funding as uncertain and increase the cost band | `VCH-25` | nothing |
| `AMB-11` | whether `-1141` (duplicate `clientOrderId`) can fire for a *different* intent | keys are unique per intent; on `-1141` the system resolves by query before any new key | `VCH-08` | nothing |
| `AMB-12` | limits on concurrent working orders per symbol under volatility (dynamic throttling, e.g. `-1207`) | cap working orders at `P-EXE-040` (≤3) and treat any throttling error as a deferral with backoff | `VCH-16` | nothing |

**Rule (`AX-17:§4.2-R1`):** an `AMB` that is still open at `LIVE`-arming time keeps its safe behaviour
*and* is disclosed in the arming record. No `AMB` may be "closed by assumption".

### 4.3 External unknowns (`AX-17:§4.3`)

| Id | Unknown | Handling |
|---|---|---|
| `EXT-01` | the owner's execution device and its measured limits | `BENCH-01…10` produce the numbers; topology chosen by `OI-OPS-01`; no silent degradation |
| `EXT-02` | the owner's capital and risk appetite | `OI-RISK-*`; system stays `OFF` without them |
| `EXT-03` | the owner's notification channel | `OI-OPS-02`; no `LIVE` without it |
| `EXT-04` | whether historical external (cross-venue) data may be used for *research only* | ADR-011 restricts use to regime/beta context, never execution, never signals on Toobit prices; if the owner forbids even that, the affected features (cross-venue family) are simply not enabled — the rest of the system is unaffected |
| `EXT-05` | future venue changes (fees, tiers, instruments) | drift detection + conformance re-run + ADR |

---

## 5. Coverage audit (`AX-17:§5`)

| Question | Answer |
|---|---|
| Is there a clause with no owner? | No: §3 assigns every document; within documents, clause ids carry their number. |
| Is there a test with no clause? | No: AX-14 §3 and per-document test tables all cite their clauses. |
| Is there a parameter with no citation? | No: AX-15 §1 requires `cited by`; `T-ARCH-005` enforces. |
| Is there a component with no test obligation? | No: every module in AX-13 §2 has tests in AX-14 §3. |
| Is there a gate with no evidence list? | No: AX-14 §6. |
| Is there a decision with no rule? | No: §4 rules cover action, refusal, escalation, and recovery for every state machine (kernel, FSM, governor, kills, promotion). |
| Is any number unexplained? | No: AX-15 with classes and derivations; `[V]` values come from the harness. |
| Could an implementer still need to ask something? | Only the `OI-*` inputs (AX-15 §9) and the `AMB-*` facts, both of which have defined safe fallbacks — so a build can proceed and a live launch cannot happen by accident. |

---

## 6. Independence audit (`AX-17:§6`)

| Prior-project artifact | Used how | Evidence of non-inheritance |
|---|---|---|
| `APEX_GEN5.md` (blueprint, 20 983 lines) | read for *lessons* (L1–L8) and for the list of weaknesses to avoid | no engine, layer, naming scheme, or module boundary of AX-* corresponds to E01–E12 or the GEN5 engine list; AX-01's plane set (`vap/mdp/sfp/fcp/pfp/exp/rg/lnp/cop`) has no counterpart in GEN5 |
| `coding.patch` / CP-1…CP-8 | read to learn that the prior project stopped before implementation | AX-* specifies contracts and gates independent of any prior patch structure; no AX clause references CP-* |
| GEN5's data-quality and PIT chapters | consulted as one input among several | AX-03/AX-04 derive their own laws (five clocks, `TapeCursor`, `QC-01…20`, digest snapshots) with explicit test ids; where GEN5 said "check freshness", AX-04 states how, with what threshold class, and what happens on failure |
| The prior gates `G-TOOBIT-001/002/003` | ignored as gates | AX-02's `VCH-01…40` harness replaces them wholesale; every venue fact is re-derived from the official docs/kit and re-verified by probe |
| Prior Telegram/checklist material | consulted for the operator's real habits | AX-12's operator surface is derived from the requirement "one screen, one action to stop, no urgent action ever required" (AX-12 §7.1), not from the prior checklist |

**Conclusion:** the suite is a re-derivation from axioms and verified venue facts. Where it agrees with
the prior project, it is because the underlying mathematics or the venue agrees — not because the
structure was copied.

---

## 7. Standing audit obligations (`AX-17:§7`)

1. `T-DOC-001` (forbidden-phrase lint) runs on every document change; `T-DOC-002` verifies the
   non-normative boundary of `research/` (ADR-026/ADR-027) — the research layer may never become a
   source of requirements.
2. The traceability tables above are regenerated on every change to AX-14 (tests) and AX-15
   (parameters); a missing link fails the build (`T-GATE-001`).
3. Every `AMB` transition (open→resolved) updates AX-02 §11, this register, and the arming record.
4. Any new document, clause family, or gate requires an ADR (AX-01 §5.5).
