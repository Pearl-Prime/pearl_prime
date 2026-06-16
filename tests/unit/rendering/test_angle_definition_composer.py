"""OPD-116/117 Phase B — ANGLE_DEFINITION / ANGLE_CALLBACK composition."""
from __future__ import annotations

from phoenix_v4.rendering.chapter_composer import (
    angle_callback_memory_line,
    compose_chapter_prose,
    prefix_angle_callback_prose,
)
from phoenix_v4.rendering.golden_chapter_synthesis import build_virtual_slot_streams


class _Slot:
    def __init__(self, slot_type: str, content: str, match_scores=None):
        self.slot_type = slot_type
        self.content = content
        self.match_scores = match_scores or {}


def test_angle_definition_renders_as_single_block_without_extra_bridges():
    definition = (
        "Step one names the pattern. Step two shows the cost. "
        "Step three reframes the verdict you inherited."
    )
    chapter = compose_chapter_prose(
        ["HOOK", "ANGLE_DEFINITION", "REFLECTION"],
        ["You wake already braced.", definition, "The mechanism is anticipation."],
        chapter_index=0,
        total_chapters=12,
    )
    assert definition in chapter
    assert "You wake already braced" in chapter
    assert definition.count("Step one") == 1


def test_angle_callback_memory_line_prefix():
    line = angle_callback_memory_line("Anxiety is a protective alarm.")
    assert "Earlier I said" in line
    assert "protective alarm" in line
    assert "hidden in that" in line


def test_build_virtual_slot_streams_prefixes_callback():
    slots = [
        _Slot("HOOK", "You open the inbox before coffee."),
        _Slot(
            "ANGLE_CALLBACK",
            "Layer two names the loop your body already knows.",
            match_scores={"angle_layer": 2},
        ),
    ]
    types, proses = build_virtual_slot_streams(
        slots,
        chapter_index0=2,
        angle_id="VERDICT",
        angle_layer=2,
        topic_id="anxiety",
    )
    assert "ANGLE_CALLBACK" in types
    cb_idx = types.index("ANGLE_CALLBACK")
    assert "Layer two" in proses[cb_idx]


def test_prefix_angle_callback_skips_todo_prior():
    body = "This chapter escalates the frame."
    out = prefix_angle_callback_prose(
        body,
        angle_id="VERDICT",
        layer=1,
    )
    assert out == body
