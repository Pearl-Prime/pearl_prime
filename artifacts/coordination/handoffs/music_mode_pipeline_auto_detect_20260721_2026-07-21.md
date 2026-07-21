# Handoff — music_mode_pipeline_auto_detect_20260721

## Lane

Prompt 02 of `docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/`
(`02_Pearl_Dev_pipeline_auto_detects_music_brands.md`). Wave 1 of the
music-mode wizard→pipeline pack. Code diffs authored by a Cursor session;
reviewed, tested, and landed by this Claude session.

## Status: MERGED

- Branch: `agent/music-mode-pipeline-autodetect-lane02-20260721`
- PR: https://github.com/Pearl-Prime/pearl_prime/pull/11
- Merge SHA: `d2dd06943280a7bafa2463195955e2312f45b1f6`
- Signal: `music-pipeline-auto-detect-wired=d2dd06943280a7bafa2463195955e2312f45b1f6`

## What landed

- `scripts/catalog/music_mode_branch.py`: new
  `resolve_music_args_for_brand(brand_id)` reads the registry row's
  `musician_handle` + `status: active` gate, and the pointed survey YAML's
  `output_preferences_with_lyrics.companion_ai_song_consent` (defaults
  `with-lyrics` unless explicitly false). New `apply_auto_detected_music_args()`
  fills only the fields the operator did not explicitly pass — explicit CLI
  flags always win, never overridden.
- `scripts/run_pipeline.py`: wires `apply_auto_detected_music_args` into the
  brand-dispatch path.
- `phoenix_v4/planning/catalog_planner.py`: not touched — the `MUSIC_ONLY`
  branch gating BookSpecs was already correctly wired (PR #1008); verified via
  test, not re-implemented.
- Tests: `tests/catalog/test_music_mode_branch.py` — auto-detect for the one
  real active registry entry (`ahjan_music`), inactive/unregistered/Path-X
  no-ops, survey-consent-false variant, explicit-flag-always-wins (full +
  partial override).

## Landing notes — IMPORTANT contamination fix

The working-tree copy of `scripts/run_pipeline.py` (in
`/Users/ahjan/phoenix_omega`, dirty branch
`agent/bestseller-atom-flow-lanes-20260721`) had an **unrelated in-flight
change already mixed into it**: a ~70-line "book_acceptance_stamp" block from
a different, separately-authored, unmerged lane (`bestseller-atom-flow`, not
part of this pack). That block was NOT on `origin/main` and was not this
lane's work.

Fixed by isolating just Cursor's actual +13-line music-mode auto-detect hunk
(the `apply_auto_detected_music_args` call site, `@@ -3130,6 +3201,20 @@`) and
reconstructing `scripts/run_pipeline.py` = `origin/main`'s version + only that
hunk, verified byte-for-byte against the isolated hunk before committing. The
acceptance-layer block was excluded entirely — it belongs to a different lane
and was never reviewed or authorized as part of this pack.

## Evidence

- `python3 -m pytest tests/catalog/test_music_mode_branch.py -q` → 18 passed
- `python3 scripts/ci/check_canonical_pipeline_path.py` → PASS
- `python3 scripts/ci/audit_llm_callers.py --roots scripts/run_pipeline.py scripts/catalog/music_mode_branch.py --fail-on-violation` → 0 violations
- `python3 scripts/ci/pr_governance_review.py` → APPROVED
- `push_guard.py` → OK
- CI: 11/12 green; "Core tests" red is the same pre-existing, unrelated
  `origin/main` break documented in lane 01's handoff.

## Cleanup ledger

- worktree: `/Users/ahjan/phoenix_omega_wt_music_lane01_20260721` — reused
  sequentially for lanes 01/02/04; removed after the coordination handoff PR
  merges.
- local branch: deleted (squash-merged).
- remote branch: deleted (`--delete-branch` on merge).
- scratch files: `/private/tmp/.../scratchpad/patchwork/run_pipeline.py` (the
  isolated-hunk reconstruction) — held only for the session, not committed
  anywhere; safe to discard.
- background jobs: none held.

## Next action

Lane 05 (end-to-end smoke) starts next in this session — all of 01, 02, 03, 04
are now MERGED.
