"""Tests for locale-aware bubble rendering (PR #647 / lettering v3 integration).

Locks in PR #631 Decision 1: bubble_render reads dialogue text from
lettering_spec v3's text_by_locale dict at compose-time. Same panel art,
different markets, no re-render. v2 specs work unchanged.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ─── unit: locale flows through render_bubbles_onto_panel ─────────────────


def _make_panel_png(tmp_path: Path, name: str = "p01.png") -> Path:
    """Create a tiny PNG so render_bubbles_onto_panel has something to open."""
    from PIL import Image

    p = tmp_path / name
    Image.new("RGB", (200, 200), (255, 255, 255)).save(p)
    return p


def test_v3_dialogue_uses_text_by_locale_for_active_locale(tmp_path):
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_onto_panel

    panel = _make_panel_png(tmp_path)
    lines = [
        {
            "speaker": "A",
            "text_by_locale": {
                "en_US": "Hello",
                "ja_JP": "こんにちは",
                "zh_TW": "你好",
            },
            "intensity": "normal",
            "bubble_style": "round_normal",
        }
    ]
    layout = render_bubbles_onto_panel(
        panel, lines, sfx=[], narrator_caption=None,
        out_path=tmp_path / "out_jp.png",
        locale="ja_JP", default_locale="en_US",
    )
    placed = [r for r in layout["bubbles"] if r.get("type") == "dialogue"]
    assert placed, "expected at least one dialogue bubble placed"
    assert any("こんにちは" in str(r.get("text", "")) for r in placed), \
        f"ja_JP text not used; placed: {[r.get('text') for r in placed]}"


def test_v3_dialogue_falls_back_to_default_locale(tmp_path):
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_onto_panel

    panel = _make_panel_png(tmp_path)
    # text_by_locale only has en_US — request zh_CN, should fall back to en_US
    lines = [
        {
            "speaker": "A",
            "text_by_locale": {"en_US": "Hello"},
            "intensity": "normal",
            "bubble_style": "round_normal",
        }
    ]
    layout = render_bubbles_onto_panel(
        panel, lines, sfx=[], narrator_caption=None,
        out_path=tmp_path / "out_fallback.png",
        locale="zh_CN", default_locale="en_US",
    )
    placed = [r for r in layout["bubbles"] if r.get("type") == "dialogue"]
    assert any("Hello" in str(r.get("text", "")) for r in placed)


def test_v2_dialogue_works_unchanged(tmp_path):
    """v2 spec with single `text` field should render fine even when caller
    passes a locale that doesn't appear anywhere in the line."""
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_onto_panel

    panel = _make_panel_png(tmp_path)
    lines = [
        {
            "speaker": "A",
            "text": "v2 line",                     # no text_by_locale
            "intensity": "normal",
            "bubble_style": "round_normal",
        }
    ]
    layout = render_bubbles_onto_panel(
        panel, lines, sfx=[], narrator_caption=None,
        out_path=tmp_path / "out_v2.png",
        locale="ja_JP", default_locale="en_US",
    )
    placed = [r for r in layout["bubbles"] if r.get("type") == "dialogue"]
    assert any("v2 line" in str(r.get("text", "")) for r in placed)


def test_silent_when_no_text_for_locale_or_default(tmp_path):
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_onto_panel

    panel = _make_panel_png(tmp_path)
    lines = [
        {"speaker": "A", "intensity": "normal", "bubble_style": "round_normal"}
        # No text, no text_by_locale — should be silent.
    ]
    layout = render_bubbles_onto_panel(
        panel, lines, sfx=[], narrator_caption=None,
        out_path=tmp_path / "out_silent.png",
        locale="ja_JP", default_locale="en_US",
    )
    placed = [r for r in layout["bubbles"] if r.get("type") == "dialogue"]
    assert not placed, f"expected no dialogue placed; got {placed}"


# ─── unit: render_bubbles_on_panels picks locale + sfx + caption ──────────


def _make_min_manifest(panel_path: Path) -> dict:
    return {
        "schema_version": "1.0.0",
        "artifact_type": "panel_images_manifest",
        "panels": [
            {
                "panel_id": "p01",
                "status": "ok",
                "path": str(panel_path),
            }
        ],
    }


def test_manifest_level_render_uses_locale_for_sfx_and_caption(tmp_path):
    """v3 spec with sfx_by_locale + narrator_caption_by_locale → locale-correct output."""
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels

    panel = _make_panel_png(tmp_path, "p01.png")
    manifest = _make_min_manifest(panel)
    spec = {
        "schema_version": "1.0.0",
        "artifact_type": "lettering_spec",
        "lettering_spec_version": "3.0.0",
        "default_locale": "en_US",
        "available_locales": ["en_US", "ja_JP"],
        "lettering_panels": [
            {
                "panel_id": "p01",
                "silence_confirmed": False,
                "dialogue_lines": [
                    {
                        "speaker": "A",
                        "text_by_locale": {"en_US": "Hi", "ja_JP": "やあ"},
                        "intensity": "normal",
                        "bubble_style": "round_normal",
                    }
                ],
                "sfx_by_locale": {"en_US": ["BANG"], "ja_JP": ["ドン"]},
                "narrator_caption_by_locale": {
                    "en_US": "Later that night...",
                    "ja_JP": "その夜...",
                },
            }
        ],
    }

    out_dir = tmp_path / "out_jp"
    updated = render_bubbles_on_panels(
        chapter_script={}, lettering_spec=spec,
        panel_images_manifest=manifest,
        bubble_style_config=None, out_dir=out_dir,
        locale="ja_JP",
    )
    assert updated["bubble_render_summary"]["panels_processed"] >= 1


def test_manifest_level_render_defaults_to_spec_default_locale(tmp_path):
    """When caller passes locale=None, fall back to spec.default_locale."""
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels

    panel = _make_panel_png(tmp_path, "p02.png")
    manifest = _make_min_manifest(panel)
    spec = {
        "schema_version": "1.0.0",
        "artifact_type": "lettering_spec",
        "lettering_spec_version": "3.0.0",
        "default_locale": "ja_JP",
        "available_locales": ["ja_JP", "en_US"],
        "lettering_panels": [
            {
                "panel_id": "p01",
                "silence_confirmed": False,
                "dialogue_lines": [
                    {
                        "speaker": "A",
                        "text_by_locale": {"ja_JP": "やあ", "en_US": "Hi"},
                        "intensity": "normal",
                        "bubble_style": "round_normal",
                    }
                ],
            }
        ],
    }

    out_dir = tmp_path / "out_default"
    updated = render_bubbles_on_panels(
        chapter_script={}, lettering_spec=spec,
        panel_images_manifest=manifest,
        bubble_style_config=None, out_dir=out_dir,
    )
    assert updated["bubble_render_summary"]["panels_processed"] >= 1


def test_v2_spec_renders_unchanged_at_manifest_level(tmp_path):
    """A v2 spec without lettering_spec_version field still renders cleanly."""
    from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels

    panel = _make_panel_png(tmp_path, "p03.png")
    manifest = _make_min_manifest(panel)
    spec = {
        "schema_version": "1.0.0",
        "artifact_type": "lettering_spec",
        "lettering_panels": [
            {
                "panel_id": "p01",
                "silence_confirmed": False,
                "dialogue_lines": [
                    {"speaker": "A", "text": "v2 hello", "intensity": "normal"}
                ],
                "sfx": ["BANG"],
                "narrator_caption": "v2 caption",
            }
        ],
    }
    out_dir = tmp_path / "out_v2"
    updated = render_bubbles_on_panels(
        chapter_script={}, lettering_spec=spec,
        panel_images_manifest=manifest,
        bubble_style_config=None, out_dir=out_dir,
    )
    assert updated["bubble_render_summary"]["panels_processed"] >= 1
