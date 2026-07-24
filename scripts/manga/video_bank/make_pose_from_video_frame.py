#!/usr/bin/env python3
"""Derive an INTERIM L2 pose cutout from a video frame.

Sibling of ``scripts/manga/make_object_sprite.py``: frame → cutout (ToonOut
primary, rembg fallback) → ``*_INTERIM.png`` + ``.provenance.json`` +
``.composition.json`` (skeleton). DashScope-derived poses stay INTERIM.

Usage:
  PYTHONPATH=. python3 scripts/manga/video_bank/make_pose_from_video_frame.py \\
    --frame path/to/frame.png --out path/to/mira_pose_INTERIM.png \\
    --source-clip path/to/clip.mp4 --frame-index 3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from PIL import Image

REPO = Path(__file__).resolve().parents[3]


def _cutout_toonout(im: Image.Image) -> Image.Image:
    from scripts.manga.manga_cutout_toonout import toonout_cutout

    return toonout_cutout(im.convert("RGB"))


def _cutout_rembg(im: Image.Image, *, model: str = "isnet-general-use") -> Image.Image:
    from rembg import new_session, remove

    session = new_session(model)
    return remove(im.convert("RGB"), session=session)


def _cutout_stub(im: Image.Image) -> Image.Image:
    """Test-only / last-resort: treat near-white as transparent."""
    rgba = im.convert("RGBA")
    pixels = rgba.load()
    w, h = rgba.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if r > 245 and g > 245 and b > 245:
                pixels[x, y] = (r, g, b, 0)
            else:
                pixels[x, y] = (r, g, b, 255)
    return rgba


def run_cutout(im: Image.Image, *, backend: str = "auto") -> tuple[Image.Image, str]:
    if backend == "stub":
        return _cutout_stub(im), "stub_white_key"
    if backend == "toonout":
        return _cutout_toonout(im), "toonout"
    if backend == "rembg":
        return _cutout_rembg(im), "rembg isnet-general-use"
    # auto: ToonOut → rembg → stub
    try:
        return _cutout_toonout(im), "toonout"
    except Exception:
        pass
    try:
        return _cutout_rembg(im), "rembg isnet-general-use"
    except Exception:
        return _cutout_stub(im), "stub_white_key (fallback)"


def write_sidecars(
    out: Path,
    *,
    source_clip: str,
    frame_index: int,
    frame_path: str,
    cutout_backend: str,
    extraction_command: str,
    provenance: str = "INTERIM",
    pose_id: str | None = None,
    figure_height_m: float = 1.65,
    anchor_y_px: int | None = None,
) -> dict[str, Any]:
    h = Image.open(out).size[1]
    if anchor_y_px is None:
        anchor_y_px = int(h * 0.92)
    provenance_sidecar = {
        "provenance": provenance,
        "provenance_note": (
            "DashScope free-quota video frame — INTERIM permanently; never final art. "
            "REAL replacement via self-hosted VACE/Wan on Pearl Star (RAP/pscli)."
            if provenance == "INTERIM"
            else "Self-hosted Apache Wan/VACE output after full gate chain."
        ),
        "source_clip": source_clip,
        "frame_index": frame_index,
        "derived_from": frame_path,
        "cutout_backend": cutout_backend,
        "extraction_command": extraction_command,
        "sprite_bytes": out.stat().st_size,
        "pose_id": pose_id,
        "real_replacement": {
            "spec": "MANGA_VIDEO_POSE_BANK_SUPPLY_SPEC.md §5 + MANGA_LAYER_RENDER_CONTRACT_SPEC.md §4",
            "enqueue_via": (
                "pscli enqueue VACE-1.3B / Wan i2v reference job "
                "(docs/ROBUST_AGENT_PROTOCOL.md); off-manga RAP windows only"
            ),
        },
    }
    composition_sidecar = {
        "layer_class": "L2",
        "anchor": {"y_px": anchor_y_px},
        "figure_height_m": figure_height_m,
        "schema_note": "Skeleton aligns with composition_meta / grammar slots for L2 bank admission intent.",
    }
    out.with_suffix(".provenance.json").write_text(
        json.dumps(provenance_sidecar, indent=2) + "\n", encoding="utf-8"
    )
    # composition uses .composition.json next to stem (make_object pattern variant)
    composition_path = out.parent / (out.stem + ".composition.json")
    composition_path.write_text(
        json.dumps(composition_sidecar, indent=2) + "\n", encoding="utf-8"
    )
    return {"provenance": provenance_sidecar, "composition": composition_sidecar}


def make_pose(
    frame: Path,
    out: Path,
    *,
    source_clip: str,
    frame_index: int,
    backend: str = "auto",
    pose_id: str | None = None,
    provenance: str = "INTERIM",
) -> dict[str, Any]:
    if provenance == "INTERIM" and not out.name.endswith("_INTERIM.png"):
        # Enforce filename contract for DashScope-derived INTERIM
        if out.suffix.lower() == ".png" and "_INTERIM" not in out.stem:
            out = out.with_name(out.stem + "_INTERIM.png")
    im = Image.open(frame)
    rgba, backend_used = run_cutout(im, backend=backend)
    tight = rgba.getbbox()
    if tight:
        rgba = rgba.crop(tight)
    out.parent.mkdir(parents=True, exist_ok=True)
    rgba.save(out)
    extraction_command = (
        f"PYTHONPATH=. python3 scripts/manga/video_bank/make_pose_from_video_frame.py "
        f"--frame {frame} --out {out} --source-clip {source_clip} "
        f"--frame-index {frame_index} --backend {backend}"
    )
    sidecars = write_sidecars(
        out,
        source_clip=source_clip,
        frame_index=frame_index,
        frame_path=str(frame),
        cutout_backend=backend_used,
        extraction_command=extraction_command,
        provenance=provenance,
        pose_id=pose_id,
    )
    return {"out": str(out), "bytes": out.stat().st_size, **sidecars}


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--frame", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--source-clip", required=True)
    ap.add_argument("--frame-index", type=int, required=True)
    ap.add_argument(
        "--backend",
        default="auto",
        choices=["auto", "toonout", "rembg", "stub"],
    )
    ap.add_argument("--pose-id", default="")
    ap.add_argument("--provenance", default="INTERIM", choices=["INTERIM", "REAL"])
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = make_pose(
            args.frame,
            args.out,
            source_clip=args.source_clip,
            frame_index=args.frame_index,
            backend=args.backend,
            pose_id=args.pose_id or None,
            provenance=args.provenance,
        )
    except Exception as exc:  # noqa: BLE001 — CLI boundary
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({"out": result["out"], "bytes": result["bytes"],
                      "provenance": result["provenance"]["provenance"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
