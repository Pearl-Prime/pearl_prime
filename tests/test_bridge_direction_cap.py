"""Unit tests for the A1 chapter-direction cap in chapter_composer (Phase B 2026-06-16).

The scene_anchor_density gate FAILed on the courage proof book because every entry in a
(bridge_type, emotional_job) block of bridge_transition_families.yaml shares one embedded
chapter-direction substring (e.g. all `recognition` entries contain
"seeing the pattern before defending it"). BridgeMemory dedups by exact phrase/shape/stem,
so the selector freely picked several different-shaped bridges that all carried the same
direction substring within one chapter — and the scene_anchor gate counts that shared
>=4-word substring across paragraphs.

These tests pin the fix:
  - _bridge_direction_substrings() extracts the shared >=4-word direction substring per block.
  - BridgeMemory caps how many bank bridges carrying one direction may land per chapter
    (_DIRECTION_CAP_PER_CHAPTER), and the cap resets across chapters.
  - The cap is enforced via a veto in _score_bridge_candidate (selector returns None when the
    whole block is vetoed, so the caller falls through to its direction-free legacy pool).
"""
from __future__ import annotations

import pytest

from phoenix_v4.rendering import chapter_composer as cc


@pytest.fixture(autouse=True)
def _enable_render_glue_for_bridge_cap_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bridge cap tests exercise template machinery; production default is glue OFF."""
    monkeypatch.setenv("PHOENIX_ENABLE_RENDER_GLUE", "1")
    monkeypatch.setenv("PHOENIX_BRIDGE_TRANSITION_FAMILIES", "1")
    cc._BRIDGE_TRANSITION_CACHE = None
def test_direction_substrings_extracted_for_recognition() -> None:
    ds = cc._bridge_direction_substrings()
    # The recognition block's shared direction is the courage proof's offender phrase.
    direction = ds.get(("after_opening", "recognition"), "")
    assert direction == "seeing the pattern before defending it", direction
    # Same direction is shared by other bridge_types for the same job.
    assert ds.get(("before_story", "recognition"), "") == direction
    # Every extracted direction is at least the gate's minimum width.
    for d in ds.values():
        assert len(d.split()) >= cc._DIRECTION_MIN_WORDS


def test_bridge_memory_caps_direction_per_chapter() -> None:
    bm = cc.BridgeMemory()
    direction = cc._bridge_direction_substrings()[("after_opening", "recognition")]
    seen: list[str] = []
    # Repeatedly select recognition bridges in the SAME chapter; once the cap is hit the
    # bank must stop serving direction-bearing bridges (selector returns None).
    none_after = None
    for i in range(8):
        sel = cc._select_bridge_candidate(
            bridge_type="after_opening",
            emotional_job="recognition",
            chapter_index=0,
            total_chapters=12,
            bridge_memory=bm,
            context_text=f"some context number {i}",
            seed="seed-A1",
        )
        if sel is None:
            none_after = i
            break
        seen.append(str(sel.get("text", "")))
    # The bank served at most the cap before vetoing the rest of the block.
    served_with_direction = sum(1 for t in seen if direction in t.lower())
    assert served_with_direction <= cc._DIRECTION_CAP_PER_CHAPTER, (
        f"direction served {served_with_direction}x, cap is {cc._DIRECTION_CAP_PER_CHAPTER}; seen={seen}"
    )
    assert bm.direction_count_chapter(0, direction) <= cc._DIRECTION_CAP_PER_CHAPTER
    assert none_after is not None, "selector should eventually veto the whole block"


def test_direction_cap_resets_across_chapters() -> None:
    bm = cc.BridgeMemory()
    direction = cc._bridge_direction_substrings()[("after_opening", "recognition")]
    # Saturate chapter 0.
    for i in range(6):
        cc._select_bridge_candidate(
            bridge_type="after_opening",
            emotional_job="recognition",
            chapter_index=0,
            total_chapters=12,
            bridge_memory=bm,
            context_text=f"ctx {i}",
            seed="seed-A1",
        )
    assert bm.direction_count_chapter(0, direction) <= cc._DIRECTION_CAP_PER_CHAPTER
    # A fresh chapter starts with a zeroed direction count and can serve the bank again.
    assert bm.direction_count_chapter(1, direction) == 0
    sel = cc._select_bridge_candidate(
        bridge_type="after_opening",
        emotional_job="recognition",
        chapter_index=1,
        total_chapters=12,
        bridge_memory=bm,
        context_text="fresh chapter context",
        seed="seed-A1",
    )
    assert sel is not None, "a new chapter must be able to serve the bank again"


def test_direction_veto_does_not_fire_without_a_direction() -> None:
    # A block with no qualifying shared substring must not be capped (cap is inert).
    bm = cc.BridgeMemory()
    score = cc._score_bridge_candidate(
        {"text": "A standalone bridge sentence.", "shape": "x", "stems": [], "roots": []},
        chapter_index=0,
        total_chapters=12,
        bridge_memory=bm,
        bridge_family="after_opening|recognition",
        topic_keywords=set(),
        direction="",  # no direction → veto branch skipped
    )
    assert score > -9999.0
