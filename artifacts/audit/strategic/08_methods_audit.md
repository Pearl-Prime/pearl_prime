# Workstream 8: Methods Audit — Manga Pipeline
**Date:** 2026-04-18
**Auditor:** Pearl_Architect
**Scope:** Craft and methodology gaps in manga production pipeline. Tools audit was WS7; this audit covers where the craft process is missing.
**Source canary scores:** Pearl_Editor 3.7/10, human reader 4.5/10, teacher_showcase.html typography "very bad" + repetitive, stillness_press_qa_run/manga.pdf = 3 stand-in art pages, no bubbles, no series identity.

---

## Executive Summary

The manga pipeline has a sound skeletal architecture (series setup → chapter production → ITE stages → QC) but is missing five craft layers that professional manga production requires. The pipeline generates panels once and ships — there is no compositional planning stage before render, no editorial revision loop after render, and no wiring from the existing research corpus into prompts. Character consistency is partially implemented in standalone image scripts but is not wired into the chapter production flow. The EMA learner exists but is scoped to ebook prose, not manga panel quality.

| Gap Area | Quality Impact | Effort to Fix |
|----------|---------------|---------------|
| A. Character consistency not wired into chapter production | HIGH | HIGH (3-4 weeks) |
| B. No thumbnail/name stage before panel render | HIGH | MEDIUM (1-2 weeks) |
| C. No editorial revision loop after render | HIGH | MEDIUM (1-2 weeks) |
| D. Research-to-prompt gap | MEDIUM | LOW (< 1 week) |
| E. EMA/telemetry not wired to manga | LOW (now) / HIGH (scale) | MEDIUM (1-2 weeks) |

---

## Gap A: Character Consistency

### What the spec implies
`config/manga/teacher_character_prompts.yaml` exists and is read by the pipeline. The implementation outline requires "style-locked" downstream renders and "visual/style drift checks" in QC.

### What is actually implemented (confirmed by grep)

**In standalone image scripts (scripts/image_generation/):**
- `manga_teacher_batch.py`: IP-Adapter support is fully implemented. Takes teacher reference photos from `assets/manga/teacher_reference_photos/{id}.jpg`, sends them to `flux_ip_adapter_manga.json` ComfyUI workflow via RunComfy. Seed locking: seeds default to `[42, 123, 456]` with `--seeds` override for variation runs.
- `generate_teacher_showcase_triptych.py`: Uses deterministic seed per teacher+kind pair via SHA-256 hash (`_seed_for(tid, kind)`). No IP-Adapter — txt2img only with character blocks from `TRIPTYCH_BRIEF` dict (hardcoded per teacher, not loaded from `teacher_character_prompts.yaml`).

**In the chapter production pipeline (scripts/manga/ + phoenix_v4/manga/):**
- `visual_prompt_compiler.py` uses `DEFAULT_CHARACTER_BLOCKS` dict — a 5-entry hardcoded dict covering only ahjan, maat, sai_ma, ra, master_wu. The remaining 8 teachers fall back to `"mysterious figure, thoughtful expression"`.
- There is NO call to IP-Adapter in the chapter production flow. `image_backend.py` supports `noop`, `replay`, and RunComfy backends, but the RunComfy path submits to FLUX txt2img — not the IP-Adapter workflow.
- There is NO seed locking mechanism in `run_chapter_production.py`. Each panel is generated independently with random seeds unless manually overridden.
- Character continuity across panels within a chapter: tracked only via `continuity_tags` metadata field (`teacher:ahjan`, `style:dark_psychological`, etc.) — these are output labels, not render inputs.

### Gap diagnosis
The standalone scripts (triptych generator, manga_teacher_batch) have partial character reference systems. The canonical chapter production pipeline has **neither IP-Adapter nor seed locking**. A reader will see a teacher character change appearance panel-to-panel within the same chapter. This directly explains the "stand-in art, no series identity" observation in the canary run.

Only 5 of 13 teachers have character blocks in `DEFAULT_CHARACTER_BLOCKS`. The other 8 produce generic "mysterious figure" characters in production.

**Quality impact: HIGH** — visible drift within every chapter, invisible brand identity.

**Fix recommendation:**
1. Load teacher character description from `teacher_character_prompts.yaml` in `visual_prompt_compiler.py` (replaces the hardcoded 5-entry dict). Effort: S (< 2 days).
2. Add seed locking to `run_chapter_production.py`: derive a deterministic per-teacher seed from `teacher_id + chapter_id` hash, apply to all panels in that chapter. Effort: S (1 day).
3. Wire IP-Adapter into the RunComfy backend path in `image_backend.py`, using the `WORKFLOW_IP_ADAPTER` from `manga_teacher_batch.py`. Require a reference photo to exist in `assets/manga/teacher_reference_photos/`. Effort: M (1 week).
4. ITE QC gate: add a visual drift check that flags if character skin tone / art style deviates significantly across panels (currently T-01–T-20 gates check therapeutic structure, not visual consistency). Effort: H (requires embedding similarity or VQA call).

---

## Gap B: Thumbnail / Name Stage

### What professional manga production requires
Thumbnail layouts (name in Japanese manga tradition) are rough compositional sketches drawn BEFORE final art. Purpose: confirm page rhythm, panel pacing, reading flow, and emotional arc before committing to expensive rendering. Missing this step means panels are generated directly from prompts without any compositional review, producing flat or repetitive layouts.

### What is actually implemented

`config/manga/panel_layouts.yaml` exists and is loaded by `visual_prompt_compiler.py`. It provides per-atom-type layout templates (camera angle, composition notes, panel count). This is a static lookup — not a dynamic compositional planning step.

The pipeline flow is:
```
chapter_script.json → run_chapter_production.py → visual_prompt_compiler.py → panel_prompts.json → image backend → panels
```

There is no step between `panel_prompts.json` and image render where a human or agent reviews the compositional plan. `panel_layouts.yaml` selects a layout template, but there is no mechanism to see how panels will read in sequence, check pacing, or adjust before rendering.

The video pipeline has a `run_shot_planner.py` stage that produces a ShotPlan artifact before render — the manga pipeline has no equivalent.

**Quality impact: HIGH** — explains repetitive composition and "very bad" typography observed in teacher_showcase.html. Without a name stage, the pipeline picks layout templates mechanically. All STORY panels with `mechanism_depth=moderate` get 5 panels with the same camera spec, producing compositional monotony across chapters.

**Fix recommendation:**
1. Add a `run_panel_compositor.py` stage (between `run_chapter_production.py` and image render) that:
   - Loads `panel_prompts.json`
   - Renders a low-fidelity layout sketch (bounding boxes + camera labels) as a single PNG or HTML artifact
   - Writes `panel_composition_plan.json` with panel sequence, pacing notes, variety check
   - Can be reviewed or auto-approved based on variety score
   Effort: MEDIUM (1-2 weeks). The video `run_shot_planner.py` is a template for this pattern.
2. Extend `panel_layouts.yaml` to include multiple layout variants per atom type (A/B/C), and rotate variants across a chapter to prevent monotony. Effort: LOW (2-3 days).

---

## Gap C: Editorial Feedback Loop

### What professional manga production requires
After panels are rendered, an editorial review step identifies panels that are compositionally weak, off-character, or fail the therapeutic transmission test. These panels are flagged for re-generation with adjusted prompts before the chapter is finalized.

### What is actually implemented

The ITE QC stage (`ite_qc.py`) runs T-01–T-20 gates after rendering. These gates check therapeutic structure (breath sequence integrity, gutter therapy compliance, color arc, fractal regulation). They do NOT:
- Flag individual panels for re-generation
- Allow prompt adjustments and re-render
- Support human editorial override

The pipeline runs chapter production → ITE stages → QC → output. There is no loop-back. If ITE QC fails, the operator must re-run the entire pipeline manually.

`phoenix_v4/qa/bestseller_editor.py` exists for ebook prose (book-pass gate, chapter flow review) but has no manga equivalent and no panel-level scoring.

**Quality impact: HIGH** — explains 3.7/10 Pearl_Editor score. The pipeline ships whatever the model generates on the first pass. No revision cycle means bad panels accumulate.

**Fix recommendation:**
1. Add a `run_panel_review.py` stage after render, before ITE QC:
   - Accepts `panel_prompts.json` + rendered panel paths
   - Scores each panel on: (a) character consistency with previous panels, (b) compositional variety vs. adjacent panels, (c) therapeutic transmission (does the panel convey the intended emotional beat)
   - Outputs `panel_review.json` with per-panel pass/flag/reject decision
   - Flagged panels get adjusted prompts written to `panel_reprompt.json`
   - A re-render loop runs for flagged panels only (max 2 attempts)
   Effort: MEDIUM (2 weeks). This is the highest-value single change.
2. Add `--editorial-gate` flag to `run_chapter_production.py` that requires a human sign-off on `panel_review.json` before proceeding to ITE stages. Effort: LOW (1 day, once panel_review.py exists).

---

## Gap D: Research-to-Production Gap

### What the research corpus contains

`artifacts/research/` contains:
- `manga_genre_writing_styles_2026_04_04.md` — genre-specific writing and visual styles
- `therapeutic_manga_wellness_market_research_2026_04_04.md` — therapeutic manga market analysis
- `manga_publishing_revenue_strategy.md` — publishing strategy
- `bestseller_titles_seo_covers_research.md` — bestseller pattern analysis
- `global_manga_distribution_strategy.md` — distribution research

### What actually reaches prompts (confirmed by grep)

Zero. There is no `import`, `load`, or file read of any research artifact in any script under `scripts/image_generation/` or `phoenix_v4/manga/`. Prompts in `visual_prompt_compiler.py` are generated from:
- `DEFAULT_CHARACTER_BLOCKS` (5-entry hardcoded dict)
- `DEFAULT_ENGINE_SCENES` (7-entry hardcoded dict)
- Style archetypes from `config/manga/` YAML
- Panel layouts from `config/manga/panel_layouts.yaml`

The genre writing style research (`manga_genre_writing_styles_2026_04_04.md`) identifies genre-specific panel conventions, pacing patterns, and visual motifs that should inform prompt construction. None of this reaches the prompt compiler.

The bestseller_editor (`phoenix_v4/qa/bestseller_editor.py`) applies to ebook prose; there is no manga-specific quality rubric derived from bestseller pattern research.

**Quality impact: MEDIUM** — prompts are competent but generic. The research describes what makes therapeutic manga effective; the pipeline does not use it.

**Fix recommendation:**
1. Extract genre-specific prompt tokens from `manga_genre_writing_styles_2026_04_04.md` into a new `config/manga/genre_visual_tokens.yaml`. The prompt compiler reads this file and adds genre-specific camera angles, color palette notes, and pacing cues to each panel prompt. Effort: LOW (3-5 days).
2. Create a `config/manga/bestseller_visual_patterns.yaml` distilling high-performing visual patterns from bestseller research (e.g., "high contrast opening panel", "intimate close-up for emotional beats"). Wire into `panel_layouts.yaml` selection logic. Effort: LOW (3-5 days).

---

## Gap E: Telemetry and Learning Loop

### What exists

The EMA learner (`scripts/ci/run_ema_learner.py`) is implemented and wired to `phoenix_v4/quality/ei_v2/learner.py`. It reads editorial feedback from `artifacts/ei_v2/learner_feedback.jsonl` and updates learned weights in `artifacts/ei_v2/learned_params.json`.

The ML editorial system (`scripts/ml_editorial/`) scores text sections and generates rewrite recommendations. `run_section_scoring.py` operates on text chapter segments.

The ML loop (`scripts/ml_loop/`) runs continuous scoring and weekly market recalibration.

### Manga wiring (confirmed by grep)

None. The EMA learner, ML editorial scoring, and continuous ML loop operate entirely on ebook prose (text sections, chapter_id references to text content). There is:
- No manga panel quality score feeding into `learner_feedback.jsonl`
- No reader engagement signal from manga platforms (WEBTOON Canvas analytics, KDP manga read-through) feeding into any loop
- No manga-specific quality dimension in `ei_v2_config.yaml`

The pipeline generates panels, ships them, and receives no feedback. No signal exists to improve the next chapter.

**Quality impact: LOW now / HIGH at scale** — matters when volume increases and pattern detection becomes possible.

**Fix recommendation:**
1. Add a manga feedback schema to `ei_v2_config.yaml`: panel_quality, character_consistency_score, transmission_score. Wire `ite_qc.py` to emit per-chapter scores to `artifacts/ei_v2/learner_feedback.jsonl` with `content_type: manga`. Effort: MEDIUM (1-2 weeks).
2. When manga titles are live on WEBTOON Canvas, wire episode view counts and Super Like rates into `run_weekly_market_recalibration.py` as reader signal. Effort: HIGH (requires platform API integration, post-launch).

---

## Priority Fix Order

| Priority | Gap | Action | Effort | Owner |
|----------|-----|--------|--------|-------|
| P0 | A: Character consistency | Load teacher_character_prompts.yaml in visual_prompt_compiler.py; cover all 13 teachers | S (2 days) | Pearl_Dev |
| P0 | A: Seed locking | Deterministic seed per teacher+chapter in run_chapter_production.py | S (1 day) | Pearl_Dev |
| P1 | C: Editorial loop | Add run_panel_review.py with panel-level flag/reject + re-render loop | M (2 weeks) | Pearl_Dev |
| P1 | B: Thumbnail stage | Add run_panel_compositor.py for pre-render compositional review | M (1-2 weeks) | Pearl_Dev |
| P1 | D: Research-to-prompt | Distill genre_visual_tokens.yaml + bestseller_visual_patterns.yaml from research | L (< 1 week) | Pearl_Architect |
| P1 | A: IP-Adapter wiring | Wire flux_ip_adapter_manga.json into image_backend.py chapter production path | M (1 week) | Pearl_Dev |
| P2 | B: Layout variety | Extend panel_layouts.yaml with A/B/C variants; rotate across chapter | L | Pearl_Dev |
| P2 | E: Manga telemetry | Add manga feedback schema to EMA learner | M | Pearl_Dev |

---

## Root Cause Assessment

The pipeline was architected correctly but implemented to a research/proof-of-concept standard, not a production standard. The gap between the spec (which describes a full professional manga workflow) and the implementation (which gets to first-render output and stops) is the core problem. Three decisions would change output quality immediately:

1. **Character block coverage**: Expanding `DEFAULT_CHARACTER_BLOCKS` from 5 to 13 teachers takes hours. It directly eliminates "mysterious figure" art.
2. **Seed locking**: One line of code per chapter. Eliminates within-chapter character drift.
3. **Panel review loop**: Highest effort but highest impact. No professional manga ship is single-pass.

The research corpus represents hundreds of hours of competitive intelligence that currently has zero influence on production outputs. This is recoverable with config file extraction — it does not require re-architecting anything.
