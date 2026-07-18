"""Tests for G-ORIENT — Ch1 first-120-words body/scene anchor check."""
from __future__ import annotations

from scripts.ci.check_orient_ch1_scene_anchor import (
    DEFAULT_LEXICON_PATH,
    ch1_first_words,
    lexicon_anchor_hit,
    load_lexicon,
    scene_atom_provenance_hit,
)

LEXICON = load_lexicon(DEFAULT_LEXICON_PATH)

ABSTRACT_OPENING_BOOK = (
    "Chapter 1\n\n"
    "Awareness is the foundation of every transformation a person can undertake "
    "in their life. Consciousness itself is the ground on which all growth "
    "occurs, philosophically speaking, across every tradition ever studied by "
    "anyone anywhere in recorded human history and beyond it too apparently.\n"
    "\nChapter 2\n\nMore abstract material follows here as well for good measure.\n"
)

SCENE_FIRST_BOOK = (
    "Chapter 1\n\n"
    "Her hand is back on the phone before she decided to pick it up. The "
    "screen glows in the dark bedroom while her chest tightens without "
    "warning, a small and ordinary Tuesday unraveling in real time for her.\n"
    "\nChapter 2\n\nSomething else happens next in the story.\n"
)


def test_lexicon_loads_and_is_nonempty():
    assert LEXICON
    assert "chest" in LEXICON
    assert "phone" in LEXICON


def test_abstract_opening_has_no_anchor_hit():
    window = ch1_first_words(ABSTRACT_OPENING_BOOK)
    assert lexicon_anchor_hit(window, LEXICON) is None


def test_scene_first_opening_has_anchor_hit():
    window = ch1_first_words(SCENE_FIRST_BOOK)
    hit = lexicon_anchor_hit(window, LEXICON)
    assert hit in {"hand", "phone", "screen", "bedroom", "chest"}


def test_scene_atom_provenance_true_when_ch1_has_scene_slot():
    outline = {
        "chapters": [
            {"number": 1, "slot_types_landed": ["HOOK", "SCENE", "STORY"]},
            {"number": 2, "slot_types_landed": ["HOOK"]},
        ]
    }
    assert scene_atom_provenance_hit(outline) is True


def test_scene_atom_provenance_false_when_ch1_lacks_scene_slot():
    outline = {
        "chapters": [
            {"number": 1, "slot_types_landed": ["HOOK", "REFLECTION"]},
        ]
    }
    assert scene_atom_provenance_hit(outline) is False


def test_scene_atom_provenance_false_when_outline_missing():
    assert scene_atom_provenance_hit(None) is False
    assert scene_atom_provenance_hit({}) is False
