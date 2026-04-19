"""Tests for MANGA.RESTRAINT.EXPOSITION gate."""
from __future__ import annotations

import pytest
from phoenix_v4.manga.qc.restraint_gate import check_restraint_over_exposition
from phoenix_v4.manga.series.profile_loader import MangaProfile


def _make_profile(market_demo: str = "josei", genre_family: str = "romance") -> MangaProfile:
    return MangaProfile(
        title_id="test", brand_id="b", market_demo=market_demo,
        genre_family=genre_family, subgenre="", emotional_engine="longing",
        reader_promise="test", serialization_engine="mood_based",
        chapter_hook_family="almost_confession", visual_grammar="grounded_josei_realism",
    )


def _make_over_narrated_script(panel_count: int = 8) -> dict:
    """Script where >25% panels have explicit emotional narration."""
    # Make 6 out of 8 panels (75%) have exposition patterns
    panels = []
    for i in range(panel_count):
        if i < 6:
            panels.append({"narration": "She felt her heart racing as she looked at him."})
        else:
            panels.append({"dialogue": ["I need to tell you something."]})
    return {"chapters": [{"pages": [{"panels": panels}]}]}


def _make_restrained_script() -> dict:
    """Script with no exposition patterns — all show."""
    panels = [
        {"panel_description": "She looks away, gripping her coffee cup.", "dialogue": []},
        {"panel_description": "He exhaled slowly.", "dialogue": ["..."]},
        {"panel_description": "She smiled, looked down at the table."},
        {"dialogue": ["I'll see you tomorrow."]},
    ]
    return {"chapters": [{"pages": [{"panels": panels}]}]}


def test_josei_over_narrated_fires():
    """Josei profile + >25% panels with exposition → gate fires."""
    profile = _make_profile(market_demo="josei", genre_family="romance")
    script = _make_over_narrated_script()
    result = check_restraint_over_exposition(script, profile)
    assert result is not None
    assert result["gate_id"] == "MANGA.RESTRAINT.EXPOSITION"


def test_josei_restrained_passes():
    """Josei profile + no exposition patterns → gate passes."""
    profile = _make_profile(market_demo="josei", genre_family="romance")
    script = _make_restrained_script()
    result = check_restraint_over_exposition(script, profile)
    assert result is None


def test_shonen_gate_skipped():
    """Shonen profile → gate returns None regardless of content."""
    profile = MangaProfile(
        title_id="test", brand_id="b", market_demo="shonen",
        genre_family="battle", subgenre="", emotional_engine="aspiration",
        reader_promise="test", serialization_engine="arc_based",
        chapter_hook_family="new_rival", visual_grammar="kinetic_shonen",
    )
    script = _make_over_narrated_script()
    result = check_restraint_over_exposition(script, profile)
    assert result is None  # gate skipped for shonen/battle


def test_seinen_romance_fires_if_over_narrated():
    """Seinen profile with romance genre → gate applies and fires if over-narrated."""
    profile = MangaProfile(
        title_id="test", brand_id="b", market_demo="seinen",
        genre_family="romance", subgenre="", emotional_engine="longing",
        reader_promise="test", serialization_engine="slow_burn_relationship",
        chapter_hook_family="almost_confession", visual_grammar="intimate_realism",
    )
    script = _make_over_narrated_script()
    result = check_restraint_over_exposition(script, profile)
    assert result is not None
    assert result["gate_id"] == "MANGA.RESTRAINT.EXPOSITION"


def test_empty_script_passes():
    profile = _make_profile()
    assert check_restraint_over_exposition({}, profile) is None
    assert check_restraint_over_exposition({"chapters": []}, profile) is None
