"""Lane B regression — DEFECT 2: template-tail truncation orphans.

Spec: artifacts/analysis/pearl_prime_priorities/COMPOSER_FRONTIER_FIX_SPEC_20260614.md (DEFECT 2).

The pre-fix bug: ``dedupe_scene_furniture_book`` capped phrase occurrences by deleting
the matched SUBSTRING in place (replacements=()). When the signature list held
sentence-interior fragments ("that is the part", "by the time you", "not to fix
anything", "fix anything just to give", ...), that in-place deletion sheared the
containing sentence and orphaned a byte-identical lowercase-leading tail across every
book — e.g. "Start with the pressure under the sternum. still bracing." (153x).

This suite asserts:
  1. No orphaned lowercase-leading sentence-tail survives furniture dedupe.
  2. Genuine standalone furniture is still capped at max_each (full sentence survives
     up to max_each, surplus whole sentences are dropped — no substring shearing).
  3. The empty-replacements deletion guard refuses to shear a mid-sentence substring.
  4. The purged sentence-interior fragments no longer truncate the sentences that
     contain them.
"""

from __future__ import annotations

import re

from phoenix_v4.rendering.golden_chapter_synthesis import (
    _limit_case_insensitive_phrase_occurrences,
    _match_is_sentence_bounded,
    dedupe_scene_furniture_book,
)

# A lowercase letter that starts a sentence (immediately after ". ") is the fingerprint
# of a sheared tail. Apostrophes are allowed inside the first token.
_ORPHAN_TAIL_RE = re.compile(r"[.!?]\s+[a-z]")


def _has_orphaned_lowercase_tail(text: str) -> bool:
    return bool(_ORPHAN_TAIL_RE.search(text))


def test_no_orphaned_tail_from_purged_interior_fragment_that_is_the_part() -> None:
    """The canonical DEFECT-2 orphan must not be manufactured.

    Pre-fix, "that is the part" was a capped signature; in
    "...sternum. That is the part still bracing." the substring deletion produced the
    orphan "...sternum. still bracing.". After purge + sentence-granularity capping the
    full sentence must survive intact and no lowercase-leading tail may appear.
    """
    sentence = "Start with the pressure under the sternum. That is the part still bracing."
    # Repeat the SECOND sentence well past any cap so the old code would have fired.
    blob = "\n\n".join(
        f"Chapter {i} opens here. {sentence}" for i in range(6)
    )
    out, _notes = dedupe_scene_furniture_book(blob, max_each=2)
    assert "still bracing" in out
    # The exact pre-fix orphan must never appear.
    assert "sternum. still bracing" not in out.lower()
    # And the full clause must survive verbatim at least once.
    assert "That is the part still bracing." in out
    # No lowercase-leading sentence tail anywhere (the orphan fingerprint).
    assert not _has_orphaned_lowercase_tail(out), out


def test_no_orphaned_tail_from_by_the_time_you() -> None:
    sentence = (
        "By the time you can explain the moment, the alarm has already chosen a meaning."
    )
    blob = " ".join(f"Line {i}. {sentence}" for i in range(5))
    out, _notes = dedupe_scene_furniture_book(blob, max_each=2)
    assert "can explain the moment, the alarm" in out
    # The leading clause must not be stripped, leaving a lowercase "can explain..." tail.
    assert "the moment, the alarm has already chosen a meaning" in out
    assert not _has_orphaned_lowercase_tail(out), out


def test_no_orphaned_tail_from_not_to_fix_anything() -> None:
    sentence = "This practice brings some of it into view, not to fix anything you find."
    blob = " ".join(f"Item {i}. {sentence}" for i in range(4))
    out, _notes = dedupe_scene_furniture_book(blob, max_each=2)
    # Pre-fix orphan was "...into view. to fix anything you find."
    assert "into view. to fix anything" not in out.lower()
    assert "not to fix anything you find" in out
    assert not _has_orphaned_lowercase_tail(out), out


def test_standalone_furniture_capped_at_max_each_whole_sentence() -> None:
    """Genuine furniture is still capped — surplus WHOLE sentences are dropped."""
    s = "Soft daylight along the sill."
    blob = " ".join(f"Para {i} body text here. {s}" for i in range(6))
    out, notes = dedupe_scene_furniture_book(blob, max_each=2)
    # Only max_each copies of the furniture sentence survive.
    assert out.lower().count("soft daylight along the sill") == 2
    assert notes and any("soft daylight along the sill" in n for n in notes)
    # Surrounding sentences are untouched (no shearing) — no orphan tail.
    assert not _has_orphaned_lowercase_tail(out), out


def test_existing_caps_phrase_contract_preserved() -> None:
    """Mirror of tests/test_golden_chapter_synthesis.py contract at max_each=1."""
    blob = (
        "One soft daylight along the sill. Two soft daylight along the sill. "
        "Three soft daylight along the sill."
    )
    out, notes = dedupe_scene_furniture_book(blob, max_each=1)
    assert out.count("soft daylight along the sill") == 1
    assert notes and "removed_extra" in notes[0]


def test_limit_helper_refuses_midsentence_substring_deletion() -> None:
    """Empty-replacements guard: a mid-sentence match is NOT deleted in place."""
    text = "Start with the pressure under the sternum. That is the part still bracing."
    # keep=0 so EVERY occurrence is "surplus" and would, pre-fix, be deleted.
    out, replaced = _limit_case_insensitive_phrase_occurrences(
        text, "that is the part", 0, ()
    )
    # The phrase sits mid-sentence -> refused -> text unchanged, nothing shorn.
    assert out == text
    assert replaced == 0
    assert "still bracing" in out
    assert "sternum. still bracing" not in out.lower()


def test_limit_helper_allows_whole_sentence_removal() -> None:
    """A surplus match that IS a whole sentence may be removed (no orphan possible)."""
    text = "Keep this opener. soft daylight along the sill. Keep this closer."
    # The middle "sentence" is exactly the furniture phrase (bounded both sides).
    out, replaced = _limit_case_insensitive_phrase_occurrences(
        text, "soft daylight along the sill", 0, ()
    )
    assert replaced == 1
    assert "soft daylight along the sill" not in out.lower()
    assert "Keep this opener." in out
    assert "Keep this closer." in out


def test_match_is_sentence_bounded_basics() -> None:
    # Start-of-text on the left, terminator on the right -> bounded.
    assert _match_is_sentence_bounded("foo bar. baz.", 0, 7) is True
    # Mid-sentence substring ("part" inside "the part is here") -> not bounded.
    assert _match_is_sentence_bounded("the part is here.", 4, 8) is False
    # Bounded on both sides (after terminator+space, before terminator).
    assert _match_is_sentence_bounded("A. middle. B.", 3, 9) is True
    # Followed by more words before any terminator -> not bounded on the right.
    assert _match_is_sentence_bounded("A. middle words. B.", 3, 9) is False
