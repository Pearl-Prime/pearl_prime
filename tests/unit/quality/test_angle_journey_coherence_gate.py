"""OPD-116/117 Phase B — angle_journey_coherence gate."""
from __future__ import annotations

from phoenix_v4.quality.angle_journey_coherence import evaluate_angle_journey_coherence


class _Slot:
    def __init__(self, slot_type: str, match_scores=None):
        self.slot_type = slot_type
        self.match_scores = match_scores or {}


class _Chapter:
    def __init__(self, number: int, slots: list):
        self.number = number
        self.slots = slots


def test_gate_fails_layer_five_in_chapter_three():
    proses = ["chapter body"] * 12
    result = evaluate_angle_journey_coherence(
        angle_id="VERDICT",
        runtime_format="deep_book_6h",
        topic_id="anxiety",
        chapter_proses=proses,
        angle_layer_by_chapter={3: 5, 11: 5, 12: 5},
        enriched_chapters=[
            _Chapter(3, [_Slot("ANGLE_CALLBACK", {"angle_layer": 5})]),
        ],
    )
    assert not result.valid
    assert any("layer 5" in e.lower() and "chapter 11" in e.lower() for e in result.errors)


def test_gate_skipped_without_angle():
    result = evaluate_angle_journey_coherence(
        angle_id="",
        runtime_format="deep_book_6h",
        topic_id="anxiety",
        chapter_proses=["x"],
    )
    assert result.valid
    assert any("SKIPPED" in w for w in result.warnings)
