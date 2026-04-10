"""Tests for phoenix_v4.planning.enrichment_select."""
from __future__ import annotations

import json

import pytest

from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
from phoenix_v4.planning.enrichment_select import (
    EnrichmentRequest,
    budget_from_enriched,
    dump_enriched_book_json,
    enriched_book_to_jsonable,
    select_enrichment,
)
from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine
from phoenix_v4.rendering.chapter_composer import compose_from_enriched_book


@pytest.fixture
def fmt_std():
    return load_format_spec("standard_book")


def _beatmap(topic: str, fmt_std):
    spine = load_spine(topic)
    shaped = apply_knobs(spine, load_knob_profile(topic), runtime_format="standard_book")
    return compile_beatmap(shaped, load_topic_engines(topic), fmt_std)


def test_select_enrichment_returns_book(fmt_std):
    bm = _beatmap("anxiety", fmt_std)
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="t1",
        )
    )
    assert book.stage == "enrichment_select"
    assert book.schema_version == 1
    assert book.topic == "anxiety"
    assert len(book.chapters) == 12


def test_audit_counts_present(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="audit",
        )
    )
    a = book.enrichment_audit
    assert a["total_slots"] > 0
    assert a["total_words"] == book.total_words
    assert "slots_from_registry" in a
    assert "slots_empty" in a


def test_teacher_atoms_preferred_for_hook(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="teacher_hook",
        )
    )
    hooks = [s for s in book.chapters[0].slots if s.slot_type == "HOOK"]
    assert hooks
    assert hooks[0].source == "teacher_atom"


def test_deterministic_same_seed(fmt_std):
    req = EnrichmentRequest(
        beatmap=_beatmap("grief", fmt_std),
        teacher_id=None,
        persona_id="gen_z_professionals",
        topic_id="grief",
        seed="determinism",
    )
    a = select_enrichment(req)
    b = select_enrichment(req)
    assert a.chapters[0].slots[0].content == b.chapters[0].slots[0].content


def test_different_seed_can_change_content(fmt_std):
    bm = _beatmap("anxiety", fmt_std)
    a = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="aaa",
        )
    )
    b = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="zzz",
        )
    )
    p1 = compose_from_enriched_book(a)
    p2 = compose_from_enriched_book(b)
    assert p1 != p2


def test_grief_topic(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("grief", fmt_std),
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="grief",
            seed="g",
        )
    )
    assert len(book.chapters) == 12


def test_burnout_topic(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("burnout", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="burnout",
            seed="b",
        )
    )
    assert book.topic == "burnout"


def test_compose_from_enriched_skips_content_gaps(monkeypatch, fmt_std):
    from phoenix_v4.planning import enrichment_select as es

    def empty_reg(_topic):
        return {"sections": {}}

    monkeypatch.setattr(es, "load_registry", empty_reg)
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="",
            topic_id="anxiety",
            seed="gap",
        )
    )
    prose = compose_from_enriched_book(book)
    assert "[CONTENT GAP" not in prose
    assert book.enrichment_audit["slots_empty"] > 0


def test_compose_from_enriched_includes_body(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="body",
        )
    )
    prose = compose_from_enriched_book(book)
    assert "Chapter 1" in prose
    assert book.chapters[0].working_title in prose
    assert len(prose.split()) > 100


def test_budget_from_enriched_matches_chapter_words(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="bud",
        )
    )
    b = budget_from_enriched(book)
    assert b["total_words"] == book.total_words
    assert sum(c["words"] for c in b["chapters"]) == book.total_words


def test_enriched_slot_fields_populated(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="fields",
        )
    )
    s = book.chapters[0].slots[0]
    assert s.slot_type
    assert s.source in ("teacher_atom", "persona_atom", "registry", "practice_library", "gap")
    assert s.actual_words == len((s.content or "").split())


def test_dump_enriched_json_loadable(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="json",
        )
    )
    raw = dump_enriched_book_json(book)
    data = json.loads(raw)
    assert data["stage"] == "enrichment_select"
    assert len(data["chapters"]) == 12


def test_jsonable_has_audit(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="ja",
        )
    )
    d = enriched_book_to_jsonable(book)
    assert "enrichment_audit" in d
    assert d["enrichment_audit"]["total_slots"] >= 12


def test_persona_scene_or_story_sourced(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="persona",
        )
    )
    assert book.enrichment_audit["slots_from_persona"] >= 1


def test_registry_used_when_no_teacher(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="reg",
        )
    )
    assert book.enrichment_audit["slots_from_registry"] >= 1


def test_gap_details_recorded(monkeypatch, fmt_std):
    from phoenix_v4.planning import enrichment_select as es

    def empty_reg(_topic):
        return {"sections": {}}

    monkeypatch.setattr(es, "load_registry", empty_reg)
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id=None,
            persona_id="",
            topic_id="anxiety",
            seed="gd",
        )
    )
    assert book.enrichment_audit["gap_details"]
    assert all("slot_type" in x for x in book.enrichment_audit["gap_details"])


def test_chapter_source_breakdown_sums_slots(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="br",
        )
    )
    for ch in book.chapters:
        n = sum(ch.source_breakdown.values())
        assert n == len(ch.slots)


def test_runtime_format_passthrough(fmt_std):
    bm = _beatmap("anxiety", fmt_std)
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="rt",
        )
    )
    assert book.runtime_format == bm.runtime_format
