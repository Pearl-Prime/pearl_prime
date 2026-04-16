from __future__ import annotations

import re

from phoenix_v4.rendering import golden_chapter_synthesis as gcs
from phoenix_v4.rendering.golden_chapter_synthesis import (
    EnvironmentPhraseMemory,
    _load_environment_fallback_families,
    _resolve_location_placeholders,
)


def _single_family_used(memory: EnvironmentPhraseMemory, chapter_index: int = 0) -> str:
    used = memory.family_usage_by_chapter.get(chapter_index, {})
    assert used
    return max(used.items(), key=lambda kv: kv[1])[0]


def test_weather_detail_varies_with_context() -> None:
    memory = EnvironmentPhraseMemory()
    outs = []
    for idx in range(10):
        raw = f"Desk {idx}. {{weather_detail}} near the window and screen."
        outs.append(_resolve_location_placeholders(raw, phrase_memory=memory, chapter_index=idx))
    assert len(set(outs)) >= 3


def test_street_name_never_raw_the_street() -> None:
    out = _resolve_location_placeholders("You pause at {street_name}.")
    assert "the street" not in out.strip().lower()


def test_transit_line_never_bare_train() -> None:
    out = _resolve_location_placeholders("The {transit_line} lurches.")
    assert " train " not in f" {out.lower()} "


def test_phrase_not_reused_within_twelve_chapters() -> None:
    memory = EnvironmentPhraseMemory()
    seen = set()
    for idx in range(12):
        out = _resolve_location_placeholders(
            "The moment shifts around {weather_detail}.",
            phrase_memory=memory,
            chapter_index=idx,
        )
        phrase = out.replace("The moment shifts around ", "").rstrip(".").strip().lower()
        assert phrase not in seen
        seen.add(phrase)


def test_desk_context_biases_object_or_light() -> None:
    memory = EnvironmentPhraseMemory()
    _resolve_location_placeholders(
        "Your desk, keyboard, monitor, and cursor are in front of you. {weather_detail}",
        phrase_memory=memory,
        chapter_index=1,
    )
    fam = _single_family_used(memory, 1)
    assert fam in {"object_grounding", "light_ambient"}


def test_hallway_context_biases_interior_building() -> None:
    memory = EnvironmentPhraseMemory()
    _resolve_location_placeholders(
        "In the hallway near the elevator and office carpet, {weather_detail}",
        phrase_memory=memory,
        chapter_index=6,
    )
    fam = _single_family_used(memory, 6)
    assert fam == "interior_building"


def test_window_context_biases_window_or_outside() -> None:
    memory = EnvironmentPhraseMemory()
    _resolve_location_placeholders(
        "By the window glass looking outside, {street_name}",
        phrase_memory=memory,
        chapter_index=4,
    )
    fam = _single_family_used(memory, 4)
    assert fam in {"window_reference", "outside_sound"}


def test_environment_phrase_memory_blocks_exact_repeats() -> None:
    memory = EnvironmentPhraseMemory()
    out1 = _resolve_location_placeholders(
        "Hold still with {weather_detail}",
        phrase_memory=memory,
        chapter_index=0,
    )
    out2 = _resolve_location_placeholders(
        "Hold still with {weather_detail}",
        phrase_memory=memory,
        chapter_index=0,
    )
    assert out1 != out2


def test_environment_phrase_memory_limits_family_density() -> None:
    memory = EnvironmentPhraseMemory()
    for idx in range(6):
        _resolve_location_placeholders(
            "Quietly, {weather_detail}.",
            phrase_memory=memory,
            chapter_index=idx,
        )
    fam_counts = [memory.family_usage_by_chapter.get(i, {}) for i in range(6)]
    for i in range(2, 6):
        window_total = sum(fam_counts[j].get("light_ambient", 0) for j in range(i - 2, i + 1))
        assert window_total <= 2


def test_chapter_phase_awareness_changes_family_distribution() -> None:
    memory = EnvironmentPhraseMemory()
    _resolve_location_placeholders("Desk and threshold cues. {weather_detail}", phrase_memory=memory, chapter_index=1)
    _resolve_location_placeholders("Body contact and room sound. {weather_detail}", phrase_memory=memory, chapter_index=8)
    _resolve_location_placeholders("Quiet integration by the glass. {weather_detail}", phrase_memory=memory, chapter_index=11)
    fam1 = _single_family_used(memory, 1)
    fam8 = _single_family_used(memory, 8)
    fam12 = _single_family_used(memory, 11)
    assert len({fam1, fam8, fam12}) >= 2


def test_broken_merge_phrase_resolves_cleanly() -> None:
    out = _resolve_location_placeholders("The street below is there below.")
    assert "there below" not in out.lower()


def test_output_remains_grammatical() -> None:
    out = _resolve_location_placeholders("{weather_detail}. {street_name}. {transit_line}.")
    assert "  " not in out
    assert ".." not in out
    assert "{" not in out


def test_backward_compat_phrase_memory_none() -> None:
    out = _resolve_location_placeholders("{weather_detail} and {street_name} are present.", phrase_memory=None)
    assert "{" not in out


def test_yaml_missing_graceful_fallback(monkeypatch) -> None:
    old_path = gcs._ENV_FALLBACK_PATH
    old_cache = gcs._ENV_FAMILY_CACHE
    monkeypatch.setattr(gcs, "_ENV_FALLBACK_PATH", old_path.with_name("_missing_env_fallback.yaml"))
    monkeypatch.setattr(gcs, "_ENV_FAMILY_CACHE", None)
    families = _load_environment_fallback_families()
    out = _resolve_location_placeholders("{weather_detail} {street_name} {transit_line}")
    assert "families" in families
    assert "{" not in out
    monkeypatch.setattr(gcs, "_ENV_FALLBACK_PATH", old_path)
    monkeypatch.setattr(gcs, "_ENV_FAMILY_CACHE", old_cache)
