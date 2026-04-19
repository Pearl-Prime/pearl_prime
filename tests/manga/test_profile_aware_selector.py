"""Tests for ProfileAwareSelector."""
from __future__ import annotations

import pytest
from phoenix_v4.manga.selection.profile_aware_selector import ProfileAwareSelector, _is_eligible
from phoenix_v4.manga.series.profile_loader import MangaProfile

# Minimal fixture profile
_PROFILE = MangaProfile(
    title_id="test_series",
    brand_id="test_brand",
    market_demo="shonen",
    genre_family="battle",
    subgenre="",
    emotional_engine="aspiration",
    reader_promise="you will feel fired up",
    serialization_engine="arc_based",
    chapter_hook_family="new_rival",
    visual_grammar="kinetic_shonen",
)

AGNOSTIC = {"id": "a", "text": "generic"}
SHONEN_ONLY = {"id": "b", "text": "battle cry", "manga_compat": {"allowed_market_demos": ["shonen", "seinen"]}}
JOSEI_ONLY = {"id": "c", "text": "quiet moment", "manga_compat": {"allowed_market_demos": ["josei", "shojo"]}}
EXCLUDED = {"id": "d", "text": "excluded", "manga_compat": {"excluded_market_demos": ["shonen"]}}


def test_agnostic_is_eligible():
    assert _is_eligible(AGNOSTIC, _PROFILE)


def test_allowed_demo_match():
    assert _is_eligible(SHONEN_ONLY, _PROFILE)


def test_allowed_demo_no_match():
    assert not _is_eligible(JOSEI_ONLY, _PROFILE)


def test_excluded_demo_blocks():
    assert not _is_eligible(EXCLUDED, _PROFILE)


def test_select_deterministic():
    sel = ProfileAwareSelector(_PROFILE)
    candidates = [AGNOSTIC, SHONEN_ONLY, JOSEI_ONLY, EXCLUDED]
    r1 = sel.select(role="hook", candidates=candidates, seed_inputs=("topic1", "persona1", "arc1", 1))
    r2 = sel.select(role="hook", candidates=candidates, seed_inputs=("topic1", "persona1", "arc1", 1))
    assert r1 is r2  # same object, same index


def test_select_filters_incompatible():
    sel = ProfileAwareSelector(_PROFILE)
    # Only AGNOSTIC and SHONEN_ONLY are eligible; JOSEI_ONLY and EXCLUDED should never appear
    candidates = [AGNOSTIC, SHONEN_ONLY, JOSEI_ONLY, EXCLUDED]
    results = set()
    for i in range(20):
        r = sel.select(role="hook", candidates=candidates, seed_inputs=("t", "p", "a", i))
        results.add(r["id"])
    assert "c" not in results, "josei-only candidate leaked into shonen selection"
    assert "d" not in results, "excluded candidate appeared in selection"


def test_select_fallback_when_empty_after_filter():
    sel = ProfileAwareSelector(_PROFILE)
    # All candidates incompatible — should fall back to full pool rather than raise
    candidates = [JOSEI_ONLY, EXCLUDED]
    r = sel.select(role="hook", candidates=candidates, seed_inputs=("t", "p", "a", 1))
    assert r is not None


def test_select_many_distinct():
    sel = ProfileAwareSelector(_PROFILE)
    candidates = [{"id": str(i)} for i in range(10)]
    results = sel.select_many(role="hook", candidates=candidates, seed_inputs=("t", "p", "a"), count=5)
    assert len(results) == 5
    # should prefer distinct
    ids = [r["id"] for r in results]
    assert len(set(ids)) >= 3  # at least some diversity
