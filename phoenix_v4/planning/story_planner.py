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
arc positions are planned against three story anchors:
  SCENE slot 0 (e.g., sec2)  → recognition      (early beat)
  SCENE slot 1 (e.g., sec5)  → mechanism_proof  (middle beat)
  SCENE slot 2 (e.g., sec9)  → turning_point    (late beat, ch1/ch2)
                              → embodiment       (late beat, last chapter of phase)

These are planner anchors, not a license for raw back-to-back vignette dumps.
The rendering layer is expected to keep intervening non-story material so the
chapter reads as one narrative unit rather than stacked same-character cold opens.

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


def _slot_arcs_for_entry(
    is_final_chapter: bool,
    story_picks_map: dict,
) -> Tuple[str, str, str]:
    """Arc positions for a twelve-shape continuity-plan chapter.

    Plan story_picks are authoritative for the closer position: a chapter whose
    picks name embodiment gets the embodiment arc even when the phase-derived
    default says turning_point, and vice versa (ch10-embodiment regression
    2026-07-07 — the phase default silently discarded the plan's embodiment
    pick and double-booked the neighbouring chapter's turning_point variant).
    Chapters that pick neither (or both) fall back to the phase default.
    """
    if "embodiment" in story_picks_map and "turning_point" not in story_picks_map:
        return _SLOT_ARC_FINAL
    if "turning_point" in story_picks_map and "embodiment" not in story_picks_map:
        return _SLOT_ARC
    return _SLOT_ARC_FINAL if is_final_chapter else _SLOT_ARC

_DEFAULT_ENGINES = [
    "overwhelm", "shame", "spiral", "comparison", "false_alarm", "grief", "watcher"
]

# Heuristic: a "named" character starts with a capital letter and is not a
# structural word.
_STRUCTURAL_STARTS = frozenset(
    ["The", "There", "It", "A", "An", "At", "On", "In", "She", "He", "They"]
)

# Tokens that look like proper nouns at sentence open but are not character names.
_NER_REJECT = frozenset(
    [
        "The", "Another", "It", "It's", "There", "Their", "His", "Her", "This", "That",
        "A", "An", "She", "He", "They", "Third", "Fourth", "Fifth", "First", "Second",
        "Last", "Next", "Hey", "Four", "Five", "Sixteen", "Thanksgiving", "Monday",
        "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Zoom",
        "April", "Not", "But", "And", "When", "What", "How", "Why", "After", "Before",
    ]
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
    character: Optional[str]  # recurring proper noun in the text, or None
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

def _valid_name_token(tok: str) -> bool:
    return bool(tok) and tok[0].isupper() and tok not in _NER_REJECT and len(tok) >= 2


def _token_count(text: str, name: str) -> int:
    return len(re.findall(rf"\b{re.escape(name)}(?:'s)?\b", text, flags=re.I))


def _extract_character(text: str) -> Optional[str]:
    """Return a recurring proper-noun character name from atom text (NER pass)."""
    body = text.strip()
    if not body:
        return None
    open_m = re.match(r"^([A-Z][A-Za-zÀ-ÖØ-öø-ÿ]+)(?:'s|'s|\s)", body)
    if open_m:
        tok = open_m.group(1).rstrip("'")
        if _valid_name_token(tok):
            return tok
    seen: list[str] = []
    for m in re.finditer(r"\b([A-Z][A-Za-zÀ-ÖØ-öø-ÿ']+)(?:'s)?\b", body):
        tok = m.group(1).rstrip("'")
        if not _valid_name_token(tok) or tok in seen:
            continue
        if _token_count(body, tok) >= 2:
            seen.append(tok)
    if seen:
        return seen[0]
    sentences = re.split(r"(?<=[.!?])\s+", body)
    for sent in (sentences[:3] if len(sentences) >= 3 else sentences):
        words = sent.split()
        for i, w in enumerate(words):
            if i == 0:
                continue
            tok = w.rstrip("'s,.\"")
            if _valid_name_token(tok) and _token_count(body, tok) >= 2:
                return tok
    return None


def _load_atoms_for_engine(
    base: Path,
    engine: str,
    locale: Optional[str] = None,
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
            # character / variant / word_count derive from the English source so
            # story selection stays deterministic and locale-independent. Only the
            # RENDERED text is swapped to the localized sibling when one exists at
            # {arc_pos}/locales/{locale}/micro/{stem}.txt; otherwise English is kept
            # (honest fallback, flagged by the locale-fallback gate). en-US: byte-identical.
            render_text = text
            if locale and locale != "en-US":
                loc_f = engine_dir / arc_pos / "locales" / locale / "micro" / f.name
                if loc_f.is_file():
                    loc_text = loc_f.read_text(encoding="utf-8").strip()
                    if loc_text:
                        render_text = loc_text
            atoms.append(
                AtomFile(
                    path=f,
                    arc_position=arc_pos,
                    engine=engine,
                    variant=f.stem,
                    character=_extract_character(text) or "unknown",
                    word_count=len(text.split()),
                    text=render_text,
                )
            )
    return atoms


def _load_all_atoms(
    persona_id: str,
    topic: str,
    repo_root: Path,
    engines: Optional[List[str]] = None,
    locale: Optional[str] = None,
) -> List[AtomFile]:
    base = repo_root / "story_atoms" / persona_id / "anchored" / topic
    if not base.is_dir():
        return []
    all_atoms: List[AtomFile] = []
    for engine in (engines or _DEFAULT_ENGINES):
        all_atoms.extend(_load_atoms_for_engine(base, engine, locale=locale))
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


_STORY_PICK_ARCS = frozenset({"recognition", "mechanism_proof", "turning_point", "embodiment"})


def normalize_story_pick_variant(raw: str) -> str:
    """Normalize plan story_picks value to variant stem (e.g. v03)."""
    text = str(raw or "").strip()
    if not text:
        return ""
    if text.lower().startswith("v") and " " not in text:
        return text
    parts = text.split()
    return parts[-1] if parts else text


def find_atom_by_variant(
    all_atoms: List[AtomFile],
    arc_position: str,
    variant: str,
) -> Optional[AtomFile]:
    """Resolve a story atom file by arc position + variant stem."""
    v = normalize_story_pick_variant(variant)
    if not v or arc_position not in ARC_POSITIONS:
        return None
    matches = [a for a in all_atoms if a.arc_position == arc_position and a.variant == v]
    return matches[0] if matches else None


def _pick_arc_atom(
    arc_pos: str,
    primary_character: str,
    char_idx: Dict[str, Dict[str, List[AtomFile]]],
    all_atoms: List[AtomFile],
    seed: str,
    story_num: int,
    used_atom_paths: set,
    mode: str = "soft",
    *,
    forced_variant: str = "",
) -> Optional[AtomFile]:
    """Pick one arc-position atom; explicit variant pin bypasses deterministic_index."""
    if forced_variant:
        chosen = find_atom_by_variant(all_atoms, arc_pos, forced_variant)
        if chosen is None:
            return None
        used_atom_paths.add(chosen.path)
        return chosen

    char_arcs = char_idx.get(primary_character, {})
    available = [
        a for a in char_arcs.get(arc_pos, [])
        if a.path not in used_atom_paths and a.word_count >= 30
    ]
    if available:
        idx = _deterministic_index(f"{seed}:story:{story_num}:{arc_pos}:primary", len(available))
        chosen = available[idx]
    else:
        if mode == "hard":
            anchored = [
                a for a in all_atoms
                if a.arc_position == arc_pos
                and a.path not in used_atom_paths
                and a.word_count >= 30
                and a.character == primary_character
            ]
            if not anchored:
                anchored = [
                    a for a in all_atoms
                    if a.arc_position == arc_pos
                    and a.path not in used_atom_paths
                    and a.word_count >= 30
                    and a.character in ("unknown", "")
                    and primary_character in a.text
                ]
            if not anchored:
                return None
            idx = _deterministic_index(
                f"{seed}:story:{story_num}:{arc_pos}:anchored_text", len(anchored)
            )
            chosen = anchored[idx]
        else:
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

    used_atom_paths.add(chosen.path)
    return chosen


def _story_assembly_mode(runtime_format: str, *, twelve_shape: bool = False) -> str:
    """deep_book_6h and twelve_shape use hard same-character continuity."""
    if twelve_shape:
        return "hard"
    return "hard" if (runtime_format or "").strip() == "deep_book_6h" else "soft"


def _character_has_full_coverage(
    char: str,
    char_idx: Dict[str, Dict[str, List[AtomFile]]],
    used_atom_paths: set,
) -> bool:
    char_arcs = char_idx.get(char, {})
    for arc_pos in ARC_POSITIONS:
        fresh = [
            a for a in char_arcs.get(arc_pos, [])
            if a.path not in used_atom_paths and a.word_count >= 30
        ]
        if not fresh:
            return False
    return True


def _assemble_story(
    primary_character: str,
    char_idx: Dict[str, Dict[str, List[AtomFile]]],
    all_atoms: List[AtomFile],
    seed: str,
    story_num: int,
    used_atom_paths: set,
    mode: str = "soft",
    story_picks: Optional[Dict[str, str]] = None,
) -> Optional[StoryArc]:
    """Build a StoryArc for primary_character; soft mode may borrow other characters."""
    atoms: Dict[str, AtomFile] = {}
    picks = story_picks or {}

    for arc_pos in ARC_POSITIONS:
        forced = normalize_story_pick_variant(picks.get(arc_pos, "")) if picks.get(arc_pos) else ""
        chosen = _pick_arc_atom(
            arc_pos,
            primary_character,
            char_idx,
            all_atoms,
            seed,
            story_num,
            used_atom_paths,
            mode,
            forced_variant=forced,
        )
        if chosen is None:
            if forced:
                return None
            if mode == "hard":
                continue
            return None
        atoms[arc_pos] = chosen

    if not atoms:
        return None

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
    mode: str = "soft",
    planner_warnings: Optional[List[str]] = None,
) -> List[StoryArc]:
    """Select n full-arc stories, preferring characters with the deepest coverage."""
    char_idx = _index_by_character(all_atoms)
    warns = planner_warnings if planner_warnings is not None else []

    def coverage(char: str) -> int:
        return sum(1 for arc in ARC_POSITIONS if char_idx[char].get(arc))

    candidates = sorted(
        char_idx.keys(),
        key=lambda c: (
            0 if c in _STRUCTURAL_STARTS or c == "unknown" else 1,
            1 if _character_has_full_coverage(c, char_idx, set()) else 0,
            coverage(c),
        ),
        reverse=True,
    )

    stories: List[StoryArc] = []
    used_paths: set = set()
    story_num = 0

    for char in candidates:
        if len(stories) >= n:
            break
        if char in _STRUCTURAL_STARTS or char == "unknown":
            continue
        arc = _assemble_story(
            char, char_idx, all_atoms, seed, story_num, used_paths, mode=mode,
        )
        if arc:
            stories.append(arc)
            story_num += 1
        elif mode == "hard":
            warns.append(
                f"story_plan: skipped character {char!r} — incomplete arc coverage (hard mode)"
            )

    while len(stories) < n and mode == "soft":
        arc = _assemble_story(
            primary_character="",
            char_idx={},
            all_atoms=all_atoms,
            seed=seed,
            story_num=story_num,
            used_atom_paths=used_paths,
            mode=mode,
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


def _build_schedule_from_continuity_plan(
    all_atoms: List[AtomFile],
    seed: str,
    continuity_plan: List[dict],
    planner_warnings: Optional[List[str]] = None,
) -> StorySchedule:
    """12-shape: one plan-assigned character per chapter, hard same-character arcs."""
    warns = planner_warnings if planner_warnings is not None else []
    char_idx = _index_by_character(all_atoms)
    schedule = StorySchedule()
    used_paths: set = set()

    for entry in continuity_plan:
        if not isinstance(entry, dict):
            continue
        ch = int(entry.get("chapter") or 0)
        char = str(entry.get("character") or "").strip()
        if ch < 1 or not char:
            continue

        phase_chapters = next(
            (list(r) for r in DEFAULT_PHASE_CHAPTERS.values() if ch in r),
            list(range(1, 13)),
        )
        is_final_chapter = ch == phase_chapters[-1]

        story_picks_map = {
            k: str(v).strip()
            for k, v in (entry.get("story_picks") or {}).items()
            if k in _STORY_PICK_ARCS and str(v).strip()
        }
        slot_arcs = _slot_arcs_for_entry(is_final_chapter, story_picks_map)
        seed_key = f"{seed}:twelve_shape:ch{ch}"

        if story_picks_map:
            chapter_atoms: Dict[str, AtomFile] = {}
            missing = False
            for arc_pos in slot_arcs:
                forced = (
                    normalize_story_pick_variant(story_picks_map[arc_pos])
                    if arc_pos in story_picks_map
                    else ""
                )
                atom = _pick_arc_atom(
                    arc_pos,
                    char,
                    char_idx,
                    all_atoms,
                    seed_key,
                    ch,
                    used_paths,
                    "hard",
                    forced_variant=forced,
                )
                if atom is None:
                    warns.append(
                        f"story_plan:twelve_shape ch{ch}: story_pick {arc_pos}"
                        f"={story_picks_map.get(arc_pos, forced)!r} unresolved"
                    )
                    missing = True
                    break
                chapter_atoms[arc_pos] = atom
            if missing:
                continue
            story_id = f"story_{ch}"
            for sec_idx, arc_pos in zip(SCENE_SECTION_INDICES, slot_arcs):
                atom = chapter_atoms[arc_pos]
                src = (
                    f"story_plan:twelve_shape:ch{ch}:{story_id}:{arc_pos}"
                    f":{atom.engine}:{atom.variant}"
                )
                schedule.assignments[(ch, sec_idx)] = StoryAtomSlot(
                    arc_position=arc_pos,
                    text=atom.text,
                    source=src,
                )
            continue

        arc = _assemble_story(
            char,
            char_idx,
            all_atoms,
            seed_key,
            ch,
            used_paths,
            mode="hard",
        )
        if arc is None:
            warns.append(
                f"story_plan:twelve_shape ch{ch}: could not assemble hard arc for {char!r}"
            )
            continue

        for sec_idx, arc_pos in zip(SCENE_SECTION_INDICES, slot_arcs):
            atom = arc.atoms.get(arc_pos)
            if atom is None:
                continue
            src = (
                f"story_plan:twelve_shape:ch{ch}:{arc.story_id}:{arc_pos}"
                f":{atom.engine}:{atom.variant}"
            )
            schedule.assignments[(ch, sec_idx)] = StoryAtomSlot(
                arc_position=arc_pos,
                text=atom.text,
                source=src,
            )

    return schedule


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
    runtime_format: str = "",
    planner_warnings: Optional[List[str]] = None,
    continuity_plan: Optional[List[dict]] = None,
    locale: Optional[str] = None,
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
    all_atoms = _load_all_atoms(persona_id, topic, repo_root, locale=locale)
    if not all_atoms:
        return StorySchedule()

    if continuity_plan is None:
        try:
            from phoenix_v4.planning.chapter_object_continuity import load_chapter_continuity_plan

            loaded = load_chapter_continuity_plan(persona_id, topic, repo_root)
            if loaded:
                continuity_plan = loaded
        except ImportError:
            pass

    if continuity_plan:
        return _build_schedule_from_continuity_plan(
            all_atoms,
            seed,
            continuity_plan,
            planner_warnings=planner_warnings,
        )

    mode = _story_assembly_mode(runtime_format)
    warns = planner_warnings if planner_warnings is not None else []

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
            if char in _STRUCTURAL_STARTS or char == "unknown":
                continue
            char_arcs = char_idx.get(char, {})
            has_fresh = any(
                a.path not in book_used_paths
                for arcs in char_arcs.values()
                for a in arcs
            )
            if not has_fresh:
                continue
            arc = _assemble_story(
                char,
                char_idx,
                all_atoms,
                phase_seed,
                local_num,
                book_used_paths,
                mode=mode,
            )
            if arc:
                stories.append(arc)
                local_num += 1
                book_story_num += 1
            elif mode == "hard":
                warns.append(
                    f"story_plan:{phase}: could not assemble story for {char!r} (hard mode)"
                )

        while len(stories) < n_per_phase and mode == "soft":
            arc = _assemble_story(
                "", {}, all_atoms, phase_seed, local_num, book_used_paths, mode=mode,
            )
            if arc is None:
                break
            stories.append(arc)
            local_num += 1
            book_story_num += 1

        if len(stories) < n_per_phase:
            warns.append(
                f"story_plan:{phase}: only {len(stories)}/{n_per_phase} full stories scheduled"
            )

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
