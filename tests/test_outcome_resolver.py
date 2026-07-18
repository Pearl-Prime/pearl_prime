"""Tests for phoenix_v4.planning.outcome_resolver."""
from __future__ import annotations

import pytest

from phoenix_v4.planning.exercise_registry_loader import ExerciseDefinition, load_exercise_registry
from phoenix_v4.planning.outcome_resolver import (
    check_prerequisites,
    check_redundancy,
    resolve_combined_outcome,
    validate_required_outcome,
)


@pytest.fixture
def registry():
    return load_exercise_registry()


def test_resolve_combined_outcome_uses_explicit_scores(registry):
    # extended_exhale_v2 carries explicit outcome_scores (reg 0.90, aw 0.15),
    # which supersede the legacy equal-weight tag split.
    out = resolve_combined_outcome(["extended_exhale_v2"], registry)
    assert out["regulation"] == pytest.approx(0.90)
    assert out["awareness"] == pytest.approx(0.15)


def test_resolve_combined_outcome_single_awareness_exercise(registry):
    # body_scan_v1 delivers strong awareness (0.92) instead of the old 0.5 cap.
    out = resolve_combined_outcome(["body_scan_v1"], registry)
    assert out["awareness"] == pytest.approx(0.92)
    assert out["regulation"] == pytest.approx(0.55)


def test_resolve_combined_outcome_probabilistic_or_combine(registry):
    # Two exercises reinforce a dimension via 1 - prod(1 - s), never exceeding 1.0.
    out = resolve_combined_outcome(["body_scan_v1", "extended_exhale_v2"], registry)
    # awareness: 1 - (1-0.92)(1-0.15) = 0.932
    assert out["awareness"] == pytest.approx(0.932)
    # regulation: 1 - (1-0.55)(1-0.90) = 0.955
    assert out["regulation"] == pytest.approx(0.955)
    assert 0.0 <= out["integration"] <= 1.0


def test_resolve_combined_outcome_falls_back_to_equal_split(registry):
    # An exercise WITHOUT explicit outcome_scores still uses the legacy split.
    legacy = ExerciseDefinition(
        exercise_id="legacy_two_tag",
        type="somatic",
        phase_fit=[],
        section_fit=[],
        effects=[],
        intensity="low",
        prerequisites=[],
        compatible_with=[],
        outcome_tags=["awareness", "regulation"],
    )
    out = resolve_combined_outcome(["legacy_two_tag"], {"legacy_two_tag": legacy})
    assert out["awareness"] == pytest.approx(0.5)
    assert out["regulation"] == pytest.approx(0.5)


def test_validate_required_passes(registry):
    actual = resolve_combined_outcome(
        ["sensation_tracking_v1", "extended_exhale_v2", "grounding_anchor_v1"],
        registry,
    )
    required = {"awareness": 0.5, "regulation": 0.5, "integration": 0.3}
    ok, viol = validate_required_outcome(required, actual)
    assert ok
    assert viol == []


def test_validate_required_fails_low_awareness(registry):
    actual = resolve_combined_outcome(["extended_exhale_v2"], registry)
    ok, viol = validate_required_outcome({"awareness": 0.9}, actual)
    assert not ok
    assert any("awareness" in v for v in viol)


def test_check_prerequisites_breath_anchor_requires_tracking(registry):
    viol = check_prerequisites(["breath_anchor_v1"], registry)
    assert any("prerequisite" in v for v in viol)


def test_check_prerequisites_satisfied_order(registry):
    viol = check_prerequisites(
        ["sensation_tracking_v1", "breath_anchor_v1"],
        registry,
    )
    assert viol == []


def test_check_redundancy_two_breath_warns(registry):
    ex = dict(registry)
    ex["fake_breath"] = ExerciseDefinition(
        exercise_id="fake_breath",
        type="breath",
        phase_fit=[],
        section_fit=[],
        effects=[],
        intensity="low",
        prerequisites=[],
        compatible_with=[],
        outcome_tags=["regulation"],
    )
    w = check_redundancy(["extended_exhale_v2", "fake_breath"], ex)
    assert w and "redundant_breath" in w[0]


def test_check_redundancy_single_breath_ok(registry):
    assert check_redundancy(["extended_exhale_v2", "grounding_anchor_v1"], registry) == []
