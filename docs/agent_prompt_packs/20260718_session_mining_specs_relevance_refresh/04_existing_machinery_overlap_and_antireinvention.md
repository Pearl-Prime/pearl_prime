Act as Pearl_Dev.

EXECUTE lane 04: existing machinery overlap and anti-reinvention audit.

## Goal

Confirm each implementation spec extends or reconciles with existing repo machinery rather than rebuilding it. Identify stale file paths, already-built validators, duplicate systems, and dependency mistakes.

## Read First

- all 9 source specs;
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_RELEVANCE_MATRIX.tsv`;
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/BEST_WORK_ALIGNMENT_MATRIX.tsv`.

## Required Path Checks

Verify mentioned paths when present:

- `phoenix_v4/naming/generator.py`
- `phoenix_v4/quality/register_gate.py`
- `phoenix_v4/planning/enrichment_select.py`
- `scripts/manga/assemble_from_bank.py`
- `scripts/inventory/atom_coverage_audit.py`
- `scripts/marketing/build_marketing_feed.py`
- `docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`
- `docs/specs/LFS_TO_R2_OFFLOAD_V1_SPEC.md`
- `docs/PEARL_ANIMATOR_FACELESS_SHORTS_SPEC_2026-07-18.md`
- `docs/agent_prompt_packs/20260718_deterministic_social_media_system_100pct/`
- `docs/agent_prompt_packs/20260718_non_manga_image_inventory_usage_audit/`

## Smoke

Audit overlap for 3 specs:

- naming engine;
- artifacts retention;
- prose integrity validators.

## Pilot

Audit all 9 specs for path accuracy and "reconcile don't rebuild" correctness.

## Scale Micro-Batch

Audit all 9 specs plus 10 ready-now briefs. Write:

`artifacts/qa/session_mining_specs_relevance_refresh_20260718/OVERLAP_RECONCILE_LEDGER.tsv`

Required columns:

`item_id,path_or_system,exists,current_owner,overlap_type,reconcile_action,stale_or_wrong_claim,required_patch,notes`

Must explicitly check and fix/report:

- the "spec #8 PS_QUEUE_DSN creds" numbering/dependency inconsistency;
- any ready-now brief whose fix already landed;
- any spec that duplicates deterministic social/video/image-bank systems from 2026-07-18;
- any spec that duplicates the current atom/story/exercise repair gates;
- any implementation path that no longer exists.

## Watchdog

Poll every 5 minutes. If broad `rg` is slow, search by explicit path and spec title.

## Landing Contract

`MERGED` if every item has an overlap/reconcile row and every stale claim has a required patch or retirement.

`BLOCKED` if the source specs cannot be mapped to current repo systems.

## Cleanup Ledger

Record scratch command outputs. Remove temp files outside proof root.

## Handoff

Write `artifacts/coordination/handoffs/session_mining_specs_overlap_reconcile_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Dev
LANE=04_existing_machinery_overlap_and_antireinvention
GITHUB_WRITES=none
ITEMS_AUDITED=19
PATHS_CHECKED=
STALE_CLAIMS_FOUND=
DUPLICATE_SYSTEM_RISKS=
OVERLAP_LEDGER=artifacts/qa/session_mining_specs_relevance_refresh_20260718/OVERLAP_RECONCILE_LEDGER.tsv
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_overlap_reconcile_2026-07-18.md
SIGNAL=session-mining-specs-overlap-reconcile=<MERGED|BLOCKED>
NEXT_ACTION=
```
