"""Tests for registry_resolver._parse_canonical_txt delimiter handling.

Locks the #5530 educators×imposter_syndrome failure class:
  header-present + single-delimiter/single-section must NOT silently yield
  zero usable atoms. Valid legacy parses; malformed fails with CanonicalParseError.
  Header count is never treated as proof of usable depth.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning.registry_resolver import (
    CanonicalParseError,
    _parse_canonical_txt,
)


def _write(tmp_path: Path, text: str, name: str = "CANONICAL.txt") -> Path:
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_two_delimiter_valid_blocks_parse(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "## REFLECTION v01\n"
        "---\n"
        "family: F1\n"
        "voice_mode: teacher\n"
        "---\n"
        "What I notice is the mechanism activating in the room.\n"
        "---\n"
        "\n"
        "## REFLECTION v02\n"
        "---\n"
        "family: F2\n"
        "---\n"
        "What it has cost me is the years of over-preparing.\n"
        "---\n",
    )
    atoms = _parse_canonical_txt(path, slot_type="REFLECTION")
    assert len(atoms) == 2
    assert atoms[0]["atom_id"] == "REFLECTION v01"
    assert "mechanism activating" in atoms[0]["content"]
    assert atoms[0]["metadata"].get("family") == "F1"
    assert atoms[0]["delimiter_shape"] == "two-delimiter"
    assert atoms[1]["delimiter_shape"] == "two-delimiter"


def test_single_delimiter_legacy_parses_as_prose(tmp_path: Path) -> None:
    """The educators/imposter pre-#5530 shape: header + one --- + prose."""
    path = _write(
        tmp_path,
        "## REFLECTION v01\n"
        "---\n"
        "What I notice is the particular texture of standing at the front "
        "of the room on the first day of a new course.\n"
        "\n"
        "## REFLECTION v02\n"
        "---\n"
        "What it has cost me is most visible in the time I spent over-preparing.\n",
    )
    atoms = _parse_canonical_txt(path, slot_type="REFLECTION")
    assert len(atoms) == 2
    assert "particular texture" in atoms[0]["content"]
    assert "over-preparing" in atoms[1]["content"]
    assert atoms[0]["metadata"] == {}
    assert atoms[0]["delimiter_shape"] == "single-delimiter"


def test_single_section_legacy_with_closing_delimiter_parses(tmp_path: Path) -> None:
    """`--- / prose / ---` must not silently drop (prose sat in meta slot)."""
    path = _write(
        tmp_path,
        "## REFLECTION v01\n"
        "---\n"
        "Standing at the front of the room, the mechanism activates.\n"
        "---\n",
    )
    atoms = _parse_canonical_txt(path, slot_type="REFLECTION")
    assert len(atoms) == 1
    assert "mechanism activates" in atoms[0]["content"]
    assert atoms[0]["delimiter_shape"] == "single-section-legacy"


def test_malformed_two_delimiter_empty_prose_fails_loudly(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "## REFLECTION v01\n"
        "---\n"
        "family: F1\n"
        "voice_mode: teacher\n"
        "---\n"
        "---\n",
    )
    with pytest.raises(CanonicalParseError, match="empty prose|no usable"):
        _parse_canonical_txt(path, slot_type="REFLECTION")


def test_header_only_fails_loudly(tmp_path: Path) -> None:
    path = _write(tmp_path, "## REFLECTION v01\n\n## REFLECTION v02\n")
    with pytest.raises(CanonicalParseError, match="header|usable"):
        _parse_canonical_txt(path, slot_type="REFLECTION")


def test_empty_placeholder_blocks_between_valid_atoms_are_skipped(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "## REFLECTION v01\n"
        "---\n"
        "First usable atom.\n"
        "\n"
        "## REFLECTION v02\n"
        "---\n"
        "\n"
        "## REFLECTION v03\n"
        "---\n"
        "Second usable atom.\n",
    )
    atoms = _parse_canonical_txt(path, slot_type="REFLECTION")
    assert [atom["atom_id"] for atom in atoms] == ["REFLECTION v01", "REFLECTION v03"]
    assert atoms[0]["content"] == "First usable atom."
    assert atoms[1]["content"] == "Second usable atom."


def test_placeholder_only_file_still_fails_loudly(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "## REFLECTION v01\n"
        "---\n"
        "\n"
        "## REFLECTION v02\n"
        "---\n",
    )
    with pytest.raises(CanonicalParseError, match="zero usable atoms|usable depth"):
        _parse_canonical_txt(path, slot_type="REFLECTION")


def test_metadata_only_placeholders_before_next_header_are_skipped(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "## RECOGNITION v01\n"
        "---\n"
        "path: placeholder\n"
        "BAND: 2\n"
        "---\n"
        "RECOGNITION v02\n"
        "---\n"
        "\n"
        "## RECOGNITION v03\n"
        "---\n"
        "path: real\n"
        "BAND: 4\n"
        "---\n"
        "Usable prose survives after placeholder variants.\n"
        "---\n",
    )
    atoms = _parse_canonical_txt(path, slot_type="RECOGNITION")
    assert [atom["atom_id"] for atom in atoms] == ["RECOGNITION v03"]
    assert atoms[0]["metadata"]["path"] == "real"
    assert "Usable prose survives" in atoms[0]["content"]


def test_pre_delimiter_metadata_plus_prose_parses(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        "## COMPRESSION v30\n"
        "compression_family: C5\n"
        "Recovery content is something you consume instead of something you do.\n"
        "---\n"
        "---\n"
        "---\n",
    )
    atoms = _parse_canonical_txt(path, slot_type="COMPRESSION")
    assert len(atoms) == 1
    assert atoms[0]["delimiter_shape"] == "pre-delimiter-legacy"
    assert atoms[0]["metadata"]["compression_family"] == "C5"
    assert "Recovery content" in atoms[0]["content"]


def test_header_count_is_not_usable_depth(tmp_path: Path) -> None:
    """Headers can be counted while usable atoms stay zero — must raise, not []."""
    text = (
        "## REFLECTION v01\n"
        "---\n"
        "family: F1\n"
        "---\n"
        "\n"
        "## REFLECTION v02\n"
        "---\n"
        "family: F2\n"
        "---\n"
        "\n"
    )
    path = _write(tmp_path, text)
    header_count = text.count("## ")
    assert header_count == 2
    with pytest.raises(CanonicalParseError):
        _parse_canonical_txt(path, slot_type="REFLECTION")
    # Pre-fix behavior returned []; prove we never treat headers as depth.
    # (If someone catches and returns [], that reintroduces the silent bug.)


def test_missing_file_returns_empty(tmp_path: Path) -> None:
    assert _parse_canonical_txt(tmp_path / "nope.txt") == []


def test_imposter_syndrome_silent_zero_impossible(tmp_path: Path) -> None:
    """Regression: header-present single-delimiter must yield usable atoms."""
    path = _write(
        tmp_path,
        "## REFLECTION v01\n"
        "---\n"
        "What I notice is the mechanism of imposter syndrome in the classroom.\n",
    )
    atoms = _parse_canonical_txt(path, slot_type="REFLECTION")
    assert len(atoms) >= 1
    assert atoms[0]["content"].strip()
    # Never the silent failure: headers implied, usable == 0, no exception.
    assert not (len(atoms) == 0)
