"""Tests for catalog homogeneity check."""
from __future__ import annotations

import pytest
from phoenix_v4.manga.series.profile_loader import MangaProfile
from scripts.manga.check_catalog_homogeneity import check_homogeneity


def _make_profile(title_id: str, emotional_engine: str, chapter_hook_family: str, market_demo: str = "shonen", genre_family: str = "battle", visual_grammar: str = "kinetic_shonen") -> MangaProfile:
    return MangaProfile(
        title_id=title_id,
        brand_id="test_brand",
        market_demo=market_demo,
        genre_family=genre_family,
        subgenre="",
        emotional_engine=emotional_engine,
        reader_promise="test",
        serialization_engine="arc_based",
        chapter_hook_family=chapter_hook_family,
        visual_grammar=visual_grammar,
    )


def test_collision_detected_when_two_share_engine_and_hook():
    """Two profiles sharing emotional_engine + chapter_hook_family → collision."""
    p1 = _make_profile("series_a", "aspiration", "new_rival")
    p2 = _make_profile("series_b", "aspiration", "new_rival")
    p3 = _make_profile("series_c", "longing", "almost_confession")

    warnings, collisions = check_homogeneity([p1, p2, p3])
    assert len(collisions) == 1
    assert "series_a" in collisions[0]
    assert "series_b" in collisions[0]


def test_no_collision_when_all_distinct():
    """Three profiles with distinct (emotional_engine, hook) combinations → clean."""
    p1 = _make_profile("series_a", "aspiration", "new_rival")
    p2 = _make_profile("series_b", "longing", "almost_confession")
    p3 = _make_profile("series_c", "dread", "ominous_image")

    warnings, collisions = check_homogeneity([p1, p2, p3])
    assert len(collisions) == 0


def test_lane_overlap_warning_detected():
    """Two profiles sharing demo/genre/grammar → warning (not collision)."""
    p1 = _make_profile("series_a", "aspiration", "new_rival", market_demo="shonen", genre_family="battle", visual_grammar="kinetic_shonen")
    p2 = _make_profile("series_b", "rivalry", "vow", market_demo="shonen", genre_family="battle", visual_grammar="kinetic_shonen")

    warnings, collisions = check_homogeneity([p1, p2])
    assert len(warnings) >= 1
    assert len(collisions) == 0  # no engine+hook collision


def test_empty_profiles_returns_clean():
    warnings, collisions = check_homogeneity([])
    assert warnings == []
    assert collisions == []
