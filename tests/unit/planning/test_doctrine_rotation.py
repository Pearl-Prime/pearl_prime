"""Doctrine-per-chapter rotation — REFLECTION picker wiring (NEXT-2c)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import pytest

from phoenix_v4.planning import enrichment_select as es
from phoenix_v4.planning.beatmap_compile import Beatmap, BeatmapChapter, BeatmapSlot
from phoenix_v4.planning.doctrine_rotation import (
    DoctrineRotationError,
    normalize_doctrine_id,
    pick_doctrine_atom_by_id,
    resolve_chapter_doctrine_id,
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


def _twelve_chapter_beatmap(topic: str = "anxiety") -> Beatmap:
    chapters: List[BeatmapChapter] = []
    for n in range(1, 13):
        slot = BeatmapSlot(
            slot_type="REFLECTION",
            weight=1.0,
            target_words=200,
            somatic_section_index=4,
            atom_selection_criteria={},
            enrichment_hooks=[],
            emotional_temperature="neutral",
            is_required=True,
        )
        chapters.append(
            BeatmapChapter(
                number=n,
                role="body",
                working_title=f"Ch{n}",
                thesis="",
                phase="middle",
                target_word_count=200,
                slots=[slot],
                slot_definitions=["REFLECTION"],
            )
        )
    return Beatmap(
        schema_version=1,
        stage="compile",
        topic=topic,
        family_id="test",
        runtime_format="standard_book",
        total_target_words=2400,
        chapters=chapters,
        compile_audit={},
    )


# Expected gen_z × anxiety rotation (from doctrine_distribution_plan / twelve_shape plan)
EXPECTED_ANXIETY_12 = [
    "COMPOSITE_DOCTRINE v03",
    "COMPOSITE_DOCTRINE v01",
    "COMPOSITE_DOCTRINE v05",
    "COMPOSITE_DOCTRINE v04",
    "COMPOSITE_DOCTRINE v02",
    "COMPOSITE_DOCTRINE v06",
    "COMPOSITE_DOCTRINE v07",
    "COMPOSITE_DOCTRINE v08",
    "COMPOSITE_DOCTRINE v09",
    "COMPOSITE_DOCTRINE v10",
    "COMPOSITE_DOCTRINE v11",
    "COMPOSITE_DOCTRINE v15",
]


def test_normalize_doctrine_id_strips_suffix() -> None:
    assert normalize_doctrine_id("COMPOSITE_DOCTRINE v03_pure") == "COMPOSITE_DOCTRINE v03"


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
    for ch0, expected in enumerate(EXPECTED_ANXIETY_12):
        got = resolve_chapter_doctrine_id(
            "anxiety",
            ch0,
            spine_context=spine,
            book_frame="somatic_first",
            repo_root=tmp_path,
        )
        assert got == expected, f"ch{ch0 + 1}: expected {expected}, got {got}"


def test_pick_doctrine_atom_blocks_repeat() -> None:
    pool = [_reflection_atom(1, "a"), _reflection_atom(2, "b")]
    used = {"COMPOSITE_DOCTRINE v01"}
    with pytest.raises(DoctrineRotationError):
        pick_doctrine_atom_by_id(pool, "COMPOSITE_DOCTRINE v01", used_doctrine_ids=used)


def test_twelve_chapter_gen_z_anxiety_distinct_doctrines(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """12-chapter gen_z×anxiety: 12 distinct doctrines in planned order, zero repeats."""
    topic = "anxiety"
    variant_nums = [3, 1, 5, 4, 2, 6, 7, 8, 9, 10, 11, 15]
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
        assert "composite_doctrine" in slot.source, f"ch{ch.number} expected composite, got {slot.source}"
        aid = slot.source_id or ""
        picked_ids.append(normalize_doctrine_id(aid))

    assert picked_ids == EXPECTED_ANXIETY_12
    assert len(set(picked_ids)) == 12, f"repeat detected: {picked_ids}"

    print("doctrine_rotation_proof:", picked_ids)
