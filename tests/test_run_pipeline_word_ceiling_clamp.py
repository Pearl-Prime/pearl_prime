"""DEFERRED-LANE word_budget (2026-06-15): book-level word-ceiling clamp.

Render-accounting fix for scripts/run_pipeline.py. Spine renders (standard_book et al.)
fill chapters to the runtime ceiling during apply_depth_pass, then the post-render
strengthen passes + the arch-v2 "Note on the Teachings" preamble push the book past the
runtime word ceiling. The pre-existing _per_chapter_word_cap is gated on _cli_output_format
(empty for spine), so it never fires for standard_book — the book lands at ~22.7-24.1k and
HARD_FAILs the book_pass word_budget gate (word_count <= word_range[max]=22000).

These tests cover the two helpers that close that gap:
    - _load_runtime_word_ceiling: prefers cap_word_target, falls back to word_range[max].
    - _clamp_book_to_word_ceiling: trims chapter bodies so TOTAL words (incl. preamble) are
      within the ceiling, preserving the preamble + every "Chapter N" heading, and no-ops
      when already within budget.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_pipeline import (  # noqa: E402
    _clamp_book_to_word_ceiling,
    _extract_registry_chapters,
    _load_runtime_word_ceiling,
)


def _make_book(preamble_words: int, n_chapters: int, body_words_per_chapter: int) -> str:
    parts: list[str] = []
    if preamble_words > 0:
        parts.append("Note on the Teachings\n\n" + " ".join(["alpha"] * (preamble_words - 3)))
    for n in range(1, n_chapters + 1):
        body = " ".join([f"w{n}x{i}" for i in range(body_words_per_chapter)])
        parts.append(f"Chapter {n}\n\n{body}")
    return "\n\n".join(parts)


def _heading_count(text: str) -> int:
    return len(re.findall(r"(?m)^Chapter \d+\s*$", text))


# ---------------------------------------------------------------------------
# _load_runtime_word_ceiling
# ---------------------------------------------------------------------------

def test_standard_book_ceiling_uses_cap_word_target() -> None:
    # config/format_selection/format_registry.yaml pins cap_word_target: 22000 for
    # standard_book (DURATION-DERIVATION-01 §5). The loader must return it.
    ceiling = _load_runtime_word_ceiling("standard_book", REPO_ROOT)
    assert ceiling == 22000


def test_unknown_format_returns_none() -> None:
    assert _load_runtime_word_ceiling("not_a_real_format", REPO_ROOT) is None


# ---------------------------------------------------------------------------
# _clamp_book_to_word_ceiling
# ---------------------------------------------------------------------------

def test_clamp_brings_overbudget_book_within_ceiling() -> None:
    # ~24.4k book with a preamble — the exact failure class (22.7-24.1k overshoot).
    book = _make_book(preamble_words=401, n_chapters=12, body_words_per_chapter=2000)
    assert len(book.split()) > 22000
    clamped, pre, post = _clamp_book_to_word_ceiling(book, 22000)
    assert pre == len(book.split())
    assert post <= 22000, f"clamp left {post} > 22000"
    assert post < pre


def test_clamp_preserves_preamble_and_all_chapter_headings() -> None:
    book = _make_book(preamble_words=401, n_chapters=12, body_words_per_chapter=2000)
    clamped, _pre, _post = _clamp_book_to_word_ceiling(book, 22000)
    assert clamped.startswith("Note on the Teachings")
    assert _heading_count(clamped) == 12
    # Still parseable by the gate's chapter extractor.
    assert len(_extract_registry_chapters(clamped)) == 12


def test_clamp_handles_tiny_overshoot_exactly() -> None:
    # 22.7k — the low end of the observed overshoot. Rounding must not leave it over.
    book = _make_book(preamble_words=401, n_chapters=12, body_words_per_chapter=1859)
    assert len(book.split()) > 22000
    _clamped, _pre, post = _clamp_book_to_word_ceiling(book, 22000)
    assert post <= 22000


def test_clamp_handles_book_without_preamble() -> None:
    book = _make_book(preamble_words=0, n_chapters=10, body_words_per_chapter=2300)
    assert len(book.split()) > 22000
    clamped, _pre, post = _clamp_book_to_word_ceiling(book, 22000)
    assert post <= 22000
    assert _heading_count(clamped) == 10


def test_clamp_is_noop_when_within_budget() -> None:
    book = _make_book(preamble_words=401, n_chapters=12, body_words_per_chapter=1500)
    assert len(book.split()) < 22000
    clamped, pre, post = _clamp_book_to_word_ceiling(book, 22000)
    assert clamped == book
    assert pre == post


def test_clamp_noop_on_zero_ceiling() -> None:
    book = _make_book(preamble_words=0, n_chapters=3, body_words_per_chapter=500)
    clamped, pre, post = _clamp_book_to_word_ceiling(book, 0)
    assert clamped == book
    assert pre == post


def test_clamp_trim_is_spread_not_all_on_first_chapter() -> None:
    # Proportional trim: every chapter should lose roughly its share, so no single
    # chapter is gutted while others stay full.
    book = _make_book(preamble_words=0, n_chapters=10, body_words_per_chapter=2300)
    clamped, _pre, post = _clamp_book_to_word_ceiling(book, 22000)
    assert post <= 22000
    chs = _extract_registry_chapters(clamped)
    body_lens = [len("\n".join(c.splitlines()[1:]).split()) for c in chs]
    # No chapter trimmed to near-empty while the book is ~22k across 10 chapters.
    assert min(body_lens) > 500, f"a chapter was over-trimmed: {body_lens}"


def test_clamp_slice_uses_sentence_boundary_even_for_short_first_sentence() -> None:
    book = (
        "Chapter 1\n\n"
        "Safe. Second sentence carries trace span [atom trace starts here and "
        "keeps going until its ending period."
    )

    clamped, _pre, post = _clamp_book_to_word_ceiling(book, 8)

    assert post <= 8
    assert clamped.rstrip().endswith(".")
    assert "[atom" not in clamped
    assert "Second sentence" not in clamped
