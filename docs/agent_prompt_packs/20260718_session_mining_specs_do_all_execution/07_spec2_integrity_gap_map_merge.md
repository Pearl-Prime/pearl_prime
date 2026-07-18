Act as Pearl_Dev.

EXECUTE SPEC-2 as merge-with-existing gap map, not a new parallel validator.

## Goal

Map proposed prose integrity checks to existing gates and implement only proven missing gaps in existing gate modules.

## Read First

- `docs/specs/session_mining_batch_20260718/PROSE_INTEGRITY_VALIDATOR_SET_V1_SPEC.md`
- `phoenix_v4/quality/register_gate.py`
- existing atom/story/exercise/reader gate tests.

## Smoke

Produce a gap map for PI-1 through PI-5 against existing gates.

## Pilot

Implement at most one missing check if proven absent and low-risk. Otherwise land report-only `MERGED_NOOP`.

## Scale Micro-Batch

Run relevant existing gate tests and one bounded render/read proof if code changed.

## Watchdog

Poll every 5 minutes. If false-block risk appears, stop before adding a hard gate.

## Landing Contract

`MERGED` if gap map lands and any patch is tested. `BLOCKED` if gate ownership conflicts.

## Cleanup Ledger

Record scratch reports, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec2_integrity_gap_map_merge_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=07_spec2_integrity_gap_map_merge
GITHUB_WRITES=none
GAPS_MAPPED=
NEW_PARALLEL_MODULE_CREATED=no
PATCH_APPLIED=
TESTS_RUN=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec2_integrity_gap_map_merge_2026-07-18.md
SIGNAL=spec2-integrity-gap-map-merge=<MERGED|BLOCKED>
NEXT_ACTION=
```
