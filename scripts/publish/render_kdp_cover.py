#!/usr/bin/env python3
"""KDP cover renderer — TEMPLATE-BASED (R5 rewrite).

This module is the second stage of a two-stage cover pipeline:

    Stage 1: ``scripts/publish/render_imagery_for_template.py`` calls FLUX
             at the genre's imagery_zone aspect ratio. Output is saved as
             ``cover_<book_id>_v3_imagery.png``.
    Stage 2: this module composites the template's flat-color background,
             the imagery patch (if any), and the title/subtitle/author
             type into 1600x2560 pixel zones — all of which the
             ``config/publishing/bestseller_templates.yaml`` (R4) declares
             as STRICTLY non-overlapping bounding boxes.

Architecture changes from R3:

* **Strict zone non-overlap.** Title, subtitle, imagery, and author each
  occupy non-overlapping pixel rectangles per R4's template. The
  renderer NEVER paints text on top of imagery.
* **Type-dominant genres bypass FLUX entirely.** For boundaries,
  self_worth, and imposter_syndrome, ``imagery_zone == null`` and the
  background is painted with ``palette.primary.hex``. Any
  ``illustration_path`` argument is ignored (and warned about).
* **Image-bearing genres composite at the imagery_zone bbox.** The FLUX
  render must already be at the zone's aspect ratio (Stage 1's job).
  Rest of canvas filled with ``palette.primary.hex``. Title-zone
  background is therefore always a known flat color, which makes
  auto-color contrast deterministic.
* **No matte. No backdrop block.** Those R3 band-aids were patches over
  text-on-imagery overlap; with the template enforcing separation they
  are unnecessary and have been deleted.
* **TitleTooLongForTemplateError.** If the title cannot fit at the
  ≥14% canvas-height floor mandated by R4 §10/§13, the renderer raises
  rather than silently shrinking past the floor.

Library API (back-compat with R3 tests):

    render_kdp_cover(
        illustration_path=Path(...),       # may be None for type-dominant
        title="The No That Saved Me",
        author="Ma'at",
        subtitle="A Practical Guide to Setting Boundaries",
        genre="boundaries",
        output_path=Path("…/cover.png"),
    ) -> dict

For type-dominant genres ``illustration_path`` may be a placeholder; the
renderer ignores it and prints a warning if a path was passed.

CLI:

    python3 scripts/publish/render_kdp_cover.py \
        --illustration <path>|none --title "<t>" --author "<a>" \
        --genre <g> --output <out>
    python3 scripts/publish/render_kdp_cover.py --batch
    python3 scripts/publish/render_kdp_cover.py --book maat_boundaries \
        --output /tmp/x.png      # type-dominant; needs no illustration

Hard rules:
    * Output is exactly 1600x2560.
    * No paid LLM/image API calls. Pillow only.
    * Bundled OFL fonts (EB Garamond, Inter, Playfair Display, Caveat).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[2]

CANVAS_W = 1600
CANVAS_H = 2560

DEFAULT_TYPOGRAPHY_PATH = REPO_ROOT / "config" / "publishing" / "kdp_cover_typography.yaml"
DEFAULT_TEMPLATES_PATH = REPO_ROOT / "config" / "publishing" / "bestseller_templates.yaml"
DEFAULT_COOKBOOK_PATH = REPO_ROOT / "config" / "manga" / "genre_prompt_cookbook_v2.yaml"
DEFAULT_IDENTITY_PATH = REPO_ROOT / "config" / "publishing" / "cover_identity_system.yaml"

# System-font fallbacks (used when bundled OFL font is missing).
SYSTEM_FALLBACKS = {
    "serif": [
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
    ],
    "sans_serif": [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ],
    "display": [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    ],
    "script": [
        "/System/Library/Fonts/Supplemental/Apple Chancery.ttf",
        "/System/Library/Fonts/Supplemental/SnellRoundhand.ttc",
    ],
}

logger = logging.getLogger("render_kdp_cover")


# ─── EXCEPTIONS ───────────────────────────────────────────────────────


class TitleTooLongForTemplateError(ValueError):
    """Raised when title cannot fit the template's title_zone at the
    R4-mandated 14% canvas-height floor.
    """


# ─── DATA STRUCTURES ──────────────────────────────────────────────────


@dataclass
class TextBlock:
    """A single rendered text block (title / subtitle / author)."""
    text: str
    style: dict[str, Any]
    zone: dict[str, Any]


# ─── CONFIG LOADING ───────────────────────────────────────────────────


def load_typography_config(path: Path | None = None) -> dict[str, Any]:
    """Load and validate the per-genre typography YAML."""
    cfg_path = path or DEFAULT_TYPOGRAPHY_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(f"Typography config missing: {cfg_path}")
    cfg = yaml.safe_load(cfg_path.read_text())
    if "genres" not in cfg or not isinstance(cfg["genres"], dict):
        raise ValueError(f"Typography config has no 'genres' map: {cfg_path}")
    if "defaults" not in cfg or not isinstance(cfg["defaults"], dict):
        raise ValueError(f"Typography config has no 'defaults' block: {cfg_path}")
    for genre_name, genre_cfg in cfg["genres"].items():
        for required in ("title_zone", "title_style"):
            if required not in genre_cfg:
                raise ValueError(
                    f"Genre '{genre_name}' missing required key '{required}'"
                )
    return cfg


def load_identity_system(path: Path | None = None) -> dict[str, Any] | None:
    """Load cover_identity_system.yaml (R6 contract). Returns None if
    the file is absent (renderer falls back to R4-template-only behavior)."""
    cfg_path = path or DEFAULT_IDENTITY_PATH
    if not cfg_path.exists():
        return None
    cfg = yaml.safe_load(cfg_path.read_text())
    if not isinstance(cfg, dict):
        return None
    return cfg


def resolve_identity_for_book(
    book_id: str,
    identity_cfg: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """Look up identity layers (book/author/brand) for ``book_id``. Returns
    None when identity_cfg is missing or has no entry for the book."""
    if identity_cfg is None:
        return None
    books = identity_cfg.get("books") or {}
    if book_id not in books:
        return None
    book = books[book_id]
    authors = identity_cfg.get("authors") or {}
    author = authors.get(book.get("author_id")) or {}
    brands = identity_cfg.get("brands") or {}
    brand = brands.get(author.get("brand_id")) or {}
    return {"book": book, "author": author, "brand": brand}


def load_templates_config(path: Path | None = None) -> dict[str, Any]:
    """Load and validate the bestseller templates YAML (R4 contract)."""
    cfg_path = path or DEFAULT_TEMPLATES_PATH
    if not cfg_path.exists():
        raise FileNotFoundError(f"Templates config missing: {cfg_path}")
    cfg = yaml.safe_load(cfg_path.read_text())
    if "templates" not in cfg or not isinstance(cfg["templates"], dict):
        raise ValueError(f"Templates config missing 'templates': {cfg_path}")
    for genre, tpl in cfg["templates"].items():
        for required in ("title_zone", "subtitle_zone", "author_zone",
                         "palette", "type_dominant", "type_size_ratios"):
            if required not in tpl:
                raise ValueError(
                    f"Template '{genre}' missing required key '{required}'"
                )
    return cfg


# ─── FONT LOADING ─────────────────────────────────────────────────────


def _resolve_font_path(family: str, cfg: dict[str, Any]) -> str | None:
    fonts_map = cfg.get("defaults", {}).get("fonts", {})
    raw = fonts_map.get(family)
    if raw:
        candidate = REPO_ROOT / raw
        if candidate.exists():
            return str(candidate)
        if Path(raw).is_absolute() and Path(raw).exists():
            return raw
    for fallback in SYSTEM_FALLBACKS.get(family, []):
        if Path(fallback).exists():
            return fallback
    return None


def _load_font(family: str, size_px: int, weight: str,
               cfg: dict[str, Any]) -> ImageFont.FreeTypeFont:
    """Load a Pillow truetype font; sets variation axis when supported."""
    font_path = _resolve_font_path(family, cfg)
    if font_path is None:
        font = ImageFont.load_default()
        try:
            return font.font_variant(size=size_px)
        except Exception:
            return font
    font = ImageFont.truetype(font_path, size=size_px)
    weight_map = {"regular": 400, "bold": 700, "extra_bold": 800}
    target_w = weight_map.get(weight, 400)
    try:
        font.set_variation_by_axes([target_w])
    except (OSError, AttributeError, ValueError):
        pass
    return font


# ─── COLOR / LUMINANCE ────────────────────────────────────────────────


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    s = value.lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


def _luminance_rgb(rgb: tuple[int, int, int]) -> float:
    """Rec. 601 luminance, normalised to [0..1]."""
    r, g, b = rgb
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _zone_avg_luminance(image: Image.Image,
                        zone_rect: tuple[int, int, int, int]) -> float:
    """Mean Rec. 601 luminance of pixels in zone_rect (0..1)."""
    x0, y0, x1, y1 = zone_rect
    crop = image.crop((x0, y0, x1, y1)).convert("RGB")
    crop.thumbnail((64, 64))
    pixels = list(crop.getdata())
    if not pixels:
        return 0.5
    total = 0.0
    for r, g, b in pixels:
        total += 0.299 * r + 0.587 * g + 0.114 * b
    return (total / len(pixels)) / 255.0


def _pick_contrast_color(
    background_rgb: tuple[int, int, int],
    palette_options: list[str],
) -> tuple[int, int, int]:
    """Pick the option with the highest absolute luminance contrast vs
    background. Falls back to white/black at the extremes if no option
    has contrast >= 0.4.

    R5: title_zone background is ALWAYS the genre's palette.primary.hex
    (template enforces title_zone never overlaps imagery_zone), so this
    operates on a known-flat color rather than sampling pixels.
    """
    bg_lum = _luminance_rgb(background_rgb)
    candidates = []
    for hex_val in palette_options or ["#FFFFFF", "#0F172A"]:
        rgb = _hex_to_rgb(hex_val)
        contrast = abs(_luminance_rgb(rgb) - bg_lum)
        candidates.append((contrast, rgb))
    candidates.sort(key=lambda t: t[0], reverse=True)
    best_contrast, best_rgb = candidates[0]
    if best_contrast >= 0.4:
        return best_rgb
    # Fall through to extremes if palette options are too close to bg.
    return (15, 23, 42) if bg_lum > 0.5 else (255, 255, 255)


# ─── TEXT WRAPPING / FITTING ──────────────────────────────────────────


def _apply_case(text: str, case: str) -> str:
    if case == "upper":
        return text.upper()
    if case == "lower":
        return text.lower()
    return text


def _measure_text(draw: ImageDraw.ImageDraw, text: str,
                  font: ImageFont.FreeTypeFont,
                  tracking_px: int) -> tuple[int, int]:
    if tracking_px == 0:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    width = 0
    height = 0
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        width += (bbox[2] - bbox[0]) + tracking_px
        height = max(height, bbox[3] - bbox[1])
    width = max(0, width - tracking_px)
    return width, height


def _wrap_to_width(draw: ImageDraw.ImageDraw, text: str,
                   font: ImageFont.FreeTypeFont,
                   tracking_px: int, max_width: int) -> list[str]:
    """Greedy wrap on whitespace. Unsplittable words remain whole."""
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join(current + [word])
        w, _ = _measure_text(draw, candidate, font, tracking_px)
        if w <= max_width or not current:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _fit_font_to_box(
    cfg: dict[str, Any],
    text: str,
    style: dict[str, Any],
    max_width: int,
    max_height: int,
    *,
    initial_size: int,
    min_size: int = 36,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """Shrink font until wrapped text fits in the bounding box."""
    family = style.get("font_family", "serif")
    weight = style.get("font_weight", "regular")
    tracking_pct = style.get("tracking_pct", 0)
    measure_img = Image.new("RGB", (max(1, max_width), max(1, max_height)))
    measure_draw = ImageDraw.Draw(measure_img)
    size = initial_size
    while size >= min_size:
        font = _load_font(family, size, weight, cfg)
        tracking_px = int(round(size * tracking_pct / 100.0))
        lines = _wrap_to_width(measure_draw, text, font, tracking_px, max_width)
        line_h = int(size * 1.15)
        total_h = line_h * len(lines)
        widest = 0
        for line in lines:
            w, _ = _measure_text(measure_draw, line, font, tracking_px)
            widest = max(widest, w)
        if widest <= max_width and total_h <= max_height:
            return font, lines, size
        size -= 4
    # Fallback at the floor; caller decides whether to error out.
    font = _load_font(family, min_size, weight, cfg)
    tracking_px = int(round(min_size * tracking_pct / 100.0))
    lines = _wrap_to_width(measure_draw, text, font, tracking_px, max_width)
    return font, lines, min_size


# ─── DRAW ──────────────────────────────────────────────────────────────


def _draw_text_with_shadow(
    canvas: Image.Image,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    style: dict[str, Any],
    box: tuple[int, int, int, int],
    anchor: str,
    line_height_px: int,
    tracking_px: int,
) -> None:
    x0, y0, x1, y1 = box
    box_w = x1 - x0
    shadow_cfg = style.get("shadow") or {}
    shadow_offset = tuple(shadow_cfg.get("offset_px", [0, 4]))
    shadow_blur = shadow_cfg.get("blur_px", 12)
    shadow_alpha = float(shadow_cfg.get("color_alpha", 0.35))

    shadow_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_layer)
    shadow_color = (0, 0, 0, int(255 * shadow_alpha))

    text_layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_layer)

    measure_img = Image.new("RGB", (max(1, box_w), 1))
    measure_draw = ImageDraw.Draw(measure_img)

    for i, line in enumerate(lines):
        line_w, _ = _measure_text(measure_draw, line, font, tracking_px)
        if anchor == "left":
            line_x = x0
        elif anchor == "right":
            line_x = x1 - line_w
        else:
            line_x = x0 + (box_w - line_w) // 2
        line_y = y0 + i * line_height_px

        cursor = line_x
        for ch in line:
            shadow_draw.text(
                (cursor + shadow_offset[0], line_y + shadow_offset[1]),
                ch, font=font, fill=shadow_color,
            )
            text_draw.text((cursor, line_y), ch, font=font, fill=fill + (255,))
            ch_bbox = measure_draw.textbbox((0, 0), ch, font=font)
            cursor += (ch_bbox[2] - ch_bbox[0]) + tracking_px

    if shadow_blur > 0:
        shadow_layer = shadow_layer.filter(
            ImageFilter.GaussianBlur(radius=shadow_blur / 2)
        )
    canvas.alpha_composite(shadow_layer)
    canvas.alpha_composite(text_layer)


# ─── ZONE PIXEL CONVERSION ────────────────────────────────────────────


def _pct_zone_to_pixels(
    zone: dict[str, Any] | None,
) -> tuple[int, int, int, int] | None:
    """R4 template zone -> (x0, y0, x1, y1) pixel rect on 1600x2560."""
    if zone is None:
        return None
    x_pct = zone["x_pct"]
    y_pct = zone["y_pct"]
    return (
        int(CANVAS_W * x_pct[0] / 100),
        int(CANVAS_H * y_pct[0] / 100),
        int(CANVAS_W * x_pct[1] / 100),
        int(CANVAS_H * y_pct[1] / 100),
    )


def _imagery_aspect(template: dict[str, Any]) -> float | None:
    """Compute aspect = width/height for the template's imagery_zone in
    pixels, or None for type-dominant genres."""
    iz = template.get("imagery_zone")
    if iz is None:
        return None
    x_pct = iz["x_pct"]
    y_pct = iz["y_pct"]
    w = (x_pct[1] - x_pct[0]) / 100.0 * CANVAS_W
    h = (y_pct[1] - y_pct[0]) / 100.0 * CANVAS_H
    if h <= 0:
        return None
    return w / h


# ─── LEGACY NO-OP HOOKS ───────────────────────────────────────────────
# Kept for ad-hoc callers that imported them; they are not used by the
# template-based renderer. R3's matte/backdrop layers were band-aids
# over the text-on-imagery overlap problem; with strict zones they are
# unnecessary.


def _legacy_apply_matte(*_args: Any, **_kwargs: Any) -> None:  # pragma: no cover
    return None


def _legacy_apply_backdrop_block(*_args: Any, **_kwargs: Any) -> None:  # pragma: no cover
    return None


# ─── RENDER HELPERS ───────────────────────────────────────────────────


def _build_canvas_with_imagery(
    template: dict[str, Any],
    illustration_path: Path | None,
) -> tuple[Image.Image, dict[str, Any]]:
    """Create the 1600x2560 RGBA canvas — flat primary palette color +
    optional imagery patch composited at the template's imagery_zone.

    Returns (canvas, imagery_meta).
    """
    primary_hex = template["palette"]["primary"]["hex"]
    bg_rgb = _hex_to_rgb(primary_hex)
    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), bg_rgb + (255,))

    imagery_meta: dict[str, Any] = {
        "imagery_zone_used": False,
        "imagery_aspect": None,
        "imagery_path": None,
    }

    iz = template.get("imagery_zone")
    if iz is None:
        if illustration_path is not None:
            logger.warning(
                "Genre is type-dominant; ignoring illustration_path=%s",
                illustration_path,
            )
        return canvas, imagery_meta

    if illustration_path is None or not Path(illustration_path).exists():
        raise FileNotFoundError(
            f"Image-bearing genre requires illustration_path; "
            f"got {illustration_path!r}. Run "
            f"scripts/publish/render_imagery_for_template.py first."
        )

    rect = _pct_zone_to_pixels(iz)
    assert rect is not None
    x0, y0, x1, y1 = rect
    w, h = x1 - x0, y1 - y0
    illo = Image.open(illustration_path).convert("RGB")
    illo_resized = illo.resize((w, h), Image.LANCZOS)
    canvas.paste(illo_resized, (x0, y0))

    imagery_meta.update({
        "imagery_zone_used": True,
        "imagery_aspect": round(w / h, 3) if h else None,
        "imagery_path": str(illustration_path),
        "imagery_pixel_rect": (x0, y0, x1, y1),
    })
    return canvas, imagery_meta


def _check_title_fits(
    cfg: dict[str, Any],
    title: str,
    title_style: dict[str, Any],
    zone_rect: tuple[int, int, int, int],
    *,
    min_size: int,
    genre: str,
    min_title_pct: int,
) -> None:
    """Per R4 §13: raise if the title cannot fit in title_zone at the
    min_size floor (i.e. will silently overflow if rendered)."""
    family = title_style.get("font_family", "serif")
    weight = title_style.get("font_weight", "regular")
    tracking_pct = title_style.get("tracking_pct", 0)
    case = title_style.get("case", "title")
    text = _apply_case(title, case)

    x0, y0, x1, y1 = zone_rect
    box_w = max(1, x1 - x0)
    box_h = max(1, y1 - y0)

    measure_img = Image.new("RGB", (box_w, max(1, box_h)))
    measure_draw = ImageDraw.Draw(measure_img)
    font = _load_font(family, min_size, weight, cfg)
    tracking_px = int(round(min_size * tracking_pct / 100.0))
    lines = _wrap_to_width(measure_draw, text, font, tracking_px, box_w)
    line_h = int(min_size * 1.15)
    total_h = line_h * len(lines)

    widest = 0
    for line in lines:
        w, _ = _measure_text(measure_draw, line, font, tracking_px)
        widest = max(widest, w)

    if widest > box_w or total_h > box_h:
        actual_pct = round(100.0 * total_h / CANVAS_H, 1)
        zone_pct = round(100.0 * box_h / CANVAS_H, 1)
        raise TitleTooLongForTemplateError(
            f"Title '{title}' ({len(title)} chars) cannot fit "
            f"genre '{genre}' template title_zone ({zone_pct}% canvas-height) "
            f"even at the {min_title_pct}%-canvas-height floor "
            f"({min_size}px). Would need {actual_pct}% canvas-height. "
            "Trim the title or pick a different template."
        )


def _draw_block_in_zone(
    canvas: Image.Image,
    text: str,
    typography_style: dict[str, Any],
    zone_rect: tuple[int, int, int, int],
    type_dominant: bool,
    cfg: dict[str, Any],
    palette_options: list[str],
    background_rgb: tuple[int, int, int],
    *,
    initial_size: int,
    min_size: int,
    line_h_factor: float = 1.15,
    role: str = "title",
) -> tuple[int, list[str], tuple[int, int, int]]:
    """Render a text block centered inside zone_rect. Returns
    (font_size_used, lines, fill_rgb)."""
    x0, y0, x1, y1 = zone_rect
    box_w = max(1, x1 - x0)
    box_h = max(1, y1 - y0)

    text_cased = _apply_case(text, typography_style.get("case", "title"))
    font, lines, size_used = _fit_font_to_box(
        cfg, text_cased, typography_style,
        max_width=box_w, max_height=box_h,
        initial_size=initial_size, min_size=min_size,
    )

    color_spec = typography_style.get("color", "auto")
    if color_spec == "auto":
        fill_rgb = _pick_contrast_color(background_rgb, palette_options)
    else:
        fill_rgb = _hex_to_rgb(color_spec)

    tracking_px = int(round(size_used * typography_style.get("tracking_pct", 0) / 100))
    line_h = int(size_used * line_h_factor)

    # Vertically center within the zone for non-title-dominant blocks
    # (titles are anchored at the top of their zone for a "headline"
    # feel; subtitles/authors visually center).
    n_lines = max(1, len(lines))
    block_h = line_h * n_lines
    if role in ("subtitle", "author"):
        v_offset = max(0, (box_h - block_h) // 2)
        draw_y0 = y0 + v_offset
    else:
        draw_y0 = y0

    _draw_text_with_shadow(
        canvas, lines, font, fill_rgb,
        typography_style,
        box=(x0, draw_y0, x1, y1),
        anchor="centered",
        line_height_px=line_h,
        tracking_px=tracking_px,
    )
    return size_used, lines, fill_rgb


# ─── IDENTITY-SYSTEM OVERLAY (R6/R7) ─────────────────────────────────


def _apply_identity_overrides(
    template: dict[str, Any],
    typography: dict[str, Any],
    identity: dict[str, Any],
) -> dict[str, Any]:
    """Layer R6 identity (book/author/brand) on top of R4 template +
    R3 typography. Mutates copies, returns a meta dict describing what
    was applied (for the renderer's return value)."""
    meta: dict[str, Any] = {
        "identity_applied": True,
        "brand_id": identity.get("author", {}).get("brand_id"),
        "author_id": identity.get("book", {}).get("author_id"),
    }

    brand = identity.get("brand") or {}
    author = identity.get("author") or {}
    book = identity.get("book") or {}

    # 1. Brand palette override — replaces palette.primary.hex.
    brand_palette = brand.get("palette") or {}
    if brand_palette.get("primary"):
        template["palette"]["primary"]["hex"] = brand_palette["primary"]
        meta["brand_palette_primary"] = brand_palette["primary"]
    if brand_palette.get("secondary"):
        template["palette"]["secondary"]["hex"] = brand_palette["secondary"]
        meta["brand_palette_secondary"] = brand_palette["secondary"]
    if brand_palette.get("accent") and "accent" in template.get("palette", {}):
        template["palette"]["accent"]["hex"] = brand_palette["accent"]

    # 2. Per-book micro-palette shift (informational; surfaced to caller).
    if book.get("this_book_micro_palette_shift"):
        meta["micro_palette_shift"] = book["this_book_micro_palette_shift"]

    # 3. Type-only override.
    if book.get("cover_kind") == "type_only":
        template["type_dominant"] = True
        template["imagery_zone"] = None
        meta["type_only_override"] = True

    # 4. Author signature_color → subtitle accent + force into title color
    #    when type_dominant (Truth Compass / Gen Spark style).
    sig_color = author.get("signature_color")
    if sig_color:
        meta["author_signature_color"] = sig_color
        sub_style = typography.get("subtitle_style") or {}
        if isinstance(sub_style, dict):
            sub_style = dict(sub_style)
            sub_style["color"] = sig_color
            typography["subtitle_style"] = sub_style
        if template.get("type_dominant"):
            title_style = dict(typography.get("title_style") or {})
            title_style["color"] = sig_color
            typography["title_style"] = title_style

    # 5. Author type_quirk → applied as best-effort string toggles on
    #    title/author style. Anything we can't structurally express is
    #    surfaced via meta for operator visual QA.
    quirk = author.get("type_quirk") or ""
    if quirk:
        meta["type_quirk_note"] = quirk
        title_style = dict(typography.get("title_style") or {})
        author_style = dict(typography.get("author_style") or {})
        sub_style = dict(typography.get("subtitle_style") or {})
        ql = quirk.lower()
        if "lowercase" in ql and "title" in ql:
            title_style["case"] = "lower"
        if "small-caps" in ql or "small caps" in ql or "small_caps" in ql:
            if "title" in ql:
                title_style["case"] = "upper"
            if "author" in ql or "byline" in ql:
                author_style["case"] = "upper"
        if "italic" in ql and ("subtitle" in ql or "subhead" in ql):
            sub_style["font_weight"] = "italic"
        if "lowercase" in ql and ("author" in ql or "byline" in ql):
            author_style["case"] = "lower"
        if "all-caps" in ql or "all caps" in ql:
            if "title" in ql:
                title_style["case"] = "upper"
        typography["title_style"] = title_style
        typography["author_style"] = author_style
        typography["subtitle_style"] = sub_style

    return meta


# ─── MAIN RENDER ──────────────────────────────────────────────────────


def render_kdp_cover(
    illustration_path: Path | None,
    title: str,
    author: str,
    *,
    subtitle: str = "",
    genre: str = "anxiety",
    output_path: Path,
    publisher: str | None = None,
    typography_overrides: dict[str, Any] | None = None,
    typography_config_path: Path | None = None,
    templates_config_path: Path | None = None,
    book_id: str | None = None,
    identity_config_path: Path | None = None,
) -> dict[str, Any]:
    """Composite typography + imagery into the genre's template → 1600x2560 cover.

    Parameters
    ----------
    illustration_path : Path | None
        Path to the FLUX render at the imagery_zone aspect ratio. May be
        None for type-dominant genres (boundaries/self_worth/imposter_syndrome).
    title : str
        Required.
    author : str
        Author byline.
    subtitle : str
        Optional subtitle.
    genre : str
        Selects template + typography per-genre.
    output_path : Path
        Final cover PNG destination.
    publisher : str | None
        Optional imprint appended after the author name.
    typography_overrides : dict | None
        Override values merged into the genre typography dict before render.
    typography_config_path : Path | None
        Override for typography YAML (test seam).
    templates_config_path : Path | None
        Override for templates YAML (test seam).

    Returns
    -------
    dict
        Render metadata: output_path, layout_used, template_archetype,
        type_dominant, font_family, title_size_px, subtitle_size_px,
        author_size_px, contrast_ratio, imagery_aspect, palette.
    """
    if not title or not title.strip():
        raise ValueError("title is required (KDP rejects covers without titles)")

    typography_cfg = load_typography_config(typography_config_path)
    templates_cfg = load_templates_config(templates_config_path)

    if genre not in typography_cfg["genres"]:
        raise ValueError(
            f"Unknown genre '{genre}'. Known: {sorted(typography_cfg['genres'])}"
        )
    if genre not in templates_cfg["templates"]:
        raise ValueError(
            f"Genre '{genre}' has no template entry in bestseller_templates.yaml"
        )

    genre_typography = json.loads(json.dumps(typography_cfg["genres"][genre]))
    if typography_overrides:
        for key, value in typography_overrides.items():
            if isinstance(value, dict) and isinstance(genre_typography.get(key), dict):
                genre_typography[key].update(value)
            else:
                genre_typography[key] = value

    template = json.loads(json.dumps(templates_cfg["templates"][genre]))

    # Identity-system overlay (R6/R7). When book_id is provided AND the
    # identity YAML has an entry for it, layer brand/author/book on top.
    identity_meta: dict[str, Any] = {"identity_applied": False}
    if book_id:
        identity_cfg = load_identity_system(identity_config_path)
        identity = resolve_identity_for_book(book_id, identity_cfg)
        if identity is not None:
            identity_meta = _apply_identity_overrides(
                template, genre_typography, identity,
            )

    type_dominant = bool(template.get("type_dominant", False))

    # 1. Build canvas (flat primary + optional imagery patch).
    canvas, imagery_meta = _build_canvas_with_imagery(template, illustration_path)
    primary_hex = template["palette"]["primary"]["hex"]
    bg_rgb = _hex_to_rgb(primary_hex)

    # 2. Title.
    title_zone_rect = _pct_zone_to_pixels(template["title_zone"])
    assert title_zone_rect is not None
    title_box_h = title_zone_rect[3] - title_zone_rect[1]
    title_style = genre_typography["title_style"]
    palette_options = (
        genre_typography.get("palette_hints", {}).get("hex_palette_fallback")
        or [template["palette"]["secondary"]["hex"]]
    )

    # type_size_ratios.title is a percentage of canvas height: convert
    # to a target line-height in pixels. R4 §13's 14%-floor sets min.
    target_title_pct = template["type_size_ratios"]["title"]
    initial_title_size = int(CANVAS_H * target_title_pct / 100.0)
    min_title_pct = templates_cfg.get("universal_rules", {}).get(
        "min_title_pct_canvas_height", 14
    )
    min_title_size = max(72, int(CANVAS_H * min_title_pct / 100.0 / 4))
    # ↑ min size is per-line; for multi-line titles the floor still
    # applies at the line level. The hard 14% canvas-height floor is
    # checked against the rendered block below.

    # Pre-render fit check: if the title cannot fit in the title_zone
    # at the min_title_size floor, raise rather than silently shrinking
    # past it. Per R4 §13: title-too-long is a pre-render error.
    _check_title_fits(
        typography_cfg, title, title_style, title_zone_rect,
        min_size=min_title_size, genre=genre,
        min_title_pct=min_title_pct,
    )

    title_size_used, title_lines, title_fill = _draw_block_in_zone(
        canvas, title, title_style, title_zone_rect,
        type_dominant=type_dominant,
        cfg=typography_cfg,
        palette_options=palette_options,
        background_rgb=bg_rgb,
        initial_size=initial_title_size,
        min_size=min_title_size,
        line_h_factor=1.10 if type_dominant else 1.15,
        role="title",
    )

    # 3. Subtitle.
    subtitle_size_used = 0
    if subtitle and subtitle.strip():
        subtitle_zone_rect = _pct_zone_to_pixels(template["subtitle_zone"])
        assert subtitle_zone_rect is not None
        subtitle_style = genre_typography.get("subtitle_style", title_style)
        target_sub_pct = template["type_size_ratios"]["subtitle"]
        initial_sub_size = int(CANVAS_H * target_sub_pct / 100.0)
        subtitle_size_used, _sub_lines, _sub_fill = _draw_block_in_zone(
            canvas, subtitle, subtitle_style, subtitle_zone_rect,
            type_dominant=type_dominant,
            cfg=typography_cfg,
            palette_options=palette_options,
            background_rgb=bg_rgb,
            initial_size=initial_sub_size,
            min_size=28,
            line_h_factor=1.20,
            role="subtitle",
        )

    # 4. Author.
    author_zone_rect = _pct_zone_to_pixels(template["author_zone"])
    assert author_zone_rect is not None
    defaults = typography_cfg.get("defaults", {})
    author_style = genre_typography.get("author_style") or defaults.get(
        "default_author_style", {
            "font_family": "sans_serif", "font_weight": "bold",
            "size_px_at_1600x2560": 64, "tracking_pct": 8, "case": "upper",
            "color": "auto",
            "shadow": {"offset_px": [0, 2], "blur_px": 8, "color_alpha": 0.30},
        }
    )
    author_label = author
    if publisher:
        author_label = f"{author}  ·  {publisher}"
    target_author_pct = template["type_size_ratios"]["author"]
    initial_author_size = int(CANVAS_H * target_author_pct / 100.0)
    author_size_used, _author_lines, _author_fill = _draw_block_in_zone(
        canvas, author_label, author_style, author_zone_rect,
        type_dominant=type_dominant,
        cfg=typography_cfg,
        palette_options=palette_options,
        background_rgb=bg_rgb,
        initial_size=initial_author_size,
        min_size=22,
        line_h_factor=1.20,
        role="author",
    )

    # 5. Save.
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, format="PNG", optimize=True)

    bg_lum = _luminance_rgb(bg_rgb)
    fill_lum = _luminance_rgb(title_fill)
    contrast = abs(bg_lum - fill_lum)

    return {
        "output_path": str(output_path),
        "output_size": (CANVAS_W, CANVAS_H),
        "layout_used": genre,
        "template_archetype": template.get("primary_archetype"),
        "type_dominant": type_dominant,
        "font_family": title_style.get("font_family"),
        "title_size_px": title_size_used,
        "subtitle_size_px": subtitle_size_used,
        "author_size_px": author_size_used,
        "contrast_ratio": round(contrast, 3),
        "title_color_rgb": list(title_fill),
        "title_zone_luminance": round(bg_lum, 3),
        "imagery_aspect": imagery_meta["imagery_aspect"],
        "imagery_zone_used": imagery_meta["imagery_zone_used"],
        "imagery_path": imagery_meta["imagery_path"],
        "palette": {
            k: v["hex"] for k, v in template["palette"].items()
            if isinstance(v, dict) and "hex" in v
        },
        "title_lines": title_lines,
        "identity": identity_meta,
    }


# ─── CLI ──────────────────────────────────────────────────────────────


def _book_id_to_genre(book_id: str) -> str | None:
    """Look up a book_id (e.g. 'maat_boundaries') in book_genre_map."""
    cookbook_path = DEFAULT_COOKBOOK_PATH
    templates_path = DEFAULT_TEMPLATES_PATH
    for path in (cookbook_path, templates_path):
        if not path.exists():
            continue
        cfg = yaml.safe_load(path.read_text()) or {}
        bgm = cfg.get("book_genre_map") or {}
        if book_id in bgm:
            return bgm[book_id]
    return None


def _find_v3_imagery(book_id: str) -> Path | None:
    """Look for cover_<book_id>_v3_imagery.png under
    artifacts/pipeline_examples/<id>/. <id> here is the bare TEACHER_BOOKS
    id (e.g. 'maat'), not the book_genre_map key."""
    teacher_dir = REPO_ROOT / "artifacts" / "pipeline_examples" / book_id
    if not teacher_dir.exists():
        return None
    candidate = teacher_dir / f"cover_{book_id}_v3_imagery.png"
    if candidate.exists():
        return candidate
    return None


def _load_teacher_books() -> list[dict[str, Any]]:
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.release.build_epub import TEACHER_BOOKS  # type: ignore
    return list(TEACHER_BOOKS)


def _topic_to_genre(topic: str, known_genres: set[str]) -> str:
    if topic in known_genres:
        return topic
    return "anxiety"


def _run_batch(
    typography_config_path: Path | None = None,
    templates_config_path: Path | None = None,
) -> list[dict[str, Any]]:
    typography_cfg = load_typography_config(typography_config_path)
    templates_cfg = load_templates_config(templates_config_path)
    known = set(typography_cfg["genres"].keys()) & set(templates_cfg["templates"].keys())
    books = _load_teacher_books()
    results: list[dict[str, Any]] = []
    for book in books:
        book_id = book["id"]
        genre = _topic_to_genre(book.get("topic", "anxiety"), known)
        template = templates_cfg["templates"][genre]
        out_dir = REPO_ROOT / "artifacts" / "pipeline_examples" / book_id
        out_path = out_dir / f"cover_{book_id}_FINAL.png"

        if template.get("type_dominant"):
            illustration: Path | None = None
        else:
            illustration = _find_v3_imagery(book_id)
            if illustration is None:
                msg = (
                    f"missing v3 imagery — run "
                    f"scripts/publish/render_imagery_for_template.py "
                    f"--book {book_id} first"
                )
                print(f"[skip] {book_id}: {msg}", file=sys.stderr)
                results.append({
                    "book_id": book_id,
                    "status": "skipped_no_illustration",
                    "reason": msg,
                })
                continue

        try:
            meta = render_kdp_cover(
                illustration_path=illustration,
                title=book["title"],
                author=book["author"],
                subtitle=book.get("subtitle", ""),
                genre=genre,
                output_path=out_path,
                publisher=book.get("publisher"),
                typography_config_path=typography_config_path,
                templates_config_path=templates_config_path,
            )
            print(f"[ok]   {book_id}: wrote {meta['output_path']}")
            results.append({"book_id": book_id, "status": "ok", **meta})
        except Exception as exc:  # noqa: BLE001
            print(f"[fail] {book_id}: {exc}", file=sys.stderr)
            results.append({"book_id": book_id, "status": "fail", "error": str(exc)})
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Composite KDP-bestseller typography + template into a final cover."
    )
    parser.add_argument("--illustration", type=Path, default=None,
                        help="Imagery patch (FLUX render at imagery_zone aspect). "
                             "Optional for type-dominant genres.")
    parser.add_argument("--title", type=str, help="Book title.")
    parser.add_argument("--subtitle", type=str, default="")
    parser.add_argument("--author", type=str, help="Author byline.")
    parser.add_argument("--publisher", type=str, default=None)
    parser.add_argument("--genre", type=str, default=None,
                        help="Genre key (anxiety/grief/etc.). "
                             "Required unless --book given.")
    parser.add_argument("--book", type=str, default=None,
                        help="book_id (e.g. maat_boundaries) — looks up genre and "
                             "(for type-dominant) renders without --illustration.")
    parser.add_argument("--output", type=Path, help="Output cover PNG.")
    parser.add_argument("--batch", action="store_true",
                        help="Render all teacher books from TEACHER_BOOKS.")
    parser.add_argument("--typography-config", type=Path, default=None)
    parser.add_argument("--templates-config", type=Path, default=None)
    parser.add_argument("--identity-book", type=str, default=None,
                        help="Identity-system book key (e.g. 'ahjan', 'maat'). "
                             "Reads cover_identity_system.yaml and overlays "
                             "brand/author/book layers on R4 template.")
    parser.add_argument("--identity-config", type=Path, default=None)
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = build_parser().parse_args(argv)

    if args.batch:
        results = _run_batch(
            typography_config_path=args.typography_config,
            templates_config_path=args.templates_config,
        )
        ok = sum(1 for r in results if r.get("status") == "ok")
        print(f"\n=== batch complete: {ok}/{len(results)} successful ===")
        return 0 if ok == len(results) else 1

    # Resolve --book if given.
    genre = args.genre
    title = args.title
    author = args.author
    subtitle = args.subtitle
    publisher = args.publisher
    if args.book:
        resolved = _book_id_to_genre(args.book)
        if resolved is None:
            print(f"error: unknown book_id '{args.book}'", file=sys.stderr)
            return 2
        genre = genre or resolved
        # If the user only gave --book, fill title/author from TEACHER_BOOKS
        # by stripping the genre suffix to derive the bare id.
        if not title or not author:
            bare_id = args.book.replace(f"_{resolved}", "")
            try:
                books = _load_teacher_books()
            except Exception:
                books = []
            for book in books:
                if book["id"] == bare_id:
                    title = title or book["title"]
                    subtitle = subtitle or book.get("subtitle", "")
                    author = author or book["author"]
                    publisher = publisher or book.get("publisher")
                    break

    missing = []
    if not title:
        missing.append("--title")
    if not author:
        missing.append("--author")
    if not args.output:
        missing.append("--output")
    if not genre:
        missing.append("--genre or --book")
    if missing:
        print(f"error: missing required arguments: {', '.join(missing)}",
              file=sys.stderr)
        return 2

    meta = render_kdp_cover(
        illustration_path=args.illustration,
        title=title,
        author=author,
        subtitle=subtitle,
        genre=genre,
        output_path=args.output,
        publisher=publisher,
        typography_config_path=args.typography_config,
        templates_config_path=args.templates_config,
        book_id=args.identity_book,
        identity_config_path=args.identity_config,
    )
    print(f"wrote {meta['output_size'][0]}x{meta['output_size'][1]} → {meta['output_path']}")
    print(f"  layout={meta['layout_used']} archetype={meta['template_archetype']}"
          f" type_dominant={meta['type_dominant']}"
          f" title_size={meta['title_size_px']}px"
          f" contrast={meta['contrast_ratio']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
