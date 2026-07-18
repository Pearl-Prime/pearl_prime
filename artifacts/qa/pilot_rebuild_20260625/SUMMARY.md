# Pilot Rebuild Evidence — educators + nyc_executives × 4 cells

**Date:** 2026-06-25
**origin/main SHA at build:** `091e753823789c623fe2b66f406f4d6e849f1f14`
**Build env:** isolated git worktree off origin/main (shared main tree churned
between `pr1899-rebase` and sibling refs mid-run; builds re-run in isolation).

Command per cell:

    PYTHONPATH=. python3 scripts/run_pipeline.py --no-job-check --enforce-scene-gate \
      --pipeline-mode spine --quality-profile production --exercise-journeys \
      --persona <P> --topic <T> --arc <first-matching-arc.yaml> \
      --render-book --render-dir /tmp/<subdir>

## Headline

All 4 pilot cells HARD-FAIL the tuple-viability preflight (BUILD_EXIT=1) before
Stage 1. No book is produced and no register_gate_report.json is written — the gate
aborts at the entry check (scripts/run_pipeline.py:2531,
phoenix_v4/gates/check_tuple_viability.py). register_verdict = N/A (build never
reached the register gate). This is an upstream atom/binding gap, not a
register/word-budget/ei_v2 finding.

## Per-cell results

| Cell | persona × topic | arc (first match) | engine | BUILD_EXIT | viability verdict | register | ei_v2 | words |
|------|-----------------|-------------------|--------|-----------|-------------------|----------|-------|-------|
| 1 | educators × burnout | educators__burnout__overwhelm__F006 | overwhelm | 1 | FAIL: NO_STORY_POOL | N/A | N/A | 0 |
| 2 | educators × imposter_syndrome | educators__imposter_syndrome__false_alarm__F006 | false_alarm | 1 | FAIL: NO_BINDING + NO_STORY_POOL | N/A | N/A | 0 |
| 3 | nyc_executives × burnout | nyc_executives__burnout__overwhelm__F006 | overwhelm | 1 | FAIL: NO_STORY_POOL | N/A | N/A | 0 |
| 4 | nyc_executives × anxiety | nyc_executives__anxiety__false_alarm__F006 | false_alarm | 1 | FAIL: BAND_DEFICIT (missing band 1) | N/A | N/A | 0 |

## Triage (read-only; no fixes applied)

Viability gate requires a STORY pool at atoms/<persona>/<topic>/<engine>/CANONICAL.txt
with >=12 variants whose BAND: values cover the arc emotional_curve bands, plus a
topic_engine_bindings.yaml entry allowing <engine> for <topic>.

### Cell 1 — educators × burnout × overwhelm -> NO_STORY_POOL
- atoms/educators/burnout/overwhelm/ does NOT exist. Binding OK (burnout allows
  overwhelm, watcher, grief). Needed: seed engine-keyed STORY pool >=12 banded
  variants. Present: 0/12.

### Cell 2 — educators × imposter_syndrome × false_alarm -> NO_BINDING + NO_STORY_POOL
- BINDING MISMATCH: imposter_syndrome allows only [shame, comparison]; the seeded
  arc (#1913) targets engine false_alarm, which the topic binding does NOT permit.
  Pool atoms/educators/imposter_syndrome/false_alarm/ also absent. Needed: re-point
  arc to an allowed engine + seed that pool, OR a binding-governance decision to add
  false_alarm to imposter_syndrome (not Pearl_Dev's call). Present: 0/12.

### Cell 3 — nyc_executives × burnout × overwhelm -> NO_STORY_POOL
- atoms/nyc_executives/burnout/overwhelm/ does NOT exist (same shape as Cell 1).
  Binding OK. Needed: seed engine-keyed STORY pool >=12 banded variants. Present: 0/12.

### Cell 4 — nyc_executives × anxiety × false_alarm -> BAND_DEFICIT (missing band 1)
- Closest to buildable. Pool EXISTS:
  atoms/nyc_executives/anxiety/false_alarm/CANONICAL.txt = 26 STORY variants (depth OK).
  Binding OK. Pool bands {2,3,4,5}; arc requires {1,2,3,4,5} -> missing band 1.
  Needed: add >=1 band-1 STORY variant, OR re-point arc curve to open above band 1.

## P1/P2 wave delivered vs. what the build needs

P1 (#1913) seeded arc YAMLs; P2 (#1915) backfilled SLOT-keyed pools (STORY/HOOK/...
directly under the topic). But the spine builder reads the STORY pool from the
ENGINE-keyed dir atoms/<persona>/<topic>/<engine>/. For 3 of 4 cells that
engine-keyed STORY pool was never created (burnout/overwhelm, imposter/false_alarm),
so the cells are arc-backed but not build-viable. Cell 4 has the engine pool but is
one band short.

## NEXT_ACTION
- EPUB-ready now: 0/4.
- Marginal (1 atom): Cell 4 — add a band-1 STORY variant to the existing 26-variant pool.
- Need full engine-keyed STORY pool seed (>=12 banded variants): Cells 1 & 3
  (burnout × overwhelm, both personas).
- Need binding decision + arc re-point + pool seed: Cell 2 (imposter_syndrome ×
  false_alarm is a disallowed engine).
- These are atom/seeding + binding-governance frontiers, NOT engine or gate-threshold
  fixes. No gate was loosened in this pass.
