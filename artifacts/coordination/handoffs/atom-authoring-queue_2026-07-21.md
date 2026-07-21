# Handoff — Lane 02 atom-authoring-queue (2026-07-21)

STARTUP_RECEIPT:
- AGENT=Pearl_Writer+Pearl_Editor (running as Claude Sonnet 5 in this session)
- LANE=atom-authoring-queue
- STATUS=MERGED

## What this covers

Per the operator's split ("Cursor codes Lanes 01/03/04, Claude authors Lane 02 +
lands everything"), this session did the AUTHOR half of Claude's two jobs only.
The LAND half (review + commit Cursor's Lane 01/03/04 diffs) and the
smoke-test/verify step for this bank are explicitly deferred until Lane 01
(`check_book_story_authored.py` + gate wiring) lands — Lane 02's own prompt
depends on Lane 01's output format to confirm `research_fit_bound` flips
`false -> true`, and this session was told to hold verification rather than
stall waiting on it while it authors.

## Cell authored

`millennial_women_professionals × courage × false_alarm` — the exact
(persona, topic) pair the operator flagged from seed 43001
(`research_fit: {}`, no `story_atoms` dir, `mechanism_called=0`).

Engine chosen: `false_alarm`, per `config/topic_engine_bindings.yaml:65-81`
(`courage.allowed_engines = [false_alarm, shame, spiral]`; notes: "Bold action
blocked by body alarm, visibility/exposure fear, catastrophic prediction
chains" — false_alarm is the most direct fit for the operator's flagged gap).

Directory contract matched exactly to
`story_atoms/millennial_women_professionals/anchored/anxiety/overwhelm/`
(4 arc positions × 4 variants = 16 files):

```
story_atoms/millennial_women_professionals/anchored/courage/false_alarm/
  recognition/micro/{v01,v02,v03,v04}.txt
  mechanism_proof/micro/{v01,v02,v03,v04}.txt
  embodiment/micro/{v01,v02,v03,v04}.txt
  turning_point/micro/{v01,v02,v03,v04}.txt
```

## Named mechanism (not the generic recognition_before_action boilerplate)

**"The exile reflex"** — the body's threat-detection system fires the same
banishment-level alarm (cold hands, tight chest, closed throat) for social/
professional exposure (stating a number, submitting a form, raising a flag in
a meeting) as it would for literal expulsion from the tribe, because it can't
tell a bad quarter from a bad tribe. Courage in this bank is not the absence
of the alarm — it's recognizing the alarm is real about the sensation and
wrong about the stakes, and acting through it anyway. Four independent
character throughlines (Alina — pricing pushback, Priya — self-nomination,
Renata — client bad-news, Devi — flagging a technical risk to a senior
stakeholder) each plant the physical alarm at `recognition`, deepen its cost
at `mechanism_proof`, model the integrated state at `embodiment`, and name
the mechanism explicitly at `turning_point`.

## What happened after Cursor's Lane 01/03/04 diffs landed in the working tree

Reviewed each of Cursor's three lanes against its own prompt file's
TESTS/PROOFS section (not taken on faith):
- Lane 01 (`check_research_fit_honesty.py`, `check_book_story_authored.py`,
  gates 34-35, drift-detectors steps): advisory-only as required, correct.
- Lane 03 (`run_random_2h_book_x100.py`): plain `subprocess.Popen` +
  `terminate()/kill()`, no process-group kill; `--n 3` smoke run correctly
  SKIP-UNAUTHORED + logged backlog.
- Lane 04 (`phoenix_v4/quality/acceptance_layer.py` wired into
  `run_pipeline.py`): numeric floors cited verbatim from the scorecard, never
  auto-assigns Layer 3/4.

Two unrelated, uncommitted sibling-session changes were found co-mingled in
the same shared working tree (a separate evergreen social-atom-bank gate/
config set, and an unrelated music-mode auto-detect hunk in
`run_pipeline.py`) — both were surgically excluded from this lane's commit
via git-plumbing (temp index off `origin/main^{tree}`) and left untouched in
the working tree for their own owning sessions to land.

**Real smoke test run** (not hand-waved): `run_pipeline.py --pipeline-mode
spine --quality-profile production --exercise-journeys --seed 43001` for
`millennial_women_professionals × courage` (arc
`config/source_of_truth/master_arcs/millennial_women_professionals__courage__false_alarm__F006.yaml`).
Result: `book_acceptance_stamp.json` → `acceptance_layer: path_works`
(Layer 1 not clean — `register_gate` HARD_FAIL on an unrelated F2
dangling-preposition finding in chapter 5, plus `bestseller_craft` 0.5247 <
0.55 floor). Proof root:
`artifacts/qa/bestseller_atom_flow_20260721/millennial_women_professionals__courage__false_alarm_seed43001/`.

**`research_fit_bound` did NOT flip to true — and cannot yet**, for a reason
outside this lane's or Lane 01's scope: `enrichment_audit.json`'s
`research_fit` key came back `null`, not even `{}`. `build_story_schedule()`
(`phoenix_v4/planning/story_planner.py`) is not wired into
`scripts/run_pipeline.py`'s spine render path on this branch at all — the
book fell through to the legacy engine-keyed `atoms/<persona>/<topic>/...
CANONICAL.txt` path instead of ever looking at `story_atoms/anchored/`. This
matches Lane 01's own handoff discovery note verbatim ("research_fit
stamping is not yet wired into scripts/run_pipeline.py"). The Lane 03 driver
does correctly detect the new bank on disk (`_has_story_atoms(...) → True`),
confirming the bank itself is directory-correct; the render-path wiring gap
is a separate, deeper fix not in scope for any of the 4 lanes in this pack.

`mechanism_called` is also confirmed NOT wired anywhere in the repo
(verified by Lane 04's own module docstring + grep) — so it cannot be
checked yet either, independent of the research_fit gap.

## Acceptance layer (honest, per scorecard)

This bank + the render/gate infrastructure is **infrastructure +
unverified-in-production authored prose**. NOT `authored_candidate` (needs
`research_fit_bound: true` AND `mechanism_called > 0`, neither available
yet). NOT bestseller. The gap is a follow-on lane: wire
`build_story_schedule()` into `run_pipeline.py --pipeline-mode spine`, then
re-run this exact smoke test.

## Landed — MERGED

- Branch: `agent/bestseller-atom-flow-20260721` (deleted post-merge)
- PR: https://github.com/Pearl-Prime/pearl_prime/pull/9
- MERGE_SHA: `280597dacf72ea1784389413fdd45aacc5449ea9` (squash-merge, 2026-07-21T07:10:28Z)
- 58 files changed total across 3 commits (56 in the initial commit + 1
  handoff update + 1 `docs/DATA_DICTIONARY.tsv` regen), 0 files deleted,
  well under push-guard/governance caps
- Local full `run_production_readiness_gates.py` (35 gates) confirmed
  gates 34/35 correctly WARN (not counted toward `failed`); only 2
  pre-existing, unrelated failures locally (gate 21 manga render-progress
  bytes — passed in CI's environment; gate 27 data dictionary — see below)
- CI: all checks PASS except `Core tests`, which fails on `main` itself
  (`ModuleNotFoundError: scripts.storyblocks.api_client`, from an unrelated
  storyblocks commit already merged to main before this PR) — verified via
  `gh run list --branch main --workflow "Core tests"` showing failure on
  every recent main commit, not introduced by this PR. Not fixed here
  (out of scope; belongs to the storyblocks/social-atom-bank workstream).
- CI initially also failed gate 27 (Enforced data dictionary): my two new
  `scripts/ci/check_*.py` gates weren't yet rows in
  `docs/DATA_DICTIONARY.tsv`. Fixed with a follow-up commit: extracted a
  clean `git archive` of exactly the builder's scan roots (`scripts/`,
  `phoenix_v4/`, `SOURCE_OF_TRUTH/composite_doctrine`,
  `SOURCE_OF_TRUTH/exercises_v4/approved`, `.github/workflows`,
  `config/source_of_truth/doctrine_rotation.yaml`) to avoid contaminating
  the dictionary with sibling-session uncommitted files sitting in the
  shared local working tree, ran `scripts/governance/build_data_dictionary.py`
  against that clean tree, confirmed the diff was exactly the two new WIRED
  rows, committed.
- Pre-merge safety check (`scripts/git/pre_merge_check.sh 9`): PASS
  (57→58 files, 0 deletions, well under caps).

## Next action

1. Watch PR #9 CI + governance review; squash-merge once green (operator
   auth already covers this per standing PR-governance rule).
2. Open the real follow-on: wire `build_story_schedule()` into
   `scripts/run_pipeline.py`'s spine path so `research_fit_bound` can
   actually flip for any authored `story_atoms/anchored/` cell, this one
   included. Re-run this exact smoke test once that lands.
3. Remaining priority backlog (frequency ranking not yet re-derived from
   trace logs): `first_responders × boundaries`, `healthcare_rns ×
   boundaries` — confirm from trace whether these already had banks before
   authoring.

CLEANUP: no worktree used; git-plumbing temp index (`/tmp/idx_bestseller_atom_flow`)
removed after commit; no local branch checkout disturbed (current checkout's
sibling-session uncommitted files untouched); no background jobs held; smoke
render at `/tmp/courage_smoke_43001` was copied into the repo proof root and
is otherwise scratch (removable).
