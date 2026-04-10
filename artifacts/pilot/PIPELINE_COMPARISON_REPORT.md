# Pipeline Comparison — Spine + Knob + Beatmap + Enrichment vs Registry Fast-Path

Date: 2026-04-10  
Project: `proj_state_convergence_20260328`  
Subsystem: `core_pipeline`

PR #373 (BeatmapCompile) was squash-merged to `main` before this pilot. PRs #371 and #372 were already merged.

## Per-topic results

| Topic   | New words | Old words | Delta   | Delta % | Teacher | Persona | Registry | Practice library | Gaps |
|---------|-----------|-----------|---------|---------|---------|---------|----------|------------------|------|
| anxiety | 2500      | 5033      | -2533   | -50%    | 27      | 12      | 12       | 0                | 0    |
| grief   | 2856      | 7235      | -4379   | -61%    | 25      | 12      | 12       | 0                | 0    |
| burnout | 2430      | 4817      | -2387   | -50%    | 24      | 12      | 12       | 0                | 0    |

Slot counts (new pipeline) are **51 total slots per book** (beatmap-selected subset per chapter), versus the registry fast-path which resolves **many more sections per chapter** (~10) for 12 chapters. The word-count gap is therefore **expected** for this pilot: the new path is not yet a full structural match to registry density.

Enrichment audit (`*_new/enrichment_audit.json`) shows `total_target_words` ≈ 10k (beatmap budget midpoint) while **actual** stitched prose is ~2.4k–2.9k because the pilot composer concatenates slot bodies only (no bridges, mechanism distillation, or exercise assembly).

## Content quality assessment (chapter 1 only)

### Anxiety

- **Opening / recognition:** Baseline registry hook (“You have optimized everything…”) is tightly vocational and immediate. New pipeline chapter 1 opens with a contemplative teacher-style HOOK (“The body knows truth…”) that is warm but less situation-specific than the baseline.
- **Specificity:** Baseline SCENE layers inbox, calendar, and desk beats without raw template braces. New pipeline SCENE still contains **unhydrated placeholders** such as `{weather_detail}` and `{street_name}` — **baseline is stronger for ship-ready prose**.
- **Exercises:** Baseline chapter 1 includes a full exercise + integration stack from the registry / library path. New pilot output stacks fewer slots and does not run `compose_chapter_prose` / `component_assembler`; exercise **structure** is weaker in the pilot.
- **Flow:** Baseline reads as one continuous chapter; pilot reads as labeled chapters with **sequential slot paste** (no bridges).

### Grief

- **Opening:** Baseline leads with workplace loss and social texture (“all-hands,” Slack). New pipeline leads with a universal doctrinal HOOK (“Every person carries the capacity…”) then SCENE — **baseline opens stronger for recognition in-context**.
- **Specificity:** New text still shows `{transit_line}` where baseline has replaced transit with concrete wording (“the bus”). **Baseline wins on locale hydration.**

### Burnout

(Same structural pattern as anxiety/grief: shorter pilot manuscripts, placeholder risk in persona/registry blends; baseline remains the richer reader experience until `clean_for_delivery` and full `ChapterCompose` are wired.)

## Enrichment analysis

- **Teacher vs registry (new path):** For anxiety, **27 / 51 ≈ 53%** of slots used teacher atoms, **12 / 51 ≈ 24%** persona, **12 / 51 ≈ 24%** registry — teacher + persona dominate as intended.
- **Teacher vs registry length:** Teacher/persona paragraphs are not automatically longer than registry variants in this sample; the **global word count** is dominated by **how many slots** exist in the beatmap, not by per-slot verbosity alone.
- **Persona demographic specificity:** Persona pools add scene/story texture when used; HOOK is often teacher-heavy when `teacher_id=ahjan`, so persona shines most on **SCENE/STORY** slots.
- **Practice library fallback:** **0** uses across all three topics in this pilot (`slots_from_practice_library: 0`). Early chapters omit EXERCISE in the beatmap for anxiety/grief per spine rules, so library never fired.
- **Empty slots:** **0** — gaps would appear as `[CONTENT GAP: …]`; none observed.

## Architecture assessment

- **Meaningful differentiation by topic:** Yes — spine + knobs + beatmap change chapter titles, thesis lines, and which slots exist per chapter; enrichment pulls topic-specific registry YAMLs.
- **Knob / spine visibility:** Yes at the **plan** level (weights, forbidden exercises in early chapters). Reader-facing difference is damped in the pilot because prose composition is intentionally minimal.
- **Beatmap word allocation:** Per-slot `target_words` are present in `budget.json`; actual words are lower when content is short or placeholders remain.
- **Waterfall order:** Implemented to mirror `registry_resolver.resolve_book`: teacher overlay types → persona (HOOK/SCENE/STORY) → practice library for EXERCISE before registry → registry variant — with visible gaps if nothing resolves.

## Recommendations

| Area | Verdict |
|------|---------|
| **Keep** | EnrichmentSelect waterfall; deterministic selection; visible gap markers; standalone pilot runner; `compose_from_enriched_book` additive API. |
| **Fix before wider rollout** | Run **`clean_for_delivery`** (or full book render hygiene) on pilot output so `{weather_detail}` / `{street_name}` never ship; wire **full `compose_chapter_prose`** (bridges, exercise assembly) for parity with registry reader experience. |
| **Highest-impact next step** | Either **expand beatmap** toward full registry section counts **or** define a “registry parity” format so word counts and chapter depth are comparable; then integrate EnrichmentSelect into the main renderer path behind a flag. |
| **Replace registry fast-path?** | **Not yet.** Conditions: (1) hydrated delivery prose, (2) chapter flow comparable to registry + composer path, (3) exercise handling at least as strong as `chapter_composer` + `practice_library_loader`, (4) word budget validated against `format_registry` targets with real `config/spines` on main (fixtures were used where `config/spines` is absent in this clone). |

## Evidence paths

- New pipeline outputs: `artifacts/pilot/{anxiety,grief,burnout}_new/`
- Baseline outputs: `artifacts/pilot/{anxiety,grief,burnout}_baseline/`
- Implementation: `phoenix_v4/planning/enrichment_select.py`, `phoenix_v4/rendering/chapter_composer.py` (`compose_from_enriched_book`), `scripts/pilot/run_spine_pipeline.py`
- Tests: `tests/test_enrichment_select.py` (18 passing)
