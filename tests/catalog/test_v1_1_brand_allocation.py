"""Tests for PR #1037 Path X allocation loader + high-confidence catalog builder."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
REAL_TSV = (
    REPO_ROOT
    / "artifacts"
    / "qa"
    / "worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv"
)


def test_loader_full_tsv_dimensions():
    if not REAL_TSV.exists():
        pytest.skip("PR #1037 allocation TSV not present in checkout")
    from scripts.catalog.v1_1_brand_allocation_loader import (
        load_v1_1_brand_allocation_plan,
        filter_v1_0_cells,
        summarize_by_locale,
    )

    plan = load_v1_1_brand_allocation_plan(REAL_TSV)
    assert len(plan) == 296
    brands = {b for (b, _l, _s) in plan}
    assert len(brands) == 37

    v0 = filter_v1_0_cells(plan)
    assert len(v0) == 96
    brands0 = {b for (b, _l, _s) in v0}
    assert len(brands0) == 12
    assert brands0 < brands

    by_loc = summarize_by_locale(plan)
    assert by_loc == {"en_US": 74, "ja_JP": 74, "zh_CN": 74, "zh_TW": 74}
    by_v0 = summarize_by_locale(v0)
    assert by_v0 == {"en_US": 24, "ja_JP": 24, "zh_CN": 24, "zh_TW": 24}


def test_builder_v1_0_vs_v1_1_row_counts(tmp_path: Path):
    if not REAL_TSV.exists():
        pytest.skip("PR #1037 allocation TSV not present in checkout")
    from scripts.catalog.build_high_confidence_catalog import build_catalog

    out_v0 = tmp_path / "v0.tsv"
    out_v1 = tmp_path / "v1.tsv"
    s0 = build_catalog(
        target_phase="V1.0",
        allocation_tsv=REAL_TSV,
        output_tsv=out_v0,
        write_summary_json=None,
    )
    s1 = build_catalog(
        target_phase="V1.1",
        allocation_tsv=REAL_TSV,
        output_tsv=out_v1,
        write_summary_json=None,
    )
    assert s0["row_count"] == 96
    assert s1["row_count"] <= 296
    assert s1["row_count"] == 296
    assert s1["distinct_brands"] == 37
    lines_v0 = out_v0.read_text(encoding="utf-8").strip().splitlines()
    lines_v1 = out_v1.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines_v0) == 97  # header + 96
    assert len(lines_v1) == 297


def test_loader_tsv_missing(tmp_path: Path):
    from scripts.catalog.v1_1_brand_allocation_loader import load_v1_1_brand_allocation_plan

    missing = tmp_path / "nope.tsv"
    with pytest.raises(FileNotFoundError):
        load_v1_1_brand_allocation_plan(missing)


def test_loader_invalid_surface(tmp_path: Path):
    from scripts.catalog.v1_1_brand_allocation_loader import load_v1_1_brand_allocation_plan

    p = tmp_path / "bad.tsv"
    p.write_text(
        "brand_id\tlocale\tsurface\tseries_count\tepisode_per_series_count\tpriority_phase\n"
        "x\ten_US\tscroll\t1\t1\tV1.1_proposed\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid surface"):
        load_v1_1_brand_allocation_plan(p)


def test_loader_episodes_column_alias(tmp_path: Path):
    from scripts.catalog.v1_1_brand_allocation_loader import load_v1_1_brand_allocation_plan, get_cell

    p = tmp_path / "alt.tsv"
    p.write_text(
        "brand_id\tlocale\tsurface\tseries_count\tepisodes_per_series\tpriority_phase\n"
        "x\ten_US\tebook\t3\t7\tV1.1_proposed\n",
        encoding="utf-8",
    )
    plan = load_v1_1_brand_allocation_plan(p)
    cell = get_cell(plan, "x", "en_US", "ebook")
    assert cell is not None
    assert cell["episodes_per_series"] == 7
    assert cell["series_count"] == 3


def test_get_cell_brand_not_in_tsv(tmp_path: Path):
    from scripts.catalog.v1_1_brand_allocation_loader import load_v1_1_brand_allocation_plan, get_cell

    p = tmp_path / "one.tsv"
    p.write_text(
        "brand_id\tlocale\tsurface\tseries_count\tepisode_per_series_count\tpriority_phase\n"
        "only_brand\ten_US\tebook\t1\t1\tV1.0_matrix_confirmed\n",
        encoding="utf-8",
    )
    plan = load_v1_1_brand_allocation_plan(p)
    assert get_cell(plan, "ghost_brand", "en_US", "ebook") is None
    assert get_cell(plan, "only_brand", "ja_JP", "ebook") is None


def test_loader_duplicate_key_errors(tmp_path: Path):
    from scripts.catalog.v1_1_brand_allocation_loader import load_v1_1_brand_allocation_plan

    p = tmp_path / "dup.tsv"
    p.write_text(
        "brand_id\tlocale\tsurface\tseries_count\tepisode_per_series_count\tpriority_phase\n"
        "a\ten_US\tebook\t1\t1\tV1.0_matrix_confirmed\n"
        "a\ten_US\tebook\t2\t2\tV1.0_matrix_confirmed\n",
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="duplicate allocation key"):
        load_v1_1_brand_allocation_plan(p)


def test_builder_writes_summary_json(tmp_path: Path):
    if not REAL_TSV.exists():
        pytest.skip("PR #1037 allocation TSV not present in checkout")
    from scripts.catalog.build_high_confidence_catalog import build_catalog

    out = tmp_path / "out.tsv"
    summ = tmp_path / "s.json"
    build_catalog(
        target_phase="V1.1",
        allocation_tsv=REAL_TSV,
        output_tsv=out,
        write_summary_json=summ,
    )
    data = json.loads(summ.read_text(encoding="utf-8"))
    assert data["row_count"] == 296
    assert "rows_by_locale" in data
