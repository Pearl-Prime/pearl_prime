from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.git.hourly_repo_alignment import (
    ParserError,
    Report,
    load_branch_registry,
    parse_args,
    write_report,
)


def test_write_report_refreshes_latest_alias_files(tmp_path) -> None:
    report = Report(
        started_at="2026-03-24T00:20:04Z",
        repo_root="/tmp/repo",
        dry_run=False,
        mode="online_live",
        run_label="test-label",
        github_inspection_ok=True,
        local_branch="main",
        local_main_state={"branch_line": "## main", "dirty": False, "ahead": 0, "behind": 0},
        open_pr_count=0,
        blocked_items=[],
        remaining_branch_drift=[],
        followup_candidates=["docs/BRANCH_DISPOSITION_2026_03_20.md"],
        synced_main=True,
        success=True,
        finished_at="2026-03-24T00:21:00Z",
        run_context={"argv": ["--dry-run"]},
    )
    report.add("sync-main", "/tmp/repo", "synced", "reset --hard origin/main")

    json_path, md_path = write_report(report, tmp_path)

    latest_json = tmp_path / "latest_hourly_repo_alignment.json"
    latest_md = tmp_path / "latest_hourly_repo_alignment.md"

    assert latest_json.exists()
    assert latest_md.exists()
    assert latest_json.read_text(encoding="utf-8") == json_path.read_text(encoding="utf-8")
    assert latest_md.read_text(encoding="utf-8") == md_path.read_text(encoding="utf-8")

    payload = json.loads(latest_json.read_text(encoding="utf-8"))
    assert payload["synced_main"] is True
    assert payload["mode"] == "online_live"
    assert payload["run_label"] == "test-label"
    assert payload["open_pr_count"] == 0
    assert payload["success"] is True
    assert payload["finished_at"] == "2026-03-24T00:21:00Z"
    assert "blocked_items" in payload
    assert "remaining_branch_drift" in payload
    assert "followup_candidates" in payload
    assert "run_context" in payload
    assert "branch_census_summary" in payload


def test_parse_args_accepts_report_label_and_branch_census_only() -> None:
    args = parse_args(["--report-label", "automation", "--branch-census-only"])
    assert args.report_label == "automation"
    assert args.branch_census_only is True


def test_load_branch_registry_has_pattern_and_explicit_branch() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    registry = load_branch_registry(repo_root / "config" / "governance" / "branch_registry.json")
    assert any(item["pattern"] == "agent/*" for item in registry["patterns"])
    assert any(item["branch"] == "origin/codex/runtime-consolidation" for item in registry["branches"])


def test_parse_args_raises_reportable_error_on_unknown_flag() -> None:
    with pytest.raises(ParserError):
        parse_args(["--not-a-real-flag"])
