#!/usr/bin/env python3
"""Build git history index CSV (commits + anchor PRs).

Produces artifacts/inventory/full_repo_git_history_index_<DATE>.csv. One row
per commit (reachable from any branch) plus rows for anchor PRs.

Usage:
    python3 scripts/audit/build_git_history_index.py [--out PATH] [--dry-run]
                                                     [--prs N1,N2,...]

Tier 1; no LLM calls.
"""
from __future__ import annotations

import argparse
import csv
import datetime as _dt
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_ANCHOR_PRS = [680, 682, 684, 683, 679, 678, 676, 675, 674, 685, 686]
KEYWORDS = (
    "manga", "catalog", "brand", "teacher", "pearl_prime", "pearl_news",
    "wizard", "deprecated", "superseded", "reconciliation", "audit", "archive",
)


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, cwd=REPO_ROOT, text=True)


def collect_commits() -> list[dict]:
    out = run([
        "git", "log", "--all", "--no-renames",
        "--pretty=format:COMMIT|%H|%ad|%an|%s|%d",
        "--date=short", "--shortstat",
    ])
    rows = []
    cur: dict | None = None
    for line in out.splitlines():
        if line.startswith("COMMIT|"):
            if cur:
                rows.append(cur)
            parts = line.split("|", 5)
            _, sha, date, author, subj = parts[:5]
            dec = parts[5] if len(parts) >= 6 else ""
            subj = subj.replace("\t", " ")
            kw = ",".join(k for k in KEYWORDS if k in subj.lower())
            cur = {
                "sha": sha, "date": date, "author": author,
                "subject": subj, "files": "0", "ins": "0", "dels": "0",
                "decoration": dec.strip(), "keywords": kw,
            }
        elif " files changed" in line or " file changed" in line:
            for part in line.split(","):
                p = part.strip()
                if "file" in p:
                    cur["files"] = p.split()[0]
                elif "insertion" in p:
                    cur["ins"] = p.split()[0]
                elif "deletion" in p:
                    cur["dels"] = p.split()[0]
    if cur:
        rows.append(cur)
    return rows


def collect_prs(numbers: list[int]) -> list[dict]:
    rows = []
    for n in numbers:
        try:
            j = json.loads(run([
                "gh", "pr", "view", str(n),
                "--json", "number,title,state,author,createdAt,mergedAt,mergeCommit,files,additions,deletions,headRefName,baseRefName"
            ]))
        except subprocess.CalledProcessError:
            continue
        rows.append({
            "pr_number": j["number"],
            "title": (j["title"] or "").replace("\t", " "),
            "state": j["state"],
            "author": (j.get("author") or {}).get("login", ""),
            "created": j.get("createdAt", ""),
            "merged": j.get("mergedAt") or "",
            "merge_sha": (j.get("mergeCommit") or {}).get("oid", ""),
            "files_count": str(len(j.get("files") or [])),
            "additions": str(j.get("additions") or 0),
            "deletions": str(j.get("deletions") or 0),
            "head": j.get("headRefName", ""),
            "base": j.get("baseRefName", ""),
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None)
    ap.add_argument("--prs", default=",".join(str(n) for n in DEFAULT_ANCHOR_PRS))
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = _dt.date.today().isoformat()
    default = REPO_ROOT / f"artifacts/inventory/full_repo_git_history_index_{today}.csv"
    out_path = Path(args.out) if args.out else default
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(f"[dry-run] would write {out_path}", file=sys.stderr)
        return 0

    commits = collect_commits()
    print(f"captured {len(commits):,} commits", file=sys.stderr)
    pr_numbers = [int(x) for x in args.prs.split(",") if x.strip()]
    prs = collect_prs(pr_numbers)
    print(f"captured {len(prs)} PRs", file=sys.stderr)

    with out_path.open("w") as g:
        w = csv.writer(g, delimiter="\t", quoting=csv.QUOTE_MINIMAL)
        w.writerow([
            "row_type", "key", "date", "author", "subject_or_title",
            "files_changed", "additions", "deletions", "branch_or_state",
            "merge_or_keyword_flags", "head_branch", "base_branch",
        ])
        for c in commits:
            w.writerow([
                "commit", c["sha"], c["date"], c["author"], c["subject"],
                c["files"], c["ins"], c["dels"], c["decoration"], c["keywords"], "", "",
            ])
        for p in prs:
            w.writerow([
                "pr", f"#{p['pr_number']}", p["merged"] or p["created"][:10],
                p["author"], p["title"], p["files_count"], p["additions"],
                p["deletions"], p["state"], p["merge_sha"], p["head"], p["base"],
            ])

    print(f"wrote {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
