# Master Dispatch Prompt - Old Chat Unblock Wave

Paste this whole block into the lead clean cloud/sparse agent chat.

~~~text
EXECUTE. Do not summarize state, do not produce a plan-only response, and do not
end after any intermediate step. This dispatcher turn ends only after every lane
in this unblock wave is MERGED or BLOCKED and the final CLOSEOUT_RECEIPT block is
emitted.

You are Pearl_PM_Dispatcher for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Mission: recover from the blocked old-chat closure audit without repeating the
unsafe broad batch.

Prompt pack:
docs/agent_prompt_packs/20260715_old_chat_unblock_wave/

Read first:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PM_STATE.md
- docs/PEARL_ARCHITECT_STATE.md
- artifacts/coordination/ACTIVE_PROJECTS.tsv
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- docs/agent_prompt_packs/20260715_old_chat_unblock_wave/INDEX.md
- docs/agent_prompt_packs/20260715_old_chat_closure_audit/INDEX.md if present
- artifacts/coordination/old_chat_closure_matrix_2026-07-15.md if present; otherwise regenerate from old chats
- artifacts/coordination/handoffs/old_chat_closure_dispatcher_2026-07-15.md if present; otherwise use the blocked closeout text in INDEX.md
- every lane prompt in this pack

Initial live-state commands:
```bash
git fetch --prune origin
git rev-parse origin/main
gh api "search/issues?q=repo:Ahjan108/phoenix_omega_v4.8+is:pr+is:open&per_page=1" -q '.total_count'
gh pr view 5645 --repo Ahjan108/phoenix_omega_v4.8 --json number,state,isDraft,mergeable,statusCheckRollup,headRefName,title,url
gh pr view 5636 --repo Ahjan108/phoenix_omega_v4.8 --json number,state,isDraft,mergeable,statusCheckRollup,headRefName,title,url
gh pr view 5629 --repo Ahjan108/phoenix_omega_v4.8 --json number,state,isDraft,mergeable,statusCheckRollup,headRefName,title,url,files
```

Substrate rule:
- Lanes 01-04 and 06-07 must use a clean cloud/sparse checkout from
  `origin/main`.
- Lane 05 is local-only and must not create new local worktrees while local free
  space is below 50Gi.

Dispatch:
1. Run lane 01 alone. Wait for `old-chat-blocked-closeout-durable=<sha-or-blocked>`.
2. Run lanes 02, 03, and 04 in parallel only after lane 01 is terminal.
3. Run lane 05 only after lanes 02-04 are terminal.
4. Run lane 06 only after lane 05 is terminal.
5. Run lane 07 only after lane 06 is terminal.

DISPATCH SMOKE -> PILOT -> SCALE:
- smoke: lane 01 durable artifact PR/regeneration only.
- pilot: one narrow PR-fix lane (#5645) plus one conflict lane (#5636) if lane 01 is durable.
- scale: add #5629 clean successor, then preservation cleanup and state update.

WATCHDOG / POLLING:
- Poll active lanes every 10 minutes.
- If a lane has no changed progress signal across two polls, inspect logs.
- If a lane has no changed progress signal across three polls, mark it BLOCKED
  unless it reduces scope and continues.

LANDING CONTRACT:
- MERGED: every lane is terminal and any written work is merged or already merged.
- BLOCKED: exact blocker, remote branch/PR or durable artifact, cleanup ledger, and next command.

CLEANUP LEDGER REQUIRED:
- worktrees: removed or HOLD with reason
- local branches: deleted or HOLD with reason
- remote branches: deleted after merge or HOLD with PR/blocker
- scratch files: removed or declared proof roots
- background jobs: stopped or listed with PID/queue id

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/old_chat_unblock_dispatcher_2026-07-15.md

Final dispatcher output:
```text
CLOSEOUT_RECEIPT
AGENT=Pearl_PM_Dispatcher
PROMPT_PACK=docs/agent_prompt_packs/20260715_old_chat_unblock_wave/
PROMPTS_LAUNCHED=<count>
WAVES_COMPLETE=<list>
PRS_OPENED=<urls-or-none>
PRS_MERGED=<merge-shas-or-none>
PRS_CLOSED=<urls-or-none>
BLOCKED_LANES=<lane:blocker-or-none>
CLEANUP_COMPLETE=<yes|no>
HANDOFF=artifacts/coordination/handoffs/old_chat_unblock_dispatcher_2026-07-15.md
SIGNAL=old-chat-unblock-dispatcher-terminal=<full-final-sha-or-blocked>
NEXT_ACTION=<exact next action>
```
~~~
