Act as Pearl_Dev.

EXECUTE RN-6: boundary-aware word clamp repair.

## Goal

Verify whether the renderer/composer still clamps mid-sentence or mid-atom. If so, repair it so truncation lands on safe beat/atom/chapter boundaries.

## Read First

- `docs/specs/session_mining_batch_20260718/SPEC_INDEX.md` RN-6 row
- `phoenix_v4/rendering/book_renderer.py`
- current composer/render word-budget paths

## Smoke

Derive a fresh repro with a tiny fixture. Do not reuse stale 25,020/21,634 counts as proof.

## Pilot

Patch only boundary selection. Add a test proving clamp stops on sentence/atom/beat boundary and never cuts placeholders or trace spans.

## Scale Micro-Batch

Run the targeted test and one bounded production-ish render cell. No catalog scale.

## Watchdog

Poll every 5 minutes. If render exceeds 10 minutes, degrade to fixture-only and mark production render `BLOCKED_TIMEOUT`.

## Landing Contract

`MERGED` if fresh repro is fixed or no-op proven. `BLOCKED` if current renderer behavior cannot be safely changed.

## Cleanup Ledger

Record render dirs, scratch outputs, branches, and jobs.

## Handoff

Write `artifacts/coordination/handoffs/rn6_boundary_aware_word_clamp_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=03_rn6_boundary_aware_word_clamp
GITHUB_WRITES=none
REPRO_FOUND=
PATCH_APPLIED=
BOUNDARY_TEST=
BOUNDED_RENDER=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/rn6_boundary_aware_word_clamp_2026-07-18.md
SIGNAL=rn6-boundary-aware-word-clamp=<MERGED|BLOCKED>
NEXT_ACTION=
```
