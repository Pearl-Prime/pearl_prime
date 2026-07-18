"""ACT-013 — Scoring calibration regression tests.

Validates three heuristic fixes from CATALOG_ENHANCEMENT_ROADMAP.md:
1. score_somatic_precision: fixed 15-body-word target (not proportional to length)
2. score_content_uniqueness: 3-gram phrase overlap (not word-level Jaccard)
3. score_tts_readability_heuristic: short-sentence style (median ≤6) scores ≥ 0.55
"""
from __future__ import annotations

import sys
from pathlib import Path

# Allow import of scripts/analysis module without full install
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.analysis.score_catalog_deep import (
    score_content_uniqueness,
    score_listen_experience,
    score_somatic_precision,
    score_tts_readability_heuristic,
)


# ---------------------------------------------------------------------------
# 1. score_somatic_precision — fixed 15-word target
# ---------------------------------------------------------------------------

def test_somatic_precision_long_book_with_body_words():
    """10k-word book with 15 distinct body words must score 1.0."""
    body_vocab = (
        "shoulder breath stomach jaw chest heart spine throat belly lungs "
        "exhale inhale pulse muscle nerves"
    ).split()
    filler = ("the person sat quietly noticing " * 700)  # ~3500 words
    text = filler + " ".join(body_vocab)
    score = score_somatic_precision(text)
    assert score == 1.0, f"expected 1.0 for 15 body words, got {score}"


def test_somatic_precision_zero_body_words():
    text = "This is a purely cognitive discussion about thinking and planning."
    score = score_somatic_precision(text)
    assert score == 0.0


def test_somatic_precision_partial():
    """7 body words out of 15 target → ~0.467."""
    text = "Notice your breath. Feel the shoulder. Jaw. Chest. Exhale. Spine. Belly. Rest."
    score = score_somatic_precision(text)
    assert 0.3 <= score <= 0.7, f"expected 0.3-0.7 range, got {score}"


# ---------------------------------------------------------------------------
# 2. score_content_uniqueness — 3-gram phrase overlap
# ---------------------------------------------------------------------------

_ANXIETY_CH1 = (
    "Your body ran the alarm. Before you assessed the situation. "
    "The chest tightened. The breath shortened. That is the false alarm."
)
_ANXIETY_CH2 = (
    "Notice what happens when the meeting starts. The same alarm runs. "
    "Chest tight. Breath short. The pattern repeats. That is the nervous system."
)
_GRIEF_CH1 = (
    "There is a sentence you have been saying since the loss. "
    "Something changed. The world looks different from inside."
)

def test_uniqueness_same_topic_chapters_score_high():
    """Two chapters on the same topic sharing vocabulary score ≥ 0.7 (not penalised)."""
    score = score_content_uniqueness([_ANXIETY_CH1, _ANXIETY_CH2])
    assert score >= 0.7, f"same-topic chapters over-penalised: {score}"


def test_uniqueness_different_topic_chapters_score_high():
    """Chapters on different topics score ≥ 0.85."""
    score = score_content_uniqueness([_ANXIETY_CH1, _GRIEF_CH1])
    assert score >= 0.85, f"different-topic chapters should score high: {score}"


def test_uniqueness_identical_chapters_score_low():
    """Identical chapters (100% phrase overlap) score 0.0."""
    score = score_content_uniqueness([_ANXIETY_CH1, _ANXIETY_CH1])
    assert score == 0.0, f"identical chapters should score 0: {score}"


def test_uniqueness_single_chapter():
    """Single chapter returns 1.0 (nothing to compare)."""
    assert score_content_uniqueness([_ANXIETY_CH1]) == 1.0


# ---------------------------------------------------------------------------
# 3. score_tts_readability_heuristic — short-sentence style
# ---------------------------------------------------------------------------

_PHOENIX_SHORT_PROSE = """\
Notice the breath.
Feel your jaw.
Let it soften.
The alarm ran first.
You had no choice.
That is the mechanism.

Not weakness.
Not failure.
A nervous system doing its job.

Now breathe.
Four counts in.
Six counts out.
Again.
"""

def test_tts_short_sentence_style_scores_adequately():
    """Phoenix 1-4 word sentence style must score ≥ 0.55 (was near-zero before fix)."""
    score = score_tts_readability_heuristic(_PHOENIX_SHORT_PROSE)
    assert score >= 0.55, f"short-sentence style under-scored: {score}"


def test_listen_experience_short_prose_adequate():
    """score_listen_experience on Phoenix short prose must be ≥ 0.35."""
    score = score_listen_experience(_PHOENIX_SHORT_PROSE)
    assert score >= 0.35, f"listen_experience too low for Phoenix short prose: {score}"


def test_tts_long_repetitive_scores_lower():
    """Text with extreme repetition should still score lower than varied prose."""
    repetitive = "And then the thing happened and then the thing happened and then the thing happened. " * 20
    short_score = score_tts_readability_heuristic(_PHOENIX_SHORT_PROSE)
    rep_score = score_tts_readability_heuristic(repetitive)
    assert short_score >= rep_score, "Phoenix prose should outperform repetitive text"
