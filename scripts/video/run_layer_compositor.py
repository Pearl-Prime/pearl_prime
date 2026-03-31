#!/usr/bin/env python3
"""
Stage 12 — Layer Compositor: resolved_assets + shot_plan -> composited_layers.json.
VCE §4: 5-layer compositing, parallax ratios, alpha blending, caption safe zone.
Usage: python scripts/video/run_layer_compositor.py <resolved_assets.json> <shot_plan.json> -o composited_layers.json [--format short]
"""
from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import (
    config_snapshot_hash,
    load_json,
    load_yaml,
    should_skip_output,
    write_atomically,
)
from scripts.video.vce_ffmpeg_builders import validate_filter_complex_structure

PARALLAX = {"L1": 1.0, "L2": 1.3, "L3": 1.6, "L4": 2.0}
ALPHA_L4_MIN, ALPHA_L4_MAX = 0.30, 0.60
ALPHA_L5_MIN, ALPHA_L5_MAX = 0.15, 0.25


def _alpha_in_range(shot_id: str, key: str, lo: float, hi: float) -> float:
    h = int(hashlib.sha256(f"{shot_id}:{key}".encode()).hexdigest(), 16)
    t = (h % 10000) / 10000.0
    return lo + t * (hi - lo)


def _layer_stack_for_mode(mode: str, asset_keys: dict, shot_id: str) -> list[dict]:
    """mode: three_layer (L1,L3,L5) or five_layer (all)."""
    keys = asset_keys
    l1 = keys.get("L1") or keys.get("background") or "bg"
    l3 = keys.get("L3") or keys.get("subject") or keys.get("character") or "subject"
    l5_grade = keys.get("L5") or "overlay_grade"
    if mode == "three_layer":
        return [
            {"id": "L1", "name": "background_plate", "parallax": PARALLAX["L1"], "asset_key": str(l1), "z": 0, "input_index": 0},
            {"id": "L3", "name": "character_subject", "parallax": PARALLAX["L3"], "asset_key": str(l3), "z": 2, "input_index": 1},
            {"id": "L5", "name": "overlay_grade", "parallax": 0.0, "asset_key": str(l5_grade), "z": 4, "input_index": 2,
             "alpha": _alpha_in_range(shot_id, "L5", ALPHA_L5_MIN, ALPHA_L5_MAX)},
        ]
    l2 = keys.get("L2") or "midground"
    l4 = keys.get("L4") or "foreground_particles"
    return [
        {"id": "L1", "name": "background_plate", "parallax": PARALLAX["L1"], "asset_key": str(l1), "z": 0, "input_index": 0},
        {"id": "L2", "name": "midground", "parallax": PARALLAX["L2"], "asset_key": str(l2), "z": 1, "input_index": 1},
        {"id": "L3", "name": "character_subject", "parallax": PARALLAX["L3"], "asset_key": str(l3), "z": 2, "input_index": 2},
        {"id": "L4", "name": "foreground_particles", "parallax": PARALLAX["L4"], "asset_key": str(l4), "z": 3, "input_index": 3,
         "alpha": _alpha_in_range(shot_id, "L4", ALPHA_L4_MIN, ALPHA_L4_MAX)},
        {"id": "L5", "name": "overlay_grade", "parallax": 0.0, "asset_key": str(l5_grade), "z": 4, "input_index": 4,
         "alpha": _alpha_in_range(shot_id, "L5", ALPHA_L5_MIN, ALPHA_L5_MAX)},
    ]


def _crop_x_expr(parallax_ratio: float, speed: float, w: int) -> str:
    """
    Time-drifting crop origin for parallax (escaped commas for filtergraph).
    After superscale, pan slowly so foreground moves faster than background.
    """
    # x = min(iw-W, max(0, (iw-W)/2 + speed*t)); commas escaped for filter_complex
    return f"min(iw-{w}\\,max(0\\,(iw-{w})/2+{speed * parallax_ratio:.3f}*t))"


def _scale_pad_base(w: int, h: int) -> str:
    return (
        f"scale={w}:{h}:force_original_aspect_ratio=decrease:flags=bicubic,"
        f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1"
    )


def _filter_complex_five_layer(
    shot_id: str, w: int, h: int,
    l4_a: float, l5_a: float,
) -> str:
    """Executable filter_complex: 5 inputs [0:v]..[4:v] -> [out_<shot_id>]."""
    sid = shot_id.replace("-", "_")
    # L1 static plate
    p1 = f"[0:v]{_scale_pad_base(w, h)}[L1_{sid}]"
    # L2/L3/L4: supersample then crop with parallax drift
    pr2, pr3, pr4 = PARALLAX["L2"], PARALLAX["L3"], PARALLAX["L4"]
    x2 = _crop_x_expr(1.0, 10.0, w)
    x3 = _crop_x_expr(1.0, 14.0, w)
    x4 = _crop_x_expr(1.0, 18.0, w)
    p2 = (
        f"[1:v]scale=round(iw*{pr2}):-2:flags=bicubic,"
        f"crop={w}:{h}:{x2}:0[L2_{sid}]"
    )
    p3 = (
        f"[2:v]scale=round(iw*{pr3}):-2:flags=bicubic,"
        f"crop={w}:{h}:{x3}:0[L3_{sid}]"
    )
    p4 = (
        f"[3:v]scale=round(iw*{pr4}):-2:flags=bicubic,"
        f"crop={w}:{h}:{x4}:0,"
        f"format=rgba,colorchannelmixer=aa={l4_a:.4f}[L4_{sid}]"
    )
    p5 = (
        f"[4:v]{_scale_pad_base(w, h)},"
        f"format=rgba,colorchannelmixer=aa={l5_a:.4f}[L5_{sid}]"
    )
    # Overlay stack per VCE §4 (alpha premultiplied via colorchannelmixer on L4/L5)
    o1 = f"[L1_{sid}][L2_{sid}]overlay=x=0:y=0:format=auto[bg2_{sid}]"
    o2 = f"[bg2_{sid}][L3_{sid}]overlay=x=0:y=0:format=auto[bg3_{sid}]"
    o3 = f"[bg3_{sid}][L4_{sid}]overlay=x=0:y=0:format=auto[bg4_{sid}]"
    o4 = f"[bg4_{sid}][L5_{sid}]overlay=x=0:y=0:format=auto[out_{sid}]"
    return ";".join([p1, p2, p3, p4, p5, o1, o2, o3, o4])


def _filter_complex_three_layer(shot_id: str, w: int, h: int, l5_a: float) -> str:
    """Fast path: inputs [0:v]=L1 [1:v]=L3 [2:v]=L5 -> [out_<shot_id>]."""
    sid = shot_id.replace("-", "_")
    pr3 = PARALLAX["L3"]
    x3 = _crop_x_expr(1.0, 14.0, w)
    p1 = f"[0:v]{_scale_pad_base(w, h)}[L1_{sid}]"
    p3 = (
        f"[1:v]scale=round(iw*{pr3}):-2:flags=bicubic,"
        f"crop={w}:{h}:{x3}:0[L3_{sid}]"
    )
    p5 = (
        f"[2:v]{_scale_pad_base(w, h)},"
        f"format=rgba,colorchannelmixer=aa={l5_a:.4f}[L5_{sid}]"
    )
    o1 = f"[L1_{sid}][L3_{sid}]overlay=x=0:y=0:format=auto[bg_{sid}]"
    o2 = f"[bg_{sid}][L5_{sid}]overlay=x=0:y=0:format=auto[out_{sid}]"
    return ";".join([p1, p3, p5, o1, o2])


def run_compositor(resolved: dict, shot_plan: dict, format_key: str) -> dict:
    fmt_cfg = load_yaml("config/video/format_specs.yaml")
    formats = fmt_cfg.get("formats") or {}
    spec = formats.get(format_key) or formats.get(fmt_cfg.get("default_format_key", "short"), {})
    layer_mode = (spec.get("layer_mode") or "three_layer").lower()
    if layer_mode not in ("three_layer", "five_layer"):
        layer_mode = "three_layer"

    reso = spec.get("resolution") or {"width": 1080, "height": 1920}
    out_w = int(reso.get("width", 1080))
    out_h = int(reso.get("height", 1920))

    color_cfg = load_yaml("config/video/color_grade_presets.yaml")
    preset_name = color_cfg.get("default_preset", "neutral")

    caption_policies = load_yaml("config/video/caption_policies.yaml")
    safe = (caption_policies.get("safe_zone") or {}) if isinstance(caption_policies, dict) else {}
    y_min = float(safe.get("y_min_pct", 0.72))
    y_max = float(safe.get("y_max_pct", 0.88))

    shots_out = []
    res_map = resolved.get("resolved") or {}
    for shot in shot_plan.get("shots", []):
        sid = shot["shot_id"]
        row = res_map.get(sid) or {}
        asset_id = row.get("asset_id") or f"asset-{sid}"
        keys = {
            "L1": asset_id,
            "L2": f"{asset_id}_mid",
            "L3": asset_id,
            "L4": f"{asset_id}_fg",
            "L5": preset_name,
        }
        layers = _layer_stack_for_mode("three_layer" if layer_mode == "three_layer" else "five_layer", keys, sid)
        if layer_mode == "three_layer":
            l5_a_layer = next(x["alpha"] for x in layers if x["id"] == "L5")
            fc = _filter_complex_three_layer(sid, out_w, out_h, l5_a_layer)
            input_order = ["L1", "L3", "L5"]
            l4_a_applied = None
            l5_a_applied = round(l5_a_layer, 4)
        else:
            l4_a = next(x["alpha"] for x in layers if x["id"] == "L4")
            l5_a = next(x["alpha"] for x in layers if x["id"] == "L5")
            fc = _filter_complex_five_layer(sid, out_w, out_h, l4_a, l5_a)
            input_order = ["L1", "L2", "L3", "L4", "L5"]
            l4_a_applied = round(l4_a, 4)
            l5_a_applied = round(l5_a, 4)

        ok, reason = validate_filter_complex_structure(fc)
        if not ok:
            raise RuntimeError(f"filter_complex failed validation for shot {sid}: {reason}")

        # Caption safe band between L4 (particles) and L5 (grade) — Y above lower particle sheet, below full-frame grade wash
        cap_pct_mid = (y_min + y_max) / 2.0
        caption_safe_zone = {
            "between_layers": ["L4", "L5"] if layer_mode == "five_layer" else ["L3", "L5"],
            "y_min_pct": y_min,
            "y_max_pct": y_max,
            "drawtext_y_expr": f"h*{cap_pct_mid:.3f}",
            "rationale": "Keep captions between story layers and the final grade overlay (VCE §4 safe band).",
        }

        shots_out.append({
            "shot_id": sid,
            "segment_id": shot.get("segment_id"),
            "layer_mode": layer_mode,
            "output_resolution": {"width": out_w, "height": out_h},
            "layers": layers,
            "filter_complex": fc,
            "filter_complex_input_order": input_order,
            "caption_safe_zone": caption_safe_zone,
            "l4_alpha_range": [ALPHA_L4_MIN, ALPHA_L4_MAX],
            "l5_alpha_range": [ALPHA_L5_MIN, ALPHA_L5_MAX],
            "l4_alpha_applied": l4_a_applied,
            "l5_alpha_applied": l5_a_applied,
            "color_grade_preset": preset_name,
        })

    cfg_hash = config_snapshot_hash()
    return {
        "plan_id": shot_plan.get("plan_id") or resolved.get("plan_id"),
        "vce_format": format_key,
        "config_hash": cfg_hash,
        "parallax_ratios": PARALLAX,
        "shots": shots_out,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="VCE Stage 12 — Layer compositor")
    ap.add_argument("resolved_assets", help="Path to resolved_assets.json")
    ap.add_argument("shot_plan", help="Path to shot_plan.json")
    ap.add_argument("-o", "--out", required=True, help="Output composited_layers.json")
    ap.add_argument("--format", default="short", help="VCE format key: short|mid|long|motion_comic|lofi|exercise")
    ap.add_argument("--force", action="store_true", help="Overwrite output")
    args = ap.parse_args()

    rpath, spath = Path(args.resolved_assets), Path(args.shot_plan)
    if not rpath.exists() or not spath.exists():
        print("Error: input not found", file=sys.stderr)
        return 1
    resolved = load_json(rpath)
    shot_plan = load_json(spath)
    out_path = Path(args.out)
    exp_hash = config_snapshot_hash()
    if should_skip_output(out_path, ["plan_id", "shots", "config_hash"], args.force, exp_hash):
        print(f"Skip (exists): {out_path}")
        return 0
    doc = run_compositor(resolved, shot_plan, args.format)
    write_atomically(out_path, doc)
    print(f"Wrote composited_layers ({len(doc['shots'])} shots) to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
