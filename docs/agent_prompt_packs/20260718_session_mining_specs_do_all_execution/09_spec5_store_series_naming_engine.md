Act as Pearl_Dev with Pearl_Editor support.

EXECUTE SPEC-5: store series naming engine pilot.

## Goal

Extend existing naming machinery to generate non-generic store series names for non-Waystream brands.

## Read First

- `docs/specs/session_mining_batch_20260718/STORE_SERIES_NAMING_ENGINE_V1_SPEC.md`
- `phoenix_v4/naming/generator.py`
- current catalog/brand plan writers.

## Smoke

Generate series names for one pilot brand without writing catalog files.

## Pilot

Implement series naming mode and tests for one brand. Reject generic names.

## Scale Micro-Batch

Dry-run all 36 non-Waystream brands, write report only unless operator/PM explicitly authorized file updates in-lane.

## Watchdog

Poll every 5 minutes. If dry-run grows slow, batch 5 brands at a time.

## Landing Contract

`MERGED` if pilot engine/tests land and dry-run report exists. `BLOCKED` if brand/catalog source is ambiguous.

## Cleanup Ledger

Record dry-run outputs, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec5_store_series_naming_engine_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=09_spec5_store_series_naming_engine
GITHUB_WRITES=none
PILOT_BRAND=
SERIES_NAMES_GENERATED=
GENERIC_REJECTS=
TESTS_RUN=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec5_store_series_naming_engine_2026-07-18.md
SIGNAL=spec5-store-series-naming-engine=<MERGED|BLOCKED>
NEXT_ACTION=
```
