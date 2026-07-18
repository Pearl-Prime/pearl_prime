# 02 - Pearl_GitHub PR 5645 Core Fix

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_GitHub for Phoenix Omega.

STARTUP_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=02_pr5645_core_fix
- EXECUTION_MODE=clean_cloud_checkout
- BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=PR; check logs; handoff markdown
- RESUME_SURFACE=artifacts/coordination/handoffs/02_pr5645_core_fix_2026-07-15.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/GITHUB_OPERATIONS_FRAMEWORK.md
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md

DEPENDENCY GATE:
- Require `old-chat-blocked-closeout-durable=<sha-or-blocked>` from lane 01.
- If lane 01 is BLOCKED, continue only if it preserved a remote branch/artifact with the closeout matrix.

LIVE STATE RECONCILIATION:
- `gh pr view 5645 --repo Ahjan108/phoenix_omega_v4.8 --json number,state,isDraft,mergeable,statusCheckRollup,headRefName,title,url,files`
- Inspect failing Core test logs before editing.

DISCOVERY REPORT BEFORE ACTION:
- exact failing Core check/job and failure lines
- changed files in #5645
- whether fix belongs on #5645 branch or a clean successor

PROVENANCE:
- research: old-chat stress closeout and PR #5645
- documents: Pearl Prime specs and GitHub operations framework
- builds_on: existing accent bank and stress-gate fixes
- inventory: EXTENDS or UNCHANGED

MISSION:
- Make #5645 mergeable and green, or replace it with a narrow successor PR preserving its value.

SMOKE -> PILOT -> SCALE:
- smoke: reproduce the failing Core test or identify it from CI logs.
- pilot: apply the smallest fix and run the targeted test(s).
- scale: run the full relevant Core/check suite and merge when green.

WATCHDOG / POLLING:
- poll interval: 5 minutes for tests, 10 minutes for CI.
- no-progress rule: inspect logs after two unchanged polls.
- hard stall rule: BLOCKED after three no-progress intervals with failing log URL.
- max window: 3 hours.

DO NOT:
- do not weaken gates or skip failing Core tests
- do not mix #5636/#5629 work
- do not run stress scale tests here

LANDING CONTRACT:
- MERGED: #5645 or clean successor PR is merged, with merge SHA.
- BLOCKED: remote branch/PR preserves the fix attempt and exact failure is recorded.

CLEANUP LEDGER REQUIRED:
- worktrees: none-created or removed
- branches: deleted or HOLD
- remote branches: deleted after merge or HOLD
- scratch files: removed
- background jobs: stopped/listed

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/02_pr5645_core_fix_2026-07-15.md

CLOSEOUT_RECEIPT:
- AGENT=Pearl_GitHub
- LANE=02_pr5645_core_fix
- STATUS=MERGED|BLOCKED
- PR=<url-or-none>
- MERGE_SHA=<sha-or-none>
- SIGNAL=pr5645-core-fix-terminal=<full-merge-sha-or-blocked>
- PROOF_ROOT=artifacts/coordination/handoffs/02_pr5645_core_fix_2026-07-15.md
- TESTS=<commands/checks>
- CLEANUP=<ledger>
- HANDOFF=artifacts/coordination/handoffs/02_pr5645_core_fix_2026-07-15.md
- NEXT_ACTION=<exact next action>
```
