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

Online vs offline:
- `online_live`: `git fetch origin --prune` succeeded and GitHub PR inspection succeeded
- `offline_degraded`: fetch or GitHub failed; local inspection continues; no remote mutations
"""

from __future__ import annotations

import argparse
import fnmatch
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
DEFAULT_BRANCH_REGISTRY = REPO_ROOT / "config" / "governance" / "branch_registry.json"
IGNORED_CHECKS = {"Workers Builds: pearl-prime", "auto-merge"}


class ParserError(ValueError):
    """Raised when CLI args are invalid so the caller can still write a report."""


class ReportingArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ParserError(message)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_run(
    cmd: list[str],
    *,
    cwd: Path = REPO_ROOT,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        check=False,
        capture_output=True,
        text=True,
    )


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


def graphql_safe(query: str, fields: dict[str, str] | None = None) -> tuple[Any | None, str | None]:
    cmd = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in (fields or {}).items():
        cmd.extend(["-F", f"{key}={value}"])
    proc = safe_run(cmd)
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout or "").strip() or f"exit:{proc.returncode}"
    try:
        return json.loads(proc.stdout), None
    except json.JSONDecodeError as exc:
        return None, str(exc)


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
    mode: str = "online_live"
    run_label: str | None = None
    remote_errors: list[str] = field(default_factory=list)
    github_inspection_ok: bool = False
    local_branch: str = ""
    local_main_state: dict[str, Any] = field(default_factory=dict)
    open_pr_count: int | str = "unknown"
    actions: list[Action] = field(default_factory=list)
    merged_prs: list[int] = field(default_factory=list)
    blocked_prs: list[dict[str, Any]] = field(default_factory=list)
    blocked_items: list[dict[str, Any]] = field(default_factory=list)
    backup_branch: str | None = None
    synced_main: bool = False
    pruned_branches: list[str] = field(default_factory=list)
    remaining_branch_drift: list[dict[str, Any]] = field(default_factory=list)
    followup_candidates: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    success: bool = False
    failure_reason: str | None = None
    finished_at: str | None = None
    run_context: dict[str, Any] = field(default_factory=dict)
    branch_census_summary: dict[str, Any] = field(default_factory=dict)

    def add(self, kind: str, target: str, status: str, details: str = "") -> None:
        self.actions.append(Action(kind=kind, target=target, status=status, details=details))


def try_fetch_origin() -> tuple[bool, str]:
    proc = safe_run(["git", "fetch", "origin", "--prune"])
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip() or f"exit:{proc.returncode}"
        return False, err
    return True, ""


def current_checkout_branch(cwd: Path = REPO_ROOT) -> str:
    proc = safe_run(["git", "branch", "--show-current"], cwd=cwd)
    if proc.returncode != 0:
        return "unknown"
    return proc.stdout.strip() or "unknown"


def load_worktrees() -> list[dict[str, str]]:
    proc = safe_run(["git", "worktree", "list", "--porcelain"])
    if proc.returncode != 0:
        return []
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


def safe_git_stdout(args: list[str], *, cwd: Path = REPO_ROOT) -> str | None:
    proc = safe_run(args, cwd=cwd)
    if proc.returncode != 0:
        return None
    return proc.stdout.strip()


def load_branch_registry(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload.setdefault("patterns", [])
    payload.setdefault("branches", [])
    return payload


def local_branch_names() -> list[str]:
    proc = safe_run(["git", "for-each-ref", "--format=%(refname:short)", "refs/heads"])
    if proc.returncode != 0:
        return []
    return sorted(line.strip() for line in proc.stdout.splitlines() if line.strip())


def remote_branch_names() -> list[str]:
    proc = safe_run(["git", "for-each-ref", "--format=%(refname:short)", "refs/remotes/origin"])
    if proc.returncode != 0:
        return []
    branches: list[str] = []
    for raw in proc.stdout.splitlines():
        branch = raw.strip()
        if not branch or branch in {"origin", "origin/HEAD"}:
            continue
        branches.append(branch)
    return sorted(branches)


def branch_distance_vs_main(branch: str) -> tuple[int | None, int | None]:
    stdout = safe_git_stdout(["git", "rev-list", "--left-right", "--count", f"origin/main...{branch}"])
    if not stdout:
        return None, None
    parts = stdout.split()
    if len(parts) != 2:
        return None, None
    try:
        return int(parts[0]), int(parts[1])
    except ValueError:
        return None, None


def match_branch_policy(branch: str, branch_type: str, registry: dict[str, Any]) -> dict[str, Any] | None:
    for entry in registry.get("branches", []):
        if entry.get("branch") == branch:
            return entry
    for pattern in registry.get("patterns", []):
        expected_kind = pattern.get("kind")
        if expected_kind and expected_kind != branch_type:
            continue
        if fnmatch.fnmatch(branch, pattern.get("pattern", "")):
            return pattern
    return None


def build_branch_census(report: Report, registry_path: Path) -> dict[str, Any]:
    registry = load_branch_registry(registry_path)
    local = local_branch_names()
    remote = remote_branch_names()
    live_entries: list[dict[str, Any]] = []
    unmanaged: list[str] = []

    for branch_type, names in (("local", local), ("remote", remote)):
        for branch in names:
            behind, ahead = branch_distance_vs_main(branch)
            policy = match_branch_policy(branch, branch_type, registry)
            entry: dict[str, Any] = {
                "branch": branch,
                "type": branch_type,
                "behind_main": behind,
                "ahead_main": ahead,
                "policy_match": bool(policy),
            }
            if policy:
                entry["policy"] = {
                    "owner": policy.get("owner"),
                    "disposition": policy.get("disposition"),
                    "allowed_actions": policy.get("allowed_actions", []),
                    "source_doc": policy.get("source_doc"),
                    "notes": policy.get("notes", ""),
                }
            else:
                unmanaged.append(branch)
            live_entries.append(entry)

    registry_only: list[str] = []
    live_set = set(local) | set(remote)
    for entry in registry.get("branches", []):
        b = entry.get("branch")
        if b and b not in live_set:
            registry_only.append(b)

    summary = {
        "registry_path": str(registry_path),
        "generated_at": utc_now(),
        "counts": {
            "local": len(local),
            "remote": len(remote),
            "live_total": len(live_entries),
            "unmanaged": len(unmanaged),
            "registry_only": len(registry_only),
        },
        "unmanaged_branches": unmanaged,
        "registry_only_branches": registry_only,
        "entries": live_entries,
    }

    report.branch_census_summary = summary["counts"] | {
        "unmanaged_branches": unmanaged[:20],
        "registry_only_branches": registry_only[:20],
    }
    status = "ok" if not unmanaged else f"unmanaged:{len(unmanaged)}"
    details = f"local={len(local)} remote={len(remote)} registry_only={len(registry_only)}"
    if unmanaged:
        details += f" unmanaged={', '.join(unmanaged[:8])}"
    report.add("branch-census", str(registry_path), status, details)
    return summary


def parse_local_main_state(main_path: Path) -> dict[str, Any]:
    proc = safe_run(["git", "status", "--short", "--branch"], cwd=main_path)
    if proc.returncode != 0:
        return {
            "main_worktree": str(main_path),
            "error": (proc.stderr or proc.stdout or "").strip(),
            "branch_line": "",
            "dirty": False,
            "ahead": 0,
            "behind": 0,
        }
    lines = proc.stdout.splitlines()
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
        "main_worktree": str(main_path),
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


def sync_local_main(report: Report, *, dry_run: bool, online: bool) -> None:
    worktrees = branch_to_worktree_map()
    main_path = worktrees.get("main", REPO_ROOT)
    state = parse_local_main_state(main_path)
    report.local_main_state = state
    report.notes.append(f"main state before sync decision: {state.get('branch_line') or 'unknown'}")
    if not online:
        report.add(
            "sync-main",
            str(main_path),
            "skipped-offline",
            "offline_degraded: no fetch/reset to origin/main (remote sync skipped)",
        )
        report.notes.append(
            "offline_degraded: GitHub/remote sync was intentionally skipped; local main was not reset to origin/main."
        )
        return
    if dry_run:
        status = "would-sync" if (state["dirty"] or state["ahead"] or state["behind"]) else "already-clean"
        report.add("sync-main", str(main_path), status, state.get("branch_line", ""))
        return

    ensure_main_backup(report, state)
    fetch_proc = safe_run(["git", "fetch", "origin", "--prune"], cwd=main_path)
    if fetch_proc.returncode != 0:
        err = (fetch_proc.stderr or fetch_proc.stdout or "").strip()
        report.remote_errors.append(f"sync-main fetch: {err}")
        report.add("sync-main", str(main_path), "fetch-failed", err)
        report.mode = "offline_degraded"
        report.notes.append("Fetch failed during sync-main; skipped reset to origin/main.")
        return
    run(["git", "checkout", "main"], cwd=main_path)
    run(["git", "reset", "--hard", "origin/main"], cwd=main_path)
    report.synced_main = True
    report.add("sync-main", str(main_path), "synced", "reset --hard origin/main")
    report.local_main_state = parse_local_main_state(main_path)


def unresolved_review_threads(pr_number: int) -> tuple[int, str | None]:
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
    payload, err = graphql_safe(query, {"number": str(pr_number)})
    if err:
        return 0, err
    try:
        nodes = payload["data"]["repository"]["pullRequest"]["reviewThreads"]["nodes"]
    except (KeyError, TypeError):
        return 0, "unexpected graphql shape for review threads"
    return sum(1 for node in nodes if not node["isResolved"]), None


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


def load_detailed_open_prs() -> tuple[list[dict[str, Any]] | None, str | None]:
    proc = safe_run(
        [
            "gh",
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
    if proc.returncode != 0:
        return None, (proc.stderr or proc.stdout or "").strip() or f"exit:{proc.returncode}"
    try:
        prs = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        return None, str(exc)
    detailed: list[dict[str, Any]] = []
    for pr in prs:
        proc_view = safe_run(
            [
                "gh",
                "pr",
                "view",
                str(pr["number"]),
                "--repo",
                "Ahjan108/phoenix_omega_v4.8",
                "--json",
                "number,title,url,headRefName,isDraft,mergeable,mergeStateStatus,statusCheckRollup",
            ]
        )
        if proc_view.returncode != 0:
            return None, (proc_view.stderr or proc_view.stdout or "").strip()
        try:
            detail = json.loads(proc_view.stdout)
        except json.JSONDecodeError as exc:
            return None, str(exc)
        unresolved, thread_err = unresolved_review_threads(pr["number"])
        detail["unresolvedThreads"] = unresolved
        detail["reviewThreadCheckError"] = thread_err
        detailed.append(detail)
    return detailed, None


def merge_clean_prs(
    report: Report,
    *,
    dry_run: bool,
    max_prs: int,
    detailed_prs: list[dict[str, Any]] | None,
) -> None:
    if detailed_prs is None:
        report.add("pr", "all", "skipped", "GitHub PR inspection unavailable")
        return
    merged = 0
    for pr in sorted(detailed_prs, key=lambda item: item["number"]):
        failing, pending = check_summary(pr)
        blocked_reason: list[str] = []
        if pr.get("isDraft"):
            blocked_reason.append("draft")
        thread_err = pr.get("reviewThreadCheckError")
        if thread_err:
            blocked_reason.append(f"review threads check failed: {thread_err}")
        elif pr.get("unresolvedThreads"):
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


def compute_remaining_branch_drift() -> list[dict[str, Any]]:
    proc = safe_run(
        [
            "git",
            "for-each-ref",
            "--format=%(refname:short)\t%(upstream:short)\t%(upstream:track)",
            "refs/heads",
        ]
    )
    drift: list[dict[str, Any]] = []
    if proc.returncode != 0:
        return drift
    for raw in proc.stdout.splitlines():
        branch, _, rest = raw.partition("\t")
        mid, _, track = rest.partition("\t")
        upstream = mid
        track = track.strip()
        if not branch:
            continue
        if branch == "main":
            if track and any(x in track for x in ("ahead", "behind", "gone")):
                drift.append({"branch": branch, "upstream": upstream or "none", "track": track})
            continue
        if "gone" in track or "ahead" in track or "behind" in track:
            drift.append({"branch": branch, "upstream": upstream or "none", "track": track})
        elif not upstream:
            drift.append({"branch": branch, "upstream": "none", "track": "no-upstream"})
    return drift


def prune_local_branches(report: Report, *, dry_run: bool, online: bool) -> None:
    worktree_branches = set(branch_to_worktree_map())
    proc = safe_run(
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
        if not online:
            report.add("branch", branch, "would-delete-offline", "upstream gone (not deleted offline_degraded)")
            continue
        if dry_run:
            report.add("branch", branch, "would-delete", "upstream gone")
            report.pruned_branches.append(branch)
            continue
        run(["git", "branch", "-D", branch])
        report.add("branch", branch, "deleted", "upstream gone")
        report.pruned_branches.append(branch)
    if online and not dry_run:
        run(["git", "worktree", "prune"])
        report.add("worktree", "prune", "done", "")


def run_health_check(report: Report) -> None:
    cmd = ["bash", "scripts/git/health_check.sh"]
    proc = run(cmd, check=False)
    status = "pass" if proc.returncode == 0 else f"issues:{proc.returncode}"
    tail = "\n".join(proc.stdout.splitlines()[-10:])
    report.add("health-check", shell_join(cmd), status, tail)


def gather_run_context() -> dict[str, Any]:
    gh_proc = safe_run(["gh", "auth", "status"])
    return {
        "argv": sys.argv[1:],
        "head_sha": safe_git_stdout(["git", "rev-parse", "HEAD"]),
        "origin_main_sha": safe_git_stdout(["git", "rev-parse", "origin/main"]),
        "current_branch": safe_git_stdout(["git", "branch", "--show-current"]),
        "gh_auth_ok": gh_proc.returncode == 0,
    }


def build_blocked_items(report: Report) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for b in report.blocked_prs:
        items.append(
            {
                "kind": "pr",
                "number": b["number"],
                "title": b["title"],
                "head": b["head"],
                "reasons": b["reason"],
            }
        )
    for msg in report.remote_errors:
        items.append({"kind": "remote", "detail": msg})
    return items


def build_followup_candidates(report: Report) -> list[str]:
    c: list[str] = []
    if report.mode == "offline_degraded":
        c.append("Re-run when online to refresh origin refs, PR state, and allow safe local main sync.")
    for entry in report.remaining_branch_drift:
        tr = entry.get("track", "")
        if "gone" in tr:
            c.append(f"Prune when online: local `{entry['branch']}` (upstream gone).")
        elif entry.get("branch") == "main" and ("ahead" in tr or "behind" in tr):
            c.append(f"Align local main: {tr} relative to origin/main.")
    if report.backup_branch:
        c.append(f"Verify backup branch `{report.backup_branch}` before any cleanup.")
    c.append("Branch disposition (remote codex/*): docs/BRANCH_DISPOSITION_2026_03_20.md")
    c.append("Separate harvest-to-main reporting lane: docs/REPO_ALIGNMENT_AND_MAIN_HARVEST_SPEC.md (Workstream B).")
    c.append("Branch policy registry + census: config/governance/branch_registry.json (see runbook).")
    return c


def write_branch_census(census: dict[str, Any], report_dir: Path, stamp: str) -> Path:
    path = report_dir / f"branch_census_{stamp}.json"
    path.write_text(json.dumps(census, indent=2) + "\n", encoding="utf-8")
    latest = report_dir / "latest_branch_census.json"
    shutil.copy2(path, latest)
    return path


def write_report(
    report: Report,
    report_dir: Path,
    branch_census: dict[str, Any] | None = None,
) -> tuple[Path, Path]:
    report_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = report_dir / f"hourly_repo_alignment_{stamp}.json"
    md_path = report_dir / f"hourly_repo_alignment_{stamp}.md"
    branch_census_path: Path | None = None
    if branch_census is not None:
        branch_census_path = write_branch_census(branch_census, report_dir, stamp)

    json_payload = {
        "started_at": report.started_at,
        "finished_at": report.finished_at,
        "repo_root": report.repo_root,
        "dry_run": report.dry_run,
        "mode": report.mode,
        "run_label": report.run_label,
        "success": report.success,
        "failure_reason": report.failure_reason,
        "github_inspection_ok": report.github_inspection_ok,
        "remote_errors": report.remote_errors,
        "local_branch": report.local_branch,
        "local_main_state": report.local_main_state,
        "open_pr_count": report.open_pr_count,
        "merged_prs": report.merged_prs,
        "blocked_items": report.blocked_items,
        "blocked_prs": report.blocked_prs,
        "backup_branch": report.backup_branch,
        "synced_main": report.synced_main,
        "pruned_branches": report.pruned_branches,
        "remaining_branch_drift": report.remaining_branch_drift,
        "followup_candidates": report.followup_candidates,
        "run_context": report.run_context,
        "branch_census_summary": report.branch_census_summary,
        "branch_census_path": str(branch_census_path) if branch_census_path else None,
        "notes": report.notes,
        "actions": [asdict(action) for action in report.actions],
    }
    json_text = json.dumps(json_payload, indent=2) + "\n"
    json_path.write_text(json_text, encoding="utf-8")

    gh_note = (
        "Live GitHub inspection succeeded for this run."
        if report.github_inspection_ok
        else "GitHub inspection did not complete; do not treat PR counts or merge actions as live GitHub truth."
    )
    lines = [
        "# Pearl_GitHub Hourly Repo Alignment",
        "",
        f"- Started: `{report.started_at}`",
        f"- Finished: `{report.finished_at or 'unknown'}`",
        f"- Repo: `{report.repo_root}`",
        f"- Dry run: `{report.dry_run}`",
        f"- Run label: `{report.run_label or 'none'}`",
        f"- Success: `{report.success}`",
        f"- Mode: `{report.mode}`",
        f"- GitHub inspection OK: `{report.github_inspection_ok}`",
        f"- Local branch (checkout): `{report.local_branch}`",
        f"- Open PR count: `{report.open_pr_count}`",
        f"- Branch census file: `{branch_census_path or 'none'}`",
        f"- {gh_note}",
        "",
        "## Local main state",
        "",
        "```text",
        json.dumps(report.local_main_state, indent=2),
        "```",
        "",
        "## Merged PRs",
        "",
    ]
    if report.merged_prs:
        lines.extend(f"- `#{number}`" for number in report.merged_prs)
    else:
        lines.append("- none")
    lines.extend(["", "## Blocked items", ""])
    if report.blocked_items:
        for item in report.blocked_items:
            lines.append(f"- `{item.get('kind')}`: {json.dumps(item, sort_keys=True)}")
    else:
        lines.append("- none")
    lines.extend(["", "## Remaining branch drift", ""])
    if report.remaining_branch_drift:
        for entry in report.remaining_branch_drift:
            lines.append(
                f"- `{entry.get('branch')}` upstream `{entry.get('upstream')}` — `{entry.get('track')}`"
            )
    else:
        lines.append("- none")
    lines.extend(["", "## Follow-up candidates", ""])
    if report.followup_candidates:
        lines.extend(f"- {c}" for c in report.followup_candidates)
    else:
        lines.append("- none")
    lines.extend(
        [
            "",
            f"- Backup branch: `{report.backup_branch or 'none'}`",
            f"- Synced main: `{report.synced_main}`",
            "",
            "## Pruned branches",
            "",
        ]
    )
    if report.pruned_branches:
        lines.extend(f"- `{branch}`" for branch in report.pruned_branches)
    else:
        lines.append("- none")
    lines.extend(["", "## Actions", ""])
    for action in report.actions:
        detail = f" — {action.details}" if action.details else ""
        lines.append(f"- `{action.kind}` `{action.target}`: `{action.status}`{detail}")
    if report.remote_errors:
        lines.extend(["", "## Remote errors", ""])
        lines.extend(f"- {msg}" for msg in report.remote_errors)
    if report.notes:
        lines.extend(["", "## Notes", ""])
        lines.extend(f"- {note}" for note in report.notes)
    if report.failure_reason:
        lines.extend(["", "## Failure", "", f"- `{report.failure_reason}`"])
    if report.branch_census_summary:
        lines.extend(
            [
                "",
                "## Branch census summary",
                "",
                "```text",
                json.dumps(report.branch_census_summary, indent=2),
                "```",
                "",
            ]
        )
    md_text = "\n".join(lines) + "\n"
    md_path.write_text(md_text, encoding="utf-8")

    latest_json = report_dir / "latest_hourly_repo_alignment.json"
    latest_md = report_dir / "latest_hourly_repo_alignment.md"
    shutil.copy2(json_path, latest_json)
    shutil.copy2(md_path, latest_md)
    return json_path, md_path


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = ReportingArgumentParser(description="Pearl_GitHub hourly repo alignment runner")
    parser.add_argument("--dry-run", action="store_true", help="Report actions without mutating repo or PRs")
    parser.add_argument("--max-prs", type=int, default=5, help="Maximum number of clean PRs to merge per run")
    parser.add_argument(
        "--report-label",
        default=None,
        metavar="LABEL",
        help="Label for this run (e.g. automation) recorded in JSON/Markdown reports",
    )
    parser.add_argument(
        "--report-dir",
        default=str(DEFAULT_REPORT_DIR),
        help="Directory for JSON/Markdown run reports",
    )
    parser.add_argument(
        "--branch-registry",
        default=str(DEFAULT_BRANCH_REGISTRY),
        help="Machine-readable branch policy registry used by branch census",
    )
    parser.add_argument(
        "--branch-census-only",
        action="store_true",
        help="Write branch census and alignment report without PR merges, main sync, or pruning",
    )
    return parser.parse_args(argv)


def main() -> int:
    os.chdir(REPO_ROOT)
    raw_argv = sys.argv[1:]
    try:
        args = parse_args(raw_argv)
    except ParserError as exc:
        report = Report(
            started_at=utc_now(),
            repo_root=str(REPO_ROOT),
            dry_run=False,
            run_label=None,
            success=False,
            failure_reason=f"argument-parse failed: {exc}",
            finished_at=utc_now(),
        )
        report.run_context = {"argv": raw_argv}
        report.add("error", "argv", "parse-error", str(exc))
        json_path, md_path = write_report(report, DEFAULT_REPORT_DIR)
        print(f"FAILED: wrote {json_path} and {md_path}", file=sys.stderr)
        return 2

    report = Report(
        started_at=utc_now(),
        repo_root=str(REPO_ROOT),
        dry_run=args.dry_run,
        run_label=args.report_label,
    )
    report.run_context = gather_run_context()
    report.local_branch = current_checkout_branch()
    _worktrees_early = branch_to_worktree_map()
    _main_early = _worktrees_early.get("main", REPO_ROOT)
    report.local_main_state = parse_local_main_state(_main_early)

    fetch_ok, fetch_err = try_fetch_origin()
    if not fetch_ok:
        report.mode = "offline_degraded"
        report.remote_errors.append(f"git fetch origin --prune: {fetch_err}")
        report.add("fetch", "origin", "failed", fetch_err)
    detailed_prs: list[dict[str, Any]] | None = None
    gh_err: str | None = None
    if fetch_ok:
        detailed_prs, gh_err = load_detailed_open_prs()
        if gh_err is not None:
            report.mode = "offline_degraded"
            report.github_inspection_ok = False
            report.remote_errors.append(f"github: {gh_err}")
            report.add("github", "pr-inspection", "failed", gh_err)
            report.open_pr_count = "unknown"
        else:
            report.github_inspection_ok = True
            report.open_pr_count = len(detailed_prs or [])

    branch_census: dict[str, Any] | None = None
    reg_path = Path(args.branch_registry)

    try:
        if reg_path.is_file():
            branch_census = build_branch_census(report, reg_path)
        else:
            report.add("branch-census", str(reg_path), "skipped", "registry file not found")
            report.notes.append(f"Branch registry not found at {reg_path}; census skipped.")

        if args.branch_census_only:
            report.notes.append("branch_census_only: skipped PR merges, main sync, and branch pruning.")
        else:
            merge_clean_prs(report, dry_run=args.dry_run, max_prs=args.max_prs, detailed_prs=detailed_prs)
            sync_local_main(report, dry_run=args.dry_run, online=fetch_ok)
            prune_local_branches(report, dry_run=args.dry_run, online=fetch_ok)

        report.remaining_branch_drift = compute_remaining_branch_drift()
        report.blocked_items = build_blocked_items(report)
        report.followup_candidates = build_followup_candidates(report)
        run_health_check(report)
        report.finished_at = utc_now()
        report.success = True
    except subprocess.CalledProcessError as exc:
        report.mode = "offline_degraded"
        detail = (exc.stderr or exc.stdout or "").strip()
        report.remote_errors.append(f"{shell_join(list(exc.cmd))}: exit {exc.returncode} {detail}".strip())
        report.add("error", shell_join(list(exc.cmd)), f"exit:{exc.returncode}", detail)
        if not report.remaining_branch_drift:
            report.remaining_branch_drift = compute_remaining_branch_drift()
        report.blocked_items = build_blocked_items(report)
        report.followup_candidates = build_followup_candidates(report)
        report.finished_at = utc_now()
        report.success = False
        report.failure_reason = f"{shell_join(list(exc.cmd))} exited {exc.returncode}"
        run_health_check(report)
        json_path, md_path = write_report(report, Path(args.report_dir), branch_census)
        print(f"FAILED: wrote {json_path} and {md_path}", file=sys.stderr)
        return exc.returncode

    json_path, md_path = write_report(report, Path(args.report_dir), branch_census)
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    if report.mode == "offline_degraded":
        print("WARNING: mode=offline_degraded — see report for remote/GitHub skip detail.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
