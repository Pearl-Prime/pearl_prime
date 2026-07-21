#!/usr/bin/env python3
"""Bridge Pearl Star V5 layered output into deterministic structural assembly.

This tool consumes one V5 layered panel output directory and emits an
`assemble_from_bank.py` manifest that deliberately ignores the model composite
(`layer_00.png`). The final panel is assembled from:

  - `layer_01.png` as L0 background
  - `layer_02.png` as L2 character/component
  - a verified structural plan derived from the archetype structural bridge and
    `character_placement_bbox`

Tier 1. No LLM calls. No network. Pure local file conversion + PIL metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_from_bank as afb  # noqa: E402
import structural_composition as sc  # noqa: E402
from composition_grammar import CAMERA_HEIGHT_M, alpha_tight_bbox  # noqa: E402
from mecha_clean_structural_layer import (
    is_mecha_structural_layer,
    validate_mecha_layer_meta,
)  # noqa: E402

PANEL_TEMPLATES = REPO / "config" / "manga" / "panel_templates" / "iyashikei.yaml"
L0_NAME = "layer_01.png"
L2_NAME = "layer_02.png"
MODEL_COMPOSITE_NAME = "layer_00.png"
TELEMETRY_NAME = "_telemetry.json"
PLAN_NAME = "structural_plan.json"
MANIFEST_NAME = "assembly_manifest.yaml"
CLOSEOUT_NAME = "STRUCTURAL_ASSEMBLY_PROOF.json"
CHAR_NODE_ID = "char_standing"
FLOOR_NODE_ID = "floor_support"
EYE_LEVEL_Y_PCT = 42.0
FIGURE_HEIGHT_M = 1.62
CAMERA_HEIGHT_KEY = "standing"


class BridgeError(RuntimeError):
    """Fail-closed bridge error with an operator-readable message."""


@dataclass(frozen=True)
class BridgeResult:
    manifest_path: Path
    structural_plan_path: Path
    final_composite_path: Path | None
    closeout_path: Path | None
    plan_hash: str
    panel_id: str
    archetype: str
    panel_type_id: str
    structural_template_id: str


def _repo_rel(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise BridgeError(f"required {label} missing: {path}")
    return path


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI surface
        raise BridgeError(f"could not read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BridgeError(f"expected JSON object in {path}")
    return data


def _read_yaml(path: Path) -> dict[str, Any]:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as exc:  # noqa: BLE001 - fail-closed CLI surface
        raise BridgeError(f"could not read YAML {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise BridgeError(f"expected YAML object in {path}")
    return data


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _panel_id_from_telemetry_or_path(telemetry: dict[str, Any], panel_dir: Path) -> str:
    panel_id = str(telemetry.get("panel_id") or "").strip()
    if panel_id:
        return panel_id
    fallback = panel_dir.name.strip()
    if fallback:
        return fallback
    raise BridgeError("panel_id missing from telemetry and cannot be inferred from path")


def _archetype_from_telemetry(telemetry: dict[str, Any]) -> str:
    archetype = str(telemetry.get("archetype") or "").strip()
    if not archetype:
        raise BridgeError("panel archetype cannot be resolved from telemetry")
    return archetype


def _character_bbox_for_archetype(archetype: str) -> list[float]:
    templates = _read_yaml(PANEL_TEMPLATES)
    row = ((templates.get("archetypes") or {}).get(archetype) or {})
    bbox = row.get("character_placement_bbox")
    if not (
        isinstance(bbox, list)
        and len(bbox) == 4
        and all(isinstance(v, (int, float)) for v in bbox)
    ):
        raise BridgeError(
            f"archetype {archetype!r} has no numeric character_placement_bbox"
        )
    x0, y0, x1, y1 = [float(v) for v in bbox]
    if not (0 <= x0 < x1 <= 100 and 0 <= y0 < y1 <= 100):
        raise BridgeError(
            f"archetype {archetype!r} has invalid character_placement_bbox={bbox!r}"
        )
    return [x0, y0, x1, y1]


def _bridge_row_for_archetype(archetype: str) -> tuple[str, dict[str, Any]]:
    panel_type_id = sc.bridge_hint_from_archetype(archetype)
    if not panel_type_id:
        raise BridgeError(f"structural bridge cannot resolve archetype {archetype!r}")
    try:
        row = sc.bridge_for_panel_type(panel_type_id)
    except sc.StructuralHardFail as exc:
        raise BridgeError(f"structural bridge cannot resolve {panel_type_id!r}: {exc}") from exc
    return panel_type_id, row


def _copy_layer(src: Path, out_dir: Path, name: str) -> Path:
    dst = out_dir / name
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return dst


def _composition_sidecar(path: Path) -> Path:
    return path.with_suffix(".composition.json")


def _is_mecha_v5_panel(
    telemetry: dict[str, Any],
    *,
    l0_src: Path,
    l2_src: Path,
) -> bool:
    if str(telemetry.get("genre_id") or telemetry.get("genre") or "").lower() == "mecha":
        return True
    for src in (l0_src, l2_src):
        sidecar = _composition_sidecar(src)
        if sidecar.is_file() and is_mecha_structural_layer(_read_json(sidecar)):
            return True
    return False


def _copy_reviewed_mecha_sidecars(
    *,
    l0_src: Path,
    l2_src: Path,
    l0_dst: Path,
    l2_dst: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    l0_meta_path = _require_file(_composition_sidecar(l0_src), "reviewed mecha L0 composition sidecar")
    l2_meta_path = _require_file(_composition_sidecar(l2_src), "reviewed mecha L2 composition sidecar")
    l0_meta = _read_json(l0_meta_path)
    l2_meta = _read_json(l2_meta_path)
    try:
        validate_mecha_layer_meta(l0_meta, layer_class="L0")
        validate_mecha_layer_meta(l2_meta, layer_class="L2")
    except ValueError as exc:
        raise BridgeError(f"reviewed mecha sidecar failed contract: {exc}") from exc
    shutil.copy2(l0_meta_path, _composition_sidecar(l0_dst))
    shutil.copy2(l2_meta_path, _composition_sidecar(l2_dst))
    return l0_meta, l2_meta


def _alpha_metrics(path: Path) -> dict[str, float]:
    with Image.open(path) as im:
        rgba = im.convert("RGBA")
        tight = alpha_tight_bbox(rgba)
    if tight is None:
        raise BridgeError(f"L2 asset has no non-transparent pixels: {path}")
    left, top, right, bottom = tight
    width = right - left
    height = bottom - top
    if width <= 0 or height <= 0:
        raise BridgeError(f"L2 asset has invalid alpha bbox {tight!r}: {path}")
    return {
        "left": float(left),
        "top": float(top),
        "right": float(right),
        "bottom": float(bottom),
        "width": float(width),
        "height": float(height),
        "anchor_y_px": float(bottom),
        "anchor_height_px": float(bottom - top),
    }


def _target_height_pct(
    bbox_xyxy: list[float],
    *,
    canvas_w: int,
    canvas_h: int,
    alpha: dict[str, float],
) -> float:
    x0, y0, x1, y1 = bbox_xyxy
    bbox_w_px = (x1 - x0) / 100.0 * canvas_w
    bbox_h_px = (y1 - y0) / 100.0 * canvas_h
    height_fit_by_width_px = bbox_w_px * alpha["anchor_height_px"] / alpha["width"]
    target_h_px = min(bbox_h_px, height_fit_by_width_px)
    if target_h_px <= 0:
        raise BridgeError(f"character_placement_bbox resolves to empty target: {bbox_xyxy!r}")
    return target_h_px / canvas_h * 100.0


def _uniform_scale_for_bbox(
    bbox_xyxy: list[float],
    *,
    target_height_pct: float,
) -> float:
    _x0, _y0, _x1, y1 = bbox_xyxy
    camera_height_m = CAMERA_HEIGHT_M[CAMERA_HEIGHT_KEY]
    distance_from_horizon = y1 - EYE_LEVEL_Y_PCT
    if distance_from_horizon <= 0:
        raise BridgeError(
            f"character feet y={y1:g}% must be below horizon y={EYE_LEVEL_Y_PCT:g}%"
        )
    scale = target_height_pct / (
        (FIGURE_HEIGHT_M / camera_height_m) * distance_from_horizon
    )
    profile = sc.load_validation_profile()
    thresholds = profile.get("thresholds") or {}
    min_scale = float((thresholds.get("min_uniform_scale") or {}).get("current_value", 0.0))
    max_scale = float((thresholds.get("max_uniform_scale") or {}).get("current_value", 999.0))
    if scale < min_scale or scale > max_scale:
        raise BridgeError(
            f"structural scale {scale:.4f} outside validation bounds "
            f"[{min_scale:g}, {max_scale:g}] for bbox {bbox_xyxy!r}"
        )
    return scale


def _write_composition_sidecars(
    *,
    panel_id: str,
    l0_path: Path,
    l2_path: Path,
    alpha: dict[str, float],
) -> None:
    l0_meta = {
        "schema_version": "1.0.0",
        "asset_id": f"{panel_id}_v5_layer_01_background",
        "layer_class": "L0",
        "source": "pearl_star_v5_layered_output",
        "bg_class": "full_render",
        "light": {"azimuth": "ambient"},
        "camera": {
            "angle_bucket": "eye_level",
            "eye_level_y_pct": EYE_LEVEL_Y_PCT,
            "camera_height": CAMERA_HEIGHT_KEY,
        },
        "anchor_slots": [],
    }
    l2_meta = {
        "schema_version": "1.0.0",
        "asset_id": f"{panel_id}_v5_layer_02_character",
        "layer_class": "L2",
        "source": "pearl_star_v5_layered_output",
        "crop_class": "full_figure",
        "room_capable": True,
        "abstract_stage_eligible": False,
        "scene_contamination": False,
        "light": {"azimuth": "ambient"},
        "implied_camera": {"angle_bucket": "eye_level"},
        "anchor": {"point": "feet", "y_px": alpha["anchor_y_px"]},
        "eye_y_px": alpha["top"] + alpha["height"] * 0.2,
        "figure_height_m": FIGURE_HEIGHT_M,
    }
    l0_path.with_suffix(".composition.json").write_text(
        json.dumps(l0_meta, indent=2) + "\n",
        encoding="utf-8",
    )
    l2_path.with_suffix(".composition.json").write_text(
        json.dumps(l2_meta, indent=2) + "\n",
        encoding="utf-8",
    )


def _build_structural_plan(
    *,
    panel_id: str,
    panel_type_id: str,
    structural_template_id: str,
    canvas_w: int,
    canvas_h: int,
    bbox_xyxy: list[float],
    uniform_scale: float,
) -> dict[str, Any]:
    x0, y0, x1, y1 = bbox_xyxy
    bundle = {
        "schema_version": "1.0.0",
        "bundle_id": f"v5_layered_structural_{panel_id}",
        "panel_id": panel_id,
        "panel_type_id": panel_type_id,
        "structural_template_id": structural_template_id,
        "canvas": {"width": canvas_w, "height": canvas_h},
        "nodes": [
            {
                "node_id": FLOOR_NODE_ID,
                "category": "support_surface",
                "role": "floor",
                "support_polygon_pct": [
                    [0.0, y0],
                    [100.0, y0],
                    [100.0, 100.0],
                    [0.0, 100.0],
                ],
            },
            {
                "node_id": CHAR_NODE_ID,
                "category": "character",
                "role": "primary_subject",
                "contact_point_pct": [0.0, 0.0],
                "placement_bbox_pct_xyxy": bbox_xyxy,
            },
        ],
        "edges": [
            {
                "edge_id": "e_standing",
                "relation": "standing_on",
                "from_node": CHAR_NODE_ID,
                "to_node": FLOOR_NODE_ID,
            }
        ],
        "placements": [
            {
                "node_id": CHAR_NODE_ID,
                "transform": {
                    "tx_pct": (x0 + x1) / 2.0,
                    "ty_pct": y1,
                    "uniform_scale": uniform_scale,
                    "rotation_deg": 0.0,
                },
            }
        ],
    }
    try:
        envelope = sc.build_plan_envelope(bundle, panel_type_id=panel_type_id)
        sc.verify_plan_hash(envelope)
        sc.render_from_verified_plan(envelope, require_hash=True)
    except sc.StructuralHardFail as exc:
        raise BridgeError(f"structural plan invalid: {exc}") from exc
    return envelope


def _manifest_doc(
    *,
    panel_id: str,
    archetype: str,
    episode_id: str | None,
    canvas_w: int,
    canvas_h: int,
) -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "series_id": "pearl_star_v5_structural_assembly",
        "episode_id": episode_id or "",
        "manifest_id": f"{panel_id}_v5_structural_assembly",
        "notes": (
            "Generated from Pearl Star V5 layered output. layer_00/model composite "
            "is intentionally not referenced; final placement is structural."
        ),
        "canvas": {
            "width": canvas_w,
            "height": canvas_h,
            "background_hex": "#FFFFFF",
        },
        "panels": [
            {
                "panel_id": panel_id,
                "archetype": archetype,
                "shot_type": "establishing",
                "structural_plan_path": PLAN_NAME,
                "layers": [
                    {
                        "layer_class": "L0",
                        "asset": L0_NAME,
                        "provenance": "REAL",
                        "provenance_note": "Pearl Star V5 layer_01 background.",
                    },
                    {
                        "layer_class": "L2",
                        "asset": L2_NAME,
                        "provenance": "REAL",
                        "provenance_note": "Pearl Star V5 layer_02 character/component.",
                        "structural_node_id": CHAR_NODE_ID,
                        "grounding": {"contact_shadow": True, "occluder": False},
                    },
                ],
            }
        ],
    }


def bridge_v5_panel_dir(
    v5_panel_dir: Path,
    out_dir: Path,
    *,
    assemble: bool = False,
    tests: str | None = None,
) -> BridgeResult:
    v5_panel_dir = v5_panel_dir.resolve()
    out_dir = out_dir.resolve()
    telemetry_path = _require_file(v5_panel_dir / TELEMETRY_NAME, TELEMETRY_NAME)
    model_composite_path = _require_file(
        v5_panel_dir / MODEL_COMPOSITE_NAME,
        MODEL_COMPOSITE_NAME,
    )
    l0_src = _require_file(v5_panel_dir / L0_NAME, L0_NAME)
    l2_src = _require_file(v5_panel_dir / L2_NAME, L2_NAME)

    telemetry = _read_json(telemetry_path)
    mecha_panel = _is_mecha_v5_panel(telemetry, l0_src=l0_src, l2_src=l2_src)
    panel_id = _panel_id_from_telemetry_or_path(telemetry, v5_panel_dir)
    archetype = _archetype_from_telemetry(telemetry)
    if telemetry.get("layer_type_used") not in (None, "L2"):
        raise BridgeError(
            f"panel {panel_id}: expected character-bearing layer_type_used=L2, "
            f"got {telemetry.get('layer_type_used')!r}"
        )
    bbox_xyxy = _character_bbox_for_archetype(archetype)
    panel_type_id, bridge_row = _bridge_row_for_archetype(archetype)
    structural_template_id = str(bridge_row.get("structural_template_id") or "")
    if not structural_template_id:
        raise BridgeError(f"bridge row {panel_type_id!r} has no structural_template_id")

    with Image.open(l0_src) as bg:
        canvas_w, canvas_h = bg.size
    l2_meta_for_quality: dict[str, Any] = {"crop_class": "full_figure"}
    if mecha_panel:
        l2_meta_path = _require_file(
            _composition_sidecar(l2_src),
            "reviewed mecha L2 composition sidecar",
        )
        l2_meta_for_quality = _read_json(l2_meta_path)
        try:
            validate_mecha_layer_meta(l2_meta_for_quality, layer_class="L2")
        except ValueError as exc:
            raise BridgeError(f"panel {panel_id}: reviewed mecha L2 sidecar failed contract: {exc}") from exc

    with Image.open(l2_src) as fg:
        if fg.size != (canvas_w, canvas_h):
            raise BridgeError(
                f"L2 size {fg.size} does not match L0/canvas {(canvas_w, canvas_h)}"
            )
        try:
            l2_quality = afb.require_structural_l2_quality(
                fg,
                l2_meta=l2_meta_for_quality,
                structural_template_id=structural_template_id,
            )
        except ValueError as exc:
            raise BridgeError(f"panel {panel_id}: {exc}") from exc
    alpha = _alpha_metrics(l2_src)
    target_height_pct = _target_height_pct(
        bbox_xyxy,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
        alpha=alpha,
    )
    uniform_scale = _uniform_scale_for_bbox(
        bbox_xyxy,
        target_height_pct=target_height_pct,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    l0_dst = _copy_layer(l0_src, out_dir, L0_NAME)
    l2_dst = _copy_layer(l2_src, out_dir, L2_NAME)
    if mecha_panel:
        _copy_reviewed_mecha_sidecars(
            l0_src=l0_src,
            l2_src=l2_src,
            l0_dst=l0_dst,
            l2_dst=l2_dst,
        )
    else:
        _write_composition_sidecars(
            panel_id=panel_id,
            l0_path=l0_dst,
            l2_path=l2_dst,
            alpha=alpha,
        )

    plan = _build_structural_plan(
        panel_id=panel_id,
        panel_type_id=panel_type_id,
        structural_template_id=structural_template_id,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
        bbox_xyxy=bbox_xyxy,
        uniform_scale=uniform_scale,
    )
    plan_path = out_dir / PLAN_NAME
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    manifest = _manifest_doc(
        panel_id=panel_id,
        archetype=archetype,
        episode_id=v5_panel_dir.parent.name,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
    )
    manifest_path = out_dir / MANIFEST_NAME
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")

    # Validate through the real assembler loader before declaring the bridge done.
    afb.load_manifest(manifest_path)

    final_composite_path: Path | None = None
    closeout_path: Path | None = None
    if assemble:
        assembly = afb.run(manifest_path, out_dir)
        panels = assembly.get("panels") or []
        if not panels:
            raise BridgeError("assembler produced no panel paths")
        final_composite_path = Path(str(panels[0])).resolve()
        if not final_composite_path.is_file():
            raise BridgeError(f"assembler final composite missing: {final_composite_path}")
        closeout = {
            "manga-v5-structural-assembly": "completed",
            "source_panel": panel_id,
            "source_v5_panel_dir": _repo_rel(v5_panel_dir),
            "source_asset_provenance": telemetry.get("source_asset_provenance") or {},
            "source_layers": [L0_NAME, L2_NAME],
            "ignored_model_composite": MODEL_COMPOSITE_NAME,
            "final_composite": _repo_rel(final_composite_path),
            "manifest": _repo_rel(manifest_path),
            "structural_plan": _repo_rel(plan_path),
            "plan_hash": plan["plan_hash"],
            "placement_source": "character_placement_bbox/structural_plan",
            "character_placement_bbox": bbox_xyxy,
            "panel_type_id": panel_type_id,
            "structural_template_id": structural_template_id,
            "l2_quality": l2_quality,
            "final_sha256": _sha256(final_composite_path),
            "model_layer_00_sha256": _sha256(model_composite_path),
            "final_differs_from_model_layer_00": (
                _sha256(final_composite_path) != _sha256(model_composite_path)
            ),
            "tests": tests or "not provided",
        }
        closeout_path = out_dir / CLOSEOUT_NAME
        closeout_path.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")

    return BridgeResult(
        manifest_path=manifest_path,
        structural_plan_path=plan_path,
        final_composite_path=final_composite_path,
        closeout_path=closeout_path,
        plan_hash=plan["plan_hash"],
        panel_id=panel_id,
        archetype=archetype,
        panel_type_id=panel_type_id,
        structural_template_id=structural_template_id,
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--v5-panel-dir", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument(
        "--assemble",
        action="store_true",
        help="Run assemble_from_bank.py and write the deterministic final composite.",
    )
    ap.add_argument(
        "--tests",
        default=None,
        help="Exact focused test result string to stamp into the proof closeout.",
    )
    args = ap.parse_args(argv)

    try:
        result = bridge_v5_panel_dir(
            args.v5_panel_dir,
            args.out_dir,
            assemble=args.assemble,
            tests=args.tests,
        )
    except BridgeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "ok": True,
        "panel_id": result.panel_id,
        "archetype": result.archetype,
        "panel_type_id": result.panel_type_id,
        "structural_template_id": result.structural_template_id,
        "plan_hash": result.plan_hash,
        "manifest": _repo_rel(result.manifest_path),
        "structural_plan": _repo_rel(result.structural_plan_path),
        "final_composite": _repo_rel(result.final_composite_path) if result.final_composite_path else None,
        "closeout": _repo_rel(result.closeout_path) if result.closeout_path else None,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
