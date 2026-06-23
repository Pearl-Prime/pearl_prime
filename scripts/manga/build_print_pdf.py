#!/usr/bin/env python3
"""Build print-ready PDF from composed manga pages."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from PIL import Image

from phoenix_v4.manga.distribution.config_io import (
    grammar_for_format,
    load_brand_illustration_styles,
    load_format_grammars,
)


def _mm_to_px(mm: float, dpi: int) -> int:
    return int(round(mm / 25.4 * dpi))


def build_print_pdf(
    *,
    profile: dict[str, Any],
    pages: list[Path],
    out_path: Path,
    repo_root: Path,
) -> Path:
    formats = load_format_grammars(repo_root)
    print_grammar = grammar_for_format(formats, "print")
    dims = print_grammar.get("page_dimensions") or {}
    export = print_grammar.get("export") or {}
    width_mm = float(dims.get("width_mm") or 128)
    height_mm = float(dims.get("height_mm") or 182)
    bleed_mm = float(dims.get("bleed_mm") or 3)
    dpi = int(export.get("dpi") or 600)
    color_space = str(export.get("color_space") or "cmyk")

    canvas_w = _mm_to_px(width_mm + 2 * bleed_mm, dpi)
    canvas_h = _mm_to_px(height_mm + 2 * bleed_mm, dpi)
    trim_w = _mm_to_px(width_mm, dpi)
    trim_h = _mm_to_px(height_mm, dpi)

    brand_id = str(profile.get("brand_id") or "")
    brand_styles = load_brand_illustration_styles(repo_root)
    color_palette = ((brand_styles.get(brand_id) or {}).get("color_palette")) or {}

    rendered: list[Image.Image] = []
    for page in pages:
        with Image.open(page) as src:
            im = src.convert("RGB")
            im.thumbnail((trim_w, trim_h), Image.Resampling.LANCZOS)
            canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
            x = (canvas_w - im.width) // 2
            y = (canvas_h - im.height) // 2
            canvas.paste(im, (x, y))
            rendered.append(canvas)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    if len(rendered) == 1:
        rendered[0].save(out_path, format="PDF", resolution=dpi)
    else:
        rendered[0].save(
            out_path,
            format="PDF",
            save_all=True,
            append_images=rendered[1:],
            resolution=dpi,
        )
    for im in rendered:
        im.close()

    title_id = str(profile.get("title_id") or "manga")
    pacing = profile.get("pacing") or {}
    spec = {
        "title_id": title_id,
        "canvas_px": [canvas_w, canvas_h],
        "trim_px": [trim_w, trim_h],
        "bleed_mm": bleed_mm,
        "dpi": dpi,
        "color_space_intended": color_space,
        "color_space_delivered": "rgb",
        "pacing": pacing,
        "color_palette": color_palette,
    }
    sidecar = out_path.parent / f"{title_id}_print_spec.json"
    sidecar.write_text(json.dumps(spec, indent=2) + "\n", encoding="utf-8")
    return out_path
