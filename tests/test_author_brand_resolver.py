"""Tests for phoenix_v4.planning.author_brand_resolver.

Regression lock for the topic-affinity shadowing bug: a catch-all brand-default
row placed BEFORE the topic-specific rows must not shadow them. Selection is by
specificity, not file order.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand

REPO_ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def assignments_file(tmp_path: Path) -> Path:
    """Catch-all row FIRST, then narrower topic/persona rows — the buggy ordering."""
    data = {
        "assignments": [
            # Catch-all brand default (no constraints) — intentionally first.
            {"brand_id": "demo_press", "default_author": "casey_default"},
            {"brand_id": "demo_press", "topic_ids": ["burnout"], "default_author": "dana_burnout"},
            {"brand_id": "demo_press", "topic_ids": ["grief"], "default_author": "mira_grief"},
            {
                "brand_id": "demo_press",
                "topic_ids": ["anxiety"],
                "persona_ids": ["gen_z"],
                "default_author": "kai_genz_anxiety",
            },
            # Brand whose only row explicitly suppresses authorship.
            {"brand_id": "null_press", "default_author": None},
        ]
    }
    p = tmp_path / "brand_author_assignments.yaml"
    p.write_text(yaml.safe_dump(data), encoding="utf-8")
    return p


def test_topic_row_beats_earlier_catch_all(assignments_file: Path):
    # Regression: catch-all is first in the file but the topic row must still win.
    assert (
        resolve_author_from_brand("demo_press", topic_id="burnout", assignments_path=assignments_file)
        == "dana_burnout"
    )
    assert (
        resolve_author_from_brand("demo_press", topic_id="grief", assignments_path=assignments_file)
        == "mira_grief"
    )


def test_unknown_topic_falls_back_to_catch_all(assignments_file: Path):
    assert (
        resolve_author_from_brand("demo_press", topic_id="somatic_healing", assignments_path=assignments_file)
        == "casey_default"
    )


def test_no_topic_uses_catch_all_default(assignments_file: Path):
    # With no topic supplied, no row pins anything → catch-all (first score-0 row) wins.
    assert (
        resolve_author_from_brand("demo_press", assignments_path=assignments_file) == "casey_default"
    )


def test_more_specific_persona_plus_topic_wins(assignments_file: Path):
    # Row pinning topic+persona (score 2) outranks the topic-only row (score 1).
    assert (
        resolve_author_from_brand(
            "demo_press", topic_id="anxiety", persona_id="gen_z", assignments_path=assignments_file
        )
        == "kai_genz_anxiety"
    )


def test_unknown_brand_returns_none(assignments_file: Path):
    assert resolve_author_from_brand("no_such_brand", topic_id="burnout", assignments_path=assignments_file) is None


def test_null_default_author_returns_none(assignments_file: Path):
    assert resolve_author_from_brand("null_press", assignments_path=assignments_file) is None


def test_empty_brand_returns_none(assignments_file: Path):
    assert resolve_author_from_brand("", topic_id="burnout", assignments_path=assignments_file) is None


def test_shipped_config_routes_stillness_press_by_topic():
    """Integration: the real shipped config must route stillness_press by topic."""
    cfg = REPO_ROOT / "config" / "brand_author_assignments.yaml"
    if not cfg.exists():
        pytest.skip("brand_author_assignments.yaml not present")
    assert resolve_author_from_brand("stillness_press", topic_id="anxiety", assignments_path=cfg) == "lena_thorne"
    assert resolve_author_from_brand("stillness_press", topic_id="burnout", assignments_path=cfg) == "daniel_voss"
    assert resolve_author_from_brand("stillness_press", topic_id="grief", assignments_path=cfg) == "mira_santos"
    assert resolve_author_from_brand("stillness_press", topic_id="overthinking", assignments_path=cfg) == "kai_okafor"
