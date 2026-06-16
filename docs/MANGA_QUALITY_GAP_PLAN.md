# MANGA_QUALITY_GAP_PLAN.md
# Phoenix Omega — Manga Quality Forensic Analysis & Sprint Plan

> **HISTORICAL — 2026-04-17 forensic, pre-ep_001-ship.** Describes since-resolved stubs (stub writer, 64×64 placeholders, filmstrip compositor). Read for history, not current state. Current: `docs/MANGA_PIPELINE_AUDIT_2026-04-26.md` (post-ship snapshot) + the V5 render stack (`docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md`, `docs/MANGA_V5_CATALOG_ROLLOUT_PLAN.md`).

**Session:** manga-quality-forensic-analysis-20260417  
**Branch:** agent/manga-quality-analysis-20260417-144928  
**Date:** 2026-04-17  
**Governing specs:** specs/MANGA_PRODUCTION_PIPELINE_SPEC.md, specs/MANGA_SERIES_BIBLE_SPEC.md  
**Analyzed artifact:** artifacts/manga_book/junko_sleep_anxiety_complete.pdf (4 pages, anxiety series)

---

## 1. Executive Summary (30-second read)

The manga pipeline produced **1 page / 2 panels / 128×64 pixels** of content.  
The Series Bible spec calls for **19 pages / 80–140 panels / 5200×7200 px** per chapter.  
The gap is **1.4% of required panel count** and **0.005% of required pixel area**.

**Five root causes:**

1. **The chapter writer is a stub** — `phoenix_v4/manga/chapter/writer_stub.py` produces exactly 1 page / 2 panels regardless of input. No real writer is wired in.
2. **All panel images are 64×64 identical placeholders** — FLUX generation is not connected. All 80 fixture images share one SHA-256 hash.
3. **The page compositor is a horizontal filmstrip** — `page_compose.py` tiles panels left-to-right in a single row. It cannot produce manga-page layouts, variable panel sizes, splash panels, or portrait pages.
4. **Lettering is produced but never rendered** — `lettering_spec.json` exists as a data artifact; the compositor has no code path to composite text onto panels.
5. **No series identity** — the output slug `anxiety_gen_alpha_01` has no marketing title, no character sheets, no series bible as a generative input.

The image bank (840 images) is fine. The infrastructure runs. The book-production layer does not work.

---

## 2. Ranked Gap List

All gaps from all workstreams, ordered by quality-lift-per-hour-of-work.

| Rank | Gap | Evidence | Quality Impact | Remedy |
|------|-----|----------|----------------|--------|
| 1 | **Chapter writer is a stub** | `writer_stub.py` — always 1 page / 2 panels | No real story content; 1.4% of required panels | Wire real chapter writer (Sprint 0) |
| 2 | **FLUX not connected; 64×64 placeholders** | All 80 images identical SHA-256 `46413733d3...` | Zero visual content | Connect real FLUX backend (Sprint 0) |
| 3 | **Compositor is a filmstrip, not a page layout** | `page_compose.py` lines 57–80: `total_w = sum(im.width for im in row)` | Produces 2:1 landscape strips; manga requires portrait pages with irregular panel grids | Name Stage + compositor refactor (Sprint C) |
| 4 | **Lettering never renders on art** | `lettering_spec.json` produced; compositor has no compositing code path | All dialogue is silently dropped from the page | Lettering wiring (Sprint D — already in flight) |
| 5 | **No panel borders or gutters** | `page_compose.py` places panels flush with zero whitespace | Panels bleed into each other; no visual separation | Add gutter/border pass to compositor (Sprint 0 — 1 day) |
| 6 | **Pipeline and PDF builder are disconnected** | DAG writes to `artifacts/manga/anxiety_series/final_page_composite/`; webtoon builder reads from `artifacts/pipeline_examples/manga_book/` | Output is never a valid manga PDF from pipeline data | Wire output paths (Sprint 0) |
| 7 | **No named series identity** | Output is slug `anxiety_gen_alpha_01`; no title, logline, volume plan, cover | Not a publishable product | Series Identity Layer (Sprint A) |
| 8 | **No character design sheets** | `character_refs` field in `panel_prompts.json` is populated but empty | Character consistency is 0%; Hana looks different every panel | Character Consistency System (Sprint B) |
| 9 | **No setting design sheets** | Same problem for locations/environments | Setting continuity fails across pages | Character Consistency System (Sprint B) |
| 10 | **No "name" thumbnail stage** | `page_compose.py` gets uniform tile spec; no layout-design pass | All pages have identical panel weight; no pacing expression | Name Stage (Sprint C) |
| 11 | **Chapter count/page count wrong** | Series finale (ch_10) run instead of ch_01; chapters 2–9 are stub dirs | Wrong chapter delivered; multi-chapter logic not connected | Chapter orchestration fix (Sprint 0) |
| 12 | **Series memory duplication (12 identical facts)** | `series_memory_snapshot.json` has 12 identical `chapter_pipeline_completed` for `ch_01` | Idempotency failure; state is corrupt | Idempotency guard in memory writer (Sprint 0) |
| 13 | **All webtoon chapters use same 12 images** | Panel IDs not prefixed by chapter number | Every chapter looks identical | Chapter-scoped panel IDs (Sprint 0) |
| 14 | **Author identity never surfaces** | `series/manga_author_identity.json` exists; none of it appears in output | No EI disclosure, no author byline, not a Stillness Press product | Series Identity Layer (Sprint A) |
| 15 | **No visual quality gates** | No MQG gates exist; layout QC passes 64×64 placeholders | Regressions go undetected | Visual Quality Gates (Sprint E) |

---

## 3. Proposed Sprint Sequence

### Sprint 0 — Foundation Fixes (1–2 weeks, ~40 dev-hours)
**Blocker for everything.** These are mechanical bugs, not design gaps.

- [ ] Wire the real chapter writer (replace `writer_stub.py`; use existing `MANGA_CHAPTER_WRITER_SPEC.md`)
- [ ] Connect FLUX backend for real panel image generation (remove fixture image short-circuit)
- [ ] Fix chapter_number parameter: run from ch_01, not ch_10
- [ ] Fix panel ID scoping: prefix panel IDs with chapter ID
- [ ] Wire pipeline output path to PDF builder input path
- [ ] Add gutter and border pass to `page_compose.py` (1-day fix)
- [ ] Add idempotency guard to series memory writer
- [ ] Verify lettering_spec compositing is at minimum in a stub state (Sprint D cleans it up)

**Success gate:** Pipeline produces a 19-page PDF with real art and panel borders for anxiety_gen_alpha_01/ch_01.

**Cost estimate:** ~40 dev-hours. No new infrastructure — connects existing components.

---

### Sprint A — Named Series Identity Layer (1 week, ~20 dev-hours)
**Blocker for Sprint B.**  
New spec: `specs/manga_series_identity_layer.md`

- [ ] Implement `scripts/manga/series_identity_init.py` — Claude API call with brand DNA + series brief → validated YAML
- [ ] Schema: `config/source_of_truth/manga_series/<series_id>/series_identity.yaml`
- [ ] Series identity fields: marketing_title, logline, high_concept, tagline, back_cover_blurb, comparable_titles, volume_plan, character roster with visual_archetypes, setting_bible, recurring_motifs
- [ ] Inject series_identity into every chapter writer invocation
- [ ] Worked example: convert anxiety_gen_alpha_01 to a named series "Junko and the 3am Ceiling" or equivalent

**Success gate:** `anxiety_gen_alpha_01` chapter 1 header shows series title + author byline + EI disclosure.

**Cost estimate:** ~20 dev-hours. Low complexity — mostly scaffolding around existing chapter writer.

---

### Sprint B — Character + Setting Consistency System (2–3 weeks, ~60 dev-hours)
**Requires Sprint 0 + Sprint A.**  
New specs: `specs/manga_character_setting_consistency.md`, `specs/comfyui_workflow_character_reference.md`

- [ ] Implement `CHARACTER_SHEET_BUILD` pipeline stage (runs once per series)
- [ ] ComfyUI workflow: `character_sheet_generation.json` (12 images per character: front/side/back/expressions)
- [ ] ComfyUI workflow: `panel_generation_with_reference.json` (IP-Adapter conditioning from character sheets)
- [ ] Character sheet manifest: `config/source_of_truth/manga_character_sheets/<series_id>/<character_id>/`
- [ ] Setting sheet manifest: `config/source_of_truth/manga_setting_sheets/<series_id>/<location_id>/`
- [ ] Extend `panel_prompts.json` with `character_refs` and `setting_refs` fields
- [ ] `select_reference_image()` and `select_expression_ref()` logic for per-panel expression selection
- [ ] CLIP cosine similarity drift check (Gate D2, threshold 0.82)
- [ ] One-time cost: 88 images (~$0.74, ~22 min) per series

**Success gate:** Hana in panel 1 and Hana in panel 47 score CLIP cosine similarity ≥ 0.82.

**Cost estimate:** ~60 dev-hours + ComfyUI workflow authoring. Highest implementation complexity.

---

### Sprint C — Name (Thumbnail) Stage (2 weeks, ~40 dev-hours)
**Requires Sprint 0.**  
New specs: `specs/manga_name_thumbnail_stage.md`, `specs/manga_page_layout_spec_schema.json`

- [ ] Implement `CHAPTER_NAME` stage (between Chapter Writer and Image Gen)
- [ ] Emotional role mapping: `panel_type` + `camera` + `silence_guard` → `emotional_role` (7 roles)
- [ ] Size class algorithm: rule-based → 3 candidate layouts → LLM selects best per genre
- [ ] Output: `page_layout_spec.json` with per-panel size_class, pixel_rect, bubble_zones
- [ ] Refactor `page_compose.py` to accept `page_layout_spec` and produce irregular grid layouts
- [ ] Bubble zone pass: bubble_render.py reads pre-calculated zones (not heuristic)
- [ ] Wireframe PDF renderer (PIL + reportlab) for editorial review gate
- [ ] Iyashikei layout rules: max 5 panels/page, 1 breath panel per spread, dialogue in middle pages

**Success gate:** 24-page chapter 1 wireframe approved by operator before FLUX is called.

**Cost estimate:** ~40 dev-hours. Moderate complexity; compositor refactor is the hard part.

---

### Sprint D — Lettering / Bubble Integration (1 week, ~20 dev-hours)
**Already in flight (bubble_rendering_engine spec 8d0285cedc).**

- [ ] Complete lettering_spec → compositor wire-up (the spec exists; the code path does not)
- [ ] SFX/onomatopoeia rendering on panels
- [ ] Dialogue bubble placement using pre-calculated zones from Sprint C
- [ ] Typography system: font selection per series, per bubble type
- [ ] Series title and chapter number on chapter opening page

**Success gate:** Dialogue from `chapter_script_writer_handoff.json` appears in bubbles on the final page.

**Cost estimate:** ~20 dev-hours. Low complexity — existing spec, missing implementation.

---

### Sprint E — Visual Quality Gates (1 week, ~20 dev-hours)
**Requires Sprint C output (page_layout_spec.json).**  
New spec: `specs/manga_visual_quality_gates.md`

- [ ] MQG-01: Visual Rhythm gate (distinct size classes per page ≥ 2)
- [ ] MQG-02: Silence Density gate (40–70% silent panels for iyashikei)
- [ ] MQG-03: Establishing Shot Cadence gate (environment panel every 4–6 pages)
- [ ] MQG-04: Reading Flow gate (valid reading path from panel positions)
- [ ] MQG-05: Emotional Arc gate (iyashikei: open establishing, close breath/silence)
- [ ] MQG-06: Page-Turn Payoff gate (30%+ of right-hand pages are payoff pages)
- [ ] MQG-07: Character Presence Density gate (protagonist on 60%+ of pages)
- [ ] MQG-08: Dialogue Bubble Count gate (iyashikei: avg ≤ 3 bubbles/page)
- [ ] Gate runner with BLOCKED/APPROVED/APPROVED_WITH_WARNINGS verdict
- [ ] Integration with existing CI/QC pipeline

**Success gate:** Re-running the anxiety series chapter produces APPROVED verdict on all 8 gates.

**Cost estimate:** ~20 dev-hours. Moderate complexity in gate computation logic.

---

## 4. Cost / Time Summary

| Sprint | Work (dev-hours) | Calendar (1 dev) | Compute Cost | Dependencies |
|--------|-----------------|-----------------|--------------|--------------|
| 0 — Foundation Fixes | 40 | 1–2 weeks | $0 (connects existing) | None |
| A — Series Identity | 20 | 1 week | ~$0.01/series (Claude API) | Sprint 0 |
| B — Character Consistency | 60 | 2–3 weeks | ~$0.74/series (88 FLUX images) | Sprint 0 + A |
| C — Name Stage | 40 | 2 weeks | ~$0.005/chapter (LLM layout) | Sprint 0 |
| D — Lettering (in flight) | 20 | 1 week | $0 | Sprint C (for zones) |
| E — Visual Quality Gates | 20 | 1 week | $0 | Sprint C |
| **Total** | **200** | **8–10 weeks** | **~$0.75/series** | — |

---

## 5. "Hello World" Rebuild Plan

How to re-generate `anxiety_gen_alpha_01` as a proper named series after Sprint 0–D:

```bash
# Step 1: Initialize series identity (Sprint A)
python3 scripts/manga/series_identity_init.py \
  --series_id anxiety_gen_alpha_01 \
  --brand stillness_press \
  --genre iyashikei \
  --brief "A Gen-Z girl navigating sleep anxiety discovers the 3am ceiling has something to say" \
  --output config/source_of_truth/manga_series/anxiety_gen_alpha_01/series_identity.yaml

# Step 2: Build character + setting sheets (Sprint B)
python3 scripts/manga/character_sheet_build.py \
  --series_id anxiety_gen_alpha_01 \
  --characters junko,ceiling_voice \
  --locations bedroom,dreamspace

# Step 3: Write chapter 1 with series identity as context (Sprint 0 + A)
python3 scripts/manga/chapter_writer.py \
  --series_id anxiety_gen_alpha_01 \
  --chapter ch_01 \
  --series_identity config/source_of_truth/manga_series/anxiety_gen_alpha_01/series_identity.yaml

# Step 4: Generate name (thumbnail layout) (Sprint C)
python3 scripts/manga/chapter_name.py \
  --series_id anxiety_gen_alpha_01 \
  --chapter ch_01 \
  --genre iyashikei \
  --target_pages 24
# -> Review wireframe PDF, approve before proceeding

# Step 5: Generate panel images with character references (Sprint B + 0)
python3 scripts/manga/chapter_image_gen.py \
  --series_id anxiety_gen_alpha_01 \
  --chapter ch_01 \
  --character_sheets config/source_of_truth/manga_character_sheets/anxiety_gen_alpha_01/

# Step 6: Run visual quality gates (Sprint E)
python3 scripts/manga/mqg_gate_runner.py \
  --series_id anxiety_gen_alpha_01 \
  --chapter ch_01
# -> Must produce APPROVED before proceeding

# Step 7: Composite pages with lettering (Sprint C + D)
python3 phoenix_v4/manga/chapter/page_compose.py \
  --series_id anxiety_gen_alpha_01 \
  --chapter ch_01 \
  --layout_spec artifacts/manga/anxiety_gen_alpha_01/ch_01/stages/chapter_name/page_layout_spec.json

# Step 8: Compile to PDF
python3 scripts/manga/pdf_builder.py \
  --series_id anxiety_gen_alpha_01 \
  --chapter ch_01 \
  --output artifacts/manga/anxiety_gen_alpha_01/ch_01/chapter_01.pdf
```

**Expected output:** A 24-page portrait PDF with:
- Series title + author byline on chapter opener
- Real art (not 64×64 placeholders)
- Consistent Junko character across all panels
- Variable panel sizes (splash opener, medium story panels, small reaction panels)
- Dialogue bubbles with typeset text
- EI disclosure footer
- APPROVED on all 8 MQG gates

---

## 6. Success Metric Checklist

A future QA run should pass ALL of the following before being considered "a manga":

### Structural
- [ ] PDF is portrait orientation (height > width)
- [ ] Chapter has ≥ 16 pages (absolute minimum for iyashikei; target 24)
- [ ] Each page has ≥ 2 panels (no single-panel pages except chapter opener and splash)
- [ ] At least 2 distinct panel size classes per page
- [ ] At least 1 full-page or splash panel per chapter
- [ ] Page count matches `target_page_count` in `page_layout_spec.json` ± 2

### Visual
- [ ] All panels are ≥ 512×512 px (no placeholders)
- [ ] No two panels share the same image SHA-256 (no duplicates)
- [ ] CLIP cosine similarity for main character across panels ≥ 0.82 (consistency gate)
- [ ] At least 1 establishing shot (wide environment) every 6 pages
- [ ] Panel borders/gutters present (no bleed between panels)

### Content
- [ ] Series title appears on chapter opening page
- [ ] Author name (EI character) appears on chapter opening page
- [ ] EI disclosure footer appears on at least first and last page
- [ ] At least 40% of panels are silent (iyashikei gate)
- [ ] Average dialogue bubbles per page ≤ 3 (iyashikei gate)
- [ ] Dialogue from `chapter_script_writer_handoff.json` appears on page (lettering gate)

### Pipeline
- [ ] All 8 MQG gates produce APPROVED or APPROVED_WITH_WARNINGS
- [ ] No MQG gate produces BLOCKED
- [ ] `series_memory_snapshot.json` has no duplicate facts
- [ ] `panel_images_manifest.json` shows `status: ok` for all panels (no `status: fixture`)

### Identity
- [ ] `series_identity.yaml` exists and is `status: locked`
- [ ] `character_sheets_manifest.json` exists for all characters in the series
- [ ] Series has a marketing_title (not just a slug)

---

## 7. Deliverable Index

All research and design artifacts produced in this sprint:

| File | Type | Lines | Workstream |
|------|------|-------|------------|
| `artifacts/analysis/manga_forensic_teardown.md` | Forensic analysis | ~350 | WS1 |
| `artifacts/research/manga_quality_bar/01_iyashikei_craft_study.md` | Craft research | 501 | WS2 |
| `artifacts/research/manga_quality_bar/02_studio_workflow_gap_analysis.md` | Gap analysis | ~400 | WS3 |
| `specs/manga_series_identity_layer.md` | Architecture spec | 561 | WS4 |
| `config/source_of_truth/manga_series_examples/the_garden_at_tidecalm.yaml` | Worked example | 658 | WS4 |
| `specs/manga_character_setting_consistency.md` | Architecture spec | 716 | WS5 |
| `specs/comfyui_workflow_character_reference.md` | ComfyUI spec | 637 | WS5 |
| `specs/manga_name_thumbnail_stage.md` | Architecture spec | 843 | WS6 |
| `specs/manga_page_layout_spec_schema.json` | JSON Schema | 378 | WS6 |
| `specs/manga_visual_quality_gates.md` | Gate spec | 914 | WS7 |
| `docs/MANGA_QUALITY_GAP_PLAN.md` | This document | ~350 | Synthesis |
| `.github/workflows/manga-quality-analysis.yml` | GH Actions | ~100 | Infra |

---

## 8. CLOSEOUT_RECEIPT

```
session_id:   manga-quality-forensic-analysis-20260417
branch:       agent/manga-quality-analysis-20260417-144928
commit_sha:   [see git log after commit]
pr_url:       [see gh pr create output]

top_5_gaps_ranked:
  1. Chapter writer is a stub (writer_stub.py) — 1.4% of required panel count
  2. FLUX not connected (64×64 identical placeholders, all same SHA)
  3. page_compose.py is a horizontal filmstrip (not manga page layout)
  4. Lettering produced but never composited onto panels
  5. No series identity (slug only, no marketing title/author/EI disclosure)

sprint_sequence:
  Sprint 0 — Foundation Fixes:          40h, 1–2 weeks  (mechanical bugs; blocker)
  Sprint A — Series Identity Layer:     20h, 1 week
  Sprint B — Character Consistency:     60h, 2–3 weeks  (highest visual quality lift)
  Sprint C — Name/Thumbnail Stage:      40h, 2 weeks    (biggest structural lift)
  Sprint D — Lettering (in flight):     20h, 1 week
  Sprint E — Visual Quality Gates:      20h, 1 week
  Total:                               200h, 8–10 weeks, ~$0.75/series compute

hello_world_rebuild: see Section 5 above (8-step script sequence)

success_metric: 22-item checklist in Section 6 above

next_action: >
  Operator reviews this plan. Approves sprint sequence.
  Sprint 0 (foundation fixes) begins immediately — it is all mechanical
  bug fixes, not new design. No new specs needed.
  Sprint A can be parallelized with Sprint 0 final days.
  Sprints B/C/D/E follow in sequence.
```
