#!/usr/bin/env python3
"""Derive an INTERIM L3 object sprite from an existing rendered panel.

The proper L3 lane (MANGA_LAYER_RENDER_CONTRACT_SPEC.md §4.4) renders each
object BIG on a pure-white backdrop per the series object_inventory, then
cuts it out. Until those renders exist, this tool derives a labeled INTERIM
sprite by cropping an object region out of an already-rendered panel and
running the same rembg alpha-matting cutout `render_v4_episode.apply_cutout`
uses.

Output is an RGBA sprite + a provenance sidecar naming the source panel,
the crop box, and the exact enqueue command that produces the REAL
replacement (scripts/manga/pearl_star_t2i_enqueue.py → Pearl Star queue,
per RAP). An INTERIM sprite must never ship as final art.

Tier 1 (operator-present). No LLM calls. CPU-only (rembg u2net). No network
beyond rembg's one-time local model cache.

Usage:
    PYTHONPATH=. python3 scripts/manga/make_object_sprite.py \
        --source artifacts/manga/<series>/composed_v3_qwen/ep_001_seg_027.jpg \
        --crop 120,300,900,1300 \
        --object-id kettle --state on_burner_boiling \
        --out artifacts/manga/<series>/image_bank_sprites/kettle_on_burner_boiling_INTERIM.png
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[2]


def make_sprite(source: Path, crop: tuple[int, int, int, int], out: Path,
                object_id: str, state: str, *, model: str = "isnet-general-use",
                alpha_matting: bool = False) -> dict:
    from rembg import remove, new_session
    src = Image.open(source).convert("RGB")
    region = src.crop(crop)
    session = new_session(model)
    kwargs: dict = {}
    if alpha_matting:
        kwargs = dict(alpha_matting=True,
                      alpha_matting_foreground_threshold=240,
                      alpha_matting_background_threshold=15,
                      alpha_matting_erode_size=8)
    rgba = remove(region, session=session, **kwargs)
    tight = rgba.getbbox()
    if tight:
        rgba = rgba.crop(tight)
    out.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out)

    real_replacement_cmd = (
        "PYTHONPATH=. python3 -c \""
        "from scripts.manga.pearl_star_t2i_enqueue import enqueue_panel_job; "
        f"enqueue_panel_job(task='t2i_qwen_image', prompt='<object_inventory "
        f"prompt_template_extras[{object_id}][{state}] on pure white backdrop, "
        "rendered BIG per spec §4.4>', width=1080, height=1920, "
        "out_path='<image_bank sprite path>')\""
    )
    sidecar = {
        "provenance": "INTERIM",
        "object_id": object_id,
        "state": state,
        "derived_from": str(source),
        "crop_box": list(crop),
        "cutout_backend": f"rembg {model}{' alpha_matting' if alpha_matting else ''} (same library as render_v4_episode.apply_cutout)",
        "sprite_bytes": out.stat().st_size,
        "real_replacement": {
            "spec": "MANGA_LAYER_RENDER_CONTRACT_SPEC.md §4.4 L3 render contract",
            "inventory": "config/source_of_truth/manga_profiles/series/<profile>.object_inventory.yaml",
            "enqueue_via": real_replacement_cmd,
        },
    }
    out.with_suffix(".provenance.json").write_text(json.dumps(sidecar, indent=2))
    return sidecar


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--source", required=True, type=Path)
    ap.add_argument("--crop", required=True,
                    help="left,top,right,bottom in source pixels")
    ap.add_argument("--object-id", required=True)
    ap.add_argument("--state", required=True)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--model", default="isnet-general-use",
                    help="rembg session model (isnet-general-use handles pale "
                         "objects on pale backgrounds better than u2net)")
    ap.add_argument("--alpha-matting", action="store_true")
    args = ap.parse_args(argv)
    crop = tuple(int(v) for v in args.crop.split(","))
    if len(crop) != 4:
        ap.error("--crop must be left,top,right,bottom")
    sidecar = make_sprite(args.source, crop, args.out, args.object_id, args.state,
                          model=args.model, alpha_matting=args.alpha_matting)
    print(json.dumps(sidecar, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
