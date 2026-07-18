# Grief short-format chapter flow gate fix

## Diagnosis (pre-fix)

- **Grief** `micro_book_15` / `micro_book_20` / `short_book_30` failed chapter flow while **anxiety** at the same formats passed in the duration matrix because spine pipeline called `chapter_flow_gate_report(prose)` **without** `plan` or `runtime_format_id`, so the gate always used the **standard** profile.
- Grief prose uses **many short paragraphs** (line-broken TTS-style blocks). Adjacent token Jaccard overlap is often **&lt; 0.05**, which tripped `CHOPPY_SECTION_JUMPS` under standard thresholds even when transitions read fine.
- **Chapter 12** in micro grief could be a **very short tail** (few sentences), hitting `TOO_SHORT_FOR_AUDIO_FLOW` and related errors; `TOO_SHORT` was not in the glue fixable set, so `strengthen_chapter_flow_for_delivery` did not repair it.

## Implementation

1. **`phoenix_v4/quality/chapter_flow_gate.py`**
   - `SHORT_FORM_RUNTIME_FORMAT_IDS` = `micro_book_15`, `micro_book_20`, `short_book_30`.
   - `flow_profile_for_runtime_format()` and `evaluate_chapter_flow(..., flow_profile=)`:
     - **short_form**: min transition cues **2** (vs 3), min sentences for hard TOO_SHORT **10** (vs 14) with **warning** instead of error when **2–9** sentences (`SHORT_TAIL_CHAPTER_FOR_MICRO_FORMAT`).
     - **CHOPPY_SECTION_JUMPS** skipped for short_form when paragraph count **&gt; 14** or **≤ 4** (many thin ¶ or brief tail).
   - `evaluate_chapter_flow_with_slots` accepts `flow_profile`.

2. **`phoenix_v4/rendering/book_renderer.py`**
   - `_resolve_chapter_flow_profile(plan, runtime_format_id=...)`.
   - `chapter_flow_gate_report(..., runtime_format_id=...)` so spine/registry callers can pass CLI format.
   - `strengthen_chapter_flow_for_delivery` / `strengthen_rendered_spine_manuscript` take `flow_profile` and pass it to `evaluate_chapter_flow`.
   - `render_book` passes `runtime_format_id` into `chapter_flow_gate_report`.

3. **`phoenix_v4/rendering/chapter_composer.py`**
   - `compose_from_enriched_book` passes `flow_profile_for_runtime_format(enriched.runtime_format)` into `strengthen_rendered_spine_manuscript`.

4. **`scripts/run_pipeline.py`**
   - Spine and registry render paths pass `runtime_format_id` into `chapter_flow_gate_report` so pilot cells match production profiling.

## Verification (2026-04-12)

| Target | Chapter flow result |
|--------|---------------------|
| grief `micro_book_15` | **PASS** 0/12 failed — `artifacts/pilots/grief_flow_fix/micro_book_15/chapter_flow_report.json` |
| grief `micro_book_20` | **PASS** 0/12 failed — `artifacts/pilots/grief_flow_fix/micro_book_20/chapter_flow_report.json` |
| grief `short_book_30` | **PASS** 0/12 failed — `artifacts/pilots/grief_flow_fix/short_book_30/chapter_flow_report.json` |
| anxiety `standard_book` (regression) | **PASS** 0/12 failed — `/tmp/regression_check/chapter_flow_report.json` |

**Standard+ thresholds unchanged** when `flow_profile` is `standard` (default for `standard_book` and all non-listed formats).

## Tests

- `tests/test_chapter_flow_gate.py`: short_form choppy skip + `flow_profile_for_runtime_format` mapping.
