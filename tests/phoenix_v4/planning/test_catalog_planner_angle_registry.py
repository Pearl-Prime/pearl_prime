"""CatalogPlanner angle resolution vs config/angles/angle_registry.yaml (P0-2)."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from phoenix_v4.planning.catalog_planner import AngleResolutionError, CatalogPlanner


def _write(p: Path, text: str) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def _minimal_series() -> str:
    return "series: {}\n"


def _minimal_domain() -> str:
    return "domains: {}\n"


def _minimal_capacity() -> str:
    return "capacity: {}\n"


def _minimal_brands() -> str:
    return """
    brands:
      phoenix:
        locale: en-US
        territory: US
    """


def _make_planner(tmp: Path, angle_registry_body: str) -> CatalogPlanner:
    _write(tmp / "domain_definitions.yaml", _minimal_domain())
    _write(tmp / "series_templates.yaml", _minimal_series())
    _write(tmp / "capacity_constraints.yaml", _minimal_capacity())
    _write(tmp / "brands.yaml", _minimal_brands())
    _write(tmp / "angle_registry.yaml", angle_registry_body)
    return CatalogPlanner(
        domain_path=tmp / "domain_definitions.yaml",
        series_path=tmp / "series_templates.yaml",
        capacity_path=tmp / "capacity_constraints.yaml",
        brands_path=tmp / "brands.yaml",
        locale_registry_path=None,
        angle_registry_path=tmp / "angle_registry.yaml",
    )


def test_registry_hit_topic_angle_map(tmp_path: Path) -> None:
    reg = """
    angles:
      REG_HIT:
        arc_variant: ARC_STANDARD_A_v2
        chapter_1_role_bias: destabilization
        integration_reinforcement_type: problem_inversion
        framing_mode: debunk
    catalog_planner_resolution:
      version: 1
      topic_angle_map:
        alpha_topic: REG_HIT
    """
    p = _make_planner(tmp_path, reg)
    spec = p.produce_single("alpha_topic", "any_persona", brand_id="phoenix")
    assert spec.angle_id == "REG_HIT"
    m = p.last_angle_resolution_meta()
    assert m.get("registry_hit") is True
    assert m.get("source") == "angle_registry.topic_angle_map"


def test_registry_miss_uses_topic_general_fallback(tmp_path: Path) -> None:
    reg = """
    angles:
      REG_HIT:
        arc_variant: ARC_STANDARD_A_v2
        chapter_1_role_bias: destabilization
        integration_reinforcement_type: problem_inversion
        framing_mode: debunk
    catalog_planner_resolution:
      version: 1
      topic_angle_map:
        other_topic: REG_HIT
    """
    p = _make_planner(tmp_path, reg)
    spec = p.produce_single("lonely_topic", "any_persona", brand_id="phoenix", angle_strict=False)
    assert spec.angle_id == "lonely_topic_general"
    m = p.last_angle_resolution_meta()
    assert m.get("heuristic_general_fallback") is True
    assert m.get("source") == "topic_general_fallback"


def test_registry_miss_strict_raises(tmp_path: Path) -> None:
    reg = """
    angles:
      REG_HIT:
        arc_variant: ARC_STANDARD_A_v2
        chapter_1_role_bias: destabilization
        integration_reinforcement_type: problem_inversion
        framing_mode: debunk
    catalog_planner_resolution:
      version: 1
      topic_angle_map:
        other_topic: REG_HIT
    """
    p = _make_planner(tmp_path, reg)
    with pytest.raises(AngleResolutionError):
        p.produce_single("lonely_topic", "any_persona", brand_id="phoenix", angle_strict=True)


def test_live_registry_maps_relationship_anxiety_to_familiar_wound() -> None:
    """Integration: repo angle_registry.yaml v2 declares relationship_anxiety → FAMILIAR_WOUND
    (previously HIDDEN_TRUTH under v1; remapped per docs/plans/ANGLE_CATALOG_V2_2026-05-20.md §6)."""
    p = CatalogPlanner()
    spec = p.produce_single("relationship_anxiety", "nyc_exec", brand_id="phoenix")
    assert spec.angle_id == "FAMILIAR_WOUND"
    meta = p.last_angle_resolution_meta()
    assert meta.get("registry_hit") is True
    assert meta.get("registry_angle_id") == "FAMILIAR_WOUND"
