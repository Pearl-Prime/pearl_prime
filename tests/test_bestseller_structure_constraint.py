"""BG-PR-09: bestseller structure beat order gate (bestseller_structure_map + config flag)."""
from __future__ import annotations

import logging

import pytest

from phoenix_v4.planning.bestseller_structure_map import (
    BESTSELLER_BEAT_STEPS,
    apply_bestseller_beat_order_gate,
    collect_bestseller_beat_order_violations,
    describe_expected_beat_order,
    normalize_structure_key,
    validate_chapter_beat_order,
)
from phoenix_v4.planning.chapter_planner import BESTSELLER_STRUCTURES


def test_completeness_all_twelve_structures_in_map() -> None:
    assert set(BESTSELLER_BEAT_STEPS.keys()) == set(BESTSELLER_STRUCTURES)
    assert len(BESTSELLER_BEAT_STEPS) == 12


def test_normalize_structure_key() -> None:
    assert normalize_structure_key("  Promise Engine ") == "promise_engine"
    assert normalize_structure_key("gladwell-spiral") == "gladwell_spiral"


def test_promise_engine_valid_sc_then_story() -> None:
    slots = [
        "HOOK",
        "SCENE",
        "STORY",
        "PIVOT",
        "REFLECTION",
        "EXERCISE",
        "TAKEAWAY",
        "INTEGRATION",
        "THREAD",
    ]
    assert validate_chapter_beat_order("promise_engine", slots) is None


def test_promise_engine_valid_story_story() -> None:
    slots = [
        "HOOK",
        "STORY",
        "STORY",
        "PIVOT",
        "REFLECTION",
        "EXERCISE",
        "TAKEAWAY",
        "INTEGRATION",
        "THREAD",
    ]
    assert validate_chapter_beat_order("promise_engine", slots) is None


def test_promise_engine_optional_permission_present() -> None:
    slots = [
        "HOOK",
        "SCENE",
        "STORY",
        "PIVOT",
        "REFLECTION",
        "EXERCISE",
        "TAKEAWAY",
        "INTEGRATION",
        "PERMISSION",
        "THREAD",
    ]
    assert validate_chapter_beat_order("promise_engine", slots) is None


def test_promise_engine_wrong_order_fails_validation() -> None:
    # Second beat must be SCENE|STORY before the build-mechanism STORY; PIVOT too early.
    slots = [
        "HOOK",
        "PIVOT",
        "SCENE",
        "STORY",
        "REFLECTION",
        "EXERCISE",
        "TAKEAWAY",
        "INTEGRATION",
        "THREAD",
    ]
    err = validate_chapter_beat_order("promise_engine", slots)
    assert err is not None
    assert "SCENE|STORY" in err or "expected" in err.lower()


def test_compression_ignored_in_sequence() -> None:
    slots = [
        "HOOK",
        "COMPRESSION",
        "SCENE",
        "STORY",
        "PIVOT",
        "REFLECTION",
        "EXERCISE",
        "TAKEAWAY",
        "INTEGRATION",
        "THREAD",
    ]
    assert validate_chapter_beat_order("promise_engine", slots) is None


def test_chapter_no_structure_skipped() -> None:
    seq = [["HOOK", "SCENE", "STORY"]]
    assert (
        collect_bestseller_beat_order_violations(
            chapter_slot_sequence=seq,
            chapter_bestseller_structures=[""],
            chapter_count=1,
        )
        == []
    )
    assert (
        collect_bestseller_beat_order_violations(
            chapter_slot_sequence=seq,
            chapter_bestseller_structures=None,
            chapter_count=1,
        )
        == []
    )


def test_enforce_raises_on_mismatch() -> None:
    slots = [
        "HOOK",
        "PIVOT",
        "SCENE",
        "STORY",
        "REFLECTION",
        "EXERCISE",
        "TAKEAWAY",
        "INTEGRATION",
        "THREAD",
    ]
    with pytest.raises(ValueError) as ei:
        apply_bestseller_beat_order_gate(
            chapter_slot_sequence=[slots],
            chapter_bestseller_structures=["promise_engine"],
            chapter_count=1,
            enforce=True,
        )
    assert "promise_engine" in str(ei.value).lower() or "Bestseller beat order" in str(ei.value)


def test_no_enforce_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)
    slots = [
        "HOOK",
        "PIVOT",
        "SCENE",
        "STORY",
        "REFLECTION",
        "EXERCISE",
        "TAKEAWAY",
        "INTEGRATION",
        "THREAD",
    ]
    apply_bestseller_beat_order_gate(
        chapter_slot_sequence=[slots],
        chapter_bestseller_structures=["promise_engine"],
        chapter_count=1,
        enforce=False,
    )
    assert any("bestseller_beat_order:" in r.getMessage() for r in caplog.records)
    assert any("chapter 1" in r.getMessage() for r in caplog.records)


def test_violation_messages_deterministic() -> None:
    slots = [
        "HOOK",
        "PIVOT",
        "SCENE",
        "STORY",
        "REFLECTION",
        "EXERCISE",
        "TAKEAWAY",
        "INTEGRATION",
        "THREAD",
    ]
    a = collect_bestseller_beat_order_violations(
        chapter_slot_sequence=[slots],
        chapter_bestseller_structures=["promise_engine"],
        chapter_count=1,
    )
    b = collect_bestseller_beat_order_violations(
        chapter_slot_sequence=[slots],
        chapter_bestseller_structures=["promise_engine"],
        chapter_count=1,
    )
    assert a == b
    assert len(a) == 1


def test_describe_expected_stable() -> None:
    s = describe_expected_beat_order("gladwell_spiral")
    assert "HOOK" in s and "THREAD" in s
    assert describe_expected_beat_order("gladwell_spiral") == s
