# AX-14 — Test, Verification and Release Gate Framework

**Status:** Normative. A test that is not listed here does not exist for acceptance purposes; a listed
test that does not run is a blocking defect.
**Upstream:** every document (each clause states its own obligations).
**Downstream:** the build pipeline, the promotion ladder (AX-10 §4), the release gates (§6).

---

## 1. Philosophy (`AX-14:§1`)

Correctness of a trading system is not "the strategy makes money in a backtest" — it is the conjunction
of four separable claims, each of which is verified by a different kind of test:

| Claim | Verified by |
|---|---|
| The code does what the documents say | unit, property and integration tests (§3) |
| The documents are right about the venue | the conformance harness (AX-02 §10) and `T-CONF-*` |
| The system is not fooling itself statistically | the statistical battery (AX-10 §3, `T-STAT-*`) |
| The system survives the real world | fault injection, parity, soak and drills (§4, §5) |

No gate may be passed on the strength of a *different* claim than the one it certifies
(`AX-14:§1-R1`). This is the rule that prevents "12 000 unit tests, therefore the strategy is good".

---

## 2. Test classes and their evidentiary weight (`AX-14:§2`)

| Class | Class id | Evidence class (AX-00) | Required for |
|---|---|---|---|
| Unit/property | `U` | `[D]` | every merge |
| Integration (real components, simulated venue) | `I` | `[D]` | every merge |
| Conformance (real venue, read-only or probe) | `C` | `[V-KIT]`/`[V-PROBE]` | every deployment, every `LIVE` session start |
| Fault injection | `F` | `[D]` | every release |
| Parity/decision-drift | `P` | `[D]` | every release, every promoted model |
| Statistical | `S` | `[D]` | every promotion |
| Soak/benchmark | `B` | `[D]` | every environment change, quarterly |
| Drill (human procedures) | `DR` | `[D]` (recorded) | before live, then per runbook cadence |

---

## 3. Test catalogue (`AX-14:§3`)

The following ids are the **mandatory minimum**; each document contributes its own list (AX-04 §11,
AX-05 §5, AX-06 §9, AX-07 §10, AX-08 §11, AX-09 §8, AX-10 §9, AX-11, AX-12 §12, AX-13). The ids below
are the consolidated, cross-cutting set that no single document owns.

### 3.1 Data plane (`AX-14:§3.1`)

| Id | Asserts |
|---|---|
| `T-QC-001`…`T-QC-020` | one test per quality gate `QC-01`…`QC-20` (AX-04 §3): each constructed input triggers exactly the documented action, and no other gate fires |
| `T-READY-001`…`T-READY-011` | one per readiness check (AX-04 §9): failure of check *k* ⇒ system stays `OFF`, and the report names the check |
| `T-REBUILD-001` | rebuild of one day of L1 from L0 yields digests identical to production |
| `T-REBUILD-002` | rebuild is deterministic across two runs on the same inputs |
| `T-CAP-001` | the capacity guard degrades in the documented order (AX-04 §7) and never drops L0 silently |
| `T-CAP-002` | retention deletion respects the journal's never-compacted rule |
| `T-UNI-001` | a universe change is removals-only intraday |
| `T-UNI-002` | the frozen-day universe is stable across restarts and processes |
| `T-DATA-004` | anti-survivorship: an instrument that later disappears appears in historical universes |
| `T-SNAP-001` | a snapshot digest mismatch between two processes ⇒ refusal to trade, not a warning |
| `T-BAR-002` | provisional bars are never used by a decision (PIT enforcement) |
| `T-REPAIR-001` | a detected gap is either filled with documented evidence or the series is marked permanently incomplete |
| `T-REPAIR-002` | repair never rewrites a bar used by a decision without a `CorrectionEvent` |

### 3.2 Signals, forecasts, risk (`AX-14:§3.2`)

| Id | Asserts |
|---|---|
| `T-FEAT-001` | every registered feature is reproducible from L0/L1 alone |
| `T-FEAT-002` | feature purity: no I/O, clock or RNG in the computational path |
| `T-LEAK-001` | a synthetic future-leaking feature is rejected by the admission pipeline |
| `T-LEAK-002` | purged/embargoed splits: no training row overlaps a test label |
| `T-ADM-002` | the multiple-testing correction changes the decision in a constructed case (i.e. it is really applied) |
| `T-REG-001` | the regime model is filtered-only (no future inputs) and its entropy gate works |
| `T-RISK-001` | `R` derivation reproduces AX-07 §3 for a table of inputs |
| `T-RISK-002` | the five sizing caps interact as documented; the binding cap is reported |
| `T-RISK-003` | the AX-07 §10 worked example reproduces exactly |
| `T-OPT-001` | the optimizer's solution satisfies every constraint and the post-hoc validator agrees |
| `T-TAIL-001` | the tail budget prevents a synthetic gap loss from exceeding the documented multiple of `R` |
| `T-LAB-001` | the label builder's cost terms match AX-08 at the time */
| `T-MDL-001` | a model with an uncalibrated output is refused (no `p_net`, no trade) |
| `T-MDL-002` | shrinkage formula (AX-06 §5) and its `M_eff` floor behave as documented |
| `T-COMB-001` | combination is deterministic and weight-clipped; `M_eff < M_eff_floor` ⇒ no trade |

### 3.3 Execution, governor, operations (`AX-14:§3.3`)

| Id | Asserts |
|---|---|
| `T-ID-002` | idempotency keys are unique per intent; reuse is refused at load |
| `T-PROV-002` | no `[V]` value in the config; `[C]` values carry a calibration ref |
| `T-CFG-001` | every config key exists, resolves, and records its source |
| `T-ARCH-001`…`T-ARCH-004` | import law, single writer, strict typing, no bare exception in order paths |
| `T-PIT-003` | a delayed record cannot be used before its availability time |
| `T-DET-001` | replay determinism (byte-identical decision stream) |
| `T-DET-002` | decision determinism across processes on the same snapshot |
| `T-PARITY-001`/`T-PARITY-002` | seam parity: no live-only or backtest-only code paths; identical decisions on identical tape |
| `T-SIM-001`/`T-SIM-002` | the kernel cannot distinguish venue implementations; report completeness |
| `T-EXE-001`…`T-EXE-003`, `T-COST-001`…`T-COST-004`, `T-AMB-001`…`T-AMB-006`, `T-PROT-001`…`T-PROT-004`, `T-RECON-001`…`T-RECON-007`, `T-EMER-001`…`T-EMER-003`, `T-TCA-001`/`T-TCA-002` | see AX-08 §11 |
| `T-PRETRADE-001`…`T-PRETRADE-026`, `T-GOV-001`…`T-GOV-004`, `T-KILL-001`…`T-KILL-010`, `T-OBS-001`…`T-OBS-003`, `T-DEADMAN-001` | see AX-09 §8 |
| `T-LRN-001`…`T-LRN-016` | see AX-10 §9 |
| `T-OPS-001`…`T-OPS-006`, `T-SEC-001`…`T-SEC-004`, `T-BACKUP-001`…`T-BACKUP-003`, `T-BENCH-01`…`T-BENCH-10` | see AX-12 §12 |
| `T-CONF-001`…`T-CONF-040` | one per `VCH` probe (AX-02 §10); a FAILED blocking probe forbids `LIVE` |
| `T-STAT-001`…`T-STAT-008` | DSR, PBO, SPA, MinTRL, bootstrap-CI calibration against published/synthetic references (AX-10 §3.4) |

*/ Note: `T-LAB-001` references the cost model version inside the label artifact; the assertion is that
the recorded version is the one the cost ledger would produce for that timestamp.

---

## 4. Property-based and adversarial testing (`AX-14:§4`)

1. **Quantization invariants** (Hypothesis): for random price/size/tick/step/band inputs, the quantized
   order is always within the venue's filters, and the rounding direction never increases risk
   (AX-03 §4.2).
2. **Kernel monotonicity:** for any candidate, lowering the risk budget never turns a `REFUSE` into an
   `ALLOW`, and raising the size never turns a `REDUCE` into an `ALLOW` (`T-KERNEL-MONO`).
3. **Ledger arithmetic:** `Σ fees + Σ funding + Δ equity = realised PnL` to within the venue's
   rounding, over random synthetic fill streams (`T-LEDGER-ID`).
4. **FSM completeness:** for every order state and every injected outcome, the transition table is
   total (a defined action exists) — no unhandled state (`T-FSM-TOTAL`).
5. **Redaction fuzz:** random key-shaped strings injected into every log/notification path never appear
   in output (`T-SEC-001`).
6. **Replay idempotency:** re-running the same tape with the same versions from a clean store yields
   identical decisions and identical journal *decision* records (`T-DET-001`).
7. **Interruption fuzz:** the process is killed at random points (every N events) during a paper run;
   after each restart, the system must reconcile and never duplicate an order (`T-FAULTKILL`).

---

## 5. Environment and dataset fixtures (`AX-14:§5`)

| Fixture | Contents | Used by |
|---|---|---|
| `FX-SMALL` | 3 instruments, 60 days of 15 m bars + trades + funding | unit, integration, fast property tests |
| `FX-REAL` | the full recorded archive to date (all instruments, all intervals) | statistical, benchmarks |
| `FX-GAP` | `FX-SMALL` with injected gaps, duplications, out-of-order records, a stale WS session | `T-QC-*`, repair tests |
| `FX-SCN` | the scenario suite fixtures of AX-11 §6 | fault injection, drills |
| `FX-DEGEN` | degenerate inputs: single bar, zero volume, all-zero variance, one instrument, empty universe | robustness; the system must refuse, not crash |
| `FX-XXXV` | a synthetic venue whose responses are drawn from the documented error catalogue | FSM, ambiguity, backoff tests |

`FX-XXXV` is *generated* from AX-02's error table, so a new venue fact automatically extends the tests
(`AX-14:§5-R1`).

---

## 6. Release gates (`AX-14:§6`)

Gates are cumulative and monotone: passing `Gn` implies all earlier gates passed on the same artifact
set (code hash + param hash + model hashes + profile hash). Records are stored as `GateRecord`s
(AX-10 §4.1) and referenced by hash in the deployment ledger.

| Gate | Name | Blockchain of evidence required | Blocks |
|---|---|---|---|
| **G0** | **Build** | static analysis, import law, typing, unit + property tests, config schema, contracts compile, `T-PROV-*`, `T-CFG-001` | everything |
| **G1** | **Data** | `T-QC-001…020`, `T-READY-001…011`, `T-REBUILD-001/002`, `T-CAP-001/002`, `T-UNI-001/002`, `T-DATA-004`, `T-SNAP-001`, `T-BAR-002`, `T-REPAIR-001/002` pass on `FX-GAP` and on the real archive | research results, simulation |
| **G2** | **Simulation** | integration suite, `T-SIM-*`, `T-SCN-*` (scenario suite via `FX-SCN`), `T-DET-001/002`, `T-PARITY-001/002`, report-completeness | promotion to `L2`/`L3` |
| **G3** | **Statistics** | `T-STAT-001…008`, `T-LEAK-001/002`, `T-ADM-002`, `T-LAB-001`, DSR/PBO/SPA artifacts on `FX-REAL` for the specific candidate | promotion to `L3`/`L4` |
| **G4** | **Risk** | `T-RISK-001/002/003`, `T-OPT-001`, `T-TAIL-001`, `T-MDL-*`, `T-COMB-001`, kernel monotonicity, tail scenario `S-SCN-GAP` | promotion to `L4`/`L5`, any risk-parameter change |
| **G5** | **Conformance** | `T-CONF-*` on the live month, blocking probes `PASSED`, `venue_profile.json` current, `T-VEN-*` fixtures, order-construct dry-run in `PROBE` | first `LIVE`, and each `LIVE` session start |
| **G6** | **Live-readiness** | soak benchmarks `T-BENCH-01…10`, drills `DR-01…DR-20` (AX-12 §7.5), backup/restore drill, single-writer test, kill drills, `T-FAULTKILL`, dead-man test, and the owner's explicit written authorisation | enabling `MICRO_LIVE`/`LIVE` |

**`AX-14:§6-R1` — Gate monotonicity:** a change to code, parameters, models or the venue profile
*invalidates* every gate whose evidence depends on it; the dependency map is explicit and machine-checked
(`T-GATE-001`).
**`AX-14:§6-R2` — No partial gates:** a gate is passed or not; "passed except for X" does not exist.
A failing test may be *waived* only by an ADR that changes the requirement — never by an operator
override.
**`AX-14:§6-R3` — Evidence expiry:** conformance (`G5`) evidence expires after `P-TST-001` days or on
any venue drift event; statistical (`G3`) evidence expires after `P-TST-002` months or on any model
change.

---

## 7. Continuous verification (`AX-14:§7`)

- CI runs `U`, `I`, and the fast property set on every commit; `S` and `B` run nightly; `C` runs daily
  in read-only mode and weekly with `PROBE` traffic; `F` and `P` run on a schedule and before every
  release.
- Any red test blocks the pipeline; the only escape is an ADR (never a skip mark in the code). A
  `@skip` decorator without an ADR reference fails the lint (`T-GATE-002`).
- Coverage floor `P-TST-003` % on decision-critical packages (`rg`, `exp`, `pfp`, `core`), with
  *branch* coverage on the kernel and the FSM (line coverage is not evidence for decision logic).
- Mutation testing (`P-TST-004` mutants per module, quarterly) on the kernel, the cost gate, the
  rounding law and the journal chain: a surviving mutant is a missing test (`T-GATE-003`).

---

## 8. Acceptance definition (`AX-14:§8`)

The system is **accepted** when, on a frozen artifact set: `G0…G6` all pass with stored evidence; the
owner has read the current `AX-15` owner-input table and supplied every `[O]` value; the runbooks have
been drilled; and the owner has issued written authorisation that names the mode to be enabled.
**Acceptance is per artifact set.** Any subsequent change restarts the affected gates. There is no
state of "accepted forever".
