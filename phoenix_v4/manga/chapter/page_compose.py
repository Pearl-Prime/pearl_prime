"""Lay out panel PNGs into per-page composites (horizontal strips)."""

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


def compose_final_page_pngs(
    chapter_script: Mapping[str, Any],
    panel_images_manifest: Mapping[str, Any],
    out_dir: Path,
) -> list[Path]:
    """Write ``page_001.png``, … under ``out_dir`` (one row per page, left-to-right).

    Requires Pillow. All panels on a page must be ``ok`` in the manifest with paths.
    """
    try:
        from PIL import Image
    except ImportError as e:
        raise RuntimeError(
            "compose_final_page_pngs requires Pillow; pip install Pillow"
        ) from e

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
