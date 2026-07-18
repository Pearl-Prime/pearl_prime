#!/usr/bin/env python3
"""
identify_stale_branches.py — Identify stale remote branches that are candidates
for pruning.

A branch is "stale" if:
- Its last commit is older than --threshold-days (default: 30)
- It has no open PR
- It is not main, master, or a protected pattern

NEVER auto-deletes anything. Produces a report for operator review only.

Usage:
    python3 scripts/git/identify_stale_branches.py \
        --threshold-days 30 \
        --output stale_branches.md
"""
import argparse
import subprocess
import sys
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


PROTECTED_PATTERNS = [
    r"^main$",
    r"^master$",
    r"^develop$",
    r"^release/",
    r"^hotfix/",
    r"^v\d+\.\d+",
]


def parse_args():
    p = argparse.ArgumentParser(description="Identify stale git branches")
    p.add_argument("--threshold-days", type=int, default=30,
                   help="Branches with last commit older than this are stale")
    p.add_argument("--output", default="stale_branches.md")
    p.add_argument("--log", help="Health check log file (optional, for context)")
    p.add_argument("--verbose", action="store_true")
    return p.parse_args()


def run(cmd: list[str]) -> str:
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        return result.stdout.strip()
    except Exception as e:
        print(f"Command failed: {' '.join(cmd)}: {e}", file=sys.stderr)
        return ""


def is_protected(branch: str) -> bool:
    for pat in PROTECTED_PATTERNS:
        if re.match(pat, branch):
            return True
    return False


def get_open_pr_branches() -> set[str]:
    """Get set of branches with open PRs via gh CLI."""
    try:
        out = run(["gh", "pr", "list", "--state", "open", "--json", "headRefName",
                   "--jq", ".[].headRefName"])
        return set(out.split("\n")) if out else set()
    except Exception:
        return set()


def get_remote_branches_with_age(threshold: timedelta) -> list[dict]:
    """Return list of {branch, last_commit_date, age_days, author, last_subject}."""
    raw = run([
        "git", "for-each-ref",
        "--sort=committerdate",
        "--format=%(refname:short)\t%(committerdate:iso8601)\t%(authorname)\t%(subject)",
        "refs/remotes/origin/"
    ])
    if not raw:
        return []

    results = []
    now = datetime.now(timezone.utc)

    for line in raw.split("\n"):
        parts = line.split("\t", 3)
        if len(parts) < 2:
            continue
        ref = parts[0].replace("origin/", "").strip()
        date_str = parts[1].strip()
        author = parts[2].strip() if len(parts) > 2 else "unknown"
        subject = parts[3].strip() if len(parts) > 3 else ""

        # Skip HEAD
        if ref == "HEAD" or ref == "":
            continue

        try:
            # Parse ISO 8601 date (may have offset)
            date_str_clean = re.sub(r"\s([+-]\d{4})$", r"\1", date_str)
            commit_date = datetime.fromisoformat(date_str_clean)
            if commit_date.tzinfo is None:
                commit_date = commit_date.replace(tzinfo=timezone.utc)
            age = now - commit_date
            results.append({
                "branch": ref,
                "last_commit_date": commit_date.strftime("%Y-%m-%d"),
                "age_days": age.days,
                "author": author,
                "last_subject": subject[:80],
            })
        except Exception:
            pass

    return results


def main():
    args = parse_args()
    threshold = timedelta(days=args.threshold_days)

    print(f"Fetching branch data (threshold: {args.threshold_days} days)...", file=sys.stderr)
    all_branches = get_remote_branches_with_age(threshold)
    open_pr_branches = get_open_pr_branches()

    stale = []
    for b in all_branches:
        if b["age_days"] < args.threshold_days:
            continue
        if is_protected(b["branch"]):
            continue
        if b["branch"] in open_pr_branches:
            continue
        stale.append(b)

    # Sort by age descending
    stale.sort(key=lambda x: x["age_days"], reverse=True)

    lines = [
        f"# Stale Branch Prune Candidates",
        f"",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Threshold:** {args.threshold_days} days",
        f"**Total remote branches scanned:** {len(all_branches)}",
        f"**Stale candidates:** {len(stale)}",
        f"",
        f"> ⚠️ **Do NOT auto-delete.** Operator reviews and prunes manually.",
        f"> Check each branch for unpushed work or open PRs before deleting.",
        f"",
    ]

    if stale:
        lines += [
            "## Candidates",
            "",
            "| Branch | Last Commit | Age (days) | Author | Last Subject |",
            "|--------|------------|------------|--------|--------------|",
        ]
        for b in stale:
            branch = b["branch"]
            lines.append(
                f"| `{branch}` | {b['last_commit_date']} | {b['age_days']} "
                f"| {b['author']} | {b['last_subject']} |"
            )
        lines += [
            "",
            "## How to Prune (operator runs manually)",
            "```bash",
            "# Verify no open PRs:",
            "gh pr list --head <branch>",
            "",
            "# Delete remote branch:",
            "git push origin --delete <branch>",
            "```",
        ]
    else:
        lines += ["## Result", "", f"No branches older than {args.threshold_days} days without open PRs. ✅"]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    report = "\n".join(lines)
    out.write_text(report)
    print(f"Found {len(stale)} stale branches. Report: {out}", file=sys.stderr)
    print(report)
    sys.exit(0)


if __name__ == "__main__":
    main()
