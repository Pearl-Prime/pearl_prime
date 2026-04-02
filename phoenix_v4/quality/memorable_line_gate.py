"""
Per-chapter memorable line gate (BG-PR-10).

Honors config/quality/memorable_line_registry_policy.yaml keys under
`memorable_line_registry` that apply to gating (notably block_on_violation,
strength_levels_tracked). That YAML does not define numeric sentence thresholds
or max quote length; those use defaults below and optional overrides if the
policy file gains matching keys later (fail-open, no crash on odd YAML).

Heuristic-only, deterministic, no network/LLM. Heuristics align with
SYSTEM_OWNER_VISION §3 (highlight-worthy lines), Writer Spec §3 (TTS: short,
direct, active), without importing chapter_flow_gate's _AHA_CUES.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_POLICY_PATH = REPO_ROOT / "config" / "quality" / "memorable_line_registry_policy.yaml"

# Ordering for strength_levels_tracked names (registry uses good/great for catalog tiers).
_TIER_RANK = {"fair": 0, "good": 1, "great": 2}

WORD_RE = re.compile(r"\b[\w']+\b")
SENTENCE_SPLIT_RE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])")

# Contrast / naming (regex — not the same structure as chapter_flow_gate._AHA_CUES)
_CONTRAST_PATTERNS = (
    re.compile(r"\bnot\b.+\bbut\b", re.I | re.DOTALL),
    re.compile(r"\bnot\s+the\s+problem\b", re.I),
    re.compile(r"\bthe\s+real\s+\w+", re.I),
    re.compile(r"\bwhat\s+you\s+call\b", re.I),
    re.compile(r"\binstead\b", re.I),
    re.compile(r"\bthis\s+isn't\b.+\bthis\s+is\b", re.I | re.DOTALL),
)
_HEDGE_RE = re.compile(
    r"\b(?:perhaps|maybe|might|could be|may be|it'?s possible|"
    r"sometimes|often|generally|usually|tends to|seems to|kind of|sort of)\b",
    re.I,
)
_PASSIVE_RE = re.compile(
    r"\b(?:am|is|are|was|were|been|being)\s+[\w']+ed\b",
    re.I,
)
_WEAK_MODAL_RE = re.compile(r"\b(?:might|could|would)\s+be\b", re.I)

_BODY_SENSORY = frozenset({
    "chest", "breath", "breathing", "jaw", "throat", "shoulder", "shoulders",
    "stomach", "heart", "hands", "neck", "skin", "eyes", "voice", "pulse",
    "tight", "tension", "ache", "nausea", "sweat", "heat", "cold", "shaking",
    "body", "muscle", "spine", "gut",
})
_CONCRETE_NOUN_HINTS = frozenset({
    "kitchen", "phone", "car", "door", "desk", "message", "night", "morning",
    "boss", "partner", "kid", "mother", "father", "street", "email", "text",
})
_GENERIC_ABSTRACT = frozenset({
    "things", "something", "anything", "everything", "nothing", "people",
    "someone", "everyone", "life", "world", "situation", "stuff", "issue",
    "matters", "difficult", "hard", "struggle", "challenges",
})


@dataclass
class MemorableLineResult:
    status: str  # PASS, WARN, FAIL
    memorable_line_count: int
    best_candidates: list[str] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


def _deep_merge_base(defaults: dict[str, Any], over: dict[str, Any]) -> dict[str, Any]:
    out = dict(defaults)
    for k, v in over.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge_base(out[k], v)
        else:
            out[k] = v
    return out


def _policy_defaults() -> dict[str, Any]:
    """Defaults when YAML is missing or incomplete. Numeric keys are gate-only (not in current policy)."""
    return {
        "memorable_line_registry": {
            "block_on_violation": True,
            "strength_levels_tracked": ["good", "great"],
            # Gate tuning — not in registry YAML today; can be overridden by policy if added
            "max_words_per_candidate": 20,
            "min_score_for_tracked": 4.0,
            "min_score_for_great": 5.75,
        },
    }


def load_memorable_line_policy(policy_path: Optional[Path]) -> tuple[dict[str, Any], list[str]]:
    """
    Load policy dict with defaults merged. Returns (effective policy, load warnings).
    Never raises; fail-open.
    """
    warnings: list[str] = []
    base = _policy_defaults()
    path = policy_path
    if path is None:
        path = DEFAULT_POLICY_PATH

    if not path.exists():
        warnings.append(f"memorable_line_policy missing: {path}; using defaults")
        logger.warning("%s", warnings[-1])
        return base, warnings

    try:
        import yaml  # type: ignore
    except ImportError:
        warnings.append("PyYAML not installed; using policy defaults")
        logger.warning("%s", warnings[-1])
        return base, warnings

    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except Exception as e:
        warnings.append(f"policy parse failed ({path}): {e}; using defaults")
        logger.warning("%s", warnings[-1])
        return base, warnings

    if not isinstance(raw, dict):
        warnings.append(f"policy root not a mapping ({path}); using defaults")
        logger.warning("%s", warnings[-1])
        return base, warnings

    mlr = raw.get("memorable_line_registry")
    if mlr is None:
        warnings.append(f"no memorable_line_registry key in {path}; using defaults")
        logger.warning("%s", warnings[-1])
        return base, warnings

    if not isinstance(mlr, dict):
        warnings.append(f"memorable_line_registry not a mapping in {path}; using defaults")
        logger.warning("%s", warnings[-1])
        return base, warnings

    merged = _deep_merge_base(base, {"memorable_line_registry": mlr})
    return merged, warnings


def _normalized_tiers(levels: list[Any]) -> list[str]:
    out: list[str] = []
    for x in levels or []:
        if isinstance(x, str) and x.strip():
            out.append(x.strip().lower())
    return out


def _candidate_thresholds_from_policy(mlr: dict[str, Any]) -> tuple[float, float, int]:
    """
    Returns (min_score_to_count_as_candidate, great_score_floor, max_words).
    great_score_floor is informational for metrics; counting uses min_score only.
    """
    max_words = int(mlr.get("max_words_per_candidate") or 20)
    min_tracked = float(mlr.get("min_score_for_tracked") or 4.0)
    great_min = float(mlr.get("min_score_for_great") or 5.75)

    levels = _normalized_tiers(list(mlr.get("strength_levels_tracked") or ["good", "great"]))
    if levels:
        ranked = sorted(levels, key=lambda s: _TIER_RANK.get(s, 0))
        low_name = ranked[0] if ranked else "good"
        if low_name == "great" and len(ranked) == 1:
            min_tracked = max(min_tracked, great_min)
    return min_tracked, great_min, max_words


def _count_words(s: str) -> int:
    return len(WORD_RE.findall(s))


def _split_sentences(text: str) -> list[str]:
    t = text.strip()
    if not t:
        return []
    parts = SENTENCE_SPLIT_RE.split(t)
    out: list[str] = []
    for p in parts:
        p = p.strip()
        if len(p) < 8:
            continue
        out.append(p)
    return out


def score_sentence(s: str, max_words: int) -> tuple[float, list[str]]:
    """Deterministic score and tags for one sentence."""
    tags: list[str] = []
    lower = s.lower()
    wc = _count_words(s)
    score = 0.0

    if wc <= 0:
        return 0.0, ["EMPTY"]

    if 6 <= wc <= max_words:
        score += 2.5
        tags.append("LENGTH_QUOTABLE")
    elif wc <= max_words + 5:
        score += 1.0
        tags.append("LENGTH_OK")
    else:
        score -= 1.5
        tags.append("LENGTH_LONG")

    for rx in _CONTRAST_PATTERNS:
        if rx.search(s):
            score += 2.25
            tags.append("CONTRAST_OR_NAMING")
            break

    tokens = {w.lower() for w in WORD_RE.findall(s)}
    if tokens & _BODY_SENSORY:
        score += 1.25
        tags.append("BODY_OR_SENSORY")
    if tokens & _CONCRETE_NOUN_HINTS:
        score += 1.0
        tags.append("CONCRETE_DETAIL")
    generic_hits = len(tokens & _GENERIC_ABSTRACT)
    if generic_hits >= 2 or (generic_hits >= 1 and wc <= 12):
        score -= 2.0
        tags.append("GENERIC_ABSTRACT")

    if _HEDGE_RE.search(s):
        score -= 1.75
        tags.append("HEDGE_OR_VAGUE")
    if _WEAK_MODAL_RE.search(s):
        score -= 0.75
        tags.append("WEAK_MODAL")
    if _PASSIVE_RE.search(s):
        score -= 1.25
        tags.append("PASSIVE_PATTERN")

    if "?" in s:
        score -= 1.0
        tags.append("QUESTION_MARK")

    if re.search(r"\byour\b", lower) and re.search(r"\b(not|instead|real|call)\b", lower):
        score += 0.75
        tags.append("DIRECT_NAMING")

    return round(score, 4), tags


def evaluate_memorable_lines(
    chapter_text: str,
    *,
    policy_path: Optional[Path] = None,
) -> MemorableLineResult:
    """
    Run memorable-line gate for one chapter's prose. Policy drives block_on_violation
    and tier names; numeric thresholds use merged defaults unless policy supplies them.
    """
    policy, load_warnings = load_memorable_line_policy(policy_path)
    mlr = policy.get("memorable_line_registry") or {}
    block = bool(mlr.get("block_on_violation", True))
    min_score, great_min, max_words = _candidate_thresholds_from_policy(mlr)

    issues: list[str] = list(load_warnings)
    metrics: dict[str, Any] = {
        "block_on_violation": block,
        "min_score_for_candidate": min_score,
        "min_score_for_great_tier": great_min,
        "max_words_per_candidate": max_words,
        "strength_levels_tracked": _normalized_tiers(list(mlr.get("strength_levels_tracked") or [])),
    }

    text = (chapter_text or "").strip()
    if not text:
        issues.append("EMPTY_CHAPTER")
        st = "FAIL" if block else "WARN"
        metrics["sentence_count"] = 0
        return MemorableLineResult(st, 0, [], issues, metrics)

    sentences = _split_sentences(text)
    metrics["sentence_count"] = len(sentences)

    scored: list[tuple[float, str, list[str]]] = []
    for sent in sentences:
        sc, tags = score_sentence(sent, max_words)
        scored.append((sc, sent, tags))

    candidates = [(sc, sent) for sc, sent, _ in scored if sc >= min_score]
    metrics["raw_top_score"] = max((sc for sc, _, _ in scored), default=0.0)
    metrics["candidate_count"] = len(candidates)

    # Top 3 by score, deterministic tie-break
    candidates.sort(key=lambda x: (-x[0], x[1]))
    seen: set[str] = set()
    best: list[str] = []
    for sc, sent in candidates:
        if sent not in seen and len(best) < 3:
            best.append(sent)
            seen.add(sent)

    count = len(candidates)
    if count == 0:
        issues.append("NO_MEMORABLE_LINE_CANDIDATES")
        status = "FAIL" if block else "WARN"
    else:
        status = "PASS"

    metrics["best_candidate_scores"] = [
        {"text": sent, "score": sc} for sc, sent in candidates[:3]
    ]

    return MemorableLineResult(
        status=status,
        memorable_line_count=count,
        best_candidates=best,
        issues=issues,
        metrics=metrics,
    )
