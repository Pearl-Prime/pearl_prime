"""Tests for phoenix_v4.rendering.section_packet_composer."""
from __future__ import annotations

from phoenix_v4.rendering.section_packet_composer import compose_section_packet


def test_compose_returns_audit_fields():
    out = compose_section_packet(
        chapter_index=1,
        section_index=1,
        section_type="HOOK",
        target_words=100,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={"content": "One two three four five.", "source": "registry"},
        legacy_template_section=None,
        bridge_text=None,
    )
    assert "text" in out
    assert out["word_count"] >= 5
    assert "sources_used" in out
    assert "enrichment" in out["sources_used"]
    assert out["target_words"] == 100
    assert isinstance(out["under_target"], bool)
    assert "warnings" in out


def test_placeholder_warning():
    out = compose_section_packet(
        chapter_index=1,
        section_index=2,
        section_type="HOOK",
        target_words=500,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={
            "content": "Hello {name} and {{ pause_s }} there.",
            "source": "registry",
        },
        legacy_template_section=None,
    )
    assert any("unresolved_placeholder" in w for w in out["warnings"])
    assert "{name}" not in out["text"]
    assert "pause_s" not in out["text"]


def test_under_target_flag():
    out = compose_section_packet(
        chapter_index=1,
        section_index=1,
        section_type="REFLECTION",
        target_words=1000,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={"content": "Short.", "source": "registry"},
    )
    assert out["under_target"] is True


def test_empty_enrichment_still_works():
    out = compose_section_packet(
        chapter_index=2,
        section_index=3,
        section_type="EXERCISE",
        target_words=50,
        spine_context={},
        beatmap_slot={},
        enrichment_slot=None,
    )
    assert out["text"] == ""
    assert out["word_count"] == 0
    assert out["sources_used"] == []


def test_bridge_text_prepended():
    out = compose_section_packet(
        chapter_index=2,
        section_index=1,
        section_type="HOOK",
        target_words=400,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={"content": "Body text after bridge.", "source": "registry"},
        bridge_text="First line from bridge.",
    )
    assert out["text"].startswith("First line from bridge.")
    assert "Body text" in out["text"]
    assert "bridge" in out["sources_used"]


def test_depth_module_split():
    out = compose_section_packet(
        chapter_index=3,
        section_index=5,
        section_type="DEPTH_TEST",
        target_words=200,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={
            "content": "Depth only words here repeated.",
            "source": "depth_module:mechanism_depth:teacher_atom",
        },
    )
    assert "depth_module" in out["sources_used"]
    assert "Depth only" in out["text"]
    assert out["text"] == out["text"].strip()
