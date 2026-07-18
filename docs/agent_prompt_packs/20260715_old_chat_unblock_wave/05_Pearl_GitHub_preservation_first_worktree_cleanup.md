# 05 - Pearl_GitHub Preservation-First Worktree Cleanup

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_GitHub for Phoenix Omega.

STARTUP_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=05_preservation_first_worktree_cleanup
- EXECUTION_MODE=local_no_new_worktrees
- BACKGROUND_SAFE=no
- PERSISTENCE_SURFACES=handoff markdown; patch manifests; remote branches if needed
- RESUME_SURFACE=artifacts/coordination/handoffs/05_preservation_first_worktree_cleanup_2026-07-15.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md
- artifacts/coordination/handoffs/02_pr5645_core_fix_2026-07-15.md
- artifacts/coordination/handoffs/03_pr5636_freebie_successor_2026-07-15.md
- artifacts/coordination/handoffs/04_pr5629_clean_successor_2026-07-15.md

DEPENDENCY GATES:
- Require terminal signals from lanes 01-04.
- If any are missing, STAND DOWN and emit BLOCKED.

LIVE STATE RECONCILIATION:
- `df -h / /Users /Users/ahjan/phoenix_omega`
- `git worktree list --porcelain`
- Inspect candidate worktrees one at a time; no new local worktree creation.

DISCOVERY REPORT BEFORE ACTION:
- free-space tier
- candidate cleanup list with branch/PR mapping and dirty count
- preservation method for every dirty/HOLD worktree
- deletion candidates limited to clean, merged, no-value worktrees

PROVENANCE:
- research: blocked closure matrix and lanes 01-04 handoffs
- documents: GitHub operations framework and router poison protocol
- builds_on: worktree cleanup discipline
- inventory: UNCHANGED

MISSION:
- Clean only what is safe, and preserve everything else with a manifest so disk can recover without losing valuable old-chat work.

SMOKE -> PILOT -> SCALE:
- smoke: classify root checkout, #5636 worktree, and pr5237 poisoned worktree; no deletion.
- pilot: remove at most two clean already-merged/no-value worktrees after proof.
- scale: continue in micro-batches of at most five clean worktrees; stop if any dirty/phantom-deletion pattern appears.

WATCHDOG / POLLING:
- poll interval: 5 minutes.
- no-progress rule: if a git command hangs across two polls, inspect lock/process state.
- hard stall rule: BLOCKED after three no-progress intervals with path and process evidence.
- max window: 2 hours.

PRESERVATION RULES:
- For dirty worktrees, create a manifest first. Do not create giant patches for phantom 262k deletion states; record the poisoned state and branch/HEAD, then block that path for manual/special recovery.
- For clean worktrees backing open PRs, HOLD unless PR merged/closed and no local delta remains.
- For worktrees backing merged PRs, verify no local delta, then remove one at a time.

DO NOT:
- do not `git clean -fdx`
- do not remove current root checkout
- do not delete dirty worktrees
- do not run unbounded `du`

LANDING CONTRACT:
- MERGED: cleanup handoff/manifest committed or accepted as durable, safe removals completed.
- BLOCKED: exact path blocker with preservation manifest and next safe command.

CLEANUP LEDGER REQUIRED:
- worktrees: removed or HOLD with reason
- branches: deleted or HOLD
- remote branches: deleted after merge or HOLD
- scratch files: removed/listed
- background jobs: stopped/listed

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/05_preservation_first_worktree_cleanup_2026-07-15.md

CLOSEOUT_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=05_preservation_first_worktree_cleanup
- STATUS=MERGED|BLOCKED
- WORKTREES_REMOVED=<paths-or-none>
- WORKTREES_HELD=<paths:reason-or-none>
- VALUE_PRESERVED=<manifests/branches-or-none>
- SIGNAL=preservation-worktree-cleanup-terminal=<full-final-sha-or-blocked>
- PROOF_ROOT=artifacts/coordination/handoffs/05_preservation_first_worktree_cleanup_2026-07-15.md
- TESTS=<commands>
- CLEANUP=<ledger>
- HANDOFF=artifacts/coordination/handoffs/05_preservation_first_worktree_cleanup_2026-07-15.md
- NEXT_ACTION=<exact next action>
```
