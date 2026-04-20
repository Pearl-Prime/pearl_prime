"""Tests for MANGA.YEARNING.PACING gate (MDLG-09b)."""
from __future__ import annotations

import pytest
from phoenix_v4.manga.qc.yearning_gate import check_yearning_pacing
from phoenix_v4.manga.series.profile_loader import MangaProfile


def _make_longing_profile(
    emotional_engine: str = "longing",
    genre_family: str = "romance",
    chapter_hook_family: str = "almost_confession",
) -> MangaProfile:
    return MangaProfile(
        title_id="test_longing", brand_id="b", market_demo="josei",
        genre_family=genre_family, subgenre="slow_burn",
        emotional_engine=emotional_engine, reader_promise="test",
        serialization_engine="mood_based",
        chapter_hook_family=chapter_hook_family,
        visual_grammar="grounded_josei_realism",
    )


def _make_premature_resolution_script(panel_count: int = 10) -> dict:
    """Script where >15% panels contain resolution language."""
    panels = []
    for i in range(panel_count):
        if i < 3:
            panels.append({"dialogue": ["I love you.", "She confessed at last."]})
        elif i < 6:
            panels.append({"narration": "They kissed. Finally together at last."})
        else:
            panels.append({"panel_description": "She looks away.", "dialogue": ["..."]})
    return {"chapters": [{"pages": [{"panels": panels}]}]}


def _make_sustained_yearning_script() -> dict:
    """Script sustaining tension — almost but not yet."""
    panels = [
        {"panel_description": "She almost touched his hand. Stopped herself.", "dialogue": []},
        {"narration": "She couldn't say it. The distance between them remained.", "dialogue": []},
        {"dialogue": ["I—", "...never mind."]},
        {"panel_description": "He turned away. Looked out the window. Silence fell.", "dialogue": []},
        {"panel_description": "She bit her lip and said nothing."},
    ]
    return {"chapters": [{"pages": [{"panels": panels}]}]}


def test_longing_premature_resolution_fires():
    """Longing profile + >15% panels with resolution language → gate fires."""
    profile = _make_longing_profile()
    script = _make_premature_resolution_script()
    result = check_yearning_pacing(script, profile)
    assert result is not None
    assert result["gate_id"] == "MANGA.YEARNING.PACING"
    assert result["issue_code"] == "PREMATURE_RESOLUTION_IN_YEARNING_CHAPTER"


def test_longing_sustained_tension_passes():
    """Longing profile + no resolution language → gate passes."""
    profile = _make_longing_profile()
    script = _make_sustained_yearning_script()
    result = check_yearning_pacing(script, profile)
    assert result is None


def test_battle_profile_skipped():
    """Battle/aspiration profile → gate returns None regardless of content."""
    profile = MangaProfile(
        title_id="test_battle", brand_id="b", market_demo="shonen",
        genre_family="battle", subgenre="tournament",
        emotional_engine="aspiration", reader_promise="test",
        serialization_engine="arc_based",
        chapter_hook_family="new_rival",
        visual_grammar="kinetic_shonen",
    )
    script = _make_premature_resolution_script()
    result = check_yearning_pacing(script, profile)
    assert result is None  # gate skips non-yearning profiles


def test_tenderness_engine_applies():
    """Tenderness engine also triggers yearning gate."""
    profile = _make_longing_profile(
        emotional_engine="tenderness",
        genre_family="healing",
        chapter_hook_family="hidden_truth_glimpse",
    )
    script = _make_premature_resolution_script()
    result = check_yearning_pacing(script, profile)
    assert result is not None
    assert result["gate_id"] == "MANGA.YEARNING.PACING"


def test_almost_confession_hook_applies():
    """almost_confession hook triggers gate even for non-longing engine."""
    profile = MangaProfile(
        title_id="test_hook", brand_id="b", market_demo="seinen",
        genre_family="slice_of_life", subgenre="",
        emotional_engine="cozy_restoration", reader_promise="test",
        serialization_engine="episodic",
        chapter_hook_family="almost_confession",
        visual_grammar="grounded_josei_realism",
    )
    script = _make_premature_resolution_script()
    result = check_yearning_pacing(script, profile)
    assert result is not None


def test_empty_script_passes():
    """Empty/missing chapter data → gate passes gracefully."""
    profile = _make_longing_profile()
    assert check_yearning_pacing({}, profile) is None
    assert check_yearning_pacing({"chapters": []}, profile) is None


def test_low_resolution_ratio_passes():
    """Only 1 panel with resolution language in a 10-panel chapter → passes (≤15%)."""
    profile = _make_longing_profile()
    panels = [{"dialogue": ["I love you."]}] + [
        {"panel_description": "She looked away."} for _ in range(9)
    ]
    script = {"chapters": [{"pages": [{"panels": panels}]}]}
    result = check_yearning_pacing(script, profile)
    assert result is None  # 1/10 = 10% ≤ 15% threshold
