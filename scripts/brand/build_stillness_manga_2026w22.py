#!/usr/bin/env python3
"""
Manga axis MVP — assemble stillness_press 2026-W22 KDP + WEBTOON variants from
existing V4 composited panels.

Reuses the 35 ep_001 panels in
``artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v4_qwen/ep_001/``
to produce:

  * artifacts/weekly_packages/stillness_press/2026-W22/kdp/stillness_press_2026-W22_manga.pdf
    (one panel per page, B5 print at 1080×1920 source)
  * artifacts/weekly_packages/stillness_press/2026-W22/webtoon/stillness_press_2026-W22_manga.png
    (single tall vertical-scroll composite, 1080-wide × N tall)

Then updates ``manifest.json`` so ``deliverables.manga_panels.files`` lists the new
artifacts (real content, not the README stub), and re-runs
``build_admin_packets`` for stillness_press so the per-platform ZIPs pick up the
new content.

Usage:
  PYTHONPATH=. python3 scripts/brand/build_stillness_manga_2026w22.py
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.brand.build_admin_packets import (  # noqa: E402
    build_platform_zips_for_brand,
    build_zip_for_brand,
)

BRAND_ID = "stillness_press"
WEEK_ISO = "2026-W22"
SERIES_DIR_NAME = "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
EPISODE_ID = "ep_001"
EPISODE_TITLE = "The Alarm Is Lying — Episode 1"

GUTTER_PX = 24  # vertical gap between webtoon panels


def _panel_paths(repo_root: Path) -> list[Path]:
    """Discover ep_001 V4 composited panel PNGs in numeric order."""
    panels_dir = (
        repo_root
        / "artifacts"
        / "manga"
        / SERIES_DIR_NAME
        / "composed_v4_qwen"
        / EPISODE_ID
    )
    if not panels_dir.is_dir():
        raise SystemExit(f"Missing source panel dir: {panels_dir}")
    panels = sorted(
        p for p in panels_dir.glob("ep001_*.png") if p.is_file()
    )
    if not panels:
        raise SystemExit(f"No ep001_*.png panels in {panels_dir}")
    return panels


def build_kdp_pdf(panel_paths: list[Path], out_pdf: Path) -> None:
    """One panel per PDF page (PIL native, no reportlab)."""
    if not panel_paths:
        raise ValueError("No panels for PDF")
    out_pdf.parent.mkdir(parents=True, exist_ok=True)
    pages: list[Image.Image] = []
    for p in panel_paths:
        img = Image.open(p)
        if img.mode != "RGB":
            img = img.convert("RGB")
        pages.append(img)
    pages[0].save(
        str(out_pdf),
        save_all=True,
        append_images=pages[1:],
        resolution=150.0,
    )


def build_webtoon_png(panel_paths: list[Path], out_png: Path) -> tuple[int, int]:
    """Vertical-scroll composite: panels stacked with gutters at native 1080 width."""
    if not panel_paths:
        raise ValueError("No panels for WEBTOON")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    imgs = [Image.open(p).convert("RGB") for p in panel_paths]
    width = max(img.width for img in imgs)
    total_h = sum(img.height for img in imgs) + GUTTER_PX * (len(imgs) - 1)
    canvas = Image.new("RGB", (width, total_h), color=(255, 255, 255))
    y = 0
    for i, img in enumerate(imgs):
        # Pad narrow panels horizontally to canvas width (centered)
        x = (width - img.width) // 2
        canvas.paste(img, (x, y))
        y += img.height
        if i != len(imgs) - 1:
            y += GUTTER_PX
    canvas.save(str(out_png), "PNG", optimize=True)
    return (width, total_h)


def _rel(path: Path, repo_root: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def update_manifest(
    repo_root: Path,
    manifest_path: Path,
    kdp_pdf: Path,
    webtoon_png: Path,
    panel_count: int,
) -> dict:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    rel_pdf = _rel(kdp_pdf, repo_root)
    rel_png = _rel(webtoon_png, repo_root)

    deliverables = manifest.setdefault("deliverables", {})
    deliverables["manga_panels"] = {
        "status": "ready",
        "files": [rel_pdf, rel_png],
        "episode_id": EPISODE_ID,
        "episode_title": EPISODE_TITLE,
        "panel_count": panel_count,
        "render_source": "V4_composed_v4_qwen",
        "kdp_pdf": rel_pdf,
        "webtoon_png": rel_png,
    }
    manifest["generated_at"] = ts
    # Append "manga_axis_mvp" tag without clobbering sibling-axis package_type tags.
    existing_type = (manifest.get("package_type") or "").strip()
    if "manga_axis_mvp" not in existing_type:
        manifest["package_type"] = (
            f"{existing_type}+manga_axis_mvp" if existing_type and existing_type != "stub_mvp" else "manga_axis_mvp"
        )
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    repo_root: Path = args.repo_root.resolve()

    pkg_dir = repo_root / "artifacts" / "weekly_packages" / BRAND_ID / WEEK_ISO
    manifest_path = pkg_dir / "manifest.json"
    if not manifest_path.is_file():
        raise SystemExit(f"Missing manifest: {manifest_path}")

    panel_paths = _panel_paths(repo_root)
    print(f"Found {len(panel_paths)} ep_001 V4 panels")

    kdp_pdf = pkg_dir / "kdp" / f"{BRAND_ID}_{WEEK_ISO}_manga.pdf"
    build_kdp_pdf(panel_paths, kdp_pdf)
    pdf_size = kdp_pdf.stat().st_size
    print(f"Wrote KDP PDF: {kdp_pdf} ({pdf_size / 1024:.1f} KiB)")

    webtoon_png = pkg_dir / "webtoon" / f"{BRAND_ID}_{WEEK_ISO}_manga.png"
    w, h = build_webtoon_png(panel_paths, webtoon_png)
    png_size = webtoon_png.stat().st_size
    print(f"Wrote WEBTOON PNG: {webtoon_png} ({w}x{h}, {png_size / 1024 / 1024:.1f} MiB)")

    update_manifest(repo_root, manifest_path, kdp_pdf, webtoon_png, len(panel_paths))
    print(f"Updated manifest: {manifest_path}")

    # Rebuild monolithic + per-platform ZIPs for this brand/week so the API serves
    # the new content (manga_panels.files now lists the real PDF/PNG, not the
    # README stub).
    pkg_base = repo_root / "artifacts" / "weekly_packages"
    zip_path, missing = build_zip_for_brand(
        repo_root, BRAND_ID, WEEK_ISO, packages_dir=pkg_base
    )
    if zip_path is None:
        raise SystemExit("Monolithic zip build returned None")
    if missing:
        print(f"warn: monolithic zip missing {len(missing)} file(s): {missing[:3]}")
    print(f"Rebuilt monolithic ZIP: {zip_path}")

    plat_zips = build_platform_zips_for_brand(
        repo_root, BRAND_ID, WEEK_ISO, packages_dir=pkg_base
    )
    print(f"Rebuilt {len(plat_zips)} per-platform ZIP(s)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
