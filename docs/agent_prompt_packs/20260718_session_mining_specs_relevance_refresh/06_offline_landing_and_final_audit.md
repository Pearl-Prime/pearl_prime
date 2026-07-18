Act as Pearl_PM.

EXECUTE lane 06: offline landing and final audit.

## Goal

Validate the refreshed specs are safe to land offline, produce final audit/handoff, and optionally push to PearlStar offline. Do not write to GitHub.

## Read First

- all lane 01-05 handoffs;
- refreshed spec/index files;
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/SPEC_REFRESH_CHANGELOG.md`.

## Smoke

Validate:

- refreshed `SPEC_INDEX.md` has all 9 specs and 10 ready-now briefs accounted for;
- no item lacks a classification;
- no implementation files changed.

## Pilot

Run `git diff --check` on changed spec/proof/handoff paths. Verify exact changed-file list.

## Scale Micro-Batch

If safe and PearlStar offline is configured, create/push an offline branch:

`offline/session-mining-specs-relevance-refresh-20260718`

Allowed changed paths:

- `docs/specs/` session-mining spec files;
- `artifacts/qa/session_mining_specs_relevance_refresh_20260718/`;
- `artifacts/coordination/handoffs/session_mining_specs_*_2026-07-18.md`.

If PearlStar is not reachable, leave local artifacts and branch/patch bundle.

Write:

`artifacts/qa/session_mining_specs_relevance_refresh_20260718/FINAL_SPEC_REFRESH_AUDIT.md`

## Watchdog

Poll every 5 minutes. If `git status` is slow, use explicit file list from lane 05 and `git diff --name-only`. If PearlStar push stalls, stop and preserve a bundle/patch.

## Landing Contract

`PASS` if all specs/briefs are classified, stale claims patched or recorded, no implementation files changed, and final audit/handoff exists.

`BLOCKED` if there are unresolved operator decisions, unsafe broad diffs, or missing source artifacts.

## Cleanup Ledger

Confirm:

- no unrelated dirty files touched;
- no scratch scripts outside proof root;
- no background jobs;
- any local/offline branch recorded;
- any PearlStar ref recorded;
- archive left intact.

## Handoff

Write `artifacts/coordination/handoffs/session_mining_specs_relevance_refresh_final_2026-07-18.md`.

## CLOSEOUT_RECEIPT

```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM
LANE=06_offline_landing_and_final_audit
GITHUB_WRITES=none
PEARLSTAR_REF=
SOURCE_COMMIT=4e314f94bb
SPECS_AUDITED=9
READY_NOW_BRIEFS_AUDITED=10
KEEP=
REFRESH=
MERGE_WITH_EXISTING=
RETIRE=
BLOCKED_NEEDS_OPERATOR=
SPECS_UPDATED=
SPEC_INDEX_UPDATED=
IMPLEMENTATION_FILES_CHANGED=0
FINAL_AUDIT=artifacts/qa/session_mining_specs_relevance_refresh_20260718/FINAL_SPEC_REFRESH_AUDIT.md
FINAL_VERDICT=<PASS|BLOCKED>
CLEANUP_COMPLETE=
HANDOFF=artifacts/coordination/handoffs/session_mining_specs_relevance_refresh_final_2026-07-18.md
SIGNAL=session-mining-specs-relevance-refresh-final=<PASS|BLOCKED>
NEXT_ACTION=
```
