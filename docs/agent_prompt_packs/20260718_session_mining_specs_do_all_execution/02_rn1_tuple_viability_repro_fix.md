Act as Pearl_Dev.

EXECUTE RN-1: tuple viability false `NO_STORY_POOL` repro-first fix.

## Goal

Patch tuple viability only if the current code still false-blocks cells where registry/generic fallback story pools are actually usable.

## Read First

- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md` RN-1 row
- `phoenix_v4/gates/check_tuple_viability.py`
- registry resolver code paths referenced by current tests

## Smoke

Create a current repro. If no false `NO_STORY_POOL` repro exists, do not patch; write `MERGED_NOOP_CURRENTLY_FIXED`.

## Pilot

If repro exists, patch the narrow gate so it consults current registry/generic fallback rules before emitting `NO_STORY_POOL`. Add a targeted unit test.

## Scale Micro-Batch

Run the targeted test plus one existing tuple viability/gating suite. Do not run catalog scale.

## Watchdog

Poll every 5 minutes. If repro search exceeds 10 minutes, stop with `BLOCKED_REPRO_NOT_DERIVED`.

## Landing Contract

`MERGED` if repro is proven fixed or no-op proven. `BLOCKED` if repro is ambiguous or tests fail.

## Cleanup Ledger

Record test artifacts, scratch files, worktrees/branches, and jobs.

## Handoff

Write `artifacts/coordination/handoffs/rn1_tuple_viability_repro_fix_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=02_rn1_tuple_viability_repro_fix
GITHUB_WRITES=none
REPRO_FOUND=
PATCH_APPLIED=
TESTS_RUN=
RESULT=<MERGED|MERGED_NOOP_CURRENTLY_FIXED|BLOCKED>
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/rn1_tuple_viability_repro_fix_2026-07-18.md
SIGNAL=rn1-tuple-viability-repro-fix=<MERGED|BLOCKED>
NEXT_ACTION=
```
