"""Tests for MANGA.CHAPTER.HOOK gate."""
from __future__ import annotations

import pytest
from phoenix_v4.manga.qc.hook_gate import check_chapter_hook
from phoenix_v4.manga.series.profile_loader import MangaProfile


def _make_profile(hook_family: str) -> MangaProfile:
    return MangaProfile(
        title_id="test", brand_id="b", market_demo="shonen",
        genre_family="battle", subgenre="", emotional_engine="aspiration",
        reader_promise="test", serialization_engine="arc_based",
        chapter_hook_family=hook_family, visual_grammar="kinetic_shonen",
    )


def _make_script(final_text: str) -> dict:
    return {"chapters": [{"pages": [{"panels": [{"narration": final_text}]}]}]}


def test_vow_hook_detected():
    profile = _make_profile("vow")
    script = _make_script("He swears he will never let her down again.")
    assert check_chapter_hook(script, profile) is None  # passes


def test_vow_hook_missing():
    profile = _make_profile("vow")
    script = _make_script("The sun set quietly behind the mountains.")
    issue = check_chapter_hook(script, profile)
    assert issue is not None
    assert issue["gate_id"] == "MANGA.CHAPTER.HOOK"


def test_almost_confession_detected():
    profile = _make_profile("almost_confession")
    script = _make_script("She almost said it. The words caught in her throat.")
    assert check_chapter_hook(script, profile) is None


def test_empty_script_passes():
    profile = _make_profile("vow")
    assert check_chapter_hook({}, profile) is None
    assert check_chapter_hook({"chapters": []}, profile) is None
