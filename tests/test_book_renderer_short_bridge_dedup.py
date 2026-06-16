"""Regression tests for the terse within-slot bridge re-stamp dedupe.

ws_short_bridge_dedup_20260616 — follow-on to PR #1644. The within-slot STORY
bridge bank has ~49 variants but a deep book emits ~276 within-STORY bridges, so
by pigeonhole each variant recurs ~5-6x even with a perfectly uniform selector.
"Same body. Different door. Watch what changes." (46 chars / 3 sentences) thus
formed a size-5 F1 cluster. It is too short (< 90 chars) for the fuzzy F1-signature
pass (#1644) and too short (< 30 words) for the exact book-wide dedupe, so it
survived. This delivery-layer backstop removes terse multi-sentence EXACT re-stamps
(>= 3 sentences in < 90 chars = formulaic bridge, not narrative), keep=1.
"""
from __future__ import annotations

from phoenix_v4.rendering.book_renderer import _dedup_paragraphs_book_wide

# A terse 3-sentence within-slot bridge (the real residual), 46 chars.
_BRIDGE = "Same body. Different door. Watch what changes."
# Another terse formulaic bridge.
_BRIDGE2 = "Turn the camera. The alarm sounds. Nothing moves."
# A short transitional beat with < 3 sentences — must stay free to repeat.
_BEAT = "Stay here. Breathe."
# A long narrative paragraph (>= 90 chars / >= 30 words) — handled by the existing
# passes, NOT this one; must not be touched at keep=1 by the short-bridge rule.
_LONG = (
    "Maria opens her laptop and the spreadsheet glows back at her in the dim office "
    "light. The numbers march down the column like soldiers. She has not slept."
)


def _book(*paras: str) -> str:
    out = []
    for i, p in enumerate(paras, 1):
        out.append(f"Chapter {i}")
        out.append(p)
    return "\n\n".join(out)


def test_terse_bridge_restamp_collapses_to_one():
    out, notes = _dedup_paragraphs_book_wide(_book(*[_BRIDGE] * 6))
    assert out.count("Same body. Different door") == 1
    assert sum(1 for n in notes if "short_bridge" in n) == 5


def test_distinct_terse_bridges_both_survive():
    out, _ = _dedup_paragraphs_book_wide(_book(_BRIDGE, _BRIDGE2, _BRIDGE, _BRIDGE2))
    assert out.count("Same body. Different door") == 1
    assert out.count("Turn the camera.") == 1


def test_short_two_sentence_beat_is_not_deduped():
    """< 3 sentences -> not a formulaic-bridge signature -> free to repeat."""
    out, _ = _dedup_paragraphs_book_wide(_book(*[_BEAT] * 8))
    assert out.count("Stay here. Breathe.") == 8


def test_flag_off_disables_short_bridge_dedupe(monkeypatch):
    monkeypatch.setenv("PHOENIX_F1_SIGNATURE_DEDUPE", "0")
    out, _ = _dedup_paragraphs_book_wide(_book(*[_BRIDGE] * 6))
    assert out.count("Same body. Different door") == 6


def test_chapter_headings_preserved():
    out, _ = _dedup_paragraphs_book_wide(_book(*[_BRIDGE] * 3))
    for i in (1, 2, 3):
        assert f"Chapter {i}" in out
