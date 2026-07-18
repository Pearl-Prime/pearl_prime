from __future__ import annotations

from scripts.qa.prose_integrity_gap_map import build_gap_map


def test_prose_integrity_gap_map_covers_all_pi_candidates_without_parallel_module():
    report = build_gap_map()

    assert {row["id"] for row in report["rows"]} == {"PI-1", "PI-2", "PI-3", "PI-4", "PI-5"}
    assert report["new_parallel_module_created"] is False
    assert report["hard_ship_gate_created"] is False
    assert all(row["existing_authority"] for row in report["rows"])
