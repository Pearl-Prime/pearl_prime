# Engine-keyed arc-gen pilot — NO_ARC unlock (educators + nyc_executives)

**Date:** 2026-06-29 · **Branch:** agent/story-pool-arc-gen-20260629 · **Ref:** OPD-20260629-004 (Q-BIND-01)
**Lane:** CPU-only catalog unlock (GPU-free, no paid LLM, no Qwen). Staged for ~Jul 1 CI reset.

## Premise correction (why this is arc-gen, not atom authoring)

The original lever ("seed engine-keyed STORY pools via Pearl_Writer") rested on a **stale** diagnosis.
Verified on origin/main:

- Engine-keyed STORY pools **already exist** — 697 (educators) / 546 (nyc_executives) `CANONICAL.txt`,
  seeded by merged **#1928** (engine-angle seed) + **#1946** (band-1 seed). PROGRAM_STATE §47–52
  (truth-upped 6/25 via #1926, *before* those merges) still describes the gap as `NO_STORY_POOL`; that
  is out of date.
- The live blocker is **`NO_ARC`** — missing `config/source_of_truth/master_arcs/{p}__{t}__{engine}__F006.yaml`.
  educators had 11 arcs, nyc 13 (one canonical engine per topic). Non-canonical engines fail NO_ARC.
- Fix = **deterministic** `scripts/generate_arcs_from_backlog.py` (template-scaled, no LLM/GPU —
  see [[reference_arc_authoring_mechanism]]). Dry-run: **661 missing arcs** for educators+nyc.

## Decision — OPD-20260629-004 (Q-BIND-01)

`imposter_syndrome.allowed_engines` extended `[shame, comparison]` → `[shame, comparison, false_alarm]`.
Operator-approved (expands sellable cells: imposter_syndrome × false_alarm). Logged here; TSV row to be
appended via the serial governance lane to avoid hot-file conflict.

## Pilot result (6 arcs generated, CSV-scoped subset — NOT all 661)

| Cell | tuple-viability | Note |
|---|---|---|
| educators × anxiety × false_alarm | ✅ TUPLE_VIABLE | arc-gen flipped NO_ARC → viable |
| educators × anxiety × spiral | ✅ TUPLE_VIABLE | " |
| educators × anxiety × watcher | ✅ TUPLE_VIABLE | " |
| nyc_executives × anxiety × spiral | ⚠️ BAND_DEFICIT (missing band 1) | arc OK; STORY pool lacks a band-1 atom |
| nyc_executives × anxiety × watcher | ⚠️ BAND_DEFICIT (missing band 1) | " |
| educators × imposter_syndrome × false_alarm | ⚠️ NO_STORY_POOL | binding+arc reachable; needs engine-keyed pool seeded |
| nyc_executives × imposter_syndrome × false_alarm | ⚠️ NO_STORY_POOL | " |

**Finding:** arc-gen is *necessary but not always sufficient*. It flips cells that already carry full-band
(1–5) STORY pools (the 3 educators/anxiety cells). It also surfaces the true residual gaps —
a single band-1 atom for nyc/anxiety, and an absent imposter×false_alarm STORY pool — which are the
legitimate small Pearl_Writer follow-ups (per [[project_thin_persona_tuple_viability]]: BAND_DEFICIT = add band-1 atoms).

## Build proof — educators × anxiety @ standard_book_60min (CPU)

`scripts/pilot/run_spine_pipeline.py` → **12 chapters / 12,000 words, 0 empty slots**, coherent
persona-accurate prose (educators voice: progress-monitoring forms, state-exam week, grading at 10 PM).
Output: `educators_anxiety/book.txt`, `book_plan.json`, `budget.json`, `enrichment_audit.json`.

### Register gate — FAIL (composer-frontier handoff, NOT chased here)

`phoenix_v4/quality/register_gate.py` verdict = **FAIL**: F6 (cadence repetition), F7 (over-prescribed
practice density, all 12 chapters), F13 (dwell/integration starvation). Per operator instruction, a cell
that *builds but register-FAILs* is a **composer-frontier handoff to OPD-20260629-002** (PRs #3110/#3123,
the same F7 practice-density family as self_worth), **not** an atom/arc gap. Noted, not chased.
Two pilot-path caveats also visible (and orthogonal to the arc-gen unlock): `run_spine_pipeline.py` ran the
**degraded legacy prose-chunk** enrichment (slot pools lack `## ARC_POSITION vNN` headers) and `DEFECT4`
skipped Gen-Z-keyed depth-registry sections for the thin `educators` persona.

## Verdict

Arc-gen is the correct GPU-free lever and **moves the catalog forward**: 3 cells flipped to buildable +
the binding decision lands. It is *complementary* to OPD-20260629-002 — A makes cells buildable, B makes
them register-pass. Validation-before-scaling held: only 6 arcs generated (not 661); residual gaps
documented as the next batch rather than scaled-into.

## NEXT_ACTION (cold-start-ready, batched ≤180-file PRs)

1. **Band-1 atom** for nyc_executives × anxiety (one band-1 STORY atom clears BAND_DEFICIT for spiral+watcher).
2. **Seed imposter_syndrome × false_alarm** engine-keyed STORY pool (educators + nyc) → clears NO_STORY_POOL.
3. **Expand arc-gen** to the remaining ~655 NO_ARC tuples in ≤180-file batches (deterministic; re-check
   viability per batch; cells with full-band pools flip immediately).
4. **Register-PASS** for any built cell is owned by OPD-20260629-002 (composer lane) — do not double-actor.
