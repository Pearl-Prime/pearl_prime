"""ACT-015 — Catalog buying-trigger tests.

Validates config/catalog_planning/catalog_buying_trigger.yaml:
1. File loads and parses without error
2. All 15 canonical topics have a buying-trigger entry
3. Required fields present (desire_type, primary_pain, buying_trigger_phrase, recognition_hook)
4. desire_type values are from the approved vocabulary
5. Recognition hooks are non-empty strings >= 20 characters
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
BUYING_TRIGGER_YAML = REPO_ROOT / "config" / "catalog_planning" / "catalog_buying_trigger.yaml"
CANONICAL_TOPICS_YAML = REPO_ROOT / "config" / "catalog_planning" / "canonical_topics.yaml"

VALID_DESIRE_TYPES = frozenset([
    "relief", "belonging", "certainty", "rest", "self-trust", "visibility", "connection", "courage",
])

REQUIRED_FIELDS = ("desire_type", "primary_pain", "buying_trigger_phrase", "recognition_hook")


@pytest.fixture(scope="module")
def trigger_data():
    assert BUYING_TRIGGER_YAML.exists(), f"catalog_buying_trigger.yaml not found at {BUYING_TRIGGER_YAML}"
    return yaml.safe_load(BUYING_TRIGGER_YAML.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def canonical_topics():
    if not CANONICAL_TOPICS_YAML.exists():
        return []
    data = yaml.safe_load(CANONICAL_TOPICS_YAML.read_text(encoding="utf-8"))
    return list(data.get("topics") or [])


def test_buying_trigger_file_loads(trigger_data):
    assert isinstance(trigger_data, dict)
    assert "topics" in trigger_data


def test_all_canonical_topics_covered(trigger_data, canonical_topics):
    """Every canonical topic must have a buying-trigger entry."""
    if not canonical_topics:
        pytest.skip("canonical_topics.yaml not found — skipping coverage check")
    bt_topics = set(trigger_data.get("topics") or {})
    for topic in canonical_topics:
        assert topic in bt_topics, f"No buying-trigger entry for canonical topic: {topic}"


def test_required_fields_present(trigger_data):
    topics = trigger_data.get("topics") or {}
    for topic, spec in topics.items():
        for field in REQUIRED_FIELDS:
            assert field in spec, f"Missing field '{field}' for topic '{topic}'"
            assert spec[field], f"Empty value for field '{field}' in topic '{topic}'"


def test_desire_type_values_valid(trigger_data):
    topics = trigger_data.get("topics") or {}
    for topic, spec in topics.items():
        dt = spec.get("desire_type", "")
        assert dt in VALID_DESIRE_TYPES, (
            f"Invalid desire_type '{dt}' for topic '{topic}'. "
            f"Must be one of: {sorted(VALID_DESIRE_TYPES)}"
        )


def test_recognition_hooks_substantial(trigger_data):
    """Recognition hooks must be long enough to be meaningful for copy."""
    topics = trigger_data.get("topics") or {}
    for topic, spec in topics.items():
        hook = spec.get("recognition_hook", "")
        assert len(hook) >= 20, f"recognition_hook too short for '{topic}': {hook!r}"


def test_desire_type_distribution(trigger_data):
    """Desire types must not all be the same — buying triggers should be differentiated."""
    topics = trigger_data.get("topics") or {}
    desire_types = [spec.get("desire_type") for spec in topics.values()]
    unique = len(set(desire_types))
    assert unique >= 4, f"Expected >= 4 distinct desire_types across topics, got {unique}"
