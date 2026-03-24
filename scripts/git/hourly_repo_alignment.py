#!/usr/bin/env python3
"""
Pearl_GitHub hourly repo alignment runner.

Purpose:
- Keep local main aligned to origin/main
- Auto-merge clean PRs that are already green
- Prune stale local branches with gone upstreams
- Write a machine-readable + markdown report for each run

This script is intentionally conservative about PR merging:
- it ignores Cloudflare preview failures (`Workers Builds: pearl-prime`)
- it refuses to merge draft PRs, PRs with unresolved review threads,
  or PRs with any other failing/pending checks
"""

from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = REPO_ROOT / "artifacts" / "governance" / "repo_alignment"
IGNORED_CHECKS = {"Workers Builds: pearl-prime", "auto-merge"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run(
    cmd: list[str],
    *,
    cwd: Path = REPO_ROOT,
    check: bool = True,
    capture_output: bool = True,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        check=check,
        capture_output=capture_output,
        text=True,
    )


def gh_json(args: list[str]) -> Any:
    proc = run(["gh", *args])
    return json.loads(proc.stdout)


def graphql(query: str, fields: dict[str, str] | None = None) -> Any:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in (fields or {}).items():
        cmd.extend(["-F", f"{key}={value}"])
    proc = run(cmd)
    return json.loads(proc.stdout)


def shell_join(cmd: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in cmd)


@dataclass
class Action:
    kind: str
    target: str
    status: str
    details: str = ""


@dataclass
class Report:
    started_at: str
    repo_root: str
    dry_run: bool
    actions: list[Action] = field(default_factory=list)
    merged_prs: list[int] = field(default_factory=list)
    blocked_prs: list[dict[str, Any]] = field(default_factory=list)
    backup_branch: str | None = None
    synced_main: bool = False
    pruned_branches: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def add(self, kind: str, target: str, status: str, details: str = "") -> None:
        self.actions.append(Action(kind=kind, target=target, status=status, details=details))


def load_worktrees() -> list[dict[str, str]]:
    proc = run(["git", "worktree", "list", "--porcelain"])
    entries: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for raw in proc.stdout.splitlines():
        line = raw.strip()
        if not line:
            if current:
                entries.append(current)
                current = {}
            continue
        key, _, value = line.partition(" ")
        current[key] = value
    if current:
        entries.append(current)
    return entries


def branch_to_worktree_map() -> dict[str, Path]:
    mapping: dict[str, Path] = {}
    for entry in load_worktrees():
        branch_ref = entry.get("branch")
        path = entry.get("worktree")
        if branch_ref and path and branch_ref.startswith("refs/heads/"):
            mapping[branch_ref.removeprefix("refs/heads/")] = Path(path)
    return mapping


def parse_local_main_state(main_path: Path) -> dict[str, Any]:
    status_proc = run(["git", "status", "--short", "--branch"], cwd=main_path)
    lines = status_proc.stdout.splitlines()
    branch_line = lines[0] if lines else ""
    dirty = any(line and not line.startswith("##") for line in lines)
    ahead = behind = 0
    if "[" in branch_line and "]" in branch_line:
        segment = branch_line.split("[", 1)[1].split("]", 1)[0]
        for part in segment.split(", "):
            if part.startswith("ahead "):
                ahead = int(part.removeprefix("ahead "))
            elif part.startswith("behind "):
                behind = int(part.removeprefix("behind "))
    return {
        "branch_line": branch_line,
        "dirty": dirty,
        "ahead": ahead,
        "behind": behind,
    }


def ensure_main_backup(report: Report, state: dict[str, Any]) -> str | None:
    if not state["dirty"] and state["ahead"] == 0 and state["behind"] == 0:
        return None
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = f"codex/main-autobackup-{stamp}"
    run(["git", "branch", backup, "main"])
    report.backup_branch = backup
    report.add("backup", "main", "created", backup)
    return backup


def sync_local_main(report: Report, *, dry_run: bool) -> None:
    worktrees = branch_to_worktree_map()
    main_path = worktrees.get("main", REPO_ROOT)
    state = parse_local_main_state(main_path)
    report.notes.append(f"main state before sync: {state['branch_line'] or 'unknown'}")
    if dry_run:
        status = "would-sync" if (state["dirty"] or state["ahead"] or state["behind"]) else "already-clean"
        report.add("sync-main", str(main_path), status, state["branch_line"])
        return

    ensure_main_backup(report, state)
    run(["git", "fetch", "origin", "--prune"], cwd=main_path)
    run(["git", "checkout", "main"], cwd=main_path)
    run(["git", "reset", "--hard", "origin/main"], cwd=main_path)
    report.synced_main = True
    report.add("sync-main", str(main_path), "synced", "reset --hard origin/main")


def unresolved_review_threads(pr_number: int) -> int:
    query = """
    query($number:Int!) {
      repository(owner:"Ahjan108", name:"phoenix_omega_v4.8") {
        pullRequest(number:$number) {
          reviewThreads(first:100) {
            nodes { isResolved }
          }
        }
      }
    }
    """
    payload = graphql(query, {"number": str(pr_number)})
    nodes = payload["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
    return sum(1 for node in nodes if not node["isResolved"])


def check_summary(pr: dict[str, Any]) -> tuple[list[str], list[str]]:
    failing: list[str] = []
    pending: list[str] = []
    for item in pr.get("statusCheckRollup") or []:
        name = item.get("name") or ""
        if name in IGNORED_CHECKS:
            continue
        status = item.get("status")
        conclusion = item.get("conclusion") or ""
        if status != "COMPLETED":
            pending.append(name)
            continue
        if conclusion and conclusion not in {"SUCCESS", "SKIPPED", "NEUTRAL"}:
            failing.append(name)
    return failing, pending


def load_open_prs() -> list[dict[str, Any]]:
    prs = gh_json(
        [
            "pr",
            "list",
            "--repo",
            "Ahjan108/phoenix_omega_v4.8",
            "--state",
            "open",
            "--json",
            "number,title,headRefName,isDraft",
        ]
    )
    detailed: list[dict[str, Any]] = []
    for pr in prs:
        detail = gh_json(
            [
                "pr",
                "view",
                str(pr["number"]),
                "--repo",
                "Ahjan108/phoenix_omega_v4.8",
                "--json",
                "number,title,url,headRefName,isDraft,mergeable,mergeStateStatus,statusCheckRollup",
            ]
        )
        detail["unresolvedThreads"] = unresolved_review_threads(pr["number"])
        detailed.append(detail)
    return detailed


def merge_clean_prs(report: Report, *, dry_run: bool, max_prs: int) -> None:
    merged = 0
    for pr in sorted(load_open_prs(), key=lambda item: item["number"]):
        failing, pending = check_summary(pr)
        blocked_reason: list[str] = []
        if pr.get("isDraft"):
            blocked_reason.append("draft")
        if pr.get("unresolvedThreads"):
            blocked_reason.append(f"{pr['unresolvedThreads']} unresolved review thread(s)")
        if pr.get("mergeable") != "MERGEABLE":
            blocked_reason.append(f"mergeable={pr.get('mergeable')}")
        if failing:
            blocked_reason.append(f"failing checks: {', '.join(failing)}")
        if pending:
            blocked_reason.append(f"pending checks: {', '.join(pending)}")

        if blocked_reason:
            report.blocked_prs.append(
                {
                    "number": pr["number"],
                    "title": pr["title"],
                    "head": pr["headRefName"],
                    "reason": blocked_reason,
                }
            )
            report.add("pr", f"#{pr['number']}", "blocked", "; ".join(blocked_reason))
            continue

        if merged >= max_prs:
            report.add("pr", f"#{pr['number']}", "deferred", "max_prs reached")
            continue

        if dry_run:
            report.add("pr", f"#{pr['number']}", "would-merge", pr["title"])
            report.merged_prs.append(pr["number"])
            merged += 1
            continue

        cmd = [
            "gh",
            "pr",
            "merge",
            str(pr["number"]),
            "--repo",
            "Ahjan108/phoenix_omega_v4.8",
            "--squash",
            "--admin",
            "--delete-branch",
        ]
        run(cmd)
        report.add("pr", f"#{pr['number']}", "merged", pr["title"])
        report.merged_prs.append(pr["number"])
        merged += 1
        run(["git", "fetch", "origin", "--prune"])


def prune_local_branches(report: Report, *, dry_run: bool) -> None:
    worktree_branches = set(branch_to_worktree_map())
    proc = run(
        [
            "git",
            "for-each-ref",
            "--format=%(refname:short)\t%(upstream:track)",
            "refs/heads",
        ]
    )
    for raw in proc.stdout.splitlines():
        branch, _, track = raw.partition("\t")
        if not branch or "gone" not in track:
            continue
        if branch in {"main"} or branch in worktree_branches:
            report.add("branch", branch, "kept", "checked out in worktree or protected")
            continue
        if dry_run:
            report.add("branch", branch, "would-delete", "upstream gone")
            report.pruned_branches.append(branch)
            continue
        run(["git", "branch", "-D", branch])
        report.add("branch", branch, "deleted", "upstream gone")
        report.pruned_branches.append(branch)
    if not dry_run:
        run(["git", "worktree", "prune"])
        report.add("worktree", "prune", "done", "")


def run_health_check(report: Report) -> None:
    cmd = ["bash", "scripts/git/health_check.sh"]
    proc = run(cmd, check=False)
    status = "pass" if proc.returncode == 0 else f"issues:{proc.returncode}"
    tail = "\n".join(proc.stdout.splitlines()[-10:])
    report.add("health-check", shell_join(cmd), status, tail)


def write_report(report: Report, report_dir: Path) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = report_dir / f"hourly_repo_alignment_{stamp}.json"
    md_path = report_dir / f"hourly_repo_alignment_{stamp}.md"

    json_payload = {
        "started_at": report.started_at,
        "repo_root": report.repo_root,
        "dry_run": report.dry_run,
        "backup_branch": report.backup_branch,
        "synced_main": report.synced_main,
        "merged_prs": report.merged_prs,
        "pruned_branches": report.pruned_branches,
        "blocked_prs": report.blocked_prs,
        "notes": report.notes,
        "actions": [asdict(action) for action in report.actions],
    }
    json_text = json.dumps(json_payload, indent=2) + "\n"
    json_path.write_text(json_text, encoding="utf-8")

    lines = [
        "# Pearl_GitHub Hourly Repo Alignment",
        "",
        f"- Started: `{report.started_at}`",
        f"- Repo: `{report.repo_root}`",
        f"- Dry run: `{report.dry_run}`",
        f"- Backup branch: `{report.backup_branch or 'none'}`",
        f"- Synced main: `{report.synced_main}`",
        "",
        "## Merged PRs",
        "",
    ]
    if report.merged_prs:
        lines.extend(f"- `#{number}`" for number in report.merged_prs)
    else:
        lines.append("- none")
    lines.extend(["", "## Blocked PRs", ""])
    if report.blocked_prs:
        for blocked in report.blocked_prs:
            lines.append(
                f"- `#{blocked['number']}` `{blocked['head']}`: " + "; ".join(blocked["reason"])
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Pruned Branches", ""])
    if report.pruned_branches:
        lines.extend(f"- `{branch}`" for branch in report.pruned_branches)
    else:
        lines.append("- none")
    lines.extend(["", "## Actions", ""])
    for action in report.actions:
        detail = f" — {action.details}" if action.details else ""
        lines.append(f"- `{action.kind}` `{action.target}`: `{action.status}`{detail}")
    if report.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in report.notes)
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")

    latest_json = report_dir / "latest_hourly_repo_alignment.json"
    latest_md = report_dir / "latest_hourly_repo_alignment.md"
    shutil.copy2(json_path, latest_json)
    shutil.copy2(md_path, latest_md)
    return json_path, md_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Pearl_GitHub hourly repo alignment runner")
    parser.add_argument("--dry-run", action="store_true", help="Report actions without mutating repo or PRs")
    parser.add_argument("--max-prs", type=int, default=5, help="Maximum number of clean PRs to merge per run")
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory for JSON/Markdown run reports",
    )
    return parser.parse_args()


def main() -> int:
    os.chdir(REPO_ROOT)
    args = parse_args()
    report = Report(started_at=utc_now(), repo_root=str(REPO_ROOT), dry_run=args.dry_run)

    try:
        run(["git", "fetch", "origin", "--prune"])
        merge_clean_prs(report, dry_run=args.dry_run, max_prs=args.max_prs)
        sync_local_main(report, dry_run=args.dry_run)
        prune_local_branches(report, dry_run=args.dry_run)
        run_health_check(report)
    except subprocess.CalledProcessError as exc:
        report.add("error", shell_join(exc.cmd), f"exit:{exc.returncode}", (exc.stderr or exc.stdout or "").strip())
        json_path, md_path = write_report(report, Path(args.report_dir))
        print(f"FAILED: wrote {json_path} and {md_path}", file=sys.stderr)
        return exc.returncode

    json_path, md_path = write_report(report, Path(args.report_dir))
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
