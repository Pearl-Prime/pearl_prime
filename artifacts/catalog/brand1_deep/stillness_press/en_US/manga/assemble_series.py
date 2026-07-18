#!/usr/bin/env python3
"""Assemble rendered stillness_press manga panels into deliverables.

Produces, from the per-panel PNGs under rendered/<series_dir>/ep_001/:
  - KDP PDF  (one panel per page, 150 DPI)            [LOCAL, not committed]
  - WEBTOON vertical strip (800px-wide concat)        [LOCAL, not committed]
  - contact_sheet.png (downscaled grid, < 1 MB)       [committed proof]

Following the brand-1 BUILD_MANIFEST convention: full-res PDF + strip are large
binaries that are deterministically reproducible, so they are assembled LOCALLY
for operator review and NOT committed (LFS budget exhausted). Only the small
contact-sheet thumbnail is committed as in-repo visual proof.

Usage:
  python3 assemble_series.py --series 2
  python3 assemble_series.py --series 3
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

from PIL import Image

SERIES_DIR = {
    "1": "../../../../manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen",
    "2": "rendered/stillness_press_sleep_vol1",
    "3": "rendered/stillness_press_somatic_vol1",
}
TITLES = {
    "2": "The Night Before You Sleep — Ep 1",
    "3": "Hands, Shoulders, Breath — Ep 1",
}


def load_panels(panel_dir: Path) -> list[Image.Image]:
    paths = sorted(panel_dir.glob("ep001_*.png"))
    return [Image.open(p).convert("RGB") for p in paths]


def make_pdf(panels: list[Image.Image], out_pdf: Path) -> int:
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    panels[0].save(out_pdf, "PDF", save_all=True, append_images=panels[1:], resolution=150)
    return out_pdf.stat().st_size


def make_webtoon_strip(panels: list[Image.Image], out_png: Path, width: int = 800) -> int:
    scaled = []
    for p in panels:
        h = int(p.height * width / p.width)
        scaled.append(p.resize((width, h), Image.LANCZOS))
    total_h = sum(p.height for p in scaled)
    strip = Image.new("RGB", (width, total_h), (255, 255, 255))
    y = 0
    for p in scaled:
        strip.paste(p, (0, y))
        y += p.height
    out_png.parent.mkdir(parents=True, exist_ok=True)
    strip.save(out_png, "PNG", optimize=True)
    return out_png.stat().st_size


def make_contact_sheet(panels: list[Image.Image], out_png: Path,
                       cols: int = 6, thumb_w: int = 200, max_bytes: int = 950_000) -> int:
    n = len(panels)
    rows = math.ceil(n / cols)
    thumb_h = int(panels[0].height * thumb_w / panels[0].width)
    pad = 6
    sheet_w = cols * thumb_w + (cols + 1) * pad
    sheet_h = rows * thumb_h + (rows + 1) * pad
    sheet = Image.new("RGB", (sheet_w, sheet_h), (244, 237, 224))
    for i, p in enumerate(panels):
        r, c = divmod(i, cols)
        t = p.resize((thumb_w, thumb_h), Image.LANCZOS)
        x = pad + c * (thumb_w + pad)
        y = pad + r * (thumb_h + pad)
        sheet.paste(t, (x, y))
    out_png.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out_png, "PNG", optimize=True)
    if out_png.stat().st_size > max_bytes:
        for colors in (256, 192, 128, 96, 64, 48, 32, 24, 16):
            q = sheet.quantize(colors=colors, method=Image.MEDIANCUT)
            q.save(out_png, "PNG", optimize=True)
            if out_png.stat().st_size <= max_bytes:
                break
    # last resort: shrink the sheet itself if palette reduction wasn't enough
    if out_png.stat().st_size > max_bytes:
        small = sheet.copy()
        small.thumbnail((sheet.width * 3 // 4, sheet.height * 3 // 4), Image.LANCZOS)
        q = small.quantize(colors=32, method=Image.MEDIANCUT)
        q.save(out_png, "PNG", optimize=True)
    return out_png.stat().st_size


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True, choices=["1", "2", "3"])
    ap.add_argument("--no-fullres", action="store_true",
                    help="skip the large PDF + strip (contact sheet only)")
    args = ap.parse_args()

    base = Path(__file__).parent
    panel_dir = (base / SERIES_DIR[args.series] / "ep_001").resolve()
    panels = load_panels(panel_dir)
    if not panels:
        print(f"no panels found in {panel_dir}")
        return 1
    print(f"=== Series {args.series}: {len(panels)} panels from {panel_dir} ===")

    assembled = base / "assembled" / f"series{args.series}_ep001"
    if not args.no_fullres:
        pdf_sz = make_pdf(panels, assembled / "kdp.pdf")
        print(f"  KDP PDF        -> {assembled/'kdp.pdf'} ({pdf_sz/1e6:.1f} MB) [LOCAL]")
        strip_sz = make_webtoon_strip(panels, assembled / "webtoon_strip.png")
        print(f"  WEBTOON strip  -> {assembled/'webtoon_strip.png'} ({strip_sz/1e6:.1f} MB) [LOCAL]")

    # contact sheet -> committed proof, lives next to the script
    cs = base / "rendered" / f"series{args.series}_contact_sheet.png"
    cs_sz = make_contact_sheet(panels, cs)
    print(f"  contact sheet  -> {cs} ({cs_sz/1e3:.0f} KB) [COMMITTED PROOF]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
