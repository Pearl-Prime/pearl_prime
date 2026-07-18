#!/usr/bin/env python3
"""Generate brand-consistent typographic KDP covers for stillness_press deep build.

Two-stage cover rule (COVER-TEXT-OVERLAY): FLUX renders imagery, PIL composites text.
Pearl Star ComfyUI (192.168.1.112:8188) was UNREACHABLE in-session, so this produces
the PIL text layer over a clean iyashikei-palette gradient background ($0). When Pearl
Star is reachable, the gradient can be swapped for a rendered iyashikei field; the text
compositing stays identical.

Palette mirrors the stillness_press manga visual grammar (panel_prompts.json):
warm cream + soft dawn gold, muted sage + pale terracotta, jade-green accent.

Output: 1600x2560 PNG (KDP storefront/embedded portrait, 1.6:1).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1600, 2560

# iyashikei palette
CREAM = (244, 237, 224)
DAWN_GOLD = (232, 213, 178)
SAGE = (150, 165, 142)
TERRACOTTA = (196, 144, 116)
JADE = (96, 138, 120)
INK = (58, 54, 48)
SOFT_INK = (96, 90, 80)

SERIF = "/System/Library/Fonts/Supplemental/Georgia.ttf"
SERIF_BOLD = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
SERIF_ITALIC = "/System/Library/Fonts/Supplemental/Georgia Italic.ttf"


def vertical_gradient(top: tuple, bottom: tuple) -> Image.Image:
    base = Image.new("RGB", (W, H), top)
    top_r, top_g, top_b = top
    bot_r, bot_g, bot_b = bottom
    px = base.load()
    for y in range(H):
        t = y / (H - 1)
        r = int(top_r + (bot_r - top_r) * t)
        g = int(top_g + (bot_g - top_g) * t)
        b = int(top_b + (bot_b - top_b) * t)
        for x in range(W):
            px[x, y] = (r, g, b)
    return base


def wrap(draw, text, font, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def make_cover(title, subtitle, author, publisher, out_path):
    img = vertical_gradient(CREAM, DAWN_GOLD)
    d = ImageDraw.Draw(img)

    # soft sage band behind title block (breathable negative space, low contrast)
    band_top, band_bot = 760, 1560
    band = Image.new("RGB", (W, band_bot - band_top), SAGE)
    band = Image.blend(img.crop((0, band_top, W, band_bot)), band, 0.16)
    img.paste(band, (0, band_top))
    d = ImageDraw.Draw(img)

    # jade through-line rule (the manga visual through-line motif)
    d.line([(W // 2 - 90, 700), (W // 2 + 90, 700)], fill=JADE, width=6)

    margin = 150
    max_w = W - 2 * margin

    # Title
    title_font = ImageFont.truetype(SERIF_BOLD, 132)
    title_lines = wrap(d, title.upper(), title_font, max_w)
    if len(title_lines) > 3:  # shrink for long titles
        title_font = ImageFont.truetype(SERIF_BOLD, 104)
        title_lines = wrap(d, title.upper(), title_font, max_w)
    y = 880
    for ln in title_lines:
        lw = d.textlength(ln, font=title_font)
        d.text(((W - lw) / 2, y), ln, font=title_font, fill=INK)
        y += title_font.size + 22

    # Subtitle
    y += 50
    sub_font = ImageFont.truetype(SERIF_ITALIC, 52)
    for ln in wrap(d, subtitle, sub_font, max_w - 60):
        lw = d.textlength(ln, font=sub_font)
        d.text(((W - lw) / 2, y), ln, font=sub_font, fill=TERRACOTTA)
        y += sub_font.size + 16

    # Author (lower third)
    auth_font = ImageFont.truetype(SERIF, 70)
    aw = d.textlength(author, font=auth_font)
    d.text(((W - aw) / 2, 2120), author, font=auth_font, fill=INK)

    # Publisher (footer)
    pub_font = ImageFont.truetype(SERIF, 40)
    pw = d.textlength(publisher.upper(), font=pub_font)
    d.text(((W - pw) / 2, 2360), publisher.upper(), font=pub_font, fill=SOFT_INK)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    return out_path


BOOKS = [
    ("The Room Is Safe",
     "A Body-First Guide to Anxiety for People Who Can't Switch Off",
     "anxiety_gen_z_professionals"),
    ("The Hour That Won't Let Go",
     "A Somatic Guide to the 3 A.M. Mind for Women Tired of Being Tired",
     "sleep_anxiety_midlife_women"),
    ("The Fourth Draft of a Text Message",
     "A Contemplative Guide to Quieting the Mind That Won't Stop Rehearsing",
     "overthinking_millennial_women_professionals"),
    ("The Dashboard in Your Chest",
     "A Body-First Guide to Anxiety for High-Output People Running on Empty",
     "anxiety_tech_finance_burnout"),
]

if __name__ == "__main__":
    out_dir = Path(__file__).parent / "covers"
    for title, subtitle, slug in BOOKS:
        p = make_cover(title, subtitle, "Ahjan", "Stillness Press", out_dir / f"cover_{slug}.png")
        print(f"  cover -> {p}")
    print(f"{len(BOOKS)} covers built")
