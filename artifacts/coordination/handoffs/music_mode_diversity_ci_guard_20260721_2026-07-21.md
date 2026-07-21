# Handoff — music_mode_diversity_ci_guard_20260721

## Lane

Prompt 04 of `docs/agent_prompt_packs/20260721_music_mode_wizard_to_pipeline_wiring/`
(`04_Pearl_Dev_diversity_ci_guard.md`). Wave 1 of the music-mode
wizard→pipeline pack. Code diffs authored by a Cursor session; reviewed,
tested, and landed (with two real fixes) by this Claude session.

## Status: MERGED

- Branch: `agent/music-mode-diversity-ci-guard-lane04-20260721`
- PR: https://github.com/Pearl-Prime/pearl_prime/pull/12
- Merge SHA: `155f52f4df629d5533e9fbd7d39c6915a3967f6b`
- Signal: `music-diversity-gate-wired=155f52f4df629d5533e9fbd7d39c6915a3967f6b`

## What landed

Implements the already-ratified G1-G8 thresholds
(`MUSIC-MODE-BRAND-INTEGRATION-V1-01-AMENDMENT-DIVERSITY-GATES`): G1
per-slot-pool variant reuse ≤max(5, ceil(N/5)) HARD_FAIL; G2 topic
concentration ≤30% HARD_FAIL; G3 persona concentration ≤30% HARD_FAIL; G4
format concentration ≤50% HARD_FAIL; G5 locale concentration per-platform
HARD_FAIL; G6 title fuzzy-similarity clustering WARN; G7 author-bio reuse
WARN; G8 slot-atom rotation Gini WARN. Phase-A degraded mode for N<50 (G1
only; other gates explicitly skipped rather than false-passed).

- `scripts/qa/music_brand_diversity_lib.py` (new): pure metric-computation
  library, no I/O.
- `scripts/ci/check_music_brand_diversity.py` (new): CLI entry point
  `evaluate_kit` — the exact probed name `song_kit_generator.run_diversity_gate`
  already looked for, so that adapter now reports real verdicts with zero
  further changes on its side.
- `.github/workflows/music_brand_diversity.yml` (new): required PR check +
  nightly cron, mirroring the `Drift detectors` workflow's registration
  pattern.
- `tests/test_music_brand_diversity.py` (new): 31 tests, including a
  deliberately-failing fixture per HARD_FAIL gate (G1-G5) proving the gate
  actually catches violations (mutation-test evidence).
- Live proof: ran the gate against the real `ahjan_music` bank — PASS, G1
  correctly computed (9 unique bodies/pool, 0 reuse), G2-G8 correctly
  `skipped` (Phase-A degraded, 0 catalog rows). Report committed at
  `artifacts/qa/music_brand_diversity_report_ahjan_music_20260721.{md,json}`
  (intentional keeper, not scratch).
- `artifacts/coordination/CANONICAL_ARTIFACTS_REGISTRY.tsv`: new row,
  `concept_key=music_brand_diversity_gate` (NEW-ARTIFACT-JUSTIFIED — first
  implementation of the ratified G1-G8 spec; no prior canonical artifact for
  this exact purpose).
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`: flipped
  `ws_pearl_dev_music_brand_diversity_ci_guard_20260611` from `proposed` →
  `completed`.

## Landing notes — two real CI failures found and fixed (not dismissed)

The first push (before any fix) showed 3 red checks: "Core tests" (pre-existing,
unrelated — see below), plus two **real, PR-caused** failures:

1. **`check_canonical_pipeline_path.py` (Drift detectors) false-positive.**
   `scripts/ci/check_music_brand_diversity.py:282`'s `--quality-profile`
   argparse `help=` string mentions "run_pipeline.py" in prose (documenting
   which existing flag convention it mirrors) — the chord-completeness scanner
   matched that as an incomplete bestseller-chord invocation. This script
   never dispatches a pipeline run. Fixed per CLAUDE.md's documented exemption
   for prose/docstring references: added a `# CI-ALLOWLIST: legacy-registry-ok`
   comment on the line immediately preceding the flagged `help=` line (the
   scanner's `is_allowlisted` only looks 2 physical lines back — a
   multi-line comment block placed too far above the flagged line does NOT
   suppress it; confirmed by testing locally before pushing the fix).
2. **`docs/DATA_DICTIONARY.tsv` stale (Release gates, gate 27).** The new
   script's CLI flags weren't captured in the machine-generated dictionary.
   Fixed by running `scripts/governance/build_data_dictionary.py` and
   committing the 2-line diff (never hand-edited).

Both verified fixed locally before the second push; CI confirmed both green
on re-run.

## Evidence

- `python3 -m pytest tests/test_music_brand_diversity.py -q` → 31 passed
- `python3 scripts/ci/check_music_brand_diversity.py --brand-id ahjan_music --quality-profile production` → real run, PASS
- Mutation-test evidence: `test_g1_deliberately_duplicated_fixture_fails`,
  `test_g2_topic_concentration_fails_when_concentrated`,
  `test_evaluate_kit_g1_hard_fail_under_production_profile`,
  `test_evaluate_kit_full_mode_hard_fails_g2_when_topic_concentrated`, and
  siblings per G1-G5 all assert `HARD_FAIL` on deliberately-broken fixtures
- `python3 scripts/ci/audit_llm_callers.py --roots scripts/ci/check_music_brand_diversity.py scripts/qa/music_brand_diversity_lib.py --fail-on-violation` → 0 violations
- `python3 scripts/ci/check_canonical_pipeline_path.py --base origin/main --head HEAD --gate-mode fail` → PASS (after fix)
- `python3 scripts/ci/check_data_dictionary.py` → PASS (after regen)
- `python3 scripts/ci/pr_governance_review.py` → APPROVED WITH WARNINGS (workstream-overlap + reinvention warnings — both are this PR correctly registering itself as canonical for the first time; explained in PR comment, not a real fork)
- `push_guard.py` → OK
- CI (final): 13/14 green (including the new "Music brand diversity gate"
  workflow's own first run — PASS). "Core tests" red is the same
  pre-existing, unrelated `origin/main` break documented in lane 01/02's
  handoffs.

## Cleanup ledger

- worktree: `/Users/ahjan/phoenix_omega_wt_music_lane01_20260721` — reused
  sequentially for lanes 01/02/04; removed after this coordination handoff PR
  merges.
- local branch: deleted (squash-merged).
- remote branch: deleted (`--delete-branch` on merge).
- scratch files: none.
- background jobs: none held.
- held artifacts: `artifacts/qa/music_brand_diversity_report_ahjan_music_20260721.{md,json}`
  — DECLARED intentional keeper (mission sub-task 4's live proof), not mess.

## Next action

Lane 05 (end-to-end smoke) starts next in this session — all of 01, 02, 03, 04
are now MERGED.
