#!/usr/bin/env python3
"""Two-pass bestseller cover generator: FLUX background + PIL typography overlay.

Research-backed approach:
  Pass 1: ComfyUI/FLUX generates abstract background art (NO text in prompt)
  Pass 2: Python/PIL overlays professional typography with brand identity

Design principles (from bestseller cover research 2025-2026):
  - Title occupies 50-70% of cover — bold, oversized, readable at 100×160px
  - Max 3 colors: primary 60-70%, neutral 20-30%, accent 10%
  - Bold sans-serif or heavy slab-serif for title (no thin serifs at thumbnail)
  - High contrast — survives thumbnail compression, BookTok scroll
  - 3-second test: genre, title, feeling must register instantly
  - NEVER put text in FLUX prompt — AI can't render clean typography

Usage:
  # Generate with ComfyUI backgrounds (requires COMFYUI_URL)
  python3 scripts/image_generation/generate_bestseller_covers.py --mode comfyui

  # Generate with solid gradient backgrounds (no API needed)
  python3 scripts/image_generation/generate_bestseller_covers.py --mode gradient

  # Generate specific brand only
  python3 scripts/image_generation/generate_bestseller_covers.py --brand stillness_press

  # Dry run (show what would be generated)
  python3 scripts/image_generation/generate_bestseller_covers.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ── KDP dimensions ──
FORMATS = {
    "kdp_ebook": (1600, 2560),   # 5:8 portrait
    "audiobook_square": (3200, 3200),
    "social_thumb": (1080, 1080),
}

# ── Typography layout (percentage-based, resolution-independent) ──
LAYOUT = {
    "kdp_ebook": {
        "title_y_pct": 0.15,       # title starts at 15% from top
        "title_max_w_pct": 0.85,   # title max width 85% of cover
        "title_size_pct": 0.065,   # title font size 6.5% of height
        "subtitle_y_pct": 0.55,    # subtitle at 55%
        "subtitle_size_pct": 0.028,
        "author_y_pct": 0.82,     # author name at 82%
        "author_size_pct": 0.025,
        "colophon_y_pct": 0.92,   # brand colophon at 92%
        "colophon_size_pct": 0.018,
    },
    "audiobook_square": {
        "title_y_pct": 0.20,
        "title_max_w_pct": 0.80,
        "title_size_pct": 0.075,
        "subtitle_y_pct": 0.55,
        "subtitle_size_pct": 0.032,
        "author_y_pct": 0.78,
        "author_size_pct": 0.028,
        "colophon_y_pct": 0.90,
        "colophon_size_pct": 0.020,
    },
    "social_thumb": {
        "title_y_pct": 0.15,
        "title_max_w_pct": 0.85,
        "title_size_pct": 0.09,
        "subtitle_y_pct": 0.58,
        "subtitle_size_pct": 0.04,
        "author_y_pct": 0.80,
        "author_size_pct": 0.035,
        "colophon_y_pct": 0.92,
        "colophon_size_pct": 0.025,
    },
}


# ── Font loading ──

def _load_font(size: int, bold: bool = False):
    """Load a font with system fallback chain."""
    try:
        from PIL import ImageFont
    except ImportError:
        raise RuntimeError("Pillow required: pip install Pillow")

    # Bold sans-serif priority (research: bold sans outsells serif at thumbnail)
    bold_candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFCompact.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    regular_candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]

    candidates = bold_candidates if bold else regular_candidates
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _luminance(rgb: tuple[int, int, int]) -> float:
    r, g, b = rgb
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255.0


def _text_color_for_bg(bg_rgb: tuple[int, int, int]) -> tuple[int, int, int]:
    """Return white or dark text depending on background luminance."""
    return (255, 255, 255) if _luminance(bg_rgb) < 0.5 else (30, 30, 30)


# ── Brand data loader ──

def _load_brand_data() -> dict[str, Any]:
    """Load brand identity + cover art specs."""
    try:
        import yaml
    except ImportError:
        raise RuntimeError("PyYAML required: pip install pyyaml")

    identity_path = REPO_ROOT / "config" / "catalog_planning" / "brand_identity_system.yaml"
    covers_path = REPO_ROOT / "config" / "catalog_planning" / "brand_cover_art_specs.yaml"

    identity = {}
    if identity_path.exists():
        with open(identity_path) as f:
            identity = yaml.safe_load(f) or {}

    covers = {}
    if covers_path.exists():
        with open(covers_path) as f:
            covers = yaml.safe_load(f) or {}

    return {"identity": identity, "covers": covers}


def _get_brand_info(brand_id: str, data: dict[str, Any]) -> dict[str, Any]:
    """Extract brand colors, fonts, and cover spec."""
    identity = data["identity"]
    covers = data["covers"]

    # Try teacher_brands first, then standard_brands
    brand_def = identity.get("teacher_brands", {}).get(brand_id, {})
    if not brand_def:
        brand_def = identity.get("standard_brands", {}).get(brand_id, {})

    bi = brand_def.get("brand_identity", {})
    cover_spec = covers.get("brands", {}).get(brand_id, {})

    primary_colors = bi.get("primary_colors", ["#1A1A1A", "#F5F5F5"])
    accent = bi.get("accent_color", "#D4A574")

    return {
        "display_name": brand_def.get("display_name", brand_id.replace("_", " ").title()),
        "teacher": brand_def.get("teacher", ""),
        "tagline": brand_def.get("tagline", ""),
        "primary_colors": primary_colors,
        "accent_color": accent,
        "display_font": bi.get("display_font", "Helvetica"),
        "body_font": bi.get("body_font", "Helvetica"),
        "mood": bi.get("mood", ""),
        "cover_template": bi.get("cover_template", "minimalist_gradient"),
        "cover_spec": cover_spec,
    }


# ── Background generators ──

def _generate_gradient_bg(width: int, height: int, colors: list[str], seed: int = 0) -> "Image":
    """Generate a professional gradient background (no API needed)."""
    from PIL import Image, ImageDraw

    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    c1 = _hex_to_rgb(colors[0])
    c2 = _hex_to_rgb(colors[1]) if len(colors) > 1 else c1

    # Vertical gradient
    for y in range(height):
        ratio = y / height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    return img


def _generate_comfyui_bg(
    width: int, height: int, brand_info: dict[str, Any], seed: int = 0
) -> "Image":
    """Generate abstract background via ComfyUI FLUX (no text in prompt)."""
    from PIL import Image
    import io

    comfyui_url = os.environ.get("COMFYUI_URL", "").strip()
    if not comfyui_url:
        print("    WARN: COMFYUI_URL not set, falling back to gradient")
        return _generate_gradient_bg(width, height, brand_info["primary_colors"], seed)

    # Background-only prompt (NO text, NO letters, NO typography)
    mood = brand_info.get("mood", "contemplative calm")
    colors_desc = " and ".join(brand_info["primary_colors"][:2])
    prompt = (
        f"abstract minimalist book cover background, {mood}, "
        f"gradient tones of {colors_desc}, atmospheric, soft focus, "
        f"clean composition, generous negative space, subtle texture, "
        f"professional publishing quality, no objects, no people"
    )
    negative = (
        "text, letters, words, typography, title, author name, "
        "face, person, hand, fingers, realistic photo, busy, cluttered, "
        "low quality, watermark, signature, logo, border, frame"
    )

    try:
        from scripts.video.flux_client import call_comfyui
        img_bytes = call_comfyui(
            comfyui_url, prompt, negative,
            width=width, height=height, seed=seed,
        )
        return Image.open(io.BytesIO(img_bytes))
    except Exception as e:
        print(f"    WARN: ComfyUI failed ({e}), falling back to gradient")
        return _generate_gradient_bg(width, height, brand_info["primary_colors"], seed)


# ── Typography overlay ──

def _wrap_text(text: str, font, max_width: int, draw) -> list[str]:
    """Word-wrap text to fit within max_width pixels."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width and current:
            lines.append(current)
            current = word
        else:
            current = test
    if current:
        lines.append(current)
    return lines or [text]


def _overlay_typography(
    img: "Image",
    title: str,
    subtitle: str,
    author: str,
    colophon: str,
    layout: dict[str, float],
    accent_color: str,
) -> "Image":
    """Overlay professional typography onto background image."""
    from PIL import ImageDraw

    draw = ImageDraw.Draw(img)
    w, h = img.size

    # Sample background color at center for text color decision
    center_pixel = img.getpixel((w // 2, int(h * 0.3)))
    if isinstance(center_pixel, int):
        center_pixel = (center_pixel, center_pixel, center_pixel)
    text_color = _text_color_for_bg(center_pixel[:3])
    accent_rgb = _hex_to_rgb(accent_color)

    # Title (bold, oversized — 50-70% of visual weight)
    title_size = max(24, int(h * layout["title_size_pct"]))
    title_font = _load_font(title_size, bold=True)
    title_max_w = int(w * layout["title_max_w_pct"])
    title_lines = _wrap_text(title.upper(), title_font, title_max_w, draw)

    title_y = int(h * layout["title_y_pct"])
    line_height = int(title_size * 1.2)
    for line in title_lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        line_w = bbox[2] - bbox[0]
        x = (w - line_w) // 2
        draw.text((x, title_y), line, fill=text_color, font=title_font)
        title_y += line_height

    # Accent bar (thin horizontal line between title and subtitle)
    bar_y = title_y + int(h * 0.02)
    bar_w = int(w * 0.2)
    bar_x = (w - bar_w) // 2
    draw.rectangle([(bar_x, bar_y), (bar_x + bar_w, bar_y + 3)], fill=accent_rgb)

    # Subtitle
    if subtitle:
        sub_size = max(16, int(h * layout["subtitle_size_pct"]))
        sub_font = _load_font(sub_size, bold=False)
        sub_y = int(h * layout["subtitle_y_pct"])
        sub_lines = _wrap_text(subtitle, sub_font, title_max_w, draw)
        for line in sub_lines:
            bbox = draw.textbbox((0, 0), line, font=sub_font)
            line_w = bbox[2] - bbox[0]
            x = (w - line_w) // 2
            # Slightly muted text for subtitle
            muted = tuple(max(0, min(255, c + (40 if _luminance(text_color) > 0.5 else -40))) for c in text_color)
            draw.text((x, sub_y), line, fill=muted, font=sub_font)
            sub_y += int(sub_size * 1.3)

    # Author name
    author_size = max(14, int(h * layout["author_size_pct"]))
    author_font = _load_font(author_size, bold=False)
    author_y = int(h * layout["author_y_pct"])
    bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = bbox[2] - bbox[0]
    draw.text(((w - author_w) // 2, author_y), author, fill=accent_rgb, font=author_font)

    # Colophon (brand imprint)
    if colophon:
        col_size = max(12, int(h * layout["colophon_size_pct"]))
        col_font = _load_font(col_size, bold=False)
        col_y = int(h * layout["colophon_y_pct"])
        bbox = draw.textbbox((0, 0), colophon, font=col_font)
        col_w = bbox[2] - bbox[0]
        muted = tuple(max(0, min(255, c + (60 if _luminance(text_color) > 0.5 else -60))) for c in text_color)
        draw.text(((w - col_w) // 2, col_y), colophon, fill=muted, font=col_font)

    return img


# ── Demo book metadata per teacher ──

TEACHER_BOOKS = {
    # Topics matched to teacher_select.html expected filenames (14 entries = 13 brands + adi_da)
    "awakening_press": {"title": "The Fire That Sees", "subtitle": "Radical self-inquiry for the devoted seeker", "author": "Adi Da", "teacher_override": "adi_da", "topic": "self_worth", "colors_override": ["#4A1A2A", "#1A0A10"], "accent_override": "#FF6B35", "display_name_override": "Awakening Press"},
    "stillness_press": {"title": "The Alarm You Learned to Ignore", "subtitle": "Recognizing what your body already knows", "author": "Lena Thorne", "topic": "anxiety"},
    "cognitive_clarity": {"title": "The Seeing Mind", "subtitle": "When clarity arrives before the answer does", "author": "Ada Park", "topic": "anxiety"},
    "somatic_wisdom": {"title": "The Body Knows First", "subtitle": "A polyvagal guide to what you already feel", "author": "Claire Ashford", "topic": "anxiety"},
    "qi_foundation": {"title": "Root and Breath", "subtitle": "Qi cultivation for the overwhelmed system", "author": "Master Feung", "topic": "burnout"},
    "digital_ground": {"title": "Scroll Stop", "subtitle": "Digital-age calm for the always-on generation", "author": "Miki", "topic": "imposter_syndrome"},
    "heart_balance": {"title": "Scales of Ma'at", "subtitle": "Shadow work as self-worth recalibration", "author": "Maat", "topic": "boundaries"},
    "relational_calm": {"title": "The Empty Cup", "subtitle": "Radical acceptance in relationships", "author": "Miyuki", "topic": "overthinking"},  # per OPD-111
    "warrior_calm": {"title": "Iron Gate", "subtitle": "Martial composure under pressure", "author": "Master Wu", "topic": "courage"},
    "sleep_restoration": {"title": "Night Architecture", "subtitle": "Building sleep from the inside", "author": "Master Sha", "topic": "grief"},
    "body_memory": {"title": "Held Ground", "subtitle": "Letting the body process what the mind cannot", "author": "Omote", "topic": "sleep_anxiety"},
    "solar_return": {"title": "Ember and Ash", "subtitle": "Burnout as initiation, not failure", "author": "Ra", "topic": "imposter_syndrome"},
    "devotion_path": {"title": "Open Vessel", "subtitle": "Devotion as a self-worth practice", "author": "Sai Ma", "topic": "grief"},
}


# ── Main ──

def generate_covers(
    mode: str = "gradient",
    brand_filter: str | None = None,
    fmt: str = "kdp_ebook",
    output_dir: Path | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Generate covers for all teacher brands."""
    data = _load_brand_data()
    results: list[dict[str, Any]] = []

    if output_dir is None:
        output_dir = REPO_ROOT / "brand-wizard-app" / "public" / "assets" / "covers"
    output_dir.mkdir(parents=True, exist_ok=True)

    width, height = FORMATS[fmt]
    layout = LAYOUT[fmt]

    brands = list(TEACHER_BOOKS.keys())
    if brand_filter:
        brands = [b for b in brands if b == brand_filter]

    print(f"Generating {len(brands)} covers ({fmt}, {width}×{height}, mode={mode})")
    print(f"Output: {output_dir}/")
    print()

    for brand_id in brands:
        book = TEACHER_BOOKS[brand_id]
        info = _get_brand_info(brand_id, data)
        # Allow per-book overrides (e.g. adi_da which isn't in brand_identity_system)
        if book.get("colors_override"):
            info["primary_colors"] = book["colors_override"]
        if book.get("accent_override"):
            info["accent_color"] = book["accent_override"]
        if book.get("display_name_override"):
            info["display_name"] = book["display_name_override"]
        teacher_id = book.get("teacher_override") or info.get("teacher") or brand_id
        seed = int(hashlib.md5(brand_id.encode()).hexdigest()[:8], 16) % (2**31)

        filename = f"cover_{teacher_id}_{book['topic']}.png"
        dest = output_dir / filename

        print(f"  {brand_id}: {book['title']}")

        if dry_run:
            print(f"    [DRY-RUN] → {dest}")
            results.append({"brand": brand_id, "path": str(dest), "status": "dry_run"})
            continue

        # Pass 1: Background
        if mode == "comfyui":
            bg = _generate_comfyui_bg(width, height, info, seed)
        else:
            bg = _generate_gradient_bg(width, height, info["primary_colors"], seed)

        # Pass 2: Typography overlay
        cover = _overlay_typography(
            bg,
            title=book["title"],
            subtitle=book["subtitle"],
            author=book["author"],
            colophon=info["display_name"],
            layout=layout,
            accent_color=info["accent_color"],
        )

        cover.save(str(dest), "PNG", optimize=True)
        size = dest.stat().st_size
        print(f"    OK → {filename} ({size:,} bytes)")
        results.append({"brand": brand_id, "path": str(dest), "status": "ok", "size": size})

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate bestseller-grade book covers.")
    parser.add_argument("--mode", choices=["gradient", "comfyui"], default="gradient",
                        help="Background mode: gradient (no API) or comfyui (FLUX)")
    parser.add_argument("--brand", default=None, help="Generate single brand only")
    parser.add_argument("--format", choices=list(FORMATS.keys()), default="kdp_ebook",
                        help="Cover format (default: kdp_ebook 1600×2560)")
    parser.add_argument("--output", type=Path, default=None, help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without generating")
    args = parser.parse_args()

    results = generate_covers(
        mode=args.mode,
        brand_filter=args.brand,
        fmt=args.format,
        output_dir=args.output,
        dry_run=args.dry_run,
    )

    ok = sum(1 for r in results if r["status"] == "ok")
    total = len(results)
    print(f"\n{'='*50}")
    print(f"Generated: {ok}/{total} covers")
    return 0 if ok == total or args.dry_run else 1


if __name__ == "__main__":
    raise SystemExit(main())
