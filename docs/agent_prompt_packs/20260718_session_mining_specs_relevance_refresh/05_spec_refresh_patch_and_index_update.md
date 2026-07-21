Act as Pearl_Architect with Pearl_PM.

EXECUTE lane 05: patch specs and update index.

## Goal

Apply the smallest correct doc/spec updates required by lanes 02-04. Do not implement systems. Do not push to GitHub.

## Read First

- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_RELEVANCE_MATRIX.tsv`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/BEST_WORK_ALIGNMENT_MATRIX.tsv`
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/OVERLAP_RECONCILE_LEDGER.tsv`
- all source specs from archive or local branch.

## Patch Policy

For each item:

- `KEEP`: add/update current-status metadata only if useful.
- `REFRESH`: patch the spec so it reflects current best work and correct dependencies.
- `MERGE_WITH_EXISTING`: update `SPEC_INDEX.md` to say where it merges; do not keep it as a standalone execution target unless still needed.
- `RETIRE`: mark retired in `SPEC_INDEX.md`; do not delete archive.
- `BLOCKED_NEEDS_OPERATOR`: add an operator decision line with recommended default and reason.

Any updated spec must include:

- current relevance classification;
- current source truth;
- "reconcile, do not rebuild" notes;
- acceptance labels that distinguish structural pass, operator-read pass, and production/public-release authorization;
- no GitHub-write assumption while account remains blocked.

## Smoke

Patch only `SPEC_INDEX.md` and one high-risk spec. Validate diff.

## Pilot

Patch all specs classified `REFRESH` in the Pearl Prime/quality cluster.

## Scale Micro-Batch

Patch all required specs and index. Write:

`artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_REFRESH_CHANGELOG.md`

## Watchdog

Poll every 5 minutes. If edits become broad, stop after the current spec and write `BLOCKED_UNSAFE_DOC_BATCH` with exact files.

## Landing Contract

`MERGED` if refreshed spec/index files validate, changed files match the matrix, and no implementation code is edited.

`BLOCKED` if the audit demands operator choices before safe patching.

## Cleanup Ledger

Record worktree/branch/scratch files. Do not touch unrelated dirty files. Use explicit file adds only if committing.

## Handoff

Write `artifacts/coordination/handoffs/session_mining_specs_refresh_patch_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_Architect
LANE=05_spec_refresh_patch_and_index_update
GITHUB_WRITES=none
SPECS_UPDATED=
INDEX_UPDATED=
SPECS_RETIRED=
SPECS_MERGED_WITH_EXISTING=
OPERATOR_DECISIONS_NEEDED=
CHANGELOG=artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_REFRESH_CHANGELOG.md
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_refresh_patch_2026-07-18.md
SIGNAL=session-mining-specs-refresh-patch=<MERGED|BLOCKED>
NEXT_ACTION=
```
