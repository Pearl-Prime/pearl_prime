# 04 - Pearl_Editor Atom Cohesion Stub Repair

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Editor with Pearl_Writer prose authority for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.
Lane: atom_cohesion_stub_repair_20260715

STARTUP_RECEIPT:
- AGENT=Pearl_Editor+Pearl_Writer
- LANE=atom_cohesion_stub_repair_20260715
- EXECUTION_MODE=clean_branch_authoring_and_gate_promotion
- BACKGROUND_SAFE=no
- RUNTIME_HOST=cloud_agent_clean_checkout
- PERSISTENCE_SURFACES=branch;PR;artifact;handoff
- RESUME_SURFACE=artifacts/coordination/handoffs/atom_cohesion_stub_repair_20260715.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- docs/writing/GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE.md
- docs/ATOM_DEBT_REPAIR_DEV_SPEC.md
- tests/test_prose_resolver_stub_filter.py
- scripts/ci/check_canonical_atom_parse_sweep.py
- live #5237 diff and artifacts as source evidence only

LIVE STATE RECONCILIATION:
Run:
  git fetch --prune origin
  gh pr view 5237 --repo Ahjan108/phoenix_omega_v4.8 --json number,title,state,mergeable,headRefName,updatedAt,url,statusCheckRollup
  gh pr diff 5237 --repo Ahjan108/phoenix_omega_v4.8 --name-only
  gh pr diff 5237 --repo Ahjan108/phoenix_omega_v4.8 --patch > /tmp/pr5237.patch
  gh pr checks 5237 --repo Ahjan108/phoenix_omega_v4.8 || true

PRE-REQUISITE CHECKS:
- `pilot-glue-off-read-pass=<full-SHA>` must exist.
- If pilot render-read failed, BLOCK and do not repair/scale atoms.
- #5237 must be treated as dirty source material, not as a merge candidate.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- live #5237 state and failing checks;
- which #5237 evidence artifacts are still useful;
- exact stub/cohesion mechanisms found on current origin/main;
- smallest safe repair batch and excluded dirty changes.

PROVENANCE:
- research: #5237 evidence artifacts if still valid after re-running on origin/main
- documents: PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC; GOLDEN_PHOENIX_ATOM_UPGRADE_GUIDE; ATOM_DEBT_REPAIR_DEV_SPEC
- builds_on: existing atom parser/stub filters; canonical atom parse sweep; book quality gate
- inventory: EXTENDS; no atom slot removed; no parser weakening

MISSION:
Repair atom cohesion/stub/craft debt from clean origin/main without merging #5237 as-is.

DELIVERABLES:
- clean PR with either:
  - a narrow promoted atom cohesion gate plus tests, and/or
  - a narrow repair batch for current-origin stubs/cohesion failures
- `artifacts/qa/atom_cohesion_stub_repair_20260715/`
- `artifacts/coordination/handoffs/atom_cohesion_stub_repair_20260715.md`
- exact signal token `atom-cohesion-repair-a=<full-squash-merge-SHA>`

SMALLEST SAFE BATCH:
- smoke: re-run current-main stub/craft detection for one known surface, preferably the pilot-adjacent corporate_managers/burnout evidence from #5237.
- pilot: repair at most 2-5 atom files/cells with proven current-main failures.
- scale: repair only the next bounded set named by the pilot evidence; no more than 10 files in this lane without dispatcher approval.

WATCHDOG POLLING / HANG PREVENTION:
- poll interval: 2 minutes for tests/CI.
- no-progress rule: after two unchanged polls, inspect failing test logs.
- hard stall rule: after three unchanged polls, reduce batch or BLOCK.
- max window: 2 hours.

TESTS/PROOFS:
- `PYTHONPATH=. python3 scripts/ci/check_canonical_atom_parse_sweep.py`
- `PYTHONPATH=. python3 -m pytest tests/test_prose_resolver_stub_filter.py -q`
- if promoting #5237 gate: `PYTHONPATH=. python3 -m pytest tests/ci/test_check_atom_cohesion.py -q`
- targeted render or selector proof for repaired cell(s)
- `git diff --check`
- PR checks watched to terminal

DO NOT:
- do not merge #5237 as-is.
- do not edit `CANONICAL_ARTIFACTS_REGISTRY.tsv`; propose registry updates in handoff for PM.
- do not touch STORY/TRANSITION files assigned to active Wave 4 lanes.
- do not relabel stubs to pass; author real prose or block.
- do not weaken parse/stub gates.

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
- `artifacts/coordination/handoffs/atom_cohesion_stub_repair_20260715.md`

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Editor+Pearl_Writer
- LANE=atom_cohesion_stub_repair_20260715
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL=atom-cohesion-repair-a=<full-squash-merge-SHA>
- PROOF_ROOT=artifacts/qa/atom_cohesion_stub_repair_20260715/
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
