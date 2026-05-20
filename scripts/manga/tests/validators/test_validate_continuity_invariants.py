"""Tests for validate_continuity_invariants.py — Phase B.1 step 3.

Per docs/specs/MANGA_LAYER_RENDER_CONTRACT_SPEC.md §6.3.A + §15.A.4.

Synthetic continuity_state fixtures cover pass AND fail cases for each of the
seven deterministic invariants. NO model inference — pure structural checks.

Acceptance criteria (§15.A.4):
  - All §6.3.A deterministic invariants implemented
  - class-A FAIL halts panel build
  - Synthetic fixtures cover pass + fail per invariant
  - Runs in ≤ 500 ms per panel-pair on CPU
  - False-positive rate ≤ 0.5% on synthetic
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[4]
VALIDATOR = REPO / "scripts" / "manga" / "validate_continuity_invariants.py"

sys.path.insert(0, str(REPO / "scripts" / "manga"))
import validate_continuity_invariants as vci  # noqa: E402


# ─────────────────────────────────────────────────────────────────────────────
# canonical fixtures
# ─────────────────────────────────────────────────────────────────────────────


def _load(p: Path) -> dict:
    return yaml.safe_load(p.read_text())


PROP_EVOLUTION = _load(REPO / "config" / "manga" / "continuity" / "prop_evolution.yaml")
TEMPORAL_CYCLE = _load(REPO / "config" / "manga" / "continuity" / "temporal_cycle.yaml")


SCENE_INV = {
    "scenes": [
        {
            "scene_id": "kitchen_table_dawn",
            "light_rigs": [
                {"light_rig_id": "K01_dawn_window_warm"},
                {"light_rig_id": "K02_morning_window_neutral"},
            ],
        },
        {
            "scene_id": "bedroom_night",
            "light_rigs": [{"light_rig_id": "K07_night_lamp_warm"}],
        },
    ],
}

POSE_INV = {
    "mira_aoki": [
        "front_portrait_seated",
        "front_portrait_standing",
        "hands_wrapping_cup",
        "hand_only_reaching",
    ],
}


def _panel_state(
    scene_id="kitchen_table_dawn",
    temporal="dawn",
    light_rig="K01_dawn_window_warm",
    char_hash="mira_v1_abc123",
    pose_id="front_portrait_seated",
    expression_dial=0.3,
    gaze="down_at_cup",
    cup_state="full",
) -> dict:
    return {
        "scene_state": {
            "scene_id": scene_id,
            "temporal": temporal,
            "light_rig_id": light_rig,
        },
        "character_state": {
            "mira_aoki": {
                "character_design_hash": char_hash,
                "pose_id": pose_id,
                "expression_dial": expression_dial,
                "gaze_direction": gaze,
            },
        },
        "prop_state": {
            "cup": cup_state,
        },
    }


def _inp(current, previous, beat_type="micro", **overrides) -> vci.ContinuityValidationInput:
    return vci.ContinuityValidationInput(
        current=current,
        previous=previous,
        beat_type=beat_type,
        scene_inventory=overrides.get("scene_inventory", SCENE_INV),
        prop_evolution=overrides.get("prop_evolution", PROP_EVOLUTION),
        temporal_cycle=overrides.get("temporal_cycle", TEMPORAL_CYCLE),
        character_pose_inventory=overrides.get("character_pose_inventory", POSE_INV),
    )


# ─────────────────────────────────────────────────────────────────────────────
# 1. scene_continuity
# ─────────────────────────────────────────────────────────────────────────────


def test_scene_continuity_same_scene_passes():
    prev = _panel_state()
    curr = _panel_state()
    r = vci.check_scene_continuity(_inp(curr, prev, "micro"))
    assert r.passed


def test_scene_continuity_jump_on_micro_fails():
    prev = _panel_state(scene_id="kitchen_table_dawn")
    curr = _panel_state(scene_id="bedroom_night")
    r = vci.check_scene_continuity(_inp(curr, prev, "micro"))
    assert not r.passed
    assert "scene_jump" not in r.evidence  # micro doesn't allow jump


def test_scene_continuity_jump_on_standard_passes():
    prev = _panel_state(scene_id="kitchen_table_dawn")
    curr = _panel_state(scene_id="bedroom_night")
    r = vci.check_scene_continuity(_inp(curr, prev, "standard"))
    assert r.passed
    assert r.evidence["scene_jump_allowed"] is True


def test_scene_continuity_episode_opener_skipped():
    curr = _panel_state()
    r = vci.check_scene_continuity(_inp(curr, None, "micro"))
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 2. character_identity_continuity (STRUCTURAL)
# ─────────────────────────────────────────────────────────────────────────────


def test_identity_hash_match_passes():
    prev = _panel_state(char_hash="mira_v1_abc123")
    curr = _panel_state(char_hash="mira_v1_abc123")
    r = vci.check_character_identity_continuity(_inp(curr, prev))
    assert r.passed


def test_identity_hash_mismatch_fails():
    prev = _panel_state(char_hash="mira_v1_abc123")
    curr = _panel_state(char_hash="mira_v2_DIFFERENT_xyz")
    r = vci.check_character_identity_continuity(_inp(curr, prev))
    assert not r.passed
    failures = r.evidence["failures"]
    assert failures[0]["character_id"] == "mira_aoki"
    assert failures[0]["reason"] == "character_design_hash mismatch"


def test_identity_pose_in_inventory_passes():
    curr = _panel_state(pose_id="front_portrait_seated")
    r = vci.check_character_identity_continuity(_inp(curr, None))
    assert r.passed


def test_identity_pose_not_in_inventory_fails():
    curr = _panel_state(pose_id="nonexistent_pose")
    r = vci.check_character_identity_continuity(_inp(curr, None))
    assert not r.passed
    assert any("pose_id not declared" in f["reason"] for f in r.evidence["failures"])


def test_identity_new_character_no_prev_passes():
    """A character appearing in current but not prev is fine — new entry on stage."""
    prev = _panel_state()
    curr = _panel_state()
    curr["character_state"]["new_character"] = {
        "character_design_hash": "newhash_456",
        "pose_id": "front_portrait_seated",  # not in POSE_INV but inventory only declared mira
    }
    # POSE_INV only has mira_aoki — new_character isn't there
    r = vci.check_character_identity_continuity(_inp(curr, prev))
    assert not r.passed
    # The failure: new_character not in character_pose_inventory
    assert any("not in character_pose_inventory" in f["reason"] for f in r.evidence["failures"])


def test_identity_no_chars_on_stage_skipped():
    curr = {"scene_state": {"scene_id": "x"}, "character_state": {}, "prop_state": {}}
    r = vci.check_character_identity_continuity(_inp(curr, None))
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 3. prop_persistence
# ─────────────────────────────────────────────────────────────────────────────


def test_prop_same_state_passes():
    prev = _panel_state(cup_state="full")
    curr = _panel_state(cup_state="full")
    r = vci.check_prop_persistence(_inp(curr, prev))
    assert r.passed


def test_prop_adjacent_state_passes():
    prev = _panel_state(cup_state="full")
    curr = _panel_state(cup_state="half")  # adjacent in [empty,half,full,tipped_spilled]
    r = vci.check_prop_persistence(_inp(curr, prev))
    assert r.passed


def test_prop_non_adjacent_state_fails():
    prev = _panel_state(cup_state="empty")
    curr = _panel_state(cup_state="full")  # skipped half
    r = vci.check_prop_persistence(_inp(curr, prev))
    assert not r.passed
    failure = r.evidence["failures"][0]
    assert failure["prop_id"] == "cup"
    assert failure["prev"] == "empty"
    assert failure["current"] == "full"


def test_prop_episode_opener_skipped():
    curr = _panel_state()
    r = vci.check_prop_persistence(_inp(curr, None))
    assert r.skipped


def test_prop_no_config_fails():
    prev = _panel_state()
    curr = _panel_state()
    inp = vci.ContinuityValidationInput(
        current=curr, previous=prev, beat_type="micro",
        scene_inventory=SCENE_INV, prop_evolution=None,
        temporal_cycle=TEMPORAL_CYCLE,
    )
    r = vci.check_prop_persistence(inp)
    assert not r.passed
    assert "prop_evolution config not supplied" in r.evidence["reason"]


def test_prop_unknown_type_fails():
    prev = _panel_state()
    curr = _panel_state()
    prev["prop_state"]["mystery_object"] = "weird_state_1"
    curr["prop_state"]["mystery_object"] = "weird_state_2"
    r = vci.check_prop_persistence(_inp(curr, prev))
    assert not r.passed
    failures = r.evidence["failures"]
    assert any(f["prop_id"] == "mystery_object" for f in failures)


# ─────────────────────────────────────────────────────────────────────────────
# 4. gaze_target_validity
# ─────────────────────────────────────────────────────────────────────────────


def test_gaze_object_present_passes():
    curr = _panel_state()
    curr["character_state"]["mira_aoki"]["gaze_direction"] = "at_named_object_cup"
    r = vci.check_gaze_target_validity(_inp(curr, None))
    assert r.passed


def test_gaze_object_absent_fails():
    curr = _panel_state()
    curr["character_state"]["mira_aoki"]["gaze_direction"] = "at_named_object_kettle"
    # kettle not in prop_state (only cup is)
    r = vci.check_gaze_target_validity(_inp(curr, None))
    assert not r.passed
    failures = r.evidence["failures"]
    assert failures[0]["target_kind"] == "object"
    assert failures[0]["target"] == "kettle"


def test_gaze_character_present_passes():
    curr = _panel_state()
    curr["character_state"]["mira_aoki"]["gaze_direction"] = "at_named_character_mira_aoki"
    r = vci.check_gaze_target_validity(_inp(curr, None))
    assert r.passed


def test_gaze_character_absent_fails():
    curr = _panel_state()
    curr["character_state"]["mira_aoki"]["gaze_direction"] = "at_named_character_unknown_friend"
    r = vci.check_gaze_target_validity(_inp(curr, None))
    assert not r.passed


def test_gaze_off_frame_passes():
    curr = _panel_state()
    curr["character_state"]["mira_aoki"]["gaze_direction"] = "off_frame_left"
    r = vci.check_gaze_target_validity(_inp(curr, None))
    assert r.passed  # not at_named_X — no target validation


def test_gaze_no_chars_skipped():
    curr = {"scene_state": {}, "character_state": {}, "prop_state": {}}
    r = vci.check_gaze_target_validity(_inp(curr, None))
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 5. temporal_continuity
# ─────────────────────────────────────────────────────────────────────────────


def test_temporal_same_value_passes():
    prev = _panel_state(temporal="dawn")
    curr = _panel_state(temporal="dawn")
    r = vci.check_temporal_continuity(_inp(curr, prev, "micro"))
    assert r.passed


def test_temporal_next_in_cycle_passes():
    prev = _panel_state(temporal="dawn")
    curr = _panel_state(temporal="morning")
    r = vci.check_temporal_continuity(_inp(curr, prev, "micro"))
    assert r.passed


def test_temporal_jump_on_micro_fails():
    prev = _panel_state(temporal="dawn")
    curr = _panel_state(temporal="night")  # huge jump
    r = vci.check_temporal_continuity(_inp(curr, prev, "micro"))
    assert not r.passed


def test_temporal_jump_on_standard_passes():
    prev = _panel_state(temporal="dawn")
    curr = _panel_state(temporal="night")
    r = vci.check_temporal_continuity(_inp(curr, prev, "standard"))
    assert r.passed  # exemption


def test_temporal_wraps_night_to_dawn():
    prev = _panel_state(temporal="night")
    curr = _panel_state(temporal="dawn")
    r = vci.check_temporal_continuity(_inp(curr, prev, "micro"))
    assert r.passed  # wraps via cycle


def test_temporal_episode_opener_skipped():
    curr = _panel_state()
    r = vci.check_temporal_continuity(_inp(curr, None, "micro"))
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 6. expression_dial_bounded_delta
# ─────────────────────────────────────────────────────────────────────────────


def test_dial_micro_small_delta_passes():
    prev = _panel_state(expression_dial=0.3)
    curr = _panel_state(expression_dial=0.5)  # delta 0.2, micro bound 0.3
    r = vci.check_expression_dial_bounded_delta(_inp(curr, prev, "micro"))
    assert r.passed


def test_dial_micro_large_delta_fails():
    prev = _panel_state(expression_dial=0.2)
    curr = _panel_state(expression_dial=0.8)  # delta 0.6, micro bound 0.3
    r = vci.check_expression_dial_bounded_delta(_inp(curr, prev, "micro"))
    assert not r.passed
    failure = r.evidence["failures"][0]
    assert failure["delta"] == 0.6


def test_dial_spatial_medium_delta_passes():
    prev = _panel_state(expression_dial=0.2)
    curr = _panel_state(expression_dial=0.6)  # delta 0.4, spatial bound 0.5
    r = vci.check_expression_dial_bounded_delta(_inp(curr, prev, "spatial"))
    assert r.passed


def test_dial_spatial_large_delta_fails():
    prev = _panel_state(expression_dial=0.1)
    curr = _panel_state(expression_dial=0.9)  # delta 0.8, spatial bound 0.5
    r = vci.check_expression_dial_bounded_delta(_inp(curr, prev, "spatial"))
    assert not r.passed


def test_dial_standard_unbounded_passes():
    prev = _panel_state(expression_dial=0.0)
    curr = _panel_state(expression_dial=1.0)  # delta 1.0, standard unbounded
    r = vci.check_expression_dial_bounded_delta(_inp(curr, prev, "standard"))
    assert r.passed


def test_dial_episode_opener_skipped():
    curr = _panel_state()
    r = vci.check_expression_dial_bounded_delta(_inp(curr, None, "micro"))
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 7. light_rig_within_scene
# ─────────────────────────────────────────────────────────────────────────────


def test_light_rig_declared_passes():
    curr = _panel_state(scene_id="kitchen_table_dawn", light_rig="K01_dawn_window_warm")
    r = vci.check_light_rig_within_scene(_inp(curr, None))
    assert r.passed


def test_light_rig_other_declared_passes():
    """Second rig declared for the same scene also valid."""
    curr = _panel_state(scene_id="kitchen_table_dawn", light_rig="K02_morning_window_neutral")
    r = vci.check_light_rig_within_scene(_inp(curr, None))
    assert r.passed


def test_light_rig_undeclared_for_scene_fails():
    curr = _panel_state(scene_id="kitchen_table_dawn", light_rig="K99_alien_lighting")
    r = vci.check_light_rig_within_scene(_inp(curr, None))
    assert not r.passed
    assert r.evidence["scene_id"] == "kitchen_table_dawn"
    assert r.evidence["rig_id"] == "K99_alien_lighting"


def test_light_rig_wrong_scene_fails():
    """K07 is declared for bedroom_night, not kitchen_table_dawn."""
    curr = _panel_state(scene_id="kitchen_table_dawn", light_rig="K07_night_lamp_warm")
    r = vci.check_light_rig_within_scene(_inp(curr, None))
    assert not r.passed


def test_light_rig_unknown_scene_fails():
    curr = _panel_state(scene_id="nonexistent_scene", light_rig="K01_dawn_window_warm")
    r = vci.check_light_rig_within_scene(_inp(curr, None))
    assert not r.passed


def test_light_rig_missing_skipped():
    curr = _panel_state(scene_id="kitchen_table_dawn", light_rig=None)
    curr["scene_state"]["light_rig_id"] = None
    r = vci.check_light_rig_within_scene(_inp(curr, None))
    assert r.skipped


# ─────────────────────────────────────────────────────────────────────────────
# 8. orchestration + all_class_a_passed
# ─────────────────────────────────────────────────────────────────────────────


def test_validate_continuity_all_pass():
    prev = _panel_state()
    curr = _panel_state(expression_dial=0.4)  # +0.1 delta, OK on micro
    results = vci.validate_continuity(_inp(curr, prev, "micro"))
    assert vci.all_class_a_passed(results), \
        f"failures: {[(r.check_id, r.evidence) for r in results if not r.passed]}"


def test_validate_continuity_multiple_failures():
    """Cluster of violations: scene jump on micro + huge dial delta + non-adjacent prop."""
    prev = _panel_state(scene_id="kitchen_table_dawn", expression_dial=0.0, cup_state="empty")
    curr = _panel_state(scene_id="bedroom_night", expression_dial=1.0, cup_state="full")
    results = vci.validate_continuity(_inp(curr, prev, "micro"))
    failed = [r for r in results if not r.passed]
    failed_ids = {r.check_id for r in failed}
    assert "scene_continuity" in failed_ids
    assert "expression_dial_bounded_delta" in failed_ids
    assert "prop_persistence" in failed_ids


# ─────────────────────────────────────────────────────────────────────────────
# 9. performance: ≤ 500 ms per panel-pair (§15.A.4)
# ─────────────────────────────────────────────────────────────────────────────


def test_validator_runs_under_500ms():
    prev = _panel_state()
    curr = _panel_state(expression_dial=0.4)
    t0 = time.time()
    for _ in range(10):
        results = vci.validate_continuity(_inp(curr, prev, "micro"))
    elapsed = (time.time() - t0) / 10
    assert elapsed < 0.5, f"per-pair {elapsed*1000:.1f}ms (limit 500ms per §15.A.4)"


# ─────────────────────────────────────────────────────────────────────────────
# 10. CLI smoke
# ─────────────────────────────────────────────────────────────────────────────


def test_cli_pass(tmp_path: Path):
    prev_path = tmp_path / "prev.yaml"
    curr_path = tmp_path / "curr.yaml"
    scene_path = tmp_path / "scene_inv.yaml"
    pose_path = tmp_path / "pose_inv.yaml"
    prev_path.write_text(yaml.safe_dump(_panel_state()))
    curr_path.write_text(yaml.safe_dump(_panel_state(expression_dial=0.4)))
    scene_path.write_text(yaml.safe_dump(SCENE_INV))
    pose_path.write_text(yaml.safe_dump(POSE_INV))
    r = subprocess.run(
        [
            sys.executable, str(VALIDATOR),
            "--current", str(curr_path),
            "--previous", str(prev_path),
            "--beat-type", "micro",
            "--scene-inventory", str(scene_path),
            "--character-pose-inventory", str(pose_path),
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 0, f"stdout={r.stdout}\nstderr={r.stderr}"
    assert "[PASS] scene_continuity" in r.stdout


def test_cli_fail_returns_1(tmp_path: Path):
    prev_path = tmp_path / "prev.yaml"
    curr_path = tmp_path / "curr.yaml"
    scene_path = tmp_path / "scene_inv.yaml"
    pose_path = tmp_path / "pose_inv.yaml"
    prev_path.write_text(yaml.safe_dump(_panel_state(scene_id="kitchen_table_dawn")))
    curr_path.write_text(yaml.safe_dump(_panel_state(scene_id="bedroom_night")))
    scene_path.write_text(yaml.safe_dump(SCENE_INV))
    pose_path.write_text(yaml.safe_dump(POSE_INV))
    r = subprocess.run(
        [
            sys.executable, str(VALIDATOR),
            "--current", str(curr_path),
            "--previous", str(prev_path),
            "--beat-type", "micro",
            "--scene-inventory", str(scene_path),
            "--character-pose-inventory", str(pose_path),
        ],
        capture_output=True, text=True,
    )
    assert r.returncode == 1
    assert "[FAIL] scene_continuity" in r.stdout
