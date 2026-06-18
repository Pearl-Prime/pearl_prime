#!/usr/bin/env python3
"""Package a rendered Devotion manga chapter into the weekly delivery layout.

Produces the two first-class manga deliverables the Brand Director Operations UI
serves (exactly like e-books), from an already-rendered chapter workspace:

  * webtoon vertical strip  -> {week}/webtoon/<name>.png   (single tall PNG,
        bubbled panels stacked with beat-aware gutters via the webtoon composer
        geometry — WEBTOON Canvas 800px-wide vertical scroll)
  * manga book PDF          -> {week}/kdp/<name>.pdf        (FRAME-composed
        pages assembled into a print-order PDF)

gen_brand_deliveries.py copies raw .png/.pdf (NOT .zip) into the dashboard public
dir and refreshes brand_deliveries/<base>.json, so these land as a real,
downloadable manga/webtoon intake for the brand.

  PYTHONPATH=. python3 scripts/manga/package_devotion_weekly.py \
      --workspace artifacts/manga/devotion_en_01_run \
      --brand devotion_path --week 2026-W25 --episode ep_001
"""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# Director deliveries are committed as PLAIN git blobs (.gitattributes:
# `brand-wizard-app/public/deliveries/** -filter -diff -merge` — CF Pages can't
# pull LFS), so each must stay under the no-binary-blobs CI cap (1 MB, exactly
# 1048576 B; .github/workflows/no-binary-blobs.yml). gen_brand_deliveries.py
# copies these files VERBATIM into public/deliveries/, so they must be born small.
# Target a hair under 1 MB for headroom (quantize/encode size is not exact).
TARGET_BYTES = 990_000


def _save_webtoon_under_target(canvas, out_png: Path, target: int = TARGET_BYTES) -> tuple[int, int]:
    """Save the tall webtoon strip as a <1 MB plain-blob PNG.

    Iyashikei art is soft, low-hue pastel — it survives adaptive-palette
    quantization gracefully. We keep a smooth 96-colour palette and shrink the
    reading width only as far as needed to clear the cap (maximising the width a
    reader actually sees). Full-res panel art stays in the workspace for QA.
    """
    from PIL import Image

    out_png.parent.mkdir(parents=True, exist_ok=True)
    W, H = canvas.size
    for width in range(min(W, 720), 320, -12):
        scale = width / W
        im = canvas if width == W else canvas.resize((width, max(1, int(H * scale))), Image.LANCZOS)
        q = im.quantize(colors=96, method=Image.FASTOCTREE, dither=Image.Dither.NONE)
        q.save(out_png, format="PNG", optimize=True)
        if out_png.stat().st_size <= target:
            return q.size
    # Floor: smallest tried width already written; report it.
    return q.size


def _save_pdf_under_target(pages: list[Path], out_pdf: Path, target: int = TARGET_BYTES) -> int:
    """Assemble page PNGs into a <1 MB manga PDF via img2pdf (lossless JPEG embed).

    PIL's PDF writer flate-encodes raw pixels (JPEG quality is ignored), so for a
    photoreal chapter it can't hit the cap. img2pdf embeds the JPEG DCT stream
    directly — best quality-per-byte. Search highest (scale, quality) that fits.
    """
    from io import BytesIO

    import img2pdf
    from PIL import Image

    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    ladder = [(0.72, 68), (0.68, 66), (0.64, 64), (0.60, 64),
              (0.58, 62), (0.55, 60), (0.50, 58), (0.45, 55)]
    last = b""
    for scale, quality in ladder:
        jpgs: list[bytes] = []
        for p in pages:
            im = Image.open(p).convert("RGB")
            if scale < 1.0:
                im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
            bio = BytesIO()
            im.save(bio, format="JPEG", quality=quality, optimize=True)
            jpgs.append(bio.getvalue())
            im.close()
        last = img2pdf.convert(jpgs)
        if len(last) <= target:
            out_pdf.write_bytes(last)
            return len(pages)
    out_pdf.write_bytes(last)  # floor: smallest tried, still write it
    return len(pages)


def build_webtoon_strip_png(ws: Path, out_png: Path) -> tuple[int, int]:
    """Stack bubbled panels into one tall 800px-wide webtoon strip PNG."""
    import json

    from PIL import Image

    from phoenix_v4.manga.chapter.webtoon_compose import (
        DEFAULT_STRIP_WIDTH_PX,
        _draw_panel_border,
        _paths_by_panel_id,
        _resize_to_width,
        compute_gutter_px,
    )

    script = json.loads((ws / "chapter_script_writer_handoff.json").read_text())
    manifest = json.loads((ws / "panel_images_manifest.json").read_text())
    by_id = _paths_by_panel_id(manifest)

    # Panel order from the script's pages; a page break => standard scene gutter.
    panels: list[dict] = []
    for pi, page in enumerate(script.get("pages") or []):
        for ix, panel in enumerate(page.get("panels") or []):
            e = dict(panel)
            if ix == 0 and pi > 0 and "beat_type" not in e:
                e["beat_type"] = "standard"
            panels.append(e)

    w = DEFAULT_STRIP_WIDTH_PX
    imgs: list = []
    y_ranges: list[tuple[int, int]] = []
    cursor = 0
    for i, panel in enumerate(panels):
        pid = str(panel.get("panel_id"))
        src = by_id.get(pid)
        if src is None or not src.is_file():
            raise SystemExit(f"panel {pid} has no ok image")
        with Image.open(src) as s:
            im = s.convert("RGB").copy()
        im = _resize_to_width(im, w)
        im = _draw_panel_border(im, 6, (40, 36, 32))  # soft dark ink frame
        if i > 0:
            cursor += compute_gutter_px(panel.get("beat_type"))
        y_ranges.append((cursor, cursor + im.height))
        imgs.append((cursor, im))
        cursor += im.height

    total_h = cursor
    canvas = Image.new("RGB", (w, total_h), (255, 252, 246))  # cream paper
    for y, im in imgs:
        canvas.paste(im, (0, y))
    saved_w, saved_h = _save_webtoon_under_target(canvas, out_png)
    for _, im in imgs:
        im.close()
    canvas.close()
    return saved_w, saved_h


def build_manga_pdf(ws: Path, out_pdf: Path) -> int:
    """Assemble FRAME-composed page PNGs into a single <1 MB manga PDF (print order)."""
    pages = sorted((ws / "final_page_composite").glob("page_*.png"))
    if not pages:
        raise SystemExit("no composed pages for PDF")
    return _save_pdf_under_target(pages, out_pdf)


def main() -> int:
    ap = argparse.ArgumentParser(description="Package Devotion manga weekly deliverables.")
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--brand", default="devotion_path")
    ap.add_argument("--week", default="2026-W25")
    ap.add_argument("--episode", default="ep_001")
    ap.add_argument("--series", default="devotion_en_01")
    args = ap.parse_args()

    import sys
    sys.path.insert(0, str(REPO))

    ws = args.workspace.resolve()
    pkg = REPO / "artifacts" / "weekly_packages" / args.brand / args.week
    stem = f"{args.series}_{args.episode}"

    webtoon_png = pkg / "webtoon" / f"{stem}_webtoon.png"
    kdp_pdf = pkg / "kdp" / f"{stem}_manga.pdf"

    w, h = build_webtoon_strip_png(ws, webtoon_png)
    print(f"webtoon strip: {webtoon_png.relative_to(REPO)}  ({w}x{h}px, {webtoon_png.stat().st_size//1024} KB)")

    n = build_manga_pdf(ws, kdp_pdf)
    print(f"manga PDF:     {kdp_pdf.relative_to(REPO)}  ({n} pages, {kdp_pdf.stat().st_size//1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
