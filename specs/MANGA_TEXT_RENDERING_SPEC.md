# Manga Text Rendering Specification
## AI Manga Dharma System (SpiritualTech Systems)

**Version:** 1.0
**Status:** Production
**Date:** 2026-03-21

---

## 1. CORE PRINCIPLE

**"Do NOT generate readable text inside AI panel images."**

All dialogue, narration, captions, and sound effects are **rendered as overlay** on top of pre-generated panel artwork. Text never flows from the image generator. Text is always composited in post-production by the Lettering Agent and Layout Agent, enabling:

- Precise placement control (avoiding character faces, action zones)
- Easy translation/localization (swap text, keep artwork)
- Brand DNA compliance (consistent fonts, bubble styles, SFX aesthetics)
- Clarity-mode overrides (optimize for readability vs. manga authenticity per brand)

This specification defines the **production pipeline for text overlay rendering**, from Script input through final QC validation.

---

## 2. PIPELINE STAGES

```
Script (from Chapter Writer)
    ↓
[BALLOON PLANNER] ← Decides bubble type + position per panel
    ↓
Compositor ← Z-ordering, bubble rendering, SFX placement
    ↓
Overlay Renderer ← Anti-aliasing, final text rasterization
    ↓
QA Validation ← Legibility, overlap, silence purity checks
    ↓
lettering_spec.json (Output to Layout Agent)
```

**Input:** Script containing dialogue, narration, SFX cues, and panel metadata.
**Output:** `lettering_spec.json` — Complete bubble, SFX, caption placement specifications ready for Layout Agent.

---

## 3. BALLOON PLANNER STAGE

The Balloon Planner is a **dedicated decision layer** that determines what type of bubble to use and where to place it on each panel, independent of styling decisions.

### 3.1 Balloon Planner Input

```json
{
  "panel_id": "ch03_page05_panel_02",
  "panel_dimensions": {"width": 2400, "height": 3200},
  "safe_zone": {"inset": 120},
  "script_elements": [
    {
      "line_id": "line_001",
      "type": "dialogue",
      "speaker": "Yuki",
      "content": "I remember now...",
      "emotion": "epiphany"
    },
    {
      "line_id": "line_002",
      "type": "sound_effect",
      "content": "ドキドキ",
      "intensity": "medium"
    }
  ],
  "composition_notes": {
    "character_zones": [
      {
        "character": "Yuki",
        "bbox": {"x": 300, "y": 800, "width": 800, "height": 1600}
      }
    ],
    "action_zones": [
      {
        "description": "hands clasping",
        "bbox": {"x": 600, "y": 1200, "width": 600, "height": 400}
      }
    ],
    "empty_zones": [
      {
        "region": "top_left",
        "bbox": {"x": 0, "y": 0, "width": 500, "height": 600}
      }
    ]
  }
}
```

**Inputs:**
- `panel_dimensions`: Width, height of rendered panel
- `safe_zone`: Safe text placement area (inset from edges)
- `script_elements`: Dialogue, SFX, narration cues
- `composition_notes`: Character location, action zones, visual emphasis areas
- `speaker` (for dialogue): Identifies who is speaking (used for tail direction)

### 3.2 Balloon Planner Algorithm

**For each dialogue line:**

```
1. IDENTIFY SPEAKER LOCATION
   - Find speaker in composition_notes.character_zones
   - Calculate speaker position (bbox center)

2. DETERMINE BUBBLE TYPE
   - emotion == "normal" → speech_bubble (rounded rectangle)
   - emotion == "epiphany" / "realization" → star_burst or diamond bubble
   - emotion == "whisper" / "quiet" → thin-lined speech_bubble
   - emotion == "yell" / "shout" → thick-lined angular bubble
   - speaker == "narration" → narration_box (rectangular, tan background)
   - speaker == "internal_thought" → thought_bubble (cloud outline)

3. SELECT PLACEMENT ZONE
   - Priority 1: empty_zones (preferred, least visual clutter)
   - Priority 2: top of panel (standard reading position)
   - Priority 3: beside speaker (if speaker in center/bottom)
   - Priority 4: opposite speaker (if panel composition allows)

4. AVOID COLLISION ZONES
   - Reject positions that intersect character_zones
   - Reject positions that intersect action_zones
   - Minimum clearance: 40px from character face
   - Minimum clearance: 20px from action zone

5. CALCULATE BUBBLE DIMENSIONS
   - text_length = len(content_text)
   - base_width = text_length × 8 + 40  // 8px per character + padding
   - base_height = estimated_wrapped_height + padding
   - Apply min/max constraints:
     - min_width: 200px
     - max_width: safe_zone.width - 40px
     - min_height: 80px

6. POSITION TAIL (POINTER)
   - tail_direction = direction_from_bubble_to_speaker
   - if speaker_x < bubble_x: tail_direction = "left"
   - if speaker_x > bubble_x: tail_direction = "right"
   - if speaker_y > bubble_y: tail_direction = "bottom"

7. OUTPUT PLACEMENT SPEC
   - bubble_id, type, content, position, dimensions, tail_direction
```

### 3.3 Balloon Planner Output

```json
{
  "panel_id": "ch03_page05_panel_02",
  "balloon_plan": [
    {
      "balloon_id": "balloon_001",
      "type": "speech_bubble",
      "speaker": "Yuki",
      "content": "I remember now...",
      "position": {"x": 200, "y": 150},
      "dimensions": {"width": 800, "height": 300},
      "bubble_shape": "rounded_rectangular",
      "tail_direction": "bottom_left",
      "placement_reason": "empty_zone_top_left",
      "collision_check": "passed",
      "safe_zone_status": "within_safe_zone"
    },
    {
      "sfx_id": "sfx_001",
      "type": "sound_effect",
      "content": "ドキドキ",
      "intensity": "medium",
      "position": {"x": 1400, "y": 400},
      "placement_reason": "action_emphasis_right_side",
      "collision_check": "passed"
    }
  ]
}
```

**Decision output includes:**
- `balloon_id`: Unique ID
- `type`: speech_bubble, thought_bubble, narration_box, sound_effect
- `position`: Calculated x, y coordinates
- `dimensions`: Width, height for text bounding box
- `bubble_shape`: rounded_rectangular, oval, cloud, rectangular, starburst
- `tail_direction`: bottom_left, bottom_right, left, right, top (for tail orientation)
- `placement_reason`: Why this location was chosen (for QC auditability)

---

## 4. BRAND DNA — STYLING (NOT PLACEMENT)

Brand DNA defines **all styling attributes** but **does NOT determine placement logic**. The Balloon Planner reads Brand DNA only for style references.

### 4.1 Brand DNA Structure

```json
{
  "brand_name": "Zen Garden",
  "text_rendering": {
    "clarity_mode": true,
    "manga_authentic_override": false,
    "speech_bubble_style": {
      "shape": "rounded_rectangular",
      "corner_radius": 12,
      "stroke_color": "#000000",
      "stroke_width": 3,
      "fill_color": "#FFFFFF",
      "fill_opacity": 1.0,
      "shadow_color": "#000000",
      "shadow_opacity": 0.2,
      "shadow_offset": {"x": 3, "y": 3}
    },
    "narration_box_style": {
      "shape": "rectangular",
      "stroke_color": "#000000",
      "stroke_width": 2,
      "fill_color": "#F5F5DC",
      "fill_opacity": 0.95,
      "text_align": "center"
    },
    "thought_bubble_style": {
      "shape": "cloud",
      "stroke_color": "#000000",
      "stroke_width": 2,
      "stroke_style": "dashed",
      "fill_color": "#FFFFFF",
      "fill_opacity": 0.9
    },
    "sfx_style_set": {
      "light": {
        "font_size_range": [20, 28],
        "font_weight": "normal",
        "scale_range": [0.8, 0.9]
      },
      "medium": {
        "font_size_range": [32, 40],
        "font_weight": "bold",
        "scale_range": [1.0, 1.1]
      },
      "heavy": {
        "font_size_range": [48, 64],
        "font_weight": "bold",
        "scale_range": [1.2, 1.4]
      }
    },
    "font_family": "Comic Sans MS",
    "font_family_fallback": ["Arial", "Helvetica"],
    "font_size_range": [18, 32],
    "font_size_by_emotion": {
      "normal": 24,
      "quiet": 18,
      "shout": 32,
      "whisper": 16
    },
    "text_color": "#000000",
    "line_height_multiplier": 1.3
  }
}
```

**Brand DNA controls:**
- `speech_bubble_style`: Shape, colors, stroke, shadow (styling only)
- `narration_box_style`: Rectangular box appearance
- `thought_bubble_style`: Cloud outline appearance
- `sfx_style_set`: Weight classes (light/medium/heavy)
- `font_family`: Primary font (Comic Sans MS, Georgia, etc.)
- `font_size_range`: 18-32pt typical range
- `text_color`: Dialogue color (always dark for contrast)

**Balloon Planner reads Brand DNA for:**
- Default bubble shape (but can override per emotion in script)
- Font family and size range
- Text color and styling

**Balloon Planner does NOT read from Brand DNA:**
- Placement rules (those are algorithm-based)
- Position on panel (that's determined by composition_notes)
- Collision avoidance (that's safe-zone driven)

### 4.2 Clarity Mode vs. Manga Authentic Mode

**Clarity Mode** (default for all 30 therapeutic brands):
- Prioritize readability above authenticity
- Large fonts (28-32pt baseline)
- High-contrast backgrounds (white bubbles, no transparency)
- Minimal rotation on SFX
- Ample spacing between bubbles
- Bubble borders: 3px solid (clear definition)

**Manga Authentic Mode** (optional per-brand override):
- Balance authenticity with readability
- Medium fonts (22-26pt baseline)
- Semi-transparent bubbles possible
- SFX rotation: 15-25° acceptable
- Tighter spacing allowed
- Bubble borders: 2px smooth

**Mode selection (from Brand DNA):**
```json
{
  "clarity_mode": true,
  "manga_authentic_override": false
}
```

**Balloon Planner reads mode:**
```
if brand_dna.clarity_mode AND NOT brand_dna.manga_authentic_override:
  font_size_baseline = 28  // larger for clarity
  bubble_border_width = 3  // thicker for definition
  sfx_max_rotation = 5     // minimal rotation
  bubble_opacity = 1.0     // fully opaque
else:
  font_size_baseline = 24  // moderate
  bubble_border_width = 2  // standard
  sfx_max_rotation = 20    // allows artistic rotation
  bubble_opacity = 0.9     // slight transparency OK
```

---

## 5. COMPOSITOR RULES

The Compositor takes the balloon plan from the Balloon Planner and applies Brand DNA styling to generate the complete lettering specification.

### 5.1 Z-Ordering Rules

All elements are rendered in strict z-order (bottom to top):

```
Layer 0: Panel image (background)
Layer 1: Panel borders (8px black lines)
  └─ Rendered by Layout Agent, not Compositor

Layer 2: Speech bubbles (z_order 100-109)
  ├─ Background fill: solid white
  ├─ Stroke: 3px black outline
  └─ Text: black, centered

Layer 3: Narration boxes (z_order 110-119)
  ├─ Background fill: tan/cream (#F5F5DC)
  ├─ Stroke: 2px black outline
  └─ Text: black, centered, serif font

Layer 4: Captions (z_order 120-129)
  ├─ Background: semi-transparent overlay
  ├─ Text: center-aligned, readable

Layer 5: Sound effects / SFX (z_order 130-139)
  ├─ Text only (no background fill)
  ├─ Color: red, bold, possibly rotated
  └─ Shadows: drop shadow for depth

Layer 6: Thought bubbles (z_order 140-149)
  ├─ Outline: dashed or dotted
  ├─ Fill: transparent or white
  └─ Text: inside outline
```

**Z-order assignment algorithm:**
```
z_order = {
  speech_bubble: 100,
  narration_box: 110,
  caption: 120,
  sound_effect: 130,
  thought_bubble: 140
}

# Apply offset for reading order (RTL/LTR)
if reading_direction == "rtl":
  z_order += (panel_index_from_right * 5)
elif reading_direction == "ltr":
  z_order += (panel_index_from_left * 5)
```

This ensures that in RTL, rightmost panel bubbles render behind (lower z) than leftmost, maintaining visual hierarchy.

### 5.2 Bubble Rendering Rules

**For each speech_bubble in balloon_plan:**

```
1. INSTANTIATE BUBBLE OBJECT
   from brand_dna.speech_bubble_style import:
     shape, stroke_color, stroke_width, fill_color, fill_opacity,
     shadow_color, shadow_opacity, shadow_offset

2. APPLY BALLOON PLAN DECISIONS
   position (x, y) from balloon_plan
   dimensions (width, height) from balloon_plan
   tail_direction from balloon_plan
   content (text) from script

3. RENDER BACKGROUND SHAPE
   shape_type = brand_dna.speech_bubble_style.shape
     // "rounded_rectangular", "oval", "cloud", "rectangular"
   if shape_type == "rounded_rectangular":
     corner_radius = 12  // px
   draw_shape(position, dimensions, fill_color, fill_opacity)

4. RENDER TAIL (POINTER)
   tail_length = calculate_tail_length(speaker_position, bubble_position)
   tail_width = 20-30px
   tail_direction = from balloon_plan
   draw_tail_polygon(bubble_position, tail_direction, tail_length, tail_width)

5. RENDER BORDER STROKE
   stroke_color = brand_dna.speech_bubble_style.stroke_color  // #000000
   stroke_width = brand_dna.speech_bubble_style.stroke_width  // 3px
   draw_stroke(shape, stroke_width, stroke_color)

6. APPLY SHADOW (OPTIONAL)
   shadow_opacity = brand_dna.speech_bubble_style.shadow_opacity
   if shadow_opacity > 0:
     offset_x = shadow_offset.x  // typically 3px
     offset_y = shadow_offset.y  // typically 3px
     draw_drop_shadow(offset_x, offset_y, shadow_color, shadow_opacity)

7. RENDER TEXT INSIDE BUBBLE
   font = brand_dna.font_family  // "Comic Sans MS"
   font_size = calculate_font_size(content_length, bubble_dimensions)
   text_color = brand_dna.text_color  // #000000
   line_height = brand_dna.line_height_multiplier × font_size

   # Text wrapping (pre-calculated by Balloon Planner)
   wrapped_text = balloon_plan.wrapped_text

   # Vertical & horizontal centering
   text_x = bubble_center_x
   text_y = bubble_center_y
   text_align = "center"
   vertical_align = "middle"

   render_text(wrapped_text, text_x, text_y, font, font_size,
               text_color, text_align, vertical_align)

8. APPLY TEXT ANTI-ALIASING
   anti_alias_strength = 2  // pixels of smooth fade
```

### 5.3 Narration Box Rendering

**For each narration_box in balloon_plan:**

```
1. INSTANTIATE NARRATION BOX
   from brand_dna.narration_box_style import:
     shape, stroke_color, stroke_width, fill_color, fill_opacity

2. RENDER BACKGROUND BOX
   shape = "rectangular" (always)
   fill_color = #F5F5DC  (tan/cream)
   fill_opacity = 0.95   (mostly opaque)
   draw_rectangle(position, dimensions, fill_color, fill_opacity)

3. RENDER BORDER
   stroke_color = #000000
   stroke_width = 2px
   draw_stroke(shape, stroke_width, stroke_color)

4. RENDER TEXT
   font = brand_dna.font_family  // Serif font (Georgia)
   font_size = 18-20pt  // smaller than dialogue
   text_color = #000000
   text_align = "center"
   content = narration text (from script)
   render_text(content, text_x, text_y, font, font_size,
               text_color, text_align)

5. PADDING
   padding_x = 12px
   padding_y = 8px
   (Interior text has padding from box edge)
```

### 5.4 Caption Rendering

**For each caption in balloon_plan:**

```
1. INSTANTIATE CAPTION
   position, dimensions from balloon_plan
   content = caption text (scene transition, narration)

2. RENDER BACKGROUND (OPTIONAL)
   background_color = #F5F5DC
   background_opacity = 0.85  (semi-transparent)
   draw_rectangle(position, dimensions, background_color, background_opacity)

3. RENDER TEXT
   font = brand_dna.font_family
   font_size = 16-18pt
   text_color = #000000
   text_align = "center"
   render_text(content, center_x, center_y, font, font_size,
               text_color, text_align)

4. OPTIONAL: BORDER
   stroke_color = #999999 (light gray)
   stroke_width = 1px
   (Light border for definition, not mandatory)
```

---

## 6. OVERLAY RENDERER

The Overlay Renderer takes the complete specification and applies final rasterization, anti-aliasing, and production quality standards.

### 6.1 Anti-Aliasing & Font Rendering

**Font rendering engine:**
- Use subpixel anti-aliasing (3× oversampling)
- Hinting: enabled for clarity
- Kerning: enabled for proportional fonts
- Ligatures: enabled (if font supports)

**Anti-aliasing configuration:**
```json
{
  "anti_alias_method": "subpixel",
  "oversample_factor": 3,
  "font_hinting": "enabled",
  "kerning": "enabled",
  "edge_quality": "smooth",
  "edge_fade_pixels": 2
}
```

**Text edge quality:**
```
Oversample by 3×:
  1. Render text at 3× resolution (e.g., 2400px → 7200px)
  2. Apply font hinting and kerning at high resolution
  3. Downsample to target resolution (300dpi)
  4. Apply 2px edge fade for smooth antialiasing
  5. Result: crisp, readable text with smooth edges
```

### 6.2 Bubble Shape Rendering

**Rounded rectangle (most common):**
```
bezier_curve(corner_radius = 12px)
  // Smooth curves at all four corners

Path:
  Move to (x + radius, y)
  Line to (x + width - radius, y)
  Curve to (x + width, y + radius)
  Line to (x + width, y + height - radius)
  Curve to (x + width - radius, y + height)
  Line to (x + radius, y + height)
  Curve to (x, y + height - radius)
  Line to (x, y + radius)
  Curve to (x + radius, y)
```

**Oval bubble:**
```
ellipse(cx = bubble_center_x, cy = bubble_center_y,
        rx = bubble_width / 2, ry = bubble_height / 2)
```

**Cloud bubble (thought):**
```
// Circular bumps arranged in cloud pattern
bump_radius = 80px
bumps = [
  (cx - 150, cy),
  (cx - 80, cy - 100),
  (cx + 80, cy - 100),
  (cx + 150, cy),
  (cx + 80, cy + 100),
  (cx - 80, cy + 100)
]

for each bump:
  draw_circle(bump_center, bump_radius)
  union all circles to create cloud shape
```

### 6.3 Shadow Rendering

**Drop shadow:**
```
1. Create shadow layer (offset by shadow_offset)
2. Gaussian blur: 4px radius
3. Shadow color: #000000 (black)
4. Shadow opacity: 0.2-0.3 (20-30%)
5. Composite: shadow layer behind bubble layer
```

**Shadow example:**
```
shadow_offset = {"x": 3, "y": 3}
shadow_blur = 4px
shadow_opacity = 0.2

// Render process:
1. Render bubble to shadow_layer, offset by (3, 3)
2. Apply gaussian_blur(4px) to shadow_layer
3. Set opacity of shadow_layer to 0.2
4. Composite shadow_layer below main_layer
5. Composite main_layer on top
```

### 6.4 Production Quality Output

**Final output specifications:**
```json
{
  "output_resolution": 300,
  "output_dpi": 300,
  "color_space": "sRGB",
  "color_depth": "8-bit RGB",
  "compression": "PNG lossless",
  "file_format": "PNG",
  "quality_checkpoints": {
    "text_sharpness": "WCAG AA compliant",
    "edge_smoothness": "2px fade applied",
    "color_accuracy": "sRGB ±2% Delta-E",
    "shadow_quality": "smooth gaussian blur"
  }
}
```

---

## 7. READING DIRECTION HANDLING

### 7.1 Right-to-Left (RTL) — Japanese

**Page layout (RTL):**
```
Panel reading order: [1, 2, 3] in visual RTL arrangement
  [3] [2] [1]
  [6] [5] [4]
```

**Balloon placement implications:**
- Rightmost panels render first (lower z_order)
- Leftmost panels render last (higher z_order)
- Tail direction: typically points toward left (toward next-read panel)

**Algorithm (RTL):**
```
for panel in page_panels_in_rtl_order:
  z_order_base = {speech_bubble: 100, narration: 110, sfx: 130}
  z_order_offset = (panel.reading_order - 1) × 5
  z_order_final = z_order_base + z_order_offset

  // In RTL, rightmost (first-read) panel has lower z_order
  // leftmost (last-read) panel has higher z_order
```

**RTL text direction:** Text still reads left-to-right within bubbles (only page layout is RTL).

### 7.2 Left-to-Right (LTR) — English

**Page layout (LTR):**
```
Panel reading order: [1, 2, 3] in visual LTR arrangement
  [1] [2] [3]
  [4] [5] [6]
```

**Balloon placement implications:**
- Leftmost panels render first (lower z_order)
- Rightmost panels render last (higher z_order)
- Tail direction: typically points toward right (toward next-read panel)

**Algorithm (LTR):**
```
for panel in page_panels_in_ltr_order:
  z_order_base = {speech_bubble: 100, narration: 110, sfx: 130}
  z_order_offset = (panel.reading_order - 1) × 5
  z_order_final = z_order_base + z_order_offset

  // In LTR, leftmost (first-read) panel has lower z_order
  // rightmost (last-read) panel has higher z_order
```

### 7.3 Webtoon (Vertical Scroll) — Digital

**Vertical stacking:**
```
[Panel 1]
[Panel 2]
[Panel 3]
[Panel 4]
... (infinite vertical scroll)
```

**Balloon placement implications:**
- No left-right directionality
- Panels stack vertically (top-to-bottom)
- Tail direction: typically points upward (toward character above) or downward (toward character below)

**Algorithm (Webtoon):**
```
for panel in webtoon_panels_top_to_bottom:
  z_order_base = {speech_bubble: 100, narration: 110, sfx: 130}
  // No offset needed; each panel stands alone
  z_order_final = z_order_base + (panel.vertical_position × 0.1)
```

**Webtoon considerations:**
- Mobile optimized (1080px width)
- Variable panel height
- Single-column layout
- Gutter spacing: 20-40px between panels

---

## 8. SOUND EFFECT (SFX) RENDERING

### 8.1 SFX Integration Rules

**Integrated SFX:** Rendered directly as overlay text (no background box).

**SFX placement logic:**
- Avoid character faces: minimum 80px clearance
- Avoid action zones: minimum 60px clearance
- Favor empty spaces: top-left, top-right, bottom corners
- Accent action: position SFX near action (e.g., "ビリッ" near sparks)

**SFX types:**
```
Light SFX: Small, subtle sound effects
  └─ "ペタッ" (landing sound), "すうっ" (breathing)
  └─ Font size: 20-28pt
  └─ Scale: 0.8-0.9×
  └─ Rotation: 0-5°

Medium SFX: Standard sound effects
  └─ "ドキドキ" (heartbeat), "ザッ" (movement)
  └─ Font size: 32-40pt
  └─ Scale: 1.0-1.1×
  └─ Rotation: 5-15°

Heavy SFX: Dramatic, impactful sounds
  └─ "ビリッ" (explosion), "ゴアッ" (impact)
  └─ Font size: 48-64pt
  └─ Scale: 1.2-1.4×
  └─ Rotation: 10-25°
```

### 8.2 SFX Rendering Algorithm

**For each SFX element in balloon_plan:**

```
1. LOAD FONT & CONTENT
   font = brand_dna.font_family (or specialized SFX font)
   content = sfx_text (e.g., "ドキドキ")
   intensity = balloon_plan.sfx_intensity ("light", "medium", "heavy")

2. DETERMINE SIZE & WEIGHT
   if intensity == "light":
     font_size = 24pt
     font_weight = "normal"
     scale = 0.85
     rotation = 0
   elif intensity == "medium":
     font_size = 36pt
     font_weight = "bold"
     scale = 1.0
     rotation = 10
   elif intensity == "heavy":
     font_size = 56pt
     font_weight = "bold"
     scale = 1.3
     rotation = 15

3. APPLY COLOR
   color = brand_dna.sfx_color  // typically #FF0000 (red)
   opacity = 1.0  // fully opaque

4. APPLY TRANSFORMATION
   rotation = rotation (degrees, clockwise)
   scale = scale (1.0 = 100%)
   skew = 0  // optional italic effect (5-10°)

5. APPLY SHADOW
   shadow_type = "drop_shadow"
   shadow_offset = {"x": 4, "y": 4}
   shadow_color = #000000
   shadow_opacity = 0.3

6. POSITION SFX
   position_x = balloon_plan.position.x
   position_y = balloon_plan.position.y
   anchor_point = "center"  // (x, y) is center of text

7. RENDER TEXT
   render_text(content, position_x, position_y,
               font, font_size, font_weight,
               color, opacity, rotation, scale, shadow)

8. ANTI-ALIAS
   anti_alias_strength = 2px smooth fade
```

### 8.3 Multi-SFX per Panel

**Multiple SFX example:**
```json
{
  "panel_id": "ch03_page05_panel_03",
  "sfx_elements": [
    {
      "sfx_id": "sfx_001",
      "type": "sound_effect",
      "content": "ドキドキ",
      "intensity": "medium",
      "position": {"x": 1200, "y": 500},
      "z_order": 130
    },
    {
      "sfx_id": "sfx_002",
      "type": "sound_effect",
      "content": "ビリッ",
      "intensity": "heavy",
      "position": {"x": 800, "y": 1800},
      "z_order": 131
    }
  ]
}
```

**Z-order for multiple SFX:**
- First SFX: z_order 130
- Second SFX: z_order 131
- Third SFX: z_order 132
- (Increment z_order to ensure proper layering)

---

## 9. SILENCE OVERLAY RULES

**Core rule:** Zero overlay on explicitly marked silent panels; reduced overlay on silence_guard panels.

### 9.1 Silent Panel Definition

```json
{
  "panel_id": "ch03_page07_panel_02",
  "page_type": "silent",
  "lettering_allowed": false,
  "purpose": "emotional_silence"
}
```

**Silent page characteristics:**
- **Zero text overlay:** No speech bubbles, no SFX, no captions
- **Visual emphasis:** Wide gutters (120px instead of 60px) for breathing space
- **Extended silence:** 2-4 silent panels per chapter (typical)

### 9.2 Silence Guard Panels

**Silence guard** (optional reduced lettering):
```json
{
  "panel_id": "ch03_page07_panel_01",
  "silence_guard": true,
  "lettering_minimal": true
}
```

**Silence guard constraints:**
- Maximum 1 dialogue bubble per panel
- No SFX (only optional narration)
- Reduced font size (20-22pt)
- Text placement: edges only (top or bottom)

### 9.3 Silence Validation

**QC Gate: Silence purity**
```
for each panel_marked_silent:
  if text_elements_detected():
    → ERROR: Silent panel compromised

  if gutter_width < breathing_minimum:
    → ERROR: Insufficient breathing space (need 120px)

  → PASS: Panel is visually silent
```

---

## 10. MULTILINGUAL RENDERING

### 10.1 Locale-Specific Fonts

**Font mapping by locale:**
```json
{
  "locale_fonts": {
    "ja": {
      "primary": "Hiragino Maru Gothic Pro",
      "fallback": ["Yu Gothic", "Noto Sans JP"]
    },
    "en": {
      "primary": "Comic Sans MS",
      "fallback": ["Arial", "Helvetica"]
    },
    "ko": {
      "primary": "Noto Sans CJK KR",
      "fallback": ["Noto Sans KR"]
    },
    "zh": {
      "primary": "Source Han Sans SC",
      "fallback": ["Noto Sans CJK SC"]
    }
  }
}
```

**Font selection algorithm:**
```
for each text_element:
  target_locale = element.locale  // from composition config

  if brand_dna.font_family available in target_locale:
    use brand_dna.font_family
  else:
    use locale_fonts[target_locale].primary
    if primary not available:
      use locale_fonts[target_locale].fallback[0]
```

### 10.2 Text Direction Overrides

**Bidirectional text handling:**
```json
{
  "element_id": "bubble_001",
  "content": "Hello world",
  "locale": "en",
  "text_direction": "ltr"
}
```

**Text direction rules:**
- Japanese (ja): Left-to-right (horizontal writing) or top-to-bottom (vertical writing, rare)
- English (en): Left-to-right
- Arabic (ar): Right-to-left
- Hebrew (he): Right-to-left

**Default directions:**
```
"ja", "en", "ko", "zh" → "ltr" (horizontal)
"ar", "he" → "rtl"
```

### 10.3 Bubble Resizing for Multilingual Text

**Text expansion factor by language:**
```
English (base): 1.0×
Japanese: 0.8× (characters more compact)
German: 1.3× (tends to expand)
Russian: 1.15× (moderately expands)
Arabic: 1.2× (requires space for diacritics)
```

**Dynamic bubble resizing:**
```
for each translated_text:
  expansion_factor = language_expansion_map[target_language]
  new_width = original_bubble_width × expansion_factor

  if new_width > max_bubble_width:
    → Reduce font size incrementally until fits
    → If still oversized: FLAG for manual review
```

---

## 11. ANTI-ALIASING & PRODUCTION QUALITY

### 11.1 Font Rendering Quality Standards

**Quality checklist:**
```
✓ Subpixel anti-aliasing enabled (3× oversampling)
✓ Font hinting: enabled (for clarity at small sizes)
✓ Kerning: enabled (proportional spacing)
✓ Ligatures: enabled (if font supports)
✓ Text rendering DPI: 300dpi (print standard)
✓ Color space: sRGB (8-bit RGB)
✓ Edge smoothing: 2px fade applied
✓ Shadow quality: Gaussian blur (4px radius)
```

### 11.2 Contrast Validation

**WCAG AA compliance (minimum 3:1 ratio):**

```
contrast_ratio = luminance(text_color) / luminance(background_color)

for each text_element:
  if contrast_ratio < 3.0:
    → FLAG: Low contrast warning (hard to read)

  if contrast_ratio < 4.5:
    → FLAG: Poor contrast warning (WCAG AAA fails)

  if contrast_ratio >= 7.0:
    → PASS: Excellent contrast
```

**Common contrast checks:**
```
Black text on white: ratio ~20:1 ✓ (excellent)
Black text on light gray: ratio ~3.5:1 ✓ (good)
Dark gray text on white: ratio ~2.5:1 ✗ (insufficient)
Red text on white: ratio ~2.8:1 ✗ (insufficient)
```

### 11.3 Output Validation

**File quality checks:**
```json
{
  "output_validation": {
    "file_format": "PNG",
    "resolution": 300,
    "color_space": "sRGB",
    "color_depth": "8-bit RGB",
    "file_size_estimate": "1.5-2.5MB per page",
    "compression": "PNG lossless",
    "metadata_embedded": true,
    "checksum_validation": true
  }
}
```

---

## 12. QC GATES

All text rendering output must pass quality gates before delivery to Layout Agent.

### 12.1 Text Legibility Gate

```
for each text_element:
  1. Font size minimum: 16pt (readable at 300dpi)
  2. Contrast ratio: ≥ 3.0:1 (WCAG AA)
  3. Font family: Not decorative (readable fonts only)
  4. Text-background clearance: ≥ 8px padding

  if all checks pass:
    → LEGIBLE
  else:
    → FLAG for manual review or resizing
```

### 12.2 Overlap Detection Gate

```
for each panel:
  for each pair of text_elements:
    if bounding_boxes.intersect():
      → FLAG: Text overlap detected

      // Acceptable overlaps:
      - SFX intentionally over bubbles (small SFX OK)
      - Shadows may overlap (by design)

      // Unacceptable overlaps:
      - Bubble over bubble
      - Caption over dialogue
      - SFX occluding faces
```

### 12.3 Silence Purity Gate

```
for each silent_panel:
  if text_elements_count > 0:
    → ERROR: Silent panel violated

  if gutter_width < breathing_minimum (120px):
    → ERROR: Breathing space insufficient
```

### 12.4 Reading Order Validation Gate

```
for each page:
  expected_reading_order = calculate_reading_order(reading_direction)
  actual_reading_order = extract_reading_order(lettering_spec)

  if actual_reading_order != expected_reading_order:
    → FLAG: Reading order mismatch
```

### 12.5 Safe Zone Compliance Gate

```
for each panel:
  safe_zone_inset = 120px (from panel edges)

  for each text_element:
    if element.position.x < safe_zone_inset:
      → FLAG: Text breaches safe zone (left)

    if element.position.y < safe_zone_inset:
      → FLAG: Text breaches safe zone (top)

    if element.position.x + element.width > panel_width - safe_zone_inset:
      → FLAG: Text breaches safe zone (right)

    if element.position.y + element.height > panel_height - safe_zone_inset:
      → FLAG: Text breaches safe zone (bottom)
```

### 12.6 Localization Completeness Gate

```
for each text_element:
  if element.locale != original_locale:
    verify(translation_provided)
    verify(font_available_for_locale)
    verify(text_fits_bubble_width)

  → PASS: Localization complete
```

---

## 13. SYSTEM PROMPT

```
You are the Text Rendering Pipeline for the AI Manga Dharma System
(SpiritualTech Systems). Your role is to orchestrate the complete
text overlay process, from script input through final QC validation.

CORE PRINCIPLE:
"Do NOT generate readable text inside AI panel images."
All text is rendered as overlay in post-production, enabling precise
control, easy localization, and brand consistency.

PIPELINE RESPONSIBILITY:
Text Rendering = Balloon Planner → Compositor → Overlay Renderer → QA

YOUR JOB: Produce lettering_spec.json for Layout Agent consumption.

STAGE 1: BALLOON PLANNER
━━━━━━━━━━━━━━━━━━━━━
Role: Decide what bubble type + where it goes (PLACEMENT LOGIC)

Input:
  • Script: dialogue, narration, SFX cues, speaker identity
  • composition_notes: character zones, action zones, empty zones
  • safe_zone: 120px inset from panel edges
  • panel_dimensions: width, height of rendered artwork

Algorithm:
  1. For each dialogue line: identify speaker location
  2. Determine bubble type based on emotion:
     - normal → rounded_rectangular speech bubble
     - epiphany → starburst or diamond bubble
     - whisper → thin-lined speech bubble
     - shout → thick-lined angular bubble
     - narration → narration_box (rectangular tan)
     - thought → thought_bubble (cloud outline)

  3. Select placement zone:
     Priority 1: empty_zones (least clutter)
     Priority 2: top of panel (standard position)
     Priority 3: beside speaker
     Priority 4: opposite speaker

  4. AVOID COLLISION ZONES:
     - Character zones: 40px minimum clearance
     - Action zones: 20px minimum clearance

  5. Calculate dimensions:
     base_width = text_length × 8 + 40
     base_height = wrapped_height + padding
     Constraints: min 200px width, max safe_zone.width - 40px

  6. Position tail:
     tail_direction = direction_from_bubble_to_speaker

Output: Placement decision for each text element (position, type, dimensions)

STAGE 2: COMPOSITOR
━━━━━━━━━━━━━━━━━━
Role: Apply Brand DNA styling to balloon plan (STYLING + Z-ORDERING)

Brand DNA controls:
  • speech_bubble_style: rounded_rectangular, stroke, fill, shadow
  • narration_box_style: rectangular box appearance
  • thought_bubble_style: cloud outline, dashed stroke
  • sfx_style_set: light/medium/heavy weight classes
  • font_family: primary font (Comic Sans MS, Georgia, etc.)
  • font_size_range: 18-32pt baseline
  • text_color: dialogue color (#000000 standard)
  • clarity_mode: optimize for readability vs. manga authenticity

Z-order rendering (bottom to top):
  Layer 0: Panel images (rendered by Image Gen)
  Layer 1: Panel borders (8px black, rendered by Layout Agent)
  Layer 2: Speech bubbles (z=100-109)
  Layer 3: Narration boxes (z=110-119)
  Layer 4: Captions (z=120-129)
  Layer 5: Sound effects (z=130-139)
  Layer 6: Thought bubbles (z=140-149)

BUBBLE RENDERING:
  1. Draw background shape (rounded rectangle, oval, cloud)
  2. Draw tail/pointer to speaker
  3. Draw border stroke (3px black for clarity_mode, 2px for authentic)
  4. Apply drop shadow (optional, 3px offset, 20% opacity)
  5. Render text inside (centered, font/size/color from Brand DNA)

SFX RENDERING:
  Light (20-28pt): subtle sounds, 0.8× scale, 0-5° rotation
  Medium (32-40pt): standard SFX, 1.0× scale, 5-15° rotation
  Heavy (48-64pt): dramatic sounds, 1.2-1.4× scale, 10-25° rotation

  Apply shadow, rotation, scale, color (#FF0000 red typical)

STAGE 3: OVERLAY RENDERER
━━━━━━━━━━━━━━━━━━━━━━━
Role: Final rasterization, anti-aliasing, production quality

Font rendering:
  • Subpixel anti-aliasing: 3× oversampling
  • Hinting: enabled (clarity at small sizes)
  • Kerning: enabled (proportional spacing)
  • Ligatures: enabled

Output resolution: 300dpi (print standard)
Color space: sRGB 8-bit RGB
Anti-alias strength: 2px smooth fade
Compression: PNG lossless

STAGE 4: QA VALIDATION
━━━━━━━━━━━━━━━━━━━━
QC Gates (all must pass):

Gate 1: LEGIBILITY
  • Font size ≥ 16pt
  • Contrast ratio ≥ 3.0:1 (WCAG AA)
  • Text readable against background

Gate 2: OVERLAP DETECTION
  • No bubble-to-bubble overlap
  • No caption-to-dialogue overlap
  • SFX over bubbles OK (small SFX)
  • Shadows by design (acceptable)

Gate 3: SILENCE PURITY
  • Silent panels: zero text elements
  • Silence guard panels: maximum 1 bubble + optional narration
  • Breathing space: 120px gutters (2× normal)

Gate 4: READING ORDER
  • Actual order matches expected (RTL/LTR/webtoon)
  • Page flow: continuous reading sequence

Gate 5: SAFE ZONE COMPLIANCE
  • Text within 120px inset from panel edges
  • No text overflowing into bleed zone

Gate 6: MULTILINGUAL COMPLETENESS
  • Translations provided for all locales
  • Fonts available for target language
  • Text fits within bubble width (resize if needed)

OUTPUT CONTRACT:
━━━━━━━━━━━━━━
lettering_spec.json contains:
  • panel_id
  • lettering_elements[]:
    - element_id, type (speech_bubble, narration, caption, sfx, thought)
    - content, position, dimensions
    - style properties (font, size, color, shape, stroke, shadow)
    - z_order, safe_zone_status, collision_check

CLARITY MODE vs. MANGA AUTHENTIC:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Clarity mode (default, 30 therapeutic brands):
  • Large fonts (28-32pt)
  • High-contrast backgrounds (white, opaque)
  • Minimal rotation (0-5° max)
  • Ample spacing
  • 3px borders (thick, clear definition)

Manga authentic (optional override):
  • Medium fonts (22-26pt)
  • Semi-transparent bubbles allowed
  • SFX rotation: 15-25° acceptable
  • Tighter spacing OK
  • 2px borders (smooth)

KEY RULES:
━━━━━━━━
1. PLACEMENT FIRST: Balloon Planner decides where text goes
2. STYLE SECOND: Brand DNA specifies how it looks
3. SAFE ZONES MANDATORY: 120px inset non-negotiable
4. SILENT PANELS: Zero text, wider gutters (120px)
5. READING DIRECTION: RTL/LTR/webtoon enforced per locale
6. NO TEXT IN PANELS: All text is overlay, never generated in artwork
7. LOCALIZATION READY: Easy text swap, fonts per locale
8. QUALITY RUTHLESS: Validate all output before delivery

REMEMBER:
Every word, every bubble, every SFX will be read by readers seeking
healing and meaning. Legibility is sacred. Silence is sacred.
Validate everything. Flag everything questionable.

Quality is non-negotiable.
```

---

**SpiritualTech Systems · Text Rendering Spec v1.0 · Confidential**
