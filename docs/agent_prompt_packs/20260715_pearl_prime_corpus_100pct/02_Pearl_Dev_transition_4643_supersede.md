# 02 - Pearl_Dev Transition 4643 Supersede

```text
EXECUTE. Do not stop at summary or plan. End only MERGED or BLOCKED.

You are Pearl_Dev for Phoenix Omega.

Repo: Ahjan108/phoenix_omega_v4.8
Start from a clean checkout of latest origin/main.
Lane: transition_4643_supersede_20260715

STARTUP_RECEIPT:
- AGENT=Pearl_Dev
- LANE=transition_4643_supersede_20260715
- EXECUTION_MODE=github_cli_clean_branch
- BACKGROUND_SAFE=no
- RUNTIME_HOST=cloud_agent_clean_checkout
- PERSISTENCE_SURFACES=branch;PR;artifact;handoff
- RESUME_SURFACE=artifacts/coordination/handoffs/transition_4643_supersede_20260715.md

READ FIRST:
- docs/PROGRAM_STATE.md
- docs/SESSION_UNITY_PROTOCOL.md
- docs/agent_brief.txt
- docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md
- specs/PHOENIX_ARC_FIRST_CANONICAL_SPEC.md
- specs/PHOENIX_V4_5_WRITER_SPEC.md
- phoenix_v4/planning/transition_atoms.py
- phoenix_v4/planning/registry_resolver.py
- phoenix_v4/rendering/chapter_composer.py
- tests/unit/rendering/test_deinjection_phase1.py
- tests/unit/rendering/test_composer_glue_off_default.py

LIVE STATE RECONCILIATION:
Run:
  git fetch --prune origin
  gh pr view 4643 --repo Ahjan108/phoenix_omega_v4.8 --json number,title,state,mergeable,headRefName,baseRefName,updatedAt,url,statusCheckRollup
  gh pr diff 4643 --repo Ahjan108/phoenix_omega_v4.8 --name-only
  gh pr diff 4643 --repo Ahjan108/phoenix_omega_v4.8 --patch > /tmp/pr4643.patch
  gh pr view 4644 --repo Ahjan108/phoenix_omega_v4.8 --json state,mergeCommit,mergedAt,title
  gh pr view 5162 --repo Ahjan108/phoenix_omega_v4.8 --json state,mergeCommit,mergedAt,title

PRE-REQUISITE CHECKS:
- `corpus-foundation-ready=<full-SHA>` exists in a durable handoff/PR.
- #4644 and #5162 must be merged on origin/main.
- If #4643 is already merged, verify its merge SHA, write a stand-down handoff, and emit `transition-pilot-reconciled=<merge-sha>`.

DISCOVERY REPORT BEFORE ACTION:
- current origin/main SHA;
- #4643 live state and failing checks;
- exact files in #4643 still absent or stale on origin/main;
- smallest safe supersede scope;
- reason any #4643 file is excluded.

PROVENANCE:
- research: #4643 pasted transition closeout is context only; live #4643 diff and current consumer code are source
- documents: PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC; PHOENIX_ARC_FIRST_CANONICAL_SPEC; PHOENIX_V4_5_WRITER_SPEC
- builds_on: TRANSITION consumer `phoenix_v4/planning/transition_atoms.py`; registry resolver `_KNOWN_SLOT_DIRS`; composer `_authored_transition`
- inventory: EXTENDS; no render-glue resurrection; no slot contract reduction

MISSION:
Land or supersede the useful #4643 transition atom work from a fresh branch. Do not merge #4643 as-is.

SCOPE DEFAULT:
- Prefer cleanly porting only:
  - `atoms/gen_z_professionals/anxiety/TRANSITION/CANONICAL.txt`
  - `atoms/corporate_managers/financial_stress/TRANSITION/CANONICAL.txt`
- Only include identity contracts, chapter thesis bank, or the de-injection spec if live discovery proves they are still needed and non-duplicative.
- Do not touch PM hot files.

DELIVERABLES:
- clean PR superseding #4643, linked in the PR body
- `artifacts/qa/transition_4643_supersede_20260715/`
- `artifacts/coordination/handoffs/transition_4643_supersede_20260715.md`
- exact signal token `transition-pilot-reconciled=<full-squash-merge-SHA>`

SMALLEST SAFE BATCH:
- smoke: port/validate one transition bank (`gen_z_professionals/anxiety`) and prove parser/select works for all four boundaries.
- pilot: port/validate both pilot transition banks.
- scale: no wider scale in this lane. Wider TRANSITION coverage waits for Wave 4B after pilot render-read.

WATCHDOG POLLING / HANG PREVENTION:
- poll interval: 2 minutes for CI.
- no-progress rule: after two unchanged polls, inspect failed job logs.
- hard stall rule: after three unchanged polls, fix obvious lane-owned failures or BLOCK with evidence.
- max window: 90 minutes.

TESTS/PROOFS:
- targeted parser/select proof using `phoenix_v4.planning.transition_atoms.select_authored_transition`
- `PYTHONPATH=. python3 -m pytest tests/unit/rendering/test_deinjection_phase1.py tests/unit/rendering/test_composer_glue_off_default.py -q`
- `PYTHONPATH=. python3 scripts/ci/check_canonical_atom_parse_sweep.py`
- `git diff --check`
- PR checks watched to MERGED or BLOCKED

DO NOT:
- do not merge #4643 directly.
- do not enable render glue.
- do not edit broad thesis/identity config unless discovery proves it is required.
- do not scale beyond the two pilot cells.
- do not leave PR-open-only success.

LANDING CONTRACT:
- MERGED: PR opened, required checks green, squash-merged, signal emitted.
- BLOCKED: exact blocker, evidence, remote branch pushed if useful, handoff written.

CLEANUP LEDGER REQUIRED:
- worktree:
- local branch:
- remote branch:
- scratch files:
- background jobs:
- held artifacts:

HANDOFF REQUIRED:
- `artifacts/coordination/handoffs/transition_4643_supersede_20260715.md`

CLOSEOUT_RECEIPT:
- AGENT=Pearl_Dev
- LANE=transition_4643_supersede_20260715
- STATUS=MERGED|BLOCKED
- BRANCH:
- PR:
- MERGE_SHA:
- SIGNAL=transition-pilot-reconciled=<full-squash-merge-SHA>
- PROOF_ROOT=artifacts/qa/transition_4643_supersede_20260715/
- TESTS:
- CLEANUP:
- HANDOFF:
- NEXT_ACTION:
```
