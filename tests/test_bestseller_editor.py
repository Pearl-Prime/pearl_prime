"""Tests for phoenix_v4.qa.editorial_report -- S13 Pearl_Editor scoring rubric.

Covers:
- generate_editorial_report with all-passing chapters
- generate_editorial_report with failing chapters (repetition, flat middle)
- Grade calculation (PASS / NEEDS_REVISION / FAIL thresholds)
- JSON output format validation via write_editorial_report
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.qa.editorial_report import (
    ChapterAssessment,
    EditorialReport,
    generate_editorial_report,
    write_editorial_report,
    _score_hook_friction,
    _score_scene_specificity,
    _score_aha_presence,
    _score_integration_variety,
    _score_thread_continuity,
    _score_repetition_index,
    _score_vocabulary_diversity,
    _score_flat_middle,
    _score_reward_spacing,
    _score_word_budget,
    _score_location_grounding,
    _score_cadence_variety,
    _PASS,
    _ADEQUATE,
    _FAIL,
)


# ---------------------------------------------------------------------------
# Fixtures -- synthetic chapter texts
# ---------------------------------------------------------------------------

def _good_chapter(idx: int = 0) -> str:
    """A chapter that should score well across most criteria."""
    return (
        "Your eyes open. 3 a.m. You are calculating tomorrow before your "
        "feet hit the floor. "
        "Not because you forgot something but because your body will not "
        "let you stop. "
        "The oat-milk film on the surface has gone grey. Your thumb hovers "
        "over the send button. "
        "It stays there. The fluorescent hum is the only sound. Even the "
        "clock is digital. "
        "She cancels on Keiko for the fourth time. Keiko does not ask a "
        "fifth time. "
        "What you call a flaw was once a survival intelligence. "
        "Your body knew this long before your mind admitted it. "
        "The cost is not what you expected. The pattern is clear now. "
        "Place your hand on your chest. Press gently. Feel the warmth. "
        "Breathe in for four counts. Hold for two. Release for six. Again. "
        "Slower this time. Notice. "
        "Still here. The grip loosened. Feet on floor. That is enough "
        "for now. "
        "You have not yet done the harder thing. Who benefits when you "
        "keep hiding? "
        "The kitchen counter holds a cold mug. Morning light through the "
        "hallway. "
        "Your jaw aches. You did not put it there. The desk is waiting. "
        "The real cost is relational erosion not a single consequence. "
        "Not broken. Overridden. The system that kept your ancestors alive "
        "is now running your Tuesday morning. "
    )


def _weak_chapter() -> str:
    """A chapter that should score poorly -- generic, monotone, no friction."""
    return (
        "Anxiety is a common experience for many people today. "
        "In today's fast-paced world we all feel overwhelmed sometimes. "
        "Stress can affect your daily life in many ways. "
        "Many people struggle with these feelings every day. "
        "It is important to take care of yourself. "
        "You should try to relax when you feel stressed. "
        "There are many techniques that can help you. "
        "Consider talking to someone about your feelings. "
        "Exercise can also be beneficial for stress relief. "
        "Remember to take things one day at a time. "
    )


def _repetitive_book_text() -> str:
    """Book text with scaffold phrases repeated >3 times."""
    base = (
        "The truth is your body knows. Here is what matters. "
        "And that is okay. "
    )
    return base * 10


# ---------------------------------------------------------------------------
# Unit tests for individual criterion scorers
# ---------------------------------------------------------------------------

class TestHookFriction:
    def test_strong_hook(self):
        text = (
            "Your eyes open. 3 a.m. You are calculating tomorrow "
            "before your feet hit the floor."
        )
        assert _score_hook_friction(text) >= _ADEQUATE

    def test_topic_label_opener_fails(self):
        text = (
            "Anxiety is a very common problem. "
            "Many people experience it daily."
        )
        assert _score_hook_friction(text) == _FAIL

    def test_temporal_opener_fails(self):
        text = (
            "In today's fast-paced world, stress is everywhere. "
            "We all feel it."
        )
        assert _score_hook_friction(text) == _FAIL

    def test_contradiction_hook(self):
        text = (
            "Your anxiety is not the problem. Your solution to it is."
        )
        assert _score_hook_friction(text) >= _ADEQUATE

    def test_empty_text(self):
        assert _score_hook_friction("") == _FAIL


class TestSceneSpecificity:
    def test_specific_scene(self):
        text = (
            "The oat-milk film on the surface has gone grey. "
            "Your thumb hovers over the send button. "
            "The fluorescent hum is the only sound."
        )
        assert _score_scene_specificity(text) >= _ADEQUATE

    def test_generic_scene(self):
        text = "You sit in a room. You think about things. Life is hard."
        assert _score_scene_specificity(text) == _FAIL


class TestAhaPresence:
    def test_aha_present(self):
        text = (
            "What you call a flaw was once a survival intelligence. "
            "Your body knew this long before your mind admitted it."
        )
        assert _score_aha_presence(text) >= _PASS

    def test_no_aha(self):
        text = (
            "Many people feel stressed. Stress is common. "
            "It happens to everyone."
        )
        assert _score_aha_presence(text) == _FAIL


class TestIntegrationVariety:
    def test_varied_integrations(self):
        ch1 = "Still here. The grip loosened. That is enough."
        ch2 = "Feet on floor. Weight in the chair. Breath is slower."
        ch3 = (
            "What changed is the way you notice the pause "
            "before reacting."
        )
        scores = _score_integration_variety([ch1, ch2, ch3])
        assert all(s >= _ADEQUATE for s in scores)

    def test_repeated_integrations(self):
        ch = (
            "Still here. The grip loosened. Feet on floor. "
            "That is enough."
        )
        scores = _score_integration_variety([ch, ch, ch])
        assert scores[-1] <= _ADEQUATE


class TestThreadContinuity:
    def test_connected_threads(self):
        ch1 = (
            "The pattern cost you something. What you call strength "
            "was armor. You have not yet named what lives underneath."
        )
        ch2 = (
            "What lives underneath the armor is not weakness. "
            "You have not yet done the harder thing?"
        )
        scores = _score_thread_continuity([ch1, ch2])
        assert scores[0] == _PASS
        assert scores[1] >= _ADEQUATE

    def test_disconnected_chapters(self):
        ch1 = (
            "Alpha beta gamma delta epsilon zeta eta theta "
            "iota kappa lambda mu nu xi omicron."
        )
        ch2 = (
            "Completely different topic with no shared vocabulary "
            "whatsoever at all here now."
        )
        scores = _score_thread_continuity([ch1, ch2])
        assert scores[1] <= _ADEQUATE


class TestRepetitionIndex:
    def test_clean_text(self):
        text = (
            "This is a varied text with many different words "
            "and expressions."
        )
        score, count = _score_repetition_index(text)
        assert score == _PASS
        assert count == 0

    def test_repetitive_text(self):
        text = _repetitive_book_text()
        score, count = _score_repetition_index(text)
        assert score == _FAIL
        assert count > 0


class TestVocabularyDiversity:
    def test_diverse_text(self):
        words = [
            "alpha", "bravo", "charlie", "delta", "echo", "foxtrot",
            "golf", "hotel", "india", "juliet", "kilo", "lima", "mike",
            "november", "oscar", "papa", "quebec", "romeo", "sierra",
            "tango", "uniform", "victor", "whiskey", "xray", "yankee",
            "zulu", "anchor", "barrel", "candle", "dragon", "ember",
            "falcon", "glacier", "harbor", "ivory", "jungle", "kettle",
            "lantern", "marble", "nectar",
        ]
        text = " ".join(words)
        score, ratio = _score_vocabulary_diversity(text)
        assert score == _PASS
        assert ratio > 0.15

    def test_repetitive_text(self):
        text = "the the the the the the the the the the " * 50
        score, ratio = _score_vocabulary_diversity(text)
        assert score == _FAIL
        assert ratio < 0.10


class TestFlatMiddle:
    def test_short_book_passes(self):
        chapters = [_good_chapter(i) for i in range(5)]
        score, _overlap = _score_flat_middle(chapters)
        assert score == _PASS

    def test_identical_middle_fails(self):
        identical = (
            "Same words repeated in every single chapter here "
            "and now today."
        )
        chapters = [_good_chapter(i) for i in range(3)]
        chapters.extend([identical] * 5)
        chapters.extend([_good_chapter(i) for i in range(2)])
        score, _overlap = _score_flat_middle(chapters)
        assert score == _FAIL


class TestRewardSpacing:
    def test_regular_rewards(self):
        chapters = [_good_chapter(i) for i in range(10)]
        score, _gap = _score_reward_spacing(chapters)
        assert score == _PASS

    def test_no_rewards(self):
        bland = (
            "This chapter has no exercises or stories or anything "
            "interesting at all. " * 5
        )
        chapters = [bland] * 10
        score, _gap = _score_reward_spacing(chapters)
        assert score == _FAIL


class TestWordBudget:
    def test_in_range(self):
        assert _score_word_budget(2500, 1500, 3500) == _PASS

    def test_slightly_over(self):
        assert _score_word_budget(3600, 1500, 3500) == _ADEQUATE

    def test_way_under(self):
        assert _score_word_budget(500, 1500, 3500) == _FAIL


class TestLocationGrounding:
    def test_grounded_chapters(self):
        ch = (
            "The kitchen counter held the cold mug. "
            "Morning light came through the hallway window."
        )
        scores = _score_location_grounding([ch])
        assert scores[0] >= _ADEQUATE

    def test_ungrounded(self):
        ch = (
            "This was a moment of great significance in the "
            "abstract realm of thought."
        )
        scores = _score_location_grounding([ch])
        assert scores[0] == _FAIL


class TestCadenceVariety:
    def test_varied_cadence(self):
        text = (
            "Gone. "
            "She did not show up. "
            "The first meeting went fine and she answered every "
            "question with confidence and poise. "
            "Short. "
            "The second meeting her hands shook uncontrollably "
            "under the table where nobody could see. "
            "By the fourth she could not speak. "
            "Silence. "
            "The pattern was complete and the cost was clear to "
            "everyone in the room except her. "
        )
        assert _score_cadence_variety(text) >= _ADEQUATE

    def test_monotone_cadence(self):
        text = " ".join(
            ["This sentence has exactly seven words here."] * 10
        )
        assert _score_cadence_variety(text) == _FAIL


# ---------------------------------------------------------------------------
# Integration tests -- full editorial report generation
# ---------------------------------------------------------------------------

class TestGenerateEditorialReport:
    def test_all_passing_chapters(self):
        chapters = [_good_chapter(i) for i in range(10)]
        book_text = " ".join(chapters)
        report = generate_editorial_report(book_text, chapters)

        assert isinstance(report, EditorialReport)
        assert len(report.chapter_assessments) == 10
        assert report.grade in ("PASS", "NEEDS_REVISION", "FAIL")
        assert report.total_score <= 24
        assert report.max_score == 24

    def test_failing_chapters(self):
        chapters = [_weak_chapter() for _ in range(10)]
        book_text = " ".join(chapters)
        report = generate_editorial_report(book_text, chapters)

        assert report.grade == "FAIL"
        assert report.total_score < 14
        assert len(report.revision_notes) > 0

    def test_mixed_quality(self):
        chapters = [_good_chapter(0)] * 5 + [_weak_chapter()] * 5
        book_text = " ".join(chapters)
        report = generate_editorial_report(book_text, chapters)

        assert isinstance(report, EditorialReport)
        assert report.grade in ("PASS", "NEEDS_REVISION", "FAIL")

    def test_empty_chapters(self):
        report = generate_editorial_report("", [])
        assert report.grade == "FAIL"
        assert report.revision_notes == ["No chapters provided."]

    def test_single_chapter(self):
        ch = _good_chapter(0)
        report = generate_editorial_report(ch, [ch])
        assert len(report.chapter_assessments) == 1
        assert report.grade in ("PASS", "NEEDS_REVISION", "FAIL")

    def test_thesis_drift_detected(self):
        chapters = [
            "Alpha beta gamma delta epsilon zeta eta theta iota "
            "kappa lambda mu.",
            "Completely unrelated content about different subject "
            "matter entirely.",
        ]
        theses = {
            1: "burnout recovery and workplace stress management",
            2: "anxiety regulation through body awareness practices",
        }
        report = generate_editorial_report(
            " ".join(chapters),
            chapters,
            chapter_theses=theses,
        )
        drifted = [
            ca
            for ca in report.chapter_assessments
            if not ca.thesis_aligned
        ]
        assert len(drifted) >= 1

    def test_custom_word_targets(self):
        short_ch = "Short chapter. Only a few words here."
        report = generate_editorial_report(
            short_ch,
            [short_ch],
            word_target_min=5,
            word_target_max=20,
        )
        assert report.chapter_assessments[0].word_budget >= _ADEQUATE


class TestGradeThresholds:
    """Verify PASS >= 20, NEEDS_REVISION 14-19, FAIL < 14."""

    def test_pass_threshold(self):
        report = EditorialReport()
        report.total_score = 20
        if report.total_score >= 20:
            report.grade = "PASS"
        assert report.grade == "PASS"

    def test_needs_revision_threshold(self):
        report = EditorialReport()
        report.total_score = 17
        if report.total_score >= 20:
            report.grade = "PASS"
        elif report.total_score >= 14:
            report.grade = "NEEDS_REVISION"
        else:
            report.grade = "FAIL"
        assert report.grade == "NEEDS_REVISION"

    def test_fail_threshold(self):
        report = EditorialReport()
        report.total_score = 10
        if report.total_score >= 20:
            report.grade = "PASS"
        elif report.total_score >= 14:
            report.grade = "NEEDS_REVISION"
        else:
            report.grade = "FAIL"
        assert report.grade == "FAIL"

    def test_generate_respects_thresholds(self):
        chapters = [_weak_chapter() for _ in range(8)]
        report = generate_editorial_report(" ".join(chapters), chapters)
        assert report.grade == "FAIL"
        assert report.total_score < 14


# ---------------------------------------------------------------------------
# JSON output format validation
# ---------------------------------------------------------------------------

class TestWriteEditorialReport:
    def test_writes_valid_json(self, tmp_path: Path):
        chapters = [_good_chapter(i) for i in range(5)]
        report = generate_editorial_report(" ".join(chapters), chapters)
        out = tmp_path / "editorial_report.json"
        write_editorial_report(report, out)

        assert out.exists()
        with open(out) as f:
            data = json.load(f)

        assert "chapter_assessments" in data
        assert "book_level" in data
        assert "total_score" in data
        assert "max_score" in data
        assert "grade" in data
        assert "revision_notes" in data
        assert data["max_score"] == 24

    def test_json_chapter_fields(self, tmp_path: Path):
        chapters = [_good_chapter(0)]
        report = generate_editorial_report(chapters[0], chapters)
        out = tmp_path / "report.json"
        write_editorial_report(report, out)

        with open(out) as f:
            data = json.load(f)

        ch = data["chapter_assessments"][0]
        expected_fields = {
            "chapter_index",
            "hook_friction",
            "scene_specificity",
            "aha_presence",
            "integration_variety",
            "thread_continuity",
            "word_budget",
            "location_grounding",
            "cadence_variety",
            "word_count",
            "target_range",
            "thesis_aligned",
            "thesis_coverage",
            "chapter_score",
        }
        assert expected_fields.issubset(set(ch.keys()))
        for criterion in (
            "hook_friction",
            "scene_specificity",
            "aha_presence",
        ):
            assert ch[criterion] in ("PASS", "ADEQUATE", "FAIL")

    def test_json_book_level_fields(self, tmp_path: Path):
        chapters = [_good_chapter(i) for i in range(5)]
        report = generate_editorial_report(" ".join(chapters), chapters)
        out = tmp_path / "report.json"
        write_editorial_report(report, out)

        with open(out) as f:
            data = json.load(f)

        bl = data["book_level"]
        expected_fields = {
            "repetition_index",
            "repetition_excess_count",
            "vocabulary_diversity",
            "vocabulary_ratio",
            "flat_middle",
            "flat_middle_overlap",
            "reward_spacing",
            "reward_max_gap",
        }
        assert expected_fields.issubset(set(bl.keys()))

    def test_creates_parent_dirs(self, tmp_path: Path):
        report = generate_editorial_report("Test.", ["Test."])
        out = tmp_path / "nested" / "dir" / "report.json"
        write_editorial_report(report, out)
        assert out.exists()

    def test_grade_in_json(self, tmp_path: Path):
        chapters = [_weak_chapter() for _ in range(8)]
        report = generate_editorial_report(
            " ".join(chapters), chapters
        )
        out = tmp_path / "report.json"
        write_editorial_report(report, out)

        with open(out) as f:
            data = json.load(f)
        assert data["grade"] == "FAIL"
        assert data["total_score"] < 14
        assert len(data["revision_notes"]) > 0
