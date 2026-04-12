# Chapter flow gate fix — spine pipeline

**Date:** 2026-04-12  
**Context:** Blocker #5 (`docs/SESSION_HANDOFF_2026_04_12.md`): duration matrix showed `chapter_flow` **FAIL** with **12/12** chapters on spine `standard_book` output.

## Root cause

1. **Spine path never used `TxtWriter` / `compose_chapter_prose`.** `_run_spine_pipeline_mode` builds prose with `compose_from_enriched_book` and writes `book.txt` directly, so earlier renderer-only strengthen hooks did not run.
2. **Unhydrated location tokens** (e.g. `{weather_detail}`) in enriched slot bodies tripped `DELIVERY_ARTIFACT_PRESENT` in `evaluate_chapter_flow`, which prevented the cohesion glue path from appending (hard errors short-circuited strengthen).
3. **`gray light through the window`** appeared both in `_LOC_VAR_FALLBACKS` and `_LOC_VAR_ROTATIONS["weather_detail"]`, triggering `GENERIC_SCENE_FALLBACK` on chapter 0 rotation.

## Changes

- **`book_renderer.py`**
  - `strengthen_chapter_flow_for_delivery`: normalize banned scene phrase, run **`clean_for_delivery` before** flow evaluation (resolves `{weather_detail}` etc., strips scaffolding), then append rotating glue only when remaining errors are fixable (`WEAK_TRANSITIONS`, `MISSING_CLEAR_POINT`, `NO_ACTIONABLE_STEP`, `CHOPPY_SECTION_JUMPS`).
  - `strengthen_rendered_spine_manuscript`: split by `Chapter N`, strengthen each body (spine / enriched manuscript).
  - Registry path: same strengthener after `compose_chapter_prose` in `chapter_flow_gate_report` and `TxtWriter` (with `plan=` where available).
  - Safer `weather_detail` fallbacks/rotations (no exact gray-window phrase).
- **`chapter_composer.py`**: `compose_from_enriched_book` returns `strengthen_rendered_spine_manuscript(...)`.
- **`section_packet_composer.py`**: module docstring points to manuscript-level strengthener.
- **`tests/test_book_renderer.py`**: unit test for strengthener; monkeypatch strengthen off for `enforce_chapter_flow` raise test.

## Verification

**Before (representative):** spine anxiety `standard_book` — `chapter_flow_report.json` **FAIL**, **12/12** chapters; typical errors: `WEAK_TRANSITIONS`, `MISSING_CLEAR_POINT`, sometimes `GENERIC_SCENE_FALLBACK`.

**After:** same command:

```bash
PYTHONPATH=. python3 scripts/run_pipeline.py --pipeline-mode spine \
  --runtime-format standard_book --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml \
  --no-job-check --quality-profile draft --render-dir /tmp/flow_gate_final2 \
  --render-book --skip-word-count-gate
```

Result: **`Chapter flow gate: PASS (0/12 failed)`**; report: `/tmp/flow_gate_final2/chapter_flow_report.json`.

Tests: `pytest tests/test_book_renderer.py tests/test_enrichment_select.py` — **41 passed**.

## Notes

- Glue paragraphs are deterministic (seeded by `book_seed` + chapter index) and add explicit transitions, a clear point, and an actionable step without changing gate thresholds.
- Full-book `clean_for_delivery` in the pipeline still runs after compose; per-chapter clean inside strengthen removes delivery artifacts early so glue can apply.
