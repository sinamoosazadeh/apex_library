# AX-12 — Operations, Security, Observability and the Operator

**Status:** Normative.
**Upstream:** AX-04, AX-08, AX-09, AX-10.
**Downstream:** AX-14, AX-16, `contracts/config.default.yaml`.

A single-operator system fails for operational reasons far more often than for modelling reasons. This
document therefore treats deployment, secrets, recovery and the human interface as *designed
components*, not as afterthoughts (A8, L7).

---

## 1. Deployment topologies (`AX-12:§1`)

| Topology | Where the live loop runs | Where research runs | When it is admissible |
|---|---|---|---|
| **A — Single node** (default) | the owner's device (e.g. Termux/Android, or any always-on machine the owner controls) | same node, in low-priority windows | if and only if every blocking benchmark in §2 passes with measured evidence |
| **B — Edge + compute** | a small always-on edge node with the live loop | an optional heavier node for research only | if the owner has such a node; the live loop must still function alone for `P-OPS-001` days without the research node |
| **C — Server-first** | a VPS | same or separate | only by an explicit owner decision recorded in AX-18; it is *not* the default, and it does not silently replace topology A |

**Invariant (`AX-12:§1-R1`):** the *live* loop's correctness and safety must never depend on a second
machine, on a specific network path, or on the research environment being reachable. Everything needed
to protect and close positions lives at the venue and in the local journal.

**No-silent-degradation rule (`AX-12:§1-R2`):** when a measured constraint (CPU, RAM, disk, thermal,
network) prevents a capability from meeting its benchmark, the design response is one of: (a) measure
and document; (b) relocate the capability to a node that meets it; (c) reduce the *scope* of the
capability (e.g. smaller universe) with the owner's explicit approval. **Never** (d) quietly lower a
safety threshold, shorten a warm-up, or skip a gate.

---

## 2. Hardware and environment benchmarks (`AX-12:§2`)

Each benchmark is a scripted, repeatable workload with a pass/fail criterion; results are stored as
evidence and re-run after any environment change. These benchmarks close the Class-3 unknowns of
AX-00 §3.

| ID | Workload | Pass criterion (defaults; `[O]`/`[C]`) |
|---|---|---|
| `BENCH-01` | full decision cycle for the whole universe on the current dataset, 1 000 iterations | p99 ≤ `P-OPS-010` (default 5 s) |
| `BENCH-02` | sustained ingest at the configured tier mix for 24 h, including persistence | zero lost L0 records; write latency p99 ≤ `P-OPS-011`; no unbounded memory growth |
| `BENCH-03` | journal append + hash chain at the peak event rate | p99 ≤ `P-OPS-012`; chain verifies |
| `BENCH-04` | rebuild of one day of L1 from L0 (AX-04 §6.4) | ≤ `P-DATA-052` |
| `BENCH-05` | order round-trip under simulated load (paper adapter) | p99 `t_ack` ≤ `P-OPS-013` measured against the venue's real distribution (§VCH-16) |
| `BENCH-06` | 24 h WS soak with reconnects, heartbeats and gap repairs | reconnect handling correct; no missed protection windows |
| `BENCH-07` | storage growth for 7 days at the configured universe | within `P-OPS-014` % of the model of AX-04 §7 |
| `BENCH-08` | backup + restore drill (§6.3) | restore verified, RPO/RTO met |
| `BENCH-09` | thermal/battery soak: 4 h of continuous operation on the target device | no throttling that breaks `BENCH-01/02/03` criteria; battery behaviour documented |
| `BENCH-10` | end-to-end paper day with the scenario suite subset | all scenario criteria pass |

`AX-12:§2-R1` — A capability whose benchmark fails is **disabled in live**, not degraded silently; the
operator receives a single message stating the capability, the measured value, the required value and
the two admissible options (§1-R2).

---

## 3. Process supervision and lifecycle (`AX-12:§3`)

- **One writer**: exactly one live process; a lock file and a PID check prevent a second instance
  (`T-OPS-001`). A second instance attempting to start must exit with a clear message.
- **Supervisor**: a minimal, well-understood supervisor (systemd unit, `tmux`/`supervisord`, or the
  platform equivalent) with restart-on-failure, exponential backoff capped at `P-OPS-020`, and
  crash-loop protection (after `P-OPS-021` restarts in `P-OPS-022` minutes, the system starts in
  `OFF`/disarmed and sends a `SEV-1`).
- **Crash-only design**: the process assumes it may die at any instruction. Therefore: intents are
  journaled before transmission (INV-3); the venue holds protection; every boot runs the readiness pass
  (AX-04 §9) and the reconciliation (AX-08 §7) before any order.
- **Graceful shutdown**: stop accepting new decisions ⇒ finish or abandon in-flight intents (journaled)
  ⇒ flush the journal ⇒ verify the chain ⇒ exit. Protection orders are **never** cancelled on shutdown.
- **Watchdog**: the supervisor restarts on a missed internal heartbeat (`P-OPS-023`); an external
  watchdog (cron or the supervisor's own timer) verifies the process is alive and the journal is
  advancing, and notifies the operator if not (`T-OPS-002`).

---

## 4. Time, schedulers and cadence (`AX-12:§4`)

- All schedules are UTC; local time is a display concern only. No DST logic exists in the system
  (`T-OPS-003`).
- The tick scheduler uses a monotonic clock for intervals and the venue-corrected wall clock for
  timestamps (AX-03 §3.1). Long pauses are detected (a tick that is late by more than
  `P-OPS-030` triggers a "missed cycle" record, and the decision is *skipped*, not back-filled).
- Bar-close scheduling uses the grace period of AX-03 §3.3 and is re-anchored to the venue clock, not
  the local clock.

---

## 5. Keys, secrets and access (`AX-12:§5`)

### 5.1 Venue key policy (`AX-12:§5.1`)

1. **Permissions:** trading only. Withdrawal must be impossible: the key is created without withdrawal
   permission *and* the system contains no withdrawal call site (`T-SEC-003`).
2. **IP whitelist:** enabled; the venue rejects unbound keys (`-1023`) `[V-DOC]`. The whitelist is the
   set of egress IPs actually used; if the device's IP is dynamic, the design response is to (a) use a
   fixed egress if available, or (b) re-authorise deliberately with the operator present — never to
   disable the whitelist silently.
3. **Rotation:** key rotation every `P-SEC-001` days or immediately on suspicion; rotation is a runbook
   (`RB-09`) with an overlap window (create new, verify, remove old).
4. **Separation:** different keys for `PAPER`-adjacent probes and for live, so that a probe accident
   cannot touch the live budget. (If the venue's key model does not support this cleanly, the design
   restricts probes to read-only calls.)

### 5.2 Secret handling (`AX-12:§5.2`)

- Secrets live in the OS secret store or an encrypted file with `0600` permissions outside the
  repository; they are loaded by the config loader only.
- **Redaction law:** a redaction filter is applied to every log line, journal payload, metric label,
  notification and error message; the filter is tested by `T-SEC-001` which attempts to leak key-like
  patterns through every output path.
- Secrets never appear in: the repository, chat, issue trackers, screenshots, notifications, crash
  dumps, or the journal. A leak is a `SEV-1` with immediate rotation.
- The system refuses to start if the key is stored in a world-readable file (`T-SEC-002`).

### 5.3 Environment hardening (`AX-12:§5.3`)

Minimal OS surface; no inbound ports exposed; outbound only the venue and the notifier; package
versions pinned and recorded; the host's clock service enabled (NTP or platform equivalent) because
`-1021` is a trading-safety hazard (AX-02 §2.3).

---

## 6. Backup, restore and disaster recovery (`AX-12:§6`)

### 6.1 What is protected (`AX-12:§6.1`)

| Artifact | RPO target | Why |
|---|---|---|
| Journal (append-only, hash-chained) | `P-OPS-040` (default 15 min) | audit spine; loss is unacceptable |
| L1 hot store | `P-OPS-041` (default 24 h) | rebuilding is possible from L0, but expensive |
| L0 segments | `P-OPS-042` (default 24 h) | the raw truth; loss degrades all future research |
| Model/parameter registry + calibration artifacts | immediate (copy on write) | irreplaceable evidence |
| Configuration + `venue_profile.json` | immediate | reproducibility |

### 6.2 Backup method (`AX-12:§6.2`)

Deterministic, encrypted, incremental snapshots (SQLite backup API or a stopped-writer copy for
consistency, plus segment copies for L0) to `P-OPS-043` locations, one of which is **off-device**.
Verification: each backup's manifest records row counts and segment hashes; the manifest is verified at
creation and re-verified at restore.

### 6.3 Restore drills (`AX-12:§6.3`)

A restore is performed and verified quarterly, and after any schema migration: restore to a scratch
directory, run the integrity checks, rebuild L1 for one day from L0, and compare digests to the
production values. **Untested backups are not backups** (`AX-12:§6.3-R1`, `BENCH-08`).

### 6.4 Disaster scenarios (`AX-12:§6.4`)

| Scenario | Response |
|---|---|
| Device lost/destroyed with open positions | restore journal on a new node; reconcile with the venue; protection was venue-side throughout; resume in `OFF` first |
| Journal corrupt | treat as `K1`; restore from backup; if the gap cannot be closed, mark the affected period `UNRECONSTRUCTIBLE` and continue with an explicit note in every affected artefact |
| Venue-side position with no corresponding local record | the reconciliation adopts the venue position as truth and journals a correction (AX-08 §7) |
| Key compromised | rotate, revoke, review the fill history for unauthorised activity, harden |

---

## 7. The operator interface (`AX-12:§7`)

### 7.1 Principles (`AX-12:§7.1`)

The operator must be able to: see the system's state in one screen; stop it with one action; understand
*why* it is doing what it is doing; and never be required to act quickly to prevent a loss. Anything
that violates these is a design defect.

### 7.2 Command surface (`AX-12:§7.2`)

| Command | Effect | Confirmation |
|---|---|---|
| `status` | print the §7.3 view | none |
| `arm` / `disarm` | permit/forbid new risk (positions stay protected) | none (safe direction), `arm` requires readiness pass |
| `pause` / `resume` | stop/restart the decision loop (protection unaffected) | none |
| `kill soft` | `K8` soft: no new risk | single confirm |
| `kill hard` | `K8` hard: bounded flatten all | two-step confirm with the position summary echoed |
| `flatten <instrument>` | close one position via AX-08 §9 | two-step confirm |
| `reconcile now` | run the full reconciliation | none |
| `promote <model>` | apply a `GateRecord` (AX-10 §4) | echo the evidence summary + confirm |
| `params diff|apply` | show/apply a `ParamSet` (class-aware; risk parameters need dual control, §8) | two-step for risk parameters |
| `explain <decision_id>|refusal` | dump the inputs, gates and reason codes for one decision | none |
| `backfill <scope>` / `rebuild <scope>` | maintenance operations | none (they do not touch risk) |
| `report <window>` | generate the standard report | none |

Anything not on this list does not exist as a command (`T-OPS-004`).

### 7.3 Status view (`AX-12:§7.3`)

Fixed schema (also used for the Telegram `status` message): mode; armed yes/no; governor state +
trigger + age; risk multiplier decomposition (`m_gov`, `m_data`, `m_regime`, `m_exec`); positions
(instrument, side, notional, `R` consumed, protection state, unrealised); today's loss vs `L_day`;
margin utilisation; data health by instrument; kill states; reconciliation freshness and result;
pending operator actions with deadlines; last `P-OPS-050` refusals with reason codes; clock offset;
WS session ages; journal chain status; disk headroom.

### 7.4 Notification schema (`AX-12:§7.4`)

Notifications are structured (a fixed template per event type), rate-limited for `SEV-3/4`, never
rate-limited for `SEV-1/2` (AX-09 §6.2), and never contain secrets. Every notification carries the
`decision_id`/`incident_id` it refers to so that it can be resolved back to the journal.

### 7.5 Runbooks (`AX-12:§7.5`)

Minimum set (each with numbered steps, expected outputs, and an abort condition): `RB-01` boot and
readiness failure; `RB-02` data staleness; `RB-03` WS failure; `RB-04` venue API outage; `RB-05`
`UNKNOWN` outcome incident; `RB-06` protection failure; `RB-07` reconciliation divergence; `RB-08` kill
switch activation and recovery; `RB-09` key rotation; `RB-10` clock skew; `RB-11` disk pressure;
`RB-12` backup/restore; `RB-13` model promotion; `RB-14` parameter change; `RB-15` cost-model refit;
`RB-16` governor re-arm; `RB-17` ladder demotion; `RB-18` incident postmortem; `RB-19` device
migration; `RB-20` quarterly review. Each runbook is *drilled* at least once before `LIVE` and
annually thereafter; drills are recorded as evidence (`T-OPS-005`).

---

## 8. Change management (`AX-12:§8`)

**Code:** change → tests (AX-14 battery) → review → deploy to `PAPER` → observe `P-OPS-060` days →
deploy to `LIVE` → verify readiness + reconciliation → monitor `P-OPS-061` hours. Rollback = redeploy
the previous pinned artifact; the artifact hash identifies the running code at all times.
**No functional change is deployed while the governor is `DEFENSIVE` or stricter** (`AX-12:§8-R1`),
except changes that *reduce* risk.
**Parameters:** class-aware. `[C]` parameters change only via their calibration procedure;
`[O]` parameters change only via the operator with a recorded reason; **risk-limit parameters require
dual control**: the operator issues the change, then a separate confirmation step (a second command
with the echoed old/new values and a cooling-off delay `P-OPS-070`) applies it. The friction is
deliberate (A5).
**Registry:** every deployed combination (code hash, param set hash, model hashes, profile hash) is
recorded in a deployment ledger; the ledger is the index of "which system produced this result".

---

## 9. Observability (`AX-12:§9`)

- **Metrics** (names, units, and thresholds live in AX-15): decision-cycle latency; tick lateness;
  records ingested/rejected per gate; series staleness; WS reconnects; request weight consumed by class;
  order outcomes by code; `UNKNOWN` events; reconciliation results; protection state per position;
  governor state and multipliers; realised vs modelled cost; refusal counts by reason; journal chain
  status and size; disk headroom; clock offset; memory/CPU of the process.
- **Logs:** structured (JSON), one event per line, with `ts`, `level`, `component`, `event`,
  `correlation_id` (decision/intent/order), and redacted payloads. Log levels are fixed per event type
  (no ad-hoc printing).
- **Correlation:** every decision and every order carries a `correlation_id` linking the snapshot, the
  decision, the intents, the venue responses, the fills and the journal entries — this is what makes
  `explain <id>` possible.
- **Telemetry retention:** metrics aggregated to `P-OPS-080`-day retention; logs rotated and compressed;
  nothing in telemetry may be needed for the audit trail (the journal is authoritative).
- **Dashboards:** the minimum acceptable view is the §7.3 status plus three time series: equity and
  drawdown, realised-vs-modelled cost, and governor state with triggers.

---

## 10. Incidents (`AX-12:§10`)

Classification: `SEV-1` (safety/integrity: journal break, flatten failure, key compromise, liquidation),
`SEV-2` (control: divergences, protection failures, repeated `UNKNOWN`), `SEV-3` (degradation),
`SEV-4` (informational). Every `SEV-1/2` produces: an incident record; an automatic evidence bundle
(raw payloads, journal range, metrics, configuration hashes); a postmortem within `P-OPS-090` days;
and — if a design clause was wrong or missing — an ADR that amends the documents. **Mandatory after any
`SEV-1`:** parameters and model versions are frozen until the postmortem closes (`AX-12:§10-R1`), so
that the incident is not masked by a subsequent change.

---

## 11. Operational limits (`AX-12:§11`)

| Limit | Default | Rationale |
|---|---|---|
| max open positions | `P-RSK-070` | bounded attention and margin, and a bounded flatten time (A5) |
| max new positions per minute | `P-EXE-041` | operational pace, not throughput |
| max notifications per hour (`SEV-3/4`) | `P-OPS-100` | alert fatigue control |
| max manual actions per hour | `P-OPS-101` | deliberate friction against impulsive intervention |
| max single manual position change | `P-OPS-102` × `R` | the operator cannot accidentally move more risk than the system allows a signal to |

The last row is important: **the human is inside the same risk envelope as the machines**
(`AX-12:§11-R1`); manual overrides that would exceed the envelope are refused by the risk kernel.

---

## 12. Test obligations (`AX-12:§12`)

`T-OPS-001`…`T-OPS-006` (single writer, watchdog, UTC-only, command surface, drills, deployment
ledger), `T-SEC-001`…`T-SEC-004` (redaction, permissions, no withdrawal call sites, key-rotation
procedure), `T-BACKUP-001`…`T-BACKUP-003` (manifest verification, restore drill, RPO/RTO), `T-BENCH-01`…
`T-BENCH-10` (the §2 benchmarks implemented as executable acceptance scripts).
