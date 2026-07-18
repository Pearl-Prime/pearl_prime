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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_TEMPLATES_PATH = REPO_ROOT / "config" / "catalog_planning" / "teacher_wrapper_templates.yaml"
_REGISTRY_PATH = REPO_ROOT / "config" / "teachers" / "teacher_registry.yaml"

_templates_cache: Optional[Dict[str, Any]] = None
_registry_cache: Optional[Dict[str, Any]] = None

_SLOT_RE = re.compile(r"\{([A-Z_][A-Z0-9_]*)\}")

# Values that must never substitute a wrapper slot (bare adjectives / vague defaults).
_PLACEHOLDER_SLOT_VALUES: frozenset[str] = frozenset({
    "contemplative",  # legacy TRADITION default — grammatically bare adjective
    "the practice",
    "mindfulness and somatic",
})

_TRADITION_BARE_ADJECTIVE = frozenset({"contemplative"})

# Book-wide soft cap for identical generalized intro prefixes. Matches the
# book_quality_gate default cap (12) with one headroom slot so rotation
# prefers unused variants before the gate fires.
_WRAPPER_BOOK_CAP_DEFAULT = 11
_NGRAM_WINDOW_SIZES = (4, 5, 6)


def _wrapper_ngrams(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9']+", (text or "").lower())
    out: list[str] = []
    for n in _NGRAM_WINDOW_SIZES:
        for i in range(0, max(0, len(words) - n + 1)):
            out.append(" ".join(words[i : i + n]))
    return out


@dataclass
class WrapperUsageMemory:
    """Book-wide usage counter for resolved teacher-wrapper prefix stems."""

    book_cap: int = _WRAPPER_BOOK_CAP_DEFAULT
    _counts: dict[str, int] = field(default_factory=dict)
    _ngram_counts: dict[str, int] = field(default_factory=dict)

    @staticmethod
    def normalize_key(text: str) -> str:
        return re.sub(r"\s+", " ", (text or "").lower().strip())

    def count(self, text: str) -> int:
        return self._counts.get(self.normalize_key(text), 0)

    def record(self, text: str) -> None:
        key = self.normalize_key(text)
        self._counts[key] = self._counts.get(key, 0) + 1
        for ng in _wrapper_ngrams(text):
            self._ngram_counts[ng] = self._ngram_counts.get(ng, 0) + 1

    def at_cap(self, text: str) -> bool:
        return self.count(text) >= self.book_cap

    def max_ngram_load(self, text: str) -> int:
        """Highest 4–6-gram count this prefix would reach after one more use."""
        loads = [self._ngram_counts.get(ng, 0) + 1 for ng in _wrapper_ngrams(text)]
        return max(loads) if loads else 0

    def ngram_over_cap(self, text: str) -> bool:
        return self.max_ngram_load(text) > self.book_cap + 1


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



def _teacher_wrapper_slots_from_yaml(teacher_id: str) -> Dict[str, str]:
    """Per-teacher slot overrides from teacher_wrapper_templates.yaml."""
    templates = _load_templates()
    block = (templates.get("teacher_wrapper_slots") or {}).get(teacher_id) or {}
    return {k: str(v).strip() for k, v in block.items() if v}


def _slot_value_is_placeholder(key: str, value: str) -> bool:
    v = str(value or "").strip().lower()
    if not v:
        return True
    if key == "TRADITION" and v in _TRADITION_BARE_ADJECTIVE:
        return True
    if key == "TRADITION" and v in _PLACEHOLDER_SLOT_VALUES:
        return True
    if key == "PRACTICE_NAME" and v == "the practice":
        return True
    if key == "TEACHING_LINEAGE" and v == "mindfulness and somatic":
        return True
    return False

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

    yaml_slots = _teacher_wrapper_slots_from_yaml(teacher_id)

    slots: Dict[str, str] = {}
    if teacher_name:
        slots["TEACHER_NAME"] = teacher_name
    if tradition and not _slot_value_is_placeholder("TRADITION", tradition):
        slots["TRADITION"] = tradition
    elif yaml_slots.get("TRADITION"):
        slots["TRADITION"] = yaml_slots["TRADITION"]
    elif slot_defaults.get("TRADITION"):
        slots["TRADITION"] = str(slot_defaults["TRADITION"]).strip()
    if tradition_short and not _slot_value_is_placeholder("TRADITION_SHORT", tradition_short):
        slots["TRADITION_SHORT"] = tradition_short
    elif yaml_slots.get("TRADITION_SHORT"):
        slots["TRADITION_SHORT"] = yaml_slots["TRADITION_SHORT"]
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
        if not val or _slot_value_is_placeholder(key, val):
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


def _pick_variant(
    variants: List[str],
    slots: Dict[str, str],
    seed: str,
    *,
    usage_memory: Optional[WrapperUsageMemory] = None,
) -> Optional[str]:
    """Pick a fully-resolvable variant; prefer least-used when memory is provided."""
    if not variants:
        return None
    resolved_pool: list[tuple[str, str]] = []
    for cand in variants:
        resolved = _resolve(cand, slots)
        if resolved:
            resolved_pool.append((cand, resolved))
    if not resolved_pool:
        return None

    h = int(hashlib.sha1(seed.encode("utf-8")).hexdigest(), 16)
    if usage_memory is None:
        start = h % len(resolved_pool)
        for i in range(len(resolved_pool)):
            return resolved_pool[(start + i) % len(resolved_pool)][1]
        return None

    under_cap = [
        (cand, resolved)
        for cand, resolved in resolved_pool
        if not usage_memory.at_cap(resolved) and not usage_memory.ngram_over_cap(resolved)
    ]
    candidates = under_cap or [
        (cand, resolved)
        for cand, resolved in resolved_pool
        if not usage_memory.at_cap(resolved)
    ] or resolved_pool

    def _sort_key(item: tuple[str, str]) -> tuple[int, int, int]:
        _cand, resolved = item
        return (
            usage_memory.max_ngram_load(resolved),
            usage_memory.count(resolved),
            int(hashlib.sha1(f"{seed}:{resolved}".encode("utf-8")).hexdigest(), 16),
        )

    candidates.sort(key=_sort_key)
    return candidates[0][1]


def resolve_wrapper(
    *,
    teacher_id: Optional[str],
    section_type: str,
    seed: str,
    spine_context: Optional[Dict[str, Any]] = None,
    usage_memory: Optional[WrapperUsageMemory] = None,
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
        chosen = _pick_variant(
            pool,
            slots,
            f"{seed}:{mode}:{wrapper_key}",
            usage_memory=usage_memory,
        )
        if chosen:
            if usage_memory is not None and chosen.strip():
                usage_memory.record(chosen)
            # Prefix/suffix partition:
            #   intro_wrapper + exercise_wrapper → prefix only
            #   conclusion_wrapper               → suffix only
            if wrapper_key == "conclusion_wrapper":
                return ("", chosen)
            return (chosen, "")

    return ("", "")


def join_wrapped(prefix: str, body: str, suffix: str) -> str:
    """Join a resolved (prefix, body, suffix) framing into delivered prose.

    intro_wrapper prefixes are *continuation lead-ins* that end in an ellipsis
    ("What {TEACHER_NAME} keeps pointing toward is...") and are authored to flow
    INLINE into the body's opening sentence. Joining them with a paragraph break
    orphans the lead-in ("...is..." dangling above the doctrine) — the
    TEACHER_DOCTRINE_INTRO bleed (follow-up to PR #1508). So an ellipsis-terminated
    prefix is joined inline with a single space; a label-style prefix (exercise
    wrappers, e.g. "A practice from {TEACHER_NAME}: ...") keeps its paragraph break.
    Suffixes (conclusion wrappers) are always appended as their own closing paragraph.
    """
    body = (body or "").strip()
    out = body
    if prefix:
        p = prefix.rstrip()
        if p.endswith("...") or p.endswith("…"):
            out = f"{p} {out.lstrip()}".strip() if out else p
        else:
            out = f"{p}\n\n{out}".strip() if out else p
    if suffix:
        s = suffix.strip()
        out = f"{out}\n\n{s}".strip() if out else s
    return out


def apply_wrapper(
    content: str,
    *,
    teacher_id: Optional[str],
    section_type: str,
    seed: str,
    spine_context: Optional[Dict[str, Any]] = None,
    usage_memory: Optional[WrapperUsageMemory] = None,
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
        usage_memory=usage_memory,
    )
    if not prefix and not suffix:
        return body
    return join_wrapped(prefix, body, suffix)
