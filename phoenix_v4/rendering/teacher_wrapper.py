"""
Teacher wrapper voice framing for section packet composition.

Loads `config/catalog_planning/teacher_wrapper_templates.yaml` and resolves a
(prefix, suffix) framing pair for teacher_atom content based on teacher metadata,
section type, and a deterministic seed.

Contract:
  - Returns ("", "") if no wrapper can be fully resolved (safety: NEVER emits
    unresolved {SLOT} tokens into prose).
  - `named` mode is preferred when the teacher has a display/formal name.
  - Variant selection is deterministic given the seed.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_TEMPLATES_PATH = REPO_ROOT / "config" / "catalog_planning" / "teacher_wrapper_templates.yaml"
_REGISTRY_PATH = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"

_templates_cache: Optional[Dict[str, Any]] = None
_registry_cache: Optional[Dict[str, Any]] = None

_SLOT_RE = re.compile(r"\{([A-Z_][A-Z0-9_]*)\}")


def _load_yaml(p: Path) -> Dict[str, Any]:
    if not p.exists():
        return {}
    try:
        import yaml
        with open(p, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def _load_templates() -> Dict[str, Any]:
    global _templates_cache
    if _templates_cache is None:
        _templates_cache = _load_yaml(_TEMPLATES_PATH)
    return _templates_cache or {}


def _load_registry() -> Dict[str, Any]:
    global _registry_cache
    if _registry_cache is None:
        _registry_cache = _load_yaml(_REGISTRY_PATH)
    return _registry_cache or {}


def _reset_caches_for_tests() -> None:
    """Clear cached YAML — tests that monkeypatch template paths call this."""
    global _templates_cache, _registry_cache
    _templates_cache = None
    _registry_cache = None


def _section_wrapper_key(section_type: str) -> str:
    """Map section_type → which wrapper block to use."""
    st = str(section_type or "").strip().upper()
    if st == "EXERCISE":
        return "exercise_wrapper"
    if st in ("CONCLUSION", "OUTRO", "CLOSE", "CLOSER"):
        return "conclusion_wrapper"
    return "intro_wrapper"


def _teacher_slot_values(
    teacher_id: str,
    spine_context: Optional[Dict[str, Any]],
    slot_defaults: Dict[str, str],
) -> Dict[str, str]:
    """
    Build the {SLOT: value} map for the given teacher.

    Priority:
      1. spine_context explicit overrides (teacher_name, tradition, ...)
      2. teacher_registry.yaml display_name / formal_name / ei_profile.*
      3. slot_defaults from the templates YAML
    """
    ctx = spine_context or {}
    registry = (_load_registry().get("teachers") or {}).get(teacher_id, {}) or {}
    ei = registry.get("ei_profile") or {}

    def pick(*keys: str) -> str:
        for k in keys:
            v = ctx.get(k)
            if v:
                return str(v).strip()
            v = registry.get(k)
            if v:
                return str(v).strip()
            v = ei.get(k)
            if v:
                return str(v).strip()
        return ""

    teacher_name = (
        pick("teacher_name", "display_name")
        or str(registry.get("formal_name") or "").strip()
    )
    tradition = pick("tradition")
    tradition_short = pick("tradition_short")
    lineage = pick("teaching_lineage", "lineage", "tradition_phrase")
    practice_name = pick("practice_name")

    slots: Dict[str, str] = {}
    if teacher_name:
        slots["TEACHER_NAME"] = teacher_name
    if tradition:
        slots["TRADITION"] = tradition
    elif slot_defaults.get("TRADITION"):
        slots["TRADITION"] = str(slot_defaults["TRADITION"]).strip()
    if tradition_short:
        slots["TRADITION_SHORT"] = tradition_short
    elif slot_defaults.get("TRADITION_SHORT"):
        slots["TRADITION_SHORT"] = str(slot_defaults["TRADITION_SHORT"]).strip()
    if lineage:
        slots["TEACHING_LINEAGE"] = lineage
    elif slot_defaults.get("TEACHING_LINEAGE"):
        slots["TEACHING_LINEAGE"] = str(slot_defaults["TEACHING_LINEAGE"]).strip()
    if practice_name:
        slots["PRACTICE_NAME"] = practice_name
    # PRACTICE_NAME default is intentionally NOT applied from slot_defaults here
    # unless spine_context sets it — vague "the practice" defaults feel generic
    # in named exercise wrappers. Falls through to a variant not requiring it.
    if not practice_name and slot_defaults.get("PRACTICE_NAME"):
        slots["PRACTICE_NAME"] = str(slot_defaults["PRACTICE_NAME"]).strip()

    return slots


def _variant_pool(wrapper_block: Dict[str, Any]) -> List[str]:
    """Flatten pattern + variants into an ordered list."""
    out: List[str] = []
    p = wrapper_block.get("pattern")
    if isinstance(p, str) and p.strip():
        out.append(p.strip())
    for v in wrapper_block.get("variants") or []:
        if isinstance(v, str) and v.strip():
            out.append(v.strip())
    return out


def _resolve(pattern: str, slots: Dict[str, str]) -> Optional[str]:
    """Substitute {SLOT} tokens. Returns None if any token would be left unresolved."""
    def sub(m: re.Match[str]) -> str:
        key = m.group(1)
        val = slots.get(key)
        if not val:
            raise KeyError(key)
        return val

    try:
        resolved = _SLOT_RE.sub(sub, pattern)
    except KeyError:
        return None
    # Defense in depth: reject any remaining {TOKEN} tokens.
    if _SLOT_RE.search(resolved):
        return None
    return resolved


def _pick_variant(variants: List[str], slots: Dict[str, str], seed: str) -> Optional[str]:
    """Deterministically pick a fully-resolvable variant. Returns None if none resolve."""
    if not variants:
        return None
    h = int(hashlib.sha1(seed.encode("utf-8")).hexdigest(), 16)
    start = h % len(variants)
    for i in range(len(variants)):
        cand = variants[(start + i) % len(variants)]
        resolved = _resolve(cand, slots)
        if resolved:
            return resolved
    return None


def resolve_wrapper(
    *,
    teacher_id: Optional[str],
    section_type: str,
    seed: str,
    spine_context: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str]:
    """
    Return (prefix, suffix) strings to wrap teacher_atom_content.

    Returns ("", "") when:
      - no teacher_id is provided
      - templates yaml is missing / unreadable
      - no variant fully resolves under the available slots

    Invariant: returned strings never contain unresolved "{TOKEN}" placeholders.
    """
    if not teacher_id:
        return ("", "")

    tid = str(teacher_id).strip()
    if not tid:
        return ("", "")

    templates = _load_templates()
    if not templates:
        return ("", "")

    slot_defaults = {
        k: str(v) for k, v in (templates.get("slot_defaults") or {}).items() if v
    }
    slots = _teacher_slot_values(tid, spine_context, slot_defaults)

    # Choose mode: named when we have a real TEACHER_NAME, else generalized.
    teacher_name = slots.get("TEACHER_NAME")
    mode_order = (["named", "generalized", "composite"]
                  if teacher_name else ["generalized", "composite"])

    wrapper_key = _section_wrapper_key(section_type)

    for mode in mode_order:
        block = (templates.get(mode) or {}).get(wrapper_key)
        if not isinstance(block, dict):
            continue
        pool = _variant_pool(block)
        chosen = _pick_variant(pool, slots, f"{seed}:{mode}:{wrapper_key}")
        if chosen:
            # Prefix/suffix partition:
            #   intro_wrapper + exercise_wrapper → prefix only
            #   conclusion_wrapper               → suffix only
            if wrapper_key == "conclusion_wrapper":
                return ("", chosen)
            return (chosen, "")

    return ("", "")


def apply_wrapper(
    content: str,
    *,
    teacher_id: Optional[str],
    section_type: str,
    seed: str,
    spine_context: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Convenience: resolve + apply. Returns content unchanged if no wrapper applies.
    """
    body = (content or "").strip()
    if not body:
        return body
    prefix, suffix = resolve_wrapper(
        teacher_id=teacher_id,
        section_type=section_type,
        seed=seed,
        spine_context=spine_context,
    )
    if not prefix and not suffix:
        return body
    parts: List[str] = []
    if prefix:
        parts.append(prefix)
    parts.append(body)
    if suffix:
        parts.append(suffix)
    return "\n\n".join(parts)
