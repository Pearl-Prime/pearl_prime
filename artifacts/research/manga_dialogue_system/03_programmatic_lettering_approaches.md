# Programmatic Lettering Approaches for Manga
## Design Reference Document — Phoenix Omega Manga Pipeline

**Version:** 1.0  
**Date:** 2026-04-17  
**Author:** Pearl_Research  
**Purpose:** Technical reference for implementing manga speech bubble rendering in Python/Pillow

---

## Overview

This document covers the technical landscape of manga lettering tools, open-source libraries, academic research, and provides concrete implementation patterns for the Phoenix Omega pipeline's Python/Pillow-based renderer. The goal is to go from panel image + structured dialogue data to a composited output image with genre-accurate, correctly-placed speech bubbles.

---

## 1. Professional Tools Overview

### 1.1 Clip Studio Paint

The dominant professional tool for manga creation. Relevant to pipeline design as a reference point.

**Balloon tools:**
- CSP provides preset balloon shapes: oval, cloud, jagged/spiky, rectangular
- Each balloon has editable anchor points for reshaping
- "Balloon tail" tool: separate control handle to position and curve the tail
- Snap-to-character feature (beta) for tail auto-pointing

**Font handling:**
- Supports Japanese and Latin fonts
- Vertical/horizontal toggle per bubble
- Per-bubble font override (so one page can mix handwritten SFX and typeset dialogue)
- Built-in balloon text fitting: text auto-shrinks to fit when balloon is too small

**Export:**
- Can export as PSD layers: balloons on separate layer from art, enabling downstream compositing
- CMYK export for print; RGB for digital

**Key limitations informing automation design:**
- Manual placement — artist draws each balloon by hand
- No auto-placement relative to speakers
- No spatial constraint enforcement (coverage %, no-overlap)
- Tail placement is manual — errors common for less experienced letterers
- Localization workflow (Japanese → English translation) requires re-lettering, which is typically fully manual

### 1.2 Adobe Illustrator / Photoshop

Used primarily for Western comic and manga localization lettering.

**Illustrator approach:**
- Balloons as vector shapes (Ellipse tool + Pathfinder for spiky variants)
- Text in Area Type or Point Type inside shape
- Paragraph styles for consistency (Body, Whisper, SFX styles)
- Artboards per page

**Photoshop approach:**
- Balloons often painted on transparent layer
- Text as separate text layer above balloon layer
- Layer groups per bubble (mask + balloon + text)

**Key limitations:** Even more manual than CSP. No tail automation. Text reflow requires manual balloon resize.

### 1.3 InDesign for Manga Adaptation (Western Localization)

Publishers use InDesign for manga adaptation when pages are pre-cleaned (text removed from art).

**Workflow:**
1. Translator provides script
2. Letterer places TIFF panel pages as linked images
3. Balloons drawn as InDesign shapes (oval, rectangle, polygon for spiky)
4. Text flowed into frame
5. Tail as separate shape, grouped
6. Export to PDF/print or JPEG for digital

**Key limitations for automation:**
- InDesign's balloon shapes are not intelligent — no geometry relationship to speaker
- Professional lettering studios use templates and style sheets to speed this up
- No programmatic API that makes InDesign automation practical for high-volume generation

---

## 2. Open Source Tools Catalog

### Panel Cleaner
- **What it does:** Detects and removes existing text/bubbles from manga panels, restores background using inpainting
- **Language/library:** Python, uses manga-ocr for detection + simple-lama-inpainting for restoration
- **Status:** Active (GitHub: dmMaze/PanelCleaner or similar forks)
- **Relevance:** Pre-processing step before re-lettering. If Phoenix Omega needs to restyle existing panels, Panel Cleaner handles text removal.
- **Limitation:** Inpainting quality varies; complex backgrounds lose detail

### Manga-OCR
- **What it does:** Optical character recognition specifically tuned for Japanese manga text in bubbles
- **Language/library:** Python, based on TrOCR/Vision Transformer fine-tuned on manga
- **Status:** Active (GitHub: kha-white/manga-ocr)
- **Relevance:** If pipeline needs to read existing bubble text for translation or content analysis
- **Accuracy:** Very high on standard manga fonts and handwritten Japanese; lower on heavily stylized SFX

### ComicTranslate / BalloonTranslator
- **What it does:** End-to-end pipeline: detect bubbles → OCR → translate → retter in target language
- **Language/library:** Python, integrates with Google Translate / DeepL APIs
- **Status:** Active forks in development
- **Relevance:** Reference implementation for the full pipeline Phoenix Omega targets. Study its bubble placement logic specifically.
- **Limitation:** Bubble placement often poor — uses bounding box of original bubble without genre-aware resizing

### ScanTailor
- **What it does:** Page scanning cleanup — deskew, despeckle, content/margin detection
- **Language/library:** C++ with Qt GUI; Python bindings available (scantailor-advanced)
- **Status:** Forked/advanced versions active
- **Relevance:** Pre-processing if working from scanned pages rather than digital originals

### OpenCV Manga Processing
- **What it does:** Not a single tool — OpenCV is a computer vision library used for:
  - Panel boundary detection (findContours on thresholded image)
  - Bubble detection (Hough circles, contour matching)
  - Character face detection (Haar cascades trained on manga faces, e.g., lbpcascade_animeface)
  - Speech bubble region extraction
- **Language/library:** Python (cv2), C++
- **Status:** Stable library; anime/manga-specific models maintained separately
- **Relevance:** Phoenix Omega can use OpenCV for speaker position detection (find face/character position to aim tail at)

### WebtoonKit / Comic-specific Python libs
- **WebtoonKit:** Primarily a scraping/display tool for webtoon format (vertical scroll). Limited production use.
- **comicapi:** Provides ComicInfo.xml handling, CBZ/CBR format management — useful for manga archive output
- **Pillow (PIL fork):** Core drawing library for Phoenix Omega — see Section 4
- **aggdraw:** Antialiased drawing extension for Pillow — bezier curves, anti-aliased lines

---

## 3. Academic/Research Approaches

### 3.1 Automatic Speech Bubble Detection

**Key papers and approaches:**

**"Speech Bubble Detection and Text Removal in Comics" (various authors, 2010s-2020s)**
- Approach: Threshold → flood fill → connected component analysis
- Identify white/light regions with text inside
- Classify by shape features: circularity ratio, aspect ratio, concavity count (for spiky bubbles)
- Tail detection: find connected narrow region extending from bubble body
- **Tradeoff:** Works well on standard bubbles; fails on borderless text and complex shapes

**YOLO-Based Bubble Detection**
- Multiple papers apply YOLOv5/v8 to manga page object detection
- Classes: speech_bubble, thought_bubble, sfx, narration_box
- Trained on annotated manga datasets (Manga109, eBDtheque)
- **Manga109 dataset:** 109 manga volumes, annotations include speech balloon bounding boxes, character faces, body positions
- Achieves ~85-92% mAP on standard bubble types
- **Tradeoff:** Needs GPU for real-time; overkill if generating new bubbles rather than detecting existing ones

**Semantic Segmentation for Bubble Regions**
- FCN/U-Net approaches trained to pixel-level segment bubble vs. art
- Better boundary accuracy than bounding box approaches
- Useful for bubble shape extraction (copying shape style from reference panels)
- Papers from teams at Waseda, Osaka, and international comics research groups

**"Text-Aware Image Composition" (general field)**
- Problem: place text overlays on images without covering salient regions
- Approaches use saliency maps to find low-information regions
- Most relevant to Phoenix Omega for placement: compute image saliency → find low-saliency zones → place bubbles there
- Libraries: opencv-saliency (StaticSaliencyFineGrained, StaticSaliencySpectralResidual)

### 3.2 Rule-Based vs. Learned Placement Tradeoffs

| Aspect | Rule-Based | ML-Based |
|--------|-----------|----------|
| Explainability | Full — every decision auditable | Black box |
| Genre customization | Easy — just change parameters | Requires retraining |
| Data requirements | None | Large annotated dataset |
| Edge case handling | Manual rules needed | Generalizes if trained on edge cases |
| Speed | Fast (ms) | Slower (100ms-1s per page) |
| Quality ceiling | Moderate — can't match human sensitivity | High with sufficient training data |
| Phoenix Omega fit | **Preferred** for v1 | Future improvement path |

**Recommendation for Phoenix Omega:** Implement rule-based placement in v1 (see Section 6). Document failure modes. In v2, use a small fine-tuned saliency model to improve placement in complex panels.

---

## 4. Python/Pillow Implementation Patterns

### 4.1 Drawing Ellipses and Rounded Rectangles

```python
from PIL import Image, ImageDraw

def draw_oval_bubble(draw: ImageDraw.Draw, x: int, y: int, 
                     w: int, h: int, 
                     fill: str = "white", outline: str = "black", 
                     border_width: int = 2) -> None:
    """Draw a standard oval speech bubble body (no tail)."""
    bbox = [x, y, x + w, y + h]
    draw.ellipse(bbox, fill=fill, outline=outline, width=border_width)

def draw_rounded_rect_bubble(draw: ImageDraw.Draw, x: int, y: int,
                              w: int, h: int, radius: int = 15,
                              fill: str = "white", outline: str = "black",
                              border_width: int = 2) -> None:
    """Draw a rounded-rectangle bubble (narration box style)."""
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=radius,
        fill=fill,
        outline=outline,
        width=border_width
    )
```

Note: `ImageDraw.rounded_rectangle` is available in Pillow >= 8.2.0. Confirm version before use.

### 4.2 Drawing Spiky/Jagged Bubble Outlines

The spiky bubble is constructed as a polygon with alternating inner and outer vertices arranged around an ellipse, with the smoothed ellipse as the base shape.

```python
import math
from PIL import Image, ImageDraw

def compute_spiky_bubble_polygon(cx: float, cy: float, 
                                  rx: float, ry: float,
                                  num_spikes: int = 8,
                                  spike_length: float = 12.0) -> list[tuple[float, float]]:
    """
    Compute polygon vertices for a spiky bubble.
    
    Args:
        cx, cy: Center of the bubble
        rx, ry: Semi-axes of the base ellipse
        num_spikes: Number of spike points (typically 6-16 depending on intensity)
        spike_length: How far spikes extend beyond the ellipse edge
    
    Returns:
        List of (x, y) tuples for polygon
    """
    vertices = []
    total_points = num_spikes * 2  # alternating inner (ellipse) and outer (spike tip)
    
    for i in range(total_points):
        angle = (2 * math.pi * i) / total_points
        
        if i % 2 == 0:
            # Spike tip: beyond the ellipse
            r_x = rx + spike_length
            r_y = ry + spike_length
        else:
            # Inner point: on or slightly inside the ellipse
            r_x = rx * 0.85
            r_y = ry * 0.85
        
        x = cx + r_x * math.cos(angle)
        y = cy + r_y * math.sin(angle)
        vertices.append((x, y))
    
    return vertices

def draw_spiky_bubble(draw: ImageDraw.Draw, cx: int, cy: int,
                       rx: int, ry: int, num_spikes: int = 8,
                       spike_length: float = 12.0,
                       fill: str = "white", outline: str = "black",
                       border_width: int = 2) -> None:
    """Draw a complete spiky speech bubble."""
    vertices = compute_spiky_bubble_polygon(
        cx, cy, rx, ry, num_spikes, spike_length
    )
    draw.polygon(vertices, fill=fill, outline=outline)
    # Re-draw outline at correct width (Pillow polygon outline is always 1px)
    # For thick outlines: draw_polyline workaround needed
    if border_width > 1:
        for i in range(len(vertices)):
            p1 = vertices[i]
            p2 = vertices[(i + 1) % len(vertices)]
            draw.line([p1, p2], fill=outline, width=border_width)
```

**Spike count guidelines by intensity:**
- Surprise/mild shock: 6-8 spikes, spike_length=8
- Anger/shout: 10-12 spikes, spike_length=14
- Scream/explosion: 14-18 spikes, spike_length=20
- Ultra-scream: 18-24 spikes, spike_length=28, double-outlined

### 4.3 Text Wrapping in Bounded Regions

```python
import textwrap
from PIL import ImageFont, ImageDraw

def wrap_text_to_width(text: str, font: ImageFont.FreeTypeFont, 
                        max_width: int) -> list[str]:
    """
    Word-wrap text to fit within max_width pixels using the given font.
    Returns list of lines.
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = " ".join(current_line + [word])
        # getbbox returns (left, top, right, bottom)
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        
        if line_width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(" ".join(current_line))
                current_line = [word]
            else:
                # Single word too long — force it
                lines.append(word)
                current_line = []
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines

def measure_text_block(lines: list[str], font: ImageFont.FreeTypeFont, 
                         line_spacing: int = 4) -> tuple[int, int]:
    """
    Returns (total_width, total_height) of a text block.
    """
    max_width = 0
    total_height = 0
    
    for line in lines:
        bbox = font.getbbox(line)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        max_width = max(max_width, w)
        total_height += h + line_spacing
    
    return max_width, total_height - line_spacing  # remove trailing spacing
```

### 4.4 Font Loading

```python
from PIL import ImageFont
from pathlib import Path

FONT_DIR = Path("/path/to/fonts")

def load_font(font_name: str, size: int) -> ImageFont.FreeTypeFont:
    """Load a TrueType font by name."""
    font_path = FONT_DIR / font_name
    return ImageFont.truetype(str(font_path), size=size)

# Font size constants (adjust for output DPI)
FONT_SIZES = {
    "whisper": 14,
    "normal": 18,
    "emphasis": 20,
    "shout": 24,
    "scream": 32,
    "sfx_small": 24,
    "sfx_large": 48,
    "sfx_huge": 72,
    "caption": 14,
}
```

### 4.5 Anti-Aliasing for Bubble Borders and Text

Pillow's ImageDraw does not natively support anti-aliasing for shapes. Workaround: draw at 2x resolution and downscale.

```python
from PIL import Image, ImageDraw

def draw_with_antialiasing(panel_image: Image.Image, 
                            draw_func,
                            scale: int = 2) -> Image.Image:
    """
    Draw shapes at 2x resolution, then downscale to get anti-aliased result.
    
    Args:
        panel_image: Base panel image
        draw_func: Callable that accepts (Image, ImageDraw) and draws onto it
        scale: Supersampling scale factor (2 is sufficient; 4 for highest quality)
    
    Returns:
        Panel image with anti-aliased drawing composited
    """
    w, h = panel_image.size
    # Create high-res blank canvas
    hires = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    hires_draw = ImageDraw.Draw(hires)
    
    # Draw at scaled coordinates — caller scales all coordinates by `scale`
    draw_func(hires, hires_draw, scale=scale)
    
    # Downscale back to original size with LANCZOS anti-aliasing
    downscaled = hires.resize((w, h), Image.LANCZOS)
    
    # Composite onto panel
    result = panel_image.copy().convert("RGBA")
    result = Image.alpha_composite(result, downscaled)
    
    return result
```

### 4.6 Alpha Compositing (Bubble Layer over Panel Image)

```python
from PIL import Image

def composite_bubble_layer(panel: Image.Image, 
                            bubble_layer: Image.Image) -> Image.Image:
    """
    Composite a bubble layer (RGBA with transparency) onto a panel image.
    
    The bubble_layer should be RGBA where:
    - Bubble body: white or filled color at full opacity
    - Bubble border: black at full opacity
    - Empty areas: fully transparent (alpha=0)
    """
    panel_rgba = panel.convert("RGBA")
    result = Image.alpha_composite(panel_rgba, bubble_layer)
    return result.convert("RGB")  # Convert back to RGB for final output

def create_bubble_layer(size: tuple[int, int]) -> tuple[Image.Image, object]:
    """Create a blank transparent layer for bubble drawing."""
    from PIL import ImageDraw
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    return layer, draw
```

### 4.7 Computing Text Bounding Box to Size Bubble Automatically

```python
def compute_bubble_size_for_text(text: str, font, 
                                   max_bubble_width: int,
                                   padding_x: int = 16,
                                   padding_y: int = 12,
                                   min_width: int = 60,
                                   min_height: int = 35) -> tuple[int, int]:
    """
    Given text and font, compute the bubble width and height needed.
    
    Returns (bubble_width, bubble_height) including padding.
    """
    # Available text width inside bubble
    text_width = max_bubble_width - (2 * padding_x)
    
    # Wrap text
    lines = wrap_text_to_width(text, font, text_width)
    text_w, text_h = measure_text_block(lines, font)
    
    bubble_w = max(min_width, text_w + 2 * padding_x)
    bubble_h = max(min_height, text_h + 2 * padding_y)
    
    return bubble_w, bubble_h

def auto_size_bubble(text: str, font, panel_width: int, panel_height: int,
                      max_width_fraction: float = 0.40,
                      max_height_fraction: float = 0.25) -> tuple[int, int, list[str]]:
    """
    Auto-size bubble within panel constraints.
    Returns (bubble_w, bubble_h, wrapped_lines).
    """
    max_bubble_width = int(panel_width * max_width_fraction)
    max_bubble_height = int(panel_height * max_height_fraction)
    
    bubble_w, bubble_h = compute_bubble_size_for_text(
        text, font, max_bubble_width
    )
    
    # If bubble_h exceeds max, reduce font size and retry (caller responsibility)
    if bubble_h > max_bubble_height:
        # Signal to caller that font reduction is needed
        return bubble_w, bubble_h, []
    
    text_width = bubble_w - 32  # subtract padding
    lines = wrap_text_to_width(text, font, text_width)
    return bubble_w, bubble_h, lines
```

### 4.8 Rendering Bubble Tails

**Triangular pointer tail:**

```python
def compute_pointer_tail(bubble_rect: tuple[int, int, int, int],
                          speaker_pos: tuple[int, int],
                          tail_width: int = 12) -> list[tuple[int, int]]:
    """
    Compute triangle vertices for a pointer tail.
    
    Args:
        bubble_rect: (x, y, w, h) of bubble bounding box
        speaker_pos: (sx, sy) approximate position of speaker's mouth
        tail_width: Width of tail base on bubble edge
    
    Returns:
        List of 3 (x, y) tuples forming the triangle
    """
    bx, by, bw, bh = bubble_rect
    sx, sy = speaker_pos
    
    # Find which edge of the bubble is closest to the speaker
    bubble_cx = bx + bw / 2
    bubble_cy = by + bh / 2
    
    dx = sx - bubble_cx
    dy = sy - bubble_cy
    
    # Determine attachment edge
    if abs(dx) > abs(dy):
        if dx > 0:  # speaker is to the right
            attach_x = bx + bw
            attach_y = bubble_cy
            p1 = (attach_x, attach_y - tail_width // 2)
            p2 = (attach_x, attach_y + tail_width // 2)
        else:  # speaker is to the left
            attach_x = bx
            attach_y = bubble_cy
            p1 = (attach_x, attach_y - tail_width // 2)
            p2 = (attach_x, attach_y + tail_width // 2)
    else:
        if dy > 0:  # speaker is below
            attach_x = bubble_cx
            attach_y = by + bh
            p1 = (attach_x - tail_width // 2, attach_y)
            p2 = (attach_x + tail_width // 2, attach_y)
        else:  # speaker is above
            attach_x = bubble_cx
            attach_y = by
            p1 = (attach_x - tail_width // 2, attach_y)
            p2 = (attach_x + tail_width // 2, attach_y)
    
    tip = (sx, sy)
    return [p1, p2, tip]

def draw_bubble_tail(draw, tail_vertices: list[tuple[int, int]],
                      fill: str = "white", outline: str = "black",
                      border_width: int = 2) -> None:
    """Draw the tail triangle."""
    draw.polygon(tail_vertices, fill=fill)
    # Draw outline lines (excluding the base — that's covered by bubble body)
    draw.line([tail_vertices[0], tail_vertices[2]], fill=outline, width=border_width)
    draw.line([tail_vertices[1], tail_vertices[2]], fill=outline, width=border_width)
```

**Bezier curve tail (aggdraw):**

```python
# Requires: pip install aggdraw
import aggdraw
from PIL import Image

def draw_curved_tail_aggdraw(image: Image.Image,
                              base_p1: tuple, base_p2: tuple,
                              tip: tuple,
                              control_offset: int = 20) -> Image.Image:
    """
    Draw a curved (bezier) tail using aggdraw for anti-aliased curves.
    Used for soft/emotional bubble tails (shōjo, iyashikei).
    """
    canvas = aggdraw.Draw(image)
    brush = aggdraw.Brush("white")
    pen = aggdraw.Pen("black", width=2)
    
    # Control point for bezier curve
    mid_x = (base_p1[0] + base_p2[0]) / 2
    mid_y = (base_p1[1] + base_p2[1]) / 2
    ctrl = (mid_x + control_offset, mid_y + control_offset)
    
    path = aggdraw.Path()
    path.moveto(*base_p1)
    path.curveto(ctrl[0], ctrl[1], ctrl[0], ctrl[1], *tip)
    path.lineto(*base_p2)
    path.close()
    
    canvas.path(path, pen, brush)
    canvas.flush()
    return image
```

### 4.9 Drop Shadow / Border Effect Techniques

```python
from PIL import Image, ImageFilter

def add_drop_shadow(bubble_layer: Image.Image, 
                     offset: tuple[int, int] = (3, 3),
                     shadow_color: tuple = (0, 0, 0, 100),
                     blur_radius: int = 4) -> Image.Image:
    """
    Add a drop shadow behind a bubble layer.
    Returns a new layer with shadow + original composited.
    """
    w, h = bubble_layer.size
    
    # Create shadow image
    shadow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    # Extract alpha mask from bubble
    r, g, b, alpha = bubble_layer.split()
    
    # Create shadow color fill
    shadow_fill = Image.new("RGBA", (w, h), shadow_color)
    shadow.paste(shadow_fill, mask=alpha)
    
    # Blur the shadow
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Create result canvas
    result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    
    # Paste shadow at offset
    ox, oy = offset
    result.paste(shadow, (ox, oy), shadow)
    
    # Composite original bubble over shadow
    result = Image.alpha_composite(result, bubble_layer)
    
    return result

def add_double_outline(draw, shape_draw_func, outline_color: str = "black",
                        inner_color: str = "white", 
                        outer_width: int = 4, inner_width: int = 2) -> None:
    """
    Draw a double-outlined bubble (thick outer, thin inner white gap).
    Common for scream bubbles in shōnen.
    """
    # Draw thick outer outline
    shape_draw_func(draw, outline=outline_color, border_width=outer_width)
    # Draw inner white gap
    shape_draw_func(draw, outline=inner_color, border_width=inner_width)
```

---

## 5. SVG-Based Approach

### 5.1 SVG Advantages for Scalable Bubbles

- Resolution-independent: same bubble SVG scales to print (300dpi) or web (96dpi) without quality loss
- Parameterized templates: SVG allows CSS variables / JS parameters to resize bubbles programmatically
- Text flow: SVG `<foreignObject>` can embed HTML text with word-wrap
- Path-based bubbles: spiky and curved shapes defined as smooth bezier paths rather than polygon approximations
- Better anti-aliasing than Pillow by default (browser or librsvg renders at full quality)

### 5.2 Python SVG Libraries

| Library | Capability | Notes |
|---------|-----------|-------|
| **svgwrite** | Write SVG from Python | Clean API; no rendering |
| **lxml** | Parse/write SVG as XML | Lower level; full control |
| **cairosvg** | SVG → PNG conversion | Uses Cairo; requires libcairo |
| **svglib + reportlab** | SVG → PDF/PNG pipeline | Used in some comics workflows |
| **Wand (ImageMagick)** | SVG import + compositing | Depends on system Inkscape/rsvg |

### 5.3 Parameterized Bubble Template in SVG

```python
import svgwrite

def create_oval_bubble_svg(text: str, cx: float, cy: float, 
                             rx: float, ry: float,
                             font_size: int = 16) -> str:
    """Generate SVG string for an oval bubble with text."""
    dwg = svgwrite.Drawing(size=(f"{cx*2}", f"{cy*2}"))
    
    # Bubble fill
    dwg.add(dwg.ellipse(
        center=(cx, cy), 
        r=(rx, ry),
        fill="white",
        stroke="black",
        stroke_width=2
    ))
    
    # Text (centered)
    dwg.add(dwg.text(
        text,
        insert=(cx, cy),
        text_anchor="middle",
        dominant_baseline="middle",
        font_family="Komika Axis",
        font_size=font_size,
        fill="black"
    ))
    
    return dwg.tostring()
```

### 5.4 SVG → PNG Pipeline for Compositing

```python
import cairosvg
from PIL import Image
import io

def svg_bubble_to_pil(svg_string: str) -> Image.Image:
    """Convert SVG bubble to PIL Image for compositing."""
    png_bytes = cairosvg.svg2png(bytestring=svg_string.encode())
    return Image.open(io.BytesIO(png_bytes)).convert("RGBA")
```

**Recommendation for Phoenix Omega:** Use Pillow/PIL for v1 (simpler dependency chain, adequate quality). Evaluate SVG approach in v2 if quality requirements increase (e.g., print-resolution output).

---

## 6. Open Source Manga Fonts

All fonts below are usable without commercial licensing restrictions (OFL or similar).

| Font Name | License | Best Use Case | Genres | Source |
|-----------|---------|---------------|--------|--------|
| **Komika Axis** | Freeware (commercial use permitted) | Body text, standard speech | Shōnen, Isekai, General | dafont.com/blambot |
| **Anime Ace** | Freeware | Dialogue, versatile | General, most genres | blambot.com |
| **CC Wild Words** | CC BY-SA | Standard comic body | All genres | letterer-blambot releases |
| **Bangers** | OFL | Loud titles, SFX overlay | Shōnen, Sports, SFX | Google Fonts |
| **Noto Sans JP** | OFL | Japanese text, fallback | All (Japanese content) | Google Fonts |
| **Permanent Marker** | Apache 2.0 | Handwritten notes, informal | Slice of life, BL/GL notes | Google Fonts |
| **Creepster** | OFL | Horror captions, disturbing text | Horror, supernatural isekai | Google Fonts |
| **Comic Neue** | OFL | Friendly, readable body | Kodomomuke, josei, soft shōjo | comicneue.com |
| **Luckiest Guy** | Apache 2.0 | Big SFX, chapter titles | Shōnen, sports | Google Fonts |
| **Audiowide** | OFL | Robotic/tech speech, mecha comms | Mecha, sci-fi isekai | Google Fonts |
| **Special Elite** | Apache 2.0 | Typewriter/old documents | Horror, seinen (documents) | Google Fonts |
| **Rock Salt** | Apache 2.0 | Rough handwritten | Grunge, seinen, horror | Google Fonts |
| **Cabin Sketch** | OFL | Sketchy/informal | Slice of life, kodomomuke | Google Fonts |
| **Ultra** | Apache 2.0 | Bold declarations, ultra-spiky bubbles | Shōnen peak moments | Google Fonts |
| **Oswald** | OFL | Clean narration boxes | Seinen, narration | Google Fonts |
| **Kalam** | OFL | Handwritten diary/letter | Shōjo letters, josei notes | Google Fonts |
| **Exo 2** | OFL | Electronic/system voice | Mecha, isekai status screens | Google Fonts |
| **Libre Baskerville** | OFL | Formal narration, villain speeches | Seinen, villain monologue | Google Fonts |

**Recommended Phoenix Omega font stack:**

```python
FONT_MAP = {
    # Bubble body text by genre
    "shonen_body": "KomikaAxis.ttf",
    "shojo_body": "ComicNeue-Regular.ttf",
    "seinen_body": "AnimeAce.ttf",
    "horror_body": "AnimeAce.ttf",   # deliberately plain — see doc 01
    "horror_caption": "SpecialElite-Regular.ttf",
    "isekai_system": "Audiowide-Regular.ttf",
    "mecha_comms": "Audiowide-Regular.ttf",
    "sfx_general": "Bangers-Regular.ttf",
    "sfx_horror": "RockSalt-Regular.ttf",
    "handwritten": "PermanentMarker-Regular.ttf",
    "narration": "Oswald-Regular.ttf",
    "japanese_fallback": "NotoSansJP-Regular.otf",
}
```

---

## 7. Bubble Placement Algorithm Design

### 7.1 Full Algorithm Specification

```python
"""
ALGORITHM: place_bubbles_for_panel

INPUT:  panel_image (PIL.Image), 
        dialogue_entries: List[DialogueEntry]
        
        where DialogueEntry = {
            speaker_position_hint: Literal["top_left", "top_right", 
                                           "bottom_left", "bottom_right",
                                           "center", "off_panel"],
            text: str,
            emotion: Literal["neutral", "happy", "angry", "fearful", 
                             "sad", "surprised", "whisper", "shout", "scream"],
            intensity: int  # 1-10 scale
        }

OUTPUT: List[BubblePlacement]
        where BubblePlacement = {
            x: int, y: int,       # top-left corner
            w: int, h: int,       # bubble dimensions
            bubble_type: str,     # "oval", "spiky", "cloud", "rect", "whisper"
            tail_direction: str,  # "down_left", "down_right", "up_left", "up_right", "none"
            speaker_pos: tuple,   # (x, y) for tail tip
            text: str,
            font_size: int,
            wrapped_lines: List[str]
        }
"""

def place_bubbles_for_panel(panel_image, dialogue_entries, genre="shonen"):
    """Main placement orchestrator."""
    w, h = panel_image.size
    placements = []
    
    # STEP 1: Define placement zones
    zones = define_placement_zones(w, h)
    
    # STEP 2: Assign zones to entries by reading order
    assigned = assign_zones_to_entries(dialogue_entries, zones)
    
    # STEP 3: For each entry, compute bubble
    for entry, zone in assigned:
        font, font_size = select_font(entry["emotion"], entry["intensity"], genre)
        
        bw, bh, lines = auto_size_bubble(
            entry["text"], font, zone["max_w"], zone["max_h"]
        )
        
        # Retry with smaller font if too large
        while not lines and font_size > 10:
            font_size -= 1
            font = load_font(font.path, font_size)
            bw, bh, lines = auto_size_bubble(
                entry["text"], font, zone["max_w"], zone["max_h"]
            )
        
        # Position bubble within zone
        bx, by = position_in_zone(zone, bw, bh, entry["speaker_position_hint"])
        
        # Determine bubble type from emotion/intensity
        bubble_type = select_bubble_type(entry["emotion"], entry["intensity"])
        
        # Compute tail direction
        tail_dir, speaker_xy = compute_tail(
            bx, by, bw, bh, entry["speaker_position_hint"], w, h
        )
        
        placements.append({
            "x": bx, "y": by, "w": bw, "h": bh,
            "bubble_type": bubble_type,
            "tail_direction": tail_dir,
            "speaker_pos": speaker_xy,
            "text": entry["text"],
            "font_size": font_size,
            "wrapped_lines": lines
        })
    
    # STEP 4: Coverage check
    placements = enforce_coverage_limit(placements, w, h, max_fraction=0.30)
    
    # STEP 5: Overlap resolution
    placements = resolve_overlaps(placements, margin=4)
    
    return placements
```

### 7.2 Zone Definitions

```python
def define_placement_zones(panel_w: int, panel_h: int) -> dict:
    """
    Define safe bubble placement zones.
    Center of panel is reserved for character art.
    """
    return {
        # Reading-order primary zones (Japanese: right-to-left, top-to-bottom)
        "A": {  # Top-right — first speaker
            "x": int(panel_w * 0.55), "y": int(panel_h * 0.02),
            "max_w": int(panel_w * 0.42), "max_h": int(panel_h * 0.30),
            "priority": 1
        },
        "B": {  # Top-left — second speaker
            "x": int(panel_w * 0.02), "y": int(panel_h * 0.02),
            "max_w": int(panel_w * 0.42), "max_h": int(panel_h * 0.30),
            "priority": 2
        },
        "C": {  # Top-center — single dominant speaker or narrator
            "x": int(panel_w * 0.20), "y": int(panel_h * 0.02),
            "max_w": int(panel_w * 0.60), "max_h": int(panel_h * 0.20),
            "priority": 3
        },
        "D": {  # Bottom-right — third speaker
            "x": int(panel_w * 0.55), "y": int(panel_h * 0.68),
            "max_w": int(panel_w * 0.42), "max_h": int(panel_h * 0.28),
            "priority": 4
        },
        "E": {  # Bottom-left — fourth speaker
            "x": int(panel_w * 0.02), "y": int(panel_h * 0.68),
            "max_w": int(panel_w * 0.42), "max_h": int(panel_h * 0.28),
            "priority": 5
        },
        "N": {  # Narrator/caption strip — top full width
            "x": 0, "y": 0,
            "max_w": panel_w, "max_h": int(panel_h * 0.12),
            "priority": 0,  # Pre-assigned for narration
            "type": "caption"
        },
        "NB": {  # Narrator strip — bottom full width
            "x": 0, "y": int(panel_h * 0.88),
            "max_w": panel_w, "max_h": int(panel_h * 0.12),
            "priority": 0,
            "type": "caption"
        }
    }
```

### 7.3 Bubble Type Selection

```python
def select_bubble_type(emotion: str, intensity: int) -> str:
    """Map emotion + intensity to bubble shape type."""
    if emotion == "whisper":
        return "whisper"
    elif emotion in ("angry", "shout", "scream") and intensity >= 7:
        return "scream"
    elif emotion in ("angry", "shout", "surprised") and intensity >= 4:
        return "spiky"
    elif emotion in ("thought", "internal"):
        return "cloud"
    elif emotion == "robotic":
        return "electronic"
    elif emotion == "horror":
        return "drip"
    elif intensity <= 2 and emotion == "neutral":
        return "oval"
    else:
        return "oval"  # default

SPIKE_COUNT_MAP = {
    "spiky": (8, 10.0),     # (num_spikes, spike_length)
    "scream": (16, 22.0),
    "ultra": (22, 30.0),
}
```

### 7.4 Coverage Enforcement

```python
def enforce_coverage_limit(placements: list, 
                             panel_w: int, panel_h: int,
                             max_fraction: float = 0.30) -> list:
    """
    If total bubble area exceeds max_fraction of panel area,
    scale down font sizes until compliant.
    """
    panel_area = panel_w * panel_h
    max_bubble_area = panel_area * max_fraction
    
    for _ in range(10):  # max 10 iterations
        total_area = sum(p["w"] * p["h"] for p in placements)
        if total_area <= max_bubble_area:
            break
        
        # Reduce all font sizes by 1
        for p in placements:
            if p["font_size"] > 10:
                p["font_size"] -= 1
                font = load_font(get_font_path(p), p["font_size"])
                bw, bh, lines = auto_size_bubble(
                    p["text"], font, p["w"], panel_h
                )
                if lines:
                    p["w"], p["h"] = bw, bh
                    p["wrapped_lines"] = lines
    
    return placements
```

### 7.5 Overlap Resolution

```python
def resolve_overlaps(placements: list, margin: int = 4) -> list:
    """
    Simple AABB (axis-aligned bounding box) collision detection.
    Push overlapping bubbles apart.
    Max 20 iterations to avoid infinite loop.
    """
    def overlaps(a, b):
        return not (
            a["x"] + a["w"] + margin <= b["x"] or
            b["x"] + b["w"] + margin <= a["x"] or
            a["y"] + a["h"] + margin <= b["y"] or
            b["y"] + b["h"] + margin <= a["y"]
        )
    
    def push_apart(a, b):
        """Push b away from a."""
        overlap_x = (a["x"] + a["w"] // 2) - (b["x"] + b["w"] // 2)
        overlap_y = (a["y"] + a["h"] // 2) - (b["y"] + b["h"] // 2)
        
        if abs(overlap_x) > abs(overlap_y):
            shift = (a["w"] + b["w"]) // 2 + margin
            b["x"] = a["x"] - shift if overlap_x > 0 else a["x"] + shift
        else:
            shift = (a["h"] + b["h"]) // 2 + margin
            b["y"] = a["y"] - shift if overlap_y > 0 else a["y"] + shift
    
    for _ in range(20):
        changed = False
        for i in range(len(placements)):
            for j in range(i + 1, len(placements)):
                if overlaps(placements[i], placements[j]):
                    push_apart(placements[i], placements[j])
                    changed = True
        if not changed:
            break
    
    return placements
```

### 7.6 Three or More Speakers

When 3+ speakers appear in a single panel:

1. **Cascade zones:** A → B → D → E in reading order
2. **Reduce font size** for all bubbles by 2pt to create space
3. **Group bubbles near speakers:** If speaker positions are known, cluster bubbles near their half of the panel
4. **Crowd/group speech:** Merge multiple speakers with same text into one bubble with multiple tails (or use single "crowd cheer" bubble in top-center)
5. **Stack vertically:** In some cases, two bubbles from the same speaker at different moments stack with slight offset — use vertical alignment, same tail direction

### 7.7 SFX Placement

SFX are not speech bubbles — they are typographic elements drawn directly into the art.

```python
def place_sfx(panel_image, sfx_text: str, 
               zone_hint: str = "action",
               style: str = "shonen") -> dict:
    """
    Place a sound effect label.
    Returns placement parameters (not composited — caller handles rendering).
    """
    w, h = panel_image.size
    
    font_size = {
        "shonen": 48,    # Big, bold, fills space
        "horror": 24,    # Small, unsettling placement
        "iyashikei": 28, # Medium, friendly
        "seinen": 36,    # Medium-large
    }.get(style, 36)
    
    # SFX placement: near center of action zone, rotated
    sfx_angle = random.choice([-15, -10, 0, 10, 15])  # slight tilt
    
    # Rough placement — production use should detect action zone via saliency
    placement_zone = {
        "action": (w * 0.25, h * 0.35),     # Center-left of panel
        "impact": (w * 0.45, h * 0.45),     # Center
        "background": (w * 0.70, h * 0.60), # Background area
    }.get(zone_hint, (w * 0.45, h * 0.45))
    
    return {
        "x": int(placement_zone[0]),
        "y": int(placement_zone[1]),
        "text": sfx_text,
        "font_size": font_size,
        "angle": sfx_angle,
        "type": "sfx"
    }
```

### 7.8 Narrator Caption Boxes

Caption boxes always use the full-width strip zones (N for top, NB for bottom). They never have tails. They use rectangular (not oval) borders.

```python
def create_narrator_caption(text: str, position: str = "top",
                              panel_w: int = 800,
                              panel_h: int = 1200) -> dict:
    """Create a narrator caption box placement."""
    strip_h = int(panel_h * 0.10)  # 10% height strip
    
    return {
        "x": 4,
        "y": 4 if position == "top" else panel_h - strip_h - 4,
        "w": panel_w - 8,
        "h": strip_h,
        "bubble_type": "rect",
        "tail_direction": "none",
        "speaker_pos": None,
        "text": text,
        "font_size": 14,
        "is_caption": True
    }
```

---

## 8. Integration Summary: Phoenix Omega Rendering Pipeline

The recommended v1 pipeline order:

```
1. RECEIVE: panel_image (PIL.Image), dialogue_data (List[DialogueEntry]), genre
2. DETECT speakers (optional): use OpenCV face detection for tail targeting
3. PLAN: place_bubbles_for_panel() → List[BubblePlacement]
4. CREATE: bubble_layer = Image.new("RGBA", panel_size, (0,0,0,0))
5. FOR each placement:
   a. Draw bubble body (oval/spiky/cloud/rect) onto bubble_layer
   b. Draw tail onto bubble_layer (pointer or curved)
   c. Render text with wrap onto bubble_layer
6. COMPOSITE: alpha_composite(panel_rgba, bubble_layer)
7. EXPORT: save as RGB PNG
```

**Dependencies (pip):**
```
Pillow>=9.0.0
aggdraw>=1.3.11          # optional: curved tails
cairosvg>=2.5.2          # optional: SVG approach
opencv-python>=4.7.0     # optional: face/speaker detection
numpy>=1.23.0            # optional: saliency computation
```

---

*End of Document 03 — Programmatic Lettering Approaches*
