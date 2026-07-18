# 06 - Pearl_PM State Router Update After Unblock

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_PM for Phoenix Omega.

STARTUP_RECEIPT:
- AGENT=Pearl_PM
- LANE=06_state_router_update_after_unblock
- EXECUTION_MODE=clean_cloud_checkout
- BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=PR; handoff markdown
- RESUME_SURFACE=artifacts/coordination/handoffs/06_state_router_update_after_unblock_2026-07-15.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/DOCS_INDEX.md
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- handoffs from lanes 01-05

DEPENDENCY GATES:
- Require terminal signals from lanes 01-05.
- If missing, STAND DOWN and emit BLOCKED.

LIVE STATE RECONCILIATION:
- Re-fetch origin/main.
- Recheck #5645, #5636, #5629, #5206, #5237, #5295, #5518.
- Recheck whether cleanup lane changed worktree/branch state.

DISCOVERY REPORT BEFORE ACTION:
- PROGRAM_STATE deltas that are now safe
- ACTIVE_WORKSTREAMS rows to update/close
- router/hygiene text to update, if not already adequate
- hot-file collision check

PROVENANCE:
- research: durable closeout artifacts and lanes 01-05 handoffs
- documents: PROGRAM_STATE, SESSION_UNITY_PROTOCOL, agent_brief
- builds_on: router v4 cleanup/landing contract
- inventory: UNCHANGED

MISSION:
- Update durable state only after clean successor surfaces exist, so future agents stop requeueing stale old-chat work.

SMOKE -> PILOT -> SCALE:
- smoke: one no-risk stale PR/state correction.
- pilot: PROGRAM_STATE plus one workstream row.
- scale: remaining state/router cleanup after smoke/pilot diff passes.

WATCHDOG / POLLING:
- poll interval: 5 minutes for tests, 10 minutes for CI.
- no-progress rule: inspect logs after two unchanged polls.
- hard stall rule: BLOCKED after three no-progress intervals with branch/check evidence.
- max window: 3 hours.

DO NOT:
- do not rewrite PROGRAM_STATE wholesale
- do not claim old-chat 100% completion unless lane 07 verifies it
- do not edit subsystem authority maps broadly

LANDING CONTRACT:
- MERGED: state/router PR merged.
- BLOCKED: remote branch preserves docs diff and exact blocker.

CLEANUP LEDGER REQUIRED:
- worktrees: none-created or removed
- branches: deleted or HOLD
- remote branches: deleted after merge or HOLD
- scratch files: removed
- background jobs: stopped/listed
- stale rows: updated or named follow-up

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/06_state_router_update_after_unblock_2026-07-15.md

CLOSEOUT_RECEIPT:
- AGENT=Pearl_PM
- LANE=06_state_router_update_after_unblock
- STATUS=MERGED|BLOCKED
- PR=<url-or-none>
- MERGE_SHA=<sha-or-none>
- SIGNAL=old-chat-state-update-terminal=<full-merge-sha-or-blocked>
- PROOF_ROOT=artifacts/coordination/handoffs/06_state_router_update_after_unblock_2026-07-15.md
- TESTS=<commands/checks>
- CLEANUP=<ledger>
- HANDOFF=artifacts/coordination/handoffs/06_state_router_update_after_unblock_2026-07-15.md
- NEXT_ACTION=<launch lane 07 or blocker>
```
