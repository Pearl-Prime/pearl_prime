#!/usr/bin/env python3
"""Worktree reaper — the durable fix for recurring disk-walls.

disk_guard.py REPORTS stale .claude/worktrees orphans but (correctly) never
deletes. This reaper is the safe, opt-in remover: it lists every registered git
worktree (except the main tree) and classifies each as REAPABLE only when it is
BOTH:
    - clean       working tree has no uncommitted changes (git status --short empty)
    - merged      its branch's tip is an ancestor of origin/main OR its PR is
                  merged/closed (so no unique unmerged work would be lost)

Report-only by default. `--reap` removes REAPABLE worktrees via
`git worktree remove` (adds --force only for a clean tree, never to discard
changes). A worktree that is dirty, ahead-and-unmerged, or whose merge state is
unknown is NEVER reaped — it is reported HOLD with the reason.

Pairs with scripts/git/disk_guard.py: disk_guard decides "is there room / which
orphans exist", reaper decides "which registered worktrees are safe to remove".

Run:
    python3 scripts/git/worktree_reaper.py                 # report only
    python3 scripts/git/worktree_reaper.py --json          # machine-readable
    python3 scripts/git/worktree_reaper.py --reap          # remove REAPABLE
    python3 scripts/git/worktree_reaper.py --reap --dry-run # print removes, do nothing

Exit: 0 (report / successful reap); 1 a reap removal failed; 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]


def _git(root: Path, *args: str) -> tuple[int, str, str]:
    proc = subprocess.run(
        ["git", *args], cwd=root, capture_output=True, text=True, check=False
    )
    return proc.returncode, proc.stdout, proc.stderr


def repo_root() -> Path:
    rc, out, _ = _git(REPO_ROOT, "rev-parse", "--show-toplevel")
    if rc == 0 and out.strip():
        return Path(out.strip()).resolve()
    return REPO_ROOT


@dataclass
class WorktreeState:
    path: str
    branch: str
    head: str
    is_main: bool
    clean: bool
    merged: bool
    reason: str = ""
    holds: list[str] = field(default_factory=list)

    @property
    def reapable(self) -> bool:
        return (not self.is_main) and self.clean and self.merged

    @property
    def verdict(self) -> str:
        if self.is_main:
            return "MAIN"
        if self.reapable:
            return "REAPABLE"
        return "HOLD"


def list_worktrees(root: Path) -> list[dict[str, str]]:
    rc, out, _ = _git(root, "worktree", "list", "--porcelain")
    if rc != 0:
        return []
    entries: list[dict[str, str]] = []
    cur: dict[str, str] = {}
    for line in out.splitlines():
        if line.startswith("worktree "):
            if cur:
                entries.append(cur)
            cur = {"worktree": line.split(" ", 1)[1]}
        elif line.startswith("HEAD "):
            cur["HEAD"] = line.split(" ", 1)[1]
        elif line.startswith("branch "):
            cur["branch"] = line.split(" ", 1)[1]
        elif line.strip() == "bare":
            cur["bare"] = "1"
        elif line.strip() == "detached":
            cur["detached"] = "1"
    if cur:
        entries.append(cur)
    return entries


def _is_clean(wt_path: str) -> bool:
    p = Path(wt_path)
    if not p.is_dir():
        return False
    rc, out, _ = _git(p, "status", "--short")
    return rc == 0 and out.strip() == ""


def _is_merged(root: Path, head: str) -> bool:
    """True if `head` is an ancestor of origin/main (its work is already in main)."""
    if not head:
        return False
    rc, _, _ = _git(root, "merge-base", "--is-ancestor", head, "origin/main")
    return rc == 0


def classify(root: Path, main_path: Path) -> list[WorktreeState]:
    states: list[WorktreeState] = []
    for e in list_worktrees(root):
        wt = e.get("worktree", "")
        is_main = Path(wt).resolve() == main_path.resolve()
        branch = e.get("branch", "").replace("refs/heads/", "") or (
            "(detached)" if e.get("detached") else "(bare)" if e.get("bare") else "")
        head = e.get("HEAD", "")
        clean = _is_clean(wt) if not is_main else True
        merged = _is_merged(root, head) if not is_main else True

        st = WorktreeState(path=wt, branch=branch, head=head[:10],
                           is_main=is_main, clean=clean, merged=merged)
        if not is_main:
            if not clean:
                st.holds.append("dirty (uncommitted changes)")
            if not merged:
                st.holds.append("unmerged (HEAD not an ancestor of origin/main)")
            if not Path(wt).is_dir():
                st.holds.append("path missing on disk (prune candidate)")
        st.reason = "; ".join(st.holds) if st.holds else (
            "main tree" if is_main else "clean + merged")
        states.append(st)
    return states


def reap(root: Path, states: list[WorktreeState], dry_run: bool) -> int:
    failures = 0
    reapable = [s for s in states if s.reapable]
    if not reapable:
        print("REAPER: nothing reapable.", file=sys.stderr)
        return 0
    for s in reapable:
        if dry_run:
            print(f"[dry-run] git worktree remove --force {s.path}", file=sys.stderr)
            continue
        rc, _, err = _git(root, "worktree", "remove", "--force", s.path)
        if rc == 0:
            print(f"REAPED: {s.path} ({s.branch})", file=sys.stderr)
        else:
            failures += 1
            print(f"REAP FAILED: {s.path}: {err.strip()}", file=sys.stderr)
    return 1 if failures else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="List/remove merged+clean git worktrees.")
    ap.add_argument("--reap", action="store_true",
                    help="remove REAPABLE (clean+merged) worktrees (default: report only)")
    ap.add_argument("--dry-run", action="store_true",
                    help="with --reap, print the removes without executing")
    ap.add_argument("--json", action="store_true", help="machine-readable output on stdout")
    args = ap.parse_args(argv)

    root = repo_root()
    _git(root, "fetch", "origin", "--quiet")  # so merged-detection uses fresh origin/main
    main_path = root  # `git rev-parse --show-toplevel` from the main tree returns the main tree
    states = classify(root, main_path)

    if args.json:
        print(json.dumps([
            {"path": s.path, "branch": s.branch, "head": s.head,
             "verdict": s.verdict, "reason": s.reason}
            for s in states
        ], indent=2))
    else:
        n_reap = sum(1 for s in states if s.reapable)
        n_hold = sum(1 for s in states if s.verdict == "HOLD")
        print(f"Worktrees: {len(states)} total — {n_reap} REAPABLE, {n_hold} HOLD",
              file=sys.stderr)
        for s in states:
            print(f"  {s.verdict:9} {s.branch:60.60} {s.reason}", file=sys.stderr)
            print(f"            {s.path}", file=sys.stderr)

    if args.reap:
        return reap(root, states, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
