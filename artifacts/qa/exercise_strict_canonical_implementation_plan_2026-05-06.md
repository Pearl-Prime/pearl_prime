# EXERCISE-BANK-RESOLUTION-01 — Strict-Canonical Production Gate Implementation Plan

**Date:** 2026-05-06  
**Cap entry:** EXERCISE-BANK-RESOLUTION-01 in docs/PEARL_ARCHITECT_STATE.md  
**Status:** diagnostic + recommended patch (no code change in this PR — testing requires local env)

## Goal

Per cap-entry option 1: when `--quality-profile production`, raise
`EnrichmentGapError` if EXERCISE slots resolve via `practice_library`
fall-through. Production must resolve EXERCISE from `teacher_banks`
(approved_atoms/EXERCISE) or persona-atom EXERCISE bank — not
practice_library (which is the spec §4.5 third source).

## Current code path (origin/main)

`phoenix_v4/planning/enrichment_select.py:944-995` (PR #612 additive
mode, EXERCISE-slot rule):

```python
if stype == "EXERCISE":
    # teacher → practice_library → fall-through hard-fail
    _at_hit_ex = ...try teacher_atoms...
    if _at_hit_ex:
        # use teacher_atom; audit_counts["slots_from_teacher"] += 1
    else:
        _apl = _try_practice_library(chapter_index0, topic, persona_id, seed)
        if _apl:
            _add_pieces.append(_apl[0])
            _add_sources.append("practice_library")
            audit_counts["slots_from_practice_library"] += 1
```

`phoenix_v4/planning/enrichment_select.py:1063-1077` already raises
`EnrichmentGapError` when ALL sources empty. The new gate raises
when production AND practice_library fired.

## Recommended patch (POST-enrichment gate; smallest scope)

In `scripts/run_pipeline.py`, after each enrichment call site that
captures `audit_counts`, add the gate:

```python
# EXERCISE-BANK-RESOLUTION-01: strict-canonical for production.
# Production MUST resolve EXERCISE from teacher_banks/approved_atoms or
# persona-atom EXERCISE bank — not practice_library fall-through.
if quality_profile == "production":
    _practice_lib_count = audit_counts.get("slots_from_practice_library", 0)
    if _practice_lib_count > 0:
        from phoenix_v4.planning.enrichment_select import EnrichmentGapError
        raise EnrichmentGapError(
            f"EXERCISE-BANK-RESOLUTION-01 strict-canonical (production): "
            f"{_practice_lib_count} EXERCISE slot(s) resolved via "
            f"practice_library fall-through. Production must resolve "
            f"from teacher_banks/approved_atoms/EXERCISE or persona-atom "
            f"EXERCISE bank. Add atoms upstream (Pearl_Editor + "
            f"Pearl_Writer ws), or use --quality-profile draft/debug "
            f"to allow practice_library fall-through during dev."
        )
```

**Diff size:** ~15 lines per call site. Two call sites identified:
1. After single-book enrichment in `_render_book` (~line 629 region)
2. After per-chapter enrichment in catalog loop (~line 2163 region)

Total ~30 lines patched.

## Test plan (separate Pearl_Dev session with local env)

- `tests/test_exercise_strict_canonical.py` (NEW):
  - `test_strict_gate_raises_on_production_when_practice_library_fires`
  - `test_strict_gate_allows_practice_library_on_draft_profile`
  - `test_strict_gate_passes_when_teacher_or_persona_atom_resolves`
- Smoke run on gen_z_professionals × anxiety with
  `--quality-profile production` + no teacher EXERCISE atoms (should
  now raise EnrichmentGapError instead of silently falling through to
  practice_library).
- Smoke run on same with `--quality-profile draft` (should fall through
  to practice_library as before; backward-compatible).

## Why this PR is diagnostic-only, not the fix

The patch is well-defined but pushing untested production-code changes
without a local test environment is risky. Specifically:
- Cannot run `pytest tests/test_exercise_strict_canonical.py -v` locally
  (LFS smudge filter issues observed in prior recovery).
- Cannot run the smoke render to verify gate fires correctly.
- A regression here would gate ALL production renders, blocking all
  catalog work.

## Followup ws (Pearl_Dev with local env)

`ws_exercise_strict_canonical_production_$DATE` (still open):
- Apply the patch above to `scripts/run_pipeline.py`
- Add the test file
- Run pytest + smoke
- Verify draft profile still allows fall-through (backward-compat)
- Open implementation PR

## Closes

- This PR closes the **diagnostic** half of `ws_exercise_strict_canonical_production_$DATE`
- The implementation half re-opens for Pearl_Dev local-env session

🤖 Generated with [Claude Code](https://claude.com/claude-code)
