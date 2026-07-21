# 05 - Pearl_Writer STORY Atoms Scale Wave A

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Writer for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.
Lane: story_atoms_scale_wave_a_20260715

STARTUP_RECEIPT:
- AGENT=Pearl_Writer
- LANE=story_atoms_scale_wave_a_20260715
- EXECUTION_MODE=clean_branch_atom_authoring
- BACKGROUND_SAFE=no
- RUNTIME_HOST=cloud_agent_clean_checkout
- PERSISTENCE_SURFACES=branch;PR;artifact;handoff
- RESUME_SURFACE=artifacts/coordination/handoffs/story_atoms_scale_wave_a_20260715.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md
- docs/WRITER_COMMS_SYSTEMS_100.md
- phoenix_v4/planning/story_planner.py
- phoenix_v4/planning/registry_resolver.py
- tests/test_story_type_conformance.py
- tests/unit/planning/test_story_picks.py

LIVE STATE RECONCILIATION:
Run:
  git fetch --prune origin
  gh pr view 4633 --repo Ahjan108/phoenix_omega_v4.8 --json state,mergeCommit,mergedAt,title
  rg -n "STORY|story-scale|pilot-glue-off-read-pass|atom-cohesion-repair-a" artifacts/coordination docs/PROGRAM_STATE.md || true

PRE-REQUISITE CHECKS:
- `pilot-glue-off-read-pass=<full-SHA>` must exist.
- `atom-cohesion-repair-a=<full-SHA>` must exist.
- #4633 named 3-level STORY wave 1 must be merged.
- If any prerequisite is missing, BLOCK.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- exact STORY coverage gaps from current-main render/proof artifacts;
- chosen cells/engines for Wave A and why;
- files that will be touched;
- overlap check against active atom/cohesion/transition lanes.

PROVENANCE:
- research: current proof artifacts from pilot render-read and coverage controller; no stale #5206 claims unless re-derived
- documents: PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC; GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE; WRITER_COMMS_SYSTEMS_100
- builds_on: #4633 named 3-level STORY atoms; `story_planner.build_story_schedule`; engine-keyed STORY routing
- inventory: EXTENDS; no STORY bank deletions without ratification

MISSION:
Scale named STORY atoms after pilot render-read passes, using bounded micro-waves. Do not touch TRANSITION banks in this lane.

DELIVERABLES:
- clean PR with Wave A STORY atom additions/repairs only
- `artifacts/qa/story_atoms_scale_wave_a_20260715/`
- `artifacts/coordination/handoffs/story_atoms_scale_wave_a_20260715.md`
- exact signal token `story-scale-wave-a=<full-squash-merge-SHA>`

SMALLEST SAFE BATCH:
- smoke: one persona/topic/engine STORY bank with at least 3 named-character atoms and required metadata.
- pilot: 2-5 cells/engines chosen from current proof gaps.
- scale: only after smoke + pilot parse/select/render proof; no more than 10 cells/engines in Wave A.

AUTHORING REQUIREMENTS:
- Write third-person present STORY prose unless the governing docs for the slot say otherwise.
- Include required metadata, especially `emotional_intensity_band` when applicable.
- Keep named characters stable inside a cell.
- No placeholders, TODO/TBD, bracket stubs, unresolved variables, or generic topic lectures.
- No locale atom edits.

WATCHDOG POLLING / HANG PREVENTION:
- poll interval: 2 minutes for tests/CI.
- no-progress rule: after two unchanged polls, inspect logs.
- hard stall rule: after three unchanged polls, reduce batch or BLOCK.
- max window: 2 hours.

TESTS/PROOFS:
- `PYTHONPATH=. python3 scripts/ci/check_canonical_atom_parse_sweep.py`
- `PYTHONPATH=. python3 -m pytest tests/test_story_type_conformance.py tests/unit/planning/test_story_picks.py tests/unit/planning/test_opd142_story_schedule_routing.py tests/unit/planning/test_opd143_story_slot_distinct_per_chapter.py -q`
- targeted selector/render proof for smoke and pilot cells
- `git diff --check`
- PR checks watched to terminal

DO NOT:
- do not start before pilot render-read passes.
- do not touch TRANSITION banks.
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
- `artifacts/coordination/handoffs/story_atoms_scale_wave_a_20260715.md`

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Writer
- LANE=story_atoms_scale_wave_a_20260715
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL=story-scale-wave-a=<full-squash-merge-SHA>
- PROOF_ROOT=artifacts/qa/story_atoms_scale_wave_a_20260715/
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
