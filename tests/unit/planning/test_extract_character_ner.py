"""F1: NER character extraction for story_atoms (Holistic v2 Phase B)."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning.story_planner import _extract_character, _load_all_atoms

REPO = Path(__file__).resolve().parents[3]
PERSONA = "gen_z_professionals"
TOPIC = "anxiety"


@pytest.fixture(scope="module")
def overwhelm_atoms():
    return _load_all_atoms(PERSONA, TOPIC, REPO)


def test_no_structural_false_positives_in_index(overwhelm_atoms):
    """14 formerly-misattributed atoms must not index as The/Another/It."""
    bad = {a.path.name: a.character for a in overwhelm_atoms if a.character in (
        "The", "Another", "It", "It's", "Third", "Chri", "PTO", "Slack",
    )}
    assert not bad, f"structural mis-attributions remain: {bad}"


def test_opening_possessive_priya():
    text = (
        "Priya submits the project update at 11:47pm. It is thorough. She has "
        "checked it three times. Priya turns her laptop away."
    )
    assert _extract_character(text) == "Priya"


def test_the_opener_finds_zara_elsewhere():
    text = (
        "The fourth deliverable goes out at 4:58pm. Zara sits back and watches "
        "the send button. Zara does not feel relief yet."
    )
    assert _extract_character(text) == "Zara"


def test_no_named_character_returns_none():
    text = "The room is quiet. Nothing moves. The light stays the same."
    assert _extract_character(text) is None
