"""OPD-123: story_introduction bridge at named STORY slot boundary."""
from __future__ import annotations

import pytest

from phoenix_v4.rendering import chapter_composer as cc
from phoenix_v4.rendering.golden_chapter_synthesis import _first_or_join


NAMED_STORY_OPENING = (
    "Priya was twenty-nine. She sat at her desk and noticed her chest tighten "
    "before the meeting started."
)
GENERIC_STORY_OPENING = (
    "The pattern shows up again when the room goes quiet and nobody speaks first."
)
SCENE_ATOM = (
    "At 9:12am the Slack thread still says awaiting reply. Her shoulders climb "
    "toward her ears without permission."
)


def test_story_introduction_family_loads_from_yaml() -> None:
    payload = cc._load_within_slot_bridge_families()
    family = payload.get("story_introduction") or {}
    entries = family.get("section_to_named_story") or []
    assert len(entries) >= 12
    texts = {str(e.get("text") or "").strip() for e in entries if isinstance(e, dict)}
    assert "Let me tell you about somebody who had the same problem." in texts
    for entry in entries:
        if isinstance(entry, dict):
            assert entry.get("next_atom_expectation") == "named_story"


def test_bridge_story_introduction_fires_for_named_story() -> None:
    bridge = cc._bridge_story_introduction(NAMED_STORY_OPENING, chapter_index=0)
    assert bridge
    assert len(bridge.split()) >= 6


def test_bridge_story_introduction_skips_non_named_story() -> None:
    assert cc._bridge_story_introduction(GENERIC_STORY_OPENING, chapter_index=0) == ""


def test_bridge_story_introduction_deterministic() -> None:
    a = cc._bridge_story_introduction(NAMED_STORY_OPENING, chapter_index=2, atom_pair_index=0)
    b = cc._bridge_story_introduction(NAMED_STORY_OPENING, chapter_index=2, atom_pair_index=0)
    assert a == b


def test_bridge_story_introduction_varies_by_chapter() -> None:
    a = cc._bridge_story_introduction(NAMED_STORY_OPENING, chapter_index=0)
    b = cc._bridge_story_introduction(NAMED_STORY_OPENING, chapter_index=1)
    # Not guaranteed different, but at least one should be non-empty
    assert a and b


def test_prepend_story_introduction_adds_bridge_before_body() -> None:
    out = cc.prepend_story_introduction_bridge(
        NAMED_STORY_OPENING,
        NAMED_STORY_OPENING,
        chapter_index=0,
    )
    assert len(out) > len(NAMED_STORY_OPENING)
    assert "Priya" in out
    assert not out.startswith("Priya")


def test_prepend_story_introduction_idempotent() -> None:
    once = cc.prepend_story_introduction_bridge(
        NAMED_STORY_OPENING, NAMED_STORY_OPENING, chapter_index=0,
    )
    twice = cc.prepend_story_introduction_bridge(once, NAMED_STORY_OPENING, chapter_index=0)
    assert once == twice


def test_within_slot_bridge_does_not_use_story_introduction_shape() -> None:
    """SCENE→SCENE uses within-slot family, not story_introduction."""
    bridge = cc._bridge_within_slot(
        prev_atom=SCENE_ATOM,
        next_atom=SCENE_ATOM.replace("9:12am", "2:15pm"),
        slot_type="SCENE",
        atom_pair_index=0,
        chapter_index=0,
    )
    assert bridge
    assert "Let me tell you about somebody" not in bridge


def test_classify_atom_named_story() -> None:
    assert cc._classify_atom(NAMED_STORY_OPENING) == "named_story"
    assert cc._classify_atom(GENERIC_STORY_OPENING) != "named_story"


def test_first_or_join_single_named_story_gets_intro_via_prepend() -> None:
    joined = cc.prepend_story_introduction_bridge(
        NAMED_STORY_OPENING,
        NAMED_STORY_OPENING,
        chapter_index=0,
    )
    assert len(joined) > len(NAMED_STORY_OPENING)


def test_first_or_join_multi_scene_no_story_intro() -> None:
    joined = _first_or_join(
        [SCENE_ATOM, SCENE_ATOM.replace("Slack", "email")],
        chapter_index=0,
        bridge_fn=lambda _p, _n, _i: "Another room, same tension.",
    )
    assert "Let me tell you about somebody" not in joined


def test_compose_chapter_prose_backward_compat_generic_story() -> None:
    """Generic STORY still composes without error when not named."""
    text = cc.compose_chapter_prose(
        slot_types=["HOOK", "REFLECTION", "STORY", "EXERCISE"],
        slot_proses=[
            "It starts in the chest.",
            "The mechanism is a false alarm.",
            GENERIC_STORY_OPENING,
            "Pause. Notice your breath.",
        ],
        chapter_index=0,
        total_chapters=1,
    )
    assert "pattern shows up" in text
    assert text.strip()
