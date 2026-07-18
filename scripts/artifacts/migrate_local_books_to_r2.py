#!/usr/bin/env python3
"""Migrate locally rendered books from .claude/worktrees → Cloudflare R2.

One-shot helper for the 96 books rendered during the draft-profile QA run
that currently live under
.claude/worktrees/restore-first-100-qa-wrapper-20260425/. Pushes each book
directory to R2, writes per-book manifests, and prints a summary.

Designed to be re-run safely: skips a book if its manifest already exists
and the sha256s match.

Usage:
    python3 scripts/artifacts/migrate_local_books_to_r2.py \\
        --root .claude/worktrees/restore-first-100-qa-wrapper-20260425/out/qa_books/ \\
        --series-id-from-dir-name \\
        --dry-run

    # Then for real:
    python3 scripts/artifacts/migrate_local_books_to_r2.py \\
        --root .claude/worktrees/restore-first-100-qa-wrapper-20260425/out/qa_books/

Discovery convention (the --series-id-from-dir-name flag):
    <root>/<series_id>/<book_id>/<files>
    →  R2 key prefix: manga/rendered_books/<series_id>/<book_id>/
    →  manifest:      artifacts/manifests/manga_rendered_books/<series_id>/<book_id>.yaml

If your layout differs, pass --layout flat-books and one --series-id flag
to override.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _migrate_one_book(book_dir: Path, series_id: str, book_id: str, dry_run: bool) -> tuple[bool, int, int]:
    """Returns (uploaded, files_count, total_bytes)."""
    files = sorted(p for p in book_dir.rglob("*") if p.is_file())
    if not files:
        print(f"  ⚠️  empty: {book_dir.relative_to(REPO) if book_dir.is_relative_to(REPO) else book_dir}")
        return (False, 0, 0)

    total_bytes = sum(f.stat().st_size for f in files)
    if dry_run:
        print(f"  [dry-run] would push {len(files)} files, {total_bytes:,} B")
        return (False, len(files), total_bytes)

    from scripts.artifacts.r2_push_helper import push_book_render

    manifest_path = push_book_render(
        out_dir=book_dir,
        series_id=series_id,
        book_id=book_id,
    )
    print(f"  ✓ {len(files)} files, {total_bytes:,} B")
    print(f"    manifest: {manifest_path.relative_to(REPO)}")
    return (True, len(files), total_bytes)


def _main() -> int:
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    from scripts.agent.assert_remote import assert_remote

    try:
        assert_remote(allow_override=True)
    except Exception as e:
        sys.stderr.write(f"{e}\n")
        return 2

    p = argparse.ArgumentParser(description="Migrate local rendered books → R2")
    p.add_argument("--root", required=True, help="Root dir containing per-series/per-book trees")
    p.add_argument(
        "--layout",
        choices=["series-then-book", "flat-books"],
        default="series-then-book",
        help="series-then-book = <root>/<series_id>/<book_id>/files; flat-books = <root>/<book_id>/files",
    )
    p.add_argument(
        "--series-id-from-dir-name",
        action="store_true",
        help="Derive series_id from the directory name (default with series-then-book layout)",
    )
    p.add_argument(
        "--series-id",
        help="Hard-code series_id (use with --layout flat-books)",
    )
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        sys.stderr.write(f"❌ --root must be a directory: {root}\n")
        return 2

    print(f"═══ Phoenix Omega — local-books → R2 migration ═══")
    print(f"Root:    {root}")
    print(f"Layout:  {args.layout}")
    print(f"Dry-run: {args.dry_run}")
    print()

    plan: list[tuple[Path, str, str]] = []  # (book_dir, series_id, book_id)

    if args.layout == "series-then-book":
        for series_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            series_id = series_dir.name
            for book_dir in sorted(p for p in series_dir.iterdir() if p.is_dir()):
                plan.append((book_dir, series_id, book_dir.name))
    else:  # flat-books
        if not args.series_id:
            sys.stderr.write("❌ --layout flat-books requires --series-id\n")
            return 2
        for book_dir in sorted(p for p in root.iterdir() if p.is_dir()):
            plan.append((book_dir, args.series_id, book_dir.name))

    if not plan:
        print("Nothing to migrate.")
        return 0

    print(f"Discovered {len(plan)} books across {len({s for _,s,_ in plan})} series")
    print()

    uploaded_count = 0
    files_total = 0
    bytes_total = 0
    for book_dir, series_id, book_id in plan:
        print(f"{series_id} / {book_id}")
        uploaded, files, bytes_ = _migrate_one_book(book_dir, series_id, book_id, args.dry_run)
        if uploaded:
            uploaded_count += 1
        files_total += files
        bytes_total += bytes_

    print()
    print(f"═══ Summary ═══")
    print(f"Books processed: {len(plan)}")
    print(f"Books uploaded:  {uploaded_count}")
    print(f"Files:           {files_total}")
    print(f"Bytes:           {bytes_total:,}")
    if args.dry_run:
        print()
        print("Dry-run complete. Re-run without --dry-run to push.")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
