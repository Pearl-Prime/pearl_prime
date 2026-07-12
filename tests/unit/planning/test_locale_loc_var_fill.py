"""Locale loc-var fills must not silently inject English into zh-TW prose."""
from __future__ import annotations

from phoenix_v4.planning import injection_resolver as ir


def setup_function() -> None:
    ir._LOCALE_FALLBACKS_CACHE = None


def test_zh_tw_loc_var_fill_uses_cjk_bank() -> None:
    text = "站立時，你才注意到窗外透進的 {weather_detail}。從這裡看得見 {street_name}。"
    out = ir._fill_locale_tokens(text, locale="zh-TW")
    assert "soft daylight" not in out
    assert "the street below" not in out
    assert "{weather_detail}" not in out
    assert "{street_name}" not in out
    assert "日光" in out or "柔和" in out
    assert "街道" in out


def test_en_us_loc_var_fill_unchanged() -> None:
    text = "You notice {weather_detail} along the sill and {street_name}."
    out = ir._fill_locale_tokens(text, locale="en-US")
    assert "soft daylight" in out
    assert "the street below" in out
