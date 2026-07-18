Act as Pearl_PM.

EXECUTE lane 01: spec artifact truth lock.

## Goal

Prove exactly what spec artifacts exist, where they live, what commit/branch contains them, and whether the archive/local-branch/docs copies match. Do not edit specs in this lane.

## Read First

- `/Users/ahjan/phoenix_workspace_archive/session_idea_mining_20260718/specs/SPEC_INDEX.md`
- `git show --stat --oneline 4e314f94bb`
- `git show --name-only 4e314f94bb`
- `docs/agent_prompt_packs/20260718_session_mining_specs_relevance_refresh/INDEX.md`

## Smoke

Verify these three files from the archive and commit:

- `SPEC_INDEX.md`
- `ATOM_SURFACE_TAXONOMY_AND_VARIATION_MANIFEST_V1_SPEC.md`
- `PROSE_INTEGRITY_VALIDATOR_SET_V1_SPEC.md`

Confirm path, byte count, sha256, and whether the same file exists in `docs/specs/`.

## Pilot

Verify all 10 spec-set files from archive and commit `4e314f94bb`.

## Scale Micro-Batch

Build the full source truth report for all files:

`artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_SOURCE_TRUTH.md`

Include:

- archive path;
- local branch;
- commit;
- base SHA;
- file list;
- sha256 per file;
- any mismatch between archive/local branch/docs path;
- whether GitHub push is blocked.

## Watchdog

Poll every 5 minutes. If `git show` is slow or blocked, use archive files and record branch verification as `BLOCKED_GIT_LOCAL`.

## Landing Contract

`MERGED` if source truth is complete for all 10 files.

`BLOCKED` if archive or commit is missing and no equivalent source can be found.

## Cleanup Ledger

Record temporary checksum files. Remove scratch files outside proof root.

## Handoff

Write `artifacts/coordination/handoffs/session_mining_specs_truth_lock_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=01_spec_artifact_truth_lock
GITHUB_WRITES=none
ARCHIVE_EXISTS=
SOURCE_COMMIT_EXISTS=
LOCAL_BRANCH_EXISTS=
FILES_VERIFIED=
MISMATCHES=
SOURCE_TRUTH=artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_SOURCE_TRUTH.md
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_truth_lock_2026-07-18.md
SIGNAL=session-mining-specs-truth-lock=<MERGED|BLOCKED>
NEXT_ACTION=
```
