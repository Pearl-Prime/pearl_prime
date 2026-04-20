"""Tests for lettering_from_script.py — v2 extended schema."""

from __future__ import annotations

import pytest

from phoenix_v4.manga.chapter.lettering_from_script import (
    build_lettering_spec_from_chapter_script,
    _panel_has_dialogue_text,
)
from phoenix_v4.manga.models.validation import validate_instance


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_script(panels: list[dict]) -> dict:
    return {
        "artifact_type": "chapter_script_writer_handoff",
        "schema_version": "1.0.0",
        "series_id": "test_series",
        "chapter_id": "ch01",
        "pages": [
            {
                "page_number": 1,
                "panels": [dict(p) for p in panels],
            }
        ],
    }


# ---------------------------------------------------------------------------
# _panel_has_dialogue_text
# ---------------------------------------------------------------------------

class TestPanelHasDialogueText:
    def test_str_dialogue_true(self):
        panel = {"panel_id": "p1", "dialogue": ["Hello!", "World"]}
        assert _panel_has_dialogue_text(panel) is True

    def test_str_dialogue_empty_strings(self):
        panel = {"panel_id": "p1", "dialogue": ["", "   "]}
        assert _panel_has_dialogue_text(panel) is False

    def test_no_dialogue(self):
        panel = {"panel_id": "p1"}
        assert _panel_has_dialogue_text(panel) is False

    def test_none_dialogue(self):
        panel = {"panel_id": "p1", "dialogue": None}
        assert _panel_has_dialogue_text(panel) is False

    def test_empty_list(self):
        panel = {"panel_id": "p1", "dialogue": []}
        assert _panel_has_dialogue_text(panel) is False

    def test_dict_dialogue_true(self):
        """Fix for WS4-identified dict-handling bug."""
        panel = {
            "panel_id": "p1",
            "dialogue": [{"speaker": "hero", "text": "I won't give up!"}],
        }
        assert _panel_has_dialogue_text(panel) is True

    def test_dict_dialogue_empty_text(self):
        panel = {
            "panel_id": "p1",
            "dialogue": [{"speaker": "hero", "text": ""}],
        }
        assert _panel_has_dialogue_text(panel) is False

    def test_dict_dialogue_missing_text_key(self):
        panel = {
            "panel_id": "p1",
            "dialogue": [{"speaker": "hero"}],
        }
        assert _panel_has_dialogue_text(panel) is False

    def test_mixed_str_and_dict(self):
        panel = {
            "panel_id": "p1",
            "dialogue": ["", {"speaker": "hero", "text": "Alive!"}],
        }
        assert _panel_has_dialogue_text(panel) is True


# ---------------------------------------------------------------------------
# build_lettering_spec_from_chapter_script — v2
# ---------------------------------------------------------------------------

class TestLetteringSpecV2:
    def test_silent_panel(self):
        script = _make_script([{"panel_id": "p01", "action": "Wide shot"}])
        spec = build_lettering_spec_from_chapter_script(script)
        assert spec["schema_version"] == "2.0.0"
        assert spec["artifact_type"] == "lettering_spec"
        row = spec["lettering_panels"][0]
        assert row["panel_id"] == "p01"
        assert row["silence_confirmed"] is True
        assert row["dialogue_lines"] == []
        assert row["sfx"] == []
        assert row["narrator_caption"] is None

    def test_dialogue_panel_str_format(self):
        script = _make_script([
            {"panel_id": "p01", "dialogue": ["I won't give up!"]}
        ])
        spec = build_lettering_spec_from_chapter_script(script)
        row = spec["lettering_panels"][0]
        assert row["silence_confirmed"] is False
        assert len(row["dialogue_lines"]) == 1
        dl = row["dialogue_lines"][0]
        assert dl["text"] == "I won't give up!"
        assert dl["speaker"] == "speaker_1"
        assert dl["bubble_style"] == "round_normal"  # normal intensity default

    def test_dialogue_panel_dict_format(self):
        script = _make_script([
            {
                "panel_id": "p01",
                "dialogue": [
                    {
                        "speaker": "protagonist",
                        "text": "I won't give up!",
                        "emotion": "determination",
                        "intensity": "shouting",
                        "bubble_style": "spiky_emphasis",
                        "position_hint": "top_right",
                    }
                ],
            }
        ])
        spec = build_lettering_spec_from_chapter_script(script)
        row = spec["lettering_panels"][0]
        assert row["silence_confirmed"] is False
        dl = row["dialogue_lines"][0]
        assert dl["speaker"] == "protagonist"
        assert dl["intensity"] == "shouting"
        assert dl["bubble_style"] == "spiky_emphasis"
        assert dl["position_hint"] == "top_right"
        assert dl["bubble_style"] == "spiky_emphasis"
        assert dl["font_override"] == "bold_action"

    def test_no_dialogue_sfx_panel(self):
        """Panel with only SFX should have silence_confirmed=True."""
        script = _make_script([
            {"panel_id": "p01", "sfx": ["CRACK"], "action": "Punch lands"}
        ])
        spec = build_lettering_spec_from_chapter_script(script)
        row = spec["lettering_panels"][0]
        assert row["silence_confirmed"] is False  # has SFX
        assert row["sfx"] == ["CRACK"]
        assert row["dialogue_lines"] == []

    def test_narrator_caption(self):
        script = _make_script([
            {"panel_id": "p01", "narrator_caption": "Three weeks earlier..."}
        ])
        spec = build_lettering_spec_from_chapter_script(script)
        row = spec["lettering_panels"][0]
        assert row["silence_confirmed"] is False  # has caption
        assert row["narrator_caption"] == "Three weeks earlier..."

    def test_multi_speaker_panel(self):
        script = _make_script([
            {
                "panel_id": "p01",
                "dialogue": [
                    {"speaker": "hero", "text": "Ready?", "intensity": "normal"},
                    {"speaker": "rival", "text": "Don't hold back.", "intensity": "calm"},
                ],
            }
        ])
        spec = build_lettering_spec_from_chapter_script(script)
        row = spec["lettering_panels"][0]
        assert len(row["dialogue_lines"]) == 2
        assert row["dialogue_lines"][0]["speaker"] == "hero"
        assert row["dialogue_lines"][1]["speaker"] == "rival"
        # Reading-order positions: first line → top_right, second → top_left
        assert row["dialogue_lines"][0]["position_hint"] == "top_right"
        assert row["dialogue_lines"][1]["position_hint"] == "top_left"

    def test_internal_monologue_intensity(self):
        script = _make_script([
            {
                "panel_id": "p01",
                "dialogue": [
                    {"speaker": "hero", "text": "Why can't I be stronger?", "intensity": "internal"}
                ],
            }
        ])
        spec = build_lettering_spec_from_chapter_script(script)
        dl = spec["lettering_panels"][0]["dialogue_lines"][0]
        assert dl["bubble_style"] == "cloud_thought"
        assert dl["tail_style"] == "dotless"
        assert dl["font_override"] == "italic_internal"

    def test_schema_version_is_2(self):
        script = _make_script([{"panel_id": "p01"}])
        spec = build_lettering_spec_from_chapter_script(script)
        assert spec["schema_version"] == "2.0.0"

    def test_v1_fallback(self):
        """schema_version='1.0.0' produces legacy minimal output."""
        script = _make_script([
            {"panel_id": "p01", "dialogue": ["Test line"]}
        ])
        spec = build_lettering_spec_from_chapter_script(script, schema_version="1.0.0")
        row = spec["lettering_panels"][0]
        assert "dialogue_lines" not in row
        assert "sfx" not in row
        assert row["silence_confirmed"] is False

    def test_missing_panel_id_raises(self):
        script = _make_script([{"action": "no id"}])
        with pytest.raises(ValueError, match="panel_id"):
            build_lettering_spec_from_chapter_script(script)

    def test_schema_validates(self):
        """v2 output must pass the lettering_spec JSON schema."""
        script = _make_script([
            {
                "panel_id": "p01",
                "dialogue": [
                    {"speaker": "hero", "text": "Let's go!", "intensity": "excited"}
                ],
                "sfx": ["BANG"],
            },
            {"panel_id": "p02", "action": "Silence"},
        ])
        spec = build_lettering_spec_from_chapter_script(script)
        # Should not raise
        validate_instance(spec, "lettering_spec")
