"""Planner-owned spine packet integrity gate."""
from __future__ import annotations

from pathlib import Path

from scripts.ci.check_spine_packet_integrity import audit_case, CANONICAL_CASES

REPO = Path(__file__).resolve().parents[2]


def test_canonical_spine_packet_integrity_cases_pass() -> None:
    rows = [audit_case(case, repo_root=REPO) for case in CANONICAL_CASES]
    assert rows
    fails = [row for row in rows if row["status"] == "FAIL"]
    assert not fails, fails
