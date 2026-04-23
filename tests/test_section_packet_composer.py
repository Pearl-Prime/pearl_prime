"""Tests for phoenix_v4.rendering.section_packet_composer."""
from __future__ import annotations

from phoenix_v4.rendering.section_packet_composer import compose_section_packet


def test_compose_returns_audit_fields():
    # Use SCENE not HOOK: since PR #575, HOOK sections consume the enrichment
    # slot into the scene_recognition flow (replacing the source name), which
    # hides the generic "enrichment" source. SCENE exercises the default path.
    long_enr = " ".join([f"w{i}" for i in range(12)])
    out = compose_section_packet(
        chapter_index=1,
        section_index=1,
        section_type="SCENE",
        target_words=100,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={"content": long_enr, "source": "registry"},
        legacy_template_section=None,
        bridge_text=None,
    )
    assert "text" in out
    assert out["word_count"] >= 12
    assert "sources_used" in out
    assert "enrichment" in out["sources_used"]
    assert out["target_words"] == 100
    assert isinstance(out["under_target"], bool)
    assert "warnings" in out


def test_placeholder_warning():
    # Use SCENE not HOOK: PR #575 routes HOOK enrichment through
    # scene_recognition, bypassing the placeholder-check path. SCENE keeps
    # the enrichment slot content that this test targets.
    pad = " ".join([f"p{i}" for i in range(12)])
    out = compose_section_packet(
        chapter_index=1,
        section_index=2,
        section_type="SCENE",
        target_words=500,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={
            "content": pad + " Hello {name} and {{ pause_s }} there.",
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


def test_exercise_phase_prepends_journey_intro():
    long_ex = " ".join([f"ex{i}" for i in range(12)])
    out = compose_section_packet(
        chapter_index=1,
        section_index=4,
        section_type="EXERCISE",
        target_words=200,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={"content": long_ex, "source": "registry"},
        exercise_phase="awareness",
    )
    assert any(x.startswith("journey_intro:") for x in out["sources_used"])
    assert "notice what it's been holding" in out["text"]
    assert "ex0" in out["text"]


def test_bridge_text_prepended():
    # Use SCENE not HOOK: PR #575 replaces HOOK enrichment with
    # scene_recognition bank content, so the "b0" enrichment marker gets
    # consumed. SCENE preserves the enrichment-alongside-bridge contract.
    long_body = " ".join([f"b{i}" for i in range(12)])
    out = compose_section_packet(
        chapter_index=2,
        section_index=1,
        section_type="SCENE",
        target_words=400,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={"content": long_body, "source": "registry"},
        bridge_text="First line from bridge.",
    )
    assert out["text"].startswith("First line from bridge.")
    assert "b0" in out["text"]
    assert "bridge" in out["sources_used"]


def test_stacks_teacher_and_enrichment_without_duplicating_identical():
    # Use SCENE not HOOK (PR #575 scene_recognition replaces enrichment), and
    # provide teacher_id in spine_context — the composer only appends
    # teacher_atom in explicit teacher mode (see composer comment: "Without a
    # teacher_id the content has no owner, no wrapper, and no voice attribution.").
    long_reg = " ".join([f"r{i}" for i in range(12)])
    long_teacher = " ".join([f"t{i}" for i in range(12)])
    out = compose_section_packet(
        chapter_index=1,
        section_index=1,
        section_type="SCENE",
        target_words=500,
        spine_context={"teacher_id": "ahjan"},
        beatmap_slot={},
        enrichment_slot={"content": long_reg, "source": "registry"},
        teacher_atom_content=long_teacher,
    )
    assert "teacher_atom" in out["sources_used"]
    assert "enrichment" in out["sources_used"]
    assert "t0" in out["text"] and "r0" in out["text"]


def test_skips_enrichment_when_same_as_legacy():
    prose = " ".join([f"x{i}" for i in range(12)])
    out = compose_section_packet(
        chapter_index=1,
        section_index=2,
        section_type="HOOK",
        target_words=500,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={"content": prose, "source": "registry"},
        legacy_template_section={"text": prose},
    )
    assert out["sources_used"].count("enrichment") == 0
    assert "legacy_template" in out["sources_used"]


def test_beatmap_target_words_override_and_supplements():
    long_a = " ".join(f"a{i}" for i in range(12))
    long_b = " ".join(f"b{i}" for i in range(12))
    out = compose_section_packet(
        chapter_index=1,
        section_index=1,
        section_type="REFLECTION",
        target_words=50,
        spine_context={},
        beatmap_slot={"target_words": 500},
        enrichment_slot={"content": long_a, "source": "registry"},
        supplemental_enrichment_blocks=[long_b],
    )
    assert out["target_words"] == 500
    assert out["under_target"] is True
    assert any(s.startswith("enrichment_supplement:") for s in out["sources_used"])
    assert "a0" in out["text"] and "b0" in out["text"]


def test_depth_module_split():
    long_depth = " ".join([f"d{i}" for i in range(12)])
    out = compose_section_packet(
        chapter_index=3,
        section_index=5,
        section_type="DEPTH_TEST",
        target_words=200,
        spine_context={},
        beatmap_slot={},
        enrichment_slot={
            "content": long_depth,
            "source": "depth_module:mechanism_depth:teacher_atom",
        },
    )
    assert "depth_module" in out["sources_used"]
    assert "d0" in out["text"]
    assert out["text"] == out["text"].strip()


def test_packet_word_cap_truncates_stacked_packet():
    body = " ".join(f"w{i}" for i in range(80))
    out = compose_section_packet(
        chapter_index=1,
        section_index=1,
        section_type="HOOK",
        target_words=500,
        spine_context={"packet_word_cap": 25},
        beatmap_slot={},
        enrichment_slot={"content": body, "source": "registry"},
    )
    assert out["word_count"] <= 25


def test_slot_level_target_words_cap_truncates_output():
    """When stacked layers exceed target_words, output is truncated (with 10% headroom)."""
    body = " ".join(f"word{i}" for i in range(200))
    out = compose_section_packet(
        chapter_index=0,
        section_index=0,
        section_type="HOOK",
        target_words=50,
        spine_context={},
        beatmap_slot={"target_words": 50},
        enrichment_slot={"content": body, "source": "registry"},
    )
    # 50 * 1.10 = 55 word hard cap
    assert out["word_count"] <= 55, f"Expected ≤55 words, got {out['word_count']}"
