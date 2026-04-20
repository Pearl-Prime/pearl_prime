# Manga Name (ネーム) Thumbnail Stage Specification
## AI Manga Dharma System — SpiritualTech Systems

**Version:** 1.0
**Status:** Design
**Workstream:** 6
**Date:** 2026-04-17

---

## 1. PURPOSE & RATIONALE

The **Name Stage** (ネーム, *nēmu*) is the editorial approval gate inserted between the Chapter Writer and Image Generation. It produces thumbnail page layouts — rough wireframes showing panel counts, panel size hierarchy, bubble zone reservations, and page-turn beats — before FLUX is ever invoked.

**Why this matters:**

- Rejecting a bad name is cheap (seconds). Rejecting bad FLUX renders is expensive (GPU hours, pipeline restarts).
- Uniform panel grids (what `page_compose.py` currently produces) are aesthetically wrong for iyashikei. Visual rhythm requires deliberate size variation.
- Bubble zones must be *reserved before art is drawn*. The current pipeline places bubbles heuristically after render; this forces awkward cropping and unsafe text zones.
- Page-turn payoffs are the primary reader retention mechanism. They cannot be retrofitted; they must be architecturally placed.

**The Name Stage makes two decisions that all downstream agents consume as contracts:**
1. `page_layout_spec.json` — per-panel grid positions, size classes, bubble zone reservations
2. Wireframe PDF — visual editorial review artifact (rendered before FLUX)

---

## 2. PIPELINE POSITION

```
Chapter Writer
    ↓
chapter_script_writer_handoff.json
    ↓
[CHAPTER_NAME STAGE]  ← NEW — Workstream 6
    ↓
page_layout_spec.json  +  wireframe.pdf
    ↓ (editorial approval gate — human or automated)
Chapter Image Gen  (FLUX)
    ↓
Lettering Agent
    ↓
Layout Agent  (page_compose.py refactor reads page_layout_spec.json)
    ↓
QC Agent
```

The Name Stage sits between `CHAPTER_WRITER` and `CHAPTER_IMAGE_GEN` in the stage sequence defined by `MANGA_PRODUCTION_PIPELINE_SPEC.md` Section 3.1.

---

## 3. INPUTS

### 3.1 Primary Input: `chapter_script_writer_handoff.json`

The Name Stage reads the `writer_handoff` portion of the chapter script (as defined in `MANGA_CHAPTER_WRITER_SPEC.md` Section 5). Key fields consumed:

```json
{
  "chapter_id": "ch_01",
  "pages": [
    {
      "page_number": 1,
      "page_type": "standard | silent | high_action",
      "mood": "establishing | tense | intimate | ...",
      "panels": [
        {
          "panel_id": "CH001_P01_PL01",
          "panel_type": "dialogue | silent | action | reaction | revelation",
          "camera": "wide | medium | close | extreme_close | pov | two_shot",
          "subject": "protagonist | environment | ...",
          "action": "...",
          "mood_direction": "...",
          "silence_guard": false,
          "dialogue": [ ... ],
          "sfx": [ ... ],
          "caption": null
        }
      ]
    }
  ]
}
```

Fields used by the Name Stage algorithm:
- `panel_type` → maps to `emotional_role` (see Section 4.1)
- `camera` → informs size class (wide camera = large/splash; extreme_close = small)
- `dialogue` array length → determines bubble zone count and size
- `silence_guard` → forces size reduction on guard panels
- `page_type: "silent"` → triggers breath-page layout template
- `page_type: "high_action"` → triggers action-heavy layout template

### 3.2 Secondary Input: Genre Config

```json
{
  "genre": "iyashikei",
  "reading_direction": "ltr",
  "target_page_count": 24,
  "page_size": { "width": 5200, "height": 7200 },
  "grid_columns": 12,
  "grid_rows": 18,
  "gutter_px": 60
}
```

Genre config determines which layout guidelines apply (see Section 5).

---

## 4. NAME GENERATION ALGORITHM

### 4.1 Emotional Role Mapping

The Name Stage derives `emotional_role` from `panel_type` + `camera` + `silence_guard`:

| panel_type | camera | silence_guard | → emotional_role |
|-----------|--------|--------------|-----------------|
| `silent` | any | false | `breath` |
| `silent` | any | true | `silence` |
| `dialogue` | `wide` or `pov` | — | `establishing` |
| `dialogue` | `medium` or `two_shot` | — | `intimate_dialogue` |
| `dialogue` | `close` or `extreme_close` | — | `reaction` |
| `action` | `wide` | — | `action` |
| `action` | `medium` or `close` | — | `action` |
| `reaction` | any | — | `reaction` |
| `revelation` | any | — | `revelation` |

### 4.2 Size Class Assignment (Rule-Based)

Map `emotional_role` → `size_class`:

| emotional_role | default_size_class | notes |
|---------------|-------------------|-------|
| `establishing` | `large` | or `splash` if first panel of chapter |
| `action` | `large` | wide crop preferred |
| `intimate_dialogue` | `medium` | close-up framing |
| `reaction` | `small` | cut fast, tight |
| `breath` | `large` | minimal content, maximize space |
| `silence` | `medium` | adjacent to breath panels |
| `revelation` | `full_page` or `splash` | major reveals get maximum space |

**Size class pixel allocations** (on 5200×7200 page, 180px bleed, 60px gutter):

| size_class | approx fraction | typical pixel height |
|-----------|----------------|---------------------|
| `full_page` | 1/1 | 6840px (full content area) |
| `splash` | 2/3 | 4560px |
| `large` | 1/2 | 3240px |
| `medium` | 1/3 | 2160px |
| `small` | 1/4 | 1620px |
| `gutter` | 1/8 | 720px — narrow accent strip |

### 4.3 Grid Position Assignment

The Name Stage uses a 12-column × 18-row logical grid (each cell = approximately 393px × 380px at 5200×7200). Panels are assigned `row`, `col`, `row_span`, `col_span` to tile the page without overlap.

**Assignment algorithm:**

```
function assign_grid_positions(panels, genre_config):
  grid = new 18×12 boolean grid  // false = unoccupied
  reading_order = 1

  for each panel in panels (in reading order, LTR = top-left to bottom-right):
    size = panel.size_class
    span = size_class_to_span(size, available_space(grid))
    pos = find_top_left_fit(grid, span.row_span, span.col_span)

    if pos is None:
      # degrade: reduce size_class by one step and retry
      size = demote(size)
      span = size_class_to_span(size, available_space(grid))
      pos = find_top_left_fit(grid, span.row_span, span.col_span)

    mark_occupied(grid, pos, span)
    panel.position = { row: pos.row, col: pos.col, row_span: span.row_span, col_span: span.col_span }
    panel.reading_order = reading_order++
```

**Size class → grid span lookup:**

| size_class | row_span | col_span |
|-----------|----------|----------|
| `full_page` | 18 | 12 |
| `splash` | 12 | 12 |
| `large` | 9 | 12 |
| `medium` | 6 | 6 |
| `small` | 4 | 6 |
| `gutter` | 2 | 12 |

Partial-width `medium` and `small` panels can be col_span=4 or col_span=3 when space is constrained, enabling 2- or 3-column rows.

### 4.4 Bubble Zone Calculation

For each panel with dialogue, the Name Stage reserves `bubble_zones` — rectangular areas within the panel where text will be placed. These are passed to the Lettering Agent, replacing heuristic placement.

**Calculation:**

```
function calculate_bubble_zones(panel, panel_pixel_dims):
  zones = []
  dialogue_count = len(panel.dialogue)
  sfx_present = len(panel.sfx) > 0

  if dialogue_count == 0:
    return []  # no zones needed

  # Available text area: panel minus safe zone (120px inset all sides)
  text_area = {
    x: 120, y: 120,
    w: panel_pixel_dims.width - 240,
    h: panel_pixel_dims.height - 240
  }

  # Divide text area into zones based on dialogue count
  if dialogue_count == 1:
    zones = [top_zone(text_area, fraction=0.25)]  # single bubble, top 25%

  elif dialogue_count == 2:
    zones = [
      top_zone(text_area, fraction=0.25),
      bottom_zone(text_area, fraction=0.20)
    ]

  elif dialogue_count >= 3:
    zones = distribute_vertically(text_area, dialogue_count, max_fraction=0.15)

  # Each zone: {x, y, w, h, type}
  # type: "speech" | "thought" | "narration" | "sfx"
  for i, line in enumerate(panel.dialogue):
    zones[i].type = bubble_type_from(line.bubble_type)

  if sfx_present:
    zones.append(sfx_zone(text_area))  # corner zone for SFX

  return zones
```

**Zone coordinates are expressed as percentages of panel pixel dimensions** (0–100), so they scale correctly regardless of final render resolution.

---

## 5. IYASHIKEI LAYOUT GUIDELINES

These rules override the generic size class defaults when `genre == "iyashikei"`:

### 5.1 Page-Level Rules

**Opening page (page 1):**
- Always `establishing` shot
- Force size_class to `full_page` or `splash`
- Zero bubble zones (pure visual opening)

**Closing page (final page):**
- Must end with `breath` or `silence` panel
- Final panel: size_class `large` minimum
- Zero or one bubble zone maximum

**Dialogue concentration:**
- Pages with high dialogue density (avg >2 bubbles/panel) must not appear in first 3 or last 3 pages
- Dialogue-heavy pages cluster in the middle third of the chapter

**Breath panel requirement:**
- At minimum one `breath` panel (size_class `large` or bigger, zero bubbles) per page spread (every 2 pages)
- If a spread has no breath panel, the Name Stage inserts a `gutter` breath strip

### 5.2 Panel Count Limits

| page_type | min panels | max panels |
|-----------|-----------|-----------|
| opening (page 1) | 1 | 1 |
| standard | 2 | 5 |
| silent | 1 | 4 |
| high_action | 3 | 6 |
| closing (last page) | 1 | 2 |

Iyashikei: **never more than 5 panels per page** (unlike shōnen which allows 6+).

### 5.3 Rhythm Alternation

Enforce alternation between "dense" and "open" pages:

```
if current_page has >= 4 panels:
  next_page.max_panels = 3
  next_page.must_include_large_or_bigger = true
```

### 5.4 Page-Turn Payoff Placement

For LTR reading: odd-numbered pages are right-hand pages (revealed on page turn).

**Rule:** At least 30% of odd-numbered pages must have `page_turn_payoff: true`.

**Payoff triggers** (automatic):
- `panel_type: "revelation"` on last panel of page
- `page_type: "silent"` following a high-action page
- `size_class: "splash"` or `full_page` on any panel of the page

---

## 6. HYBRID GENERATION: THREE-CANDIDATE SELECTION

The Name Stage generates **three layout candidates per page** and selects the best for genre fit.

### 6.1 Candidate Generation

```
function generate_candidates(page, genre_config):
  candidate_A = rule_based_layout(page)  // Section 4 algorithm
  candidate_B = vary_sizes(candidate_A, variation="compress")  // smaller panels, more
  candidate_C = vary_sizes(candidate_A, variation="expand")    // fewer, larger panels

  return [candidate_A, candidate_B, candidate_C]
```

### 6.2 LLM Selection

When `llm_assist: true` in the genre config, Claude receives:

```
SYSTEM: You are a manga layout editor specializing in iyashikei.
        Select the layout candidate that best serves genre feel.

USER: Chapter beat: [panel_type, camera, mood_direction per panel]
      Genre: iyashikei (slow, healing, environmental)
      
      Candidate A: [JSON layout summary]
      Candidate B: [JSON layout summary]
      Candidate C: [JSON layout summary]
      
      Which candidate best serves iyashikei pacing and why?
      Output: { "selection": "A|B|C", "rationale": "..." }
```

When `llm_assist: false`, the rule-based algorithm selects the candidate closest to genre target density (Section 5.2 panel count limits).

---

## 7. OUTPUT: `page_layout_spec.json`

Full schema is defined in `specs/manga_page_layout_spec_schema.json`. The logical structure:

```json
{
  "schema_version": "1.0",
  "chapter_id": "ch_01",
  "genre": "iyashikei",
  "reading_direction": "ltr",
  "target_page_count": 24,
  "generation_method": "hybrid_llm",
  "pages": [
    {
      "page_number": 1,
      "page_type": "opening_splash",
      "panels": [
        {
          "panel_id": "CH001_P01_PL01",
          "size_class": "full_page",
          "position": { "row": 0, "col": 0, "row_span": 18, "col_span": 12 },
          "bubble_zones": [],
          "emotional_role": "establishing",
          "reading_order": 1,
          "pixel_rect": { "x": 180, "y": 180, "w": 4840, "h": 6840 }
        }
      ],
      "page_turn_payoff": false,
      "page_turn_note": null,
      "breath_panel_present": false,
      "dialogue_density": 0.0
    }
  ],
  "chapter_stats": {
    "total_panels": 78,
    "silent_panel_count": 32,
    "silent_panel_pct": 0.41,
    "breath_panel_count": 18,
    "avg_bubbles_per_page": 1.8,
    "page_turn_payoff_count": 5,
    "page_turn_payoff_odd_page_pct": 0.38
  }
}
```

**Field definitions:**

| field | type | description |
|-------|------|-------------|
| `panel_id` | string | matches panel_id from chapter_script |
| `size_class` | enum | `full_page`, `splash`, `large`, `medium`, `small`, `gutter` |
| `position.row` | int | top row in 18-row grid (0-based) |
| `position.col` | int | left col in 12-col grid (0-based) |
| `position.row_span` | int | rows occupied |
| `position.col_span` | int | cols occupied |
| `bubble_zones` | array | reserved text areas (see Section 4.4) |
| `emotional_role` | enum | `establishing`, `action`, `intimate_dialogue`, `reaction`, `breath`, `silence`, `revelation` |
| `reading_order` | int | 1-based reading sequence within page |
| `pixel_rect` | object | absolute pixel coordinates on 5200×7200 page: `{x, y, w, h}` |
| `page_turn_payoff` | bool | true if this page is designed as a page-turn reveal |
| `page_turn_note` | string or null | editorial note for the payoff beat |
| `breath_panel_present` | bool | true if at least one panel has emotional_role `breath` |
| `dialogue_density` | float | avg bubble zones per panel on this page |

---

## 8. WIREFRAME RENDER

Before FLUX is invoked, the Name Stage produces a wireframe PDF for editorial review.

### 8.1 What the Wireframe Shows

Each page is rendered as labeled rectangles on a white canvas:
- Rectangle fill: light gray for panels, white for gutter
- Border: 2px black
- Label inside each rectangle: `panel_id | size_class | emotional_role`
- Bubble zones: dashed blue rectangles inside panels
- Page number: bottom center
- Page turn payoff indicator: gold star bottom-right corner

### 8.2 Wireframe Renderer (PIL-based)

```python
# phoenix_v4/manga/name/wireframe_render.py

def render_wireframe_page(
    page_spec: dict,
    page_dims: tuple[int, int] = (5200, 7200),
    scale: float = 0.1,  # renders at 520×720 for preview
) -> Image:
    """Render a single page from page_layout_spec.json as a labeled wireframe."""
    ...

def render_wireframe_chapter(
    layout_spec: dict,
    out_path: Path,
) -> Path:
    """Render all pages into a multi-page PDF wireframe."""
    # Uses PIL + reportlab or fpdf2 for PDF assembly
    ...
```

### 8.3 Editorial Approval Gate

The wireframe is the gate. Three outcomes:

| outcome | action |
|---------|--------|
| `approved` | Proceed to FLUX image generation with `page_layout_spec.json` locked |
| `revision_requested` | Human edits `page_layout_spec.json` directly; re-render wireframe |
| `regenerate` | Name Stage reruns with modified constraints |

In automated runs (batch production), approval is auto-granted if all MQG gates pass (see `specs/manga_visual_quality_gates.md`).

---

## 9. PAGE_COMPOSE.PY REFACTOR SPECIFICATION

The current `phoenix_v4/manga/chapter/page_compose.py` uses **uniform horizontal tiling** (all panels in a row, equal height). This must be replaced with **irregular grid composition** driven by `page_layout_spec.json`.

### 9.1 Current Behavior (to be replaced)

```python
# Current: simple horizontal strip
target_h = max(im.height for im in loaded)
# all panels are scaled to the same height and placed left-to-right
```

This produces uniform horizontal strips — wrong for iyashikei and wrong for variable panel sizes.

### 9.2 New Interface

The refactored `compose_final_page_pngs` signature should be:

```python
def compose_final_page_pngs(
    chapter_script: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    out_dir: Path,
    page_layout_spec: Mapping[str, Any] | None = None,  # NEW PARAMETER
) -> list[Path]:
```

When `page_layout_spec` is `None`, the function falls back to the current horizontal strip behavior (backward compatibility).

When `page_layout_spec` is provided, the function:

1. Reads `page_layout_spec["pages"]` to get per-panel `pixel_rect` values
2. For each panel, scales the rendered image to fit `pixel_rect.w × pixel_rect.h`
3. Pastes each panel onto a 5200×7200 canvas at `(pixel_rect.x, pixel_rect.y)`
4. Draws gutter fills (white) between panels based on grid gaps
5. Does NOT re-tile or re-sort panels — `pixel_rect` is the authoritative position

### 9.3 Bubble Zone Pass-Through

The refactored compositor passes `bubble_zones` from the layout spec to the Lettering Agent:

```python
def extract_bubble_zones_for_lettering(
    page_layout_spec: Mapping[str, Any],
) -> dict[str, list[dict]]:
    """Return {panel_id: [bubble_zone, ...]} for consumption by the Lettering Agent."""
    ...
```

The Lettering Agent's Balloon Planner (as specified in `MANGA_TEXT_RENDERING_SPEC.md` Section 3) currently determines bubble positions from `composition_notes.empty_zones`. After the refactor, it receives pre-calculated `bubble_zones` from `page_layout_spec.json` and treats them as authoritative placement zones, bypassing the heuristic placement algorithm.

---

## 10. WORKED EXAMPLE: FIRST 6 PAGES OF AN IYASHIKEI CHAPTER 1

The following shows what a 24-page iyashikei chapter 1 name looks like for the first 6 pages.

**Chapter context:** Protagonist (Yuki) arrives at a new town; first encounter with the garden she will tend. Mood arc: quiet arrival → small curiosity → first breath.

### Page 1 — Opening Splash

```json
{
  "page_number": 1,
  "page_type": "opening_splash",
  "panels": [
    {
      "panel_id": "CH001_P01_PL01",
      "size_class": "full_page",
      "position": { "row": 0, "col": 0, "row_span": 18, "col_span": 12 },
      "bubble_zones": [],
      "emotional_role": "establishing",
      "reading_order": 1,
      "pixel_rect": { "x": 180, "y": 180, "w": 4840, "h": 6840 }
    }
  ],
  "page_turn_payoff": false,
  "page_turn_note": null,
  "breath_panel_present": false,
  "dialogue_density": 0.0
}
```

*Editorial note: Wide shot of the coastal town at golden hour. No dialogue. Pure setting. The reader's first breath with this world.*

### Page 2 — Standard (Train Arrival)

```json
{
  "page_number": 2,
  "page_type": "standard",
  "panels": [
    {
      "panel_id": "CH001_P02_PL01",
      "size_class": "large",
      "position": { "row": 0, "col": 0, "row_span": 9, "col_span": 12 },
      "bubble_zones": [
        { "x": 10, "y": 5, "w": 30, "h": 12, "type": "narration" }
      ],
      "emotional_role": "establishing",
      "reading_order": 1,
      "pixel_rect": { "x": 180, "y": 180, "w": 4840, "h": 3300 }
    },
    {
      "panel_id": "CH001_P02_PL02",
      "size_class": "medium",
      "position": { "row": 9, "col": 0, "row_span": 5, "col_span": 6 },
      "bubble_zones": [],
      "emotional_role": "reaction",
      "reading_order": 2,
      "pixel_rect": { "x": 180, "y": 3540, "w": 2360, "h": 1860 }
    },
    {
      "panel_id": "CH001_P02_PL03",
      "size_class": "medium",
      "position": { "row": 9, "col": 6, "row_span": 5, "col_span": 6 },
      "bubble_zones": [],
      "emotional_role": "breath",
      "reading_order": 3,
      "pixel_rect": { "x": 2600, "y": 3540, "w": 2360, "h": 1860 }
    },
    {
      "panel_id": "CH001_P02_PL04",
      "size_class": "gutter",
      "position": { "row": 14, "col": 0, "row_span": 4, "col_span": 12 },
      "bubble_zones": [
        { "x": 5, "y": 20, "w": 70, "h": 60, "type": "speech" }
      ],
      "emotional_role": "intimate_dialogue",
      "reading_order": 4,
      "pixel_rect": { "x": 180, "y": 5460, "w": 4840, "h": 1380 }
    }
  ],
  "page_turn_payoff": false,
  "page_turn_note": null,
  "breath_panel_present": true,
  "dialogue_density": 0.5
}
```

*Editorial note: Top large panel — train pulling in, Yuki at window. Middle two panels — her face (reaction), then the platform flowers (breath). Bottom gutter panel — station agent's greeting, single speech bubble. Dialogue introduced gently, not as visual weight.*

### Page 3 — Standard (Walking Through Town)

```json
{
  "page_number": 3,
  "page_type": "standard",
  "panels": [
    {
      "panel_id": "CH001_P03_PL01",
      "size_class": "splash",
      "position": { "row": 0, "col": 0, "row_span": 12, "col_span": 12 },
      "bubble_zones": [
        { "x": 60, "y": 5, "w": 30, "h": 10, "type": "narration" }
      ],
      "emotional_role": "establishing",
      "reading_order": 1,
      "pixel_rect": { "x": 180, "y": 180, "w": 4840, "h": 4380 }
    },
    {
      "panel_id": "CH001_P03_PL02",
      "size_class": "small",
      "position": { "row": 12, "col": 0, "row_span": 3, "col_span": 4 },
      "bubble_zones": [],
      "emotional_role": "reaction",
      "reading_order": 2,
      "pixel_rect": { "x": 180, "y": 4620, "w": 1540, "h": 1080 }
    },
    {
      "panel_id": "CH001_P03_PL03",
      "size_class": "small",
      "position": { "row": 12, "col": 4, "row_span": 3, "col_span": 4 },
      "bubble_zones": [],
      "emotional_role": "reaction",
      "reading_order": 3,
      "pixel_rect": { "x": 1780, "y": 4620, "w": 1540, "h": 1080 }
    },
    {
      "panel_id": "CH001_P03_PL04",
      "size_class": "small",
      "position": { "row": 12, "col": 8, "row_span": 3, "col_span": 4 },
      "bubble_zones": [],
      "emotional_role": "reaction",
      "reading_order": 4,
      "pixel_rect": { "x": 3380, "y": 4620, "w": 1540, "h": 1080 }
    },
    {
      "panel_id": "CH001_P03_PL05",
      "size_class": "gutter",
      "position": { "row": 15, "col": 0, "row_span": 3, "col_span": 12 },
      "bubble_zones": [],
      "emotional_role": "breath",
      "reading_order": 5,
      "pixel_rect": { "x": 180, "y": 5760, "w": 4840, "h": 1020 }
    }
  ],
  "page_turn_payoff": true,
  "page_turn_note": "Reader turns to see the garden for the first time on page 4",
  "breath_panel_present": true,
  "dialogue_density": 0.2
}
```

*Editorial note: Dominant splash of the town lane (sets setting). Three quick small reaction panels — Yuki noticing shop signs, a cat, a door. Bottom gutter breath strip — an empty flagstone path, no characters. Page turn payoff: reader turns this odd page to reveal the garden.*

### Page 4 — Opening Revelation (The Garden)

```json
{
  "page_number": 4,
  "page_type": "standard",
  "panels": [
    {
      "panel_id": "CH001_P04_PL01",
      "size_class": "full_page",
      "position": { "row": 0, "col": 0, "row_span": 18, "col_span": 12 },
      "bubble_zones": [],
      "emotional_role": "revelation",
      "reading_order": 1,
      "pixel_rect": { "x": 180, "y": 180, "w": 4840, "h": 6840 }
    }
  ],
  "page_turn_payoff": false,
  "page_turn_note": null,
  "breath_panel_present": true,
  "dialogue_density": 0.0
}
```

*Editorial note: Page 4 is the payoff for page 3's turn. Full-page garden reveal. No text. Pure visual impact. This is the chapter's emotional anchor.*

### Page 5 — Standard (First Encounter in the Garden)

```json
{
  "page_number": 5,
  "page_type": "standard",
  "panels": [
    {
      "panel_id": "CH001_P05_PL01",
      "size_class": "large",
      "position": { "row": 0, "col": 0, "row_span": 8, "col_span": 8 },
      "bubble_zones": [],
      "emotional_role": "establishing",
      "reading_order": 1,
      "pixel_rect": { "x": 180, "y": 180, "w": 3000, "h": 2880 }
    },
    {
      "panel_id": "CH001_P05_PL02",
      "size_class": "medium",
      "position": { "row": 0, "col": 8, "row_span": 8, "col_span": 4 },
      "bubble_zones": [
        { "x": 8, "y": 5, "w": 80, "h": 25, "type": "speech" }
      ],
      "emotional_role": "intimate_dialogue",
      "reading_order": 2,
      "pixel_rect": { "x": 3240, "y": 180, "w": 1780, "h": 2880 }
    },
    {
      "panel_id": "CH001_P05_PL03",
      "size_class": "medium",
      "position": { "row": 8, "col": 0, "row_span": 6, "col_span": 6 },
      "bubble_zones": [
        { "x": 10, "y": 60, "w": 75, "h": 25, "type": "speech" }
      ],
      "emotional_role": "intimate_dialogue",
      "reading_order": 3,
      "pixel_rect": { "x": 180, "y": 3120, "w": 2240, "h": 2160 }
    },
    {
      "panel_id": "CH001_P05_PL04",
      "size_class": "small",
      "position": { "row": 8, "col": 6, "row_span": 4, "col_span": 6 },
      "bubble_zones": [],
      "emotional_role": "reaction",
      "reading_order": 4,
      "pixel_rect": { "x": 2480, "y": 3120, "w": 2540, "h": 1440 }
    },
    {
      "panel_id": "CH001_P05_PL05",
      "size_class": "gutter",
      "position": { "row": 14, "col": 0, "row_span": 4, "col_span": 12 },
      "bubble_zones": [],
      "emotional_role": "breath",
      "reading_order": 5,
      "pixel_rect": { "x": 180, "y": 5460, "w": 4840, "h": 1380 }
    }
  ],
  "page_turn_payoff": false,
  "page_turn_note": null,
  "breath_panel_present": true,
  "dialogue_density": 0.4
}
```

*Editorial note: Asymmetric layout. Large panel left (garden ground level, Yuki stepping in) + tall narrow panel right (the gardener noticing her — intimate dialogue, one bubble). Lower register: medium dialogue panel (the gardener's question, Yuki's response), small reaction panel (her face — no text). Bottom gutter breath strip: close on soil and roots.*

### Page 6 — Silence Page

```json
{
  "page_number": 6,
  "page_type": "silent",
  "panels": [
    {
      "panel_id": "CH001_P06_PL01",
      "size_class": "large",
      "position": { "row": 0, "col": 0, "row_span": 9, "col_span": 12 },
      "bubble_zones": [],
      "emotional_role": "breath",
      "reading_order": 1,
      "pixel_rect": { "x": 180, "y": 180, "w": 4840, "h": 3300 }
    },
    {
      "panel_id": "CH001_P06_PL02",
      "size_class": "medium",
      "position": { "row": 9, "col": 0, "row_span": 5, "col_span": 6 },
      "bubble_zones": [],
      "emotional_role": "silence",
      "reading_order": 2,
      "pixel_rect": { "x": 180, "y": 3540, "w": 2360, "h": 1860 }
    },
    {
      "panel_id": "CH001_P06_PL03",
      "size_class": "medium",
      "position": { "row": 9, "col": 6, "row_span": 5, "col_span": 6 },
      "bubble_zones": [],
      "emotional_role": "silence",
      "reading_order": 3,
      "pixel_rect": { "x": 2600, "y": 3540, "w": 2360, "h": 1860 }
    },
    {
      "panel_id": "CH001_P06_PL04",
      "size_class": "large",
      "position": { "row": 14, "col": 0, "row_span": 4, "col_span": 12 },
      "bubble_zones": [],
      "emotional_role": "breath",
      "reading_order": 4,
      "pixel_rect": { "x": 180, "y": 5460, "w": 4840, "h": 1380 }
    }
  ],
  "page_turn_payoff": false,
  "page_turn_note": null,
  "breath_panel_present": true,
  "dialogue_density": 0.0
}
```

*Editorial note: All-silent page following dialogue introduction. Top large panel — Yuki stands alone in garden, wide shot. Two medium panels: close on her hands touching a leaf, close on the afternoon light through branches. Bottom large strip — the garden as a whole, Yuki a small figure. No speech, no SFX. Five-beat silence protocol: stillness → detail → world.*

---

## 11. STAGE MANIFEST OUTPUT

The Name Stage writes to:
```
artifacts/manga/{series}/{chapter_id}/stages/chapter_name/
├── page_layout_spec.json
├── wireframe.pdf
└── stage_manifest.json
```

`stage_manifest.json`:
```json
{
  "schema_version": "1.0.0",
  "artifact_type": "stage_manifest",
  "stage_id": "chapter_name",
  "stage_name": "Name (thumbnail layout)",
  "attempt": 1,
  "status": "approved",
  "outputs": {
    "page_layout_spec": "page_layout_spec.json",
    "wireframe": "wireframe.pdf"
  },
  "approval": {
    "method": "automated",
    "gates_passed": ["MQG-01", "MQG-02", "MQG-03", "MQG-04", "MQG-05", "MQG-06", "MQG-07", "MQG-08"],
    "timestamp": "2026-04-17T10:00:00Z"
  }
}
```

---

*SpiritualTech Systems · Name Stage Spec v1.0 · Confidential*
