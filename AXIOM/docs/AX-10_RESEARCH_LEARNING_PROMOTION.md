# AX-10 — Research Protocol, Promotion Ladder and Model Lifecycle

**Status:** Normative.
**Upstream:** AX-05 (features), AX-06 (forecasts), AX-07 (risk), AX-09 (governor), AX-11 (simulator).
**Downstream:** AX-14 (gates), AX-15 (parameters), AX-16 (roadmap).

The learning plane (`lnp`) is the only place where the system is allowed to change. It is offline by
construction: it reads the tape, produces artifacts, and puts them behind the gates below. Nothing in
`lnp` runs in the trading path.

---

## 1. Why a protocol (`AX-10:§1`)

With a single venue, a few hundred instruments' worth of history, and an owner who will act on months
of evidence rather than years, the dominant risk is not "failing to find a strategy" — it is
**manufacturing a false one** and paying for it with real capital. Every rule in this document exists to
make false discovery expensive and true discovery reproducible.

---

## 2. Hypothesis registry and pre-registration (`AX-10:§2`)

Every research question is registered **before** any data is touched, with:

| Field | Meaning |
|---|---|
| `hypothesis_id` | unique id |
| `statement` | falsifiable statement, including the direction of the effect |
| `mechanism` | why the effect should exist (AX-05 §2.2) |
| `features` | exact feature ids/versions (AX-05) |
| `universe_rule` | which instruments, chosen by rule (not by hindsight) |
| `period` | the dates to be tested (fixed in advance) |
| `metric` | the primary metric and its decision threshold |
| `sample_requirement` | the minimum `n_eff` from the power calculation (AX-05 §2.4) |
| `stopping_rule` | when the test ends (a date, or a fixed number of observations) |
| `registered_ts` | timestamp and hash of the record |

`AX-10:§2-R1` — A test whose registry entry was written *after* the data was examined is recorded as
`EXPLORATORY` and may never be used as promotion evidence; exploratory results may only generate new
pre-registered hypotheses.
`AX-10:§2-R2` — Registrations are immutable; amendments create new versions with their own hashes and
are journaled.

---

## 3. Datasets and statistical protocol (`AX-10:§3`)

### 3.1 Dataset builder (`AX-10:§3.1`)

Inputs: L0/L1 (AX-04), the historical `UniverseRecord`s (survivorship-free, AX-04 §4.3), the feature
registry versions, the cost-model version, the label definition (AX-06 §2.1). Every dataset carries its
own manifest with all versions and hashes; two datasets with different manifests are never compared.

### 3.2 Splits (`AX-10:§3.2`)

- **Purged K-fold** with **embargo**: for horizon `H` and maximum feature window `W`, the purge width is
  `H` bars (labels overlapping the test fold are removed from training) and the embargo is `P-LRN-001`
  bars after each test fold (default: `max(H, P-LRN-002)`), because features have memory
  (`[D]`: without the embargo, training rows adjacent to test rows leak information through
  overlapping windows — the single most common cause of backtest inflation).
- **Walk-forward** for final validation: expanding or rolling windows, retrained at each step
  (`P-LRN-003` steps), producing a *sequence* of out-of-sample results, never a single number.
- **No shuffling, ever.** A shuffled split is a defect (`T-LRN-001`).

### 3.3 Overlapping labels (`AX-10:§3.3`)

Labels are weighted by uniqueness (AX-06 §2.2); the effective sample is `n_eff = Σ w_u` and all
statistics (Sharpe, IC, bootstrap) use it. Reporting an unweighted statistic is a defect
(`T-LRN-002`).

### 3.4 Multiple-testing control (`AX-10:§3.4`)

Three layers, all mandatory for promotion evidence:

1. **Family-wise control for the final claim:** White's Reality Check / Hansen's SPA on the *set* of
   models that survived earlier screens, using the stationary bootstrap (`P-LRN-004` replications),
   reporting the SPA p-value.
2. **Deflated Sharpe Ratio (DSR)** `[D]`: with `SR̂` the observed Sharpe, `T` observations, `N` trials,
   skew `γ₃`, kurtosis `γ₄`:
   `SR* = √Var(SR_trials) · ( (1−γ)Φ⁻¹(1 − 1/N) + γΦ⁻¹(1 − 1/(N·e)) )` (the expected maximum Sharpe
   under the null of no skill, `γ` = Euler–Mascheroni), and
   `PSR(SR*) = Φ( (SR̂ − SR*)·√(T−1) / √(1 − γ₃SR̂ + (γ₄−1)/4·SR̂²) )`.
   A promotion requires `PSR(SR*) ≥ P-LRN-005` (default 0.95). This is the number that answers
   "how lucky would a no-skill search have to be to produce this", and it is the reason the trial count
   `N` must be recorded honestly (every tested configuration counts — `T-LRN-003` audits the count).
3. **PBO via CSCV** [Bailey et al.]: split the out-of-sample period into `P-LRN-006` blocks, form all
   combinations, and compute the probability that the in-sample-best configuration underperforms the
   median out-of-sample. Promotion requires `PBO ≤ P-LRN-007` (default 0.5 — i.e., the candidate must
   not be the systematic winner of a coin-flip tournament; lower is better and reported).

**Minimum track record length:** `MinTRL = 1 + (1 − γ₃·SR + (γ₄−1)/4·SR²) · (z_{1−α}/(SR − SR*))²`
`[D]`; if the available out-of-sample length is below `MinTRL`, the result is reported as
`INSUFFICIENT` and cannot promote.

### 3.5 FDR for feature families (`AX-10:§3.5`)

Feature admission (AX-05 §2.3) uses Benjamini–Hochberg at `P-ADM-003`; the tested family and its size
are recorded. A family that is re-tested later is counted again (the trial budget of §7 exists to keep
this number honest).

---

## 4. The promotion ladder (`AX-10:§4`)

| Rung | Name | Capital at risk | Entry requirements | Demotion triggers |
|---|---|---|---|---|
| `L0` | Idea | none | hypothesis registered (§2) with a mechanism | — |
| `L1` | Research | none | dataset built per §3.1; in-sample fit plausible; no claim yet | — |
| `L2` | **Validated research** | none | purged/embargoed OOS results; `PSR(SR*) ≥ P-LRN-005`; `PBO ≤ P-LRN-007`; positive under cost stress `P-ADM-004`; positive in ≥ `P-LRN-010` of the pre-declared regime subsets; `n_eff ≥ sample_requirement`; `MinTRL` satisfied | any of these failing at re-validation |
| `L3` | **Shadow** | none (no orders) | ≥ `P-LRN-011` days of live-data operation producing *decisions* (recorded) daily; **decision-parity** test passed against replay (§AX-11 §5.2); no data-health disqualifications in the window | parity failure; < 90 % decision coverage days |
| `L4` | **Paper** | none (simulated fills) | ≥ `P-LRN-012` days of paper execution; realised simulator-vs-model cost difference within `P-LRN-013`; ≥ `P-LRN-014` simulated round trips; refusal-rate sanity (the model is not refused by the cost gate in > `P-LRN-015` of signals) | cost divergence above band; refusal-rate anomaly |
| `L5` | **Micro-live** | `P-LRN-016` × the planned risk budget (default 0.10) | reconciliation clean for `P-LRN-017` days; zero `SEV-1`; realised cost inside the model's `p75` band; live IC within the bootstrap CI of the research IC; ≥ `P-LRN-018` realised trades | any `SEV-1`; cost band breach; IC outside CI (with the multiple-testing caveat handled by using the pre-registered threshold only) |
| `L6` | **Scaled** | full risk budget | ≥ `P-LRN-019` trades at `L5`; DSR recomputed on *live* data ≥ `P-LRN-020`; drawdown within the calibrated `q99`; operational incident rate ≤ `P-LRN-021`/month | ladder demotion per §4.4 |

**`AX-10:§4-R1`** — Rungs advance one at a time, with a written gate record (AX-14 §6) containing the
evidence artifacts. There is no "skip"; there is no "try it small to see". Skipping is the behaviour
that turns a research project into a donation.

### 4.1 Gate evidence artifact (`AX-10:§4.1`)

Each promotion produces `GateRecord(rung_from, rung_to, evidence_refs[], metrics, decision, decided_ts,
decided_by)`. `decided_by` = `AUTO` (only for demotions) or the operator's identifier (for promotions).
Promotions are **never** automatic (§4.3-R1 analog for money).

### 4.2 Time budgets (`AX-10:§4.2`)

Minimum durations exist because sample size cannot be bought with cleverness:
`P-LRN-011` (shadow) ≥ 14 days, `P-LRN-012` (paper) ≥ 21 days, `P-LRN-017` (clean reconciliation at
`L5`) ≥ 5 days. These are `[O]` with a permitted range and a stated derivation `[D]`: they are set at
the smallest duration that yields at least one full weekly cycle *and* at least `P-LRN-018`/`P-LRN-019`
observations at the expected turnover.

### 4.3 Demotion rules (`AX-10:§4.3`)

Automatic demotion by one rung when: `PSR` on the live/paper window falls below `P-LRN-030`; the CUSUM
alarm fires twice (AX-06 §6.3); realised cost exceeds the `q99` band; a `SEV-1` occurs; or the
governor's `DEFENSIVE` is triggered by a *model* trigger (as opposed to a market trigger). Demotions are
immediate and may worsen; recovery requires the same evidence as the original promotion
(**re-qualification**, not "waiting it out").

### 4.4 Operational demotion (`AX-10:§4.4`)

Independently of performance: `> P-LRN-021` `SEV-2` incidents in a month, or any unresolved `SEV-1`
older than `P-LRN-031`, moves the system to `L4` (paper) until the operational defect is closed and
verified. Rationale `[D]`: with a single operator, an unreliable system is more dangerous than a
losing one — an unreliable system is also *unmeasurable*.

---

## 5. Model registry and champions (`AX-10:§5`)

- One **champion** per horizon per family; any number of **challengers** run in shadow (never with
  capital) producing recorded decisions for comparison.
- Challenger→champion promotion happens only through §4 and only at a scheduled review (`P-LRN-040`
  cadence, monthly by default) so that the champion is stable within a window and attribution remains
  clean.
- Artifacts are immutable and referenced by hash; "latest" is not a version (`AX-03:§1.1-R3`).
- Every champion's parameters, feature versions and the calibration artifacts are recorded in one
  `ModelCard` (purpose, mechanism, training window, `n_eff`, trial count `N`, `PSR`, `PBO`, known
  failure modes, monitoring metrics with thresholds, and the kill rule).

---

## 6. Monitoring and drift (`AX-10:§6`)

Automated daily: feature PSI and availability (AX-05 §5), forecast calibration bins and Brier skill
(AX-06 §3.3), rolling IC with block-bootstrap CI, CUSUM alarms, cost-model residual, turnover versus
assumption (`N_bets` re-estimation, AX-07 §3.2), refusal composition, execution-quality table
(AX-08 §8). Weekly: a written report with deltas and the governor's state history. Quarterly: a deep
review that re-runs `CAL-GOV-01`, `CAL-COST-01`, `CAL-STP-01`, and re-examines every `T2` component
against the admission test (removal is expected and healthy: `AX-01:§6`).

**Drift → action mapping** is fixed: PSI breach ⇒ weight shrinks to zero (AX-06 §5 via reliability);
calibration breach ⇒ suspend the horizon; IC posterior below `P-MON-002` ⇒ demote (AX-05 §5);
cost residual breach ⇒ `K5` and re-fit; `N_bets` deviation > `P-LRN-050` ⇒ recompute `R`
(AX-07 §3.2) because the account's risk of ruin scales with the square root of turnover.

---

## 7. Experiment budget (`AX-10:§7`)

To keep the trial count `N` (and therefore the DSR) honest and to bound overfitting:

- At most `P-LRN-060` pre-registered hypotheses may be *completed* per calendar month; the registry
  enforces the cap (a queue, not a rejection).
- Every test is logged with its `N` contribution in a trial ledger; the DSR of any promotion uses the
  ledger's count over the relevant family (the count is never reset by re-labelling a search).
- Compute budget: heavy searches (parameter sweeps) must be declared in advance with a grid size, and
  the grid size enters `N`. An undeclared sweep invalidates any promotion that follows it
  (`AX-10:§7-R1`).

---

## 8. Decommissioning (`AX-10:§8`)

A model or feature is retired when: it fails re-qualification, its mechanism is falsified by new
evidence, its capacity falls below the minimum tradable size, or its maintenance cost exceeds its
contribution. Retirement means: champion demoted, monitoring continues for `P-LRN-070` days
(to document *why* it died, which is the asset that survives), then archival with its `ModelCard`
marked `RETIRED` and the reason recorded. Deleted code is not removed from the registry: the registry is
the institutional memory, and re-discovering a known dead end is wasted trial budget.

---

## 9. Test obligations (`AX-10:§9`)

| Area | Tests |
|---|---|
| Protocol | `T-LRN-001` (no shuffling), `T-LRN-002` (uniqueness weights applied), `T-LRN-003` (trial count = ledger count), `T-LRN-004` (post-hoc registration ⇒ exploratory) |
| Statistics | `T-LRN-005` (DSR implementation against published examples), `T-LRN-006` (PBO/CSCV implementation against a synthetic coin-flip tournament), `T-LRN-007` (SPA against a null simulation), `T-LRN-008` (MinTRL) |
| Ladder | `T-LRN-010` (each gate refuses without its evidence; a promotion without a `GateRecord` is impossible), `T-LRN-011` (demotion is automatic and immediate), `T-LRN-012` (re-qualification after demotion) |
| Registry | `T-LRN-013` (artifact immutability/lookup by hash), `T-LRN-014` (`ModelCard` completeness) |
| Budget | `T-LRN-015` (hypothesis cap enforced), `T-LRN-016` (undeclared sweep ⇒ promotion invalidated) |
