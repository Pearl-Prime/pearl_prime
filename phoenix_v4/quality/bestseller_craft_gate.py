"""
Bestseller craft gate — Orient / Name / Turn / Give / Pull (ONTGP) heuristics.

Maps to docs/PEARL_PRIME_BESTSELLER_WRITING_OVERLAY_SPEC.md §4. Structural signals
only; optional LLM refinement via call_llm_json (callback contract, no network here).

Deterministic: same chapter_text + thresholds → same result.
"""
from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Dict, List, Optional, Union

from phoenix_v4.quality.ei_v2.dimension_gates import BODY_WORDS

# --- Overlay §4 diagnostic questions (LLM tier contract) ---

DIAGNOSTIC_QUESTIONS: Dict[str, str] = {
    "orient": (
        "Can you describe the physical or emotional space the reader is in after the first 30 seconds? "
        "If they only understand the topic, orient failed — they must be in something, not informed."
    ),
    "name": (
        "Is there a single sentence in the STORY or PIVOT that the reader could screenshot and send "
        "to a friend with 'this is me'? If no sentence has that quality, naming is too diffuse."
    ),
    "turn": (
        "After PIVOT and early REFLECTION, does the reader's model of their own situation change? "
        "If they think the same thing before and after, there was no turn."
    ),
    "give": (
        "Could the reader do the exercise right now, in the next 60 seconds, without equipment? "
        "If 'sort of' or 'with interpretation,' the give is not concrete enough."
    ),
    "pull": (
        "After INTEGRATION + THREAD, does the reader have a specific question they want answered — "
        "a named, articulable tension? If the pull is vague, the thread failed."
    ),
}

# Thresholds and zone sizing: overridable via ``thresholds`` in evaluate_bestseller_craft.
DEFAULT_THRESHOLDS: Dict[str, Union[float, int]] = {
    "fail_below": 0.2,
    "warn_below": 0.4,
    "orient_word_span": 150,
    "pull_word_span": 100,
    "name_start_frac": 0.12,
    "name_end_frac": 0.45,
    "turn_start_frac": 0.22,
    "turn_end_frac": 0.58,
    "give_start_frac": 0.48,
}

_SPATIAL_TEMPORAL = frozenset({
    "now", "here", "today", "tonight", "morning", "evening", "door", "floor", "room",
    "street", "traffic", "train", "desk", "phone", "window", "hallway", "kitchen",
    "bed", "chair", "elevator", "message", "ping", "alarm",
})

_ORIENT_BODY = BODY_WORDS | frozenset({
    "hand", "hands", "feet", "neck", "throat", "skin", "eyes", "ears", "finger", "fingers",
    "wrist", "spine", "ribs", "forehead", "cheek", "lip", "lips",
})

_ABSTRACT_TOPIC_PATTERNS = re.compile(
    r"(?is)\b(this chapter is about|in this chapter|today we will|we will explore|"
    r"let\'s discuss|throughout this (chapter|section)|anxiety is a|burnout happens when|"
    r"self[\s-]?worth means)\b",
)

_NAME_PATTERNS = [
    re.compile(r"\bnot\s+[^,.]{1,40}\s*,\s*but\s+", re.I),
    re.compile(r"\bthe real \w+ is\b", re.I),
    re.compile(r"\bwhat you call\b", re.I),
    re.compile(r"\bactually\b.+\b(is|was|means)\b", re.I),
    re.compile(r"\bthe pattern is\b", re.I),
]

_TURN_MARKERS = re.compile(
    r"(?is)(\bbut\b|\bexcept\b|the problem is not|what actually happens|this is why|"
    r"instead of|not because|the truth is|you thought|you assumed|"
    r"the cost is not|it was never|that is not what)\b",
)
_NEGATION_ASSERTION = re.compile(
    r"(?is)\b(?:not|never|no)\b[^.!?]{0,80}\b(?:is|are|was|were|does|did|will|means)\b",
)

_GIVE_IMPERATIVE = re.compile(
    r"(?i)(?:^|[.!?]\s+|\n)\s*(place|feel|notice|breathe|write|say|press|name|choose|count|"
    r"sit|stand|exhale|inhale|lift|lower|hold|track|whisper|read|list)\b",
)
_GIVE_TIME_BOUND = re.compile(
    r"\b(right now|for (?:ten|10|four|4|six|6|three|3) (?:seconds|counts|breaths)|"
    r"next sixty seconds|within a minute)\b",
    re.I,
)
_GIVE_VAGUE = re.compile(
    r"\b(try to relax|try to|maybe you could|sort of|consider whether|"
    r"think about when you have time|whenever you can)\b",
    re.I,
)

_PULL_GENERIC = re.compile(
    r"(?is)\b(there is more to explore|more to this journey|we will continue|"
    r"in the next chapter|stay tuned|coming up we)\b",
)
_PULL_STRONG = re.compile(
    r"(?is)(\?|what happens when|you have not yet|still yours|the harder thing|"
    r"who benefits when|what you have not yet named|which part of you)\b",
)


def _words(text: str) -> List[str]:
    return (text or "").split()


def _slice_by_words(text: str, start: int, end: int) -> str:
    w = _words(text)
    if start >= len(w):
        return ""
    return " ".join(w[start : min(end, len(w))])


def _clamp01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _score_orient(zone: str) -> tuple[float, List[str], List[str]]:
    issues: List[str] = []
    remed: List[str] = []
    z = (zone or "").strip()
    words = z.split()
    if len(words) < 12:
        issues.append("orient_zone_too_short_for_placement")
        return 0.1, issues, remed

    low = z.lower()
    wl = set(re.findall(r"\w+", low))

    if _ABSTRACT_TOPIC_PATTERNS.search(low[:400]):
        issues.append("abstract_topic_or_essay_opener_in_orient_zone")
        abstract_penalty = 0.55
    else:
        abstract_penalty = 0.0

    body_hits = len(wl & {b.lower() for b in _ORIENT_BODY})
    you_hits = len(re.findall(r"\b(you|your|you're|you are)\b", low))
    st_hits = sum(1 for t in _SPATIAL_TEMPORAL if t in low)

    body_part = _clamp01(body_hits / 5.0)
    you_part = _clamp01(you_hits / 6.0)
    place_part = _clamp01(st_hits / 4.0)

    raw = 0.38 * body_part + 0.32 * you_part + 0.18 * place_part + 0.12 * (1.0 - abstract_penalty)
    score = _clamp01(raw)

    if score < 0.35:
        remed.append("Open with body, place, or moment — not topic summary (overlay §5).")
    return score, issues, remed


def _name_candidate_sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _score_name(zone: str) -> tuple[float, List[str], List[str]]:
    issues: List[str] = []
    remed: List[str] = []
    z = (zone or "").strip()
    if len(z.split()) < 25:
        issues.append("name_zone_too_thin")
        return 0.12, issues, remed

    pat_hits = sum(1 for p in _NAME_PATTERNS if p.search(z))
    sentences = _name_candidate_sentences(z)
    short_punchy = 0
    for s in sentences:
        wc = len(s.split())
        if wc <= 15 and wc >= 4:
            if re.search(r"\b(is|was|means|cost|pattern|call|name|truth)\b", s, re.I):
                short_punchy += 1

    pattern_score = _clamp01(pat_hits / 2.5)
    punch_score = _clamp01(short_punchy / 3.0)
    score = _clamp01(0.55 * pattern_score + 0.45 * punch_score)

    if score < 0.35:
        remed.append("Add one screenshot-worthy naming line — contrast, reversal, or pattern (overlay §4 Name).")
    return score, issues, remed


def _score_turn(zone: str) -> tuple[float, List[str], List[str]]:
    issues: List[str] = []
    remed: List[str] = []
    z = (zone or "").strip()
    if len(z.split()) < 20:
        issues.append("turn_zone_too_thin")
        return 0.1, issues, remed

    markers = len(_TURN_MARKERS.findall(z))
    markers += len(_NEGATION_ASSERTION.findall(z))
    but_count = len(re.findall(r"\bbut\b", z.lower()))
    score = _clamp01(0.35 + 0.12 * min(markers, 6) + 0.08 * min(but_count, 4))
    if markers < 1 and but_count < 1:
        issues.append("few_reframe_or_contrast_markers")
        score = min(score, 0.35)

    if score < 0.35:
        remed.append("Introduce a clear reframe or contradiction — reader model should shift (overlay §4 Turn).")
    return score, issues, remed


def _score_give(zone: str) -> tuple[float, List[str], List[str]]:
    issues: List[str] = []
    remed: List[str] = []
    z = (zone or "").strip()
    lines = [ln.strip() for ln in z.splitlines() if ln.strip()]
    imperatives = sum(1 for ln in lines if _GIVE_IMPERATIVE.search(ln))
    imperatives = max(imperatives, len(_GIVE_IMPERATIVE.findall(z)))
    vague_hits = len(_GIVE_VAGUE.findall(z))
    time_hits = len(_GIVE_TIME_BOUND.findall(z))

    if vague_hits >= 2:
        issues.append("vague_exercise_language")
    imp_score = _clamp01(imperatives / 4.0)
    time_score = _clamp01(time_hits / 2.0)
    vague_penalty = _clamp01(vague_hits / 3.0)

    score = _clamp01(0.55 * imp_score + 0.35 * time_score + 0.1 * (1.0 - vague_penalty))
    if imperatives < 1:
        score = min(score, 0.28)
        issues.append("no_clear_imperatives_in_give_zone")

    if score < 0.35:
        remed.append("Use concrete imperatives and time bounds the reader can do now (overlay §4 Give).")
    return score, issues, remed


def _score_pull(zone: str) -> tuple[float, List[str], List[str]]:
    issues: List[str] = []
    remed: List[str] = []
    z = (zone or "").strip()
    if len(z.split()) < 15:
        issues.append("pull_zone_too_short")
        return 0.1, issues, remed

    gen_hits = len(_PULL_GENERIC.findall(z))
    strong_hits = len(_PULL_STRONG.findall(z))
    q_marks = z.count("?")

    if gen_hits >= 1:
        issues.append("generic_thread_or_explore_closer")
        score = _clamp01(0.15 + 0.2 * strong_hits + 0.05 * min(q_marks, 2))
    else:
        score = _clamp01(0.35 + 0.2 * strong_hits + 0.1 * min(q_marks, 3))

    if strong_hits < 1 and q_marks < 1:
        score = min(score, 0.32)
        issues.append("no_named_tension_or_question_in_closer")

    if score < 0.35:
        remed.append("End with a named tension or sharp question — not a teaser slogan (overlay §7).")
    return score, issues, remed


def _merge_llm_scores(
    heuristic: Dict[str, float],
    chapter_text: str,
    call_llm_json: Optional[Callable[[str, str, str], dict]],
) -> Dict[str, float]:
    """
    Optional LLM tier: ``call_llm_json(chapter_text, move_name, diagnostic_question)``
    → ``{"score": float, "reasoning": str, ...}``. No network here; caller supplies the callback.
    """
    if call_llm_json is None:
        return heuristic
    out = dict(heuristic)
    for move in ("orient", "name", "turn", "give", "pull"):
        try:
            resp = call_llm_json(chapter_text, move, DIAGNOSTIC_QUESTIONS[move])
        except Exception:
            continue
        if isinstance(resp, dict) and "score" in resp:
            try:
                out[move] = _clamp01(float(resp["score"]))
            except (TypeError, ValueError):
                pass
    return out


def _overall_status(
    scores: Dict[str, float],
    thresholds: Dict[str, Any],
) -> tuple[str, List[str]]:
    fail_b = float(thresholds.get("fail_below", DEFAULT_THRESHOLDS["fail_below"]))
    warn_b = float(thresholds.get("warn_below", DEFAULT_THRESHOLDS["warn_below"]))
    issues: List[str] = []
    mins = min(scores.values()) if scores else 0.0
    worst = [m for m, s in scores.items() if s < fail_b]
    warn_m = [m for m, s in scores.items() if fail_b <= s < warn_b]

    if worst:
        issues.append(f"move_fail:{','.join(worst)}")
        return "FAIL", issues
    if warn_m:
        issues.append(f"move_warn:{','.join(warn_m)}")
        return "WARN", issues
    if mins < warn_b:
        return "WARN", issues
    return "PASS", issues


@dataclass(frozen=True)
class CraftGateResult:
    status: str
    move_scores: Dict[str, float] = field(default_factory=dict)
    issues: List[str] = field(default_factory=list)
    remediation: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def evaluate_bestseller_craft(
    chapter_text: str,
    *,
    thresholds: Optional[Dict[str, Any]] = None,
    call_llm_json: Optional[Callable[[str, str, str], dict]] = None,
) -> CraftGateResult:
    """
    Heuristic ONTGP evaluation. Optional ``call_llm_json(chapter_text, move_name, diagnostic_question)``
    returns a dict with at least ``score`` in [0, 1]; when absent or invalid, heuristic scores stand.
    """
    thr: Dict[str, Any] = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    orient_words = int(thr.get("orient_word_span", DEFAULT_THRESHOLDS["orient_word_span"]))
    pull_words = int(thr.get("pull_word_span", DEFAULT_THRESHOLDS["pull_word_span"]))
    name_sf = float(thr.get("name_start_frac", DEFAULT_THRESHOLDS["name_start_frac"]))
    name_ef = float(thr.get("name_end_frac", DEFAULT_THRESHOLDS["name_end_frac"]))
    turn_sf = float(thr.get("turn_start_frac", DEFAULT_THRESHOLDS["turn_start_frac"]))
    turn_ef = float(thr.get("turn_end_frac", DEFAULT_THRESHOLDS["turn_end_frac"]))
    give_sf = float(thr.get("give_start_frac", DEFAULT_THRESHOLDS["give_start_frac"]))
    text = (chapter_text or "").strip()
    all_issues: List[str] = []
    all_remed: List[str] = []
    metrics: Dict[str, Any] = {}

    if not text:
        return CraftGateResult(
            "FAIL",
            {k: 0.0 for k in ("orient", "name", "turn", "give", "pull")},
            ["empty_chapter"],
            ["Provide chapter prose to evaluate."],
            {"word_count": 0},
        )

    words = _words(text)
    n = len(words)
    metrics["word_count"] = n

    orient_zone = _slice_by_words(text, 0, min(orient_words, n))
    name_zone = _slice_by_words(text, int(n * name_sf), int(n * name_ef))
    turn_zone = _slice_by_words(text, int(n * turn_sf), int(n * turn_ef))
    give_zone = _slice_by_words(text, int(n * give_sf), n)
    pull_zone = _slice_by_words(text, max(0, n - pull_words), n)

    metrics["zones"] = {
        "orient_words": len(orient_zone.split()),
        "name_words": len(name_zone.split()),
        "turn_words": len(turn_zone.split()),
        "give_words": len(give_zone.split()),
        "pull_words": len(pull_zone.split()),
    }

    o_s, o_i, o_r = _score_orient(orient_zone)
    n_s, n_i, n_r = _score_name(name_zone)
    t_s, t_i, t_r = _score_turn(turn_zone)
    g_s, g_i, g_r = _score_give(give_zone)
    p_s, p_i, p_r = _score_pull(pull_zone)

    all_issues.extend(o_i + n_i + t_i + g_i + p_i)

    all_remed.extend(o_r + n_r + t_r + g_r + p_r)

    heuristic_scores = {
        "orient": round(o_s, 4),
        "name": round(n_s, 4),
        "turn": round(t_s, 4),
        "give": round(g_s, 4),
        "pull": round(p_s, 4),
    }
    metrics["heuristic_scores"] = dict(heuristic_scores)

    move_scores = _merge_llm_scores(heuristic_scores, text, call_llm_json)
    metrics["final_move_scores"] = dict(move_scores)
    if call_llm_json is not None:
        metrics["llm_tier"] = "callback_invoked"

    status, st_issues = _overall_status(move_scores, thr)
    all_issues = st_issues + all_issues

    return CraftGateResult(
        status=status,
        move_scores=move_scores,
        issues=all_issues,
        remediation=all_remed,
        metrics=metrics,
    )
