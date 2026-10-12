# AXIOM `contracts/` — machine-checkable handoff artifacts

These files are the parts of the design that a compiler, a linter or a test runner can verify. They are
generated/validated rather than narrated, so the implementation team starts from executable truth
instead of prose.

| File | Role | Authority | Verification |
|---|---|---|---|
| `build_registry.py` | single source of truth for every tunable value (one table → both artifacts) | AX-15 §0-R1, AX-13 §6 | `python3 contracts/build_registry.py --check` must print `registry check: OK` |
| `config.default.yaml` | the default configuration, grouped by plane, every key commented with its parameter id, class, unit, calibration or owner-input reference | AX-13 §6 | loads with a YAML parser; class-`O` keys are `null` on purpose (system stays OFF) |
| `registry.json` | machine-readable parameter registry (id, class, unit, default, range, calibration ref, owner input, note) consumed by the config loader | AX-15 §12 | every `P-*` id in the documents resolves here; drift fails `--check` |
| `sql/schema.sql` | local store DDL: L0 segment index, L1 curated tables, L2 derived tables, execution/audit tables, journal with append-only triggers, operator views | AX-04 §6, AX-03 §5.3, ADR-005 | `sqlite3 :memory: < sql/schema.sql` must succeed |
| `schemas/*.json` | JSON Schema (2020-12) for every artifact crossing a module or process boundary | AX-03 §1, AX-13 §3 | each file parses; `common.json` holds shared primitive types (`ulid`, `hash`, `decimal`, `ts_ms`, …) |

## Loader rules (AX-13 §6)

The configuration loader must refuse, loudly and before any network call:

1. an unknown key, or a key absent from `registry.json`;
2. a class-`C` value without a resolvable `calibration_ref`;
3. a class-`O` value that is present without an `EV-PARAM-CHANGE` record naming the owner and a reason
   (values are `null` until the owner supplies them — AX-15 §9);
4. a value outside its registry `range`;
5. **any class-`V` value in the config file** — venue facts live only in `venue_profile.json`, produced
   by the conformance harness (AX-02 §10);
6. a registry entry whose class is `V` at all (the generator itself refuses to emit one).

## Why there is a generator

Two artifacts that must agree (human-readable config and machine-readable registry) will disagree the
first time someone edits one of them by hand. The generator makes the disagreement impossible to merge:
the check mode fails the build instead (AX-15 §11.4, `T-CFG-001`).

## What is deliberately *not* here

* No secrets: `ops.notify_destination_ref` is a reference into the OS secret store, never a literal
  (AX-12 §5.2, `T-SEC-001`).
* No venue facts: tick sizes, fees, rate limits, bands and precisions are `[V-PROBE]` values and come
  from `venue_profile.json`.
* No research datasets: `lnp` artifacts (datasets, folds, model files) are content-addressed and live in
  the artifact store described by `EV-BOOT`/`ModelCard`, not in this directory.
