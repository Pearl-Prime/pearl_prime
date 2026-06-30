"""
Regression Museum backfill test — the permanent ratchet.

This test loads the known-bad book (saved at the moment each failure class was
first discovered) and asserts that EVERY expected failure class fires.

If you weaken or delete a detector, this test fails.
If you add a new failure class, add it to `expected_classes` here.
"""

import re
from pathlib import Path

import pytest

from phoenix_v4.quality.regression_museum import run_museum_gates, Violation

FIXTURE = Path(__file__).parent / "fixtures" / "regression_museum" / "known_bad_book.txt"

PERSONA = "gen_z_professionals"


def _load_book_from_flat_text(path: Path) -> dict:
    """
    Parse the flat book.txt format into the internal book dict.

    Format: chapters separated by lines matching /^Chapter \d+/ or
    by the presence of a chapter heading line.
    Each chapter has index (1-based) and text.
    """
    raw = path.read_text(encoding="utf-8", errors="replace")

    # Split on "Chapter N" headings
    parts = re.split(r"(?m)^(Chapter \d+.*?)$", raw)

    chapters = []
    # parts: [preamble, "Chapter 1", body1, "Chapter 2", body2, ...]
    i = 1  # skip leading preamble if blank
    chapter_index = 1
    while i + 1 < len(parts):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        chapters.append({
            "index": chapter_index,
            "heading": heading,
            "text": body.strip(),
            "exercise_atom_ids": [],  # flat format has no explicit atom IDs
        })
        chapter_index += 1
        i += 2

    if not chapters:
        # Fallback: treat entire file as one chapter
        chapters = [{"index": 1, "heading": "Book", "text": raw, "exercise_atom_ids": []}]

    return {"chapters": chapters, "persona": PERSONA}


@pytest.fixture(scope="module")
def known_bad_book():
    assert FIXTURE.exists(), f"Known-bad fixture missing: {FIXTURE}"
    return _load_book_from_flat_text(FIXTURE)


@pytest.fixture(scope="module")
def museum_result(known_bad_book):
    return run_museum_gates(known_bad_book, persona=PERSONA)


def test_known_bad_book_is_blocked(museum_result):
    """The broken book must be blocked — not just warned."""
    assert museum_result["blocked"], (
        f"Expected known-bad book to be BLOCKED. Got: {museum_result['summary']}"
    )


def test_doubled_word_fires(museum_result):
    """'The the train' — doubled-word artifact must be detected."""
    classes = {v.failure_class for v in museum_result["violations"]}
    assert "doubled_word" in classes, (
        "doubled_word detector did not fire on known-bad book. "
        "Check detectors.detect_doubled_word."
    )


def test_off_persona_vocabulary_fires(museum_result):
    """Bhakti Yoga, Six Worlds, enlightened teacher appear in gen_z book."""
    classes = {v.failure_class for v in museum_result["violations"]}
    assert "off_persona_vocabulary" in classes, (
        "off_persona_vocabulary detector did not fire. "
        "Bhakti/Six Worlds/enlightened teacher should be blocked terms."
    )


def test_cross_chapter_verbatim_duplication_fires(museum_result):
    """'Your badge beeps at the door...' block is repeated verbatim across chapters."""
    classes = {v.failure_class for v in museum_result["violations"]}
    assert "cross_chapter_verbatim_duplication" in classes, (
        "cross_chapter_verbatim_duplication detector did not fire. "
        "Known-bad book has entire chapter blocks pasted verbatim."
    )


def test_repeated_scene_anchor_fires(museum_result):
    """'soft daylight along the sill' appears 30+ times — should fire."""
    classes = {v.failure_class for v in museum_result["violations"]}
    assert "repeated_scene_anchor" in classes, (
        "repeated_scene_anchor detector did not fire. "
        "'soft daylight along the sill' appears dozens of times in the known-bad book."
    )


def test_off_persona_evidence_contains_known_terms(museum_result):
    """Spot-check: at least one violation references a real blocked term."""
    vocab_violations = [
        v for v in museum_result["violations"]
        if v.failure_class == "off_persona_vocabulary"
    ]
    assert vocab_violations, "No off_persona_vocabulary violations found"
    evidences = " ".join(v.evidence for v in vocab_violations).lower()
    known_terms = ["bhakti", "six worlds", "enlightened teacher", "self-realization", "dharma"]
    found = [t for t in known_terms if t in evidences]
    assert found, (
        f"Off-persona violations found but none contain expected terms {known_terms}. "
        f"Evidence sample: {evidences[:300]}"
    )


def test_doubled_word_evidence_contains_the_the(museum_result):
    """Spot-check: doubled-word violations include 'the the'."""
    dw_violations = [
        v for v in museum_result["violations"]
        if v.failure_class == "doubled_word"
    ]
    assert dw_violations, "No doubled_word violations found"
    evidences = " ".join(v.evidence for v in dw_violations).lower()
    assert "the the" in evidences, (
        f"doubled_word violations found but 'the the' not in evidence. "
        f"Evidence sample: {evidences[:300]}"
    )


def test_all_expected_classes_fire(museum_result):
    """
    Master ratchet: every expected failure class must fire on the known-bad book.
    Add new classes here as new failure classes are discovered and fixed.
    """
    expected_classes = {
        "doubled_word",
        "off_persona_vocabulary",
        "cross_chapter_verbatim_duplication",
        "cross_chapter_sentence_repeat",
        "repeated_scene_anchor",
    }
    found_classes = {v.failure_class for v in museum_result["violations"]}
    missing = expected_classes - found_classes
    assert not missing, (
        f"Museum detectors missing for these known failure classes: {missing}\n"
        f"Found: {found_classes}\n"
        f"Summary: {museum_result['summary']}"
    )


def test_cross_chapter_sentence_repeat_fires(museum_result):
    """The 6+ word sentence-granularity detector must flag repeated lines."""
    classes = {v.failure_class for v in museum_result["violations"]}
    assert "cross_chapter_sentence_repeat" in classes, (
        "cross_chapter_sentence_repeat detector did not fire on the known-bad book. "
        f"Summary: {museum_result['summary']}"
    )


def test_cross_chapter_sentence_repeat_clean_book_passes():
    """A book with no cross-chapter 6+ word sentence repeats yields no violations."""
    from phoenix_v4.quality.regression_museum.detectors import (
        detect_cross_chapter_sentence_repeat,
    )

    book = {
        "chapters": [
            {"index": 1, "text": "The morning light fell across the quiet kitchen table."},
            {"index": 2, "text": "A different sentence entirely lives inside this second chapter."},
            {"index": 3, "text": "Short lines pass."},  # < 6 words, ignored
        ]
    }
    assert detect_cross_chapter_sentence_repeat(book) == []

    repeated = {
        "chapters": [
            {"index": 1, "text": "This exact sentence appears in more than one chapter."},
            {"index": 2, "text": "This exact sentence appears in more than one chapter."},
        ]
    }
    violations = detect_cross_chapter_sentence_repeat(repeated)
    assert len(violations) == 1
    assert violations[0].failure_class == "cross_chapter_sentence_repeat"
