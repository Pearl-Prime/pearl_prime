#!/usr/bin/env python3
"""Build full repo file inventory CSV.

Produces artifacts/inventory/full_repo_file_inventory_<DATE>.csv with one row
per tracked file. Banned by design: narrow-pattern enumeration. Uses git
ls-files for full-tree coverage.

Usage:
    python3 scripts/audit/build_full_repo_inventory.py [--out PATH] [--dry-run]

Tier 1 (operator-present); no LLM calls.
"""
from __future__ import annotations

import argparse
import datetime as _dt
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

BINARY_EXTS = {
    "png", "jpg", "jpeg", "gif", "webp", "ico", "pdf", "zip", "tar", "gz",
    "tgz", "bz2", "xz", "7z", "rar", "mp3", "mp4", "mov", "wav", "flac",
    "docx", "xlsx", "pptx", "so", "dylib", "o", "a", "pyc", "pkl", "npy",
    "npz", "bin", "ttf", "otf", "woff", "woff2", "h5", "pt", "ckpt",
    "safetensors", "lfs",
}
MEDIA_IMAGE = {"png", "jpg", "jpeg", "gif", "webp", "ico", "svg"}
MEDIA_VIDEO = {"mp4", "mov", "avi", "webm", "mkv"}
MEDIA_AUDIO = {"mp3", "wav", "flac", "ogg", "m4a"}
ARCHIVE_EXTS = {"zip", "tar", "gz", "tgz", "bz2", "xz", "7z", "rar"}
CODE_EXTS = {"py", "js", "ts", "jsx", "tsx", "go", "rs", "rb", "java", "kt", "swift", "c", "cpp", "h", "hpp"}
CONFIG_EXTS = {"yaml", "yml", "json", "toml", "ini", "cfg", "conf", "env", "lock"}
DOC_EXTS = {"md", "txt", "rst", "adoc", "org"}
SCHEMA_EXTS = {"schema.json", "graphql", "proto"}
TEST_HINT = {"test_", "_test"}


def run(cmd: list[str], **kw) -> str:
    return subprocess.check_output(cmd, cwd=REPO_ROOT, text=True, **kw)


def list_tracked_files() -> list[str]:
    return [p for p in run(["git", "ls-files"]).splitlines() if p]


def build_last_commit_map() -> dict[str, tuple[str, str, str]]:
    """Build path -> (sha, date, author) by walking `git log --all --name-only`.
    First-seen path wins (default reverse-chrono order)."""
    out = run(
        ["git", "log", "--all", "--no-renames",
         "--pretty=format:COMMIT|%H|%ad|%an", "--date=short", "--name-only"]
    )
    last: dict[str, tuple[str, str, str]] = {}
    cur: tuple[str, str, str] | None = None
    for line in out.splitlines():
        if line.startswith("COMMIT|"):
            _, sha, date, author = line.split("|", 3)
            cur = (sha, date, author)
        elif line.strip() and cur is not None:
            if line not in last:
                last[line] = cur
    return last


def classify(path: str, ext: str) -> str:
    if any(seg in path.split("/") for seg in ("tests", "test")) or any(h in path for h in TEST_HINT):
        return "test"
    if ext in MEDIA_IMAGE: return "media_image"
    if ext in MEDIA_VIDEO: return "media_video"
    if ext in MEDIA_AUDIO: return "media_audio"
    if ext in ARCHIVE_EXTS: return "archive"
    if ext in CODE_EXTS: return "code"
    if ext in CONFIG_EXTS: return "config"
    if ext in DOC_EXTS: return "doc"
    if path.startswith("schemas/") or "schema" in ext: return "schema"
    if "atoms/" in path or "fixtures/" in path or "template_expand2/" in path: return "fixture"
    if "artifacts/" in path: return "generated"
    if ext in BINARY_EXTS: return "binary"
    if ext in {"csv", "tsv"}: return "data"
    return "other"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = _dt.date.today().isoformat()
    default = REPO_ROOT / f"artifacts/inventory/full_repo_file_inventory_{today}.csv"
    out_path = Path(args.out) if args.out else default
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if args.dry_run:
        print(f"[dry-run] would write {out_path}", file=sys.stderr)
        return 0

    files = list_tracked_files()
    print(f"enumerated {len(files):,} tracked files", file=sys.stderr)
    last = build_last_commit_map()

    n = 0
    with out_path.open("w") as g:
        g.write(
            "path\ttop_level_area\textension\tsize_bytes\tline_count\t"
            "classification\tlast_commit_sha\tlast_commit_date\tlast_author\n"
        )
        for path in files:
            tla = path.split("/", 1)[0] if "/" in path else "(root)"
            base = path.rsplit("/", 1)[-1]
            ext = base.rsplit(".", 1)[-1].lower() if "." in base else "(none)"
            full = REPO_ROOT / path
            try:
                size = full.stat().st_size
            except FileNotFoundError:
                size = 0
            cls_ = classify(path, ext)
            if cls_ in {"binary", "media_image", "media_video", "media_audio", "archive"}:
                lc = "binary"
            elif not full.exists():
                lc = "missing"
            else:
                try:
                    lc = str(sum(1 for _ in full.open("rb")))
                except OSError:
                    lc = "missing"
            sha, date, author = last.get(path, ("", "", ""))
            g.write(f"{path}\t{tla}\t{ext}\t{size}\t{lc}\t{cls_}\t{sha}\t{date}\t{author}\n")
            n += 1

    print(f"wrote {n:,} rows to {out_path}", file=sys.stderr)
    return 0 if n == len(files) else 1


if __name__ == "__main__":
    sys.exit(main())
