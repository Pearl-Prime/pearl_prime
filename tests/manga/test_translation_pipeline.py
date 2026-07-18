"""Tests for the manga translation pipeline.

Uses the deterministic mock backend (no network); locks in:
- Per-line dialogue translation
- SFX list translation
- Narrator caption translation
- Idempotency (re-running doesn't re-translate)
- ko_KR placeholder behavior
- Backend override per locale
- available_locales metadata update
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from phoenix_v4.manga.translation.iyashikei_glossary import (  # type: ignore
    SFX_POLICY_BY_LOCALE,
    TERMINOLOGY,
    TONE_NOTES_BY_LOCALE,
    system_prompt_for,
)
from phoenix_v4.manga.translation.translators import (  # type: ignore
    BackendUnavailableError,
    available_backends,
    bulk_translate,
    translate,
)
from scripts.manga.translate_chapter_script import (  # type: ignore
    translate_chapter_script,
)


# ─── translator backends ──────────────────────────────────────────────────


def test_mock_backend_is_deterministic():
    out = translate("hello", target_locale="ja_JP", backend="mock")
    assert out == "[ja_JP] hello"
    out2 = translate("hello", target_locale="ja_JP", backend="mock")
    assert out == out2


def test_translate_returns_input_for_source_locale():
    out = translate("hello", target_locale="en_US", backend="qwen_ollama")
    assert out == "hello"


def test_translate_returns_input_for_empty_string():
    out = translate("", target_locale="ja_JP", backend="qwen_ollama")
    assert out == ""
    out_ws = translate("   ", target_locale="ja_JP", backend="qwen_ollama")
    assert out_ws == "   "


def test_unknown_backend_raises():
    with pytest.raises(BackendUnavailableError, match="Unknown backend"):
        translate("hi", target_locale="ja_JP", backend="not_a_backend")


def test_placeholder_backend_returns_input():
    """ko_KR / connector-not-ready placeholder mode."""
    out = translate("Hi", target_locale="ko_KR", backend="placeholder")
    assert out == "Hi"


def test_available_backends_includes_qwen_and_overrides():
    backends = available_backends()
    assert "qwen_ollama" in backends     # Tier 2 default
    assert "deepseek" in backends         # operator override
    assert "google_ai" in backends        # operator override
    assert "mock" in backends             # tests
    assert "placeholder" in backends      # ko_KR


def test_bulk_translate_respects_order():
    out = bulk_translate(["a", "b", "c"], target_locale="zh_TW", backend="mock")
    assert out == ["[zh_TW] a", "[zh_TW] b", "[zh_TW] c"]


# ─── glossary / system prompt ─────────────────────────────────────────────


def test_glossary_covers_all_catalog_locales():
    catalog_locales = ("ja_JP", "zh_TW", "zh_CN", "ko_KR")
    for locale in catalog_locales:
        assert locale in TONE_NOTES_BY_LOCALE
        assert locale in SFX_POLICY_BY_LOCALE


def test_terminology_lockins_match_locales():
    for term, locales in TERMINOLOGY.items():
        for locale in ("ja_JP", "zh_TW", "zh_CN", "ko_KR"):
            assert locale in locales, f"term '{term}' missing {locale}"


def test_system_prompt_includes_tone_and_sfx():
    sp = system_prompt_for("ja_JP")
    assert "iyashikei" in sp.lower() or "癒し" in sp
    assert "BANG" in sp or "ドン" in sp  # SFX policy mentions one


# ─── chapter_script-level translation ─────────────────────────────────────


def _spec_with_one_panel():
    return {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "available_locales": ["en_US"],
        "default_locale": "en_US",
        "pages": [
            {
                "panels": [
                    {
                        "panel_id": "p01",
                        "dialogue_lines": [
                            {
                                "speaker": "A",
                                "text_by_locale": {"en_US": "The tea is still warm."},
                                "intensity": "calm",
                            }
                        ],
                        "sfx_by_locale": {"en_US": ["BANG"]},
                        "narrator_caption_by_locale": {"en_US": "Tuesday morning."},
                    }
                ]
            }
        ],
    }


def test_translate_chapter_script_populates_all_target_locales():
    spec, stats = translate_chapter_script(
        _spec_with_one_panel(),
        target_locales=["ja_JP", "zh_TW"],
        backend="mock",
    )

    panel = spec["pages"][0]["panels"][0]
    assert panel["dialogue_lines"][0]["text_by_locale"]["ja_JP"] == "[ja_JP] The tea is still warm."
    assert panel["dialogue_lines"][0]["text_by_locale"]["zh_TW"] == "[zh_TW] The tea is still warm."

    assert panel["sfx_by_locale"]["ja_JP"] == ["[ja_JP] BANG"]
    assert panel["sfx_by_locale"]["zh_TW"] == ["[zh_TW] BANG"]

    assert panel["narrator_caption_by_locale"]["ja_JP"] == "[ja_JP] Tuesday morning."
    assert panel["narrator_caption_by_locale"]["zh_TW"] == "[zh_TW] Tuesday morning."


def test_translate_chapter_script_updates_available_locales():
    spec, _ = translate_chapter_script(
        _spec_with_one_panel(),
        target_locales=["ja_JP", "zh_TW", "zh_CN"],
        backend="mock",
    )
    assert "en_US" in spec["available_locales"]
    assert "ja_JP" in spec["available_locales"]
    assert "zh_TW" in spec["available_locales"]
    assert "zh_CN" in spec["available_locales"]


def test_translate_chapter_script_idempotent_without_force():
    """Running translate twice with the same target_locales should NOT
    re-translate locales that are already populated."""
    spec1 = _spec_with_one_panel()
    spec2, _ = translate_chapter_script(spec1, target_locales=["ja_JP"], backend="mock")
    # Manually mutate to detect re-translation
    spec2["pages"][0]["panels"][0]["dialogue_lines"][0]["text_by_locale"]["ja_JP"] = "DO_NOT_OVERWRITE"
    spec3, _ = translate_chapter_script(spec2, target_locales=["ja_JP"], backend="mock")
    assert (
        spec3["pages"][0]["panels"][0]["dialogue_lines"][0]["text_by_locale"]["ja_JP"]
        == "DO_NOT_OVERWRITE"
    )


def test_translate_chapter_script_force_re_translates():
    spec1 = _spec_with_one_panel()
    spec2, _ = translate_chapter_script(spec1, target_locales=["ja_JP"], backend="mock")
    spec2["pages"][0]["panels"][0]["dialogue_lines"][0]["text_by_locale"]["ja_JP"] = "STALE"
    spec3, _ = translate_chapter_script(
        spec2, target_locales=["ja_JP"], backend="mock", force=True
    )
    assert (
        spec3["pages"][0]["panels"][0]["dialogue_lines"][0]["text_by_locale"]["ja_JP"]
        == "[ja_JP] The tea is still warm."
    )


def test_translate_chapter_script_ko_kr_placeholder_default():
    """ko_KR backend defaults to 'placeholder' (echoes en_US) until Naver
    connector ships in Phase 2."""
    spec, _ = translate_chapter_script(
        _spec_with_one_panel(),
        target_locales=["ko_KR"],
        backend="mock",  # default for non-ko locales
        # Don't override ko_KR — should default to placeholder
    )
    panel = spec["pages"][0]["panels"][0]
    assert panel["dialogue_lines"][0]["text_by_locale"]["ko_KR"] == "The tea is still warm."


def test_translate_chapter_script_per_locale_backend_override():
    spec, _ = translate_chapter_script(
        _spec_with_one_panel(),
        target_locales=["ja_JP", "zh_TW"],
        backend="mock",
        backend_overrides={"zh_TW": "placeholder"},
    )
    panel = spec["pages"][0]["panels"][0]
    # ja_JP went through mock → wrapped
    assert panel["dialogue_lines"][0]["text_by_locale"]["ja_JP"] == "[ja_JP] The tea is still warm."
    # zh_TW went through placeholder → echoed
    assert panel["dialogue_lines"][0]["text_by_locale"]["zh_TW"] == "The tea is still warm."


def test_translate_chapter_script_handles_empty_dialogue():
    spec = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "default_locale": "en_US",
        "pages": [{"panels": [{"panel_id": "p01", "silence_confirmed": True}]}],
    }
    spec_out, stats = translate_chapter_script(
        spec, target_locales=["ja_JP"], backend="mock"
    )
    # No exception; available_locales updated
    assert "ja_JP" in spec_out["available_locales"]
    assert stats["ja_JP"] == 0
