"""Phase-1 story-type / naming / variety enforcement (docs/STORY_TYPES_AND_STRUCTURES.md §7/§3/§9).

Deterministic; no LLM. Extends the existing phoenix_v4/quality/story_atom_lint.py.
"""
import textwrap
from pathlib import Path

import pytest

from phoenix_v4.quality.story_atom_lint import (
    check_story_type_conformance,
    check_character_study_naming,
    story_type_variety_flag,
    load_principle_teachers,
    lint_story_atom_yaml,
)


# ── §7 conformance ────────────────────────────────────────────────────────
def test_conformance_conformant_cases_return_no_flags():
    assert check_story_type_conformance("parable", "composite") == []
    assert check_story_type_conformance("direct_teaching", "composite") == []
    assert check_story_type_conformance("recognition_exchange", "true_story") == []
    assert check_story_type_conformance("character_study", "true_story") == []


def test_conformance_untagged_atom_is_vacuous():
    # No story_type → no opinion (the persona catalog until Phase-3 tagging).
    assert check_story_type_conformance(None, "composite") == []
    assert check_story_type_conformance("", None) == []


def test_conformance_composite_forbids_recognition_exchange():
    flags = check_story_type_conformance("recognition_exchange", "composite")
    assert "COMPOSITE_FORBIDS_RECOGNITION_EXCHANGE" in flags


def test_conformance_recognition_exchange_requires_true_story():
    flags = check_story_type_conformance("recognition_exchange", "composite")
    assert "RECOGNITION_EXCHANGE_REQUIRES_TRUE_STORY" in flags
    # true_story is fine
    assert "RECOGNITION_EXCHANGE_REQUIRES_TRUE_STORY" not in check_story_type_conformance(
        "recognition_exchange", "true_story"
    )


def test_conformance_principle_teacher_type_restriction():
    # principle teacher may NOT use character_study / recognition_exchange
    assert "PRINCIPLE_TEACHER_TYPE_FORBIDDEN" in check_story_type_conformance(
        "character_study", "composite", teacher_is_principle=True
    )
    # but parable/atmospheric/direct_teaching are allowed
    assert check_story_type_conformance("parable", "composite", teacher_is_principle=True) == []
    assert check_story_type_conformance("atmospheric", "composite", teacher_is_principle=True) == []


def test_conformance_unknown_type_flagged():
    assert check_story_type_conformance("epic_saga", "composite") == ["UNKNOWN_STORY_TYPE"]


# ── §3 naming ─────────────────────────────────────────────────────────────
def test_character_study_named_passes():
    prose = "Naomi sat in her car outside the subway for forty minutes, engine off."
    assert check_character_study_naming("character_study", prose) is None


def test_character_study_unnamed_flagged():
    prose = "She sat in the quarterly review for the third time that week, and the tightening arrived."
    assert check_character_study_naming("character_study", prose) == "CHARACTER_STUDY_UNNAMED"


def test_naming_only_applies_to_character_study():
    unnamed = "She sat in the quiet room and did not move."
    assert check_character_study_naming("atmospheric", unnamed) is None
    assert check_character_study_naming("direct_teaching", unnamed) is None
    assert check_character_study_naming(None, unnamed) is None


# ── §9 variety ────────────────────────────────────────────────────────────
def test_variety_flags_single_type():
    assert story_type_variety_flag(["character_study", "character_study"]) == "LOW_STORY_TYPE_VARIETY"


def test_variety_passes_two_distinct():
    assert story_type_variety_flag(["character_study", "parable"]) is None


def test_variety_ignores_untagged_and_empty():
    assert story_type_variety_flag([]) is None
    assert story_type_variety_flag(["", "  "]) is None  # untagged book → no opinion


# ── registry: principle teachers ──────────────────────────────────────────
def test_load_principle_teachers_finds_maat():
    principle = load_principle_teachers()
    assert "maat" in principle, "maat carries teacher_as_principle: true in the registry"


# ── end-to-end yaml atom lint ─────────────────────────────────────────────
def _write_atom(tmp_path: Path, meta: str, body: str) -> Path:
    d = tmp_path / "STORY"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "test_STORY_000.yaml"
    p.write_text(f"{meta}\nbody: |\n{textwrap.indent(body, '  ')}\n", encoding="utf-8")
    return p


def test_yaml_atom_conformance_violation_fails(tmp_path):
    body = (
        "There was a woman who sat outside the interview room. Rinpoche walked past and "
        "stopped. She said she was nervous. He looked at her and walked on, and she "
        "realized the battle was one she had invented, and it cost her the morning."
    )
    p = _write_atom(
        tmp_path,
        "atom_id: test_STORY_000\nstory_origin: composite\nstory_type: recognition_exchange\nband: '2'",
        body,
    )
    res = lint_story_atom_yaml(p)
    assert res.status == "FAIL"
    assert "COMPOSITE_FORBIDS_RECOGNITION_EXCHANGE" in res.flags


def test_yaml_atom_conformant_not_failed_by_conformance(tmp_path):
    body = (
        "Naomi sat in her car outside the hospital and could not turn the ignition. She had "
        "wanted to be the strong one, but she couldn't stop shaking, and she realized she had "
        "been exhausted for months and had lost sleep pretending otherwise."
    )
    p = _write_atom(
        tmp_path,
        "atom_id: test_STORY_001\nstory_origin: composite\nstory_type: character_study\nband: '3'",
        body,
    )
    res = lint_story_atom_yaml(p)
    # named character_study, conformant metadata → no conformance/naming flags
    assert "CHARACTER_STUDY_UNNAMED" not in res.flags
    assert not any(
        f.startswith("COMPOSITE_") or f.startswith("PRINCIPLE_") or f == "UNKNOWN_STORY_TYPE"
        for f in res.flags
    )
