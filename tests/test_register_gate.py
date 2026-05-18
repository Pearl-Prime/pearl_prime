"""
Tests for phoenix_v4.quality.register_gate.

Per spec §7 — regression tests for each F1-F7 detector + the calibration
assertion that the gate MUST fail the 2026-05-18 verdict book.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.quality.register_gate import (
    evaluate_register,
    evaluate_register_from_path,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


# ─────────────────────────────────────────────────────────────────────────────
# F1 — templated paragraph repetition
# ─────────────────────────────────────────────────────────────────────────────

def test_f1_warns_on_2_near_duplicate_paragraphs():
    """
    Two paragraphs with high word-set Jaccard overlap should produce F1 WARN.

    Note: the F1 detector uses word-set Jaccard as a proxy for paragraph
    similarity. Two paragraphs about anxiety with DIFFERENT mechanism vocab
    (e.g. "identity anxiety" vs "allostatic load") may share <55% word
    content even though they share template structure — those are flagged
    by the real-book calibration test instead. This unit test verifies that
    near-verbatim repeats DO get flagged.
    """
    para = (
        "The mechanism is hypervigilance as trained response. This is what happens "
        "in the body of the professional when the performance review activates the "
        "system built for survival but now runs in the workplace context. Your thumb "
        "scrolling. Your survival hardware is responding to real inputs. The data "
        "is correct. The output makes sense for the data."
    )
    body = (
        f"Chapter 1\n\n{para}\n\nA different paragraph about coffee and the morning.\n\n"
        f"Chapter 2\n\n{para} The body is the messenger.\n"
    )
    result = evaluate_register(body)
    f1 = [f for f in result.findings if f.failure_id == "F1"]
    assert len(f1) >= 1, "expected at least one F1 finding for the duplicated paragraph template"
    # Cluster size 2 = WARN per spec
    assert any(f.severity == "WARN" for f in f1)


def test_f1_fails_on_3_plus_template_instances():
    """Three+ near-duplicates of the same paragraph template should produce F1 FAIL."""
    template = (
        "The mechanism is {MECH}. This is what happens in the body of the professional "
        "when the unclear career path activates the system that was built for survival "
        "but now runs in the context of the workplace. Your restless legs under the desk. "
        "The vigilance loop is intact. The pressure is genuine. The body is staying in calibration with the pressure."
    )
    body = "Chapter 1\n\n" + template.format(MECH="identity anxiety") + "\n\n"
    body += "Chapter 2\n\n" + template.format(MECH="allostatic load") + "\n\n"
    body += "Chapter 3\n\n" + template.format(MECH="anticipatory anxiety") + "\n\n"
    result = evaluate_register(body)
    f1_fail = [f for f in result.findings if f.failure_id == "F1" and f.severity == "FAIL"]
    assert len(f1_fail) >= 1, "expected at least one F1 FAIL for 3+ instances of the same template"


# ─────────────────────────────────────────────────────────────────────────────
# F2 — broken slot fragments (HARD_FAIL)
# ─────────────────────────────────────────────────────────────────────────────

def test_f2a_hard_fails_on_colon_period_artifact():
    """': .' empty-slot artifact must HARD_FAIL the book."""
    body = "Chapter 1\n\nAhjan's reading of this is precise: .\n\nMore content here.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(f.failure_id == "F2" and "F2.A" in f.summary for f in result.findings)


def test_f2b_hard_fails_on_dangling_preposition():
    """Paragraph ending with preposition + period must HARD_FAIL."""
    body = "Chapter 1\n\nIn Ahjan's framework, the path begins with.\n\nMore content.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(f.failure_id == "F2" and "F2.B" in f.summary for f in result.findings)


def test_f2c_hard_fails_on_lowercase_noun_sentence_start():
    """Sentence starting with lowercase noun must HARD_FAIL."""
    body = "Chapter 1\n\nThe pipeline ran. mechanism running continuously is written into your biology.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(f.failure_id == "F2" and "F2.C" in f.summary for f in result.findings)


def test_f2d_hard_fails_on_sub_4_word_fragment():
    """A 3-word standalone fragment like 'Ahjan's the practice' must HARD_FAIL."""
    body = "Chapter 1\n\nAhjan's the practice\n\nThe next real paragraph here.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(f.failure_id == "F2" and "F2.D" in f.summary for f in result.findings)


# ─────────────────────────────────────────────────────────────────────────────
# F3 — off-doctrine teacher-bank overrun
# ─────────────────────────────────────────────────────────────────────────────

def test_f3_fails_on_3_plus_off_doctrine_tokens_in_chapter_for_ahjan():
    """ahjan (Tantric Buddhist) book with Krishna + Bhakti + transmission of light = FAIL."""
    body = (
        "Chapter 1\n\n"
        "This direct transmission of light from teacher to student is sacred.\n"
        "Krishna teaches focus through work.\n"
        "Bhakti yoga underscores self-love and balanced relationships.\n"
    )
    result = evaluate_register(body, teacher_id="ahjan")
    f3_fail = [f for f in result.findings if f.failure_id == "F3" and f.severity == "FAIL"]
    assert len(f3_fail) >= 1


def test_f3_no_fire_without_teacher_id():
    """Without teacher_id, F3 is skipped entirely (defaults can't be evaluated)."""
    body = "Chapter 1\n\nKrishna teaches Bhakti yoga. Transmission of light.\n"
    result = evaluate_register(body, teacher_id="")
    f3 = [f for f in result.findings if f.failure_id == "F3"]
    assert len(f3) == 0


# ─────────────────────────────────────────────────────────────────────────────
# F4 — closing-line repetition
# ─────────────────────────────────────────────────────────────────────────────

def test_f4_warns_when_2_chapters_share_closing():
    closing = "What remains is the moment after the alarm fires, when your body still wants to obey a prediction."
    body = (
        f"Chapter 1\n\nSome opening.\nMore content here for length.\nFinal beat. {closing}\n\n"
        f"Chapter 2\n\nDifferent opening.\nDifferent middle.\nDifferent closing beat. {closing}\n"
    )
    result = evaluate_register(body)
    f4 = [f for f in result.findings if f.failure_id == "F4"]
    assert len(f4) == 1
    assert f4[0].severity == "WARN"


def test_f4_fails_when_3_plus_chapters_share_closing():
    closing = "What remains is the moment after the alarm fires, when your body still wants to obey a prediction."
    body = ""
    for i in range(1, 4):
        body += f"Chapter {i}\n\nUnique opening for chapter {i}. Middle filler. {closing}\n\n"
    result = evaluate_register(body)
    f4 = [f for f in result.findings if f.failure_id == "F4"]
    assert any(f.severity == "FAIL" for f in f4)


# ─────────────────────────────────────────────────────────────────────────────
# F6 — pedagogical-cadence 4-gram repetition
# ─────────────────────────────────────────────────────────────────────────────

def test_f6_fails_when_cadence_4gram_repeats_3_plus_times():
    """Same 4-gram sentence-length sequence appearing in 3+ paragraphs across chapters."""
    # Build sentences with fixed word counts that produce identical 4-grams
    # word counts [6, 6, 11, 8] (the audit's known cadence)
    s1 = "The variables are real and concrete."  # 6 words
    s2 = "The stakes are genuine and present."  # 6 words
    s3 = "The uncertainty is not manufactured by your anxiety alone here."  # 11 words
    s4 = "It is manufactured by the surrounding conditions."  # 8 words
    paragraph = " ".join([s1, s2, s3, s4])
    body = ""
    for i in range(1, 5):  # 4 chapters with identical cadence
        body += f"Chapter {i}\n\n{paragraph}\n\n"
    result = evaluate_register(body)
    f6 = [f for f in result.findings if f.failure_id == "F6"]
    assert len(f6) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# F7 — over-prescribed practice density
# ─────────────────────────────────────────────────────────────────────────────

def test_f7_fails_when_chapter_has_4_plus_distinct_practices():
    body = (
        "Chapter 1\n\n"
        "Try this for ninety seconds: notice where your attention is scanning.\n\n"
        "Breathe in through your nose for four counts. Hold for two seconds. Out for six.\n\n"
        "Notice a thought that repeats itself in your mind. Follow it back step by step.\n\n"
        "Write the prediction your mind is treating like a fact for the next five minutes.\n\n"
    )
    result = evaluate_register(body)
    f7 = [f for f in result.findings if f.failure_id == "F7" and f.severity == "FAIL"]
    assert len(f7) >= 1


# ─────────────────────────────────────────────────────────────────────────────
# Verdict aggregation
# ─────────────────────────────────────────────────────────────────────────────

def test_clean_book_passes():
    body = (
        "Chapter 1\n\nA clean opening paragraph with embodied prose. The body knows. The chest tightens once. The breath returns.\n\n"
        "Another paragraph with a different texture entirely. Eyes open. Hands on the desk. The morning continues.\n\n"
        "Chapter 2\n\nA different opening. New scene, new character. The light comes in through different windows.\n\n"
        "Different details. Different beat. Different closing line for this chapter that is wholly its own.\n\n"
        "Chapter 3\n\nMore variety. The third chapter takes a third angle. Specific somatic detail throughout.\n\n"
        "Yet another distinct closing that does not mirror the prior chapters at all whatsoever.\n"
    )
    result = evaluate_register(body)
    # Note: without active F1-F7 triggers, should be PASS or ADVISORY
    assert result.verdict in {"PASS", "ADVISORY"}, f"clean book got verdict={result.verdict} with findings={result.findings}"


def test_hard_fail_short_circuits():
    """Any F2 violation produces HARD_FAIL regardless of other findings."""
    body = "Chapter 1\n\nClean clean clean. But this colon: .\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"


# ─────────────────────────────────────────────────────────────────────────────
# Calibration assertion — the gate MUST FAIL the 2026-05-18 verdict book
# ─────────────────────────────────────────────────────────────────────────────

CALIBRATION_BOOK = (
    REPO_ROOT
    / "artifacts"
    / "pearl_prime"
    / "extended_book_2h"
    / "ahjan_gen_z_professionals_anxiety_en_US_20260518T131809Z_round5"
    / "book.txt"
)


@pytest.mark.skipif(not CALIBRATION_BOOK.exists(), reason="calibration book not on disk in this worktree")
def test_calibration_book_must_fail():
    """
    Per spec §7: applying the gate to the 2026-05-18 verdict book must
    produce a FAIL or HARD_FAIL verdict. If it passes, thresholds are too lenient.
    """
    result = evaluate_register_from_path(
        CALIBRATION_BOOK,
        teacher_id="ahjan",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
    )
    assert result.verdict in {"FAIL", "HARD_FAIL"}, (
        f"calibration book got verdict={result.verdict} — register gate thresholds "
        f"are too lenient. Findings: {len(result.findings)}"
    )
    # Specifically, the audit identified F1, F2, F3, F4 as definite failures
    failure_ids = {f.failure_id for f in result.findings}
    for fid in {"F1", "F2", "F3", "F4"}:
        assert fid in failure_ids, f"expected {fid} finding on calibration book; got {failure_ids}"
