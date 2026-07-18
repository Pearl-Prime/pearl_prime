Act as Pearl_PM with Pearl_Architect support.

EXECUTE lane 02: current SSOT and active workstream relevance audit.

## Goal

Classify each of the 9 specs and 10 ready-now briefs against current program state, active workstreams, subsystem authority, and GitHub/PearlStar reality.

## Read First

- `docs/PROGRAM_STATE.md`
- `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_SOURCE_TRUTH.md`
- all 10 source spec files.

## Smoke

Classify 3 items:

- `ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md`
- `CATALOG_GPU_DISPATCHER_V1_SPEC.md`
- ready-now `RN-2 thesis-bank re-key`.

## Pilot

Classify all 9 specs.

## Scale Micro-Batch

Classify all 9 specs and all 10 ready-now briefs. Write:

`artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_RELEVANCE_MATRIX.tsv`

Required columns:

`item_id,item_type,title,current_status,classification,reason,current_authority,current_overlap_or_dependency,still_high_value,stale_claims,operator_decision_needed,next_action`

Required checks:

- Does current SSOT say the problem still exists?
- Does an active workstream already own it?
- Is it blocked by GitHub suspension, credentials, PearlStar, R2, or operator approval?
- Is it implementation work, spec work, or already executed?
- Does the item still serve current best goals?

## Watchdog

Poll every 5 minutes. If active workstream scan is too large, use targeted `rg` for spec names, subsystem names, and file paths.

## Landing Contract

`MERGED` if all 19 items are classified with evidence.

`BLOCKED` if SSOT/active workstream files cannot be read.

## Cleanup Ledger

Record scratch TSVs/scripts. Remove scratch outside proof root.

## Handoff

Write `artifacts/coordination/handoffs/session_mining_specs_relevance_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=02_current_ssot_and_active_workstream_relevance
GITHUB_WRITES=none
ITEMS_AUDITED=19
KEEP=
REFRESH=
MERGE_WITH_EXISTING=
RETIRE=
BLOCKED_NEEDS_OPERATOR=
RELEVANCE_MATRIX=artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_RELEVANCE_MATRIX.tsv
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_relevance_2026-07-18.md
SIGNAL=session-mining-specs-relevance=<MERGED|BLOCKED>
NEXT_ACTION=
```
