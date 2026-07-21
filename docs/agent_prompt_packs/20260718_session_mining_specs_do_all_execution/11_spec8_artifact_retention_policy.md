Act as Pearl_DevOps.

EXECUTE SPEC-8: artifact retention/offload policy dry-run.

## Goal

Extend existing LFS-to-R2/offload policy with retention classification, dry-run pruning, pointer manifests, and owner signoff. Do not delete artifacts.

## Read First

- `docs/specs/session_mining_batch_20260718/ARTIFACTS_RETENTION_POLICY_V1_SPEC.md`
- `docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md`
- `.gitattributes`

## Smoke

Classify one artifact family as `REGENERABLE`, `DURABLE`, or `EPHEMERAL` in dry-run report only.

## Pilot

Create retention manifest schema and dry-run checker. Do not offload or delete.

## Scale Micro-Batch

Dry-run classify top artifact families by size. Any real prune/offload remains operator-gated.

## Watchdog

Poll every 5 minutes. If size scan is slow, use bounded top-level `du` and stop at report.

## Landing Contract

`MERGED` if dry-run manifest/checker lands and no deletion occurs. `BLOCKED` if artifact authority is ambiguous.

## Cleanup Ledger

Record size scans, temp manifests, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec8_artifact_retention_policy_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_DevOps
LANE=11_spec8_artifact_retention_policy
GITHUB_WRITES=none
FILES_DELETED=0
REAL_OFFLOADS=0
FAMILIES_CLASSIFIED=
DRY_RUN_RECLAIMABLE_BYTES=
TESTS_RUN=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec8_artifact_retention_policy_2026-07-18.md
SIGNAL=spec8-artifact-retention-policy=<MERGED|BLOCKED>
NEXT_ACTION=
```
