# Manga Layout Agent Specification
## AI Manga Dharma System (SpiritualTech Systems)

**Version:** 1.0
**Status:** Production
**Date:** 2026-03-21

---

## 1. ROLE & BOUNDARY

The Layout Agent is the final **panel compositing stage** in the Manga Dharma pipeline. Its sole responsibility is to assemble pre-rendered, individually-generated panel images into publication-ready manga pages, respecting reading direction, page architecture, and lettering overlay specifications.

**Ownership boundaries:**
- **Layout Agent generates:** Final page layouts, bleed-safe composites, reading flow validation
- **Layout Agent does NOT generate:** Panel images (Image Gen), lettering placement decisions (Lettering Agent), visual composition (Visual Agent), text content (Chapter Writer)
- **Layout Agent does NOT modify:** Rendered panel images, lettering_spec.json contents, visual prompts, story text

This is a **composition-and-assembly** system, not a generative system.

---

## 2. PIPELINE POSITION

```
Teaching Library
    ↓
Genre Agent
    ↓
Story Architect
    ↓
Chapter Writer
    ↓
Visual Agent (generates composition_notes, panel_prompts.json)
    ↓
Image Gen (renders individual panel images)
    ↓
Lettering Agent (generates lettering_spec.json, bubble/SFX/caption placements)
    ↓
[LAYOUT AGENT] ← FINAL STAGE
    ↓
QC Agent (validates finished pages)
```

**Inputs received by Layout Agent:**
1. `rendered_panels[]` — Individual panel images from Image Gen (PNG, 300dpi)
2. `lettering_spec.json` — Bubble, SFX, caption placements from Lettering Agent
3. `composition_notes` — Panel arrangement metadata from Visual Agent
4. `page_layout_rules` — Grid systems and spacing from style_bible
5. `reading_direction` — RTL, LTR, or webtoon (from locale config)

**Output delivered to QC Agent:**
- `finished_pages[]` — Final page composites (print-ready, bleed-safe, metadata)

---

## 3. INPUTS SPECIFICATION

### 3.1 Rendered Panels Input
```json
{
  "rendered_panels": [
    {
      "panel_id": "ch03_page05_panel_02",
      "image_path": "/outputs/images/ch03_page05_panel_02.png",
      "dimensions": {"width": 2400, "height": 3200},
      "dpi": 300,
      "color_profile": "sRGB",
      "panel_position": {"x": 0, "y": 0},
      "safe_zone": {"inset": 120},
      "rendered_at": "2026-03-21T14:32:00Z"
    }
  ]
}
```

**Properties:**
- `panel_id`: Unique identifier matching lettering_spec.json references
- `image_path`: Full path to PNG (must exist before Layout Agent runs)
- `dimensions`: Pixel dimensions at 300 dpi (typical: 2400×3200 for standard panel)
- `dpi`: Resolution (300 for print, 72 for web preview)
- `safe_zone`: Inset margin where text will not overlap (managed by Lettering Agent)
- `color_profile`: sRGB for digital, CMYK for professional print

### 3.2 Lettering Spec Input
The Layout Agent receives `lettering_spec.json` containing all bubble, SFX, and caption placements:

```json
{
  "panel_id": "ch03_page05_panel_02",
  "lettering_elements": [
    {
      "element_id": "bubble_001",
      "type": "speech_bubble",
      "content": "I remember now...",
      "position": {"x": 400, "y": 600},
      "dimensions": {"width": 800, "height": 300},
      "style": "rounded_rectangular",
      "tail_direction": "bottom_left",
      "font": "Comic Sans MS",
      "font_size": 28,
      "color": "#000000",
      "z_order": 100
    },
    {
      "element_id": "sfx_001",
      "type": "sound_effect",
      "content": "ドキドキ",
      "position": {"x": 1000, "y": 200},
      "rotation": 15,
      "font_size": 48,
      "color": "#FF0000",
      "z_order": 110
    }
  ]
}
```

**Expected fields:**
- `element_id`: Unique ID within panel
- `type`: speech_bubble, narration_box, caption, sound_effect, thought_bubble
- `position`: x, y coordinates (origin at panel top-left)
- `dimensions`: width, height (if bounded box)
- `z_order`: Rendering depth (higher = rendered on top)
- All style properties (font, size, color) from Brand DNA

### 3.3 Composition Notes Input
Visual Agent provides layout metadata:

```json
{
  "page_id": "ch03_page05",
  "layout_template": "2x3_grid",
  "panels": [
    {
      "panel_id": "ch03_page05_panel_01",
      "grid_position": [0, 0],
      "page_position": {"x": 0, "y": 0},
      "type": "standard",
      "reading_order": 1
    },
    {
      "panel_id": "ch03_page05_panel_02",
      "grid_position": [1, 0],
      "page_position": {"x": 2600, "y": 0},
      "type": "standard",
      "reading_order": 2
    }
  ]
}
```

**Properties:**
- `layout_template`: Grid type (2x3, 3x2, 4-panel, irregular, etc.)
- `grid_position`: Row, column in grid (for gutter calculation)
- `page_position`: Absolute pixel position on final page
- `type`: standard, splash, silent, or breathing
- `reading_order`: Sequence number for flow validation

### 3.4 Page Layout Rules (from style_bible)
```json
{
  "page_dimensions": {"width": 5200, "height": 7200},
  "grid_systems": {
    "2x3": {"rows": 2, "columns": 3, "gutter_width": 60},
    "3x2": {"rows": 3, "columns": 2, "gutter_width": 60},
    "4-panel": {"rows": 2, "columns": 2, "gutter_width": 80},
    "splash": {"rows": 1, "columns": 1, "gutter_width": 0}
  },
  "margins": {
    "bleed": 180,
    "safe_zone": 120,
    "gutter": 60
  },
  "line_weight": 8
}
```

---

## 4. PAGE LAYOUT GRAMMAR

The Layout Agent assembles pages using **grid-based layout templates**. Each template defines panel arrangement, gutter widths, and breathing space.

### 4.1 Standard Grid Systems

#### 2×3 Grid (6 panels)
```
[Panel 1] [Panel 2] [Panel 3]
[Panel 4] [Panel 5] [Panel 6]
```
- **Typical use:** Multi-scene chapters, dialogue-heavy sequences
- **Gutter width:** 60px (standard)
- **Panel dimensions:** ~2400×3200px each (at 300dpi)
- **Page dimensions:** 5200×7200px (full bleed)

**Calculation:**
```
page_width = (panel_width × 3) + (gutter × 2) + (margin_left + margin_right)
5200 = (2400 × 3) + (60 × 2) + (180 × 2)
```

#### 3×2 Grid (6 panels, portrait emphasis)
```
[Panel 1] [Panel 2]
[Panel 3] [Panel 4]
[Panel 5] [Panel 6]
```
- **Typical use:** Vertical action sequences, emotional close-ups
- **Panel dimensions:** ~2300×2400px each
- **Gutter width:** 60px

#### 4-Panel (Yonkoma style)
```
[Panel 1] [Panel 2]
[Panel 3] [Panel 4]
```
- **Typical use:** Short-form comedy, comedic relief
- **Panel dimensions:** ~2400×3200px each
- **Gutter width:** 80px (wider for visual separation)

#### Irregular Layouts
- **Hybrid grids:** Mix standard panels with splashes
- **Asymmetric gutters:** Vary gutter width per row for pacing
- **Staggered panels:** Offset rows to create flow emphasis
- **Speech-driven layouts:** Panel sizes scale to accommodate lettering density

### 4.2 Gutter Width Rules

**Standard gutter:** 60px (for clean reading separation)
**Wide gutter:** 80px (for comedy, emphasis panels)
**Tight gutter:** 40px (for fast-paced action sequences)
**Zero gutter:** Only for splash pages or double-spreads (visual continuity)

Gutters are **always filled with page background** (typically white or paper texture).

### 4.3 Bleed & Safe Zone Calculation

**Bleed margin:** 180px on all sides (for print trimming tolerance)
**Safe zone (text):** 120px inset from panel edges (guaranteed readable area)
**Safe zone (imagery):** 140px inset (critical elements avoid this zone)

Layout Agent validates:
```
if (lettering_position.x < safe_zone_inset ||
    lettering_position.x + lettering_width > panel_width - safe_zone_inset) {
  → FLAG: Text breach detected → QC alert
}
```

### 4.4 Panel Borders

**Border style:** Solid black line, 8px weight (at 300dpi)
**Border color:** #000000 (pure black)
**Border rendering:** Rendered **outside** panel image boundaries (Layout Agent responsibility)

Border algorithm:
```
for each panel in page:
  draw_rectangle(
    x: panel.x - (border_weight / 2),
    y: panel.y - (border_weight / 2),
    width: panel.width + border_weight,
    height: panel.height + border_weight,
    stroke: 8px black,
    fill: none
  )
```

---

## 5. READING DIRECTION ENFORCEMENT

### 5.1 Right-to-Left (RTL) — Japanese Standard

**Page reading order:** Top-right → Middle-right → Bottom-right → Top-middle → … → Bottom-left

**Panel arrangement algorithm:**
```json
{
  "reading_direction": "rtl",
  "page_sequence": [1, 2, 3, 4, 5, 6],
  "grid_position_to_sequence": {
    "[0,0]": 3, "[0,1]": 2, "[0,2]": 1,
    "[1,0]": 6, "[1,1]": 5, "[1,2]": 4
  }
}
```

For 2×3 grid (RTL):
```
[3] [2] [1]
[6] [5] [4]
```

**Validation rule:** If `reading_order` sequence does not match RTL pattern, Layout Agent flags error.

**Impact on page layout:**
- Panels are physically positioned RTL (rightmost panel first in visual space)
- Reading flow arrows (if present) point RTL
- Speech balloon tails follow RTL emphasis (typically left-leaning)

### 5.2 Left-to-Right (LTR) — English/European Standard

**Page reading order:** Top-left → Middle-left → Bottom-left → Top-middle → … → Bottom-right

For 2×3 grid (LTR):
```
[1] [2] [3]
[4] [5] [6]
```

**Position calculation:**
```
x_position = grid_column × (panel_width + gutter)
y_position = grid_row × (panel_height + gutter)
```

### 5.3 Webtoon (Vertical Scroll) — Digital Vertical Stack

**Reading direction:** Top → Bottom (infinite vertical scroll)

**Layout rule:** Single column, panels stack vertically with minimal gutters (20-40px).

```json
{
  "reading_direction": "webtoon",
  "page_width": 1080,
  "panel_height_variable": true,
  "gutter_width": 30,
  "stack_order": "top_to_bottom"
}
```

**Panel dimensions (webtoon):**
- Width: 1080px (mobile-optimized)
- Height: Variable per panel (aspect ratio preserved from render)
- Gutter: 30px between panels

**Validation:** Webtoon pages must validate as single-column, no horizontal offset.

---

## 6. PAGE TYPE HANDLING

### 6.1 Standard Pages

**Definition:** Multi-panel pages following grid layouts (2×3, 3×2, 4-panel, etc.)

**Processing:**
1. Load all panels for page
2. Calculate grid positions (from composition_notes)
3. Apply gutter spacing
4. Compose panels into page canvas
5. Render panel borders
6. Apply lettering overlay
7. Export final page

**Example:** Most story pages, dialogue scenes, action sequences.

### 6.2 Splash Pages

**Definition:** Full-bleed single image, no panels, no gutters.

```json
{
  "page_type": "splash",
  "panel_count": 1,
  "grid_position": [0, 0],
  "dimensions": {
    "width": 5200,
    "height": 7200
  },
  "border": false,
  "gutter": 0
}
```

**Processing:**
1. Load single panel image (full page dimensions)
2. NO gutter calculation
3. NO panel border
4. Apply full-page lettering overlay (if any)
5. Bleed-safe margins still apply to lettering

**Typical use:** Chapter title pages, emotional climax moments, full-page action shots.

**Lettering on splash:** Captions and SFX may overlay splash pages; ensure text remains readable against artwork.

### 6.3 Double-Spread Pages

**Definition:** Two facing pages treated as single visual composition (used in print).

```json
{
  "page_type": "double_spread",
  "left_page_id": "ch03_page04",
  "right_page_id": "ch03_page05",
  "combined_width": 10400,
  "combined_height": 7200,
  "gutter_center": 600
}
```

**Processing:**
1. Load panels for both left and right pages
2. Compose left page to left canvas (x: 0 to 4900)
3. Compose right page to right canvas (x: 5500 to 10400)
4. Center gutter width: 600px (for spine/trim line)
5. Validate reading flow across both pages
6. Apply bleed safely (180px minimum on outer edges, 100px on center gutter)

**Reading direction impact:**
- RTL: Right page rendered first, left page second
- LTR: Left page rendered first, right page second

**Typical use:** Major reveals, landscape vistas, fight sequences.

### 6.4 Silent Pages

**Definition:** Panels with minimal or zero text overlay, emphasizing visual narrative.

```json
{
  "page_type": "silent",
  "silence_guard": true,
  "lettering_allowed": false,
  "breathing_panels": ["ch03_page06_panel_01", "ch03_page06_panel_02"]
}
```

**Processing:**
1. Compose page normally
2. Validate: zero lettering elements for flagged panels
3. If breathing_panels specified: apply extended gutters (120px instead of 60px)
4. Output page with breathing space

**Breathing space calculation:**
```
breathing_gutter = standard_gutter × 2 = 120px
page_height_adjusted = (panel_height × rows) + (breathing_gutter × (rows - 1))
```

**Typical use:** Moment of silence, emotional beats, action-without-dialogue.

---

## 7. TEXT OVERLAY PIPELINE

The Layout Agent receives all text placement specifications from the Lettering Agent (lettering_spec.json) and renders them onto the composed page.

### 7.1 Text Overlay Stack (Z-ordering)

**Rendering order (bottom to top):**
1. **Layer 0:** Panel images (background)
2. **Layer 1:** Panel borders (8px black lines)
3. **Layer 2:** Speech bubbles (white fill, black stroke)
4. **Layer 3:** Narration boxes (tan/cream background)
5. **Layer 4:** Captions (semi-transparent overlay)
6. **Layer 5:** Sound effects (red, bold, rotated)
7. **Layer 6:** Thought bubbles (dashed outline)

**Z-order from lettering_spec.json is preserved** (Layout Agent does not reorder).

### 7.2 Speech Bubble Rendering

**Input from lettering_spec.json:**
```json
{
  "element_id": "bubble_001",
  "type": "speech_bubble",
  "content": "こんにちは",
  "position": {"x": 400, "y": 600},
  "dimensions": {"width": 800, "height": 300},
  "style": "rounded_rectangular",
  "tail_direction": "bottom_left",
  "font": "Comic Sans MS",
  "font_size": 28,
  "font_weight": "normal",
  "color": "#000000",
  "background_color": "#FFFFFF",
  "stroke_color": "#000000",
  "stroke_width": 3,
  "z_order": 100
}
```

**Rendering algorithm:**
```
1. Draw background shape:
   - rounded_rectangular: 12px corner radius
   - oval: ellipse fill
   - rectangular: sharp corners
   - cloud: irregular bubble outline
2. Draw tail (pointer to speaker):
   - Position: specified by tail_direction
   - Tail width: 20-30px
   - Tail length: 40-60px (depending on distance to character)
3. Draw border stroke: 3px, specified color
4. Render text (centered within bubble):
   - Font: as specified
   - Size: as specified
   - Color: as specified
   - Vertical alignment: center
   - Horizontal alignment: center
   - Line wrapping: enabled (Lettering Agent pre-calculated wrapping)
5. Anti-alias edges: 2px smooth fade
```

**Bubble positioning validation:**
- Bubble must not overlap panel borders
- Bubble must not exceed safe_zone boundaries
- Bubble should have 10px minimum clearance from panel edge
- Tail must point toward speaking character (visual validation by QC)

### 7.3 Sound Effect (SFX) Rendering

**Input from lettering_spec.json:**
```json
{
  "element_id": "sfx_001",
  "type": "sound_effect",
  "content": "ドキドキ",
  "position": {"x": 1000, "y": 200},
  "font": "Impact",
  "font_size": 48,
  "font_weight": "bold",
  "color": "#FF0000",
  "rotation": 15,
  "scale": 1.2,
  "shadow_type": "drop_shadow",
  "shadow_offset": {"x": 4, "y": 4},
  "z_order": 110
}
```

**Rendering algorithm:**
```
1. Load font (Impact, bold weight)
2. Render text:
   - Size: 48pt (or as specified)
   - Color: #FF0000 (red, or as specified)
3. Apply transformation:
   - Rotation: 15° (clockwise)
   - Scale: 1.2× (20% larger)
4. Apply shadow:
   - Drop shadow: 4px right, 4px down, black, 50% opacity
5. Positioning:
   - Anchor: center (x, y is center point)
   - Place text to NOT obscure critical action
6. Anti-alias: high-quality (2px smooth)
```

**SFX weight classes (from Brand DNA):**
- **Light:** font_size 20-28pt, 0.8× scale
- **Medium:** font_size 32-40pt, 1.0× scale
- **Heavy:** font_size 48-64pt, 1.2-1.4× scale

**Typical Japanese SFX:** ドキドキ (heartbeat), ビリッ (shock), ザッ (movement)

### 7.4 Caption Rendering

**Input from lettering_spec.json:**
```json
{
  "element_id": "caption_001",
  "type": "caption",
  "content": "The next morning...",
  "position": {"x": 0, "y": 50},
  "dimensions": {"width": 5000, "height": 100},
  "background_color": "#F5F5DC",
  "background_opacity": 0.9,
  "font": "Georgia",
  "font_size": 18,
  "color": "#000000",
  "text_align": "center",
  "z_order": 105
}
```

**Rendering algorithm:**
```
1. Draw background box:
   - Color: #F5F5DC (beige)
   - Opacity: 0.9 (90% opaque)
   - Width: full width or specified
   - Height: fit content + padding
2. Draw border (optional): 1px dark gray
3. Render text:
   - Font: Georgia (serif, readable)
   - Size: 18pt
   - Color: black
   - Alignment: center
   - Vertical center: within box
4. Padding: 8-12px all sides
5. Anti-alias: standard (1px smooth)
```

**Caption positioning:** Top of page (location for scene transitions), center (for narration), or full-width (for chapter title).

---

## 8. OUTPUT — FINISHED PAGES

### 8.1 Page Output Format

**Filename:** `finished_ch{chapter:02d}_page{number:03d}.png`
**Example:** `finished_ch03_page005.png`

**Metadata structure:**
```json
{
  "finished_page": {
    "page_id": "ch03_page05",
    "chapter_number": 3,
    "page_number": 5,
    "filename": "finished_ch03_page005.png",
    "format": "PNG",
    "dimensions": {"width": 5200, "height": 7200},
    "dpi": 300,
    "color_profile": "sRGB",
    "bleed_safe": true,
    "reading_direction": "rtl",
    "page_type": "standard",
    "layout_template": "2x3",
    "composition_timestamp": "2026-03-21T14:45:30Z",
    "panels_used": ["ch03_page05_panel_01", "ch03_page05_panel_02", "ch03_page05_panel_03", "ch03_page05_panel_04", "ch03_page05_panel_05", "ch03_page05_panel_06"],
    "lettering_elements_count": 12,
    "text_legibility_score": 0.94,
    "qa_status": "pending_review"
  }
}
```

### 8.2 Output Resolution & Color Space

**Digital (Web):**
- Resolution: 96 dpi
- Color space: sRGB
- Format: PNG (lossless)
- File size: ~800KB per page

**Print (Professional):**
- Resolution: 300 dpi
- Color space: CMYK (or RGB for PDF)
- Format: PNG or PDF
- File size: ~2-3MB per page

**Mobile (Webtoon):**
- Resolution: 72 dpi
- Dimensions: 1080×(variable height)
- Format: PNG (mobile-optimized)
- File size: ~200-400KB per page

### 8.3 Metadata Output

Layout Agent outputs both images and metadata:

```json
{
  "finished_pages": [
    {
      "page_id": "ch03_page05",
      "image_path": "/outputs/finished_pages/finished_ch03_page005.png",
      "metadata": {
        "dimensions": [5200, 7200],
        "dpi": 300,
        "color_space": "sRGB",
        "page_type": "standard",
        "reading_direction": "rtl",
        "panel_count": 6,
        "text_elements": 12,
        "bleed_validated": true,
        "safe_zone_validated": true,
        "reading_flow_validated": true
      }
    }
  ],
  "composition_log": {
    "timestamp": "2026-03-21T14:45:30Z",
    "total_pages": 25,
    "total_panels": 148,
    "total_text_elements": 423,
    "errors": [],
    "warnings": [
      {
        "page_id": "ch03_page12",
        "type": "text_legibility_warning",
        "message": "SFX element 'bubble_034' has low contrast on background panel"
      }
    ]
  }
}
```

---

## 9. QUALITY GATES

Layout Agent validates all output before delivery to QC Agent.

### 9.1 Reading Flow Validation

**Gate 1: Panel sequence correctness**
```
for each page:
  if reading_direction == "rtl":
    expected_sequence = [rightmost, middle, leftmost]
    validate(actual_sequence == expected_sequence)
  elif reading_direction == "ltr":
    expected_sequence = [leftmost, middle, rightmost]
    validate(actual_sequence == expected_sequence)
  elif reading_direction == "webtoon":
    validate(single_column AND top_to_bottom)
```

**Gate 2: Reading order continuity**
```
for each page_transition:
  last_panel_of_page_N.reading_order < first_panel_of_page_N+1.reading_order
  → Ensures continuous narrative flow
```

### 9.2 Text Legibility Gates

**Gate 3: Safe zone compliance**
```
for each text_element in page:
  element_bbox = {
    x_min: position.x,
    x_max: position.x + width,
    y_min: position.y,
    y_max: position.y + height
  }

  # Validate within safe zone
  if x_min < safe_zone_inset OR x_max > (panel_width - safe_zone_inset):
    → FLAG: Safe zone breach

  # Validate text not over panel border
  if element_bbox.overlaps(panel_border):
    → FLAG: Text-border collision
```

**Gate 4: Contrast validation**
```
for each speech_bubble:
  contrast_ratio = luminance(text_color) / luminance(background_color)
  if contrast_ratio < 3.0:  # WCAG minimum
    → FLAG: Low contrast (text may be hard to read)
```

**Gate 5: Overlap detection**
```
for each pair of text_elements in same panel:
  if bounding_boxes.intersect():
    → FLAG: Text overlap detected
```

### 9.3 Bleed Safety Validation

**Gate 6: Bleed margin preservation**
```
for each panel_position:
  bleed_safe = (position.x >= bleed_margin AND
                position.y >= bleed_margin AND
                position.x + panel_width <= page_width - bleed_margin AND
                position.y + panel_height <= page_height - bleed_margin)

  if NOT bleed_safe:
    → FLAG: Panel extends into bleed zone (will be trimmed in print)
```

**Gate 7: Print-safe color validation**
```
if color_profile == "CMYK":
  for each pixel:
    validate_cmyk_range(color)
    # Ensure no out-of-gamut colors
```

### 9.4 Silent Page Validation

**Gate 8: Silence purity check**
```
for each silent_page:
  for each panel_marked_no_text:
    if text_element_detected():
      → FLAG: Silent page compromised

    # Validate breathing space
    if gutter_width < breathing_gutter_minimum:
      → FLAG: Insufficient breathing space
```

### 9.5 Double-Spread Validation

**Gate 9: Center gutter integrity**
```
if page_type == "double_spread":
  # Validate no visual elements cross spine
  if (element.x < spine_left_boundary OR
      element.x > spine_right_boundary):
    # If critical element near spine, flag for QC review
    → WARN: Element near center gutter (may be lost in binding)
```

---

## 10. SYSTEM PROMPT

```
You are the Layout Agent for the AI Manga Dharma System (SpiritualTech Systems).

Your role: Compose individual panel images into finished manga pages, respecting
all reading direction, layout grammar, and text overlay specifications.

CORE RESPONSIBILITIES:
1. Assemble panel images from Image Gen into page layouts
2. Apply lettering overlay specifications from Lettering Agent
3. Enforce reading direction (RTL/LTR/webtoon)
4. Manage gutter spacing, bleed margins, safe zones
5. Validate all output against quality gates
6. Output publication-ready pages with metadata

WHAT YOU DO:
✓ Compose panels into pages using grid systems
✓ Render speech bubbles, SFX, captions from lettering_spec.json
✓ Calculate positions and spacing (gutters, margins, safe zones)
✓ Apply borders, shadows, anti-aliasing
✓ Validate reading flow, text legibility, bleed safety
✓ Generate finished pages (PNG, 300dpi for print)

WHAT YOU DO NOT DO:
✗ Generate panel images (Image Gen does this)
✗ Decide lettering placement (Lettering Agent does this)
✗ Modify visual composition (Visual Agent did this)
✗ Rewrite or edit text content
✗ Make style decisions (Brand DNA specifies all styling)

INPUT CONTRACTS:
- rendered_panels[]: Pre-rendered panel images (PNG, 300dpi)
- lettering_spec.json: All bubble, SFX, caption placements (from Lettering Agent)
- composition_notes: Panel arrangement metadata (from Visual Agent)
- page_layout_rules: Grid templates and spacing (from style_bible)
- reading_direction: "rtl" | "ltr" | "webtoon" (from locale config)

OUTPUT CONTRACT:
- finished_pages[]: Publication-ready page images (PNG, metadata JSON)
- composition_log: Validation results and warnings
- All pages must pass quality gates before delivery to QC Agent

READING DIRECTION RULES:
- RTL (Japanese): Panels flow right → middle → left (panel 3,2,1 then 6,5,4)
- LTR (English): Panels flow left → middle → right (panel 1,2,3 then 4,5,6)
- Webtoon (Digital): Single column, top → bottom infinite scroll

PAGE TYPES:
- Standard: Multi-panel grids (2x3, 3x2, 4-panel, irregular)
- Splash: Full-bleed single image (no borders, no gutters)
- Double-spread: Two facing pages (spine gutter 600px minimum)
- Silent: Minimal text, breathing space emphasis (gutters 2× normal)

GRID LAYOUT CALCULATOR:
- Panel dimensions (at 300dpi): typically 2400×3200px per panel
- Gutter width: 60px standard, 80px wide, 40px tight
- Bleed margin: 180px on all sides (print safety)
- Safe zone (text): 120px inset from panel edges
- Page size (2×3 at 300dpi): 5200×7200px total

TEXT OVERLAY Z-ORDERING (bottom to top):
1. Panel images
2. Panel borders (8px black lines)
3. Speech bubbles
4. Narration boxes
5. Captions
6. Sound effects (SFX)
7. Thought bubbles

QUALITY GATES (all must pass):
1. Reading flow correctness (sequence matches reading_direction)
2. Safe zone compliance (text within safe zones)
3. Contrast validation (minimum 3.0:1 ratio)
4. Overlap detection (no text collisions)
5. Bleed safety (panels within bleed margins)
6. Silent page validation (zero text on flagged panels)
7. Reading order continuity (sequential page flow)

ERROR HANDLING:
- Bleed breach: FLAG as error (will be cut off in printing)
- Safe zone breach: FLAG as error (text may be unreadable)
- Text overlap: FLAG as warning (may be acceptable if intentional)
- Low contrast: FLAG as warning (legibility at risk)
- Silent page compromise: FLAG as error (visual intent violated)

OUTPUT FORMAT:
- Filename: finished_ch{chapter:02d}_page{number:03d}.png
- Resolution: 300dpi for print, 96dpi for web
- Color space: sRGB (web) or CMYK (professional print)
- Format: PNG (lossless)
- Metadata: JSON with page info, validation results, warnings

Remember: You are the final assembly stage. Your output is publication-ready.
Every pixel, every gutter, every text element will be seen by readers.
Validate ruthlessly. Flag everything questionable. Perfection is the baseline.
```

---

**SpiritualTech Systems · Layout Agent Spec v1.0 · Confidential**
