#!/usr/bin/env python3
"""Deterministic layered panel assembly from a series image bank.

The bank-assembly lane of the V5 layered architecture: given a manifest of
banked layer assets (L0 backdrop plates, L2 character cutouts, L3 object
sprites, optional L1/L4), composite panels OFFLINE with zero GPU work and
zero randomness. This is the "bank × assembly = many stories" half of the
layered-image system; GPU rendering of the bank assets themselves stays with
`render_v5_episode.py` (live dispatch) / `render_v4_episode.py` (legacy).

Spec authority (this tool implements, it does not re-specify):
  - docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §4  — layer taxonomy,
    z-order (incl. L3 above_L2/below_L2), L4 screen-blend contract
  - docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §10 — composite placement
    math (tight-crop → min-scale → LANCZOS → centered paste, 0px feather)
  - docs/specs/MANGA_V5_LAYERED_ARCHITECTURE.md §7      — layer semantics
  - schemas/manga/assembly_manifest.schema.json         — manifest contract

Reuses (does not reimplement):
  - phoenix_v4.manga.chapter.bubble_render.render_bubbles_onto_panel for the
    lettering pass (--bubbles)
  - scripts/manga/validate_layer.py checks remain the QA authority for the
    input cutouts; this tool validates manifest structure + provenance only.

Provenance doctrine: every layer in the manifest MUST declare REAL or
INTERIM provenance. The assembler stamps a provenance table
(`<out>/_provenance.json` + `.md`) into the output dir and refuses any
manifest with unlabeled layers. An INTERIM layer is a labeled stand-in —
never presentable as final art.

Tier 1 (operator-present). No LLM calls. No network. No paid APIs.
Pure local PIL compositing of already-rendered images.

Usage:
    PYTHONPATH=. python3 scripts/manga/assemble_from_bank.py \
        --manifest artifacts/manga/<series>/assembly_manifests/<name>.yaml \
        --out-dir  artifacts/manga/<series>/assembled/<name>/ \
        [--strip] [--bubbles] [--locale en_US] [--dry-run]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import warnings
from pathlib import Path
from typing import Any

import numpy as np
import yaml
from PIL import Image, ImageChops, ImageFilter

from composition_grammar import (
    ABSTRACT_BG,
    AssemblyReport,
    CAMERA_HEIGHT_M,
    GateResult,
    GateSeverity,
    alpha_tight_bbox,
    bbox_legacy_paste,
    defringe_cutout,
    derive_defocus,
    derive_tone_gradient,
    dialogue_bust_paste,
    effective_l0_meta,
    g3_horizon_scale_check,
    g4_shadow_applied,
    g6_defringe_applied,
    load_composition_meta,
    paste_occluder_from_slot,
    plan_horizon_scale_paste,
    render_contact_shadow_layer,
    resolve_anchor_slot,
    run_combination_gates,
)
from structural_composition import (
    ResolvedTransform,
    StructuralHardFail,
    apply_transform_to_point_pct,
    render_from_verified_plan,
)
from mecha_clean_structural_layer import validate_mecha_layer_meta

REPO = Path(__file__).resolve().parents[2]

# §10 z-order table (bottom → top). L3 flips to 15 when z_order=below_L2.
Z_DEFAULT = {"L0": 0, "L1": 10, "L2": 20, "L3": 30, "L4": 40}
Z_L3_BELOW_L2 = 15

CUTOUT_CLASSES = {"L1", "L2", "L3"}
STRUCTURAL_L2_ALPHA_THRESHOLD = 128
STRUCTURAL_L2_SIGNIFICANT_COMPONENT_MIN_PCT = 1.0
STRUCTURAL_L2_MAIN_COMPONENT_MIN_RATIO = 0.9
STRUCTURAL_L2_MAX_SIGNIFICANT_COMPONENTS = 1


def _structural_purity_gate_name(layer_class: str) -> str:
    return f"{layer_class}_STRUCTURAL_PURITY"


def _require_structural_purity_gate(
    meta: dict[str, Any] | None,
    *,
    layer_class: str,
    report: AssemblyReport,
) -> None:
    purity = validate_mecha_layer_meta(meta, layer_class=layer_class)
    if not purity:
        return
    report.gates.append(
        GateResult(
            _structural_purity_gate_name(layer_class),
            GateSeverity.PASS,
            f"contract={purity['contract']} role={purity['role']} subject={purity['subject']}",
        ),
    )


def _resolve(path_str: str, manifest_dir: Path) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    for base in (REPO, manifest_dir):
        cand = base / p
        if cand.is_file():
            return cand
    return REPO / p  # let the open() raise with the canonical candidate


def load_manifest(manifest_path: Path) -> dict[str, Any]:
    manifest = yaml.safe_load(manifest_path.read_text())
    errors = validate_manifest(manifest)
    if errors:
        raise ValueError(
            "manifest failed validation:\n  - " + "\n  - ".join(errors)
        )
    from panel_planning_rules import (  # noqa: WPS433
        shot_type_for_archetype,
        validate_manifest_composition_planning,
    )
    from validate_chapter_composition_grammar import validate_chapter_composition_grammar  # noqa: WPS433

    for panel in manifest.get("panels") or []:
        if not panel.get("shot_type"):
            shot = shot_type_for_archetype(panel.get("archetype"))
            if shot:
                panel["shot_type"] = shot

    planning = validate_manifest_composition_planning(
        manifest, manifest_path.parent, REPO,
    )
    if planning:
        raise ValueError(
            "manifest failed composition planning:\n  - " + "\n  - ".join(planning)
        )
    ch_fails = [
        f for f in validate_chapter_composition_grammar(manifest, manifest_path.parent)
        if f.severity == "FAIL"
    ]
    if ch_fails:
        msgs = [f"{f.rule_id} {f.panel_id}: {f.message}" for f in ch_fails]
        raise ValueError(
            "manifest failed chapter composition grammar:\n  - " + "\n  - ".join(msgs)
        )
    return manifest


def validate_manifest(manifest: dict[str, Any]) -> list[str]:
    """Structural + provenance validation. Returns a list of errors (empty = ok).

    Deliberately duplicates the load-bearing rules of
    schemas/manga/assembly_manifest.schema.json so the tool fails closed
    without a jsonschema dependency; CI can additionally validate against
    the schema file.
    """
    errors: list[str] = []
    for key in ("schema_version", "series_id", "canvas", "panels"):
        if key not in manifest:
            errors.append(f"missing top-level key: {key}")
    if errors:
        return errors
    canvas = manifest["canvas"]
    if not (isinstance(canvas.get("width"), int) and isinstance(canvas.get("height"), int)):
        errors.append("canvas.width/height must be integers")
    for i, panel in enumerate(manifest["panels"]):
        pid = panel.get("panel_id", f"<panels[{i}]>")
        layers = panel.get("layers") or []
        has_structural_plan = bool(
            panel.get("structural_plan") is not None or panel.get("structural_plan_path")
        )
        if not layers:
            errors.append(f"{pid}: no layers")
        for j, layer in enumerate(layers):
            lc = layer.get("layer_class")
            if lc not in Z_DEFAULT:
                errors.append(f"{pid}.layers[{j}]: bad layer_class {lc!r}")
                continue
            if not layer.get("asset"):
                errors.append(f"{pid}.layers[{j}]: missing asset")
            if layer.get("provenance") not in ("REAL", "INTERIM"):
                errors.append(
                    f"{pid}.layers[{j}] ({lc}): provenance must be REAL or INTERIM "
                    "— unlabeled layers are refused (stub-as-done guard)"
                )
            if lc in CUTOUT_CLASSES and not layer.get("bbox_pct"):
                if not (
                    lc == "L2"
                    and (layer.get("anchor_slot") or has_structural_plan)
                ):
                    errors.append(f"{pid}.layers[{j}] ({lc}): bbox_pct required for {lc}")
            bbox = layer.get("bbox_pct")
            if bbox is not None and (
                len(bbox) != 4 or not all(isinstance(v, (int, float)) for v in bbox)
            ):
                errors.append(f"{pid}.layers[{j}]: bbox_pct must be [x,y,w,h] numbers")
    return errors


def _load_structural_plan_context(
    panel: dict[str, Any],
    manifest_dir: Path,
) -> dict[str, Any] | None:
    inline = panel.get("structural_plan")
    path_ref = panel.get("structural_plan_path")
    if inline is None and not path_ref:
        return None
    if inline is not None and path_ref:
        raise ValueError(f"{panel['panel_id']}: structural_plan and structural_plan_path are mutually exclusive")
    if inline is not None:
        envelope = inline
    else:
        plan_path = _resolve(str(path_ref), manifest_dir)
        envelope = json.loads(plan_path.read_text(encoding="utf-8"))
    try:
        consumed = render_from_verified_plan(envelope, require_hash=True)
    except StructuralHardFail as exc:
        raise ValueError(f"{panel['panel_id']}: structural plan invalid — {exc}") from exc

    nodes = consumed["support_graph"]["nodes"]
    placements = consumed["resolved_placements"]
    return {
        "envelope": envelope,
        "plan_hash": consumed["plan_hash"],
        "placements_by_id": {row["node_id"]: row["transform"] for row in placements},
        "nodes_by_id": {row["node_id"]: row for row in nodes},
        "character_node_ids": [
            row["node_id"] for row in nodes if row.get("category") == "character"
        ],
        "structural_template_id": (
            envelope.get("structural_template_id")
            or (envelope.get("plan_body") or {}).get("structural_template_id")
        ),
    }


def _infer_anchor_x_in_tight(
    cutout: Image.Image,
    tight_box: tuple[int, int, int, int],
    anchor_y_px: float,
) -> float:
    alpha = cutout.getchannel("A")
    left, top, right, bottom = tight_box
    anchor_y = max(top, min(bottom - 1, int(anchor_y_px)))
    for band in (8, 16, 32, 64, 128, 256):
        y0 = max(top, anchor_y - band)
        y1 = min(bottom, anchor_y + 1)
        if y1 <= y0:
            continue
        band_box = alpha.crop((left, y0, right, y1)).getbbox()
        if band_box and (band_box[2] - band_box[0]) >= 12:
            return (band_box[0] + band_box[2]) / 2.0
    return (right - left) / 2.0


def _resolved_transform_from_dict(transform: dict[str, Any]) -> ResolvedTransform:
    return ResolvedTransform(
        tx_pct=float(transform["tx_pct"]),
        ty_pct=float(transform["ty_pct"]),
        uniform_scale=float(transform.get("uniform_scale", 1.0)),
        rotation_deg=float(transform.get("rotation_deg", 0.0)),
    )


def _connected_alpha_components(mask: np.ndarray) -> list[dict[str, Any]]:
    """Return alpha-mask connected components sorted largest first.

    OpenCV is used when present because production panels are large; the small
    dependency-free fallback keeps the assembler usable in lean environments.
    """
    try:
        import cv2  # type: ignore[import-not-found]  # noqa: WPS433

        count, _labels, stats, _centroids = cv2.connectedComponentsWithStats(
            mask.astype("uint8"),
            8,
        )
        rows = []
        for idx in range(1, count):
            x, y, w, h, area = [int(v) for v in stats[idx]]
            if area > 0:
                rows.append({"area_px": area, "bbox_px": [x, y, x + w, y + h]})
        return sorted(rows, key=lambda row: row["area_px"], reverse=True)
    except Exception:  # noqa: BLE001 - fall back to pure Python scan
        height, width = mask.shape
        seen = np.zeros(mask.shape, dtype=bool)
        rows: list[dict[str, Any]] = []
        for start_y in range(height):
            start_xs = np.flatnonzero(mask[start_y] & ~seen[start_y])
            for start_x in start_xs:
                if seen[start_y, start_x] or not mask[start_y, start_x]:
                    continue
                stack = [(int(start_x), int(start_y))]
                seen[start_y, start_x] = True
                min_x = max_x = int(start_x)
                min_y = max_y = int(start_y)
                area = 0
                while stack:
                    x, y = stack.pop()
                    area += 1
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    for dy in (-1, 0, 1):
                        ny = y + dy
                        if ny < 0 or ny >= height:
                            continue
                        for dx in (-1, 0, 1):
                            if dx == 0 and dy == 0:
                                continue
                            nx = x + dx
                            if (
                                0 <= nx < width
                                and mask[ny, nx]
                                and not seen[ny, nx]
                            ):
                                seen[ny, nx] = True
                                stack.append((nx, ny))
                rows.append({
                    "area_px": area,
                    "bbox_px": [min_x, min_y, max_x + 1, max_y + 1],
                })
        return sorted(rows, key=lambda row: row["area_px"], reverse=True)


def structural_l2_quality_report(
    cutout: Image.Image,
    *,
    l2_meta: dict[str, Any] | None = None,
    structural_template_id: str | None = None,
) -> dict[str, Any]:
    """Deterministically validate that structural L2 is one clean subject.

    This catches the exact failure mode where a model foreground layer contains
    the character plus stray room fragments. Placement math cannot fix a dirty
    cutout; structural composition must reject it before claiming proof.
    """
    rgba = cutout.convert("RGBA")
    alpha = np.array(rgba.getchannel("A"))
    mask = alpha > STRUCTURAL_L2_ALPHA_THRESHOLD
    height, width = mask.shape
    opaque_px = int(mask.sum())
    report: dict[str, Any] = {
        "alpha_threshold": STRUCTURAL_L2_ALPHA_THRESHOLD,
        "canvas_size": [width, height],
        "opaque_px": opaque_px,
        "opaque_coverage_pct": round(opaque_px / max(width * height, 1) * 100, 3),
        "structural_template_id": structural_template_id or "",
        "crop_class": (l2_meta or {}).get("crop_class", ""),
        "failures": [],
    }
    if opaque_px <= 0:
        report["component_count"] = 0
        report["significant_component_count"] = 0
        report["main_component_area_ratio"] = 0.0
        report["failures"].append("no_opaque_subject_pixels")
        return report

    ys, xs = np.where(mask)
    report["alpha_bbox_px"] = [
        int(xs.min()),
        int(ys.min()),
        int(xs.max()) + 1,
        int(ys.max()) + 1,
    ]
    components = _connected_alpha_components(mask)
    min_significant_area = max(
        64,
        int(opaque_px * STRUCTURAL_L2_SIGNIFICANT_COMPONENT_MIN_PCT / 100.0),
    )
    significant = [
        row for row in components
        if int(row["area_px"]) >= min_significant_area
    ]
    main = components[0] if components else {"area_px": 0, "bbox_px": [0, 0, 0, 0]}
    main_ratio = int(main["area_px"]) / max(opaque_px, 1)
    report.update({
        "component_count": len(components),
        "significant_component_min_area_px": min_significant_area,
        "significant_component_count": len(significant),
        "main_component_area_ratio": round(main_ratio, 4),
        "main_component_bbox_px": main["bbox_px"],
        "top_components": components[:5],
    })

    if len(significant) > STRUCTURAL_L2_MAX_SIGNIFICANT_COMPONENTS:
        report["failures"].append("multi_component_foreground_contamination")
    if main_ratio < STRUCTURAL_L2_MAIN_COMPONENT_MIN_RATIO:
        report["failures"].append("main_subject_area_ratio_too_low")
    return report


def require_structural_l2_quality(
    cutout: Image.Image,
    *,
    l2_meta: dict[str, Any] | None = None,
    structural_template_id: str | None = None,
) -> dict[str, Any]:
    report = structural_l2_quality_report(
        cutout,
        l2_meta=l2_meta,
        structural_template_id=structural_template_id,
    )
    failures = report.get("failures") or []
    if failures:
        raise ValueError(
            "L2 foreground quality FAIL — "
            f"{','.join(str(f) for f in failures)}; "
            f"significant_components={report.get('significant_component_count')} "
            f"main_component_ratio={report.get('main_component_area_ratio')}"
        )
    return report


def _zone_polygon_pct(zone: dict[str, Any]) -> list[tuple[float, float]]:
    poly = zone.get("polygon_pct") or zone.get("support_polygon_pct")
    if isinstance(poly, list) and len(poly) >= 3:
        return [(float(pt[0]), float(pt[1])) for pt in poly]
    bbox = zone.get("bbox_pct")
    if isinstance(bbox, list) and len(bbox) == 4:
        x, y, w, h = [float(v) for v in bbox]
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    bbox_xyxy = zone.get("bbox_pct_xyxy")
    if isinstance(bbox_xyxy, list) and len(bbox_xyxy) == 4:
        x0, y0, x1, y1 = [float(v) for v in bbox_xyxy]
        return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    return []


def _polygon_area(poly: list[tuple[float, float]]) -> float:
    if len(poly) < 3:
        return 0.0
    area = 0.0
    for i, (x0, y0) in enumerate(poly):
        x1, y1 = poly[(i + 1) % len(poly)]
        area += x0 * y1 - x1 * y0
    return abs(area) / 2.0


def _point_in_pct_polygon(point: tuple[float, float], poly: list[tuple[float, float]]) -> bool:
    if len(poly) < 3:
        return False
    x, y = point
    inside = False
    j = len(poly) - 1
    for i, (xi, yi) in enumerate(poly):
        xj, yj = poly[j]
        if ((yi > y) != (yj > y)) and (
            x < (xj - xi) * (y - yi) / ((yj - yi) or 1e-12) + xi
        ):
            inside = not inside
        j = i
    return inside


def _support_zone_sort_key(zone: dict[str, Any]) -> tuple[int, float, str]:
    poly = _zone_polygon_pct(zone)
    # Higher priority wins; smaller zones win ties so specific furniture zones
    # override broad floor polygons deterministically.
    return (
        -int(zone.get("priority", 0)),
        _polygon_area(poly),
        str(zone.get("zone_id") or zone.get("id") or ""),
    )


def require_l0_support_zone(
    l0_meta: dict[str, Any],
    *,
    layer: dict[str, Any],
    node: dict[str, Any],
    transform: ResolvedTransform,
    structural_template_id: str | None,
) -> dict[str, Any] | None:
    """Validate the structural contact point against declared L0 support zones.

    This is opt-in via L0 composition metadata. When declared, zones are treated
    as authority: standing characters must land on clear floor/ground, while
    seated-table scenes require an explicit intentional seat/table contract.
    """
    support_zones = l0_meta.get("support_zones") or []
    grounding = layer.get("grounding") or {}
    if not support_zones:
        if grounding.get("require_l0_support_zone"):
            raise ValueError("L0 support-zone FAIL — no support_zones declared on L0")
        return None
    if not isinstance(support_zones, list):
        raise ValueError("L0 support-zone FAIL — support_zones must be a list")

    contact_pct = apply_transform_to_point_pct(
        node.get("contact_point_pct") or [0.0, 0.0],
        transform,
    )
    containing = [
        zone for zone in support_zones
        if _point_in_pct_polygon(contact_pct, _zone_polygon_pct(zone))
    ]
    containing = sorted(containing, key=_support_zone_sort_key)
    report: dict[str, Any] = {
        "contact_pct": [round(contact_pct[0], 3), round(contact_pct[1], 3)],
        "structural_template_id": structural_template_id or "",
        "containing_zone_ids": [
            str(zone.get("zone_id") or zone.get("id") or "")
            for zone in containing
        ],
        "failures": [],
    }
    if not containing:
        report["failures"].append("no_support_zone_at_contact_point")
        raise ValueError(
            "L0 support-zone FAIL — no_support_zone_at_contact_point; "
            f"contact_pct={report['contact_pct']}"
        )

    selected = containing[0]
    zone_id = str(selected.get("zone_id") or selected.get("id") or "")
    kind = str(selected.get("kind") or selected.get("role") or "")
    occupancy = str(selected.get("occupancy") or "clear")
    allows_support = bool(selected.get("allows_character_support", False))
    allowed_templates = [
        str(v) for v in (
            selected.get("allowed_structural_templates")
            or selected.get("allowed_templates")
            or []
        )
    ]
    support_mode = str(
        grounding.get("support_mode")
        or grounding.get("support_contract")
        or ""
    )
    report.update({
        "selected_zone_id": zone_id,
        "selected_zone_kind": kind,
        "selected_zone_occupancy": occupancy,
        "selected_zone_allows_character_support": allows_support,
        "selected_zone_allowed_templates": allowed_templates,
        "support_mode": support_mode,
    })

    if allowed_templates and structural_template_id not in allowed_templates:
        report["failures"].append("support_zone_template_not_allowed")

    if structural_template_id == "seated_table_scene":
        if support_mode != "intentional_seat_table":
            report["failures"].append("seated_table_requires_intentional_support_mode")
        if kind not in {"seat_table", "seat", "chair", "table"}:
            report["failures"].append("seated_table_requires_seat_or_table_zone")
        if not allows_support:
            report["failures"].append("support_zone_disallows_character_support")
    else:
        if support_mode == "intentional_seat_table":
            report["failures"].append("standing_scene_cannot_use_seat_table_mode")
        if kind not in {"floor", "ground", "clear_floor", "walkable_floor"}:
            report["failures"].append("standing_requires_floor_support_zone")
        if occupancy not in {"clear", "empty", "walkable"}:
            report["failures"].append("standing_contact_on_occupied_zone")
        if not allows_support:
            report["failures"].append("support_zone_disallows_character_support")

    failures = report["failures"]
    if failures:
        raise ValueError(
            "L0 support-zone FAIL — "
            f"{','.join(failures)}; "
            f"zone={zone_id or '<unnamed>'} kind={kind or '<unset>'} "
            f"occupancy={occupancy} contact_pct={report['contact_pct']}"
        )
    return report


def _structural_support_paste_plan(
    cutout: Image.Image,
    l2_meta: dict[str, Any],
    l0_meta: dict[str, Any],
    node: dict[str, Any],
    transform: ResolvedTransform,
    *,
    canvas_size: tuple[int, int],
) -> tuple[Image.Image | None, tuple[int, int], float, tuple[int, int, int, int], tuple[float, float]]:
    if abs(transform.rotation_deg) > 1e-9:
        raise ValueError("structural render path currently supports zero rotation only")

    W, H = canvas_size
    cutout = defringe_cutout(cutout)
    tight = alpha_tight_bbox(cutout)
    if tight is None:
        return None, (0, 0), 0.0, (0, 0, 0, 0), (0.0, 0.0)

    y_horizon = H * (l0_meta.get("camera") or {}).get("eye_level_y_pct", 42) / 100
    local_contact_pct = node.get("contact_point_pct") or [0.0, 0.0]
    world_contact_pct = apply_transform_to_point_pct(local_contact_pct, transform)
    world_contact_x = W * world_contact_pct[0] / 100.0
    world_contact_y = H * world_contact_pct[1] / 100.0
    if world_contact_y <= y_horizon:
        return None, (0, 0), 0.0, (0, 0, 0, 0), world_contact_pct

    layer_tight = cutout.crop(tight)
    anchor_y = float((l2_meta.get("anchor") or {}).get("y_px", 0.0))
    anchor_in_tight = anchor_y - tight[1]
    if anchor_in_tight <= 0:
        return None, (0, 0), 0.0, (0, 0, 0, 0), world_contact_pct
    anchor_x_in_tight = _infer_anchor_x_in_tight(cutout, tight, anchor_y)

    cam_h_key = (l0_meta.get("camera") or {}).get("camera_height", "seated")
    camera_height_m = CAMERA_HEIGHT_M.get(cam_h_key, 1.15)
    figure_height_m = float(l2_meta.get("figure_height_m", 1.62))
    target_figure_h = (
        (figure_height_m / camera_height_m) * (world_contact_y - y_horizon) * transform.uniform_scale
    )
    if target_figure_h <= 0:
        return None, (0, 0), 0.0, (0, 0, 0, 0), world_contact_pct

    scale = target_figure_h / anchor_in_tight
    new_w = max(1, int(layer_tight.width * scale))
    new_h = max(1, int(layer_tight.height * scale))
    scaled = layer_tight.resize((new_w, new_h), Image.LANCZOS)

    paste_x = int(world_contact_x - anchor_x_in_tight * scale)
    paste_y = int(world_contact_y - anchor_in_tight * scale)
    bbox = (paste_x, paste_y, paste_x + new_w, paste_y + new_h)
    return scaled, (paste_x, paste_y), target_figure_h, bbox, world_contact_pct


def _apply_l0_derivation(
    plate: Image.Image,
    derivation: dict[str, Any],
    canvas_size: tuple[int, int],
) -> Image.Image:
    """§8 derived backgrounds — zero-GPU PIL ops."""
    W, H = canvas_size
    dtype = derivation.get("type")
    if dtype == "defocus":
        params = derivation.get("params") or {}
        resized = plate.resize((W, H), Image.LANCZOS)
        return derive_defocus(resized, **params)
    if dtype == "tone_gradient":
        params = derivation.get("params") or {}
        return derive_tone_gradient((W, H), **params)
    if dtype == "void":
        color = "#FFFFFF" if derivation.get("void", "white") == "white" else "#000000"
        return Image.new("RGBA", (W, H), color)
    raise ValueError(f"unknown L0 derivation type: {dtype!r}")


def _grammar_l2_composite(
    canvas: Image.Image,
    cutout: Image.Image,
    *,
    l0_plate: Image.Image,
    l0_meta: dict[str, Any],
    l2_meta: dict[str, Any],
    layer: dict[str, Any],
    panel: dict[str, Any],
    report: AssemblyReport,
) -> Image.Image:
    """G1/G2/G8 pre-flight + G3/G4/G5/G6 grounding when sidecars exist."""
    derivation = None
    for lyr in panel.get("layers") or []:
        if lyr.get("layer_class") == "L0":
            derivation = lyr.get("derivation")
            break

    eff_l0 = effective_l0_meta(l0_meta, derivation)
    report.gates.extend(run_combination_gates(l2_meta, eff_l0))
    fails = [g for g in report.gates if g.severity == GateSeverity.FAIL]
    if fails:
        raise ValueError(
            f"{panel['panel_id']}: composition grammar FAIL — {fails[0].gate}: {fails[0].message}"
        )

    shot_type = panel.get("shot_type") or layer.get("shot_type")
    grounding = layer.get("grounding") or {}
    slot = resolve_anchor_slot(
        eff_l0,
        anchor_slot=layer.get("anchor_slot"),
        shot_type=shot_type,
    )
    bg = eff_l0.get("bg_class", "full_render")
    W, H = canvas.size

    if bg in ABSTRACT_BG or derivation:
        canvas = dialogue_bust_paste(canvas, cutout, l2_meta, slot)
        report.ops_applied.extend(["abstract_stage_paste", "G6_defringe"])
        report.gates.append(g6_defringe_applied(True))
        return canvas

    scaled, dest, target_h, contact_bbox = plan_horizon_scale_paste(
        cutout, l2_meta, eff_l0, slot, canvas_size=(W, H),
    )
    report.ops_applied.extend(["G3_horizon_scale", "G6_defringe"])
    report.gates.append(g3_horizon_scale_check(eff_l0, slot, H, target_h))

    if scaled is None:
        return canvas

    if grounding.get("contact_shadow", True) and contact_bbox != (0, 0, 0, 0):
        az = (eff_l0.get("light") or {}).get("azimuth", "camera_left")
        x0, y0, x1, y1 = contact_bbox
        floor = canvas.crop((
            max(0, x0), max(0, y1 - 20), min(W, x1), min(H, y1 + 5),
        ))
        shadow = render_contact_shadow_layer((W, H), contact_bbox, az, floor_sample=floor)
        canvas.alpha_composite(shadow)
        report.ops_applied.append("G4_contact_shadow_under_L2")
        report.gates.append(g4_shadow_applied(True))

    canvas.alpha_composite(scaled, dest=dest)

    if grounding.get("occluder", True) and slot.get("occluder_crop_bbox_pct"):
        canvas = paste_occluder_from_slot(canvas, l0_plate, slot)
        report.ops_applied.append("G5_occluder_BOOK")

    return canvas


def _structural_l2_composite(
    canvas: Image.Image,
    cutout: Image.Image,
    *,
    l0_plate: Image.Image,
    l0_meta: dict[str, Any],
    l2_meta: dict[str, Any],
    layer: dict[str, Any],
    panel: dict[str, Any],
    report: AssemblyReport,
    structural: dict[str, Any],
) -> Image.Image:
    """Render L2 from a verified structural plan instead of bbox placement."""
    derivation = None
    for lyr in panel.get("layers") or []:
        if lyr.get("layer_class") == "L0":
            derivation = lyr.get("derivation")
            break

    eff_l0 = effective_l0_meta(l0_meta, derivation)
    report.gates.extend(run_combination_gates(l2_meta, eff_l0))
    fails = [g for g in report.gates if g.severity == GateSeverity.FAIL]
    if fails:
        raise ValueError(
            f"{panel['panel_id']}: composition grammar FAIL — {fails[0].gate}: {fails[0].message}"
        )

    if eff_l0.get("bg_class", "full_render") in ABSTRACT_BG or derivation:
        warnings.warn(
            f"{panel['panel_id']}: structural_plan present on abstract/derived stage — falling back to grammar path",
            stacklevel=2,
        )
        report.gates.append(
            GateResult("placement", GateSeverity.WARN, "structural_plan_abstract_fallback"),
        )
        return _grammar_l2_composite(
            canvas,
            cutout,
            l0_plate=l0_plate,
            l0_meta=l0_meta,
            l2_meta=l2_meta,
            layer=layer,
            panel=panel,
            report=report,
        )

    node_id = layer.get("structural_node_id")
    if not node_id:
        char_node_ids = structural["character_node_ids"]
        if len(char_node_ids) == 1:
            node_id = char_node_ids[0]
        else:
            raise ValueError(
                f"{panel['panel_id']}: structural L2 requires structural_node_id when plan has multiple character nodes"
            )
    if node_id not in structural["placements_by_id"]:
        raise ValueError(f"{panel['panel_id']}: structural node {node_id!r} missing from resolved_placements")
    node = structural["nodes_by_id"].get(node_id)
    if not node or node.get("category") != "character":
        raise ValueError(f"{panel['panel_id']}: structural node {node_id!r} must be a character node for L2")

    transform = _resolved_transform_from_dict(structural["placements_by_id"][node_id])
    quality = require_structural_l2_quality(
        cutout,
        l2_meta=l2_meta,
        structural_template_id=structural.get("structural_template_id"),
    )
    report.gates.append(
        GateResult(
            "L2_QUALITY",
            GateSeverity.PASS,
            "single clean subject "
            f"main_component_ratio={quality['main_component_area_ratio']} "
            f"significant_components={quality['significant_component_count']}",
        ),
    )
    support = require_l0_support_zone(
        eff_l0,
        layer=layer,
        node=node,
        transform=transform,
        structural_template_id=structural.get("structural_template_id"),
    )
    if support:
        report.gates.append(
            GateResult(
                "L0_SUPPORT_ZONE",
                GateSeverity.PASS,
                f"zone={support['selected_zone_id']} "
                f"kind={support['selected_zone_kind']} "
                f"mode={support['support_mode'] or 'default'}",
            ),
        )
    scaled, dest, target_h, contact_bbox, world_contact_pct = _structural_support_paste_plan(
        cutout,
        l2_meta,
        eff_l0,
        node,
        transform,
        canvas_size=canvas.size,
    )
    if scaled is None:
        return canvas

    report.ops_applied.extend(["STRUCT_support_plan", "G3_horizon_scale", "G6_defringe"])
    report.gates.append(
        GateResult("placement", GateSeverity.PASS, f"structural_plan_hash={structural['plan_hash']}"),
    )
    g3_slot = {"feet_y_pct": world_contact_pct[1]}
    report.gates.append(g3_horizon_scale_check(eff_l0, g3_slot, canvas.size[1], target_h))

    grounding = layer.get("grounding") or {}
    if grounding.get("contact_shadow", True) and contact_bbox != (0, 0, 0, 0):
        az = (eff_l0.get("light") or {}).get("azimuth", "camera_left")
        x0, y0, x1, y1 = contact_bbox
        W, H = canvas.size
        floor = canvas.crop((
            max(0, x0), max(0, y1 - 20), min(W, x1), min(H, y1 + 5),
        ))
        shadow = render_contact_shadow_layer((W, H), contact_bbox, az, floor_sample=floor)
        canvas.alpha_composite(shadow)
        report.ops_applied.append("G4_contact_shadow_under_L2")
        report.gates.append(g4_shadow_applied(True))

    canvas.alpha_composite(scaled, dest=dest)

    if (
        grounding.get("occluder", True)
        and layer.get("anchor_slot")
        and structural.get("structural_template_id") == "seated_table_scene"
    ):
        slot = resolve_anchor_slot(
            eff_l0,
            anchor_slot=layer.get("anchor_slot"),
            shot_type=panel.get("shot_type") or layer.get("shot_type"),
        )
        if slot.get("occluder_crop_bbox_pct"):
            canvas = paste_occluder_from_slot(canvas, l0_plate, slot)
            report.ops_applied.append("G5_occluder_BOOK")

    return canvas


def composite_layer(canvas: Image.Image, layer_cutout: Image.Image,
                    bbox_pct: list[float]) -> Image.Image:
    """MANGA_LAYER_RENDER_CONTRACT_SPEC §10 math, verbatim semantics.

    Tight-crop the cutout to its alpha bbox, min-scale it into the target
    bbox (canvas-percentage coords), LANCZOS resample, centered paste,
    hard alpha (0px feather).
    """
    W, H = canvas.size
    x_pct, y_pct, w_pct, h_pct = bbox_pct
    target_x = int(W * x_pct / 100)
    target_y = int(H * y_pct / 100)
    target_w = int(W * w_pct / 100)
    target_h = int(H * h_pct / 100)
    tight_box = layer_cutout.getbbox()
    if tight_box is None:  # fully transparent asset
        return canvas
    layer_tight = layer_cutout.crop(tight_box)
    scale = min(target_w / layer_tight.width, target_h / layer_tight.height)
    new_size = (max(1, int(layer_tight.width * scale)),
                max(1, int(layer_tight.height * scale)))
    layer_scaled = layer_tight.resize(new_size, Image.LANCZOS)
    paste_x = target_x + (target_w - new_size[0]) // 2
    paste_y = target_y + (target_h - new_size[1]) // 2
    canvas.alpha_composite(layer_scaled, dest=(paste_x, paste_y))
    return canvas


def screen_blend_overlay(canvas: Image.Image, overlay: Image.Image,
                         opacity: float = 1.0) -> Image.Image:
    """§4.5 L4 contract: screen blend for additive effects, 2-3px Gaussian
    on alpha before blend (spec §10 feathering policy for L4)."""
    overlay = overlay.convert("RGBA").resize(canvas.size, Image.LANCZOS)
    alpha = overlay.getchannel("A").filter(ImageFilter.GaussianBlur(2.5))
    if opacity < 1.0:
        alpha = alpha.point(lambda a: int(a * opacity))
    base_rgb = canvas.convert("RGB")
    screened = ImageChops.screen(base_rgb, overlay.convert("RGB"))
    out = Image.composite(screened, base_rgb, alpha)
    return out.convert("RGBA")


def _layer_z(layer: dict[str, Any]) -> int:
    if layer.get("z_override") is not None:
        return int(layer["z_override"])
    lc = layer["layer_class"]
    if lc == "L3" and layer.get("z_order") == "below_L2":
        return Z_L3_BELOW_L2
    return Z_DEFAULT[lc]


def assemble_panel(panel: dict[str, Any], canvas_spec: dict[str, Any],
                   manifest_dir: Path) -> tuple[Image.Image, list[dict], AssemblyReport | None]:
    """Assemble one panel. Returns (image, per-layer provenance records, grammar report)."""
    W, H = canvas_spec["width"], canvas_spec["height"]
    bg_hex = canvas_spec.get("background_hex", "#FFFFFF")
    canvas = Image.new("RGBA", (W, H), bg_hex)
    records: list[dict] = []
    grammar_report = AssemblyReport(panel["panel_id"], panel.get("shot_type", ""))
    structural = _load_structural_plan_context(panel, manifest_dir)

    layers = sorted(panel["layers"], key=_layer_z)
    l0_plate: Image.Image | None = None
    l0_meta: dict[str, Any] | None = None

    for layer in layers:
        asset_path = _resolve(layer["asset"], manifest_dir)
        img = Image.open(asset_path).convert("RGBA")
        if layer.get("flip_h"):
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        opacity = float(layer.get("opacity", 1.0))
        lc = layer["layer_class"]

        if lc == "L0":
            l0_meta = load_composition_meta(asset_path)
            _require_structural_purity_gate(
                l0_meta,
                layer_class="L0",
                report=grammar_report,
            )
            l0_plate = img.copy()
            derivation = layer.get("derivation")
            if derivation:
                canvas = _apply_l0_derivation(img, derivation, (W, H))
                grammar_report.ops_applied.append(f"derive_{derivation.get('type')}")
            else:
                bg = img.resize((W, H), Image.LANCZOS)
                canvas.alpha_composite(bg)
        elif lc == "L4" and layer.get("blend", "screen") == "screen":
            canvas = screen_blend_overlay(canvas, img, opacity)
        elif lc == "L2":
            l2_meta = load_composition_meta(asset_path)
            _require_structural_purity_gate(
                l2_meta,
                layer_class="L2",
                report=grammar_report,
            )
            if opacity < 1.0:
                a = img.getchannel("A").point(lambda v: int(v * opacity))
                img.putalpha(a)
            if structural and l0_meta and l2_meta and l0_plate is not None:
                canvas = _structural_l2_composite(
                    canvas,
                    img,
                    l0_plate=l0_plate,
                    l0_meta=l0_meta,
                    l2_meta=l2_meta,
                    layer=layer,
                    panel=panel,
                    report=grammar_report,
                    structural=structural,
                )
            elif l0_meta and l2_meta and l0_plate is not None:
                canvas = _grammar_l2_composite(
                    canvas, img,
                    l0_plate=l0_plate,
                    l0_meta=l0_meta,
                    l2_meta=l2_meta,
                    layer=layer,
                    panel=panel,
                    report=grammar_report,
                )
            else:
                if l0_meta and not l2_meta:
                    warnings.warn(
                        f"{panel['panel_id']}: bbox_legacy — L2 composition_meta absent",
                        stacklevel=2,
                    )
                    grammar_report.gates.append(
                        GateResult("meta", GateSeverity.WARN, "bbox_legacy — L2 meta absent"),
                    )
                elif l2_meta and not l0_meta:
                    warnings.warn(
                        f"{panel['panel_id']}: bbox_legacy — L0 composition_meta absent",
                        stacklevel=2,
                    )
                    grammar_report.gates.append(
                        GateResult("meta", GateSeverity.WARN, "bbox_legacy — L0 meta absent"),
                    )
                if not layer.get("bbox_pct"):
                    raise ValueError(f"{panel['panel_id']}: L2 requires bbox_pct in legacy mode")
                warnings.warn(
                    f"{panel['panel_id']}: bbox_legacy — using §10 composite_layer",
                    stacklevel=2,
                )
                grammar_report.gates.append(
                    GateResult("placement", GateSeverity.WARN, "bbox_legacy"),
                )
                grammar_report.ops_applied.append("bbox_legacy_§10")
                canvas = composite_layer(canvas, img, layer["bbox_pct"])
        else:
            if lc == "L3":
                _require_structural_purity_gate(
                    load_composition_meta(asset_path),
                    layer_class="L3",
                    report=grammar_report,
                )
            if opacity < 1.0:
                a = img.getchannel("A").point(lambda v: int(v * opacity))
                img.putalpha(a)
            if not layer.get("bbox_pct"):
                raise ValueError(f"{panel['panel_id']}: {lc} requires bbox_pct")
            canvas = composite_layer(canvas, img, layer["bbox_pct"])

        records.append({
            "panel_id": panel["panel_id"],
            "layer_class": lc,
            "z": _layer_z(layer),
            "asset": str(asset_path.relative_to(REPO)) if asset_path.is_relative_to(REPO) else str(asset_path),
            "bytes": asset_path.stat().st_size,
            "provenance": layer["provenance"],
            "provenance_note": layer.get("provenance_note", ""),
        })

    has_grammar = bool(grammar_report.ops_applied or grammar_report.gates)
    return canvas, records, grammar_report if has_grammar else None


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def render_strip(panel_paths: list[Path], out_path: Path,
                 gutter_px: int = 80, bg_hex: str = "#FFFFFF") -> Path:
    """Stack panels into one vertical webtoon strip (fixed gutters).

    Beat-type-aware gutters live in phoenix_v4.manga.chapter.webtoon_compose
    .compose_episode_strips — that path needs the full episode payload
    contract; this is the minimal bank-demo stacker for assembly output.
    """
    imgs = [Image.open(p).convert("RGB") for p in panel_paths]
    w = max(i.width for i in imgs)
    h = sum(i.height for i in imgs) + gutter_px * (len(imgs) - 1)
    strip = Image.new("RGB", (w, h), bg_hex)
    y = 0
    for img in imgs:
        strip.paste(img, ((w - img.width) // 2, y))
        y += img.height + gutter_px
    strip.save(out_path, quality=92)
    return out_path


def run(manifest_path: Path, out_dir: Path, *, strip: bool = False,
        bubbles: bool = False, locale: str = "en_US",
        dry_run: bool = False) -> dict[str, Any]:
    manifest = load_manifest(manifest_path)
    if dry_run:
        n_layers = sum(len(p["layers"]) for p in manifest["panels"])
        print(f"DRY-RUN ok: {len(manifest['panels'])} panels, {n_layers} layers, "
              f"provenance labels present on all layers")
        return {"dry_run": True, "panels": len(manifest["panels"])}

    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_dir = manifest_path.parent
    all_records: list[dict] = []
    panel_paths: list[Path] = []
    gate_reports: list[dict] = []

    for panel in manifest["panels"]:
        img, records, grammar_report = assemble_panel(panel, manifest["canvas"], manifest_dir)
        out_path = out_dir / f"{panel['panel_id']}.png"
        img.save(out_path)
        all_records.extend(records)

        if grammar_report is not None:
            gate_reports.append({
                "panel_id": grammar_report.panel_id,
                "shot_type": grammar_report.shot_type,
                "passed": grammar_report.passed,
                "ops_applied": grammar_report.ops_applied,
                "gates": [
                    {"gate": g.gate, "severity": g.severity.value, "message": g.message}
                    for g in grammar_report.gates
                ],
            })

        final_path = out_path
        if bubbles and (panel.get("dialogue") or panel.get("narrator_caption") or panel.get("sfx")):
            sys.path.insert(0, str(REPO))
            from phoenix_v4.manga.chapter.bubble_render import render_bubbles_onto_panel
            bubbled = out_dir / f"{panel['panel_id']}_bubbled.png"
            render_bubbles_onto_panel(
                out_path,
                panel.get("dialogue") or [],
                panel.get("sfx") or [],
                panel.get("narrator_caption"),
                out_path=bubbled,
                locale=locale,
            )
            final_path = bubbled
        panel_paths.append(final_path)
        print(f"  {panel['panel_id']}: {final_path.name} "
              f"({final_path.stat().st_size:,} bytes)")

    # provenance table — the honest-labeling artifact, always written
    interim = [r for r in all_records if r["provenance"] == "INTERIM"]
    prov = {
        "manifest": str(manifest_path),
        "manifest_sha256": _sha256(manifest_path),
        "series_id": manifest["series_id"],
        "panels": len(manifest["panels"]),
        "layers_total": len(all_records),
        "layers_real": len(all_records) - len(interim),
        "layers_interim": len(interim),
        "records": all_records,
    }
    (out_dir / "_provenance.json").write_text(json.dumps(prov, indent=2))
    lines = ["| panel | layer | z | provenance | bytes | asset |", "|---|---|---|---|---|---|"]
    for r in all_records:
        lines.append(f"| {r['panel_id']} | {r['layer_class']} | {r['z']} | "
                     f"**{r['provenance']}** | {r['bytes']:,} | {r['asset']} |")
    (out_dir / "_provenance.md").write_text("\n".join(lines) + "\n")

    if gate_reports:
        (out_dir / "gate_report.json").write_text(json.dumps({
            "manifest": str(manifest_path),
            "panels": gate_reports,
        }, indent=2))

    result: dict[str, Any] = {"panels": [str(p) for p in panel_paths], "provenance": prov}
    if gate_reports:
        result["gate_report"] = gate_reports
    if strip:
        strip_path = out_dir / f"{manifest.get('manifest_id', manifest_path.stem)}_strip.jpg"
        render_strip(panel_paths, strip_path)
        result["strip"] = str(strip_path)
        print(f"  strip: {strip_path} ({strip_path.stat().st_size:,} bytes)")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--strip", action="store_true", help="also emit a vertical strip")
    ap.add_argument("--bubbles", action="store_true",
                    help="lettering pass via phoenix_v4 bubble_render")
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--dry-run", action="store_true",
                    help="validate manifest only; no PIL work")
    args = ap.parse_args(argv)
    run(args.manifest, args.out_dir, strip=args.strip, bubbles=args.bubbles,
        locale=args.locale, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
