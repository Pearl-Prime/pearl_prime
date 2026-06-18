"""Lay out panel PNGs into per-page composites.

Historically this composed a single edge-to-edge *horizontal strip* per page and
ignored ``config/manga/panel_layout_templates/*.yaml`` entirely. It now delegates
to the FRAME engine (``phoenix_v4/manga/chapter/page_frame.py``): named
multi-panel grid templates + a PIL frame/gutter renderer that draws panel borders,
lays inter-panel gutters, fits each panel into its cell by aspect, and supports
RTL page-turn order. The healing/iyashikei register (Devotion brand / Open Vessel
Press / Sai Ma) gets a calmer layout family with wider gutters and more whitespace.

The public contract is unchanged: ``compose_final_page_pngs(chapter_script,
panel_images_manifest, out_dir) -> list[Path]`` writing ``page_001.png`` ….
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping


def _paths_by_panel_id(manifest: Mapping[str, Any]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for p in manifest.get("panels") or []:
        if str(p.get("status")) != "ok":
            continue
        path = p.get("path")
        if not path:
            continue
        out[str(p["panel_id"])] = Path(str(path)).resolve()
    return out


def _compose_legacy_strip(
    chapter_script: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    out_dir: Path,
) -> list[Path]:
    """Legacy horizontal-strip composer (pre-frame-engine fallback).

    Retained as a safety net for environments where the frame template library
    is unavailable. One row per page, left-to-right, edge-to-edge.
    """
    from PIL import Image

    by_id = _paths_by_panel_id(panel_images_manifest)
    out_dir = Path(out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    pages = chapter_script.get("pages") or []
    for pi, page in enumerate(pages, start=1):
        panel_entries = page.get("panels") or []
        paths: list[Path] = []
        for panel in panel_entries:
            pid = str(panel.get("panel_id") or "")
            if not pid:
                raise ValueError("page has panel without panel_id")
            fp = by_id.get(pid)
            if fp is None or not fp.is_file():
                raise ValueError(
                    f"panel {pid!r} missing ok image path in manifest for page {pi}"
                )
            paths.append(fp)

        loaded = [Image.open(p).convert("RGBA") for p in paths]
        to_close: list[Any] = list(loaded)
        try:
            target_h = max(im.height for im in loaded)
            row: list[Any] = []
            for im in loaded:
                if im.height != target_h:
                    nw = max(1, int(round(im.width * target_h / im.height)))
                    im2 = im.resize((nw, target_h), Image.Resampling.LANCZOS)
                    row.append(im2)
                    to_close.append(im2)
                else:
                    row.append(im)
            total_w = sum(im.width for im in row)
            canvas = Image.new("RGBA", (total_w, target_h), (255, 255, 255, 255))
            x = 0
            for im in row:
                canvas.paste(im, (x, 0), im)
                x += im.width
            out_path = out_dir / f"page_{pi:03d}.png"
            canvas.save(out_path, format="PNG")
            written.append(out_path)
        finally:
            for im in to_close:
                im.close()

    return written


def compose_final_page_pngs(
    chapter_script: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    out_dir: Path,
    *,
    genre: str | None = None,
    reading_direction: str | None = None,
) -> list[Path]:
    """Write framed ``page_001.png``, … under ``out_dir``.

    Composes each page into a framed multi-panel grid (borders + gutters) chosen
    by (panel_count, page_type, genre) via the frame engine. Requires Pillow.

    ``genre`` / ``reading_direction`` are optional overrides; when omitted they
    are read from the chapter script (or each page's ``page_type`` /
    ``reading_direction``). Falls back to the legacy horizontal-strip composer
    only if the frame template library cannot be loaded.
    """
    try:
        from PIL import Image  # noqa: F401
    except ImportError as e:
        raise RuntimeError(
            "compose_final_page_pngs requires Pillow; pip install Pillow"
        ) from e

    try:
        from phoenix_v4.manga.chapter.page_frame import (
            PageFrameError,
            compose_framed_page_pngs,
            load_grid_library,
        )

        load_grid_library()  # raises PageFrameError if library missing/invalid
    except Exception:
        return _compose_legacy_strip(chapter_script, panel_images_manifest, out_dir)

    try:
        return compose_framed_page_pngs(
            chapter_script,
            panel_images_manifest,
            out_dir,
            genre=genre,
            reading_direction=reading_direction,
        )
    except PageFrameError:
        return _compose_legacy_strip(chapter_script, panel_images_manifest, out_dir)
