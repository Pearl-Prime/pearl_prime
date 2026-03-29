from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_pipeline import (  # noqa: E402
    ALIASES_PATH,
    _count_proseful_sections,
    _topic_source_readiness_issues,
    resolve_to_canonical,
)


def test_resolve_to_canonical_preserves_supported_overthinking_topic() -> None:
    topic, persona = resolve_to_canonical(
        ALIASES_PATH,
        "overthinking",
        "gen_z_professionals",
        repo_root=REPO_ROOT,
        arc_topic="overthinking",
    )

    assert topic == "overthinking"
    assert persona == "gen_z_professionals"


def test_resolve_to_canonical_keeps_legacy_relationship_anxiety_alias() -> None:
    topic, persona = resolve_to_canonical(
        ALIASES_PATH,
        "relationship_anxiety",
        "gen_z",
        repo_root=REPO_ROOT,
    )

    assert topic == "anxiety"
    assert persona == "gen_z_professionals"


def test_count_proseful_sections_overthinking_scene_bank_is_proseful() -> None:
    scene_path = REPO_ROOT / "atoms" / "gen_z_professionals" / "overthinking" / "SCENE" / "CANONICAL.txt"

    # PR-S1: 20 scene variants with substantive body prose each (see SOURCE_BANK_REPAIR_DEV_SPEC).
    assert _count_proseful_sections(scene_path) == 20


def test_topic_source_readiness_overthinking_spiral_has_scene_and_story() -> None:
    issues = _topic_source_readiness_issues(
        persona_id="gen_z_professionals",
        topic_id="overthinking",
        engine_id="spiral",
    )

    assert issues == []
