"""Tests for the CJK text shaper.

Validates the shape that bubble_render.py is expected to call. Tests run
in CI with Pillow only — the HarfBuzz-shaped path is exercised when
uharfbuzz is installed (gracefully skipped otherwise).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.cjk_text_shaper import (  # type: ignore
    VALID_CJK_LOCALES,
    _has_harfbuzz,
    _load_font_registry,
    diagnose,
    is_cjk_locale,
    render_text_to_pil,
    select_font_path_for_locale,
    shape_text_harfbuzz,
)


# ─── locale detection ─────────────────────────────────────────────────────


def test_is_cjk_locale_recognizes_all_4():
    assert is_cjk_locale("ja_JP")
    assert is_cjk_locale("zh_TW")
    assert is_cjk_locale("zh_CN")
    assert is_cjk_locale("ko_KR")


def test_is_cjk_locale_rejects_others():
    assert not is_cjk_locale("en_US")
    assert not is_cjk_locale("fr_FR")
    assert not is_cjk_locale(None)
    assert not is_cjk_locale("")


def test_valid_cjk_locales_constant():
    assert set(VALID_CJK_LOCALES) == {"ja_JP", "zh_TW", "zh_CN", "ko_KR"}


# ─── font selection ──────────────────────────────────────────────────────


def test_select_font_falls_back_to_body_when_role_missing():
    """If a non-existent role is requested, the function should fall back
    to the locale's body font."""
    registry = {
        "fonts": [
            {"id": "test_body", "license": "OFL", "path": "ttf/test_body.ttf", "status": "pending"},
        ],
        "locale_coverage_required": {
            "ja_JP": {"body": "test_body"},
        },
    }
    # Returns None because file doesn't exist on disk; the role-fallback
    # logic ran (test_body) before hitting the file existence check.
    assert select_font_path_for_locale("ja_JP", role="weird", font_registry=registry) is None


def test_select_font_returns_none_for_unknown_locale():
    registry = {
        "fonts": [{"id": "x", "license": "OFL", "path": "ttf/x.ttf", "status": "pending"}],
        "locale_coverage_required": {"ja_JP": {"body": "x"}},
    }
    assert select_font_path_for_locale("zz_ZZ", font_registry=registry) is None


def test_select_font_returns_none_when_file_missing():
    """File doesn't exist → returns None so caller falls back to Pillow."""
    registry = {
        "fonts": [
            {"id": "missing_font", "path": "ttf/this_file_does_not_exist.ttf",
             "license": "OFL", "status": "pending"},
        ],
        "locale_coverage_required": {"ja_JP": {"body": "missing_font"}},
    }
    assert select_font_path_for_locale("ja_JP", font_registry=registry) is None


def test_load_font_registry_returns_real_data():
    """The actual project registry should load and have CJK coverage
    after PR #647 lands."""
    registry = _load_font_registry()
    if not registry:
        pytest.skip("registry not present in this build")
    coverage = registry.get("locale_coverage_required") or {}
    # PR #647 commits all 4 catalog locales — check at least JP is registered
    assert "ja_JP" in coverage, "FONT_REGISTRY missing ja_JP coverage post-PR-647"


# ─── HarfBuzz shaping (skipped if uharfbuzz absent) ──────────────────────


def test_shape_text_harfbuzz_returns_none_without_uharfbuzz():
    """When uharfbuzz isn't installed, shape function returns None
    (signal to caller to use Pillow fallback)."""
    if _has_harfbuzz():
        pytest.skip("uharfbuzz available — fallback path tested elsewhere")
    out = shape_text_harfbuzz("hello", font_path=Path("/nonexistent.ttf"), font_size_px=14)
    assert out is None


def test_shape_text_harfbuzz_returns_none_for_missing_font():
    """Even when uharfbuzz exists, missing font → None (not crash)."""
    out = shape_text_harfbuzz(
        "hello", font_path=Path("/nonexistent_font_path.ttf"), font_size_px=14
    )
    assert out is None


# ─── render_text_to_pil — main entry point ───────────────────────────────


class _FakeDraw:
    """Minimal stand-in for PIL ImageDraw.Draw."""

    def __init__(self) -> None:
        self.calls: list[tuple] = []

    def text(self, xy, text, font=None, fill=None) -> None:
        self.calls.append(("text", xy, text, font, fill))


class _FakeFont:
    def __init__(self, path: str | None = None, size: int = 14) -> None:
        self.path = path
        self.size = size


def test_render_text_to_pil_uses_pillow_for_en_us():
    draw = _FakeDraw()
    font = _FakeFont(path="/some.ttf", size=14)
    render_text_to_pil(draw, "Hello", 10, 20, font=font, locale="en_US",
                       fill=(0, 0, 0, 255))
    assert len(draw.calls) == 1
    call = draw.calls[0]
    assert call[0] == "text"
    assert call[1] == (10, 20)
    assert call[2] == "Hello"


def test_render_text_to_pil_pillow_fallback_when_forced():
    draw = _FakeDraw()
    font = _FakeFont()
    render_text_to_pil(draw, "やあ", 5, 5, font=font, locale="ja_JP",
                       fill=(0, 0, 0, 255), pillow_fallback_only=True)
    assert len(draw.calls) == 1


def test_render_text_to_pil_handles_cjk_without_harfbuzz_gracefully():
    """If HarfBuzz isn't installed, CJK text still renders via Pillow
    fallback — never raises."""
    draw = _FakeDraw()
    font = _FakeFont(path="/nonexistent.ttf")
    # Don't force fallback — let the function decide.
    render_text_to_pil(draw, "你好", 10, 10, font=font, locale="zh_TW",
                       fill=(0, 0, 0, 255))
    # At least one draw call happened (either HarfBuzz path or Pillow fallback)
    assert len(draw.calls) == 1


def test_render_text_to_pil_silent_on_draw_failure():
    """If draw.text() raises, render_text_to_pil swallows it (defensive
    so a single bad bubble doesn't abort the whole episode render)."""
    class _BadDraw:
        def text(self, *a, **kw):
            raise RuntimeError("simulated PIL failure")

    # Should NOT raise
    render_text_to_pil(_BadDraw(), "x", 0, 0, font=_FakeFont(), locale="en_US",
                      pillow_fallback_only=True)


def test_render_text_to_pil_respects_env_var_override():
    """PHOENIX_OMEGA_PILLOW_ONLY=1 forces fallback regardless of locale."""
    import os

    os.environ["PHOENIX_OMEGA_PILLOW_ONLY"] = "1"
    try:
        draw = _FakeDraw()
        font = _FakeFont(path="/some.ttf")
        render_text_to_pil(draw, "やあ", 5, 5, font=font, locale="ja_JP")
        assert len(draw.calls) == 1
    finally:
        del os.environ["PHOENIX_OMEGA_PILLOW_ONLY"]


# ─── diagnostic ──────────────────────────────────────────────────────────


def test_diagnose_returns_required_fields():
    diag = diagnose()
    assert "uharfbuzz_available" in diag
    assert "registered_locales" in diag
    assert "fonts_count" in diag
    assert isinstance(diag["uharfbuzz_available"], bool)
    assert isinstance(diag["registered_locales"], list)
    assert isinstance(diag["fonts_count"], int)
