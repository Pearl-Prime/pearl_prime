"""
Science wrapper voice framing for section packet composition.

Sibling of `phoenix_v4/rendering/teacher_wrapper.py`. Loads
`config/catalog_planning/science_wrapper_templates.yaml` and resolves a
(prefix, suffix) framing pair for research-cited content based on a science
anchor's slot metadata, section type, and a deterministic seed.

Per BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01 (OVERLAY_SPEC "Author-first wrapper
doctrine") and OPD-20260606-005: the ONE author *references* research; the author
never narrates *as* the scientist. Science framing is third-person-citing
attribution supplied INSIDE the slot's own voice zone — a FINDING cited in a
REFLECTION stays authorial-I; a FINDING that opens a STORY stays third-person
omniscient. The wrapper supplies attribution, never a new speaker.

Contract (mirrors teacher_wrapper.py):
  - Returns ("", "") if no wrapper can be fully resolved (safety: NEVER emits
    unresolved {SLOT} tokens into prose, and never emits an un-attributed claim).
  - Mode resolution order is named → generalized → composite.
  - `named` mode is anti-fabrication-gated: it is attempted ONLY when a real
    {RESEARCHER} *and* {STUDY} are present. If either is missing, named mode is
    skipped and the resolver falls back to generalized (then composite). Never
    invent a researcher or a study.
  - Variant selection is deterministic given the seed.
  - intro_wrapper / exercise_wrapper → prefix; conclusion_wrapper → suffix.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_TEMPLATES_PATH = (
    REPO_ROOT / "config" / "catalog_planning" / "science_wrapper_templates.yaml"
)

_templates_cache: Optional[Dict[str, Any]] = None

_SLOT_RE = re.compile(r"\{([A-Z_][A-Z0-9_]*)\}")

# Anti-fabrication: named mode requires a real, citable researcher *and* study.
# These are the slots that must be present (from a real citation, never a
# slot_defaults fallback) before any named-mode variant may be attempted.
_NAMED_MODE_REQUIRED_SLOTS = ("RESEARCHER", "STUDY")

# Slots that may be filled from `slot_defaults` in the templates YAML.
# RESEARCHER and STUDY are intentionally EXCLUDED — defaulting them would
# manufacture provenance, which the anti-fabrication doctrine forbids. Only
# field-level slots (a body of work, not a citable paper) may default.
_DEFAULTABLE_SLOTS = ("FIELD", "FIELD_SHORT", "MECHANISM", "FINDING")


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


def _reset_caches_for_tests() -> None:
    """Clear cached YAML — tests that monkeypatch template paths call this."""
    global _templates_cache
    _templates_cache = None


def _section_wrapper_key(section_type: str) -> str:
    """Map section_type → which wrapper block to use.

    Mirrors teacher_wrapper._section_wrapper_key exactly so the two resolvers
    partition section types identically.
    """
    st = str(section_type or "").strip().upper()
    if st == "EXERCISE":
        return "exercise_wrapper"
    if st in ("CONCLUSION", "OUTRO", "CLOSE", "CLOSER"):
        return "conclusion_wrapper"
    return "intro_wrapper"


def _science_slot_values(
    spine_context: Optional[Dict[str, Any]],
    slot_defaults: Dict[str, str],
) -> Dict[str, str]:
    """
    Build the {SLOT: value} map for the science anchor.

    Priority:
      1. spine_context explicit values (researcher, study, finding, ...)
      2. slot_defaults from the templates YAML — FIELD-level slots only.

    Anti-fabrication: RESEARCHER and STUDY are sourced *exclusively* from
    spine_context. They are never filled from slot_defaults, because a defaulted
    researcher/study would invent provenance for a claim that has none.

    Recognized spine_context keys (case-insensitive on the canonical slot names,
    plus a few friendly aliases):
      RESEARCHER (researcher / researcher_name / author / scientist),
      STUDY      (study / study_name / paper / citation),
      FIELD      (field / discipline),
      FIELD_SHORT(field_short),
      FINDING    (finding),
      MECHANISM  (mechanism).
    """
    ctx = spine_context or {}

    # Normalize spine_context keys to upper-case once so callers can pass either
    # {"RESEARCHER": ...} or {"researcher": ...}.
    norm: Dict[str, str] = {}
    for k, v in ctx.items():
        if v is None:
            continue
        sv = str(v).strip()
        if sv:
            norm[str(k).strip().upper()] = sv

    aliases = {
        "RESEARCHER": ("RESEARCHER", "RESEARCHER_NAME", "AUTHOR", "SCIENTIST"),
        "STUDY": ("STUDY", "STUDY_NAME", "PAPER", "CITATION"),
        "FIELD": ("FIELD", "DISCIPLINE"),
        "FIELD_SHORT": ("FIELD_SHORT",),
        "FINDING": ("FINDING",),
        "MECHANISM": ("MECHANISM",),
    }

    def pick(slot: str) -> str:
        for key in aliases.get(slot, (slot,)):
            v = norm.get(key)
            if v:
                return v
        return ""

    slots: Dict[str, str] = {}

    # Provenance slots — spine_context ONLY, never defaulted.
    researcher = pick("RESEARCHER")
    if researcher:
        slots["RESEARCHER"] = researcher
    study = pick("STUDY")
    if study:
        slots["STUDY"] = study

    # Field-level slots — spine_context, then slot_defaults.
    for slot in _DEFAULTABLE_SLOTS:
        v = pick(slot)
        if v:
            slots[slot] = v
        elif slot_defaults.get(slot):
            slots[slot] = str(slot_defaults[slot]).strip()

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


def _block_slot_requirements(wrapper_block: Dict[str, Any]) -> List[str]:
    """Declared hard-required slots for a wrapper block (may be empty)."""
    reqs = wrapper_block.get("slot_requirements")
    if not isinstance(reqs, list):
        return []
    return [str(r).strip() for r in reqs if str(r).strip()]


def _resolve(pattern: str, slots: Dict[str, str]) -> Optional[str]:
    """Substitute {SLOT} tokens. Returns None if any token would be left unresolved."""
    def sub(m: "re.Match[str]") -> str:
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
    section_type: str,
    seed: str,
    spine_context: Optional[Dict[str, Any]] = None,
) -> Tuple[str, str]:
    """
    Return (prefix, suffix) strings to wrap research-cited atom content.

    Returns ("", "") when:
      - templates yaml is missing / unreadable
      - no variant fully resolves under the available slots

    Anti-fabrication: named mode is attempted ONLY when both a real {RESEARCHER}
    and {STUDY} are present in `spine_context`. Otherwise the resolver falls back
    to generalized (then composite), so an absent citation can never produce a
    named-attribution line.

    Invariant: returned strings never contain unresolved "{TOKEN}" placeholders.
    """
    templates = _load_templates()
    if not templates:
        return ("", "")

    slot_defaults = {
        k: str(v) for k, v in (templates.get("slot_defaults") or {}).items() if v
    }
    slots = _science_slot_values(spine_context, slot_defaults)

    # Anti-fabrication gate: named mode requires a real researcher AND study.
    has_named_provenance = all(
        slots.get(s) for s in _NAMED_MODE_REQUIRED_SLOTS
    )
    mode_order = (
        ["named", "generalized", "composite"]
        if has_named_provenance
        else ["generalized", "composite"]
    )

    wrapper_key = _section_wrapper_key(section_type)

    for mode in mode_order:
        block = (templates.get(mode) or {}).get(wrapper_key)
        if not isinstance(block, dict):
            continue
        # Honor the block's declared slot_requirements as a hard precheck. This
        # enforces multi-slot provenance even when a chosen variant happens to
        # reference only a subset (e.g. named exercise requires RESEARCHER+STUDY
        # though its bare pattern names only RESEARCHER's study).
        reqs = _block_slot_requirements(block)
        if any(not slots.get(r) for r in reqs):
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


def join_wrapped(prefix: str, body: str, suffix: str) -> str:
    """Join a resolved (prefix, body, suffix) framing into delivered prose.

    Mirrors teacher_wrapper.join_wrapped: intro_wrapper prefixes are
    *continuation lead-ins* that end in an ellipsis ("Research in {FIELD}
    consistently finds...") and are authored to flow INLINE into the body's
    opening sentence. Joining them with a paragraph break orphans the lead-in
    (the doctrine-intro bleed, follow-up to PR #1508), so an ellipsis-terminated
    prefix is joined inline with a single space; a label-style prefix (exercise
    wrappers, e.g. "A practice grounded in {FIELD} research") keeps its paragraph
    break. Suffixes (conclusion wrappers) are always appended as their own
    closing paragraph.
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
        section_type=section_type,
        seed=seed,
        spine_context=spine_context,
    )
    if not prefix and not suffix:
        return body
    return join_wrapped(prefix, body, suffix)
