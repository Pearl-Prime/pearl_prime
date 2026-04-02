#!/usr/bin/env python3
"""Raster onboarding proof assets as PNG (Pillow). Updates registry to .png paths.

Pearl Prime pipeline-demo tier — deterministic raster slides for gallery / Pages.
Requires: pip install -r scripts/onboarding/requirements-rasterize.txt

Usage:
  python3 scripts/onboarding/generate_onboarding_proof_pngs.py
"""
from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from onboarding_proof_visual import gradient_for_row, hex_to_rgb

ROOT = Path(__file__).resolve().parents[2]
CONFIG_REG = ROOT / "config" / "onboarding" / "example_registry.json"
PUBLIC_REG = ROOT / "brand-wizard-app" / "public" / "onboarding" / "example_registry.json"
PUBLIC_ROOT = ROOT / "brand-wizard-app" / "public"
TODAY = date.today().isoformat()

W, H = 1080, 1440
MARGIN = 72


def _try_import_pil():
    try:
        from PIL import Image, ImageDraw, ImageFont

        return Image, ImageDraw, ImageFont
    except ImportError as e:
        raise SystemExit(
            "Pillow is required. Run: pip install -r scripts/onboarding/requirements-rasterize.txt\n" + str(e)
        ) from e


def load_font(ImageFont, size: int):
    candidates = [
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 0),
        ("/System/Library/Fonts/Supplemental/Arial.ttf", 0),
        ("/Library/Fonts/Arial.ttf", 0),
        ("C:\\Windows\\Fonts\\arial.ttf", 0),
        ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 0),
    ]
    for path, idx in candidates:
        p = Path(path)
        if p.is_file():
            try:
                return ImageFont.truetype(str(p), size, index=idx)
            except OSError:
                continue
    return ImageFont.load_default()


def fill_gradient(Image, draw, top: tuple[int, int, int], bot: tuple[int, int, int]) -> None:
    for y in range(H):
        t = y / max(H - 1, 1)
        r = int(top[0] * (1 - t) + bot[0] * t)
        g = int(top[1] * (1 - t) + bot[1] * t)
        b = int(top[2] * (1 - t) + bot[2] * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def mid_lum(c1: tuple[int, int, int], c2: tuple[int, int, int]) -> float:
    m = ((c1[0] + c2[0]) / 2, (c1[1] + c2[1]) / 2, (c1[2] + c2[2]) / 2)
    return 0.299 * m[0] + 0.587 * m[1] + 0.114 * m[2]


def wrap_lines(text: str, max_chars: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    n = 0
    for w in words:
        add = len(w) + (1 if cur else 0)
        if n + add > max_chars and cur:
            lines.append(" ".join(cur))
            cur = [w]
            n = len(w)
        else:
            cur.append(w)
            n += add
    if cur:
        lines.append(" ".join(cur))
    return lines[:8]


def fs_asset_path(web_path: str) -> Path:
    return PUBLIC_ROOT / web_path.lstrip("/")


def is_audio_row(row: dict) -> bool:
    p = row.get("asset_path") or ""
    return bool(re.search(r"\.(mp3|wav|m4a|aac|ogg)$", str(p), re.I))


def png_path_for_row(row: dict) -> str:
    ap = row.get("asset_path") or ""
    rid = row.get("id", "")
    if isinstance(ap, str) and ap.lower().endswith(".svg"):
        return ap[:-4] + ".png"
    if not str(ap).strip() and isinstance(rid, str) and rid.startswith("pack_v1_"):
        return f"/onboarding/proof/generated/{rid}.png"
    return f"/onboarding/proof/generated/{rid}.png"


def render_mission(Image, ImageDraw, ImageFont, row: dict):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    g1, g2 = gradient_for_row(row)
    t1, t2 = hex_to_rgb(g1), hex_to_rgb(g2)
    fill_gradient(Image, draw, t1, t2)
    font_title = load_font(ImageFont, 36)
    font_lg = load_font(ImageFont, 30)
    font_sm = load_font(ImageFont, 22)
    font_tile = load_font(ImageFont, 24)
    tc = (248, 250, 252) if mid_lum(t1, t2) < 140 else (15, 23, 42)
    draw.rounded_rectangle([48, 48, W - 48, H - 48], radius=32, outline=(226, 232, 240), width=2)
    y = 80
    draw.text((MARGIN, y), row["id"], fill=tc, font=font_title)
    y += 52
    for line in wrap_lines(row.get("caption", ""), 42):
        draw.text((MARGIN, y), line, fill=tc, font=font_lg)
        y += 38
    y += 20
    draw.text((MARGIN, y), "Pearl Prime pipeline demo • PNG • multi-output composite", fill=tc, font=font_sm)
    tiles = [
        ("Book cover", 100, 420, 440, 520),
        ("Audiobook", 560, 420, 440, 520),
        ("Social / reel", 100, 980, 440, 520),
        ("Article card", 560, 980, 440, 520),
    ]
    for label, x, yy, ww, hh in tiles:
        draw.rounded_rectangle([x, yy, x + ww, yy + hh], radius=20, fill=(248, 250, 252), outline=(148, 163, 184))
        draw.text((x + 22, yy + 28), label, fill=(15, 23, 42), font=font_tile)
    draw.text((MARGIN, H - 100), f"onboarding_pipeline_demo • {TODAY}", fill=tc, font=font_sm)
    return img


def render_standard(Image, ImageDraw, ImageFont, row: dict):
    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)
    g1, g2 = gradient_for_row(row)
    t1, t2 = hex_to_rgb(g1), hex_to_rgb(g2)
    fill_gradient(Image, draw, t1, t2)
    font_id = load_font(ImageFont, 32)
    font_cap = load_font(ImageFont, 34)
    font_sub = load_font(ImageFont, 24)
    font_foot = load_font(ImageFont, 22)
    tc = (248, 250, 252) if mid_lum(t1, t2) < 140 else (15, 23, 42)
    muted = (203, 213, 225) if tc[0] > 200 else (148, 163, 184)
    draw.rounded_rectangle([MARGIN - 8, MARGIN - 8, W - MARGIN + 8, H - MARGIN + 8], radius=28, outline=muted, width=2)
    y = MARGIN + 8
    draw.text((MARGIN, y), row["id"], fill=tc, font=font_id)
    y += 50
    for line in wrap_lines(row.get("caption", ""), 40):
        draw.text((MARGIN, y), line, fill=tc, font=font_cap)
        y += 42
    y += 12
    sub = f"{row.get('lane','')} | {row.get('market','')} | {row.get('persona','')} | {row.get('style_variant','')}"
    draw.text((MARGIN, y), sub[:90], fill=muted, font=font_sub)
    y += 36
    draw.text((MARGIN, y), "Pearl Prime pipeline demo • PNG (not FLUX)", fill=muted, font=font_sub)
    foot = row.get("comparison_set_id") or "standalone"
    draw.text((MARGIN, H - 90), f"{foot} • {row.get('style_variant','')}", fill=muted, font=font_foot)
    draw.text((MARGIN, H - 52), f"onboarding_pipeline_demo • {TODAY}", fill=muted, font=font_foot)
    return img


def main() -> int:
    Image, ImageDraw, ImageFont = _try_import_pil()

    data = json.loads(CONFIG_REG.read_text(encoding="utf-8"))
    n = 0
    for row in data:
        if is_audio_row(row):
            continue
        fmt = row.get("format", "")
        if fmt not in (
            "cover",
            "manga_panel",
            "article_hero",
            "tool_ui",
            "persona_visual",
            "topic_visual",
        ):
            continue

        rid = row.get("id", "")
        is_pack = isinstance(rid, str) and rid.startswith("pack_v1_")

        if row.get("status") not in ("ready", "planned") and not is_pack:
            continue

        web_png = png_path_for_row(row)
        out = fs_asset_path(web_png)
        out.parent.mkdir(parents=True, exist_ok=True)

        if rid == "pack_v1_mission_output_overview":
            img = render_mission(Image, ImageDraw, ImageFont, row)
        else:
            img = render_standard(Image, ImageDraw, ImageFont, row)
        img.save(out, format="PNG", optimize=True)

        row["asset_path"] = web_png
        row["status"] = "ready"
        row["created_at"] = TODAY
        row.pop("placeholder_reason", None)
        row.pop("intentional_non_ready", None)
        if is_pack:
            row["source"] = "onboarding_pipeline_demo"
            row["production_fidelity"] = "pipeline_demo"
        n += 1

    blob = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    CONFIG_REG.write_text(blob, encoding="utf-8")
    PUBLIC_REG.write_text(blob, encoding="utf-8")
    print(f"Wrote {n} PNGs and synced registries.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
