from __future__ import annotations

from pathlib import Path

from phoenix_v4.manga.serial.spine_loader import (
    build_multivolume_dry_run_plan,
    load_serial_spine,
    validate_multivolume_spine_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SERIES_ID = "heart_balance_shojo__en_US__romance_josei_drama__series01"


def test_multivolume_spine_contract_validates_existing_serial_loader():
    spine = load_serial_spine(SERIES_ID, repo_root=REPO_ROOT)

    assert spine is not None
    assert not validate_multivolume_spine_contract(spine)


def test_multivolume_spine_dry_run_has_five_volumes_and_no_renders():
    plan = build_multivolume_dry_run_plan(SERIES_ID, repo_root=REPO_ROOT)

    assert plan["parallel_spine_created"] is False
    assert plan["panel_renders"] == 0
    assert len(plan["volume_plans"]) == 5
    assert all(row["production_constraints"]["dry_run_only"] for row in plan["volume_plans"])
