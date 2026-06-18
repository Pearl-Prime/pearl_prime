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
    out_png.parent.mkdir(parents=True, exist_ok=True)
    # The iyashikei art is flat-colored with big quiet gutters → a palette (P-mode)
    # PNG compresses an order of magnitude smaller than RGB while staying a REAL,
    # directly-servable PNG (NOT LFS). Required: deliverables must be < 1 MB so they
    # commit as plain git blobs (.gitattributes -filter) and serve real bytes on
    # Cloudflare Pages, which does not pull LFS (see .gitattributes teacher_pics note).
    out = canvas.convert("P", palette=Image.ADAPTIVE, colors=256)
    out.save(out_png, format="PNG", optimize=True)
    if out_png.stat().st_size > 1_000_000:
        # Fall back to fewer colors if still over the 1 MB no-binary-blobs cap.
        canvas.convert("P", palette=Image.ADAPTIVE, colors=64).save(
            out_png, format="PNG", optimize=True
        )
    for _, im in imgs:
        im.close()
    canvas.close()
    return w, total_h


def build_manga_pdf(ws: Path, out_pdf: Path, *, max_bytes: int = 1_000_000) -> int:
    """Assemble FRAME-composed page PNGs into a single manga PDF (print order).

    JPEG-compresses the page rasters inside the PDF and steps quality/scale down
    until the file is < ``max_bytes`` (the no-binary-blobs 1 MB cap), so the PDF
    commits as a plain git blob and serves real bytes on Cloudflare Pages (which
    does not pull LFS). Reading-clear at tablet size; this is the review/preview
    edition, not the press master.
    """
    from PIL import Image

    page_paths = sorted((ws / "final_page_composite").glob("page_*.png"))
    if not page_paths:
        raise SystemExit("no composed pages for PDF")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    for scale, quality in ((1.0, 70), (0.8, 65), (0.66, 60), (0.5, 55)):
        imgs = []
        for p in page_paths:
            im = Image.open(p).convert("RGB")
            if scale < 1.0:
                im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))),
                               Image.Resampling.LANCZOS)
            imgs.append(im)
        imgs[0].save(
            out_pdf, format="PDF", save_all=True, append_images=imgs[1:],
            resolution=150.0, quality=quality,
        )
        for im in imgs:
            im.close()
        if out_pdf.stat().st_size <= max_bytes:
            break
    return len(page_paths)


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
