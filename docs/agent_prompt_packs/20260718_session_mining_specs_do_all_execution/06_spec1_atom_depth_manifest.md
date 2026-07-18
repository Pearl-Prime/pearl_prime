Act as Pearl_Dev with Pearl_Architect support.

EXECUTE SPEC-1: atom depth/source/variation manifest.

## Goal

Extend existing atom coverage/inventory machinery into a measurement-only manifest for atom job, depth, reader-state entry/exit, source/provenance, story/exercise/tool distinctions, and variation sufficiency. Do not rewrite atoms.

## Read First

- `docs/specs/session_mining_batch_20260718/ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md`
- `scripts/inventory/atom_coverage_audit.py`
- latest atom audit/repair proof roots if present.

## Smoke

Measure one known cell and emit a small matrix. Include Ch1/corporate burnout if available.

## Pilot

Implement reusable classification/manifest code and run across one persona/topic family.

## Scale Micro-Batch

Run across bounded en-US production-scope cells only. Do not run all catalog unless smoke/pilot pass and runtime is safe.

## Watchdog

Poll every 5 minutes. If inventory hangs, reduce to one root and emit a partial manifest.

## Landing Contract

`MERGED` if manifest code/proof lands and no atom text is edited. `BLOCKED` if classifier cannot reconcile current atom types.

## Cleanup Ledger

Record scratch matrices, branches, jobs.

## Handoff

Write `artifacts/coordination/handoffs/spec1_atom_depth_manifest_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=06_spec1_atom_depth_manifest
GITHUB_WRITES=none
CELLS_MEASURED=
ATOM_TEXT_EDITED=no
MANIFEST_PATH=
TESTS_RUN=
PEARLSTAR_REF=
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/spec1_atom_depth_manifest_2026-07-18.md
SIGNAL=spec1-atom-depth-manifest=<MERGED|BLOCKED>
NEXT_ACTION=
```
