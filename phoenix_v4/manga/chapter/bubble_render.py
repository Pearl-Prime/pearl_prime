"""Manga speech bubble renderer (Pillow-based).

Pipeline stage: CHAPTER_BUBBLE_RENDER
Slot:           after CHAPTER_LETTERING, before CHAPTER_LAYOUT (page_compose)

Architecture
------------
Option A (pre-composition): bubbles are composited onto individual panel PNGs
before page_compose tiles them into page strips.  This preserves per-panel
coordinate systems, coverage limits, and reading-order assignment.

For each panel with ``silence_confirmed=False`` in lettering_spec_v2:
  1. Open the panel PNG from ``panel_images_manifest``.
  2. For each ``dialogue_line`` in the lettering spec, place a bubble.
  3. Render SFX directly on the art (no bubble wrapper).
  4. Render narrator captions as full-width caption strips.
  5. Write a new PNG named ``{original_stem}_bubbled.png``.
  6. Return an updated manifest pointing at the new files.

Public API
----------
``render_bubbles_on_panels(chapter_script, lettering_spec, panel_images_manifest,
                            bubble_style_config, out_dir)``
    → updated panel_images_manifest (dict)

``render_bubbles_onto_panel(panel_image_path, dialogue_lines, sfx, narrator_caption,
                             *, bubble_style_config, out_path, coverage_limit)``
    → bubble_layout record (dict)
"""

from __future__ import annotations

import copy
import math
import textwrap
from pathlib import Path
from typing import Any, Mapping, Sequence

# ---------------------------------------------------------------------------
# Font helpers
# ---------------------------------------------------------------------------

_FONT_SIZES: dict[str, int] = {
    "whisper": 10,
    "calm": 12,
    "normal": 14,
    "excited": 16,
    "shouting": 18,
    "screaming": 22,
    "internal": 11,
}

_FONT_CACHE: dict[tuple[str, int], Any] = {}


def _get_font(intensity: str = "normal", bold: bool = False) -> Any:
    """Return a PIL ImageFont.  Falls back to default if no TTF is found."""
    from PIL import ImageFont

    size = _FONT_SIZES.get(intensity, 14)
    key = (intensity, int(bold))
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    # Try project fonts first, then system fallbacks
    candidate_paths: list[Path] = []
    repo_root = Path(__file__).resolve().parents[3]
    fonts_dir = repo_root / "fonts" / "manga"
    if fonts_dir.is_dir():
        for p in sorted(fonts_dir.glob("*.ttf")) + sorted(fonts_dir.glob("*.otf")):
            candidate_paths.append(p)

    # Common system paths
    system_fallbacks = [
        Path("/System/Library/Fonts/Helvetica.ttc"),
        Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"),
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/Windows/Fonts/arial.ttf"),
    ]
    candidate_paths.extend(p for p in system_fallbacks if p.exists())

    font = None
    for p in candidate_paths:
        try:
            font = ImageFont.truetype(str(p), size=size)
            break
        except Exception:
            continue

    if font is None:
        font = ImageFont.load_default()

    _FONT_CACHE[key] = font
    return font


# ---------------------------------------------------------------------------
# Geometry helpers
# ---------------------------------------------------------------------------

BBox = tuple[int, int, int, int]  # x1, y1, x2, y2


def _text_bbox(text: str, font: Any, draw: Any) -> tuple[int, int]:
    """Return (text_w, text_h) for the given text+font."""
    try:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    except AttributeError:
        # Older Pillow
        w, h = draw.textsize(text, font=font)
        return w, h


def _wrap_text(text: str, font: Any, draw: Any, max_width: int) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    if not text:
        return []
    words = text.split()
    if not words:
        return []

    # Estimate characters-per-line from M-width
    try:
        m_bbox = draw.textbbox((0, 0), "M", font=font)
        char_w = max(1, m_bbox[2] - m_bbox[0])
    except AttributeError:
        char_w = max(1, draw.textsize("M", font=font)[0])

    chars_per_line = max(8, max_width // char_w)
    lines = textwrap.wrap(text, width=chars_per_line)
    return lines if lines else [text]


def _measure_wrapped(lines: list[str], font: Any, draw: Any) -> tuple[int, int]:
    """Return (total_w, total_h) for a block of wrapped lines."""
    if not lines:
        return 0, 0
    widths = []
    heights = []
    for line in lines:
        w, h = _text_bbox(line, font, draw)
        widths.append(w)
        heights.append(h)
    return max(widths), sum(heights) + max(0, (len(lines) - 1) * 2)


# ---------------------------------------------------------------------------
# Zone-to-pixel conversion
# ---------------------------------------------------------------------------

# Fractional zones: (x1_frac, y1_frac, x2_frac, y2_frac)
_ZONE_FRACTIONS: dict[str, tuple[float, float, float, float]] = {
    "top_right":    (0.52, 0.03, 0.98, 0.32),
    "top_left":     (0.02, 0.03, 0.48, 0.32),
    "top_center":   (0.20, 0.03, 0.80, 0.25),
    "bottom_left":  (0.02, 0.68, 0.48, 0.97),
    "bottom_right": (0.52, 0.68, 0.98, 0.97),
    "bottom_center":(0.20, 0.72, 0.80, 0.97),
    "center_left":  (0.02, 0.38, 0.44, 0.62),
    "center_right": (0.56, 0.38, 0.98, 0.62),
}


def _zone_to_pixels(zone: str, pw: int, ph: int) -> BBox:
    x1f, y1f, x2f, y2f = _ZONE_FRACTIONS.get(zone, (0.52, 0.03, 0.98, 0.32))
    return (int(x1f * pw), int(y1f * ph), int(x2f * pw), int(y2f * ph))


# ---------------------------------------------------------------------------
# Bubble shape drawers
# ---------------------------------------------------------------------------

def _draw_round_bubble(
    draw: Any,
    bbox: BBox,
    *,
    fill: tuple = (255, 255, 255, 230),
    outline: tuple = (0, 0, 0, 255),
    width: int = 2,
) -> None:
    """Draw a round/oval speech bubble (standard dialogue)."""
    draw.ellipse(bbox, fill=fill, outline=outline, width=width)


def _draw_spiky_bubble(
    draw: Any,
    bbox: BBox,
    *,
    fill: tuple = (255, 255, 255, 230),
    outline: tuple = (0, 0, 0, 255),
    spike_count: int = 12,
    spike_height: int = 10,
    width: int = 2,
) -> None:
    """Draw a jagged/spiky bubble for shouts and emphasis."""
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    rx = (x2 - x1) / 2
    ry = (y2 - y1) / 2
    points: list[tuple[float, float]] = []
    total_pts = spike_count * 2
    for i in range(total_pts):
        angle = 2 * math.pi * i / total_pts
        # Alternate between inner ellipse and outer spikes
        if i % 2 == 0:
            r_x, r_y = rx, ry
        else:
            r_x = rx + spike_height
            r_y = ry + spike_height
        px = cx + r_x * math.cos(angle)
        py = cy + r_y * math.sin(angle)
        points.append((px, py))
    draw.polygon(points, fill=fill, outline=outline)


def _draw_cloud_bubble(
    draw: Any,
    bbox: BBox,
    *,
    fill: tuple = (255, 255, 255, 200),
    outline: tuple = (80, 80, 80, 255),
    width: int = 2,
) -> None:
    """Draw a cloud/thought bubble (scalloped edges)."""
    x1, y1, x2, y2 = bbox
    w = x2 - x1
    h = y2 - y1
    # Main body ellipse
    draw.ellipse(bbox, fill=fill, outline=outline, width=width)
    # Scallops: small circles around the perimeter
    scallop_r = max(6, min(w, h) // 8)
    cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
    rx, ry = w / 2 - scallop_r // 2, h / 2 - scallop_r // 2
    n_scallops = max(6, int(2 * math.pi * max(rx, ry) / (scallop_r * 2.2)))
    for i in range(n_scallops):
        angle = 2 * math.pi * i / n_scallops
        sx = cx + rx * math.cos(angle)
        sy = cy + ry * math.sin(angle)
        sr = scallop_r
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=fill, outline=outline, width=width,
        )


def _draw_caption_box(
    draw: Any,
    bbox: BBox,
    *,
    fill: tuple = (0, 0, 0, 180),
    outline: tuple = (200, 200, 200, 255),
    width: int = 1,
) -> None:
    """Draw a narrator caption box (rectangle with semi-transparent fill)."""
    draw.rectangle(bbox, fill=fill, outline=outline, width=width)


def _draw_whisper_bubble(
    draw: Any,
    bbox: BBox,
    *,
    fill: tuple = (255, 255, 255, 180),
    outline: tuple = (100, 100, 100, 200),
    dash_len: int = 6,
    gap_len: int = 4,
    width: int = 1,
) -> None:
    """Draw a dashed-border ellipse for whispered dialogue."""
    # Fill first
    draw.ellipse(bbox, fill=fill, outline=None)
    # Approximate dashed border by drawing arc segments
    x1, y1, x2, y2 = bbox
    cx = (x1 + x2) / 2
    cy = (y1 + y2) / 2
    rx = (x2 - x1) / 2
    ry = (y2 - y1) / 2
    circumference = math.pi * (3 * (rx + ry) - math.sqrt((3 * rx + ry) * (rx + 3 * ry)))
    n_segments = max(8, int(circumference / (dash_len + gap_len)))
    for i in range(n_segments):
        if i % 2 == 1:  # gaps
            continue
        start_angle = 360 * i / n_segments
        end_angle = 360 * (i + 0.55) / n_segments
        draw.arc(bbox, start=start_angle, end=end_angle, fill=outline, width=width)


def _draw_scream_bubble(
    draw: Any,
    bbox: BBox,
    *,
    fill: tuple = (255, 240, 200, 230),
    outline: tuple = (200, 0, 0, 255),
    width: int = 3,
) -> None:
    """Ultra-jagged bubble for screaming (many spikes, colored border)."""
    _draw_spiky_bubble(
        draw, bbox,
        fill=fill, outline=outline,
        spike_count=18, spike_height=14, width=width,
    )


_BUBBLE_DRAWERS = {
    "round_normal": _draw_round_bubble,
    "spiky_emphasis": _draw_spiky_bubble,
    "cloud_thought": _draw_cloud_bubble,
    "square_narration": _draw_caption_box,
    "whisper_dashed": _draw_whisper_bubble,
    "scream_ultra": _draw_scream_bubble,
    "shojo_soft": _draw_round_bubble,   # round with softer style — handled via fill alpha
    "electronic_sharp": _draw_caption_box,  # sharp rectangle
    "drip_horror": _draw_round_bubble,  # placeholder; TODO drip edges
}


# ---------------------------------------------------------------------------
# Tail renderer
# ---------------------------------------------------------------------------

def _draw_tail_pointer(
    draw: Any,
    bubble_bbox: BBox,
    tail_target: tuple[int, int],
    *,
    fill: tuple = (255, 255, 255, 230),
    outline: tuple = (0, 0, 0, 255),
    tail_width: int = 8,
) -> None:
    """Draw a triangular pointer tail from bubble_bbox toward tail_target."""
    x1, y1, x2, y2 = bubble_bbox
    bcx = (x1 + x2) / 2
    bcy = (y1 + y2) / 2

    tx, ty = tail_target
    # Direction from bubble center to target
    dx = tx - bcx
    dy = ty - bcy
    dist = math.hypot(dx, dy) or 1.0
    # Normalise
    ndx, ndy = dx / dist, dy / dist
    # Perpendicular
    perp_x, perp_y = -ndy, ndx

    # Anchor on bubble edge: move from center toward target
    # Use ellipse boundary approximation
    ew = (x2 - x1) / 2
    eh = (y2 - y1) / 2
    # Parametric ellipse: scale factor so the point lands on the edge
    scale = 1.0 / math.hypot(ndx / max(ew, 1), ndy / max(eh, 1))
    anchor_x = bcx + ndx * scale
    anchor_y = bcy + ndy * scale

    half_w = tail_width / 2
    p1 = (anchor_x + perp_x * half_w, anchor_y + perp_y * half_w)
    p2 = (anchor_x - perp_x * half_w, anchor_y - perp_y * half_w)
    p3 = (float(tx), float(ty))

    draw.polygon([p1, p2, p3], fill=fill, outline=outline)


def _tail_target_from_hint(hint: str, pw: int, ph: int) -> tuple[int, int]:
    """Estimate the speaker's mouth position from a position_hint."""
    mapping = {
        "top_left":    (int(pw * 0.20), int(ph * 0.55)),
        "top_right":   (int(pw * 0.80), int(ph * 0.55)),
        "top_center":  (int(pw * 0.50), int(ph * 0.60)),
        "bottom_left": (int(pw * 0.20), int(ph * 0.45)),
        "bottom_right":(int(pw * 0.80), int(ph * 0.45)),
        "bottom_center":(int(pw * 0.50), int(ph * 0.40)),
        "center_left": (int(pw * 0.15), int(ph * 0.50)),
        "center_right":(int(pw * 0.85), int(ph * 0.50)),
    }
    return mapping.get(hint, (pw // 2, ph // 2))


# ---------------------------------------------------------------------------
# Per-bubble sizing
# ---------------------------------------------------------------------------

_H_PAD = 14   # horizontal padding inside bubble
_V_PAD = 10   # vertical padding inside bubble


def _compute_bubble_bbox(
    zone_bbox: BBox,
    wrapped_lines: list[str],
    font: Any,
    draw: Any,
    pw: int,
    ph: int,
) -> BBox:
    """Compute a bubble bbox that fits the text, clamped to the zone."""
    text_w, text_h = _measure_wrapped(wrapped_lines, font, draw)
    bw = max(60, text_w + _H_PAD * 2)
    bh = max(30, text_h + _V_PAD * 2)

    zx1, zy1, zx2, zy2 = zone_bbox
    # Center within zone
    cx = (zx1 + zx2) // 2
    cy = (zy1 + zy2) // 2
    x1 = max(zx1, cx - bw // 2)
    y1 = max(zy1, cy - bh // 2)
    x2 = min(zx2, x1 + bw)
    y2 = min(zy2, y1 + bh)
    # If clamped, re-center
    if x2 - x1 < bw:
        x1 = max(0, x2 - bw)
    if y2 - y1 < bh:
        y1 = max(0, y2 - bh)
    x2 = min(pw, x1 + bw)
    y2 = min(ph, y1 + bh)
    return (x1, y1, x2, y2)


# ---------------------------------------------------------------------------
# Text rendering inside a bubble
# ---------------------------------------------------------------------------

def _render_text_in_bubble(
    draw: Any,
    bubble_bbox: BBox,
    wrapped_lines: list[str],
    font: Any,
    *,
    text_fill: tuple = (0, 0, 0, 255),
    narrator: bool = False,
) -> None:
    """Draw wrapped text centered inside the bubble bbox."""
    x1, y1, x2, y2 = bubble_bbox
    bw = x2 - x1
    bh = y2 - y1
    if not wrapped_lines:
        return

    _, line_h = _text_bbox(wrapped_lines[0], font, draw)
    line_h = max(line_h, 8)
    total_h = len(wrapped_lines) * line_h + (len(wrapped_lines) - 1) * 2
    start_y = y1 + (bh - total_h) // 2

    fill = (220, 220, 220, 255) if narrator else text_fill
    for i, line in enumerate(wrapped_lines):
        tw, _ = _text_bbox(line, font, draw)
        x = x1 + (bw - tw) // 2
        y = start_y + i * (line_h + 2)
        draw.text((x, y), line, font=font, fill=fill)


# ---------------------------------------------------------------------------
# Coverage enforcement
# ---------------------------------------------------------------------------

def _coverage_ratio(bubbles: list[BBox], pw: int, ph: int) -> float:
    total = sum((b[2] - b[0]) * (b[3] - b[1]) for b in bubbles)
    panel_area = pw * ph
    return total / panel_area if panel_area > 0 else 0.0


# ---------------------------------------------------------------------------
# Bubble placement + rendering for a single panel
# ---------------------------------------------------------------------------

def _default_zone_sequence() -> list[str]:
    """Reading-order zone assignment (right-to-left top-first for manga)."""
    return [
        "top_right", "top_left",
        "bottom_right", "bottom_left",
        "top_center", "bottom_center",
        "center_right", "center_left",
    ]


def render_bubbles_onto_panel(
    panel_image_path: Path,
    dialogue_lines: list[dict[str, Any]],
    sfx: list[str],
    narrator_caption: str | None,
    *,
    bubble_style_config: dict[str, Any] | None = None,
    out_path: Path | None = None,
    coverage_limit: float = 0.30,
) -> dict[str, Any]:
    """Composite speech bubbles, SFX, and captions onto a single panel PNG.

    Returns a ``bubble_layout`` record describing what was placed.
    Non-destructive: the original file is never modified.

    Parameters
    ----------
    panel_image_path : Path
        Source panel PNG.
    dialogue_lines : list[dict]
        Normalised dialogue line dicts from lettering_spec_v2.
    sfx : list[str]
        Sound-effect labels (rendered directly on art, not in bubbles).
    narrator_caption : str | None
        Narrator caption text (rendered as a full-width strip at top or bottom).
    bubble_style_config : dict, optional
        Genre-level style overrides (not yet used in v1 — reserved).
    out_path : Path, optional
        Output path.  Defaults to ``{stem}_bubbled.png`` beside the source.
    coverage_limit : float
        Fraction of panel area that bubbles may occupy (default 0.30).

    Returns
    -------
    dict  bubble_layout record with keys: panel_id (stem), bubbles, sfx, covered.
    """
    from PIL import Image, ImageDraw

    panel_image_path = Path(panel_image_path)
    if out_path is None:
        out_path = panel_image_path.with_name(
            panel_image_path.stem + "_bubbled" + panel_image_path.suffix
        )
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with Image.open(panel_image_path) as base_img:
        img = base_img.convert("RGBA")

    pw, ph = img.size
    overlay = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    placed_bubbles: list[BBox] = []
    layout_records: list[dict[str, Any]] = []

    zone_seq = _default_zone_sequence()
    zone_idx = 0

    # ── Narrator caption strip ─────────────────────────────────────
    if narrator_caption:
        cap_font = _get_font("calm")
        cap_lines = _wrap_text(narrator_caption, cap_font, draw, int(pw * 0.9))
        _, line_h = _text_bbox(cap_lines[0] if cap_lines else "M", cap_font, draw)
        cap_h = (len(cap_lines) * (line_h + 2)) + _V_PAD * 2
        cap_bbox: BBox = (0, 0, pw, min(ph, cap_h + 4))
        _draw_caption_box(draw, cap_bbox, fill=(0, 0, 0, 180))
        _render_text_in_bubble(draw, cap_bbox, cap_lines, cap_font, narrator=True)
        placed_bubbles.append(cap_bbox)
        layout_records.append({"type": "caption", "bbox": cap_bbox, "text": narrator_caption})

    # ── Dialogue bubbles ────────────────────────────────────────────
    for line in dialogue_lines:
        text: str = str(line.get("text") or "").strip()
        if not text:
            continue

        intensity: str = str(line.get("intensity") or "normal")
        bubble_style: str = str(line.get("bubble_style") or "round_normal")
        position_hint: str = str(line.get("position_hint") or zone_seq[zone_idx % len(zone_seq)])
        tail_style: str = str(line.get("tail_style") or "pointer")
        font_override: Any = line.get("font_override")

        # Font
        bold = intensity in ("excited", "shouting", "screaming") or font_override == "bold_action"
        italic = intensity == "internal" or font_override == "italic_internal"
        font = _get_font(intensity, bold=bold)

        # Coverage loop: shrink font one step if over limit
        for attempt in range(4):
            zone_bbox = _zone_to_pixels(position_hint, pw, ph)
            max_text_w = (zone_bbox[2] - zone_bbox[0]) - _H_PAD * 2
            wrapped = _wrap_text(text, font, draw, max(40, max_text_w))
            bubble_bbox = _compute_bubble_bbox(zone_bbox, wrapped, font, draw, pw, ph)
            test_bubbles = placed_bubbles + [bubble_bbox]
            if _coverage_ratio(test_bubbles, pw, ph) <= coverage_limit:
                break
            # shrink — use smaller intensity tier
            _tiers = ["screaming", "shouting", "excited", "normal", "calm", "whisper"]
            cur_tier = _tiers.index(intensity) if intensity in _tiers else 3
            next_tier = min(cur_tier + 1, len(_tiers) - 1)
            intensity = _tiers[next_tier]
            font = _get_font(intensity, bold=False)
        else:
            # Could not fit within coverage limit — log and skip
            layout_records.append({
                "type": "skipped",
                "reason": "coverage_limit",
                "text": text[:40],
            })
            continue

        # Draw bubble shape
        drawer = _BUBBLE_DRAWERS.get(bubble_style, _draw_round_bubble)

        if bubble_style == "shojo_soft":
            drawer(draw, bubble_bbox, fill=(255, 245, 250, 220))
        elif bubble_style == "electronic_sharp":
            drawer(draw, bubble_bbox, fill=(200, 230, 255, 210), outline=(0, 100, 200, 255))
        elif bubble_style == "whisper_dashed":
            drawer(draw, bubble_bbox)
        else:
            drawer(draw, bubble_bbox)

        # Draw tail
        if tail_style == "pointer":
            tail_target = _tail_target_from_hint(position_hint, pw, ph)
            bubble_fill = (255, 255, 255, 230)
            if bubble_style == "shojo_soft":
                bubble_fill = (255, 245, 250, 220)
            elif bubble_style in ("electronic_sharp",):
                bubble_fill = (200, 230, 255, 210)
            _draw_tail_pointer(draw, bubble_bbox, tail_target, fill=bubble_fill)
        # dotless / broken: no tail

        # Render text
        text_fill = (255, 255, 255, 255) if bubble_style == "square_narration" else (0, 0, 0, 255)
        _render_text_in_bubble(draw, bubble_bbox, wrapped, font, text_fill=text_fill)

        placed_bubbles.append(bubble_bbox)
        layout_records.append({
            "type": "dialogue",
            "speaker": line.get("speaker"),
            "text": text,
            "bubble_style": bubble_style,
            "intensity": intensity,
            "position_hint": position_hint,
            "bbox": bubble_bbox,
        })

        zone_idx += 1

    # ── SFX overlay ────────────────────────────────────────────────
    for sfx_text in sfx:
        if not sfx_text:
            continue
        sfx_font = _get_font("screaming", bold=True)
        # Place SFX at an off-center position (diagonally scattered)
        sfx_idx = sfx.index(sfx_text)
        sfx_x = int(pw * (0.30 + sfx_idx * 0.15) % pw)
        sfx_y = int(ph * 0.40)
        # Bold outline for readability over art
        outline_col = (0, 0, 0, 200)
        sfx_fill = (220, 40, 40, 255)  # red — genre override in v2
        for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2)]:
            draw.text((sfx_x + ox, sfx_y + oy), sfx_text, font=sfx_font, fill=outline_col)
        draw.text((sfx_x, sfx_y), sfx_text, font=sfx_font, fill=sfx_fill)
        layout_records.append({"type": "sfx", "text": sfx_text, "position": (sfx_x, sfx_y)})

    # ── Composite and save ─────────────────────────────────────────
    composite = Image.alpha_composite(img, overlay)
    composite.save(str(out_path), format="PNG")

    final_coverage = _coverage_ratio(placed_bubbles, pw, ph)
    return {
        "panel_stem": panel_image_path.stem,
        "out_path": str(out_path),
        "bubbles": layout_records,
        "coverage_ratio": round(final_coverage, 4),
        "panel_size": (pw, ph),
    }


# ---------------------------------------------------------------------------
# Manifest-level entry point
# ---------------------------------------------------------------------------

def render_bubbles_on_panels(
    chapter_script: Mapping[str, Any],
    lettering_spec: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    bubble_style_config: Mapping[str, Any] | None,
    out_dir: Path,
) -> dict[str, Any]:
    """Render speech bubbles for all non-silent panels; return updated manifest.

    Parameters
    ----------
    chapter_script : dict
        The chapter_script writer handoff artifact.
    lettering_spec : dict
        lettering_spec v2 artifact (schema_version "2.0.0" preferred; falls
        back gracefully if v1 with empty dialogue_lines).
    panel_images_manifest : dict
        Existing panel_images_manifest artifact.
    bubble_style_config : dict or None
        Genre-level style config (reserved for v2 — pass None for defaults).
    out_dir : Path
        Directory to write ``*_bubbled.png`` files.

    Returns
    -------
    dict  Updated panel_images_manifest with bubbled panel paths where applied.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Index lettering spec by panel_id
    lettering_by_pid: dict[str, dict[str, Any]] = {}
    for row in lettering_spec.get("lettering_panels") or []:
        pid = str(row.get("panel_id") or "")
        if pid:
            lettering_by_pid[pid] = row

    # Build updated manifest (deep copy to avoid mutating caller's dict)
    updated_manifest = copy.deepcopy(dict(panel_images_manifest))
    bubble_layout_records: list[dict[str, Any]] = []

    for panel_entry in updated_manifest.get("panels") or []:
        if str(panel_entry.get("status")) != "ok":
            continue
        pid = str(panel_entry.get("panel_id") or "")
        letter = lettering_by_pid.get(pid, {})

        # Skip silent panels
        if letter.get("silence_confirmed", True):
            continue

        src_path = panel_entry.get("path")
        if not src_path or not Path(src_path).is_file():
            continue

        dialogue_lines: list[dict[str, Any]] = list(letter.get("dialogue_lines") or [])
        sfx: list[str] = list(letter.get("sfx") or [])
        narrator_caption: str | None = letter.get("narrator_caption")

        if not dialogue_lines and not sfx and not narrator_caption:
            continue

        bubbled_path = out_dir / (Path(src_path).stem + "_bubbled.png")
        layout = render_bubbles_onto_panel(
            Path(src_path),
            dialogue_lines,
            sfx,
            narrator_caption,
            bubble_style_config=dict(bubble_style_config or {}),
            out_path=bubbled_path,
        )
        # Update the manifest entry to point to the bubbled PNG
        panel_entry["path"] = str(bubbled_path)
        panel_entry["bubble_render"] = {
            "applied": True,
            "coverage_ratio": layout["coverage_ratio"],
            "bubble_count": sum(
                1 for r in layout["bubbles"] if r.get("type") == "dialogue"
            ),
        }
        bubble_layout_records.append(layout)

    # Attach summary to manifest
    updated_manifest["bubble_render_summary"] = {
        "panels_processed": len(bubble_layout_records),
        "out_dir": str(out_dir),
    }
    return updated_manifest
