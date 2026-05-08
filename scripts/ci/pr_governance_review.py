#!/usr/bin/env python3
"""
PR Governance Review — Automated Pearl_PM + Pearl_Architect gate.

Runs on every PR to main. Validates:
1. SCOPE: files changed stay within a single subsystem (or explicitly cross-subsystem)
2. AUTHORITY: the subsystem's authority docs exist and are referenced
3. MASS DELETION: blocks PRs deleting >50 files
4. DRIFT: detects common drift patterns (duplicate specs, parallel UIs, etc.)
5. OWNERSHIP: files are in the right subsystem per SUBSYSTEM_AUTHORITY_MAP
6. CONFLICT: checks for overlap with active workstreams

Exit 0 = approved. Exit 1 = blocked (with reasons).

Usage:
    python3 scripts/ci/pr_governance_review.py
    # Reads PR diff from git (origin/main...HEAD)

    python3 scripts/ci/pr_governance_review.py --json
    # Output machine-readable JSON

    python3 scripts/ci/pr_governance_review.py --pr 253
    # Review a specific PR by number (requires gh CLI)
"""

import subprocess
import sys
import os
import json
import csv
import re
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Subsystem mapping
# ---------------------------------------------------------------------------

def load_subsystem_map():
    """Load SUBSYSTEM_AUTHORITY_MAP.tsv → dict of path prefixes → subsystem info."""
    tsv_path = REPO_ROOT / "artifacts" / "coordination" / "SUBSYSTEM_AUTHORITY_MAP.tsv"
    if not tsv_path.exists():
        return {}

    subsystems = {}
    with open(tsv_path, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            sid = row.get("subsystem_id", "")
            config_paths = row.get("config_path", "").split(";")
            authority = row.get("authority_doc", "").split(";")
            owner = row.get("owner_agent", "")
            for cp in config_paths:
                cp = cp.strip()
                if cp:
                    subsystems[cp] = {
                        "subsystem_id": sid,
                        "authority_docs": [a.strip() for a in authority if a.strip()],
                        "owner_agent": owner,
                    }
    return subsystems


def load_active_workstreams():
    """Load ACTIVE_WORKSTREAMS.tsv → list of active workstream write scopes."""
    tsv_path = REPO_ROOT / "artifacts" / "coordination" / "ACTIVE_WORKSTREAMS.tsv"
    if not tsv_path.exists():
        return []

    workstreams = []
    with open(tsv_path, newline='') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            status = row.get("status", "")
            if status in ("active", "in_progress"):
                workstreams.append({
                    "id": row.get("workstream_id", ""),
                    "task": row.get("task", ""),
                    "write_scope": row.get("write_scope", ""),
                    "owner": row.get("owner_agent", ""),
                })
    return workstreams

# ---------------------------------------------------------------------------
# Git diff analysis
# ---------------------------------------------------------------------------

def _telemetry_pr_changed_files(source: str, **kwargs: object) -> None:
    parts = [f"[pr_governance_review] changed_files_source={source}"]
    for k, v in kwargs.items():
        if v is None:
            continue
        s = str(v).replace("\n", " ").strip()
        if not s:
            continue
        parts.append(f"{k}={s}")
    print(" ".join(parts), file=sys.stderr)


def _parse_gh_name_status(stdout: str) -> list[dict]:
    files: list[dict] = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, path = parts
            files.append({"status": status.strip(), "path": path.strip()})
    return files


def _change_type_to_status(change_type: str) -> str:
    ct = (change_type or "").upper()
    if ct == "ADDED":
        return "A"
    if ct in ("DELETED", "REMOVED"):
        return "D"
    if ct in ("MODIFIED", "CHANGED"):
        return "M"
    if ct == "RENAMED":
        return "M"
    return "M"


def _files_from_pr_view_json(pr_number) -> list[dict]:
    result = subprocess.run(
        ["gh", "pr", "view", str(pr_number), "--json", "files"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        return []
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []
    out: list[dict] = []
    for ent in data.get("files") or []:
        path = ent.get("path") or ""
        if not path:
            continue
        out.append(
            {
                "status": _change_type_to_status(ent.get("changeType") or ""),
                "path": path,
            }
        )
    return out


def get_changed_files(pr_number=None):
    """Get list of changed files with status (A/M/D)."""
    if not pr_number:
        result = subprocess.run(
            ["git", "diff", "--name-status", "origin/main...HEAD"],
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return _parse_gh_name_status(result.stdout)

    result = subprocess.run(
        ["gh", "pr", "diff", str(pr_number), "--name-status"],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )
    parsed = _parse_gh_name_status(result.stdout)
    if result.returncode == 0 and parsed:
        _telemetry_pr_changed_files("gh_pr_diff_name_status", gh_pr_diff_rc=result.returncode)
        return parsed

    extra: dict[str, object] = {}
    if result.returncode != 0:
        extra["gh_pr_diff_rc"] = result.returncode
        err = (result.stderr or "").strip()
        if err:
            extra["gh_pr_diff_stderr"] = err[:200]
    elif not (result.stdout or "").strip():
        extra["detail"] = "empty_or_failed_diff"
    else:
        extra["detail"] = "gh_pr_diff_unparseable"

    _telemetry_pr_changed_files("gh_pr_view_json_files", **extra)
    return _files_from_pr_view_json(pr_number)

# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_mass_deletion(files):
    """BLOCK if >50 files deleted."""
    deleted = [f for f in files if f["status"] == "D"]
    if len(deleted) > 50:
        dirs = defaultdict(int)
        for f in deleted:
            top = f["path"].split("/")[0]
            dirs[top] += 1
        top_dirs = sorted(dirs.items(), key=lambda x: -x[1])[:10]
        return {
            "check": "mass_deletion",
            "status": "BLOCKED",
            "message": f"PR deletes {len(deleted)} files (threshold: 50)",
            "details": {
                "deleted_count": len(deleted),
                "top_directories": dict(top_dirs),
            }
        }
    return {
        "check": "mass_deletion",
        "status": "PASS",
        "message": f"{len(deleted)} deletions (within threshold)",
    }


def check_subsystem_scope(files, subsystem_map):
    """WARN if PR touches multiple subsystems without explicit cross-subsystem flag."""
    touched_subsystems = set()
    unowned_files = []

    for f in files:
        path = f["path"]
        matched = False
        for prefix, info in subsystem_map.items():
            if path.startswith(prefix.rstrip("*").rstrip("/")):
                touched_subsystems.add(info["subsystem_id"])
                matched = True
                break
        if not matched:
            # Check top-level directory mapping
            top = path.split("/")[0]
            common_unowned = {".github", ".claude", "CLAUDE.md", ".gitignore",
                            "README.md", "ps.txt", "requirements.txt"}
            if top not in common_unowned and not path.startswith("artifacts/"):
                unowned_files.append(path)

    if len(touched_subsystems) > 3:
        return {
            "check": "subsystem_scope",
            "status": "WARN",
            "message": f"PR touches {len(touched_subsystems)} subsystems: {', '.join(sorted(touched_subsystems))}. Consider splitting.",
            "details": {"subsystems": sorted(touched_subsystems)},
        }

    return {
        "check": "subsystem_scope",
        "status": "PASS",
        "message": f"Touches {len(touched_subsystems)} subsystem(s)",
        "details": {"subsystems": sorted(touched_subsystems)},
    }


def check_authority_docs(files, subsystem_map):
    """WARN if authority docs for touched subsystems don't exist."""
    missing_docs = []
    for f in files:
        path = f["path"]
        for prefix, info in subsystem_map.items():
            if path.startswith(prefix.rstrip("*").rstrip("/")):
                for doc in info["authority_docs"]:
                    doc_path = REPO_ROOT / doc
                    if not doc_path.exists():
                        missing_docs.append(doc)
                break

    missing_docs = list(set(missing_docs))
    if missing_docs:
        return {
            "check": "authority_docs",
            "status": "WARN",
            "message": f"{len(missing_docs)} authority doc(s) missing: {', '.join(missing_docs[:5])}",
            "details": {"missing": missing_docs},
        }

    return {
        "check": "authority_docs",
        "status": "PASS",
        "message": "All authority docs present",
    }


def check_drift_patterns(files):
    """WARN on common drift patterns."""
    warnings = []

    added_files = [f["path"] for f in files if f["status"] == "A"]

    # Pattern 1: New spec when canonical exists
    new_specs = [f for f in added_files if f.startswith("specs/") and f.endswith(".md")]
    if len(new_specs) > 2:
        warnings.append(f"Adding {len(new_specs)} new specs — verify no duplicates of existing canonical specs")

    # Pattern 2: New docs that might duplicate existing
    new_docs = [f for f in added_files if f.startswith("docs/") and f.endswith(".md")]
    if len(new_docs) > 5:
        warnings.append(f"Adding {len(new_docs)} new docs — verify against DOCS_INDEX for duplicates")

    # Pattern 3: New config dirs that might shadow existing
    new_configs = [f for f in added_files if f.startswith("config/") and f.endswith(".yaml")]

    # Pattern 4: Files outside standard directories
    nonstandard = [f for f in added_files if "/" not in f and not f.startswith(".")]
    if nonstandard:
        warnings.append(f"Root-level files added: {', '.join(nonstandard[:5])}. Should these be in a subdirectory?")

    if warnings:
        return {
            "check": "drift_patterns",
            "status": "WARN",
            "message": "; ".join(warnings),
            "details": {"warnings": warnings},
        }

    return {
        "check": "drift_patterns",
        "status": "PASS",
        "message": "No drift patterns detected",
    }


def check_workstream_conflict(files, workstreams):
    """WARN if PR modifies files claimed by an active workstream."""
    conflicts = []
    for ws in workstreams:
        scope_paths = [s.strip() for s in ws["write_scope"].split(";") if s.strip()]
        for f in files:
            for sp in scope_paths:
                sp_clean = sp.rstrip("*").rstrip("/")
                if sp_clean and f["path"].startswith(sp_clean):
                    conflicts.append({
                        "file": f["path"],
                        "workstream": ws["id"],
                        "owner": ws["owner"],
                    })
                    break

    if conflicts:
        ws_ids = list(set(c["workstream"] for c in conflicts))
        return {
            "check": "workstream_conflict",
            "status": "WARN",
            "message": f"Overlaps with {len(ws_ids)} active workstream(s): {', '.join(ws_ids)}",
            "details": {"conflicts": conflicts[:10]},
        }

    return {
        "check": "workstream_conflict",
        "status": "PASS",
        "message": "No active workstream conflicts",
    }


def check_pr_size(files):
    """INFO on PR size for awareness."""
    total = len(files)
    added = len([f for f in files if f["status"] == "A"])
    modified = len([f for f in files if f["status"] == "M"])
    deleted = len([f for f in files if f["status"] == "D"])

    status = "PASS"
    msg = f"{total} files ({added} added, {modified} modified, {deleted} deleted)"

    if total > 200:
        status = "WARN"
        msg = f"Large PR: {msg}. Consider splitting into smaller PRs."
    elif total > 500:
        status = "BLOCKED"
        msg = f"Very large PR: {msg}. Must split or get explicit approval."

    return {
        "check": "pr_size",
        "status": status,
        "message": msg,
        "details": {"total": total, "added": added, "modified": modified, "deleted": deleted},
    }

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    use_json = "--json" in sys.argv
    pr_number = None
    for i, arg in enumerate(sys.argv):
        if arg == "--pr" and i + 1 < len(sys.argv):
            pr_number = sys.argv[i + 1]

    subsystem_map = load_subsystem_map()
    workstreams = load_active_workstreams()
    files = get_changed_files(pr_number)

    if not files:
        if use_json:
            print(json.dumps({"status": "PASS", "message": "No files changed", "checks": []}))
        else:
            print("✅ No files changed — nothing to review.")
        sys.exit(0)

    # Run all checks
    results = [
        check_mass_deletion(files),
        check_pr_size(files),
        check_subsystem_scope(files, subsystem_map),
        check_authority_docs(files, subsystem_map),
        check_drift_patterns(files),
        check_workstream_conflict(files, workstreams),
    ]

    blocked = [r for r in results if r["status"] == "BLOCKED"]
    warned = [r for r in results if r["status"] == "WARN"]
    passed = [r for r in results if r["status"] == "PASS"]

    overall = "BLOCKED" if blocked else ("WARN" if warned else "PASS")

    if use_json:
        print(json.dumps({
            "status": overall,
            "checks": results,
            "summary": {
                "blocked": len(blocked),
                "warnings": len(warned),
                "passed": len(passed),
            }
        }, indent=2))
    else:
        print("=" * 60)
        print("PR GOVERNANCE REVIEW (Pearl_PM + Pearl_Architect)")
        print("=" * 60)

        for r in results:
            icon = {"PASS": "✅", "WARN": "⚠️ ", "BLOCKED": "⛔"}[r["status"]]
            print(f"{icon} [{r['check']}] {r['message']}")

        print()
        if blocked:
            print(f"⛔ BLOCKED — {len(blocked)} blocking issue(s). Do NOT merge.")
            for b in blocked:
                print(f"   → {b['check']}: {b['message']}")
        elif warned:
            print(f"⚠️  APPROVED WITH WARNINGS — {len(warned)} warning(s). Review before merge.")
        else:
            print("✅ APPROVED — all checks passed.")

    sys.exit(1 if blocked else 0)


if __name__ == "__main__":
    main()
