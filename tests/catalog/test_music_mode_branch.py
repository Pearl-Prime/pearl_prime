"""Music-mode catalog branch: registry resolution + BookSpec filtering."""
from __future__ import annotations

import logging
from pathlib import Path

import pytest

from phoenix_v4.planning.catalog_planner import BookSpec, CatalogPlanner
from scripts.catalog import music_mode_branch as mmb


REPO_ROOT = Path(__file__).resolve().parents[2]


def test_resolve_music_brand_is_music_only():
    assert mmb.resolve_catalog_branch("_template_music", repo_root=REPO_ROOT) is mmb.CatalogBranch.MUSIC_ONLY


def test_resolve_path_x_brand_is_standard():
    assert mmb.resolve_catalog_branch("stillness_press", repo_root=REPO_ROOT) is mmb.CatalogBranch.STANDARD


def test_overlap_music_precedence_logs_warning(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.WARNING)

    def fake_music(_root: Path) -> set[str]:
        return {"collision_brand"}

    def fake_path_x(_root: Path) -> set[str]:
        return {"collision_brand"}

    monkeypatch.setattr(mmb, "load_music_brand_ids", fake_music)
    monkeypatch.setattr(mmb, "load_path_x_brand_ids", fake_path_x)

    assert mmb.resolve_catalog_branch("collision_brand", repo_root=REPO_ROOT) is mmb.CatalogBranch.MUSIC_ONLY
    assert any("music_mode precedence" in r.getMessage() for r in caplog.records)


def test_filter_drops_teacher_mode_and_composite_tags():
    specs = [
        BookSpec(
            topic_id="grief",
            persona_id="nyc_exec",
            series_id=None,
            installment_number=None,
            teacher_id="default_teacher",
            brand_id="_template_music",
            angle_id="grief_general",
            domain_id="grief_cluster",
            seed="a",
            teacher_mode=False,
        ),
        BookSpec(
            topic_id="shame",
            persona_id="nyc_exec",
            series_id=None,
            installment_number=None,
            teacher_id="t1",
            brand_id="_template_music",
            angle_id="shame_general",
            domain_id="shame_cluster",
            seed="b",
            teacher_mode=True,
        ),
    ]
    filtered = mmb.filter_to_music_mode_book_specs(specs)
    assert len(filtered) == 1
    assert filtered[0].seed == "a"


def test_filter_dict_rows_teacher_mode_string():
    rows = [
        {"brand_id": "x", "teacher_mode": "false"},
        {"brand_id": "x", "teacher_mode": "true"},
    ]
    assert len(mmb.filter_catalog_entry_dicts_music_mode(rows)) == 1


def test_generate_for_brand_music_is_all_non_teacher_mode():
    planner = CatalogPlanner()
    specs = planner.generate_for_brand("_template_music", 12, seed="music_seed", repo_root=REPO_ROOT)
    assert specs
    assert all(not s.teacher_mode for s in specs)
    assert all(s.brand_id == "_template_music" for s in specs)


def test_generate_for_brand_path_x_matches_produce_wave():
    planner = CatalogPlanner()
    brand_id = "stillness_press"
    n = 8
    seed = "parity_seed"
    a = planner.generate_for_brand(brand_id, n, seed=seed, repo_root=REPO_ROOT)
    b = planner.produce_wave(n, seed=seed, brand_id=brand_id, teacher_mode=False)
    assert [x.to_dict() for x in a] == [x.to_dict() for x in b]


def test_generate_for_brand_topics_match_master_arc_inventory():
    planner = CatalogPlanner()
    specs = planner.generate_for_brand("stillness_press", 16, seed="arc_alignment", repo_root=REPO_ROOT)
    arc_pairs = set()
    for path in (REPO_ROOT / "config" / "source_of_truth" / "master_arcs").glob("*.yaml"):
        parts = path.stem.split("__")
        if len(parts) < 4:
            continue
        arc_pairs.add(("__".join(parts[:-3]), parts[-3]))

    missing = [(s.persona_id, s.topic_id) for s in specs if (s.persona_id, s.topic_id) not in arc_pairs]
    assert not missing, f"generate_for_brand produced non-arc-backed pairs: {missing[:5]}"
