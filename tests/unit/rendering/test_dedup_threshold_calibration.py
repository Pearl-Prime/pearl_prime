"""
OPD-109 Phase 3 — dedup threshold calibration tests.

Defect ref: ws_opd109_phase3_selector_dedup_fix_20260519
Validation: deep_book_6h render with the OPD-109 Phase 2 enriched atom pool
            (15K new SCENE/STORY words) was eliding ~275 paragraphs per book
            via `_dedup_paragraphs_book_wide`. Rendered word count climbed
            only +3,400 vs. the +15K depth-pass headroom.

Fix: atom-sized paragraphs (20-200 words) are allowed up to
`_atom_paragraph_keep_default()` occurrences (defaults to 2; env override
`PHOENIX_ATOM_PARAGRAPH_KEEP`). Longer paragraphs (>200 words) keep the
legacy `keep=1` cap because they typically indicate template/scaffold
leakage that should not appear twice.

These tests cover:
    1. Atom-sized paragraph (50-80 words, twice) survives dedup.
    2. Atom-sized paragraph (50-80 words, thrice) gets one strip.
    3. Long paragraph (250+ words, twice) still gets stripped to 1.
    4. Short paragraph (<20 words) is always exempt (legacy behavior).
    5. Calibration: `keep=1` legacy is still the base; the atom-bucket keep
       is purely additive.
"""
from __future__ import annotations

import pytest

from phoenix_v4.rendering.book_renderer import (
    _atom_paragraph_keep_default,
    _dedup_paragraphs_book_wide,
    _keep_cap_for_paragraph,
)


def _para(n_words: int, suffix: str = "") -> str:
    """Build a paragraph with exactly `n_words` words.

    `suffix` differentiates two near-duplicates; default "" → identical
    paragraphs with the same fingerprint.
    """
    base = " ".join([f"word{i}" for i in range(n_words)])
    return f"{base}{suffix}"


# ---------------------------------------------------------------------------
# Test 1: atom-sized paragraph repeating twice → both kept.
# ---------------------------------------------------------------------------


def test_atom_sized_paragraph_twice_both_kept() -> None:
    """A 60-word paragraph appearing in two chapters should be preserved
    under the OPD-109 Phase 3 calibration (atom-bucket keep = 2).
    """
    para = _para(60)
    text = f"Chapter 1\n\n{para}\n\nfiller filler filler.\n\nChapter 2\n\n{para}\n\nfiller filler filler."

    deduped, notes = _dedup_paragraphs_book_wide(text)

    occurrences = deduped.count(para)
    assert occurrences == 2, (
        f"Atom-sized paragraph stripped: occurrences={occurrences} (want 2). "
        f"Notes: {notes}"
    )
    assert not notes, (
        f"Atom-sized twice should produce no elision notes; got {notes}"
    )


# ---------------------------------------------------------------------------
# Test 2: atom-sized paragraph repeating thrice → only two kept.
# ---------------------------------------------------------------------------


def test_atom_sized_paragraph_thrice_one_stripped() -> None:
    """A 60-word paragraph appearing three times → keep first two, strip third.

    Confirms the rotation isn't a free pass — repetition beyond the bucket
    cap still elides.
    """
    para = _para(60)
    text = (
        f"Chapter 1\n\n{para}\n\nfiller filler filler.\n\n"
        f"Chapter 2\n\n{para}\n\nmore filler text words.\n\n"
        f"Chapter 3\n\n{para}\n\nthird chapter content."
    )

    deduped, notes = _dedup_paragraphs_book_wide(text)

    occurrences = deduped.count(para)
    assert occurrences == 2, (
        f"3rd occurrence should be stripped: occurrences={occurrences}. Notes: {notes}"
    )
    assert len(notes) == 1, (
        f"One strip note expected; got {len(notes)}: {notes}"
    )


# ---------------------------------------------------------------------------
# Test 3: long paragraph still keep=1 (legacy behavior preserved).
# ---------------------------------------------------------------------------


def test_long_paragraph_keep_one_unchanged() -> None:
    """A 250-word paragraph (above the atom bucket ceiling) still falls back
    to base keep=1. Templates/scaffold leakage protection survives.
    """
    para = _para(250)
    text = (
        f"Chapter 1\n\n{para}\n\nfiller filler filler all good.\n\n"
        f"Chapter 2\n\n{para}\n\nmore filler more filler more filler."
    )

    deduped, notes = _dedup_paragraphs_book_wide(text)

    occurrences = deduped.count(para)
    assert occurrences == 1, (
        f"Long paragraph (>200w) should be stripped to 1; got {occurrences}. "
        f"Notes: {notes}"
    )
    assert len(notes) == 1, f"Expected 1 strip note, got {len(notes)}"


# ---------------------------------------------------------------------------
# Test 4: short paragraph always exempt (regardless of keep cap).
# ---------------------------------------------------------------------------


def test_short_paragraph_always_exempt() -> None:
    """A 15-word paragraph (below min_words=30) is exempt from any dedup.

    This is the legacy behavior; the OPD-109 Phase 3 calibration must not
    accidentally change it.
    """
    short = _para(15)
    text = (
        f"Chapter 1\n\n{short}\n\nfiller filler filler.\n\n"
        f"Chapter 2\n\n{short}\n\nfiller filler filler.\n\n"
        f"Chapter 3\n\n{short}\n\nfiller filler filler.\n\n"
        f"Chapter 4\n\n{short}\n\nfiller filler filler."
    )

    deduped, notes = _dedup_paragraphs_book_wide(text)

    occurrences = deduped.count(short)
    assert occurrences == 4, (
        f"Short paragraph (<30w) should always be exempt; got {occurrences}"
    )


# ---------------------------------------------------------------------------
# Test 5: per-paragraph keep cap helper agrees with bucket rules.
# ---------------------------------------------------------------------------


def test_keep_cap_for_paragraph_bucket_rules() -> None:
    """Verify the `_keep_cap_for_paragraph` helper hits the expected branches."""
    atom_keep = _atom_paragraph_keep_default()  # default 2
    base_keep = 1

    # Atom-sized: keep = max(base, atom_keep) = atom_keep
    assert _keep_cap_for_paragraph(_para(60), base_keep=base_keep) == atom_keep
    assert _keep_cap_for_paragraph(_para(150), base_keep=base_keep) == atom_keep
    assert _keep_cap_for_paragraph(_para(200), base_keep=base_keep) == atom_keep

    # Above the atom ceiling: keep = base
    assert _keep_cap_for_paragraph(_para(201), base_keep=base_keep) == base_keep
    assert _keep_cap_for_paragraph(_para(500), base_keep=base_keep) == base_keep

    # Below the atom floor: keep = base (and pasted-as-too-short anyway)
    assert _keep_cap_for_paragraph(_para(10), base_keep=base_keep) == base_keep


# ---------------------------------------------------------------------------
# Test 6: env override (PHOENIX_ATOM_PARAGRAPH_KEEP) survives.
# ---------------------------------------------------------------------------


def test_env_override_atom_paragraph_keep(monkeypatch: pytest.MonkeyPatch) -> None:
    """Setting PHOENIX_ATOM_PARAGRAPH_KEEP=3 should bump the atom bucket cap."""
    monkeypatch.setenv("PHOENIX_ATOM_PARAGRAPH_KEEP", "3")
    assert _atom_paragraph_keep_default() == 3

    para = _para(60)
    text = (
        f"Chapter 1\n\n{para}\n\nfiller f f.\n\n"
        f"Chapter 2\n\n{para}\n\nfiller f f.\n\n"
        f"Chapter 3\n\n{para}\n\nfiller f f."
    )
    deduped, notes = _dedup_paragraphs_book_wide(text)
    # All 3 should survive under keep=3.
    assert deduped.count(para) == 3, (
        f"keep=3 override didn't apply; got {deduped.count(para)} occurrences"
    )
    assert not notes, f"keep=3 should produce no elision notes; got {notes}"


# ---------------------------------------------------------------------------
# Test 7: legacy long-paragraph keep cap still env-overridable.
# ---------------------------------------------------------------------------


def test_long_paragraph_keep_cap_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    """PHOENIX_BOOK_DEDUPE_KEEP still controls the long-paragraph cap.

    Regression smoke: confirms the OPD-109 Phase 3 patch did not silently
    replace the existing env knob.
    """
    monkeypatch.setenv("PHOENIX_BOOK_DEDUPE_KEEP", "2")
    para = _para(250)  # above atom ceiling
    text = (
        f"Chapter 1\n\n{para}\n\nfiller.\n\nChapter 2\n\n{para}\n\nfiller."
    )
    deduped, notes = _dedup_paragraphs_book_wide(text)
    assert deduped.count(para) == 2, (
        f"Long-paragraph env override didn't take effect; got {deduped.count(para)}"
    )
