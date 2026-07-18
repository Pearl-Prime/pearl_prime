"""Speech atom selector — deterministic, anti-repetition manga dialogue selection.

Loads ``config/source_of_truth/manga_speech_atoms/schema.yaml`` and exposes:

  filter_candidates()     — narrow atoms by genre / archetype / emotion / intensity
  select_atom()           — deterministically pick one atom, respecting anti-repetition
  select_variant()        — deterministically pick a text variant from the selected atom
  fill_slots()            — replace {stake}/{name}/{place}/{opponent} from context
  select_atoms_for_chapter() — high-level: assign atoms to every dialogue panel

Anti-repetition rules (from specs/manga_speech_atom_taxonomy.md §2):

  ``forbidden_after``   — directional, within-chapter, adjacent-panel constraint
  ``cooldown_chapters`` — cross-chapter frequency cap; 0 = no cap

Selection algorithm mirrors ``_deterministic_int`` from ``story_architect.py`` /
``story_strategy_loader.py`` for consistent reproducibility across all components.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Module-level cache
# ---------------------------------------------------------------------------

_REPO_ROOT: Path | None = None
_ATOMS_CACHE: list[dict] | None = None


def _repo_root() -> Path:
    global _REPO_ROOT
    if _REPO_ROOT is None:
        _REPO_ROOT = Path(__file__).resolve().parents[2]
    return _REPO_ROOT


def _load_atoms() -> list[dict]:
    """Load (and cache) all atoms from schema.yaml."""
    global _ATOMS_CACHE
    if _ATOMS_CACHE is not None:
        return _ATOMS_CACHE

    p = (
        _repo_root()
        / "config"
        / "source_of_truth"
        / "manga_speech_atoms"
        / "schema.yaml"
    )
    if not p.is_file():
        _ATOMS_CACHE = []
        return _ATOMS_CACHE

    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("PyYAML is required to load speech atoms") from e

    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    _ATOMS_CACHE = list(data.get("atoms") or [])
    return _ATOMS_CACHE


# ---------------------------------------------------------------------------
# Core deterministic primitive
# ---------------------------------------------------------------------------

def _h(seed: str, n: int) -> int:
    """Stable integer in ``[0, n)`` from *seed*.  Same pattern as story_strategy_loader."""
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16) % max(1, n)


# ---------------------------------------------------------------------------
# Anti-repetition helpers
# ---------------------------------------------------------------------------

def _passes_cooldown(
    atom: dict,
    cooldown_history: dict[str, int],
    current_chapter_index: int,
) -> bool:
    """Return True if atom has not been used recently enough to be blocked."""
    cooldown = int(atom.get("cooldown_chapters") or 0)
    if cooldown == 0:
        return True
    last_used = cooldown_history.get(atom.get("atom_id", ""))
    if last_used is None:
        return True
    return (current_chapter_index - last_used) >= cooldown


def _passes_forbidden_after(atom: dict, last_atom_id: str | None) -> bool:
    """Return True if *last_atom_id* is NOT in this atom's ``forbidden_after`` list."""
    if last_atom_id is None:
        return True
    return last_atom_id not in (atom.get("forbidden_after") or [])


# ---------------------------------------------------------------------------
# Candidate filtering
# ---------------------------------------------------------------------------

def filter_candidates(
    genre: str | None = None,
    archetype: str | None = None,
    emotion: str | None = None,
    intensity: str | None = None,
    *,
    atoms: list[dict] | None = None,
) -> list[dict]:
    """Return atoms matching *all* provided dimension filters.

    Any filter that is ``None`` is ignored (match-all for that dimension).
    Loads from disk on first call if *atoms* is not provided.

    Falls back through progressively relaxed criteria when no match is found:
    1. genre + archetype + emotion + intensity  (exact)
    2. genre + emotion + intensity              (drop archetype)
    3. genre + emotion                          (drop intensity)
    4. genre only                               (broadest genre match)
    5. all atoms                                (absolute fallback)
    """
    pool = list(atoms if atoms is not None else _load_atoms())

    def _match(a: dict, g: str | None, ar: str | None, em: str | None, it: str | None) -> bool:
        if g and a.get("genre") != g:
            return False
        if ar and a.get("archetype") != ar:
            return False
        if em and a.get("emotion") != em:
            return False
        if it and a.get("intensity") != it:
            return False
        return True

    # Try progressively relaxed filters until we get at least one match
    fallback_chains: list[tuple[str | None, str | None, str | None, str | None]] = [
        (genre, archetype, emotion, intensity),
        (genre, None,      emotion, intensity),
        (genre, None,      emotion, None     ),
        (genre, None,      None,    None     ),
        (None,  None,      None,    None     ),
    ]
    for g, ar, em, it in fallback_chains:
        result = [a for a in pool if _match(a, g, ar, em, it)]
        if result:
            return result
    return pool  # should never reach here, but guard anyway


# ---------------------------------------------------------------------------
# Atom selection
# ---------------------------------------------------------------------------

def select_atom(
    candidate_atoms: list[dict],
    series_id: str,
    chapter_id: str,
    panel_id: str,
    *,
    cooldown_history: dict[str, int] | None = None,
    last_atom_id: str | None = None,
    current_chapter_index: int = 0,
) -> dict:
    """Deterministically select one atom from *candidate_atoms*.

    Applies anti-repetition rules:
    1. Pass both cooldown + forbidden_after  (preferred)
    2. Relax forbidden_after, keep cooldown  (fallback 1)
    3. Use full candidate list               (fallback 2)

    Returns the selected atom dict.
    """
    if not candidate_atoms:
        raise ValueError("candidate_atoms must not be empty")

    history = cooldown_history or {}
    seed = f"{series_id}:{chapter_id}:{panel_id}"

    # Pass 1: full anti-repetition
    eligible = [
        a for a in candidate_atoms
        if _passes_cooldown(a, history, current_chapter_index)
        and _passes_forbidden_after(a, last_atom_id)
    ]

    if not eligible:
        # Pass 2: relax forbidden_after
        eligible = [
            a for a in candidate_atoms
            if _passes_cooldown(a, history, current_chapter_index)
        ]

    if not eligible:
        # Pass 3: final fallback
        eligible = list(candidate_atoms)

    return eligible[_h(seed, len(eligible))]


# ---------------------------------------------------------------------------
# Variant selection
# ---------------------------------------------------------------------------

def select_variant(
    atom: dict,
    series_id: str,
    chapter_id: str,
    panel_id: str,
) -> str:
    """Deterministically select one text string from an atom's variants.

    The pool is ``[text_template] + variants``; variant 0 is the template.
    Returns the chosen text (may contain ``{slot}`` placeholders).
    """
    all_texts: list[str] = [atom.get("text_template") or ""]
    all_texts.extend(atom.get("variants") or [])
    # Remove empty/None entries
    all_texts = [t for t in all_texts if t]
    if not all_texts:
        return ""
    seed = f"{series_id}:{chapter_id}:{panel_id}:variant"
    return all_texts[_h(seed, len(all_texts))]


# ---------------------------------------------------------------------------
# Slot filling
# ---------------------------------------------------------------------------

_SLOT_DEFAULTS: dict[str, str] = {
    "stake": "everything",
    "name": "them",
    "place": "here",
    "opponent": "you",
}


def fill_slots(text: str, context: dict[str, str] | None = None) -> str:
    """Replace ``{stake}``, ``{name}``, ``{place}``, ``{opponent}`` with context values.

    Falls back to module-level defaults when a slot is not present in *context*.
    """
    ctx = dict(_SLOT_DEFAULTS)
    if context:
        ctx.update(context)
    try:
        return text.format_map(ctx)
    except (KeyError, ValueError):
        # If format fails for any reason, return text as-is
        return text


# ---------------------------------------------------------------------------
# Chapter-level selection
# ---------------------------------------------------------------------------

def select_atoms_for_chapter(
    chapter_script: dict,
    *,
    series_id: str = "",
    genre: str | None = None,
    emotional_job: str | None = None,
    cooldown_history: dict[str, int] | None = None,
    current_chapter_index: int = 0,
    slot_context: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Assign speech atoms to every dialogue panel in *chapter_script*.

    Iterates pages → panels in reading order.  Panels with no dialogue text are
    skipped (silence panels).  The returned dict maps ``panel_id`` to an
    ``AtomAssignment`` dict.

    Parameters
    ----------
    chapter_script:
        Standard ``chapter_script_writer_handoff`` dict.
    series_id:
        Used as seed component for deterministic selection.
    genre:
        Genre string (e.g. "shonen").  Falls back to
        ``chapter_script.get("genre")`` if not provided.
    emotional_job:
        Override ``chapter_script.get("emotional_job")`` for EI-weighted filtering.
    cooldown_history:
        Mutable dict mapping ``atom_id → last_chapter_index_used``.  Updated
        in-place with atoms selected this chapter.
    current_chapter_index:
        Zero-based chapter sequence position.  Used for cooldown comparisons.
    slot_context:
        Values for ``{stake}``, ``{name}``, ``{place}``, ``{opponent}`` slots.

    Returns
    -------
    dict with keys:
      ``assignments``  — dict[panel_id, AtomAssignment]
      ``chapter_id``   — echoed from script
      ``genre``        — resolved genre string
      ``atom_count``   — number of panels that received an atom
    """
    chapter_id = chapter_script.get("chapter_id") or chapter_script.get("series_id") or ""
    resolved_genre = genre or chapter_script.get("genre") or "shonen"
    resolved_job = emotional_job or chapter_script.get("emotional_job") or None

    history: dict[str, int] = cooldown_history if cooldown_history is not None else {}
    assignments: dict[str, dict] = {}
    last_atom_id: str | None = None

    all_atoms = _load_atoms()

    for page in chapter_script.get("pages") or []:
        for panel in page.get("panels") or []:
            panel_id = str(panel.get("panel_id") or "")
            dialogue = panel.get("dialogue") or []

            # Skip silent panels
            has_text = any(
                (isinstance(d, str) and d.strip())
                or (isinstance(d, dict) and str(d.get("text") or "").strip())
                for d in dialogue
            )
            if not has_text:
                continue

            # Infer emotion / intensity / archetype from existing dialogue metadata if available
            emotion: str | None = None
            intensity: str | None = None
            archetype: str | None = None

            # Use first dialogue item if it's a dict with metadata
            first_dl = next(
                (d for d in dialogue if isinstance(d, dict)),
                None,
            )
            if first_dl:
                emotion = first_dl.get("emotion") or None
                intensity = first_dl.get("intensity") or None
                # panel may carry speaker → archetype mapping; best-effort
                archetype = first_dl.get("archetype") or first_dl.get("speaker_archetype") or None

            # Prefer atoms that match emotional_job
            if resolved_job and not emotion:
                # Map emotional_job to emotion dimension
                _JOB_TO_EMOTION = {
                    "shame": "determination",
                    "overwhelm": "anger",
                    "grief": "grief",
                    "false_alarm": "surprise",
                    "spiral": "despair",
                    "watcher": "awe",
                    "comparison": "contempt",
                }
                emotion = _JOB_TO_EMOTION.get(resolved_job)

            candidates = filter_candidates(
                genre=resolved_genre,
                archetype=archetype,
                emotion=emotion,
                intensity=intensity,
                atoms=all_atoms,
            )

            atom = select_atom(
                candidates,
                series_id=series_id,
                chapter_id=chapter_id,
                panel_id=panel_id,
                cooldown_history=history,
                last_atom_id=last_atom_id,
                current_chapter_index=current_chapter_index,
            )

            variant_text = select_variant(atom, series_id, chapter_id, panel_id)
            rendered_text = fill_slots(variant_text, slot_context)

            assignments[panel_id] = {
                "atom_id": atom.get("atom_id"),
                "atom": atom,
                "selected_text": rendered_text,
                "bubble_style": atom.get("bubble_style"),
                "font_override": atom.get("font_override"),
                "sfx_companion": atom.get("sfx_companion"),
                "tail_style": atom.get("tail_style"),
                "position_hint": atom.get("position_hint"),
                "word_count_target": atom.get("word_count_target"),
                "ei_emotion_mapping": atom.get("ei_emotion_mapping"),
            }

            # Update anti-repetition state
            last_atom_id = atom.get("atom_id")
            atom_id_key = atom.get("atom_id") or ""
            if atom_id_key:
                history[atom_id_key] = current_chapter_index

    return {
        "assignments": assignments,
        "chapter_id": chapter_id,
        "genre": resolved_genre,
        "atom_count": len(assignments),
    }


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def list_atom_ids(
    genre: str | None = None,
    archetype: str | None = None,
    emotion: str | None = None,
    intensity: str | None = None,
) -> list[str]:
    """Return sorted list of atom_ids matching the given filters."""
    return sorted(
        a.get("atom_id", "")
        for a in filter_candidates(genre=genre, archetype=archetype,
                                   emotion=emotion, intensity=intensity)
    )
