"""Unit tests for composition_grammar.py — G1 legality and G3 gate checks."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

from composition_grammar import (  # noqa: E402
    GateSeverity,
    g1_crop_bg_legality,
    g3_horizon_scale_check,
    run_combination_gates,
)

KITCHEN_L0 = {
    "asset_id": "L0_2b9283d4c387",
    "bg_class": "full_render",
    "camera": {"angle_bucket": "eye_level", "eye_level_y_pct": 42, "camera_height": "seated"},
    "light": {"azimuth": "camera_left"},
}

WAIST_L2 = {
    "crop_class": "waist_up",
    "implied_camera": {"angle_bucket": "eye_level"},
    "light": {"azimuth": "camera_left"},
}

THIGH_L2 = {
    "crop_class": "thigh_up",
    "diegetic_pair": "L0_2b9283d4c387",
    "implied_camera": {"angle_bucket": "eye_level"},
    "light": {"azimuth": "camera_left"},
}


def test_g1_waist_up_on_full_render_is_illegal():
    r = g1_crop_bg_legality(WAIST_L2, KITCHEN_L0)
    assert r.severity == GateSeverity.FAIL
    assert "ILLEGAL" in r.message


def test_g1_waist_up_on_defocus_is_legal():
    l0 = {**KITCHEN_L0, "bg_class": "defocus_derived"}
    r = g1_crop_bg_legality(WAIST_L2, l0)
    assert r.severity == GateSeverity.PASS


def test_g1_diegetic_pair_auto_pass():
    r = g1_crop_bg_legality(THIGH_L2, KITCHEN_L0)
    assert r.severity == GateSeverity.PASS
    assert "diegetic" in r.message


def test_g1_thigh_up_on_full_render_legal_ops():
    l2 = {**THIGH_L2, "diegetic_pair": None}
    r = g1_crop_bg_legality(l2, KITCHEN_L0)
    assert r.severity == GateSeverity.PASS


def test_combination_gates_full_suite():
    results = run_combination_gates(WAIST_L2, KITCHEN_L0)
    assert any(r.gate == "G1" and r.severity == GateSeverity.FAIL for r in results)
    assert all(r.severity != GateSeverity.FAIL for r in results if r.gate != "G1")


def test_g3_within_tolerance():
    slot = {"feet_y_pct": 78, "expected_figure_h_pct": 55}
    # 55% of 1920 = 1056 px
    r = g3_horizon_scale_check(KITCHEN_L0, slot, 1920, 1056.0)
    assert r.severity == GateSeverity.PASS


def test_g3_outside_tolerance_fails():
    slot = {"feet_y_pct": 78, "expected_figure_h_pct": 55}
    r = g3_horizon_scale_check(KITCHEN_L0, slot, 1920, 700.0)
    assert r.severity == GateSeverity.FAIL


def test_dialogue_bust_uses_slot_metadata():
    from composition_grammar import DEFAULT_ABSTRACT_STAGE_SLOT, dialogue_bust_paste
    from PIL import Image

    canvas = Image.new("RGBA", (1080, 1920), "#FFFFFF")
    cutout = Image.new("RGBA", (200, 400), (0, 0, 0, 0))
    for y in range(50, 350):
        for x in range(40, 160):
            cutout.putpixel((x, y), (200, 100, 100, 255))
    slot = {**DEFAULT_ABSTRACT_STAGE_SLOT, "feet_y_pct": 90, "expected_figure_h_pct": 40}
    out = dialogue_bust_paste(canvas, cutout, {"eye_y_px": 120}, slot)
    alpha = out.getchannel("A")
    bbox = alpha.getbbox()
    assert bbox is not None
    # Custom slot feet_y_pct=90 → paste bottom near 90% frame height
    assert bbox[3] >= int(1920 * 0.85)
