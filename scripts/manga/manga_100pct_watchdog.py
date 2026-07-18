#!/usr/bin/env python3
"""Fail-closed foundation-PR watchdog for the manga 100% cloud program."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable

SUCCESS_CONCLUSIONS = {"SUCCESS"}
FAILURE_CONCLUSIONS = {
    "ACTION_REQUIRED",
    "CANCELLED",
    "FAILURE",
    "STARTUP_FAILURE",
    "STALE",
    "TIMED_OUT",
}
PENDING_STATES = {"EXPECTED", "IN_PROGRESS", "PENDING", "QUEUED", "REQUESTED", "WAITING"}
SHA_RE = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


def _default_runner(command: list[str]) -> CommandResult:
    completed = subprocess.run(command, text=True, capture_output=True, check=False)
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def _check_name(row: dict[str, Any]) -> str:
    return str(row.get("name") or row.get("context") or row.get("workflowName") or "unnamed-check")


def _check_state(row: dict[str, Any]) -> tuple[str, str]:
    status = str(row.get("status") or "").upper()
    conclusion = str(row.get("conclusion") or row.get("state") or "").upper()
    return status, conclusion


def evaluate_pr_snapshot(
    snapshot: dict[str, Any],
    *,
    optional_checks: Iterable[str] = (),
    expected_head_sha: str | None = None,
) -> dict[str, Any]:
    """Evaluate a ``gh pr view --json`` snapshot without mutating GitHub."""
    optional = set(optional_checks)
    failures: list[dict[str, Any]] = []
    pending: list[dict[str, Any]] = []
    successful: list[str] = []
    skipped_optional: list[str] = []

    for row in snapshot.get("statusCheckRollup") or []:
        name = _check_name(row)
        status, conclusion = _check_state(row)
        details_url = row.get("detailsUrl") or row.get("targetUrl")
        compact = {"name": name, "status": status, "conclusion": conclusion, "details_url": details_url}
        if name in optional and conclusion in {"SKIPPED", "NEUTRAL", "SUCCESS"}:
            skipped_optional.append(name)
        elif conclusion in SUCCESS_CONCLUSIONS:
            successful.append(name)
        elif conclusion in FAILURE_CONCLUSIONS or conclusion in {"ERROR"}:
            failures.append(compact)
        elif conclusion in {"SKIPPED", "NEUTRAL"}:
            failures.append({**compact, "reason": "required check did not succeed"})
        elif status in PENDING_STATES or not conclusion:
            pending.append(compact)
        else:
            failures.append({**compact, "reason": "unknown check state"})

    head_sha = str(snapshot.get("headRefOid") or snapshot.get("head_sha") or "")
    merged = bool(snapshot.get("mergedAt")) or str(snapshot.get("state") or "").upper() == "MERGED"
    merge_commit = snapshot.get("mergeCommit") or {}
    merge_sha = str(merge_commit.get("oid") if isinstance(merge_commit, dict) else merge_commit or "")
    is_draft = bool(snapshot.get("isDraft", snapshot.get("draft", False)))
    mergeable = str(snapshot.get("mergeable") or "").upper()
    merge_state = str(snapshot.get("mergeStateStatus") or "").upper()

    blockers: list[str] = []
    if expected_head_sha and head_sha != expected_head_sha:
        blockers.append(f"head SHA mismatch: expected {expected_head_sha}, found {head_sha or 'missing'}")
    if failures:
        blockers.append("one or more required checks failed or were skipped")
    if pending:
        blockers.append("one or more required checks are incomplete")
    if not merged and is_draft:
        blockers.append("foundation PR is still draft")
    if not merged and mergeable not in {"MERGEABLE", "TRUE"}:
        blockers.append(f"foundation PR is not mergeable: {mergeable or 'UNKNOWN'}")
    if not merged and merge_state and merge_state not in {"CLEAN", "HAS_HOOKS", "UNSTABLE"}:
        blockers.append(f"merge state is not ready: {merge_state}")
    if merged and not SHA_RE.fullmatch(merge_sha):
        blockers.append("merged PR has no valid 40-character merge SHA")

    checks_pass = not failures and not pending
    ready_action_allowed = checks_pass and not merged and is_draft and mergeable in {"MERGEABLE", "TRUE"}
    merge_action_allowed = checks_pass and not merged and not is_draft and mergeable in {"MERGEABLE", "TRUE"}
    dispatch_allowed = merged and checks_pass and not blockers

    return {
        "pr_number": snapshot.get("number"),
        "url": snapshot.get("url"),
        "state": snapshot.get("state"),
        "draft": is_draft,
        "mergeable": mergeable,
        "merge_state_status": merge_state,
        "head_sha": head_sha,
        "merge_sha": merge_sha or None,
        "merged": merged,
        "required_checks_pass": checks_pass,
        "successful_checks": sorted(successful),
        "optional_checks_skipped": sorted(skipped_optional),
        "pending_checks": pending,
        "failing_checks": failures,
        "ready_action_allowed": ready_action_allowed,
        "merge_action_allowed": merge_action_allowed,
        "dispatch_allowed": dispatch_allowed,
        "blockers": blockers,
    }


def gh_snapshot(repo: str, pr_number: int, runner: Callable[[list[str]], CommandResult] = _default_runner) -> dict[str, Any]:
    fields = (
        "number,url,state,isDraft,mergeable,mergeStateStatus,headRefOid,baseRefOid,"
        "mergedAt,mergeCommit,statusCheckRollup"
    )
    result = runner(["gh", "pr", "view", str(pr_number), "--repo", repo, "--json", fields])
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "gh pr view failed")
    return json.loads(result.stdout)


def _write_receipt(path: Path, report: dict[str, Any], *, repository: str) -> None:
    receipt = {
        "schema_version": "1.0.0",
        "repository": repository,
        "checked_at": datetime.now(timezone.utc).isoformat(),
        **report,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run_watchdog(
    *,
    repository: str,
    pr_number: int,
    expected_head_sha: str | None,
    optional_checks: list[str],
    receipt_path: Path,
    snapshot_path: Path | None = None,
    allow_ready: bool = False,
    allow_merge: bool = False,
    poll_seconds: float = 30.0,
    max_polls: int = 1,
    runner: Callable[[list[str]], CommandResult] = _default_runner,
) -> dict[str, Any]:
    attempts = 0
    action_attempts: list[dict[str, Any]] = []
    while True:
        attempts += 1
        snapshot = (
            json.loads(snapshot_path.read_text(encoding="utf-8"))
            if snapshot_path is not None
            else gh_snapshot(repository, pr_number, runner)
        )
        report = evaluate_pr_snapshot(
            snapshot,
            optional_checks=optional_checks,
            expected_head_sha=expected_head_sha,
        )

        if report["dispatch_allowed"]:
            break
        if report["failing_checks"]:
            report["next_action"] = "dispatch Pearl_DevOps with failing_checks and fetch each details_url log"
            break
        if report["ready_action_allowed"] and allow_ready and snapshot_path is None:
            result = runner(["gh", "pr", "ready", str(pr_number), "--repo", repository])
            action_attempts.append(
                {"action": "mark_ready", "returncode": result.returncode, "stderr": result.stderr.strip()}
            )
            if result.returncode:
                report["blockers"].append("mark-ready action failed: " + (result.stderr.strip() or "unknown error"))
                report["next_action"] = "repository-authorized operator must mark PR ready"
                break
            continue
        if report["merge_action_allowed"] and allow_merge and snapshot_path is None:
            command = ["gh", "pr", "merge", str(pr_number), "--repo", repository, "--squash"]
            if report.get("head_sha"):
                command.extend(["--match-head-commit", report["head_sha"]])
            result = runner(command)
            action_attempts.append(
                {"action": "merge", "returncode": result.returncode, "stderr": result.stderr.strip()}
            )
            if result.returncode:
                report["blockers"].append("merge action failed: " + (result.stderr.strip() or "unknown error"))
                report["next_action"] = "repository-authorized operator must merge the PR"
                break
            continue

        if report["pending_checks"] and (max_polls == 0 or attempts < max_polls) and snapshot_path is None:
            time.sleep(poll_seconds)
            continue
        if report["ready_action_allowed"] and not allow_ready:
            report["next_action"] = "rerun with --allow-ready under a repository-authorized identity"
        elif report["merge_action_allowed"] and not allow_merge:
            report["next_action"] = "rerun with --allow-merge under a repository-authorized identity"
        else:
            report["next_action"] = "resolve blockers, then rerun watchdog"
        break

    report["poll_attempts"] = attempts
    report["action_attempts"] = action_attempts
    _write_receipt(receipt_path, report, repository=repository)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default="Ahjan108/phoenix_omega_v4.8")
    parser.add_argument("--pr", type=int, default=5597)
    parser.add_argument("--expected-head-sha")
    parser.add_argument("--optional-check", action="append", default=[])
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--snapshot-json", type=Path)
    parser.add_argument("--allow-ready", action="store_true")
    parser.add_argument("--allow-merge", action="store_true")
    parser.add_argument("--poll-seconds", type=float, default=30.0)
    parser.add_argument("--max-polls", type=int, default=1, help="0 means unlimited")
    args = parser.parse_args()
    report = run_watchdog(
        repository=args.repo,
        pr_number=args.pr,
        expected_head_sha=args.expected_head_sha,
        optional_checks=args.optional_check,
        receipt_path=args.receipt,
        snapshot_path=args.snapshot_json,
        allow_ready=args.allow_ready,
        allow_merge=args.allow_merge,
        poll_seconds=args.poll_seconds,
        max_polls=args.max_polls,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["dispatch_allowed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
