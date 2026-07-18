# Golden chapter workflow (Pearl Dev)

**Status:** implementation in progress.  
**Code:** `phoenix_v4/rendering/golden_chapter_synthesis.py`, spine composition in `phoenix_v4/rendering/chapter_composer.py` (`compose_from_enriched_book`).

## Problem

Spine enrichment resolved atoms into slots, but `compose_from_enriched_book` previously **concatenated** slot bodies in beatmap order. That behaves like a fragment assembler: weak transitions, repeated scene glue, markdown `---` lines, and shallow chapters even when `compose_chapter_prose` existed.

## Pivot

1. **Per chapter:** map enriched slots → virtual streams → `compose_chapter_prose` via `compose_golden_spine_chapter` (frame governance included).
2. **Post spine strengthen:** `strengthen_chapter_flow_for_delivery` still runs `_normalize_generic_scene_lighting`, which can inject a repeated signature phrase. Apply **book-wide** furniture limiting after `strengthen_rendered_spine_manuscript`.
3. **Sanitizer:** strip markdown dividers, Python dict/list–like repr lines, optional secular keyword strips for anxiety, fix common double-article glitches.
4. **Pilot / report:** `--golden-chapter-pilot` on spine renders writes `golden_chapter_report.json` plus extracted chapter text for acceptance review.

## Whole-book extension

Reuse the same per-chapter composer for all chapters; add cross-chapter forbidden-phrase memory (book-level caps) and optional repair loop (evaluate → sanitize → one rewrite pass) when LLM synthesis is wired.

## Acceptance language

Do not claim bestseller readiness for the full book until chapter_flow, editorial, scene_anchor_density, and book_quality_gate clear on a representative pilot. A single golden chapter may claim only: path works, exposed source gaps, or composition still leaking.
