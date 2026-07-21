"""Tests for G-ACCENT — weekly accent-fill preflight matrix."""
from __future__ import annotations

import csv
from pathlib import Path

from scripts.ci.check_accent_supply_preflight import (
    build_report,
    load_top_cells,
    preflight_cell,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

MATRIX_ROWS = [
    {"cell_id": "C001", "index": "1", "persona": "corporate_managers", "topic": "burnout"},
    {"cell_id": "C002", "index": "2", "persona": "gen_z_professionals", "topic": "depression"},
    {"cell_id": "C003", "index": "3", "persona": "corporate_managers", "topic": "burnout"},  # dup
]


def _write_matrix(tmp_path: Path) -> Path:
    path = tmp_path / "MATRIX.tsv"
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["cell_id", "index", "persona", "topic"], delimiter="\t")
        writer.writeheader()
        writer.writerows(MATRIX_ROWS)
    return path


def test_load_top_cells_dedupes_and_ranks(tmp_path):
    matrix = _write_matrix(tmp_path)
    cells = load_top_cells(matrix, top_n=10)
    assert cells == [
        ("corporate_managers", "burnout"),
        ("gen_z_professionals", "depression"),
    ]


def test_load_top_cells_respects_top_n(tmp_path):
    matrix = _write_matrix(tmp_path)
    cells = load_top_cells(matrix, top_n=1)
    assert cells == [("corporate_managers", "burnout")]


def test_known_clean_pilot_cell_has_no_gap():
    row = preflight_cell(
        persona_id="corporate_managers",
        topic_id="burnout",
        brand_id="stillness_press",
        locale="en_US",
        repo_root=REPO_ROOT,
    )
    assert row["capability_gaps"] == {}
    assert row["has_gap"] is False


def test_known_underfilled_cell_has_gap():
    row = preflight_cell(
        persona_id="gen_z_professionals",
        topic_id="depression",
        brand_id="stillness_press",
        locale="en_US",
        repo_root=REPO_ROOT,
    )
    assert row["has_gap"] is True
    assert "no_supply_pool" in row["capability_gaps"].values()


def test_build_report_aggregates_fill_rate(tmp_path):
    matrix = _write_matrix(tmp_path)
    report = build_report(
        matrix_path=matrix,
        top_n=10,
        brand_id="stillness_press",
        locale="en_US",
        repo_root=REPO_ROOT,
    )
    assert report["cells_checked"] == 2
    assert report["cells_with_gap"] == 1
    assert report["fill_rate"] == 0.5
