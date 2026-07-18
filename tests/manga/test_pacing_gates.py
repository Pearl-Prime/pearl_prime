"""Tests for MANGA.SILENCE.DENSITY and MANGA.GENRE.AUTHENTICITY pacing gates."""
from __future__ import annotations

import pytest
from phoenix_v4.manga.qc.pacing_gates import check_silence_density, check_genre_authenticity
from phoenix_v4.manga.series.profile_loader import MangaProfile


def _make_profile(words_per_page_target: int = 100, silent_panel_ratio: float = 0.15, genre_family: str = "battle", market_demo: str = "shonen") -> MangaProfile:
    return MangaProfile(
        title_id="test", brand_id="b", market_demo=market_demo,
        genre_family=genre_family, subgenre="", emotional_engine="aspiration",
        reader_promise="test", serialization_engine="arc_based",
        chapter_hook_family="new_rival", visual_grammar="kinetic_shonen",
        words_per_page_target=words_per_page_target,
        silent_panel_ratio=silent_panel_ratio,
    )


def _make_script_with_wpp(words_per_page: int, pages: int = 5) -> dict:
    """Create a chapter script with approximately words_per_page words per page."""
    word = "word"
    pages_data = []
    for _ in range(pages):
        # Put words_per_page words in dialogue on one panel per page
        dialogue_text = " ".join([word] * words_per_page)
        pages_data.append({"panels": [{"dialogue": [dialogue_text]}]})
    return {"chapters": [{"pages": pages_data}]}


def _make_script_with_silence(silent_ratio: float, total_panels: int = 10) -> dict:
    """Create a chapter script with specified silent panel ratio."""
    silent_count = int(total_panels * silent_ratio)
    panels = []
    for i in range(total_panels):
        if i < silent_count:
            panels.append({"narration": ""})  # silent panel
        else:
            panels.append({"dialogue": ["some text here"]})
    return {"chapters": [{"pages": [{"panels": panels}]}]}


def test_shonen_90wpp_passes_target_100():
    """Shonen target=100 wpp, tolerance=30. 90 wpp should pass."""
    profile = _make_profile(words_per_page_target=100)
    script = _make_script_with_wpp(90)
    result = check_genre_authenticity(script, profile)
    assert result is None  # within ±30% of 100


def test_iyashikei_20wpp_fails_shonen_gate():
    """Shonen target=100 wpp. 20 wpp is way outside the ±30% tolerance."""
    profile = _make_profile(words_per_page_target=100)
    script = _make_script_with_wpp(20)
    result = check_genre_authenticity(script, profile)
    assert result is not None
    assert result["gate_id"] == "MANGA.GENRE.AUTHENTICITY"


def test_silence_ratio_020_passes_target_020():
    """Profile target=0.20, tolerance=0.15. Actual 0.20 should pass."""
    profile = _make_profile(silent_panel_ratio=0.20)
    script = _make_script_with_silence(0.20)
    result = check_silence_density(script, {}, profile)
    assert result is None


def test_silence_ratio_060_fails_target_015():
    """Profile target=0.15, tolerance=0.15. Actual 0.60 should fail (delta=0.45 > 0.15)."""
    profile = _make_profile(silent_panel_ratio=0.15)
    script = _make_script_with_silence(0.60)
    result = check_silence_density(script, {}, profile)
    assert result is not None
    assert result["gate_id"] == "MANGA.SILENCE.DENSITY"


def test_empty_script_passes_both_gates():
    profile = _make_profile()
    assert check_genre_authenticity({}, profile) is None
    assert check_silence_density({}, {}, profile) is None
