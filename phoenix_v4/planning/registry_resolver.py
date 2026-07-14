"""
Section Registry Resolver — the canonical content pipeline for Pearl Prime.

Loads pre-authored section registries (registry/{topic}.yaml) and
resolves a complete book by selecting one variant per section per chapter
using deterministic hashing.

Two enrichment modes:
  Teacher mode: teacher atoms overlay HOOK, EXERCISE, INTEGRATION, PIVOT,
    PERMISSION, TAKEAWAY, THREAD, TEACHER_DOCTRINE. SCENEs stay from registry.
  Regular mode: persona atoms overlay HOOK, STORY from
    atoms/{persona}/{topic}/. SCENEs stay from registry (Qwen-by-purpose;
    robotic persona SCENE banks are code-path dead). REFLECTIONs and
    INTEGRATIONs stay from registry.

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
COMPOSITE_DOCTRINE_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "composite_doctrine"
ATOMS_ROOT = REPO_ROOT / "atoms"

# Section types that get overlaid in teacher mode (everything except SCENE and REFLECTION)
_TEACHER_OVERLAY_TYPES = frozenset({
    "TEACHER_DOCTRINE", "COMPRESSION", "COMPOSITE_TEACHER_DOCTRINE", "HOOK", "EXERCISE",
    "INTEGRATION", "PIVOT", "PERMISSION", "TAKEAWAY", "THREAD",
})
# Section types that get overlaid in regular/persona mode.
# SCENE is intentionally excluded: registry variants are purpose-driven (Qwen via
# scene_*_purpose). Persona SCENE banks (atoms/*/SCENE/CANONICAL.txt) are not used.
_PERSONA_OVERLAY_TYPES = frozenset({"HOOK", "STORY"})
# Mapping from registry section type to teacher atom directory name.
#
# TEACHER_DOCTRINE lookup chain (first non-empty pool wins, per
# TEACHER-POOL-SEMANTICS-01):
#   1. TEACHER_DOCTRINE/ — operator-canonical location for explicit doctrine
#      atoms (e.g. Pearl_Writer #4's OPD-109 Phase 2 expansion in PR #1230
#      added 10 ahjan TEACHER_DOCTRINE atoms here).
#   2. COMPRESSION/ — legacy location for compact doctrine-shaped atoms.
#   3. REFLECTION/ — secondary fallback (some teachers store doctrine here).
#   4. TEACHING/ — on-disk teacher-bank slot name some teachers used before
#      the TEACHER_DOCTRINE alias existed; preserved for backward compat.
# Per F2 in atom_usage_audit_2026-05-06.md, and PR fixing the resolver bug
# that omitted TEACHER_DOCTRINE/ from the lookup chain entirely (Pearl_Writer
# #4 had to dual-locate atoms in TEACHER_DOCTRINE/ + COMPRESSION/ as a hack).
_TEACHER_TYPE_MAP = {
    "TEACHER_DOCTRINE": ["TEACHER_DOCTRINE", "COMPRESSION", "REFLECTION", "TEACHING"],
    "COMPRESSION": ["TEACHER_DOCTRINE", "COMPRESSION", "REFLECTION", "TEACHING"],
    "COMPOSITE_TEACHER_DOCTRINE": [
        "TEACHER_DOCTRINE", "COMPRESSION", "REFLECTION", "TEACHING",
    ],
    "HOOK": ["HOOK"],
    "EXERCISE": ["EXERCISE"],
    "INTEGRATION": ["INTEGRATION"],
    "PIVOT": ["PIVOT"],
    "PERMISSION": ["PERMISSION"],
    "TAKEAWAY": ["TAKEAWAY"],
    "THREAD": ["THREAD"],
}

# Regular-mode composite pools (SOURCE_OF_TRUTH/composite_doctrine/<topic_id>/).
_COMPOSITE_TYPE_MAP = {
    "TEACHER_DOCTRINE": ["COMPOSITE_TEACHER_DOCTRINE"],
    "COMPRESSION": ["COMPOSITE_TEACHER_DOCTRINE"],
    "COMPOSITE_TEACHER_DOCTRINE": ["COMPOSITE_TEACHER_DOCTRINE"],
    "REFLECTION": ["COMPOSITE_TEACHER_REFLECTION"],
    "COMPOSITE_TEACHER_REFLECTION": ["COMPOSITE_TEACHER_REFLECTION"],
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



class DuplicateSelectedAtomError(ValueError):
    # A non-reusable authored atom/body would repeat within one book.
    pass


def _normalized_body_hash(content: str) -> str:
    normalized = " ".join(str(content or "").split()).casefold()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _deterministic_index(seed: str, pool_size: int) -> int:
    # SHA256-based deterministic selection.
    if pool_size <= 0:
        return 0
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") % pool_size


def _select_unique_story_overlay(
    atom_pool: list[dict],
    *,
    seed_key: str,
    used_ids: set[str],
    used_body_hashes: set[str],
) -> dict:
    candidates = [
        atom
        for atom in atom_pool
        if str(atom.get("atom_id") or "") not in used_ids
        and _normalized_body_hash(str(atom.get("content") or ""))
        not in used_body_hashes
    ]
    if not candidates:
        raise DuplicateSelectedAtomError(
            "STORY overlay pool exhausted before book completion: no unused "
            "atom ID/body remains. Author more STORY supply; do not repeat."
        )
    candidates = sorted(
        candidates,
        key=lambda atom: (
            str(atom.get("atom_id") or ""),
            _normalized_body_hash(str(atom.get("content") or "")),
        ),
    )
    chosen = candidates[_deterministic_index(seed_key, len(candidates))]
    used_ids.add(str(chosen.get("atom_id") or ""))
    used_body_hashes.add(
        _normalized_body_hash(str(chosen.get("content") or ""))
    )
    return chosen

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

# DEFECT 7 (composer-guard lane, fail-closed backstop): 546/3,521 primary
# CANONICAL.txt banks ship malformed block headers — every even-numbered block
# loses its "## " prefix and is absorbed into the prior atom body, leaking raw
# atom-id labels ("INTEGRATION v06", "RECOGNITION v04") verbatim into reader
# prose. The content-repair lane prepends "## " to those lines; this guard makes
# the parser ALSO recognize a *bare* block header — a standalone "<TOKEN> vNN"
# line whose next non-empty line is "---" — so even an un-repaired atom still
# parses into the correct SEPARATE blocks instead of one merged body.
#
# Token set is the EXACT enumerated list from the fix-spec's header-repair regex
# (COMPOSER_FRONTIER_FIX_SPEC_20260614.md DEFECT 7) so the guard recognizes the
# same headers the repair script would write.
import re as _re

_BARE_BLOCK_HEADER_TOKENS = frozenset({
    "HOOK", "SCENE", "STORY", "REFLECTION", "PIVOT", "EXERCISE", "INTEGRATION",
    "THREAD", "TAKEAWAY", "PERMISSION", "COMPRESSION", "RECOGNITION",
    "MECHANISM_PROOF", "TURNING_POINT", "EMBODIMENT", "COST_REVEAL", "RECKONING",
})
# A standalone bare header: <UPPER_TOKEN> v<digits>, nothing else on the line.
_BARE_BLOCK_HEADER_RE = _re.compile(r"^([A-Z][A-Z_]*)\s+v\d+$")


def _is_bare_block_header(stripped: str, next_nonempty: str) -> bool:
    """True if ``stripped`` is a bare (no-"## ") block header for a known token.

    The next non-empty line must be the ``---`` metadata/body delimiter — this is
    the same structural signature the content-repair lane keys on, and it prevents
    a grammatical mid-atom phrase (which is never followed by a lone ``---``) from
    being mistaken for a header.
    """
    if next_nonempty.strip() != "---":
        return False
    m = _BARE_BLOCK_HEADER_RE.match(stripped)
    if not m:
        return False
    return m.group(1) in _BARE_BLOCK_HEADER_TOKENS


class CanonicalParseError(ValueError):
    """Header-present CANONICAL.txt block produced no usable prose atom."""


# Lines that look like atom metadata (`key: value`), not prose paragraphs.
_META_LINE_RE = _re.compile(r"^[\w.-]+\s*:\s*.*$")


def _looks_like_metadata_only(lines: list[str]) -> bool:
    """True when every non-empty line is a short YAML-ish ``key: value`` row."""
    nonempty = [ln.strip() for ln in lines if ln.strip()]
    if not nonempty:
        return True
    return all(
        _META_LINE_RE.match(ln) or ln.startswith("#")
        for ln in nonempty
    )


def _parse_canonical_txt(
    path: Path,
    *,
    slot_type: Optional[str] = None,
    text: Optional[str] = None,
) -> list[dict]:
    """Parse atoms/persona/topic/TYPE/CANONICAL.txt into list of atom dicts.

    Supported delimiter shapes (explicit):

    **Two-delimiter (canonical):**
        ## TYPE vNN
        ---
        optional metadata
        ---
        prose body
        ---

    **Single-delimiter / single-section legacy:**
        ## TYPE vNN
        ---
        prose body
        ---          # optional closing delimiter

    In the legacy shape, text after the first ``---`` is prose (not metadata).
    A header is never evidence of usable depth: header-present blocks with no
    prose raise ``CanonicalParseError`` instead of being silently dropped
    (educators×imposter_syndrome REFLECTION failure mode / #5530).

    Also tolerant of MALFORMED banks where the "## " prefix is missing from a
    block header (DEFECT 7 data corruption): a standalone ``TYPE vNN`` line whose
    next non-empty line is ``---`` is recognized as a bare block header and starts
    a new block, so the un-repaired atom-id label never gets absorbed into the
    prior block's body and leaked into reader prose.
    """
    from phoenix_v4.planning.scene_atom_header_parser import attach_scene_metadata

    if text is None:
        if not path.exists():
            return []
        text = path.read_text(encoding="utf-8")
    raw_lines = text.splitlines()
    blocks: list[dict] = []
    current_id = ""
    current_header = ""
    in_body = False
    body_lines: list[str] = []
    meta_lines: list[str] = []
    pre_delimiter_lines: list[str] = []
    delimiter_count = 0
    header_count = 0
    malformed: list[str] = []
    st_upper = (slot_type or "").strip().upper()

    def _flush_block(*, next_header: bool = False) -> None:
        nonlocal current_id, body_lines, meta_lines, pre_delimiter_lines, delimiter_count
        if not current_id:
            return

        body_text = "\n".join(body_lines).strip()
        meta_text = "\n".join(meta_lines).strip()
        pre_text = "\n".join(pre_delimiter_lines).strip()
        content = ""
        meta: dict = {}
        shape = ""

        metadata_prefix: list[str] = []
        pre_prose_lines: list[str] = []
        if pre_delimiter_lines:
            saw_prose = False
            for raw in pre_delimiter_lines:
                stripped = raw.strip()
                if not stripped:
                    if saw_prose:
                        pre_prose_lines.append(raw)
                    continue
                if not saw_prose and _META_LINE_RE.match(stripped):
                    metadata_prefix.append(raw)
                    continue
                saw_prose = True
                pre_prose_lines.append(raw)

        if delimiter_count >= 2 and body_text:
            # Canonical two-delimiter: metadata then prose.
            shape = "two-delimiter"
            content = body_text
            if meta_lines and yaml is not None:
                try:
                    parsed = yaml.safe_load("\n".join(meta_lines))
                    if isinstance(parsed, dict):
                        meta = parsed
                except Exception:
                    meta = {}
        elif delimiter_count >= 1 and pre_prose_lines:
            # Legacy authored shape: metadata/prose appear directly after the
            # header, followed only by closing delimiters.
            shape = "pre-delimiter-legacy"
            content = "\n".join(pre_prose_lines).strip()
            if metadata_prefix and yaml is not None:
                try:
                    parsed = yaml.safe_load("\n".join(metadata_prefix))
                    if isinstance(parsed, dict):
                        meta = parsed
                except Exception:
                    meta = {}
        elif delimiter_count == 1 and meta_text:
            # Explicit single-delimiter legacy: sole section after --- is prose.
            shape = "single-delimiter"
            content = meta_text
        elif delimiter_count >= 1 and not body_text and not meta_text:
            # Some legacy banks interleave real atoms with empty placeholder
            # headers (`## TYPE vNN` + `---`) for unused even-numbered slots.
            # Skip those placeholders locally, but still fail loud at EOF if
            # the file resolves to zero usable atoms overall.
            return
        elif delimiter_count >= 2 and not body_text and meta_text:
            if _looks_like_metadata_only(meta_lines):
                if next_header:
                    # Another legacy placeholder shape stores only metadata for
                    # an unused slot, then immediately starts the next header.
                    # Skip those interleaved placeholders, but still fail loud
                    # if the file ends on metadata-without-prose.
                    return
                malformed.append(
                    f"{current_id!r}: two-delimiter block has metadata but empty "
                    "prose (header count is not usable depth)"
                )
                return
            # Legacy single-section written as `--- / prose / ---` (prose sat in
            # the first segment; second delimiter opened an empty body).
            shape = "single-section-legacy"
            content = meta_text
        elif delimiter_count == 0 and (body_text or meta_text):
            shape = "no-delimiter"
            content = (body_text or meta_text)
        else:
            malformed.append(
                f"{current_id!r}: header present but no usable prose "
                f"(delimiters={delimiter_count}, shape unresolved)"
            )
            return

        if not content:
            malformed.append(
                f"{current_id!r}: header present but empty prose after {shape or 'parse'}"
            )
            return

        atom = {
            "atom_id": current_id,
            "content": content,
            "metadata": meta,
            "delimiter_shape": shape,
        }
        if st_upper == "SCENE" or current_id.upper().startswith("SCENE "):
            atom = attach_scene_metadata(atom, f"## {current_id}")
        blocks.append(atom)

    def _next_nonempty(start_idx: int) -> str:
        for j in range(start_idx + 1, len(raw_lines)):
            if raw_lines[j].strip():
                return raw_lines[j]
        return ""

    for i, line in enumerate(raw_lines):
        stripped = line.strip()
        if stripped.startswith("## "):
            _flush_block(next_header=True)
            current_header = stripped
            current_id = stripped.replace("## ", "").strip()
            header_count += 1
            body_lines = []
            meta_lines = []
            pre_delimiter_lines = []
            in_body = False
            delimiter_count = 0
        elif _is_bare_block_header(stripped, _next_nonempty(i)):
            # Malformed bank: header line lost its "## " prefix. Treat exactly
            # like a "## " header so the raw atom-id label cannot be absorbed
            # into the prior block body.
            _flush_block(next_header=True)
            current_header = stripped
            current_id = stripped
            header_count += 1
            body_lines = []
            meta_lines = []
            pre_delimiter_lines = []
            in_body = False
            delimiter_count = 0
        elif stripped == "---":
            delimiter_count += 1
            if delimiter_count >= 2:
                in_body = True
        elif delimiter_count == 0 and current_id:
            pre_delimiter_lines.append(line)
        elif delimiter_count == 1 and not in_body:
            meta_lines.append(line)
        elif in_body:
            body_lines.append(line)

    _flush_block()
    if malformed:
        raise CanonicalParseError(
            f"Malformed CANONICAL.txt at {path}: "
            + "; ".join(malformed)
            + ". Use HEADER + --- + prose (single-delimiter legacy) or "
            "HEADER + --- + metadata + --- + prose (two-delimiter)."
        )
    if header_count and not blocks:
        raise CanonicalParseError(
            f"Malformed CANONICAL.txt at {path}: found {header_count} header(s) "
            "but parsed zero usable atoms (header count ≠ usable depth)."
        )
    return blocks


def _load_composite_doctrine_atoms(
    topic_id: str,
    repo_root: Optional[Path] = None,
    locale: Optional[str] = None,
) -> dict[str, list[dict]]:
    """Load topic-scoped composite teacher doctrine/reflection from CANONICAL.txt.

    Locale-aware: when ``locale`` is set and not 'en-US', reads the localized
    ``{dir}/locales/{locale}/CANONICAL.txt`` when present, otherwise falls back
    to the base English ``CANONICAL.txt`` (mirrors persona-atom locale threading
    via ``_locale_canonical_path``). en-US behaviour is unchanged.
    """
    topic = (topic_id or "").strip()
    if not topic:
        return {}
    root = (repo_root or REPO_ROOT) / "SOURCE_OF_TRUTH" / "composite_doctrine" / topic
    atoms: dict[str, list[dict]] = {}
    doctrine_blocks = _parse_canonical_txt(_locale_canonical_path(root, locale))
    if doctrine_blocks:
        atoms["COMPOSITE_TEACHER_DOCTRINE"] = doctrine_blocks
    reflection_blocks = _parse_canonical_txt(
        _locale_canonical_path(root / "REFLECTION", locale)
    )
    if reflection_blocks:
        atoms["COMPOSITE_TEACHER_REFLECTION"] = reflection_blocks
    if atoms:
        logger.info(
            "Loaded composite doctrine types %s for topic '%s'",
            list(atoms.keys()),
            topic,
        )
    return atoms


def _pick_composite_pool(
    composite_atoms: dict[str, list[dict]],
    slot_type: str,
) -> list[dict]:
    """First non-empty composite pool for a beatmap/registry slot type."""
    st = slot_type.strip().upper()
    for key in _COMPOSITE_TYPE_MAP.get(st, [st]):
        pool = composite_atoms.get(key, [])
        if pool:
            return pool
    return []


_KNOWN_SLOT_DIRS = frozenset({
    "HOOK", "SCENE", "STORY", "REFLECTION", "EXERCISE", "INTEGRATION",
    "TEACHER_DOCTRINE", "COMPRESSION", "PERMISSION", "PIVOT",
    "TAKEAWAY", "THREAD", "TRANSITION", "DWELL",
    "ANGLE_DEFINITION", "ANGLE_CALLBACK",
})


def _locale_canonical_path(slot_dir: Path, locale: Optional[str]) -> Path:
    """Return locale-specific CANONICAL.txt path if it exists, else base English path.

    Convention (mirrors phoenix_v4/rendering/prose_resolver._locale_atom_path):
        {slot_dir}/locales/{locale}/CANONICAL.txt  →  preferred when locale != en-US
        {slot_dir}/CANONICAL.txt                   →  fallback (English)
    """
    base = slot_dir / "CANONICAL.txt"
    if locale and locale != "en-US":
        locale_path = slot_dir / "locales" / locale / "CANONICAL.txt"
        if locale_path.exists():
            return locale_path
    return base


def _load_persona_atoms(
    persona_id: str,
    topic_id: str,
    locale: Optional[str] = None,
    engine: Optional[str] = None,
) -> dict[str, list[dict]]:
    """Load persona-specific atoms from atoms/{persona}/{topic}/{type}/CANONICAL.txt.

    Returns dict keyed by slot type (HOOK, SCENE, STORY, etc.) -> list of atom dicts.

    Engine-bank atoms (atoms/{persona}/{topic}/{engine}/CANONICAL.txt with named-character
    content) are PREPENDED to atoms["STORY"] before generic atoms/{persona}/{topic}/STORY/
    CANONICAL.txt content.

    F-COHERENCE (DEVOTION_PATH_TOPIC_ENGINE_RECONCILIATION_V1_SPEC §6): when ``engine`` is
    supplied (the plan's bound engine, e.g. ``overwhelm`` vs ``grief``), the STORY pool is
    routed to **that engine only** — i.e. keyed on (topic, engine), not topic alone. Without
    this, every engine dir was merged into one bucket, so two engine-LEGAL plans with the
    same persona+topic (e.g. burnout__overwhelm vs burnout__grief) drew the identical merged
    pool and, under the same seed, rendered byte-identical prose (the re-point #1682 was
    legal-but-cosmetic). Routing by engine also stops a single book from mixing named-character
    stories drawn from a forbidden sibling engine.

    Backward-compatible: when ``engine`` is None/empty, OR the requested engine has no dir on
    disk for this (persona, topic), the previous all-engines-merged behavior is preserved so
    STORY never silently empties. Each engine atom is tagged with its ``engine`` for trace.
    Selection in enrichment_select._try_persona_content uses a seeded-pseudorandom index over
    the resulting pool. Closes the engine-bank-to-grid wiring chain started by PR #669 (which
    changed SOMATIC_10_SLOT_GRID sec 2/5/9 to STORY).

    Engine dirs are detected by exclusion against _KNOWN_SLOT_DIRS — this fixes the prior
    bug where midlife_women's UPPERCASE engine names (COMPARISON, GRIEF, OVERWHELM, SHAME)
    were treated as separate slot-type keys instead of STORY content.

    When ``locale`` is set and not 'en-US', each slot/engine directory is first probed for
    ``locales/{locale}/CANONICAL.txt`` and falls back to the base English ``CANONICAL.txt``
    when the locale variant is missing. This makes the spine pipeline locale-aware in the
    same way prose_resolver.py is for the registry/teacher path.
    """
    persona_root = ATOMS_ROOT / persona_id / topic_id
    if not persona_root.exists():
        return {}

    atoms: dict[str, list[dict]] = {}
    # Engine-bank STORY atoms collected per engine name (lowercased) so we can route by
    # the plan's bound engine (F-COHERENCE) instead of merging every engine together.
    engine_atoms_by_name: dict[str, list[dict]] = {}

    for sub in persona_root.iterdir():
        if not sub.is_dir():
            continue
        # Skip the locales/ sibling directory itself when iterating engine/slot dirs.
        if sub.name == "locales":
            continue
        canonical = _locale_canonical_path(sub, locale)
        if not canonical.exists():
            continue
        slot_type_upper = sub.name.upper()
        parsed = _parse_canonical_txt(canonical, slot_type=slot_type_upper)
        if not parsed:
            continue
        if slot_type_upper in _KNOWN_SLOT_DIRS:
            atoms[slot_type_upper] = parsed
        else:
            # Engine dir (e.g. overwhelm, grief, shame, OVERWHELM, EMBODIMENT_V01_*) —
            # bucket per engine so the plan engine can route STORY by (topic, engine).
            engine_name = sub.name.lower()
            for _a in parsed:
                # Tag with engine for downstream trace / selection (idempotent).
                if isinstance(_a, dict):
                    _a.setdefault("engine", engine_name)
            engine_atoms_by_name.setdefault(engine_name, []).extend(parsed)

    # Route the engine-bank STORY pool to the requested engine when present (F-COHERENCE).
    # Fall back to all-engines-merged when no engine is requested or the engine dir is
    # absent, so STORY never empties (backward-compatible).
    requested_engine = (engine or "").strip().lower()
    if requested_engine and engine_atoms_by_name.get(requested_engine):
        engine_story_atoms = list(engine_atoms_by_name[requested_engine])
        engine_route = requested_engine
    else:
        engine_story_atoms = [a for pool in engine_atoms_by_name.values() for a in pool]
        engine_route = "ALL" if not requested_engine else f"{requested_engine}->ALL(missing)"

    if engine_story_atoms:
        atoms["STORY"] = engine_story_atoms + atoms.get("STORY", [])

    if atoms:
        logger.info(
            "Loaded %d persona atom types for '%s/%s' locale=%s engine=%s "
            "(engine-bank STORY atoms: %d; available engines: %s)",
            len(atoms), persona_id, topic_id, locale or "en-US", engine_route,
            len(engine_story_atoms), ",".join(sorted(engine_atoms_by_name)) or "none",
        )
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
    # Complete resolved book from section registry.
    __slots__ = (
        "chapters",
        "topic",
        "seed",
        "registry_path",
        "teacher_id",
        "selection_audit",
    )

    def __init__(
        self,
        chapters: list[ResolvedChapter],
        topic: str,
        seed: str,
        registry_path: str = "",
        teacher_id: str = "",
        selection_audit: Optional[dict[str, Any]] = None,
    ):
        self.chapters = chapters
        self.topic = topic
        self.seed = seed
        self.registry_path = registry_path
        self.teacher_id = teacher_id
        self.selection_audit = selection_audit or {}

    @property
    def word_count(self) -> int:
        return sum(ch.word_count for ch in self.chapters)

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)

    def to_prose(self) -> str:
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
    locale: Optional[str] = None,
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
        locale: Optional locale (e.g. 'ja-JP'). When set and not 'en-US',
            persona atoms are read from
            atoms/{persona}/{topic}/{slot}/locales/{locale}/CANONICAL.txt
            with a fallback to the base English CANONICAL.txt.

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
    persona_atoms = (
        _load_persona_atoms(persona_id, reg_topic, locale=locale)
        if persona_id and reg_topic
        else {}
    )

    chapters: list[ResolvedChapter] = []
    used_story_atom_ids: set[str] = set()
    used_story_body_hashes: set[str] = set()
    story_selection_rows: list[dict[str, Any]] = []

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
            #
            # First-match semantics per TEACHER-POOL-SEMANTICS-01 cap entry:
            # The loop below picks the FIRST non-empty pool from the type-alias
            # list and breaks. This is intentional and load-bearing — it makes
            # render output deterministic given (seed, ch_key, sec_key) and
            # preserves render-cache stability. Switching to union-pool semantics
            # would change seed→atom mapping and require a regeneration pass on
            # any cached/shipped books.
            #
            # For TEACHER_DOCTRINE the chain is now:
            #   TEACHER_DOCTRINE → COMPRESSION → REFLECTION → TEACHING
            # so teachers with an explicit TEACHER_DOCTRINE/ directory win
            # over the legacy COMPRESSION/REFLECTION/TEACHING fallback.
            # Teachers without TEACHER_DOCTRINE/ on disk still resolve via the
            # legacy chain — backward-compatible.
            # Content gaps that surface in this code path (e.g., teachers
            # whose doctrine lives only under TEACHING/) are routed to
            # Pearl_Editor + Pearl_Writer content migration ws's (e.g.,
            # ws_ahjan_teaching_atoms_migration_20260506), not to a code-side
            # semantics flip.
            if teacher_atoms and sec_type in _TEACHER_OVERLAY_TYPES:
                atom_pool: list[dict] = []
                for dir_name in _TEACHER_TYPE_MAP.get(sec_type, [sec_type]):
                    atom_pool = teacher_atoms.get(dir_name, [])
                    if atom_pool:
                        break
                if atom_pool:
                    t_idx = _deterministic_index(
                        f"{seed}:{ch_key}:{sec_key}:{purpose}:teacher",
                        len(atom_pool),
                    )
                    overlay_content = atom_pool[t_idx]["content"]
                    overlay_id = atom_pool[t_idx]["atom_id"]

            # Persona overlay: hooks, scenes, stories (even in teacher mode)
            if not overlay_content and persona_atoms and sec_type in _PERSONA_OVERLAY_TYPES:
                atom_pool = persona_atoms.get(sec_type, [])
                if atom_pool:
                    selector_key = (
                        f"{seed}:{ch_key}:{sec_key}:{purpose}:persona"
                    )
                    if sec_type == "STORY":
                        selected_atom = _select_unique_story_overlay(
                            atom_pool,
                            seed_key=selector_key,
                            used_ids=used_story_atom_ids,
                            used_body_hashes=used_story_body_hashes,
                        )
                        overlay_content = selected_atom["content"]
                        overlay_id = selected_atom["atom_id"]
                        story_selection_rows.append(
                            {
                                "chapter_key": ch_key,
                                "section_key": sec_key,
                                "section_id": sec_id,
                                "atom_id": overlay_id,
                                "body_sha256": _normalized_body_hash(
                                    overlay_content
                                ),
                            }
                        )
                    else:
                        p_idx = _deterministic_index(
                            selector_key,
                            len(atom_pool),
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

            # ── DEFAULT: use registry variant (purpose-seeded — restore #4) ──
            v_idx = _deterministic_index(
                f"{seed}:{ch_key}:{sec_key}:{purpose}", len(variants)
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

    body_counts: dict[str, int] = {}
    id_counts: dict[str, int] = {}
    for row in story_selection_rows:
        body_hash = row["body_sha256"]
        atom_id = row["atom_id"]
        body_counts[body_hash] = body_counts.get(body_hash, 0) + 1
        id_counts[atom_id] = id_counts.get(atom_id, 0) + 1
    duplicate_ids = sorted(
        atom_id for atom_id, count in id_counts.items() if count > 1
    )
    duplicate_body_hashes = sorted(
        body_hash for body_hash, count in body_counts.items() if count > 1
    )
    if duplicate_ids or duplicate_body_hashes:
        raise DuplicateSelectedAtomError(
            "duplicate STORY selection escaped unique selector: "
            f"ids={duplicate_ids} body_hashes={duplicate_body_hashes}"
        )
    selection_audit = {
        "story_selection_count": len(story_selection_rows),
        "selected_story_atom_ids": [
            row["atom_id"] for row in story_selection_rows
        ],
        "duplicate_story_atom_ids": duplicate_ids,
        "duplicate_story_body_hashes": duplicate_body_hashes,
        "rows": story_selection_rows,
        "status": "PASS",
    }

    book = ResolvedBook(
        chapters=chapters,
        topic=topic,
        seed=seed,
        registry_path=str(reg_path),
        teacher_id=teacher_id or "",
        selection_audit=selection_audit,
    )

    logger.info(
        "Resolved book: %d chapters, %d words, seed='%s', teacher='%s'",
        book.chapter_count, book.word_count, seed, teacher_id or "none",
    )
    return book
