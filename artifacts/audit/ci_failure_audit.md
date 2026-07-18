# CI Failure Audit — phoenix_omega_v4.8

**Date:** 2026-04-10
**Author:** Pearl_Dev
**PROJECT_ID:** proj_state_convergence_20260328

---

## Fixed Failures

### 1. Core tests: `test_render_book_enforce_chapter_flow_raises`

- **Workflow:** `core-tests.yml` → "Run fast/core pytest"
- **Test:** `tests/test_book_renderer.py::test_render_book_enforce_chapter_flow_raises`
- **Symptom:** `Failed: DID NOT RAISE ChapterFlowGateError` on CI (Python 3.11), passes locally (Python 3.9)
- **Root cause:** `chapter_flow_gate_report()` in `phoenix_v4/rendering/book_renderer.py` returned `"PASS"` when 0 chapters were extracted (vacuous truth: `"PASS" if failed == 0`). On Python 3.11, placeholder-only plans produce rendered text that `_extract_rendered_chapters` cannot parse into chapters, so `chapters = []`, `failed = 0`, status = `"PASS"` — the ChapterFlowGateError is never raised.
- **Fix:** Changed both branches (slot-level at line 758, text-only fallback at line 797) from `"PASS" if failed == 0` to `"PASS" if (failed == 0 and len(chapters) > 0)`. A book with 0 extractable chapters now always FAILs.
- **Commit:** `fix: chapter_flow_gate_report vacuous PASS on 0 chapters`
- **Verification:** 1368/1368 tests pass, production readiness gates pass, preflight OK.

---

## Known Remaining Failures (not fixed in this workstream)

### 2. Release gates: Rigorous system test — missing gen_z_student atoms

- **Workflow:** `release-gates.yml` → "Rigorous system test (skip sim for speed)"
- **Test:** `test_non_story_atoms_for_all_books`
- **Symptom:** `Non-STORY coverage not 100%: missing canonical pools for 15 (persona, topic, slot_type) combinations`
- **Detail:** Missing atoms for `gen_z_student` persona in 3 topics (`compassion_fatigue`, `financial_anxiety`, `financial_stress`) across 5 slot types (`HOOK`, `SCENE`, `REFLECTION`, `EXERCISE`, `INTEGRATION`)
- **Impact:** Only runs on push/schedule (`if: github.event_name != 'pull_request'`), does NOT block PRs
- **Root cause:** Content gap — atoms were never written for these persona×topic×slot combinations
- **Recommended fix:** Generate missing atoms via atom writing campaign (`scripts/atom_writing/run_writing_campaign.py`)
- **Not fixed here:** Content generation is out of scope for this workstream

### 3. Release gates: Pearl Prime release evidence — missing canary artifact

- **Workflow:** `release-gates.yml` → "Write Pearl Prime release evidence (push/schedule/dispatch)"
- **Symptom:** `Missing required evidence: artifacts/canary_plans/canary_summary.json`
- **Impact:** Cascading failure from rigorous test failing (canary step runs after rigorous test)
- **Root cause:** Pipeline canary step is skipped/fails when rigorous test fails first
- **Recommended fix:** Resolves automatically once gen_z_student atoms are written

### 4. Other failing workflows (not required for branch protection)

| Workflow | Conclusion | Notes |
|----------|-----------|-------|
| `change-impact.yml` | failure | Not a required check |
| `pearl-news-full-qa.yml` | failure | Not a required check |
| `max-quality-catalog.yml` | failure | Not a required check |
| `translate-bestseller-atoms.yml` | failure | Not a required check |
| `pages build and deployment` | failure | GitHub Pages deployment — not a required check |

These workflows are not in the branch protection required checks list. They should be triaged separately.
