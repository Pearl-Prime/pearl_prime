Act as Pearl_Int with Pearl_Dev support.

EXECUTE SPEC-3: catalog GPU dispatcher dry-run.

## Goal

Create or refresh a dry-run work discovery/queue feeder layer aligned to Conductor V3, PearlStar, V5 queue, image/video/social pipelines, and blocked GitHub reality. Do not enqueue live GPU work unless explicitly authorized.

## Read First

- `docs/specs/session_mining_batch_20260718/CATALOG_GPU_DISPATCHER_V1_SPEC.md`
- `docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`
- current PearlStar/offline handoffs
- current image/video/social pipeline specs.

## Smoke

Discover pending render work for one family in dry-run mode. Do not enqueue.

## Pilot

Implement normalized dry-run `RenderJob` discovery for two families.

## Scale Micro-Batch

Dry-run all configured families and write priority queue plan. No live ComfyUI/pscli/queue writes unless a separate operator authorization is present.

## Watchdog

Poll every 5 minutes. If a family scan stalls, skip that family with `DISCOVERY_TIMEOUT` and continue.

## Landing Contract

`MERGED` if dry-run discovery and tests/report land. `BLOCKED` if queue substrate/auth is required for even dry-run.

## Cleanup Ledger

Record temp queue plans, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec3_catalog_gpu_dispatcher_dryrun_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Int
LANE=12_spec3_catalog_gpu_dispatcher_dryrun
GITHUB_WRITES=none
LIVE_QUEUE_WRITES=none
FAMILIES_DISCOVERED=
DRY_RUN_JOBS=
TESTS_RUN=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec3_catalog_gpu_dispatcher_dryrun_2026-07-18.md
SIGNAL=spec3-catalog-gpu-dispatcher-dryrun=<MERGED|BLOCKED>
NEXT_ACTION=
```
