"""Signature phrase recurrence limits in clean_for_delivery."""

from __future__ import annotations

from unittest.mock import patch

from phoenix_v4.quality.ei_v2.config import invalidate_ei_v2_config_cache
from phoenix_v4.rendering.book_renderer import (
    _build_signature_phrase_index,
    _enforce_signature_recurrence_limit,
    clean_for_delivery,
)


def _phrase() -> str:
    return "one two three four five six seven eight"


def test_build_signature_phrase_index_top_n() -> None:
    p = _phrase()
    text = " ".join([p, p, p, "other words here"])
    idx = _build_signature_phrase_index(text, min_words=8, top_n=5)
    assert idx.get(p) == 3
    assert len(idx) <= 5


def test_phrase_six_times_reduced_to_three() -> None:
    p = _phrase()
    text = " ".join([p] * 6)
    cleaned, removed = _enforce_signature_recurrence_limit(text, max_recurrences=3, min_words=8)
    assert cleaned.count(p) == 3
    assert removed


def test_phrase_two_times_untouched() -> None:
    p = _phrase()
    text = " ".join([p] * 2)
    cleaned, removed = _enforce_signature_recurrence_limit(text, max_recurrences=3, min_words=8)
    assert cleaned.count(p) == 2
    assert not removed


def test_short_phrases_untouched() -> None:
    # Four-word units only: ensure no accidental repeated 8-gram across the join boundaries.
    parts = [f"alpha beta gamma delta block{n} x" for n in range(12)]
    text = " ".join(parts)
    cleaned, removed = _enforce_signature_recurrence_limit(text, max_recurrences=3, min_words=8)
    assert cleaned == text
    assert not removed


def test_removed_phrases_in_return_value() -> None:
    p = _phrase()
    text = " ".join([p] * 5)
    _, removed = _enforce_signature_recurrence_limit(text, max_recurrences=3, min_words=8)
    assert isinstance(removed, list)
    assert removed


def test_disabled_via_config_no_change() -> None:
    invalidate_ei_v2_config_cache()
    p = _phrase()
    text = " ".join([p] * 6)
    fake_cfg = {"manuscript_recurrence": {"enabled": False}}
    with patch("phoenix_v4.quality.ei_v2.config.load_ei_v2_config", return_value=fake_cfg):
        gov: dict = {}
        out = clean_for_delivery(text, plan={"runtime_format_id": "standard_book"}, governance_report=gov)
    assert out.count(p) == 6
    assert not gov.get("recurrence_report")
    invalidate_ei_v2_config_cache()
