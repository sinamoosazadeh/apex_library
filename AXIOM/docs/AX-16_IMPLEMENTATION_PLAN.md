# AX-16 — Implementation Plan (WBS, Sequence, Definition of Done)

**Status:** Normative for sequencing and acceptance of work packages.
**Upstream:** all design documents; AX-14 (gates); AX-15 (parameters).

The plan is written so that a builder who has never seen this conversation can start on any work package
and know: its inputs, its outputs, its proof of completion, and what it must not do.

---

## 1. Sequencing law (`AX-16:§1`)

1. **No work package may start before its dependencies are *accepted*** (not merely written). Acceptance
   is the gate record of AX-14 §6.
2. **Nothing may be built out of order to "get something running"** except the vertical slice of §7.3,
   which exists precisely to make the first executable path safe (paper only).
3. **Every package ends with tests from AX-14** and a `DoD` record (Definition of Done, §2).
4. **Every package has an owner-input dependency list**; if an `OI-*` is missing, the package's
   dependent *capability* stays disabled — the package itself still completes.

---

## 2. Definition of Done (`AX-16:§2`)

A work package is done when: (a) the code is merged behind its interface contract (AX-13);
(b) all AX-14 tests for its tier are green; (c) parameters used are all in the registry;
(d) documentation clauses it implements are cited in the code (docstring `# AX-nn:§m`);
(e) the relevant gate artifacts are produced; (f) a reviewer who did not write it can run it from the
README's instructions; (g) any deviation is recorded as an ADR. **"Works on my machine" is not a DoD
element; a container/Termux-runnable script is.**

---

## 3. Workstreams (`AX-16:§3`)

| WS | Name | Packages | Depends on | Primary gates |
|---|---|---|---|---|
| `WS-0` | Skeleton & contracts | `WP-000` repo/build, `WP-001` core types/ids/hashing/clock, `WP-002` config+registry loader, `WP-003` journal+redaction, `WP-004` CLI skeleton, `WP-005` contracts (config/sql/schemas) | — | `G0` |
| `WS-1` | Venue access | `WP-010` HTTP client+signer+rate governor, `WP-011` clock sync, `WP-012` classifier+retry/backoff policy, `WP-013` conformance harness (all `VCH` probes), `WP-014` WS client (market streams), `WP-015` `venue_profile.json` producer | `WS-0` | `G0`, `G5` |
| `WS-2` | Data plane | `WP-020` collectors (HOT/WARM), `WP-021` `Gatekeeper` (QC-01…20), `WP-022` L0 store, `WP-023` L1 store + `TapeCursor`, `WP-024` universe builder, `WP-025` snapshot builder, `WP-026` health monitor, `WP-027` repair engine, `WP-028` retention/capacity guard, `WP-029` readiness checks | `WS-1` | `G1` |
| `WS-3` | Signals | `WP-030` registry/scaling/clip, `WP-031` trend+vol families, `WP-032` liquidity/microstructure, `WP-033` flow/carry, `WP-034` cross-section, `WP-035` calendar/seasonality, `WP-036` admission pipeline (marginal information, FDR, sample size) | `WS-2` | `G1`, `G3` |
| `WS-4` | Forecast/state | `WP-040` labels (net-return, triple barrier, uniqueness), `WP-041` M1 ridge + HAC + bootstrap, `WP-042` calibration (cross-fit + isotonic + Brier), `WP-043` M2 bounded GBM + admission, `WP-044` HMM/CUSUM regime layer, `WP-045` combination + shrinkage + trade gate | `WS-3` | `G3`, `G4` |
| `WS-5` | Portfolio/risk | `WP-050` covariance chain, `WP-051` clustering + HRP/inverse-variance, `WP-052` constrained QP + validator, `WP-053` five sizing caps + `R` derivation, `WP-054` stops + tail budget, `WP-055` leverage/margin/liquidation law, `WP-056` targets + turnover/no-trade band | `WS-4` | `G4` |
| `WS-6` | Execution | `WP-060` planner (bounds/slicing), `WP-061` order manager + FSM + ambiguity ladder, `WP-062` protection manager, `WP-063` reconciler, `WP-064` cost ledger + TCA, `WP-065` emergency flatten | `WS-5`, `WS-1` | `G4`, `G5` |
| `WS-7` | Governor & ops | `WP-070` risk kernel (RK-01…25), `WP-071` governor state machine + triggers + dwell/recovery, `WP-072` kills `K1…K8`, `WP-073` escalation/notifier, `WP-074` supervisor/heartbeat/watchdog, `WP-075` backup/restore, `WP-076` status view + runbooks | `WS-6` | `G4`, `G6` |
| `WS-8` | Learning | `WP-080` dataset builder (survivorship-free, purged/embargoed), `WP-081` simulator (fills/paths/failures), `WP-082` replay engine + determinism, `WP-083` stats (DSR/PBO/SPA/MinTRL/bootstrap), `WP-084` promotion gates + registry, `WP-085` drift monitor | `WS-2`, `WS-4` | `G2`, `G3` |
| `WS-9` | Verification | `WP-090` test harness + fixtures (`FX-*`), `WP-091` property/adversarial suites, `WP-092` fault-injection scenarios, `WP-093` parity harness, `WP-094` benchmark scripts `BENCH-01…10`, `WP-095` drills `DR-01…20` | parallel with all | all gates |

---

## 4. Critical path (`AX-16:§4`)

```
WS-0 → WS-1 → WS-2 → WS-3 → WS-4 → WS-5 → WS-6 → WS-7 → G6 → LIVE
                              ↘ WS-8 ↗ (needed from WS-2 onward)
                     WS-9 (continuous, starts with WS-0)
```

Facts that follow, and that the plan respects:
- **Data history accumulates in parallel with development** (`WP-020` starts as early as possible and
  runs continuously) — history is the one resource that cannot be bought later (L5).
- **The simulator (WS-8) is not the last step**: it is required for `G2`, which gates every research
  result, and it must exist before signals can be *validated*, not before they are written.
- **WS-9 is not a phase**: a test harness written after the code is a test harness that tests what the
  code does, not what the design says.

---

## 5. Milestones (`AX-16:§5`)

| Milestone | Contents | Exit criterion |
|---|---|---|
| `M0 — Skeleton` | `WS-0` complete; repo builds; config loads; journal chains; CLI `status` works with a stub | `G0` pass with report |
| `M1 — Truth` | `WS-1` complete; every `VCH` probe implemented; profile produced; WS streams live | `G0`+`G5` (read-only) pass; conformance report lists every unresolved `AMB-*` |
| `M2 — Data` | `WS-2` complete; ≥ `P-DATA-*` days of continuous collection with zero unexplained gaps | `G1` pass on the real archive |
| `M3 — Signals` | `WS-3` complete; admission pipeline runs end-to-end | `G1`+`G3` (feature-level) pass |
| `M4 — Forecast` | `WS-4` complete; a fallback model (the always-available `M0`: no forecast ⇒ no trade) drives a paper day | `G3` pass for `M1` ridge |
| `M5 — Risk` | `WS-5` complete; sizing/targets reproduce AX-07 §10 | `G4` pass |
| `M6 — Execution` | `WS-6` complete; paper venue + real read-only venue in `SHADOW` | `G2`+`G4` pass; scenario suite green |
| `M7 — Safe operation` | `WS-7` complete; governor/kills/drills | `G6` pass (except the owner's authorisation) |
| `M8 — Promotion` | `WS-8` complete; first candidate through `L2`→`L4` in shadow/paper | `GateRecord`s exist for `L3`, `L4` |
| `M9 — Micro-live` | owner authorisation, `PROBE` verified, armed | `G6` complete; written authorisation recorded |

---

## 6. Effort and work-package template (`AX-16:§6`)

Each package specification (a short document per `WP`) contains exactly:

```
WP-id, title
Purpose                 (1–3 sentences, in terms of the design clause it implements)
Inputs                  (artifacts/interfaces it consumes — with AX-13 names)
Outputs                 (modules/classes/interfaces it produces — with AX-13 names)
Clauses implemented     (explicit list, e.g. AX-04:§3, AX-08:§5.2)
Parameters used         (AX-15 ids only)
Tests required          (AX-14 ids; a package with no tests is refused)
Fixtures and data       (AX-14 §5)
Failure modes handled   (with the test that proves each)
Out of scope            (explicit; this is where "no guessing" is enforced)
DoD checklist           (§2)
Open questions          (must be empty at start; anything here blocks the package)
```

**Estimation rule:** effort is estimated only after the package specification is written and reviewed;
the estimate is recorded in the plan artifact. Estimates are for sequencing only and are not part of
acceptance. `AX-16:§6-R1` — a package whose specification still contains an open question **cannot be
started**: that is precisely the "coders must not guess" requirement, made enforceable.

---

## 7. First executable slice (`AX-16:§7`)

### 7.1 Purpose (`AX-16:§7.1`)

To have, as early as possible, a *complete vertical* of the safest path — read → decide → refuse/act in
`PAPER` — so that integration risk is discovered in week one rather than at the end. It contains no
alpha: its strategy is "always refuse". That is not a placeholder; it is a permanent, valid system state
(the system may legitimately trade nothing for as long as it takes).

### 7.2 Contents (`AX-16:§7.2`)

`WP-000`, `WP-001`, `WP-002`, `WP-003`, `WP-004`, `WP-010` (read-only routes only), `WP-011`,
`WP-012`, `WP-020` (bars only), `WP-021` (QC gates on bars), `WP-022`, `WP-023` (bars),
`WP-024`/`WP-025` (minimal), `WP-026`, `WP-060` (no-op planner), `WP-061` (paper adapter only),
`WP-070` (RK subset needed for a refusal), `WP-073` (console notifier), `WP-090` (harness).
Deliverable: `axiom run --env PAPER` produces a daily decision record containing refusals with reasons,
zero orders, and a status view.

### 7.3 Forbidden in the slice (`AX-16:§7.3`)

No live credentials; no signed calls; no orders; no `LIVE` mode reachable (the mode enum value exists but
the binary refuses to enter it without `G6` evidence — enforced in code, `T-OPS-006`).

---

## 8. Risk register (`AX-16:§8`)

| Risk | Impact | Mitigation (already in the design) |
|---|---|---|
| Venue facts change silently | orders rejected or mispriced | conformance harness + drift detection + fail-closed kernel (`RK-08`, `EV-VENUE-DRIFT`) |
| Data history too short for statistics | cannot promote anything honestly | start collection immediately; the honest answer may be "no trades yet" (allowed and expected) |
| Phone/device limits | capability unavailable | benchmarks with explicit pass/fail; no silent degradation (AX-12 §1-R2, §2) |
| Overfitting under pressure to trade | capital loss | pre-registration, DSR/PBO, ladder rungs, time budgets (AX-10) |
| Single operator unavailable | unprotected or stuck state | venue-side protection, dead-man defaults to stricter (AX-09 §6.4) |
| Scope creep into HFT/MM | the design's latency assumptions break | non-goals are binding (AX-01 §2); ADR required to change |
| Key compromise | capital loss beyond risk budget | no withdrawal permission, IP whitelist, rotation, redaction, `SEV-1` path |

---

## 9. What the implementation team must not do (`AX-16:§9`)

1. Do not invent parameters, thresholds, or defaults: every number has an AX-15 id.
2. Do not add features, signals, order types, venues or data sources not in AX-05/AX-13 without an ADR.
3. Do not add a retry, a cache, or a "just in case" branch in a decision path: each of these changes the
   system's decision function and must be designed (`AX-01:§5.4`).
4. Do not implement live behaviour behind a flag "for later testing" without the gate that authorises it.
5. Do not fix an ambiguity by choosing the convenient interpretation: raise it; the answer becomes an
   ADR and the affected document changes first (`AX-01:§5`).
6. Do not delete tests to make a build green; delete the *requirement* by ADR if it is wrong.
