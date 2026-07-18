#!/usr/bin/env python3
"""Generate a deterministic mecha clean-layer structural proof packet.

The packet proves clean L0/L2/L3 mecha contracts through assemble_from_bank.py.
It is structural QA art, not final Pearl Star production art.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml
from PIL import Image, ImageDraw, ImageFilter

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_from_bank as afb  # noqa: E402
import structural_composition as sc  # noqa: E402
from composition_grammar import alpha_tight_bbox  # noqa: E402
from mecha_clean_structural_layer import CONTRACT_ID  # noqa: E402

ROOT = REPO / "artifacts" / "qa" / "pearl_star_mecha_clean_structural_proof_2026-07-13"
CANVAS = (1024, 1024)


def _repo_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _l0_contract() -> dict[str, Any]:
    return {
        "id": CONTRACT_ID,
        "status": "clean",
        "role": "environment_support",
        "subject": "environment",
        "contains_primary_subject": False,
        "contains_foreground_subject": False,
        "contains_pilot": False,
        "contains": [],
    }


def _l2_contract(subject: str) -> dict[str, Any]:
    return {
        "id": CONTRACT_ID,
        "status": "clean",
        "role": "single_subject_cutout",
        "subject": subject,
        "contains_background": False,
        "contains_environment": False,
        "contains": [subject],
        "background_context": [],
    }


def _l3_contract(subject: str = "telemetry") -> dict[str, Any]:
    return {
        "id": CONTRACT_ID,
        "status": "clean",
        "role": "isolated_object",
        "subject": subject,
        "contains": [subject],
    }


def _draw_hangar_plate(
    path: Path,
    *,
    variant: str,
    support_zones: list[dict[str, Any]],
) -> None:
    w, h = CANVAS
    img = Image.new("RGBA", CANVAS, "#101723")
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([0, 0, w, h], fill=(16, 23, 35, 255))
    d.rectangle([0, 0, w, 610], fill=(21, 30, 45, 255))
    for x in range(80, w, 170):
        d.line([(x, 0), (x - 120, 630)], fill=(88, 116, 138, 70), width=7)
    for y in range(80, 620, 120):
        d.line([(0, y), (w, y + 30)], fill=(80, 98, 116, 55), width=4)
    d.polygon([(0, 610), (w, 560), (w, h), (0, h)], fill=(44, 52, 63, 255))
    d.line([(0, 610), (w, 560)], fill=(128, 161, 174, 140), width=4)
    for x in range(-180, w + 200, 140):
        d.line([(x, h), (x + 290, 575)], fill=(100, 126, 138, 58), width=3)
    for y in range(700, h, 95):
        d.line([(0, y), (w, y - 45)], fill=(100, 126, 138, 48), width=3)

    if variant == "threshold":
        d.rectangle([760, 120, 930, 530], fill=(51, 67, 83, 255), outline=(143, 183, 196, 150), width=5)
        d.rectangle([792, 180, 898, 478], fill=(108, 152, 170, 120))
    elif variant == "seat":
        d.rounded_rectangle([338, 580, 706, 765], radius=48, fill=(48, 65, 84, 255), outline=(143, 183, 196, 150), width=6)
        d.rectangle([410, 710, 470, 905], fill=(35, 47, 62, 255))
        d.rectangle([574, 710, 634, 905], fill=(35, 47, 62, 255))
        d.rounded_rectangle([430, 430, 614, 625], radius=48, fill=(62, 80, 100, 255), outline=(143, 183, 196, 150), width=6)
    else:
        d.rectangle([700, 700, 940, 920], fill=(51, 67, 83, 255), outline=(143, 183, 196, 150), width=4)

    for zone in support_zones:
        poly = zone.get("polygon_pct") or []
        if not poly and zone.get("bbox_pct"):
            x, y, zw, zh = zone["bbox_pct"]
            poly = [[x, y], [x + zw, y], [x + zw, y + zh], [x, y + zh]]
        pts = [(int(x / 100 * w), int(y / 100 * h)) for x, y in poly]
        if len(pts) >= 3:
            d.line([*pts, pts[0]], fill=(80, 220, 190, 155), width=4)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(path)


def _draw_mecha_l2(path: Path) -> None:
    img = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx = 512
    d.polygon([(cx, 122), (610, 260), (575, 395), (449, 395), (414, 260)], fill=(202, 218, 226, 255), outline=(20, 28, 38, 255))
    d.rectangle([452, 300, 572, 595], fill=(170, 194, 208, 255), outline=(20, 28, 38, 255), width=8)
    d.rectangle([384, 355, 448, 650], fill=(120, 148, 168, 255), outline=(20, 28, 38, 255), width=7)
    d.rectangle([576, 355, 640, 650], fill=(120, 148, 168, 255), outline=(20, 28, 38, 255), width=7)
    d.rectangle([438, 585, 500, 860], fill=(118, 143, 166, 255), outline=(20, 28, 38, 255), width=7)
    d.rectangle([524, 585, 586, 860], fill=(118, 143, 166, 255), outline=(20, 28, 38, 255), width=7)
    d.rectangle([414, 840, 510, 895], fill=(88, 112, 136, 255), outline=(20, 28, 38, 255), width=6)
    d.rectangle([516, 840, 612, 895], fill=(88, 112, 136, 255), outline=(20, 28, 38, 255), width=6)
    d.rectangle([475, 238, 549, 292], fill=(96, 190, 210, 240), outline=(20, 28, 38, 255), width=5)
    img.save(path)


def _draw_pilot_l2(path: Path, *, seated: bool = False) -> None:
    img = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx = 512
    if seated:
        d.ellipse([450, 178, 574, 302], fill=(237, 210, 188, 255), outline=(25, 25, 30, 255), width=5)
        d.pieslice([438, 154, 586, 315], 180, 360, fill=(36, 32, 36, 255))
        d.rectangle([488, 286, 536, 322], fill=(237, 210, 188, 255))
        d.rounded_rectangle([425, 300, 599, 530], radius=34, fill=(238, 246, 244, 255), outline=(25, 25, 30, 255), width=5)
        d.rounded_rectangle([390, 515, 635, 642], radius=42, fill=(72, 94, 112, 255), outline=(25, 25, 30, 255), width=5)
        d.rectangle([444, 610, 580, 645], fill=(72, 94, 112, 255))
        d.line([(430, 380), (350, 535)], fill=(238, 246, 244, 255), width=34)
        d.line([(594, 380), (674, 535)], fill=(238, 246, 244, 255), width=34)
        d.rounded_rectangle([444, 625, 492, 790], radius=18, fill=(238, 246, 244, 255), outline=(25, 25, 30, 255), width=4)
        d.rounded_rectangle([532, 625, 580, 790], radius=18, fill=(238, 246, 244, 255), outline=(25, 25, 30, 255), width=4)
    else:
        d.ellipse([456, 122, 568, 234], fill=(237, 210, 188, 255), outline=(25, 25, 30, 255), width=5)
        d.pieslice([444, 106, 580, 250], 180, 360, fill=(36, 32, 36, 255))
        d.rectangle([488, 220, 536, 255], fill=(237, 210, 188, 255))
        d.rounded_rectangle([438, 238, 586, 515], radius=36, fill=(238, 246, 244, 255), outline=(25, 25, 30, 255), width=5)
        d.rectangle([454, 500, 570, 535], fill=(238, 246, 244, 255))
        d.line([(438, 318), (355, 490)], fill=(238, 246, 244, 255), width=34)
        d.line([(586, 318), (669, 490)], fill=(238, 246, 244, 255), width=34)
        d.rounded_rectangle([454, 505, 500, 825], radius=18, fill=(238, 246, 244, 255), outline=(25, 25, 30, 255), width=4)
        d.rounded_rectangle([524, 505, 570, 825], radius=18, fill=(238, 246, 244, 255), outline=(25, 25, 30, 255), width=4)
        d.ellipse([426, 802, 510, 850], fill=(64, 74, 86, 255), outline=(25, 25, 30, 255), width=4)
        d.ellipse([514, 802, 598, 850], fill=(64, 74, 86, 255), outline=(25, 25, 30, 255), width=4)
    img.save(path)


def _draw_l3_telemetry(path: Path) -> None:
    img = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([388, 410, 636, 560], radius=28, fill=(84, 218, 226, 230), outline=(22, 76, 92, 255), width=8)
    d.line([(430, 500), (472, 455), (516, 505), (592, 440)], fill=(255, 255, 255, 235), width=8)
    d.rectangle([430, 530, 590, 540], fill=(255, 255, 255, 180))
    img.save(path)


def _alpha_anchor(path: Path) -> dict[str, float]:
    with Image.open(path) as im:
        tight = alpha_tight_bbox(im.convert("RGBA"))
    if tight is None:
        raise RuntimeError(f"no alpha bbox: {path}")
    left, top, right, bottom = tight
    return {"top": top, "bottom": bottom, "height": bottom - top, "anchor_y_px": bottom}


def _write_sidecars(
    panel_dir: Path,
    *,
    support_zones: list[dict[str, Any]],
    subject: str,
    seated: bool,
    has_l3: bool,
) -> None:
    src = panel_dir / "source_v5_panel"
    alpha = _alpha_anchor(src / "layer_02.png")
    (src / "layer_01.composition.json").write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": f"{panel_dir.name}_l0_empty_hangar_support",
        "layer_class": "L0",
        "genre": "mecha",
        "style_register": "mecha_hangar",
        "bg_class": "full_render",
        "light": {"azimuth": "ambient"},
        "camera": {"angle_bucket": "eye_level", "eye_level_y_pct": 42, "camera_height": "standing"},
        "anchor_slots": [],
        "support_zones": support_zones,
        "structural_layer_contract": _l0_contract(),
    }, indent=2) + "\n", encoding="utf-8")
    (src / "layer_02.composition.json").write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": f"{panel_dir.name}_l2_clean_{subject}",
        "layer_class": "L2",
        "genre": "mecha",
        "style_register": f"mecha_{subject}",
        "crop_class": "full_figure",
        "room_capable": True,
        "abstract_stage_eligible": False,
        "scene_contamination": False,
        "light": {"azimuth": "ambient"},
        "implied_camera": {"angle_bucket": "eye_level"},
        "anchor": {"point": "feet", "y_px": alpha["anchor_y_px"]},
        "eye_y_px": alpha["top"] + alpha["height"] * (0.18 if subject == "mecha" else 0.2),
        "figure_height_m": 5.8 if subject == "mecha" else 1.62,
        "pose_context": "seated" if seated else "standing",
        "structural_layer_contract": _l2_contract(subject),
    }, indent=2) + "\n", encoding="utf-8")
    if has_l3:
        (src / "layer_03.composition.json").write_text(json.dumps({
            "schema_version": "1.0.0",
            "asset_id": f"{panel_dir.name}_l3_telemetry",
            "layer_class": "L3",
            "genre": "mecha",
            "style_register": "mecha_telemetry",
            "crop_class": "object_macro",
            "structural_layer_contract": _l3_contract("telemetry"),
        }, indent=2) + "\n", encoding="utf-8")


def _plan(
    *,
    panel_id: str,
    structural_template_id: str,
    panel_type_id: str,
    relation: str,
    support_role: str,
    support_polygon_pct: list[list[float]],
    tx_pct: float,
    ty_pct: float,
    scale: float,
) -> dict[str, Any]:
    body = {
        "panel_id": panel_id,
        "canvas": {"width": CANVAS[0], "height": CANVAS[1]},
        "structural_template_id": structural_template_id,
        "panel_type_id": panel_type_id,
        "required_support_proof": [relation],
        "allowed_relations": sorted({relation, "standing_on", "seated_on", "resting_on", "held_by", "occluded_by"}),
        "support_graph": {
            "nodes": [
                {
                    "node_id": "support",
                    "category": "support_surface",
                    "role": support_role,
                    "support_polygon_pct": support_polygon_pct,
                },
                {
                    "node_id": "char",
                    "category": "character",
                    "role": "primary_subject",
                    "contact_point_pct": [0.0, 0.0],
                },
            ],
            "edges": [{
                "edge_id": "e_support",
                "relation": relation,
                "from_node": "char",
                "to_node": "support",
            }],
        },
        "resolved_placements": [{
            "node_id": "char",
            "transform": {
                "tx_pct": tx_pct,
                "ty_pct": ty_pct,
                "uniform_scale": scale,
                "rotation_deg": 0.0,
                "transform_model": sc.TRANSFORM_MODEL,
            },
        }],
        "transform_model": sc.TRANSFORM_MODEL,
    }
    envelope = {
        "schema_version": "1.0.0",
        "envelope_id": f"plan_{panel_id}",
        "transform_model": sc.TRANSFORM_MODEL,
        "structural_template_id": structural_template_id,
        "panel_type_id": panel_type_id,
        "plan_body": body,
        "plan_hash": sc.compute_plan_hash(body),
        "validation": {"status": "pass", "failures": []},
    }
    sc.verify_plan_hash(envelope)
    sc.render_from_verified_plan(envelope, require_hash=True)
    return envelope


def _panel_manifest_entry(spec: dict[str, Any]) -> dict[str, Any]:
    panel_id = spec["panel_id"]
    layers: list[dict[str, Any]] = [
        {
            "layer_class": "L0",
            "asset": f"{panel_id}/source_v5_panel/layer_01.png",
            "provenance": "REAL",
            "provenance_note": "Deterministic clean mecha support plate.",
        },
        {
            "layer_class": "L2",
            "asset": f"{panel_id}/source_v5_panel/layer_02.png",
            "provenance": "REAL",
            "provenance_note": f"Clean single-subject mecha L2: {spec['subject']}.",
            "structural_node_id": "char",
            "grounding": spec["grounding"],
        },
    ]
    if spec.get("l3"):
        layers.append({
            "layer_class": "L3",
            "asset": f"{panel_id}/source_v5_panel/layer_03.png",
            "bbox_pct": [70, 16, 18, 12],
            "provenance": "INTERIM",
            "provenance_note": "Clean isolated telemetry prop proving L3 purity gate.",
        })
    return {
        "panel_id": panel_id,
        "shot_type": spec["shot_type"],
        "structural_plan_path": f"{panel_id}/structural_plan.json",
        "layers": layers,
    }


def _build_model_composite(src: Path) -> None:
    bg = Image.open(src / "layer_01.png").convert("RGBA")
    l2 = Image.open(src / "layer_02.png").convert("RGBA").resize((620, 620), Image.LANCZOS)
    bg.alpha_composite(l2, (202, 300))
    if (src / "layer_03.png").is_file():
        prop = Image.open(src / "layer_03.png").convert("RGBA").resize((190, 190), Image.LANCZOS)
        bg.alpha_composite(prop, (700, 170))
    bg.save(src / "layer_00.png")
    bg.save(src / "composite.png")


def _panel_specs() -> list[dict[str, Any]]:
    floor = {
        "zone_id": "clear_hangar_floor",
        "kind": "floor",
        "polygon_pct": [[0, 62], [100, 56], [100, 100], [0, 100]],
        "occupancy": "clear",
        "allows_character_support": True,
        "allowed_structural_templates": ["standing_room_scene"],
        "priority": 0,
    }
    seat = {
        "zone_id": "cockpit_seat_support",
        "kind": "seat_table",
        "bbox_pct": [34, 55, 35, 22],
        "occupancy": "intentional_support",
        "allows_character_support": True,
        "allowed_structural_templates": ["seated_table_scene"],
        "priority": 10,
    }
    return [
        {
            "panel_id": "p01_clean_mecha_hangar_floor",
            "shot_type": "establishing",
            "variant": "hangar",
            "support_zones": [floor],
            "subject": "mecha",
            "l2": "mecha",
            "plan": dict(
                structural_template_id="standing_room_scene",
                panel_type_id="establish_standing_room",
                relation="standing_on",
                support_role="floor",
                support_polygon_pct=[[0, 62], [100, 56], [100, 100], [0, 100]],
                tx_pct=48,
                ty_pct=86,
                scale=0.56,
            ),
            "grounding": {"contact_shadow": True, "occluder": False, "support_mode": "standing_floor"},
        },
        {
            "panel_id": "p02_clean_pilot_threshold_floor_l3",
            "shot_type": "medium",
            "variant": "threshold",
            "support_zones": [floor],
            "subject": "pilot",
            "l2": "pilot",
            "l3": True,
            "plan": dict(
                structural_template_id="standing_room_scene",
                panel_type_id="action_standing_room",
                relation="standing_on",
                support_role="floor",
                support_polygon_pct=[[0, 62], [100, 56], [100, 100], [0, 100]],
                tx_pct=42,
                ty_pct=85,
                scale=0.68,
            ),
            "grounding": {"contact_shadow": True, "occluder": False, "support_mode": "standing_floor"},
        },
        {
            "panel_id": "p03_clean_seated_pilot_cockpit_seat",
            "shot_type": "medium",
            "variant": "seat",
            "support_zones": [seat],
            "subject": "pilot",
            "l2": "pilot_seated",
            "plan": dict(
                structural_template_id="seated_table_scene",
                panel_type_id="dialogue_seated_table",
                relation="seated_on",
                support_role="seat_or_table",
                support_polygon_pct=[[34, 55], [69, 55], [69, 77], [34, 77]],
                tx_pct=52,
                ty_pct=68,
                scale=0.72,
            ),
            "grounding": {
                "contact_shadow": True,
                "occluder": False,
                "support_mode": "intentional_seat_table",
            },
        },
    ]


def build_packet() -> dict[str, Any]:
    if ROOT.exists():
        shutil.rmtree(ROOT)
    ROOT.mkdir(parents=True, exist_ok=True)
    specs = _panel_specs()
    manifest_panels: list[dict[str, Any]] = []
    panel_results: list[dict[str, Any]] = []
    for spec in specs:
        panel_dir = ROOT / spec["panel_id"]
        src = panel_dir / "source_v5_panel"
        src.mkdir(parents=True, exist_ok=True)
        _draw_hangar_plate(src / "layer_01.png", variant=spec["variant"], support_zones=spec["support_zones"])
        if spec["l2"] == "mecha":
            _draw_mecha_l2(src / "layer_02.png")
        else:
            _draw_pilot_l2(src / "layer_02.png", seated=spec["l2"] == "pilot_seated")
        if spec.get("l3"):
            _draw_l3_telemetry(src / "layer_03.png")
        _build_model_composite(src)
        _write_sidecars(
            panel_dir,
            support_zones=spec["support_zones"],
            subject=spec["subject"],
            seated=spec["l2"] == "pilot_seated",
            has_l3=bool(spec.get("l3")),
        )

        plan = _plan(panel_id=spec["panel_id"], **spec["plan"])
        (panel_dir / "structural_plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        (src / "_telemetry.json").write_text(json.dumps({
            "panel_id": spec["panel_id"],
            "genre_id": "mecha",
            "layer_type_used": "L2",
            "mecha_layer_contract": CONTRACT_ID,
            "layer_roles": {
                "layer_00.png": "model_composite",
                "layer_01.png": "clean_empty_support_plate",
                "layer_02.png": f"clean_single_{spec['subject']}",
                **({"layer_03.png": "clean_isolated_telemetry_prop"} if spec.get("l3") else {}),
            },
            "structural_template_id": spec["plan"]["structural_template_id"],
            "support_zone_contract": spec["support_zones"],
        }, indent=2) + "\n", encoding="utf-8")
        manifest_panels.append(_panel_manifest_entry(spec))

    manifest = {
        "schema_version": "1.0.0",
        "series_id": "pearl_star_mecha_clean_structural_proof",
        "episode_id": "ep_001",
        "manifest_id": "pearl_star_mecha_clean_structural_proof_2026_07_13",
        "canvas": {"width": CANVAS[0], "height": CANVAS[1], "background_hex": "#FFFFFF"},
        "panels": manifest_panels,
    }
    manifest_path = ROOT / "assembly_manifest.yaml"
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    assembly = afb.run(Path(_repo_rel(manifest_path)), ROOT)
    gates_by_panel = {g["panel_id"]: g for g in assembly.get("gate_report", [])}

    for spec in specs:
        panel_dir = ROOT / spec["panel_id"]
        src = panel_dir / "source_v5_panel"
        final_path = ROOT / f"{spec['panel_id']}.png"
        gate_report = gates_by_panel[spec["panel_id"]]
        (panel_dir / "gate_report.json").write_text(json.dumps({
            "manifest": _repo_rel(manifest_path),
            "panel": gate_report,
        }, indent=2) + "\n", encoding="utf-8")
        final_differs = _sha256(final_path) != _sha256(src / "layer_00.png")
        required_gates = ["L0_STRUCTURAL_PURITY", "L2_STRUCTURAL_PURITY", "L2_QUALITY", "L0_SUPPORT_ZONE"]
        if spec.get("l3"):
            required_gates.append("L3_STRUCTURAL_PURITY")
        closeout = {
            "manga-mecha-clean-structural-proof-panel": "completed",
            "panel_id": spec["panel_id"],
            "structural_template_id": spec["plan"]["structural_template_id"],
            "panel_type_id": spec["plan"]["panel_type_id"],
            "subject": spec["subject"],
            "source_v5_panel_dir": _repo_rel(src),
            "manifest": _repo_rel(manifest_path),
            "structural_plan": _repo_rel(panel_dir / "structural_plan.json"),
            "final_composite": _repo_rel(final_path),
            "gate_report": _repo_rel(panel_dir / "gate_report.json"),
            "required_gates": required_gates,
            "actual_gates": [g["gate"] for g in gate_report["gates"]],
            "gate_passed": gate_report["passed"],
            "final_differs_from_model_layer_00": final_differs,
            "final_sha256": _sha256(final_path),
            "model_layer_00_sha256": _sha256(src / "layer_00.png"),
        }
        missing = [gate for gate in required_gates if gate not in closeout["actual_gates"]]
        if missing:
            raise RuntimeError(f"{spec['panel_id']} missing gates: {missing}")
        (panel_dir / "MECHA_CLEAN_STRUCTURAL_PROOF.json").write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
        panel_results.append(closeout)

    summary = {
        "manga-mecha-clean-structural-proof": "completed",
        "contract": CONTRACT_ID,
        "root": _repo_rel(ROOT),
        "panel_count": len(panel_results),
        "panels": panel_results,
        "all_gate_passed": all(p["gate_passed"] for p in panel_results),
        "all_final_differs_from_layer_00": all(p["final_differs_from_model_layer_00"] for p in panel_results),
        "honest_limitations": [
            "Deterministic structural QA visuals only; not final Pearl Star production art.",
            "Does not claim manga 100% green.",
            "Legacy contaminated mecha bank layers are intentionally blocked until regenerated clean.",
        ],
    }
    (ROOT / "MECHA_CLEAN_STRUCTURAL_PROOF_CLOSEOUT.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (ROOT / "MECHA_CLEAN_STRUCTURAL_PROOF_CLOSEOUT.md").write_text(
        "# Mecha Clean Structural Proof Closeout\n\n"
        f"- status: completed\n- contract: {CONTRACT_ID}\n- panels: {len(panel_results)}\n"
        f"- all gates passed: {summary['all_gate_passed']}\n"
        f"- all finals differ from layer_00: {summary['all_final_differs_from_layer_00']}\n\n"
        "This packet proves clean structural-layer mechanics. It is not final manga art and does not claim overall manga green.\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    summary = build_packet()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
