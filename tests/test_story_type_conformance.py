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


def test_naming_detects_possessive_and_diacritics():
    from phoenix_v4.quality.story_atom_lint import _has_named_person
    assert _has_named_person("Zoë's PTO request is approved in the time it takes.")
    assert _has_named_person("Marcus is on a call with the project lead.")
    assert _has_named_person("Sam reads the invite three times.")


def test_naming_only_applies_to_character_study():
    unnamed = "She sat in the quiet room and did not move."
    assert check_character_study_naming("atmospheric", unnamed) is None
    assert check_character_study_naming("direct_teaching", unnamed) is None
    assert check_character_study_naming(None, unnamed) is None


def test_character_study_unnamed_is_hard_gate_fail(tmp_path):
    from phoenix_v4.quality.story_atom_lint import _HARD_GATE_FAIL_CODES
    assert "CHARACTER_STUDY_UNNAMED" in _HARD_GATE_FAIL_CODES
    assert "LOW_STORY_TYPE_VARIETY" in _HARD_GATE_FAIL_CODES
    body = (
        "She sat in the quarterly review for the third time that week, and she couldn't "
        "stop shaking, and she realized she had been exhausted for months pretending otherwise."
    )
    p = _write_atom(
        tmp_path,
        "atom_id: test_STORY_unnamed\nstory_origin: composite\nstory_type: character_study\nband: '3'",
        body,
    )
    res = lint_story_atom_yaml(p)
    assert res.status == "FAIL"
    assert "CHARACTER_STUDY_UNNAMED" in res.flags


def test_anchored_story_path_requires_name(tmp_path):
    from phoenix_v4.quality.story_atom_lint import (
        check_anchored_story_naming,
        is_anchored_story_atom_path,
        _escalate,
        lint_story,
        _HARD_GATE_FAIL_CODES,
    )
    p = (
        tmp_path / "story_atoms" / "gen_z_professionals" / "anchored"
        / "anxiety" / "overwhelm" / "recognition" / "micro" / "v01.txt"
    )
    p.parent.mkdir(parents=True)
    prose = "She sat in the quiet room and did not move for a long time."
    p.write_text(prose, encoding="utf-8")
    assert is_anchored_story_atom_path(p)
    assert check_anchored_story_naming(prose) == "CHARACTER_STUDY_UNNAMED"
    base = lint_story(prose, p)
    escalated = _escalate(base, ["CHARACTER_STUDY_UNNAMED"], _HARD_GATE_FAIL_CODES)
    assert escalated.status == "FAIL"


def test_localized_anchored_story_accepts_named_source_sibling(tmp_path):
    from phoenix_v4.quality.story_atom_lint import check_anchored_story_naming

    source = (
        tmp_path / "story_atoms" / "gen_z_professionals" / "anchored"
        / "anxiety" / "overwhelm" / "recognition" / "micro" / "v03.txt"
    )
    source.parent.mkdir(parents=True)
    source.write_text(
        "Priya submits the update and feels the panic before anyone replies.",
        encoding="utf-8",
    )
    localized = (
        tmp_path / "story_atoms" / "gen_z_professionals" / "anchored"
        / "anxiety" / "overwhelm" / "recognition" / "locales" / "zh-TW" / "micro" / "v03.txt"
    )
    localized.parent.mkdir(parents=True)
    localized.write_text(
        "Priya在送出更新後，胸口還是先緊了起來。",
        encoding="utf-8",
    )
    assert check_anchored_story_naming(localized.read_text(encoding="utf-8"), localized) is None


def test_localized_anchored_story_still_fails_when_source_is_unnamed(tmp_path):
    from phoenix_v4.quality.story_atom_lint import check_anchored_story_naming

    source = (
        tmp_path / "story_atoms" / "gen_z_professionals" / "anchored"
        / "anxiety" / "overwhelm" / "recognition" / "micro" / "v04.txt"
    )
    source.parent.mkdir(parents=True)
    source.write_text(
        "She sends the update and feels the panic before anyone replies.",
        encoding="utf-8",
    )
    localized = (
        tmp_path / "story_atoms" / "gen_z_professionals" / "anchored"
        / "anxiety" / "overwhelm" / "recognition" / "locales" / "zh-TW" / "micro" / "v04.txt"
    )
    localized.parent.mkdir(parents=True)
    localized.write_text(
        "她送出更新後，胸口還是先緊了起來。",
        encoding="utf-8",
    )
    assert (
        check_anchored_story_naming(localized.read_text(encoding="utf-8"), localized)
        == "CHARACTER_STUDY_UNNAMED"
    )


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


def test_unknown_story_type_is_warn_not_blocking(tmp_path):
    """Esoteric teacher extension types (receiver_witness, soul_remembrance, …) are
    surfaced as WARN, never a blocking conformance FAIL — don't red-wall CI."""
    from phoenix_v4.quality.story_atom_lint import _CONFORMANCE_FAIL_CODES
    assert "UNKNOWN_STORY_TYPE" not in _CONFORMANCE_FAIL_CODES
    body = (
        "There was a woman who sat in the quiet for a long time. She had lost the thread "
        "and could not sleep, and she realized the silence itself was the teaching she "
        "had been avoiding for most of her striving, exhausting years."
    )
    p = _write_atom(
        tmp_path,
        "atom_id: t_STORY_9\nstory_origin: composite\nstory_type: soul_remembrance\nband: '3'",
        body,
    )
    res = lint_story_atom_yaml(p)
    assert "UNKNOWN_STORY_TYPE" in res.flags
    assert not any(f in _CONFORMANCE_FAIL_CODES for f in res.flags)


def test_localized_and_candidate_atoms_out_of_scope():
    from phoenix_v4.quality.story_atom_lint import _is_in_scope_story_yaml
    assert _is_in_scope_story_yaml(
        Path("SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms/STORY/adi_da_STORY_001.yaml")
    )
    assert not _is_in_scope_story_yaml(
        Path("SOURCE_OF_TRUTH/teacher_banks/adi_da/approved_atoms_localized/ja-JP/STORY/adi_da_STORY_000_ja-JP.yaml")
    )
    assert not _is_in_scope_story_yaml(
        Path("SOURCE_OF_TRUTH/teacher_banks/ahjan/candidate_atoms/STORY/ahjan_STORY_000_mined.yaml")
    )


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
