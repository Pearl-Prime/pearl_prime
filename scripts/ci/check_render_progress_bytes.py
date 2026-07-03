#!/usr/bin/env python3
"""Drift detector: RENDER_PROGRESS.tsv rows marked done must be real renders.

The stub-as-done kill. Prior manga sessions committed RENDER_PROGRESS.tsv rows
with status=ok and bytes=1 (1-byte stub files) and reported them as finished
renders. This gate makes that structurally impossible to merge: any row whose
status is a success value MUST carry a byte size >= the real-render floor
(50 KB — real manga panels on origin/main are 1.6–3.1 MB; a legitimate panel is
never < 50 KB).

RENDER_PROGRESS.tsv schema (tab-separated):
    panel_id<TAB>status<TAB>bytes<TAB>seconds
Success statuses: ok, done, complete, rendered. The image for <panel_id> is
<panel_id>.png in the same directory as the TSV.

Scan scope:
    --paths P...   scan exactly these files (tests / explicit)
    --base REF     scan RENDER_PROGRESS.tsv files changed vs REF (PR mode)
    (neither)      scan every RENDER_PROGRESS.tsv in the tree (readiness runner)

By default only the bytes COLUMN is checked (this lands green on origin/main,
where sleep_vol1/somatic_vol1 record real byte sizes even though their LFS
images render box-side and are not committed). Pass --require-images to also
assert the sibling <panel_id>.png exists and is itself >= the floor — the mode
the box-side render lanes should run once panels are committed.

Run:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_render_progress_bytes.py \\
        --base origin/main --head HEAD

Exit: 0 pass; 1 fail (rows below the floor, or missing images under
--require-images).
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so scripts.ci.X import resolves this
from drift_detector_git import changed_paths, repo_root_from_script  # noqa: E402

REPO_ROOT = repo_root_from_script(Path(__file__))

MIN_BYTES = 50_000  # real-render floor; a legitimate manga panel is never smaller
SUCCESS_STATUSES = {"ok", "done", "complete", "rendered", "success"}
EXPECTED_HEADER = ("panel_id", "status", "bytes", "seconds")
_TSV_NAME = "RENDER_PROGRESS.tsv"


@dataclass
class Violation:
    file: str
    line: int
    reason: str


def _lfs_or_disk_bytes(path: Path) -> int:
    """True byte size, LFS-pointer-aware. A committed LFS pointer is ~130 B on
    disk but carries the real size on its `size` line — return THAT so a real
    render behind a pointer is not mistaken for a stub."""
    if not path.is_file():
        return -1
    size = path.stat().st_size
    if size < 400:  # possible LFS pointer
        try:
            head = path.read_text(errors="ignore")
        except OSError:
            return size
        if head.startswith("version https://git-lfs"):
            for line in head.splitlines():
                if line.startswith("size "):
                    try:
                        return int(line.split()[1])
                    except (IndexError, ValueError):
                        return size
    return size


def scan_tsv(repo_root: Path, rel: str, require_images: bool) -> list[Violation]:
    path = repo_root / rel
    violations: list[Violation] = []
    try:
        lines = path.read_text().splitlines()
    except OSError as e:
        return [Violation(rel, 0, f"unreadable: {e}")]
    if not lines:
        return [Violation(rel, 0, "empty RENDER_PROGRESS.tsv")]

    header = tuple(lines[0].split("\t"))
    if header[:4] != EXPECTED_HEADER:
        return [Violation(rel, 1, f"unexpected header {header!r}; "
                                  f"expected {EXPECTED_HEADER}")]

    for i, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cols = line.split("\t")
        if len(cols) < 3:
            violations.append(Violation(rel, i, f"malformed row: {line!r}"))
            continue
        panel_id, status, bytes_str = cols[0], cols[1].strip().lower(), cols[2].strip()
        if status not in SUCCESS_STATUSES:
            continue  # pending/failed rows are honest; only success rows must be real
        try:
            byte_count = int(bytes_str)
        except ValueError:
            violations.append(Violation(rel, i, f"{panel_id}: status={status} but "
                                                f"bytes={bytes_str!r} is not an integer"))
            continue
        if byte_count < MIN_BYTES:
            violations.append(Violation(rel, i, f"{panel_id}: status={status} but "
                                                f"bytes={byte_count} < {MIN_BYTES} floor "
                                                f"(stub-as-done)"))
            continue
        if require_images:
            img = path.parent / f"{panel_id}.png"
            real = _lfs_or_disk_bytes(img)
            if real < 0:
                violations.append(Violation(rel, i, f"{panel_id}: status={status} but "
                                                    f"image {img.name} missing"))
            elif real < MIN_BYTES:
                violations.append(Violation(rel, i, f"{panel_id}: image {img.name} is "
                                                    f"{real} bytes < {MIN_BYTES} floor"))
    return violations


def discover_all(repo_root: Path) -> list[str]:
    return sorted(
        str(p.relative_to(repo_root))
        for p in repo_root.rglob(_TSV_NAME)
        if ".git" not in p.parts
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="RENDER_PROGRESS.tsv stub-as-done gate")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--base", default=None, help="git base ref for PR diff")
    ap.add_argument("--head", default="HEAD", help="git head ref")
    ap.add_argument("--paths", nargs="*", default=None,
                    help="explicit RENDER_PROGRESS.tsv paths (tests)")
    ap.add_argument("--require-images", action="store_true",
                    help="also assert each success row's <panel_id>.png exists and "
                         ">= floor (box-side lanes after images are committed)")
    args = ap.parse_args(argv)

    if args.paths is not None:
        targets = [p for p in args.paths if Path(p).name == _TSV_NAME]
    elif args.base:
        targets = [p for p in changed_paths(args.base, args.head, args.repo_root)
                   if Path(p).name == _TSV_NAME]
    else:
        targets = discover_all(args.repo_root)

    violations: list[Violation] = []
    for rel in sorted(set(targets)):
        violations.extend(scan_tsv(args.repo_root, rel, args.require_images))

    if not violations:
        print(f"RENDER-PROGRESS BYTES: PASS ({len(set(targets))} file(s) checked)",
              file=sys.stderr)
        return 0
    for v in violations:
        print(f"FAIL: {v.file}:{v.line}: {v.reason}", file=sys.stderr)
    print(f"RENDER-PROGRESS BYTES: {len(violations)} violation(s) — blocking",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
