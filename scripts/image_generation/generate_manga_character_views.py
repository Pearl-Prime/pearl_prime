#!/usr/bin/env python3
"""Generate manga character views for teacher showcase: front, 3/4, profile.

Modes:
  --mode comfyui: ComfyUI FLUX on Pearl Star (production quality)
  --mode placeholder: PIL gradient + text (immediate, no API)

Usage:
  python3 scripts/image_generation/generate_manga_character_views.py
  python3 scripts/image_generation/generate_manga_character_views.py --mode comfyui
  python3 scripts/image_generation/generate_manga_character_views.py --teacher ahjan
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
OUTPUT_DIR = REPO_ROOT / "brand-wizard-app" / "public" / "assets" / "manga_covers"

VIEWS = ["front", "three_quarter", "profile"]
VIEW_LABELS = {"front": "Front Portrait", "three_quarter": "3/4 View", "profile": "Profile View"}

# Teacher → brand colors (from brand_identity_system.yaml)
TEACHER_COLORS = {
    "ahjan": (["#64748B", "#D4A574"], "#B8860B"),
    "adi_da": (["#4A1A2A", "#1A0A10"], "#FF6B35"),
    "joshin": (["#1A1A1A", "#FFFFFF"], "#8B7355"),
    "junko": (["#F2C14E", "#5A4A8A"], "#FFD700"),  # per OPD-111 — cosmic/channeling palette (gold/luminous blue)
    "miyuki": (["#F5F0E8", "#A0937D"], "#8B7D6B"),  # per OPD-111 — inherits former junko wabi-sabi palette
    "maat": (["#312E81", "#D97706"], "#F59E0B"),
    "master_feung": (["#8B7355", "#D4A574"], "#C5A03D"),
    "master_sha": (["#1A0033", "#8B5CF6"], "#A78BFA"),
    "master_wu": (["#36454F", "#DC143C"], "#8B0000"),
    "miki": (["#1E293B", "#22D3EE"], "#06B6D4"),
    "omote": (["#36454F", "#CD5C5C"], "#A0522D"),
    "pamela_fellows": (["#FFF5EE", "#D4A0A0"], "#C1666B"),
    "ra": (["#1A1410", "#EA580C"], "#F97316"),
    "sai_ma": (["#7C3AED", "#FBB6CE"], "#A855F7"),
}

TEACHER_NAMES = {
    "ahjan": "Ahjan", "adi_da": "Adi Da", "joshin": "Joshin",
    "junko": "Junko", "miyuki": "Miyuki", "maat": "Maat", "master_feung": "Master Feung",
    "master_sha": "Master Sha", "master_wu": "Master Wu", "miki": "Miki",
    "omote": "Omote", "pamela_fellows": "Pamela Fellows", "ra": "Ra",
    "sai_ma": "Sai Ma",
}


def _hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _generate_placeholder(
    teacher_id: str, view: str, width: int, height: int, output_path: Path
) -> bool:
    """Generate styled placeholder with gradient + character silhouette indication."""
    from PIL import Image, ImageDraw

    colors, accent = TEACHER_COLORS.get(teacher_id, (["#333333", "#666666"], "#999999"))
    c1 = _hex_to_rgb(colors[0])
    c2 = _hex_to_rgb(colors[1])
    acc = _hex_to_rgb(accent)

    img = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(img)

    # Gradient background
    for y in range(height):
        ratio = y / height
        r = int(c1[0] * (1 - ratio) + c2[0] * ratio)
        g = int(c1[1] * (1 - ratio) + c2[1] * ratio)
        b = int(c1[2] * (1 - ratio) + c2[2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Character silhouette (circle for head + trapezoid for shoulders)
    cx, cy = width // 2, int(height * 0.35)
    head_r = int(min(width, height) * 0.12)

    # View-specific offset
    if view == "three_quarter":
        cx = int(width * 0.45)
    elif view == "profile":
        cx = int(width * 0.40)

    # Head circle
    draw.ellipse(
        [cx - head_r, cy - head_r, cx + head_r, cy + head_r],
        fill=acc, outline=None,
    )

    # Shoulders
    shoulder_top = cy + head_r + int(height * 0.02)
    shoulder_w = int(head_r * 2.5)
    draw.polygon([
        (cx - shoulder_w, shoulder_top + int(height * 0.15)),
        (cx - int(head_r * 0.8), shoulder_top),
        (cx + int(head_r * 0.8), shoulder_top),
        (cx + shoulder_w, shoulder_top + int(height * 0.15)),
    ], fill=acc)

    # Text labels
    try:
        from PIL import ImageFont
        font_path = "/System/Library/Fonts/Helvetica.ttc"
        title_font = ImageFont.truetype(font_path, max(16, height // 30)) if os.path.exists(font_path) else ImageFont.load_default()
        label_font = ImageFont.truetype(font_path, max(12, height // 40)) if os.path.exists(font_path) else ImageFont.load_default()
    except Exception:
        from PIL import ImageFont
        title_font = ImageFont.load_default()
        label_font = ImageFont.load_default()

    name = TEACHER_NAMES.get(teacher_id, teacher_id)
    lum = (0.299 * c1[0] + 0.587 * c1[1] + 0.114 * c1[2]) / 255
    text_color = (255, 255, 255) if lum < 0.5 else (30, 30, 30)

    # Name at top
    bbox = draw.textbbox((0, 0), name, font=title_font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, int(height * 0.05)), name, fill=text_color, font=title_font)

    # View label at bottom
    label = VIEW_LABELS[view]
    bbox = draw.textbbox((0, 0), label, font=label_font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, int(height * 0.88)), label, fill=text_color, font=label_font)

    # "Manga Character" indicator
    indicator = "MANGA CHARACTER"
    bbox = draw.textbbox((0, 0), indicator, font=label_font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, int(height * 0.93)), indicator, fill=(*acc, ), font=label_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(str(output_path), "PNG", optimize=True)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate manga character views.")
    parser.add_argument("--mode", choices=["placeholder", "comfyui"], default="placeholder")
    parser.add_argument("--teacher", default=None)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    teachers = list(TEACHER_NAMES.keys())
    if args.teacher:
        teachers = [t for t in teachers if t == args.teacher]

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = 0
    total = 0

    for tid in teachers:
        print(f"\n  {tid}:")
        for view in VIEWS:
            filename = f"{tid}_{view}.png"
            output_path = OUTPUT_DIR / filename
            total += 1

            if args.dry_run:
                print(f"    [DRY-RUN] → {filename}")
                ok += 1
                continue

            if args.mode == "comfyui":
                # TODO: implement ComfyUI generation using teacher_character_prompts.yaml
                print(f"    ComfyUI mode not yet implemented, using placeholder")
                success = _generate_placeholder(tid, view, 800, 1200, output_path)
            else:
                success = _generate_placeholder(tid, view, 800, 1200, output_path)

            if success:
                size = output_path.stat().st_size
                print(f"    OK ({size:,} bytes) → {filename}")
                ok += 1
            else:
                print(f"    FAILED → {filename}")

    print(f"\n{'='*50}")
    print(f"Generated: {ok}/{total} character views")
    print(f"Output: {OUTPUT_DIR}/")
    return 0 if ok == total else 1


if __name__ == "__main__":
    raise SystemExit(main())
