#!/usr/bin/env python3
"""Generate deterministic four-panel V5 structural assembly proof packet.

The packet is intentionally simple QA art: it proves assembly mechanics,
support-zone contracts, and L2/L3 separation through assemble_from_bank.py.
It does not claim final production visual quality.
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

ROOT = REPO / "artifacts" / "qa" / "pearl_star_v5_structural_assembly_multi_proof_2026-07-13"
CANVAS = (1024, 1024)


def _repo_rel(path: Path) -> str:
    return str(path.resolve().relative_to(REPO))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _draw_room_plate(path: Path, *, support_zones: list[dict[str, Any]], variant: str) -> None:
    w, h = CANVAS
    img = Image.new("RGBA", CANVAS, "#f8eddc")
    d = ImageDraw.Draw(img, "RGBA")
    floor_y = 664 if variant != "seated" else 585
    d.rectangle([0, 0, w, floor_y], fill=(249, 240, 224, 255))
    d.polygon([(0, floor_y), (w, floor_y - 36), (w, h), (0, h)], fill=(226, 199, 160, 255))
    d.line([(0, floor_y), (w, floor_y - 36)], fill=(145, 112, 78, 120), width=3)
    for i in range(-120, w + 160, 130):
        d.line([(i, h), (i + 215, floor_y - 20)], fill=(145, 112, 78, 45), width=2)
    for y in range(floor_y + 90, h, 112):
        d.line([(0, y), (w, y - 28)], fill=(145, 112, 78, 36), width=2)

    if variant == "seated":
        d.rectangle([350, 615, 710, 740], fill=(147, 103, 67, 255), outline=(87, 58, 37, 180), width=4)
        d.rectangle([420, 700, 475, 855], fill=(106, 72, 48, 255))
        d.rectangle([585, 700, 640, 855], fill=(106, 72, 48, 255))
        d.rectangle([450, 520, 615, 630], fill=(132, 91, 58, 255), outline=(87, 58, 37, 180), width=4)
    else:
        d.rectangle([700, 735, 920, 930], fill=(185, 208, 178, 255), outline=(106, 130, 99, 150), width=3)
        d.ellipse([650, 500, 742, 592], fill=(83, 126, 76, 225))
        d.ellipse([700, 552, 804, 650], fill=(70, 117, 69, 225))
        d.rectangle([694, 648, 742, 710], fill=(146, 88, 48, 255), outline=(90, 58, 36, 150), width=2)

    if variant == "medium":
        d.rectangle([86, 142, 308, 330], fill=(225, 240, 237, 255), outline=(123, 145, 138, 160), width=4)
        d.line([(197, 142), (197, 330)], fill=(123, 145, 138, 110), width=3)
    else:
        d.rectangle([672, 118, 946, 350], fill=(225, 240, 237, 255), outline=(123, 145, 138, 160), width=4)
        d.line([(809, 118), (809, 350)], fill=(123, 145, 138, 110), width=3)
        d.line([(672, 234), (946, 234)], fill=(123, 145, 138, 110), width=3)

    # Visualize declared zones subtly for QA without covering furniture.
    for zone in support_zones:
        poly = zone.get("polygon_pct") or []
        if not poly and zone.get("bbox_pct"):
            x, y, zw, zh = zone["bbox_pct"]
            poly = [[x, y], [x + zw, y], [x + zw, y + zh], [x, y + zh]]
        pts = [(int(x / 100 * w), int(y / 100 * h)) for x, y in poly]
        if len(pts) >= 3:
            outline = (90, 170, 95, 120) if zone.get("allows_character_support") else (210, 80, 60, 150)
            d.line([*pts, pts[0]], fill=outline, width=3)
    img = img.filter(ImageFilter.SMOOTH_MORE)
    img.save(path)


def _draw_standing_l2(path: Path, *, scale: float = 1.0) -> None:
    img = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx = 512
    top = int(150 + (1.0 - scale) * 90)
    head_r = int(52 * scale)
    body_w = int(120 * scale)
    body_h = int(260 * scale)
    leg_h = int(250 * scale)
    y_head = top + head_r
    d.ellipse([cx - head_r, top, cx + head_r, top + 2 * head_r], fill=(248, 222, 200, 255), outline=(56, 43, 38, 255), width=4)
    d.pieslice([cx - head_r - 10, top - 8, cx + head_r + 10, top + 2 * head_r + 20], 180, 360, fill=(43, 34, 32, 255))
    body_top = y_head + head_r - 5
    body_bottom = body_top + body_h
    d.rounded_rectangle([cx - body_w // 2, body_top, cx + body_w // 2, body_bottom], radius=34, fill=(250, 244, 225, 255), outline=(70, 61, 52, 255), width=4)
    d.line([(cx - body_w // 2, body_top + 70), (cx - body_w, body_top + 210)], fill=(250, 244, 225, 255), width=int(34 * scale))
    d.line([(cx + body_w // 2, body_top + 70), (cx + body_w, body_top + 210)], fill=(250, 244, 225, 255), width=int(34 * scale))
    for off in (-32, 32):
        d.rounded_rectangle([cx + off - 17, body_bottom - 5, cx + off + 17, body_bottom + leg_h], radius=16, fill=(248, 248, 242, 255), outline=(93, 82, 72, 220), width=3)
        d.ellipse([cx + off - 27, body_bottom + leg_h - 8, cx + off + 27, body_bottom + leg_h + 28], fill=(248, 238, 226, 255), outline=(93, 82, 72, 220), width=3)
    img.save(path)


def _draw_seated_l2(path: Path) -> None:
    img = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    cx = 512
    d.ellipse([450, 180, 574, 304], fill=(248, 222, 200, 255), outline=(56, 43, 38, 255), width=4)
    d.pieslice([436, 160, 588, 318], 180, 360, fill=(43, 34, 32, 255))
    d.rounded_rectangle([430, 300, 594, 540], radius=36, fill=(250, 244, 225, 255), outline=(70, 61, 52, 255), width=4)
    d.rounded_rectangle([388, 520, 636, 640], radius=44, fill=(246, 226, 210, 255), outline=(93, 82, 72, 220), width=4)
    d.line([(430, 390), (355, 528)], fill=(250, 244, 225, 255), width=34)
    d.line([(594, 390), (669, 528)], fill=(250, 244, 225, 255), width=34)
    d.rounded_rectangle([445, 615, 492, 790], radius=18, fill=(248, 248, 242, 255), outline=(93, 82, 72, 220), width=3)
    d.rounded_rectangle([532, 615, 579, 790], radius=18, fill=(248, 248, 242, 255), outline=(93, 82, 72, 220), width=3)
    img.save(path)


def _draw_l3_prop(path: Path) -> None:
    img = Image.new("RGBA", CANVAS, (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle([400, 400, 620, 560], radius=40, fill=(120, 165, 220, 255), outline=(50, 80, 130, 255), width=8)
    d.ellipse([452, 438, 488, 474], fill=(255, 255, 255, 230))
    d.ellipse([532, 438, 568, 474], fill=(255, 255, 255, 230))
    img.save(path)


def _alpha_anchor(path: Path) -> dict[str, float]:
    with Image.open(path) as im:
        tight = alpha_tight_bbox(im.convert("RGBA"))
    if tight is None:
        raise RuntimeError(f"no alpha bbox: {path}")
    left, top, right, bottom = tight
    return {"top": top, "bottom": bottom, "height": bottom - top, "anchor_y_px": bottom}


def _write_sidecars(panel_dir: Path, *, support_zones: list[dict[str, Any]]) -> None:
    src = panel_dir / "source_v5_panel"
    alpha = _alpha_anchor(src / "layer_02.png")
    (src / "layer_01.composition.json").write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": f"{panel_dir.name}_l0_support_plate",
        "layer_class": "L0",
        "bg_class": "full_render",
        "light": {"azimuth": "ambient"},
        "camera": {"angle_bucket": "eye_level", "eye_level_y_pct": 42, "camera_height": "standing"},
        "anchor_slots": [],
        "support_zones": support_zones,
    }, indent=2) + "\n", encoding="utf-8")
    (src / "layer_02.composition.json").write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": f"{panel_dir.name}_l2_clean_subject",
        "layer_class": "L2",
        "crop_class": "full_figure",
        "room_capable": True,
        "abstract_stage_eligible": False,
        "scene_contamination": False,
        "light": {"azimuth": "ambient"},
        "implied_camera": {"angle_bucket": "eye_level"},
        "anchor": {"point": "feet", "y_px": alpha["anchor_y_px"]},
        "eye_y_px": alpha["top"] + alpha["height"] * 0.2,
        "figure_height_m": 1.62,
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
            "provenance_note": "Deterministic support-zone proof plate.",
        },
        {
            "layer_class": "L2",
            "asset": f"{panel_id}/source_v5_panel/layer_02.png",
            "provenance": "REAL",
            "provenance_note": "Clean single-subject structural proof L2.",
            "structural_node_id": "char",
            "grounding": spec["grounding"],
        },
    ]
    if spec.get("l3"):
        layers.append({
            "layer_class": "L3",
            "asset": f"{panel_id}/source_v5_panel/layer_03.png",
            "bbox_pct": [72, 18, 14, 14],
            "provenance": "INTERIM",
            "provenance_note": "Separate prop layer proving L3 does not contaminate L2 quality.",
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
        prop = Image.open(src / "layer_03.png").convert("RGBA").resize((170, 170), Image.LANCZOS)
        bg.alpha_composite(prop, (700, 200))
    bg.save(src / "layer_00.png")
    bg.save(src / "composite.png")


def _panel_specs() -> list[dict[str, Any]]:
    floor = {
        "zone_id": "clear_floor",
        "kind": "floor",
        "polygon_pct": [[0, 65], [100, 65], [100, 100], [0, 100]],
        "occupancy": "clear",
        "allows_character_support": True,
        "allowed_structural_templates": ["standing_room_scene"],
        "priority": 0,
    }
    return [
        {
            "panel_id": "p01_standing_wide_clear_floor",
            "shot_type": "establishing",
            "variant": "wide",
            "support_zones": [floor],
            "plan": dict(
                structural_template_id="standing_room_scene",
                panel_type_id="establish_standing_room",
                relation="standing_on",
                support_role="floor",
                support_polygon_pct=[[0, 65], [100, 65], [100, 100], [0, 100]],
                tx_pct=14,
                ty_pct=85,
                scale=0.45,
            ),
            "grounding": {"contact_shadow": True, "occluder": False, "support_mode": "standing_floor"},
            "l2": "standing",
        },
        {
            "panel_id": "p02_standing_medium_clear_floor",
            "shot_type": "medium",
            "variant": "medium",
            "support_zones": [floor],
            "plan": dict(
                structural_template_id="standing_room_scene",
                panel_type_id="action_standing_room",
                relation="standing_on",
                support_role="floor",
                support_polygon_pct=[[0, 65], [100, 65], [100, 100], [0, 100]],
                tx_pct=48,
                ty_pct=88,
                scale=0.78,
            ),
            "grounding": {"contact_shadow": True, "occluder": False, "support_mode": "standing_floor"},
            "l2": "standing",
        },
        {
            "panel_id": "p03_seated_table_intentional_support",
            "shot_type": "medium",
            "variant": "seated",
            "support_zones": [{
                "zone_id": "seat_table_support",
                "kind": "seat_table",
                "bbox_pct": [34, 56, 36, 23],
                "occupancy": "intentional_support",
                "allows_character_support": True,
                "allowed_structural_templates": ["seated_table_scene"],
                "priority": 10,
            }],
            "plan": dict(
                structural_template_id="seated_table_scene",
                panel_type_id="dialogue_seated_table",
                relation="seated_on",
                support_role="seat_or_table",
                support_polygon_pct=[[34, 56], [70, 56], [70, 79], [34, 79]],
                tx_pct=52,
                ty_pct=68,
                scale=0.7,
            ),
            "grounding": {
                "contact_shadow": True,
                "occluder": False,
                "support_mode": "intentional_seat_table",
            },
            "l2": "seated",
        },
        {
            "panel_id": "p04_standing_l3_prop_separate",
            "shot_type": "establishing",
            "variant": "wide",
            "support_zones": [floor],
            "plan": dict(
                structural_template_id="standing_room_scene",
                panel_type_id="establish_standing_room",
                relation="standing_on",
                support_role="floor",
                support_polygon_pct=[[0, 65], [100, 65], [100, 100], [0, 100]],
                tx_pct=25,
                ty_pct=86,
                scale=0.55,
            ),
            "grounding": {"contact_shadow": True, "occluder": False, "support_mode": "standing_floor"},
            "l2": "standing",
            "l3": True,
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
        _draw_room_plate(src / "layer_01.png", support_zones=spec["support_zones"], variant=spec["variant"])
        if spec["l2"] == "seated":
            _draw_seated_l2(src / "layer_02.png")
        else:
            _draw_standing_l2(src / "layer_02.png", scale=1.0)
        if spec.get("l3"):
            _draw_l3_prop(src / "layer_03.png")
        _build_model_composite(src)
        _write_sidecars(panel_dir, support_zones=spec["support_zones"])

        plan = _plan(panel_id=spec["panel_id"], **spec["plan"])
        (panel_dir / "structural_plan.json").write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        (src / "_telemetry.json").write_text(json.dumps({
            "panel_id": spec["panel_id"],
            "layer_type_used": "L2",
            "layer_roles": {
                "layer_00.png": "model_composite",
                "layer_01.png": "support_zone_background",
                "layer_02.png": "clean_foreground_subject",
                **({"layer_03.png": "separate_L3_prop"} if spec.get("l3") else {}),
            },
            "structural_template_id": spec["plan"]["structural_template_id"],
            "support_zone_contract": spec["support_zones"],
        }, indent=2) + "\n", encoding="utf-8")
        manifest_panels.append(_panel_manifest_entry(spec))

    manifest = {
        "schema_version": "1.0.0",
        "series_id": "pearl_star_v5_structural_multi_proof",
        "episode_id": "ep_001",
        "manifest_id": "pearl_star_v5_structural_multi_proof_2026_07_13",
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
        closeout = {
            "manga-v5-structural-multi-proof-panel": "completed",
            "panel_id": spec["panel_id"],
            "structural_template_id": spec["plan"]["structural_template_id"],
            "panel_type_id": spec["plan"]["panel_type_id"],
            "source_v5_panel_dir": _repo_rel(src),
            "manifest": _repo_rel(manifest_path),
            "structural_plan": _repo_rel(panel_dir / "structural_plan.json"),
            "final_composite": _repo_rel(final_path),
            "gate_report": _repo_rel(panel_dir / "gate_report.json"),
            "required_gates": ["L2_QUALITY", "L0_SUPPORT_ZONE"],
            "gate_passed": gate_report["passed"],
            "final_differs_from_model_layer_00": final_differs,
            "final_sha256": _sha256(final_path),
            "model_layer_00_sha256": _sha256(src / "layer_00.png"),
        }
        (panel_dir / "STRUCTURAL_ASSEMBLY_PROOF.json").write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
        panel_results.append(closeout)

    summary = {
        "manga-v5-structural-multi-proof": "completed",
        "root": _repo_rel(ROOT),
        "panel_count": len(panel_results),
        "panels": panel_results,
        "all_gate_passed": all(p["gate_passed"] for p in panel_results),
        "all_final_differs_from_layer_00": all(p["final_differs_from_model_layer_00"] for p in panel_results),
        "honest_limitations": [
            "Deterministic QA visuals only; not final production art.",
            "Does not claim manga 100% green.",
        ],
    }
    (ROOT / "MANGA_V5_MULTI_PROOF_CLOSEOUT.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    (ROOT / "MANGA_V5_MULTI_PROOF_CLOSEOUT.md").write_text(
        "# Manga V5 Structural Multi Proof Closeout\n\n"
        f"- status: completed\n- panels: {len(panel_results)}\n"
        f"- all gates passed: {summary['all_gate_passed']}\n"
        f"- all finals differ from layer_00: {summary['all_final_differs_from_layer_00']}\n\n"
        "These are deterministic structural QA visuals, not final manga art.\n",
        encoding="utf-8",
    )
    return summary


def main() -> int:
    summary = build_packet()
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
