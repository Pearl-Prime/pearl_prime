# Manga Pipeline Forensic Teardown
## Series: Junko × Sleep Anxiety — `anxiety_gen_alpha_01`
**Date:** 2026-04-17  
**Analyst:** Pearl_Research  
**Scope:** Panel-level forensic critique of what the pipeline actually delivered vs what a real manga should deliver.

---

## Section 1: What Was Actually Delivered

### The PDF (`artifacts/manga_book/junko_sleep_anxiety_complete.pdf`)

- **4 "pages"** — each page is a single full-height vertical webtoon strip, not a manga page
- Each strip is **800 px wide × ~9,960–10,060 px tall** (ch01–ch03) or **800 × 8,320 px** (ch04)
- Aspect ratio per strip: approximately **1:12.5** — a scroll, not a page
- The PDF is simply 4 of these vertical images concatenated; PIL's `save_all=True` makes each strip one PDF page
- The book has **no cover**, **no chapter title pages**, **no table of contents**, **no series identity page**, **no author byline**
- The only text visible in the output is: chapter title banners, panel narration captions rendered in plain Helvetica, and SFX rendered in plain red text — no speech bubbles, no manga-authentic lettering, no balloon geometry

### The Webtoon Strips (`artifacts/manga_book/ch01_webtoon.png` through `ch04_webtoon.png`)

| File | Dimensions | Format |
|---|---|---|
| ch01_webtoon.png | 800 × 9,960 | RGB vertical scroll |
| ch02_webtoon.png | 800 × 9,960 | RGB vertical scroll |
| ch03_webtoon.png | 800 × 9,960 | RGB vertical scroll |
| ch04_webtoon.png | 800 × 8,320 | RGB vertical scroll |

Each strip contains:
- A 100 px header banner with chapter title in white Helvetica on dark purple-gray
- Panels resized to 800 px wide with 20 px dark gutters between them
- Panels are actual 1024×1024 AI-generated images for ch01 only (12 real images)
- Panels for ch02, ch03, and ch04 reuse the **identical 12 panel image files** (`p01_01.png` through `p05_04.png`) — every chapter renders the same images

### The Internal Pipeline Output (`artifacts/manga/anxiety_series/`)

This is the output of the **automated DAG pipeline** (`chapter_runner.py`) — distinct from the webtoon builder. It produced:

- `chapter_script_writer_handoff.json`: **1 page, 2 panels** — only chapter 10 ("What Remains")
- `panel_images_manifest.json`: **2 panels** (`p_10_0`, `p_10_1`), both `status: ok`
- `final_page_composite/page_001.png`: **128 × 64 pixels** — a horizontal strip of two 64×64 fixture images side-by-side
- `lettering_spec.json`: 2 entries, both `silence_confirmed: true`
- All 80 fixture images in `fixture_images/` are **identical** (same SHA-256 hash: `46413733...`) — they are all the same 64×64 pixel placeholder PNG

---

## Section 2: What Was Supposed to Be Delivered

### Per the Story Architecture (`series/story_architecture_handoff.json`)

The series `anxiety_gen_alpha_01` has:
- **10 chapters** with full titles and story beats:
  1. The First Alarm — Pattern recognition / Somatic awareness
  2. The Loop — Automatic response cycle / Cost visibility
  3. Someone Else's Calm — Social comparison / Internal vs external
  4. The Wall Moves Earlier — Capacity erosion / Input-recovery ratio
  5. Three AM Rehearsal — Anticipatory anxiety / Jaw-clenching body truth
  6. The Helpful Mask — Functional freeze / Performance vs presence
  7. When The Floor Drops — Panic as self-confrontation / Groundlessness as freedom
  8. The Cost Ledger — Accumulated price of anxiety / What was traded
  9. Sitting With The Scanner — Learning to not fix / Hearing instead of solving
  10. What Remains — Integration / The Bright after contraction

### Per Each Chapter Request (`chapters/ch_01/` through `chapters/ch_10/`)

Each chapter has a `chapter_request.json` with **6 panels** planned (`p01_01` through `p01_06`). At minimum this implies 6 panels per chapter, **10 chapters = 60 panels minimum** for the full book.

### Per the Series Bible Spec (`specs/MANGA_SERIES_BIBLE_SPEC.md`, §3)

The spec defines a **19-page chapter structure** with named acts and visual density targets:
- COMPRESSION (pages 1–4): 7–10 panels/page
- MA / Negative Space (pages 5–8): 5–7 panels/page
- CHOICE (pages 9–12): 3–5 panels/page
- TONGLEN (pages 13–16): 2–4 panels/page
- AFTER (pages 17–19): 1–2 panels/page

This yields approximately **80–140 panels per chapter**. For 10 chapters: **800–1,400 panels total**.

### Per the Source Chapter Scripts (`artifacts/pipeline_examples/manga_book/`)

The webtoon builder's actual source data shows what a properly-written chapter looks like. Ch01 ("The 2 AM Scroll") contains:
- **5 pages**, **12 panels**
- Every panel has a rich `visual_prompt` (50–100 words), `narration` (prose), `emotional_band` (1–3), `camera` (extreme_close / medium / wide_overhead / split_symbolic), `mood` (numb_routine / isolation / dread_surfacing / vulnerable_stillness), and `body_anchor` (somatic physical detail)
- SFX present: `*(scroll scroll scroll)*`, `*(swipe)*`, `*(chatter, trays, morning bustle)*`
- Character name "Nana" used consistently with series identity "Junko × Sleep Anxiety"

### Per the Layout Agent Spec (`specs/MANGA_LAYOUT_AGENT_SPEC.md`)

The spec calls for:
- Grid-based page layouts (2×3, 3×2, 4-panel, irregular)
- Page dimensions: 5200 × 7200 px
- Panel dimensions: 2400 × 3200 px at 300 dpi
- Gutter widths: 60–80 px
- Text overlay: background panel → bubbles → SFX → captions with z-ordering
- Reading direction enforcement (RTL/LTR/webtoon)
- Panel borders, bleed-safe composites

### Per the Lettering Spec (`specs/MANGA_TEXT_RENDERING_SPEC.md`)

The spec calls for:
- Speech balloon geometry (tail pointing to speaker)
- Balloon types: dialogue, thought, caption, SFX
- SHA-256 hash verification of all text elements
- NotoSans / NotoSans-Bold fonts per `lettering_style_bible.json`
- Silent panels produce `silence_confirmed: true` entries — active assertion
- Post-silence bubbles: smallest/lightest/shortest in chapter with `first_after_silence: true`

### Per the Author Identity (`series/manga_author_identity.json`)

A full author identity exists — **Brook Hearthlight**, EI author for brand **Stillness Press**, genre **dark_psychological** — with an EI disclosure text. This was supposed to appear in the book.

---

## Section 3: Gap Inventory

**Gap 1 — Chapter scope truncated from 10 to 1 (root issue: wrong chapter number passed to writer)**

The automated pipeline (`chapter_runner.py`) produced output for **only one chapter** (ch_01 in the directory, but `chapter_number: 10` per `chapter_request.json`). The `chapter_script_writer_handoff.json` contains the beat text "Establish: Integration / Deepen: The Bright after contraction" which matches `story_architecture_handoff.json` chapter 10 ("What Remains") — not chapter 1 ("The First Alarm"). The `chapter_request.json` in the root workspace has `"chapter_number": 10` but `"chapter_id": "ch_01"`. The mismatch means the writer stage resolved chapter 10 beats into a file labeled ch_01.

Evidence: `artifacts/manga/anxiety_series/chapter_request.json` line 7: `"chapter_number": 10`. `story_architecture_handoff.json` chapter 10 beats exactly match the script. All 9 remaining chapters (`ch_02` through `ch_10`) contain only a stub `chapter_request.json` with placeholder visual prompts (`"visual_prompt": "manga panel 1 for chapter 2"`) — no script, no images, no lettering spec.

**Gap 2 — 1 page produced instead of 19 (writer stage collapses chapter to stub)**

`chapter_script_writer_handoff.json` has **1 page with 2 panels**. The Series Bible calls for 19 pages per chapter. Even the ch01 reference script in `pipeline_examples` has 5 pages and 12 panels.

Evidence: `chapter_script_writer_handoff.json` — `"pages": [{"page_number": 1, ...}]`, single entry. `chapter_script_internal_record.json` identical. `specs/MANGA_SERIES_BIBLE_SPEC.md` §3: "19-page structural formula."

The writer stub (`phoenix_v4/manga/chapter/writer_stub.py`) — named "stub" in the import path at `chapter_runner.py` line 13 — appears to generate only one page with two panels regardless of chapter length. This is a deliberate stub, not a complete implementation.

**Gap 3 — All panel images are 64×64 placeholder squares (fixture images, not AI-generated art)**

The `panel_images_manifest.json` records both panels as `status: ok` with paths to `fixture_images/p_10_0.png` and `fixture_images/p_10_1.png`. These are 64×64 RGB PNGs, all with the identical SHA-256 hash (`46413733d372fc240720093ecf681356ca21331bda64d538b21549391906a71a`). There are 80 fixture images total, every single one the same file.

The spec calls for 2400×3200 px panels at 300 dpi. The pipeline produced 64×64 px placeholder squares.

Evidence: `panel_images_manifest.json` `"width": 64, "height": 64`. `fixture_images/` — 80 files, 249 bytes each, one unique hash. Image backend used: fixture/stub backend, not a real generative backend.

**Gap 4 — page_compose.py produces a horizontal strip, not a manga page grid**

`phoenix_v4/manga/chapter/page_compose.py` docstring (line 26): `"one row per page, left-to-right"`. The function:

```python
total_w = sum(im.width for im in row)
canvas = Image.new("RGBA", (total_w, target_h), ...)
```

This concatenates all panels on a page side-by-side into one wide horizontal image. For the actual output: 2 panels at 64×64 each → 128×64 final composite. This is not a manga page. A manga page requires a 2D grid (rows AND columns), portrait orientation (taller than wide), gutter spacing, and panel size variation. The composer produces a single horizontal row per page regardless of how many panels exist.

Evidence: `final_page_composite/page_001.png` — 128×64 pixels, landscape orientation, 2:1 aspect ratio. Layout Agent Spec calls for 5200×7200 px pages (portrait, ~0.72 aspect ratio). The output is inverted in orientation and 0.014% of the required pixel area.

**Gap 5 — Lettering spec contains only `silence_confirmed: true` entries — no text rendered anywhere**

`lettering_spec.json` has two entries, both `silence_confirmed: true`. No dialogue, no SFX, no captions, no balloon geometry. The chapter script confirms this — both panels have `"dialogue": []` — but this is an artifact of the stub writer generating content-free panels.

The source chapter scripts (`ch01_the_2am_scroll.json`) contain rich narration, SFX, and body anchors. The lettering spec for the actual book output contains nothing.

Evidence: `lettering_spec.json` — 14 lines, zero text elements. `chapter_script_writer_handoff.json` panels — `"dialogue": []` on both.

**Gap 6 — All 4 chapters in the webtoon use identical panel images (reused ch01 image set)**

The webtoon builder (`scripts/release/build_manga_webtoon.py`) looks for panel images by panel_id in a single shared `panels/` directory. All 4 chapters use the same panel_id scheme (`p01_01`, `p01_02`, ... `p05_04`). The panels directory contains 12 files covering ch01. When the builder runs ch02, ch03, and ch04, it finds the same 12 files and reuses them for different story content.

Evidence: Ch02 script `"panel_id": "p01_01"` — identical to ch01. Panels directory: 12 files, no chapter prefix. `build_chapter_strip()` line 182: `img_path = panels_dir / f"{pid}.png"` — flat lookup with no chapter namespace.

**Gap 7 — No dialogue exists anywhere in the delivered book**

All four chapter scripts in `pipeline_examples/` have `"dialogue": ""` on every panel. The series is rendered entirely in narration captions. There are no character speech bubbles anywhere. Characters never speak.

This is not necessarily spec-violating (the spec allows silent chapters), but combined with all other gaps it means the reader sees: narrator text rendered in plain Helvetica over colored placeholder backgrounds, with no character interaction, no SFX except three instances across all four chapters.

Evidence: All `ch0*.json` dialogue fields are empty strings on all 46 panels. SFX appear only on 3 panels: `p01_01` (scroll scroll scroll), `p04_01` (swipe), `ch03 p03_01` (chatter, trays, morning bustle).

**Gap 8 — Series identity, author identity, and EI disclosure never appear in the output**

`series/manga_author_identity.json` defines author "Brook Hearthlight," brand "Stillness Press," and an EI disclosure text. None of this appears anywhere in the PDF or webtoon strips. There is no series title page, no author credit, no brand mark, no volume/chapter numbering in the content (only the webtoon filename prefix ch01–ch04).

Evidence: `manga_author_identity.json` — `"display_name": "Brook Hearthlight"`, `"brand_id": "stillness_press"`. `build_manga_webtoon.py` — header draws only `chapter.get("title", "Untitled")`. No byline, no series metadata, no disclosure text rendered anywhere in the output pipeline.

**Gap 9 — Series memory records ch_01 pipeline completion 12 times (phantom run loop)**

`series/series_memory.json` contains **12 identical fact entries**, each `"kind": "chapter_pipeline_completed"` for `"chapter_id": "ch_01"`. The pipeline was run at least 12 times against the same workspace without advancing to any other chapter. The `_stage_memory` function (`chapter_runner.py` line 356) appends a new fact on every run rather than checking for idempotency.

Evidence: `series_memory.json` — 12 entries, all identical dicts. `series_memory_merge.py` (inferred from runner code): `"op": "append_fact"` — no deduplication.

**Gap 10 — Panel prompt visual descriptions are generic copy-paste tokens, not scene-specific art direction**

`panel_prompts.json` contains two panels with identical prompts — the same 47-token string for both. Neither prompt describes the specific story beat (Integration / The Bright after contraction). Both are generic: `"young woman, dark hair, contemplative expression, simple dark clothing, manga, black and white..."`. The prompt text for `p_10_0` and `p_10_1` is character-for-character identical, including all `composition_notes`, `continuity_tags`, and `sdf_conditioning` fields.

Evidence: `panel_prompts.json` — `panels[0].prompt == panels[1].prompt` (verified by inspection). `silence_compliance: false` on both panels despite lettering spec marking both `silence_confirmed: true`.

**Gap 11 — The `final_page_composite` is never used by the PDF builder**

The automated pipeline writes to `artifacts/manga/anxiety_series/final_page_composite/page_001.png`. The PDF builder (`scripts/release/build_manga_webtoon.py`) reads from a completely different path: `artifacts/pipeline_examples/manga_book/`. These are disconnected subsystems with no data flow between them. The pipeline output (128×64 px composites from fixture images) is dead output that feeds nothing.

Evidence: `build_manga_webtoon.py` line 247–263 — reads from `artifacts/pipeline_examples/manga_book/`. `chapter_runner.py` `_stage_layout()` writes to `workspace / manga_paths.FINAL_PAGE_COMPOSITE_DIR` = `artifacts/manga/anxiety_series/final_page_composite/`. No script bridges these.

**Gap 12 — The 10-chapter story arc terminates at chapter 10 instead of beginning at chapter 1**

The pipeline ran with `chapter_number=10` producing only the final chapter's beats. The completed arc resolution ("Integration: The Bright after contraction") was generated without any of the preceding 9 chapters that build toward it. A reader of the "complete" book sees: one minimal page from the series finale — nothing else from the automated pipeline's chapter content.

Evidence: `chapter_request.json` root workspace — `"chapter_number": 10`. `story_architecture_handoff.json` — chapter 10 is the resolution chapter. Chapters 1–9 beats never rendered.

---

## Section 4: Root Causes

**RC-A: Writer stub is not a complete implementation**

The import at `chapter_runner.py` line 13 calls `build_chapter_script_pair_from_handoff` from `phoenix_v4/manga/chapter/writer_stub.py`. A module named `_stub` is a placeholder. The stub produces one page with two panels regardless of story input. Until a real LLM-backed writer agent is wired here, every chapter will be a 1-page, 2-panel, content-free script.

**RC-B: Image backend is fixture/stub mode, not generative**

`build_panel_images_manifest` uses a fixture backend that returns pre-existing 64×64 PNG files. No connection to a real image generation service (ComfyUI, RunComfy, SDXL, etc.) is active. The fixture images are all identical. There is no mechanism in the pipeline to detect or flag this condition — `revision_queue.json` reports `"chapter_clearance": "pass"` with no issues.

**RC-C: page_compose.py implements horizontal tiling, not page layout**

`page_compose.py` lines 60–75: `total_w = sum(im.width for im in row)` — width is additive (horizontal). `target_h = max(im.height for im in loaded)` — height is the tallest panel only. This is a filmstrip concatenator. A manga page compositor must place panels at (x, y) grid positions with independent row and column assignments. The function has no concept of rows-per-page, column count, or portrait canvas creation.

**RC-D: Chapter request file has chapter_number mismatch (10 in root, varying in chapters/)**

The root workspace `chapter_request.json` has `"chapter_number": 10` while `"chapter_id": "ch_01"`. The per-chapter files in `chapters/ch_01/chapter_request.json` have `"chapter_number": 1` — correct. But the DAG pipeline reads from the root workspace, not from `chapters/`. The pipeline has run only against the root workspace, advancing chapter 10 content into a ch_01-labeled directory.

**RC-E: Webtoon builder and chapter pipeline are disconnected subsystems**

`build_manga_webtoon.py` reads from `artifacts/pipeline_examples/manga_book/` — a static example directory with hand-crafted JSON and 12 manually provided panel images. The chapter pipeline writes to `artifacts/manga/anxiety_series/`. There is no orchestrator, no handoff script, and no path configuration connecting these two systems. The webtoon builder is a standalone demonstration tool, not the pipeline's output stage.

**RC-F: Panel ID namespace is flat with no chapter prefix**

All 4 chapter scripts use `p01_01` through `p05_04`. The panels directory has one flat set of 12 images covering these IDs. Ch02–ch04 silently reuse ch01 images because the IDs collide. A correct namespace would use `ch01_p01_01`, `ch02_p01_01`, etc. The `chapter_request.json` files in `chapters/` do use chapter-prefixed IDs (`p01_01` for ch01, `p02_01` for ch02) but the `pipeline_examples` scripts do not.

**RC-G: QC passes unconditionally on stub output**

`revision_queue.json` reports `"chapter_clearance": "pass"`, `"issues": []`. The QC stage (`build_revision_queue_for_chapter`) does not detect that panels are 64×64 fixture images rather than generated art, that the page composite is 128×64 landscape rather than portrait, or that all dialogue is empty. The QC agent has no minimum resolution gate, no composition orientation gate, and no content presence gate.

**RC-H: Series memory append is not idempotent**

`_stage_memory()` appends one `chapter_pipeline_completed` fact per run without checking whether the same chapter has already been recorded. After 12 pipeline runs, series memory has 12 identical facts. This inflates memory size and could corrupt future state lookups.

---

## Section 5: Industry Comparison

### What Was Delivered

| Metric | Delivered | Industry Standard (iyashikei / shojo) | Ratio |
|---|---|---|---|
| Chapters | 4 webtoon / 1 DAG pipeline | 10 planned in series arc | 40% / 10% |
| Pages per chapter | 1 (DAG) / 5 (webtoon) | 19–24 (series bible: 19) | 5% / 26% |
| Panels per chapter | 2 (DAG) / 10–12 (webtoon) | ~80–140 (series bible) | 1.4% / 8.5% |
| Panel image dimensions | 64×64 px (DAG) / 1024×1024 px (webtoon) | 2400×3200 px at 300 dpi (spec) | 0.06% / 10% of pixel area |
| Page composite dimensions | 128×64 px | 5200×7200 px | 0.005% of pixel area |
| Panel aspect ratio | 2:1 landscape (DAG) | 3:4 to 2:3 portrait | Inverted |
| Dialogue panels | 0 | Variable; iyashikei typically low-dialogue but not zero | — |
| Speech bubbles | 0 | Required lettering element | Absent |
| Lettering overlay | None (plain Helvetica captions) | Balloon geometry, SFX rendering, z-ordered overlay | Absent |
| Author identity on page | Absent | Standard: byline, copyright, imprint | Absent |
| Series title page | Absent | Standard: volume cover, series title, chapter list | Absent |
| Unique panel images | 12 (shared across all 4 chapters) | 46 (webtoon) / 20–280 (full spec) | — |

### Comparison to the Spec's Own Standard

The Series Bible (`MANGA_SERIES_BIBLE_SPEC.md` §3) defines the **19-page chapter formula**. A compliant chapter 1 should open with pages 1–4 at 7–10 panels/page (28–40 panels in COMPRESSION alone). The delivered DAG chapter has 2 panels in 1 page — 1–7% of the COMPRESSION section alone.

The Layout Agent Spec calls for pages at 5200×7200 px. The delivered composite is 128×64 px — **0.005% of the required pixel area**.

### What Would a Real Iyashikei Chapter Look Like

A real iyashikei chapter (e.g., Yotsuba&!, Mushishi, A Silent Voice) delivers:
- 20–28 pages, portrait (B6 or tankōbon: ~128×182 mm)
- 3–7 panels per page with deliberate size variation
- At least one silent page or near-silent sequence per chapter
- Character-specific visual vocabulary maintained across chapters (linework, screen tone, hair)
- Legible lettering in localized fonts with speech balloon geometry
- Distinct pacing: compressed multi-panel early pages opening into sparse, breathing late pages
- Gutter spacing used as a pacing device, not a decorative gap

The current pipeline output is: 2 identical 64×64 pixel squares placed side by side on a 128×64 canvas, with a lettering spec confirming silence on both panels. Delivered to a reader, this would appear as two small gray squares on a white background. The PDF's webtoon strips are better — genuine scene content, genuine AI-generated imagery — but each chapter presents identical images under different story titles because the panel ID namespace is flat.

---

## Summary of Critical Failures (Priority Order)

1. **Writer is a stub** — produces 1 page / 2 panels regardless of input. No real chapter content is ever generated by the automated pipeline. Fix: wire a real LLM-backed writer agent.

2. **Image backend is fixture mode** — all panels are identical 64×64 placeholders. No generative image service is connected. Fix: wire ComfyUI/RunComfy backend; fixture mode must be test-only.

3. **page_compose.py is a horizontal filmstrip** — produces landscape strips, not manga pages. Fix: rewrite to place panels in a 2D portrait grid per the Layout Agent Spec.

4. **Webtoon builder and chapter pipeline are disconnected** — no data flows from the automated pipeline to the PDF builder. Fix: an orchestrator must pass `final_page_composite/` output to the release stage.

5. **Panel ID namespace collision** — all chapters share the same panel IDs; images from ch01 render for all chapters. Fix: prefix panel IDs with chapter number (e.g., `ch02_p01_01`).

6. **Chapter number mismatch** — root workspace has `chapter_number: 10`; pipeline ran chapter 10 beats into a ch_01 directory. Fix: validate chapter_number against chapter_id before running.

7. **QC passes stub output unconditionally** — no gate for panel resolution, composite orientation, or content presence. Fix: add minimum resolution gate (e.g., reject panels < 512 px), add portrait orientation gate on composites.

8. **Series identity never renders** — author, brand, EI disclosure, series title are all in data but nothing connects them to the output. Fix: render identity page as first page of the PDF.
