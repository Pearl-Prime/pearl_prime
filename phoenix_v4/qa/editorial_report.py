"""
Spec S13 Pearl_Editor Scoring Rubric -- 12-criterion editorial assessment.

Operates on rendered prose (full book text + per-chapter texts) rather than
plan metadata.  Each criterion scores PASS (2), ADEQUATE (1), or FAIL (0)
for a maximum of 24 points across 12 criteria.

Grading:
    >=20  PASS
    14-19 NEEDS_REVISION
    <14   FAIL

Public API
----------
- ``generate_editorial_report(book_text, chapters, ...)`` -> EditorialReport
- ``write_editorial_report(report, output_path)`` -> None
"""
from __future__ import annotations

import json
import re
import statistics
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Score constants
# ---------------------------------------------------------------------------
_PASS = 2
_ADEQUATE = 1
_FAIL = 0

_GRADE_PASS_THRESHOLD = 20
_GRADE_REVISION_THRESHOLD = 14


def _score_label(val: int) -> str:
    if val >= _PASS:
        return "PASS"
    if val >= _ADEQUATE:
        return "ADEQUATE"
    return "FAIL"


# ---------------------------------------------------------------------------
# Text helpers
# ---------------------------------------------------------------------------

def _sentences_from_text(text: str) -> List[str]:
    """Split text into sentences on common punctuation boundaries."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]


def _word_list(text: str) -> List[str]:
    return re.findall(r"[a-z']+", text.lower())


def _unique_ratio(text: str) -> float:
    words = _word_list(text)
    if not words:
        return 0.0
    return len(set(words)) / len(words)


# ---------------------------------------------------------------------------
# Criterion-specific regex patterns
# ---------------------------------------------------------------------------

_HOOK_FRICTION_PATTERNS = [
    re.compile(r"\bnot\b.{1,60}\bbut\b", re.I),
    re.compile(r"\b\d+\s*a\.?m\.?\b", re.I),
    re.compile(r"\byour\s+(eyes|hands|jaw|chest|throat|stomach)\b", re.I),
    re.compile(r"\byou\s+(cancel|disappear|avoid|freeze|clench|stare)\b", re.I),
]

_TOPIC_LABEL_OPENER = re.compile(
    r"(?i)^(anxiety|burnout|self[\s-]?worth|depression|shame|grief|stress)"
    r"\s+(is|happens|means|affects|can)\b"
)
_TEMPORAL_OPENER = re.compile(
    r"(?i)^(in today|in recent|throughout history|over the past)"
)

_SCENE_DETAIL_PATTERNS = [
    re.compile(r"\b(oat-milk|fluorescent|digital clock|grey|buzzing|hum)\b", re.I),
    re.compile(r"\b\d+\s*(messages?|texts?|emails?|missed calls?)\b", re.I),
    re.compile(r"\b(thumb|finger|wrist|jaw|sternum|rib|temple)\b", re.I),
    re.compile(r"\b(cold|warm|damp|dry|cracked|sticky|gritty)\b", re.I),
    re.compile(r"\b(hover|clench|grip|press|tap|scroll|swipe)\b", re.I),
]

_AHA_PATTERNS = [
    re.compile(r"\bnot\b.{1,40}\bbut\b", re.I),
    re.compile(r"\bwhat you (call|thought|assumed)\b", re.I),
    re.compile(r"\byour body\b.{1,40}\b(knew|recognized|said|held)\b", re.I),
    re.compile(
        r"\bthe (cost|price|consequence|pattern)\b.{1,30}\b(is|was|has been)\b",
        re.I,
    ),
    re.compile(r"\b(survival|adaptation|intelligence|strategy)\b", re.I),
]

_INTEGRATION_BRIDGE_FINGERPRINTS = [
    "still here",
    "feet on floor",
    "weight in the chair",
    "breath is slower",
    "that is enough",
    "what changed",
    "what remains",
    "the grip loosened",
    "let it carry",
]

_THREAD_PATTERNS = [
    re.compile(r"\?", re.I),
    re.compile(r"\byou have not yet\b", re.I),
    re.compile(r"\bstill yours\b", re.I),
    re.compile(r"\bthe harder thing\b", re.I),
    re.compile(r"\bwho benefits\b", re.I),
]

_SCAFFOLD_PHRASES = [
    "the truth is",
    "here is what",
    "and that is okay",
    "let me be clear",
    "this is not your fault",
    "what this means going forward is simple",
    "that moment matters because",
    "so this is not just your private glitch",
]

_LOCATION_CUES = re.compile(
    r"\b(office|kitchen|bedroom|bathroom|subway|train|car|desk|elevator|"
    r"hallway|sidewalk|parking lot|waiting room|coffee shop|street|"
    r"morning|evening|3\s*a\.?m\.?|midnight|dawn|dusk|lunch|dinner)\b",
    re.I,
)


# ---------------------------------------------------------------------------
# Per-chapter criterion scorers
# ---------------------------------------------------------------------------

def _score_hook_friction(chapter_text: str) -> int:
    """Criterion 1: Hook friction -- first 2 sentences create cognitive friction."""
    sents = _sentences_from_text(chapter_text)
    if len(sents) < 2:
        return _FAIL
    hook = " ".join(sents[:2])
    low = hook.lower()
    if _TOPIC_LABEL_OPENER.search(low):
        return _FAIL
    if _TEMPORAL_OPENER.search(low):
        return _FAIL
    hits = sum(1 for p in _HOOK_FRICTION_PATTERNS if p.search(hook))
    if hits >= 2:
        return _PASS
    if hits >= 1:
        return _ADEQUATE
    words_first = len(sents[0].split())
    if words_first <= 6:
        return _ADEQUATE
    return _FAIL


def _score_scene_specificity(chapter_text: str) -> int:
    """Criterion 2: Scene specificity -- 3-detail rule per scene."""
    hits = sum(1 for p in _SCENE_DETAIL_PATTERNS if p.search(chapter_text))
    if hits >= 3:
        return _PASS
    if hits >= 2:
        return _ADEQUATE
    return _FAIL


def _score_aha_presence(chapter_text: str) -> int:
    """Criterion 3: Aha density -- at least 1 genuine aha per chapter."""
    hits = sum(1 for p in _AHA_PATTERNS if p.search(chapter_text))
    if hits >= 2:
        return _PASS
    if hits >= 1:
        return _ADEQUATE
    return _FAIL


def _score_integration_variety(chapters: List[str]) -> List[int]:
    """Criterion 4: Integration variety -- no repeated integration bridges.

    Returns a per-chapter score list.
    """
    if not chapters:
        return []
    chapter_bridges: List[set] = []
    for ch in chapters:
        low = ch.lower()
        found = set()
        for bp in _INTEGRATION_BRIDGE_FINGERPRINTS:
            if bp in low:
                found.add(bp)
        chapter_bridges.append(found)

    scores: List[int] = []
    seen_bridges: Counter = Counter()
    for bridges in chapter_bridges:
        repeated = sum(1 for b in bridges if seen_bridges[b] > 0)
        for b in bridges:
            seen_bridges[b] += 1
        if not bridges:
            scores.append(_ADEQUATE)
        elif repeated == 0:
            scores.append(_PASS)
        elif repeated <= 1:
            scores.append(_ADEQUATE)
        else:
            scores.append(_FAIL)
    return scores


def _score_thread_continuity(chapters: List[str]) -> List[int]:
    """Criterion 5: Thread continuity -- threads reference prior chapters.

    Returns per-chapter scores (first chapter always PASS).
    """
    if not chapters:
        return []
    scores: List[int] = [_PASS]
    for idx in range(1, len(chapters)):
        prior_words = set(_word_list(chapters[idx - 1])[-200:])
        current_words = set(_word_list(chapters[idx])[:200])
        overlap = len(prior_words & current_words)
        thread_hits = sum(
            1 for p in _THREAD_PATTERNS if p.search(chapters[idx][-500:])
        )
        if overlap >= 8 and thread_hits >= 1:
            scores.append(_PASS)
        elif overlap >= 4 or thread_hits >= 1:
            scores.append(_ADEQUATE)
        else:
            scores.append(_FAIL)
    return scores


def _score_repetition_index(book_text: str) -> tuple:
    """Criterion 6: Repetition index -- scaffold phrases capped at 3.

    Returns ``(score, excess_count)``.
    """
    low = book_text.lower()
    total_repeats = 0
    for phrase in _SCAFFOLD_PHRASES:
        count = low.count(phrase)
        if count > 3:
            total_repeats += count - 3
    if total_repeats == 0:
        return _PASS, 0
    if total_repeats <= 2:
        return _ADEQUATE, total_repeats
    return _FAIL, total_repeats


def _score_vocabulary_diversity(book_text: str) -> tuple:
    """Criterion 7: Vocabulary diversity -- >0.15 unique ratio.

    Returns ``(score, ratio)``.
    """
    ratio = _unique_ratio(book_text)
    if ratio > 0.15:
        return _PASS, round(ratio, 4)
    if ratio > 0.10:
        return _ADEQUATE, round(ratio, 4)
    return _FAIL, round(ratio, 4)


def _score_flat_middle(chapters: List[str]) -> tuple:
    """Criterion 8: Flat middle detection -- chapters 4-8 vocab overlap <85%.

    Returns ``(score, max_overlap)``.
    """
    if len(chapters) < 8:
        return _PASS, 0.0

    middle_start = 3
    middle_end = min(7, len(chapters) - 1)
    middle_chapters = chapters[middle_start : middle_end + 1]

    max_overlap = 0.0
    for i in range(len(middle_chapters)):
        for j in range(i + 1, len(middle_chapters)):
            words_a = set(_word_list(middle_chapters[i]))
            words_b = set(_word_list(middle_chapters[j]))
            if not words_a or not words_b:
                continue
            overlap = len(words_a & words_b) / min(len(words_a), len(words_b))
            max_overlap = max(max_overlap, overlap)

    if max_overlap < 0.85:
        return _PASS, round(max_overlap, 4)
    if max_overlap < 0.92:
        return _ADEQUATE, round(max_overlap, 4)
    return _FAIL, round(max_overlap, 4)


def _score_reward_spacing(chapters: List[str]) -> tuple:
    """Criterion 9: Reward spacing -- exercise or story every 3 chapters.

    Returns ``(score, max_gap)``.
    """
    if len(chapters) <= 3:
        return _PASS, 0

    reward_indices: List[int] = []
    for idx, ch in enumerate(chapters):
        low = ch.lower()
        has_exercise = bool(
            re.search(
                r"\b(place|breathe|press|notice|exhale|inhale|count|hold)\b", low
            )
        )
        has_story = bool(
            re.search(r"\b(she|he|they|maya|david|keiko)\b", low)
        )
        has_reframe = bool(re.search(r"\bnot\b.{1,40}\bbut\b", low))
        if has_exercise or has_story or has_reframe:
            reward_indices.append(idx)

    if not reward_indices:
        return _FAIL, len(chapters)

    max_gap = reward_indices[0]
    for i in range(1, len(reward_indices)):
        gap = reward_indices[i] - reward_indices[i - 1]
        max_gap = max(max_gap, gap)
    max_gap = max(max_gap, len(chapters) - 1 - reward_indices[-1])

    if max_gap <= 3:
        return _PASS, max_gap
    if max_gap <= 4:
        return _ADEQUATE, max_gap
    return _FAIL, max_gap


def _score_word_budget(
    chapter_word_count: int, target_min: int, target_max: int
) -> int:
    """Criterion 10: Word budget adherence -- within format target range."""
    if target_min <= chapter_word_count <= target_max:
        return _PASS
    tolerance = max(100, int((target_max - target_min) * 0.10))
    if (target_min - tolerance) <= chapter_word_count <= (target_max + tolerance):
        return _ADEQUATE
    return _FAIL


def _score_location_grounding(chapters: List[str]) -> List[int]:
    """Criterion 11: Location grounding -- location cues present and varied.

    Returns per-chapter scores.
    """
    scores: List[int] = []
    all_locations_seen: Counter = Counter()
    for ch in chapters:
        found = set(m.group().lower() for m in _LOCATION_CUES.finditer(ch))
        if len(found) >= 2:
            repeated = sum(1 for loc in found if all_locations_seen[loc] > 1)
            if repeated <= len(found) // 2:
                scores.append(_PASS)
            else:
                scores.append(_ADEQUATE)
        elif len(found) == 1:
            scores.append(_ADEQUATE)
        else:
            scores.append(_FAIL)
        for loc in found:
            all_locations_seen[loc] += 1
    return scores


def _score_cadence_variety(chapter_text: str) -> int:
    """Criterion 12: Cadence variety -- sentence length variation per chapter."""
    sents = _sentences_from_text(chapter_text)
    if len(sents) < 5:
        return _ADEQUATE
    lengths = [len(s.split()) for s in sents]
    if not lengths:
        return _FAIL
    std_dev = statistics.stdev(lengths) if len(lengths) > 1 else 0.0
    length_range = max(lengths) - min(lengths)
    has_short = any(ln <= 3 for ln in lengths)
    has_long = any(ln >= 15 for ln in lengths)

    if std_dev >= 4.0 and length_range >= 12 and has_short and has_long:
        return _PASS
    if std_dev >= 2.5 and length_range >= 8:
        return _ADEQUATE
    return _FAIL


# ---------------------------------------------------------------------------
# Thesis drift (editorial layer)
# ---------------------------------------------------------------------------

def _editorial_thesis_drift(
    chapters: List[str],
    chapter_theses: Optional[Dict[int, str]] = None,
) -> List[dict]:
    """Check whether each chapter aligns with its assigned thesis.

    ``chapter_theses`` maps 1-based chapter number to thesis text.
    """
    if not chapter_theses:
        return [{"aligned": True, "coverage": 1.0, "thesis": ""} for _ in chapters]

    results: List[dict] = []
    for idx, ch_text in enumerate(chapters):
        ch_num = idx + 1
        thesis = chapter_theses.get(ch_num, "")
        if not thesis:
            results.append({"aligned": True, "coverage": 1.0, "thesis": ""})
            continue
        thesis_words = set(_word_list(thesis))
        chapter_words = set(_word_list(ch_text))
        if not thesis_words:
            results.append({"aligned": True, "coverage": 1.0, "thesis": thesis})
            continue
        hits = len(thesis_words & chapter_words)
        coverage = hits / len(thesis_words)
        results.append({
            "aligned": coverage >= 0.3,
            "coverage": round(coverage, 3),
            "thesis": thesis,
        })
    return results


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------

@dataclass
class ChapterAssessment:
    """Per-chapter assessment from the 12-criterion rubric."""

    chapter_index: int
    hook_friction: int = 0
    scene_specificity: int = 0
    aha_presence: int = 0
    integration_variety: int = 0
    thread_continuity: int = 0
    word_budget: int = 0
    location_grounding: int = 0
    cadence_variety: int = 0
    word_count: int = 0
    target_min: int = 0
    target_max: int = 0
    thesis_aligned: bool = True
    thesis_coverage: float = 1.0

    @property
    def chapter_total(self) -> int:
        return (
            self.hook_friction
            + self.scene_specificity
            + self.aha_presence
            + self.integration_variety
            + self.thread_continuity
            + self.word_budget
            + self.location_grounding
            + self.cadence_variety
        )

    def to_dict(self) -> dict:
        return {
            "chapter_index": self.chapter_index,
            "hook_friction": _score_label(self.hook_friction),
            "scene_specificity": _score_label(self.scene_specificity),
            "aha_presence": _score_label(self.aha_presence),
            "integration_variety": _score_label(self.integration_variety),
            "thread_continuity": _score_label(self.thread_continuity),
            "word_budget": _score_label(self.word_budget),
            "location_grounding": _score_label(self.location_grounding),
            "cadence_variety": _score_label(self.cadence_variety),
            "word_count": self.word_count,
            "target_range": [self.target_min, self.target_max],
            "thesis_aligned": self.thesis_aligned,
            "thesis_coverage": self.thesis_coverage,
            "chapter_score": self.chapter_total,
        }


@dataclass
class EditorialReport:
    """Full editorial report from the 12-criterion rubric."""

    chapter_assessments: List[ChapterAssessment] = field(default_factory=list)
    # Book-level criteria
    repetition_index: int = 0
    repetition_excess_count: int = 0
    vocabulary_diversity: int = 0
    vocabulary_ratio: float = 0.0
    flat_middle: int = 0
    flat_middle_overlap: float = 0.0
    reward_spacing: int = 0
    reward_max_gap: int = 0
    # Totals
    total_score: int = 0
    max_score: int = 24
    grade: str = "FAIL"
    revision_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "chapter_assessments": [
                ca.to_dict() for ca in self.chapter_assessments
            ],
            "book_level": {
                "repetition_index": _score_label(self.repetition_index),
                "repetition_excess_count": self.repetition_excess_count,
                "vocabulary_diversity": _score_label(self.vocabulary_diversity),
                "vocabulary_ratio": self.vocabulary_ratio,
                "flat_middle": _score_label(self.flat_middle),
                "flat_middle_overlap": self.flat_middle_overlap,
                "reward_spacing": _score_label(self.reward_spacing),
                "reward_max_gap": self.reward_max_gap,
            },
            "total_score": self.total_score,
            "max_score": self.max_score,
            "grade": self.grade,
            "revision_notes": self.revision_notes,
        }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_editorial_report(
    book_text: str,
    chapters: List[str],
    flow_report: Optional[dict] = None,
    craft_scores: Optional[dict] = None,
    *,
    chapter_theses: Optional[Dict[int, str]] = None,
    word_target_min: int = 1500,
    word_target_max: int = 3500,
) -> EditorialReport:
    """Generate a structured editorial report using the spec S13 rubric.

    Parameters
    ----------
    book_text : str
        The full rendered book text.
    chapters : list[str]
        Per-chapter texts (in order).
    flow_report : dict, optional
        ``chapter_flow_report.json`` data (reserved for future enrichment).
    craft_scores : dict, optional
        ONTGP craft scores from ``bestseller_craft_gate`` (reserved for future
        enrichment).
    chapter_theses : dict[int, str], optional
        Maps 1-based chapter number to thesis text for drift checking.
    word_target_min, word_target_max : int
        Per-chapter word count target range.

    Returns
    -------
    EditorialReport
    """
    report = EditorialReport()
    revision_notes: List[str] = []

    if not chapters:
        report.grade = "FAIL"
        report.revision_notes = ["No chapters provided."]
        return report

    # ---- per-chapter criteria (1, 2, 3, 10, 11, 12) ----
    integration_scores = _score_integration_variety(chapters)
    thread_scores = _score_thread_continuity(chapters)
    location_scores = _score_location_grounding(chapters)
    drift_results = _editorial_thesis_drift(chapters, chapter_theses)

    chapter_assessments: List[ChapterAssessment] = []
    for idx, ch_text in enumerate(chapters):
        wc = len(ch_text.split())
        ca = ChapterAssessment(
            chapter_index=idx,
            hook_friction=_score_hook_friction(ch_text),
            scene_specificity=_score_scene_specificity(ch_text),
            aha_presence=_score_aha_presence(ch_text),
            integration_variety=(
                integration_scores[idx]
                if idx < len(integration_scores)
                else _ADEQUATE
            ),
            thread_continuity=(
                thread_scores[idx] if idx < len(thread_scores) else _PASS
            ),
            word_budget=_score_word_budget(wc, word_target_min, word_target_max),
            location_grounding=(
                location_scores[idx]
                if idx < len(location_scores)
                else _ADEQUATE
            ),
            cadence_variety=_score_cadence_variety(ch_text),
            word_count=wc,
            target_min=word_target_min,
            target_max=word_target_max,
            thesis_aligned=(
                drift_results[idx]["aligned"]
                if idx < len(drift_results)
                else True
            ),
            thesis_coverage=(
                drift_results[idx]["coverage"]
                if idx < len(drift_results)
                else 1.0
            ),
        )
        chapter_assessments.append(ca)

        # Collect revision notes for failing criteria
        if ca.hook_friction == _FAIL:
            revision_notes.append(
                f"Ch {idx + 1}: Hook lacks cognitive friction."
            )
        if ca.scene_specificity == _FAIL:
            revision_notes.append(
                f"Ch {idx + 1}: Scene needs 3+ non-transferable sensory details."
            )
        if ca.aha_presence == _FAIL:
            revision_notes.append(
                f"Ch {idx + 1}: No identifiable aha moment."
            )
        if ca.integration_variety == _FAIL:
            revision_notes.append(
                f"Ch {idx + 1}: Integration bridges repeat prior chapters."
            )
        if ca.thread_continuity == _FAIL:
            revision_notes.append(
                f"Ch {idx + 1}: Thread does not reference prior chapter."
            )
        if ca.word_budget == _FAIL:
            revision_notes.append(
                f"Ch {idx + 1}: Word count ({ca.word_count}) outside target "
                f"[{word_target_min}, {word_target_max}]."
            )
        if ca.location_grounding == _FAIL:
            revision_notes.append(
                f"Ch {idx + 1}: No location or body cues."
            )
        if ca.cadence_variety == _FAIL:
            revision_notes.append(
                f"Ch {idx + 1}: Sentence rhythm is monotone."
            )
        if not ca.thesis_aligned:
            revision_notes.append(
                f"Ch {idx + 1}: Content drifts from assigned thesis "
                f"(coverage {ca.thesis_coverage:.0%})."
            )

    report.chapter_assessments = chapter_assessments

    # ---- book-level criteria (6, 7, 8, 9) ----
    full_text = book_text if book_text else " ".join(chapters)

    rep_score, rep_count = _score_repetition_index(full_text)
    report.repetition_index = rep_score
    report.repetition_excess_count = rep_count
    if rep_score == _FAIL:
        revision_notes.append(
            f"Book: Scaffold phrases exceed 3-use cap by {rep_count} instances."
        )

    vocab_score, vocab_ratio = _score_vocabulary_diversity(full_text)
    report.vocabulary_diversity = vocab_score
    report.vocabulary_ratio = vocab_ratio
    if vocab_score == _FAIL:
        revision_notes.append(
            f"Book: Vocabulary diversity too low ({vocab_ratio:.2%})."
        )

    flat_score, flat_overlap = _score_flat_middle(chapters)
    report.flat_middle = flat_score
    report.flat_middle_overlap = flat_overlap
    if flat_score == _FAIL:
        revision_notes.append(
            f"Book: Flat middle detected -- chapters 4-8 overlap "
            f"{flat_overlap:.0%}."
        )

    reward_score, reward_gap = _score_reward_spacing(chapters)
    report.reward_spacing = reward_score
    report.reward_max_gap = reward_gap
    if reward_score == _FAIL:
        revision_notes.append(f"Book: Reward gap of {reward_gap} chapters.")

    # ---- compute total score ----
    def _avg_criterion(attr: str) -> int:
        vals = [getattr(ca, attr) for ca in chapter_assessments]
        mean = sum(vals) / len(vals) if vals else 0.0
        if mean >= 1.5:
            return _PASS
        if mean >= 0.75:
            return _ADEQUATE
        return _FAIL

    chapter_criteria_total = sum(
        _avg_criterion(attr)
        for attr in (
            "hook_friction",
            "scene_specificity",
            "aha_presence",
            "integration_variety",
            "thread_continuity",
            "word_budget",
            "location_grounding",
            "cadence_variety",
        )
    )

    book_criteria_total = rep_score + vocab_score + flat_score + reward_score

    total = chapter_criteria_total + book_criteria_total
    report.total_score = total
    report.max_score = 24

    if total >= _GRADE_PASS_THRESHOLD:
        report.grade = "PASS"
    elif total >= _GRADE_REVISION_THRESHOLD:
        report.grade = "NEEDS_REVISION"
    else:
        report.grade = "FAIL"

    report.revision_notes = revision_notes
    return report


def write_editorial_report(
    report: EditorialReport, output_path: "str | Path"
) -> None:
    """Write the editorial report as JSON to *output_path*."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)
