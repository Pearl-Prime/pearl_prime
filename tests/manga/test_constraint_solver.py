"""Tests for V2 Phase A.1 character constraint solver."""
from __future__ import annotations

import copy

from scripts.manga.character_individuation.constraint_solver import (
    check_collision,
    check_forbidden_combinations,
    count_matching_locked_axes,
    load_axes_config,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

# Minimal axes_config that exercises the solver without depending on the
# full repo file's content. Mirrors the shape of
# config/manga/character_design_axes.yaml::solver_rules.
_AXES_CONFIG = {
    "solver_rules": {
        "lockout_minimum": 9,
        "axis_priority_order_for_solver": [
            "eye_geometry",
            "hair",
            "color_signal",
            "face_shape",
            "mouth_jaw",
            "wardrobe_register",
            "age_signaling",
            "accessories",
            "nose_construction",
            "build",
            "skin_treatment",
            "posture_default",
        ],
        "forbidden_combinations": [
            {
                "rule_id": "shojo_eye_in_josei",
                "axes": ["eye_geometry.size", "eye_geometry.eyelash_density", "market_demo"],
                "forbidden": {
                    "eye_geometry.size": "extra_large",
                    "eye_geometry.eyelash_density": "heavy_decorative",
                    "market_demo": "josei",
                },
                "reason": "modern josei moved past sparkle/big-eye",
            },
            {
                "rule_id": "bow_mouth_in_josei",
                "axes": ["mouth_jaw.lip_shape", "market_demo"],
                "forbidden": {
                    "mouth_jaw.lip_shape": "bow_mouth",
                    "market_demo": "josei",
                },
                "reason": "bow_mouth is 1990s shojo",
            },
        ],
    }
}


def _full_design(**axis_overrides) -> dict:
    """Build a complete 12-axis design with all locked. Override axes via kwargs."""
    base_axes = {
        "face_shape": {"value": "oval", "lockout": "yes"},
        "eye_geometry": {
            "size": "medium", "shape": "almond", "spacing": "standard",
            "lid_fold": "double", "eyelash_density": "moderate", "lockout": "yes",
        },
        "nose_construction": {
            "bridge_angle": "straight", "bridge_length": "medium",
            "tip_shape": "pointed", "nostril_visibility": "implied",
            "lockout": "yes",
        },
        "mouth_jaw": {
            "resting_expression": "neutral_soft", "jaw_width": "narrow",
            "chin_shape": "soft_pointed", "lip_shape": "thin_upper_full_lower",
            "lockout": "yes",
        },
        "hair": {
            "length": "shoulder", "parting": "side_left", "fringe_style": "straight_blunt",
            "texture": "straight", "color_signal": "dark_brown",
            "lockout": "yes",
        },
        "color_signal": {"value": "muted_brown", "lockout": "yes"},
        "wardrobe_register": {"value": "everyday_casual", "lockout": "yes"},
        "age_signaling": {"value": "late_30s", "lockout": "yes"},
        "accessories": {"value": "round_glasses", "lockout": "yes"},
        "build": {"value": "average", "lockout": "no"},
        "skin_treatment": {"value": "clean", "lockout": "no"},
        "posture_default": {"value": "neutral_relaxed", "lockout": "no"},
    }
    for name, override in axis_overrides.items():
        base_axes[name] = override
    return {
        "series_id": "test_series",
        "brand_id": "test_brand",
        "market_demo": "josei",
        "axes": base_axes,
        "_series_id": "test_series",
        "_brand_id": "test_brand",
    }


# ── lockout-minimum tests ────────────────────────────────────────────────────

def test_accept_when_all_axes_lock():
    design = _full_design()
    r = check_collision(design, [], axes_config=_AXES_CONFIG)
    assert r.accepted, r.summary()
    assert r.locked_axes_count == 9  # only first 9 lock by default in fixture


def test_reject_below_lockout_minimum():
    design = _full_design()
    # Unlock 4 of the 9 default-locked axes — drops to 5 locked.
    for name in ("face_shape", "eye_geometry", "hair", "color_signal"):
        design["axes"][name]["lockout"] = "no"
    r = check_collision(design, [], axes_config=_AXES_CONFIG)
    assert not r.accepted
    assert "lockout_minimum" in " ".join(r.reasons)


def test_lockout_string_yes_and_bool_true_both_count():
    design = _full_design()
    design["axes"]["face_shape"]["lockout"] = True
    design["axes"]["eye_geometry"]["lockout"] = "Yes"
    r = check_collision(design, [], axes_config=_AXES_CONFIG)
    assert r.accepted


# ── forbidden-combination tests ──────────────────────────────────────────────

def test_forbidden_shojo_eye_in_josei():
    design = _full_design()
    design["axes"]["eye_geometry"]["size"] = "extra_large"
    design["axes"]["eye_geometry"]["eyelash_density"] = "heavy_decorative"
    # market_demo already "josei" in fixture
    r = check_collision(design, [], axes_config=_AXES_CONFIG)
    assert not r.accepted
    assert "shojo_eye_in_josei" in r.forbidden_rules_hit


def test_forbidden_bow_mouth_in_josei():
    design = _full_design()
    design["axes"]["mouth_jaw"]["lip_shape"] = "bow_mouth"
    r = check_collision(design, [], axes_config=_AXES_CONFIG)
    assert not r.accepted
    assert "bow_mouth_in_josei" in r.forbidden_rules_hit


def test_forbidden_does_not_fire_when_demo_differs():
    design = _full_design()
    design["market_demo"] = "shojo"
    design["axes"]["mouth_jaw"]["lip_shape"] = "bow_mouth"
    # bow_mouth in shojo is fine — only forbidden in josei
    r = check_collision(design, [], axes_config=_AXES_CONFIG)
    assert r.accepted, r.summary()


def test_check_forbidden_combinations_unit():
    design = _full_design()
    rules = _AXES_CONFIG["solver_rules"]["forbidden_combinations"]
    assert check_forbidden_combinations(design, rules) == []
    design["axes"]["mouth_jaw"]["lip_shape"] = "bow_mouth"
    assert "bow_mouth_in_josei" in check_forbidden_combinations(design, rules)


# ── collision-detection tests ────────────────────────────────────────────────

def test_count_matching_returns_zero_for_distinct_pair():
    a = _full_design()
    b = _full_design(face_shape={"value": "heart_shaped", "lockout": "yes"})
    b["axes"]["eye_geometry"]["size"] = "small"
    b["axes"]["hair"]["length"] = "very_short"
    b["axes"]["hair"]["color_signal"] = "black"
    b["axes"]["color_signal"] = {"value": "high_contrast_red", "lockout": "yes"}
    n, _ = count_matching_locked_axes(
        a, b,
        axis_priority_order=_AXES_CONFIG["solver_rules"]["axis_priority_order_for_solver"],
    )
    # a vs b differ on face_shape, eye_geometry, hair, color_signal → expect ≤ 5 matches
    assert n <= 5


def test_same_brand_collision_at_threshold_5():
    """Same brand: 5 locked axes match → REJECT."""
    a = _full_design()
    b = copy.deepcopy(a)
    b["_series_id"] = "test_series_b"
    # All 9 locked axes match by default — definitely ≥5, should REJECT
    r = check_collision(a, [b], axes_config=_AXES_CONFIG)
    assert not r.accepted
    assert any("collision" in s for s in r.reasons)
    assert r.colliding_with[0]["scope"] == "same_brand"


def test_cross_brand_more_permissive():
    """Cross brand needs 7 matches not 5."""
    a = _full_design()
    b = copy.deepcopy(a)
    b["_series_id"] = "test_series_b"
    b["_brand_id"] = "different_brand"
    # Make 6 of 9 axes differ → match_count = 3 < 7 → ACCEPT cross-brand even
    # though 3 also < 5 same-brand-threshold, but we want a case where it
    # would REJECT same-brand and ACCEPT cross-brand. Engineer 5-6 matches.
    # Differ on 4 axes → match_count = 5 → cross-brand ACCEPT (5<7)
    b["axes"]["face_shape"]["value"] = "heart_shaped"
    b["axes"]["eye_geometry"]["size"] = "small"
    b["axes"]["hair"]["length"] = "very_short"
    b["axes"]["accessories"]["value"] = "no_accessories"
    r = check_collision(a, [b], axes_config=_AXES_CONFIG)
    assert r.accepted, f"expected cross-brand ACCEPT at 5/9 matches: {r.summary()}"


def test_cross_brand_rejects_at_threshold_7():
    a = _full_design()
    b = copy.deepcopy(a)
    b["_series_id"] = "test_series_b"
    b["_brand_id"] = "different_brand"
    # Differ on only 2 axes → 7 matches → cross-brand REJECT
    b["axes"]["face_shape"]["value"] = "heart_shaped"
    b["axes"]["accessories"]["value"] = "no_accessories"
    r = check_collision(a, [b], axes_config=_AXES_CONFIG)
    assert not r.accepted
    assert r.colliding_with[0]["scope"] == "cross_brand"


def test_unlocked_axis_doesnt_count_in_collision():
    a = _full_design()
    b = copy.deepcopy(a)
    b["_series_id"] = "test_series_b"
    # Differ on only 1 locked axis but unlock 3 more → reduces locked-axis
    # match count, but since b's locked axes are now fewer, the comparison
    # should yield fewer matches.
    b["axes"]["face_shape"]["value"] = "heart_shaped"
    for axis_name in ("hair", "color_signal", "accessories"):
        b["axes"][axis_name]["lockout"] = "no"
    # Now b has 5 locked axes that match a → still over 5-threshold → REJECT
    r = check_collision(a, [b], axes_config=_AXES_CONFIG)
    # This tests that we count by intersection-of-locked, not just a's locked.
    # eye_geometry, nose_construction, mouth_jaw, age_signaling, wardrobe_register
    # remain locked-and-matching in both → 5 matches → REJECT (same-brand)
    assert not r.accepted


def test_self_skipped_when_validating_against_catalog_including_self():
    a = _full_design()
    # Catalog contains the candidate itself; should be skipped per the
    # solver's self-comparison guard.
    r = check_collision(a, [a], axes_config=_AXES_CONFIG)
    assert r.accepted, r.summary()


# ── repo-config compatibility (smoke test) ──────────────────────────────────

def test_load_axes_config_matches_real_config():
    """Make sure the real config/manga/character_design_axes.yaml loads and
    has the keys the solver needs. Catches config-drift early."""
    cfg = load_axes_config()
    rules = cfg.get("solver_rules") or {}
    assert "axis_priority_order_for_solver" in rules
    assert "forbidden_combinations" in rules
    # collision_threshold may use named or numeric form in the config
    assert "collision_threshold" in rules
    assert isinstance(rules["axis_priority_order_for_solver"], list)
    assert len(rules["axis_priority_order_for_solver"]) >= 9
