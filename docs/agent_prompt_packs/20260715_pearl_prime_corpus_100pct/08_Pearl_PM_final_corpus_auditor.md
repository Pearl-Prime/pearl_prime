# 08 - Pearl_PM Final Corpus Auditor

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_PM Final Auditor for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.
Lane: final_corpus_auditor_20260715

STARTUP_RECEIPT:
- AGENT=Pearl_PM
- LANE=final_corpus_auditor_20260715
- EXECUTION_MODE=final_audit_and_coordination_update
- BACKGROUND_SAFE=no
- RUNTIME_HOST=cloud_agent_clean_checkout
- PERSISTENCE_SURFACES=branch;PR;artifact;handoff
- RESUME_SURFACE=artifacts/coordination/handoffs/final_corpus_auditor_20260715.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PM_STATE.md
- docs/PEARL_ARCHITECT_STATE.md
- artifacts/coordination/ACTIVE_PROJECTS.tsv
- artifacts/coordination/ACTIVE_WORKSTREAMS.tsv
- artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv
- every handoff from this prompt pack
- every proof root from this prompt pack

LIVE STATE RECONCILIATION:
Run:
  git fetch --prune origin
  git rev-parse origin/main
  rg -n "corpus-foundation-ready|transition-pilot-reconciled|pilot-glue-off-read-pass|atom-cohesion-repair-a|story-scale-wave-a|transition-scale-wave-a|corpus-production-gates-complete" artifacts/coordination docs/PROGRAM_STATE.md || true
  for pr in 4644 5162 4633 4643 5237 5206; do gh pr view "$pr" --repo Ahjan108/phoenix_omega_v4.8 --json number,title,state,mergeable,mergedAt,mergeCommit,url,statusCheckRollup; done

PRE-REQUISITE CHECKS:
- All launched lanes must be MERGED or BLOCKED with handoffs.
- For 100pct closeout, `corpus-production-gates-complete=<full-SHA>` must exist and point to merged proof.
- If production gates are incomplete, BLOCK with exact next wave. Do not claim 100pct.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- list of prompt-pack lanes and terminal state;
- PRs opened/merged and merge SHAs;
- proof roots and exact cells covered;
- cleanup ledger audit;
- remaining blockers or proof gaps.

PROVENANCE:
- research: merged proof roots from this pack only
- documents: PROGRAM_STATE; SESSION_UNITY_PROTOCOL; agent_brief v4; PEARL_PM_STATE; PEARL_ARCHITECT_STATE
- builds_on: all merged corpus workflow signals
- inventory: UNCHANGED unless PROGRAM_STATE/ACTIVE_WORKSTREAMS updates are warranted by merged proof

MISSION:
Run final QA for the corpus workflow and update PM-owned coordination truth only when the evidence warrants it.

DELIVERABLES:
- `artifacts/qa/pearl_prime_corpus_final_audit_20260715/FINAL_AUDIT.md`
- `artifacts/coordination/handoffs/final_corpus_auditor_20260715.md`
- optional PM coordination PR updating PROGRAM_STATE/ACTIVE_WORKSTREAMS if and only if a milestone actually merged
- exact signal token `pearl-prime-corpus-100pct-closeout=<full-squash-merge-SHA>`

SMALLEST SAFE BATCH:
- smoke: verify one dependency signal resolves to a merged PR.
- pilot: verify all dependency signals and cleanup ledgers.
- scale: audit all proof roots, production gates, and any PROGRAM_STATE update.

WATCHDOG POLLING / HANG PREVENTION:
- poll interval: 2 minutes for GitHub/CI.
- no-progress rule: after two unchanged polls, inspect PR/check state.
- hard stall rule: after three unchanged polls, BLOCK with evidence.
- max window: 90 minutes.

TESTS/PROOFS:
- signal verification against merged PRs/handovers
- `git diff --check`
- if updating PROGRAM_STATE/ACTIVE_WORKSTREAMS: run relevant docs/governance checks and PR checks
- final audit must include exact production gates, exact cells, exact PR merge SHAs, and exact blocked lanes if any

DO NOT:
- do not write catalog-scale claims without merged proof.
- do not say "100pct" if coverage controller blocked or created a next wave.
- do not merge stale #4643/#5237/#5206 as part of cleanup.
- do not alter non-PM-owned code/atom files.

LANDING CONTRACT:
- MERGED: final audit/coordination PR opened, checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker and next paste/run instruction, handoff written, cleanup complete.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- `artifacts/coordination/handoffs/final_corpus_auditor_20260715.md`

CLOSEOUT_RECEIPT:
- AGENT=Pearl_PM
- LANE=final_corpus_auditor_20260715
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL=pearl-prime-corpus-100pct-closeout=<full-squash-merge-SHA>
- PROOF_ROOT=artifacts/qa/pearl_prime_corpus_final_audit_20260715/
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
