"""Tests for phoenix_v4.planning.enrichment_select."""
from __future__ import annotations

import json

import pytest

from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
from phoenix_v4.planning.enrichment_select import (
    EnrichedBook,
    EnrichedChapter,
    EnrichedSlot,
    EnrichmentRequest,
    apply_depth_pass,
    budget_from_enriched,
    dump_enriched_book_json,
    enriched_book_to_jsonable,
    peek_registry_content_for_beatmap_slot,
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


def test_peek_registry_for_beatmap_slot_non_empty_under_teacher(fmt_std):
    bm = _beatmap("anxiety", fmt_std)
    seed = "teacher_hook"
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed=seed,
        )
    )
    assert book.chapters[0].slots[0].source == "teacher_atom"
    peek = peek_registry_content_for_beatmap_slot(
        beatmap=bm,
        chapter_number=1,
        slot_index=0,
        topic_id="anxiety",
        teacher_id="ahjan",
        persona_id="gen_z_professionals",
        seed=seed,
    )
    assert len(peek.split()) > 10
    assert peek.strip() != book.chapters[0].slots[0].content.strip()


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


def _repo_root():
    from pathlib import Path

    return Path(__file__).resolve().parent.parent


def test_depth_pass_fills_thin_chapter(fmt_std):
    """Thin chapter (large deficit) receives at least one DEPTH_* slot."""
    slot = EnrichedSlot("HOOK", "short", "gap", "id", 2500, 1, [])
    ch = EnrichedChapter(1, "r", "wt", "th", [slot], 1, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        "ahjan",
        "gen_z_professionals",
        "standard_book",
        [ch],
        1,
        {},
    )
    import yaml

    depth_map = yaml.safe_load(
        (_repo_root() / "config" / "depth" / "depth_module_map.yaml").read_text(encoding="utf-8")
    )
    out = apply_depth_pass(book, depth_map, repo_root=_repo_root())
    depth_slots = [s for s in out.chapters[0].slots if s.slot_type.startswith("DEPTH_")]
    assert depth_slots
    assert out.enrichment_audit.get("depth_modules_added")


def test_depth_pass_skips_full_chapter(fmt_std):
    """When deficit <= 100, no depth slots are appended."""
    slot = EnrichedSlot("HOOK", "word " * 40, "t", "id", 100, 40, [])
    ch = EnrichedChapter(1, "r", "wt", "th", [slot], 40, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        None,
        "gen_z_professionals",
        "standard_book",
        [ch],
        40,
        {},
    )
    depth_map = {
        "depth_modules": {
            "recognition_depth": {
                "chapter_affinity": "all",
                "sources": [{"type": "teacher_atom", "slot_types": ["HOOK"]}],
                "target_words_per_chapter": [200, 400],
            }
        },
        "topic_overrides": {"anxiety": {"depth_priority_early": ["recognition_depth"]}},
    }
    out = apply_depth_pass(book, depth_map, repo_root=_repo_root())
    assert not [s for s in out.chapters[0].slots if s.slot_type.startswith("DEPTH_")]


def test_depth_pass_respects_banned(fmt_std):
    """Grief early: banned_early blocks practice_scaffold."""
    slot = EnrichedSlot("HOOK", "x", "t", "id", 3000, 1, [])
    ch = EnrichedChapter(1, "r", "wt", "th", [slot], 1, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "grief",
        "ahjan",
        "gen_z_professionals",
        "standard_book",
        [ch],
        1,
        {},
    )
    depth_map = {
        "depth_modules": {
            "practice_scaffold": {
                "chapter_affinity": "all",
                "sources": [{"type": "component_template", "pool": "bridge"}],
                "target_words_per_chapter": [200, 400],
            }
        },
        "topic_overrides": {
            "grief": {
                "depth_priority_early": ["practice_scaffold"],
                "banned_early": ["practice_scaffold"],
            }
        },
    }
    out = apply_depth_pass(book, depth_map, repo_root=_repo_root())
    assert not any("practice_scaffold" in s.slot_type.lower() for s in out.chapters[0].slots)


def test_depth_pass_respects_affinity(fmt_std):
    """Module with chapter_affinity excluding ch1 does not apply to chapter 1."""
    slot = EnrichedSlot("HOOK", "x", "t", "id", 3000, 1, [])
    ch = EnrichedChapter(1, "r", "wt", "th", [slot], 1, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        "ahjan",
        "gen_z_professionals",
        "standard_book",
        [ch],
        1,
        {},
    )
    depth_map = {
        "depth_modules": {
            "mechanism_depth": {
                "chapter_affinity": [2, 3],
                "sources": [{"type": "teacher_atom", "slot_types": ["REFLECTION"]}],
                "target_words_per_chapter": [300, 600],
            }
        },
        "topic_overrides": {"anxiety": {"depth_priority_early": ["mechanism_depth"]}},
    }
    out = apply_depth_pass(book, depth_map, repo_root=_repo_root())
    assert not any("MECHANISM_DEPTH" in s.slot_type for s in out.chapters[0].slots)


def test_depth_pass_respects_topic_restriction(fmt_std):
    """witnessing_presence restricted to grief does not load for anxiety."""
    slot = EnrichedSlot("HOOK", "x", "t", "id", 3000, 1, [])
    ch = EnrichedChapter(1, "r", "wt", "th", [slot], 1, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        "ahjan",
        "gen_z_professionals",
        "standard_book",
        [ch],
        1,
        {},
    )
    depth_map = {
        "depth_modules": {
            "witnessing_presence": {
                "chapter_affinity": [1, 2],
                "topic_restriction": ["grief", "depression"],
                "sources": [{"type": "teacher_atom", "slot_types": ["PERMISSION"]}],
                "target_words_per_chapter": [200, 500],
            }
        },
        "topic_overrides": {"anxiety": {"depth_priority_early": ["witnessing_presence"]}},
    }
    out = apply_depth_pass(book, depth_map, repo_root=_repo_root())
    assert not any("WITNESSING" in s.slot_type for s in out.chapters[0].slots)


def test_depth_pass_uses_alternate_variants(fmt_std):
    """Registry depth path prefers F2+ variants over F1."""
    from phoenix_v4.planning.enrichment_select import _load_depth_content

    text = _load_depth_content(
        {
            "type": "registry_variant",
            "section_types": ["HOOK"],
            "variant_preference": ["F2", "F3", "F4"],
        },
        topic="anxiety",
        teacher_id=None,
        persona_id="gen_z_professionals",
        chapter_number=1,
        seed="depth:anxiety:1:recognition_depth",
        repo_root=_repo_root(),
    )
    assert text
    reg = __import__(
        "phoenix_v4.planning.registry_resolver", fromlist=["load_registry"]
    ).load_registry("anxiety")
    f1 = reg["sections"]["chapter_01"]["sections"]["section_01"]["variants"][0]["content"]
    assert text.strip() != f1.strip()


def test_depth_pass_logs_audit(fmt_std):
    slot = EnrichedSlot("HOOK", "short", "t", "id", 2500, 1, [])
    ch = EnrichedChapter(1, "r", "wt", "th", [slot], 1, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        "ahjan",
        "gen_z_professionals",
        "standard_book",
        [ch],
        1,
        {},
    )
    import yaml

    depth_map = yaml.safe_load(
        (_repo_root() / "config" / "depth" / "depth_module_map.yaml").read_text(encoding="utf-8")
    )
    out = apply_depth_pass(book, depth_map, repo_root=_repo_root())
    entries = out.enrichment_audit["depth_modules_added"]
    assert entries
    assert all("chapter" in e and "module" in e and "words_added" in e for e in entries)


def test_depth_pass_stops_at_target(fmt_std):
    """Truncates a long block so added words do not exceed deficit cap for one chunk."""
    long_text = "word " * 500
    slot = EnrichedSlot("HOOK", long_text, "t", "id", 600, 400, [])
    ch = EnrichedChapter(1, "r", "wt", "th", [slot], 400, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        "ahjan",
        "gen_z_professionals",
        "standard_book",
        [ch],
        400,
        {},
    )
    depth_map = {
        "depth_modules": {
            "recognition_depth": {
                "chapter_affinity": "all",
                "sources": [{"type": "teacher_atom", "slot_types": ["HOOK"]}],
                "target_words_per_chapter": [200, 120],
            }
        },
        "topic_overrides": {"anxiety": {"depth_priority_early": ["recognition_depth"]}},
    }
    out = apply_depth_pass(book, depth_map, repo_root=_repo_root())
    depth_slots = [s for s in out.chapters[0].slots if s.slot_type.startswith("DEPTH_")]
    assert depth_slots
    assert depth_slots[0].actual_words <= 120


def test_depth_pass_banned_chapters_grief(fmt_std):
    """banned_chapters blocks practice_scaffold in listed chapters."""
    slot = EnrichedSlot("HOOK", "x", "t", "id", 3000, 1, [])
    ch = EnrichedChapter(3, "r", "wt", "th", [slot], 1, {})
    book = EnrichedBook(
        1,
        "enrichment_select",
        "grief",
        "ahjan",
        "gen_z_professionals",
        "standard_book",
        [ch],
        1,
        {},
    )
    depth_map = {
        "depth_modules": {
            "practice_scaffold": {
                "chapter_affinity": "all",
                "sources": [{"type": "component_template", "pool": "bridge"}],
                "target_words_per_chapter": [200, 400],
            }
        },
        "topic_overrides": {
            "grief": {
                "depth_priority_mid": ["practice_scaffold"],
                "banned_chapters": {"practice_scaffold": [1, 2, 3, 4, 5, 6, 7, 8]},
            }
        },
    }
    out = apply_depth_pass(book, depth_map, repo_root=_repo_root())
    assert not any("practice_scaffold" in s.source for s in out.chapters[0].slots)
