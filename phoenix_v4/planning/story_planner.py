"""Story planner: select and schedule full 4-arc character stories per book phase.

Architecture
------------
Each book has 4 phases (HARDSHIP/HELP/HEALING/HOPE), each covering 3 chapters.
The planner selects N_PER_PHASE (default 3) "full arch stories" per phase.

A full arch story = one character's journey through all four arc positions:
  recognition → mechanism_proof → turning_point → embodiment

Atoms are loaded from:
  story_atoms/{persona}/anchored/{topic}/{engine}/{arc_position}/micro/v*.txt

Character matching
------------------
Arc-position atom files share NO guaranteed variant index alignment — v03 of
recognition is Priya, but v03 of mechanism_proof may be Nadia.  The planner:
  1. Scans every atom file and records the first named character found.
  2. Groups atoms by character name across arc positions.
  3. Selects characters with the deepest coverage (most arc positions present).
  4. For arc positions missing from a character, borrows the best-fit atom
     from the shared pool at that arc position (same emotional register, novel
     character name so the reader meets someone new but the arc feels coherent).

Story spread
------------
Each full story is assigned to ONE chapter in the phase.  Within that chapter,
arc positions are spread across the three SCENE section slots:
  SCENE slot 0 (e.g., sec2)  → recognition
  SCENE slot 1 (e.g., sec5)  → mechanism_proof
  SCENE slot 2 (e.g., sec9)  → turning_point  (sec9 in ch1/ch2)
                              → embodiment     (sec9 in the last chapter of phase)

The planner returns a StorySchedule that maps (chapter_index, scene_slot_index)
→ StoryAtomSlot so the injection resolver can look up the exact atom to inject.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from phoenix_v4.planning.registry_resolver import _deterministic_index

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #

ARC_POSITIONS: Tuple[str, ...] = (
    "recognition",
    "mechanism_proof",
    "turning_point",
    "embodiment",
)

BOOK_PHASES: Tuple[str, ...] = ("HARDSHIP", "HELP", "HEALING", "HOPE")

# Default chapter ranges per phase (1-based, inclusive), for a 12-chapter book.
DEFAULT_PHASE_CHAPTERS: Dict[str, range] = {
    "HARDSHIP": range(1, 4),
    "HELP":     range(4, 7),
    "HEALING":  range(7, 10),
    "HOPE":     range(10, 13),
}

# SCENE section indices within a chapter (1-based, as used by the composer).
SCENE_SECTION_INDICES: Tuple[int, ...] = (2, 5, 9)

# Arc positions assigned to each SCENE slot index (0-based within chapter).
# Slot 2 gets embodiment only in the LAST chapter of a phase; otherwise turning_point.
_SLOT_ARC: Tuple[str, str, str] = ("recognition", "mechanism_proof", "turning_point")
_SLOT_ARC_FINAL: Tuple[str, str, str] = ("recognition", "mechanism_proof", "embodiment")

_DEFAULT_ENGINES = [
    "overwhelm", "shame", "spiral", "comparison", "false_alarm", "grief", "watcher"
]

# Heuristic: a "named" character starts with a capital letter and is not a
# structural word.
_STRUCTURAL_STARTS = frozenset(
    ["The", "There", "It", "A", "An", "At", "On", "In", "She", "He", "They"]
)


# --------------------------------------------------------------------------- #
# Data classes
# --------------------------------------------------------------------------- #

@dataclass
class AtomFile:
    path: Path
    arc_position: str
    engine: str
    variant: str
    character: str      # first proper noun found in the text
    word_count: int
    text: str


@dataclass
class StoryArc:
    """One character's full 4-arc narrative (some arc positions may be borrowed)."""
    story_id: str
    primary_character: str
    atoms: Dict[str, AtomFile]  # arc_position → AtomFile


@dataclass
class StoryAtomSlot:
    """What the injection resolver injects at a specific (chapter, section) position."""
    arc_position: str
    text: str
    source: str  # e.g. "story_plan:HARDSHIP:story_1:recognition:overwhelm:v03"


@dataclass
class StorySchedule:
    """Maps (chapter_index, section_index) → StoryAtomSlot."""
    assignments: Dict[Tuple[int, int], StoryAtomSlot] = field(default_factory=dict)

    def get(self, chapter_index: int, section_index: int) -> Optional[StoryAtomSlot]:
        return self.assignments.get((chapter_index, section_index))


# --------------------------------------------------------------------------- #
# Atom loading
# --------------------------------------------------------------------------- #

def _extract_character(text: str) -> str:
    """Return the first apparent proper-noun character name from atom text."""
    words = text.split()
    if not words:
        return "unknown"
    first = words[0].rstrip("'s,.")
    if first not in _STRUCTURAL_STARTS and first[0].isupper():
        return first
    # Try second word
    if len(words) > 1:
        second = words[1].rstrip("'s,.")
        if second[0].isupper() and second not in _STRUCTURAL_STARTS:
            return second
    return first


def _load_atoms_for_engine(
    base: Path,
    engine: str,
) -> List[AtomFile]:
    atoms: List[AtomFile] = []
    engine_dir = base / engine
    if not engine_dir.is_dir():
        return atoms
    for arc_pos in ARC_POSITIONS:
        micro = engine_dir / arc_pos / "micro"
        if not micro.is_dir():
            continue
        for f in sorted(micro.glob("*.txt")):
            text = f.read_text(encoding="utf-8").strip()
            if not text:
                continue
            atoms.append(
                AtomFile(
                    path=f,
                    arc_position=arc_pos,
                    engine=engine,
                    variant=f.stem,
                    character=_extract_character(text),
                    word_count=len(text.split()),
                    text=text,
                )
            )
    return atoms


def _load_all_atoms(
    persona_id: str,
    topic: str,
    repo_root: Path,
    engines: Optional[List[str]] = None,
) -> List[AtomFile]:
    base = repo_root / "story_atoms" / persona_id / "anchored" / topic
    if not base.is_dir():
        return []
    all_atoms: List[AtomFile] = []
    for engine in (engines or _DEFAULT_ENGINES):
        all_atoms.extend(_load_atoms_for_engine(base, engine))
    return all_atoms


# --------------------------------------------------------------------------- #
# Character matching
# --------------------------------------------------------------------------- #

def _index_by_character(atoms: List[AtomFile]) -> Dict[str, Dict[str, List[AtomFile]]]:
    """character → arc_position → [AtomFile]"""
    idx: Dict[str, Dict[str, List[AtomFile]]] = {}
    for a in atoms:
        idx.setdefault(a.character, {}).setdefault(a.arc_position, []).append(a)
    return idx


def _assemble_story(
    primary_character: str,
    char_idx: Dict[str, Dict[str, List[AtomFile]]],
    all_atoms: List[AtomFile],
    seed: str,
    story_num: int,
    used_atom_paths: set,
) -> Optional[StoryArc]:
    """Build a StoryArc for primary_character, filling missing arc positions from the pool."""
    atoms: Dict[str, AtomFile] = {}
    char_arcs = char_idx.get(primary_character, {})

    for arc_pos in ARC_POSITIONS:
        available = [
            a for a in char_arcs.get(arc_pos, [])
            if a.path not in used_atom_paths and a.word_count >= 30
        ]
        if available:
            idx = _deterministic_index(f"{seed}:story:{story_num}:{arc_pos}:primary", len(available))
            chosen = available[idx]
        else:
            # Borrow from the pool — prefer a different character name than primary
            pool = [
                a for a in all_atoms
                if a.arc_position == arc_pos
                and a.path not in used_atom_paths
                and a.word_count >= 30
                and a.character != primary_character
            ]
            if not pool:
                pool = [
                    a for a in all_atoms
                    if a.arc_position == arc_pos and a.word_count >= 30
                ]
            if not pool:
                return None
            idx = _deterministic_index(f"{seed}:story:{story_num}:{arc_pos}:borrow", len(pool))
            chosen = pool[idx]

        atoms[arc_pos] = chosen
        used_atom_paths.add(chosen.path)

    return StoryArc(
        story_id=f"story_{story_num}",
        primary_character=primary_character,
        atoms=atoms,
    )


# --------------------------------------------------------------------------- #
# Story selection
# --------------------------------------------------------------------------- #

def _select_stories(
    all_atoms: List[AtomFile],
    seed: str,
    n: int,
) -> List[StoryArc]:
    """Select n full-arc stories, preferring characters with the deepest coverage."""
    char_idx = _index_by_character(all_atoms)

    # Score characters: more arc positions = higher priority.
    def coverage(char: str) -> int:
        return sum(1 for arc in ARC_POSITIONS if char_idx[char].get(arc))

    # Prefer named characters over structural starts, then by coverage depth.
    candidates = sorted(
        char_idx.keys(),
        key=lambda c: (
            0 if c in _STRUCTURAL_STARTS else 1,  # named first
            coverage(c),                            # deeper coverage
        ),
        reverse=True,
    )

    stories: List[StoryArc] = []
    used_paths: set = set()
    story_num = 0

    for char in candidates:
        if len(stories) >= n:
            break
        arc = _assemble_story(char, char_idx, all_atoms, seed, story_num, used_paths)
        if arc:
            stories.append(arc)
            story_num += 1

    # If we still need more stories (sparse pool), fill with pool-only arcs.
    while len(stories) < n:
        arc = _assemble_story(
            primary_character="",
            char_idx={},
            all_atoms=all_atoms,
            seed=seed,
            story_num=story_num,
            used_atom_paths=used_paths,
        )
        if arc is None:
            break
        stories.append(arc)
        story_num += 1

    return stories


# --------------------------------------------------------------------------- #
# Schedule building
# --------------------------------------------------------------------------- #

def _schedule_phase(
    phase: str,
    stories: List[StoryArc],
    chapter_range: range,
) -> Dict[Tuple[int, int], StoryAtomSlot]:
    """Assign stories to (chapter, section) slots within a phase.

    One story per chapter.  Arc positions spread across the three SCENE slots.
    The last chapter in the phase gets embodiment in slot 2 instead of turning_point.
    """
    assignments: Dict[Tuple[int, int], StoryAtomSlot] = {}
    chapters = list(chapter_range)

    for story_idx, story in enumerate(stories):
        if story_idx >= len(chapters):
            break
        ch = chapters[story_idx]
        is_final_chapter = (ch == chapters[-1])
        slot_arcs = _SLOT_ARC_FINAL if is_final_chapter else _SLOT_ARC

        for slot_i, (sec_idx, arc_pos) in enumerate(zip(SCENE_SECTION_INDICES, slot_arcs)):
            atom = story.atoms.get(arc_pos)
            if atom is None:
                continue
            src = (
                f"story_plan:{phase}:{story.story_id}:{arc_pos}"
                f":{atom.engine}:{atom.variant}"
            )
            assignments[(ch, sec_idx)] = StoryAtomSlot(
                arc_position=arc_pos,
                text=atom.text,
                source=src,
            )

    return assignments


# --------------------------------------------------------------------------- #
# Public API
# --------------------------------------------------------------------------- #

def build_story_schedule(
    persona_id: str,
    topic: str,
    seed: str,
    repo_root: Path,
    n_per_phase: int = 3,
    phase_chapters: Optional[Dict[str, range]] = None,
) -> StorySchedule:
    """Build a full-book story schedule: 3-6 full-arch stories per phase.

    Returns a StorySchedule mapping (chapter_index, section_index) → StoryAtomSlot.
    The injection resolver calls schedule.get(chapter_index, section_index) and
    uses the result if not None.

    Args:
        persona_id: persona slug (e.g. "gen_z_professionals")
        topic:      topic slug (e.g. "anxiety")
        seed:       book-level seed for deterministic selection
        repo_root:  repo root Path
        n_per_phase: number of full stories per book phase (3-6)
        phase_chapters: override the default HARDSHIP/HELP/HEALING/HOPE chapter ranges
    """
    all_atoms = _load_all_atoms(persona_id, topic, repo_root)
    if not all_atoms:
        return StorySchedule()

    p_chapters = phase_chapters or DEFAULT_PHASE_CHAPTERS
    schedule = StorySchedule()

    # Share used_atom_paths across phases so each atom appears in at most one phase.
    # This gives readers 12 distinct character vignettes (3 stories × 4 phases)
    # rather than the same characters repeating across the book.
    book_used_paths: set = set()
    book_story_num = 0

    char_idx = _index_by_character(all_atoms)
    candidates = sorted(
        char_idx.keys(),
        key=lambda c: (
            0 if c in _STRUCTURAL_STARTS else 1,
            sum(1 for arc in ARC_POSITIONS if char_idx[c].get(arc)),
        ),
        reverse=True,
    )

    for phase in BOOK_PHASES:
        ch_range = p_chapters.get(phase, range(1, 4))
        phase_seed = f"{seed}:story_plan:{phase}"
        stories: List[StoryArc] = []
        local_num = 0

        for char in candidates:
            if len(stories) >= n_per_phase:
                break
            # Skip characters whose atoms are all already used in a prior phase.
            char_arcs = char_idx.get(char, {})
            has_fresh = any(
                a.path not in book_used_paths
                for arcs in char_arcs.values()
                for a in arcs
            )
            if not has_fresh:
                continue
            arc = _assemble_story(
                char, char_idx, all_atoms, phase_seed, local_num, book_used_paths
            )
            if arc:
                stories.append(arc)
                local_num += 1
                book_story_num += 1

        # Fill any remaining slots from the pool (all phases exhausted the named characters).
        while len(stories) < n_per_phase:
            arc = _assemble_story(
                "", {}, all_atoms, phase_seed, local_num, book_used_paths
            )
            if arc is None:
                break
            stories.append(arc)
            local_num += 1
            book_story_num += 1

        phase_assignments = _schedule_phase(phase, stories, ch_range)
        schedule.assignments.update(phase_assignments)

    return schedule


def describe_schedule(schedule: StorySchedule) -> str:
    """Human-readable summary of the story schedule for logging/audit."""
    lines = ["Story Schedule:"]
    for (ch, sec), slot in sorted(schedule.assignments.items()):
        char = slot.source.split(":")[4] if len(slot.source.split(":")) > 4 else "?"
        lines.append(
            f"  Ch{ch:2d}/sec{sec:2d}  {slot.arc_position:20s}  {char}  src={slot.source}"
        )
    return "\n".join(lines)
