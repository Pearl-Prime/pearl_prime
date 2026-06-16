"""Regression tests for the F1-signature cross-chapter dedupe.

ws_f1_signature_dedup_20260616 — delivery-layer backstop for the residual named
F1 clusters left by the enrichment depth-dedup (PR #1632): short, dense,
multi-sentence "signature" re-stamps (HOOK / EXERCISE / doctrine) that fire a
large F1 cluster but escape the book-wide dedupe's 30-word floor and vary by a
trailing clause (so exact-fingerprint dedupe misses them too).

The pass mirrors register_gate's F1 detector (>=3 sentences, Jaccard >= 0.55),
keep=1, scoped to short paragraphs (< 45 words) so bulk SCENE/STORY content is
untouched. End-to-end book-level F1 drop is proven in
artifacts/qa/f1_signature_dedup_20260616/.
"""
from __future__ import annotations

import pytest

from phoenix_v4.rendering import book_renderer as br
from phoenix_v4.rendering.book_renderer import _dedup_paragraphs_book_wide

# The real residual cluster: "task is open" HOOK (24 words / 4 sentences / 135 chars).
_HOOK = (
    "The task is open. You have been looking at it for forty minutes. This is "
    "not laziness. Your body knows something your calendar doesn't."
)
# Per-chapter trailing-clause variant (the shape the composer emits — defeats exact dedupe).
_HOOK_VAR = (
    "The task is open. You have been looking at it for forty minutes. This is "
    "not laziness. Your body knows something your calendar doesn't. Not laziness "
    "but your body running a different calculation than the one on your screen."
)
# Short transitional beat: 3 sentences but < 90 chars — must stay free to repeat.
_SHORT_BEAT = "Stay here. Breathe. Let it land."
# Bulk content paragraph: >= 45 words — must never be touched by the signature pass.
_BULK = (
    "Maria opens her laptop and the spreadsheet glows back at her in the dim light "
    "of the early office. The numbers march down the column like soldiers on parade, "
    "indifferent to her. She has not slept properly in a week now. The quarterly "
    "review is tomorrow morning and the model is plainly, embarrassingly wrong again."
)


def _book(*paras: str) -> str:
    out = []
    for i, p in enumerate(paras, 1):
        out.append(f"Chapter {i}")
        out.append(p)
    return "\n\n".join(out)


def test_identical_signature_collapses_to_one():
    text = _book(*[_HOOK] * 12)
    out, notes = _dedup_paragraphs_book_wide(text)
    assert out.count("The task is open") == 1
    assert len(notes) == 11


def test_trailing_clause_variant_also_collapses():
    """Fuzzy (Jaccard) catches the per-chapter trailing-clause variant too."""
    text = _book(_HOOK, _HOOK, _HOOK_VAR, _HOOK, _HOOK_VAR)
    out, _ = _dedup_paragraphs_book_wide(text)
    assert out.count("The task is open") == 1


def test_short_beat_is_not_deduped():
    """< 90-char multi-sentence beats stay free to repeat (no over-removal)."""
    text = _book(*[_SHORT_BEAT] * 10)
    out, _ = _dedup_paragraphs_book_wide(text)
    assert out.count("Stay here. Breathe.") == 10


def test_bulk_content_paragraph_untouched_by_signature_pass():
    """>= 45-word content paragraphs are out of the signature class; the existing
    book-wide keep rules (OPD-109) apply, not keep=1."""
    # Two DIFFERENT bulk paragraphs must both survive.
    other = _BULK.replace("Maria", "Devon").replace("spreadsheet", "inbox")
    text = _book(_BULK, other)
    out, _ = _dedup_paragraphs_book_wide(text)
    assert "Maria opens her laptop" in out
    assert "Devon opens her laptop" in out


def test_flag_off_disables_signature_pass(monkeypatch):
    monkeypatch.setenv("PHOENIX_F1_SIGNATURE_DEDUPE", "0")
    text = _book(*[_HOOK] * 12)
    out, _ = _dedup_paragraphs_book_wide(text)
    # With the pass off, the 24-word hook falls through the 30-word floor and all survive.
    assert out.count("The task is open") == 12


def test_signature_predicate_classifies_hook_not_beat_not_bulk():
    assert br._f1_sig_is_signature(_HOOK, len(_HOOK.split()), len(_HOOK)) is True
    assert br._f1_sig_is_signature(_SHORT_BEAT, len(_SHORT_BEAT.split()), len(_SHORT_BEAT)) is False
    assert br._f1_sig_is_signature(_BULK, len(_BULK.split()), len(_BULK)) is False


def test_chapter_headings_preserved():
    text = _book(*[_HOOK] * 3)
    out, _ = _dedup_paragraphs_book_wide(text)
    for i in (1, 2, 3):
        assert f"Chapter {i}" in out
