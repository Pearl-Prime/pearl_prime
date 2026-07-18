"""Tests for config/manga/manga_pacing_by_genre.yaml integrity."""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

PACING_YAML = Path("config/manga/manga_pacing_by_genre.yaml")
REQUIRED_GENRE_KEYS = [
    "words_per_page_range",
    "silent_panel_ratio_range",
    "spread_frequency",
    "narration_tolerance",
]


@pytest.fixture(scope="module")
def pacing_data() -> dict:
    with open(PACING_YAML) as f:
        return yaml.safe_load(f)


def _genres(pacing_data: dict) -> dict:
    """Return genre dict from either 'genres' or 'genre_pacing' top-level key."""
    return pacing_data.get("genres") or pacing_data.get("genre_pacing") or {}


def test_file_exists():
    assert PACING_YAML.is_file(), f"{PACING_YAML} not found"


def test_top_level_keys(pacing_data):
    has_genres = "genres" in pacing_data or "genre_pacing" in pacing_data
    assert has_genres, "Missing 'genres' or 'genre_pacing' top-level key"
    assert "genre_family_aliases" in pacing_data, "Missing 'genre_family_aliases' key"


def test_all_genres_have_required_fields(pacing_data):
    for genre_id, entry in _genres(pacing_data).items():
        for key in REQUIRED_GENRE_KEYS:
            assert key in entry, f"Genre '{genre_id}' missing required field '{key}'"


def test_words_per_page_range_valid(pacing_data):
    for genre_id, entry in _genres(pacing_data).items():
        rng = entry["words_per_page_range"]
        # Accept both list [min, max] and dict {min: ..., max: ...}
        if isinstance(rng, list):
            lo, hi = rng[0], rng[1]
        else:
            lo, hi = rng.get("min", 0), rng.get("max", 999)
        assert lo <= hi, f"Genre '{genre_id}' words_per_page_range min > max: {rng}"


def test_silent_panel_ratio_range_valid(pacing_data):
    for genre_id, entry in _genres(pacing_data).items():
        rng = entry["silent_panel_ratio_range"]
        if isinstance(rng, list):
            lo, hi = rng[0], rng[1]
        else:
            lo, hi = rng.get("min", 0.0), rng.get("max", 1.0)
        assert 0.0 <= lo <= 1.0, f"Genre '{genre_id}' silent ratio min out of [0,1]: {lo}"
        assert 0.0 <= hi <= 1.0, f"Genre '{genre_id}' silent ratio max out of [0,1]: {hi}"
        assert lo <= hi, f"Genre '{genre_id}' silent ratio min > max: {rng}"


def test_aliases_point_to_known_genres(pacing_data):
    known = set(_genres(pacing_data).keys())
    for alias, target in pacing_data["genre_family_aliases"].items():
        assert target in known, (
            f"Alias '{alias}' points to unknown genre '{target}'. "
            f"Known: {sorted(known)}"
        )


def test_healing_genre_has_low_wpp(pacing_data):
    """Healing genre must have low word density — core of iyashikei grammar."""
    healing = _genres(pacing_data).get("healing", {})
    rng = healing.get("words_per_page_range", [0, 999])
    hi = rng[1] if isinstance(rng, list) else rng.get("max", 999)
    assert hi <= 55, (
        f"Healing genre wpp max should be ≤55 (iyashikei low-text grammar). Got {rng}"
    )


def test_battle_genre_has_high_wpp(pacing_data):
    """Battle genre should allow high word density for exposition and match commentary."""
    battle = _genres(pacing_data).get("battle", {})
    rng = battle.get("words_per_page_range", [0, 0])
    hi = rng[1] if isinstance(rng, list) else rng.get("max", 0)
    assert hi >= 100, (
        f"Battle genre wpp max should be ≥100. Got {rng}"
    )
