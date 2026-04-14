"""Frame registry + frame_governance_check (phrase-list v1)."""

from __future__ import annotations

from pathlib import Path

from phoenix_v4.quality.frame_governor import frame_governance_check, load_frame_registry


def _registry() -> dict:
    return load_frame_registry()


def test_somatic_flags_every_organ_frequency() -> None:
    reg = _registry()
    r = frame_governance_check(
        "Some teachers claim every organ has a frequency.",
        "somatic_first",
        5,
        reg,
    )
    assert any(v.get("type") == "absolute_claim" for v in r.violations)


def test_somatic_flags_disease_is_dissonance() -> None:
    reg = _registry()
    r = frame_governance_check(
        "They say disease is dissonance in the field.",
        "somatic_first",
        5,
        reg,
    )
    assert any(v.get("type") == "absolute_claim" for v in r.violations)


def test_somatic_does_not_flag_nervous_system() -> None:
    reg = _registry()
    r = frame_governance_check(
        "The nervous system responds to predictions before facts.",
        "somatic_first",
        0,
        reg,
    )
    assert not any(v.get("type") == "absolute_claim" for v in r.violations)


def test_spiritual_first_allows_patterns() -> None:
    reg = _registry()
    r = frame_governance_check(
        "Every organ has a frequency of love.",
        "spiritual_first",
        0,
        reg,
    )
    assert r.frame_compliant
    assert r.violations == []


def test_spiritual_entry_chapter_min_blocks_early_karma() -> None:
    reg = _registry()
    r = frame_governance_check(
        "You might describe chakra imagery in the chest.",
        "somatic_first",
        0,
        reg,
    )
    assert any(v.get("type") == "spiritual_before_entry_chapter" for v in r.violations)


def test_spiritual_allowed_from_chapter_three() -> None:
    reg = _registry()
    r = frame_governance_check(
        "You might describe chakra imagery in the chest.",
        "somatic_first",
        3,
        reg,
    )
    assert not any(v.get("type") == "spiritual_before_entry_chapter" for v in r.violations)


def test_missing_frame_registry_graceful(tmp_path: Path) -> None:
    r = frame_governance_check("anything", "somatic_first", 0, {})
    assert r.frame_compliant
