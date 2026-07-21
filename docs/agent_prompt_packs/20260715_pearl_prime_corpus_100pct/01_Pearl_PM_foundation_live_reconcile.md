# 01 - Pearl_PM Foundation Live Reconcile

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_PM for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.
Lane: corpus_foundation_live_reconcile_20260715

STARTUP_RECEIPT:
- AGENT=Pearl_PM
- LANE=corpus_foundation_live_reconcile_20260715
- EXECUTION_MODE=github_cli_and_repo_coordination
- BACKGROUND_SAFE=no
- RUNTIME_HOST=cloud_agent_clean_checkout
- PERSISTENCE_SURFACES=branch;PR;artifact;handoff
- RESUME_SURFACE=artifacts/coordination/handoffs/corpus_foundation_live_reconcile_20260715.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PM_STATE.md
- docs/PEARL_ARCHITECT_STATE.md
- artifacts/coordination/ACTIVE_PROJECTS.tsv
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- docs/agent_prompt_packs/20260715_pearl_prime_corpus_100pct/INDEX.md

LIVE STATE RECONCILIATION:
Run:
  git fetch --prune origin
  git rev-parse origin/main
  for pr in 4644 5162 4633 4643 5237 5206; do gh pr view "$pr" --repo Ahjan108/phoenix_omega_v4.8 --json number,title,state,isDraft,mergeable,mergedAt,mergeCommit,headRefName,baseRefName,updatedAt,url,statusCheckRollup; done
  gh pr list --repo Ahjan108/phoenix_omega_v4.8 --state open --limit 300 --json number,title,headRefName,isDraft,mergeable,updatedAt,url,statusCheckRollup
  for pr in 4643 5237 5206; do gh pr diff "$pr" --repo Ahjan108/phoenix_omega_v4.8 --name-only; gh pr checks "$pr" --repo Ahjan108/phoenix_omega_v4.8 || true; done

PRE-REQUISITE CHECKS:
- `#4644`, `#5162`, and `#4633` must be merged or this lane BLOCKS.
- If #4643 is already merged, verify its merge SHA and skip Wave 1 by emitting `transition-pilot-reconciled=<merge-sha>` in the handoff.
- If #5237 or #5206 became mergeable, do not merge them here; record live state for later lanes.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- verified PR states for #4644/#5162/#4633/#4643/#5237/#5206;
- open workstream collisions involving atoms, STORY, TRANSITION, render glue, coordination hot files;
- exact downstream wave launch/dependency map;
- smallest safe batch recommendation.

PROVENANCE:
- research: pasted notes are non-authoritative context only; live GitHub and PROGRAM_STATE are authority
- documents: PROGRAM_STATE; SESSION_UNITY_PROTOCOL; agent_brief v4; PEARL_PM_STATE; PEARL_ARCHITECT_STATE
- builds_on: pearl_prime_story_planner; pearl_prime_enrichment_select; TRANSITION consumer from #4644/#5162
- inventory: UNCHANGED; this lane coordinates only

MISSION:
Create the live collision map and foundation handoff for the pack. Do not implement atom or renderer changes.

DELIVERABLES:
- `artifacts/coordination/handoffs/corpus_foundation_live_reconcile_20260715.md`
- optional small coordination PR containing the handoff and, only if required, a PM-owned ACTIVE_WORKSTREAMS row
- exact signal token `corpus-foundation-ready=<full-squash-merge-SHA>`

SMALLEST SAFE BATCH:
- smoke: verify one merged infrastructure PR (#5162) and one stale PR (#4643).
- pilot: verify all six requested PRs plus open workstream collisions.
- scale: write only the foundation handoff/coordination row; no implementation.

WATCHDOG POLLING / HANG PREVENTION:
- poll interval: 2 minutes for GitHub API/CI.
- no-progress rule: after two unchanged polls, inspect `gh pr view` and Actions links.
- hard stall rule: after three unchanged polls, BLOCK with current GitHub evidence.
- max window: 45 minutes.

TESTS/PROOFS:
- `git rev-parse origin/main`
- `gh pr view` and `gh pr checks` outputs captured in the handoff
- no code tests required unless a coordination PR is opened; if opened, run `git diff --check`

DO NOT:
- do not merge stale PRs.
- do not edit atoms.
- do not edit render code.
- do not mark downstream work done.

LANDING CONTRACT:
- MERGED: open a narrow coordination PR, required checks green or documented non-blocking, squash-merge, emit `corpus-foundation-ready=<full-squash-merge-SHA>`.
- BLOCKED: exact blocker, evidence, handoff written, cleanup complete.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- `artifacts/coordination/handoffs/corpus_foundation_live_reconcile_20260715.md`

CLOSEOUT_RECEIPT:
- AGENT=Pearl_PM
- LANE=corpus_foundation_live_reconcile_20260715
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL=corpus-foundation-ready=<full-squash-merge-SHA>
- PROOF_ROOT=artifacts/coordination/handoffs/corpus_foundation_live_reconcile_20260715.md
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
