"""F2: hard-mode same-character story assembly (Holistic v2 Phase B)."""
from __future__ import annotations

from pathlib import Path

from phoenix_v4.planning.story_planner import (
    AtomFile,
    ARC_POSITIONS,
    StoryArc,
    _assemble_story,
    _index_by_character,
    _story_assembly_mode,
    build_story_schedule,
)

REPO = Path(__file__).resolve().parents[3]


def _atom(char: str, arc: str, n: int) -> AtomFile:
    text = (
        f"{char} does something difficult in {arc}. {char} continues the beat in {arc}. "
        f"{char} feels the weight of the moment and stays with it. {char} notices the room, "
        f"the breath, and the story moving forward through {arc} without fixing anything yet."
    )
    return AtomFile(
        path=Path(f"/fake/{char}/{arc}/v{n:02d}.txt"),
        arc_position=arc,
        engine="overwhelm",
        variant=f"v{n:02d}",
        character=char,
        word_count=len(text.split()),
        text=text,
    )


def test_hard_mode_never_borrows_foreign_character():
    priya_atoms = [_atom("Priya", arc, i) for i, arc in enumerate(ARC_POSITIONS[:2])]
    marcus_atoms = [_atom("Marcus", arc, i + 10) for i, arc in enumerate(ARC_POSITIONS)]
    all_atoms = priya_atoms + marcus_atoms
    char_idx = _index_by_character(all_atoms)
    arc = _assemble_story(
        "Priya", char_idx, all_atoms, "seed", 0, set(), mode="hard",
    )
    assert arc is not None
    assert all(a.character == "Priya" for a in arc.atoms.values())
    assert len(arc.atoms) == 2


def test_hard_mode_returns_none_when_primary_has_no_atoms():
    char_idx = _index_by_character([_atom("Marcus", "recognition", 1)])
    arc = _assemble_story(
        "Priya", char_idx, [], "seed", 0, set(), mode="hard",
    )
    assert arc is None


def test_soft_mode_borrows_other_character():
    priya_atoms = [_atom("Priya", arc, i) for i, arc in enumerate(ARC_POSITIONS[:2])]
    marcus_atoms = [_atom("Marcus", arc, i + 10) for i, arc in enumerate(ARC_POSITIONS)]
    all_atoms = priya_atoms + marcus_atoms
    char_idx = _index_by_character(all_atoms)
    arc = _assemble_story(
        "Priya", char_idx, all_atoms, "seed", 0, set(), mode="soft",
    )
    assert arc is not None
    assert any(a.character != "Priya" for a in arc.atoms.values())


def test_runtime_format_selects_mode():
    assert _story_assembly_mode("deep_book_6h") == "hard"
    assert _story_assembly_mode("micro_book_15") == "soft"


def test_deep_book_schedule_same_character_per_chapter():
    sched = build_story_schedule(
        "gen_z_professionals", "anxiety", "hard_test", REPO, runtime_format="deep_book_6h",
    )
    by_ch: dict[int, list[str | None]] = {}
    for (ch, _sec), slot in sched.assignments.items():
        from phoenix_v4.planning.story_planner import _extract_character

        by_ch.setdefault(ch, []).append(_extract_character(slot.text))
    for ch, names in by_ch.items():
        assert len(set(names)) <= 1, f"chapter {ch} mixed characters: {names}"
