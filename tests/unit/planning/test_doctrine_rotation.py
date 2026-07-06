"""Doctrine-per-chapter rotation — REFLECTION picker wiring (NEXT-2c)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from phoenix_v4.planning import enrichment_select as es
from phoenix_v4.planning.beatmap_compile import Beatmap, BeatmapChapter, BeatmapSlot
from phoenix_v4.planning.doctrine_rotation import (
    normalize_doctrine_id,
    pick_doctrine_atom_by_id,
    resolve_chapter_doctrine_id,
    spacing_window,
)
from phoenix_v4.planning.enrichment_select import EnrichmentRequest, select_enrichment


def _reflection_atom(vnum: int, body: str) -> dict:
    return {
        "atom_id": f"COMPOSITE_DOCTRINE v{vnum:02d}",
        "content": body,
        "metadata": {},
    }


def _write_reflection_bank(path: Path, variants: List[tuple[int, str]]) -> None:
    lines: List[str] = []
    for vnum, body in variants:
        lines.append(f"## COMPOSITE_DOCTRINE v{vnum:02d}")
        lines.append("---")
        lines.append("---")
        lines.append(body)
        lines.append("---")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def _twelve_chapter_beatmap(
    topic: str = "anxiety",
    *,
    reflections_per_chapter: int = 1,
    runtime_format: str = "standard_book",
) -> Beatmap:
    chapters: List[BeatmapChapter] = []
    for n in range(1, 13):
        slots = [
            BeatmapSlot(
                slot_type="REFLECTION",
                weight=1.0,
                target_words=200,
                somatic_section_index=4,
                atom_selection_criteria={},
                enrichment_hooks=[],
                emotional_temperature="neutral",
                is_required=True,
            )
            for _ in range(reflections_per_chapter)
        ]
        chapters.append(
            BeatmapChapter(
                number=n,
                role="body",
                working_title=f"Ch{n}",
                thesis="",
                phase="middle",
                target_word_count=200 * reflections_per_chapter,
                slots=slots,
                slot_definitions=["REFLECTION"] * reflections_per_chapter,
            )
        )
    return Beatmap(
        schema_version=1,
        stage="compile",
        topic=topic,
        family_id="test",
        runtime_format=runtime_format,
        total_target_words=2400 * reflections_per_chapter,
        chapters=chapters,
        compile_audit={},
    )


# gen_z × anxiety 12-shape continuity plan (bounded v01–v05 pool per doctrine_rotation).
TWELVE_SHAPE_PLAN_ANXIETY = [
    "COMPOSITE_DOCTRINE v03",
    "COMPOSITE_DOCTRINE v01",
    "COMPOSITE_DOCTRINE v05",
    "COMPOSITE_DOCTRINE v04",
    "COMPOSITE_DOCTRINE v02",
    "COMPOSITE_DOCTRINE v03",
    "COMPOSITE_DOCTRINE v01",
    "COMPOSITE_DOCTRINE v05",
    "COMPOSITE_DOCTRINE v04",
    "COMPOSITE_DOCTRINE v02",
    "COMPOSITE_DOCTRINE v03",
    "COMPOSITE_DOCTRINE v01",
]

# Bounded-reuse config sequence (doctrine_rotation.yaml → topic_sequences.anxiety):
# the 5 authored variants (v03,v01,v05,v04,v02) cycled every 5 chapters. Each recurs
# exactly 5 chapters apart (window = min(5,12) = 5) and never in adjacent chapters.
EXPECTED_ANXIETY_12_BOUNDED = [
    "COMPOSITE_DOCTRINE v03",
    "COMPOSITE_DOCTRINE v01",
    "COMPOSITE_DOCTRINE v05",
    "COMPOSITE_DOCTRINE v04",
    "COMPOSITE_DOCTRINE v02",
    "COMPOSITE_DOCTRINE v03",
    "COMPOSITE_DOCTRINE v01",
    "COMPOSITE_DOCTRINE v05",
    "COMPOSITE_DOCTRINE v04",
    "COMPOSITE_DOCTRINE v02",
    "COMPOSITE_DOCTRINE v03",
    "COMPOSITE_DOCTRINE v01",
]

# The 5 authored anxiety REFLECTION variants actually present in the bank (v01–v05).
ANXIETY_POOL_VARIANTS = [3, 1, 5, 4, 2]


def test_normalize_doctrine_id_preserves_pure_suffix() -> None:
    assert normalize_doctrine_id("COMPOSITE_DOCTRINE v03_pure") == "COMPOSITE_DOCTRINE v03_pure"
    assert normalize_doctrine_id("COMPOSITE_DOCTRINE v03") == "COMPOSITE_DOCTRINE v03"


def test_spacing_window_formula() -> None:
    """window = min(pool_size, chapter_count), floored at 1; widens as the pool grows."""
    assert spacing_window(5, 12) == 5    # small pool → window == pool size
    assert spacing_window(12, 12) == 12  # pool == chapters → strict no-repeat
    assert spacing_window(20, 12) == 12  # pool grew past chapters → widen to chapters
    assert spacing_window(1, 12) == 1    # degenerate pool
    assert spacing_window(0, 0) == 1     # never below 1


def test_resolve_from_twelve_shape_plan(tmp_path: Path) -> None:
    plan_dir = tmp_path / "config" / "source_of_truth" / "twelve_shape_chapter_plans"
    plan_dir.mkdir(parents=True)
    (plan_dir / "gen_z_professionals_anxiety.yaml").write_text(
        (Path(es.REPO_ROOT) / "config" / "source_of_truth" / "twelve_shape_chapter_plans" / "gen_z_professionals_anxiety.yaml").read_text(),
        encoding="utf-8",
    )
    rot_cfg = tmp_path / "config" / "source_of_truth" / "doctrine_rotation.yaml"
    rot_cfg.parent.mkdir(parents=True, exist_ok=True)
    rot_cfg.write_text(
        (Path(es.REPO_ROOT) / "config" / "source_of_truth" / "doctrine_rotation.yaml").read_text(),
        encoding="utf-8",
    )
    from phoenix_v4.planning.chapter_object_continuity import load_chapter_continuity_plan

    plan = load_chapter_continuity_plan("gen_z_professionals", "anxiety", tmp_path)
    spine = {"chapter_continuity_plan": plan, "twelve_shape_continuity": True}
    for ch0, expected in enumerate(TWELVE_SHAPE_PLAN_ANXIETY):
        got = resolve_chapter_doctrine_id(
            "anxiety",
            ch0,
            spine_context=spine,
            book_frame="somatic_first",
            repo_root=tmp_path,
        )
        assert got == expected, f"ch{ch0 + 1}: expected {expected}, got {got}"


def test_pick_doctrine_atom_blocks_adjacent_repeat() -> None:
    """Bounded reuse: an ADJACENT repeat is never assigned — degrade to LRU, no crash.

    The prior chapter used v01; asking for v01 again must NOT return v01 and must NOT
    raise (fail-safe) — it degrades to the least-recently-used pool atom (v02, unused).
    """
    pool = [_reflection_atom(1, "a"), _reflection_atom(2, "b")]
    atom = pick_doctrine_atom_by_id(
        pool,
        "COMPOSITE_DOCTRINE v01",
        recent_doctrine_ids=["COMPOSITE_DOCTRINE v01"],  # prior (adjacent) chapter
        chapter_count=2,
    )
    assert atom is not None  # never crashes / returns None on a non-empty pool
    assert normalize_doctrine_id(atom["atom_id"]) == "COMPOSITE_DOCTRINE v02"


def test_pick_doctrine_atom_allows_spaced_reuse() -> None:
    """Bounded reuse: a repeat AT OR BEYOND the spacing window is allowed.

    Pool of 5 variants over 12 chapters → window = min(5, 12) = 5. A v01 last used
    5 chapters ago (gap == window) may be reassigned.
    """
    pool = [_reflection_atom(v, f"body{v}") for v in (1, 2, 3, 4, 5)]
    # v01 used at the oldest of 5 prior chapters → exactly `window` chapters back.
    recent = [
        "COMPOSITE_DOCTRINE v01",
        "COMPOSITE_DOCTRINE v02",
        "COMPOSITE_DOCTRINE v03",
        "COMPOSITE_DOCTRINE v04",
        "COMPOSITE_DOCTRINE v05",
    ]
    atom = pick_doctrine_atom_by_id(
        pool,
        "COMPOSITE_DOCTRINE v01",
        recent_doctrine_ids=recent,
        chapter_count=12,
    )
    assert atom is not None
    assert normalize_doctrine_id(atom["atom_id"]) == "COMPOSITE_DOCTRINE v01"


def test_pick_doctrine_atom_blocks_within_window_repeat() -> None:
    """A repeat CLOSER than the spacing window is blocked → LRU fallback, no crash."""
    pool = [_reflection_atom(v, f"body{v}") for v in (1, 2, 3, 4, 5)]
    # window = 5; v05 was used 2 chapters ago (gap 2 < 5) → must not be reassigned.
    recent = [
        "COMPOSITE_DOCTRINE v01",
        "COMPOSITE_DOCTRINE v02",
        "COMPOSITE_DOCTRINE v03",
        "COMPOSITE_DOCTRINE v05",
        "COMPOSITE_DOCTRINE v04",
    ]
    atom = pick_doctrine_atom_by_id(
        pool,
        "COMPOSITE_DOCTRINE v05",
        recent_doctrine_ids=recent,
        chapter_count=12,
    )
    assert atom is not None
    assert normalize_doctrine_id(atom["atom_id"]) != "COMPOSITE_DOCTRINE v05"


def test_pick_doctrine_atom_missing_variant_degrades_to_lru() -> None:
    """Fail-safe: an assigned variant absent from the pool degrades to LRU, never None."""
    pool = [_reflection_atom(v, f"body{v}") for v in (1, 2, 3, 4, 5)]
    atom = pick_doctrine_atom_by_id(
        pool,
        "COMPOSITE_DOCTRINE v15",  # not in the pool
        recent_doctrine_ids=["COMPOSITE_DOCTRINE v01"],
        chapter_count=12,
    )
    assert atom is not None
    assert normalize_doctrine_id(atom["atom_id"]) != "COMPOSITE_DOCTRINE v01"  # LRU, not adjacent


def test_pick_doctrine_atom_allows_intra_chapter_repick() -> None:
    """Multi-REFLECTION chapters resolve the SAME doctrine for each slot — allowed.

    doctrine_distribution_plan rule 1: one doctrine per chapter, shared across all
    REFLECTION slots. Passing current_chapter_doctrine_id lets the guard tell an
    intra-chapter re-pick (allowed) apart from a cross-chapter repeat (blocked).
    """
    pool = [_reflection_atom(3, "b"), _reflection_atom(1, "a")]
    used = {"COMPOSITE_DOCTRINE v03"}  # slot 1 of this chapter already stored v03
    atom = pick_doctrine_atom_by_id(
        pool,
        "COMPOSITE_DOCTRINE v03",
        used_doctrine_ids=used,
        current_chapter_doctrine_id="COMPOSITE_DOCTRINE v03",
    )
    assert atom is not None
    assert normalize_doctrine_id(atom["atom_id"]) == "COMPOSITE_DOCTRINE v03"


def test_pick_doctrine_atom_legacy_set_is_conservative() -> None:
    """Backward-compat: a legacy unordered `used_doctrine_ids` set (no recency) is
    treated conservatively — every prior id counts as within-window, so a repeat
    degrades to LRU rather than being reassigned (and still never raises)."""
    pool = [_reflection_atom(1, "a"), _reflection_atom(3, "b")]
    atom = pick_doctrine_atom_by_id(
        pool,
        "COMPOSITE_DOCTRINE v01",  # prior chapter used v01
        used_doctrine_ids={"COMPOSITE_DOCTRINE v01"},
        current_chapter_doctrine_id="COMPOSITE_DOCTRINE v03",  # this chapter is v03
    )
    assert atom is not None
    assert normalize_doctrine_id(atom["atom_id"]) == "COMPOSITE_DOCTRINE v03"


def _stage_anxiety_rotation_fixtures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Copy the real anxiety rotation config + 12-shape plan + a REFLECTION bank into tmp.

    The REFLECTION bank holds only the 5 authored variants (v01–v05) — matching the
    real SOURCE_OF_TRUTH bank — so the build exercises bounded reuse over a pool that
    is smaller than the 12-chapter book.
    """
    topic = "anxiety"
    variant_nums = ANXIETY_POOL_VARIANTS  # [3, 1, 5, 4, 2] → the 5 real v01–v05 atoms
    bodies = [(v, f"Doctrine body for variant v{v:02d} with enough words to pass gate.") for v in variant_nums]
    _write_reflection_bank(
        tmp_path / "SOURCE_OF_TRUTH" / "composite_doctrine" / topic / "REFLECTION" / "CANONICAL.txt",
        bodies,
    )
    rot_src = Path(es.REPO_ROOT) / "config" / "source_of_truth" / "doctrine_rotation.yaml"
    rot_dst = tmp_path / "config" / "source_of_truth" / "doctrine_rotation.yaml"
    rot_dst.parent.mkdir(parents=True, exist_ok=True)
    rot_dst.write_text(rot_src.read_text(encoding="utf-8"), encoding="utf-8")
    plan_src = (
        Path(es.REPO_ROOT)
        / "config"
        / "source_of_truth"
        / "twelve_shape_chapter_plans"
        / "gen_z_professionals_anxiety.yaml"
    )
    plan_dst = tmp_path / "config" / "source_of_truth" / "twelve_shape_chapter_plans" / "gen_z_professionals_anxiety.yaml"
    plan_dst.parent.mkdir(parents=True, exist_ok=True)
    plan_dst.write_text(plan_src.read_text(encoding="utf-8"), encoding="utf-8")

    monkeypatch.setattr(es, "load_registry", lambda _t: {"sections": {}})
    monkeypatch.setattr(
        es,
        "_load_persona_atoms",
        lambda *_a, **_k: {
            "REFLECTION": [
                {"atom_id": f"p{i}", "content": f"Persona fallback {i} with enough words here.", "metadata": {}}
                for i in range(3)
            ],
        },
    )


def test_twelve_chapter_gen_z_anxiety_bounded_reuse_fills_all(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """12-chapter gen_z×anxiety over a 5-variant pool: EVERY chapter gets a doctrine.

    Bounded reuse — the 5 authored variants (v01–v05) cover all 12 chapters via a
    spaced cycle. Previously chapters 6–12 (assigned v06–v15, absent from the pool)
    were silently dropped. Now: no silent drops, no crash, spaced repeats only.
    """
    topic = "anxiety"
    _stage_anxiety_rotation_fixtures(tmp_path, monkeypatch)

    req = EnrichmentRequest(
        topic_id=topic,
        persona_id="gen_z_professionals",
        teacher_id=None,
        beatmap=_twelve_chapter_beatmap(topic),
        seed="doctrine_rotation_proof",
        publishable_book=False,
        spine_context={"book_frame": "somatic_first"},
    )
    book = select_enrichment(req, repo_root=tmp_path)

    picked_ids: List[str] = []
    for ch in book.chapters:
        slot = ch.slots[0]
        # No silent drops: EVERY chapter's REFLECTION slot carries composite doctrine.
        assert "composite_doctrine" in slot.source, f"ch{ch.number} expected composite, got {slot.source}"
        aid = slot.source_id or ""
        picked_ids.append(normalize_doctrine_id(aid))

    # All 12 chapters filled from the 5-variant pool, in the spaced-cycle order.
    assert len(picked_ids) == 12
    assert picked_ids == EXPECTED_ANXIETY_12_BOUNDED
    # Every assigned variant exists in the 5-variant pool (no phantom v06–v15).
    pool_ids = {f"COMPOSITE_DOCTRINE v{v:02d}" for v in ANXIETY_POOL_VARIANTS}
    assert set(picked_ids) <= pool_ids, f"assigned a variant outside the pool: {set(picked_ids) - pool_ids}"
    # Bounded reuse: 5 distinct lessons, and no lesson repeats in adjacent chapters.
    assert len(set(picked_ids)) == len(ANXIETY_POOL_VARIANTS)
    assert all(a != b for a, b in zip(picked_ids, picked_ids[1:])), f"adjacent repeat: {picked_ids}"


def test_multi_reflection_chapter_no_crash_shares_doctrine(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression (multi-reflection crash, #4672/#4673 follow-up) under bounded reuse.

    A deep/standard template (deep_book_6h) has TWO REFLECTION slots per chapter.
    This asserts:

      1. the 12-chapter build completes (no crash, no DoctrineRotationError);
      2. both REFLECTION slots in a chapter SHARE that chapter's one doctrine
         (doctrine_distribution_plan rule 1);
      3. every chapter is filled from the 5-variant pool via the spaced cycle, and
         no lesson repeats in adjacent chapters (bounded reuse).

    The compact (1-reflection) shape is covered by
    ``test_twelve_chapter_gen_z_anxiety_bounded_reuse_fills_all``.
    """
    topic = "anxiety"
    _stage_anxiety_rotation_fixtures(tmp_path, monkeypatch)

    req = EnrichmentRequest(
        topic_id=topic,
        persona_id="gen_z_professionals",
        teacher_id=None,
        beatmap=_twelve_chapter_beatmap(
            topic, reflections_per_chapter=2, runtime_format="deep_book_6h",
        ),
        seed="multi_reflection_regression",
        publishable_book=False,
        spine_context={"book_frame": "somatic_first"},
    )
    # Must NOT raise DoctrineRotationError (the pre-fix crash).
    book = select_enrichment(req, repo_root=tmp_path)

    assert len(book.chapters) == 12, "expected a completed 12-chapter build"

    chapter_doctrines: List[str] = []
    for ch in book.chapters:
        slot_ids = [
            normalize_doctrine_id(s.source_id or "")
            for s in ch.slots
            if "composite_doctrine" in s.source
        ]
        assert slot_ids, f"ch{ch.number}: expected composite doctrine in REFLECTION slots"
        # (2) all REFLECTION slots in this chapter share ONE doctrine
        assert len(set(slot_ids)) == 1, (
            f"ch{ch.number}: REFLECTION slots must share one doctrine, got {slot_ids}"
        )
        chapter_doctrines.append(slot_ids[0])

    # planned spaced-cycle order, unchanged by the multi-slot shape
    assert chapter_doctrines == EXPECTED_ANXIETY_12_BOUNDED
    # (3) bounded reuse: every chapter filled from the 5-variant pool, no adjacent repeat
    pool_ids = {f"COMPOSITE_DOCTRINE v{v:02d}" for v in ANXIETY_POOL_VARIANTS}
    assert set(chapter_doctrines) <= pool_ids
    assert all(a != b for a, b in zip(chapter_doctrines, chapter_doctrines[1:])), (
        f"adjacent repeat: {chapter_doctrines}"
    )
