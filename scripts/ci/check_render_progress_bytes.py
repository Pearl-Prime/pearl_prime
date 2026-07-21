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

Offloaded assets (LFS_TO_R2_OFFLOAD_V1_SPEC): when the sibling PNG is absent
on disk, --require-images falls back to artifacts/manifests/lfs_offload/*.tsv
entries keyed by repo_path. A manifest row with bytes >= floor and a valid
sha256 passes manifest-verify. Weekly deep-verify fetches from R2 via
scripts/ci/deep_verify_r2_offload.py — this gate does NOT weaken the floor.

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

# Offload manifest lane (LFS_TO_R2_OFFLOAD_V1_SPEC §4.2)
sys.path.insert(0, str(REPO_ROOT))
try:
    from scripts.artifacts.lfs_offload_manifest import (  # noqa: E402
        OffloadEntry,
        load_all_manifests,
    )
except ImportError:
    OffloadEntry = None  # type: ignore[misc, assignment]
    load_all_manifests = None  # type: ignore[assignment]

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


def _offload_index(repo_root: Path, manifest_dir: str | None) -> dict[str, "OffloadEntry"]:
    if load_all_manifests is None:
        return {}
    if manifest_dir:
        # Load only manifests under the explicit dir (tests / overrides).
        from scripts.artifacts.lfs_offload_manifest import (  # noqa: E402
            discover_manifests,
            load_manifest_tsv,
        )

        d = repo_root / manifest_dir
        index: dict[str, OffloadEntry] = {}
        if d.is_dir():
            for mf in sorted(d.glob("*.tsv")):
                for e in load_manifest_tsv(mf).entries:
                    index[e.repo_path] = e
        return index
    return load_all_manifests(repo_root)


def _manifest_verify(
    repo_root: Path,
    rel_tsv: str,
    panel_id: str,
    offload_index: dict[str, "OffloadEntry"],
) -> Violation | None:
    """Return a Violation if manifest-verify fails; None if manifest proves real bytes."""
    if not offload_index:
        return None
    img_rel = str((Path(rel_tsv).parent / f"{panel_id}.png").as_posix())
    entry = offload_index.get(img_rel)
    if entry is None:
        return None
    if entry.bytes < MIN_BYTES:
        return Violation(
            rel_tsv, 0,
            f"{panel_id}: offload manifest bytes={entry.bytes} < {MIN_BYTES} floor",
        )
    if len(entry.sha256) != 64 or not all(c in "0123456789abcdef" for c in entry.sha256):
        return Violation(rel_tsv, 0, f"{panel_id}: offload manifest sha256 invalid")
    return None  # manifest-verify PASS


def scan_tsv(
    repo_root: Path,
    rel: str,
    require_images: bool,
    offload_index: dict[str, "OffloadEntry"] | None = None,
) -> list[Violation]:
    path = Path(rel)
    if not path.is_absolute():
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
                idx = offload_index or {}
                img_rel = str((Path(rel).parent / f"{panel_id}.png").as_posix())
                entry = idx.get(img_rel)
                if entry is not None:
                    mv = _manifest_verify(repo_root, rel, panel_id, idx)
                    if mv is not None:
                        violations.append(Violation(rel, i, mv.reason))
                    # else: manifest-verify PASS — offloaded asset proven
                else:
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
    ap.add_argument("--offload-manifest-dir", default="artifacts/manifests/lfs_offload",
                    help="directory of TSV offload manifests for manifest-verify fallback")
    args = ap.parse_args(argv)

    offload_index = _offload_index(args.repo_root, args.offload_manifest_dir) if args.require_images else {}

    if args.paths is not None:
        targets = [p for p in args.paths if Path(p).name == _TSV_NAME]
    elif args.base:
        targets = [p for p in changed_paths(args.base, args.head, args.repo_root)
                   if Path(p).name == _TSV_NAME]
    else:
        targets = discover_all(args.repo_root)

    violations: list[Violation] = []
    for rel in sorted(set(targets)):
        violations.extend(scan_tsv(args.repo_root, rel, args.require_images, offload_index))

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
