"""OPD-124: canonical chapter sequence enforcement in chapter_planner."""
from __future__ import annotations

import pytest

from phoenix_v4.planning.chapter_planner import (
    enforce_canonical_chapter_sequence,
    load_chapter_structure_template,
    plan_chapters,
    validate_named_story_slot_expectations,
)
from phoenix_v4.quality.chapter_flow_gate import (
    evaluate_canonical_sequence_compliance,
)


def test_chapter_structure_template_loads() -> None:
    tmpl = load_chapter_structure_template()
    assert tmpl.get("schema_version") == 1
    roles = [e["slot_role"] for e in tmpl.get("canonical_chapter_sequence") or []]
    assert roles == [
        "hook",
        "scene_or_section",
        "first_section_content",
        "named_story",
        "teacher_insight",
        "exercise",
        "close",
    ]


def test_deep_book_6h_reorders_story_after_section() -> None:
    messy = ["HOOK", "STORY", "REFLECTION", "EXERCISE", "STORY", "TEACHER_DOCTRINE", "INTEGRATION"]
    ordered, roles, _warnings = enforce_canonical_chapter_sequence(
        messy, runtime_format="deep_book_6h", chapter_index=0,
    )
    assert ordered.index("HOOK") < ordered.index("REFLECTION")
    assert ordered.index("REFLECTION") < ordered.index("STORY")
    assert "hook" in roles
    assert "named_story" in roles


def test_deep_book_6h_all_seven_roles_mapped() -> None:
    row = [
        "HOOK",
        "SCENE",
        "REFLECTION",
        "STORY",
        "TEACHER_DOCTRINE",
        "EXERCISE",
        "INTEGRATION",
    ]
    _ordered, roles, warnings = enforce_canonical_chapter_sequence(
        row, runtime_format="deep_book_6h", chapter_index=0,
    )
    canonical = {
        "hook",
        "scene_or_section",
        "first_section_content",
        "named_story",
        "teacher_insight",
        "exercise",
        "close",
    }
    assert canonical <= set(roles)
    assert not any("missing hook" in w for w in warnings)


def test_micro_book_15_allows_collapsed_scene() -> None:
    row = ["HOOK", "REFLECTION", "STORY", "EXERCISE", "INTEGRATION"]
    ordered, roles, warnings = enforce_canonical_chapter_sequence(
        row, runtime_format="micro_book_15", chapter_index=0,
    )
    assert ordered == row
    assert "hook" in roles
    assert any("collapse" in w.lower() or "no SCENE" in w for w in warnings)


def test_scene_capped_at_two_before_story() -> None:
    row = ["HOOK", "SCENE", "SCENE", "SCENE", "REFLECTION", "STORY", "INTEGRATION"]
    ordered, _roles, warnings = enforce_canonical_chapter_sequence(
        row, runtime_format="deep_book_6h", chapter_index=0,
    )
    assert ordered.count("SCENE") == 2
    assert any("SCENE count" in w for w in warnings)


def test_plan_chapters_emits_slot_roles_for_long_form() -> None:
    grid = [
        ["HOOK", "STORY", "REFLECTION", "EXERCISE", "STORY", "TEACHER_DOCTRINE", "INTEGRATION"],
    ]
    result = plan_chapters(
        slot_definitions=grid,
        chapter_count=1,
        selector_key_prefix="test-opd124",
        runtime_format="deep_book_6h",
    )
    assert result.chapter_slot_roles is not None
    assert len(result.chapter_slot_roles) == 1
    assert "hook" in result.chapter_slot_roles[0]
    assert result.slot_definitions[0].index("REFLECTION") < result.slot_definitions[0].index(
        "STORY"
    )


def test_enforce_warns_missing_scene_long_form() -> None:
    row = ["HOOK", "REFLECTION", "STORY", "TEACHER_DOCTRINE", "EXERCISE", "INTEGRATION"]
    _ordered, _roles, warnings = enforce_canonical_chapter_sequence(
        row, runtime_format="deep_book_6h", chapter_index=0,
    )
    assert any("scene_or_section" in w or "SCENE" in w for w in warnings)


def test_validate_named_story_short_atom_warns() -> None:
    short = "Kenji sat. He worried."
    warnings = validate_named_story_slot_expectations(short, chapter_index=0, min_words=200)
    assert any("short" in w for w in warnings)


def test_validate_named_story_named_character_ok() -> None:
    long_named = "Mara was thirty-four. " + "She noticed her breath. " * 40
    warnings = validate_named_story_slot_expectations(long_named, chapter_index=0, min_words=50)
    assert not any("named-character" in w for w in warnings)


def test_canonical_sequence_compliance_passes_ordered_slots() -> None:
    slots = [
        "HOOK",
        "SCENE",
        "REFLECTION",
        "STORY",
        "TEACHER_DOCTRINE",
        "EXERCISE",
        "INTEGRATION",
    ]
    warnings = evaluate_canonical_sequence_compliance(
        slots, runtime_format_id="deep_book_6h",
    )
    assert not any("violation" in w for w in warnings)
    assert not any("STORY before" in w for w in warnings)


def test_canonical_sequence_compliance_warns_story_before_reflection() -> None:
    slots = ["HOOK", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION"]
    warnings = evaluate_canonical_sequence_compliance(
        slots, runtime_format_id="deep_book_6h",
    )
    assert any("STORY before" in w or "violation" in w or "missing" in w for w in warnings)


def test_canonical_sequence_ignored_for_micro() -> None:
    slots = ["HOOK", "STORY", "REFLECTION"]
    warnings = evaluate_canonical_sequence_compliance(
        slots, runtime_format_id="micro_book_15",
    )
    assert warnings == []
