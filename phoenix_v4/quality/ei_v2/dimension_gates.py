"""
EI V2 dimension gates: per-chapter quality gates (uniqueness, engagement,
somatic precision, cohesion, listen_experience). Used for chapter-level
validation; selective block per blocked_dimensions when fail_mode is block.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Any, List

from phoenix_v4.quality.ei_v2.tts_readability import _syllable_estimate, score_tts_readability

# Body-word set for somatic precision (align with ei_adapter)
BODY_WORDS = frozenset({
    "shoulder", "shoulders", "breath", "breathing", "stomach", "jaw", "chest",
    "heart", "racing", "tight", "tensed", "tension", "relax", "release",
    "ground", "grounded", "body", "sensation", "felt", "feeling",
})

# Ordered longest-first so shorter phrases do not hide longer matches in counting.
COHESION_TRANSITIONAL_PHRASES: tuple[str, ...] = tuple(
    sorted(
        (
            "as we have seen",
            "in the previous chapter",
            "in the last chapter",
            "as we've seen",
            "as we saw",
            "remember when",
            "building on",
            "building from",
            "that pattern",
            "as discussed",
            "earlier we",
            "from the last",
            "from last time",
            "earlier",
        ),
        key=len,
        reverse=True,
    )
)


def _norm_dimension_gate_name(name: str) -> str:
    return str(name).strip().lower().replace("-", "_")


def _parse_blocked_dimensions_list(raw: Any) -> list[str]:
    if raw is None:
        return []
    if isinstance(raw, (str, bytes)):
        return []
    if not isinstance(raw, (list, tuple)):
        return []
    out: list[str] = []
    for x in raw:
        s = str(x).strip()
        if s:
            out.append(s)
    return out


def _cohesion_significant_words(text: str) -> set[str]:
    return {w for w in re.findall(r"\w+", text.lower()) if len(w) >= 3}


@dataclass
class GateResult:
    dimension: str
    status: str  # PASS, WARN, FAIL
    score: float
    issues: List[str] = field(default_factory=list)
    remediation: List[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dimension": self.dimension,
            "status": self.status,
            "score": self.score,
            "issues": self.issues,
            "remediation": self.remediation,
        }


def gate_uniqueness(text: str, other_texts: List[str], chapter_index: int) -> GateResult:
    """Score uniqueness of this chapter text vs others (avoid duplicate phrasing)."""
    if not text or not text.strip():
        return GateResult("uniqueness", "WARN", 0.0, issues=["empty text"])
    text_lower = text.lower().strip()
    words = set(re.findall(r"\w+", text_lower))
    if len(words) < 5:
        return GateResult("uniqueness", "WARN", 0.5, issues=["very short text"])
    score = 1.0
    issues = []
    for other in other_texts:
        if not other:
            continue
        other_words = set(re.findall(r"\w+", other.lower()))
        overlap = len(words & other_words) / max(len(words), 1)
        if overlap > 0.7:
            score = min(score, 0.29)
            issues.append("high overlap with another chapter")
    status = "PASS" if score >= 0.6 else ("WARN" if score >= 0.3 else "FAIL")
    return GateResult("uniqueness", status, round(score, 3), issues=issues)


def gate_cohesion(
    text: str,
    other_texts: List[str],
    chapter_index: int,
    cohesion_cfg: dict[str, Any] | None = None,
) -> GateResult:
    """Score backward linkage to the immediately prior chapter.

    ``other_texts`` must follow ``book_renderer`` order: all composed chapters
    except the current, in ascending original index order. The prior chapter
    is then ``other_texts[chapter_index - 1]`` when ``chapter_index > 0``.
    """
    cfg = cohesion_cfg or {}
    min_refs = int(cfg.get("min_cross_chapter_refs", 1))
    pass_t = float(cfg.get("pass_threshold", 0.40))
    warn_t = float(cfg.get("warn_threshold", 0.25))

    if not text or not text.strip():
        return GateResult("cohesion", "WARN", 0.0, issues=["empty text"])

    if chapter_index <= 0:
        return GateResult("cohesion", "PASS", 1.0)

    prior: str | None = None
    if chapter_index > 0 and len(other_texts) >= chapter_index:
        prior = other_texts[chapter_index - 1]
    elif chapter_index > 0 and other_texts:
        prior = other_texts[min(chapter_index - 1, len(other_texts) - 1)]

    if not prior or not str(prior).strip():
        return GateResult(
            "cohesion",
            "WARN",
            round(warn_t, 3),
            issues=["prior chapter text unavailable"],
        )

    text_lower = text.lower()
    phrase_hits = sum(1 for p in COHESION_TRANSITIONAL_PHRASES if p in text_lower)

    curr = _cohesion_significant_words(text)
    pr = _cohesion_significant_words(prior)
    overlap_ratio = len(curr & pr) / max(len(curr), 1)

    ref_strength = min(1.0, phrase_hits / float(max(min_refs, 1)))
    overlap_strength = min(1.0, overlap_ratio / 0.20)
    score = round(0.5 * ref_strength + 0.5 * overlap_strength, 3)

    signals = phrase_hits + (1 if overlap_ratio >= 0.05 else 0)
    if signals < min_refs:
        score = min(score, warn_t - 0.02)

    if score >= pass_t:
        status = "PASS"
    elif score >= warn_t:
        status = "WARN"
    else:
        status = "FAIL"

    issues: list[str] = []
    if status != "PASS":
        issues.append("weak backward link to prior chapter")
    return GateResult("cohesion", status, score, issues=issues)


def gate_engagement(text: str, chapter_index: int) -> GateResult:  # noqa: ARG001
    """Minimum engagement: sentence variety and length."""
    if not text or not text.strip():
        return GateResult("engagement", "FAIL", 0.0, issues=["empty text", "too short"])
    text = text.strip()
    word_count = len(text.split())
    if word_count < 15:
        return GateResult(
            "engagement", "FAIL", 0.0,
            issues=["too short", f"word count {word_count} below minimum 15"],
        )
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) < 2:
        return GateResult("engagement", "WARN", 0.5, issues=["single sentence"])
    score = min(1.0, word_count / 80.0)
    status = "PASS" if score >= 0.5 else "WARN"
    return GateResult("engagement", status, round(score, 3))


def gate_somatic_precision(text: str) -> GateResult:
    """Body-word presence for somatic-heavy content."""
    if not text or not text.strip():
        return GateResult("somatic_precision", "WARN", 0.0, issues=["empty text"])
    text_lower = text.lower()
    words = set(re.findall(r"\w+", text_lower))
    body_hits = len(words & BODY_WORDS)
    score = min(1.0, body_hits / 4.0)
    if score < 0.2:
        return GateResult(
            "somatic_precision", "WARN" if score > 0 else "FAIL",
            round(score, 3),
            issues=["few or no body/sensation words"],
        )
    status = "PASS" if score >= 0.3 else "WARN"
    return GateResult("somatic_precision", status, round(score, 3))


def _listen_words(text: str) -> list[str]:
    return re.findall(r"\b[\w'-]+\b", (text or "").lower())


def _ear_friendly_jargon_score(words: list[str]) -> float:
    """Higher = friendlier for listening: penalize first-seen words with >=5 syllables."""
    if not words:
        return 1.0
    syllable_min = 5
    seen_long: set[str] = set()
    weighted = 0.0
    for w in words:
        if _syllable_estimate(w) < syllable_min:
            continue
        if w not in seen_long:
            seen_long.add(w)
            weighted += 1.0
        else:
            weighted += 0.2
    density = weighted / len(words)
    return max(0.0, 1.0 - min(1.0, density * 10.0))


def _audio_repetition_score(words: list[str], window: int, ngram_n: int) -> float:
    """Higher = less grating repetition: duplicate word n-grams inside sliding windows."""
    if len(words) < window or window < ngram_n + 1:
        return 1.0
    bad = 0
    total = 0
    for start in range(0, len(words) - window + 1):
        chunk = words[start : start + window]
        ngrams = [tuple(chunk[i : i + ngram_n]) for i in range(len(chunk) - ngram_n + 1)]
        counts = Counter(ngrams)
        total += 1
        if any(c >= 2 for c in counts.values()):
            bad += 1
    frac = bad / max(1, total)
    return max(0.0, 1.0 - min(1.0, frac * 2.5))


def gate_listen_experience(text: str, listen_cfg: dict[str, Any] | None = None) -> GateResult:
    """Audio-listening quality using tts_readability signals plus jargon and repetition heuristics."""
    cfg = listen_cfg or {}
    pass_t = float(cfg.get("pass_threshold", 0.5))
    warn_t = float(cfg.get("warn_threshold", 0.3))
    tts_subcfg = cfg.get("tts_readability") if isinstance(cfg.get("tts_readability"), dict) else None
    rep_window = int(cfg.get("repetition_window_words", 200))
    rep_n = int(cfg.get("repetition_ngram_words", 4))

    if not text or not text.strip():
        return GateResult("listen_experience", "WARN", 0.0, issues=["empty text"])

    tts = score_tts_readability(text.strip(), cfg=tts_subcfg)
    dims = tts.get("dimensions") or {}
    rhythm = float(dims.get("rhythm_variance", 0.0))
    para = float(dims.get("paragraph_breathing", 0.0))
    tts_safe = float(dims.get("tts_pattern_safety", 0.0))

    words = _listen_words(text)
    jargon = _ear_friendly_jargon_score(words)
    repetition = _audio_repetition_score(words, rep_window, rep_n)

    composite = (
        0.22 * rhythm
        + 0.22 * para
        + 0.22 * tts_safe
        + 0.18 * jargon
        + 0.16 * repetition
    )
    composite = round(max(0.0, min(1.0, composite)), 3)

    issues: list[str] = []
    if rhythm < 0.35:
        issues.append("low sentence rhythm variance for listening")
    if para < 0.45:
        issues.append("paragraph breaks too sparse or too choppy for breath pacing")
    if tts_safe < 0.7:
        issues.append("TTS-hostile patterns detected")
    if jargon < 0.55:
        issues.append("high jargon / long-word density for ear")
    if repetition < 0.55:
        issues.append("phrase repetition within short listening distance")
    for issue in (tts.get("issues") or [])[:6]:
        if isinstance(issue, str) and issue not in issues:
            issues.append(issue)

    if composite >= pass_t:
        status = "PASS"
    elif composite >= warn_t:
        status = "WARN"
    else:
        status = "FAIL"

    return GateResult("listen_experience", status, composite, issues=issues)


@dataclass
class ChapterGateReport:
    chapter_index: int
    gates: List[GateResult]
    overall_status: str
    fail_count: int
    warn_count: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "chapter_index": self.chapter_index,
            "gates": [g.to_dict() for g in self.gates],
            "overall_status": self.overall_status,
            "fail_count": self.fail_count,
            "warn_count": self.warn_count,
        }


@dataclass
class DimensionGatesRunReport:
    """Aggregated per-chapter dimension gate run with selective delivery blocking."""

    chapter_index: int
    gates: List[GateResult]
    overall_status: str
    fail_count: int
    warn_count: int
    blocks_delivery: bool
    dimension_gate_phase: int
    fail_mode: str
    blocked_dimensions: List[str]

    def to_dict(self) -> dict[str, Any]:
        blocked_norm = frozenset(_norm_dimension_gate_name(x) for x in self.blocked_dimensions)
        gates_out: list[dict[str, Any]] = []
        for g in self.gates:
            row = g.to_dict()
            row["dimension_gate_phase"] = self.dimension_gate_phase
            row["contributes_to_delivery_block"] = (
                self.fail_mode == "block"
                and bool(blocked_norm)
                and g.status == "FAIL"
                and _norm_dimension_gate_name(g.dimension) in blocked_norm
            )
            gates_out.append(row)
        return {
            "chapter_index": self.chapter_index,
            "gates": gates_out,
            "overall_status": self.overall_status,
            "fail_count": self.fail_count,
            "warn_count": self.warn_count,
            "blocks_delivery": self.blocks_delivery,
            "dimension_gate_phase": self.dimension_gate_phase,
            "fail_mode": self.fail_mode,
            "blocked_dimensions": self.blocked_dimensions,
        }


def run_chapter_dimension_gates(
    text: str,
    other_texts: List[str],
    chapter_index: int,
    dimension_gates_cfg: dict[str, Any] | None = None,
) -> DimensionGatesRunReport:
    """Run all dimension gates and compute whether delivery should block (phase-aware)."""
    cfg = dimension_gates_cfg or {}
    phase = int(cfg.get("dimension_gate_phase", 1))
    fail_mode = str(cfg.get("fail_mode", "warn"))
    blocked_list = _parse_blocked_dimensions_list(cfg.get("blocked_dimensions"))
    blocked_set = frozenset(_norm_dimension_gate_name(x) for x in blocked_list)
    cohesion_cfg = cfg.get("cohesion") if isinstance(cfg.get("cohesion"), dict) else {}
    listen_cfg = cfg.get("listen_experience") if isinstance(cfg.get("listen_experience"), dict) else {}

    gates: list[GateResult] = [
        gate_uniqueness(text, other_texts, chapter_index),
        gate_engagement(text, chapter_index),
        gate_somatic_precision(text),
        gate_cohesion(text, other_texts, chapter_index, cohesion_cfg),
    ]
    if phase >= 3:
        gates.append(gate_listen_experience(text, listen_cfg))

    fail_count = sum(1 for g in gates if g.status == "FAIL")
    warn_count = sum(1 for g in gates if g.status == "WARN")
    if any(g.status == "FAIL" for g in gates):
        overall = "FAIL"
    elif any(g.status == "WARN" for g in gates):
        overall = "WARN"
    else:
        overall = "PASS"

    blocks_delivery = False
    if fail_mode == "block" and blocked_set:
        for g in gates:
            if g.status == "FAIL" and _norm_dimension_gate_name(g.dimension) in blocked_set:
                blocks_delivery = True
                break

    return DimensionGatesRunReport(
        chapter_index=chapter_index,
        gates=gates,
        overall_status=overall,
        fail_count=fail_count,
        warn_count=warn_count,
        blocks_delivery=blocks_delivery,
        dimension_gate_phase=phase,
        fail_mode=fail_mode,
        blocked_dimensions=blocked_list,
    )
