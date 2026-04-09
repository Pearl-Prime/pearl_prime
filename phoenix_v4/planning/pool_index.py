# DEPRECATED: Atom assembly path. Use section registry pipeline (registry_resolver.py).
# Retained for backward compatibility with topics that lack registries.
# New topics MUST use registry/registry_{topic}.yaml.
"""
Pool index: atoms by slot type for (persona, topic).
Used by capability check and slot resolver. Canonical layout: block-file pattern.
STORY: atoms/<persona>/<topic>/<engine>/CANONICAL.txt (existing).
Other slot types: atoms/<persona>/<topic>/<slot_type>/CANONICAL.txt (or <slot_type>/<engine>/CANONICAL.txt).
"""
from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"
CONFIG_ROOT = REPO_ROOT / "config"
COMPRESSION_ATOMS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "compression_atoms"
logger = logging.getLogger(__name__)


@dataclass
class AtomEntry:
    """Minimal entry for an atom in a pool. atom_source: teacher_native | teacher_synthetic | practice_fallback (Teacher Mode)."""
    atom_id: str
    metadata: Optional[dict[str, Any]] = None
    atom_source: Optional[str] = None  # teacher_native | teacher_synthetic | practice_fallback


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def _bindings_topic_key(topic_slug: str) -> str:
    # grief_topic was renamed to grief; keep backward compat for any stale refs
    if topic_slug == "grief_topic":
        return "grief"
    return topic_slug


def _load_story_entries(
    atoms_root: Path,
    persona_slug: str,
    topic_slug: str,
    bindings: dict,
    locale: Optional[str] = None,
) -> list[AtomEntry]:
    """Load STORY atoms from engines allowed for topic (delegate to assembly_compiler)."""
    from phoenix_v4.planning.assembly_compiler import _load_story_atoms_for_persona_topic
    raw = _load_story_atoms_for_persona_topic(atoms_root, persona_slug, topic_slug, bindings, locale=locale)
    out: list[AtomEntry] = []
    narrative_keys = ("mechanism_depth", "cost_type", "cost_intensity", "identity_stage", "callback_id", "callback_phase")
    for a in raw:
        meta: dict[str, Any] = {"band": a.get("band", 3)}
        if a.get("semantic_family"):
            meta["semantic_family"] = str(a["semantic_family"])
        if a.get("role"):
            meta["role"] = a["role"]
        for k in narrative_keys:
            if k in a and a[k] is not None:
                meta[k] = a[k]
        out.append(AtomEntry(atom_id=a["atom_id"], metadata=meta))
    return out


def _parse_block_file_canonical(path: Path, persona: str, topic: str, slot_type: str) -> list[AtomEntry]:
    """Parse a CANONICAL.txt block file (non-STORY). Blocks: ## TYPE vNN --- metadata --- prose ---."""
    if not path.exists():
        return []
    text = path.read_text()
    # Match ## SOMETHING vNN --- ... ---
    block_re = re.compile(
        r"^##\s+(\S+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---",
        re.MULTILINE,
    )
    out: list[AtomEntry] = []
    for m in block_re.finditer(text):
        _label, ver = m.group(1), m.group(2)
        metadata = m.group(3)
        atom_id = f"{persona}_{topic}_{slot_type}_v{ver}"
        # Optional ID line in metadata overrides
        for line in metadata.splitlines():
            if line.strip().lower().startswith("id:"):
                atom_id = line.split(":", 1)[1].strip()
                break
        out.append(AtomEntry(atom_id=atom_id, metadata={}))
    return out


def _load_compression_pool(persona_slug: str, topic_slug: str) -> list[AtomEntry]:
    """Load COMPRESSION atoms from SOURCE_OF_TRUTH/compression_atoms/approved/<persona>/<topic>/. DEV SPEC 2."""
    approved_dir = COMPRESSION_ATOMS_ROOT / "approved" / persona_slug / topic_slug
    if not approved_dir.exists():
        return []
    entries: list[AtomEntry] = []
    for path in sorted(approved_dir.glob("*.yaml")):
        data = _load_yaml(path)
        if not data:
            continue
        atom_id = data.get("atom_id") or path.stem
        wc = data.get("word_count")
        if wc is not None:
            wc = int(wc)
        meta: dict[str, Any] = {}
        if wc is not None:
            meta["word_count"] = wc
        fam = data.get("compression_family")
        if fam:
            meta["compression_family"] = str(fam)
        entries.append(AtomEntry(atom_id=atom_id, metadata=meta if meta else None))
    return entries


def _load_teacher_pool(teacher_atoms_root: Path, slot_type: str) -> list[AtomEntry]:
    """Load teacher approved atoms from teacher_atoms_root/<slot_type>/*.yaml. Teacher Mode V4. Stamp atom_source from YAML source:."""
    slot_dir = teacher_atoms_root / slot_type
    if not slot_dir.exists():
        return []
    entries: list[AtomEntry] = []
    for path in sorted(slot_dir.glob("*.yaml")):
        data = _load_yaml(path)
        if not data:
            continue
        atom_id = data.get("atom_id") or path.stem
        meta: dict[str, Any] = {}
        if slot_type == "STORY":
            band = data.get("band")
            if band is not None:
                # Teacher banks may carry "universal" as a legacy/non-numeric marker.
                # Compile-time band contract remains numeric; prefer emotional_intensity_band when present.
                try:
                    meta["band"] = int(band)
                except (TypeError, ValueError):
                    if str(band).strip().lower() == "universal":
                        meta["band_universal"] = True
                        eib = data.get("emotional_intensity_band")
                        if eib is not None:
                            try:
                                meta["band"] = int(eib)
                            except (TypeError, ValueError):
                                meta["band"] = 3
                        else:
                            meta["band"] = 3
                    else:
                        logger.warning(
                            "Invalid STORY band %r in %s; defaulting to 3",
                            band,
                            path,
                        )
                        meta["band"] = 3
            else:
                meta["band"] = 3
        fam = data.get("semantic_family")
        if fam is not None:
            meta["semantic_family"] = str(fam)
        # Propagate narrative metadata for teacher STORY atoms (role, depth, stage, cost)
        if slot_type == "STORY":
            for nk in ("mechanism_depth", "cost_type", "cost_intensity", "identity_stage"):
                if nk in data and data[nk] is not None:
                    meta[nk] = data[nk]
            # Infer role from mechanism_depth for V4 Book Template role-based selection
            depth = meta.get("mechanism_depth", 1)
            try:
                depth = int(depth)
            except (TypeError, ValueError):
                depth = 1
            _DEPTH_TO_ROLE = {1: "RECOGNITION", 2: "MECHANISM_PROOF", 3: "TURNING_POINT", 4: "EMBODIMENT"}
            meta["role"] = _DEPTH_TO_ROLE.get(depth, "RECOGNITION")

        src = data.get("source") or ""
        atom_source = "teacher_synthetic" if src and "synthetic" in str(src).lower() else "teacher_native"
        entries.append(AtomEntry(atom_id=atom_id, metadata=meta if meta else None, atom_source=atom_source))
    return entries


def _locale_atom_path(base_path: Path, locale: Optional[str]) -> Path:
    """Return locale-specific atom path if exists, else base English path."""
    if locale and locale != "en-US":
        locale_path = base_path.parent / "locales" / locale / base_path.name
        if locale_path.exists():
            return locale_path
    return base_path


class PoolIndex:
    """Index of approved atoms by (persona, topic, slot_type). Supports Teacher Mode via teacher_atoms_root."""

    def __init__(
        self,
        atoms_root: Optional[Path] = None,
        bindings_path: Optional[Path] = None,
        teacher_atoms_root: Optional[Path] = None,
        locale: Optional[str] = None,
    ):
        self.atoms_root = atoms_root or ATOMS_ROOT
        self.bindings_path = bindings_path or (CONFIG_ROOT / "topic_engine_bindings.yaml")
        self.teacher_atoms_root = teacher_atoms_root
        self.locale = locale
        self._bindings = _load_yaml(self.bindings_path)

    def get_pool(
        self,
        slot_type: str,
        persona_id: str,
        topic_id: str,
        format_plan: Optional[dict] = None,
        required_count: Optional[int] = None,
        teacher_exercise_fallback: bool = False,
        teacher_story_fallback: bool = False,
        **kwargs,
    ) -> list[AtomEntry]:
        """
        Return list of AtomEntry for (persona, topic, slot_type).
        When teacher_atoms_root is set, loads from teacher_banks/<teacher_id>/approved_atoms/<slot_type>/*.yaml first.
        EXERCISE fallback: when teacher_exercise_fallback and 0 < len(teacher_pool) < required_count, merge with practice library (teacher first); sort by (source_priority, stable_hash(atom_id)).
        Otherwise: STORY from engines; others from atoms/<persona>/<topic>/<slot_type>/CANONICAL.txt.
        """
        # HOOK and SCENE use persona atoms even in teacher mode — they carry
        # location template variables for grounding. Location is WHERE, not WHO.
        _TEACHER_SKIP_SLOTS = frozenset({"HOOK", "SCENE"})
        if self.teacher_atoms_root is not None and slot_type not in _TEACHER_SKIP_SLOTS:
            teacher_pool = _load_teacher_pool(self.teacher_atoms_root, slot_type)
            # ── Teacher fallback: merge teacher atoms with persona atoms when pool is short ──
            # EXERCISE fallback: merge with practice library (existing)
            # STORY fallback: merge with persona STORY pool (NEW — teacher wrapper applied at render)
            # All teaching slots can fall back to persona atoms when teacher pool is short/empty
            _FALLBACK_SLOTS = {"EXERCISE", "STORY", "REFLECTION", "INTEGRATION", "PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "COMPRESSION"}
            _teacher_story_fallback = teacher_story_fallback

            if slot_type in _FALLBACK_SLOTS and required_count is not None and 0 < len(teacher_pool) < required_count:
                # Determine which fallback pool to use
                if slot_type == "EXERCISE" and teacher_exercise_fallback:
                    from phoenix_v4.planning.practice_selector import get_backstop_pool
                    backstop = list(get_backstop_pool())
                elif slot_type == "STORY" and _teacher_story_fallback:
                    # Load persona STORY atoms as fallback — wrapped with teacher voice at render
                    backstop = list(_load_story_entries(self.atoms_root, persona_id, topic_id, self._bindings, locale=self.locale))
                    for entry in backstop:
                        if hasattr(entry, "metadata") and entry.metadata is not None:
                            entry.metadata["atom_source"] = "persona_fallback"
                elif _teacher_story_fallback and slot_type in _FALLBACK_SLOTS:
                    # For all other teaching slots: load persona atoms as silent fallback
                    if slot_type == "COMPRESSION":
                        backstop = list(_load_compression_pool(persona_id, topic_id))
                    else:
                        path = self.atoms_root / persona_id / topic_id / slot_type / "CANONICAL.txt"
                        backstop = list(_parse_block_file_canonical(path, persona_id, topic_id, slot_type))
                else:
                    backstop = []

                if backstop:
                    merged = list(teacher_pool) + backstop
                    _SOURCE_PRIORITY = {"teacher_native": 0, "teacher_synthetic": 1, "practice_fallback": 2, "persona_fallback": 2}

                    def _sort_key(e: AtomEntry) -> tuple:
                        src = getattr(e, "atom_source", None) or (e.metadata or {}).get("atom_source") or "teacher_native"
                        pri = _SOURCE_PRIORITY.get(src, 0)
                        h = hashlib.sha256(e.atom_id.encode("utf-8")).hexdigest()
                        return (pri, h)

                    merged.sort(key=_sort_key)
                    return merged

            if teacher_pool:
                return teacher_pool
            # Empty teacher pool: try persona fallback if enabled
            if _teacher_story_fallback and slot_type in _FALLBACK_SLOTS:
                if slot_type == "STORY":
                    return list(_load_story_entries(self.atoms_root, persona_id, topic_id, self._bindings, locale=self.locale))
                elif slot_type == "COMPRESSION":
                    return list(_load_compression_pool(persona_id, topic_id))
                elif slot_type == "EXERCISE":
                    from phoenix_v4.planning.practice_selector import get_backstop_pool
                    return list(get_backstop_pool())
                else:
                    path = self.atoms_root / persona_id / topic_id / slot_type / "CANONICAL.txt"
                    path = _locale_atom_path(path, self.locale)
                    return list(_parse_block_file_canonical(path, persona_id, topic_id, slot_type))
            return []
        if slot_type == "STORY":
            return _load_story_entries(
                self.atoms_root,
                persona_id,
                topic_id,
                self._bindings,
                locale=self.locale,
            )
        if slot_type == "COMPRESSION":
            return _load_compression_pool(persona_id, topic_id)
        # Non-STORY: single path atoms/<persona>/<topic>/<slot_type>/CANONICAL.txt (locale-aware)
        path = self.atoms_root / persona_id / topic_id / slot_type / "CANONICAL.txt"
        path = _locale_atom_path(path, self.locale)
        pool = _parse_block_file_canonical(path, persona_id, topic_id, slot_type)
        # EXERCISE backstop: when canonical missing/empty, fill from practice library
        if slot_type == "EXERCISE" and not pool:
            from phoenix_v4.planning.practice_selector import get_backstop_pool
            pool = get_backstop_pool()
        return pool

    def get_pool_sizes(
        self,
        persona_id: str,
        topic_id: str,
        slot_definitions: list[list[str]],
    ) -> dict[str, int]:
        """Return pool size per slot type that appears in slot_definitions."""
        slot_types = set()
        for row in slot_definitions:
            slot_types.update(row)
        sizes: dict[str, int] = {}
        for st in slot_types:
            pool = self.get_pool(st, persona_id, topic_id, None)
            sizes[st] = len(pool)
        return sizes
