#!/usr/bin/env python3
"""KDP cover typography overlay pipeline.

FLUX renders the bare illustration. This module composites bestseller-grade
typography (title, subtitle, author) on top of it via Pillow, producing the
KDP-shipped 1600x2560 portrait cover.

Library API
-----------

    render_kdp_cover(
        illustration_path=Path("…/cover_<book>_v2_dev.png"),
        title="The Alarm Is Lying",
        subtitle="A Nervous System Guide to Anxiety Recovery",
        author="Ahjan",
        genre="anxiety",
        output_path=Path("…/cover_<book>_FINAL.png"),
    ) -> dict

CLI
---

    python3 scripts/publish/render_kdp_cover.py \
        --illustration <path> --title "<title>" --author "<author>" \
        --genre anxiety --output <path>

    python3 scripts/publish/render_kdp_cover.py --batch
        # Reads scripts/release/build_epub.py TEACHER_BOOKS, finds each book's
        # latest *_v2_dev.png OR *_v2_schnell.png illustration in the matching
        # artifacts/pipeline_examples/<id>/ dir, renders the final cover into
        # the same dir as cover_<book_id>_FINAL.png.

Design
------

* Diffusion models can't reliably render readable text → text is composited
  in PIL after illustration generation.
* Per-genre layouts live in ``config/publishing/kdp_cover_typography.yaml``
  so the operator edits typography rules without touching Python.
* Auto-color samples the illustration's title zone luminance (Rec. 601:
  0.299R + 0.587G + 0.114B) and picks light text on dark zones, dark text
  on light zones.
* No paid LLM/image API calls. Pillow only.

Hard rules:
* Output is exactly 1600x2560.
* Refuses cleanly on missing illustration or missing title.
* Bundled fonts (EB Garamond / Inter / Playfair Display, all OFL) are the
  default; system fonts are the fallback if a bundled file is missing.
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

# KDP ideal embedded / storefront portrait (height × width per Amazon Help G200645690).
CANVAS_W = 1600
CANVAS_H = 2560

DEFAULT_TYPOGRAPHY_PATH = REPO_ROOT / "config" / "publishing" / "kdp_cover_typography.yaml"

# System-font fallbacks if bundled font file is missing.
SYSTEM_FALLBACKS = {
    "serif": ["/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
              "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
              "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
              "/System/Library/Fonts/Supplemental/Georgia.ttf"],
    "sans_serif": ["/System/Library/Fonts/Helvetica.ttc",
                   "/System/Library/Fonts/HelveticaNeue.ttc",
                   "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
                   "/System/Library/Fonts/Supplemental/Arial.ttf"],
    "display": ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
                "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf"],
    "script": ["/System/Library/Fonts/Supplemental/Apple Chancery.ttf"],
}

logger = logging.getLogger("render_kdp_cover")


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


# ─── FONT LOADING ─────────────────────────────────────────────────────


def _resolve_font_path(family: str, cfg: dict[str, Any]) -> str | None:
    fonts_map = cfg.get("defaults", {}).get("fonts", {})
    raw = fonts_map.get(family)
    if raw:
        candidate = REPO_ROOT / raw
        if candidate.exists():
            return str(candidate)
        # Allow absolute paths too
        if Path(raw).is_absolute() and Path(raw).exists():
            return raw
    for fallback in SYSTEM_FALLBACKS.get(family, []):
        if Path(fallback).exists():
            return fallback
    return None


def _load_font(family: str, size_px: int, weight: str, cfg: dict[str, Any]) -> ImageFont.FreeTypeFont:
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
        # Variable-font weight axis (Pillow ≥ 9.2)
        font.set_variation_by_axes([target_w])
    except (OSError, AttributeError, ValueError):
        # Non-variable font, or no wght axis — silently keep as-is.
        pass
    return font


# ─── COLOR / LUMINANCE ────────────────────────────────────────────────


def _zone_avg_luminance(image: Image.Image, zone_rect: tuple[int, int, int, int]) -> float:
    """Mean Rec. 601 luminance of pixels in the zone rect (0..1)."""
    x0, y0, x1, y1 = zone_rect
    crop = image.crop((x0, y0, x1, y1)).convert("RGB")
    # Downsample for speed; mean is invariant under uniform sampling.
    crop.thumbnail((64, 64))
    pixels = list(crop.getdata())
    if not pixels:
        return 0.5
    total = 0.0
    for r, g, b in pixels:
        total += 0.299 * r + 0.587 * g + 0.114 * b
    return (total / len(pixels)) / 255.0


def _auto_color(image: Image.Image, zone_rect: tuple[int, int, int, int],
                palette_hints: dict[str, Any]) -> tuple[int, int, int]:
    luminance = _zone_avg_luminance(image, zone_rect)
    fallback = palette_hints.get("hex_palette_fallback") or ["#FFFFFF", "#0F172A"]
    light_hex = fallback[0]
    dark_hex = fallback[-1]
    chosen = light_hex if luminance < 0.5 else dark_hex
    return _hex_to_rgb(chosen)


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    s = value.lstrip("#")
    if len(s) == 3:
        s = "".join(ch * 2 for ch in s)
    return (int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16))


# ─── TEXT WRAPPING / FITTING ──────────────────────────────────────────


def _apply_case(text: str, case: str) -> str:
    if case == "upper":
        return text.upper()
    if case == "lower":
        return text.lower()
    return text


def _measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
                  tracking_px: int) -> tuple[int, int]:
    if tracking_px == 0:
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]
    # Per-char layout for tracking control
    width = 0
    height = 0
    for ch in text:
        bbox = draw.textbbox((0, 0), ch, font=font)
        width += (bbox[2] - bbox[0]) + tracking_px
        height = max(height, bbox[3] - bbox[1])
    width = max(0, width - tracking_px)
    return width, height


def _wrap_to_width(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
                   tracking_px: int, max_width: int) -> list[str]:
    """Greedy wrap. Splits on whitespace, keeps unsplittable words intact."""
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
    measure_img = Image.new("RGB", (max_width or 100, max_height or 100))
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
    # Fallback: smallest acceptable, accept overflow
    font = _load_font(family, min_size, weight, cfg)
    tracking_px = int(round(min_size * tracking_pct / 100.0))
    lines = _wrap_to_width(measure_draw, text, font, tracking_px, max_width)
    return font, lines, min_size


# ─── SHADOW / DRAW ────────────────────────────────────────────────────


def _draw_text_with_shadow(
    canvas: Image.Image,
    lines: list[str],
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    style: dict[str, Any],
    box: tuple[int, int, int, int],  # x0, y0, x1, y1
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

    # Render shadow on a separate transparent layer
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

        # Draw with tracking
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
        shadow_layer = shadow_layer.filter(ImageFilter.GaussianBlur(radius=shadow_blur / 2))
    canvas.alpha_composite(shadow_layer)
    canvas.alpha_composite(text_layer)


# ─── ZONE LAYOUT ──────────────────────────────────────────────────────


def _zone_rect(zone: dict[str, Any], canvas_w: int, canvas_h: int) -> tuple[int, int, int, int]:
    max_w_pct = zone.get("max_width_pct", 86)
    max_h_pct = zone.get("max_height_pct", 22)
    voffset_pct = zone.get("vertical_offset_pct", 6)
    anchor = zone.get("anchor", "centered")
    box_w = int(canvas_w * max_w_pct / 100)
    box_h = int(canvas_h * max_h_pct / 100)
    y0 = int(canvas_h * voffset_pct / 100)
    if anchor == "left":
        x0 = int(canvas_w * 0.06)
    elif anchor == "right":
        x0 = canvas_w - int(canvas_w * 0.06) - box_w
    else:
        x0 = (canvas_w - box_w) // 2
    return x0, y0, x0 + box_w, y0 + box_h


# ─── MAIN RENDER ──────────────────────────────────────────────────────


def render_kdp_cover(
    illustration_path: Path,
    title: str,
    author: str,
    *,
    subtitle: str = "",
    genre: str = "anxiety",
    output_path: Path,
    publisher: str | None = None,
    typography_overrides: dict[str, Any] | None = None,
    typography_config_path: Path | None = None,
) -> dict[str, Any]:
    """Composite typography onto a bare illustration → final KDP cover.

    Parameters
    ----------
    illustration_path : Path
        Bare 1600x2560 illustration (FLUX-rendered).
    title : str
        Book title (required; no covers without titles).
    author : str
        Author byline.
    subtitle : str
        Optional subtitle (defaults to "").
    genre : str
        Selects the per-genre layout from the typography YAML.
    output_path : Path
        Final cover destination (PNG).
    publisher : str | None
        Optional publisher imprint (rendered in the author block if present).
    typography_overrides : dict | None
        Operator-supplied dict merged into the genre cfg before render.
    typography_config_path : Path | None
        Override for the typography YAML location (test seam).

    Returns
    -------
    dict
        Render metadata: output_path, layout_used, font_family,
        title_size_px, contrast_ratio, etc.
    """
    if not title or not title.strip():
        raise ValueError("title is required (KDP rejects covers without titles)")
    if not Path(illustration_path).exists():
        raise FileNotFoundError(f"Illustration not found: {illustration_path}")

    cfg = load_typography_config(typography_config_path)
    if genre not in cfg["genres"]:
        raise ValueError(
            f"Unknown genre '{genre}'. Known: {sorted(cfg['genres'])}"
        )

    genre_cfg = json.loads(json.dumps(cfg["genres"][genre]))  # deep copy
    if typography_overrides:
        for key, value in typography_overrides.items():
            if isinstance(value, dict) and isinstance(genre_cfg.get(key), dict):
                genre_cfg[key].update(value)
            else:
                genre_cfg[key] = value

    # 1. Load + normalize illustration to canvas.
    illo = Image.open(illustration_path).convert("RGB")
    if illo.size != (CANVAS_W, CANVAS_H):
        illo = illo.resize((CANVAS_W, CANVAS_H), Image.LANCZOS)
    canvas = illo.convert("RGBA")

    # 2. Title block.
    title_zone = genre_cfg["title_zone"]
    title_style = genre_cfg["title_style"]
    title_rect = _zone_rect(title_zone, CANVAS_W, CANVAS_H)

    title_text = _apply_case(title, title_style.get("case", "title"))
    initial_title_size = title_style.get("size_px_at_1600x2560", 144)
    title_font, title_lines, title_size_used = _fit_font_to_box(
        cfg, title_text, title_style,
        max_width=title_rect[2] - title_rect[0],
        max_height=title_rect[3] - title_rect[1],
        initial_size=initial_title_size,
    )
    title_color_spec = title_style.get("color", "auto")
    palette_hints = genre_cfg.get("palette_hints", {})
    if title_color_spec == "auto":
        title_fill = _auto_color(illo, title_rect, palette_hints)
    else:
        title_fill = _hex_to_rgb(title_color_spec)

    title_tracking_px = int(round(title_size_used * title_style.get("tracking_pct", 0) / 100))
    title_line_h = int(title_size_used * 1.15)

    _draw_text_with_shadow(
        canvas, title_lines, title_font, title_fill,
        title_style,
        box=title_rect,
        anchor=title_zone.get("anchor", "centered"),
        line_height_px=title_line_h,
        tracking_px=title_tracking_px,
    )

    # 3. Subtitle block (immediately below the title).
    subtitle_size_used = 0
    if subtitle and subtitle.strip():
        subtitle_style = genre_cfg.get("subtitle_style", title_style)
        sub_max_width = title_rect[2] - title_rect[0]
        sub_max_height = int(CANVAS_H * 0.10)
        subtitle_text = _apply_case(subtitle, subtitle_style.get("case", "title"))
        sub_font, sub_lines, subtitle_size_used = _fit_font_to_box(
            cfg, subtitle_text, subtitle_style,
            max_width=sub_max_width, max_height=sub_max_height,
            initial_size=subtitle_style.get("size_px_at_1600x2560", 56),
        )
        sub_y0 = title_rect[1] + (len(title_lines) * title_line_h) + int(CANVAS_H * 0.015)
        sub_rect = (title_rect[0], sub_y0, title_rect[2], sub_y0 + sub_max_height)
        sub_fill_spec = subtitle_style.get("color", "auto")
        if sub_fill_spec == "auto":
            sub_fill = _auto_color(illo, sub_rect, palette_hints)
        else:
            sub_fill = _hex_to_rgb(sub_fill_spec)
        sub_tracking_px = int(round(subtitle_size_used * subtitle_style.get("tracking_pct", 0) / 100))
        sub_line_h = int(subtitle_size_used * 1.2)
        _draw_text_with_shadow(
            canvas, sub_lines, sub_font, sub_fill,
            subtitle_style,
            box=sub_rect,
            anchor=title_zone.get("anchor", "centered"),
            line_height_px=sub_line_h,
            tracking_px=sub_tracking_px,
        )

    # 4. Author block.
    defaults = cfg.get("defaults", {})
    author_zone = genre_cfg.get("author_zone") or defaults.get("default_author_zone", {
        "position": "bottom", "anchor": "centered",
        "max_width_pct": 70, "max_height_pct": 6, "vertical_offset_pct": 90,
    })
    author_style = genre_cfg.get("author_style") or defaults.get("default_author_style", {
        "font_family": "sans_serif", "font_weight": "bold",
        "size_px_at_1600x2560": 64, "tracking_pct": 8, "case": "upper",
        "color": "auto", "shadow": {"offset_px": [0, 2], "blur_px": 8, "color_alpha": 0.3},
    })
    author_rect = _zone_rect(author_zone, CANVAS_W, CANVAS_H)
    author_label = author
    if publisher:
        author_label = f"{author}  ·  {publisher}"
    author_text = _apply_case(author_label, author_style.get("case", "upper"))
    author_font, author_lines, author_size_used = _fit_font_to_box(
        cfg, author_text, author_style,
        max_width=author_rect[2] - author_rect[0],
        max_height=author_rect[3] - author_rect[1],
        initial_size=author_style.get("size_px_at_1600x2560", 64),
        min_size=28,
    )
    author_fill_spec = author_style.get("color", "auto")
    if author_fill_spec == "auto":
        author_fill = _auto_color(illo, author_rect, palette_hints)
    else:
        author_fill = _hex_to_rgb(author_fill_spec)
    author_tracking_px = int(round(author_size_used * author_style.get("tracking_pct", 0) / 100))
    author_line_h = int(author_size_used * 1.2)
    _draw_text_with_shadow(
        canvas, author_lines, author_font, author_fill,
        author_style,
        box=author_rect,
        anchor=author_zone.get("anchor", "centered"),
        line_height_px=author_line_h,
        tracking_px=author_tracking_px,
    )

    # 5. Save.
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(output_path, format="PNG", optimize=True)

    title_luminance = _zone_avg_luminance(illo, title_rect)
    fill_lum = (0.299 * title_fill[0] + 0.587 * title_fill[1] + 0.114 * title_fill[2]) / 255
    contrast = abs(title_luminance - fill_lum)

    return {
        "output_path": str(output_path),
        "output_size": (CANVAS_W, CANVAS_H),
        "layout_used": genre,
        "font_family": title_style.get("font_family"),
        "title_size_px": title_size_used,
        "subtitle_size_px": subtitle_size_used,
        "author_size_px": author_size_used,
        "title_zone_luminance": round(title_luminance, 3),
        "title_color_rgb": list(title_fill),
        "contrast_ratio": round(contrast, 3),
        "title_lines": title_lines,
    }


# ─── CLI ──────────────────────────────────────────────────────────────


def _find_latest_illustration(book_id: str) -> Path | None:
    teacher_dir = REPO_ROOT / "artifacts" / "pipeline_examples" / book_id
    if not teacher_dir.exists():
        return None
    candidates: list[Path] = []
    for pattern in (f"cover_{book_id}_*_v2_dev.png",
                    f"cover_{book_id}_*_v2_schnell.png",
                    f"cover_{book_id}_v2_dev.png",
                    f"cover_{book_id}_v2_schnell.png"):
        candidates.extend(teacher_dir.glob(pattern))
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]


def _load_teacher_books() -> list[dict[str, Any]]:
    sys.path.insert(0, str(REPO_ROOT))
    from scripts.release.build_epub import TEACHER_BOOKS  # type: ignore
    return list(TEACHER_BOOKS)


def _topic_to_genre(topic: str, known_genres: set[str]) -> str:
    if topic in known_genres:
        return topic
    return "anxiety"  # safe default


def _run_batch(typography_config_path: Path | None = None) -> list[dict[str, Any]]:
    cfg = load_typography_config(typography_config_path)
    known = set(cfg["genres"].keys())
    books = _load_teacher_books()
    results: list[dict[str, Any]] = []
    for book in books:
        book_id = book["id"]
        illustration = _find_latest_illustration(book_id)
        if illustration is None:
            print(f"[skip] {book_id}: no v2 illustration found", file=sys.stderr)
            results.append({"book_id": book_id, "status": "skipped_no_illustration"})
            continue
        genre = _topic_to_genre(book.get("topic", "anxiety"), known)
        out = REPO_ROOT / "artifacts" / "pipeline_examples" / book_id / f"cover_{book_id}_FINAL.png"
        try:
            meta = render_kdp_cover(
                illustration_path=illustration,
                title=book["title"],
                author=book["author"],
                subtitle=book.get("subtitle", ""),
                genre=genre,
                output_path=out,
                publisher=book.get("publisher"),
                typography_config_path=typography_config_path,
            )
            print(f"[ok]   {book_id}: wrote {meta['output_path']}")
            results.append({"book_id": book_id, "status": "ok", **meta})
        except Exception as exc:  # noqa: BLE001
            print(f"[fail] {book_id}: {exc}", file=sys.stderr)
            results.append({"book_id": book_id, "status": "fail", "error": str(exc)})
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Composite KDP-bestseller typography onto a FLUX illustration."
    )
    parser.add_argument("--illustration", type=Path, help="Bare 1600x2560 illustration.")
    parser.add_argument("--title", type=str, help="Book title.")
    parser.add_argument("--subtitle", type=str, default="", help="Optional subtitle.")
    parser.add_argument("--author", type=str, help="Author byline.")
    parser.add_argument("--publisher", type=str, default=None)
    parser.add_argument("--genre", type=str, default="anxiety",
                        help="Genre key from kdp_cover_typography.yaml")
    parser.add_argument("--output", type=Path, help="Output cover PNG.")
    parser.add_argument("--batch", action="store_true",
                        help="Render all teacher books from TEACHER_BOOKS.")
    parser.add_argument("--typography-config", type=Path, default=None,
                        help="Override typography YAML path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    args = build_parser().parse_args(argv)
    if args.batch:
        results = _run_batch(typography_config_path=args.typography_config)
        ok = sum(1 for r in results if r.get("status") == "ok")
        print(f"\n=== batch complete: {ok}/{len(results)} successful ===")
        return 0 if ok == len(results) else 1

    missing = [
        f"--{name}" for name, value in [
            ("illustration", args.illustration),
            ("title", args.title),
            ("author", args.author),
            ("output", args.output),
        ] if value is None
    ]
    if missing:
        print(f"error: missing required arguments: {', '.join(missing)}", file=sys.stderr)
        return 2

    meta = render_kdp_cover(
        illustration_path=args.illustration,
        title=args.title,
        author=args.author,
        subtitle=args.subtitle,
        genre=args.genre,
        output_path=args.output,
        publisher=args.publisher,
        typography_config_path=args.typography_config,
    )
    print(f"wrote {meta['output_size'][0]}x{meta['output_size'][1]} → {meta['output_path']}")
    print(f"  layout={meta['layout_used']} title_size={meta['title_size_px']}px"
          f" contrast={meta['contrast_ratio']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
