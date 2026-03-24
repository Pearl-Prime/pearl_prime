from __future__ import annotations

import json

from scripts.git.hourly_repo_alignment import Report, write_report


def test_write_report_refreshes_latest_alias_files(tmp_path) -> None:
    report = Report(
        started_at="2026-03-24T00:20:04Z",
        repo_root="/tmp/repo",
        dry_run=False,
        synced_main=True,
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
