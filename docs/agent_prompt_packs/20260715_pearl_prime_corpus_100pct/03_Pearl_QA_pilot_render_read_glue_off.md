# 03 - Pearl_QA Pilot Render-Read Glue Off

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_QA for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.
Lane: pilot_render_read_glue_off_20260715

STARTUP_RECEIPT:
- AGENT=Pearl_QA
- LANE=pilot_render_read_glue_off_20260715
- EXECUTION_MODE=production_render_read
- BACKGROUND_SAFE=no
- RUNTIME_HOST=cloud_agent_clean_checkout_or_capable_runner
- PERSISTENCE_SURFACES=branch;PR;artifact;handoff
- RESUME_SURFACE=artifacts/coordination/handoffs/pilot_render_read_glue_off_20260715.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- docs/PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC.md
- phoenix_v4/rendering/render_glue.py
- phoenix_v4/planning/transition_atoms.py
- phoenix_v4/rendering/chapter_composer.py
- scripts/run_pipeline.py --pipeline-mode spine --quality-profile production --exercise-journeys (canonical command shape for any production render invocation)

LIVE STATE RECONCILIATION:
Run:
  git fetch --prune origin
  gh pr view 4643 --repo Ahjan108/phoenix_omega_v4.8 --json state,mergeable,mergedAt,mergeCommit,url
  gh pr list --repo Ahjan108/phoenix_omega_v4.8 --state merged --search "transition-pilot-reconciled" --limit 20 || true
  git grep -n "PHOENIX_ENABLE_RENDER_GLUE\\|render_glue_enabled\\|select_authored_transition" origin/main -- phoenix_v4 || true

PRE-REQUISITE CHECKS:
- `transition-pilot-reconciled=<full-SHA>` must exist on a merged PR, PR body, PROGRAM_STATE, or handoff.
- If missing, BLOCK. Do not render against local-only transition atoms.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- transition-pilot merge SHA;
- exact pilot cells pinned from #4643/supersede proof;
- exact arcs selected for render;
- whether render glue is unset/OFF;
- known unrelated main red risks.

PROVENANCE:
- research: live transition supersede proof and #4643 source context
- documents: PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC; PEARL_PRIME_WHOLE_WORKFLOW_HARDENING_SPEC
- builds_on: run_pipeline spine path; TRANSITION consumer; render glue master kill switch
- inventory: UNCHANGED; QA lane only, unless adding proof artifacts

MISSION:
Render-read the two pilot cells with transition glue OFF. Verify the rendered prose, not just parser selection.

PILOT CELLS:
- Cell A default: `gen_z_professionals` x `anxiety`, default arc `config/source_of_truth/master_arcs/gen_z_professionals__anxiety__spiral__F006.yaml`.
- Cell B default: `corporate_managers` x `financial_stress`, default arc `config/source_of_truth/master_arcs/corporate_managers__financial_stress__overwhelm__F006.yaml`.
- Before running, re-pin engines/arcs from the transition supersede proof. If live proof names different engines, use those and record the delta.

DELIVERABLES:
- `artifacts/qa/pearl_prime_corpus_pilot_glue_off_20260715/`
- rendered `book.txt`, logs, quality summaries, transition evidence, and read report for both cells
- `PILOT_READ_REPORT.md` with layer-honest verdict: structurally clear, authored candidate, system working, or PROVEN-AT-BAR only if operator read approval is actually captured
- `artifacts/coordination/handoffs/pilot_render_read_glue_off_20260715.md`
- exact signal token `pilot-glue-off-read-pass=<full-squash-merge-SHA>`

SMALLEST SAFE BATCH:
- smoke: run transition consumer tests and a one-chapter/shortest feasible render probe or dry proof for Cell A.
- pilot: full render-read both pilot cells.
- scale: no catalog scale here. If both pass, write proof PR only.

RENDER COMMAND SHAPE:
  PHOENIX_ENABLE_RENDER_GLUE=0 PYTHONPATH=. python3 scripts/run_pipeline.py \
    --topic anxiety --persona gen_z_professionals \
    --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__spiral__F006.yaml \
    --pipeline-mode spine --runtime-format extended_book_2h \
    --quality-profile production --exercise-journeys --no-job-check --render-book \
    --render-dir artifacts/qa/pearl_prime_corpus_pilot_glue_off_20260715/gen_z_professionals_anxiety_spiral

  PHOENIX_ENABLE_RENDER_GLUE=0 PYTHONPATH=. python3 scripts/run_pipeline.py \
    --topic financial_stress --persona corporate_managers \
    --arc config/source_of_truth/master_arcs/corporate_managers__financial_stress__overwhelm__F006.yaml \
    --pipeline-mode spine --runtime-format extended_book_2h \
    --quality-profile production --exercise-journeys --no-job-check --render-book \
    --render-dir artifacts/qa/pearl_prime_corpus_pilot_glue_off_20260715/corporate_managers_financial_stress_overwhelm

WATCHDOG POLLING / HANG PREVENTION:
- poll interval: 5 minutes while renders run.
- no-progress rule: after two unchanged polls, inspect render logs and artifact byte counts.
- hard stall rule: after three unchanged polls, reduce render scope if possible or BLOCK with logs.
- max window: 2 hours.

TESTS/PROOFS:
- `PYTHONPATH=. python3 -m pytest tests/unit/rendering/test_deinjection_phase1.py tests/unit/rendering/test_composer_glue_off_default.py -q`
- render commands above, with exact exit codes
- grep proof that banned glue phrases are absent: `Turn it into motion`, `Now we're going to do a practice`, `Ahead of you:`
- grep or audit proof that authored transition bodies appear where expected
- quality summaries from render dirs
- `git diff --check`

PASS CRITERIA:
- both books render on merged origin/main state;
- render glue remains OFF;
- authored transitions appear or empty transitions are explained by pool exhaustion;
- no bracket stubs or template glue leaks in rendered manuscripts;
- read report says at least `authored candidate` for both cells, or BLOCK with exact seam failures.

DO NOT:
- do not patch atoms in this lane.
- do not enable glue to make flow pass.
- do not call operator Layer-4 approval unless the operator actually reads.
- do not claim catalog-scale success.

LANDING CONTRACT:
- MERGED: proof PR opened, checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker, evidence, handoff written.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- `artifacts/coordination/handoffs/pilot_render_read_glue_off_20260715.md`

CLOSEOUT_RECEIPT:
- AGENT=Pearl_QA
- LANE=pilot_render_read_glue_off_20260715
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL=pilot-glue-off-read-pass=<full-squash-merge-SHA>
- PROOF_ROOT=artifacts/qa/pearl_prime_corpus_pilot_glue_off_20260715/
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
