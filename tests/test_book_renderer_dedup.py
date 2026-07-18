"""Unit tests for `_dedup_paragraphs_book_wide` (patch (a) of the dedupe-leak
diagnosis at `artifacts/qa/dedupe_leak_diagnosis_2026-05-16.md`).

The function is the cross-chapter safety net that strips verbatim paragraph
repeats that survived intra-chapter dedupe. The chapter-scoped
`_dedup_repeated_blocks` resets its seen-set at each `Chapter N` heading per
PR #939's documented trade-off; this pass closes that gap.
"""

from __future__ import annotations

import logging
import re

import pytest

from phoenix_v4.rendering.book_renderer import (
    _dedup_paragraphs_book_wide,
    clean_for_delivery,
)


# --------------------------------------------------------------------------- #
# Fixtures                                                                    #
# --------------------------------------------------------------------------- #


# Slightly tweaked from the real Tanya/spiral leak (~210 chars / ~33 words) so
# it clears both gates (>=120 chars AND >=30 words) and exercises the safety
# net the way the production canary did.
#
# OPD-109 Phase 3 (2026-05-19): the calibration upgraded atom-sized paragraphs
# (20-200 words) from keep=1 to keep=2 by default — the 53-word paragraph below
# now falls into the atom bucket. Tests asserting the legacy keep=1 cap pass
# the explicit `keep=1` kwarg OR set `PHOENIX_ATOM_PARAGRAPH_KEEP=1` so the
# regression-protection intent is preserved. The default-behavior tests assert
# the new keep=2 cap.
_REPEATED_PARAGRAPH = (
    "Tanya delivers a campaign that underperforms expectations and the "
    "underperformance triggers a spiral about being replaced by someone "
    "younger and faster, and by the end of the spiral she is convinced "
    "her shoulders are tight and the spiral has a narrative momentum of "
    "its own that she did not invent."
)


def _build_book(repeats: int = 16, chapters: int = 12) -> str:
    """Return a 12-chapter book.txt where a 200-char paragraph repeats `repeats`
    times spread across `chapters` chapters. Each chapter also gets a unique
    long paragraph so the book isn't entirely repeats."""
    parts: list[str] = []
    placed = 0
    for ch in range(1, chapters + 1):
        parts.append(f"Chapter {ch}")
        parts.append(
            f"Unique chapter-{ch} opening paragraph with enough words to "
            f"clear the dedupe min_words gate of thirty: this is body text "
            f"specific to chapter {ch} and intentionally unique across the "
            f"manuscript so the safety-net does not touch it."
        )
        # Distribute the repeats roughly evenly across chapters.
        if placed < repeats:
            slots_left = repeats - placed
            chapters_left = chapters - ch + 1
            per_ch = max(1, slots_left // chapters_left)
            for _ in range(per_ch):
                if placed < repeats:
                    parts.append(_REPEATED_PARAGRAPH)
                    placed += 1
        # A short transitional line that MUST be allowed to repeat.
        parts.append("She thinks about the day ahead.")
    return "\n\n".join(parts)


# --------------------------------------------------------------------------- #
# Core dedupe behaviour                                                       #
# --------------------------------------------------------------------------- #


def test_dedupes_long_repeat_to_default_keep_count() -> None:
    """OPD-109 Phase 3: atom-sized paragraphs default to keep=2.

    The 53-word `_REPEATED_PARAGRAPH` falls into the atom bucket (20-200 words),
    so the default keep cap is 2. 14 occurrences are elided from the 16
    spawned by the fixture.
    """
    book = _build_book(repeats=16)
    assert book.count(_REPEATED_PARAGRAPH) == 16

    deduped, notes = _dedup_paragraphs_book_wide(book)

    assert deduped.count(_REPEATED_PARAGRAPH) == 2
    assert len(notes) == 14
    for note in notes:
        assert "book_wide_paragraph_dedupe" in note


def test_dedupes_long_repeat_to_legacy_keep_one_under_explicit_override(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Legacy `keep=1` cap is still reachable via the env override.

    `PHOENIX_ATOM_PARAGRAPH_KEEP=1` disables the OPD-109 Phase 3 atom bucket,
    restoring the pre-Phase-3 single-occurrence cap. Regression protection
    for production canaries that opt back in.
    """
    monkeypatch.setenv("PHOENIX_ATOM_PARAGRAPH_KEEP", "1")
    book = _build_book(repeats=16)
    assert book.count(_REPEATED_PARAGRAPH) == 16

    deduped, notes = _dedup_paragraphs_book_wide(book)

    assert deduped.count(_REPEATED_PARAGRAPH) == 1
    assert len(notes) == 15
    for note in notes:
        assert "book_wide_paragraph_dedupe" in note


def test_short_paragraphs_are_not_affected() -> None:
    book = _build_book(repeats=16)
    # The short "She thinks about the day ahead." transitional line repeats
    # once per chapter — must NOT be touched.
    before_short = book.count("She thinks about the day ahead.")
    assert before_short == 12

    deduped, _notes = _dedup_paragraphs_book_wide(book)
    assert deduped.count("She thinks about the day ahead.") == before_short


def test_chapter_headings_preserved() -> None:
    book = _build_book(repeats=16)
    deduped, _notes = _dedup_paragraphs_book_wide(book)
    # All 12 chapter headings must survive.
    chapter_count = len(re.findall(r"^Chapter\s+\d+$", deduped, re.MULTILINE))
    assert chapter_count == 12


def test_unique_paragraphs_preserved() -> None:
    book = _build_book(repeats=16)
    deduped, _notes = _dedup_paragraphs_book_wide(book)
    for ch in range(1, 13):
        marker = f"Unique chapter-{ch} opening paragraph"
        assert marker in deduped, f"unique paragraph for ch{ch} was dropped"


def test_logs_elision_exactly_once_per_fingerprint(caplog: pytest.LogCaptureFixture) -> None:
    """OPD-109 Phase 3: the log line now reports `kept_cap_upper_bound` (the
    maximum keep across the per-paragraph buckets) so the operator can tell
    whether the atom-bucket cap or the base cap drove the strip.
    """
    book = _build_book(repeats=16)
    with caplog.at_level(logging.INFO, logger="phoenix_v4.rendering.book_renderer"):
        _dedup_paragraphs_book_wide(book)
    matching = [r for r in caplog.records if "book-wide paragraph elision" in r.getMessage()]
    assert len(matching) == 1
    msg = matching[0].getMessage()
    assert "appeared 16 times" in msg
    assert "kept_cap_upper_bound 2" in msg


def test_keep_knob_override_via_kwarg() -> None:
    book = _build_book(repeats=16)
    deduped_keep2, notes_keep2 = _dedup_paragraphs_book_wide(book, keep=2)
    assert deduped_keep2.count(_REPEATED_PARAGRAPH) == 2
    assert len(notes_keep2) == 14

    deduped_keep5, notes_keep5 = _dedup_paragraphs_book_wide(book, keep=5)
    assert deduped_keep5.count(_REPEATED_PARAGRAPH) == 5
    assert len(notes_keep5) == 11


def test_keep_knob_override_via_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PHOENIX_BOOK_DEDUPE_KEEP", "3")
    book = _build_book(repeats=16)
    deduped, notes = _dedup_paragraphs_book_wide(book)
    assert deduped.count(_REPEATED_PARAGRAPH) == 3
    assert len(notes) == 13


def test_empty_input_returns_empty() -> None:
    out, notes = _dedup_paragraphs_book_wide("")
    assert out == ""
    assert notes == []

    out, notes = _dedup_paragraphs_book_wide("   \n\n  \n")
    assert notes == []


def test_no_repeats_returns_text_unchanged_modulo_normalization() -> None:
    book = (
        "Chapter 1\n\n"
        "Para A with enough words to clear the gate, it has about forty "
        "words and well over one hundred and twenty characters of body "
        "text so the safety net considers it eligible for dedupe.\n\n"
        "Chapter 2\n\n"
        "Para B with enough words to clear the gate, it has about forty "
        "words and well over one hundred and twenty characters of body "
        "text so the safety net considers it eligible for dedupe.\n"
    )
    deduped, notes = _dedup_paragraphs_book_wide(book)
    assert notes == []
    assert "Para A" in deduped
    assert "Para B" in deduped


def test_casing_and_whitespace_preserved_in_kept_paragraph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Casing/whitespace preservation regression test.

    OPD-109 Phase 3: the 40-word `p1`/`p2` pair falls into the atom bucket,
    where the default keep cap is 2 (both would survive). Restore the legacy
    keep=1 contract for this test so the kept-verbatim assertion still bites
    on the first occurrence's casing.
    """
    monkeypatch.setenv("PHOENIX_ATOM_PARAGRAPH_KEEP", "1")
    p1 = (
        "  TANYA   DELIVERS  a campaign   that underperforms expectations and "
        "the underperformance triggers a spiral about being replaced by "
        "someone younger and faster, and by the end of the spiral she is "
        "convinced her shoulders are tight."
    )
    p2 = (
        "tanya delivers a campaign that underperforms expectations and "
        "the underperformance triggers a spiral about being replaced by "
        "someone younger and faster, and by the end of the spiral she is "
        "convinced her shoulders are tight."
    )
    text = f"Chapter 1\n\n{p1}\n\nChapter 2\n\n{p2}\n"
    deduped, notes = _dedup_paragraphs_book_wide(text)
    # The first paragraph (with unusual casing) is kept verbatim after strip();
    # the second is elided. We check that "TANYA" survived (i.e., kept text
    # was not lowercased) and the second occurrence is gone.
    assert "TANYA" in deduped
    assert deduped.count("tanya delivers a campaign") == 0  # only TANYA form kept
    assert len(notes) == 1


# --------------------------------------------------------------------------- #
# Wiring into clean_for_delivery                                              #
# --------------------------------------------------------------------------- #


def test_clean_for_delivery_invokes_book_wide_dedupe() -> None:
    """OPD-109 Phase 3: clean_for_delivery still routes through book-wide
    dedup; the atom-sized `_REPEATED_PARAGRAPH` now lands at 2 occurrences
    (atom-bucket keep=2) instead of 1.
    """
    book = _build_book(repeats=16)
    gov: dict = {}
    out = clean_for_delivery(book, governance_report=gov)
    assert out.count(_REPEATED_PARAGRAPH) == 2
    assert "whole_book_dedupe_notes" in gov
    notes = gov["whole_book_dedupe_notes"]
    # Must be non-empty: chapter-scoped dedupe leaves at least one occurrence
    # per chapter standing (12 chapters in fixture), so the book-wide pass
    # must elide >= 10 of them after the atom-bucket retention.
    assert len(notes) >= 1
    for note in notes:
        assert "book_wide_paragraph_dedupe" in note


def test_clean_for_delivery_no_governance_report_does_not_crash() -> None:
    """Smoke: clean_for_delivery without a governance report must not raise.

    OPD-109 Phase 3: with atom-bucket keep=2, the final count is 2 (not 1).
    """
    book = _build_book(repeats=16)
    out = clean_for_delivery(book)
    assert out.count(_REPEATED_PARAGRAPH) == 2
