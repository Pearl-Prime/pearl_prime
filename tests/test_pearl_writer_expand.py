"""
Tests for Pearl_Writer thin-section expansion runtime.

Contract: docs/PEARL_WRITER_EXPANSION_SPEC.md
Covers:
  - Trigger condition (below/above threshold)
  - Dry-run mode reporting
  - Voice context passed through to prompt
  - LLM call mocked for unit tests
  - section_packet_composer integration (expand_thin_sections flag)
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from phoenix_v4.rendering.pearl_writer_expand import (
    DEFAULT_THIN_THRESHOLD,
    expand_section,
    should_expand,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

def _thin_packet(wc: int = 80, target: int = 450) -> dict:
    return {
        "text": " ".join(["word"] * wc),
        "word_count": wc,
        "target_words": target,
        "sources_used": ["bridge", "legacy_template", "enrichment"],
        "warnings": [],
        "section_type": "HOOK",
        "chapter_index": 1,
        "section_index": 0,
    }


def _fat_packet(wc: int = 400, target: int = 450) -> dict:
    return {
        "text": " ".join(["word"] * wc),
        "word_count": wc,
        "target_words": target,
        "sources_used": ["bridge", "enrichment", "teacher_atom"],
        "warnings": [],
        "section_type": "SCENE",
        "chapter_index": 2,
        "section_index": 1,
    }


def _spine_context(teacher_id: str = "dr_calm") -> dict:
    return {
        "topic": "anxiety",
        "persona_id": "corporate_manager",
        "teacher_id": teacher_id,
        "engine": "standard_book",
        "format": "standard_book",
        "seed": "test_seed",
    }


# ── Trigger condition tests ───────────────────────────────────────────────────

class TestShouldExpand:
    def test_thin_below_350_triggers(self):
        packet = _thin_packet(wc=200, target=450)
        assert should_expand(packet) is True

    def test_exactly_at_threshold_does_not_trigger(self):
        # threshold = min(350, 450-100) = 350; wc=350 is NOT < 350
        packet = _thin_packet(wc=350, target=450)
        assert should_expand(packet) is False

    def test_one_below_threshold_triggers(self):
        packet = _thin_packet(wc=349, target=450)
        assert should_expand(packet) is True

    def test_fat_packet_does_not_trigger(self):
        packet = _fat_packet(wc=400, target=450)
        assert should_expand(packet) is False

    def test_low_target_adjusts_threshold(self):
        # target=300 → threshold = min(350, 300-100) = 200
        packet = _thin_packet(wc=199, target=300)
        assert should_expand(packet) is True

    def test_low_target_above_adjusted_threshold_no_trigger(self):
        # target=300 → threshold = 200; wc=200 is NOT < 200
        packet = _thin_packet(wc=200, target=300)
        assert should_expand(packet) is False

    def test_zero_word_count_triggers(self):
        packet = _thin_packet(wc=0, target=450)
        assert should_expand(packet) is True


# ── Dry-run mode tests ────────────────────────────────────────────────────────

class TestDryRun:
    def _make_request(self, wc: int = 80, target: int = 450) -> dict:
        packet = _thin_packet(wc=wc, target=target)
        return {
            "packet": packet,
            "spine_context": _spine_context(),
            "teacher_voice": "Calm, grounded, somatic register.",
            "seed": "test:dry:1:0:expansion_v1",
        }

    def test_dry_run_does_not_call_llm(self):
        req = self._make_request()
        with patch(
            "phoenix_v4.rendering.pearl_writer_expand._call_claude_api"
        ) as mock_api:
            result = expand_section(req, dry_run=True)
        mock_api.assert_not_called()
        assert result["dry_run"] is True

    def test_dry_run_reports_would_expand(self):
        req = self._make_request(wc=80, target=450)
        result = expand_section(req, dry_run=True)
        assert result["dry_run_report"]["would_expand"] is True
        assert result["dry_run_report"]["current_words"] == 80
        assert result["dry_run_report"]["target_words"] == 450

    def test_dry_run_words_to_add(self):
        req = self._make_request(wc=100, target=450)
        result = expand_section(req, dry_run=True)
        report = result["dry_run_report"]
        # words_to_add should be capped at DEFAULT_MAX_BUDGET (400)
        expected = min(450 - 100, 400)
        assert report["words_to_add"] == expected

    def test_dry_run_returns_original_text(self):
        req = self._make_request(wc=80)
        result = expand_section(req, dry_run=True)
        assert result["text"] == req["packet"]["text"]
        assert result["expanded"] is False

    def test_dry_run_fat_packet_no_report(self):
        """Fat section should not produce a dry_run_report (not thin)."""
        req = {
            "packet": _fat_packet(wc=400),
            "spine_context": _spine_context(),
            "seed": "test:fat:2:1:expansion_v1",
        }
        result = expand_section(req, dry_run=True)
        assert result["expanded"] is False
        assert "dry_run_report" not in result


# ── Voice context pass-through tests ─────────────────────────────────────────

class TestVoiceContext:
    def _expand_with_voice(self, voice, *, mock_output: str = "expanded " * 500) -> tuple:
        packet = _thin_packet(wc=80)
        req = {
            "packet": packet,
            "spine_context": _spine_context(teacher_id="dr_calm"),
            "teacher_voice": voice,
            "seed": "test:voice:1:0:expansion_v1",
        }
        captured: list = []

        def fake_call(*, system_prompt, user_prompt, max_tokens, model, timeout=None, api_key=None, **kw):
            captured.append(user_prompt)
            return mock_output

        with patch(
            "phoenix_v4.rendering.pearl_writer_expand._call_claude_api",
            side_effect=fake_call,
        ):
            result = expand_section(req, dry_run=False)

        return result, captured

    def test_string_voice_appears_in_prompt(self):
        voice = "Grounded, somatic, second-person warmth."
        _, captured = self._expand_with_voice(voice)
        assert len(captured) == 1
        assert "Grounded, somatic, second-person warmth." in captured[0]

    def test_list_voice_atoms_appear_in_prompt(self):
        voice = ["Atom one text here.", "Atom two text here."]
        _, captured = self._expand_with_voice(voice)
        assert "Atom one text here." in captured[0]

    def test_dict_voice_appears_in_prompt(self):
        voice = {"style": "calm", "register": "somatic"}
        _, captured = self._expand_with_voice(voice)
        assert "calm" in captured[0]

    def test_teacher_id_appears_in_prompt(self):
        voice = "Voice reference text."
        _, captured = self._expand_with_voice(voice)
        assert "dr_calm" in captured[0]

    def test_no_voice_context_skipped(self):
        """Missing teacher_id AND missing teacher_voice → skip expansion."""
        packet = _thin_packet(wc=80)
        req = {
            "packet": packet,
            "spine_context": {"topic": "anxiety"},  # no teacher_id
            "teacher_voice": None,
            "seed": "test:no_voice:expansion_v1",
        }
        result = expand_section(req, dry_run=False)
        assert result["expanded"] is False
        assert any("skipped" in w for w in result["warnings"])


# ── LLM mock integration tests ────────────────────────────────────────────────

class TestLLMMock:
    def _make_request(self, wc: int = 80) -> dict:
        return {
            "packet": _thin_packet(wc=wc),
            "spine_context": _spine_context(),
            "teacher_voice": "Voice reference.",
            "seed": "test:llm:1:0:expansion_v1",
        }

    def test_successful_expansion(self):
        mock_text = " ".join(["expanded"] * 460)
        with patch(
            "phoenix_v4.rendering.pearl_writer_expand._call_claude_api",
            return_value=mock_text,
        ):
            result = expand_section(self._make_request(), dry_run=False)

        assert result["expanded"] is True
        assert result["word_count"] == 460
        assert result["text"] == mock_text
        assert "pearl_writer:expansion_v1" in result["sources_used_delta"]

    def test_api_failure_falls_back(self):
        with patch(
            "phoenix_v4.rendering.pearl_writer_expand._call_claude_api",
            return_value=None,
        ):
            result = expand_section(self._make_request(wc=80), dry_run=False)

        assert result["expanded"] is False
        assert any("api_call_failed" in w for w in result["warnings"])
        assert result["text"] == " ".join(["word"] * 80)

    def test_fat_section_skips_llm(self):
        req = {
            "packet": _fat_packet(wc=400),
            "spine_context": _spine_context(),
            "teacher_voice": "Voice ref.",
            "seed": "test:fat:expansion_v1",
        }
        with patch(
            "phoenix_v4.rendering.pearl_writer_expand._call_claude_api"
        ) as mock_api:
            result = expand_section(req, dry_run=False)
        mock_api.assert_not_called()
        assert result["expanded"] is False

    def test_layer_map_returned(self):
        mock_text = "Para one.\n\nPara two.\n\nPara three."
        with patch(
            "phoenix_v4.rendering.pearl_writer_expand._call_claude_api",
            return_value=mock_text,
        ):
            result = expand_section(self._make_request(), dry_run=False)

        assert isinstance(result["layer_map"], dict)
        assert "para_1" in result["layer_map"]

    def test_sources_used_delta_on_expansion(self):
        mock_text = " ".join(["word"] * 460)
        with patch(
            "phoenix_v4.rendering.pearl_writer_expand._call_claude_api",
            return_value=mock_text,
        ):
            result = expand_section(self._make_request(), dry_run=False)

        assert result["sources_used_delta"] == ["pearl_writer:expansion_v1"]


# ── section_packet_composer integration ──────────────────────────────────────

class TestComposerIntegration:
    """Smoke-tests for the expand_thin_sections flag in compose_section_packet."""

    def _base_kwargs(self) -> dict:
        return dict(
            chapter_index=1,
            section_index=0,
            section_type="HOOK",
            target_words=450,
            spine_context=_spine_context(),
            beatmap_slot={},
            enrichment_slot=None,
            bridge_text="Short bridge.",
        )

    def test_default_off_no_expansion(self):
        """expand_thin_sections defaults to False — no pearl_writer key in result."""
        from phoenix_v4.rendering.section_packet_composer import compose_section_packet

        result = compose_section_packet(**self._base_kwargs())
        assert "pearl_writer_expansion" not in result

    def test_flag_on_thin_section_calls_expand(self):
        from phoenix_v4.rendering.section_packet_composer import compose_section_packet

        mock_text = " ".join(["expanded"] * 460)
        with patch(
            "phoenix_v4.rendering.pearl_writer_expand._call_claude_api",
            return_value=mock_text,
        ):
            result = compose_section_packet(
                **self._base_kwargs(),
                expand_thin_sections=True,
                teacher_voice="Voice ref.",
            )

        assert "pearl_writer_expansion" in result
        assert result["pearl_writer_expansion"]["expanded"] is True

    def test_flag_on_fat_section_no_expansion(self):
        """Fat section above threshold: should_expand is False → no expansion key in result."""
        from phoenix_v4.rendering.section_packet_composer import compose_section_packet

        # Avoid 400× identical "word": clean_for_delivery manuscript_recurrence strips
        # repeated 8-word phrases, which would collapse this fixture to a tiny word_count.
        fat_text = " ".join(f"w{i % 500}" for i in range(400))
        kwargs = {k: v for k, v in self._base_kwargs().items() if k != "bridge_text"}
        result = compose_section_packet(
            **kwargs,
            bridge_text=fat_text,
            expand_thin_sections=True,
            teacher_voice="Voice ref.",
        )

        # Threshold = min(350, 450-100) = 350; 400 words > 350 → no expansion attempted
        assert "pearl_writer_expansion" not in result
        # HOOK section_type triggers scene_recognition bank injection (~12-17 extra words)
        # per PR #575 (BookSlotTracker + HOOK scene-recognition routing). Accept the overhead
        # while still confirming the 400-word fat bridge dominates and expansion was skipped.
        assert result["word_count"] >= 400
