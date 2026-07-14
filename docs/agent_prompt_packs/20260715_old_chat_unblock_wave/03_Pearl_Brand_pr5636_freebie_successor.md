# 03 - Pearl_Brand PR 5636 Freebie Successor

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Brand for Phoenix Omega.

STARTUP_RECEIPT:
- AGENT=Pearl_Brand
- LANE=03_pr5636_freebie_successor
- EXECUTION_MODE=clean_cloud_checkout
- BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=PR; preview/test logs; handoff markdown
- RESUME_SURFACE=artifacts/coordination/handoffs/03_pr5636_freebie_successor_2026-07-15.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/OLD_CHAT_AND_HOME_PROMOTION_SPEC.md
- BRAND_ADMIN_CANONICAL_PACKAGE.md if present
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- old_chat_specs/Untitled 321.txt
- artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md

DEPENDENCY GATE:
- Require `old-chat-blocked-closeout-durable=<sha-or-blocked>` from lane 01.

LIVE STATE RECONCILIATION:
- `gh pr view 5636 --repo Ahjan108/phoenix_omega_v4.8 --json number,state,isDraft,mergeable,statusCheckRollup,headRefName,title,url,files`
- Inspect conflict files and changed paths.

DISCOVERY REPORT BEFORE ACTION:
- conflict list
- value list from PR #5636
- decision: resolve #5636 directly, or create narrow successor PR from clean main

PROVENANCE:
- research: old chat 321 and #5636 diff
- documents: brand/freebie authority docs
- builds_on: existing freebie report capture flow
- inventory: EXTENDS or UNCHANGED

MISSION:
- Rescue the Waystream post-experience/freebie capture work from #5636 into a clean merged PR, or leave it BLOCKED with exact conflict/test proof.

SMOKE -> PILOT -> SCALE:
- smoke: isolate one capture path and one report artifact from #5636.
- pilot: resolve conflicts for the minimal files and run the smallest JS/browser/unit smoke.
- scale: run scoped preview/E2E/a11y checks only after pilot passes.

WATCHDOG / POLLING:
- poll interval: 5 minutes for tests, 10 minutes for CI/preview.
- no-progress rule: inspect logs after two unchanged polls.
- hard stall rule: BLOCKED after three no-progress intervals with conflict/check evidence.
- max window: 3 hours.

DO NOT:
- do not force-publish a draft/conflicting PR
- do not touch unrelated brand pages
- do not expose secrets or provider credentials

LANDING CONTRACT:
- MERGED: #5636 or a clean successor PR merged with tests/proof.
- BLOCKED: remote branch/PR preserves value and names the blocker.

CLEANUP LEDGER REQUIRED:
- worktrees: none-created or removed
- branches: deleted or HOLD
- remote branches: deleted after merge or HOLD
- scratch files/reports: committed as proof or deleted
- background jobs: stopped/listed

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/03_pr5636_freebie_successor_2026-07-15.md

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Brand
- LANE=03_pr5636_freebie_successor
- STATUS=MERGED|BLOCKED
- PR=<url-or-none>
- MERGE_SHA=<sha-or-none>
- SIGNAL=pr5636-freebie-successor-terminal=<full-merge-sha-or-blocked>
- PROOF_ROOT=artifacts/coordination/handoffs/03_pr5636_freebie_successor_2026-07-15.md
- TESTS=<commands/checks>
- CLEANUP=<ledger>
- HANDOFF=artifacts/coordination/handoffs/03_pr5636_freebie_successor_2026-07-15.md
- NEXT_ACTION=<exact next action>
```
