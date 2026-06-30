# Plan-Scale QA — ~1000-PLAN SWEEP verdict (count-invariant scope)

**Date:** 2026-06-30 · **Agent:** Pearl_Dev + Pearl_Research · **Runner:** `scripts/qa/plan_scale_qa_sweep.py`
(EXTENDS the pilot harness `scripts/qa/plan_scale_qa_suite.py` — imports `build_plan` / `plan_cohesion`, never forks)

Follows pilot PR #3605. Scope corrected by the pilot's own headline: **plan-only, deterministic, CPU,
count-invariant**. No `--render-book`, no LLM, no GPU.

## Sweep size & buildability

- **1,281 plans** = 183 arc-backed (persona × topic) cells × 7 durations (micro_15/20, short_30, standard, extended_2h, deep_4h, deep_6h)
- **Buildability census: PLANNABLE 1281 / 1281.** NO_ARC 0 · BAND_DEFICIT 0 · NO_STORY_POOL 0 · PLAN_ERROR 0.
  (Cells were chosen to already have arcs, so the sweep measures quality not buildability — as instructed.)
- 14 personas; thinnest on arcs: **educators (5 cells), gen_z_student (5), nyc_executives (6)**; all others 15, corporate_managers 17.

## Count-invariant cohesion pass rate: **1281 / 1281 (100%)**

Scored ONLY on count-invariant checks (arc coverage, band-arc smoothness, final-not-peak, dwell macro-cadence,
bestseller-structure variety, cost-chapter placement) — the set that passed 14/14 in the pilot. The structural /
chapter-count-vs-assembled proxy is **DROPPED from the verdict** (see Guardrail A).

Pass rate is uniform across every duration, persona, and topic (each: 183/183, etc.).

### META-FINDING (answers "is the screen trustworthy at scale?")

The count-invariant cohesion screen is **a trustworthy FLOOR but a NON-DISCRIMINATING gate.** It passes 100% of
template-generated plans because `generate_book_plan` is a deterministic, structurally-uniform template — every plan
satisfies the same invariants by construction. The screen will reliably catch a *malformed* plan, but it **cannot rank
or reject** plans on quality, because plan-level structure does not vary across the catalog. **Conclusion for the sweep
gate: the count-invariant screen is safe to run at 1000+ scale (zero false alarms, zero structural failures) but should
NOT be used as a quality SELECTOR — only as a pre-flight floor. Quality discrimination must happen at assembled-prose
time (register_gate / EI v2 / the repetition fix), not at plan time.**

## GUARDRAIL A — chapter-count finding: VERIFIED INTENDED-BY-DESIGN (NOT escalated)

The pilot's "structural proxy BROKEN" (assembled ≠ plan chapter count) was verified against the codebase's documented
distinction:

- **`compact_chapter_subset`** (spine-path count) in `config/format_selection/format_registry.yaml`: micro_15 `[1,4,7,10,12]`→5,
  micro_20→6, short_30→8. Formats `standard_book`+ have **no** subset → render the **full 12-chapter spine** (registry line 175:
  "Full 12-chapter spine (no compact_chapter_subset)").
- The assembler picks chapter count from the **spine** (`run_pipeline.py`: `load_spine(... runtime_format)` → `apply_knobs`
  → `compile_beatmap` → `_n_chapters = len(beatmap.chapters)`), NOT from `chapter_count_default` (a different SSOT,
  AUTO-PLAN-SSOT-01, for the auto-PLAN path).
- The compaction + renumber-1..N is the documented **PR-D-SPINE-01 / PR-G** design (`phoenix_v4/planning/knob_apply.py`
  docstring: "The renumbering is intentional…").

**Verdict: the ≥standard_book→12 clamp IS the documented word-budget/spine design.** Structural-proxy claim **DROPPED**
from the verdict. **No OPD-20260629-002 handoff opened for the chapter-count finding.** (The pilot's *register* F2 HARD_FAIL
on `burnout × extended_book_2h` remains a separate, valid prose-gate handoff — it is a render-time gate, unrelated to chapter count.)

## GUARDRAIL B — repetition DETECTOR (measure-only; routed, not fixed)

Plan-level between-atom repetition detector added (`within_book_repetition` + cross-cell aggregation). It scores at the
**assembled** chapter count (compact_chapter_subset / full spine), so it measures the repetition the READER actually gets,
not the arc's inflated 20-chapter count.

- **Within-book severity census: 1281 MEDIUM / 0 HIGH / 0 LOW / 0 NONE.** Every book has modest thesis repetition
  (`thesis_dups` 0–1 across 12 chapters; score 0.12–0.19). It rises with chapter count (compact formats 0.12 → 12-chapter
  formats ≥0.185) as the per-engine thesis pool (≈12 distinct) gets exhausted. No book is clean; none is severe.
- **Cross-cell repetition (the topic-agnostic reuse the blind read flagged): CONFIRMED + QUANTIFIED.** The top theses each
  appear across **128 different (persona × topic) cells** — chapter theses are **engine-keyed templates**, so any two books
  sharing an engine (e.g. `comparison`) get near-identical theses regardless of persona/topic. 30 theses recur in ≥3 cells.

**This is a DETECTOR result only.** The FIX is owned by the **Atom Cohesion Chunked Plan (A–F) / adjacency-aware selector**
(chunks A+E already dispatched). The flagged cells in `REPETITION_CENSUS.json` are a **ROUTE to that lane**, not a new lane.
Highest-value target for that lane: **engine-keyed thesis templating** (128-cell reuse) — diversify theses by persona/topic,
not just engine.

## micro_book_15 mid-sentence truncation

**FLAGGED as a standalone small follow-up (y).** Pilot observed micro_book_15 ending mid-sentence ("Breathing through the")
because the runtime word-ceiling clamp trims the final chapter tail. This is a renderer/word-budget bug local to
micro_book_15, **not fixed here** — route to a small renderer follow-up (own ticket).

## EI v2 spot-check

Not re-run at sweep scale (sweep is plan-only; EI v2 scores prose, not plans — running it on a plan is forbidden). The
pilot's render-time EI v2 (composite 0.59–0.67, all > 0.55 pass) stands as the assembled-quality reference.

## Files (aggregate only — no per-plan JSONs)

- `MATRIX.tsv` — all 1,281 rows (persona, topic, duration, engine, buildability, chapter_count, count-invariant cohesion, repetition severity/score)
- `SUMMARY.json` — census + pass rates by duration/persona/topic
- `REPETITION_CENSUS.json` — within-book flagged + cross-cell repeated theses (route to Atom-Cohesion lane)

## Verdict for scale-up

- **Buildability + count-invariant cohesion: GREEN at 1,281 plans** (100% PLANNABLE, 100% PASS, zero failures).
- **The count-invariant screen is a safe FLOOR, not a quality selector** — do not use it to rank/accept plans.
- **Repetition is universal-MEDIUM**; the engine-keyed thesis reuse (128 cells) is the highest-value cohesion fix — routed
  to the Atom Cohesion lane. micro_15 truncation routed to a small renderer follow-up.
- **No new escalations.** Chapter-count finding closed as intended-by-design.
