# APEX_GEN6 — Bounded GEN5 Learning Brief

**Prepared:** 2026-10-10  
**Purpose:** compact, provenance-aware context for an independent APEX_GEN6 design.  
**Status:** secondary learning aid; not a GEN6 specification, not a complete GEN5 archive, not a fresh audit, and not authorization to implement or trade.

## How to use this brief

Read this file **only after recording an independent first-principles design checkpoint** based on the owner’s task and fixed constraints. It is intended to convey transferable experience, verified owner boundaries, evidence limitations, and a few high-value operational observations without importing GEN5’s architecture as a template.

Do not follow links or open additional GEN5 materials automatically. If a particular design decision depends on a specific historical claim, identify the exact claim and source first; then request or inspect only the smallest relevant source excerpt. Do not claim full review of GEN5, its audit, its code, or its historical conversation from this brief.

## Owner’s fixed design envelope

The owner’s current instruction establishes these as constraints for the GEN6 baseline:

- Cryptocurrency markets only.
- Futures only; not spot or other asset classes.
- Toobit only as the trading exchange/integration in the baseline.
- Initial implementation, setup, execution, and first use are to be on the owner’s own phone. A VPS or cloud environment must not silently replace this requirement.
- Do not lower functionality, quality, evidence standards, or safety silently to fit the phone. First seek a credible solution within the constraints. If a material limitation remains, describe it explicitly and give a conditional alternative only for the affected capability; any relaxation requires the owner’s explicit decision.
- No design document, simulation, or historical test grants permission for LIVE trading or use of real capital.
- Never request, expose, or transfer the owner’s secrets, credentials, `.env`, or private database through GitHub or chat.

A prior owner ruling, D48, allowed public historical candle data for source-tagged RESEARCH/BACKTEST only, while PAPER/LIVE remained Toobit-only. The newer instruction “Toobit only” may be stricter and may restrict non-Toobit historical sources as well. Do not silently assume an exception: keep the baseline Toobit-only and flag the research-data interpretation if it materially affects the design. Do not integrate another exchange in the baseline.

## Device facts and unknowns

Historical records describe an Android phone and a GEN5 environment using Termux with an Ubuntu proot. These are historical environment facts, **not automatically mandatory GEN6 implementation choices**. The owner’s present requirement is phone-first; the exact software stack remains a design choice unless separately reaffirmed.

The records available for this brief do not establish the phone’s exact make/model, CPU, RAM, Android build, free storage, sustained thermal capacity, battery condition, or network performance. Do not invent or infer these values. A phone-feasibility claim needs either a measured device profile or an explicit minimum hardware envelope and a later on-device acceptance gate.

The following are dated GEN5 operational reports, not current device specifications or independently rerun benchmarks:

- A phone PAPER cycle was reported to take more than 7.5 hours with zero cells persisted.
- A performance comparison around 12.4 seconds versus 0.14 seconds was reported for a database-related path; raw profiling artifacts are not present in this workspace.
- Historical records report a phone database around 1.25 GB, 140 completed symbol/timeframe cells, and 485,591 QUALITY facts.
- E11 was reported by the owner as trained on phone at N=720 with 7,694 samples across 20 cells and accuracy 0.742007. The raw report/artifact is not available here for independent validation; this does not establish timeout/resume behavior or current performance.

These reports are useful warnings to measure end-to-end workload, persistence, restart behavior, and actual phone capacity. They are not proof that the current phone has the same state, nor a justification to remove features or relax design quality.

## GEN5 provenance and evidence boundaries

The public project repository identified by the owner is:

- Repository: https://github.com/sinamoosazadeh/Upstage
- Code/spec comparison baseline: `main@85b2c155d7b054a468379ddfd802eb239d0801f9`
- Pinned tree: https://github.com/sinamoosazadeh/Upstage/tree/85b2c155d7b054a468379ddfd802eb239d0801f9
- Original `APEX_GEN5.md` identity recorded in the source notes: 20,551 lines, SHA-256 `216bcc9e5f3e54c7567303bea7b642a9f5ccf482d2282d05dc78c2f7cb0fbd9e`.
- Amended working `main` identity recorded in the source notes: 20,983 lines, SHA-256 `493568887acb7164c985a0310809140ef3a6b3651e15d05782708b7f73e98569`.
- These are distinct design snapshots; do not conflate them.
- The source register reports 24 merged PRs through this main snapshot: #1–#23 and #25. PR #24 was superseded/unmerged and must not be counted as a separate merged delivery.

The third-party audit is on a different branch:

- Report v26: https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e2f1-upstage/AUDIT/APEX_GEN5_AUDIT.md
- Index: https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e2f1-upstage/AUDIT/APEX_GEN5_AUDIT_INDEX.md

Historical source notes report 392 audit rows/hypotheses across families A–R; verifier summaries report 346 CONFIRMED, 46 PARTIAL, zero REJECTED, plus 16 cross-findings whose membership in the 392 is unresolved. These are not 392 unimplemented features, 392 approved fixes, or a fresh review. `D64–D89` are recorded as proposals without an owner ruling, not approved requirements.

Historical test counts, code-path observations, owner-reported device results, audit/verifier findings, and acceptance on a real phone/venue are different evidence classes. A sandbox PASS is not a phone/Toobit/PAPER acceptance result. A `CONFIRMED` finding is not proof that it was fixed. Do not report a historical claim as newly tested.

The two local companion files `APEX_GEN5_TO_GEN6_SOURCE_MATERIALS_REGISTER_2026-10-06.md` and `APEX_GEN5_POSTFREEZE_DISCOVERY_DELTA_INDEX_2026-10-06.md` were present as untracked files in the working Upstage checkout; they were not part of the pinned main snapshot. Their presence in any other repository, including `apex_library`, must be checked rather than assumed.

## Transferable lessons — principles, not a GEN6 blueprint

Use the following only as questions to test an independently formed design. They do not prescribe modules, algorithms, or architecture.

1. **A written requirement, a code path, an exercised caller, and an accepted operational result are distinct.** A design should make it possible to trace an important behavior through its actual production use and its acceptance evidence. Do not infer end-to-end behavior merely because a function, test, diagram, or specification clause exists.
2. **Data identity, time, provenance, corrections, and point-in-time availability can invalidate downstream conclusions.** Define the semantics needed by the chosen system and ensure they are consistent from source through decisions and reports. Do not import GEN5’s field names or identity scheme.
3. **Trading outcomes can be uncertain or partially observed.** A design should explicitly reason about persistence, idempotency, interruption, retries, recovery, and reconciling disagreements whenever those concepts apply. Do not copy GEN5’s particular FSM, ledger, or retry design.
4. **Local or synthetic tests prove only their tested scope.** State the environment, test oracle, data class, and exclusions. Treat phone, venue, multi-day PAPER, restore, and LIVE evidence as separate gates where relevant.
5. **Resource constraints must be measured at the system boundary that matters.** A microbenchmark or a passing unit test is not a substitute for the complete workload, persistence, restart, and sustained operation on the target phone. Do not turn old GEN5 timing claims into current capacity limits.
6. **Complexity and numeric rules need reasons.** Avoid adding a model, threshold, score, data field, or control simply because GEN5 had one. A number should have a defensible basis, explicit units/meaning, and a method for validation or calibration.
7. **Operations and human control are part of system quality.** Important states, refusals, failures, and required operator actions should be observable and understandable to the intended owner; keep owner approval and product requirements distinct from implementation convenience.
8. **Historical change and audit records can disagree or be incomplete.** Preserve snapshot identity, date, authorship/evidence type, proposal status, and unresolved source gaps. Do not merge identifiers or counts just because their names look similar.

Historical records also show substantial documentation, traceability, staged code delivery, and test effort. Treat those as useful process artifacts, not proof that the architecture was sound or the complete operational system was accepted. The central redesign opportunity is to choose the system from first principles and then use verified, transferable experience to challenge it—without inheriting GEN5’s structure.

## Recommended reading boundary for the receiving model

The project-learning source for GEN6 should be this curated brief, not the full Upstage repository. The receiving model should first form and record its independent design checkpoint, then read this file. It should not crawl the old design, all source code, all PRs, all 392 findings, all 15 V reports, or all probes by default.

If a specific claim in this brief becomes decisive, the model may request the exact underlying source excerpt or open the precise pinned source for that claim only. It must state what question the extra material answers and must not expand into a full GEN5 audit. Do not expose secrets, databases, or unapproved phone artifacts.