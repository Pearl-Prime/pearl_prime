#!/usr/bin/env python3
"""
build_manga_webtoon.py

Assembles manga panels into webtoon-format vertical scroll pages and a combined PDF.

For each chapter JSON, stacks panels vertically (800px wide) with a chapter title
header and 20px dark gutters. Panels with existing images are resized; panels
without images get styled placeholders. Outputs per-chapter PNGs and a combined
PDF to artifacts/manga_book/.

Usage:
    python3 scripts/release/build_manga_webtoon.py [--panels-dir DIR] [--chapters-dir DIR] [--out DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ── constants ────────────────────────────────────────────────────────────────

WEBTOON_WIDTH = 800
PANEL_HEIGHT = 1200          # placeholder panel height
GUTTER = 20                  # px gap between panels
HEADER_HEIGHT = 100          # chapter title banner height

BG_COLOR = (26, 21, 32)      # #1a1520 manga purple-dark
GUTTER_COLOR = (12, 10, 18)  # slightly darker for gutters
HEADER_COLOR = (30, 25, 40)

WHITE = (255, 255, 255)
GRAY = (160, 160, 170)
RED = (220, 60, 60)
LABEL_COLOR = (130, 120, 150)


# ── font helpers ─────────────────────────────────────────────────────────────

def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load a reasonable system font; fall back to default bitmap."""
    candidates = []
    if bold:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFCompact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
    else:
        candidates = [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFCompact.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


FONT_TITLE = _load_font(36, bold=True)
FONT_LABEL = _load_font(20, bold=True)
FONT_BODY = _load_font(18)
FONT_SMALL = _load_font(14)
FONT_SFX = _load_font(22, bold=True)


# ── text wrapping helper ────────────────────────────────────────────────────

def _wrap(text: str, font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
          max_width: int) -> list[str]:
    """Wrap text to fit within max_width pixels using the given font."""
    if not text:
        return []
    # Estimate chars per line, then refine
    avg_char_w = max(font.getlength("M"), 8)
    chars = max(int(max_width / avg_char_w), 10)
    lines = textwrap.wrap(text, width=chars)
    # Verify and re-wrap if any line is too long
    refined: list[str] = []
    for line in lines:
        while font.getlength(line) > max_width and chars > 5:
            chars -= 2
            sub = textwrap.wrap(line, width=chars)
            line = sub[0]
            if len(sub) > 1:
                lines.extend(sub[1:])
        refined.append(line)
    return refined


def _text_height(lines: list[str], font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
                 spacing: int = 4) -> int:
    bbox = font.getbbox("Ay")
    line_h = bbox[3] - bbox[1] + spacing
    return line_h * len(lines)


# ── placeholder generation ───────────────────────────────────────────────────

def make_placeholder(panel: dict) -> Image.Image:
    """Generate a styled placeholder image for a missing panel."""
    img = Image.new("RGB", (WEBTOON_WIDTH, PANEL_HEIGHT), BG_COLOR)
    draw = ImageDraw.Draw(img)
    pad = 40
    max_w = WEBTOON_WIDTH - 2 * pad
    y = pad

    # Panel ID label
    pid = panel.get("panel_id", "???")
    draw.text((pad, y), f"[ {pid} ]", fill=LABEL_COLOR, font=FONT_LABEL)
    y += 35

    # Narration / dialogue (white, centered block)
    narration = panel.get("narration", "")
    dialogue = panel.get("dialogue", "")
    main_text = dialogue if dialogue else narration
    if main_text:
        lines = _wrap(main_text, FONT_BODY, max_w)
        for line in lines:
            lw = FONT_BODY.getlength(line)
            x = pad + (max_w - lw) / 2
            draw.text((x, y), line, fill=WHITE, font=FONT_BODY)
            y += 26
        y += 20

    # Visual prompt (smaller gray)
    prompt = panel.get("visual_prompt", "")
    if prompt:
        lines = _wrap(prompt, FONT_SMALL, max_w)
        for line in lines:
            draw.text((pad, y), line, fill=GRAY, font=FONT_SMALL)
            y += 20
        y += 15

    # SFX in red
    sfx = panel.get("sfx", "")
    if sfx:
        lines = _wrap(sfx, FONT_SFX, max_w)
        for line in lines:
            lw = FONT_SFX.getlength(line)
            x = pad + (max_w - lw) / 2
            draw.text((x, y), line, fill=RED, font=FONT_SFX)
            y += 30

    return img


# ── chapter assembly ─────────────────────────────────────────────────────────

def build_chapter_strip(chapter: dict, panels_dir: Path) -> tuple[Image.Image, int, int]:
    """
    Build a single vertical webtoon strip for one chapter.

    Returns (image, found_count, placeholder_count).
    """
    title = chapter.get("title", "Untitled")
    pages = chapter.get("pages", [])

    # Collect panel images in order
    panel_images: list[Image.Image] = []
    found = 0
    placeholders = 0

    for page in pages:
        for panel in page.get("panels", []):
            pid = panel.get("panel_id", "")
            img_path = panels_dir / f"{pid}.png"
            if img_path.exists():
                pimg = Image.open(img_path).convert("RGB")
                # Resize to WEBTOON_WIDTH, keeping aspect ratio
                w, h = pimg.size
                new_h = int(h * (WEBTOON_WIDTH / w))
                pimg = pimg.resize((WEBTOON_WIDTH, new_h), Image.LANCZOS)
                panel_images.append(pimg)
                found += 1
            else:
                panel_images.append(make_placeholder(panel))
                placeholders += 1

    # Calculate total height
    total_h = HEADER_HEIGHT
    for pimg in panel_images:
        total_h += GUTTER + pimg.height
    total_h += GUTTER  # bottom margin

    # Build the strip
    strip = Image.new("RGB", (WEBTOON_WIDTH, total_h), GUTTER_COLOR)
    draw = ImageDraw.Draw(strip)

    # Chapter title header
    draw.rectangle([0, 0, WEBTOON_WIDTH, HEADER_HEIGHT], fill=HEADER_COLOR)
    tw = FONT_TITLE.getlength(title)
    tx = (WEBTOON_WIDTH - tw) / 2
    ty = (HEADER_HEIGHT - 40) / 2
    draw.text((tx, ty), title, fill=WHITE, font=FONT_TITLE)

    # Paste panels
    y = HEADER_HEIGHT + GUTTER
    for pimg in panel_images:
        strip.paste(pimg, (0, y))
        y += pimg.height + GUTTER

    return strip, found, placeholders


# ── PDF generation (PIL-native, no reportlab needed) ─────────────────────────

def save_pdf(strips: list[Image.Image], out_path: Path) -> None:
    """Save a multi-page PDF from a list of PIL images."""
    if not strips:
        return
    # Convert all to RGB (required for PDF save)
    rgb_strips = [s.convert("RGB") for s in strips]
    rgb_strips[0].save(
        str(out_path),
        save_all=True,
        append_images=rgb_strips[1:],
        resolution=150.0,
    )


# ── main ─────────────────────────────────────────────────────────────────────

CHAPTER_FILES = [
    "ch01_the_2am_scroll.json",
    "ch02_the_bodys_refusal.json",
    "ch03_the_breath_before_sleep.json",
    "ch04_the_morning_after.json",
]


def main() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    parser = argparse.ArgumentParser(description="Build manga webtoon strips and PDF")
    parser.add_argument(
        "--panels-dir",
        type=Path,
        default=repo_root / "artifacts" / "pipeline_examples" / "manga_book" / "panels",
        help="Directory containing panel PNGs (default: artifacts/pipeline_examples/manga_book/panels)",
    )
    parser.add_argument(
        "--chapters-dir",
        type=Path,
        default=repo_root / "artifacts" / "pipeline_examples" / "manga_book",
        help="Directory containing chapter JSON scripts",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=repo_root / "artifacts" / "manga_book",
        help="Output directory (default: artifacts/manga_book)",
    )
    args = parser.parse_args()

    panels_dir: Path = args.panels_dir
    chapters_dir: Path = args.chapters_dir
    out_dir: Path = args.out

    if not panels_dir.is_dir():
        print(f"ERROR: panels directory not found: {panels_dir}", file=sys.stderr)
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    strips: list[Image.Image] = []
    summary_rows: list[tuple[str, int, int]] = []

    for ch_file in CHAPTER_FILES:
        ch_path = chapters_dir / ch_file
        if not ch_path.exists():
            print(f"WARNING: chapter file not found, skipping: {ch_path}", file=sys.stderr)
            continue

        with open(ch_path) as f:
            chapter = json.load(f)

        ch_id = chapter.get("chapter_id", ch_file)
        title = chapter.get("title", "Untitled")

        strip, found, placeholder = build_chapter_strip(chapter, panels_dir)
        strips.append(strip)
        summary_rows.append((title, found, placeholder))

        # Derive output name from chapter file name: ch01_the_2am_scroll -> ch01_webtoon
        ch_num = ch_file.split("_")[0]  # "ch01"
        out_png = out_dir / f"{ch_num}_webtoon.png"
        strip.save(str(out_png))
        print(f"  Saved: {out_png}  ({strip.width}x{strip.height})")

    # Combined PDF
    if strips:
        pdf_path = out_dir / "junko_sleep_anxiety_complete.pdf"
        save_pdf(strips, pdf_path)
        print(f"  Saved PDF: {pdf_path}")

    # Summary
    print()
    print("=" * 60)
    print("  MANGA WEBTOON BUILD SUMMARY")
    print("=" * 60)
    total_found = 0
    total_placeholder = 0
    for title, found, placeholder in summary_rows:
        total = found + placeholder
        total_found += found
        total_placeholder += placeholder
        print(f"  {title:<35s}  {found:>2}/{total:>2} found  ({placeholder} placeholder)")
    print("-" * 60)
    grand = total_found + total_placeholder
    print(f"  {'TOTAL':<35s}  {total_found:>2}/{grand:>2} found  ({total_placeholder} placeholder)")
    print("=" * 60)


if __name__ == "__main__":
    main()
