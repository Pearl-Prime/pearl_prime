"""Regression tests for zh-TW QUOTE accent supply (supported-accent underfill).

Ground truth (draft render 2026-07-14): the zh-TW / gen_z_professionals / anxiety
extended_book_2h production build stopped with

    [PRODUCTION GATE] Supported accent underfill detected:
      - QUOTE: 3

even though SOURCE_OF_TRUTH/accent_banks/quotes/anxiety/zh_TW.yaml supplies 12
verified, public-domain Taiwan-appropriate quotes (Laozi, Zhuangzi, Confucius,
Su Shi, …). The pool loaded (pool_size=12) but 0 were assigned because the
selection filter measured length with ``len(body.split())`` — CJK text is
space-free, so every quote counted as one "word" and was rejected under the
``min_words`` floor. The fix makes the length check CJK-honest via
``phoenix_v4.text.wordcount.count_words`` and renders the localized Chinese
original (not the English translation) for CJK locales.

Test (a): zh-TW quote supply present -> QUOTE fills to its floor, no supported
          underfill, and rendered quote bodies are the Chinese originals.
Test (b): genuinely missing supply -> precise preflight blocker (which accent,
          how many short, why).
"""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning import accent_planner
from phoenix_v4.planning.accent_planner import (
    attach_accent_plan,
    preflight_accent_supply,
    _resolve_quote_text,
    _score_entry_for_chapter,
)
from phoenix_v4.planning.enrichment_select import (
    EnrichedBook,
    EnrichedChapter,
    EnrichedSlot,
)
from phoenix_v4.text.wordcount import has_cjk_script

REPO_ROOT = Path(__file__).resolve().parents[3]

# Chapter slot skeleton that can host QUOTE (needs HOOK and THREAD slots) plus
# the STORY / REFLECTION / EXERCISE / INTEGRATION / PIVOT surfaces the other
# accent classes bind to, so the share-cap competition mirrors a real book.
_SLOT_TYPES = [
    "HOOK",
    "STORY",
    "REFLECTION",
    "EXERCISE",
    "PIVOT",
    "STORY",
    "INTEGRATION",
    "THREAD",
]

# A block of prose long enough that _chapter_can_host_accents (>=80 words) passes.
_FILLER = ("你並不孤單。這份焦慮是一種保護性的警報，而不是性格上的缺陷。" * 6)


def _slot(slot_type: str) -> EnrichedSlot:
    words = max(20, len(_FILLER))
    return EnrichedSlot(
        slot_type=slot_type,
        content=_FILLER,
        source="atom",
        source_id=f"atom_{slot_type.lower()}",
        target_words=words,
        actual_words=words,
        enrichment_applied=[],
    )


def _chapter(number: int, thesis: str) -> EnrichedChapter:
    slots = [_slot(st) for st in _SLOT_TYPES]
    total = sum(s.actual_words for s in slots)
    return EnrichedChapter(
        number=number,
        role="body",
        working_title=f"第{number}章",
        thesis=thesis,
        slots=slots,
        total_words=total,
        source_breakdown={"atom": total},
    )


def _zhtw_anxiety_book() -> EnrichedBook:
    theses = [
        "unnamed_feeling",
        "unnamed_feeling",
        "anxiety_spike",
        "anxiety_spike",
        "anxiety_spike",
        "emotional_overwhelm",
        "unnamed_feeling",
        "unnamed_feeling",
        "emotional_overwhelm",
        "anxiety_spike",
        "unnamed_feeling",
        "emotional_overwhelm",
    ]
    chapters = [_chapter(i + 1, theses[i]) for i in range(12)]
    total = sum(c.total_words for c in chapters)
    return EnrichedBook(
        schema_version=1,
        stage="enriched",
        topic="anxiety",
        teacher_id=None,
        persona_id="gen_z_professionals",
        runtime_format="extended_book_2h",
        chapters=chapters,
        total_words=total,
        enrichment_audit={},
        # Explicitly arm the contract-v1 accent lane (also auto-arms for
        # production + extended_book_2h) so the QUOTE:3 pilot floor is in effect.
        spine_context={"enrichment_contract_v1": True, "quality_profile": "production"},
        locale="zh-TW",
    )


def test_zhtw_quotes_are_selectable_after_cjk_word_count_fix():
    """Every zh-TW quote must clear the selection length filter (was rejected)."""
    quotes = accent_planner._load_quotes("anxiety", "zh_TW", REPO_ROOT)
    assert quotes, "zh_TW anxiety quote bank must supply candidates"
    scored_ok = 0
    for q in quotes:
        score = _score_entry_for_chapter(
            q,
            accent_class="QUOTE",
            topic_id="anxiety",
            locale_cluster="zh_TW",
            composite_mode=False,  # isolate the length filter from secular gating
            chapter_number=1,
            chapter_count=12,
            position="before_HOOK",
            book_idea="recognition_before_action",
            book_motif="quiet_capacity",
            seed="t",
        )
        if score >= 0:
            scored_ok += 1
    assert scored_ok >= 3, (
        "CJK quotes must not be rejected as 1-word bodies; "
        f"only {scored_ok}/{len(quotes)} scored >= 0"
    )


def test_zhtw_quote_body_renders_chinese_original_not_translation():
    entry = {
        "quote_id": "q_test",
        "text": "上善若水。水善利萬物而不爭。",
        "text_en": "The highest good is like water.",
        "author": "老子",
        "primary_source": "《道德經》第八章",
    }
    zh = _resolve_quote_text(entry, locale_cluster="zh_TW")
    assert has_cjk_script(zh), f"zh-TW quote must render the Chinese original, got: {zh!r}"
    assert "上善若水" in zh
    # Robustness: even if locale plumbing drops to the en_US default, a CJK
    # original still renders in-language (mirrors the real draft where
    # plan.json.locale was None) rather than emitting a translation mid-book.
    assert has_cjk_script(_resolve_quote_text(entry, locale_cluster="en_US"))

    # en_US flagship parity: for a real en_US entry (English `text`), the
    # historical text_en-first order is byte-identical.
    en_entry = {
        "quote_id": "q_en",
        "text": "I exist as I am, that is enough.",
        "text_en": "I exist as I am, that is enough.",
        "author": "Walt Whitman",
        "primary_source": "Leaves of Grass (1855)",
    }
    assert _resolve_quote_text(en_entry, locale_cluster="en_US") == "I exist as I am, that is enough."


def test_zhtw_book_fills_quote_floor_with_no_supported_underfill():
    book = _zhtw_anxiety_book()
    planned = attach_accent_plan(
        book,
        brand_id="way_stream_sanctuary",
        seed="zhtw-quote-test",
        locale="zh-TW",
    )
    audit = planned.enrichment_audit or {}
    strategy = audit.get("enrichment_strategy_report") or {}
    alignment = audit.get("bestseller_alignment_report") or {}

    budget = int(strategy.get("accent_budget", {}).get("QUOTE", 0))
    assigned = int(strategy.get("assignment_counts", {}).get("QUOTE", 0))
    assert budget == 3, f"gen_z_professionals:anxiety pilot QUOTE floor must be 3, got {budget}"
    assert assigned == budget, f"QUOTE should fill to floor {budget}, assigned {assigned}"

    supported_underfill = alignment.get("supported_underfilled_budget_by_class") or {}
    assert "QUOTE" not in supported_underfill, (
        f"QUOTE must not be a supported underfill after fix: {supported_underfill}"
    )

    # planned == rendered: every assigned QUOTE body is present and Chinese.
    quote_bodies = []
    for ch in planned.chapters:
        for beat in ch.accent_beats:
            if beat.get("class") == "QUOTE":
                quote_bodies.append(ch.accent_bodies.get(beat["accent_id"], ""))
    assert len(quote_bodies) == budget
    assert all(has_cjk_script(b) for b in quote_bodies), (
        f"rendered zh-TW quotes must contain Chinese text: {quote_bodies}"
    )


def test_preflight_blocks_precisely_on_missing_quote_supply():
    """Genuinely absent supply -> precise, early preflight blocker."""
    blockers = preflight_accent_supply(
        {"QUOTE": 3, "ENCOURAGEMENT": 0},
        {"QUOTE": [], "ENCOURAGEMENT": []},
        locale_cluster="zh_TW",
    )
    assert len(blockers) == 1, f"only budgeted+empty classes block: {blockers}"
    msg = blockers[0]
    assert "QUOTE" in msg
    assert "need 3" in msg
    assert "0 available" in msg
    assert "zh_TW" in msg


def test_preflight_silent_when_supply_present():
    blockers = preflight_accent_supply(
        {"QUOTE": 3},
        {"QUOTE": [{"quote_id": "q1", "text": "上善若水。"}]},
        locale_cluster="zh_TW",
    )
    assert blockers == []
