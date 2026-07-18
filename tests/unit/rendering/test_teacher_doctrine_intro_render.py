"""F5: TEACHER_DOCTRINE_INTRO preamble before Chapter 1 (Holistic v2 Phase B)."""
from __future__ import annotations

from pathlib import Path

from phoenix_v4.planning.chapter_planner import resolve_teacher_doctrine_intro

REPO = Path(__file__).resolve().parents[3]


def test_ahjan_gen_z_anxiety_atom_verbatim():
    body = resolve_teacher_doctrine_intro(
        "gen_z_professionals",
        "anxiety",
        "ahjan",
        REPO,
        chapter_architecture_version=2,
    )
    assert "Thai Forest tradition" in body
    assert "bracing as suffering" in body


def test_v1_architecture_returns_empty():
    assert resolve_teacher_doctrine_intro(
        "gen_z_professionals", "anxiety", "ahjan", REPO, chapter_architecture_version=1,
    ) == ""


def test_missing_atom_falls_back_to_doctrine_yaml():
    body = resolve_teacher_doctrine_intro(
        "gen_z_professionals",
        "anxiety",
        "nonexistent_teacher_xyz",
        REPO,
        chapter_architecture_version=2,
    )
    assert body == ""


def test_opd137_ahjan_atom_exists_at_canonical_path():
    """OPD-137: atom presence is the opt-in signal for prepend in run_pipeline.py
    (regardless of --chapter-architecture-version). Guard the atom path against rename."""
    atom = (
        REPO / "atoms" / "gen_z_professionals" / "anxiety"
        / "TEACHER_DOCTRINE_INTRO" / "ahjan" / "CANONICAL.txt"
    )
    assert atom.is_file(), f"OPD-137 atom path drift: {atom} not found"
    body = atom.read_text(encoding="utf-8")
    assert "Thai Forest tradition" in body
    assert "bracing as suffering" in body
    assert "noticing without correction" in body
