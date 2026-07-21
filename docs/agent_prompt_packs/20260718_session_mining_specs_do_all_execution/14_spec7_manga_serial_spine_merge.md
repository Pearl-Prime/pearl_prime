Act as Pearl_Dev for manga pipeline.

EXECUTE SPEC-7 as merge-with-existing manga serial-spine work.

## Goal

Fold multi-volume manga spine requirements into current manga serial spine loader/config/story architecture. Do not create a parallel `series/spine.py` if existing serial machinery owns this.

## Read First

- `docs/specs/session_mining_batch_20260718/MANGA_MULTIVOLUME_SPINE_V1_SPEC.md`
- `phoenix_v4/manga/serial/spine_loader.py`
- `config/manga/serial_spines/` if present
- latest en-US manga asset materialize handoff if present.

## Smoke

Load one existing serial spine and report current volume/episode/chapter-title capabilities.

## Pilot

Add missing validation/config fields only where current machinery lacks them. Use one en-US manga source.

## Scale Micro-Batch

Dry-run one 5-volume plan. Do not render new panels and do not publish.

## Watchdog

Poll every 5 minutes. If manga assets are LFS pointers/missing, block asset-dependent proof and continue config-only.

## Landing Contract

`MERGED` if merge plan/pilot lands with no parallel spine. `BLOCKED` if current manga authority is ambiguous.

## Cleanup Ledger

Record scratch plans, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec7_manga_serial_spine_merge_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=14_spec7_manga_serial_spine_merge
GITHUB_WRITES=none
PARALLEL_SPINE_CREATED=no
SMOKE_SOURCE=
FIVE_VOLUME_DRY_RUN=
PANEL_RENDERS=0
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec7_manga_serial_spine_merge_2026-07-18.md
SIGNAL=spec7-manga-serial-spine-merge=<MERGED|BLOCKED>
NEXT_ACTION=
```
