"""
Stage 6 prose resolution: plan + atoms/config → atom_id → prose.
Uses same sources as Stage 3: atoms/ CANONICAL.txt, topic_engine_bindings,
compression_atoms/approved, teacher_banks/approved_atoms.
Normalized: placeholder/silence ids are not resolved; missing atoms yield empty or error per policy.
"""
from __future__ import annotations

import logging
import re

logger = logging.getLogger(__name__)
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"
CONFIG_ROOT = REPO_ROOT / "config"
TEACHER_BANKS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"
COMPRESSION_ATOMS_ROOT = REPO_ROOT / "SOURCE_OF_TRUTH" / "compression_atoms"


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _bindings_topic_key(topic_slug: str) -> str:
    if topic_slug == "grief_topic":
        return "grief"
    return topic_slug


@dataclass
class PlanContext:
    """Persona, topic, engines, teacher mode from plan (book_spec or top-level)."""
    persona_id: str
    topic_id: str
    engines: list[str]
    teacher_mode: bool = False
    teacher_id: str = ""

    @classmethod
    def from_plan(cls, plan: dict[str, Any], bindings_path: Optional[Path] = None) -> PlanContext:
        book_spec = plan.get("book_spec") or {}
        persona_id = (
            plan.get("persona_id")
            or book_spec.get("persona_id")
            or book_spec.get("persona")
            or ""
        ).strip()
        topic_id = (
            plan.get("topic_id")
            or book_spec.get("topic_id")
            or book_spec.get("topic")
            or ""
        ).strip()
        if not persona_id or not topic_id:
            # Fallback: infer from first STORY atom_id (e.g. nyc_executives_self_worth_comparison_RECOGNITION_v05)
            atom_ids = plan.get("atom_ids") or []
            story_id = next(
                (a for a in atom_ids if "placeholder" not in a and "silence:" not in a and "_" in a),
                None,
            )
            if story_id:
                # atom_id format: persona_topic_engine_ROLE_vNN (e.g. nyc_executives_self_worth_comparison_RECOGNITION_v05)
                # Infer topic by matching known bindings key, then persona = prefix before _topic_
                bp = bindings_path or (CONFIG_ROOT / "topic_engine_bindings.yaml")
                bindings = _load_yaml(bp) if bp else {}
                for tkey in (bindings.keys() if isinstance(bindings, dict) else []):
                    if tkey.startswith("---") or not isinstance(bindings.get(tkey), dict):
                        continue
                    sep = f"_{tkey}_"
                    if sep in story_id:
                        topic_id = topic_id or tkey
                        persona_id = persona_id or story_id.split(sep)[0]
                        break
            if not persona_id:
                persona_id = "nyc_executives"
            if not topic_id:
                topic_id = "self_worth"

        bindings_path = bindings_path or (CONFIG_ROOT / "topic_engine_bindings.yaml")
        bindings = _load_yaml(bindings_path)
        bkey = _bindings_topic_key(topic_id)
        engines = (bindings.get(bkey) or {}).get("allowed_engines") or []
        if not engines:
            engines = ["comparison", "shame", "false_alarm", "overwhelm", "spiral", "watcher", "grief"]

        teacher_mode = plan.get("teacher_mode") is True or book_spec.get("teacher_mode") is True
        teacher_id = (plan.get("teacher_id") or book_spec.get("teacher_id") or "").strip()

        return cls(
            persona_id=persona_id,
            topic_id=topic_id,
            engines=engines,
            teacher_mode=teacher_mode,
            teacher_id=teacher_id,
        )


def _is_placeholder_or_silence(atom_id: str) -> bool:
    return (
        atom_id.startswith("placeholder:") or atom_id.startswith("silence:")
    )


def _slot_type_from_placeholder_or_silence(atom_id: str) -> str:
    if atom_id.startswith("placeholder:"):
        parts = atom_id.split(":", 2)
        return parts[1] if len(parts) >= 2 else "UNKNOWN"
    if atom_id.startswith("silence:"):
        parts = atom_id.split(":", 2)
        return parts[1] if len(parts) >= 2 else "UNKNOWN"
    return "UNKNOWN"


@dataclass
class RenderResult:
    """Prose map plus any unresolved/missing for caller to handle."""
    prose_map: dict[str, str] = field(default_factory=dict)
    missing_ids: list[str] = field(default_factory=list)
    placeholder_or_silence_ids: list[tuple[str, str]] = field(default_factory=list)  # (atom_id, slot_type)


def _parse_canonical_with_prose(path: Path, persona: str, topic: str, engine: str) -> dict[str, str]:
    """Parse STORY engine CANONICAL.txt; atom_id contract matches assembly_compiler._parse_canonical_txt."""
    if not path.exists():
        return {}
    from phoenix_v4.planning.assembly_compiler import _resolve_story_role

    text = path.read_text(encoding="utf-8")
    # Per-block: ## RAW vNN --- metadata --- prose --- (same boundaries as Stage 3 parser)
    block = re.compile(
        r"^##\s+([A-Z_]+)\s+v(\d+)\s*\n---\s*\n([\s\S]*?)\n---\s*\n([\s\S]*?)(?=\n---|\Z)",
        re.MULTILINE,
    )
    out: dict[str, str] = {}
    for m in block.finditer(text):
        raw_role, ver, metadata, prose = m.group(1), m.group(2), m.group(3), m.group(4)
        role = _resolve_story_role(raw_role, ver, metadata)
        if role is None:
            continue
        if raw_role == role:
            atom_id = f"{persona}_{topic}_{engine}_{role}_v{ver}"
        else:
            raw_slug = re.sub(r"[^A-Za-z0-9]+", "_", raw_role).strip("_").upper() or "LEGACY"
            atom_id = f"{persona}_{topic}_{engine}_{role}_{raw_slug}_v{ver}"
        out[atom_id] = prose.strip()
    return out


def _parse_block_file_with_prose(path: Path, persona: str, topic: str, slot_type: str) -> dict[str, str]:
    """Parse non-STORY CANONICAL.txt. Format: ## TYPE vNN --- prose --- (or ## TYPE vNN --- metadata --- prose ---). Return atom_id -> prose."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8")
    parts = re.split(r"\n---\s*\n", text)
    out: dict[str, str] = {}
    for i, part in enumerate(parts):
        m = re.search(r"##\s+(\S+)\s+v(\d+)", part)
        if not m:
            continue
        _label, ver = m.group(1), m.group(2)
        atom_id = f"{persona}_{topic}_{slot_type}_v{ver}"
        for line in part.splitlines():
            if line.strip().lower().startswith("id:"):
                atom_id = line.split(":", 1)[1].strip()
                break
        # Prose: next part. (Non-STORY often has --- prose --- only; STORY has --- metadata --- prose --- so prose at i+2.)
        if i + 1 < len(parts):
            candidate = parts[i + 1].strip()
            if candidate.startswith("##"):
                continue  # no prose between this header and next

            # Detect metadata blocks broadly (not just STORY keys). Many non-STORY atoms
            # use keys like mode:, reframe_type:, weight:, carry_line: before prose.
            meta_lines = [ln.strip() for ln in candidate.splitlines() if ln.strip()]
            keylike_lines = [
                ln for ln in meta_lines
                if re.match(r"^[A-Za-z_][A-Za-z0-9_ ]{0,40}\s*:\s*.+$", ln)
            ]
            looks_like_metadata = (
                bool(meta_lines)
                and len(keylike_lines) >= 2
                and (len(keylike_lines) / len(meta_lines)) >= 0.6
            )

            if looks_like_metadata and i + 2 < len(parts):
                candidate = parts[i + 2].strip()
            out[atom_id] = candidate
    return out


def _load_compression_prose(persona: str, topic: str) -> dict[str, str]:
    """Load COMPRESSION atom_id -> body from approved YAMLs."""
    approved_dir = COMPRESSION_ATOMS_ROOT / "approved" / persona / topic
    if not approved_dir.exists():
        return {}
    out: dict[str, str] = {}
    for path in sorted(approved_dir.glob("*.yaml")):
        data = _load_yaml(path)
        if not data:
            continue
        atom_id = data.get("atom_id") or path.stem
        body = data.get("body")
        if body is not None:
            out[atom_id] = body.strip() if isinstance(body, str) else str(body).strip()
    return out


def _load_teacher_prose(teacher_atoms_root: Path, slot_type: str, locale: Optional[str] = None) -> dict[str, str]:
    """Load teacher atom_id -> body from YAMLs under teacher_atoms_root/<slot_type>/*.yaml.

    When locale is set, checks <slot_type>/locales/{locale}/*.yaml first,
    falling back to <slot_type>/*.yaml for atoms without locale versions.
    """
    slot_dir = teacher_atoms_root / slot_type
    if not slot_dir.exists():
        return {}
    out: dict[str, str] = {}

    # Try locale-specific YAMLs first
    if locale and locale != "en-US":
        locale_dir = slot_dir / "locales" / locale
        if locale_dir.exists():
            for path in sorted(locale_dir.glob("*.yaml")):
                data = _load_yaml(path)
                if not data:
                    continue
                atom_id = data.get("atom_id") or path.stem
                body = data.get("body")
                if body is not None:
                    out[atom_id] = body.strip() if isinstance(body, str) else str(body).strip()

    # Fill in any atoms not found in locale dir from base (English)
    for path in sorted(slot_dir.glob("*.yaml")):
        data = _load_yaml(path)
        if not data:
            continue
        atom_id = data.get("atom_id") or path.stem
        if atom_id not in out:  # Don't overwrite locale version
            body = data.get("body")
            if body is not None:
                out[atom_id] = body.strip() if isinstance(body, str) else str(body).strip()
    return out


def _locale_atom_path(base_path: Path, locale: Optional[str]) -> Path:
    """Return locale-specific atom path if it exists, else base English path.

    Convention: {slot_dir}/locales/{locale}/CANONICAL.txt takes priority over
    {slot_dir}/CANONICAL.txt when locale is set and not en-US.
    """
    if locale and locale != "en-US":
        locale_path = base_path.parent / "locales" / locale / base_path.name
        if locale_path.exists():
            return locale_path
    return base_path


def resolve_prose_for_plan(
    plan: dict[str, Any],
    atoms_root: Optional[Path] = None,
    bindings_path: Optional[Path] = None,
    teacher_banks_root: Optional[Path] = None,
    compression_atoms_root: Optional[Path] = None,
    locale: Optional[str] = None,
) -> RenderResult:
    """
    Resolve every real atom_id in plan to prose. Uses plan context (persona, topic, engines, teacher).
    Placeholder/silence ids are not in prose_map; missing real ids are listed in missing_ids.

    When locale is set (e.g. 'zh-TW'), prefers atoms from locales/{locale}/CANONICAL.txt,
    falling back to English CANONICAL.txt when locale version doesn't exist.
    """
    atoms_root = atoms_root or ATOMS_ROOT
    if locale is None:
        locale = plan.get("locale") or plan.get("book_spec", {}).get("locale")
    bindings_path = bindings_path or (CONFIG_ROOT / "topic_engine_bindings.yaml")
    teacher_banks_root = teacher_banks_root or TEACHER_BANKS_ROOT
    compression_atoms_root = compression_atoms_root or COMPRESSION_ATOMS_ROOT

    ctx = PlanContext.from_plan(plan, bindings_path)
    prose_map: dict[str, str] = {}
    missing: list[str] = []
    placeholder_silence: list[tuple[str, str]] = []

    if locale and locale != "en-US":
        logger.info("Prose resolver: locale=%s, using locale-specific atoms where available", locale)

    # STORY: from atoms/<persona>/<topic>/<engine>/CANONICAL.txt (or locales/{locale}/ variant)
    for engine in ctx.engines:
        path = atoms_root / ctx.persona_id / ctx.topic_id / engine / "CANONICAL.txt"
        path = _locale_atom_path(path, locale)
        prose_map.update(_parse_canonical_with_prose(path, ctx.persona_id, ctx.topic_id, engine))

    # Teacher Mode: override teaching/narrative slots with teacher_banks prose.
    # HOOK and SCENE stay from the persona atom pool — they carry location
    # template variables ({street_name}, {transit_line}, etc.) that the
    # renderer needs for location grounding. Location is WHERE the reader is,
    # not WHO is teaching.
    if ctx.teacher_mode and ctx.teacher_id and teacher_banks_root.exists():
        teacher_root = teacher_banks_root / ctx.teacher_id / "approved_atoms"
        if teacher_root.exists():
            for slot_type in ("STORY", "REFLECTION", "EXERCISE", "INTEGRATION",
                              "PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "COMPRESSION", "TEACHING"):
                prose_map.update(_load_teacher_prose(teacher_root, slot_type, locale=locale))

    # Non-STORY canonical (REFLECTION, EXERCISE, HOOK, SCENE, etc.) — locale-aware
    for slot_type in ("REFLECTION", "EXERCISE", "HOOK", "SCENE", "INTEGRATION", "PIVOT", "TAKEAWAY", "THREAD", "PERMISSION"):
        path = atoms_root / ctx.persona_id / ctx.topic_id / slot_type / "CANONICAL.txt"
        path = _locale_atom_path(path, locale)
        prose_map.update(_parse_block_file_with_prose(path, ctx.persona_id, ctx.topic_id, slot_type))

    # COMPRESSION from SOURCE_OF_TRUTH/compression_atoms/approved/<persona>/<topic>/*.yaml
    comp_dir = compression_atoms_root / "approved" / ctx.persona_id / ctx.topic_id
    if comp_dir.exists():
        for path in sorted(comp_dir.glob("*.yaml")):
            data = _load_yaml(path)
            if not data:
                continue
            atom_id = data.get("atom_id") or path.stem
            body = data.get("body")
            if body is not None:
                prose_map[atom_id] = body.strip() if isinstance(body, str) else str(body).strip()

    # Practice library: resolve practice_id (lib34_*, ab37_*) to text from store
    try:
        from phoenix_v4.planning.practice_selector import get_practice_prose_map
        practice_prose = get_practice_prose_map()
        if practice_prose:
            prose_map.update(practice_prose)
    except Exception:
        pass

    # TAKEAWAY slots: resolve arc_thesis:chN from plan.chapter_thesis (1-based key = N+1)
    chapter_thesis = plan.get("chapter_thesis")
    if isinstance(chapter_thesis, dict) and chapter_thesis:
        for aid in plan.get("atom_ids") or []:
            if aid.startswith("arc_thesis:ch"):
                try:
                    ch_str = aid.split(":", 2)[-1]
                    ch_0based = int(ch_str)
                    thesis = chapter_thesis.get(ch_0based + 1)
                    if thesis:
                        prose_map[aid] = thesis
                except (ValueError, IndexError):
                    pass

    atom_ids = plan.get("atom_ids") or []
    for aid in atom_ids:
        if _is_placeholder_or_silence(aid):
            placeholder_silence.append((aid, _slot_type_from_placeholder_or_silence(aid)))
            continue
        if aid not in prose_map:
            missing.append(aid)

    return RenderResult(
        prose_map=prose_map,
        missing_ids=missing,
        placeholder_or_silence_ids=placeholder_silence,
    )
