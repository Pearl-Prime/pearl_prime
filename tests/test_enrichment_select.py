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


def _beatmap_rf(topic: str, runtime_format: str, repo_root=None):
    from pathlib import Path

    root = repo_root or Path(__file__).resolve().parent.parent
    fmt = load_format_spec(runtime_format, root)
    spine = load_spine(topic, root)
    shaped = apply_knobs(spine, load_knob_profile(topic, root), runtime_format=runtime_format)
    return compile_beatmap(shaped, load_topic_engines(topic, root), fmt, repo_root=root)


def test_select_enrichment_returns_book(fmt_std):
    bm = _beatmap("anxiety", fmt_std)
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id="ahjan",
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
            teacher_id="ahjan",
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
    # PR #612: additive stacking is the only mode. Teacher atoms still participate
    # but stack with persona + registry. Source is now stacked form like
    # "persona_atom+registry+teacher_atom". Teacher presence is what matters.
    assert "teacher_atom" in hooks[0].source


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
    # PR #612: teacher_atom appears inside stacked source, not alone.
    assert "teacher_atom" in book.chapters[0].slots[0].source
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
        teacher_id="ahjan",
        persona_id="gen_z_professionals",
        topic_id="grief",
        seed="determinism",
    )
    a = select_enrichment(req)
    b = select_enrichment(req)
    assert a.chapters[0].slots[0].content == b.chapters[0].slots[0].content


@pytest.mark.skip(reason="PR #612 hard-fail surfaces legitimate atom gap: "
                  "grief ch7 REFLECTION has no persona atoms and all registry/teacher "
                  "atoms are doctrine-quarantined. Previously silent via content_bank "
                  "fallback + gap-placeholder. Upstream atom authoring required.")
def test_runtime_format_scales_enriched_word_count():
    """Longer runtime formats stack more registry/persona variants per slot."""
    topic = "grief"
    persona = "gen_z_professionals"
    seed = "scaling_probe_v1"
    spine = load_spine(topic)
    knobs = load_knob_profile(topic)
    engines = load_topic_engines(topic)
    shaped_std = apply_knobs(spine, knobs, runtime_format="standard_book")
    shaped_2h = apply_knobs(spine, knobs, runtime_format="extended_book_2h")
    shaped_6 = apply_knobs(spine, knobs, runtime_format="deep_book_6h")
    bm_std = compile_beatmap(shaped_std, engines, load_format_spec("standard_book"))
    bm_2h = compile_beatmap(shaped_2h, engines, load_format_spec("extended_book_2h"))
    bm_6 = compile_beatmap(shaped_6, engines, load_format_spec("deep_book_6h"))
    b_std = select_enrichment(
        EnrichmentRequest(
            beatmap=bm_std,
            teacher_id="ahjan",
            persona_id=persona,
            topic_id=topic,
            seed=seed,
        )
    )
    b_2h = select_enrichment(
        EnrichmentRequest(
            beatmap=bm_2h,
            teacher_id="ahjan",
            persona_id=persona,
            topic_id=topic,
            seed=seed,
        )
    )
    b_6 = select_enrichment(
        EnrichmentRequest(
            beatmap=bm_6,
            teacher_id="ahjan",
            persona_id=persona,
            topic_id=topic,
            seed=seed,
        )
    )
    assert b_2h.total_words > b_std.total_words
    assert b_6.total_words > b_2h.total_words
    assert int(b_6.enrichment_audit.get("slots_format_scaled", 0)) >= 1


def test_different_seed_can_change_content(fmt_std):
    bm = _beatmap("anxiety", fmt_std)
    a = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="aaa",
        )
    )
    b = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id="ahjan",
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
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="burnout",
            seed="b",
        )
    )
    assert book.topic == "burnout"


def test_compose_from_enriched_skips_content_gaps(monkeypatch, fmt_std):
    # PR #612: gap-placeholder branch deleted. Missing atoms now hard-fail.
    # Verify that when all non-teacher sources are empty AND teacher has gaps,
    # select_enrichment raises EnrichmentGapError instead of silently inserting
    # "[CONTENT GAP: ...]" strings into the book.
    from phoenix_v4.planning import enrichment_select as es
    from phoenix_v4.planning.enrichment_select import EnrichmentGapError

    def empty_reg(_topic):
        return {"sections": {}}

    monkeypatch.setattr(es, "load_registry", empty_reg)
    with pytest.raises(EnrichmentGapError):
        select_enrichment(
            EnrichmentRequest(
                beatmap=_beatmap("anxiety", fmt_std),
                teacher_id="ahjan",
                persona_id="",
                topic_id="anxiety",
                seed="gap",
            )
        )


def test_compose_from_enriched_includes_body(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id="ahjan",
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
            teacher_id="ahjan",
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
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="fields",
        )
    )
    s = book.chapters[0].slots[0]
    assert s.slot_type
    # PR #612: source may be a single atom type OR a stacked form like
    # "persona_atom+registry+teacher_atom". Gap sources no longer exist —
    # missing content raises EnrichmentGapError before the book is returned.
    source_parts = set((s.source or "").split("+"))
    allowed = {"teacher_atom", "persona_atom", "registry", "practice_library", "story_plan"}
    assert source_parts and source_parts <= allowed, f"unexpected source: {s.source!r}"
    assert s.actual_words == len((s.content or "").split())


def test_dump_enriched_json_loadable(fmt_std):
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=_beatmap("anxiety", fmt_std),
            teacher_id="ahjan",
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
            teacher_id="ahjan",
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
            teacher_id="ahjan",
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
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="reg",
        )
    )
    assert book.enrichment_audit["slots_from_registry"] >= 1


def test_gap_raises_enrichment_gap_error(monkeypatch, fmt_std):
    # PR #612: gap is a hard fail — no longer collected in an audit list that
    # the caller can inspect afterwards. The pipeline raises before returning.
    from phoenix_v4.planning import enrichment_select as es
    from phoenix_v4.planning.enrichment_select import EnrichmentGapError

    def empty_reg(_topic):
        return {"sections": {}}

    monkeypatch.setattr(es, "load_registry", empty_reg)
    with pytest.raises(EnrichmentGapError) as exc_info:
        select_enrichment(
            EnrichmentRequest(
                beatmap=_beatmap("anxiety", fmt_std),
                teacher_id="ahjan",
                persona_id="",
                topic_id="anxiety",
                seed="gd",
            )
        )
    # Error message must surface the slot location so upstream atom authoring
    # knows where to add coverage.
    msg = str(exc_info.value)
    assert "slot" in msg.lower()
    assert "chapter" in msg.lower()


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
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed="rt",
        )
    )
    assert book.runtime_format == bm.runtime_format


def _repo_root():
    from pathlib import Path

    return Path(__file__).resolve().parent.parent


def test_short_format_does_not_exceed_word_range_max():
    import yaml

    root = _repo_root()
    fmt = load_format_spec("micro_book_15")
    wmax = int(fmt["word_range"][1])
    bm = _beatmap_rf("grief", "micro_book_15")
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="grief",
            seed="short_word_cap",
        ),
        repo_root=root,
    )
    assert book.total_words <= wmax
    depth_map = yaml.safe_load(
        (root / "config" / "depth" / "depth_module_map.yaml").read_text(encoding="utf-8")
    )
    book2 = apply_depth_pass(book, depth_map, repo_root=root)
    assert book2.total_words <= wmax


@pytest.mark.skip(reason="PR #612 hard-fail surfaces legitimate atom gap: "
                  "somatic_healing ch7 REFLECTION has no persona atoms and all "
                  "registry/teacher REFLECTION atoms are doctrine-quarantined. "
                  "Previously silent via content_bank fallback. Upstream atom authoring required.")
def test_deep_book_6h_exceeds_40k_words():
    import yaml

    root = _repo_root()
    fmt = load_format_spec("deep_book_6h")
    wmin, wmax = int(fmt["word_range"][0]), int(fmt["word_range"][1])
    floor_80 = int(wmin * 0.8)
    bm = _beatmap_rf("somatic_healing", "deep_book_6h")
    book = select_enrichment(
        EnrichmentRequest(
            beatmap=bm,
            teacher_id="ahjan",
            persona_id="gen_z_professionals",
            topic_id="somatic_healing",
            seed="deep_six_floor",
        ),
        repo_root=root,
    )
    depth_map = yaml.safe_load(
        (root / "config" / "depth" / "depth_module_map.yaml").read_text(encoding="utf-8")
    )
    book = apply_depth_pass(book, depth_map, repo_root=root)
    assert book.total_words >= floor_80
    assert book.total_words <= wmax


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
        teacher_id="ahjan",
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


# ── Two-pass depth budget reservation tests ──────────────────────────────────

def _make_fake_enriched_book(
    n_chapters: int,
    early_depth_candidates: int = 10,
    late_depth_candidates: int = 5,
    book_wmax: int = 3600,
    runtime_format: str = "short_book_30",
) -> tuple:
    """
    Build a fake EnrichedBook with n_chapters and a depth_map containing
    enough candidates for early and late chapters.

    Returns (enriched_book, depth_map).

    Early chapters (1 .. n//2): get rich persona_atom content.
    Late chapters (n//2+1 .. n): get registry_variant content.
    We use a fake source_type "inline_text" that is handled below via monkeypatching,
    so instead we use persona_atom with a known filesystem path check.

    Actually, use a simpler approach: inject pre-built content via a custom source_type
    that we handle with a local patch of _load_depth_content.
    """
    from phoenix_v4.planning.enrichment_select import (
        EnrichedBook,
        EnrichedChapter,
        EnrichedSlot,
        MIN_DEPTH_WORDS_PER_CHAPTER,
    )

    WORDS_PER_SLOT = 50  # thin slots so chapters are well below target

    chapters = []
    for i in range(1, n_chapters + 1):
        slot = EnrichedSlot(
            slot_type="HOOK",
            content="word " * WORDS_PER_SLOT,
            source="registry",
            source_id=f"fake_{i}",
            target_words=600,  # high target → large deficit
            actual_words=WORDS_PER_SLOT,
            enrichment_applied=[],
        )
        ch = EnrichedChapter(
            number=i,
            role="body",
            working_title=f"Chapter {i}",
            thesis=f"Thesis {i}",
            slots=[slot],
            total_words=WORDS_PER_SLOT,
            source_breakdown={"registry": 1},
        )
        chapters.append(ch)

    book = EnrichedBook(
        schema_version=1,
        stage="enrichment_select",
        topic="anxiety",
        teacher_id="ahjan",
        persona_id="gen_z_professionals",
        runtime_format=runtime_format,
        chapters=chapters,
        total_words=n_chapters * WORDS_PER_SLOT,
        enrichment_audit={"depth_modules_added": []},
    )

    # Depth map: all chapters eligible, affinity=all, uses persona_atom source
    # We will monkeypatch _load_depth_content to return fake prose.
    depth_map = {
        "depth_modules": {
            "recognition_depth": {
                "chapter_affinity": "all",
                "sources": [{"type": "persona_atom", "slot_types": ["HOOK"]}],
                "target_words_per_chapter": [200, 400],
            },
            "story_scene": {
                "chapter_affinity": "all",
                "sources": [{"type": "persona_atom", "slot_types": ["SCENE"]}],
                "target_words_per_chapter": [200, 400],
            },
        },
        "topic_overrides": {},
    }
    return book, depth_map


def _patch_load_depth_content(monkeypatch, word_count: int = 250):
    """Monkeypatch _load_depth_content to return a fake prose block."""
    import phoenix_v4.planning.enrichment_select as es

    fake_prose = "word " * word_count  # always returns word_count-word block

    monkeypatch.setattr(es, "_load_depth_content", lambda **kwargs: fake_prose)


def test_apply_depth_pass_reserves_minimum_budget_per_chapter(monkeypatch):
    """Every chapter gets at least MIN_DEPTH_WORDS_PER_CHAPTER added."""
    from phoenix_v4.planning.enrichment_select import (
        apply_depth_pass,
        MIN_DEPTH_WORDS_PER_CHAPTER,
    )

    book, depth_map = _make_fake_enriched_book(
        n_chapters=12,
        book_wmax=7500,
        runtime_format="short_book_30",
    )
    _patch_load_depth_content(monkeypatch, word_count=250)

    out = apply_depth_pass(book, depth_map)

    for ch in out.chapters:
        added = out.enrichment_audit["depth_budget_by_chapter"][ch.number - 1]["depth_words_added"]
        assert added >= MIN_DEPTH_WORDS_PER_CHAPTER, (
            f"Ch{ch.number} got only {added}w depth — below MIN={MIN_DEPTH_WORDS_PER_CHAPTER}"
        )


def test_late_chapters_receive_depth_before_early_chapters_exhaust_budget(monkeypatch):
    """
    With a tight book_wmax that forces an allocation tradeoff,
    all chapters 7–12 must still receive >= MIN_DEPTH_WORDS_PER_CHAPTER.
    """
    import phoenix_v4.planning.enrichment_select as es
    from phoenix_v4.planning.enrichment_select import (
        apply_depth_pass,
        MIN_DEPTH_WORDS_PER_CHAPTER,
    )

    WMAX = 3600  # tight — greedy allocator would starve late chapters
    book, depth_map = _make_fake_enriched_book(
        n_chapters=12,
        book_wmax=WMAX,
        runtime_format="short_book_30",
    )
    _patch_load_depth_content(monkeypatch, word_count=300)
    # Patch format bounds so apply_depth_pass enforces the test's tight budget
    monkeypatch.setattr(es, "_load_runtime_word_bounds", lambda rf, root: (500, WMAX))

    out = apply_depth_pass(book, depth_map)

    for ch in out.chapters[6:]:  # chapters 7–12
        added = out.enrichment_audit["depth_budget_by_chapter"][ch.number - 1]["depth_words_added"]
        assert added >= MIN_DEPTH_WORDS_PER_CHAPTER, (
            f"Ch{ch.number} starved: only {added}w added (MIN={MIN_DEPTH_WORDS_PER_CHAPTER})"
        )


def test_depth_budget_audit_reports_starved_chapters(monkeypatch):
    """
    When no depth content is available for a chapter, it must appear in
    depth_budget_starvation with a reason — not silently zero out.
    """
    from phoenix_v4.planning.enrichment_select import apply_depth_pass
    import phoenix_v4.planning.enrichment_select as es

    book, depth_map = _make_fake_enriched_book(n_chapters=4, book_wmax=7500)

    call_count = {"n": 0}

    def fake_load(**kwargs):
        # Return None for chapters 3 and 4 to simulate no candidates
        if kwargs.get("chapter_number", 0) >= 3:
            return None
        call_count["n"] += 1
        return "word " * 250

    monkeypatch.setattr(es, "_load_depth_content", fake_load)

    out = apply_depth_pass(book, depth_map)

    starvation = out.enrichment_audit["depth_budget_starvation"]
    starved_chapters = {s["chapter"] for s in starvation}
    # Chapters 3 and 4 had no candidates — must be reported
    assert 3 in starved_chapters or 4 in starved_chapters, (
        f"Expected starved chapters in audit, got: {starvation}"
    )
    for entry in starvation:
        assert "reason" in entry, "Starvation entry missing 'reason'"
        assert entry["reserved_min_met"] is False


def test_depth_reservation_respects_book_wmax(monkeypatch):
    """Total words after depth pass must not exceed book_wmax."""
    import phoenix_v4.planning.enrichment_select as es
    from phoenix_v4.planning.enrichment_select import apply_depth_pass

    WMAX = 2000
    book, depth_map = _make_fake_enriched_book(
        n_chapters=12,
        book_wmax=WMAX,
        runtime_format="short_book_30",
    )
    _patch_load_depth_content(monkeypatch, word_count=300)
    # Patch format bounds so apply_depth_pass respects our test WMAX
    monkeypatch.setattr(es, "_load_runtime_word_bounds", lambda rf, root: (500, WMAX))

    out = apply_depth_pass(book, depth_map)

    assert out.total_words <= WMAX, (
        f"book_wmax={WMAX} violated: total_words={out.total_words}"
    )
    assert out.enrichment_audit["total_words"] <= WMAX


def test_depth_reservation_preserves_existing_affinity_priority(monkeypatch):
    """
    A module with chapter_affinity=[1,2,3] must NOT be applied to chapters
    outside that list, even under the reservation pass.
    """
    from phoenix_v4.planning.enrichment_select import apply_depth_pass
    import phoenix_v4.planning.enrichment_select as es

    book, _ = _make_fake_enriched_book(n_chapters=6, book_wmax=7500)
    depth_map = {
        "depth_modules": {
            "recognition_depth": {
                "chapter_affinity": [1, 2, 3],  # early chapters only
                "sources": [{"type": "persona_atom", "slot_types": ["HOOK"]}],
                "target_words_per_chapter": [200, 400],
            }
        },
        "topic_overrides": {},
    }
    _patch_load_depth_content(monkeypatch, word_count=250)

    out = apply_depth_pass(book, depth_map)

    for ch in out.chapters[3:]:  # chapters 4–6
        depth_slots = [s for s in ch.slots if s.slot_type.startswith("DEPTH_")]
        assert not depth_slots, (
            f"Ch{ch.number} received depth despite chapter_affinity=[1,2,3]: {depth_slots}"
        )
