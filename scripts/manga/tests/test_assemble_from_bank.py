"""Tests for assemble_from_bank.py — deterministic bank assembly.

Covers:
    - manifest validation (provenance mandatory, bbox mandatory for cutout
      classes, bad layer_class refused)
    - §10 composite math: tight-crop, min-scale, centered paste
    - z-order: L3 above_L2 vs below_L2 occlusion actually flips pixels
    - L4 screen blend lightens, never darkens
    - determinism: same manifest → byte-identical panel output
    - provenance table written with REAL/INTERIM counts

Run from repo root:
    PYTHONPATH=. python3 -m pytest scripts/manga/tests/test_assemble_from_bank.py -v
"""
from __future__ import annotations

import sys
import json
from pathlib import Path

import pytest
import yaml
from PIL import Image

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import assemble_from_bank as afb  # noqa: E402
import v5_layered_to_structural_manifest as v5_bridge  # noqa: E402


# ── fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture()
def bank(tmp_path: Path) -> dict[str, Path]:
    """Synthetic layer assets: green L0 plate, red L2 square, blue L3 dot."""
    paths = {}
    l0 = Image.new("RGBA", (200, 300), (0, 200, 0, 255))
    paths["l0"] = tmp_path / "l0.png"
    l0.save(paths["l0"])

    l2 = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
    for x in range(20, 80):
        for y in range(20, 80):
            l2.putpixel((x, y), (200, 0, 0, 255))
    paths["l2"] = tmp_path / "l2.png"
    l2.save(paths["l2"])

    l3 = Image.new("RGBA", (60, 60), (0, 0, 0, 0))
    for x in range(10, 50):
        for y in range(10, 50):
            l3.putpixel((x, y), (0, 0, 200, 255))
    paths["l3"] = tmp_path / "l3.png"
    l3.save(paths["l3"])

    l4 = Image.new("RGBA", (200, 300), (80, 80, 80, 120))
    paths["l4"] = tmp_path / "l4.png"
    l4.save(paths["l4"])
    return paths


def _manifest(bank: dict[str, Path], tmp_path: Path, *, l3_z: str = "above_L2",
              with_l4: bool = False) -> Path:
    layers = [
        {"layer_class": "L0", "asset": str(bank["l0"]), "provenance": "REAL"},
        {"layer_class": "L2", "asset": str(bank["l2"]),
         "bbox_pct": [25, 25, 50, 50], "provenance": "REAL"},
        {"layer_class": "L3", "asset": str(bank["l3"]),
         "bbox_pct": [30, 30, 30, 30], "z_order": l3_z, "provenance": "INTERIM",
         "provenance_note": "test sprite"},
    ]
    if with_l4:
        layers.append({"layer_class": "L4", "asset": str(bank["l4"]),
                       "blend": "screen", "provenance": "INTERIM"})
    m = {
        "schema_version": "1.0.0",
        "series_id": "test_series",
        "manifest_id": "t",
        "canvas": {"width": 200, "height": 300, "background_hex": "#FFFFFF"},
        "panels": [{"panel_id": "p1", "shot_type": "establishing", "layers": layers}],
    }
    p = tmp_path / "m.yaml"
    p.write_text(yaml.safe_dump(m))
    return p


def _write_structural_sidecars(
    bank: dict[str, Path],
    *,
    support_zones: list[dict] | None = None,
) -> None:
    l0_meta = {
        "schema_version": "1.0.0",
        "asset_id": "l0_test",
        "layer_class": "L0",
        "light": {"azimuth": "camera_left"},
        "bg_class": "full_render",
        "camera": {"eye_level_y_pct": 40, "camera_height": "standing"},
        "anchor_slots": [],
    }
    if support_zones is not None:
        l0_meta["support_zones"] = support_zones
    (bank["l0"].with_suffix(".composition.json")).write_text(json.dumps(l0_meta))
    (bank["l2"].with_suffix(".composition.json")).write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": "l2_test",
        "layer_class": "L2",
        "light": {"azimuth": "camera_left"},
        "crop_class": "full_figure",
        "anchor": {"point": "feet", "y_px": 80},
        "eye_y_px": 25,
        "figure_height_m": 1.62,
    }))


def _mecha_clean_l0_contract() -> dict:
    return {
        "id": "mecha_clean_structural_layer_v1",
        "status": "clean",
        "role": "environment_support",
        "subject": "environment",
        "contains_primary_subject": False,
        "contains_foreground_subject": False,
        "contains_pilot": False,
        "contains": [],
    }


def _mecha_clean_l2_contract(subject: str = "pilot") -> dict:
    return {
        "id": "mecha_clean_structural_layer_v1",
        "status": "clean",
        "role": "single_subject_cutout",
        "subject": subject,
        "contains_background": False,
        "contains_environment": False,
        "contains": [subject],
        "background_context": [],
    }


def _mecha_clean_l3_contract(subject: str = "telemetry") -> dict:
    return {
        "id": "mecha_clean_structural_layer_v1",
        "status": "clean",
        "role": "isolated_object",
        "subject": subject,
        "contains": [subject],
    }


def _mecha_support_zones() -> list[dict]:
    return [{
        "zone_id": "clear_hangar_floor",
        "kind": "floor",
        "polygon_pct": [[0, 72], [100, 72], [100, 100], [0, 100]],
        "occupancy": "clear",
        "allows_character_support": True,
        "allowed_structural_templates": ["standing_room_scene"],
    }]


def _write_mecha_clean_sidecars(bank: dict[str, Path]) -> None:
    _write_structural_sidecars(bank, support_zones=_mecha_support_zones())
    l0_path = bank["l0"].with_suffix(".composition.json")
    l0_meta = json.loads(l0_path.read_text())
    l0_meta.update({
        "genre": "mecha",
        "style_register": "mecha_hangar",
        "structural_layer_contract": _mecha_clean_l0_contract(),
    })
    l0_path.write_text(json.dumps(l0_meta, indent=2) + "\n")

    l2_path = bank["l2"].with_suffix(".composition.json")
    l2_meta = json.loads(l2_path.read_text())
    l2_meta.update({
        "genre": "mecha",
        "style_register": "mecha_pilot",
        "scene_contamination": False,
        "structural_layer_contract": _mecha_clean_l2_contract("pilot"),
    })
    l2_path.write_text(json.dumps(l2_meta, indent=2) + "\n")

    (bank["l3"].with_suffix(".composition.json")).write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": "l3_mecha_clean_prop",
        "layer_class": "L3",
        "genre": "mecha",
        "style_register": "mecha_prop",
        "crop_class": "object_macro",
        "structural_layer_contract": _mecha_clean_l3_contract("telemetry"),
    }, indent=2) + "\n")


def _structural_plan(
    tmp_path: Path,
    *,
    tx_pct: float = 50.0,
    ty_pct: float = 80.0,
    bad_hash: bool = False,
    structural_template_id: str = "standing_room_scene",
    panel_type_id: str = "establish_standing_room",
    relation: str = "standing_on",
    support_role: str = "floor",
    support_polygon_pct: list[list[float]] | None = None,
) -> Path:
    support_polygon_pct = support_polygon_pct or [[5, 72], [95, 72], [95, 98], [5, 98]]
    allowed_relations = sorted({
        relation,
        "standing_on",
        "seated_on",
        "resting_on",
        "held_by",
        "occluded_by",
    })
    plan = {
        "schema_version": "1.0.0",
        "envelope_id": "plan_p1",
        "transform_model": "structural_mvp_v1",
        "structural_template_id": structural_template_id,
        "panel_type_id": panel_type_id,
        "plan_body": {
            "panel_id": "p1",
            "canvas": {"width": 200, "height": 300},
            "structural_template_id": structural_template_id,
            "panel_type_id": panel_type_id,
            "required_support_proof": [relation],
            "allowed_relations": allowed_relations,
            "support_graph": {
                "nodes": [
                    {
                        "node_id": "floor",
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
                "edges": [
                    {
                        "edge_id": "e1",
                        "relation": relation,
                        "from_node": "char",
                        "to_node": "floor",
                    }
                ],
            },
            "resolved_placements": [
                {
                    "node_id": "char",
                    "transform": {
                        "tx_pct": tx_pct,
                        "ty_pct": ty_pct,
                        "uniform_scale": 1.0,
                        "rotation_deg": 0.0,
                        "transform_model": "structural_mvp_v1",
                    },
                }
            ],
            "transform_model": "structural_mvp_v1",
        },
    }
    import structural_composition as sc
    plan["plan_hash"] = sc.compute_plan_hash(plan["plan_body"])
    if bad_hash:
        plan["plan_hash"] = "0" * 64
    out = tmp_path / f"structural_{int(tx_pct)}.json"
    out.write_text(json.dumps(plan, indent=2))
    return out


def _manifest_structural(
    bank: dict[str, Path],
    tmp_path: Path,
    plan_path: Path,
    *,
    grounding: dict | None = None,
) -> Path:
    grounding = grounding or {"contact_shadow": False, "occluder": False}
    m = {
        "schema_version": "1.0.0",
        "series_id": "test_series",
        "manifest_id": "structural",
        "canvas": {"width": 200, "height": 300, "background_hex": "#FFFFFF"},
        "panels": [{
            "panel_id": "p1",
            "shot_type": "establishing",
            "structural_plan_path": str(plan_path),
            "layers": [
                {"layer_class": "L0", "asset": str(bank["l0"]), "provenance": "REAL"},
                {
                    "layer_class": "L2",
                    "asset": str(bank["l2"]),
                    "provenance": "REAL",
                    "structural_node_id": "char",
                    "grounding": grounding,
                },
            ],
        }],
    }
    p = tmp_path / "structural_manifest.yaml"
    p.write_text(yaml.safe_dump(m))
    return p


def _v5_panel_output(tmp_path: Path) -> Path:
    panel_dir = tmp_path / "v5" / "ep_001" / "ep001_013"
    panel_dir.mkdir(parents=True)

    # Deliberately blue model composite. The structural assembly output should
    # be green background + red character, proving layer_00 is not copied.
    Image.new("RGBA", (200, 300), (0, 0, 200, 255)).save(panel_dir / "layer_00.png")
    Image.new("RGBA", (200, 300), (0, 200, 0, 255)).save(panel_dir / "layer_01.png")

    l2 = Image.new("RGBA", (200, 300), (0, 0, 0, 0))
    for x in range(70, 130):
        for y in range(90, 150):
            l2.putpixel((x, y), (200, 0, 0, 255))
    l2.save(panel_dir / "layer_02.png")

    (panel_dir / "composite.png").write_bytes((panel_dir / "layer_00.png").read_bytes())
    (panel_dir / "_telemetry.json").write_text(json.dumps({
        "panel_id": "ep001_013",
        "archetype": "sparse_establishing_wide",
        "layer_type_used": "L2",
        "layer_roles": {
            "layer_00.png": "model_composite",
            "layer_01.png": "background",
            "layer_02.png": "foreground_component",
        },
        "layer_paths": [
            str(panel_dir / "layer_00.png"),
            str(panel_dir / "layer_01.png"),
            str(panel_dir / "layer_02.png"),
        ],
    }, indent=2))
    return panel_dir


def _mark_v5_panel_mecha(panel_dir: Path) -> None:
    telemetry = json.loads((panel_dir / "_telemetry.json").read_text())
    telemetry["genre_id"] = "mecha"
    (panel_dir / "_telemetry.json").write_text(json.dumps(telemetry, indent=2))


def _write_v5_mecha_sidecars(panel_dir: Path, *, clean: bool = True) -> None:
    l0_contract = _mecha_clean_l0_contract()
    l2_contract = _mecha_clean_l2_contract("pilot")
    l2_contaminated = False
    if not clean:
        l2_contract.update({
            "status": "blocked",
            "contains_background": True,
            "contains_environment": True,
            "contains": ["pilot", "cockpit", "environment"],
            "background_context": ["cockpit", "environment"],
        })
        l2_contaminated = True

    (panel_dir / "layer_01.composition.json").write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": "v5_mecha_l0",
        "layer_class": "L0",
        "genre": "mecha",
        "style_register": "mecha_hangar",
        "bg_class": "full_render",
        "camera": {"eye_level_y_pct": 40, "camera_height": "standing"},
        "light": {"azimuth": "camera_left"},
        "anchor_slots": [],
        "support_zones": _mecha_support_zones(),
        "structural_layer_contract": l0_contract,
    }, indent=2) + "\n")
    (panel_dir / "layer_02.composition.json").write_text(json.dumps({
        "schema_version": "1.0.0",
        "asset_id": "v5_mecha_l2",
        "layer_class": "L2",
        "genre": "mecha",
        "style_register": "mecha_pilot",
        "crop_class": "full_figure",
        "light": {"azimuth": "camera_left"},
        "anchor": {"point": "feet", "y_px": 150},
        "eye_y_px": 96,
        "figure_height_m": 1.62,
        "scene_contamination": l2_contaminated,
        "structural_layer_contract": l2_contract,
    }, indent=2) + "\n")


def _pollute_l2_with_stray_component(panel_dir: Path) -> None:
    """Make layer_02 look like a dirty model foreground: subject + stray prop."""
    l2 = Image.new("RGBA", (200, 300), (0, 0, 0, 0))
    for x in range(70, 130):
        for y in range(80, 180):
            l2.putpixel((x, y), (200, 0, 0, 255))
    for x in range(5, 55):
        for y in range(210, 275):
            l2.putpixel((x, y), (120, 70, 20, 255))
    l2.save(panel_dir / "layer_02.png")


# ── validation ───────────────────────────────────────────────────────────────


def test_provenance_mandatory(bank, tmp_path):
    m = yaml.safe_load(_manifest(bank, tmp_path).read_text())
    del m["panels"][0]["layers"][1]["provenance"]
    errors = afb.validate_manifest(m)
    assert any("provenance" in e for e in errors)


def test_bbox_mandatory_for_cutouts(bank, tmp_path):
    m = yaml.safe_load(_manifest(bank, tmp_path).read_text())
    del m["panels"][0]["layers"][1]["bbox_pct"]
    errors = afb.validate_manifest(m)
    assert any("bbox_pct required" in e for e in errors)


def test_bbox_not_required_for_structural_l2(bank, tmp_path):
    m = yaml.safe_load(_manifest(bank, tmp_path).read_text())
    del m["panels"][0]["layers"][1]["bbox_pct"]
    m["panels"][0]["structural_plan_path"] = "structural.json"
    errors = afb.validate_manifest(m)
    assert not any("bbox_pct required" in e for e in errors)


def test_bad_layer_class_refused(bank, tmp_path):
    m = yaml.safe_load(_manifest(bank, tmp_path).read_text())
    m["panels"][0]["layers"][0]["layer_class"] = "L9"
    errors = afb.validate_manifest(m)
    assert any("bad layer_class" in e for e in errors)


# ── §10 math ─────────────────────────────────────────────────────────────────


def test_composite_scales_into_bbox_centered(bank):
    canvas = Image.new("RGBA", (200, 300), (255, 255, 255, 255))
    cutout = Image.open(bank["l2"]).convert("RGBA")
    afb.composite_layer(canvas, cutout, [25, 25, 50, 50])
    # tight content is 60x60 → min-scale into 100x150 target = ×1.667 → 100x100
    # centered: x span [50,150], y span [75+25=100, 200]
    assert canvas.getpixel((100, 150))[:3] == (200, 0, 0)   # center is red
    assert canvas.getpixel((40, 150))[:3] == (255, 255, 255)  # outside bbox untouched
    assert canvas.getpixel((100, 90))[:3] == (255, 255, 255)  # above centered paste


def test_z_order_flip_changes_occlusion(bank, tmp_path):
    out_a = tmp_path / "above"
    out_b = tmp_path / "below"
    afb.run(_manifest(bank, tmp_path, l3_z="above_L2"), out_a)
    # rewrite manifest with below_L2 (same file name → same panel id)
    afb.run(_manifest(bank, tmp_path, l3_z="below_L2"), out_b)
    a = Image.open(out_a / "p1.png")
    b = Image.open(out_b / "p1.png")
    # overlap zone: L3 bbox [30,30,30,30] on 200x300 → x∈[60,120], y∈[90,180]
    # above_L2 → blue wins in the overlap; below_L2 → red wins
    assert a.getpixel((90, 135))[:3] == (0, 0, 200)
    assert b.getpixel((90, 135))[:3] == (200, 0, 0)


def test_l4_screen_blend_never_darkens(bank, tmp_path):
    out = tmp_path / "l4out"
    afb.run(_manifest(bank, tmp_path, with_l4=True), out)
    img = Image.open(out / "p1.png").convert("RGB")
    base = Image.open(bank["l0"]).convert("RGB")
    # sample a pure-L0 pixel: screen blend must not darken any channel
    px, bx = img.getpixel((10, 290)), base.getpixel((10, 290))
    assert all(p >= b for p, b in zip(px, bx))


# ── determinism + provenance ─────────────────────────────────────────────────


def test_deterministic_output(bank, tmp_path):
    m = _manifest(bank, tmp_path)
    out1, out2 = tmp_path / "r1", tmp_path / "r2"
    afb.run(m, out1)
    afb.run(m, out2)
    assert (out1 / "p1.png").read_bytes() == (out2 / "p1.png").read_bytes()


def test_provenance_table_written(bank, tmp_path):
    out = tmp_path / "prov"
    result = afb.run(_manifest(bank, tmp_path), out)
    assert (out / "_provenance.json").is_file()
    assert (out / "_provenance.md").is_file()
    assert result["provenance"]["layers_real"] == 2
    assert result["provenance"]["layers_interim"] == 1


def test_refuses_unlabeled_manifest(bank, tmp_path):
    mp = _manifest(bank, tmp_path)
    m = yaml.safe_load(mp.read_text())
    del m["panels"][0]["layers"][2]["provenance"]
    mp.write_text(yaml.safe_dump(m))
    with pytest.raises(ValueError, match="provenance"):
        afb.run(mp, tmp_path / "refused")


def test_structural_plan_consumes_verified_transform(bank, tmp_path):
    _write_structural_sidecars(bank)
    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)
    out = tmp_path / "structural_out"
    afb.run(_manifest_structural(bank, tmp_path, plan), out)
    img = Image.open(out / "p1.png").convert("RGB")
    assert img.getpixel((150, 210)) == (200, 0, 0)
    assert img.getpixel((60, 210)) == (0, 200, 0)
    gate_report = json.loads((out / "gate_report.json").read_text())
    assert gate_report["panels"][0]["passed"] is True
    assert any(g["gate"] == "L2_QUALITY" for g in gate_report["panels"][0]["gates"])
    assert any("structural_plan_hash=" in g["message"] for g in gate_report["panels"][0]["gates"])


def test_structural_l0_support_zone_clean_floor_passes(bank, tmp_path):
    _write_structural_sidecars(bank, support_zones=[
        {
            "zone_id": "clear_floor",
            "kind": "floor",
            "polygon_pct": [[0, 72], [100, 72], [100, 100], [0, 100]],
            "occupancy": "clear",
            "allows_character_support": True,
            "allowed_structural_templates": ["standing_room_scene"],
        }
    ])
    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)
    out = tmp_path / "support_floor"
    afb.run(_manifest_structural(bank, tmp_path, plan), out)

    gate_report = json.loads((out / "gate_report.json").read_text())
    gates = gate_report["panels"][0]["gates"]
    assert any(g["gate"] == "L0_SUPPORT_ZONE" for g in gates)


def test_structural_l0_support_zone_blocks_standing_on_table(bank, tmp_path):
    _write_structural_sidecars(bank, support_zones=[
        {
            "zone_id": "clear_floor",
            "kind": "floor",
            "polygon_pct": [[0, 72], [100, 72], [100, 100], [0, 100]],
            "occupancy": "clear",
            "allows_character_support": True,
            "allowed_structural_templates": ["standing_room_scene"],
            "priority": 0,
        },
        {
            "zone_id": "table_top",
            "kind": "table",
            "bbox_pct": [60, 70, 30, 25],
            "occupancy": "occupied",
            "allows_character_support": False,
            "priority": 10,
        },
    ])
    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)

    with pytest.raises(ValueError, match="L0 support-zone FAIL"):
        afb.run(_manifest_structural(bank, tmp_path, plan), tmp_path / "table_fail")


def test_structural_l0_support_zone_allows_intentional_seated_table(bank, tmp_path):
    _write_structural_sidecars(bank, support_zones=[
        {
            "zone_id": "seat_table_support",
            "kind": "seat_table",
            "bbox_pct": [60, 70, 30, 25],
            "occupancy": "intentional_support",
            "allows_character_support": True,
            "allowed_structural_templates": ["seated_table_scene"],
            "priority": 10,
        }
    ])
    plan = _structural_plan(
        tmp_path,
        tx_pct=75.0,
        ty_pct=80.0,
        structural_template_id="seated_table_scene",
        panel_type_id="dialogue_seated_table",
        relation="seated_on",
        support_role="seat_or_table",
        support_polygon_pct=[[60, 70], [90, 70], [90, 95], [60, 95]],
    )
    out = tmp_path / "seated_pass"
    afb.run(_manifest_structural(
        bank,
        tmp_path,
        plan,
        grounding={
            "contact_shadow": False,
            "occluder": False,
            "support_mode": "intentional_seat_table",
        },
    ), out)

    gate_report = json.loads((out / "gate_report.json").read_text())
    gates = gate_report["panels"][0]["gates"]
    assert any(
        g["gate"] == "L0_SUPPORT_ZONE" and "zone=seat_table_support" in g["message"]
        for g in gates
    )


def test_structural_l0_support_zone_blocks_seated_table_without_intentional_mode(bank, tmp_path):
    _write_structural_sidecars(bank, support_zones=[
        {
            "zone_id": "seat_table_support",
            "kind": "seat_table",
            "bbox_pct": [60, 70, 30, 25],
            "occupancy": "intentional_support",
            "allows_character_support": True,
            "allowed_structural_templates": ["seated_table_scene"],
            "priority": 10,
        }
    ])
    plan = _structural_plan(
        tmp_path,
        tx_pct=75.0,
        ty_pct=80.0,
        structural_template_id="seated_table_scene",
        panel_type_id="dialogue_seated_table",
        relation="seated_on",
        support_role="seat_or_table",
        support_polygon_pct=[[60, 70], [90, 70], [90, 95], [60, 95]],
    )

    with pytest.raises(ValueError, match="seated_table_requires_intentional_support_mode"):
        afb.run(_manifest_structural(bank, tmp_path, plan), tmp_path / "seated_without_mode")


def test_structural_l3_prop_does_not_pollute_l2_quality(bank, tmp_path):
    _write_structural_sidecars(bank, support_zones=[
        {
            "zone_id": "clear_floor",
            "kind": "floor",
            "polygon_pct": [[0, 72], [100, 72], [100, 100], [0, 100]],
            "occupancy": "clear",
            "allows_character_support": True,
            "allowed_structural_templates": ["standing_room_scene"],
        }
    ])
    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)
    manifest_path = _manifest_structural(bank, tmp_path, plan)
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["panels"][0]["layers"].append({
        "layer_class": "L3",
        "asset": str(bank["l3"]),
        "bbox_pct": [4, 10, 18, 18],
        "provenance": "INTERIM",
        "provenance_note": "separate prop fixture",
    })
    manifest_path.write_text(yaml.safe_dump(manifest))

    out = tmp_path / "l3_prop"
    afb.run(manifest_path, out)
    gate_report = json.loads((out / "gate_report.json").read_text())
    gates = gate_report["panels"][0]["gates"]
    assert any(g["gate"] == "L2_QUALITY" for g in gates)
    assert any(g["gate"] == "L0_SUPPORT_ZONE" for g in gates)


def test_mecha_structural_purity_clean_layers_pass(bank, tmp_path):
    _write_mecha_clean_sidecars(bank)
    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)
    out = tmp_path / "mecha_clean"
    afb.run(_manifest_structural(bank, tmp_path, plan), out)

    gate_report = json.loads((out / "gate_report.json").read_text())
    gates = gate_report["panels"][0]["gates"]
    assert any(g["gate"] == "L0_STRUCTURAL_PURITY" for g in gates)
    assert any(g["gate"] == "L2_STRUCTURAL_PURITY" for g in gates)
    assert any(g["gate"] == "L2_QUALITY" for g in gates)
    assert any(g["gate"] == "L0_SUPPORT_ZONE" for g in gates)


def test_mecha_l0_structural_purity_blocks_pilot_in_background(bank, tmp_path):
    _write_mecha_clean_sidecars(bank)
    l0_path = bank["l0"].with_suffix(".composition.json")
    l0_meta = json.loads(l0_path.read_text())
    l0_meta["structural_layer_contract"].update({
        "status": "blocked",
        "contains_primary_subject": True,
        "contains_pilot": True,
        "contains": ["pilot", "cockpit"],
    })
    l0_path.write_text(json.dumps(l0_meta, indent=2) + "\n")
    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)

    with pytest.raises(ValueError, match="L0 structural purity FAIL"):
        afb.run(_manifest_structural(bank, tmp_path, plan), tmp_path / "mecha_dirty_l0")


def test_mecha_l2_structural_purity_blocks_cockpit_context(bank, tmp_path):
    _write_mecha_clean_sidecars(bank)
    l2_path = bank["l2"].with_suffix(".composition.json")
    l2_meta = json.loads(l2_path.read_text())
    l2_meta["scene_contamination"] = True
    l2_meta["structural_layer_contract"].update({
        "status": "blocked",
        "contains_background": True,
        "contains_environment": True,
        "contains": ["pilot", "cockpit", "environment"],
        "background_context": ["cockpit", "environment"],
    })
    l2_path.write_text(json.dumps(l2_meta, indent=2) + "\n")
    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)

    with pytest.raises(ValueError, match="L2 structural purity FAIL"):
        afb.run(_manifest_structural(bank, tmp_path, plan), tmp_path / "mecha_dirty_l2")


def test_mecha_l3_structural_purity_blocks_scene_context(bank, tmp_path):
    _write_mecha_clean_sidecars(bank)
    l3_path = bank["l3"].with_suffix(".composition.json")
    l3_meta = json.loads(l3_path.read_text())
    l3_meta["structural_layer_contract"].update({
        "status": "blocked",
        "contains": ["background", "cockpit", "mecha"],
    })
    l3_path.write_text(json.dumps(l3_meta, indent=2) + "\n")

    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)
    manifest_path = _manifest_structural(bank, tmp_path, plan)
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["panels"][0]["layers"].append({
        "layer_class": "L3",
        "asset": str(bank["l3"]),
        "bbox_pct": [4, 10, 18, 18],
        "provenance": "INTERIM",
        "provenance_note": "dirty mecha prop fixture",
    })
    manifest_path.write_text(yaml.safe_dump(manifest))

    with pytest.raises(ValueError, match="L3 structural purity FAIL"):
        afb.run(manifest_path, tmp_path / "mecha_dirty_l3")


def test_structural_plan_hash_mismatch_refused(bank, tmp_path):
    _write_structural_sidecars(bank)
    plan = _structural_plan(tmp_path, bad_hash=True)
    with pytest.raises(ValueError, match="structural plan invalid"):
        afb.run(_manifest_structural(bank, tmp_path, plan), tmp_path / "structural_bad")


def test_v5_output_dir_converts_to_valid_assembly_manifest(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    out = tmp_path / "bridge"
    result = v5_bridge.bridge_v5_panel_dir(panel_dir, out)

    assert result.manifest_path.is_file()
    assert result.structural_plan_path.is_file()
    manifest = afb.load_manifest(result.manifest_path)
    assert manifest["panels"][0]["panel_id"] == "ep001_013"
    assert manifest["panels"][0]["structural_plan_path"] == "structural_plan.json"


def test_v5_bridge_maps_l0_l2_to_layer_files(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    result = v5_bridge.bridge_v5_panel_dir(panel_dir, tmp_path / "bridge")
    manifest = yaml.safe_load(result.manifest_path.read_text())
    layers = manifest["panels"][0]["layers"]

    assert layers[0]["layer_class"] == "L0"
    assert layers[0]["asset"] == "layer_01.png"
    assert layers[1]["layer_class"] == "L2"
    assert layers[1]["asset"] == "layer_02.png"
    assert "layer_00.png" not in result.manifest_path.read_text()
    assert json.loads((panel_dir / "_telemetry.json").read_text())["layer_roles"]["layer_00.png"] == "model_composite"


def test_sparse_establishing_wide_resolves_structural_bbox_plan(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    result = v5_bridge.bridge_v5_panel_dir(panel_dir, tmp_path / "bridge")
    plan = json.loads(result.structural_plan_path.read_text())
    body = plan["plan_body"]
    transform = body["resolved_placements"][0]["transform"]

    assert result.panel_type_id == "establish_standing_room"
    assert result.structural_template_id == "standing_room_scene"
    assert body["panel_type_id"] == "establish_standing_room"
    assert transform["tx_pct"] == 14.0
    assert transform["ty_pct"] == 85.0
    assert body["support_graph"]["nodes"][1]["placement_bbox_pct_xyxy"] == [3.0, 65.0, 25.0, 85.0]

    import structural_composition as sc
    sc.verify_plan_hash(plan)


def test_v5_bridge_missing_layer_02_fails(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    (panel_dir / "layer_02.png").unlink()

    with pytest.raises(v5_bridge.BridgeError, match="layer_02.png"):
        v5_bridge.bridge_v5_panel_dir(panel_dir, tmp_path / "bridge")


def test_v5_bridge_rejects_multi_component_foreground(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    _pollute_l2_with_stray_component(panel_dir)

    with pytest.raises(v5_bridge.BridgeError, match="L2 foreground quality FAIL"):
        v5_bridge.bridge_v5_panel_dir(panel_dir, tmp_path / "bridge")


def test_v5_bridge_requires_reviewed_mecha_sidecars(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    _mark_v5_panel_mecha(panel_dir)

    with pytest.raises(v5_bridge.BridgeError, match="reviewed mecha L2 composition sidecar"):
        v5_bridge.bridge_v5_panel_dir(panel_dir, tmp_path / "bridge")


def test_v5_bridge_rejects_blocked_mecha_sidecar(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    _mark_v5_panel_mecha(panel_dir)
    _write_v5_mecha_sidecars(panel_dir, clean=False)

    with pytest.raises(v5_bridge.BridgeError, match="reviewed mecha L2 sidecar failed contract"):
        v5_bridge.bridge_v5_panel_dir(panel_dir, tmp_path / "bridge")


def test_v5_bridge_accepts_clean_reviewed_mecha_sidecars(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    _mark_v5_panel_mecha(panel_dir)
    _write_v5_mecha_sidecars(panel_dir, clean=True)
    result = v5_bridge.bridge_v5_panel_dir(panel_dir, tmp_path / "bridge", assemble=True)

    assert result.final_composite_path is not None
    gate_report = json.loads((tmp_path / "bridge" / "gate_report.json").read_text())
    gates = gate_report["panels"][0]["gates"]
    assert any(g["gate"] == "L0_STRUCTURAL_PURITY" for g in gates)
    assert any(g["gate"] == "L2_STRUCTURAL_PURITY" for g in gates)


def test_structural_assembler_rejects_multi_component_l2(bank, tmp_path):
    _write_structural_sidecars(bank)
    l2 = Image.open(bank["l2"]).convert("RGBA")
    for x in range(2, 18):
        for y in range(2, 18):
            l2.putpixel((x, y), (120, 70, 20, 255))
    l2.save(bank["l2"])

    plan = _structural_plan(tmp_path, tx_pct=75.0, ty_pct=80.0)
    with pytest.raises(ValueError, match="L2 foreground quality FAIL"):
        afb.run(_manifest_structural(bank, tmp_path, plan), tmp_path / "dirty_l2")


def test_v5_structural_assembly_uses_plan_not_model_composite(tmp_path):
    panel_dir = _v5_panel_output(tmp_path)
    result = v5_bridge.bridge_v5_panel_dir(panel_dir, tmp_path / "bridge", assemble=True)

    assert result.final_composite_path is not None
    assert result.final_composite_path.read_bytes() != (panel_dir / "layer_00.png").read_bytes()
    img = Image.open(result.final_composite_path).convert("RGB")
    assert img.getpixel((28, 233)) == (200, 0, 0)
    assert img.getpixel((100, 120)) == (0, 200, 0)

    provenance = json.loads((tmp_path / "bridge" / "_provenance.json").read_text())
    assert all("layer_00.png" not in r["asset"] for r in provenance["records"])


SERIES = REPO / (
    "artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying"
)
PILOT_MANIFEST = SERIES / "assembly_manifests/composition_grammar_pilot.yaml"
CONTROL_MANIFEST = SERIES / "assembly_manifests/composition_grammar_control.yaml"
DEMO_REAL_PILOT = SERIES / "assembly_manifests/demo_alarm_metaphor_6p_REAL_pilot.yaml"
MIN_REAL_BYTES = 50_000


def _bank_assets_real() -> bool:
    """True when Pearl Star REAL image_bank PNGs are present (not LFS pointers)."""
    probe = SERIES / "image_bank/L1/wall_alarm_green_idle.png"
    return probe.is_file() and probe.stat().st_size >= MIN_REAL_BYTES


def _manifest_assets_present(manifest_path: Path) -> bool:
    if not manifest_path.is_file():
        return False
    manifest = yaml.safe_load(manifest_path.read_text())
    for panel in manifest.get("panels") or []:
        for layer in panel.get("layers") or []:
            asset = Path(str(layer.get("asset", "")))
            path = asset if asset.is_absolute() else REPO / asset
            if not path.is_file():
                return False
    return True


def _manifest_g1_illegal_panels(manifest_path: Path) -> list[str]:
    """Return panel_ids where waist_up/bust L2 × full_render L0 lacks defocus derivation."""
    import json

    manifest = yaml.safe_load(manifest_path.read_text())
    illegal: list[str] = []
    for panel in manifest.get("panels") or []:
        l0_meta: dict = {}
        l2_meta: dict | None = None
        deriv = None
        for lyr in panel.get("layers") or []:
            if lyr.get("layer_class") == "L0":
                ap = REPO / lyr["asset"]
                sc = ap.with_suffix(".composition.json")
                if sc.is_file():
                    l0_meta = json.loads(sc.read_text())
                deriv = lyr.get("derivation")
            if lyr.get("layer_class") == "L2":
                ap = REPO / lyr["asset"]
                sc = ap.with_suffix(".composition.json")
                if sc.is_file():
                    l2_meta = json.loads(sc.read_text())
        if not l2_meta:
            continue
        bg = l0_meta.get("bg_class", "full_render")
        if deriv and deriv.get("type") == "defocus":
            bg = "defocus_derived"
        crop = l2_meta.get("crop_class", "")
        if bg == "full_render" and crop in ("waist_up", "bust", "face_cu"):
            illegal.append(panel["panel_id"])
    return illegal


@pytest.mark.skipif(not DEMO_REAL_PILOT.is_file(), reason="demo REAL pilot manifest missing")
def test_demo_real_pilot_manifest_g1_legal():
    """Hand-authored demo manifest must defocus L0 when L2 crop is bust/waist_up on full_render."""
    illegal = _manifest_g1_illegal_panels(DEMO_REAL_PILOT)
    assert illegal == [], f"G1-illegal panels (add L0 derivation defocus): {illegal}"


@pytest.mark.skipif(not DEMO_REAL_PILOT.is_file(), reason="demo REAL pilot manifest missing")
@pytest.mark.skipif(not _bank_assets_real(), reason="REAL image_bank PNGs not present")
def test_demo_real_pilot_manifest_assembles(tmp_path):
    """Demo REAL pilot assembles all 6 panels with grammar gates passing."""
    out = tmp_path / "demo_real"
    result = afb.run(DEMO_REAL_PILOT, out)
    pngs = list(out.glob("demo_p*.png"))
    assert len(pngs) == 6
    assert result["gate_report"]
    assert all(p["passed"] for p in result["gate_report"])


@pytest.mark.skipif(not PILOT_MANIFEST.is_file(), reason="pilot manifest not present")
@pytest.mark.skipif(not _manifest_assets_present(PILOT_MANIFEST), reason="pilot manifest assets missing")
def test_grammar_pilot_manifest_assembles(tmp_path):
    """Grammar panels assemble through the real bank path."""
    out = tmp_path / "pilot"
    result = afb.run(PILOT_MANIFEST, out)
    assert result["gate_report"]
    assert all(p["passed"] for p in result["gate_report"])


@pytest.mark.skipif(not CONTROL_MANIFEST.is_file(), reason="control manifest not present")
def test_grammar_control_illegal_combo_fails(tmp_path):
    """waist_up × full_render hard-fails G1 when both sidecars exist."""
    with pytest.raises(ValueError, match="composition grammar FAIL|composition planning"):
        afb.run(CONTROL_MANIFEST, tmp_path / "control_out")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
