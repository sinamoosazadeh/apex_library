# APEX_GEN5 → APEX_GEN6 Source Materials Register

**Prepared:** 2026-10-06  
**Purpose:** inventory the durable records, GitHub artifacts, lists, decisions, audits, code-change waves, and known gaps that a successor model must receive before redesigning APEX_GEN5 as APEX_GEN6. This is a source map and extraction checklist, **not** the Gen6 design and **not** authorization to implement changes.

## 1. Completeness statement and counting rules

The conversation history has been condensed more than once. The surviving dossier and session ledger explicitly mark details that were lost, and the uploaded `.patch` is only a documentation diff—not the complete project history. Therefore no honest reviewer can guarantee that this index contains every chat-only item unless the owner compares it against an export of the original conversation. This register is the most complete inventory supported by the persisted local files and read-only GitHub checks made on 2026-10-06; it labels what remains unknown rather than filling gaps by inference.

Use separate counts for separate kinds of material. Do **not** add audit rows, report files, cross-findings, decisions, PRs, and code stages together as if they were disjoint bug counts.

| Item being counted | Count visible in the records | Meaning and limit |
|---|---:|---|
| Merged GitHub pull requests through `main@85b2c155d7b054a468379ddfd802eb239d0801f9` | **24** | PRs #1–#23 plus #25 are shown as merged. PR #24 is superseded/unmerged; its work was transported through #25 and must not be counted as an additional merged delivery. Some PRs are planning/design documentation, not code fixes. |
| Third-party audit | **1 report, 392 rows** | Report version 26, families A–R. The report itself calls its rows hypotheses and describes scope limitations. |
| Numbered independent verification rounds | **9 rounds: V1–V9** | This is the high-level round count, not the number of Markdown files or necessarily the number of distinct accounts. |
| Verification report files | **15** | V1a–V1e (5), V2 (1), V3/V3b/V3c (3), V4–V9 (6). Each report’s probes are separate files/directories. |
| Cross-findings | **16 X-findings reported** | The persisted summary does not settle whether these are inside or in addition to the audit’s 392 rows. Preserve their individual IDs and do not silently add them to 392. |
| Planning-agent error/lesson register | **IDs #1–#49 are referenced** | The surviving text is incomplete: the ledger says #1–#21 and #24–#28 lost detail; the ledger preserves summaries for some later IDs; #48–#49 appear in the site-memory dump but are absent from the ledger’s #1–#47 register. The original chat is needed for a complete verbatim list. |
| Owner decision IDs | **D1–D63 recorded; D64–D89 = 26 proposals** | D37–D45 are specifically recorded as missing/lost in the available log. D64–D89 were proposed and unruled in the ledger snapshot; they are not 26 approved or implemented fixes. |
| Initial implementation stages | **CP-1…CP-8** | The original Rev-3 plan defines eight serial stages. Later merged history continues through CP-9 and CP-10…CP-14.6. There is no single safe “number of bug-fix sets” derivable by counting those labels. |
| Explicit design identities | **At least 2** | Original frozen blueprint and post-CP-14.6 amended working blueprint have different hashes and line counts. An intermediate hash is also recorded. See §3. |

### What is not currently evidenced

The saved records describe a proposed **approximately 210-row cross-verification by six agents** as an open question, not a completed run. The accessible report set contains nine numbered V rounds and 15 report files. No separate completed “more-than-nine-agent” audit round or result package was identified in the saved records or under `AUDIT/` at any of the 46 current public branch tips checked. If the owner remembers a later supplementary round, treat that as a **specific search target** in the original chat export, other possible paths, historical/deleted branches, or private artifacts—not as either disproven or already captured.

## 2. Identifier key: keep the different lists separate

| Prefix/form | What it labels | Do not confuse it with |
|---|---|---|
| `CP-1`…`CP-8`, later `CP-9`…`CP-14.6` | Implementation stages, hotfixes, handoffs, and closeouts. | Independent audits or owner decisions. |
| `D1`…`D63`, proposed `D64`…`D89` | Owner decision IDs and later proposal IDs. | Audit row numbers or proof that a code change landed. |
| `ADR-P2-*`, `ADR-SESSION-A`, `ADR-CP14-*` | Formal pre-adjudications/design or implementation decision records. | The audit’s finding verdicts. |
| `ISSUE-*` / `ISSUE-CP*-*` | Project issue/bug tracking IDs and dispositions. | A one-to-one count of unique defects; issues can reference several audit rows and PRs. |
| `A-001`…`R-*`, `K-*`, `L-*`, `P-*`, `Q-*`, etc. | Third-party audit and V-report finding IDs. Families A–R are not engine names. | `E01`…`E12` engine names. In particular, audit rows `E-001` and engine `E01` are different namespaces. |
| `V1a`…`V9`, `X-V*` | Verification reports/rounds and cross-findings. | New product requirements. |
| `T-*`, `FIX_*`, `GF_SC_*`, `AI.10`, `AI.13`, `G-*` | Test IDs, fixtures, blueprint acceptance requirements, and external gates. | Results: a planned test or a blank matrix cell is not evidence that it ran. |

For Gen6 source records, preserve each finding as its own row even if several reports repeat it. Link repeated IDs across sources instead of merging them.

## 3. Blueprint identity and design-change sources

Both design snapshots and the exact intervening changes must be supplied. The local Rev-3 files sometimes use the original hash where later main-branch records use the amended one.

| Artifact | Identity / location | What the successor needs it for | Caution |
|---|---|---|---|
| Original frozen `APEX_GEN5.md` | 20,551 lines; SHA-256 `216bcc9e5f3e54c7567303bea7b642a9f5ccf482d2282d05dc78c2f7cb0fbd9e`; local snapshot in this workspace and in the dossier’s Appendix B. | Preserve the original frozen design as the comparison baseline. | Do not call this the post-CP-14.6 working hash. |
| Amended working `main:APEX_GEN5.md` | `main@85b2c155d7b054a468379ddfd802eb239d0801f9`; 20,983 lines; SHA-256 `493568887acb7164c985a0310809140ef3a6b3651e15d05782708b7f73e98569`. | The code-history comparison and owner amendment record refer to this working version. The full text and diff against the original are included in `APEX_GEN5_PROJECT_DOSSIER_2026-10-06.md` Appendix B. | It is an amended working design, not the original frozen bytes. The hash change is documented and must be explained, not described as either silent tampering or proof of correctness. |
| Intermediate post-CP-14.6 hash | `34e72c4ea3088e053cb33bf008511a9f5a0404734f28a7630359ff9c2bbd1a84`, recorded in the main CP9 handoff before CP-14.6-FIX. | Shows an intermediate point in the design amendment chain. | Compare the exact full diffs/receipt; do not skip straight from 216bcc to 493568 without retaining the intermediate record. |
| `docs/APEX_GEN5_frozen_216bcc.md` | 11-line identity/amendment receipt on main. | Records original, intermediate, and post-fix design hashes and the stated scope of amendments. | A receipt is not a replacement copy of the blueprint. |
| PR #17 and `HANDOFF_SESSION_A` | [PR #17](https://github.com/sinamoosazadeh/Upstage/pull/17); doc-only Session A design patch P1–P8 per D1–D20; detailed handoff embedded in `main:PHASE2_HANDOFF_CP9.md`. | Extract the original owner instructions/decisions D1–D20 and exact design-patch wording. | Do not infer an owner ruling beyond the recorded text. |
| `PROMPT.md`, `README.md`, and the owner’s written instructions | Main `PROMPT.md` retains the Chief-Engineer source record with a status note; `README.md` identifies original vs amended hash. The current session memory and both continuity files preserve additional owner rules. | Carry forward communication, scope, safety, change-control, and delivery requirements separately from product requirements. | The old `START EXECUTION` block naming the deleted/abandoned repository is explicitly superseded. Do not act on it. |

**Known identity inconsistency to preserve:** `PHASE2_SESSION_LEDGER.md` §2 pairs “20,983 lines” with the old `216bcc` hash. The dossier’s snapshot table, main amendment receipt, README, and CP-14.6 records pair 20,551/216bcc with the original and 20,983/493568 with the amended working file. Do not repeat the ledger’s mismatched pair as fact.

## 4. GitHub implementation/change history: PR register

A read-only GitHub pull-request listing showed 24 merged PRs through the main snapshot, and PR #25 explicitly says it supersedes #24. Read each PR page, its commits/diff, the corresponding filled handoff, and its test evidence. A title is a locator, not proof of exact behavior.

| PR | Scope locator and source | Classification / extraction note |
|---:|---|---|
| #1 | [Rev-3 plan: 16 control files, eight-stage serial execution, PROMPT status note](https://github.com/sinamoosazadeh/Upstage/pull/1) | Process/control-file revision, not a code defect fix. |
| #2 | [CP-1 Foundation + Feature Fabric + Engine Base](https://github.com/sinamoosazadeh/Upstage/pull/2) | First implementation stage and handoff. |
| #3 | [Owner PR page](https://github.com/sinamoosazadeh/Upstage/pull/3) | The page title is only a branch name; the owner’s PR comment identifies this as CP-2 E01–E03, with integration, handoff/matrix/decision-log updates, and ISSUE-CP2-001..016. Preserve the comment and commits, not just the title. |
| #4 | [CP-3 E04 Volatility, E05 FVG, E06 OrderBlock](https://github.com/sinamoosazadeh/Upstage/pull/4) | Engine implementation stage. |
| #5 | [CP-4 E07 RTM, E08 Wyckoff, E09 Trend](https://github.com/sinamoosazadeh/Upstage/pull/5) | Engine implementation stage. |
| #6 | [CP-5 E10–E12 and E07↔E12 integration](https://github.com/sinamoosazadeh/Upstage/pull/6) | Engine implementation/integration stage. |
| #7 | [CP-6 Context, Pattern, Setup, Playbook, Forecast, Decision, Risk](https://github.com/sinamoosazadeh/Upstage/pull/7) | Full downstream analysis/risk stage. |
| #8 | [CP-7 Execution, Ledger, Scheduler, Telegram, Alerts](https://github.com/sinamoosazadeh/Upstage/pull/8) | Runtime/execution stage; preserve the PR’s exact test record with its commit and distinguish it from owner-phone/venue acceptance. |
| #9 | [CP-8 Research/Governance/Ops and closeout](https://github.com/sinamoosazadeh/Upstage/pull/9) | Original Rev-3 closeout; later code and audit history came after it. |
| #10 | [CP-9 addendum: wiring, canonical mirror, docs, patch cleanup](https://github.com/sinamoosazadeh/Upstage/pull/10) | Post-CP-8 operational extension. |
| #11 | [Close ISSUE-CP9-006 with governed PAPER plan bridge](https://github.com/sinamoosazadeh/Upstage/pull/11) | Separate bridge change; preserve its bridge contract/tests. |
| #12 | [CP-10 Toobit public response unwrap and named error fail-closed](https://github.com/sinamoosazadeh/Upstage/pull/12) | Venue/API correction. |
| #13 | [CP-11 venue-adaptive, tail-aligned Toobit backfill](https://github.com/sinamoosazadeh/Upstage/pull/13) | Venue/backfill correction. |
| #14 | [CP-12 venue OHLC-hygienic backfill source](https://github.com/sinamoosazadeh/Upstage/pull/14) | Data-source/quality correction. |
| #15 | [CP-13 closed-bar law, frontier resume, partial-bar repair, drop-evidence persistence](https://github.com/sinamoosazadeh/Upstage/pull/15) | Data lifecycle/repair change. |
| #16 | [CP-13.1 close-time-vs-now repair guard, ISSUE-CP13-004](https://github.com/sinamoosazadeh/Upstage/pull/16) | Follow-up hotfix; keep separate from CP-13. |
| #17 | [Session A design patch P1–P8 per owner D1–D20](https://github.com/sinamoosazadeh/Upstage/pull/17) | Doc-only design/owner decision patch. |
| #18 | [CP-14 engine-context producer, E11 artifact, catch-up, PAPER account, staleness, CIRCUIT_OPEN](https://github.com/sinamoosazadeh/Upstage/pull/18) | First CP-14 implementation wave; read the full CP-14 handoff. |
| #19 | [CP-14.1 resumable bar-capped E11 training and exact-parity speedups](https://github.com/sinamoosazadeh/Upstage/pull/19) | Training/runtime performance stage; preserve exact-parity and device evidence separately. |
| #20 | [CP-14.2 D36 eight-class E11 fit with entropy/confidence validation](https://github.com/sinamoosazadeh/Upstage/pull/20) | Owner decision plus model/validation implementation. |
| #21 | [CP-14.3 D46 PAPER bootstrap P minimum and E11 validation/fit study](https://github.com/sinamoosazadeh/Upstage/pull/21) | Decision and validation stage. |
| #22 | [CP-14.4 D47 fit protocol/verdict, D49 mechanism, D48 record, fit-study changes](https://github.com/sinamoosazadeh/Upstage/pull/22) | Decision/implementation/test bundle; read handoff and owner-run evidence. |
| #23 | [CP-14.5 D49 recommendations, fit protocol, `catalog_events` params, release-gate evidence](https://github.com/sinamoosazadeh/Upstage/pull/23) | Correction to CP-14.4; do not collapse its distinct changed contracts into #22. |
| #24 | [CP-14.6 initial PR](https://github.com/sinamoosazadeh/Upstage/pull/24) | **Not merged; superseded by #25.** It records `theta_H=1.105878`, `quality_H_Q2=1.229880`, `quality_H_Q5=0.564415`; D50–D53/D59 work; two earlier full-suite runs at 3,040 passed; and D54–D58 as not implemented. Retain as provenance but do not count it as a separate merged delivery or as the final test count. |
| #25 | [CP-14.6 transport + CP-14.6-FIX](https://github.com/sinamoosazadeh/Upstage/pull/25) | Merged delivery superseding #24. PR body records the transported patch, D49 values, D50–D53/D59 changes, two 3,051-test runs, and remaining D54–D58 non-implementation. CP-14.6-FIX records D62/D63 and closes ISSUE-CP14-068, ISSUE-CP14-069, and ISSUE-CP14-072; ADR-CP14-033 records the accompanying design clarifications. It cites source patch `owner-evidence-cp146/01a0d4bf-faf2-7ceb-a29c-2aa583f06fc7.patch`, 249,174 bytes, SHA-256 `819d9ff5c19266e730eeb6ba288e29d810cd2993691975029ec1ad951fc7f052`. |

### Main-branch files that carry the implementation record

These are the filled main-branch historical records, not the short local templates contained in the 22-section patch:

| Main file / snapshot | Why extract it | Version warning |
|---|---|---|
| `PHASE2_HANDOFF_CP1.md`…`PHASE2_HANDOFF_CP8.md` | Filled, stage-specific delivered-file, interface, test, issue, deviation, run, and remaining-work records. | Use the exact line counts/hashes in the main manifest. Local root copies are short or blank templates and several differ byte-for-byte; they are not substitutes for main. |
| `PHASE2_HANDOFF_CP9.md` | 1,011-line post-CP-8 history. It contains CP-9 base, `HANDOFF_BRIDGE`, CP-10/11/12/13/13.1 hotfixes, Session A, CP-14, CP-14.1 through CP-14.6, D21–D63, phone acceptance, data changes, tests, issues, and transport records. This is the primary compact source for the later code-change waves. | Do not treat it as only “CP-9”; it is an appended history ledger. Preserve every subsection and its evidence boundaries. |
| Main `PHASE2_CHECKPOINT_STATUS.md` | 168-line actual historical board, CP-1…CP-8 and later CP-9/Session A/CP-14 records. | Local 88-line board is reset to PENDING and is not the main history. |
| Main `PHASE2_TRACEABILITY_MATRIX.md` | 666-line blueprint→component→test map with historical result entries (368 literal `PASS(` markers in the captured snapshot). | PASS markers are historical test claims; they do not establish owner-phone or venue acceptance. Local 66-line copy is mostly blank. |
| Main `PHASE2_DECISION_LOG.md` | 1,233-line record of ADR-P2, D1–D63, ADR-CP14, issues, dispositions, and planning-agent error entries. | Local patch copy is 54 lines and omits D1–D63. The older source line references in continuity materials must be mapped to this exact version. |
| Main `PHASE2_FINAL_REPORT.md` | 339-line CP-8 closeout report; records 2,553 tests and external-gate/status claims at its date. | Dated 2026-09-14; stale relative to CP-9…CP-14.6, later test counts, and the external audit. It is not a Gen5 final acceptance certificate. |
| `docs/APEX_GEN5_frozen_216bcc.md`, `README.md`, `PROMPT.md`, `params/*.yaml`, `tests/fixtures/*` | Hash receipt, run/config conventions, original authority text, governed parameters, and synthetic/golden fixtures. | These are part of the main tree and are individually listed with hashes in dossier §12/Appendix B. Fixtures are not owner-phone production data. |

The dossier §12 manifest lists **all 225 tracked paths** in `main@85b2c15` (174 Python paths) with hashes/byte counts/line counts. Appendix B embeds the main specification and non-code text/config/fixture sources. Python and shell bodies are not copied into the dossier; a successor needing code context should receive the exact main snapshot/repository access, not infer the implementation from a Markdown summary.

## 5. Audit and verification source files

### GitHub branch-scope check for additional audit packages

On 2026-10-06 the public GitHub `/branches?per_page=100` endpoint returned **46 branch refs**. The `contents/AUDIT` directory was checked at each listed branch tip. Fourteen tips have the known audit/verifier material: the primary-audit branch plus the 13 verifier branches listed below. The other 32 `contents/AUDIT` requests returned 404 (no `AUDIT` directory at that branch tip). This check reduces the chance that a second verifier package is hiding under another current branch’s `AUDIT/` directory, but it does **not** rule out report files under a different directory name, deleted/unlisted branches, historical commits, private material, or chat-only agent runs.

### Third-party audit

| Artifact | Exact locator | Scope/status |
|---|---|---|
| `AUDIT/APEX_GEN5_AUDIT.md` | Branch `arena/01a0e2f1-upstage`; report commit `015d19b`; blob `ee7052cc9d7959140157834a8b420f6b75aaf817`; 770,455 bytes; [raw report](https://raw.githubusercontent.com/sinamoosazadeh/Upstage/arena/01a0e2f1-upstage/AUDIT/APEX_GEN5_AUDIT.md). | Version 26, dated 2026-09-28, with a reported 392 rows over families A–R. Its own limits say the findings are auditor hypotheses; device, secrets, production database, real venue/Telegram, and complete history were not available to that auditor. The evolving report’s final row count must be checked against the exact version supplied. |
| `AUDIT/APEX_GEN5_AUDIT_INDEX.md` | Same branch; blob `62ffe1587c9c94c69cf0b87c73636571e9e42dfc`; 149,837 bytes; [raw index](https://raw.githubusercontent.com/sinamoosazadeh/Upstage/arena/01a0e2f1-upstage/AUDIT/APEX_GEN5_AUDIT_INDEX.md). | Navigation/priority index; not a substitute for the full audit report or row evidence. |

The session history records that all 66 audit chunks (0–65) were fetched, including retries after HTTP 502. The dossier copies selected A–F rows plus later selected families and summaries; it is **not** a verbatim, complete 392-row table. Retain the exact report and index when building Gen6 inputs.

### Verification report package: 9 numbered rounds, 15 reports

The following branch/file mapping is based on the dossier plus fresh read-only GitHub Contents-API checks on 2026-10-06. Each report’s corresponding `AUDIT/probes_<report>/` directory must travel with it; probe sources and outputs are evidence, not disposable scratch. The directories contain `.py`, `.out`, `.json`, and/or related files. Their full contents were **not** read in this session, so this inventory identifies where they are, not what every probe proves.

| Round/report | Public branch and file | Finding scope represented | Probe directory / important note |
|---|---|---|---|
| V1a | [`AUDIT/VERIFY_V1a.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e911-upstage/AUDIT/VERIFY_V1a.md), `arena/01a0e911-upstage` | C-002/C-003/C-004/C-006/C-008/C-010/C-012/C-013; nine rows reassigned to V1c. | `AUDIT/probes_V1a/`; synthetic evidence, not device/order acceptance. |
| V1b | [`AUDIT/VERIFY_V1b.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e9b8-upstage/AUDIT/VERIFY_V1b.md), `arena/01a0e9b8-upstage` | E-003 and E-016. | `AUDIT/probes_V1b/`; contains individual code/output and pytest artifacts. |
| V1c | [`AUDIT/VERIFY_V1c.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e9af-upstage/AUDIT/VERIFY_V1c.md), `arena/01a0e9af-upstage` | C-001/C-005/C-007/C-009/C-011/C-014/C-015, O-006, V-003. | `AUDIT/probes_V1c/`; this branch is V1c, **not V9**. |
| V1d | [`AUDIT/VERIFY_V1d.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0ed03-upstage/AUDIT/VERIFY_V1d.md), `arena/01a0ed03-upstage` | E-012…E-022 and X-V1d-001. | `AUDIT/probes_V1d/`; preserves API/manual-override and frozen-file discrepancy probes. |
| V1e | [`AUDIT/VERIFY_V1e.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0ed2b-upstage/AUDIT/VERIFY_V1e.md), `arena/01a0ed2b-upstage` | E-001/E-002/E-004…E-011; seven reported confirmed and three partial. | `AUDIT/probes_V1e/`; synthetic/fake code evidence. |
| V2 | [`AUDIT/VERIFY_V2.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e8aa-upstage/AUDIT/VERIFY_V2.md), branch now verified as `arena/01a0e8aa-upstage`; report blob `c73e3581242cf2c0bf07c931ca0968e19fb325eb`, 75,573 bytes. | D-001…D-031; dossier summary says 30 CONFIRMED and D-008 PARTIAL, with 620 targeted tests reported. | `AUDIT/probes_V2/`; earlier ledger/dossier left the branch name unresolved, now resolved by API. The single-plan 6,500>6,000 claim did not reproduce; separate multi-cell atomic-reservation gap was unproven. |
| V3 | [`AUDIT/VERIFY_V3.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e8ac-upstage/AUDIT/VERIFY_V3.md), `arena/01a0e8ac-upstage` | K-001…K-012. | `AUDIT/probes_V3/`; JSON probes are present; do not infer their results from filenames. |
| V3b | [`AUDIT/VERIFY_V3b.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e9b1-upstage/AUDIT/VERIFY_V3b.md), `arena/01a0e9b1-upstage` | K-013…K-034, X-V3b-001; L-001…L-015 reassigned to V3c. | `AUDIT/probes_V3b/`. |
| V3c | [`AUDIT/VERIFY_V3c.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0ed04-upstage/AUDIT/VERIFY_V3c.md), `arena/01a0ed04-upstage` | L-001…L-015; L-013 is PENDING in the preserved summary table. | `AUDIT/probes_V3c/`. |
| V4 | [`AUDIT/VERIFY_V4.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e8ad-upstage/AUDIT/VERIFY_V4.md), `arena/01a0e8ad-upstage` | 41 F/G rows. | `AUDIT/probes_V4/`; 35 reported confirmed, six partial; synthetic targeted tests. |
| V5 | [`AUDIT/VERIFY_V5.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e8b1-upstage/AUDIT/VERIFY_V5.md), `arena/01a0e8b1-upstage` | H/I families. | `AUDIT/probes_V5/`; V5 and V6 reports share this branch. |
| V6 | [`AUDIT/VERIFY_V6.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e8b1-upstage/AUDIT/VERIFY_V6.md), branch `arena/01a0e8b1-upstage`; report blob `7619375842c9a875b830ee5a524e410fee8955a0`, 162,028 bytes. | A/B/J/O/V; 49 mandated IDs plus X-V6-001/X-V6-002. | `AUDIT/probes_V6/`; branch/file location is now confirmed, unlike the older ledger’s ellipsis. |
| V7 | [`AUDIT/VERIFY_V7.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e8b8-upstage/AUDIT/VERIFY_V7.md), `arena/01a0e8b8-upstage` | M-001…M-016 and N-001…N-023 (39 rows). | `AUDIT/probes_V7/`; this branch also contains V9. |
| V8 | [`AUDIT/VERIFY_V8.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e8b7-upstage/AUDIT/VERIFY_V8.md), `arena/01a0e8b7-upstage` | Active P-rows; P-014/P-017 are described as discarded draft proposals, not active findings. | `AUDIT/probes_V8/`. |
| V9 | [`AUDIT/VERIFY_V9.md`](https://github.com/sinamoosazadeh/Upstage/blob/arena/01a0e8b8-upstage/AUDIT/VERIFY_V9.md), `arena/01a0e8b8-upstage`; report blob `502c71b92857f9a06a3663f2218ddb0612d220e2`, 111,816 bytes. | Q-001…Q-032 and R-001…R-021 (53 rows). | `AUDIT/probes_V9/`; current API confirms V9 is co-located with V7, not on V1c’s branch as one older ledger entry suggests. |

**Reported aggregate only:** the independent-review summary preserved in the dossier/ledger is 346 CONFIRMED / 46 PARTIAL / 0 REJECTED plus 16 cross-findings; it is not a fresh rerun. Preserve each report’s separate verdict/severity and the report’s exact evidence type (synthetic fixture, temp SQLite, repository-code trace, device, venue, etc.).

## 6. Owner decisions, ADRs, issues, and proposals to extract

| List / file | Where to obtain it | What to preserve and what is still missing |
|---|---|---|
| D1–D63 owner decisions | Filled main `PHASE2_DECISION_LOG.md`, `main:PHASE2_HANDOFF_CP9.md` (especially Session A and CP-14…CP-14.6 sections), PR bodies/comments, and owner messages. | Keep original owner wording, date, evidence, scope, implementation state, and amendments. D48 specifically restricts the public historical candle pack to source-tagged RESEARCH/BACKTEST; PAPER/LIVE use Toobit. D62 writes the fourteen `q_thr_by_tf` rows; D63 closes the regime-window item (see CP-14.6-FIX / ADR-CP14-033). D37–D45 are explicitly recorded as used in chat but absent from the surviving decision-log headings; retrieve from original chat if possible. |
| D64–D89 | `PHASE2_SESSION_LEDGER.md` §5 and the site-context dump; Phase-3 table is marked proposed/unruled/on hold. | There are 26 proposal IDs, not 26 approved fixes. Preserve alternatives and the planner recommendation as proposals; do not promote them into binding design without the owner’s ruling. |
| ADR-P2-001…017 | Main Decision Log / Rev-3 control files; summarized in ledger §7. | Plan/repository/process pre-adjudications: Upstage target, from-zero rule, capacity/staging, tree, fixtures, testing, etc. These are separate from later CP-14 changes. |
| ADR-SESSION-A | `HANDOFF_SESSION_A` in main CP-9 handoff and PR #17. | Owner D1–D20 doc-only design patch context. |
| ADR-CP14-001…033 | Main Decision Log and CP-9 handoff CP-14 records. | Later code/design adjudications through CP-14.6-FIX. The ledger says next free ADR-CP14-034; confirm against the exact source revision. |
| Issue / defect register | Main Decision Log and filled main handoffs; ledger §6 is a compact status map. | Include earlier resolved issues as lessons, not only currently open ones. Specific anchors include ISSUE-CP2-007, CP9-006, CP13-004, CP14-061…079, and the next-number note ISSUE-CP14-080. Statuses differ; verify each in the exact main file. |
| ISSUE-076…079 follow-up threads | Main CP-9 handoff and ledger §§5–8. | Themes include replay CLI/index migration/batched commits; boot self-test/progress/per-cell persistence; drift RTT; and `_input_fingerprint` DB-wide hashing plus unindexed `window()` join. They are issue threads, not four separate audit campaigns. |
| D54–D58 implementation state | Main CP-14.6 handoff and PR #24/#25 bodies. | They are recorded but **not implemented** in the CP-14.6 record; `composite_estimate` remains `NOT_WIRED`/ISSUE-CP14-070. Do not present them as fixes that landed. D60/D61 are artifact/verification rules, not operational code procedures. |

### Planning-agent error / lesson register

The intended set is approximately 50 lessons, specifically IDs **#1–#49** in the available continuity text. The material is spread across:

- `main:PHASE2_DECISION_LOG.md` planning-agent error register near its later lines (the dossier points to the error #22/#23 entries around L1075 in that snapshot);
- local `PHASE2_SESSION_LEDGER.md` §12, which says #1–#47 exist across the old main log and chat, preserves #22/#23 and summaries #29–#47, and explicitly says #1–#21 and #24–#28 lost their detail;
- `PHASE2_SITE_CONTEXT_SUMMARY.md`, whose injected-memory text contains #48/#49 and notes they were still missing from the ledger at dump time;
- original owner/assistant chat messages, which are required to recover the missing explanations verbatim.

Extract each lesson with its number, original mistake, owner correction, consequence, later remedy, and whether it is already fixed. Do not fill the missing #1–#21/#24–#28 text from guesses.

## 7. Other required evidence and requirement lists

These are not “audit sets,” but they contain Gen5 obligations, fixes, tests, or operational facts that a redesign must not omit:

- **Acceptance requirements and traceability:** `PHASE2_TRACEABILITY_MATRIX.md` Parts I–III; blueprint `AI.10` test IDs; `AI.13` external gates; chapter-level acceptance tests; `PHASE2_CHECKPOINTS.md`; filled main status board. In the local patch the matrix/board are blank/reset, while main has historical entries.
- **Engine and risk coverage:** E01–E12 complete engine specifications and V-report findings; 13 setup gates; 14 risk vetoes; fixture/test identifiers (`FIX_*`, `GF_SC_01/02`, etc.). These are distinct sources, not interchangeable summaries.
- **Test-run history:** CP-8 final report records 2,553 tests; CP-9 base handoff records 2,627; later CP-14.6/PR #25 records 3,051 passed in each of two runs. Keep each count attached to its commit, command, suite, warnings/skips, and date; do not treat the counts as one cumulative total or as owner-phone/venue acceptance.
- **Phone, PAPER, E11 and performance evidence:** main CP-9 handoff phone-acceptance subsections, PR #24/#25, `PHASE2_SESSION_LEDGER.md` §§8–9, and the site-context dump. Claims include a phone-trained E11 artifact, D47/D49 measurements, 140 cells/QUALITY facts, long-cycle observations, Toobit behavior, and explicit owner-run acceptance commands. The phone report is named `data/e11_train_report_20260924T181954Z.json`; its artifact SHA-256 is explicitly unavailable in this sandbox. `data/e11_preview_720.yaml` and `params/e11_classifier_v1.yaml` are also not part of the tracked main snapshot (the classifier is gitignored). The phone DB, secrets, and raw owner-phone files are not in this patch; never send secrets or transfer the database via GitHub.
- **Unticked safety/release gates:** copy every remaining unchecked item from the CP-14.6 owner-phone acceptance checklist and `AI.13`, including target-device, multi-day PAPER, restore, risk/fallback, and owner-signoff gates. A test green on a sandbox is not evidence that these gates passed.
- **Owner constraints and communication rules:** current 2026-10-06 session memory (copied in dossier Appendix A), `PHASE2_SESSION_LEDGER.md` §3, and the site-context dump. Preserve the distinctions between owner decisions, assistant recommendations, agent claims, and unresolved questions. Key constraints include no simplification or temporary workaround, owner approval before behavior-changing decisions, phone PAPER, E11 rigor, exact traceability, source-tagged public historical candles only in RESEARCH/BACKTEST (D48), no secrets/database in GitHub, and trader-comprehensible Persian communication.
- **Superseded/dead-end material:** `AI_SUGGESTION_PLAN.md` is deleted and its earlier multi-agent split is obsolete; old repository `START EXECUTION` text in `PROMPT.md` is superseded; prior-attempt code is not to be reused. Preserve these as “do not follow” context, not as active requirements.

## 8. Persistent local files already available in this workspace

| File | What it contains | Limitation / use |
|---|---|---|
| `APEX_GEN5_PROJECT_DOSSIER_2026-10-06.md` | 88,322-line dossier, sections 1–12 and appendices A/B; project identity, design comparison, selected findings, result map, source inventory, manifest, full design exhibits. | The dossier states that it is not a full 392-row re-audit, does not fully transcribe all V reports, and does not inspect probe contents. |
| `PATCH_CONTENTS_INDEX_2026-10-06.md` | Exact map of the 22-section local documentation `.patch`, including physical patch-line ranges. | Maps that patch only; it is not the full GitHub/PR/audit archive. |
| `PHASE2_SESSION_LEDGER.md` | Draft 612-line reconstruction of session history, D/ADR/ISSUE indexes, code/device state, V rounds, errors, dead ends, and open questions. | It explicitly records lost detail, is not a verbatim transcript, and contains stale/mismatched anchors. |
| `PHASE2_SITE_CONTEXT_SUMMARY.md` | 126-line historical injected-memory dump plus dump-time notes. | A date-specific snapshot; not current status. It contains claims/notes not necessarily present in the ledger. |
| Local short Rev-3 control files | `PHASE2_*` board, log, matrix, handoff templates and `STEP1_FIX_CP2-CP8.md`. | Some are byte-identical to main; others are shortened/reset and differ from filled main history. Check the comparison in dossier §9 before treating any as authoritative. |
| Current local `PROMPT.md` | Original Chief-Engineer text with status note. | Retained authority/history document; old repository target is explicitly superseded. |
| Deleted-file patch entry for `AI_SUGGESTION_PLAN.md` | The patch shows an old Persian exploratory planning proposal. | Deleted/withdrawn; do not resurrect it. |

## 9. Contradictions and gaps the Gen6 input bundle must expose

1. **Original vs amended design:** 216bcc/20,551 lines vs 493568/20,983 lines; the old ledger mispairs one hash. Provide the receipt and whole-file diff.
2. **Rev-3 plan vs later implementation:** plan says CP-1…CP-8; actual main handoff/PR history continues through CP-9 and CP-10…CP-14.6. Do not erase the later work to make the plan look consistent.
3. **Main vs local files:** filled main board/matrix/log/handoffs differ from local short, untracked PENDING/blank copies. Keep the exact source ref with every copied document.
4. **Error-list incompleteness:** #1–#21 and #24–#28 details are lost in the ledger; #48–#49 are in the site-memory dump, not the ledger’s #1–#47 register. The chat export is needed for a complete list.
5. **Decision gaps:** D37–D45 were used in chat but their wording/details are lost or missing in the log; D64–D89 are proposals on hold, not owner-approved changes.
6. **Audit counting:** 392 report rows plus 16 cross-findings; whether the 16 are included in 392 is unresolved. Preserve both values and the unresolved boundary.
7. **Verification package limits:** 15 reports are identifiable, but the dossier’s evidence review did not read every full V report and did not inspect the contents of all probe files. V3c L-013 remains PENDING in the report summary.
8. **Potential later agent round:** the surviving ledger calls the ~210-row/six-agent cross-check an unanswered question. No distinct completed later >9-agent round was found in the accessible records; search the raw chat export and other temporary branches if the owner remembers one.
9. **Synthetic vs operational evidence:** many V probes and targeted tests are synthetic/repository-code evidence. Do not promote them to real phone, Toobit, Telegram, 24/7 PAPER, or LIVE evidence.
10. **PR #24 vs #25:** #24’s CP-14.6 work was not merged; #25 transported the work plus CP-14.6-FIX. Preserve #24 for provenance, but do not count its patch as a second independent merged fix wave.
11. **Unimplemented items:** CP-14.6 records D54–D58 as not implemented; D64–D89 are unruled proposals. Do not represent either group as shipped.
12. **Stale closeout evidence:** main `PHASE2_FINAL_REPORT.md` is from CP-8 and dated 2026-09-14. Later PRs report newer suites and changes; neither the old final report nor a green synthetic suite proves final owner acceptance.
13. **CP-8 handoff typo:** the local template says “CP-9 consumes” under CP-8 interfaces even though Rev-3 ends at CP-8. Flag it rather than inventing an extra stage.

## 10. Owner’s copy/paste extraction checklist for the new session

To make the Gen6 handoff auditable, collect these distinct bundles and label their evidence status:

- **Blueprint bundle:** both exact `APEX_GEN5.md` versions; the frozen receipt; the whole diff/amendment trail through CP-14.6-FIX; all owner-approved amendments separated from recommendations.
- **Implementation bundle:** the exact `main@85b2c15` source snapshot or repository access; PRs #1–#25 (with #24 explicitly marked superseded); filled main CP-1…CP-9 handoffs, status board, matrix, decision log, final report, README, tests, fixtures, parameters, and the 225-path/hash manifest.
- **Audit bundle:** full third-party audit and index; all 15 V reports; every corresponding `probes_V*` file and output; any later cross-verification package if it exists. The source reports and evidence are required even if the new model will not rerun their probes.
- **Decision bundle:** exact owner text for D1–D63; the D64–D89 proposal table with every alternative/recommendation; ADR-P2 and ADR-CP14 records; all issue IDs with status/evidence; explicit owner approvals, rejections, and unresolved questions.
- **Agent-error bundle:** the complete #1–#49 planner/assistant mistake list, with missing #1–#21/#24–#28 recovered from the original chat if possible; keep #48/#49 from the site snapshot as distinct entries.
- **Operational-evidence bundle:** dated test reports, owner-phone PAPER runs, E11 artifacts/measurement reports, logs, and every unchecked gate. Keep synthetic tests, repository traces, phone observations, venue responses, and proposals in separate evidence classes. Do not transfer the database or secrets through GitHub/chat.
- **User-instruction bundle:** exact standing constraints and corrections from the chat plus current session memory; distinguish process/communication requirements from trading-system design requirements.
- **Unknowns bundle:** explicit loss markers for chat detail, unresolved V-report items, unmapped branches/probes, status conflicts, and unapproved proposals. Do not let the successor model silently fill these gaps.

For every copied item, retain at least: **ID/name; exact source path/URL; commit/blob/hash; author or source class; date; verbatim text/evidence; status (owner-approved / reported / independently reproduced / proposal / rejected / unknown); linked design and code anchors; side effects/interactions; tests/artifact; and whether the Gen6 redesign should preserve, correct, reject, or defer it.** The model may recommend a Gen6 change, but must not convert a report claim or unruled proposal into an owner decision.

### Chat-history-specific search and copy/paste checklist

The owner’s chat export is the only possible source for text explicitly marked lost or for agent prompts/replies not committed to GitHub. Search across the entire history, not only the latest chat segment. Copy the full relevant exchange (prompt, response, owner correction/ruling, follow-up, and final status), not just a summarized assistant answer.

| Search anchor / phrase | Extract as a separate record | Cross-check against |
|---|---|---|
| `#1`…`#49`, “mistake”, “error”, “planning agent”, “assistant error” | The complete numbered error list; especially recover verbatim #1–#21 and #24–#28, which the ledger says are lost. Include owner correction, consequence, and later remedy. Keep #48 and #49 even though they appear only in the site-memory dump. | Main Decision Log error register; Ledger §12; Site Context Summary. |
| `Rev-1`, `Rev-2`, `Rev-3`, `P1`…`P8`, `G1`…`G20`, `P1`…`P21` | Plan revisions, freeze instructions, scope/rationale changes, and any owner-approved project/process amendments. | PR #1, `PHASE2_MASTER_PLAN.md`, `PHASE2_GLOBAL_DIRECTIVES.md`, Session A / PR #17. |
| `D1`…`D63`, especially `D37`…`D45`, `D48`, `D49`, `D62`, `D63` | Original owner wording, alternatives, decision/ruling, date, acceptance evidence, later amendment, and exact implementation status. D37–D45 need recovery from chat if available. | Main Decision Log and CP-14 sections in `PHASE2_HANDOFF_CP9.md`; PRs #17–#25. |
| `D64`…`D89`, “Phase 3”, “on hold”, “proposal”, “decision table” | Each proposal’s full rationale, options, recommendation, owner reply (including no-ruling), cross-links, and whether it remained unapproved. | Ledger §5, ISSUE-076…079 options, current owner instructions. |
| `ADR-P2-`, `ADR-SESSION-A`, `ADR-CP14-`, `ISSUE-`, `ISSUE-CP` | Every ADR and issue discussion, not merely the final status: initial report, side effects/interactions, rejected options, owner approval, fix PR, test, and closure evidence. | Main Decision Log, filled handoffs, PR bodies/comments, ledger §§6–7. |
| `V1`, `V2`…`V9`, `VERIFY_`, `392`, “confirmed”, “partial”, “cross-finding”, `X-V` | The audit execution plan and the exact prompt sent to each reviewing account; each final response; corrections and owner decisions; all separate findings. Search for any additional supplementary round described as “more than nine agents”, “400 items”, “210 rows”, or “six agents”. | Full third-party report; all 15 `VERIFY_*.md` files and every `probes_V*` directory; the saved ledger’s open-question entries. |
| `CP-1`…`CP-14.6`, `CP-14.6-FIX`, `executor`, `handoff`, `green`, `closeout`, “push failed” | Each coding-stage request/acceptance exchange, exact changed IDs/files, executor clarification, test run/commit/PR, and owner acceptance or refusal. Keep CP-14.6 and CP-14.6-FIX distinct; PR #24 and PR #25 have different transport/merge status. | PRs #1–#25, especially filled `PHASE2_HANDOFF_CP1..CP9.md` on main; do not use reset local templates as history. |
| `E01`…`E12`, `E-001`…`E-022`, `FIX_`, `GF_SC_`, `T-`, `AI.10`, `AI.13`, `G-` | Engine contracts, audit-row IDs, test/fixture inventories, acceptance-gate lists, failure reports, and owner acceptance. Keep engine E01 separate from audit row E-001. | `APEX_GEN5.md`, traceability matrix, test tree, V reports, external-gate checklist. |
| “test”, exact commands, `2553`, `2627`, `3040`, `3051`, `pytest`, `PASS`, `WARN`, `SKIP` | Exact command, code/ref, environment/device, timestamp, all result lines and warnings/skips, whether suite was complete, and who ran it. | Filled handoffs, PRs #8–#25, `PHASE2_FINAL_REPORT.md`, traceability matrix. |
| `PAPER`, `LIVE`, `Toobit`, `Telegram`, `Termux`, `140 cells`, `QUALITY`, `E11`, `train report`, `restore`, `24/7` | All real-owner phone/production observations, device constraints, venue/API/network results, E11 training/artifact, performance/run durations, database facts, and unticked acceptance gates. Separate owner evidence from sandbox mocks. | CP-9…CP-14.6 phone-acceptance sections; exact phone artifact names in §7; AI.13 and the owner checklist. |
| “APEX_GEN5.md”, “frozen”, “hash”, “amendment”, “D48”, “public candle”, “source tag” | Every design amendment, owner rationale, change to a frozen clause, and source/data boundary. Keep original, intermediate, and amended snapshots separately. | Original 216bcc and main 493568 snapshots; receipt; full spec diff; Decision Log D48. |
| `Evidence`, “QX”, “UNAVAILABLE”, “12 engines”, “Conflict Resolver”, “G—” | Owner’s current design-learning corrections and exact required explanation boundaries; keep design/code/undefined distinctions and deferred G-subjects as teaching instructions, not silently as new system behavior. | Current session memory (2026-10-05/06), full blueprint, current implementation. |
| `USB`, `LAN`, `SSH`, “database”, “secret”, `.env`, “prompt in chat” | Transfer/security/process constraints and any artifacts explicitly excluded from GitHub or commits. | Current user constraints and `.gitignore`; never copy secrets into the Gen6 package. |
| Any message about “new repo”, “from zero”, “reuse code”, “frozen design”, “Gen6” | The requested end state: redesign and deliver a complete frozen APEX_GEN6 design document for later coding; preserve no-reuse/no-shortcut rules and any required owner approval gates. | Current task, Rev-3 authority history, owner’s latest instructions. |

Do not treat the absence of a search hit in a condensed memory dump as proof that the original conversation did not contain a later item. If a copied exchange cannot be located, mark it `not found in available chat export`; do not replace it with a plausible reconstruction.

## 11. Status of this register

This document is a navigation and completeness-control aid compiled from the current compacted context, the local dossier/continuity files, the local `main@85b2c15` snapshot, and read-only public GitHub metadata/pages checked on 2026-10-06. It does **not** claim that every probe, every temporary branch file, every original chat message, or every GitHub code file was independently read in full. The dossier’s §12 manifest is the authoritative path inventory for all 225 tracked main files; the report/PR tables above identify the additional audit and change-history packages. The uncompressed original conversation remains necessary to recover content explicitly marked lost and to determine whether the remembered later >9-agent supplementary round exists.