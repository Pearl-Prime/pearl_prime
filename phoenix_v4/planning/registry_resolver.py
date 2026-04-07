"""
Section Registry Resolver — the canonical content pipeline for Pearl Prime.

Loads pre-authored section registries (registry/{topic}.yaml) and
resolves a complete book by selecting one variant per section per chapter
using deterministic hashing. Teacher atoms overlay TEACHER_DOCTRINE and
EXERCISE sections when available.

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

            # Teacher overlay: replace TEACHER_DOCTRINE with teacher atoms
            if sec_type == "TEACHER_DOCTRINE" and teacher_atoms:
                doctrine_atoms = teacher_atoms.get("COMPRESSION", []) or \
                                 teacher_atoms.get("REFLECTION", [])
                if doctrine_atoms:
                    # Pick teacher atom deterministically
                    t_idx = _deterministic_index(
                        f"{seed}:{ch_key}:{sec_key}:teacher", len(doctrine_atoms)
                    )
                    atom = doctrine_atoms[t_idx]
                    resolved_sections.append(ResolvedSection(
                        section_id=sec_id,
                        section_type="TEACHER_DOCTRINE",
                        variant_id=atom["atom_id"],
                        content=atom["content"],
                        purpose=purpose,
                    ))
                    continue

            # Standard variant selection
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
