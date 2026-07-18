# 04 - Pearl_Research PR 5629 Clean Successor

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Research for Phoenix Omega.

STARTUP_RECEIPT:
- AGENT=Pearl_Research
- LANE=04_pr5629_clean_successor
- EXECUTION_MODE=clean_cloud_checkout
- BACKGROUND_SAFE=yes
- PERSISTENCE_SURFACES=PR; handoff markdown
- RESUME_SURFACE=artifacts/coordination/handoffs/04_pr5629_clean_successor_2026-07-15.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/research/PEARL_RESEARCH_PROMPT_GENERATION_LAYER.md if present
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- old_chat_specs/Untitled 319.txt
- old_chat_specs/Untitled 320.txt
- artifacts/coordination/handoffs/01_durable_blocked_closeout_pr_2026-07-15.md

DEPENDENCY GATE:
- Require `old-chat-blocked-closeout-durable=<sha-or-blocked>` from lane 01.

LIVE STATE RECONCILIATION:
- `gh pr view 5629 --repo Ahjan108/phoenix_omega_v4.8 --json number,state,isDraft,mergeable,statusCheckRollup,headRefName,title,url,files`
- Verify whether the research prompt-generation layer is already on `origin/main`.

DISCOVERY REPORT BEFORE ACTION:
- file list from #5629 and why it is polluted or safe
- narrow desired file set for research prompt-generation layer
- decision: clean successor PR, no-op because landed, or BLOCKED because source unavailable

PROVENANCE:
- research: chats 319/320 and existing research docs
- documents: research authority docs and active workstreams
- builds_on: existing research runner/prompt compiler
- inventory: EXTENDS or UNCHANGED

MISSION:
- Replace polluted #5629 with a clean, narrow research prompt-generation successor PR, or block with exact missing-source proof.

SMOKE -> PILOT -> SCALE:
- smoke: one import/static check for the prompt builder or regenerated equivalent.
- pilot: run the smallest research prompt-generation test fixture.
- scale: run targeted research tests and merge the clean PR only after pilot passes.

WATCHDOG / POLLING:
- poll interval: 5 minutes for tests, 10 minutes for CI.
- no-progress rule: inspect logs after two unchanged polls.
- hard stall rule: BLOCKED after three no-progress intervals with branch/log evidence.
- max window: 3 hours.

DO NOT:
- do not carry unrelated freebie/localization/artifact deletions from #5629
- do not mix old local dirty branch changes
- do not create new capability without provenance

LANDING CONTRACT:
- MERGED: clean successor PR merged or #5629 proven safe and merged.
- BLOCKED: remote branch/PR preserves regenerated work and exact blocker is recorded.

CLEANUP LEDGER REQUIRED:
- worktrees: none-created or removed
- branches: deleted or HOLD
- remote branches: deleted after merge or HOLD
- scratch/generated examples: committed intentionally or deleted
- background jobs: stopped/listed

HANDOFF REQUIRED:
- artifacts/coordination/handoffs/04_pr5629_clean_successor_2026-07-15.md

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Research
- LANE=04_pr5629_clean_successor
- STATUS=MERGED|BLOCKED
- PR=<url-or-none>
- MERGE_SHA=<sha-or-none>
- SIGNAL=pr5629-clean-research-terminal=<full-merge-sha-or-blocked>
- PROOF_ROOT=artifacts/coordination/handoffs/04_pr5629_clean_successor_2026-07-15.md
- TESTS=<commands/checks>
- CLEANUP=<ledger>
- HANDOFF=artifacts/coordination/handoffs/04_pr5629_clean_successor_2026-07-15.md
- NEXT_ACTION=<exact next action>
```
