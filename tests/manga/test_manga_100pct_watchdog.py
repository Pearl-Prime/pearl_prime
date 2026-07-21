from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "scripts" / "manga"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from manga_100pct_watchdog import evaluate_pr_snapshot, run_watchdog

HEAD = "a" * 40
MERGE = "b" * 40


def _snapshot(*, draft: bool, state: str = "OPEN", conclusion: str = "SUCCESS"):
    return {
        "number": 5597,
        "url": "https://example.test/pr/5597",
        "state": state,
        "isDraft": draft,
        "mergeable": "MERGEABLE",
        "mergeStateStatus": "CLEAN",
        "headRefOid": HEAD,
        "mergedAt": "2026-07-14T00:00:00Z" if state == "MERGED" else None,
        "mergeCommit": {"oid": MERGE} if state == "MERGED" else None,
        "statusCheckRollup": [
            {"name": "Core tests", "status": "COMPLETED", "conclusion": conclusion},
            {"name": "Auto-merge bot-fix", "status": "COMPLETED", "conclusion": "SKIPPED"},
        ],
    }


def test_green_draft_requests_ready_but_blocks_dispatch():
    report = evaluate_pr_snapshot(_snapshot(draft=True), optional_checks=["Auto-merge bot-fix"], expected_head_sha=HEAD)
    assert report["required_checks_pass"] is True
    assert report["ready_action_allowed"] is True
    assert report["dispatch_allowed"] is False


def test_merged_green_snapshot_allows_dispatch():
    report = evaluate_pr_snapshot(
        _snapshot(draft=False, state="MERGED"),
        optional_checks=["Auto-merge bot-fix"],
        expected_head_sha=HEAD,
    )
    assert report["dispatch_allowed"] is True
    assert report["merge_sha"] == MERGE


def test_failed_required_check_is_reported():
    report = evaluate_pr_snapshot(_snapshot(draft=False, conclusion="FAILURE"), optional_checks=["Auto-merge bot-fix"])
    assert report["required_checks_pass"] is False
    assert report["failing_checks"][0]["name"] == "Core tests"


def test_snapshot_mode_writes_fail_closed_receipt(tmp_path: Path):
    snapshot = tmp_path / "snapshot.json"
    receipt = tmp_path / "receipt.json"
    snapshot.write_text(json.dumps(_snapshot(draft=True)), encoding="utf-8")
    report = run_watchdog(
        repository="Ahjan108/phoenix_omega_v4.8",
        pr_number=5597,
        expected_head_sha=HEAD,
        optional_checks=["Auto-merge bot-fix"],
        receipt_path=receipt,
        snapshot_path=snapshot,
    )
    assert report["dispatch_allowed"] is False
    saved = json.loads(receipt.read_text(encoding="utf-8"))
    assert saved["next_action"].startswith("rerun with --allow-ready")
