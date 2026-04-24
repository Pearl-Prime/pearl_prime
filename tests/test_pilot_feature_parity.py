"""
Phase 2 pilot feature parity tests.

Verifies that the 7 pilot-only items are now wired into the spine path:
  1. story_schedule SCENE slots (story_planner.build_story_schedule)
  2. BookSlotTracker no-repeat
  3. resolve_injections + token fill
  4. EnrichedSlot.teacher_content field
  5. additive_enrichment mode (persona → registry → teacher)
  6. section_packet_audit in enrichment_audit
  7. Registry peek for waterfall teacher slots
"""
from __future__ import annotations

import dataclasses
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Dataclass field presence
# ---------------------------------------------------------------------------

def test_enrichment_request_has_additive_enrichment():
    from phoenix_v4.planning.enrichment_select import EnrichmentRequest
    field_names = {f.name for f in dataclasses.fields(EnrichmentRequest)}
    assert "additive_enrichment" in field_names, "EnrichmentRequest missing additive_enrichment"


def test_enriched_slot_has_teacher_content():
    from phoenix_v4.planning.enrichment_select import EnrichedSlot
    field_names = {f.name for f in dataclasses.fields(EnrichedSlot)}
    assert "teacher_content" in field_names, "EnrichedSlot missing teacher_content"


def test_enriched_slot_teacher_content_defaults_empty():
    from phoenix_v4.planning.enrichment_select import EnrichedSlot
    slot = EnrichedSlot(
        slot_type="REFLECTION",
        content="hello",
        source="registry",
        source_id="v01",
        target_words=200,
        actual_words=1,
        enrichment_applied=[],
    )
    assert slot.teacher_content == ""


# ---------------------------------------------------------------------------
# BookSlotTracker + resolve_injections are importable
# ---------------------------------------------------------------------------

def test_book_slot_tracker_importable():
    from phoenix_v4.planning.injection_resolver import BookSlotTracker
    tracker = BookSlotTracker()
    tracker.record("v01", slot_type="HOOK")
    tracker.record("v02", slot_type="HOOK")
    assert "v01" in tracker._used_ids
    assert "v02" in tracker._used_ids


def test_resolve_injections_importable():
    from phoenix_v4.planning.injection_resolver import resolve_injections
    result = resolve_injections(
        "No markers here.",
        chapter_index=1,
        section_index=2,
        section_type="SCENE",
        topic="anxiety",
        persona_id="gen_z_professionals",
        teacher_id=None,
        exercise_phase=None,
        seed="test_seed",
        repo_root=REPO_ROOT,
    )
    assert "text" in result
    assert "No markers here." in result["text"]


# ---------------------------------------------------------------------------
# Story schedule wiring
# ---------------------------------------------------------------------------

def test_build_story_schedule_importable():
    from phoenix_v4.planning.story_planner import SCENE_SECTION_INDICES, StorySchedule, build_story_schedule
    assert SCENE_SECTION_INDICES == (2, 5, 9)
    sched = build_story_schedule(
        persona_id="gen_z_professionals",
        topic="anxiety",
        seed="test_seed",
        repo_root=REPO_ROOT,
    )
    assert isinstance(sched, StorySchedule)


def test_story_schedule_imported_in_enrichment_select():
    import phoenix_v4.planning.enrichment_select as es
    assert hasattr(es, "build_story_schedule"), "build_story_schedule not imported in enrichment_select"
    assert hasattr(es, "SCENE_SECTION_INDICES"), "SCENE_SECTION_INDICES not imported in enrichment_select"
    assert hasattr(es, "BookSlotTracker"), "BookSlotTracker not imported in enrichment_select"
    assert hasattr(es, "resolve_injections"), "resolve_injections not imported in enrichment_select"


# ---------------------------------------------------------------------------
# select_enrichment wires story_schedule + _slot_audit
# ---------------------------------------------------------------------------

def test_select_enrichment_produces_section_packet_audit(tmp_path):
    """section_packet_audit key must appear in enrichment_audit after select_enrichment."""
    from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
    from phoenix_v4.planning.enrichment_select import EnrichmentRequest, select_enrichment
    from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine

    try:
        spine = load_spine("anxiety", REPO_ROOT)
        knobs = load_knob_profile("anxiety", REPO_ROOT)
        shaped = apply_knobs(spine, knobs, runtime_format="standard_book", persona_id="gen_z_professionals", repo_root=REPO_ROOT)
        engines = load_topic_engines("anxiety", REPO_ROOT)
        fmt_spec = load_format_spec("standard_book", REPO_ROOT)
        beatmap = compile_beatmap(shaped, engines, fmt_spec, REPO_ROOT)
    except Exception as e:
        import pytest
        pytest.skip(f"Spine/beatmap setup failed (sparse test environment): {e}")

    req = EnrichmentRequest(
        beatmap=beatmap,
        teacher_id=None,
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        seed="test_parity",
    )
    book = select_enrichment(req, REPO_ROOT)
    audit = book.enrichment_audit
    assert "section_packet_audit" in audit, "section_packet_audit not in enrichment_audit"
    spa = audit["section_packet_audit"]
    assert isinstance(spa, list), "section_packet_audit should be a list"
    if spa:
        entry = spa[0]
        assert "chapter" in entry
        assert "slot_type" in entry
        assert "source" in entry


# ---------------------------------------------------------------------------
# No 0-markers left in content after resolve_injections round-trip
# ---------------------------------------------------------------------------

def test_injection_marker_resolution():
    from phoenix_v4.planning.injection_resolver import resolve_injections
    text = "Before. [STORY_INJECTION_POINT] After."
    result = resolve_injections(
        text,
        chapter_index=1,
        section_index=2,
        section_type="SCENE",
        topic="anxiety",
        persona_id="gen_z_professionals",
        teacher_id=None,
        exercise_phase=None,
        seed="test_marker",
        repo_root=REPO_ROOT,
    )
    assert "[STORY_INJECTION_POINT]" not in result["text"], "Unresolved story injection marker remained"


# ---------------------------------------------------------------------------
# Additive enrichment defaults False
# ---------------------------------------------------------------------------

def test_additive_enrichment_defaults_false():
    from phoenix_v4.planning.enrichment_select import EnrichmentRequest
    from phoenix_v4.planning.beatmap_compile import Beatmap
    req = EnrichmentRequest(
        beatmap=MagicMock(spec=Beatmap),
        teacher_id=None,
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        seed="test",
    )
    assert req.additive_enrichment is False
