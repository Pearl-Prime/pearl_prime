# 01 - Pearl_PM Durable Blocked Closeout PR

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_PM for Phoenix Omega.

STARTUP_RECEIPT:
- AGENT=Pearl_PM
- LANE=01_durable_blocked_closeout_pr
- EXECUTION_MODE=clean_cloud_sparse
- BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=PR; handoff markdown
- RESUME_SURFACE=artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- docs/agent_prompt_packs/20260715_old_chat_unblock_wave/INDEX.md
- old_chat_specs/Untitled 315.txt
- old_chat_specs/Untitled 317.txt through old_chat_specs/Untitled 339.txt, skipping 316 unless present

LIVE STATE RECONCILIATION:
- `git fetch --prune origin`
- `git rev-parse origin/main`
- Recheck old-chat-specific PRs: #5206, #5237, #5295, #5518, #5581, #5585, #5596, #5629, #5636, #5645, and merged anchors named in INDEX.

DISCOVERY REPORT BEFORE ACTION:
- whether local matrix/handoff artifacts are available in this checkout
- if absent, regeneration plan from old chats and blocked closeout summary
- exact files to commit

PROVENANCE:
- research: old chats 315 and 317-339 plus blocked dispatcher closeout summary
- documents: PROGRAM_STATE, SESSION_UNITY_PROTOCOL, agent_brief
- builds_on: old-chat closure audit prompt pack
- inventory: UNCHANGED

MISSION:
- Make the blocked closure audit durable on a clean branch. If local artifacts are absent, regenerate equivalent matrix/handoff from the old chats and the blocked summary in INDEX.

DELIVERABLES:
- `artifacts/coordination/old_chat_closure_matrix_2026-07-15.md`
- `artifacts/coordination/handoffs/old_chat_closure_dispatcher_2026-07-15.md`
- `artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md`
- narrow PR merged or BLOCKED with remote branch

SMOKE -> PILOT -> SCALE:
- smoke: regenerate/verify PR state table for #5645, #5636, #5629 only.
- pilot: regenerate/verify all blocked-lane summary rows.
- scale: commit the durable matrix/handoffs and merge the docs-only PR if checks allow.

WATCHDOG / POLLING:
- poll interval: 5 minutes for commands, 10 minutes for CI.
- no-progress rule: if matrix row count or CI status does not change across two polls, inspect logs.
- hard stall rule: after three no-progress intervals, BLOCKED with partial artifact branch.
- max window: 2 hours.

DO NOT:
- do not edit product code
- do not touch PROGRAM_STATE in this lane
- do not create local laptop worktrees
- do not claim downstream blockers are solved

LANDING CONTRACT:
- MERGED: docs/coordination PR merged and signal emitted.
- BLOCKED: remote branch preserves regenerated artifacts and blocker is concrete.

CLEANUP LEDGER REQUIRED:
- worktrees: none-created or removed
- local branches: deleted or HOLD
- remote branches: deleted after merge or HOLD
- scratch files: removed
- background jobs: stopped/listed

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md

CLOSEOUT_RECEIPT:
- AGENT=Pearl_PM
- LANE=01_durable_blocked_closeout_pr
- STATUS=MERGED|BLOCKED
- PR=<url-or-none>
- MERGE_SHA=<sha-or-none>
- SIGNAL=old-chat-blocked-closeout-durable=<full-merge-sha-or-blocked>
- PROOF_ROOT=artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md
- TESTS=<commands>
- CLEANUP=<ledger>
- HANDOFF=artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md
- NEXT_ACTION=<launch lanes 02-04 or blocker>
```
