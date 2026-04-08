"""
Section Registry Resolver — the canonical content pipeline for Pearl Prime.

Loads pre-authored section registries (registry/{topic}.yaml) and
resolves a complete book by selecting one variant per section per chapter
using deterministic hashing.

Two enrichment modes:
  Teacher mode: teacher atoms overlay HOOK, EXERCISE, INTEGRATION, PIVOT,
    PERMISSION, TAKEAWAY, THREAD, TEACHER_DOCTRINE. SCENEs stay from registry.
  Regular mode: persona atoms overlay HOOK, SCENE, STORY from
    atoms/{persona}/{topic}/. REFLECTIONs and INTEGRATIONs stay from registry.

This replaces the atom assembly path (pool_index + slot_resolver) as the
sole content source for book production.

Registry format:
    sections:
      chapter_01:
        chapter: 1
        title: "..."
        sections:
          section_01:
            section_id: ch01_sec01
            type: HOOK
            variants:
              - variant_id: ch01_sec01_hook_f1
                content: "..."
              - variant_id: ch01_sec01_hook_f2
                content: "..."

Usage:
    registry = load_registry("grief")
    book = resolve_book(registry, seed="book001", teacher_id="adi_da")
"""
from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
REGISTRY_ROOT = REPO_ROOT / "registry"
TEACHER_BANKS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
ATOMS_ROOT = REPO_ROOT / "atoms"

# Section types that get overlaid in teacher mode (everything except SCENE and REFLECTION)
_TEACHER_OVERLAY_TYPES = frozenset({
    "TEACHER_DOCTRINE", "HOOK", "EXERCISE", "INTEGRATION",
    "PIVOT", "PERMISSION", "TAKEAWAY", "THREAD",
})
# Section types that get overlaid in regular/persona mode
_PERSONA_OVERLAY_TYPES = frozenset({"HOOK", "SCENE", "STORY"})
# Mapping from registry section type to teacher atom directory name
_TEACHER_TYPE_MAP = {
    "TEACHER_DOCTRINE": ["COMPRESSION", "REFLECTION"],
    "HOOK": ["HOOK"],
    "EXERCISE": ["EXERCISE"],
    "INTEGRATION": ["INTEGRATION"],
    "PIVOT": ["PIVOT"],
    "PERMISSION": ["PERMISSION"],
    "TAKEAWAY": ["TAKEAWAY"],
    "THREAD": ["THREAD"],
}

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]


def _load_yaml(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _deterministic_index(seed: str, pool_size: int) -> int:
    """SHA256-based deterministic selection — same seed always picks same index."""
    if pool_size <= 0:
        return 0
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % pool_size


# ---------------------------------------------------------------------------
# Registry loading
# ---------------------------------------------------------------------------

def load_registry(topic: str, registry_path: Optional[Path] = None) -> dict:
    """Load a section registry for a topic.

    Args:
        topic: Topic ID (e.g., "grief", "anxiety", "burnout")
        registry_path: Explicit path override. If None, auto-discovers
                       from registry/{topic}.yaml

    Returns:
        Parsed registry dict with 'sections' key containing chapter data.

    Raises:
        FileNotFoundError: If no registry exists for the topic.
    """
    if registry_path:
        path = Path(registry_path)
    else:
        path = REGISTRY_ROOT / f"{topic}.yaml"

    if not path.exists():
        raise FileNotFoundError(
            f"No section registry for topic '{topic}'. "
            f"Expected: {path}\n"
            f"Create registry/{topic}.yaml with 12 chapters × 10 sections × 5 variants."
        )

    data = _load_yaml(path)
    sections = data.get("sections", {})
    if not sections:
        raise ValueError(f"Registry at {path} has no 'sections' key or is empty.")

    logger.info("Loaded registry: %s (%d chapters)", path.name, len(sections))
    return data


def available_registries() -> list[str]:
    """Return list of topic IDs that have registries."""
    if not REGISTRY_ROOT.exists():
        return []
    return [
        p.stem
        for p in REGISTRY_ROOT.glob("*.yaml")
    ]


# ---------------------------------------------------------------------------
# Teacher atom overlay
# ---------------------------------------------------------------------------

def _load_teacher_atoms(teacher_id: str) -> dict[str, list[dict]]:
    """Load teacher-specific atoms for overlay (TEACHER_DOCTRINE, EXERCISE, etc.).

    Returns dict keyed by slot type -> list of atom dicts with 'content' field.
    """
    teacher_root = TEACHER_BANKS_ROOT / teacher_id / "approved_atoms"
    if not teacher_root.exists():
        return {}

    atoms: dict[str, list[dict]] = {}
    for slot_dir in teacher_root.iterdir():
        if not slot_dir.is_dir():
            continue
        slot_type = slot_dir.name.upper()
        slot_atoms = []
        for atom_file in sorted(slot_dir.glob("*.yaml")):
            atom_data = _load_yaml(atom_file)
            if atom_data.get("body") or atom_data.get("content"):
                slot_atoms.append({
                    "atom_id": atom_file.stem,
                    "content": atom_data.get("body", atom_data.get("content", "")),
                    "metadata": {k: v for k, v in atom_data.items()
                                 if k not in ("body", "content")},
                })
        if slot_atoms:
            atoms[slot_type] = slot_atoms

    if atoms:
        logger.info("Loaded %d teacher atom types for '%s'",
                     len(atoms), teacher_id)
    return atoms


# ---------------------------------------------------------------------------
# CANONICAL.txt parser (persona atoms)
# ---------------------------------------------------------------------------

def _parse_canonical_txt(path: Path) -> list[dict]:
    """Parse atoms/persona/topic/TYPE/CANONICAL.txt into list of atom dicts.

    Format:
        ## TYPE vNN
        ---
        optional metadata
        ---
        prose body
        ---
    """
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    blocks: list[dict] = []
    current_id = ""
    in_body = False
    body_lines: list[str] = []
    delimiter_count = 0

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            # Save previous block
            if current_id and body_lines:
                content = "\n".join(body_lines).strip()
                if content:
                    blocks.append({"atom_id": current_id, "content": content})
            current_id = stripped.replace("## ", "").strip()
            body_lines = []
            in_body = False
            delimiter_count = 0
        elif stripped == "---":
            delimiter_count += 1
            if delimiter_count >= 2:
                in_body = True
        elif in_body:
            body_lines.append(line)

    # Last block
    if current_id and body_lines:
        content = "\n".join(body_lines).strip()
        if content:
            blocks.append({"atom_id": current_id, "content": content})

    return blocks


def _load_persona_atoms(persona_id: str, topic_id: str) -> dict[str, list[dict]]:
    """Load persona-specific atoms from atoms/{persona}/{topic}/{type}/CANONICAL.txt.

    Returns dict keyed by slot type (HOOK, SCENE, STORY, etc.) -> list of atom dicts.
    """
    persona_root = ATOMS_ROOT / persona_id / topic_id
    if not persona_root.exists():
        return {}

    atoms: dict[str, list[dict]] = {}
    for slot_dir in persona_root.iterdir():
        if not slot_dir.is_dir():
            continue
        slot_type = slot_dir.name.upper()
        canonical = slot_dir / "CANONICAL.txt"
        if canonical.exists():
            parsed = _parse_canonical_txt(canonical)
            if parsed:
                atoms[slot_type] = parsed

    # Also check for engine-specific STORY atoms (atoms/persona/topic/engine/CANONICAL.txt)
    # These are in subdirs like "grief", "shame", "comparison" under the topic dir
    for sub in persona_root.iterdir():
        if sub.is_dir() and (sub / "CANONICAL.txt").exists():
            slot_type_upper = sub.name.upper()
            # Skip if it's already a known slot type dir (HOOK, SCENE, etc.)
            if slot_type_upper in atoms:
                continue
            # This is an engine dir — treat its atoms as STORY type
            parsed = _parse_canonical_txt(sub / "CANONICAL.txt")
            if parsed:
                if "STORY" not in atoms:
                    atoms["STORY"] = []
                atoms["STORY"].extend(parsed)

    if atoms:
        logger.info("Loaded %d persona atom types for '%s/%s'",
                     len(atoms), persona_id, topic_id)
    return atoms


# ---------------------------------------------------------------------------
# Book resolution
# ---------------------------------------------------------------------------

class ResolvedSection:
    """A single resolved section within a chapter."""
    __slots__ = ("section_id", "section_type", "variant_id", "content", "purpose")

    def __init__(self, section_id: str, section_type: str, variant_id: str,
                 content: str, purpose: str = ""):
        self.section_id = section_id
        self.section_type = section_type
        self.variant_id = variant_id
        self.content = content
        self.purpose = purpose


class ResolvedChapter:
    """A fully resolved chapter with all sections."""
    __slots__ = ("chapter_index", "title", "sections")

    def __init__(self, chapter_index: int, title: str,
                 sections: list[ResolvedSection]):
        self.chapter_index = chapter_index
        self.title = title
        self.sections = sections

    @property
    def word_count(self) -> int:
        return sum(len(s.content.split()) for s in self.sections)


class ResolvedBook:
    """Complete resolved book from section registry."""
    __slots__ = ("chapters", "topic", "seed", "registry_path", "teacher_id")

    def __init__(self, chapters: list[ResolvedChapter], topic: str, seed: str,
                 registry_path: str = "", teacher_id: str = ""):
        self.chapters = chapters
        self.topic = topic
        self.seed = seed
        self.registry_path = registry_path
        self.teacher_id = teacher_id

    @property
    def word_count(self) -> int:
        return sum(ch.word_count for ch in self.chapters)

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    def to_prose(self) -> str:
        """Render to plain text (chapter headings + section content)."""
        parts: list[str] = []
        for ch in self.chapters:
            parts.append(f"Chapter {ch.chapter_index + 1}")
            parts.append("")
            for sec in ch.sections:
                content = sec.content.strip()
                if content:
                    parts.append(content)
                    parts.append("")
        return "\n".join(parts).strip()


def resolve_book(
    registry: dict,
    seed: str,
    teacher_id: Optional[str] = None,
    persona_id: Optional[str] = None,
) -> ResolvedBook:
    """Resolve a complete book from a section registry.

    For each section in each chapter, selects one variant deterministically
    based on the seed. If teacher_id is provided, overlays teacher-specific
    atoms on TEACHER_DOCTRINE and optionally EXERCISE sections.

    Args:
        registry: Loaded registry dict (from load_registry())
        seed: Deterministic seed string (e.g., "book001" or catalog_id)
        teacher_id: Optional teacher for doctrine/exercise overlay
        persona_id: Optional persona for future persona-aware selection

    Returns:
        ResolvedBook with all chapters and sections resolved.
    """
    sections_data = registry.get("sections", {})
    teacher_atoms = _load_teacher_atoms(teacher_id) if teacher_id else {}
    # Infer topic from registry filename or metadata
    reg_topic = registry.get("topic", "")
    if not reg_topic:
        # Try to extract from sections metadata
        for ch_data in sections_data.values():
            for sec_data in ch_data.get("sections", {}).values():
                meta = sec_data.get("metadata", {})
                if meta.get("topic"):
                    reg_topic = meta["topic"]
                    break
            if reg_topic:
                break
    # Always load persona atoms when persona_id is provided — even in teacher mode.
    # Teacher mode = teacher overlay (doctrine, exercises) + persona overlay (hooks, scenes).
    # Teachers speak TO personas — they don't replace them.
    persona_atoms = _load_persona_atoms(persona_id, reg_topic) if persona_id and reg_topic else {}

    chapters: list[ResolvedChapter] = []

    for ch_key in sorted(sections_data.keys()):
        ch_data = sections_data[ch_key]
        ch_index = ch_data.get("chapter", len(chapters))
        ch_title = ch_data.get("title", f"Chapter {ch_index}")
        ch_sections_data = ch_data.get("sections", {})

        resolved_sections: list[ResolvedSection] = []

        for sec_key in sorted(ch_sections_data.keys()):
            sec_data = ch_sections_data[sec_key]
            sec_id = sec_data.get("section_id", sec_key)
            sec_type = sec_data.get("type", "REFLECTION")
            purpose = sec_data.get("purpose", "")
            variants = sec_data.get("variants", [])

            if not variants:
                logger.warning("Section %s has no variants, skipping", sec_id)
                continue

            # ── OVERLAY PRIORITY ──
            # 1. Teacher atoms for teacher-voiced sections (doctrine, exercises, etc.)
            # 2. Persona atoms for persona-grounded sections (hooks, scenes, stories)
            # 3. Practice library for EXERCISE when atoms are thin (272 exercises with aha + integration)
            # Both teacher + persona can be active simultaneously — teacher speaks TO the persona.
            overlay_content = None
            overlay_id = None

            # Teacher overlay: doctrine, exercises, integration, pivot, permission, etc.
            if teacher_atoms and sec_type in _TEACHER_OVERLAY_TYPES:
                atom_pool: list[dict] = []
                for dir_name in _TEACHER_TYPE_MAP.get(sec_type, [sec_type]):
                    atom_pool = teacher_atoms.get(dir_name, [])
                    if atom_pool:
                        break
                if atom_pool:
                    t_idx = _deterministic_index(
                        f"{seed}:{ch_key}:{sec_key}:teacher", len(atom_pool)
                    )
                    overlay_content = atom_pool[t_idx]["content"]
                    overlay_id = atom_pool[t_idx]["atom_id"]

            # Persona overlay: hooks, scenes, stories (even in teacher mode)
            if not overlay_content and persona_atoms and sec_type in _PERSONA_OVERLAY_TYPES:
                atom_pool = persona_atoms.get(sec_type, [])
                if atom_pool:
                    p_idx = _deterministic_index(
                        f"{seed}:{ch_key}:{sec_key}:persona", len(atom_pool)
                    )
                    overlay_content = atom_pool[p_idx]["content"]
                    overlay_id = atom_pool[p_idx]["atom_id"]

            # Practice library fallback for EXERCISE slots
            if not overlay_content and sec_type == "EXERCISE":
                try:
                    from phoenix_v4.exercises.practice_library_loader import get_exercise_for_chapter
                    composed = get_exercise_for_chapter(
                        chapter_index=len(chapters),
                        topic_id=reg_topic,
                        persona_id=persona_id or "",
                        seed=seed,
                    )
                    if composed:
                        overlay_content = composed
                        overlay_id = f"practice_library:ch{len(chapters)}"
                except Exception:
                    pass  # fall through to registry variant

            if overlay_content:
                resolved_sections.append(ResolvedSection(
                    section_id=sec_id,
                    section_type=sec_type,
                    variant_id=overlay_id or sec_id,
                    content=overlay_content,
                    purpose=purpose,
                ))
                continue

            # ── DEFAULT: use registry variant ──
            v_idx = _deterministic_index(
                f"{seed}:{ch_key}:{sec_key}", len(variants)
            )
            variant = variants[v_idx]
            resolved_sections.append(ResolvedSection(
                section_id=sec_id,
                section_type=sec_type,
                variant_id=variant.get("variant_id", f"{sec_id}_v{v_idx}"),
                content=variant.get("content", ""),
                purpose=purpose,
            ))

        chapters.append(ResolvedChapter(
            chapter_index=len(chapters),
            title=ch_title,
            sections=resolved_sections,
        ))

    topic = registry.get("topic", "unknown")
    reg_path = registry.get("_source_path", "")

    book = ResolvedBook(
        chapters=chapters,
        topic=topic,
        seed=seed,
        registry_path=str(reg_path),
        teacher_id=teacher_id or "",
    )

    logger.info(
        "Resolved book: %d chapters, %d words, seed='%s', teacher='%s'",
        book.chapter_count, book.word_count, seed, teacher_id or "none",
    )
    return book
