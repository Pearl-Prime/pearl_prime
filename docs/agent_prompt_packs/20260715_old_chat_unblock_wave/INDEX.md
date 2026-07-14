# Old Chat Unblock Wave Prompt Pack

## Program

- Goal: unblock the all-BLOCKED closeout from `docs/agent_prompt_packs/20260715_old_chat_closure_audit/` without repeating the unsafe broad batch.
- Source signal: `old-chat-dispatcher-terminal=blocked`.
- Router date: 2026-07-15 Asia/Taipei.
- Live `origin/main` at final pack verification: `319ad84af8c3dfd3770bf3b08acd3bf6cfa6b44b`.
- Local disk at final pack verification: about 11Gi free on `/System/Volumes/Data`; local execution remains emergency-low.
- Prompt count: 8 prompt files total: 1 dispatcher + 7 lane prompts.

## Blocked Closeout Summary

The closure audit produced local artifacts but no durable PRs:

- `artifacts/coordination/old_chat_closure_matrix_2026-07-15.md`
- `artifacts/coordination/handoffs/old_chat_closure_dispatcher_2026-07-15.md`

All ten lanes were terminal BLOCKED. No PRs were opened, merged, or closed. No worktrees, branches, or paths were deleted.

Primary blockers:

- dirty branch-changing local root prevented durable matrix PR
- #5645 mergeable but Core tests failed
- #5636 draft/conflicting/no checks
- #5629 mergeable but polluted; not a narrow research carrier
- research prompt-generation layer is local-only or must be regenerated cleanly
- poisoned/dirty worktrees require preservation-first cleanup
- PM state/router updates are unsafe until clean successor surfaces exist

## Wave Order

- Wave 0: `01_Pearl_PM_durable_blocked_closeout_pr.md`
- Wave 1: `02_Pearl_GitHub_pr5645_core_fix.md`, `03_Pearl_Brand_pr5636_freebie_successor.md`, `04_Pearl_Research_pr5629_clean_successor.md`
- Wave 2: `05_Pearl_GitHub_preservation_first_worktree_cleanup.md`
- Wave 3: `06_Pearl_PM_state_router_update_after_unblock.md`
- Wave 4: `07_Pearl_PM_unblock_final_auditor.md`

## Lane Matrix

| Prompt | Owner | Substrate | Depends on | Output | Status |
| --- | --- | --- | --- | --- | --- |
| 01 | Pearl_PM | clean cloud/sparse checkout | none | durable closeout/matrix PR or regenerated equivalent, `old-chat-blocked-closeout-durable=<sha-or-blocked>` | prepared |
| 02 | Pearl_GitHub | clean cloud checkout | 01 | #5645 merged or blocked with exact Core failure, `pr5645-core-fix-terminal=<sha-or-blocked>` | prepared |
| 03 | Pearl_Brand | clean cloud checkout | 01 | #5636 resolved/merged or clean successor blocked, `pr5636-freebie-successor-terminal=<sha-or-blocked>` | prepared |
| 04 | Pearl_Research | clean cloud checkout | 01 | clean replacement for polluted #5629, `pr5629-clean-research-terminal=<sha-or-blocked>` | prepared |
| 05 | Pearl_GitHub | local, no new worktrees | 01-04 terminal | preservation-first worktree cleanup ledger, `preservation-worktree-cleanup-terminal=<sha-or-blocked>` | prepared |
| 06 | Pearl_PM | clean cloud checkout | 01-05 terminal | PROGRAM_STATE/workstream/router update, `old-chat-state-update-terminal=<sha-or-blocked>` | prepared |
| 07 | Pearl_PM | clean cloud/API | 01-06 terminal | final unblock audit, `old-chat-unblock-final-terminal=<sha-or-blocked>` | prepared |

## Non-Negotiable Rules

- Do not retry the previous giant batch.
- No new local worktrees while local free space is below 50Gi.
- Clean cloud/sparse checkout is required for lanes 01-04 and 06-07.
- Lane 05 may run locally, but only preservation-first and only after lanes 01-04 are terminal.
- Every lane must end MERGED or BLOCKED, with a handoff `.md`, cleanup ledger, and exact signal token.
- "PR open" is not success unless the lane is BLOCKED and names the remaining blocker.
- #5295 remains owner-gated and out of scope for this unblock wave.
- Catalog-skeleton mass PRs are out of scope.

## Pack Self-Audit

- Overlap check: lane 01 owns durable audit artifacts; lane 02 owns #5645; lane 03 owns #5636; lane 04 owns #5629/research successor; lane 05 owns local worktree preservation; lane 06 owns state/router hot files; lane 07 audits only.
- Missing gate check: every lane includes smoke -> pilot -> scale, watchdog/polling, MERGED-or-BLOCKED landing, cleanup ledger, handoff `.md`, and exact signal token.
- Unsafe giant-batch check: no lane may merge unrelated PRs, delete all worktrees, or run large stress/render jobs.
- Cleanup check: final auditor rejects any lane without worktree, branch, scratch, and background-job ledger.

## Final Status

- Status: prompt pack prepared, not executed.
- Next action: paste `00_MASTER_DISPATCH_PROMPT.md` into the lead clean cloud/sparse agent.
