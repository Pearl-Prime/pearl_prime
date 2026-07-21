#!/usr/bin/env python3
"""Minimal offline land via temp-index plumbing (disk-safe; no worktree).

BASE tree → hash-object -w each explicit path → update-index → write-tree →
commit-tree → push pearlstar_offline. Never touches the shared index.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[3]  # lane07 → oldchats7_finish → qa → artifacts → repo root
assert (ROOT / ".git").exists(), f"bad ROOT {ROOT}"
BASE = "9e9b9e606791590337cd7d0f2fb425def2e6f760"
REF = "refs/heads/offline/atom-source-authority-repair-20260718"
BRANCH = "offline/atom-source-authority-repair-20260718"
HANDOFF = "artifacts/coordination/handoffs/atom_source_authority_repair_2026-07-18.md"
CLOSEOUT = "artifacts/qa/oldchats7_finish_20260718/lane07/CLOSEOUT_RECEIPT.txt"


def run(cmd, *, env=None, input_text=None):
    merged = os.environ.copy()
    merged.setdefault("GIT_LFS_SKIP_SMUDGE", "1")
    if env:
        merged.update(env)
    return subprocess.run(
        cmd,
        cwd=ROOT,
        env=merged,
        text=True,
        capture_output=True,
        input=input_text,
    )


def load_paths() -> list[str]:
    paths = [
        p.strip()
        for p in (LANE / "LAND_PATHS.txt").read_text().splitlines()
        if p.strip() and not p.strip().startswith("#")
    ]
    for extra in (
        "artifacts/qa/oldchats7_finish_20260718/lane07/LAND_PATHS.txt",
        "artifacts/qa/oldchats7_finish_20260718/lane07/land_offline.py",
        CLOSEOUT,
        HANDOFF,
    ):
        if extra not in paths:
            paths.append(extra)
    missing = [p for p in paths if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit(f"missing land paths: {missing}")
    return paths


def stage_paths(paths: list[str], index_env: dict) -> None:
    # Prefer update-index --add --cacheinfo (one call batch) after hash-object
    info_lines = []
    for path in paths:
        blob = run(["git", "hash-object", "-w", path], env=index_env)
        if blob.returncode != 0:
            raise SystemExit(f"hash-object failed {path}: {blob.stderr}")
        sha = blob.stdout.strip()
        info_lines.append(f"100644 {sha}\t{path}")
    upd = run(
        ["git", "update-index", "--index-info"],
        env=index_env,
        input_text="\n".join(info_lines) + "\n",
    )
    if upd.returncode != 0:
        raise SystemExit(f"update-index failed: {upd.stderr}")


def commit_tree(tree_sha: str, parents: list[str], msg: str, index_env: dict) -> str:
    cmd = ["git", "commit-tree", tree_sha]
    for p in parents:
        cmd.extend(["-p", p])
    cmd.extend(["-m", msg])
    c = run(cmd, env=index_env)
    if c.returncode != 0:
        raise SystemExit(c.stderr or c.stdout)
    return c.stdout.strip()


def set_signal(sha: str) -> None:
    handoff = ROOT / HANDOFF
    text = handoff.read_text()
    text = re.sub(
        r"atom-source-authority-repair=\S+",
        f"atom-source-authority-repair={sha}",
        text,
    )
    text = re.sub(
        r"LANDED=offline/atom-source-authority-repair-20260718@\S+",
        f"LANDED=offline/atom-source-authority-repair-20260718@{sha}",
        text,
    )
    if "LANDED=offline/atom-source-authority-repair-20260718@" not in text:
        text = text.rstrip() + f"\n\nLANDED=offline/atom-source-authority-repair-20260718@{sha}\n"
    handoff.write_text(text)

    close = ROOT / CLOSEOUT
    ct = close.read_text()
    ct = re.sub(r"LANDED=\S+", f"LANDED={BRANCH}@{sha}", ct)
    ct = re.sub(
        r"SIGNAL=atom-source-authority-repair=\S+",
        f"SIGNAL=atom-source-authority-repair={sha}",
        ct,
    )
    ct = re.sub(r"CLEANUP_COMPLETE=\S+", "CLEANUP_COMPLETE=yes", ct)
    close.write_text(ct)


def main() -> None:
    paths = load_paths()
    tmp = Path(tempfile.mkdtemp(prefix="lane07_idx_"))
    index = tmp / "index"
    index_env = {"GIT_INDEX_FILE": str(index), "GIT_LFS_SKIP_SMUDGE": "1"}

    # Reset signal to PENDING for payload blob
    set_signal("<PENDING_SHA>")

    rt = run(["git", "read-tree", f"{BASE}^{{tree}}"], env=index_env)
    if rt.returncode != 0:
        raise SystemExit(f"read-tree failed: {rt.stderr}")

    stage_paths(paths, index_env)
    tree1 = run(["git", "write-tree"], env=index_env)
    if tree1.returncode != 0:
        raise SystemExit(tree1.stderr)
    tree1_sha = tree1.stdout.strip()

    name = run(["git", "diff", "--name-only", BASE, tree1_sha])
    changed = [x for x in name.stdout.splitlines() if x.strip()]
    unexpected = [p for p in changed if p not in paths]
    if unexpected:
        raise SystemExit(f"DIFF GATE FAIL unexpected: {unexpected}")
    stat = run(["git", "diff", "--stat", BASE, tree1_sha]).stdout
    (LANE / "DIFF_STAT.txt").write_text(stat)
    print(stat)
    print("changed", len(changed), "intended", len(paths))

    msg = (
        "fix(atoms): source-authority repair for 11 blocked types (lane07)\n\n"
        "Phase A provenance dossiers + Phase B deepen/seed SOURCED|PARTIAL;\n"
        "MOTIF remains NO-SOURCE in still_blocked_manifest.\n"
    )
    payload = commit_tree(tree1_sha, [BASE], msg, index_env)
    print("PAYLOAD", payload)

    # Stamp handoff/closeout with tip=payload first, then tip commit for docs
    set_signal(payload)
    stage_paths([HANDOFF, CLOSEOUT], index_env)
    tree2 = run(["git", "write-tree"], env=index_env)
    if tree2.returncode != 0:
        raise SystemExit(tree2.stderr)
    tip = commit_tree(
        tree2.stdout.strip(),
        [payload],
        "docs(handoff): atom-source-authority-repair signal sha",
        index_env,
    )
    print("TIP", tip)

    # Disk greppable signal = tip (dispatcher); blob in tip commit records payload
    set_signal(tip)

    push = run(
        [
            "git",
            "-c",
            "core.sshCommand=ssh -o ConnectTimeout=8",
            "push",
            "pearlstar_offline",
            f"{tip}:{REF}",
        ]
    )
    print(push.stdout)
    print(push.stderr)
    if push.returncode != 0:
        raise SystemExit(f"push failed rc={push.returncode}: {push.stderr}")

    run(["git", "branch", "-f", BRANCH, tip])
    (LANE / "LAND_RECEIPT.txt").write_text(
        f"REF={REF}\nTIP={tip}\nPAYLOAD={payload}\nBASE={BASE}\n"
        f"CHANGED={len(changed)}\nSIGNAL=atom-source-authority-repair={tip}\n"
        f"HANDOFF_IN_TIP_BLOB=atom-source-authority-repair={payload}\n"
    )
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"LANDED {BRANCH}@{tip}")
    print(f"atom-source-authority-repair={tip}")


if __name__ == "__main__":
    main()
