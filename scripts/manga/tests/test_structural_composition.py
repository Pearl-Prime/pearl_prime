"""Focused tests for Structural Composition MVP runtime layer."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import structural_composition as sc  # noqa: E402


def _seated_bundle(**overrides):
    b = {
        "schema_version": "1.0.0",
        "bundle_id": "b_seated",
        "panel_id": "p_seated",
        "panel_type_id": "dialogue_seated_table",
        "structural_template_id": "seated_table_scene",
        "canvas": {"width": 1000, "height": 1000},
        "nodes": [
            {
                "node_id": "seat",
                "category": "support_surface",
                "role": "seat_or_table",
                # seat polygon covering lower-middle of canvas
                "support_polygon_pct": [
                    [30, 55], [70, 55], [72, 75], [28, 75],
                ],
            },
            {
                "node_id": "char",
                "category": "character",
                "role": "primary_subject",
                # local contact at origin of placement; world = transform
                "contact_point_pct": [0.0, 0.0],
            },
        ],
        "edges": [
            {
                "edge_id": "e1",
                "relation": "seated_on",
                "from_node": "char",
                "to_node": "seat",
            }
        ],
        "placements": [
            {
                "node_id": "char",
                "transform": {
                    "tx_pct": 50.0,
                    "ty_pct": 65.0,
                    "uniform_scale": 1.0,
                    "rotation_deg": 0.0,
                },
            }
        ],
    }
    b.update(overrides)
    return b


def _standing_bundle(**overrides):
    b = {
        "schema_version": "1.0.0",
        "bundle_id": "b_stand",
        "panel_id": "p_stand",
        "panel_type_id": "establish_standing_room",
        "structural_template_id": "standing_room_scene",
        "canvas": {"width": 1000, "height": 1000},
        "nodes": [
            {
                "node_id": "floor",
                "category": "support_surface",
                "role": "floor",
                "support_polygon_pct": [
                    [5, 80], [95, 80], [95, 98], [5, 98],
                ],
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
                "relation": "standing_on",
                "from_node": "char",
                "to_node": "floor",
            }
        ],
        "placements": [
            {
                "node_id": "char",
                "transform": {
                    "tx_pct": 50.0,
                    "ty_pct": 90.0,
                    "uniform_scale": 1.0,
                    "rotation_deg": 0.0,
                },
            }
        ],
    }
    b.update(overrides)
    return b


def test_missing_graph_hard_fail():
    b = _seated_bundle()
    b["edges"] = []
    with pytest.raises(sc.StructuralHardFail) as ei:
        sc.validate_support_graph(b)
    assert ei.value.code == "MISSING_GRAPH"


def test_unknown_category_hard_fail():
    b = _seated_bundle()
    b["nodes"][0]["category"] = "spaceship"
    with pytest.raises(sc.StructuralHardFail) as ei:
        sc.validate_support_graph(b)
    assert ei.value.code == "UNKNOWN_CATEGORY"


def test_support_cycle_hard_fail():
    b = _seated_bundle()
    b["nodes"].append({
        "node_id": "prop",
        "category": "prop",
        "contact_point_pct": [0, 0],
        "requires_support": False,
    })
    b["edges"] = [
        {"edge_id": "e1", "relation": "seated_on", "from_node": "char", "to_node": "seat"},
        {"edge_id": "e2", "relation": "resting_on", "from_node": "seat", "to_node": "prop"},
        {"edge_id": "e3", "relation": "held_by", "from_node": "prop", "to_node": "char"},
    ]
    # seat is support_surface; resting_on from seat→prop is weird but forms cycle char→seat→prop→char
    with pytest.raises(sc.StructuralHardFail) as ei:
        sc.validate_support_graph(b)
    assert ei.value.code == "SUPPORT_CYCLE"


def test_unsupported_rotation_hard_fail():
    b = _seated_bundle()
    b["placements"][0]["transform"]["rotation_deg"] = 45.0
    with pytest.raises(sc.StructuralHardFail) as ei:
        sc.validate_support_graph(b)
    assert ei.value.code == "UNSUPPORTED_ROTATION"


def test_seated_contact_uses_point_in_polygon_not_area_ratio():
    # Inside polygon → pass
    sc.validate_support_graph(_seated_bundle())
    # Outside polygon → CONTACT_FAIL (pip), not area-ratio language
    bad = _seated_bundle()
    bad["placements"][0]["transform"]["ty_pct"] = 10.0  # above seat
    with pytest.raises(sc.StructuralHardFail) as ei:
        sc.validate_support_graph(bad)
    assert ei.value.code == "CONTACT_FAIL"
    assert "point-in-polygon" in str(ei.value).lower() or "point-in-polygon" in ei.value.args[0].lower() or "polygon" in str(ei.value).lower()


def test_point_in_polygon_unit():
    square = [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)]
    assert sc.point_in_polygon((5.0, 5.0), square) is True
    assert sc.point_in_polygon((15.0, 5.0), square) is False
    # tolerance expands polygon
    assert sc.point_in_polygon((11.0, 5.0), square, tolerance=2.0) is True


def test_plan_hash_not_self_referential():
    env = sc.build_plan_envelope(_seated_bundle())
    assert "plan_hash" not in env["plan_body"]
    assert env["plan_hash"] == sc.compute_plan_hash(env["plan_body"])
    # Tamper body → mismatch
    env["plan_body"]["panel_id"] = "tampered"
    with pytest.raises(sc.StructuralHardFail) as ei:
        sc.verify_plan_hash(env)
    assert ei.value.code == "PLAN_HASH_MISMATCH"


def test_renderer_verifies_plan_hash_before_rendering():
    env = sc.build_plan_envelope(_standing_bundle())
    out = sc.render_from_verified_plan(env)
    assert out["recomputed_placement"] is False
    assert out["plan_hash"] == env["plan_hash"]
    env2 = json.loads(json.dumps(env))
    env2["plan_hash"] = "0" * 64
    with pytest.raises(sc.StructuralHardFail) as ei:
        sc.render_from_verified_plan(env2)
    assert ei.value.code == "PLAN_HASH_MISMATCH"


def test_real_l0_support_overlay_same_resolved_transform():
    env = sc.build_plan_envelope(_seated_bundle())
    overlay = sc.emit_support_overlay(env)
    assert overlay["same_resolved_transform_path"] is True
    assert overlay["transform_model"] == sc.TRANSFORM_MODEL
    assert overlay["regions"][0]["transform_source"] == "envelope.plan_body.resolved_placements"


def test_bridge_panel_type_to_template():
    row = sc.bridge_for_panel_type("dialogue_seated_table")
    assert row["structural_template_id"] == "seated_table_scene"
    assert "seated_on" in row["required_support_proof"]


def test_floating_torso_hard_fail():
    b = _seated_bundle()
    b["edges"] = []  # missing graph caught first
    with pytest.raises(sc.StructuralHardFail):
        sc.validate_support_graph(b)


def test_nonuniform_scale_hard_fail():
    b = _seated_bundle()
    b["placements"][0]["transform"]["sx"] = 1.0
    b["placements"][0]["transform"]["sy"] = 2.0
    with pytest.raises(sc.StructuralHardFail) as ei:
        sc.validate_support_graph(b)
    assert ei.value.code == "UNSUPPORTED_NONUNIFORM_SCALE"
