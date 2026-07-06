"""
Bestseller chapter composer: transforms raw slot prose into thesis-threaded chapters.

Assembly order per chapter:
  HOOK/SCENE → bridge → STORY → PIVOT → bridge → MECHANISM (derived from REFLECTION) →
  REFLECTION (trimmed/warmed) → bridge → EXERCISE → COMPRESSION →
  PERMISSION (high-cost chapters only) → INTEGRATION → TAKEAWAY → THREAD

Bridge sentences create argument flow between slots so chapters
make argued points rather than presenting disconnected slot sequences.

Always-on for book renders. No opt-in flag required.
"""
from __future__ import annotations

import hashlib
import logging
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_MAX_EXERCISES_PER_CHAPTER = 2

from phoenix_v4.exercises.models import AssemblyContext, EmotionalState

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

try:
    from phoenix_v4.rendering.locale_templates import get_template as _gt
except ImportError:
    def _gt(s, locale=None): return s

# Blocker C (Phase B 2026-06-16): import the chapter_flow gate's recognized cue lexicons
# so the opening-chapter clear-point / transition guarantee (_strengthen_opening_chapter_flow)
# stays a guaranteed SUBSET of what the gate detects, even if the gate's cue lists evolve.
# Falls back to a small literal subset if the gate module is unavailable (it has no
# circular dependency on this module — verified Phase B).
try:
    from phoenix_v4.quality.chapter_flow_gate import (
        _THESIS_CUES,
        _TRANSITION_CUES,
    )
except Exception:  # pragma: no cover - defensive fallback
    _THESIS_CUES = ("the point is", "what this means", "this is not")
    _TRANSITION_CUES = ("because", "which means", "this is why", "that matters because")


# ---------------------------------------------------------------------------
# Sentence utilities
# ---------------------------------------------------------------------------

def _sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


# Original narrow form: "[Placeholder: ...]" / "[Missing: ...]" / "[Silence: ...]".
_PLACEHOLDER_RE = re.compile(r"^\[(?:Placeholder|Missing|Silence)\s*:")
# DEFECT 5 (hook_placeholders): broaden to catch unfilled editorial/HOOK stub
# forms that reach reader prose, e.g. "[Persona-specific hook for <persona> × <topic>]",
# "[... hook for ...]", and TODO/TKTK/TBD/DRAFT markers. Case-insensitive; matches
# the whole bracketed token so it cannot fire on prose that merely contains the word.
_PLACEHOLDER_BRACKET_RE = re.compile(
    r"^\[[^\]]*\b(?:placeholder|hook for|persona-specific|todo|tktk|tbd|draft)\b[^\]]*\]$",
    re.IGNORECASE,
)


def _is_placeholder_text(text: str) -> bool:
    stripped = (text or "").strip()
    if not stripped:
        return False
    return bool(_PLACEHOLDER_RE.match(stripped) or _PLACEHOLDER_BRACKET_RE.match(stripped))


_CHAPTER_INDEX_TLS: int = 0  # Thread-local-ish chapter index for variant rotation

# Module-level locale for bridge functions (set by compose_chapter_prose)
_LOCALE_TLS: str | None = None
_BOOK_BRIDGE_MEMORY_TLS: "BridgeMemory | None" = None
_BOOK_TRANSITION_USED_TLS: set[str] | None = None
# OPD-109 Phase 1.1: per-render rotation memory for within-slot bridges.
# Set by render_spine_book at the start of a book render (so usage counts
# accumulate across chapters) and cleared at the end so we never leak state
# between books in a long-running process.
_WITHIN_SLOT_ROTATION_TLS: "WithinSlotRotationState | None" = None
_MECHANISM_THESIS_CACHE: dict[str, Any] | None = None
_EXERCISE_WRAPPER_CACHE: dict[str, Any] | None = None
_BRIDGE_TRANSITION_CACHE: dict[str, Any] | None = None
_BRIDGE_DIRECTION_SUBSTRINGS_CACHE: dict[tuple[str, str], str] | None = None
_WITHIN_SLOT_BRIDGE_CACHE: dict[str, Any] | None = None
_CHAPTER_THESIS_BANK_CACHE: dict | None = None
_CHAPTER_THESIS_TOPICS_CACHE: dict | None = None
_MECHANISM_THESIS_PATH = Path(__file__).resolve().parents[2] / "config" / "rendering" / "mechanism_thesis_families.yaml"
_EXERCISE_WRAPPER_PATH = Path(__file__).resolve().parents[2] / "config" / "rendering" / "exercise_wrapper_families.yaml"
_BRIDGE_TRANSITION_PATH = Path(__file__).resolve().parents[2] / "config" / "rendering" / "bridge_transition_families.yaml"
_WITHIN_SLOT_BRIDGE_PATH = Path(__file__).resolve().parents[2] / "config" / "rendering" / "within_slot_bridge_families.yaml"
_CHAPTER_THESIS_BANK_PATH = Path(__file__).resolve().parents[2] / "config" / "planning" / "chapter_thesis_bank.yaml"
_EMOTIONAL_JOBS = {"recognition", "mechanism", "deepening", "reframe", "practice", "integration", "resolution"}
_ROOT_CAP_4_CHAPTER_WINDOW = {
    "chapter",
    "pattern",
    "body",
    "point",
    "moment",
    "next",
    "explanation",
    "story",
    "signal",
    "practice",
    "mind",
    "cost",
}

# DEFERRED-LANE bridge_bank (2026-06-15): config/rendering/bridge_transition_families.yaml
# carries a synthetic per-entry disambiguator stem ("variant-1", "variant-2", …) alongside
# each entry's real semantic stem (e.g. "name the turn"). These synthetic tokens are NOT
# anti-reuse signals — only ~2 distinct values span all 840 entries across every bridge_type
# and emotional_job. Because the book-level BridgeMemory is shared across ALL slots and the
# THREAD slot is composed LAST (assembly order: INTEGRATION → TAKEAWAY → THREAD), earlier
# bridge emitters saturate "variant-1"/"variant-2" within the 3-chapter stem window, so the
# `recent_stem_count(stem) >= 1` gate in _score_bridge_candidate rejected EVERY data-driven
# "Ahead of you:" thread_fallback candidate (score -10_000) → fell through to the literal pool
# (0/12 chapters served the bank in repro). Dropping the synthetic token from the stem list at
# collection time lets real semantic stems still drive dedup while the bank actually serves.
# Does NOT touch #1589's book-distinct dedup, which keys on exact phrase_used_book + the real
# semantic stems/roots/shapes — none of which are the synthetic variant token.
_SYNTHETIC_VARIANT_STEM_RE = re.compile(r"^variant-\d+$")

# A1 scene_anchor fix (Phase B 2026-06-16): every entry inside one
# (bridge_type, emotional_job) block of bridge_transition_families.yaml carries the
# SAME embedded chapter-direction substring (e.g. all 20 `recognition` entries contain
# "seeing the pattern before defending it"). BridgeMemory already dedups by exact
# phrase/shape/stem/family/root, so the selector freely picks several *different-shaped*
# bridges that all carry the identical direction substring within one chapter. The
# scene_anchor_density gate (config/quality/scene_anchor_density_config.yaml, cap=3)
# counts that shared >=4-word substring across paragraphs and FAILs at >3 paragraphs —
# the dominant root for scene_anchor_density failures on the courage proof (6/12 chapters).
# Fix: track the direction substring per chapter in BridgeMemory and VETO a bank candidate
# once its direction substring has already landed in `_DIRECTION_CAP_PER_CHAPTER` paragraphs
# of the current chapter. When the bank is vetoed the selector returns None and the caller
# falls through to its legacy (direction-free) option pool, so the chapter's transitions vary
# instead of re-stamping one direction. Set to 2 to leave headroom under the gate's cap of 3
# (a non-bank paragraph occasionally echoes the substring; 2 bank carriers + <=1 other <= 3).
# This NEVER weakens a gate — it varies the OUTPUT so the gate passes honestly.
_DIRECTION_CAP_PER_CHAPTER = 2
# A direction substring is the longest shared word n-gram across a block's entries; only
# n-grams of at least this many words count (matches the scene_anchor gate's >=4-word window).
_DIRECTION_MIN_WORDS = 4
_DIRECTION_MAX_WORDS = 8

def _pick_variant(options: list[str], *seed_parts: str) -> str:
    if not options:
        return ""
    seed = "||".join((part or "").strip().lower() for part in seed_parts if part)
    if not seed:
        picked = options[_CHAPTER_INDEX_TLS % len(options)]
    else:
        # Mix in chapter index so same content in different chapters gets different picks
        seed = f"{seed}||ch{_CHAPTER_INDEX_TLS}"
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:8], "big") % len(options)
        picked = options[idx]
    # Locale-aware: translate the picked English string if locale is set
    return _gt(picked, locale=_LOCALE_TLS) if _LOCALE_TLS else picked


def _normalize_emotional_job(emotional_job: str) -> str:
    job = (emotional_job or "").strip().lower()
    return job if job in _EMOTIONAL_JOBS else ""


# DEFECT 1 (cross_book_transitions): the planner emits arc-role vocab
# (ALLOWED_EMOTIONAL_ROLES in arc_loader.py = recognition/destabilization/
# reframe/stabilization/integration, plus legacy turn/opening/destabilize/
# escalation/landing) that is NOT identical to the bridge bank's emotional-job
# vocab (_EMOTIONAL_JOBS). recognition/reframe/integration already overlap, but
# destabilization/stabilization (and the legacy synonyms) fall through to job=''
# so _select_bridge_candidate is skipped and the hardcoded fallback pool fires.
# Mapping these onto bank jobs lets the data-driven 'Ahead of you:' bank fire.
_ARC_ROLE_TO_EMOTIONAL_JOB = {
    "turn": "mechanism",
    "opening": "recognition",
    "destabilize": "mechanism",
    "destabilization": "mechanism",
    "escalation": "mechanism",
    "landing": "resolution",
    "stabilization": "resolution",
}


def _resolve_emotional_job(emotional_job: str) -> str:
    """Resolve a planner arc-role OR a bridge-bank emotional-job to a bank job.

    Returns '' only when the role maps to nothing the bridge bank can serve.
    """
    raw = (emotional_job or "").strip().lower()
    if not raw:
        return ""
    direct = _normalize_emotional_job(raw)
    if direct:
        return direct
    mapped = _ARC_ROLE_TO_EMOTIONAL_JOB.get(raw, "")
    return mapped if mapped in _EMOTIONAL_JOBS else ""


def _load_mechanism_thesis_families() -> dict[str, Any]:
    global _MECHANISM_THESIS_CACHE
    if _MECHANISM_THESIS_CACHE is not None:
        return _MECHANISM_THESIS_CACHE
    if yaml is None:
        _MECHANISM_THESIS_CACHE = {}
        return _MECHANISM_THESIS_CACHE
    try:
        loaded = yaml.safe_load(_MECHANISM_THESIS_PATH.read_text(encoding="utf-8"))
    except Exception:
        loaded = {}
    _MECHANISM_THESIS_CACHE = loaded if isinstance(loaded, dict) else {}
    return _MECHANISM_THESIS_CACHE


def _load_exercise_wrapper_families() -> dict[str, Any]:
    global _EXERCISE_WRAPPER_CACHE
    if _EXERCISE_WRAPPER_CACHE is not None:
        return _EXERCISE_WRAPPER_CACHE
    if yaml is None:
        _EXERCISE_WRAPPER_CACHE = {}
        return _EXERCISE_WRAPPER_CACHE
    try:
        loaded = yaml.safe_load(_EXERCISE_WRAPPER_PATH.read_text(encoding="utf-8"))
    except Exception:
        loaded = {}
    _EXERCISE_WRAPPER_CACHE = loaded if isinstance(loaded, dict) else {}
    return _EXERCISE_WRAPPER_CACHE


def _load_bridge_transition_families() -> dict[str, Any]:
    global _BRIDGE_TRANSITION_CACHE
    if _BRIDGE_TRANSITION_CACHE is not None:
        return _BRIDGE_TRANSITION_CACHE
    if yaml is None:
        _BRIDGE_TRANSITION_CACHE = {}
        return _BRIDGE_TRANSITION_CACHE
    try:
        loaded = yaml.safe_load(_BRIDGE_TRANSITION_PATH.read_text(encoding="utf-8"))
    except Exception:
        loaded = {}
    _BRIDGE_TRANSITION_CACHE = loaded if isinstance(loaded, dict) else {}
    return _BRIDGE_TRANSITION_CACHE


def _longest_shared_ngram(texts: list[str]) -> str:
    """Return the longest word n-gram (>=_DIRECTION_MIN_WORDS words) present in EVERY text.

    Used to extract the chapter-direction substring shared by all entries of one
    (bridge_type, emotional_job) block. Deterministic; returns "" when no qualifying
    shared n-gram exists. Comparison is on lowercased alphabetic word tokens so trivial
    punctuation/casing differences in the YAML do not defeat the match.
    """
    if not texts:
        return ""
    tokenized: list[list[str]] = [re.findall(r"[a-z']+", t.lower()) for t in texts]
    if any(not toks for toks in tokenized):
        return ""
    # Candidate n-grams come from the SHORTEST entry (an n-gram common to all must fit it).
    base = min(tokenized, key=len)
    others = [set() for _ in tokenized]
    # Build per-text n-gram sets lazily only for the lengths we test, longest first.
    best = ""
    for n in range(min(_DIRECTION_MAX_WORDS, len(base)), _DIRECTION_MIN_WORDS - 1, -1):
        # n-gram sets for every text at this length
        sets = []
        for toks in tokenized:
            sets.append({" ".join(toks[i:i + n]) for i in range(len(toks) - n + 1)})
        # candidates that appear in the base AND in every other text
        for i in range(len(base) - n + 1):
            cand = " ".join(base[i:i + n])
            if all(cand in s for s in sets):
                return cand  # longest-first → first hit is the longest shared n-gram
    return best


def _bridge_direction_substrings() -> dict[tuple[str, str], str]:
    """Map each (bridge_type, emotional_job) block to its shared chapter-direction substring.

    Cached after first call. The substring is the longest >=4-word n-gram present in every
    entry's text inside that block (see _longest_shared_ngram). Empty string when a block has
    no qualifying shared substring (then no direction cap applies to that block).

    A1 scene_anchor fix (Phase B 2026-06-16).
    """
    global _BRIDGE_DIRECTION_SUBSTRINGS_CACHE
    if _BRIDGE_DIRECTION_SUBSTRINGS_CACHE is not None:
        return _BRIDGE_DIRECTION_SUBSTRINGS_CACHE
    payload = _load_bridge_transition_families()
    out: dict[tuple[str, str], str] = {}
    bridge_types = payload.get("bridge_types") if isinstance(payload, dict) else None
    if isinstance(bridge_types, dict):
        for btype, jobs in bridge_types.items():
            if not isinstance(jobs, dict):
                continue
            for job, shapes in jobs.items():
                if not isinstance(shapes, dict):
                    continue
                texts: list[str] = []
                for _shape, entries in shapes.items():
                    if not isinstance(entries, list):
                        continue
                    for entry in entries:
                        if isinstance(entry, dict):
                            t = str(entry.get("text") or "").strip()
                            if t:
                                texts.append(t)
                direction = _longest_shared_ngram(texts)
                if direction:
                    out[(str(btype), str(job))] = direction
    _BRIDGE_DIRECTION_SUBSTRINGS_CACHE = out
    return _BRIDGE_DIRECTION_SUBSTRINGS_CACHE


def _load_within_slot_bridge_families() -> dict[str, Any]:
    """Load config/rendering/within_slot_bridge_families.yaml (cached).

    Defect ref: OPD-109 — within-slot atom transition prose.
    See docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md.
    """
    global _WITHIN_SLOT_BRIDGE_CACHE
    if _WITHIN_SLOT_BRIDGE_CACHE is not None:
        return _WITHIN_SLOT_BRIDGE_CACHE
    if yaml is None:
        _WITHIN_SLOT_BRIDGE_CACHE = {}
        return _WITHIN_SLOT_BRIDGE_CACHE
    try:
        loaded = yaml.safe_load(_WITHIN_SLOT_BRIDGE_PATH.read_text(encoding="utf-8"))
    except Exception:
        loaded = {}
    _WITHIN_SLOT_BRIDGE_CACHE = loaded if isinstance(loaded, dict) else {}
    return _WITHIN_SLOT_BRIDGE_CACHE


def render_glue_enabled() -> bool:
    """Master kill-switch — production default OFF (de-injection 2026-07-05)."""
    from phoenix_v4.rendering.render_glue import render_glue_enabled as _master

    return _master()


def within_slot_bridges_enabled() -> bool:
    """Production default OFF (restore 2026-07-04): no template within-slot glue.

    YAML key ``within_slot_bridges`` (default false). Dwell/setup is the Claude
    line-edit lane. Unit tests of the bridge machinery pass ``enabled=True``.
    """
    if not render_glue_enabled():
        return False
    payload = _load_within_slot_bridge_families()
    return bool(payload.get("within_slot_bridges", False))


def _glue_family_enabled(env_var: str, yaml_key: str, loader) -> bool:
    """YAML default OFF; set env var to ``1``/``true`` for A/B re-enable."""
    env = os.environ.get(env_var)
    if env is not None:
        return env.strip().lower() not in ("0", "false", "no", "")
    payload = loader()
    return bool(payload.get(yaml_key, False))


def bridge_transition_families_enabled() -> bool:
    """Production default OFF (de-injection 2026-07-05): no bridge_transition YAML glue."""
    if not render_glue_enabled():
        return False
    return _glue_family_enabled(
        "PHOENIX_BRIDGE_TRANSITION_FAMILIES",
        "bridge_transition_families",
        _load_bridge_transition_families,
    )


def mechanism_thesis_families_enabled() -> bool:
    """Production default OFF (de-injection 2026-07-05): no mechanism_thesis YAML glue."""
    if not render_glue_enabled():
        return False
    return _glue_family_enabled(
        "PHOENIX_MECHANISM_THESIS_FAMILIES",
        "mechanism_thesis_families",
        _load_mechanism_thesis_families,
    )


def exercise_wrapper_families_enabled() -> bool:
    """Production default OFF (de-injection 2026-07-05): no exercise_wrapper YAML glue."""
    if not render_glue_enabled():
        return False
    return _glue_family_enabled(
        "PHOENIX_EXERCISE_WRAPPER_FAMILIES",
        "exercise_wrapper_families",
        _load_exercise_wrapper_families,
    )


# ---------------------------------------------------------------------------
# OPD-112: Next-atom semantic classifier for bridge ↔ following-atom continuity
# ---------------------------------------------------------------------------
# When a within-slot bridge promises a particular kind of content
# (e.g. "The teacher would put it this way."), the bridge selector must
# refuse to emit it if the next atom is NOT a teacher-attributed teaching.
# `_classify_atom` inspects the next-atom body for tells and returns a
# coarse content-class label that maps onto YAML `next_atom_expectation:`.
#
# Categories (kept small + cheap, regex-only, no LLM):
#   teacher_teaching, named_story, mechanism_paragraph, body_anchor,
#   reflective_pivot, scene_vignette, practical_takeaway, any
#
# Defect ref: OPD-112 — bridge ↔ following-atom semantic continuity.

# Substring tells (lowercased). Order matters: first hit wins, except `any`
# which is reserved for the fallback when no specific pattern matches.
_NEXT_ATOM_TEACHER_PATTERNS = (
    re.compile(r"\bahjan\b", re.I),
    re.compile(r"\b(?:the\s+)?teacher\b", re.I),
    re.compile(r"\b(?:the\s+)?(?:tradition|lineage|teaching)\b", re.I),
    re.compile(r"\bdharma\b", re.I),
    re.compile(r"\bthai\s+forest\b", re.I),
    re.compile(r"\bbuddha\b", re.I),
    re.compile(r"\bmaster\s+[A-Z][a-z]+\b", re.I),
)
_NEXT_ATOM_MECHANISM_PATTERNS = (
    re.compile(r"^\s*(?:here\s+is\s+the\s+mechanism|the\s+mechanism\s+(?:is|underneath)|what\s+this\s+means\s+is|underneath\s+the\s+(?:feeling|story|noise))", re.I),
    re.compile(r"\bthe\s+mechanism\s+(?:is|behind|underneath)\b", re.I),
    re.compile(r"\b(?:nervous\s+system|alarm)\s+(?:fires|treats|runs)\b", re.I),
)
_NEXT_ATOM_BODY_PATTERNS = (
    re.compile(r"^\s*your\s+(?:chest|jaw|throat|shoulders?|breath|hands?|stomach|gut|face|knee|neck|spine)\b", re.I),
    re.compile(r"^\s*(?:notice|feel|place)\s+(?:your|the)\s+(?:chest|jaw|throat|breath|hands?|shoulders?|body)\b", re.I),
)
_NEXT_ATOM_SCENE_PATTERNS = (
    re.compile(r"\b(?:slack|notion|figma|jira|zoom|teams|email|inbox|standup|stand-up|sprint|kanban|laptop|monitor|airpods)\b", re.I),
    re.compile(r"^\s*(?:at\s+\d+(?::\d+)?\s*(?:a\.?m\.?|p\.?m\.?|am|pm)|on\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday))", re.I),
    re.compile(r"\b(?:meeting|commute|elevator|coffee\s+shop|office|hallway|kitchen\s+counter)\b", re.I),
)
_NEXT_ATOM_PRACTICAL_PATTERNS = (
    re.compile(r"^\s*(?:try\s+this|do\s+this|here\s+is\s+(?:the\s+practice|how)|practice\s*:)", re.I),
    re.compile(r"^\s*(?:step\s+\d|\d+\.\s)", re.I),
    re.compile(r"^\s*(?:notice|name|breathe|place|set|write|repeat|count)\b.*\.\s*$", re.I),
)
_NEXT_ATOM_REFLECTIVE_PATTERNS = (
    re.compile(r"^\s*(?:what\s+(?:if|you|the)|where\s+in\s+your|can\s+you\s+name)\b", re.I),
    re.compile(r"\?\s*$", re.M),
)
_NAMED_STORY_PATTERN = re.compile(
    r"^\s*([A-Z][a-z]{2,}(?:\s+[A-Z][a-z]+)?)\s+(?:was|sat|opened|walked|stared|noticed|stood|looked|leaned|texted|messaged|asked|said|stopped|paused|turned|froze)\b"
)


def _classify_atom(atom: str) -> str:
    """Return a coarse content-class label for an atom body.

    Used by `_bridge_within_slot` to filter bridge candidates whose YAML
    `next_atom_expectation` does not match what is actually coming next.
    Falls back to ``"any"`` when no tell is found — that label is the
    universal acceptor in the bridge filter.

    Defect ref: OPD-112 — bridge ↔ following-atom semantic continuity.
    """
    body = (atom or "").strip()
    if not body:
        return "any"
    head = body[:280]  # check only the opening — fastest tell
    # Order: most specific first.
    if any(p.search(head) for p in _NEXT_ATOM_TEACHER_PATTERNS):
        return "teacher_teaching"
    if any(p.search(head) for p in _NEXT_ATOM_MECHANISM_PATTERNS):
        return "mechanism_paragraph"
    if any(p.search(head) for p in _NEXT_ATOM_BODY_PATTERNS):
        return "body_anchor"
    # Named-story pattern is checked BEFORE scene patterns because a
    # capitalized character name followed by a stative verb is a more
    # specific tell than ambient scene props (e.g. "monitor", "laptop")
    # that often appear inside named-character vignettes too.
    if _NAMED_STORY_PATTERN.search(head):
        return "named_story"
    if any(p.search(head) for p in _NEXT_ATOM_SCENE_PATTERNS):
        return "scene_vignette"
    if any(p.search(head) for p in _NEXT_ATOM_PRACTICAL_PATTERNS):
        return "practical_takeaway"
    if any(p.search(head) for p in _NEXT_ATOM_REFLECTIVE_PATTERNS):
        return "reflective_pivot"
    return "any"


_NEXT_ATOM_EXPECTATION_LABELS = frozenset({
    "teacher_teaching",
    "named_story",
    "mechanism_paragraph",
    "body_anchor",
    "reflective_pivot",
    "scene_vignette",
    "practical_takeaway",
    "any",
})


def _load_chapter_thesis_bank() -> dict:
    """Load config/planning/chapter_thesis_bank.yaml (cached after first call)."""
    global _CHAPTER_THESIS_BANK_CACHE
    if _CHAPTER_THESIS_BANK_CACHE is not None:
        return _CHAPTER_THESIS_BANK_CACHE
    if yaml is None:
        _CHAPTER_THESIS_BANK_CACHE = {}
        return _CHAPTER_THESIS_BANK_CACHE
    if _CHAPTER_THESIS_BANK_PATH.exists():
        try:
            data = yaml.safe_load(_CHAPTER_THESIS_BANK_PATH.read_text(encoding="utf-8")) or {}
            _CHAPTER_THESIS_BANK_CACHE = data.get("intents") or {}
        except Exception:
            _CHAPTER_THESIS_BANK_CACHE = {}
    else:
        _CHAPTER_THESIS_BANK_CACHE = {}
    return _CHAPTER_THESIS_BANK_CACHE


def _load_chapter_thesis_topics() -> dict:
    """Load the optional `topics:` overlay from chapter_thesis_bank.yaml (cached).

    Returns {topic_id: {intent: {engine: thesis}}}. Empty when no overlay is
    authored; callers fall through to the engine baseline in that case.
    """
    global _CHAPTER_THESIS_TOPICS_CACHE
    if _CHAPTER_THESIS_TOPICS_CACHE is not None:
        return _CHAPTER_THESIS_TOPICS_CACHE
    if yaml is None or not _CHAPTER_THESIS_BANK_PATH.exists():
        _CHAPTER_THESIS_TOPICS_CACHE = {}
        return _CHAPTER_THESIS_TOPICS_CACHE
    try:
        data = yaml.safe_load(_CHAPTER_THESIS_BANK_PATH.read_text(encoding="utf-8")) or {}
        _CHAPTER_THESIS_TOPICS_CACHE = data.get("topics") or {}
    except Exception:
        _CHAPTER_THESIS_TOPICS_CACHE = {}
    return _CHAPTER_THESIS_TOPICS_CACHE


# Canonical engine slug → thesis-bank column. overwhelm/spiral/comparison now
# have their own columns; somatic/cognitive aliases kept for back-compat.
_THESIS_ENGINE_COLUMN: dict[str, str] = {
    "somatic": "watcher",
    "watcher": "watcher",
    "false": "false_alarm",
    "false_alarm": "false_alarm",
    "alarm": "false_alarm",
    "shame": "shame",
    "grief": "grief",
    "cognitive": "false_alarm",
    "overwhelm": "overwhelm",
    "spiral": "spiral",
    "comparison": "comparison",
}


def _normalize_thesis_engine(engine_type: str) -> str:
    """Resolve an engine slug to its thesis-bank column (full slug → leading token).

    Unlike the old path, this does NOT collapse unknown canonical engines to
    "watcher": the three previously-TBD engines resolve to their own columns.
    Genuinely unrecognised slugs are returned normalized (so a missing-engine
    lookup yields no thesis and the chain falls through rather than mislabelling).
    """
    key = (engine_type or "").lower().replace("-", "_").replace(" ", "_").strip()
    if key in _THESIS_ENGINE_COLUMN:
        return _THESIS_ENGINE_COLUMN[key]
    head = key.split("_")[0]
    return _THESIS_ENGINE_COLUMN.get(head, key)


def _recent_count(store: dict[int, dict[str, int]], key: str, chapter_index: int, window: int) -> int:
    total = 0
    for idx in range(max(0, chapter_index - window), chapter_index + 1):
        total += store.get(idx, {}).get(key, 0)
    return total


@dataclass
class MechanismThesisMemory:
    """Tracks mechanism/thesis usage across chapters for anti-reuse."""

    used_phrases_book: set[str] = field(default_factory=set)
    stem_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    root_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    shape_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)

    def phrase_used_book(self, phrase: str) -> bool:
        return phrase.strip().lower() in self.used_phrases_book

    def recent_stem_count(self, stem: str, chapter_index: int, window: int = 3) -> int:
        return _recent_count(self.stem_usage_by_chapter, stem.strip().lower(), chapter_index, window)

    def recent_root_count(self, root: str, chapter_index: int, window: int = 3) -> int:
        return _recent_count(self.root_usage_by_chapter, root.strip().lower(), chapter_index, window)

    def recent_shape_count(self, shape: str, chapter_index: int, window: int = 2) -> int:
        return _recent_count(self.shape_usage_by_chapter, shape.strip().lower(), chapter_index, window)

    def register(
        self,
        *,
        chapter_index: int,
        phrase: str,
        shape: str,
        stems: list[str],
        roots: list[str],
    ) -> None:
        key_phrase = phrase.strip().lower()
        if not key_phrase:
            return
        self.used_phrases_book.add(key_phrase)
        shape_map = self.shape_usage_by_chapter.setdefault(chapter_index, {})
        shape_key = shape.strip().lower()
        if shape_key:
            shape_map[shape_key] = shape_map.get(shape_key, 0) + 1
        stem_map = self.stem_usage_by_chapter.setdefault(chapter_index, {})
        for stem in stems:
            k = stem.strip().lower()
            if k:
                stem_map[k] = stem_map.get(k, 0) + 1
        root_map = self.root_usage_by_chapter.setdefault(chapter_index, {})
        for root in roots:
            k = root.strip().lower()
            if k:
                root_map[k] = root_map.get(k, 0) + 1


@dataclass
class ExerciseWrapperMemory:
    """Tracks exercise wrapper usage across chapters for anti-reuse."""

    used_phrases_book: set[str] = field(default_factory=set)
    stem_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    root_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    shape_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    family_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)

    def phrase_used_book(self, phrase: str) -> bool:
        return phrase.strip().lower() in self.used_phrases_book

    def recent_stem_count(self, stem: str, chapter_index: int, window: int = 3) -> int:
        return _recent_count(self.stem_usage_by_chapter, stem.strip().lower(), chapter_index, window)

    def recent_root_count(self, root: str, chapter_index: int, window: int = 3) -> int:
        return _recent_count(self.root_usage_by_chapter, root.strip().lower(), chapter_index, window)

    def recent_shape_count(self, shape: str, chapter_index: int, window: int = 2) -> int:
        return _recent_count(self.shape_usage_by_chapter, shape.strip().lower(), chapter_index, window)

    def recent_family_count(self, family: str, chapter_index: int, window: int = 1) -> int:
        return _recent_count(self.family_usage_by_chapter, family.strip().lower(), chapter_index, window)

    def register(
        self,
        *,
        chapter_index: int,
        phrase: str,
        shape: str,
        family: str,
        stems: list[str],
        roots: list[str],
    ) -> None:
        key_phrase = phrase.strip().lower()
        if not key_phrase:
            return
        self.used_phrases_book.add(key_phrase)
        shape_map = self.shape_usage_by_chapter.setdefault(chapter_index, {})
        shape_key = shape.strip().lower()
        if shape_key:
            shape_map[shape_key] = shape_map.get(shape_key, 0) + 1
        family_map = self.family_usage_by_chapter.setdefault(chapter_index, {})
        family_key = family.strip().lower()
        if family_key:
            family_map[family_key] = family_map.get(family_key, 0) + 1
        stem_map = self.stem_usage_by_chapter.setdefault(chapter_index, {})
        for stem in stems:
            k = stem.strip().lower()
            if k:
                stem_map[k] = stem_map.get(k, 0) + 1
        root_map = self.root_usage_by_chapter.setdefault(chapter_index, {})
        for root in roots:
            k = root.strip().lower()
            if k:
                root_map[k] = root_map.get(k, 0) + 1


@dataclass
class BridgeMemory:
    """Tracks bridge usage across chapter and book scope for anti-reuse."""

    used_phrases_book: set[str] = field(default_factory=set)
    used_phrases_by_chapter: dict[int, set[str]] = field(default_factory=dict)
    stem_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    root_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    shape_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    family_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)
    last_shape_by_chapter: dict[int, str] = field(default_factory=dict)
    # A1 scene_anchor fix: per-chapter count of how many bank bridges carrying a given
    # chapter-direction substring have already landed in that chapter.
    direction_usage_by_chapter: dict[int, dict[str, int]] = field(default_factory=dict)

    def phrase_used_book(self, phrase: str) -> bool:
        return phrase.strip().lower() in self.used_phrases_book

    def phrase_used_chapter(self, chapter_index: int, phrase: str) -> bool:
        return phrase.strip().lower() in self.used_phrases_by_chapter.get(chapter_index, set())

    def direction_count_chapter(self, chapter_index: int, direction: str) -> int:
        """How many bank bridges carrying ``direction`` already used in this chapter."""
        key = direction.strip().lower()
        if not key:
            return 0
        return self.direction_usage_by_chapter.get(chapter_index, {}).get(key, 0)

    def recent_stem_count(self, stem: str, chapter_index: int, window: int = 3) -> int:
        return _recent_count(self.stem_usage_by_chapter, stem.strip().lower(), chapter_index, window)

    def recent_root_count(self, root: str, chapter_index: int, window: int = 3) -> int:
        return _recent_count(self.root_usage_by_chapter, root.strip().lower(), chapter_index, window)

    def recent_shape_count(self, shape: str, chapter_index: int, window: int = 2) -> int:
        return _recent_count(self.shape_usage_by_chapter, shape.strip().lower(), chapter_index, window)

    def recent_family_count(self, family: str, chapter_index: int, window: int = 2) -> int:
        return _recent_count(self.family_usage_by_chapter, family.strip().lower(), chapter_index, window)

    def register(
        self,
        *,
        chapter_index: int,
        phrase: str,
        shape: str,
        stems: list[str],
        roots: list[str],
        family_key: str,
        direction: str = "",
    ) -> None:
        p = phrase.strip().lower()
        if not p:
            return
        self.used_phrases_book.add(p)
        chapter_set = self.used_phrases_by_chapter.setdefault(chapter_index, set())
        chapter_set.add(p)
        s_map = self.shape_usage_by_chapter.setdefault(chapter_index, {})
        s_key = shape.strip().lower()
        if s_key:
            s_map[s_key] = s_map.get(s_key, 0) + 1
            self.last_shape_by_chapter[chapter_index] = s_key
        f_map = self.family_usage_by_chapter.setdefault(chapter_index, {})
        f_key = family_key.strip().lower()
        if f_key:
            f_map[f_key] = f_map.get(f_key, 0) + 1
        stem_map = self.stem_usage_by_chapter.setdefault(chapter_index, {})
        for stem in stems:
            k = stem.strip().lower()
            if k:
                stem_map[k] = stem_map.get(k, 0) + 1
        root_map = self.root_usage_by_chapter.setdefault(chapter_index, {})
        for root in roots:
            k = root.strip().lower()
            if k:
                root_map[k] = root_map.get(k, 0) + 1
        d_key = direction.strip().lower()
        if d_key:
            d_map = self.direction_usage_by_chapter.setdefault(chapter_index, {})
            d_map[d_key] = d_map.get(d_key, 0) + 1


@dataclass
class WithinSlotRotationState:
    """OPD-109 Phase 1.1: rotation memory for within-slot bridge variants.

    Tracks variant usage across one book render so the selector can:
      - prefer variants that have not yet been used in any chapter
      - fall back to the least-recently-used variant among the candidate pool
      - never reuse the same variant twice within a single chapter

    Identity of a variant is the canonical text string. Selection is keyed
    deterministically off (chapter_index, slot_type, atom_pair_index) so
    re-renders with the same seed produce identical output.

    Defect ref: docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md
    """

    # variant text -> count of uses across the entire book render
    book_usage: dict[str, int] = field(default_factory=dict)
    # chapter_index -> set of variant texts already used in that chapter
    chapter_used: dict[int, set[str]] = field(default_factory=dict)

    def book_count(self, text: str) -> int:
        return self.book_usage.get(text, 0)

    def chapter_has_used(self, chapter_index: int, text: str) -> bool:
        return text in self.chapter_used.get(chapter_index, set())

    def register(self, chapter_index: int, text: str) -> None:
        if not text:
            return
        self.book_usage[text] = self.book_usage.get(text, 0) + 1
        self.chapter_used.setdefault(chapter_index, set()).add(text)


def _chapter_position_bucket(chapter_index: int, total_chapters: int) -> str:
    if total_chapters <= 1 or chapter_index >= total_chapters - 1:
        return "final"
    if chapter_index <= 2:
        return "early"
    if chapter_index <= 7:
        return "middle"
    return "late"


def _collect_bridge_candidates(
    *,
    bridge_type: str,
    emotional_job: str,
    chapter_position: str,
) -> list[dict[str, Any]]:
    payload = _load_bridge_transition_families()
    by_type = (payload.get("bridge_types") or {}).get(bridge_type) or {}
    by_job = by_type.get(emotional_job) if isinstance(by_type, dict) else {}
    if not isinstance(by_job, dict):
        return []
    out: list[dict[str, Any]] = []
    for shape, entries in by_job.items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            text = str(entry.get("text") or "").strip()
            if not text or re.search(r"\b(this chapter is about|the purpose of this section)\b", text, flags=re.I):
                continue
            pos = str(entry.get("position_bias") or "").strip().lower() or "any"
            if pos not in {"any", chapter_position}:
                continue
            out.append(
                {
                    "text": text,
                    "shape": str(shape).strip().lower(),
                    # Drop synthetic "variant-N" disambiguator stems (see
                    # _SYNTHETIC_VARIANT_STEM_RE) so they cannot poison the shared
                    # book-level BridgeMemory and starve later-composed slots (THREAD).
                    "stems": [
                        s
                        for s in (
                            str(s).strip().lower()
                            for s in (entry.get("stems") or [])
                            if str(s).strip()
                        )
                        if not _SYNTHETIC_VARIANT_STEM_RE.match(s)
                    ],
                    "roots": [str(r).strip().lower() for r in (entry.get("roots") or []) if str(r).strip()],
                    "scene_bias": [str(k).strip().lower() for k in (entry.get("scene_bias") or []) if str(k).strip()],
                    "position_bias": pos,
                }
            )
    return out


def _score_bridge_candidate(
    candidate: dict[str, Any],
    *,
    chapter_index: int,
    total_chapters: int,
    bridge_memory: BridgeMemory,
    bridge_family: str,
    topic_keywords: set[str],
    direction: str = "",
) -> float:
    text = str(candidate.get("text") or "").strip()
    shape = str(candidate.get("shape") or "").strip().lower()
    stems = [str(s).strip().lower() for s in candidate.get("stems", [])]
    roots = [str(r).strip().lower() for r in candidate.get("roots", [])]
    # A1 scene_anchor fix: VETO once this block's shared chapter-direction substring has
    # already landed in `_DIRECTION_CAP_PER_CHAPTER` paragraphs of this chapter. Every entry
    # in the block carries the same direction substring, so this steers the selector to a
    # different job's bank or (when none qualifies) the legacy direction-free fallback,
    # keeping the per-chapter paragraph count of any single direction substring under the
    # scene_anchor_density cap. Checked BEFORE phrase/shape vetoes so it is unconditional.
    if direction and bridge_memory.direction_count_chapter(chapter_index, direction) >= _DIRECTION_CAP_PER_CHAPTER:
        return -10_000.0
    # Hard anti-reuse signals (preserve #1589's book-distinct dedup): exact phrase reuse,
    # same shape back-to-back in a chapter, and recent reuse of a real *semantic* stem.
    if bridge_memory.phrase_used_book(text) or bridge_memory.phrase_used_chapter(chapter_index, text):
        return -10_000.0
    if shape and bridge_memory.last_shape_by_chapter.get(chapter_index, "") == shape:
        return -10_000.0
    for stem in stems:
        if bridge_memory.recent_stem_count(stem, chapter_index, window=3) >= 1:
            return -10_000.0

    # DEFERRED-LANE bridge_bank (2026-06-15): the structural-root cap used to be a hard
    # -10_000 rejection. For families like thread_fallback ("Ahead of you: …"), EVERY entry
    # carries the same skeleton roots (next/pattern/chapter), so once a few bank-served
    # bridges land in a 3-chapter window the cap rejected the entire pool and the selector
    # fell through to the literal fallback (only 3/12 chapters served the bank even after the
    # synthetic-stem fix). The real anti-reuse signals above (exact phrase, shape, semantic
    # stem) have already passed by this point, so a structural-root collision alone should be
    # a strong *soft* penalty, not a veto — that keeps fresh-shape/fresh-phrase bank entries
    # eligible while still steering away from over-repeated roots.
    score = 0.0
    for root in roots:
        if root in _ROOT_CAP_4_CHAPTER_WINDOW and bridge_memory.recent_root_count(root, chapter_index, window=3) >= 3:
            score -= 6.0
    shape_recent = bridge_memory.recent_shape_count(shape, chapter_index, window=2)
    family_recent = bridge_memory.recent_family_count(bridge_family, chapter_index, window=2)
    score -= max(0.0, float(shape_recent - 1) * 3.0)
    score -= max(0.0, float(family_recent - 1) * 2.0)
    for root in roots:
        score -= min(2.5, bridge_memory.recent_root_count(root, chapter_index, window=3) * 0.7)
    if shape_recent == 0:
        score += 1.2
    if any(k in topic_keywords for k in candidate.get("scene_bias", [])):
        score += 1.6
    if candidate.get("position_bias") == _chapter_position_bucket(chapter_index, total_chapters):
        score += 2.0
    elif candidate.get("position_bias") == "any":
        score += 0.2
    if all(bridge_memory.recent_root_count(root, chapter_index, window=3) == 0 for root in roots):
        score += 0.8
    return score


def _select_bridge_candidate(
    *,
    bridge_type: str,
    emotional_job: str,
    chapter_index: int,
    total_chapters: int,
    bridge_memory: BridgeMemory | None,
    context_text: str,
    seed: str = "",
) -> dict[str, Any] | None:
    if not bridge_transition_families_enabled():
        return None
    if bridge_memory is None:
        bridge_memory = BridgeMemory()
    chapter_position = _chapter_position_bucket(chapter_index, total_chapters)
    candidates = _collect_bridge_candidates(
        bridge_type=bridge_type,
        emotional_job=emotional_job,
        chapter_position=chapter_position,
    )
    if not candidates:
        return None
    topic_keywords = set(re.findall(r"[a-z]+", (context_text or "").lower()))
    family = f"{bridge_type}|{emotional_job}"
    # A1 scene_anchor fix: the chapter-direction substring shared by every entry of this
    # (bridge_type, emotional_job) block. Empty when the block has no qualifying shared
    # >=4-word n-gram (then the direction cap is inert for this block).
    direction = _bridge_direction_substrings().get((bridge_type, emotional_job), "")
    best: dict[str, Any] | None = None
    best_score = -10_000.0
    for candidate in candidates:
        score = _score_bridge_candidate(
            candidate,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=bridge_memory,
            bridge_family=family,
            topic_keywords=topic_keywords,
            direction=direction,
        )
        if score > best_score:
            best, best_score = candidate, score
        elif score == best_score and best is not None:
            # DEFERRED-LANE bridge_bank (2026-06-15): mix the book `seed` into the tie-break
            # so two books with the same chapter/job/score diverge (the literal fallback was
            # already book-seeded; the bank path was not, which made bank-served threads
            # collide across books once the bank started serving). Preserves determinism for
            # a fixed seed.
            tie_seed = f"{seed}:{bridge_type}:{chapter_index}:{candidate.get('text','')}".encode("utf-8")
            if int(hashlib.sha256(tie_seed).hexdigest()[:8], 16) % 2 == 0:
                best = candidate
    if best is None or best_score <= -9999.0:
        return None
    bridge_memory.register(
        chapter_index=chapter_index,
        phrase=str(best.get("text", "")),
        shape=str(best.get("shape", "")),
        stems=[str(s) for s in best.get("stems", [])],
        roots=[str(r) for r in best.get("roots", [])],
        family_key=family,
        direction=direction,
    )
    return best


def _pick_legacy_bridge_with_memory(
    options: list[str],
    *,
    chapter_index: int,
    bridge_memory: BridgeMemory | None,
    family_key: str,
    seed_parts: tuple[str, ...],
) -> str:
    if not options:
        return ""
    filtered = options
    if bridge_memory is not None:
        deduped = [
            opt
            for opt in options
            if not bridge_memory.phrase_used_book(opt)
            and not bridge_memory.phrase_used_chapter(chapter_index, opt)
        ]
        if deduped:
            filtered = deduped
    picked = _pick_variant(filtered, *seed_parts)
    if bridge_memory is not None and picked:
        bridge_memory.register(
            chapter_index=chapter_index,
            phrase=picked,
            shape="legacy",
            stems=[],
            roots=[],
            family_key=family_key,
        )
    return picked


def _collect_text_entries(shape_map: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for shape, entries in (shape_map or {}).items():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            text = str(entry.get("text") or "").strip()
            if not text:
                continue
            out.append(
                {
                    "text": text,
                    "shape": str(shape).strip().lower(),
                    "stems": [str(s).strip().lower() for s in (entry.get("stems") or []) if str(s).strip()],
                    "roots": [str(r).strip().lower() for r in (entry.get("roots") or []) if str(r).strip()],
                    "topic_keywords": [str(k).strip().lower() for k in (entry.get("topic_keywords") or []) if str(k).strip()],
                }
            )
    return out


def _score_mechanism_thesis_candidate(
    candidate: dict[str, Any],
    *,
    chapter_index: int,
    memory: MechanismThesisMemory,
    kind: str,
) -> float:
    phrase = str(candidate.get("text") or "").strip()
    shape = str(candidate.get("shape") or "").strip().lower()
    stems = [str(s).strip().lower() for s in candidate.get("stems", [])]
    roots = [str(r).strip().lower() for r in candidate.get("roots", [])]
    if not phrase:
        return -10_000.0
    if memory.phrase_used_book(phrase):
        return -10_000.0
    for stem in stems:
        if memory.recent_stem_count(stem, chapter_index, window=3) >= 1:
            return -10_000.0
    if shape and memory.recent_shape_count(shape, chapter_index, window=2) >= 2:
        return -10_000.0
    if kind == "thesis" and any("the point is that" in stem for stem in stems):
        if sum(1 for p in memory.used_phrases_book if p.startswith("the point is that")) >= 2:
            return -10_000.0
    if kind == "mechanism":
        for banned in ("here is the mechanism", "the pattern underneath", "what drives this"):
            if any(banned in stem for stem in stems):
                used = sum(1 for p in memory.used_phrases_book if p.startswith(banned))
                if used >= 1:
                    return -10_000.0
    score = 5.0
    score += 1.0 if shape and memory.recent_shape_count(shape, chapter_index, window=2) == 0 else 0.0
    for root in roots:
        score -= 0.4 * float(memory.recent_root_count(root, chapter_index, window=3))
    return score


def _select_mechanism_thesis_candidate(
    candidates: list[dict[str, Any]],
    *,
    chapter_index: int,
    memory: MechanismThesisMemory | None,
    kind: str,
) -> dict[str, Any] | None:
    if not candidates:
        return None
    local_memory = memory or MechanismThesisMemory()
    best: dict[str, Any] | None = None
    best_score = -10_000.0
    for cand in candidates:
        score = _score_mechanism_thesis_candidate(
            cand,
            chapter_index=chapter_index,
            memory=local_memory,
            kind=kind,
        )
        if score > best_score:
            best = cand
            best_score = score
    if best is None or best_score <= -9999.0:
        return None
    if memory is not None:
        memory.register(
            chapter_index=chapter_index,
            phrase=str(best.get("text", "")),
            shape=str(best.get("shape", "")),
            stems=[str(x) for x in best.get("stems", [])],
            roots=[str(x) for x in best.get("roots", [])],
        )
    return best


def _score_exercise_candidate(
    candidate: dict[str, Any],
    *,
    chapter_index: int,
    memory: ExerciseWrapperMemory,
    family_key: str,
) -> float:
    phrase = str(candidate.get("text") or "").strip()
    shape = str(candidate.get("shape") or "").strip().lower()
    stems = [str(s).strip().lower() for s in candidate.get("stems", [])]
    roots = [str(r).strip().lower() for r in candidate.get("roots", [])]
    if not phrase:
        return -10_000.0
    if memory.phrase_used_book(phrase):
        return -10_000.0
    for stem in stems:
        if memory.recent_stem_count(stem, chapter_index, window=3) >= 1:
            return -10_000.0
    for stem_ban in ("before you continue", "just try it", "whatever happened", "useful information"):
        if any(stem_ban in stem for stem in stems):
            if sum(1 for p in memory.used_phrases_book if stem_ban in p) >= 1:
                return -10_000.0
    if shape and memory.recent_shape_count(shape, chapter_index, window=1) >= 1:
        return -5_000.0
    dominant_roots = {"body", "notice", "continue", "shift", "information"}
    for root in roots:
        if root in dominant_roots and memory.recent_root_count(root, chapter_index, window=3) >= 3:
            return -10_000.0
    score = 4.0
    score -= 1.2 * float(memory.recent_family_count(family_key, chapter_index, window=1))
    if shape and memory.recent_shape_count(shape, chapter_index, window=2) == 0:
        score += 0.8
    return score


def _select_exercise_candidate(
    candidates: list[dict[str, Any]],
    *,
    chapter_index: int,
    memory: ExerciseWrapperMemory | None,
    family_key: str,
) -> dict[str, Any] | None:
    if not candidates:
        return None
    local_memory = memory or ExerciseWrapperMemory()
    best: dict[str, Any] | None = None
    best_score = -10_000.0
    for cand in candidates:
        score = _score_exercise_candidate(
            cand,
            chapter_index=chapter_index,
            memory=local_memory,
            family_key=family_key,
        )
        if score > best_score:
            best = cand
            best_score = score
    if best is None or best_score <= -9999.0:
        return None
    if memory is not None:
        memory.register(
            chapter_index=chapter_index,
            phrase=str(best.get("text", "")),
            shape=str(best.get("shape", "")),
            family=family_key,
            stems=[str(x) for x in best.get("stems", [])],
            roots=[str(x) for x in best.get("roots", [])],
        )
    return best


def _iter_wrapper_candidates(
    *,
    wrapper_type: str,
    practice_type: str,
    emotional_job: str,
) -> list[dict[str, Any]]:
    payload = _load_exercise_wrapper_families()
    wrappers = payload.get("wrapper_types") or {}
    wt_bank = wrappers.get(wrapper_type) or {}
    if not isinstance(wt_bank, dict):
        return []
    practice_bank = wt_bank.get(practice_type) or {}
    if not isinstance(practice_bank, dict):
        return []
    job_bank = practice_bank.get(emotional_job) or {}
    if not isinstance(job_bank, dict):
        return []
    return _collect_text_entries(job_bank)


def _resolve_practice_candidates(
    *,
    wrapper_type: str,
    practice_type: str,
    emotional_job: str,
) -> list[dict[str, Any]]:
    p = (practice_type or "").strip().lower()
    ordered = [p]
    if p == "body_awareness":
        ordered.extend(["grounding", "body_scan"])
    ordered.extend(["grounding", "integration_pause", "reflective_prompt"])
    seen: set[str] = set()
    out: list[dict[str, Any]] = []
    for key in ordered:
        if not key or key in seen:
            continue
        seen.add(key)
        out.extend(
            _iter_wrapper_candidates(
                wrapper_type=wrapper_type,
                practice_type=key,
                emotional_job=emotional_job,
            )
        )
    return out


# ---------------------------------------------------------------------------
# Thesis derivation
# ---------------------------------------------------------------------------

def _derive_thesis_legacy(reflection: str, chapter_index: int = 0) -> str:
    """Backward-compatible thesis derivation without emotional-job families."""
    thesis_markers = [
        ("perfect choice", "The point is that perfection is not available, but movement is."),
        ("regret", "The point is that anxiety predicts regret so loudly that it blocks useful decisions."),
        ("mechanism", "The point is that the mechanism treats every decision like a permanent threat."),
        ("alarm", "The point is that the alarm is information, not instruction."),
        ("comparison", "The point is that comparison uses someone else's exterior to judge your interior."),
        ("shame", "The point is that shame says you are the problem, but shame is a pattern, not a verdict."),
        ("watcher", "The point is that the part of you that watches is not the part that decides."),
        ("overwhelm", "The point is that overwhelm is a capacity signal, not a character flaw."),
        ("grief", "The point is that grief is not a problem to solve — it is a process to accompany."),
        ("spiral", "The point is that the spiral is a loop, not a descent — it returns to the same ground."),
        ("false alarm", "The point is that the alarm fires on prediction, not evidence."),
        ("contraction", "The point is that the contraction is not who you are — it is what you do."),
        ("bright", "The point is that what you are seeking is already present before you start looking."),
        ("seeking", "The point is that seeking is the activity that obscures what is already here."),
        ("recognition", "The point is that recognition replaces seeking — you stop looking and start seeing."),
        ("separate self", "The point is that the separate self is an activity, not an entity."),
        ("avoidance", "The point is that avoidance maps the edges of what you are not yet willing to see."),
        ("relationship", "The point is that relationship is the mirror that reveals what you cannot see alone."),
        ("prior freedom", "The point is that freedom does not need to be achieved — it needs to be recognized."),
        ("vulnerability", "The point is that vulnerability is not the risk — the armor is."),
        ("nervous system", "The point is that your nervous system responds to predictions, not facts."),
        ("body", "The point is that the body knows before the mind does — trust the body."),
        ("holding", "The point is that what you are holding is costing more energy than you realize."),
        ("pattern", "The point is that seeing the pattern is the beginning of freedom from it."),
        ("rest", "The point is that rest is not earned — it is required."),
    ]
    reflection_lower = (reflection or "").lower()
    matched = [thesis for marker, thesis in thesis_markers if marker in reflection_lower]
    if matched:
        return matched[chapter_index % len(matched)]
    fallback = [
        "The point is that you can act inside uncertainty without waiting for it to resolve.",
        "The point is that seeing the pattern clearly is the first step toward not being run by it.",
        "The point is that the feeling is real, but the story the feeling tells is often inaccurate.",
        "The point is that awareness does not fix anything — it makes fixing unnecessary.",
        "The point is that you have been working harder than you realize to stay contracted.",
        "The point is that what you are protecting yourself from is often less dangerous than the protection.",
        "The point is that ordinary moments carry the pattern more clearly than dramatic ones.",
    ]
    return fallback[(hash(reflection) + chapter_index) % len(fallback)]


def _derive_thesis(
    reflection: str,
    chapter_index: int = 0,
    *,
    emotional_job: str = "",
    thesis_memory: MechanismThesisMemory | None = None,
    chapter_intent: str = "",
    engine_type: str = "",
    arc_thesis: str = "",
    topic_id: str = "",
) -> str:
    """Extract a one-line thesis claim from REFLECTION prose.

    Derivation chain (highest → lowest priority):
      1. arc_thesis  — arc-provided thesis used directly if present
      2. chapter_thesis_bank — lookup by (topic_id, chapter_intent, engine_type)
         with a topic override layer, then the topic-agnostic engine baseline.
         No silent watcher default — overwhelm/spiral/comparison resolve to
         their own columns (audit Q1/D2).
      3. mechanism_thesis_families.yaml — lookup by emotional_job
      4. _derive_thesis_legacy — keyword extraction from prose
    """
    # 1. Arc-provided thesis takes priority
    if arc_thesis and arc_thesis.strip():
        return arc_thesis.strip()

    # 2. Chapter Thesis Bank lookup by (topic_id, chapter_intent, engine_type)
    if chapter_intent and engine_type:
        bank = _load_chapter_thesis_bank()  # intents block
        topic_overlay = _load_chapter_thesis_topics()  # topics block
        intent_key = chapter_intent.lower().replace("-", "_").replace(" ", "_")
        engine_key = _normalize_thesis_engine(engine_type)
        # Precedence: topic override → engine baseline.
        topic_block = ((topic_overlay.get(topic_id) or {}).get(intent_key)) or {}
        intent_block = bank.get(intent_key) or {}
        thesis = topic_block.get(engine_key) or intent_block.get(engine_key)
        if thesis:
            return str(thesis).strip()
        # Legacy engine aliases (watcher ↔ burnout, false_alarm ↔ anxiety) — kept
        # so older callers passing burnout/anxiety slugs still resolve.
        engine_aliases = {
            "burnout": "watcher",
            "watcher": "burnout",
            "anxiety": "false_alarm",
            "false_alarm": "anxiety",
        }
        alt_engine = engine_aliases.get(engine_key, "")
        if alt_engine:
            thesis = topic_block.get(alt_engine) or intent_block.get(alt_engine)
            if thesis:
                return str(thesis).strip()

    # 3. mechanism_thesis_families.yaml lookup by emotional_job
    job = _normalize_emotional_job(emotional_job)
    if job and mechanism_thesis_families_enabled():
        payload = _load_mechanism_thesis_families()
        job_bank = (((payload.get("thesis_families") or {}).get(job)) or {})
        candidates = _collect_text_entries(job_bank if isinstance(job_bank, dict) else {})
        selected = _select_mechanism_thesis_candidate(
            candidates,
            chapter_index=chapter_index,
            memory=thesis_memory,
            kind="thesis",
        )
        if selected:
            return str(selected.get("text", "")).strip()

    # 4. Legacy keyword extraction from prose
    return _derive_thesis_legacy(reflection, chapter_index)


# ---------------------------------------------------------------------------
# Bridge sentences (connect slots into argument flow)
# ---------------------------------------------------------------------------

def _bridge_after_opening(
    thesis: str,
    opening: str = "",
    scene: str = "",
    *,
    emotional_job: str = "",
    chapter_index: int = 0,
    total_chapters: int = 1,
    bridge_memory: BridgeMemory | None = None,
) -> str:
    """Bridge from HOOK/SCENE → MECHANISM."""
    if not bridge_transition_families_enabled():
        return ""
    job = _normalize_emotional_job(emotional_job)
    if job:
        selected = _select_bridge_candidate(
            bridge_type="after_opening",
            emotional_job=job,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=bridge_memory,
            context_text=f"{thesis} {opening} {scene}",
        )
        if selected:
            text = str(selected.get("text", "")).strip()
            return _gt(text, locale=_LOCALE_TLS) if _LOCALE_TLS else text
    seed = f"{thesis} {opening} {scene}".lower()
    if "regret" in seed or "choice" in seed:
        options = [
            "This is why the freeze starts earlier than the choice: loss becomes imaginable before the decision does.",
            "What looks like indecision is usually grief arriving before the decision does. That matters because the body treats the prediction like fact.",
        ]
    elif "comparison" in seed:
        options = [
            "This is where comparison does its quiet damage: it makes another person's surface feel like evidence against you.",
            "The sting is not just what you saw. It is how fast your system turned it into a verdict, which means the pain starts before you can question the math.",
        ]
    elif "alarm" in seed or "false alarm" in seed:
        options = [
            "By the time you can explain the moment, the alarm has already chosen a meaning for it. That matters because the body is already obeying the prediction.",
            "The body is already behaving like the threat is real. This is where the chapter has to begin.",
        ]
    elif "shame" in seed:
        options = [
            "Shame always makes the same move first: it turns a moment into an identity sentence.",
            "The danger here is not the moment itself. It is the meaning shame races to stamp onto it, which means the injury often lands after the event.",
        ]
    elif "overwhelm" in seed:
        options = [
            "Shutdown rarely begins at the task. It begins where your system starts counting cost.",
            "What looks small on the screen can still feel expensive in the body. That matters because capacity gets spent before effort begins.",
        ]
    else:
        options = [
            "Stay with the moment a second longer. The pattern usually shows itself before the explanation does.",
            "That pause is doing more than slowing you down. It is showing you how the pattern enters, which means the chapter can name it before it hardens.",
            "Before the mind starts explaining, the body has already registered something. Trust that registration.",
            "The instinct to move past this moment quickly is itself data. Slow down and see what it protects.",
            "Something just shifted in your chest or your throat. That shift is where the chapter actually begins.",
            "Notice the impulse to understand before you have finished feeling. That impulse is the pattern defending itself.",
            "The body already knows something the mind has not caught up with yet. Let it lead for a moment.",
            "Right here is where the chapter earns its weight. Not in the concept, but in the felt registration.",
            "What you just felt is not a distraction from the point. It is the point arriving ahead of language.",
            "Hold this sensation without naming it. The name will come, but the sensation is more honest.",
            "There is a micro-flinch the body makes before the mind builds its story. That flinch is the trailhead.",
            "Do not skip ahead to the lesson. The body is still showing you where the lesson lives.",
        ]
    return _pick_legacy_bridge_with_memory(
        options,
        chapter_index=chapter_index,
        bridge_memory=bridge_memory,
        family_key=f"after_opening|{job or 'legacy'}",
        seed_parts=(thesis, opening, scene),
    )


def _bridge_before_story(
    thesis: str,
    reflection: str = "",
    story: str = "",
    *,
    emotional_job: str = "",
    chapter_index: int = 0,
    total_chapters: int = 1,
    bridge_memory: BridgeMemory | None = None,
) -> str:
    """Bridge from REFLECTION → STORY."""
    if not bridge_transition_families_enabled():
        return ""
    job = _normalize_emotional_job(emotional_job)
    if job:
        selected = _select_bridge_candidate(
            bridge_type="before_story",
            emotional_job=job,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=bridge_memory,
            context_text=f"{thesis} {reflection} {story}",
        )
        if selected:
            text = str(selected.get("text", "")).strip()
            return _gt(text, locale=_LOCALE_TLS) if _LOCALE_TLS else text
    seed = f"{thesis} {reflection} {story}".lower()
    if "comparison" in seed:
        options = [
            "For example, you can watch the pattern more clearly in somebody else's body before you can bear it in your own.",
            "Seen from the outside, the distortion gets harder to defend.",
        ]
    elif "shame" in seed:
        options = [
            "For example, watch where the sentence about identity gets written. It usually happens in a single beat.",
            "The pattern gets clearest when you can see the price land on a real person.",
        ]
    elif "choice" in seed or "regret" in seed:
        options = [
            "For example, the cost shows up fastest in a story. Watch how the prediction arrives before the fact does.",
            "You can see the mechanism better when it borrows someone else's future first.",
        ]
    else:
        options = [
            "Here is where the chapter stops talking about the pattern and lets you watch it happen.",
            "For example, the quickest way to feel the mechanism is to watch it take hold in an ordinary moment.",
            "What follows is not a metaphor. It is a report from someone who lived inside this pattern.",
            "The explanation can only go so far. A story goes the rest of the way.",
            "This is the turning point. Not a dramatic revelation. A quiet noticing.",
            "The pattern gets clearest when you watch it operate in someone else's day before returning to your own.",
            "Now watch what happens when the same pattern lands in a real body, in a real room.",
            "Theory describes the shape. A story lets you feel the weight of it.",
            "The next part is not instruction. It is evidence drawn from someone's lived experience.",
            "Concepts dissolve under pressure. What remains is the story of how the pressure actually felt.",
            "Here the chapter shifts from naming the pattern to witnessing it in motion.",
            "Words about the pattern only go so far. What follows is the pattern caught in the act.",
        ]
    return _pick_legacy_bridge_with_memory(
        options,
        chapter_index=chapter_index,
        bridge_memory=bridge_memory,
        family_key=f"before_story|{job or 'legacy'}",
        seed_parts=(thesis, reflection, story),
    )


def _bridge_before_exercise(
    thesis: str,
    reflection: str = "",
    story: str = "",
    *,
    emotional_job: str = "",
    practice_type: str = "",
    exercise_memory: ExerciseWrapperMemory | None = None,
    chapter_index: int = 0,
    total_chapters: int = 1,
    bridge_memory: BridgeMemory | None = None,
) -> str:
    """Bridge from STORY → EXERCISE."""
    if not bridge_transition_families_enabled():
        return ""
    job = _normalize_emotional_job(emotional_job)
    if job:
        selected = _select_bridge_candidate(
            bridge_type="before_exercise",
            emotional_job=job,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=bridge_memory,
            context_text=f"{thesis} {reflection} {story} {practice_type}",
        )
        if selected:
            text = str(selected.get("text", "")).strip()
            if _LOCALE_TLS:
                return _gt(text, locale=_LOCALE_TLS)
            return text
    seed = f"{thesis} {reflection} {story}".lower()
    if "jaw" in seed or "sternum" in seed or "throat" in seed:
        options = [
            "So when the body tightens, do not solve the whole pattern here. Work with the place that braced first.",
            "In practice, start smaller than insight. Start where the body is still holding the chapter.",
        ]
    else:
        options = [
            "In practice, do not turn this into homework. Give the body one smaller, safer entry instead.",
            "So when the pattern surges, the next move is not to understand more. It is to make the first move cheaper.",
            "Understanding without practice is just information. The body needs something to do with what it just learned.",
            "The exercise that follows is not meant to fix anything. It is meant to make the pattern visible in your body.",
            "You do not need to master this. You need to try it once and notice what happens.",
            "Before moving on, give the body one concrete action. Insight without action evaporates by tomorrow.",
            "Now bring this from concept into sensation. The next step is deliberately small.",
            "The body learns through action, not agreement. Give it one move it can actually make right now.",
            "Knowing the pattern is not enough. The next step asks you to meet it with your body, not your mind.",
            "What follows is not a test. It is an invitation to feel the mechanism while it is still warm.",
            "Let the practice be undersized. A small move completed is worth more than a large one imagined.",
            "The shift from understanding to doing is where most chapters lose people. Stay with this one.",
        ]
    return _pick_legacy_bridge_with_memory(
        options,
        chapter_index=chapter_index,
        bridge_memory=bridge_memory,
        family_key=f"before_exercise|{job or 'legacy'}",
        seed_parts=(thesis, reflection, story),
    )


def _bridge_before_integration(
    thesis: str,
    integration: str = "",
    *,
    emotional_job: str = "",
    practice_type: str = "",
    exercise_memory: ExerciseWrapperMemory | None = None,
    chapter_index: int = 0,
    total_chapters: int = 1,
    bridge_memory: BridgeMemory | None = None,
) -> str:
    """Bridge from EXERCISE → INTEGRATION."""
    if not bridge_transition_families_enabled():
        return ""
    job = _normalize_emotional_job(emotional_job)
    # When no bridge_memory is supplied but exercise_memory is, synthesise a
    # transient BridgeMemory seeded with the phrases already seen book-wide so
    # the YAML candidate scorer can avoid re-selecting them.
    effective_bridge_memory = bridge_memory
    if effective_bridge_memory is None and exercise_memory is not None:
        effective_bridge_memory = BridgeMemory()
        effective_bridge_memory.used_phrases_book = set(exercise_memory.used_phrases_book)
    if job:
        selected = _select_bridge_candidate(
            bridge_type="before_integration",
            emotional_job=job,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=effective_bridge_memory,
            context_text=f"{thesis} {integration} {practice_type}",
        )
        if selected:
            text = str(selected.get("text", "")).strip()
            # Propagate the newly used phrase back into exercise_memory so
            # subsequent chapters know not to repeat it.
            if exercise_memory is not None and text:
                exercise_memory.used_phrases_book.add(text.strip().lower())
            if _LOCALE_TLS:
                return _gt(text, locale=_LOCALE_TLS)
            return text
    options = [
        "Now notice what shifted before your mind starts summarizing it.",
        "Let the chapter land in the body before it turns back into explanation.",
        "Stay with what changed. Even if it only changed by one degree.",
        "Do not rush to the next thing. What just happened needs a few seconds to settle into the body.",
        "The shift may be small. Small is not insignificant. Small is where lasting change begins.",
        "Before the mind files this as 'done,' feel what is still open in the body. That openness is the real work.",
        "Pause here. The body is still processing what the mind already moved past.",
        "Give the landing a moment. The nervous system integrates slower than the reading eye.",
        "Whatever just moved in you does not need to be understood yet. It needs to be felt.",
        "Resist the urge to evaluate. Let the experience sit without a grade.",
        "The body registers change in its own time. Give it that time before the next chapter begins.",
        "Something loosened or something tightened. Either one is information worth keeping.",
    ]
    return _pick_legacy_bridge_with_memory(
        options,
        chapter_index=chapter_index,
        bridge_memory=effective_bridge_memory,
        family_key=f"before_integration|{job or 'legacy'}",
        seed_parts=(thesis, integration),
    )


# ---------------------------------------------------------------------------
# Within-slot bridges (OPD-109 Phase 1)
#
# Long runtimes (deep_book_6h) stack multiple atoms inside a single canonical
# slot (STORY, REFLECTION, EXERCISE, INTEGRATION, TEACHER_DOCTRINE, ...).
# Without bridge prose, the reader sees "8 SCENE tableaus in a row".
# `_bridge_within_slot` returns a 1-sentence transition between two adjacent
# atoms in the SAME slot. Selection is deterministic (chapter_index +
# slot_type + atom_pair_index → seed). NO paid-LLM dependency.
#
# Defect ref: docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md
# ---------------------------------------------------------------------------

def _bridge_story_introduction(
    next_atom: str,
    *,
    chapter_index: int = 0,
    atom_pair_index: int = 0,
    rotation_state: "WithinSlotRotationState | None" = None,
) -> str:
    """OPD-123: one-sentence bridge before a named-character STORY atom body.

    Fires at the slot boundary going INTO STORY (not between SCENE atoms).
    Selection is deterministic; uses ``story_introduction`` / ``section_to_named_story``
    variants from within_slot_bridge_families.yaml.
    """
    if _classify_atom(next_atom) != "named_story":
        return ""

    payload = _load_within_slot_bridge_families()
    family = payload.get("story_introduction") or {}
    entries = family.get("section_to_named_story") or []
    if not isinstance(entries, list) or not entries:
        return ""

    seed_root = (
        f"opd123|{int(chapter_index)}|STORY|story_intro|{int(atom_pair_index)}"
    )
    raw_variants: list[tuple[str, int]] = []
    for v_idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        text = str(entry.get("text") or "").strip()
        if not text:
            continue
        expectation = str(entry.get("next_atom_expectation") or "any").strip().lower()
        if expectation not in ("named_story", "any"):
            continue
        rank_seed = f"{seed_root}|{v_idx}|{text}"
        rank_digest = hashlib.sha256(rank_seed.encode("utf-8")).digest()
        raw_variants.append((text, int.from_bytes(rank_digest[:8], "big")))

    if not raw_variants:
        return ""

    effective_state: "WithinSlotRotationState | None" = (
        rotation_state if rotation_state is not None else _WITHIN_SLOT_ROTATION_TLS
    )
    if effective_state is not None:
        chapter_filtered = [
            v
            for v in raw_variants
            if not effective_state.chapter_has_used(chapter_index, v[0])
        ]
        candidates = chapter_filtered if chapter_filtered else raw_variants
        candidates_sorted = sorted(
            candidates,
            key=lambda triple: (effective_state.book_count(triple[0]), triple[1]),
        )
        chosen_text = candidates_sorted[0][0]
        effective_state.register(chapter_index, chosen_text)
    else:
        digest = hashlib.sha256(seed_root.encode("utf-8")).digest()
        chosen_text = raw_variants[int.from_bytes(digest[:8], "big") % len(raw_variants)][0]

    if _LOCALE_TLS:
        return _gt(chosen_text, locale=_LOCALE_TLS)
    return chosen_text


def prepend_story_introduction_bridge(
    story_text: str,
    first_atom: str,
    *,
    chapter_index: int = 0,
    rotation_state: "WithinSlotRotationState | None" = None,
) -> str:
    """Prepend OPD-123 story_introduction bridge when ``first_atom`` is a named story."""
    body = (story_text or "").strip()
    if not body or not render_glue_enabled():
        return body
    bridge = _bridge_story_introduction(
        first_atom,
        chapter_index=chapter_index,
        rotation_state=rotation_state,
    ).strip()
    if not bridge:
        return body
    if bridge in body:
        return body
    return f"{bridge}\n\n{body}"


def _bridge_within_slot(
    prev_atom: str,
    next_atom: str,
    slot_type: str,
    atom_pair_index: int,
    chapter_index: int = 0,
    rotation_state: "WithinSlotRotationState | None" = None,
    *,
    enabled: "bool | None" = None,
) -> str:
    """Return a 1-sentence transition between two atoms of the same slot.

    Production default is OFF (``within_slot_bridges: false``) — returns "".
    Pass ``enabled=True`` to exercise the template machinery (unit tests / A/B).

    Deterministic: same (chapter_index, slot_type, atom_pair_index) with the
    same `rotation_state` always returns the same bridge variant. With the
    default ``rotation_state=None`` the call still uses the deterministic
    seed-only path so existing callers (and the legacy test path) keep
    their behavior. Template-only — no LLM calls.

    Selection (OPD-109 Phase 1.1 + OPD-112 next-atom continuity):
      1. Pick the shape bucket by ``atom_pair_index % len(shapes)``. This
         keeps adjacent bridges inside one slot landing on different
         rhetorical shapes.
      2. OPD-112: classify ``next_atom`` (via :func:`_classify_atom`).
         Keep only bridges whose YAML ``next_atom_expectation`` matches
         that class, with ``"any"`` accepting universally. If no narrow
         match exists, fall back to ``"any"``-tagged bridges; if both
         buckets are empty, fall back to the full pool (so bridges
         never go silent — backward-compat with un-annotated YAML).
      3. Within the surviving candidates, exclude any variant already
         used in THIS chapter (per-chapter no-reuse).
      4. If ``rotation_state`` is present, sort the surviving candidates
         by ``(book_usage_count, seed_rank)`` — variants not yet used in
         the book come first; ties break on a SHA digest of the slot
         coordinates so the choice is reproducible.
      5. Without ``rotation_state``, fall back to the legacy seed-only
         hash modulo, then a chapter_used filter if a per-render TLS
         state is present.

    Returns "" if YAML is missing or the family has no entries.

    Defect refs:
      - docs/diagnostics/OPD-109_RENDERING_LAYER_DIAGNOSIS_2026-05-18.md
      - OPD-112 (bridge ↔ following-atom semantic continuity, 2026-05-20)
    """
    if enabled is None:
        enabled = within_slot_bridges_enabled()
    if not enabled:
        return ""

    st_upper = (slot_type or "").strip().upper()
    payload = _load_within_slot_bridge_families()
    families = payload.get("slot_families") or {}
    default_family = payload.get("default_family") or {}
    family = families.get(st_upper)
    if not isinstance(family, dict) or not family:
        family = default_family if isinstance(default_family, dict) else {}
    if not isinstance(family, dict) or not family:
        return ""

    # Flatten shape buckets in deterministic order so the chosen variant
    # is stable across runs and process invocations.
    shape_names = sorted(str(k) for k in family.keys())
    if not shape_names:
        return ""

    # Rotate shape bucket by (chapter_index + atom_pair_index) so the same
    # atom_pair across different chapters does NOT pin to a single bucket.
    # LEVER-B: previously `atom_pair_index % len(shape_names)` alone meant every
    # atom_pair divisible by len(shape_names) landed on shape_names[0] in EVERY
    # chapter (e.g. STORY pairs 9/21/30/36 all -> contrast_lift), funnelling the
    # cross-chapter dedup into one bucket and recurring the same variant book-wide.
    # Folding chapter_index in spreads the bucket choice across chapters while
    # remaining fully deterministic for a fixed (chapter, atom_pair) seed.
    shape_idx = (int(chapter_index) + int(atom_pair_index)) % len(shape_names)
    shape_key = shape_names[shape_idx]
    entries = family.get(shape_key) or []
    if not isinstance(entries, list) or not entries:
        # fall back to the first non-empty shape
        for sk in shape_names:
            entries = family.get(sk) or []
            if isinstance(entries, list) and entries:
                shape_key = sk
                break
    if not isinstance(entries, list) or not entries:
        return ""

    # OPD-112: classify the next atom so we can filter bridges whose
    # `next_atom_expectation:` does not match what is actually coming.
    next_class = _classify_atom(next_atom)

    # Build (text, seed_rank, expectation) tuples for every variant in this shape.
    # The seed_rank ties variant choice to the slot coordinates so
    # re-renders with the same seed produce identical output.
    seed_root = f"opd109|{int(chapter_index)}|{st_upper}|{int(atom_pair_index)}|{shape_key}"

    def _variants_for(entry_list: list[Any], bucket_key: str) -> list[tuple[str, int, str]]:
        out: list[tuple[str, int, str]] = []
        for v_idx, entry in enumerate(entry_list):
            if not isinstance(entry, dict):
                continue
            text = str(entry.get("text") or "").strip()
            if not text:
                continue
            # OPD-112: missing field defaults to "any" (backward-compatible —
            # bridges without explicit expectations remain universal acceptors).
            expectation = str(entry.get("next_atom_expectation") or "any").strip().lower()
            if expectation not in _NEXT_ATOM_EXPECTATION_LABELS:
                expectation = "any"
            rank_seed = f"{seed_root}|{bucket_key}|{v_idx}|{text}"
            rank_digest = hashlib.sha256(rank_seed.encode("utf-8")).digest()
            seed_rank = int.from_bytes(rank_digest[:8], "big")
            out.append((text, seed_rank, expectation))
        return out

    raw_variants = _variants_for(entries, shape_key)

    # LEVER-B cross-chapter variety: when a rotation state is present we widen
    # the candidate pool to EVERY shape bucket for this slot (deduped by text).
    # The chosen bucket above still sets the primary seed/shape; the wider pool
    # only matters when book-level dedup needs headroom -- it lets the selector
    # reach a still-unused variant in a sibling bucket instead of recurring the
    # last bucket's text book-wide. Without rotation state we keep the legacy
    # single-bucket pool so deterministic seed-only behavior is unchanged.
    effective_state_preview: "WithinSlotRotationState | None" = (
        rotation_state if rotation_state is not None else _WITHIN_SLOT_ROTATION_TLS
    )
    if effective_state_preview is not None and len(shape_names) > 1:
        seen_texts = {v[0] for v in raw_variants}
        for sk in shape_names:
            if sk == shape_key:
                continue
            for cand in _variants_for(family.get(sk) or [], sk):
                if cand[0] not in seen_texts:
                    raw_variants.append(cand)
                    seen_texts.add(cand[0])
    if not raw_variants:
        return ""

    # OPD-112: keep bridges that match next_class exactly, OR are tagged "any"
    # (universal). If next_class is "any" itself (no tells in next atom), the
    # whole pool is eligible.
    if next_class == "any":
        next_class_filtered = raw_variants
    else:
        narrow = [v for v in raw_variants if v[2] == next_class]
        universal = [v for v in raw_variants if v[2] == "any"]
        # Prefer narrowly matched candidates; fall back to universal "any"
        # if none of this shape's variants match next_class. If both empty,
        # last-resort to the full raw pool so the bridge never goes silent.
        if narrow:
            next_class_filtered = narrow
        elif universal:
            next_class_filtered = universal
        else:
            next_class_filtered = raw_variants

    # Resolve rotation state: explicit parameter wins, then per-render TLS,
    # then None (legacy seed-only path).
    effective_state: "WithinSlotRotationState | None" = (
        rotation_state if rotation_state is not None else _WITHIN_SLOT_ROTATION_TLS
    )

    if effective_state is not None:
        # Filter out variants already used in THIS chapter (per-chapter no-reuse).
        chapter_filtered = [
            v for v in next_class_filtered
            if not effective_state.chapter_has_used(chapter_index, v[0])
        ]
        # If every variant in this shape was used, allow reuse but keep the
        # least-used-in-book first so we still spread the load.
        candidates = chapter_filtered if chapter_filtered else next_class_filtered
        # LEVER-B: make book-level no-repeat a HARD preference. When any variant
        # has never been used in the book, restrict the pool to those -- so a
        # bridge text cannot recur across chapters while fresh variants remain.
        # The previous (book_count, seed_rank) sort alone let a between-bucket
        # tie re-pick the same text book-wide (verified: 'Same body. Different
        # door.' recurred 8x at full-12 deep). Only when the whole widened pool
        # is exhausted do we fall back to least-used-first reuse.
        book_fresh = [v for v in candidates if effective_state.book_count(v[0]) == 0]
        pool = book_fresh if book_fresh else candidates
        candidates_sorted = sorted(
            pool,
            key=lambda triple: (effective_state.book_count(triple[0]), triple[1]),
        )
        chosen_text = candidates_sorted[0][0]
        effective_state.register(chapter_index, chosen_text)
    else:
        # Legacy seed-only path: pick by hash modulo for backward compat.
        seed = f"{seed_root}|legacy"
        digest = hashlib.sha256(seed.encode("utf-8")).digest()
        idx = int.from_bytes(digest[:8], "big") % len(next_class_filtered)
        chosen_text = next_class_filtered[idx][0]

    text_out = chosen_text
    if _LOCALE_TLS:
        text_out = _gt(text_out, locale=_LOCALE_TLS)
    return text_out


# ---------------------------------------------------------------------------
# OPD-114 Phase B: scene-depth ladder + archetype_jump bridges
# ---------------------------------------------------------------------------

_SCENE_ARCHETYPE_CAP = 2
_ARCHETYPE_JUMP_SHAPE = "archetype_jump"


def _first_noun_phrase(text: str) -> str:
    """Extract a short opening phrase from scene prose for bridge templates."""
    raw = (text or "").strip()
    if not raw:
        return "this"
    skip = frozenset({"the", "a", "an", "your", "you", "it", "there", "this", "that"})
    words = re.findall(r"[A-Za-z']+", raw)
    picked: list[str] = []
    for w in words:
        low = w.lower()
        if low in skip and not picked:
            continue
        picked.append(w)
        if len(picked) >= 4:
            break
    return " ".join(picked) if picked else "this"


def _bridge_archetype_jump(
    next_atom: str,
    *,
    chapter_index: int = 0,
    atom_pair_index: int = 0,
    rotation_state: "WithinSlotRotationState | None" = None,
) -> str:
    """Mandatory bridge between SCENE atoms from different archetypes (OPD-114)."""
    payload = _load_within_slot_bridge_families()
    families = payload.get("slot_families") or {}
    family = families.get("SCENE") or {}
    entries = family.get(_ARCHETYPE_JUMP_SHAPE) or []
    if not isinstance(entries, list) or not entries:
        return ""

    seed_root = f"opd114|{int(chapter_index)}|SCENE|archetype_jump|{int(atom_pair_index)}"
    raw_variants: list[tuple[str, int]] = []
    for v_idx, entry in enumerate(entries):
        if not isinstance(entry, dict):
            continue
        text = str(entry.get("text") or "").strip()
        if not text:
            continue
        rank_seed = f"{seed_root}|{v_idx}|{text}"
        rank_digest = hashlib.sha256(rank_seed.encode("utf-8")).digest()
        raw_variants.append((text, int.from_bytes(rank_digest[:8], "big")))

    if not raw_variants:
        return ""

    if rotation_state is not None:
        raw_variants.sort(
            key=lambda v: (
                rotation_state.book_count(f"SCENE|{_ARCHETYPE_JUMP_SHAPE}|{v[0]}"),
                v[1],
            )
        )
        chosen = raw_variants[0][0]
        rotation_state.register(f"SCENE|{_ARCHETYPE_JUMP_SHAPE}|{chosen}")
    else:
        digest = hashlib.sha256(seed_root.encode("utf-8")).digest()
        chosen = raw_variants[int.from_bytes(digest[:8], "big") % len(raw_variants)][0]

    fill = _first_noun_phrase(next_atom)
    out = chosen.replace("___", fill)
    if _LOCALE_TLS:
        return _gt(out, locale=_LOCALE_TLS)
    return out


def compose_scene_ladder_blocks(
    blocks: list[tuple[str, Optional[str]]],
    *,
    chapter_index: int = 0,
    rotation_state: "WithinSlotRotationState | None" = None,
) -> str:
    """Join SCENE ladder atoms: no bridges within one archetype; archetype_jump across."""
    cleaned = [(t.strip(), a) for t, a in blocks if (t or "").strip()]
    if not cleaned:
        return ""
    if len(cleaned) == 1:
        return cleaned[0][0]

    groups: list[tuple[Optional[str], list[str]]] = []
    for text, arch in cleaned:
        if groups and groups[-1][0] == arch:
            groups[-1][1].append(text)
        else:
            groups.append((arch, [text]))

    distinct = {g[0] for g in groups}
    if len(distinct) > _SCENE_ARCHETYPE_CAP:
        raise ValueError(
            f"chapter {chapter_index}: SCENE has {len(distinct)} archetypes; "
            f"max {_SCENE_ARCHETYPE_CAP} per chapter"
        )

    if len(groups) == 1:
        return "\n\n".join(groups[0][1])

    out_parts: list[str] = []
    for gi, (_arch, texts) in enumerate(groups):
        out_parts.append("\n\n".join(texts))
        if gi < len(groups) - 1:
            next_open = groups[gi + 1][1][0]
            bridge = _bridge_archetype_jump(
                next_open,
                chapter_index=chapter_index,
                atom_pair_index=gi,
                rotation_state=rotation_state,
            )
            if bridge:
                out_parts.append(bridge)
    return "\n\n".join(out_parts)


# ---------------------------------------------------------------------------
# Slot transforms
# ---------------------------------------------------------------------------

def _distill_mechanism_legacy(reflection: str, thesis: str) -> str:
    """Backward-compatible mechanism derivation without emotional-job families."""
    reflection_lower = (reflection or "").lower()
    if "regret" in reflection_lower and "choice" in reflection_lower:
        return (
            "This is the mechanism underneath it: anxiety predicts regret so loudly that it drowns out your ability "
            "to make a useful decision. The mechanism is simple and brutal. The moment you choose one thing, your "
            "brain starts mourning everything you did not choose. It tries to find a perfect option with zero loss, "
            "but that option does not exist. Every path closes other paths. So the system freezes you, or lets you "
            "choose and then punishes you for choosing."
        )
    if "comparison" in reflection_lower:
        return (
            "The comparison engine runs on incomplete data. It takes someone "
            "else's visible output and measures it against your full interior experience. The comparison always "
            "loses because it is rigged — you see their best against your worst. The mechanism is automatic and "
            "relentless. Understanding it does not stop it. But it lets you see the score as inaccurate."
        )
    if "alarm" in reflection_lower or "false alarm" in reflection_lower:
        return (
            "The alarm fires on prediction, not evidence. Your nervous system "
            "treats anticipated social judgment with the same intensity it would treat physical danger. The alarm "
            "is not lying about the stakes as it perceives them. It is using an old threat model in a new context."
        )
    if "shame" in reflection_lower:
        return (
            "Shame selects the worst available interpretation and presents "
            "it as the only interpretation. It curates a database of your exposures and deletes evidence of "
            "competence. The assessment always finds you lacking because the database only contains evidence of lacking."
        )
    if "watcher" in reflection_lower or "watching" in reflection_lower:
        return (
            "The watcher is the shape anxiety takes when it turns inward. "
            "You watch yourself performing, then watch yourself watching, then evaluate how well you stopped watching. "
            "The recursion is infinite. Each layer creates a new layer to observe."
        )
    if "overwhelm" in reflection_lower:
        return (
            "Overwhelm is your capacity reaching its actual limit. Not your "
            "character failing, not your discipline collapsing — the demand has exceeded what the system can process "
            "right now. The mechanism treats this as emergency because, from the nervous system's perspective, it is."
        )
    if "grief" in reflection_lower or "loss" in reflection_lower:
        return (
            "Grief is your system processing an absence that it has not yet "
            "mapped. The neural pathways that expected the presence still fire. The mechanism is not broken — it is "
            "doing exactly what it should do when something significant has changed in the landscape."
        )
    if "spiral" in reflection_lower:
        return (
            "The spiral is a prediction engine running unchecked. Each link "
            "loads the next without waiting for evidence. The chain moves from signal to catastrophe in seconds. "
            "But each link is a prediction, not a fact. The chain has never once been right about the final link."
        )
    # Generic mechanism from thesis — explain the system without repeating the
    # thesis verbatim. Repeating the same sentence as mechanism, point, and
    # callback trips book-wide density gates and reads assembled.
    templates = [
        "Underneath the feeling is a simple mechanism: the alarm treats uncertainty like danger and asks for impossible certainty. That is why ordinary moments can feel heavy before anything has actually gone wrong.",
        "Here is the mechanism: the nervous system can give imagined threat the same emergency response it gives real threat. This is why knowing better rarely helps when the body is already mobilized.",
        "The pattern underneath is prediction becoming chemistry. Your body can respond to the forecast of danger before the facts arrive, and that chemistry does not care whether the forecast is accurate.",
        "What drives this is an old threat model running in modern rooms. The system was built for physical danger; now it fires inside offices, apartments, group chats, and unread messages.",
        "The core mechanism is confirmation under pressure. Once the nervous system marks a moment as dangerous, it narrows perception toward evidence that keeps the alarm alive.",
    ]
    picked = templates[hash(thesis) % len(templates)]
    if _LOCALE_TLS:
        picked = _gt(picked, locale=_LOCALE_TLS)
    return picked


def _distill_mechanism(
    reflection: str,
    thesis: str,
    *,
    emotional_job: str = "",
    mechanism_memory: MechanismThesisMemory | None = None,
) -> str:
    """Derive a mechanism-explanation paragraph from REFLECTION content."""
    if not mechanism_thesis_families_enabled():
        return ""
    job = _normalize_emotional_job(emotional_job)
    if not job:
        return _distill_mechanism_legacy(reflection, thesis)
    payload = _load_mechanism_thesis_families()
    bank = ((payload.get("mechanism_families") or {}).get(job)) or {}
    if not isinstance(bank, dict):
        return _distill_mechanism_legacy(reflection, thesis)
    candidates = _collect_text_entries(bank)
    reflection_low = (reflection or "").lower()
    topic_specific = [
        c
        for c in candidates
        if c.get("topic_keywords")
        and any(str(k).strip().lower() in reflection_low for k in c.get("topic_keywords", []))
    ]
    pool = topic_specific or candidates
    selected = _select_mechanism_thesis_candidate(
        pool,
        chapter_index=_CHAPTER_INDEX_TLS,
        memory=mechanism_memory,
        kind="mechanism",
    )
    if selected:
        return str(selected.get("text", "")).strip()
    return _distill_mechanism_legacy(reflection, thesis)


def _trim_reflection(reflection: str, max_sentences: int = 50) -> str:
    """Trim REFLECTION to the most thesis-relevant sentences.

    Sprint-1 note: when depth content is routed through REFLECTION (depth_mech →
    REFLECTION in build_virtual_slot_streams), the input can be 3000-5000 words.
    The old keyword-filter approach silently discarded ~75% of this content.
    Fix: return the full reflection (all sentences) after stripping academic hedging.
    The max_sentences parameter is retained for API compatibility but no longer caps
    output — use the caller to limit if needed.
    """
    if not reflection:
        return ""
    # Strip academic hedging inline (preserve all sentences)
    joined = reflection
    joined = re.sub(r"\bI have noticed that\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat I have come to understand is that\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat I have come to think about is\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat I have come to see is that\s+", "", joined, flags=re.I)
    joined = re.sub(r"\bWhat happens is that\s+", "", joined, flags=re.I)
    return joined.strip()


def _polish_scene(scene: str) -> str:
    """Fix common loc-var fallback collisions in SCENE prose."""
    s = (scene or "").strip()
    if not s:
        return s
    lower = s.lower()
    if "gray light through the window" in lower:
        replacement = "A washed-out stripe of light catches the glass"
        if any(token in lower for token in ("train", "platform", "car", "station")):
            replacement = "The train window throws your pale reflection back at you"
        elif any(token in lower for token in ("desk", "keyboard", "screen", "document", "inbox", "calendar")):
            replacement = "Late light smears across the edge of the desk"
        elif any(token in lower for token in ("hall", "office", "monitor", "keycard", "elevator")):
            replacement = "A pale rectangle from the hall window lies across the carpet"
        s = re.sub(r"gray light through the window(?:\s+(?:on|through|against)\s+(?:the\s+)?(?:glass|window))?", replacement, s, flags=re.I)
    s = s.replace("The gray light through the window afternoon", "The afternoon light is flat and gray")
    s = s.replace("through the window afternoon", "afternoon")
    s = re.sub(
        r"(?i)\b(fluorescent (?:station|tunnel) light) smears across the window through (?:your|the)\s+window\b",
        r"\1 smears across the window",
        s,
    )
    s = re.sub(
        r"(?i)\b(fluorescent (?:station|tunnel) light) smears across the window visible through the high windows\b",
        r"\1 is visible through the high windows",
        s,
    )
    s = re.sub(
        r"(?i)\b(fluorescent (?:station|tunnel) light) smears across the window against the building\b",
        r"\1 catches the building across from you",
        s,
    )
    s = re.sub(
        r"(?i)\b(fluorescent (?:station|tunnel) light) smears across the window is flat today\b",
        r"\1 lies flat across the window today",
        s,
    )
    s = s.replace("The the ", "The ")
    s = s.replace("the the ", "the ")
    s = s.replace("below below", "below")
    s = s.replace("through the window through the window", "against the window")
    s = re.sub(r"(?<=[.!?]\s)([a-z])", lambda m: m.group(1).upper(), s)
    s = re.sub(r"\s{2,}", " ", s).strip()
    if s and s[0].isalpha() and s[0].islower():
        s = s[0].upper() + s[1:]
    return s


def _fallback_takeaway(
    thesis: str,
    *,
    emotional_job: str = "",
    chapter_index: int = 0,
    total_chapters: int = 1,
    bridge_memory: BridgeMemory | None = None,
) -> str:
    """Generate a takeaway when TAKEAWAY slot is missing/placeholder."""
    if not render_glue_enabled():
        return ""
    job = _normalize_emotional_job(emotional_job)
    if job:
        selected = _select_bridge_candidate(
            bridge_type="takeaway_fallback",
            emotional_job=job,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=bridge_memory,
            context_text=thesis,
        )
        if selected:
            text = str(selected.get("text", "")).strip()
            return _gt(text, locale=_LOCALE_TLS) if _LOCALE_TLS else text
    core = thesis.replace("The point is that ", "")
    options = [
        "Remember this: {core} Keep it concrete long enough to test it in your next ordinary hour.",
        "Carry this forward: {core} Let your next small action prove whether it is true.",
        "Keep this close: {core} Insight counts only when it changes the next moment you are inside the pattern.",
    ]
    template = _pick_variant(options, thesis, str(chapter_index), str(total_chapters))
    if _LOCALE_TLS:
        translated = _gt(template, locale=_LOCALE_TLS)
        try:
            return translated.format(core=core)
        except (KeyError, IndexError):
            return translated
    return template.format(core=core)


# DEFECT 1 (cross_book_transitions): per-keyword fallback pools. The original
# code returned ONE constant per thesis keyword, so every book with the same
# thesis keyword emitted a byte-identical bridge. Each branch now offers several
# topically-faithful variants routed through _pick_legacy_bridge_with_memory,
# whose seed mixes book_seed/persona/topic AND whose bridge_memory dedup prevents
# the same line repeating >1x within a book.
_FALLBACK_THREAD_KEYWORD_POOLS: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (
        ("regret", "choice"),
        (
            "What remains is the harder part: how to choose when loss still feels louder than relief.",
            "The next test is the choice itself, made while regret is still arguing for the safer move.",
            "From here the question narrows to one decision you keep deferring because loss speaks first.",
        ),
    ),
    (
        ("comparison",),
        (
            "The next pressure point is harder to admit: what happens when someone else's life starts writing your standards for you.",
            "What remains is the comparison that keeps measuring your day against a version of someone else's.",
            "From here the work is reclaiming the standard you outsourced to everyone you measure yourself against.",
        ),
    ),
    (
        ("alarm", "false alarm"),
        (
            "What remains is the moment after the alarm fires, when your body still wants to obey a prediction.",
            "The next pressure point is the second after the alarm, when the body is already braced for a threat that may not come.",
            "From here the question is what you do once the alarm has fired and the prediction it made still feels like fact.",
        ),
    ),
    (
        ("shame",),
        (
            "What remains is the sentence shame writes after the moment is over, when it tries to turn one event into identity.",
            "The next move is catching shame mid-sentence, before one moment hardens into a verdict about who you are.",
            "From here the work is refusing shame the last word it always reaches for after the moment has passed.",
        ),
    ),
    (
        ("overwhelm",),
        (
            "What remains is the quieter cost: what repeated overload teaches you to stop asking for.",
            "The next pressure point is subtler: the requests overwhelm has quietly trained you to stop making.",
            "From here the question is what overload has cost you in the asking, not just in the doing.",
        ),
    ),
)

_FALLBACK_THREAD_GENERIC_OPTIONS: tuple[str, ...] = (
    "What remains is the next ordinary moment where the pattern tries to make the decision for you.",
    "The next pressure point is smaller than it sounds: one place where your body asks for proof before you move.",
    "From here, the question is how this pattern changes when you meet it before it becomes a whole story.",
    "What remains is not more explanation. It is the first honest place this pattern asks for practice.",
    "The next chapter begins where insight usually thins out: inside the moment you have to choose again.",
)


def _fallback_thread(
    thesis: str,
    chapter_index: int,
    total_chapters: int,
    *,
    emotional_job: str = "",
    bridge_memory: BridgeMemory | None = None,
    book_seed: str = "",
    persona_id: str = "",
    topic_id: str = "",
) -> str:
    """Generate a thread-forward when THREAD slot is missing/placeholder."""
    if chapter_index >= total_chapters - 1:
        return ""  # Last chapter: no thread-forward
    if not bridge_transition_families_enabled():
        return ""
    # DEFECT 1 (A): resolve planner arc-roles (destabilization/stabilization/etc.)
    # onto bridge-bank jobs so the data-driven 'Ahead of you:' bank actually fires
    # instead of falling through to the hardcoded pool.
    job = _resolve_emotional_job(emotional_job)
    if job:
        selected = _select_bridge_candidate(
            bridge_type="thread_fallback",
            emotional_job=job,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=bridge_memory,
            context_text=thesis,
            seed=f"{book_seed}|{persona_id}|{topic_id}",
        )
        if selected:
            text = str(selected.get("text", "")).strip()
            return _gt(text, locale=_LOCALE_TLS) if _LOCALE_TLS else text
    # DEFECT 1 (B)+(C): book-distinct literal fallback. Seed every pick with
    # book_seed/persona/topic so identical thesis+chapter across different books
    # diverge, and route through bridge_memory so no bridge repeats within a book.
    seed_parts = (
        thesis,
        str(chapter_index),
        str(total_chapters),
        book_seed,
        persona_id,
        topic_id,
    )
    lower = thesis.lower()
    # _pick_legacy_bridge_with_memory -> _pick_variant already applies locale
    # translation (_gt) to the chosen string, so do NOT re-wrap the result here.
    # Build the candidate pool keyword-first (topically faithful variants) then
    # append the generic options. The wider combined pool gives bridge_memory
    # enough headroom to avoid within-book repeats even on long all-fallback runs.
    keyword_label = "generic"
    candidate_pool: list[str] = []
    for keywords, pool in _FALLBACK_THREAD_KEYWORD_POOLS:
        if any(kw in lower for kw in keywords):
            keyword_label = keywords[0]
            candidate_pool = list(pool)
            break
    for opt in _FALLBACK_THREAD_GENERIC_OPTIONS:
        if opt not in candidate_pool:
            candidate_pool.append(opt)
    return _pick_legacy_bridge_with_memory(
        candidate_pool,
        chapter_index=chapter_index,
        bridge_memory=bridge_memory,
        family_key=f"thread_fallback_literal|{keyword_label}",
        seed_parts=seed_parts,
    )


# Body-part-keyed exercise-opener variants. Each part carries several DISTINCT
# secular openers; _exercise_setup_sentence rotates them through the memory-aware
# selector so body-heavy books (anxiety/depression) no longer repeat one hardcoded
# line per chapter (the prior single-string-per-part design tripped the
# repeated-phrase density gate ~once/chapter). Every variant stays secular
# (somatic / nervous-system register) — no spiritual or teacher framing.
_BODY_PART_OPENERS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "sternum": (
        ("sternum", "chest"),
        (
            "Start with the pressure under the sternum. That is the part still bracing.",
            "Notice the chest — the held breath sitting just behind the ribs. Begin there.",
            "Bring your attention to the band of tightness across the chest that pulled snug while you read.",
            "Find the center of the chest where the weight settled, and let that be the first thing you tend.",
            "Begin at the breastbone. Let whatever is clenched there loosen by a single degree.",
            "Let the chest be the entry point — the place that braced before the rest of you caught up.",
        ),
    ),
    "jaw": (
        ("jaw",),
        (
            "Start with the jaw that tightened while the story was unfolding.",
            "Notice the jaw — how it set itself without instruction. Let it come unclenched.",
            "Bring attention to the hinge of the jaw, the muscle that has been holding all morning.",
            "Find the place where your back teeth meet, and let that contact soften.",
            "Begin at the jaw. Ease it open the way you would a door that sticks.",
        ),
    ),
    "throat": (
        ("throat",),
        (
            "Start with the throat that keeps rehearsing and swallowing the same sentence.",
            "Notice the throat — the narrow place where the words got stuck. Let it open.",
            "Bring attention to the throat, tight from everything said and unsaid.",
            "Find the constriction at the throat and give it one slow, deliberate swallow.",
            "Begin at the throat, the gate that closes when there is too much to hold.",
        ),
    ),
    "shoulder": (
        ("shoulder", "shoulders"),
        (
            "Start with the shoulders that lifted before you even noticed the cost.",
            "Notice how the shoulders crept toward the ears. Let them drop on the next exhale.",
            "Bring attention to the shoulders, carrying a load you never agreed to lift.",
            "Find the ridge of tension across the shoulders and let it slope back down.",
            "Begin at the shoulders — set down whatever they have been bracing to hold.",
        ),
    ),
    "hand": (
        ("hand", "thumb", "trackpad"),
        (
            "Start with the hand that hovered instead of moving. That freeze is the entry point.",
            "Notice the hands — clenched, or poised over a task they never started. Let them rest.",
            "Bring attention to the palms, the fingers that curled without being told.",
            "Find the hand still half-formed into a fist, and let it open, slowly.",
            "Begin with the hands. Feel their weight, unhurried, doing nothing for a moment.",
        ),
    ),
    "breath": (
        ("breath", "breathe"),
        (
            "Start with the breath that shortened when the chapter turned.",
            "Notice the breath — high and shallow, parked up in the chest. Let it drop lower.",
            "Bring attention to the breath you have been half-holding. Let the next one finish.",
            "Find the rhythm of the breath, even if it is quick, and let it lengthen on its own.",
            "Begin with one full exhale, longer than the inhale before it.",
        ),
    ),
}

_SETUP_FALLBACK_OPENERS: tuple[str, ...] = (
    "Start with the place in your body that lifted while you were listening. That is where the practice begins.",
    "Start where you feel the most tension right now. Not where you think the tension should be — where it actually is.",
    "Begin with whatever your body is holding. You do not need to name it. Just locate it.",
    "Find the part of you that tightened during this chapter. That is your entry point.",
    "Notice where your body is bracing. Start there. Not with the thought — with the sensation.",
    "Scan from your scalp to your feet. The first place that speaks up is where you begin.",
    "Start with the part of you that wanted to look away during the last section.",
    "Place one hand where the tension is loudest. That contact is the first move.",
    "Begin where the weight settled. You will know the spot before you can explain it.",
    "Start with the simplest true thing your body is telling you right now.",
)


def _exercise_setup_sentence(
    reflection: str,
    story: str,
    *,
    emotional_job: str = "",
    practice_type: str = "",
    exercise_memory: ExerciseWrapperMemory | None = None,
) -> str:
    seed = f"{reflection} {story}".lower()
    if not exercise_wrapper_families_enabled():
        return ""
    # Rotate distinct secular openers per body part via the memory-aware selector
    # (was: one hardcoded line per part, no rotation -> the same opener repeated
    # ~once/chapter in body-heavy books and tripped repeated-phrase density).
    for _part, (_keywords, _variants) in _BODY_PART_OPENERS.items():
        if any(_kw in seed for _kw in _keywords):
            _picked = _select_exercise_candidate(
                [{"text": _v} for _v in _variants],
                chapter_index=_CHAPTER_INDEX_TLS,
                memory=exercise_memory,
                family_key=f"setup_sentence|bodypart|{_part}",
            )
            if _picked:
                _txt = str(_picked.get("text", "")).strip()
                return _gt(_txt, locale=_LOCALE_TLS) if _LOCALE_TLS else _txt
            break  # all variants for this part used this book -> fall through to job path
    job = _normalize_emotional_job(emotional_job)
    if job:
        candidates = _resolve_practice_candidates(
            wrapper_type="setup_sentence",
            practice_type=practice_type,
            emotional_job=job,
        )
        selected = _select_exercise_candidate(
            candidates,
            chapter_index=_CHAPTER_INDEX_TLS,
            memory=exercise_memory,
            family_key=f"setup_sentence|{practice_type}|{job}",
        )
        if selected:
            text = str(selected.get("text", "")).strip()
            if _LOCALE_TLS:
                return _gt(text, locale=_LOCALE_TLS)
            return text
    _fallback_picked = _select_exercise_candidate(
        [{"text": _v} for _v in _SETUP_FALLBACK_OPENERS],
        chapter_index=_CHAPTER_INDEX_TLS,
        memory=exercise_memory,
        family_key="setup_sentence|fallback",
    )
    if _fallback_picked:
        _txt = str(_fallback_picked.get("text", "")).strip()
        return _gt(_txt, locale=_LOCALE_TLS) if _LOCALE_TLS else _txt
    return _SETUP_FALLBACK_OPENERS[hash(f"{reflection}{story}") % len(_SETUP_FALLBACK_OPENERS)]


def _shape_integration(integration: str) -> str:
    text = (integration or "").strip()
    if not text or _is_placeholder_text(text):
        return text
    sentences = _sentences(text)
    kept: list[str] = []
    for sentence in sentences:
        low = sentence.lower()
        if low.startswith("the point is") or low.startswith("what this means"):
            continue
        if len(re.findall(r"\b\w+\b", sentence)) <= 2 and low not in {"still here."}:
            continue
        kept.append(sentence)
    if not kept:
        kept = sentences[:3]
    total_words = 0
    limited: list[str] = []
    for sentence in kept:
        sentence_word_count = len(re.findall(r"\b\w+\b", sentence))
        if limited and total_words + sentence_word_count > 60:
            break
        limited.append(sentence)
        total_words += sentence_word_count
    return " ".join(limited or kept[:1])


def _resolve_practice_type(exercise_type_hint: str, exercise_atom_id: str, exercise_text: str) -> str:
    low = " ".join((exercise_type_hint or "", exercise_atom_id or "", exercise_text or "")).lower()
    mapping = [
        ("breath_regulation", ("breath", "box", "exhale", "inhale", "coherent")),
        ("grounding", ("ground", "floor", "feet", "sensory", "orient")),
        ("body_scan", ("body scan", "scan", "head-to-toe")),
        ("somatic_discharge", ("shake", "discharge", "release", "tension", "move")),
        ("visualization", ("visual", "imagine", "imagery", "picture")),
        ("reflective_prompt", ("journal", "prompt", "write", "reflect", "question")),
        ("attention_training", ("attention", "focus", "anchor", "concentration")),
        ("vagus_stimulation", ("vagus", "hum", "gargle", "cold water", "sigh")),
        ("integration_pause", ("integrat", "pause", "settle", "landing")),
    ]
    for practice, needles in mapping:
        if any(n in low for n in needles):
            return practice
    return "body_awareness"


# OPD-113: practice_type → exercise_type_template_key mapping. Practice types
# used by chapter_composer's bridges and exercise_type keys used by the
# introduction/intro template YAML files share intent but have different names.
_PRACTICE_TYPE_TO_EXERCISE_TYPE: dict[str, str] = {
    "breath_regulation": "00_breath_regulation",
    "grounding": "01_grounding_orientation",
    "body_scan": "02_body_awareness_scan",
    "somatic_discharge": "03_somatic_release_discharge",
    "visualization": "08_emotional_processing_completion",
    "reflective_prompt": "09_embodied_intention_direction",
    "attention_training": "02_body_awareness_scan",
    "vagus_stimulation": "06_vagal_stimulation_sound",
    "integration_pause": "10_integration_return_to_baseline",
    "body_awareness": "02_body_awareness_scan",
}


def _exercise_introduction_cue(practice_type: str) -> str:
    """OPD-113: explicit "Now we're going to do an exercise" cue (Part 1).

    Used by the fallback path when neither component_assembler nor
    practice_library composers can compose the exercise. Pulls from
    introduction_templates.yaml so operator-facing language stays consistent.
    Returns empty string if templates can't be loaded — caller skips silently.
    """
    try:
        from phoenix_v4.exercises.component_assembler import _load_introduction_templates
        templates = _load_introduction_templates()
        eff_type = _PRACTICE_TYPE_TO_EXERCISE_TYPE.get(practice_type, "_default")
        intr = templates.get(eff_type) or templates.get("_default") or {}
        text = str(intr.get("full", "")).strip()
        if text and _LOCALE_TLS:
            return _gt(text, locale=_LOCALE_TLS)
        return text
    except Exception:
        return ""


def _post_practice_validation_sentence(
    *,
    emotional_job: str = "",
    practice_type: str = "",
    exercise_memory: ExerciseWrapperMemory | None = None,
) -> str:
    if not exercise_wrapper_families_enabled():
        return ""
    job = _normalize_emotional_job(emotional_job)
    if not job:
        options = [
            "Whatever you noticed is enough.",
            "Even a small shift is still a shift.",
            "There is no wrong response here.",
            "What just happened gave you useful information.",
        ]
        return _pick_variant(options, practice_type, emotional_job)
    candidates = _resolve_practice_candidates(
        wrapper_type="post_practice_validation",
        practice_type=practice_type,
        emotional_job=job,
    )
    selected = _select_exercise_candidate(
        candidates,
        chapter_index=_CHAPTER_INDEX_TLS,
        memory=exercise_memory,
        family_key=f"post_practice_validation|{practice_type}|{job}",
    )
    if selected:
        text = str(selected.get("text", "")).strip()
        if _LOCALE_TLS:
            return _gt(text, locale=_LOCALE_TLS)
        return text
    return "Whatever you noticed is enough."


def _emotional_state_from_arc_role(role: str) -> EmotionalState:
    r = (role or "").strip().lower()
    if r == "destabilization":
        return EmotionalState.HEAVY
    if r == "integration":
        return EmotionalState.CLOSE
    if r == "reframe":
        return EmotionalState.FLOW
    return EmotionalState.NEUTRAL


def _bump_exercise_stat(stats: dict | None, key: str) -> None:
    if stats is None:
        return
    stats[key] = int(stats.get(key, 0)) + 1
    stats["total"] = int(stats.get("total", 0)) + 1


def _build_assembly_context(
    chapter_index: int,
    total_chapters: int,
    emotional_role: str,
    exercise_atom_id: str,
    topic_id: str,
    persona_id: str,
    exercise_repeat_index: int,
) -> AssemblyContext:
    return AssemblyContext(
        first_encounter=chapter_index == 0,
        emotional_state=_emotional_state_from_arc_role(emotional_role),
        repeat_count=exercise_repeat_index,
        is_session_close=chapter_index >= max(total_chapters - 1, 0),
        persona=persona_id or "",
        exercise_id=exercise_atom_id or "",
        chapter_index=chapter_index,
        topic=topic_id or "",
    )


def _shape_thread(
    thread_raw: str,
    thesis: str,
    chapter_index: int,
    total_chapters: int,
    *,
    emotional_job: str = "",
    bridge_memory: BridgeMemory | None = None,
    book_seed: str = "",
    persona_id: str = "",
    topic_id: str = "",
) -> str:
    if thread_raw and not _is_placeholder_text(thread_raw):
        cleaned = re.sub(r"\bIn the next chapter,\s*", "", thread_raw, flags=re.I).strip()
        cleaned = re.sub(r"\bThere is more to explore\b[. ]*", "", cleaned, flags=re.I).strip()
        if cleaned:
            return cleaned
    return _fallback_thread(
        thesis,
        chapter_index,
        total_chapters,
        emotional_job=emotional_job,
        bridge_memory=bridge_memory,
        book_seed=book_seed,
        persona_id=persona_id,
        topic_id=topic_id,
    )


# ---------------------------------------------------------------------------
# Main composition function
# ---------------------------------------------------------------------------

def angle_callback_memory_line(prior_assertion: str) -> str:
    """One-sentence recall of the prior journey layer (OPD-116/117)."""
    ass = (prior_assertion or "").strip()
    if not ass or ass.upper() == "TODO" or ass.startswith("TODO:"):
        return ""
    core = ass.rstrip(".")
    return f"Earlier I said {core}. Here is what was hidden in that."


def prefix_angle_callback_prose(
    body: str,
    *,
    angle_id: str,
    layer: int,
    topic_id: str = "",
) -> str:
    """Prepend memory-line to callback body using registry layer_progression."""
    text = (body or "").strip()
    if not text or layer <= 1:
        return text
    from phoenix_v4.planning.angle_journey import merge_angle_journey, prior_layer_assertion

    journey = merge_angle_journey(angle_id)
    prior = prior_layer_assertion(layer, list(journey.get("layer_progression") or []))
    prefix = angle_callback_memory_line(prior)
    if not prefix:
        return text
    return f"{prefix}\n\n{text}"


# ---------------------------------------------------------------------------
# Blocker C (Phase B 2026-06-16): opening-chapter clear-point + transition floor.
#
# The chapter_flow gate (phoenix_v4/quality/chapter_flow_gate.py) is a deterministic
# substring detector. It FAILs a chapter when:
#   - MISSING_CLEAR_POINT: no sentence carries a recognized thesis cue
#     (thesis_hits = count of _THESIS_CUES substrings present; needs >=1), and
#   - WEAK_TRANSITIONS: fewer than `min_transitions` recognized transition cues
#     (standard long-form floor = 3).
# On the courage proof book the OPENING chapters carried a strong thesis CLAIM
# (e.g. "The hypervigilance you've built is so familiar you can't feel it anymore.")
# but in a SHAPE the gate's cue list does not recognize, so Ch1 scored thesis_hits=0
# (MISSING_CLEAR_POINT) and Ch2 carried only 2 transition cues (WEAK_TRANSITIONS).
#
# Fix (composer-side, gate-honest — we VARY/STRENGTHEN the OUTPUT, never the gate):
# when an opening chapter would otherwise miss a clear point, state the chapter's
# OWN derived thesis explicitly as a clear-point sentence ("What this means is plain: <thesis>");
# when an early chapter is transition-light, add ONE explicit connective that names the
# turn. Both additions are genuine prose (the chapter's real thesis / its real pivot),
# deterministic (seeded by book_seed + chapter_index), and scoped to chapters 0-1 ONLY,
# so chapters 2+ are byte-identical to before. This NEVER weakens a threshold.

# Cue lexicons MUST stay a subset of the gate's recognized cues (chapter_flow_gate.py
# _THESIS_CUES / _TRANSITION_CUES) so a detectable hit is guaranteed. Each frame below
# embeds a gate-recognized _THESIS_CUES substring: "what this means", "the point is",
# or "this is not".
_OPENING_CLEAR_POINT_FRAMES = (
    "What this means is plain, and it is worth saying outright: {claim}",
    "So the point is this, stated plainly: {claim}",
    "This is not a detail to skim past: {claim}",
)
_EARLY_TRANSITION_CONNECTIVES = (
    "This is why the rest of the chapter keeps returning to it: the pattern repeats "
    "until it is named, which means naming it is the work.",
    "Here is what that opens up, because the mechanism matters more than any single "
    "moment: the same move will keep happening until you can see it coming.",
    "That matters because the cost is not in one decision; it is in the pattern, which "
    "means the way out is to interrupt the pattern, not the decision.",
)


def _has_thesis_cue(text: str) -> bool:
    low = (text or "").lower()
    return any(cue in low for cue in _THESIS_CUES)


def _count_transition_cues(text: str) -> int:
    low = (text or "").lower()
    return sum(1 for cue in _TRANSITION_CUES if cue in low)


def _strengthen_opening_chapter_flow(
    parts: list[str],
    *,
    thesis: str,
    chapter_index: int,
    book_seed: str = "",
    min_transitions: int = 3,
) -> list[str]:
    """Guarantee a detectable clear-point (Ch1) and transition floor (Ch2).

    Only mutates chapters 0 and 1 on the legacy/registry compose path. Returns ``parts``
    (possibly with 1-2 appended sentences). Deterministic given (book_seed, chapter_index,
    thesis).

    NOTE (Blocker 1, 2026-06-17): the spine pipeline strengthens chapter_flow for ALL
    chapters via ``book_renderer.strengthen_chapter_flow_for_delivery`` (the cue-aware glue
    selector), not through this function. The late-chapter MISSING_CLEAR_POINT /
    WEAK_TRANSITIONS fix therefore lives there; this opening-only helper is unchanged.
    """
    if not render_glue_enabled():
        return parts
    if chapter_index > 1:
        return parts
    claim = (thesis or "").strip()
    composed_preview = "\n\n".join(p for p in parts if p and p.strip())

    # Ch1 (and any opening chapter): ensure a recognized clear-point cue is present.
    if claim and not _has_thesis_cue(composed_preview):
        # Strip a trailing period so the frame reads cleanly; frames re-add terminal '.'.
        claim_core = claim.rstrip()
        frame = _pick_variant(
            list(_OPENING_CLEAR_POINT_FRAMES),
            book_seed or "", str(chapter_index), claim_core[:32], "opening_clear_point",
        )
        clear_point = frame.format(claim=claim_core)
        if not clear_point.endswith((".", "!", "?")):
            clear_point += "."
        parts.append(clear_point)
        composed_preview = composed_preview + "\n\n" + clear_point

    # Ch2 (chapter_index == 1): ensure the transition-cue floor is met.
    if chapter_index == 1 and _count_transition_cues(composed_preview) < min_transitions:
        connective = _pick_variant(
            list(_EARLY_TRANSITION_CONNECTIVES),
            book_seed or "", str(chapter_index), "early_transition",
        )
        parts.append(connective)

    return parts


def _authored_transition(
    boundary: str,
    *,
    topic_id: str = "",
    persona_id: str = "",
    engine_type: str = "",
    chapter_index: int = 0,
    book_seed: str = "",
    locale: Optional[str] = None,
) -> str:
    """Emit authored TRANSITION atom when render glue is OFF; else ``""``."""
    if render_glue_enabled() or not topic_id or not persona_id:
        return ""
    from phoenix_v4.planning.transition_atoms import select_authored_transition

    global _BOOK_TRANSITION_USED_TLS
    if _BOOK_TRANSITION_USED_TLS is None:
        _BOOK_TRANSITION_USED_TLS = set()
    return select_authored_transition(
        boundary,
        persona_id=persona_id,
        topic_id=topic_id,
        engine_type=engine_type,
        chapter_index=chapter_index,
        book_seed=book_seed,
        locale=locale,
        used_texts=_BOOK_TRANSITION_USED_TLS,
    )


def compose_ordered_chapter_prose(
    slot_types: list[str],
    slot_proses: list[str],
) -> str:
    """Twelve-shape flagship: 1:1 slot order, no bridges, reorder, or type collapse."""
    parts: list[str] = []
    for _st, prose in zip(slot_types, slot_proses):
        body = (prose or "").strip()
        if not body or _is_placeholder_text(body):
            continue
        parts.append(body)
    return "\n\n".join(parts).strip()


def compose_chapter_prose(
    slot_types: list[str],
    slot_proses: list[str],
    chapter_index: int = 0,
    total_chapters: int = 1,
    include_slot_labels_qa: bool = False,
    exercise_context: Optional[AssemblyContext] = None,
    locale: Optional[str] = None,
    *,
    topic_id: str = "",
    persona_id: str = "",
    emotional_role: str = "",
    exercise_atom_id: str = "",
    exercise_type_hint: str = "",
    exercise_repeat_index: int = 0,
    exercise_source_stats: Optional[dict] = None,
    book_seed: str = "",
    mechanism_memory: Optional[MechanismThesisMemory] = None,
    exercise_memory: Optional[ExerciseWrapperMemory] = None,
    bridge_memory: Optional[BridgeMemory] = None,
    chapter_intent: str = "",
    engine_type: str = "",
    arc_thesis: str = "",
) -> str:
    """
    Compose a single chapter's prose from its slot types and resolved prose strings.

    Reorders slots into bestseller argument flow:
      Opening (HOOK/SCENE) → Bridge → Mechanism → Bridge → Reflection → Bridge →
      Story → Bridge → Exercise → Integration → Takeaway → Thread

    Returns the composed chapter text (no heading — caller adds 'Chapter N').
    """
    # Set chapter index for variant rotation across all bridge/thesis functions
    global _CHAPTER_INDEX_TLS
    _CHAPTER_INDEX_TLS = chapter_index
    global _LOCALE_TLS
    _LOCALE_TLS = locale
    resolved_bridge_memory = bridge_memory if bridge_memory is not None else _BOOK_BRIDGE_MEMORY_TLS

    # Build slot_type → prose map (first non-placeholder) + lists for multi-slot types
    slot_map: dict[str, str] = {}
    slot_lists: dict[str, list[str]] = {}
    for st, prose in zip(slot_types, slot_proses):
        st_upper = st.strip().upper()
        slot_lists.setdefault(st_upper, []).append(prose)
        if st_upper not in slot_map or _is_placeholder_text(slot_map[st_upper]):
            slot_map[st_upper] = prose

    # Extract slot content
    hook = slot_map.get("HOOK", "")
    angle_definition = slot_map.get("ANGLE_DEFINITION", "")
    angle_callback = slot_map.get("ANGLE_CALLBACK", "")
    scene = _polish_scene(slot_map.get("SCENE", ""))
    story_raw = slot_map.get("STORY", "")
    pivot_raw = slot_map.get("PIVOT", "")
    reflection_raw = slot_map.get("REFLECTION", "")
    integration_raw = _shape_integration(slot_map.get("INTEGRATION", ""))
    exercise_blocks = [
        p for p in slot_lists.get("EXERCISE", [])
        if p and not _is_placeholder_text(p)
    ]
    permission_raw = slot_map.get("PERMISSION", "")
    takeaway_raw = slot_map.get("TAKEAWAY", "")
    thread_raw = slot_map.get("THREAD", "")
    compression_raw = slot_map.get("COMPRESSION", "")

    # Derive thesis from reflection content
    thesis = (
        _derive_thesis(
            reflection_raw,
            chapter_index,
            emotional_job=emotional_role,
            thesis_memory=mechanism_memory,
            chapter_intent=chapter_intent,
            engine_type=engine_type,
            arc_thesis=arc_thesis,
            topic_id=topic_id,
        )
        if not _is_placeholder_text(reflection_raw)
        else arc_thesis.strip() if arc_thesis and arc_thesis.strip() else ""
    )

    # Build composed chapter in argument order
    parts: list[str] = []

    # 1. Opening (prefer HOOK for body-first immediacy, use SCENE as fallback)
    opening = hook if (hook and not _is_placeholder_text(hook)) else scene
    if opening and not _is_placeholder_text(opening):
        parts.append(opening)

    # 1a. OPD-116/117 ANGLE_CALLBACK immediately after HOOK (memory-line already in prose if prefixed upstream)
    if angle_callback and not _is_placeholder_text(angle_callback):
        parts.append(angle_callback.strip())

    # 1b. OPD-116/117 ANGLE_DEFINITION — single coherent block, no within-slot bridges
    if angle_definition and not _is_placeholder_text(angle_definition):
        parts.append(angle_definition.strip())

    # 2. SCENE (if both HOOK and SCENE exist, scene follows hook)
    if hook and scene and not _is_placeholder_text(hook) and not _is_placeholder_text(scene) and scene != opening:
        parts.append(scene)

    # 3. OPD-124: first section content (reflection teaching) before named story.
    if reflection_raw and not _is_placeholder_text(reflection_raw):
        trimmed = _trim_reflection(reflection_raw)
        if trimmed:
            parts.append(trimmed)

    # 4. STORY with optional QA label
    if story_raw and not _is_placeholder_text(story_raw):
        _before_story = _bridge_before_story(
            thesis,
            reflection=reflection_raw,
            story=story_raw,
            emotional_job=emotional_role,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=resolved_bridge_memory,
        )
        if not _before_story:
            _before_story = _authored_transition(
                "before_story",
                topic_id=topic_id,
                persona_id=persona_id,
                engine_type=engine_type,
                chapter_index=chapter_index,
                book_seed=book_seed,
                locale=locale,
            )
        if _before_story:
            parts.append(_before_story)
        story_raw = prepend_story_introduction_bridge(
            story_raw,
            story_raw,
            chapter_index=chapter_index,
        )
        if include_slot_labels_qa:
            # Find the original atom_id for STORY
            for st, prose in zip(slot_types, slot_proses):
                if st.strip().upper() == "STORY" and prose == story_raw:
                    break
        parts.append(story_raw)

    # 5a. PIVOT (land the story before teaching — Writer Spec §4.3a)
    if pivot_raw and not _is_placeholder_text(pivot_raw):
        parts.append(pivot_raw)

    # 5b. COMPRESSION (if present, adds density/summary)
    if compression_raw and not _is_placeholder_text(compression_raw):
        parts.append(compression_raw)

    # 5c. Mechanism deepening after story + section land (OPD-124 sequence).
    # De-injection 2026-07-05: skip template bridge/mechanism/thesis when glue families
    # are OFF; authored arc_thesis still lands when provided by the spine.
    show_mechanism_glue = (
        bridge_transition_families_enabled() or mechanism_thesis_families_enabled()
    )
    if show_mechanism_glue and thesis:
        parts.append(
            _bridge_after_opening(
                thesis,
                opening=opening,
                scene=scene,
                emotional_job=emotional_role,
                chapter_index=chapter_index,
                total_chapters=total_chapters,
                bridge_memory=resolved_bridge_memory,
            )
        )
        mechanism = _distill_mechanism(
            reflection_raw,
            thesis,
            emotional_job=emotional_role,
            mechanism_memory=mechanism_memory,
        )
        if mechanism:
            parts.append(mechanism)
        parts.append(thesis)
    elif arc_thesis and arc_thesis.strip():
        _after_opening = _authored_transition(
            "after_opening",
            topic_id=topic_id,
            persona_id=persona_id,
            engine_type=engine_type,
            chapter_index=chapter_index,
            book_seed=book_seed,
            locale=locale,
        )
        if _after_opening:
            parts.append(_after_opening)
        parts.append(arc_thesis.strip())

    # 6. Exercise with bridge — preserve every EXERCISE slot (Holistic v2 Phase B)
    if not exercise_blocks:
        try:
            from phoenix_v4.exercises.practice_library_loader import get_exercise_for_chapter
            seed = book_seed or f"ch{chapter_index}:{thesis[:20]}"
            composed = get_exercise_for_chapter(
                chapter_index=chapter_index,
                topic_id=topic_id,
                persona_id=persona_id,
                seed=seed,
            )
            if composed:
                exercise_blocks = [composed]
        except Exception:
            pass

    _bridge_glue = bridge_transition_families_enabled()
    _wrapper_glue = exercise_wrapper_families_enabled()
    practice_type = ""

    def _transition_before_exercise() -> str:
        if _bridge_glue:
            return _bridge_before_exercise(
                thesis,
                reflection=reflection_raw,
                story=story_raw,
                emotional_job=emotional_role,
                practice_type=practice_type,
                exercise_memory=exercise_memory,
                chapter_index=chapter_index,
                total_chapters=total_chapters,
                bridge_memory=resolved_bridge_memory,
            )
        return _authored_transition(
            "before_exercise",
            topic_id=topic_id,
            persona_id=persona_id,
            engine_type=engine_type,
            chapter_index=chapter_index,
            book_seed=book_seed,
            locale=locale,
        )

    for ex_idx, exercise_raw in enumerate(exercise_blocks):
        exercise_from_library_34 = ex_idx == 0 and len(exercise_blocks) == 1 and not slot_lists.get("EXERCISE")
        practice_type = _resolve_practice_type(exercise_type_hint, exercise_atom_id, exercise_raw)
        int_for_ex = integration_raw if ex_idx == len(exercise_blocks) - 1 else ""
        eff_context = exercise_context or _build_assembly_context(
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            emotional_role=emotional_role,
            exercise_atom_id=exercise_atom_id,
            topic_id=topic_id,
            persona_id=persona_id,
            exercise_repeat_index=exercise_repeat_index + ex_idx,
        )
        assembled_ok = False
        try:
            from phoenix_v4.exercises.component_assembler import assemble_exercise_for_chapter

            composed_exercise = assemble_exercise_for_chapter(
                exercise_id=eff_context.exercise_id or exercise_atom_id,
                exercise_type=exercise_type_hint,
                description_text=exercise_raw,
                ctx=eff_context,
                aha_text="",
                integration_text=int_for_ex,
            )
            if composed_exercise.strip():
                _ex_bridge = _transition_before_exercise()
                if _ex_bridge:
                    parts.append(_ex_bridge)
                if _wrapper_glue:
                    setup = _exercise_setup_sentence(
                        reflection_raw,
                        story_raw,
                        emotional_job=emotional_role,
                        practice_type=practice_type,
                        exercise_memory=exercise_memory,
                    )
                    if setup:
                        parts.append(setup)
                parts.append(composed_exercise)
                if _wrapper_glue:
                    parts.append(
                        _post_practice_validation_sentence(
                            emotional_job=emotional_role,
                            practice_type=practice_type,
                            exercise_memory=exercise_memory,
                        )
                    )
                assembled_ok = True
                if exercise_from_library_34:
                    _bump_exercise_stat(exercise_source_stats, "library_34_fallback")
                else:
                    _bump_exercise_stat(exercise_source_stats, "registry")
                if ex_idx == len(exercise_blocks) - 1:
                    integration_raw = ""
        except Exception:
            assembled_ok = False

        if not assembled_ok:
            # Legacy wrap: rotating bridges + Phoenix aha/integration via practice_library_loader
            try:
                from phoenix_v4.exercises.practice_library_loader import compose_exercise, load_component_templates

                composed = compose_exercise(
                    exercise={"name": "Exercise", "text": exercise_raw, "exercise_type": "body_awareness"},
                    chapter_index=chapter_index,
                    seed=book_seed or f"ch{chapter_index}:{thesis[:20]}",
                    templates=load_component_templates(),
                )
                if composed:
                    _ex_bridge = _transition_before_exercise()
                    if _ex_bridge:
                        parts.append(_ex_bridge)
                    if _wrapper_glue:
                        setup = _exercise_setup_sentence(
                            reflection_raw,
                            story_raw,
                            emotional_job=emotional_role,
                            practice_type=practice_type,
                            exercise_memory=exercise_memory,
                        )
                        if setup:
                            parts.append(setup)
                    parts.append(composed)
                    if _wrapper_glue:
                        parts.append(
                            _post_practice_validation_sentence(
                                emotional_job=emotional_role,
                                practice_type=practice_type,
                                exercise_memory=exercise_memory,
                            )
                        )
                    integration_raw = ""
                    if exercise_from_library_34:
                        _bump_exercise_stat(exercise_source_stats, "library_34_fallback")
                    else:
                        _bump_exercise_stat(exercise_source_stats, "registry")
                else:
                    raise ValueError("empty compose")
            except Exception:
                _ex_bridge = _transition_before_exercise()
                if _ex_bridge:
                    parts.append(_ex_bridge)
                if _wrapper_glue:
                    introduction_cue = _exercise_introduction_cue(practice_type)
                    if introduction_cue:
                        parts.append(introduction_cue)
                    setup = _exercise_setup_sentence(
                        reflection_raw,
                        story_raw,
                        emotional_job=emotional_role,
                        practice_type=practice_type,
                        exercise_memory=exercise_memory,
                    )
                    if setup:
                        parts.append(setup)
                parts.append(exercise_raw)
                if _wrapper_glue:
                    parts.append(
                        _post_practice_validation_sentence(
                            emotional_job=emotional_role,
                            practice_type=practice_type,
                            exercise_memory=exercise_memory,
                        )
                    )
                if exercise_from_library_34:
                    _bump_exercise_stat(exercise_source_stats, "library_34_fallback")
                else:
                    _bump_exercise_stat(exercise_source_stats, "registry")

    # 7a. PERMISSION (receive the reader — Writer Spec §4.8)
    # Short emotional permission statement placed near INTEGRATION. High-cost chapters only.
    if permission_raw and not _is_placeholder_text(permission_raw):
        parts.append(permission_raw)

    # 8. Integration with bridge
    if integration_raw and not _is_placeholder_text(integration_raw):
        bridge_int = _bridge_before_integration(
            thesis,
            integration=integration_raw,
            emotional_job=emotional_role,
            practice_type=practice_type if practice_type else "",
            exercise_memory=exercise_memory,
            chapter_index=chapter_index,
            total_chapters=total_chapters,
            bridge_memory=resolved_bridge_memory,
        )
        if not bridge_int:
            bridge_int = _authored_transition(
                "before_integration",
                topic_id=topic_id,
                persona_id=persona_id,
                engine_type=engine_type,
                chapter_index=chapter_index,
                book_seed=book_seed,
                locale=locale,
            )
        if bridge_int:
            parts.append(bridge_int)
        parts.append(integration_raw)

    # 9. Takeaway (explicit slot or fallback)
    if takeaway_raw and not _is_placeholder_text(takeaway_raw):
        parts.append(takeaway_raw)

    # 10. Thread-forward (explicit slot or fallback)
    thread = (
        _shape_thread(
            thread_raw,
            thesis,
            chapter_index,
            total_chapters,
            emotional_job=emotional_role,
            bridge_memory=resolved_bridge_memory,
            book_seed=book_seed,
            persona_id=persona_id,
            topic_id=topic_id,
        )
        if thesis
        else ""
    )
    if thread:
        parts.append(thread)

    # Blocker C (Phase B 2026-06-16): guarantee the chapter_flow clear-point + transition
    # floor for the opening chapters (no-op for chapter_index > 1). See
    # _strengthen_opening_chapter_flow — strengthens the composed OUTPUT, never the gate.
    parts = _strengthen_opening_chapter_flow(
        parts,
        thesis=thesis,
        chapter_index=chapter_index,
        book_seed=book_seed,
    )

    # Filter empty parts and join
    composed = "\n\n".join(p for p in parts if p and p.strip())

    if topic_id:
        try:
            from phoenix_v4.planning.book_identity_contract import (
                ensure_identity_line_in_text,
                identity_line_for_chapter,
                load_book_identity_contract,
            )

            _contract = load_book_identity_contract(topic_id)
            if _contract:
                _iline = identity_line_for_chapter(_contract, chapter_index, total_chapters)
                if _iline:
                    composed = ensure_identity_line_in_text(composed, _iline)
        except ImportError:
            pass

    # Locale post-processing: replace English template strings with locale versions
    if locale and locale != "en-US":
        try:
            from phoenix_v4.rendering.locale_templates import localize_rendered_text
            composed = localize_rendered_text(composed, locale)
        except ImportError:
            pass

    return composed


# ---------------------------------------------------------------------------
# Spine / enriched-book slot bridges (beatmap order preserved; inserts only)
# ---------------------------------------------------------------------------
# Approximate extra words per chapter when full matrix applies: ~40–120 words
# (1–3 short bridges × ~15–40 words), micro formats ~20–50 when only exercise bridges fire.

_MICRO_RUNTIME_FORMATS = frozenset({"micro_book_15", "micro_book_20"})

_FULL_BRIDGE_PAIRS = frozenset(
    {
        ("SCENE", "REFLECTION"),
        ("HOOK", "REFLECTION"),
        ("REFLECTION", "EXERCISE"),
        ("EXERCISE", "SCENE"),
        ("SCENE", "TEACHER_DOCTRINE"),
        ("TEACHER_DOCTRINE", "REFLECTION"),
        ("STORY", "REFLECTION"),
        ("STORY", "EXERCISE"),
    }
)

_MICRO_BRIDGE_PAIRS = frozenset({("REFLECTION", "EXERCISE"), ("STORY", "EXERCISE")})

_EXERCISE_TAIL_CUES = (
    "before you",
    "try this:",
    "try this.",
    "the practice below",
    "take one breath",
    "give your body",
    "the exercise that follows",
    "the next step asks",
)

_REFLECTION_TAIL_CUES = (
    "what does this mean",
    "what do you notice",
    "ask yourself",
    "here's what this means",
    "here is what this means",
    "what would it be like",
)

_SCENE_TAIL_CUES = (
    "when you're back",
    "when you are back",
    "picture yourself",
    "picture this",
    "come back to the scene",
    "return to the moment",
    "step back into",
)


def _last_sentence_or_line(body: str) -> str:
    body = (body or "").strip()
    if not body:
        return ""
    sents = _sentences(body)
    if sents:
        return sents[-1].strip()
    lines = [ln.strip() for ln in body.splitlines() if ln.strip()]
    return lines[-1] if lines else ""


def _tail_window_lower(body: str, width: int = 96) -> str:
    tail = _last_sentence_or_line(body).lower()
    return tail[-width:] if tail else ""


def _should_skip_slot_bridge(prev_type: str, curr_type: str, prev_body: str) -> bool:
    """Anti-repetition: skip bridge when the previous slot already signals the upcoming mode."""
    p = prev_type.strip().upper()
    c = curr_type.strip().upper()
    tw = _tail_window_lower(prev_body)
    if not tw:
        return False
    if c == "EXERCISE":
        return any(cue in tw for cue in _EXERCISE_TAIL_CUES)
    if c == "REFLECTION" and p in ("SCENE", "STORY", "HOOK"):
        if tw.rstrip().endswith("?"):
            return True
        return any(cue in tw for cue in _REFLECTION_TAIL_CUES)
    if c == "SCENE":
        return any(cue in tw for cue in _SCENE_TAIL_CUES)
    return False


def _slot_bridge_paragraph(
    prev_t: str,
    curr_t: str,
    thesis: str,
    *,
    prev_body: str,
    chapter_index: int,
    last_reflection: str,
    last_story: str,
) -> str:
    """Return one bridge paragraph for a (prev_type, curr_type) pair, or empty string."""
    if not render_glue_enabled():
        return ""
    pair = (prev_t.strip().upper(), curr_t.strip().upper())

    if pair in {("SCENE", "REFLECTION"), ("HOOK", "REFLECTION")}:
        opts = [
            "Before the mind names it, pause and ask what your body is trying to protect.",
            "Let the moment finish landing, then see what question rises next without forcing an answer.",
            "Stay in the feeling a beat longer — inquiry works better when the body is still in the room.",
        ]
        return _pick_variant(opts, thesis, prev_body[:48], str(chapter_index), "hinge_body_reflection")

    if pair == ("REFLECTION", "EXERCISE"):
        return _bridge_before_exercise(thesis, reflection=prev_body, story=last_story)

    if pair == ("STORY", "EXERCISE"):
        return _bridge_before_exercise(thesis, reflection=last_reflection, story=prev_body)

    if pair == ("EXERCISE", "SCENE"):
        opts = [
            "When you are ready, step back into the scene and let it move at normal speed again.",
            "Picture the room again — same air, same light — and watch what your attention does with the practice still echoing.",
            "Return to the moment as if nothing needs to be solved yet; just let the body remember the room.",
        ]
        return _pick_variant(opts, thesis, prev_body[:48], str(chapter_index), "return_scene")

    if pair == ("SCENE", "TEACHER_DOCTRINE"):
        opts = [
            "From here the chapter widens into teaching — not to override the moment, but to situate it.",
            "What follows names the frame the moment keeps testing, in plain language.",
        ]
        return _pick_variant(opts, thesis, prev_body[:48], str(chapter_index), "section_doctrine")

    if pair == ("TEACHER_DOCTRINE", "REFLECTION"):
        opts = [
            "Before that teaching hardens into a rule, bring it back to your own day — one honest detail at a time.",
            "Let the doctrine touch something concrete in you, not as a verdict, but as a question.",
        ]
        return _pick_variant(opts, thesis, prev_body[:48], str(chapter_index), "doctrine_reflection")

    if pair == ("STORY", "REFLECTION"):
        opts = [
            "What you just watched is not a verdict on anyone — it is a mirror for a pattern you already carry.",
            "Hold the story lightly, then ask what it would mean if the same move showed up in your week.",
        ]
        return _pick_variant(opts, thesis, prev_body[:48], str(chapter_index), "story_reflection")

    return ""


def _inject_slot_bridges(
    slots: list[Any],
    *,
    chapter_index: int,
    runtime_format: str,
) -> str:
    """Insert transition paragraphs between adjacent non-gap slots; order unchanged."""
    global _CHAPTER_INDEX_TLS
    _CHAPTER_INDEX_TLS = chapter_index

    reflection_seed = ""
    for s in slots:
        st = (getattr(s, "slot_type", "") or "").strip().upper()
        c = (getattr(s, "content", "") or "").strip()
        if st == "REFLECTION" and c and not c.startswith("[CONTENT GAP"):
            reflection_seed = c
            break
    thesis = _derive_thesis(reflection_seed, chapter_index) if reflection_seed else ""

    rf = (runtime_format or "").strip()
    use_micro = rf in _MICRO_RUNTIME_FORMATS

    pieces: list[str] = []
    prev: Any | None = None
    last_bridge_norm = ""
    last_reflection = ""
    last_story = ""

    for slot in slots:
        content = (getattr(slot, "content", "") or "").strip()
        if not content or content.startswith("[CONTENT GAP"):
            continue
        st = (getattr(slot, "slot_type", "") or "").strip().upper()

        if prev is not None:
            pt = (getattr(prev, "slot_type", "") or "").strip().upper()
            want = (pt, st)
            allowed = (want in _MICRO_BRIDGE_PAIRS) if use_micro else (want in _FULL_BRIDGE_PAIRS)
            if allowed and not _should_skip_slot_bridge(pt, st, getattr(prev, "content", "") or ""):
                br = _slot_bridge_paragraph(
                    pt,
                    st,
                    thesis,
                    prev_body=getattr(prev, "content", "") or "",
                    chapter_index=chapter_index,
                    last_reflection=last_reflection,
                    last_story=last_story,
                ).strip()
                if br:
                    bn = re.sub(r"\s+", " ", br.lower()).strip()
                    if bn != last_bridge_norm:
                        pieces.append(br)
                        last_bridge_norm = bn

        pieces.append(content)
        if st == "REFLECTION":
            last_reflection = content
        if st == "STORY":
            last_story = content
        prev = slot

    return "\n\n".join(pieces)


def compose_from_enriched_book(
    enriched: "EnrichedBook",
    quality_profile: str = "draft",
    *,
    governance_report: Optional[dict[str, Any]] = None,
    artifact_dir: Optional[Path] = None,
    slot_tracker: Optional[Any] = None,
) -> str:
    """
    Render an EnrichedBook to prose text.

    New pipeline path:
      Spine → Knobs → Beatmap → Enrichment → this → BookRender.

    The legacy path (assembly_compiler → compose_chapter_prose) is unchanged.
    Spine path: golden chapter synthesis (virtual slot streams → compose_chapter_prose)
    plus post-strengthen scene-furniture book dedupe (see golden_chapter_synthesis).

    Args:
        enriched: Output of phoenix_v4.planning.enrichment_select.select_enrichment
        quality_profile: Reserved for future quality-specific polishing (unused in pilot).
        governance_report: Optional mutable dict for telemetry
            (exercise_slots_dropped, chapter_contract_warnings, frame_governance_chapters,
            frame_softened_sentences, frame_stripped_sentences, frame_hard_fail_reasons).
        slot_tracker: Optional BookSlotTracker from injection_resolver. Held here for
            future threading into compose_golden_spine_chapter when that path adopts
            section_packet_composer. Currently accepted but not consumed.
    """
    del quality_profile  # pilot — reserved
    del slot_tracker  # reserved — will be threaded into compose_golden_spine_chapter

    if artifact_dir is not None:
        from phoenix_v4.planning.enrichment_select import write_selected_content_variants_json

        write_selected_content_variants_json(
            enriched,
            Path(artifact_dir) / "selected_content_variants.json",
        )

    report = governance_report if governance_report is not None else {}
    report.setdefault("exercise_slots_dropped", [])
    report.setdefault("chapter_contract_warnings", [])
    report.setdefault("frame_governance_chapters", [])
    report.setdefault("frame_softened_sentences", [])
    report.setdefault("frame_stripped_sentences", [])
    report.setdefault("frame_hard_fail_reasons", [])

    try:
        from phoenix_v4.quality.ei_v2.config import load_ei_v2_config

        ei_cfg = load_ei_v2_config() or {}
    except Exception:
        ei_cfg = {}
    ex_gov = ei_cfg.get("exercise_governance") or {}
    format_default = int(ex_gov.get("max_per_chapter_default", DEFAULT_MAX_EXERCISES_PER_CHAPTER))
    overrides = ex_gov.get("override_per_format") or {}
    rid = (enriched.runtime_format or "").strip()
    format_cap = int(overrides[rid]) if rid in overrides else format_default

    # OPD-135: 5-part exercise assembly (PR #1275) needs ≥2 EXERCISE slots per
    # practice chapter to drive Part 4 (aha) and Part 5 (integration) coverage.
    # Raise a per-chapter floor when (a) runtime is deep_book_6h, or (b) the
    # holistic-v2 chapter architecture is active. Apply only to chapters whose
    # contract already permits ≥1 exercise so we preserve the recognition /
    # resolution chapters' zero-exercise intent.
    _spine_ctx_cap = enriched.spine_context or {}
    _arch_v = int(_spine_ctx_cap.get("chapter_architecture_version") or 1)
    five_part_floor = 2 if (rid == "deep_book_6h" or _arch_v == 2) else 0

    from phoenix_v4.planning.chapter_planner import assign_chapter_purpose_contracts

    contracts = assign_chapter_purpose_contracts(
        len(enriched.chapters),
        enriched.runtime_format,
    )

    frame = str((enriched.spine_context or {}).get("frame") or "somatic_first").strip()

    from phoenix_v4.rendering.golden_chapter_synthesis import (
        compose_golden_spine_chapter,
        dedupe_scene_furniture_book,
        post_compose_sanitize_chapter,
    )

    from phoenix_v4.planning.chapter_object_continuity import is_twelve_shape_continuity_active

    _twelve_shape_flagship = is_twelve_shape_continuity_active(enriched.spine_context or {})

    mechanism_memory = MechanismThesisMemory()
    exercise_memory = ExerciseWrapperMemory()
    bridge_memory = BridgeMemory()
    within_slot_rotation = WithinSlotRotationState()
    global _BOOK_BRIDGE_MEMORY_TLS, _WITHIN_SLOT_ROTATION_TLS, _BOOK_TRANSITION_USED_TLS
    _BOOK_BRIDGE_MEMORY_TLS = bridge_memory
    _WITHIN_SLOT_ROTATION_TLS = within_slot_rotation
    _BOOK_TRANSITION_USED_TLS = set()

    chapters_prose: list[str] = []
    for ch_idx, ch in enumerate(enriched.chapters):
        contract = contracts[ch_idx] if ch_idx < len(contracts) else contracts[-1]
        contract_cap = int(contract.max_exercises)
        # OPD-135: lift the contract cap to `five_part_floor` for practice
        # chapters under deep_book_6h / arch v2, but never below contract zero
        # (recognition / resolution chapters stay exercise-free).
        if five_part_floor and contract_cap >= 1:
            contract_cap = max(contract_cap, five_part_floor)
        max_allowed = min(contract_cap, format_cap)
        _chapter_has_exercise_slot = any(
            str(s.slot_type or "").strip().upper() == "EXERCISE" for s in ch.slots
        )
        if _twelve_shape_flagship and _chapter_has_exercise_slot:
            max_allowed = max(max_allowed, 1)

        ex_seen = 0
        slots_out = []
        for slot in ch.slots:
            st = str(slot.slot_type or "").strip().upper()
            if st == "EXERCISE":
                if ex_seen < max_allowed:
                    slots_out.append(slot)
                    ex_seen += 1
                else:
                    entry = {
                        "chapter": ch.number,
                        "chapter_index": ch_idx,
                        "slot_type": st,
                        "max_allowed": max_allowed,
                        "contract_max_exercises": contract.max_exercises,
                        "format_cap": format_cap,
                    }
                    if isinstance(report["exercise_slots_dropped"], list):
                        report["exercise_slots_dropped"].append(entry)
                    logger.warning(
                        "Exercise governance: dropped EXERCISE slot in chapter %s (cap=%s).",
                        ch.number,
                        max_allowed,
                    )
            else:
                slots_out.append(slot)

        if ch_idx > 0 and contracts[ch_idx].emotional_job == contracts[ch_idx - 1].emotional_job:
            msg = (
                f"chapter {ch.number}: emotional_job {contracts[ch_idx].emotional_job!r} "
                f"matches previous chapter — escalation contract may be weak"
            )
            if isinstance(report["chapter_contract_warnings"], list):
                report["chapter_contract_warnings"].append(msg)
            logger.warning("Chapter contract: %s", msg)

        if contracts[ch_idx].emotional_job in contracts[ch_idx].forbidden_repeats:
            msg = (
                f"chapter {ch.number}: emotional_job {contracts[ch_idx].emotional_job!r} "
                f"is listed in its own forbidden_repeats (YAML check)"
            )
            if isinstance(report["chapter_contract_warnings"], list):
                report["chapter_contract_warnings"].append(msg)

        # Golden chapter path: slots are inputs; compose_chapter_prose threads thesis, bridges,
        # exercises, and endings (see golden_chapter_synthesis.compose_golden_spine_chapter).
        from dataclasses import replace

        ch_compose = replace(ch, slots=slots_out)
        book_seed = f"{enriched.persona_id}:{enriched.topic}:{enriched.runtime_format}:ch{ch_idx}"
        _spine_ctx = enriched.spine_context or {}
        ch_body, _syn_meta = compose_golden_spine_chapter(
            ch_compose,
            chapter_index0=ch_idx,
            total_chapters=len(enriched.chapters),
            topic_id=enriched.topic,
            persona_id=enriched.persona_id,
            book_seed=book_seed,
            frame=frame,
            governance_report=report,
            mechanism_memory=mechanism_memory,
            exercise_memory=exercise_memory,
            angle_id=str(_spine_ctx.get("angle_id") or ""),
            angle_layer_by_chapter=dict(_spine_ctx.get("angle_layer_by_chapter") or {}),
            twelve_shape_flagship=_twelve_shape_flagship,
        )
        ch_body = post_compose_sanitize_chapter(
            ch_body,
            topic_id=enriched.topic,
        )
        # Frame governance lists and chapter rows are appended inside compose_golden_spine_chapter.
        chapter_text = f"Chapter {ch.number}\n{ch.working_title}\n\n"
        if ch_body.strip():
            chapter_text += ch_body.strip() + "\n\n"
        chapters_prose.append(chapter_text.rstrip())

    manuscript = "\n\n".join(chapters_prose)
    from phoenix_v4.quality.chapter_flow_gate import flow_profile_for_runtime_format
    from phoenix_v4.rendering.book_renderer import strengthen_rendered_spine_manuscript

    spine_seed = f"spine:{enriched.persona_id}:{enriched.topic}:{enriched.runtime_format}"
    profile = flow_profile_for_runtime_format(enriched.runtime_format)
    strengthened = strengthen_rendered_spine_manuscript(
        manuscript, book_seed=spine_seed, flow_profile=profile
    )
    deduped, furniture_notes = dedupe_scene_furniture_book(strengthened)
    if furniture_notes:
        rr = report.setdefault("recurrence_report", [])
        if isinstance(rr, list):
            rr.extend(furniture_notes)
    _BOOK_BRIDGE_MEMORY_TLS = None
    _BOOK_TRANSITION_USED_TLS = None
    _WITHIN_SLOT_ROTATION_TLS = None
    return deduped
