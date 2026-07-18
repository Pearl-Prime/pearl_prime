"""Tests for the manga mode-wrapper foundation (teacher-mode XOR music-mode).

Covers the standalone validator + vessel loader. No pipeline integration is exercised
(that is a separate, opt-in step) — these prove the foundation in isolation.
"""
from __future__ import annotations

import pytest

from phoenix_v4.manga.mode import (
    MODES,
    ModeError,
    VesselError,
    assert_mode_xor,
    load_all_vessels,
    load_vessel,
    resolve_mode,
)

# Genres that must carry both a teacher and a music vessel (the catalog's 15).
GENRES = [
    "iyashikei", "dark_fantasy", "mecha", "supernatural_mystery", "psychological_thriller",
    "romance_josei_drama", "workplace_drama", "sci_fi_cyberpunk", "psychological_horror",
    "action_battle", "historical_period", "isekai", "sports_competition",
    "school_coming_of_age", "cultivation_martial",
]


# ── XOR validator ───────────────────────────────────────────────────────────

def test_mode_unset_is_noop_legacy():
    assert assert_mode_xor({"series_id": "legacy", "teacher_id": "ahjan"}) is None
    assert resolve_mode({"series_id": "legacy"}) is None


def test_accepts_teacher_only():
    sp = {"series_id": "s", "mode": "teacher", "teacher_id": "ahjan"}
    assert assert_mode_xor(sp) == "teacher"


def test_accepts_music_only():
    sp = {"series_id": "s", "mode": "music", "musician_id": "sora_vesper", "teacher_id": None}
    assert assert_mode_xor(sp) == "music"


def test_rejects_both_archetypes():
    sp = {"series_id": "s", "mode": "teacher", "teacher_id": "ahjan", "musician_id": "sora"}
    with pytest.raises(ModeError):
        assert_mode_xor(sp)


def test_rejects_teacher_mode_without_teacher():
    with pytest.raises(ModeError):
        assert_mode_xor({"series_id": "s", "mode": "teacher"})


def test_rejects_music_mode_without_musician():
    with pytest.raises(ModeError):
        assert_mode_xor({"series_id": "s", "mode": "music"})


def test_rejects_unknown_mode():
    with pytest.raises(ModeError):
        assert_mode_xor({"series_id": "s", "mode": "both", "teacher_id": "ahjan"})


# ── Vessel loader ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("genre", GENRES)
@pytest.mark.parametrize("mode", MODES)
def test_every_genre_has_both_vessels(genre, mode):
    v = load_vessel(genre, mode)
    assert v.get("vessel"), f"{genre}/{mode} missing vessel name"
    assert v.get("vessel_desc"), f"{genre}/{mode} missing vessel_desc"
    beats = v.get("beats") or {}
    if mode == "teacher":
        assert set(beats) >= {"wound", "turn", "renewal"}, f"{genre}/teacher beats incomplete"
    else:
        assert set(beats) >= {"opening", "mid", "closing"}, f"{genre}/music beats incomplete"


def test_pilot_vessels_match_gold_references():
    # the two hand-authored gold pilots (#1788)
    assert "Keeper" in load_vessel("dark_fantasy", "teacher")["vessel"]
    assert "sync-song" in load_vessel("mecha", "music")["vessel"]


def test_load_all_covers_the_15():
    genres = load_all_vessels()
    for g in GENRES:
        assert g in genres, f"vessel config missing genre {g}"
        assert "teacher" in genres[g] and "music" in genres[g]


def test_bad_genre_and_mode_raise():
    with pytest.raises(VesselError):
        load_vessel("not_a_genre", "teacher")
    with pytest.raises(ModeError):
        load_vessel("mecha", "not_a_mode")
