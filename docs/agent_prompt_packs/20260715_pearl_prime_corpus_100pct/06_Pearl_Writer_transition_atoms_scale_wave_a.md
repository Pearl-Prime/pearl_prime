# 06 - Pearl_Writer TRANSITION Atoms Scale Wave A

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Writer for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.
Lane: transition_atoms_scale_wave_a_20260715

STARTUP_RECEIPT:
- AGENT=Pearl_Writer
- LANE=transition_atoms_scale_wave_a_20260715
- EXECUTION_MODE=clean_branch_transition_authoring
- BACKGROUND_SAFE=no
- RUNTIME_HOST=cloud_agent_clean_checkout
- PERSISTENCE_SURFACES=branch;PR;artifact;handoff
- RESUME_SURFACE=artifacts/coordination/handoffs/transition_atoms_scale_wave_a_20260715.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md
- phoenix_v4/planning/transition_atoms.py
- phoenix_v4/rendering/chapter_composer.py
- tests/unit/rendering/test_deinjection_phase1.py
- tests/unit/rendering/test_composer_glue_off_default.py

LIVE STATE RECONCILIATION:
Run:
  git fetch --prune origin
  gh pr view 4644 --repo Ahjan108/phoenix_omega_v4.8 --json state,mergeCommit,mergedAt,title
  gh pr view 5162 --repo Ahjan108/phoenix_omega_v4.8 --json state,mergeCommit,mergedAt,title
  rg -n "TRANSITION|transition-scale|pilot-glue-off-read-pass|atom-cohesion-repair-a" artifacts/coordination docs/PROGRAM_STATE.md || true

PRE-REQUISITE CHECKS:
- `pilot-glue-off-read-pass=<full-SHA>` must exist.
- `atom-cohesion-repair-a=<full-SHA>` must exist.
- #4644 and #5162 transition infrastructure must be merged.
- If any prerequisite is missing, BLOCK.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- current TRANSITION coverage by persona/topic;
- chosen Wave A cells and engines;
- boundary gaps for `after_opening`, `before_story`, `before_exercise`, `before_integration`;
- overlap check against active STORY/cohesion lanes.

PROVENANCE:
- research: pilot render-read proof and current transition coverage audit
- documents: PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC; GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE
- builds_on: `transition_atoms.select_authored_transition`; composer `_authored_transition`; glue-off default
- inventory: EXTENDS; no glue family resurrection

MISSION:
Scale TRANSITION atoms after pilot render-read passes, using bounded micro-waves. Do not touch STORY banks in this lane.

DELIVERABLES:
- clean PR with Wave A TRANSITION atom additions only
- `artifacts/qa/transition_atoms_scale_wave_a_20260715/`
- `artifacts/coordination/handoffs/transition_atoms_scale_wave_a_20260715.md`
- exact signal token `transition-scale-wave-a=<full-squash-merge-SHA>`

SMALLEST SAFE BATCH:
- smoke: one persona/topic TRANSITION bank with all four boundaries covered and parser/select proof.
- pilot: 2-5 persona/topic cells chosen from current proof gaps.
- scale: no more than 10 cells in Wave A after smoke + pilot pass.

AUTHORING REQUIREMENTS:
- Use `atoms/{persona}/{topic}/TRANSITION/CANONICAL.txt`.
- Each atom must parse with metadata:
  - `boundary: after_opening|before_story|before_exercise|before_integration`
  - optional `engine: <engine>` only when truly engine-specific.
- Prose lands the prior beat and turns; it must not be template glue.
- Ban phrases known from retired glue: `Turn it into motion`, `Now we're going to do a practice`, `Ahead of you:`.
- No placeholders, TODO/TBD, bracket stubs, unresolved variables, or generic signposting.

WATCHDOG POLLING / HANG PREVENTION:
- poll interval: 2 minutes for tests/CI.
- no-progress rule: after two unchanged polls, inspect logs.
- hard stall rule: after three unchanged polls, reduce batch or BLOCK.
- max window: 2 hours.

TESTS/PROOFS:
- targeted parser/select proof for every new bank and all four boundaries
- `PYTHONPATH=. python3 -m pytest tests/unit/rendering/test_deinjection_phase1.py tests/unit/rendering/test_composer_glue_off_default.py -q`
- `PYTHONPATH=. python3 scripts/ci/check_canonical_atom_parse_sweep.py`
- targeted render proof for at least smoke and pilot cells with `PHOENIX_ENABLE_RENDER_GLUE=0`
- `git diff --check`
- PR checks watched to terminal

DO NOT:
- do not start before pilot render-read passes.
- do not touch STORY banks.
- do not edit PM hot coordination files.
- do not claim full corpus coverage from Wave A.

LANDING CONTRACT:
- MERGED: clean PR opened, checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker, evidence, handoff written.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- `artifacts/coordination/handoffs/transition_atoms_scale_wave_a_20260715.md`

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Writer
- LANE=transition_atoms_scale_wave_a_20260715
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL=transition-scale-wave-a=<full-squash-merge-SHA>
- PROOF_ROOT=artifacts/qa/transition_atoms_scale_wave_a_20260715/
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
