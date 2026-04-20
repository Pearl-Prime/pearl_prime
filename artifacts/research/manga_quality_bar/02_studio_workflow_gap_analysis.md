# Studio Workflow Gap Analysis
## Phoenix Omega vs. Professional Manga Production Pipeline

**Document:** `artifacts/research/manga_quality_bar/02_studio_workflow_gap_analysis.md`
**Date:** 2026-04-17
**Author:** Pearl_Research
**Status:** First draft — for editorial review

---

## Section 1: Professional Manga Studio Pipeline

This section documents how a professional manga studio — the kind producing serialized commercial work (Weekly Shonen Jump scale) or therapeutic-niche graphic novels — actually operates. Each stage is described with its outputs, typical time cost, and the quality problem it solves.

### Stage 1: Ideation / Series Pitch

**What it produces:**
- A named series with title, logline, and high concept (2–3 sentences)
- A defined protagonist wound and 3-act arc (often called a "synopsis")
- Publisher pitch document: target demographic, comparable titles, projected volume count
- Initial tone reference sheet (mood boards, visual comps from other works)

**Time cost (professional):**
- Weeks to months; editorial revision cycles before green-light
- For an independent creator: several days to a few weeks of drafting

**What it solves:**
- Forces early commitment to the *series as a product identity* — title, brand, logline
- Editorial gate that rejects vague concepts before any art is drawn
- Establishes the series as a named, bounded, saleable object

---

### Stage 2: Character Design Sheets (Turnaround Sheets)

**What it produces:**
- Front/side/back-view turnarounds for every named character
- Expression sheets (6–12 emotions per character)
- Wardrobe variation sheets (school uniform vs. home clothes vs. special outfit)
- Prop sheets for recurring objects (protagonist's signature item, villain's weapon)
- These sheets are drawn **once** and distributed to all collaborators as the reference source of truth

**Time cost (professional):**
- 1–3 days per major character (in a professional studio)
- A full cast of 4–5 characters: approximately 1–2 weeks

**What it solves:**
- Cross-panel character consistency: panel 1 and panel 200 show the same character
- Visual identity: readers recognize characters instantly
- Collaboration: multiple artists on the same series draw to the same reference

---

### Stage 3: Setting / Background Design Sheets

**What it produces:**
- Architectural cutaway drawings of recurring locations (protagonist's bedroom, school, workplace)
- Environmental style guide: urban realism vs. stylized, lighting conventions
- Prop inventory for recurring objects
- Color palette card (even in black-and-white series: screentone density map)

**Time cost (professional):**
- 2–5 days for a series with 3–5 key locations

**What it solves:**
- Consistent backgrounds across chapters
- Spatial logic: readers develop a mental map of the story world
- Art direction efficiency: background artists work from sheets rather than inventing per panel

---

### Stage 4: The Name (ネーム — Thumbnail Script)

**What it produces:**
- Rough thumbnail pages at small scale (typically A4, panels sketched at 3–4 cm each)
- Every page of the chapter blocked in — approximate panel count, shape, and size
- Dialogue placement marked (bubble positions rough-sketched, actual text written in)
- Panel flow arrows for reading direction
- Key poses and expressions rough-drawn (stick-figure quality acceptable)

**Time cost (professional):**
- A professional mangaka: 1–3 days per 24-page chapter
- This is frequently the longest single stage

**What it solves:**
- **This is the most important stage in professional manga production**
- It answers: "Does this chapter work as visual storytelling?" before any final art is drawn
- Editors review the name and return it with notes ("pages 8–12 are too slow," "the reveal on page 17 has no setup")
- It locks in bubble placement zones *before* the art is drawn — preventing the common failure of beautifully drawn panels that have nowhere for dialogue to go
- It determines variable panel sizes: a close-up on a crucial expression gets a large panel; a transitional moment gets a small one
- It identifies splash pages and double spreads before the artist commits labor to them
- It catches pacing problems, structural dead-ends, and weak chapter hooks before the expensive art stage

**Key principle:** In professional manga, all decisions about *what happens on each page* and *how much visual space each moment gets* are made at the name stage, not during inking.

---

### Stage 5: Rough Pencils / Storyboard

**What it produces:**
- Full-size (B4 paper, typically ~364×257mm) pencil drawings
- All panels drawn, not just thumbnailed
- Final panel border placement confirmed
- Character poses and backgrounds at readable resolution
- Dialogue bubbles drawn in (blank or containing rough text)

**Time cost (professional):**
- 2–5 days per chapter (24 pages), depending on complexity

**What it solves:**
- Final check on composition before inking (which is much harder to undo)
- Catches anatomical problems and visual confusions before they're committed in ink

---

### Stage 6: Inks + Screentones (Final Art)

**What it produces:**
- Clean inked pages (line art)
- Screentone or digital tone application (grey values in B&W manga)
- Cleaned-up speech bubble shapes (empty, awaiting text)
- In digital production: layered files with separate ink and tone layers

**Time cost (professional):**
- 3–7 days per chapter for a professional with assistant support
- Up to 2 weeks solo

**What it solves:**
- The publication-ready visual layer
- All artistic decisions locked in; only text to be added

---

### Stage 7: Lettering

**What it produces:**
- Typeset dialogue placed in speech bubbles
- Hand-lettered or typeset SFX placed in panels
- Translated text for localized editions
- Final bubble tail directions confirmed against art

**Time cost (professional):**
- 1–2 days per chapter

**What it solves:**
- Text rendered legibly on art that was designed to receive it (blank bubble zones reserved)
- Localization without art changes (text swapped in bubbles)

---

### Stage 8: Editorial Review

**What it produces:**
- Editor notes (written comments on printed pages or digital annotations)
- Revision list (priority-ordered)
- Chapter clearance decision: "publish," "revise," or "redraw"

**Time cost (professional):**
- 1–3 rounds of revision per chapter; each round 2–5 days

**What it solves:**
- Catches pages that don't land emotionally: "page 14 is confusing — readers won't understand why she's crying"
- Catches narrative problems the creator is too close to see
- Maintains series coherence chapter-to-chapter

---

### Stage 9: Tankōbon Assembly

**What it produces:**
- Volume-collected edition (typically 8–10 chapters per volume)
- Volume-specific cover art (different from chapter covers)
- Bonus content: character profiles, author notes, special pages
- Print-ready files at final dimensions (standard: 182×257mm, B6 size)

**Time cost (professional):**
- Several days of assembly, plus cover art (1–2 weeks)

**What it solves:**
- Series identity as a physical product
- Reader experience of a complete arc in one reading session
- Secondary market (bookstore display vs. digital chapter)

---

### Professional Time Summary: 24-Page Chapter

| Stage | Time (professional) |
|-------|-------------------|
| Series pitch / setup | 2–4 weeks (one-time) |
| Character design sheets | 1–2 weeks (one-time) |
| Setting design sheets | 3–5 days (one-time) |
| Name (thumbnail) | 1–3 days |
| Rough pencils | 2–5 days |
| Inks + screentones | 3–7 days |
| Lettering | 1–2 days |
| Editorial review | 2–5 days |
| **Total per chapter** | **~2–4 weeks** |

---

## Section 2: Phoenix Omega Current Pipeline

This section documents what Phoenix Omega actually does, based on:
- Specs in `specs/MANGA_PRODUCTION_PIPELINE_SPEC.md`, `specs/MANGA_CHAPTER_WRITER_SPEC.md`, `specs/MANGA_LAYOUT_AGENT_SPEC.md`, `specs/MANGA_SERIES_BIBLE_SPEC.md`, `specs/MANGA_TEXT_RENDERING_SPEC.md`, `specs/MANGA_STORY_ARCHITECT_SPEC.md`, `specs/AI_MANGA_PIPELINE_SUMMARY.md`
- Actual run artifacts in `artifacts/manga/anxiety_series/`

### What actually ran in the anxiety_series chapter

The stages that executed (all `status: passed`) were:

```
transmission_split → chapter_writer → chapter_visual → chapter_image_gen
→ chapter_lettering → chapter_layout → chapter_qc → series_memory_merge
→ ite_breath → ite_color_arc → ite_fractal → ite_gutter → ite_qc
```

**Critically, there was no series setup stage.** The series files in `artifacts/manga/anxiety_series/series/` are stubs:

- `style_bible.json`: Contains only `{"lexicons": {"palette": ["#0d0d0d", "#f5f5f5"]}}` — no character specs, no visual tokens, no lexicon tables
- `genre_blueprint.json`: Contains only `{"genre_id": "dark_psychological", "arc_structure": {"acts": 3}}` — 8 lines total
- `asset_registry.json`: Contains only `{"assets": [{"asset_id": "series_placeholder"}]}` — a single placeholder
- `story_architecture_handoff.json`: Chapter plot beats are stub-level — "Establish: Integration", "Deepen: The Bright after contraction"

**Actual image output:** All panel images are 64×64 pixel fixture images (identical SHA256: `46413733d3...`). The final page composite is 128×64 pixels — two 64-pixel tiles placed side by side in a horizontal strip by `page_compose.py`.

**What the actual pipeline does vs. what the specs describe:**

The specs describe a sophisticated multi-agent pipeline with rich outputs. The actual run produces:
- 2 placeholder panels per chapter
- No dialogue on any panel (both `lettering_spec.json` entries are `silence_confirmed: true`)
- A 128×64 page composite (effectively two postage-stamp images side by side)
- A `revision_queue.json` with `"chapter_clearance": "pass"` and zero issues

This reveals that **the pipeline infrastructure exists (all stage executors run) but the content generation is not connected to real image generation or real script writing**. The stages run on stub data.

### Agents that exist as specs but are not fully implemented in running code

Based on the specs and the actual artifacts:

| Agent | Spec exists? | Actually runs? | What it produces in practice |
|-------|-------------|----------------|------------------------------|
| Visual Identity Agent | Yes (VISUAL_IDENTITY_AGENT_SPEC.md) | Not confirmed | Stub style_bible.json |
| Genre Agent | Yes (MANGA_GENRE_AGENT_SPEC.md) | Not confirmed | Stub genre_blueprint.json |
| Story Architect | Yes (MANGA_STORY_ARCHITECT_SPEC.md) | Stage passes | 2-beat stub handoff |
| Chapter Writer | Yes (MANGA_CHAPTER_WRITER_SPEC.md) | Stage passes | 2-panel stub script |
| Visual Agent | Yes (in pipeline summary) | Stage passes | Identical prompts per panel |
| Image Gen (FLUX) | Referenced in specs | Runs (fixture mode) | 64×64 placeholder PNGs |
| Lettering Agent | Yes (MANGA_TEXT_RENDERING_SPEC.md) | Stage passes | silence_confirmed on all panels |
| Layout Agent | Yes (MANGA_LAYOUT_AGENT_SPEC.md) | Stage passes | Horizontal strip via page_compose.py |
| QC Agent | Yes (referenced in specs) | Stage passes | Zero issues (on stub data) |

### page_compose.py — the actual layout implementation

The file at `phoenix_v4/manga/chapter/page_compose.py` (84 lines) implements layout as:

```python
# line 57-80: for each page, load all panel images, resize to same height, 
# tile them left-to-right in a single horizontal strip
total_w = sum(im.width for im in row)
canvas = Image.new("RGBA", (total_w, target_h), (255, 255, 255, 255))
x = 0
for im in row:
    canvas.paste(im, (x, 0), im)
    x += im.width
```

This is a pure horizontal strip compositor. It:
- Takes all panels on a page and places them in a row, left to right
- Scales all panels to the same height (the tallest panel's height)
- Has no gutter between panels (panels abut directly)
- Has no margin, bleed, or safe zone
- Applies no panel borders
- Has no concept of variable panel size
- Has no splash page, double spread, or irregular grid support
- Does not composite lettering onto panels (lettering_spec is produced but not used)

---

## Section 3: Stage-by-Stage Gap Table

| Professional Stage | Phoenix Status | Quality Impact of Gap | Remedy |
|-------------------|---------------|----------------------|--------|
| **Series pitch / named identity** | No | Output has no title, no logline, no series identity. Slug is `anxiety_gen_alpha_01` — not a publication name. No reader brand recognition. | Add a SeriesIdentity config block with `title`, `logline`, `volume_plan`. Required before batch production. |
| **Character design sheets** | No | Every FLUX call regenerates the protagonist independently. No LoRA or IP-Adapter reference. Across 2 panels: same generic "young woman, dark hair" description, possibly different outputs. Across 14 chapters: character is unrecognizable as the same person. | Train per-series LoRA on approved character art, or use IP-Adapter with reference images. Panel prompt must inject `character_refs` (the spec calls for this at `panel_prompts.json → character_refs` field, but it is empty in practice). |
| **Setting design sheets** | No | Backgrounds are prompt-generated independently per panel. The spec references an `asset_registry.json` that contains only `"series_placeholder"`. Locations repeat in name only; visual appearance drifts per generation. | Populate `asset_registry.json` with real anchor images per location. Reference by `asset_id` in panel prompts (spec mandates this; not implemented). |
| **The Name (ネーム — thumbnail layout)** | No | This is the largest gap. Phoenix jumps from story_architecture_handoff (2 stub beats) directly to panel_prompts. There is no stage that decides: how many panels per page, what size each panel is, what shape the page takes, where bubbles will go, which moments get large panels. The result is a uniform horizontal strip of identically sized panels. | Add a NameStage agent between Chapter Writer and Visual Agent. Inputs: chapter_script pages. Outputs: per-page panel count and size specifications, bubble zone reservations, page type decisions (standard/splash/double-spread). |
| **Variable panel sizing** | No | page_compose.py (line 57–80) produces a horizontal strip. All panels are the same height and proportional width. Professional manga uses panel scale to direct emotional weight — a key emotional moment gets a large panel; a transitional beat gets a small one. The current output cannot express this. | Redesign page_compose.py to accept a layout_spec with panel positions and dimensions. The MANGA_LAYOUT_AGENT_SPEC.md defines grid templates (2×3, 3×2, irregular) but page_compose.py does not implement them. |
| **Splash pages** | No | The MANGA_LAYOUT_AGENT_SPEC.md specifies splash page handling at §6.2 (full-bleed single image, no gutters, no border). page_compose.py has no splash mode. Chapter-opening spreads are absent. | Add `page_type: splash` branch in page_compose.py. Simple to implement once variable layout is added. |
| **Panel borders / gutters** | No | page_compose.py places panels flush against each other with no gutter or border. Professional manga has visible panel borders (black rules) and gutters (white space between panels). This is both aesthetic and functional — borders define the panel unit; gutters create rhythm. | Add gutter_px and border_weight parameters to page_compose.py. The spec defines them: 60px standard gutter, 8px black border stroke. |
| **Bubble zone reservation** | No | Lettering_spec.json is produced (both panels show `silence_confirmed: true` in the actual run — meaning zero dialogue was rendered). Even in chapters with dialogue, the bubble placements from lettering_spec.json are never composited onto panel images in page_compose.py. The layout stage does not call any lettering overlay step. | Modify page_compose.py to composite lettering_spec overlays onto panels. The spec defines the Z-order rendering pipeline (§7 of MANGA_LAYOUT_AGENT_SPEC.md). |
| **Lettering rendered on art** | No (spec exists, not executed) | lettering_spec.json exists as a data artifact but its content is never drawn onto panel images. The final page_001.png at 128×64 contains no text. A professional 24-page chapter has hundreds of dialogue bubbles visible on final pages. | Implement lettering compositor in page_compose.py or a separate lettering stage that modifies panel images before layout. |
| **Character consistency (across panels)** | No | Both panels in the anxiety_series run use the identical prompt (same text, different panel_ids). The FLUX model is called without any seed pinning, LoRA, or IP-Adapter reference. Character appearance will differ between calls. Across 14 chapters: complete visual inconsistency. | Use deterministic seed per character (spec references `base_seed`), plus character LoRA or IP-Adapter reference image injection. |
| **Tankōbon assembly / volume identity** | No | The pipeline produces per-chapter artifacts only. There is no volume collector, no volume cover, no series-level publication package. | Add a volume assembly stage after 8–10 chapters complete. Likely lowest priority for initial quality improvements. |
| **Editorial review** | Spec only | The QC agent spec describes 30 gates and a revision_queue. In practice, revision_queue.json shows zero issues on stub data. No human review loop is wired. | The QC infrastructure exists in spec. The blocker is that QC cannot evaluate quality until real image generation runs. Wire QC to flag for human review when visual drift or lettering failures are detected. |

---

## Section 4: Ranked Gap List (Highest Quality Impact First)

### Gap 1 — No Name Stage (Thumbnail Layout)
**Impact: CRITICAL**

This is the defining gap. Professional manga quality is almost entirely determined at the name stage. Phoenix Omega has no equivalent. The result is:
- All pages are identical horizontal strips
- Panel count per page is not a storytelling decision but a data artifact
- Large emotional moments get the same visual space as transitional beats
- Bubble zones are never reserved, so lettering cannot be placed without covering art
- Pacing cannot be varied because page structure is uniform

The Series Bible spec (MANGA_SERIES_BIBLE_SPEC.md) defines a sophisticated 19-page structural formula with variable panel density across 5 page sections (COMPRESSION: 7–10 panels per page → AFTER: 1–2 panels per page). This formula cannot be expressed through page_compose.py's horizontal strip.

**Evidence:** `artifacts/manga/anxiety_series/final_page_composite/page_001.png` = 128×64 pixels, two equal panels side by side.

---

### Gap 2 — Lettering Not Rendered on Art
**Impact: CRITICAL**

lettering_spec.json is produced by the lettering stage. page_compose.py does not read it or apply it. The final pages have zero text.

Without text on panels:
- Reader cannot follow the story
- Dialogue that defines character voice is invisible
- SFX that carry emotional weight are absent
- The distinction between a "silence panel" and a "panel with missing text" is lost

**Evidence:** `artifacts/manga/anxiety_series/lettering_spec.json` shows `silence_confirmed: true` on all panels, meaning the lettering agent detected no dialogue to render — which is itself correct given that `chapter_script_writer_handoff.json` has empty dialogue arrays. But even if dialogue were present, page_compose.py has no code path to composite it.

**Code location:** `phoenix_v4/manga/chapter/page_compose.py`, lines 57–80 — no lettering overlay call exists anywhere in the file.

---

### Gap 3 — No Character Design Sheets / No Consistency Reference
**Impact: CRITICAL**

The `panel_prompts.json` shows both panels have the same prompt text but contain an empty `character_refs` array. FLUX is called without any consistency anchor.

The spec defines `character_model_sheets[]` as a required series setup output (AI_MANGA_PIPELINE_SUMMARY.md, §0 Visual Identity Agent table). In practice, no character model sheets exist in `artifacts/manga/anxiety_series/series/` — only a `style_bible.json` stub with two hex colors.

Without consistency reference:
- Characters look different in every panel
- Readers cannot identify who they are following
- The emotional arc (protagonist's face softening across chapters, per Series Bible §4.1) is invisible

---

### Gap 4 — No Series Identity
**Impact: HIGH**

The output is identified only by slug: `anxiety_gen_alpha_01`. There is no:
- Series title
- Logline
- Volume plan
- Publisher-facing identity

The Series Bible spec (MANGA_SERIES_BIBLE_SPEC.md, §1.1) defines `series_metadata.title`, `subtitle`, `publication_status`, etc. The actual `genre_blueprint.json` in the run artifacts contains only 8 lines — genre_id and act count.

A manga without a name cannot be marketed, shelved, or recognized.

---

### Gap 5 — Fixture Images (64×64 pixels, no real FLUX generation)
**Impact: HIGH**

All panel images are 64×64 pixel fixture images (identical content). Real FLUX generation is not connected. The spec describes A100 GPU clusters generating 1200×900px panels (MANGA_PRODUCTION_PIPELINE_SPEC.md, §3.2 panel_image_generator). The actual output is postage-stamp placeholders.

This means every other visual quality assessment (character consistency, setting design, screentone quality, composition) cannot be evaluated until real generation runs.

---

### Gap 6 — Uniform Panel Layout (No Variable Sizing)
**Impact: HIGH**

page_compose.py implements only horizontal tiling. The Layout Agent spec defines:
- 2×3 grids, 3×2 grids, 4-panel grids
- Irregular layouts
- Splash pages (full-bleed)
- Double spreads
- Silent page breathing space (gutters 2× normal)

None of these are implemented. The Series Bible's COMPRESSION→MA→CHOICE→TONGLEN→AFTER pacing formula (tight panels → sparse panels) cannot be expressed.

---

### Gap 7 — No Setting Design Sheets
**Impact: MEDIUM**

The `asset_registry.json` contains only `"series_placeholder"`. No real location assets exist. Background generation is prompt-only with no visual anchor. Across chapters, the school, bedroom, or street will look different every time.

---

### Gap 8 — No Panel Borders or Gutters
**Impact: MEDIUM**

page_compose.py places panels flush. Professional manga has:
- Black panel borders (8px, per spec §4.4)
- White gutters (60px standard, per spec §4.2)

These are not cosmetic. Borders define the panel unit; gutters create rhythm and reading flow.

---

### Gap 9 — No Tankōbon Assembly
**Impact: LOW (deferred)**

No volume collector, cover art, or print package. This is appropriately low priority until chapter-level quality is resolved.

---

## Section 5: Implementation Cost Estimates

### Cheap to close (days of dev work)

**A. Add panel borders and gutters to page_compose.py**
- Add `gutter_px` parameter (default: 60)
- Draw white gutter between panels before pasting
- Draw 8px black border around each panel
- File: `phoenix_v4/manga/chapter/page_compose.py`
- Estimated effort: 1–2 days
- Cost impact: None (rendering only; no additional API or GPU calls)

**B. Add splash page support to page_compose.py**
- Branch on `page_type` from chapter_script
- For `splash`: render single panel at full page dimensions
- File: `phoenix_v4/manga/chapter/page_compose.py`
- Estimated effort: 1 day
- Cost impact: None

**C. Wire lettering_spec.json compositing into page_compose.py**
- After tiling panels, read lettering_spec.json for each panel
- If not `silence_confirmed`, render speech bubbles using Pillow (already imported)
- The MANGA_TEXT_RENDERING_SPEC.md provides full rendering algorithm
- Files: `phoenix_v4/manga/chapter/page_compose.py`, new `lettering_compositor.py`
- Estimated effort: 3–5 days for basic bubble rendering; 2–3 weeks for full spec compliance
- Cost impact: None (CPU-only post-processing)

**D. Populate series identity fields in series config**
- Add `title`, `logline`, `volume_plan` to series configuration schema
- Required fields in `chapter_request.json` or a separate `series_identity.json`
- Estimated effort: 1 day
- Cost impact: None

---

### Medium effort (weeks of dev work)

**E. Variable panel layout (grid templates)**
- Replace page_compose.py's horizontal-strip logic with a layout engine that accepts panel size specs
- Implement 2×3, 3×2, 4-panel, and irregular grid templates per MANGA_LAYOUT_AGENT_SPEC.md §4.1
- Add a NameStage agent that converts chapter_script beat data into layout_spec (panel count, sizes, types per page)
- Files: `phoenix_v4/manga/chapter/page_compose.py` (rewrite), new `layout_spec.py`, new name stage executor
- Estimated effort: 2–4 weeks
- Cost impact: None (layout is CPU-only)

**F. Real FLUX image generation (connect GPU path)**
- The spec describes RunPod/FLUX integration (MANGA_PRODUCTION_PIPELINE_SPEC.md §4.3)
- Replace fixture image path with real FLUX calls using API
- Add error handling, retry logic, seed pinning
- Estimated effort: 1–2 weeks (backend integration)
- Cost impact: SIGNIFICANT — each panel at ~$0.01–0.05 GPU compute; 14 chapters × 9 panels = ~126 panels per book = $1.25–6.30 per book at current GPU rates

**G. Populate style_bible.json with real visual tokens**
- Currently `style_bible.json` has only two hex colors
- Full spec requires: camera lexicon, action lexicon, mood lexicon, silence grammar parameters, character visual registry, motif evolution map
- Estimated effort: 2–4 weeks (spec-driven content work, not engineering)
- Cost impact: None (config/data work)

---

### Expensive to close (months of dev work or significant infrastructure)

**H. Character design sheets + consistency reference (LoRA or IP-Adapter)**
- To maintain character consistency across panels, one of:
  - Train a per-series LoRA on 15–30 images of each character (requires approved character art first, then training run on GPU)
  - Use IP-Adapter with a reference image injected into each panel call
- LoRA training: 1–4 hours per character on A100; $5–20 compute cost
- IP-Adapter: lower quality consistency but no training cost; requires reference image
- Prerequisites: character design sheets must exist (hand-drawn or approved AI reference)
- Estimated effort: 4–8 weeks (includes creating reference art and training pipeline)
- Cost impact: $20–100 per series for LoRA training (one-time); IP-Adapter adds ~0% per panel

**I. The Name Stage (thumbnail layout agent)**
- Adding a name stage requires:
  - A new agent that reads chapter_script and produces per-page layout decisions (panel count, sizes, page types)
  - Integration of layout decisions into Visual Agent prompt generation (panel size affects composition prompt)
  - Redesign of page_compose.py to accept layout_spec
  - New QC gate to verify panel density matches Series Bible formula
- This is the most architecturally significant gap
- Estimated effort: 6–12 weeks end-to-end (agent + integration + QC)
- Cost impact: ~0.5–2% additional Claude API tokens per chapter for name stage LLM call

**J. Full editorial review loop (human-in-the-loop)**
- Requires: real image generation running (Gap 5), real lettering on pages (Gap C)
- A human reviewer interface to view draft pages and return notes
- Revision queue wiring so QC flags are surfaced to a human
- Estimated effort: 4–8 weeks (tooling + UX)
- Cost impact: Human review time per chapter; not compute cost

---

### Cost impact summary table

| Gap | Dev effort | Runtime cost impact |
|-----|-----------|-------------------|
| Panel borders / gutters | 1–2 days | None |
| Splash page support | 1 day | None |
| Lettering on pages | 3–5 days (basic) | None |
| Series identity fields | 1 day | None |
| Variable panel layout | 2–4 weeks | None |
| Real FLUX generation | 1–2 weeks | $1.25–6.30 per book |
| Populate style_bible | 2–4 weeks | None |
| Character LoRA / IP-Adapter | 4–8 weeks | $20–100 per series (LoRA, one-time) |
| Name stage agent | 6–12 weeks | Negligible per-chapter |
| Full editorial review loop | 4–8 weeks | Human time per chapter |

---

## Key Findings Summary

The Phoenix Omega spec documents are detailed and architecturally sound. The agents are well-designed on paper. The critical gap is between what the specs describe and what the actual runtime produces.

**The six gaps that produce the most visible quality degradation today are:**

1. **No name stage** — every page is a uniform horizontal strip regardless of narrative weight
2. **Lettering not rendered on pages** — final pages have zero text despite a lettering pipeline producing specs
3. **No character consistency reference** — characters regenerate independently per panel
4. **64×64 fixture images instead of real FLUX panels** — no real art generation is connected
5. **No panel borders or gutters** — pages lack the basic visual structure of manga
6. **Style bible is a 5-line stub** — the visual identity that should lock all downstream decisions is empty

The cheapest wins in order of effort: (1) add gutters and borders to page_compose.py, (2) wire lettering_spec.json into the compositor, (3) populate the style_bible with real visual tokens. These three changes require no new agents, no GPU cost, and would immediately produce recognizable manga page structure with text.

The most important long-term architectural investment is the **Name Stage** — without it, Phoenix Omega cannot produce variable panel layouts, and without variable layouts, the somatic pacing formulas defined in the Series Bible (COMPRESSION through AFTER) cannot be expressed visually regardless of how good the image generation becomes.

---

*Pearl_Research · Phoenix Omega · 2026-04-17*
