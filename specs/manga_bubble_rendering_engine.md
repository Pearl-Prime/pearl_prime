# Manga Speech Bubble Rendering Engine — Technical Specification

**Status:** Draft v1.0  
**Author:** Pearl_Dev  
**Date:** 2026-04-17  
**Scope:** Pillow-based bubble/SFX overlay engine for the Phoenix Omega manga pipeline

---

## Preface: Relationship to Existing Specs

`specs/LETTERING_AGENT_SPEC.md` defines the _semantic_ lettering layer — what bubbles
should say, where conceptually they belong, and how they relate to story pacing.  
This spec defines the _rendering_ layer — the Pillow code that turns those semantic
descriptions into pixels. The two specs are complementary. When they conflict, this
spec governs pixel decisions; LETTERING_AGENT_SPEC governs text-content decisions.

---

## 1. Architecture Decision: Layer Position

### The Candidates

**Option A — New stage `CHAPTER_BUBBLE_RENDER` between `CHAPTER_LETTERING` and
`CHAPTER_LAYOUT`.**  
The renderer reads each per-panel PNG from `panel_images_manifest`, composites speech
bubbles, SFX, and captions onto a new copy, and writes a `panel_images_manifest_bubbled`
pointing at the new files. `CHAPTER_LAYOUT` (`compose_final_page_pngs`) then tiles the
already-lettered panels — it never needs to know lettering happened.

**Option B — Post-composition overlay after `compose_final_page_pngs` runs.**  
The renderer receives assembled `page_NNN.png` strips and draws bubbles onto them.

### Why Option A Is Correct

`page_compose.py` already discards panel boundaries. Once panels are tiled into a strip
the code only tracks total page width; individual panel offsets are not stored anywhere.
Implementing overlap-safe bubble placement, per-panel coverage limits, and
reading-order assignment all require knowing which pixels belong to which panel.
Option B would require reconstructing panel boundaries from the manifest just to do
what Option A gets for free.

Additionally, Option A means lettering bugs do not require regenerating images, and
image regeneration does not require re-running lettering — the same decoupling goal
stated in LETTERING_AGENT_SPEC §1.

**Decision: Option A.**

### Precise Stage Slot

```
CHAPTER_IMAGE_GEN
CHAPTER_LETTERING       (currently produces silence_confirmed only)
CHAPTER_BUBBLE_RENDER   ← NEW (reads lettering_spec_v2 + manifest, writes bubbled PNGs)
CHAPTER_LAYOUT          (no changes; receives manifest_bubbled instead of manifest)
ITE_BREATH
...
```

---

## 2. New Stage: `CHAPTER_BUBBLE_RENDER`

### 2.1 Stage ID Registration

```python
# phoenix_v4/manga/models/stage_ids.py — add:
CHAPTER_BUBBLE_RENDER = "chapter_bubble_render"

# Also add to ALL_STAGE_IDS tuple immediately after CHAPTER_LETTERING.
```

### 2.2 DAG Position

```python
# phoenix_v4/manga/runner/dag_order.py — RUN_ORDER becomes:
RUN_ORDER: tuple[str, ...] = (
    sid.TRANSMISSION_SPLIT,
    sid.CHAPTER_WRITER,
    sid.CHAPTER_VISUAL,
    sid.CHAPTER_IMAGE_GEN,
    sid.CHAPTER_LETTERING,
    sid.CHAPTER_BUBBLE_RENDER,   # NEW
    sid.CHAPTER_LAYOUT,
    sid.ITE_BREATH,
    ...
)

# STAGE_NAMES — add:
sid.CHAPTER_BUBBLE_RENDER: "Speech bubble render",
```

### 2.3 Stage Contract

```
Consumes:
  chapter_script         — extended dialogue schema (Section 3)
  lettering_spec_v2      — extended lettering spec (Section 4)
  panel_images_manifest  — artifact_type="panel_images_manifest", panels[*].status="ok"
  bubble_style_config    — inline dict OR loaded from series visual_identity

Produces:
  panel_images_manifest_bubbled  — same schema as panel_images_manifest;
                                   panels[*].path updated to _bubbled.png copies
  bubble_layout_spec             — new artifact (Section 4.2)

Side effects (per panel where silence_confirmed=False):
  Writes {original_stem}_bubbled.png alongside original.
  Original PNG is NEVER modified (non-destructive — re-runs are safe).

Skips (silence_confirmed=True):
  Panel entry in manifest_bubbled copies the original path verbatim.
  No new file is written.
```

The stage is **idempotent**: if `{stem}_bubbled.png` already exists with matching
`content_sha256`, the write is skipped and the existing file is used.

---

## 3. Extended Chapter Script Dialogue Schema

### 3.1 Current State

`lettering_from_script.py: _panel_has_dialogue_text` handles two cases already:

```python
if isinstance(x, str) and x.strip():    # old flat string
    return True
if x is not None and not isinstance(x, str) and str(x).strip():  # anything else
    return True
```

The flat `list[str]` format is the only format actively used in production panels.

### 3.2 Extended Panel Dialogue Schema

A panel in `chapter_script.pages[*].panels[*]` is extended as follows.
All existing fields (`panel_id`, `action`, `mood`, `sfx`, `narrator_caption`, etc.)
are unchanged. Only `dialogue` is extended.

```json
{
  "panel_id": "p001",
  "action": "Protagonist charges forward",
  "mood": "tense",
  "silence_guard": false,
  "dialogue": [
    {
      "speaker_id": "protagonist",
      "speaker_position": "left",
      "text": "I won't give up!",
      "emotion": "determination",
      "intensity": "shouting",
      "speech_atom_id": "atom_shonen_protagonist_determination_shouting_01",
      "bubble_style_override": null
    }
  ],
  "sfx": ["CRACK"],
  "narrator_caption": null
}
```

### 3.3 Dialogue Line Field Reference

| Field | Type | Required | Default | Notes |
|---|---|---|---|---|
| `speaker_id` | string | yes | — | Must match a character id from the chapter script's cast list, OR `"narrator"` |
| `speaker_position` | enum | no | `"auto"` | `"left"`, `"right"`, `"center"`, `"off_panel"`, `"auto"` |
| `text` | string | yes | — | Verbatim dialogue. Never modified by the renderer. |
| `emotion` | enum | no | `"neutral"` | `"neutral"`, `"happy"`, `"angry"`, `"sad"`, `"fearful"`, `"surprised"`, `"determination"`, `"internal"` |
| `intensity` | enum | no | `"normal"` | `"whisper"`, `"calm"`, `"normal"`, `"excited"`, `"shouting"`, `"screaming"`, `"internal"` |
| `speech_atom_id` | string | no | null | Reference to `config/source_of_truth/manga_speech_atoms/` entry for style override |
| `bubble_style_override` | string or null | no | null | If set, overrides the bubble shape derived from intensity. Values: `"round"`, `"spiky"`, `"cloud"`, `"square"`, `"whisper"`, `"radio"` |

### 3.4 SFX Field

`panel.sfx` is `list[str]` — no change. Each string is one sound effect label.
The renderer looks up each label in `bubble_style_config.sfx_lexicon` for visual treatment.

### 3.5 Narrator Caption Field

`panel.narrator_caption` is `string | null` — no change in type. When present, it
is rendered as a full-width caption box (top or bottom, see Section 5.5).

### 3.6 Backward Compatibility Rule

If `panel.dialogue` is a `list[str]` (old format), the renderer and the updated
`lettering_from_script.py` both apply this automatic upgrade before any processing:

```python
def _normalize_dialogue(raw: list) -> list[dict]:
    result = []
    for i, x in enumerate(raw):
        if isinstance(x, str):
            result.append({
                "speaker_id": f"speaker_{i + 1}",
                "speaker_position": "auto",
                "text": x,
                "emotion": "neutral",
                "intensity": "normal",
                "speech_atom_id": None,
                "bubble_style_override": None,
            })
        elif isinstance(x, dict):
            result.append(x)  # already extended format
    return result
```

This normalization happens inside `_panel_has_dialogue_text` (for silence detection)
and inside `build_lettering_spec_from_chapter_script` (for spec construction). It must
never be applied in-place to the original `chapter_script` dict — always operate on a
local copy.

### 3.7 Required Change in `lettering_from_script.py`

`_panel_has_dialogue_text` must be updated to handle the extended dict format:

```python
def _panel_has_dialogue_text(panel: Mapping[str, Any]) -> bool:
    dialogue = panel.get("dialogue")
    if not isinstance(dialogue, list):
        return False
    for x in dialogue:
        if isinstance(x, str) and x.strip():
            return True
        if isinstance(x, dict):
            text = x.get("text", "")
            if isinstance(text, str) and text.strip():
                return True
    return False
```

`build_lettering_spec_from_chapter_script` must be extended to emit v2 fields when
extended dialogue is present. The spec change is: when any dialogue entry is a `dict`
with a `text` key, emit `dialogue_lines`, `sfx`, `narrator_caption`, and
`estimated_bubble_coverage` in the panel output (see Section 4).

The implementation must NOT break existing callers that pass `list[str]` dialogue —
the backward compatibility normalization in Section 3.6 handles that transparently.

---

## 4. Extended Lettering Spec Schema (v2)

### 4.1 Top-Level Structure

Schema stem (for `validate_instance`): `"lettering_spec"`.  
The existing `lettering_spec.schema.json` must be updated to `schema_version: "2.0.0"`.
Version `"1.0.0"` documents remain valid but produce no `dialogue_lines` field, so
`CHAPTER_BUBBLE_RENDER` must treat missing `dialogue_lines` as an empty list (not an
error) for forward compatibility of the schema upgrade path.

```json
{
  "schema_version": "2.0.0",
  "artifact_type": "lettering_spec",
  "lettering_panels": [
    {
      "panel_id": "p001",
      "silence_confirmed": false,
      "dialogue_lines": [
        {
          "speaker_id": "protagonist",
          "text": "I won't give up!",
          "emotion": "determination",
          "intensity": "shouting",
          "speech_atom_id": "atom_shonen_protagonist_determination_shouting_01",
          "bubble_style": "spiky_emphasis",
          "font_override": null,
          "position_hint": "top_right",
          "tail_style": "pointer"
        }
      ],
      "sfx": ["CRACK"],
      "narrator_caption": null,
      "estimated_bubble_coverage": 0.18
    }
  ]
}
```

### 4.2 Dialogue Line Fields in Lettering Spec

These are the _renderer-facing_ fields derived from chapter_script dialogue lines.
`lettering_from_script.py` populates them; `bubble_render.py` consumes them.

| Field | Type | Source | Notes |
|---|---|---|---|
| `speaker_id` | string | chapter_script | Passed through verbatim |
| `text` | string | chapter_script | Verbatim. Never modified. |
| `emotion` | enum | chapter_script | Used by renderer to pick font weight |
| `intensity` | enum | chapter_script | Primary driver of bubble shape and font size |
| `speech_atom_id` | string or null | chapter_script | If set, renderer loads atom config for overrides |
| `bubble_style` | string | derived | Resolved bubble shape name (see Section 5.2). Derived from intensity + emotion + bubble_style_override + speech_atom_id in that priority order. |
| `font_override` | string or null | derived or atom | Font name from font registry. Null = use intensity default. |
| `position_hint` | string | derived from speaker_position | Placement zone name. One of: `"top_right"`, `"top_left"`, `"top_center"`, `"bottom_right"`, `"bottom_left"`, `"auto"` |
| `tail_style` | string | derived from emotion+intensity | `"pointer"`, `"dotless"`, `"wavy"` (v1 wavy falls back to pointer) |

### 4.3 `estimated_bubble_coverage` Field

A float in [0.0, 1.0]. It is the lettering agent's estimate of what fraction of the
panel area will be covered by bubbles for this panel's dialogue load.

Calculation formula (approximate, before layout is known):

```python
def estimate_coverage(dialogue_lines: list[dict], panel_w: int, panel_h: int) -> float:
    total_px = 0
    for line in dialogue_lines:
        text = line.get("text", "")
        intensity = line.get("intensity", "normal")
        font_size = INTENSITY_FONT_SIZES.get(intensity, 14)
        # Approximate bubble area: text length * font_size^2 * padding_factor
        char_count = len(text)
        bubble_area = char_count * (font_size * 0.65) * (font_size * 1.4) * 1.5
        total_px += bubble_area
    panel_area = panel_w * panel_h
    return min(1.0, total_px / panel_area) if panel_area > 0 else 0.0
```

When `panel_w` and `panel_h` are not available at lettering time, use defaults of
`800 × 1100` (standard portrait panel size). The renderer recomputes actual coverage
from real image dimensions and ignores the estimate.

### 4.4 Bubble Layout Spec Artifact

A second new artifact output by `CHAPTER_BUBBLE_RENDER`. Provides a per-panel
record of exactly where each bubble was placed (useful for QC and debugging).

```json
{
  "schema_version": "1.0.0",
  "artifact_type": "bubble_layout_spec",
  "panels": [
    {
      "panel_id": "p001",
      "panel_path": "/abs/path/to/panel_p001_bubbled.png",
      "panel_width": 800,
      "panel_height": 1100,
      "actual_coverage": 0.172,
      "coverage_limit_hit": false,
      "bubbles": [
        {
          "speaker_id": "protagonist",
          "bubble_style": "spiky_emphasis",
          "bbox": [420, 33, 748, 198],
          "text": "I won't give up!",
          "font_size": 18,
          "zone": "top_right",
          "tail_tip": [540, 420]
        }
      ],
      "sfx_placements": [
        {
          "text": "CRACK",
          "bbox": [280, 500, 580, 620],
          "font_size": 52,
          "rotation_deg": 0
        }
      ],
      "narrator_caption_bbox": null
    }
  ]
}
```

Schema stem for validation: `"bubble_layout_spec"`. This schema file must be created
at `schemas/manga/bubble_layout_spec.schema.json`.

---

## 5. Bubble Renderer Module Spec

**Module path:** `phoenix_v4/manga/chapter/bubble_render.py`

### 5.1 Public API

```python
from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping


def render_bubbles_onto_panel(
    panel_image_path: Path,
    dialogue_lines: list[dict],       # from lettering_spec_v2 panel entry
    sfx: list[str],
    narrator_caption: str | None,
    *,
    bubble_style_config: dict,
    out_path: Path | None = None,
    coverage_limit: float = 0.30,
) -> dict:
    """Composite bubbles, SFX, and captions onto a copy of panel_image_path.

    Returns a bubble_layout record (one element of bubble_layout_spec["panels"]).

    If out_path is None, writes to {panel_image_path.stem}_bubbled.png in the
    same directory as panel_image_path.

    Raises:
        RuntimeError: if Pillow is not installed.
        ValueError: if coverage_limit <= 0 or > 1.
        FileNotFoundError: if panel_image_path does not exist.
    """
    ...


def build_bubble_layout_spec(
    chapter_script: Mapping[str, Any],
    lettering_spec_v2: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    bubble_style_config: Mapping[str, Any],
    out_dir: Path,
    *,
    coverage_limit: float = 0.30,
    schema_version: str = "1.0.0",
) -> dict:
    """Iterate over all panels, call render_bubbles_onto_panel, return bubble_layout_spec.

    Also returns updated panel_images_manifest_bubbled as a second value:
        layout_spec, manifest_bubbled = build_bubble_layout_spec(...)

    Silent panels (silence_confirmed=True) are passed through without rendering.
    Panels not present in the manifest (status != "ok") are skipped with a warning.
    """
    ...
```

Both functions must be importable without Pillow installed (import guarded inside the
function body with a clear `RuntimeError` message pointing to `pip install Pillow`).

### 5.2 Bubble Style Resolution

Before drawing, the renderer resolves a concrete `bubble_style` name for each
dialogue line using this precedence order:

1. `line["bubble_style_override"]` if not None — use as-is
2. Speech atom config from `bubble_style_config["speech_atoms"][atom_id]` if
   `speech_atom_id` is set and present — use `atom["bubble_style"]`
3. Intensity-to-style mapping:

```python
INTENSITY_TO_BUBBLE_STYLE: dict[str, str] = {
    "whisper":   "whisper",
    "calm":      "round",
    "normal":    "round",
    "excited":   "spiky_light",
    "shouting":  "spiky_emphasis",
    "screaming": "spiky_heavy",
    "internal":  "cloud",
}
```

4. Default: `"round"`

### 5.3 Bubble Shape Rendering

All shapes are drawn using `PIL.ImageDraw`. The canvas is a copy of the original
panel opened in `RGBA` mode. All drawing is done on the RGBA canvas and the result
is saved as PNG.

#### Round / Oval (styles: `"round"`)

```python
# Compute text bounding box first, then add padding:
padding_h = 18   # horizontal padding per side, px
padding_v = 14   # vertical padding per side, px
# bbox = (text_x - padding_h, text_y - padding_v,
#          text_x + text_w + padding_h, text_y + text_h + padding_v)
draw.ellipse(bbox, fill=(255, 255, 255, 240), outline=(0, 0, 0, 255), width=2)
# Then draw text centered inside bbox.
```

Bubble fill is `(255, 255, 255, 240)` — slightly transparent white so the panel art
is faintly visible through the bubble (gives depth without hiding art completely).
Outline color is `(0, 0, 0, 255)` at width 2px.

#### Spiky / Jagged Bubble (styles: `"spiky_light"`, `"spiky_emphasis"`, `"spiky_heavy"`)

Used for excited, shouting, screaming dialogue. Draws a spiked polygon around the
text area.

```python
import math

SPIKE_COUNTS = {
    "spiky_light":     8,
    "spiky_emphasis": 16,
    "spiky_heavy":    24,
}
SPIKE_HEIGHTS = {
    "spiky_light":     7,
    "spiky_emphasis": 12,
    "spiky_heavy":    18,
}

def _spiky_polygon(cx, cy, rx, ry, n_spikes, spike_h):
    """Return a list of (x, y) points for a spiky bubble polygon.
    cx, cy = center; rx, ry = ellipse radii; n_spikes = number of outward spikes.
    """
    n_points = n_spikes * 2          # alternating inner/outer
    points = []
    for i in range(n_points):
        angle = (2 * math.pi * i) / n_points - math.pi / 2
        # Even indices: outer spike tip; odd indices: ellipse surface
        if i % 2 == 0:
            r_x = rx + spike_h
            r_y = ry + spike_h
        else:
            r_x = rx
            r_y = ry
        points.append((cx + r_x * math.cos(angle), cy + r_y * math.sin(angle)))
    return points

points = _spiky_polygon(cx, cy, rx, ry, SPIKE_COUNTS[style], SPIKE_HEIGHTS[style])
draw.polygon(points, fill=(255, 255, 255, 240), outline=(0, 0, 0, 255))
# Draw text centered at (cx, cy).
```

The ellipse radii `rx` and `ry` are derived from the text bounding box plus padding
(same as round bubble, minus the Pillow `ellipse` call).

#### Cloud / Thought Bubble (style: `"cloud"`)

```python
# 1. Draw the main body as a round bubble (ellipse).
# 2. Draw a trail of 4 diminishing circles from the bubble bottom toward speaker_position:
trail_sizes = [20, 14, 9, 5]  # diameters in px
# Each circle is placed along a straight line from bubble bottom-center
# toward speaker_mouth_estimate (see Section 5.6).
# Spacing: each circle center is placed 1.8× the previous circle's radius from the last.
for i, diam in enumerate(trail_sizes):
    r = diam // 2
    # interpolate position from bubble_bottom to mouth_point
    t = (i + 1) / (len(trail_sizes) + 1)
    cx_trail = int(bubble_bottom_x + t * (mouth_x - bubble_bottom_x))
    cy_trail = int(bubble_bottom_y + t * (mouth_y - bubble_bottom_y))
    draw.ellipse(
        [cx_trail - r, cy_trail - r, cx_trail + r, cy_trail + r],
        fill=(255, 255, 255, 220),
        outline=(0, 0, 0, 255),
        width=1,
    )
```

#### Square / Narration Caption (style: `"square"`)

Caption boxes for `narrator_caption` and for dialogue with `bubble_style_override="square"`.

```python
# Rectangle with thin 1px border, no tail.
# Position: determined by position_hint.
# "top_caption": x=0, y=0, width=panel_width, height=text_h + 2*padding_v
# "bottom_caption": x=0, y=panel_height - (text_h + 2*padding_v), width=panel_width
# Text is left-aligned with 12px left margin, vertically centered.
draw.rectangle(bbox, fill=(255, 255, 200, 230), outline=(60, 60, 60, 255), width=1)
# Caption fill is pale yellow to distinguish from speech (matches manga convention).
```

Narrator captions always use `"top_caption"` placement unless `position_hint` is
`"bottom_*"`. Caption boxes span full panel width.

#### Whisper Bubble (style: `"whisper"`)

Dashed/broken border on an oval bubble. Pillow has no native dashed line; simulate
with arc segments:

```python
# Divide the ellipse into N arc segments; draw alternating segments.
# N_DASHES = 16; draw segments [0, 2, 4, ...] (even), skip [1, 3, 5, ...] (odd).
N_DASHES = 16
seg_deg = 360 / N_DASHES
for i in range(0, N_DASHES, 2):  # draw every other segment
    start_deg = i * seg_deg
    end_deg = start_deg + seg_deg
    draw.arc(bbox, start=start_deg, end=end_deg, fill=(0, 0, 0, 200), width=2)
# Fill the interior first with a separate round bubble (no outline), then draw arcs on top:
draw.ellipse(bbox, fill=(255, 255, 255, 200))   # fill only, no outline
# Then draw dashed arcs.
```

Font size for whisper is 0.8× the normal size for the panel's base intensity (see
Section 5.4).

#### Radio / Phone Voice (style: `"radio"`)

Rectangle with serrated top and bottom edges (zigzag). Draw as a rectangle with
a manually constructed polygon that has small triangular notches along top/bottom
edges. In v1, fall back to `"square"` style with a different fill color
`(220, 240, 255, 230)` (light blue). Annotate the fallback in the layout record.

### 5.4 Text Rendering

#### Font Loading

```python
from PIL import ImageFont

FONT_PATHS = [
    Path("fonts/AnimeAce.ttf"),           # preferred
    Path("fonts/KomikaTight.ttf"),         # fallback 1
]

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_PATHS:
        if path.is_file():
            return ImageFont.truetype(str(path), size=size)
    # System font fallback — OS-dependent but consistent enough for dev/CI
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size=size)
    except OSError:
        return ImageFont.load_default()
```

If only `ImageFont.load_default()` is available, the renderer must log a warning
(not raise) and continue. Bubble placement still works; only aesthetics degrade.

#### Font Size by Intensity

```python
INTENSITY_FONT_SIZES: dict[str, int] = {
    "whisper":   10,
    "calm":      12,
    "normal":    14,
    "excited":   16,
    "shouting":  18,
    "screaming": 22,
    "internal":  11,
}
```

`"internal"` (internal monologue) uses the `"cloud"` bubble style and italic font
weight if available. If the loaded font has no italic variant, use the regular weight
at the specified size.

#### Text Wrapping

```python
import textwrap

def _wrap_text(text: str, bubble_w: int, font) -> list[str]:
    # M-width approximation for average character width:
    m_bbox = font.getbbox("M")
    avg_char_w = (m_bbox[2] - m_bbox[0]) * 0.72   # 0.72 accounts for narrower chars
    usable_w = bubble_w - 2 * PADDING_H
    chars_per_line = max(8, int(usable_w / avg_char_w))
    return textwrap.wrap(text, width=chars_per_line) or [text]
```

`textwrap.wrap` is preferred over manual splitting because it respects word
boundaries. Never split a word across lines in v1.

After wrapping, compute total text block height:

```python
line_height = font.getbbox("Ag")[3] + 3   # 3px leading
total_text_h = len(lines) * line_height
```

Text is drawn centered horizontally and vertically within the bubble bounding box.

### 5.5 Bubble Placement Algorithm

**Coordinate system:** pixel coordinates with origin at top-left of the panel image.
All zone definitions are fractions of panel dimensions, resolved to pixel coords at
render time.

#### Zone Definitions

```python
# Zones as (x1_frac, y1_frac, x2_frac, y2_frac) — fractions of panel dimensions
ZONES: dict[str, tuple[float, float, float, float]] = {
    "top_right":     (0.52, 0.03, 0.98, 0.32),
    "top_left":      (0.02, 0.03, 0.48, 0.32),
    "top_center":    (0.20, 0.03, 0.80, 0.25),
    "bottom_right":  (0.52, 0.68, 0.98, 0.97),
    "bottom_left":   (0.02, 0.68, 0.48, 0.97),
    "center_right":  (0.52, 0.35, 0.98, 0.65),
    "center_left":   (0.02, 0.35, 0.48, 0.65),
    # Reserved for narrator captions — full width, thin:
    "top_caption":   (0.00, 0.00, 1.00, 0.12),
    "bottom_caption":(0.00, 0.88, 1.00, 1.00),
}
```

#### Reading Order Assignment

Japanese right-to-left reading order defaults. If `bubble_style_config["reading_direction"]`
is `"left_to_right"`, swap the left/right assignments.

```python
# Right-to-left (default):
DEFAULT_ZONE_SEQUENCE = [
    "top_right", "top_left", "bottom_right", "bottom_left",
    "center_right", "center_left",
]

def _assign_zones(dialogue_lines: list[dict]) -> list[str]:
    zones = []
    seq = iter(DEFAULT_ZONE_SEQUENCE)
    for line in dialogue_lines:
        hint = line.get("position_hint", "auto")
        if hint != "auto" and hint in ZONES:
            zones.append(hint)
        else:
            try:
                zones.append(next(seq))
            except StopIteration:
                zones.append("bottom_left")   # fallback: stack at bottom left
    return zones
```

If `narrator_caption` is present, it is always placed in `"top_caption"` first and
does not consume a zone from the sequence.

#### Bubble Sizing Within Zone

Given a zone and the text content:

```python
def _compute_bubble_bbox(
    zone_px: tuple[int, int, int, int],  # (x1, y1, x2, y2) in pixels
    text: str,
    font,
    style: str,
) -> tuple[int, int, int, int]:
    # 1. Compute wrapped text dimensions
    zone_w = zone_px[2] - zone_px[0]
    zone_h = zone_px[3] - zone_px[1]
    lines = _wrap_text(text, zone_w, font)
    m_h = font.getbbox("Ag")[3]
    line_h = m_h + 3
    text_w = max(font.getlength(l) for l in lines)
    text_h = len(lines) * line_h

    # 2. Add bubble padding
    bw = int(text_w + 2 * PADDING_H)
    bh = int(text_h + 2 * PADDING_V)

    # 3. Spiky styles need extra margin for spike protrusion
    if "spiky" in style:
        spike_h = SPIKE_HEIGHTS.get(style, 10)
        bw += spike_h * 2
        bh += spike_h * 2

    # 4. Clamp to zone bounds
    bw = min(bw, zone_w)
    bh = min(bh, zone_h)

    # 5. Center bubble within zone
    cx = zone_px[0] + zone_w // 2
    cy = zone_px[1] + zone_h // 2
    return (cx - bw // 2, cy - bh // 2, cx + bw // 2, cy + bh // 2)
```

#### Coverage Enforcement

After all bubbles are sized and placed, compute actual coverage:

```python
def _total_coverage(bboxes: list[tuple], panel_w: int, panel_h: int) -> float:
    total = sum((b[2] - b[0]) * (b[3] - b[1]) for b in bboxes)
    return total / (panel_w * panel_h)
```

If `total_coverage > coverage_limit`:

1. Reduce all font sizes by 1pt.
2. Recompute all bubble bounding boxes.
3. Repeat up to 3 times.
4. If still over limit after 3 reductions, split the longest dialogue line's text at
   its midpoint (nearest word boundary) and add the second half as a new bubble in
   the same zone, stacking below the first. Log a warning with panel_id.

#### Overlap Resolution

After initial placement, check all pairs of bubble bounding boxes for AABB overlap:

```python
def _aabb_overlap(a: tuple, b: tuple) -> bool:
    return not (a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1])

def _resolve_overlaps(bboxes: list[tuple], panel_w: int, panel_h: int) -> list[tuple]:
    MAX_ITERATIONS = 4
    for _ in range(MAX_ITERATIONS):
        changed = False
        for i in range(len(bboxes)):
            for j in range(i + 1, len(bboxes)):
                if _aabb_overlap(bboxes[i], bboxes[j]):
                    # Push the smaller bubble (by area) away from the larger one
                    ai = (bboxes[i][2]-bboxes[i][0]) * (bboxes[i][3]-bboxes[i][1])
                    aj = (bboxes[j][2]-bboxes[j][0]) * (bboxes[j][3]-bboxes[j][1])
                    small, large = (j, i) if aj < ai else (i, j)
                    # Compute push direction (center of small away from center of large)
                    scx = (bboxes[small][0] + bboxes[small][2]) // 2
                    scy = (bboxes[small][1] + bboxes[small][3]) // 2
                    lcx = (bboxes[large][0] + bboxes[large][2]) // 2
                    lcy = (bboxes[large][1] + bboxes[large][3]) // 2
                    dx = scx - lcx or 1
                    dy = scy - lcy or 1
                    norm = math.sqrt(dx*dx + dy*dy)
                    push = 12   # pixels per iteration
                    ox = int(push * dx / norm)
                    oy = int(push * dy / norm)
                    x1, y1, x2, y2 = bboxes[small]
                    bw = x2 - x1
                    bh = y2 - y1
                    nx1 = max(0, min(panel_w - bw, x1 + ox))
                    ny1 = max(0, min(panel_h - bh, y1 + oy))
                    bboxes[small] = (nx1, ny1, nx1 + bw, ny1 + bh)
                    changed = True
        if not changed:
            break
    return bboxes
```

If after `MAX_ITERATIONS` overlaps remain, they are recorded in the layout record
as `"overlap_unresolved": true` (not a hard error — QC gate flags them).

### 5.6 Tail Rendering

The tail visually connects a speech bubble to the speaker's approximate mouth
position.

#### Speaker Mouth Estimation

Without face detection, estimate mouth position from `speaker_position`:

```python
MOUTH_ESTIMATES: dict[str, tuple[float, float]] = {
    # (x_frac, y_frac) of panel dimensions
    "left":      (0.20, 0.55),
    "right":     (0.80, 0.55),
    "center":    (0.50, 0.60),
    "off_panel": None,   # no tail for off-panel speakers
    "auto":      (0.50, 0.60),   # same as center
}
```

If `speaker_position` is `None` or `"auto"`, use `(0.50, 0.60)`.
If `"off_panel"`, skip tail drawing entirely.

#### Pointer Tail (default)

```python
def _draw_pointer_tail(draw, bubble_bbox, mouth_pt, tail_width=10):
    # Find the point on the bubble edge closest to the mouth
    cx = (bubble_bbox[0] + bubble_bbox[2]) // 2
    cy = (bubble_bbox[1] + bubble_bbox[3]) // 2
    # Anchor is midpoint of the bubble edge closest to mouth:
    mx, my = mouth_pt
    dx = mx - cx
    dy = my - cy
    # Project to bubble edge (approximate using the bbox half-sides):
    half_w = (bubble_bbox[2] - bubble_bbox[0]) / 2
    half_h = (bubble_bbox[3] - bubble_bbox[1]) / 2
    scale = min(
        abs(half_w / dx) if dx != 0 else float("inf"),
        abs(half_h / dy) if dy != 0 else float("inf"),
    )
    anchor_x = int(cx + dx * scale * 0.9)
    anchor_y = int(cy + dy * scale * 0.9)
    # Perpendicular direction for tail width:
    perp_dx = -dy / (math.sqrt(dx*dx + dy*dy) or 1)
    perp_dy =  dx / (math.sqrt(dx*dx + dy*dy) or 1)
    half_tw = tail_width // 2
    p1 = (int(anchor_x + perp_dx * half_tw), int(anchor_y + perp_dy * half_tw))
    p2 = (int(anchor_x - perp_dx * half_tw), int(anchor_y - perp_dy * half_tw))
    p3 = (int(mx), int(my))
    draw.polygon([p1, p3, p2], fill=(255, 255, 255, 240), outline=(0, 0, 0, 255))
```

#### Dotless Tail (thought/cloud)

No tail is drawn. The cloud trail (Section 5.3) serves as the connector.

#### Tail Style Selection

```python
TAIL_STYLES: dict[str, str] = {
    "pointer":  "pointer",    # default speech
    "dotless":  "dotless",    # thought/cloud
    "wavy":     "pointer",    # v1 fallback — wavy not implemented
}
```

---

## 6. SFX Rendering Spec

Sound effects are overlaid directly on panel art, not inside a bubble shape.

### 6.1 Position Resolution

```python
# Default position map by SFX text (uppercased, stripped).
# Position is (x_frac, y_frac) of panel, at which text is centered.
SFX_POSITION_MAP: dict[str, tuple[float, float]] = {
    "CRACK":   (0.50, 0.50),
    "SLAM":    (0.50, 0.80),
    "WHOOSH":  (0.75, 0.40),
    "BANG":    (0.50, 0.40),
    "THUD":    (0.35, 0.70),
    "CRASH":   (0.50, 0.50),
    "ZAP":     (0.60, 0.35),
    "DRIP":    (0.40, 0.65),
    "CLICK":   (0.65, 0.55),
    "POP":     (0.45, 0.45),
}
# Default for unknown SFX:
SFX_DEFAULT_POSITION = (0.50, 0.45)
```

If multiple SFX are present on one panel, offset each by `(0.0, 0.12)` from the
previous to avoid stacking at the same coordinates.

### 6.2 Font Size

```python
SFX_MAJOR = {"CRACK", "SLAM", "BANG", "CRASH", "WHOOSH", "THUD"}

def sfx_font_size(sfx_text: str) -> int:
    return 56 if sfx_text.upper().strip() in SFX_MAJOR else 30
```

### 6.3 Rendering with Stroke

Pillow does not have a native stroke for text. Simulate with the classic offset draw:

```python
def _draw_sfx_text(draw, text, x, y, font):
    # Draw black outline (8 directions at offset=3px):
    outline_color = (0, 0, 0, 255)
    for dx, dy in [(-3,0),(3,0),(0,-3),(0,3),(-3,-3),(3,-3),(-3,3),(3,3)]:
        draw.text((x+dx, y+dy), text, font=font, fill=outline_color, anchor="mm")
    # Draw white fill on top:
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255), anchor="mm")
```

`anchor="mm"` centers the text at `(x, y)`. Use a separate font loaded at
`SFX_FONT_SIZE` — SFX must use a bold weight distinct from dialogue fonts.
SFX font preference order: `AnimeAce.ttf` → `KomikaTight.ttf` → system fallback.

### 6.4 Rotation

SFX is not rotated in v1. The `LETTERING_AGENT_SPEC` §2.3 SFX lexicon specifies
rotation angles — these are stored in the bubble_layout_spec as `rotation_deg`
but the Pillow renderer renders at 0° in v1 and notes the deviation.
(PIL.Image.rotate could be applied to a sub-image crop in v2.)

---

## 7. Changes Required in Existing Files

This section lists exact, minimal changes. No implementation is provided — only
the contract that the implementation must fulfill.

### `phoenix_v4/manga/models/stage_ids.py`

- Add constant: `CHAPTER_BUBBLE_RENDER = "chapter_bubble_render"`
- Add to `ALL_STAGE_IDS` tuple, positioned between `CHAPTER_LETTERING` and
  `CHAPTER_LAYOUT`

### `phoenix_v4/manga/runner/dag_order.py`

- Insert `sid.CHAPTER_BUBBLE_RENDER` into `RUN_ORDER` between `sid.CHAPTER_LETTERING`
  and `sid.CHAPTER_LAYOUT`
- Add to `STAGE_NAMES`: `sid.CHAPTER_BUBBLE_RENDER: "Speech bubble render"`

### `phoenix_v4/manga/chapter/lettering_from_script.py`

- `_panel_has_dialogue_text`: add the `isinstance(x, dict)` branch shown in Section 3.6
- `build_lettering_spec_from_chapter_script`: when any dialogue entry is a dict,
  populate `dialogue_lines`, `sfx`, `narrator_caption`, and `estimated_bubble_coverage`
  fields in each panel output entry
- Existing behavior for `list[str]` dialogue must not change (old tests must still pass)
- The function signature does not change

### `phoenix_v4/manga/chapter/chapter_production.py`

- After the `build_lettering_spec_from_chapter_script` call, add an optional
  `bubble_render` step:

```python
# New parameter on produce_chapter_assets:
bubble_render_out: Path | None = None

# After lettering is built:
bubble_layout: dict | None = None
manifest_for_layout = manifest          # default: use original
if bubble_render_out is not None:
    from phoenix_v4.manga.chapter.bubble_render import build_bubble_layout_spec
    bubble_layout, manifest_bubbled = build_bubble_layout_spec(
        chapter_script,
        lettering,
        manifest,
        bubble_style_config or {},
        Path(bubble_render_out),
    )
    validate_instance(manifest_bubbled, "panel_images_manifest")
    validate_instance(bubble_layout, "bubble_layout_spec")
    manifest_for_layout = manifest_bubbled

# Then pass manifest_for_layout to compose_final_page_pngs instead of manifest
```

- The `bubble_style_config` parameter must also be added: `bubble_style_config: dict | None = None`
- All existing behavior is preserved when `bubble_render_out` is None

### `schemas/manga/lettering_spec.schema.json`

The current schema is permissive (only requires `panel_id` per panel). The update
must remain backward compatible (v1 docs still pass):

- `schema_version` pattern stays as `^[0-9]+\.[0-9]+\.[0-9]+$`
- Add to `lettering_panels.items.properties`:
  - `dialogue_lines`: array of objects with required `speaker_id` and `text`
  - `sfx`: array of strings
  - `narrator_caption`: string or null
  - `estimated_bubble_coverage`: number, minimum 0.0, maximum 1.0
- All new fields are optional (`not` in `required`) — v1 docs remain valid

### `schemas/manga/bubble_layout_spec.schema.json` — NEW FILE

Create this file at `schemas/manga/bubble_layout_spec.schema.json`. It must validate
the structure shown in Section 4.4. Required fields at the top level:
`schema_version`, `artifact_type` (const `"bubble_layout_spec"`), `panels`.

### `phoenix_v4/manga/chapter/bubble_render.py` — NEW FILE

Public API as specified in Section 5.1. Module-level constants and helpers
as specified throughout Section 5.

### `fonts/` — NEW DIRECTORY

Create at repo root: `fonts/`.  

Required fonts (free for commercial use):
- `AnimeAce.ttf` — Blambot Anime Ace 2.0 BB (free for non-commercial; commercial
  license required for commercial production — **verify license before production use**)
- `KomikaTight.ttf` — Larabie Fonts Komika Tight (free for commercial use, credit
  required)
- `DejaVuSans-Bold.ttf` — DejaVu Fonts (SIL Open Font License — fully free)

Fallback strategy at runtime:

1. Try each path in `FONT_PATHS` in order (relative to repo root or absolute if
   configured via `MANGA_FONTS_DIR` env var)
2. Try system font path (`/usr/share/fonts/`, `/Library/Fonts/`, `C:\Windows\Fonts\`)
3. Use `ImageFont.load_default()` with a logged warning

The fonts directory must be added to `.gitignore` if font files are large binaries
not owned by the project. Alternatively, add a `fonts/README.txt` that documents
where to download each font, and commit only that file.

---

## 8. Risks and Open Questions

### 8.1 Character Face Occlusion

Without ML-based face detection, there is no way to guarantee bubbles do not cover
character faces. The heuristic mitigation is: (a) all placement zones avoid the
vertical center band (0.35–0.65 of height) which is where faces most commonly appear
in portrait-format manga panels; (b) the coverage limit of 30% bounds how much total
bubble area can land on any panel.

Ideal long-term solution: integrate face bounding boxes from the ComfyUI workflow
metadata into the `panel_images_manifest` as an optional `face_bboxes` array. The
renderer would then subtract face regions from available placement zones before
running the placement algorithm. This is a v2 enhancement; v1 uses heuristics only.

### 8.2 Vertical Text (Japanese)

v1 is horizontal-only. Vertical text rendering requires rotating the entire text
block 90°, switching to a vertical-capable font, and adjusting line breaks for
vertical flow. The `reading_direction` field in `bubble_style_config` is reserved
for this but not used in v1.

### 8.3 Font Licensing

- AnimeAce: free for personal/non-commercial. Commercial use requires a paid
  Blambot license (~$40–$120 depending on use). **This spec does not license the font.
  The implementing developer must verify and obtain appropriate licensing before
  production deployment.**
- KomikaTight: Larabie free-for-commercial-use license. Credit line required.
- DejaVu: SIL Open Font License — no restrictions.

Recommended production approach: acquire the Blambot commercial license OR use
DejaVu Bold as the default and accept slightly less manga-specific aesthetics.

### 8.4 Panel Coordinate System

Panels currently have no embedded character-position metadata. The `panel_prompts`
artifact has a `composition_notes.subject_placement` field (per LETTERING_AGENT_SPEC
§2.2) but it is free-text, not a bounding box. The mouth-estimation heuristic in
Section 5.6 is a stopgap.

To fix this properly: the visual image backend (ComfyUI) should be configured to
return face/body bounding boxes in the `gen` output. `build_panel_images_manifest`
would then store them. The bubble renderer would read `panel.face_bboxes` from the
manifest to compute exact mouth positions and exclude face regions.

### 8.5 SFX as Art

The ideal manga SFX treatment draws the sound effect directly into the art as a
stylized lettering element (integrated with the scene). The overlay approach used
in v1 looks "pasted on" compared to hand-lettered originals. The only proper fix
for this is to include SFX lettering as part of the ComfyUI generation prompt — an
ControlNet-level intervention. v1 overlay is the pragmatic baseline.

### 8.6 Curved / Bezier Tails

Pillow does not natively support bezier curve drawing. Options:
- Polygon approximation of a bezier curve (many small segments) — acceptable quality
  for v2
- Add `aggdraw` dependency (supports anti-aliased bezier paths, Apache 2.0 license)
- Generate an SVG tail and rasterize it via `cairosvg`

v1 uses pointer (triangle) tails only. When `tail_style: "wavy"` is requested, v1
silently falls back to `"pointer"` and records `"tail_style_applied": "pointer"` in
the layout spec.

### 8.7 Localization

The v1 spec covers English only. Japanese and Korean require:
- Vertical text support (8.2)
- Different font sets
- Different bubble size profiles (Japanese text is typically denser per bubble)
- Different SFX lexicons

The `bubble_style_config["locale"]` key is reserved but not consumed in v1.

### 8.8 Pillow Thread Safety

`PIL.ImageDraw` is not thread-safe when sharing Image objects across threads. The
renderer must open a fresh Image per panel call. `build_bubble_layout_spec` must not
parallelize panel rendering within a single invocation unless each panel gets an
independent Image object and Draw context.

---

## 9. Implementation Sprint Breakdown

### Task 1 — Schema + Lettering Extension (estimated 2–3 hours)

**Files:** `lettering_from_script.py`, `schemas/manga/lettering_spec.schema.json`,
`schemas/manga/bubble_layout_spec.schema.json`

1. Update `_panel_has_dialogue_text` (Section 3.6)
2. Update `build_lettering_spec_from_chapter_script` to emit v2 fields
3. Update `lettering_spec.schema.json` to accept v2 fields (backward compatible)
4. Create `bubble_layout_spec.schema.json`
5. Unit tests:
   - Old `list[str]` dialogue still passes validation and produces correct
     `silence_confirmed` output
   - New `list[dict]` dialogue produces `dialogue_lines` + `estimated_bubble_coverage`
   - `estimated_bubble_coverage` is in [0.0, 1.0]
   - Both schema versions validate with `validate_instance`

**Definition of done:** `python -m pytest tests/manga/test_lettering_from_script.py`
passes. No changes to other pipeline stages.

### Task 2 — Bubble Shape + Text Rendering (estimated 3–4 hours)

**Files:** `phoenix_v4/manga/chapter/bubble_render.py` (new), `fonts/` (new)

1. Create `fonts/` directory with `README.txt` listing download sources
2. Implement `_load_font`, `INTENSITY_FONT_SIZES`, `_wrap_text`
3. Implement round/oval, spiky, cloud, square, whisper shapes (Section 5.3)
4. Implement SFX rendering (Section 6)
5. Implement `render_bubbles_onto_panel` (Section 5.1) — single panel, no placement
   algorithm yet (place first bubble at top_right, subsequent at next zone in sequence
   — just to get shapes working)

Unit tests:
   - Each shape renders without crash on a 100×100 white test image
   - Font fallback to `load_default()` does not raise
   - SFX text renders with visible stroke
   - `render_bubbles_onto_panel` returns a dict with required layout fields

**Definition of done:** `python -m pytest tests/manga/test_bubble_shapes.py` passes.
Visual inspection of rendered test panels.

### Task 3 — Placement Algorithm + Coverage + Tails (estimated 2–3 hours)

**Files:** `phoenix_v4/manga/chapter/bubble_render.py` (extend)

1. Implement zone assignment (`_assign_zones`) with reading-order defaults
2. Implement `_compute_bubble_bbox`
3. Implement coverage enforcement loop (Section 5.5)
4. Implement AABB overlap resolution (Section 5.5)
5. Implement tail rendering — pointer tail and dotless tail (Section 5.6)
6. Integrate placement into `render_bubbles_onto_panel`

Unit tests:
   - 4-bubble panel stays under 30% coverage
   - Overlapping bubbles are separated
   - Pointer tail connects to correct bubble edge quadrant
   - Off-panel speaker produces no tail
   - Coverage limit enforcement reduces font size before splitting text

**Definition of done:** `python -m pytest tests/manga/test_bubble_placement.py` passes.
Manual review of output on a real panel image.

### Task 4 — Pipeline Integration + End-to-End Test (estimated 2–3 hours)

**Files:** `stage_ids.py`, `dag_order.py`, `chapter_production.py`, and the new
`build_bubble_layout_spec` function in `bubble_render.py`

1. Add `CHAPTER_BUBBLE_RENDER` to `stage_ids.py` and `ALL_STAGE_IDS`
2. Update `dag_order.py` `RUN_ORDER` and `STAGE_NAMES`
3. Implement `build_bubble_layout_spec` (Section 5.1)
4. Update `produce_chapter_assets` to accept `bubble_render_out` and
   `bubble_style_config` parameters (Section 7)
5. End-to-end integration test using the `DryRunBackend` image backend:
   - Produces `lettering_spec` v2
   - Produces `bubble_layout_spec`
   - Produces `panel_images_manifest_bubbled`
   - `compose_final_page_pngs` runs on bubbled PNGs without error

Unit tests:
   - `CHAPTER_BUBBLE_RENDER` is present in `ALL_STAGE_IDS` and `RUN_ORDER`
   - It appears between `CHAPTER_LETTERING` and `CHAPTER_LAYOUT` in `RUN_ORDER`
   - `produce_chapter_assets` with `bubble_render_out=None` has identical output
     to current behavior (no regression)
   - `produce_chapter_assets` with `bubble_render_out=<tmpdir>` produces
     `bubble_layout_spec` with valid schema

**Definition of done:** `python -m pytest tests/manga/test_chapter_production.py`
passes. `validate_instance(result["bubble_layout_spec"], "bubble_layout_spec")`
does not raise.

---

## Appendix A: `bubble_style_config` Shape Reference

The `bubble_style_config` dict passed to the renderer. It may be embedded in the
series `visual_identity` artifact or passed as a standalone config.

```json
{
  "reading_direction": "right_to_left",
  "locale": "en",
  "default_bubble_fill": [255, 255, 255, 240],
  "default_bubble_outline": [0, 0, 0, 255],
  "default_outline_width": 2,
  "coverage_limit": 0.30,
  "sfx_lexicon": {
    "CRACK": { "font_size": 56, "position": [0.50, 0.50] },
    "SLAM":  { "font_size": 56, "position": [0.50, 0.80] }
  },
  "speech_atoms": {
    "atom_shonen_protagonist_determination_shouting_01": {
      "bubble_style": "spiky_emphasis",
      "font_override": null,
      "tail_style": "pointer"
    }
  }
}
```

All fields are optional. The renderer falls back to the constants defined in Section 5
for any missing keys.

---

## Appendix B: File Manifest

Files that must exist after full implementation:

| Path | Status | Notes |
|---|---|---|
| `phoenix_v4/manga/models/stage_ids.py` | modify | Add `CHAPTER_BUBBLE_RENDER` |
| `phoenix_v4/manga/runner/dag_order.py` | modify | Insert in RUN_ORDER, STAGE_NAMES |
| `phoenix_v4/manga/chapter/lettering_from_script.py` | modify | v2 schema output |
| `phoenix_v4/manga/chapter/chapter_production.py` | modify | bubble_render_out param |
| `phoenix_v4/manga/chapter/bubble_render.py` | create | Full renderer module |
| `schemas/manga/lettering_spec.schema.json` | modify | Add v2 optional fields |
| `schemas/manga/bubble_layout_spec.schema.json` | create | New artifact schema |
| `fonts/README.txt` | create | Font download instructions |
| `fonts/AnimeAce.ttf` | gitignored binary | Download separately |
| `fonts/KomikaTight.ttf` | gitignored binary | Download separately |
| `tests/manga/test_bubble_shapes.py` | create | Task 2 unit tests |
| `tests/manga/test_bubble_placement.py` | create | Task 3 unit tests |

Existing test files must not regress: `tests/manga/test_lettering_from_script.py`,
`tests/manga/test_chapter_production.py`.
