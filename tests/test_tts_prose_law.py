"""Tests for TTS prose readability scorer (Writer Spec §12).

Verifies detection of rhetorical questions, long sentences, monotone
pacing, and problematic TTS patterns.
"""
from __future__ import annotations

import pytest

from phoenix_v4.quality.ei_v2.tts_readability import score_tts_readability

# Well-written prose with varied rhythm, paragraph breaks, no questions
GOOD_PROSE = (
    "The morning light filtered through the blinds. She sat at the edge of the bed, "
    "feet touching the cold floor. Something had shifted overnight.\n\n"
    "Not a dramatic change. More like a door left slightly ajar. The kind of thing "
    "you notice only when the wind catches it. A creak. A sliver of light where "
    "there used to be darkness.\n\n"
    "She stood up. Walked to the kitchen. Poured water into the kettle. "
    "These small acts carried weight today. Each one a quiet decision to begin again. "
    "The steam rose and curled against the window. Outside, the city was already moving."
)

# Prose with many rhetorical questions
QUESTION_HEAVY = (
    "Have you ever wondered why you feel this way? What if the answer was simpler "
    "than you think? Could it be that you have been looking in the wrong direction? "
    "Is it possible that the fear itself is the message? What would happen if you "
    "just stopped running? Would the world really end? Or would you discover "
    "something unexpected?"
)

# Monotone pacing: all sentences roughly same length
MONOTONE_PROSE = " ".join(
    [f"She walked to the window and looked outside for a while." for _ in range(10)]
)

# Very long sentences
LONG_SENTENCES = (
    "The way that the entire system of emotional regulation works within the human body "
    "is fundamentally connected to the nervous system pathways that run from the brain "
    "stem through the vagus nerve and into the gut and heart and lungs in ways that "
    "most people never fully appreciate or understand until they experience a moment of "
    "complete physiological overwhelm. "
    "Another extraordinarily long sentence that goes on and on and on describing the "
    "intricate mechanisms of stress response and how cortisol floods the prefrontal "
    "cortex and shuts down the executive functioning centers that normally allow us "
    "to make rational decisions in moments of crisis and uncertainty and fear."
)

# Problematic TTS patterns
TTS_PROBLEMATIC = (
    "The EXTREMELY IMPORTANT thing about ADHD is that version 3.2.1 of the DSM "
    "defines it (and this is absolutely critical to understand; yes really; no doubt "
    "about it; completely certain) as a -- fundamentally misunderstood -- condition."
)


class TestWellWrittenProseScoresHigh:
    """Good prose should score well on all dimensions."""

    def test_composite_above_threshold(self):
        result = score_tts_readability(GOOD_PROSE)
        assert result["composite"] > 0.5, f"Good prose scored {result['composite']}"

    def test_no_rhetorical_question_issues(self):
        result = score_tts_readability(GOOD_PROSE)
        rq_issues = [i for i in result["issues"] if "rhetorical" in i]
        assert len(rq_issues) == 0


class TestRhetoricalQuestionsLowerScore:
    """Prose with many questions should be penalized."""

    def test_question_safety_low(self):
        result = score_tts_readability(QUESTION_HEAVY)
        assert result["dimensions"]["rhetorical_question_safety"] < 0.6

    def test_issues_mention_rhetorical(self):
        result = score_tts_readability(QUESTION_HEAVY)
        assert any("rhetorical" in i for i in result["issues"])


class TestMonotonePacingDetected:
    """Same-length sentences should trigger rhythm warnings."""

    def test_rhythm_issues(self):
        result = score_tts_readability(MONOTONE_PROSE)
        issues_text = " ".join(result["issues"])
        assert "monotone" in issues_text or "rhythm" in issues_text, (
            f"Expected monotone/rhythm issue, got: {result['issues']}"
        )


class TestLongSentencesPenalized:
    """Sentences exceeding max word count should be flagged."""

    def test_long_sentence_issue(self):
        result = score_tts_readability(LONG_SENTENCES)
        assert any("long_sentences" in i for i in result["issues"])

    def test_sentence_length_score_low(self):
        result = score_tts_readability(LONG_SENTENCES)
        assert result["dimensions"]["sentence_length"] < 0.8


class TestProblematicTTSPatterns:
    """ALL_CAPS, semicolons, em-dashes flagged."""

    def test_tts_patterns_detected(self):
        result = score_tts_readability(TTS_PROBLEMATIC)
        assert result["metrics"]["tts_problematic_count"] > 0

    def test_tts_pattern_safety_penalized(self):
        result = score_tts_readability(TTS_PROBLEMATIC)
        assert result["dimensions"]["tts_pattern_safety"] < 1.0


class TestCompositeInBounds:
    """Composite score is always in [0, 1]."""

    @pytest.mark.parametrize("text", [
        GOOD_PROSE, QUESTION_HEAVY, MONOTONE_PROSE, LONG_SENTENCES,
        TTS_PROBLEMATIC, "", "One word.", "A. B. C.",
    ])
    def test_bounds(self, text):
        result = score_tts_readability(text)
        assert 0.0 <= result["composite"] <= 1.0


class TestConfigOverrides:
    """Custom config changes scoring behavior."""

    def test_stricter_max_sentence_words(self):
        # Prose with sentences around 20 words — normal limit (35) passes, strict (10) flags
        medium_prose = (
            "She walked slowly and carefully down the long dimly lit hallway toward the office at the far end. "
            "The old fluorescent lights buzzed and hummed overhead casting pale uneven shadows on the floor. "
            "Every single step she took felt noticeably heavier than the last one had felt before."
        )
        strict_cfg = {"max_sentence_words": 10}
        result = score_tts_readability(medium_prose, cfg=strict_cfg)
        assert result["metrics"]["long_sentence_fraction"] > 0
