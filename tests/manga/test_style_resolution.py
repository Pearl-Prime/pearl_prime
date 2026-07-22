"""Wave-2 Item 4 — style_id authority chain (phoenix_v4.manga.style_resolution).

Regression coverage for the "every chapter renders dark_psychological
regardless of genre" bug: a healing chapter with no explicit --style-id used
to hard-default to dark_psychological. These tests pin the documented
authority chain (explicit override -> script style -> request style ->
teacher archetype -> profile grammar -> genre-family signal -> fallback).
"""
from __future__ import annotations

from phoenix_v4.manga.style_resolution import (
    FALLBACK_STYLE_ID,
    resolve_style_id,
)


def test_healing_genre_resolves_to_cozy_iyashikei() -> None:
    style_id, source = resolve_style_id(genre_id="healing")
    assert style_id == "cozy_iyashikei"
    assert source == "genre_family_signal"


def test_psychological_horror_resolves_to_dark_psychological() -> None:
    style_id, source = resolve_style_id(genre_id="psychological_horror")
    assert style_id == "dark_psychological"
    assert source == "genre_family_signal"


def test_mecha_resolves_to_power_progression() -> None:
    style_id, source = resolve_style_id(genre_id="mecha")
    assert style_id == "power_progression"
    assert source == "genre_family_signal"


def test_explicit_override_wins_over_everything() -> None:
    style_id, source = resolve_style_id(
        explicit_override="hyper_clean_cinematic",
        chapter_script={"style_id": "cozy_iyashikei", "genre": "mecha"},
        request_style="webtoon_vertical_romance",
        teacher_id="ahjan",
        genre_id="mecha",
    )
    assert style_id == "hyper_clean_cinematic"
    assert source == "explicit_override"


def test_no_signal_falls_back_to_grounded_realism() -> None:
    style_id, source = resolve_style_id()
    assert style_id == FALLBACK_STYLE_ID == "grounded_realism"
    assert source == "narrow_fallback"


def test_unknown_genre_falls_back_to_grounded_realism() -> None:
    style_id, source = resolve_style_id(genre_id="not_a_real_genre_xyz")
    assert style_id == "grounded_realism"
    assert source == "narrow_fallback"


def test_script_style_beats_genre_signal_but_not_explicit_override() -> None:
    style_id, source = resolve_style_id(
        chapter_script={"style_id": "sensory_closeup"}, genre_id="mecha"
    )
    assert style_id == "sensory_closeup"
    assert source == "script_style"


def test_request_style_beats_genre_signal() -> None:
    style_id, source = resolve_style_id(
        request_style="symbolic_reflection", genre_id="mecha"
    )
    assert style_id == "symbolic_reflection"
    assert source == "request_style"


def test_genre_read_from_chapter_script_when_genre_id_not_passed() -> None:
    style_id, source = resolve_style_id(chapter_script={"genre": "healing"})
    assert style_id == "cozy_iyashikei"
    assert source == "genre_family_signal"


def test_genre_normalization_handles_case_and_separators() -> None:
    style_id, _source = resolve_style_id(genre_id="Psychological-Horror")
    assert style_id == "dark_psychological"
