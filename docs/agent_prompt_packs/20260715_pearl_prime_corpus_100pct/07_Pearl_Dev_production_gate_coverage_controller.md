# 07 - Pearl_Dev Production Gate Coverage Controller

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Dev with Pearl_QA support for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.
Lane: production_gate_coverage_controller_20260715

STARTUP_RECEIPT:
- AGENT=Pearl_Dev+Pearl_QA
- LANE=production_gate_coverage_controller_20260715
- EXECUTION_MODE=production_gate_runner_and_coverage_controller
- BACKGROUND_SAFE=no
- RUNTIME_HOST=cloud_agent_clean_checkout_or_capable_runner
- PERSISTENCE_SURFACES=branch;PR;artifact;handoff;optional_next_prompt_pack
- RESUME_SURFACE=artifacts/coordination/handoffs/production_gate_coverage_controller_20260715.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md
- scripts/run_pipeline.py --pipeline-mode spine --quality-profile production --exercise-journeys (canonical command shape for any production render invocation)
- scripts/run_production_readiness_gates.py
- scripts/ci/check_canonical_atom_parse_sweep.py
- current proof roots from Wave 2, Wave 3, Wave 4A, and Wave 4B

LIVE STATE RECONCILIATION:
Run:
  git fetch --prune origin
  rg -n "pilot-glue-off-read-pass|atom-cohesion-repair-a|story-scale-wave-a|transition-scale-wave-a" artifacts/coordination docs/PROGRAM_STATE.md || true
  gh pr list --repo Ahjan108/phoenix_omega_v4.8 --state open --limit 300 --json number,title,headRefName,isDraft,mergeable,updatedAt,url,statusCheckRollup

PRE-REQUISITE CHECKS:
- `story-scale-wave-a=<full-SHA>` must exist.
- `transition-scale-wave-a=<full-SHA>` must exist.
- If either missing, BLOCK.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- merged signals consumed;
- current coverage matrix for STORY, TRANSITION, atom cohesion/stubs, and pilot render-read;
- exact cells selected for smoke, pilot, and scale proof;
- full production gate list and any known unrelated-main red.

PROVENANCE:
- research: merged proof roots from prior waves only
- documents: PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC; PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC; PROGRAM_STATE
- builds_on: run_pipeline spine production path; production readiness gates; parse sweep; book quality gates
- inventory: UNCHANGED unless adding proof controller artifacts

MISSION:
Run the production proof controller for the corpus workflow. Continue smoke -> pilot -> scale micro-waves until proof-backed coverage is complete or a concrete blocker is proven. Do not author atoms here unless a tiny test harness/proof script is needed.

DELIVERABLES:
- `artifacts/qa/pearl_prime_corpus_production_gates_20260715/`
- coverage matrix naming every tested cell and gate result
- render logs and quality summaries
- if coverage is complete: final proof PR with `corpus-production-gates-complete=<full-squash-merge-SHA>`
- if coverage is incomplete but more authoring is needed: next prompt pack or handoff with exact next wave, and BLOCK this lane with evidence
- `artifacts/coordination/handoffs/production_gate_coverage_controller_20260715.md`

SMALLEST SAFE BATCH:
- smoke: one newly repaired/story+transition-covered cell rendered with production profile and glue OFF.
- pilot: 2-5 representative cells across the newly repaired surfaces.
- scale: widen only after smoke + pilot pass; max 10 cells per scale wave before writing an intermediate proof and re-evaluating.

RENDER COMMAND SHAPE:
  PHOENIX_ENABLE_RENDER_GLUE=0 PYTHONPATH=. python3 scripts/run_pipeline.py \
    --topic <topic> --persona <persona> \
    --arc <arc.yaml> --pipeline-mode spine \
    --runtime-format extended_book_2h \
    --quality-profile production --exercise-journeys --no-job-check --render-book \
    --render-dir artifacts/qa/pearl_prime_corpus_production_gates_20260715/<cell_id>

WATCHDOG POLLING / HANG PREVENTION:
- poll interval: 5 minutes for renders, 2 minutes for CI.
- no-progress rule: after two unchanged polls, inspect logs and artifact counts.
- hard stall rule: after three unchanged polls, reduce batch size or BLOCK.
- max window: 3 hours per proof wave.

TESTS/PROOFS:
- `PYTHONPATH=. python3 scripts/ci/check_canonical_atom_parse_sweep.py`
- targeted story/transition/cohesion tests from prior lanes
- `PYTHONPATH=. python3 scripts/run_production_readiness_gates.py` when feasible
- production renders with `PHOENIX_ENABLE_RENDER_GLUE=0`
- no bracket stubs, retired glue phrases, or unresolved variables in rendered manuscripts
- coverage matrix with exact counts derived live, not copied from old prompts
- `git diff --check`
- PR checks watched to terminal

DO NOT:
- do not author broad atom changes here.
- do not claim 100pct if any coverage gap remains.
- do not treat #5206 stale audit counts as proof unless re-derived.
- do not hide unrelated-main red; label it precisely.

LANDING CONTRACT:
- MERGED: proof PR opened, checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker, evidence, handoff or next prompt pack written, cleanup complete.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- `artifacts/coordination/handoffs/production_gate_coverage_controller_20260715.md`

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Dev+Pearl_QA
- LANE=production_gate_coverage_controller_20260715
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL=corpus-production-gates-complete=<full-squash-merge-SHA>
- PROOF_ROOT=artifacts/qa/pearl_prime_corpus_production_gates_20260715/
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
