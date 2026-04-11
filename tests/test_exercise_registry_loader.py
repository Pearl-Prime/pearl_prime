"""Tests for phoenix_v4.planning.exercise_registry_loader."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning.exercise_registry_loader import (
    load_exercise_registry,
    load_journey_templates,
    load_thesis_outcome_map,
)


def test_load_exercise_registry_has_six_exercises():
    reg = load_exercise_registry()
    assert len(reg) == 6
    assert "body_scan_v1" in reg
    assert reg["extended_exhale_v2"].type == "breath"
    assert "awareness" in reg["sensation_tracking_v1"].outcome_tags


def test_load_thesis_outcome_map_dimensions():
    m = load_thesis_outcome_map()
    assert "anxiety_spike" in m
    assert m["burnout_pattern"]["integration"] == pytest.approx(0.7)


def test_load_journey_templates_four_keys():
    tpl = load_journey_templates()
    assert len(tpl) == 4
    assert "anxiety_downshift" in tpl
    assert "phases" in tpl["classic_somatic_entry"]


def test_load_exercise_registry_missing_file_returns_empty(tmp_path: Path):
    reg = load_exercise_registry(path=tmp_path / "nope.yaml")
    assert reg == {}


def test_load_thesis_map_missing_file_returns_empty(tmp_path: Path):
    assert load_thesis_outcome_map(path=tmp_path / "nope.yaml") == {}


def test_load_journey_templates_missing_file_returns_empty(tmp_path: Path):
    assert load_journey_templates(path=tmp_path / "nope.yaml") == {}


def test_exercise_definition_prerequisites_list():
    reg = load_exercise_registry()
    assert "sensation_tracking_v1" in reg["breath_anchor_v1"].prerequisites
