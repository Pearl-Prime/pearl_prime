"""Tests for lettering_spec v3 schema + locale_resolver + migration helper."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ─── schema tests ──────────────────────────────────────────────────────────


@pytest.fixture(scope="module")
def schema():
    return json.loads(
        (REPO / "schemas" / "manga" / "lettering_spec.schema.json").read_text(encoding="utf-8")
    )


def _validator(schema):
    import jsonschema  # type: ignore

    root = (REPO / "schemas" / "manga").resolve()
    store = {p.name: json.loads(p.read_text(encoding="utf-8")) for p in root.glob("*.schema.json")}
    resolver = jsonschema.RefResolver(base_uri=root.as_uri() + "/", referrer=schema, store=store)
    return jsonschema.Draft202012Validator(schema, resolver=resolver)


def test_v2_spec_still_validates(schema):
    """Backward compat — a v2-style spec must still pass the v3 schema."""
    v = _validator(schema)
    spec = {
        "schema_version": "1.0.0",
        "artifact_type": "lettering_spec",
        "lettering_panels": [
            {
                "panel_id": "p01",
                "dialogue_lines": [{"speaker": "A", "text": "Hello"}],
                "sfx": ["BANG"],
                "narrator_caption": "Later that night...",
            }
        ],
    }
    errors = list(v.iter_errors(spec))
    assert not errors, f"v2 spec should validate: {errors}"


def test_v3_spec_with_text_by_locale(schema):
    v = _validator(schema)
    spec = {
        "schema_version": "1.0.0",
        "artifact_type": "lettering_spec",
        "lettering_spec_version": "3.0.0",
        "default_locale": "en_US",
        "available_locales": ["en_US", "ja_JP", "zh_TW"],
        "lettering_panels": [
            {
                "panel_id": "p01",
                "dialogue_lines": [
                    {
                        "speaker": "A",
                        "text_by_locale": {
                            "en_US": "Hello",
                            "ja_JP": "こんにちは",
                            "zh_TW": "你好",
                        },
                    }
                ],
                "sfx_by_locale": {
                    "en_US": ["BANG"],
                    "ja_JP": ["ドン"],
                    "zh_TW": ["碰"],
                },
                "narrator_caption_by_locale": {
                    "en_US": "Later that night...",
                    "ja_JP": "その夜...",
                },
            }
        ],
    }
    errors = list(v.iter_errors(spec))
    assert not errors, f"v3 spec should validate: {errors}"


def test_v3_rejects_unknown_locale_key(schema):
    v = _validator(schema)
    spec = {
        "schema_version": "1.0.0",
        "artifact_type": "lettering_spec",
        "lettering_spec_version": "3.0.0",
        "lettering_panels": [
            {
                "panel_id": "p01",
                "dialogue_lines": [{
                    "speaker": "A",
                    "text_by_locale": {"weird_locale": "x"},
                }],
            }
        ],
    }
    errors = list(v.iter_errors(spec))
    assert any("weird_locale" in e.message or "additional" in e.message.lower() for e in errors), \
        f"unknown locale should be rejected; errors: {[e.message for e in errors]}"


def test_v3_rejects_invalid_lettering_spec_version(schema):
    v = _validator(schema)
    spec = {
        "schema_version": "1.0.0",
        "artifact_type": "lettering_spec",
        "lettering_spec_version": "9.9.9",
        "lettering_panels": [{"panel_id": "p01"}],
    }
    errors = list(v.iter_errors(spec))
    assert any("9.9.9" in e.message or "lettering_spec_version" in str(e.absolute_path) for e in errors)


# ─── locale_resolver tests ──────────────────────────────────────────────────


from phoenix_v4.manga.chapter.locale_resolver import (  # type: ignore  # noqa: E402
    assert_locale_complete,
    coverage_check,
    resolve_dialogue_text,
    resolve_font_override,
    resolve_narrator_caption,
    resolve_sfx,
)


def test_resolve_dialogue_text_uses_explicit_locale():
    line = {"text_by_locale": {"en_US": "Hello", "ja_JP": "こんにちは"}}
    assert resolve_dialogue_text(line, locale="ja_JP", default_locale="en_US") == "こんにちは"


def test_resolve_dialogue_text_falls_back_to_default_locale():
    line = {"text_by_locale": {"en_US": "Hello"}}
    assert resolve_dialogue_text(line, locale="ja_JP", default_locale="en_US") == "Hello"


def test_resolve_dialogue_text_v2_backward_compat():
    line = {"text": "Hi"}
    assert resolve_dialogue_text(line, locale="ja_JP", default_locale="en_US") == "Hi"


def test_resolve_dialogue_text_returns_none_when_silent():
    line = {"speaker": "A"}
    assert resolve_dialogue_text(line, locale="ja_JP", default_locale="en_US") is None


def test_resolve_font_override_per_locale():
    line = {
        "font_override": "all_caps_scream",
        "font_override_by_locale": {"ja_JP": "bold_action"},  # CJK can't do all_caps
    }
    assert resolve_font_override(line, locale="ja_JP", default_locale="en_US") == "bold_action"
    assert resolve_font_override(line, locale="en_US", default_locale="en_US") == "all_caps_scream"


def test_resolve_sfx_per_locale():
    panel = {
        "sfx": ["BANG"],
        "sfx_by_locale": {"ja_JP": ["ドン"], "zh_TW": ["碰"]},
    }
    assert list(resolve_sfx(panel, locale="ja_JP", default_locale="en_US")) == ["ドン"]
    assert list(resolve_sfx(panel, locale="zh_CN", default_locale="en_US")) == ["BANG"]  # falls to v2


def test_resolve_narrator_caption_falls_back():
    panel = {"narrator_caption_by_locale": {"en_US": "Later..."}}
    assert resolve_narrator_caption(panel, locale="ja_JP", default_locale="en_US") == "Later..."


def test_coverage_check_per_locale():
    panel = {
        "estimated_bubble_coverage": 0.20,
        "estimated_bubble_coverage_by_locale": {"ja_JP": 0.15, "en_US": 0.25},
    }
    assert coverage_check(panel, locale="ja_JP", default_locale="en_US") == 0.15
    assert coverage_check(panel, locale="zh_TW", default_locale="en_US") == 0.25


def test_assert_locale_complete_passes_when_explicit():
    spec = {
        "default_locale": "en_US",
        "lettering_panels": [
            {
                "panel_id": "p01",
                "dialogue_lines": [
                    {"speaker": "A", "text_by_locale": {"en_US": "Hi", "ja_JP": "やあ"}}
                ],
            }
        ],
    }
    assert assert_locale_complete(spec, "ja_JP") == []


def test_assert_locale_complete_passes_via_v2_fallback():
    spec = {
        "default_locale": "en_US",
        "lettering_panels": [
            {
                "panel_id": "p01",
                "dialogue_lines": [{"speaker": "A", "text": "Hi"}],
            }
        ],
    }
    # v2 `text` field is fallback when no text_by_locale present
    assert assert_locale_complete(spec, "ja_JP") == []


def test_assert_locale_complete_reports_missing():
    spec = {
        "default_locale": "en_US",
        "lettering_panels": [
            {
                "panel_id": "p01",
                "dialogue_lines": [{"speaker": "A"}],  # no text anywhere
            }
        ],
    }
    errors = assert_locale_complete(spec, "ja_JP")
    assert len(errors) == 1
    assert "p01" in errors[0]
    assert "ja_JP" in errors[0]


# ─── migration helper tests ────────────────────────────────────────────────


from scripts.manga.migrate_lettering_v2_to_v3 import migrate_spec  # type: ignore  # noqa: E402


def test_migrate_spec_wraps_v2_text():
    v2 = {
        "schema_version": "1.0.0",
        "artifact_type": "lettering_spec",
        "lettering_panels": [
            {
                "panel_id": "p01",
                "dialogue_lines": [{"speaker": "A", "text": "Hi"}],
                "sfx": ["BANG"],
                "narrator_caption": "Later...",
            }
        ],
    }
    migrated, changed = migrate_spec(v2)
    assert changed
    assert migrated["lettering_spec_version"] == "3.0.0"
    assert migrated["default_locale"] == "en_US"
    assert migrated["lettering_panels"][0]["dialogue_lines"][0]["text_by_locale"] == {"en_US": "Hi"}
    assert migrated["lettering_panels"][0]["sfx_by_locale"] == {"en_US": ["BANG"]}
    assert migrated["lettering_panels"][0]["narrator_caption_by_locale"] == {"en_US": "Later..."}
    # v2 fields preserved for backward-compat
    assert migrated["lettering_panels"][0]["dialogue_lines"][0]["text"] == "Hi"


def test_migrate_spec_idempotent_on_v3():
    v3 = {
        "artifact_type": "lettering_spec",
        "lettering_spec_version": "3.0.0",
        "lettering_panels": [],
    }
    migrated, changed = migrate_spec(v3)
    assert not changed
    assert migrated == v3


def test_migrate_spec_uses_custom_default_locale():
    v2 = {
        "artifact_type": "lettering_spec",
        "lettering_panels": [
            {"panel_id": "p01", "dialogue_lines": [{"speaker": "A", "text": "やあ"}]}
        ],
    }
    migrated, _ = migrate_spec(v2, default_locale="ja_JP")
    assert migrated["default_locale"] == "ja_JP"
    assert migrated["lettering_panels"][0]["dialogue_lines"][0]["text_by_locale"] == {"ja_JP": "やあ"}
