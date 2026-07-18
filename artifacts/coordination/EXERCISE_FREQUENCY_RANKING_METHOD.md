# Exercise Frequency Ranking — Method + Corpus (2026-07-07)

Companion to `exercise_frequency_ranking.tsv`. Read-only prep for the A+ frame-authoring rollout (specs/RENDITION_SYSTEM_SPEC.md §3.3/§5.3, OPD-20260707-001): which practice-library exercises to author frames for first. **No authoring, no wiring — analysis artifact only.** Lane re-parks behind `flagship-read-approved` after this lands.

## Key finding (changes how "frequency" can honestly be measured)

The 29 compiled books on main (`selected_content_variants.json`, plus all 80 `enrichment_audit.json`) contain **zero practice-library ids** — their EXERCISE slots carry persona-atom ids (`EXERCISE vNN`, `source: persona_atom`), the pre-practice-library path. So an artifact-count ranking is impossible today; the practice library's catalog exposure is **prospective**, governed by the loader's deterministic selection.

Selection is a uniform hash within per-type pools (`_deterministic_index` over `content_type` pools). The store (`SOURCE_OF_TRUTH/practice_library/store/practice_items.jsonl`) is exactly **8 content types × 34 items = 272**. Uniform hash ⇒ every item in a type has equal expected share — item-level "heat" exists **only where a plan names an id explicitly**.

## Ranking model

- **Tier 1 — plan-named (author frames FIRST):** `med_007` (= `lib34_meditations_07`), named 4× in the flagship ch1 twelve-shape manifest (`artifacts/qa/ch1_12shape_preview_v4_20260705/manifest.json`). The only explicitly referenced practice-library exercise on main. The "med_007 class" is currently a class of one.
- **Tier 2 — flagship-adjacent type:** the remaining 33 `meditations` (the type the flagship demonstrably draws from).
- **Tier 3 — uniform remainder:** the other 7 types; within-type order is alphabetical (no honest signal differentiates them).
- **Expected appearances (uniform model):** 12 exercise slots/book ÷ (8 types × 34 items) ≈ **44.1 appearances per item per 1,000 catalog books** (~163 per item across ~3,700 anxiety titles). This is a model number, not a measurement — labeled as such in the TSV column name.

`med_NNN` (inbox `meditations_library_34*.json`, 34 ids) maps 1:1 to store `lib34_meditations_NN`.

## Reproduction

Corpus enumerated from `git ls-tree -r origin/main` at `a369f049728f308ed507639d58b27c973d8ea7ee`: 29 `selected_content_variants.json`, 80 `enrichment_audit.json`, 2 twelve-shape files, 47 exercise/planning configs — read via `git cat-file blob` (no working-tree contact). Id sweep regex: `(lib34|med|ab_tady)_[a-zA-Z0-9_]+`. The 39 `ab_tady_37` inbox items are not in the production store and are excluded (store-only scope).

## Layer label

This artifact is **analysis over EXECUTED-REAL inputs** (store + manifests + compiled artifacts); the frequency column is a **model projection**, not a measurement. Re-rank from real data once catalog builds record practice ids in `selected_content_variants.json` (the journeys/practice wiring item in the rendition spec's build order).
