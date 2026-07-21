#!/usr/bin/env python3
"""Select clean real V5 layers and assemble them through structural gates.

This is the honest bridge for Pearl Star V5 output where the model may emit a
good preview composite while raw layer roles are imperfect. It never uses
layer_00.png as an assembly source. Instead it:

  - treats layer_01.png as the L0 support plate
  - evaluates layer_02.png and optional layer_03.png as foreground candidates
  - keeps the largest alpha component from the best clean candidate
  - normalizes that selected component to output layer_02.png
  - writes reviewed mecha structural sidecars, plan, manifest, and closeout
  - delegates final rendering and gates to assemble_from_bank.py

Tier 1. No LLM calls. No network. No GPU dispatch. Local deterministic image
inspection + repo-native structural assembly only.
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

import numpy as np
import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_from_bank as afb  # noqa: E402
import structural_composition as sc  # noqa: E402
from composition_grammar import alpha_tight_bbox  # noqa: E402
from mecha_clean_structural_layer import CONTRACT_ID, validate_mecha_layer_meta  # noqa: E402

MODEL_COMPOSITE_NAME = "layer_00.png"
L0_NAME = "layer_01.png"
OUTPUT_L2_NAME = "layer_02.png"
CANDIDATE_NAMES = ("layer_02.png", "layer_03.png")
TELEMETRY_NAME = "_telemetry.json"
MANIFEST_NAME = "assembly_manifest.yaml"
PLAN_NAME = "structural_plan.json"
CLOSEOUT_JSON = "REAL_V5_STRUCTURAL_CLOSEOUT.json"
CLOSEOUT_MD = "REAL_V5_STRUCTURAL_CLOSEOUT.md"
CHAR_NODE_ID = "char"
SUPPORT_NODE_ID = "support"
REQUIRED_GATES = {
    "L0_STRUCTURAL_PURITY",
    "L2_STRUCTURAL_PURITY",
    "L2_QUALITY",
    "L0_SUPPORT_ZONE",
}
DEFAULT_STANDING_TRANSFORM = (50.0, 86.0, 0.62)
DEFAULT_SEATED_TRANSFORM = (62.0, 74.0, 1.05)


class RealV5StructuralError(RuntimeError):
    """Fail-closed CLI error with an operator-readable message."""


@dataclass(frozen=True)
class Component:
    area_px: int
    bbox_px: tuple[int, int, int, int]
    edge_contacts: list[str]
    mask: np.ndarray

    def to_report(self, total_alpha_px: int, canvas_w: int, canvas_h: int) -> dict[str, Any]:
        x0, y0, x1, y1 = self.bbox_px
        return {
            "area_px": self.area_px,
            "area_ratio_of_alpha": round(self.area_px / max(total_alpha_px, 1), 4),
            "area_ratio_of_canvas": round(self.area_px / max(canvas_w * canvas_h, 1), 4),
            "bbox_px": [x0, y0, x1, y1],
            "bbox_pct": [
                round(x0 / canvas_w * 100, 3),
                round(y0 / canvas_h * 100, 3),
                round((x1 - x0) / canvas_w * 100, 3),
                round((y1 - y0) / canvas_h * 100, 3),
            ],
            "edge_contacts": self.edge_contacts,
        }


@dataclass(frozen=True)
class CandidateReport:
    source_name: str
    source_path: Path
    accepted: bool
    rejection_reasons: list[str]
    retained_component: Component | None
    total_alpha_px: int
    removed_px: int
    coverage: float
    component_count: int
    components: list[dict[str, Any]]
    rank_score: float

    def to_report(self) -> dict[str, Any]:
        return {
            "source_name": self.source_name,
            "source_path": _repo_rel(self.source_path),
            "accepted": self.accepted,
            "rejection_reasons": self.rejection_reasons,
            "total_alpha_px": self.total_alpha_px,
            "removed_px": self.removed_px,
            "coverage": round(self.coverage, 6),
            "component_count": self.component_count,
            "rank_score": round(self.rank_score, 4),
            "retained_component": self.components[0] if self.components else None,
            "components": self.components[:8],
        }


@dataclass(frozen=True)
class AssemblyResult:
    panel_id: str
    output_dir: Path
    final_path: Path
    closeout_path: Path
    manifest_path: Path
    structural_plan_path: Path
    selected_candidate: CandidateReport


def _repo_rel(path: Path) -> str:
    path = path.resolve()
    try:
        return str(path.relative_to(REPO))
    except ValueError:
        return str(path)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise RealV5StructuralError(f"could not read JSON {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RealV5StructuralError(f"expected JSON object in {path}")
    return data


def _require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise RealV5StructuralError(f"required {label} missing: {path}")
    return path


def _composition_sidecar(path: Path) -> Path:
    return path.with_suffix(".composition.json")


def _edge_contacts(bbox: tuple[int, int, int, int], canvas_w: int, canvas_h: int) -> list[str]:
    x0, y0, x1, y1 = bbox
    contacts: list[str] = []
    if x0 <= 0:
        contacts.append("left")
    if y0 <= 0:
        contacts.append("top")
    if x1 >= canvas_w:
        contacts.append("right")
    if y1 >= canvas_h:
        contacts.append("bottom")
    return contacts


def _connected_components(mask: np.ndarray) -> list[Component]:
    try:
        from scipy import ndimage as ndi  # type: ignore
    except Exception:  # pragma: no cover - exercised only when scipy is absent
        return _connected_components_fallback(mask)

    labels, count = ndi.label(mask)
    if count <= 0:
        return []
    objects = ndi.find_objects(labels)
    h, w = mask.shape
    components: list[Component] = []
    for label_id, slc in enumerate(objects, start=1):
        if slc is None:
            continue
        ys, xs = slc
        local = labels[ys, xs] == label_id
        area = int(local.sum())
        if area <= 0:
            continue
        y0, y1 = int(ys.start), int(ys.stop)
        x0, x1 = int(xs.start), int(xs.stop)
        comp_mask = labels == label_id
        bbox = (x0, y0, x1, y1)
        components.append(Component(area, bbox, _edge_contacts(bbox, w, h), comp_mask))
    return sorted(components, key=lambda c: c.area_px, reverse=True)


def _connected_components_fallback(mask: np.ndarray) -> list[Component]:
    h, w = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    components: list[Component] = []
    for y in range(h):
        for x in np.where(mask[y] & ~seen[y])[0]:
            if seen[y, x] or not mask[y, x]:
                continue
            stack = [(int(x), int(y))]
            seen[y, x] = True
            coords: list[tuple[int, int]] = []
            while stack:
                cx, cy = stack.pop()
                coords.append((cx, cy))
                for nx, ny in ((cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)):
                    if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((nx, ny))
            xs = [pt[0] for pt in coords]
            ys = [pt[1] for pt in coords]
            bbox = (min(xs), min(ys), max(xs) + 1, max(ys) + 1)
            comp_mask = np.zeros(mask.shape, dtype=bool)
            comp_mask[ys, xs] = True
            components.append(Component(len(coords), bbox, _edge_contacts(bbox, w, h), comp_mask))
    return sorted(components, key=lambda c: c.area_px, reverse=True)


def _evaluate_candidate(path: Path) -> CandidateReport:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
    alpha = np.asarray(rgba.getchannel("A"))
    mask = alpha > 16
    canvas_h, canvas_w = mask.shape
    total_alpha_px = int(mask.sum())
    components = _connected_components(mask)
    component_reports = [
        component.to_report(total_alpha_px, canvas_w, canvas_h)
        for component in components
    ]
    reasons: list[str] = []
    retained = components[0] if components else None
    coverage = total_alpha_px / max(canvas_w * canvas_h, 1)
    removed_px = total_alpha_px - (retained.area_px if retained else 0)

    if total_alpha_px <= 0 or retained is None:
        reasons.append("no_foreground_alpha")
    else:
        retained_ratio = retained.area_px / max(total_alpha_px, 1)
        retained_canvas_ratio = retained.area_px / max(canvas_w * canvas_h, 1)
        x0, y0, x1, y1 = retained.bbox_px
        bbox_w_ratio = (x1 - x0) / canvas_w
        bbox_h_ratio = (y1 - y0) / canvas_h
        if retained_ratio < 0.75:
            reasons.append("main_component_ratio_too_low_for_selection")
        if retained_canvas_ratio < 0.01:
            reasons.append("main_component_too_small")
        if len(retained.edge_contacts) >= 2:
            reasons.append("main_component_contacts_multiple_edges")
        if bbox_w_ratio > 0.98 and bbox_h_ratio > 0.98:
            reasons.append("main_component_full_canvas")
        if coverage > 0.65:
            reasons.append("foreground_coverage_too_high")

    rank_score = -1.0
    if retained is not None:
        retained_ratio = retained.area_px / max(total_alpha_px, 1)
        rank_score = (
            retained_ratio
            + min(coverage, 0.35)
            - 0.18 * len(retained.edge_contacts)
            - 0.03 * max(0, len(components) - 1)
        )
    return CandidateReport(
        source_name=path.name,
        source_path=path,
        accepted=not reasons,
        rejection_reasons=reasons,
        retained_component=retained,
        total_alpha_px=total_alpha_px,
        removed_px=removed_px,
        coverage=coverage,
        component_count=len(components),
        components=component_reports,
        rank_score=rank_score,
    )


def _clean_to_largest_component(src: Path, dst: Path, component: Component) -> None:
    with Image.open(src) as image:
        rgba = image.convert("RGBA")
    arr = np.array(rgba)
    arr[~component.mask, 3] = 0
    dst.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr, mode="RGBA").save(dst)


def _select_candidate(panel_root: Path) -> tuple[CandidateReport, list[CandidateReport]]:
    reports = [
        _evaluate_candidate(panel_root / name)
        for name in CANDIDATE_NAMES
        if (panel_root / name).is_file()
    ]
    if not reports:
        raise RealV5StructuralError("no foreground candidates found: layer_02.png/layer_03.png")
    accepted = [report for report in reports if report.accepted]
    if not accepted:
        details = "; ".join(
            f"{r.source_name}={','.join(r.rejection_reasons) or 'unknown'}"
            for r in reports
        )
        raise RealV5StructuralError(f"no clean foreground candidate accepted: {details}")
    selected = sorted(
        accepted,
        key=lambda r: (-r.rank_score, CANDIDATE_NAMES.index(r.source_name)),
    )[0]
    return selected, reports


def _subject_from_inputs(panel_id: str, telemetry: dict[str, Any], subject: str) -> str:
    if subject in {"pilot", "mecha"}:
        return subject
    lowered = " ".join([
        panel_id.lower(),
        str(telemetry.get("prompt") or "").lower(),
        str(telemetry.get("layer_roles") or "").lower(),
    ])
    if "mecha" in lowered and "pilot" not in lowered:
        return "mecha"
    return "pilot"


def _default_l0_meta(
    *,
    panel_id: str,
    structural_template_id: str,
    support_mode: str,
) -> dict[str, Any]:
    if support_mode == "intentional_seat_table":
        zones = [{
            "zone_id": "seat_table_support",
            "kind": "seat_table",
            "bbox_pct": [34, 55, 35, 22],
            "occupancy": "intentional_support",
            "allows_character_support": True,
            "allowed_structural_templates": [structural_template_id],
            "priority": 10,
        }]
    else:
        zones = [{
            "zone_id": "clear_floor",
            "kind": "floor",
            "polygon_pct": [[0, 62], [100, 56], [100, 100], [0, 100]],
            "occupancy": "clear",
            "allows_character_support": True,
            "allowed_structural_templates": [structural_template_id],
            "priority": 0,
        }]
    return {
        "schema_version": "1.0.0",
        "asset_id": f"{panel_id}_l0_real_v5_selected_support",
        "layer_class": "L0",
        "genre": "mecha",
        "style_register": "mecha_real_v5_selected_component",
        "bg_class": "full_render",
        "light": {"azimuth": "ambient"},
        "camera": {
            "angle_bucket": "eye_level",
            "eye_level_y_pct": 42,
            "camera_height": "standing",
        },
        "anchor_slots": [],
        "support_zones": zones,
        "structural_layer_contract": {
            "id": CONTRACT_ID,
            "status": "clean",
            "role": "environment_support",
            "subject": "environment",
            "contains_primary_subject": False,
            "contains_foreground_subject": False,
            "contains_pilot": False,
            "contains": [],
        },
    }


def _copy_or_write_l0_sidecar(
    *,
    src_l0: Path,
    dst_l0: Path,
    panel_id: str,
    structural_template_id: str,
    support_mode: str,
) -> dict[str, Any]:
    sidecar = _composition_sidecar(src_l0)
    if sidecar.is_file():
        meta = _read_json(sidecar)
    else:
        meta = _default_l0_meta(
            panel_id=panel_id,
            structural_template_id=structural_template_id,
            support_mode=support_mode,
        )
    validate_mecha_layer_meta(meta, layer_class="L0")
    _composition_sidecar(dst_l0).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def _alpha_anchor_metrics(path: Path) -> dict[str, Any]:
    with Image.open(path) as image:
        rgba = image.convert("RGBA")
    tight = alpha_tight_bbox(rgba)
    if tight is None:
        raise RealV5StructuralError(f"selected L2 has no alpha: {path}")
    left, top, right, bottom = tight
    return {
        "alpha_bbox_px": [left, top, right, bottom],
        "alpha_coverage": round(
            int((np.asarray(rgba.getchannel("A")) > 16).sum()) / max(rgba.width * rgba.height, 1),
            6,
        ),
        "anchor_y_px": bottom,
        "eye_y_px": round(top + (bottom - top) * 0.2, 3),
    }


def _write_l2_sidecar(
    *,
    dst_l2: Path,
    panel_id: str,
    subject: str,
    source_report: CandidateReport,
    figure_height_m: float,
) -> dict[str, Any]:
    metrics = _alpha_anchor_metrics(dst_l2)
    meta = {
        "schema_version": "1.0.0",
        "asset_id": f"{panel_id}_l2_real_v5_selected_{subject}",
        "layer_class": "L2",
        "genre": "mecha",
        "style_register": f"mecha_real_v5_selected_{subject}",
        "crop_class": "full_figure",
        "room_capable": True,
        "abstract_stage_eligible": False,
        "scene_contamination": False,
        "light": {"azimuth": "ambient"},
        "implied_camera": {"angle_bucket": "eye_level"},
        "anchor": {"point": "feet", "y_px": metrics["anchor_y_px"]},
        "eye_y_px": metrics["eye_y_px"],
        "figure_height_m": figure_height_m,
        "structural_layer_contract": {
            "id": CONTRACT_ID,
            "status": "clean",
            "role": "single_subject_cutout",
            "subject": subject,
            "contains_background": False,
            "contains_environment": False,
            "contains": [subject],
            "background_context": [],
        },
        "cutout": {
            "alpha_bbox_px": metrics["alpha_bbox_px"],
            "alpha_coverage": metrics["alpha_coverage"],
            "selected_component_from": source_report.source_name,
            "removed_px": source_report.removed_px,
        },
    }
    validate_mecha_layer_meta(meta, layer_class="L2")
    _composition_sidecar(dst_l2).write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    return meta


def _support_polygon_for_plan(
    l0_meta: dict[str, Any],
    *,
    structural_template_id: str,
    support_mode: str,
) -> tuple[str, list[list[float]]]:
    zones = l0_meta.get("support_zones") or []
    for zone in sorted(zones, key=lambda z: -int(z.get("priority", 0))):
        allowed = zone.get("allowed_structural_templates") or zone.get("allowed_templates") or []
        if allowed and structural_template_id not in [str(v) for v in allowed]:
            continue
        if support_mode == "intentional_seat_table":
            bbox = zone.get("bbox_pct")
            if isinstance(bbox, list) and len(bbox) == 4:
                x, y, w, h = [float(v) for v in bbox]
                return str(zone.get("kind") or "seat_or_table"), [[x, y], [x + w, y], [x + w, y + h], [x, y + h]]
        poly = zone.get("polygon_pct") or zone.get("support_polygon_pct")
        if isinstance(poly, list) and len(poly) >= 3:
            return str(zone.get("kind") or "floor"), [[float(p[0]), float(p[1])] for p in poly]
        bbox_xyxy = zone.get("bbox_pct_xyxy")
        if isinstance(bbox_xyxy, list) and len(bbox_xyxy) == 4:
            x0, y0, x1, y1 = [float(v) for v in bbox_xyxy]
            return str(zone.get("kind") or "floor"), [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    if support_mode == "intentional_seat_table":
        return "seat_or_table", [[34, 55], [69, 55], [69, 77], [34, 77]]
    return "floor", [[0, 62], [100, 56], [100, 100], [0, 100]]


def _resolve_transform_values(
    *,
    support_mode: str,
    tx_pct: float | None,
    ty_pct: float | None,
    uniform_scale: float | None,
) -> tuple[float, float, float]:
    default_tx, default_ty, default_scale = (
        DEFAULT_SEATED_TRANSFORM
        if support_mode == "intentional_seat_table"
        else DEFAULT_STANDING_TRANSFORM
    )
    return (
        default_tx if tx_pct is None else tx_pct,
        default_ty if ty_pct is None else ty_pct,
        default_scale if uniform_scale is None else uniform_scale,
    )


def _build_plan(
    *,
    panel_id: str,
    canvas_w: int,
    canvas_h: int,
    structural_template_id: str,
    panel_type_id: str,
    relation: str,
    support_role: str,
    support_polygon_pct: list[list[float]],
    tx_pct: float,
    ty_pct: float,
    uniform_scale: float,
) -> dict[str, Any]:
    allowed_relations = sorted({
        relation,
        "standing_on",
        "seated_on",
        "resting_on",
        "held_by",
        "occluded_by",
    })
    plan_body = {
        "panel_id": panel_id,
        "canvas": {"width": canvas_w, "height": canvas_h},
        "structural_template_id": structural_template_id,
        "panel_type_id": panel_type_id,
        "required_support_proof": [relation],
        "allowed_relations": allowed_relations,
        "support_graph": {
            "nodes": [
                {
                    "node_id": SUPPORT_NODE_ID,
                    "category": "support_surface",
                    "role": support_role,
                    "support_polygon_pct": support_polygon_pct,
                },
                {
                    "node_id": CHAR_NODE_ID,
                    "category": "character",
                    "role": "primary_subject",
                    "contact_point_pct": [0.0, 0.0],
                },
            ],
            "edges": [
                {
                    "edge_id": "e_support",
                    "relation": relation,
                    "from_node": CHAR_NODE_ID,
                    "to_node": SUPPORT_NODE_ID,
                }
            ],
        },
        "resolved_placements": [
            {
                "node_id": CHAR_NODE_ID,
                "transform": {
                    "tx_pct": tx_pct,
                    "ty_pct": ty_pct,
                    "uniform_scale": uniform_scale,
                    "rotation_deg": 0.0,
                    "transform_model": sc.TRANSFORM_MODEL,
                },
            }
        ],
        "transform_model": sc.TRANSFORM_MODEL,
    }
    envelope = {
        "schema_version": "1.0.0",
        "envelope_id": f"real_v5_structural_{panel_id}",
        "transform_model": sc.TRANSFORM_MODEL,
        "structural_template_id": structural_template_id,
        "panel_type_id": panel_type_id,
        "plan_body": plan_body,
        "plan_hash": sc.compute_plan_hash(plan_body),
    }
    sc.render_from_verified_plan(envelope, require_hash=True)
    return envelope


def _write_manifest(
    *,
    path: Path,
    panel_id: str,
    canvas_w: int,
    canvas_h: int,
    support_mode: str,
) -> None:
    manifest = {
        "schema_version": "1.0.0",
        "series_id": "pearl_star_real_v5_structural_selected_component",
        "manifest_id": f"{panel_id}_real_v5_selected_component",
        "canvas": {"width": canvas_w, "height": canvas_h, "background_hex": "#FFFFFF"},
        "panels": [{
            "panel_id": panel_id,
            "shot_type": "establishing",
            "structural_plan_path": PLAN_NAME,
            "layers": [
                {
                    "layer_class": "L0",
                    "asset": L0_NAME,
                    "provenance": "REAL",
                    "provenance_note": "Pearl Star real V5 layer_01 support plate.",
                },
                {
                    "layer_class": "L2",
                    "asset": OUTPUT_L2_NAME,
                    "provenance": "REAL",
                    "provenance_note": "Selected largest alpha component from real V5 foreground candidate.",
                    "structural_node_id": CHAR_NODE_ID,
                    "grounding": {
                        "contact_shadow": True,
                        "occluder": False,
                        "support_mode": support_mode,
                        "require_l0_support_zone": True,
                    },
                },
            ],
        }],
    }
    path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")


def assemble_real_v5_structural(
    *,
    v5_panel_root: Path,
    out_dir: Path,
    subject: str = "auto",
    panel_id: str | None = None,
    structural_template_id: str = "standing_room_scene",
    panel_type_id: str = "establish_standing_room",
    relation: str = "standing_on",
    support_role: str | None = None,
    support_mode: str = "standing_floor",
    tx_pct: float | None = None,
    ty_pct: float | None = None,
    uniform_scale: float | None = None,
    figure_height_m: float | None = None,
    tests: str | None = None,
) -> AssemblyResult:
    v5_panel_root = v5_panel_root.resolve()
    out_dir = out_dir.resolve()
    telemetry_path = _require_file(v5_panel_root / TELEMETRY_NAME, TELEMETRY_NAME)
    model_path = _require_file(v5_panel_root / MODEL_COMPOSITE_NAME, MODEL_COMPOSITE_NAME)
    l0_src = _require_file(v5_panel_root / L0_NAME, L0_NAME)
    telemetry = _read_json(telemetry_path)
    resolved_panel_id = panel_id or str(telemetry.get("panel_id") or v5_panel_root.parent.name or v5_panel_root.name)
    selected_subject = _subject_from_inputs(resolved_panel_id, telemetry, subject)
    resolved_figure_height_m = figure_height_m
    if resolved_figure_height_m is None:
        resolved_figure_height_m = 5.8 if selected_subject == "mecha" else 1.62

    selected, all_reports = _select_candidate(v5_panel_root)
    if selected.retained_component is None:
        raise RealV5StructuralError(f"selected candidate has no retained component: {selected.source_name}")

    out_dir.mkdir(parents=True, exist_ok=True)
    l0_dst = out_dir / L0_NAME
    l2_dst = out_dir / OUTPUT_L2_NAME
    shutil.copy2(l0_src, l0_dst)
    _clean_to_largest_component(selected.source_path, l2_dst, selected.retained_component)

    l0_meta = _copy_or_write_l0_sidecar(
        src_l0=l0_src,
        dst_l0=l0_dst,
        panel_id=resolved_panel_id,
        structural_template_id=structural_template_id,
        support_mode=support_mode,
    )
    l2_meta = _write_l2_sidecar(
        dst_l2=l2_dst,
        panel_id=resolved_panel_id,
        subject=selected_subject,
        source_report=selected,
        figure_height_m=resolved_figure_height_m,
    )

    with Image.open(l0_dst) as bg:
        canvas_w, canvas_h = bg.size
    with Image.open(l2_dst) as fg:
        if fg.size != (canvas_w, canvas_h):
            raise RealV5StructuralError(
                f"selected L2 size {fg.size} does not match L0/canvas {(canvas_w, canvas_h)}"
            )
        afb.require_structural_l2_quality(
            fg.convert("RGBA"),
            l2_meta=l2_meta,
            structural_template_id=structural_template_id,
        )

    inferred_support_role, support_polygon_pct = _support_polygon_for_plan(
        l0_meta,
        structural_template_id=structural_template_id,
        support_mode=support_mode,
    )
    resolved_tx_pct, resolved_ty_pct, resolved_uniform_scale = _resolve_transform_values(
        support_mode=support_mode,
        tx_pct=tx_pct,
        ty_pct=ty_pct,
        uniform_scale=uniform_scale,
    )
    plan = _build_plan(
        panel_id=resolved_panel_id,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
        structural_template_id=structural_template_id,
        panel_type_id=panel_type_id,
        relation=relation,
        support_role=support_role or inferred_support_role,
        support_polygon_pct=support_polygon_pct,
        tx_pct=resolved_tx_pct,
        ty_pct=resolved_ty_pct,
        uniform_scale=resolved_uniform_scale,
    )
    plan_path = out_dir / PLAN_NAME
    plan_path.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    manifest_path = out_dir / MANIFEST_NAME
    _write_manifest(
        path=manifest_path,
        panel_id=resolved_panel_id,
        canvas_w=canvas_w,
        canvas_h=canvas_h,
        support_mode=support_mode,
    )
    afb.load_manifest(manifest_path)
    assembly = afb.run(manifest_path, out_dir)
    final_paths = [Path(str(p)) for p in assembly.get("panels") or []]
    if not final_paths:
        raise RealV5StructuralError("assembler produced no final panel")
    final_path = final_paths[0].resolve()
    if not final_path.is_file():
        raise RealV5StructuralError(f"assembler final panel missing: {final_path}")
    if _sha256(final_path) == _sha256(model_path):
        raise RealV5StructuralError("final structural PNG equals layer_00 model composite")

    gate_report_path = out_dir / "gate_report.json"
    gate_report = _read_json(gate_report_path)
    panels = gate_report.get("panels") or []
    if not panels:
        raise RealV5StructuralError("assembler did not emit gate report panels")
    actual_gates = {
        str(gate.get("gate"))
        for gate in panels[0].get("gates") or []
        if isinstance(gate, dict)
    }
    missing = sorted(REQUIRED_GATES - actual_gates)
    if missing:
        raise RealV5StructuralError(f"assembler gate report missing required gates: {missing}")
    if not panels[0].get("passed"):
        raise RealV5StructuralError("assembler gate report did not pass")

    closeout = {
        "raw-v5-layer-roles": "not-green",
        "selected-component-structural-assembly": "green-for-proof",
        "manga-100pct-green": "not-claimed",
        "panel_id": resolved_panel_id,
        "source_v5_panel_root": _repo_rel(v5_panel_root),
        "ignored_model_composite": MODEL_COMPOSITE_NAME,
        "selected_candidate": selected.to_report(),
        "candidate_reports": [report.to_report() for report in all_reports],
        "output_layer_map": {
            "layer_01.png": "L0 background/support",
            "layer_02.png": f"L2 selected largest component from {selected.source_name}",
        },
        "support": {
            "structural_template_id": structural_template_id,
            "panel_type_id": panel_type_id,
            "relation": relation,
            "support_role": support_role or inferred_support_role,
            "support_mode": support_mode,
            "tx_pct": resolved_tx_pct,
            "ty_pct": resolved_ty_pct,
            "uniform_scale": resolved_uniform_scale,
        },
        "subject": selected_subject,
        "manifest": _repo_rel(manifest_path),
        "structural_plan": _repo_rel(plan_path),
        "gate_report": _repo_rel(gate_report_path),
        "actual_gates": sorted(actual_gates),
        "final_composite": _repo_rel(final_path),
        "final_sha256": _sha256(final_path),
        "model_layer_00_sha256": _sha256(model_path),
        "final_differs_from_layer_00": True,
        "tests": tests or "not provided",
    }
    closeout_path = out_dir / CLOSEOUT_JSON
    closeout_path.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
    md = [
        "# Real V5 Structural Closeout",
        "",
        "- raw-v5-layer-roles=not-green",
        "- selected-component-structural-assembly=green-for-proof",
        "- manga-100pct-green=not-claimed",
        f"- panel_id={resolved_panel_id}",
        f"- selected_candidate={selected.source_name}",
        f"- removed_px={selected.removed_px}",
        f"- final_composite={_repo_rel(final_path)}",
        f"- required_gates={','.join(sorted(REQUIRED_GATES))}",
        f"- tests={tests or 'not provided'}",
        "",
    ]
    (out_dir / CLOSEOUT_MD).write_text("\n".join(md), encoding="utf-8")
    return AssemblyResult(
        panel_id=resolved_panel_id,
        output_dir=out_dir,
        final_path=final_path,
        closeout_path=closeout_path,
        manifest_path=manifest_path,
        structural_plan_path=plan_path,
        selected_candidate=selected,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--v5-panel-root", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--panel-id", default=None)
    parser.add_argument("--subject", choices=["auto", "pilot", "mecha"], default="auto")
    parser.add_argument("--structural-template-id", default="standing_room_scene")
    parser.add_argument("--panel-type-id", default="establish_standing_room")
    parser.add_argument("--relation", default="standing_on")
    parser.add_argument("--support-role", default=None)
    parser.add_argument("--support-mode", default="standing_floor")
    parser.add_argument(
        "--tx-pct",
        type=float,
        default=None,
        help="Override structural contact x percent; seated default is tuned separately.",
    )
    parser.add_argument(
        "--ty-pct",
        type=float,
        default=None,
        help="Override structural contact y percent; seated default is tuned separately.",
    )
    parser.add_argument(
        "--uniform-scale",
        type=float,
        default=None,
        help="Override structural scale; seated default is tuned separately.",
    )
    parser.add_argument("--figure-height-m", type=float, default=None)
    parser.add_argument("--tests", default=None)
    args = parser.parse_args(argv)

    try:
        result = assemble_real_v5_structural(
            v5_panel_root=args.v5_panel_root,
            out_dir=args.out_dir,
            subject=args.subject,
            panel_id=args.panel_id,
            structural_template_id=args.structural_template_id,
            panel_type_id=args.panel_type_id,
            relation=args.relation,
            support_role=args.support_role,
            support_mode=args.support_mode,
            tx_pct=args.tx_pct,
            ty_pct=args.ty_pct,
            uniform_scale=args.uniform_scale,
            figure_height_m=args.figure_height_m,
            tests=args.tests,
        )
    except RealV5StructuralError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "ok": True,
        "panel_id": result.panel_id,
        "selected_candidate": result.selected_candidate.source_name,
        "removed_px": result.selected_candidate.removed_px,
        "manifest": _repo_rel(result.manifest_path),
        "structural_plan": _repo_rel(result.structural_plan_path),
        "final_composite": _repo_rel(result.final_path),
        "closeout": _repo_rel(result.closeout_path),
        "raw-v5-layer-roles": "not-green",
        "selected-component-structural-assembly": "green-for-proof",
        "manga-100pct-green": "not-claimed",
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
