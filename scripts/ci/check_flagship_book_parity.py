#!/usr/bin/env python3
"""
Flagship golden parity CI gate — multi-snapshot (CH1 + full book).

Snapshots:
  ch1  — artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt (active, byte-locked)
  full — artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt (dormant until operator ratifies)

Authority:
  artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json
  artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK_METADATA.json

Spawned by:
  - .github/workflows/drift-detectors.yml
  - scripts/run_production_readiness_gates.py (gate #28 ch1; #29 full when ratified)
  - tests/test_flagship_book_parity.py

Usage:
  python3 scripts/ci/check_flagship_book_parity.py
  python3 scripts/ci/check_flagship_book_parity.py --snapshot ch1
  python3 scripts/ci/check_flagship_book_parity.py --snapshot full
  python3 scripts/ci/check_flagship_book_parity.py --snapshot all
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE_SCRIPT = REPO_ROOT / "scripts/run_pipeline.py"
_CHAPTER_SPLIT = re.compile(r"^Chapter\s+(\d+)\b", re.I | re.M)


@dataclass(frozen=True)
class SnapshotSpec:
    name: str
    canonical_path: Path
    metadata_path: Path
    scope: str  # ch1 | full


SNAPSHOTS: dict[str, SnapshotSpec] = {
    "ch1": SnapshotSpec(
        name="ch1",
        canonical_path=REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt",
        metadata_path=REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json",
        scope="ch1",
    ),
    "full": SnapshotSpec(
        name="full",
        canonical_path=REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK.txt",
        metadata_path=REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_BOOK_METADATA.json",
        scope="full",
    ),
}


def _load_metadata(spec: SnapshotSpec) -> dict:
    if not spec.metadata_path.exists():
        print(f"FAIL: metadata missing at {spec.metadata_path}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(spec.metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: metadata unparseable: {exc}", file=sys.stderr)
        sys.exit(2)


def _normalize_bytes(text: str) -> bytes:
    return (text.rstrip() + "\n").encode("utf-8")


def extract_ch1_prose(book_text: str) -> str:
    m = re.search(r"Chapter 1\b.*?\n\n(.*?)(?=\n\nChapter 2\b|\Z)", book_text, re.S)
    body = m.group(1).strip() if m else book_text.strip()
    if body.startswith("##"):
        body = body.split("\n\n", 1)[-1].strip()
    return body


def _pipeline_cmd(meta: dict, *, render_dir: Path) -> list[str]:
    inv = meta.get("invocation") or []
    if inv:
        cmd = [str(x) for x in inv]
        cmd = [("<render_dir>" if x == "<render_dir>" else x) for x in cmd]
        for i, tok in enumerate(cmd):
            if tok == "<render_dir>":
                cmd[i] = str(render_dir)
        if cmd[0] in ("PYTHONPATH=.",):
            cmd = cmd[1:]
        return cmd
    seed = meta.get("seed", "flagship_phase2_layer6")
    return [
        sys.executable,
        str(PIPELINE_SCRIPT),
        "--topic", "anxiety",
        "--persona", "gen_z_professionals",
        "--arc", "config/source_of_truth/master_arcs/gen_z_professionals__anxiety__overwhelm__F006.yaml",
        "--pipeline-mode", "spine",
        "--runtime-format", "extended_book_2h",
        "--quality-profile", "production",
        "--exercise-journeys",
        "--no-job-check",
        "--render-book",
        "--render-dir", str(render_dir),
        "--seed", seed,
    ]


def _rebuild_book(meta: dict, *, render_dir: Path) -> str:
    cmd = _pipeline_cmd(meta, render_dir=render_dir)
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(REPO_ROOT)}
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT), env=env, capture_output=True, text=True, timeout=600,
        )
    except subprocess.TimeoutExpired:
        print("FAIL: pipeline rebuild timed out (600s)", file=sys.stderr)
        sys.exit(3)
    book_path = render_dir / "book.txt"
    if not book_path.exists():
        print("FAIL: pipeline rebuild did not emit book.txt", file=sys.stderr)
        if result.stderr:
            print(result.stderr[-4000:], file=sys.stderr)
        sys.exit(3)
    return book_path.read_text(encoding="utf-8")


def _is_dormant(meta: dict, spec: SnapshotSpec) -> bool:
    if spec.name == "full":
        if meta.get("status") == "dormant":
            return True
        if not spec.canonical_path.exists():
            return True
    return False


def check_snapshot(
    spec: SnapshotSpec,
    *,
    from_file: Path | None = None,
    verbose: bool = False,
) -> int:
    meta = _load_metadata(spec)

    if _is_dormant(meta, spec):
        print(f"⏸️  FLAGSHIP {spec.name.upper()} GOLDEN — DORMANT (no ratified snapshot yet)")
        print(f"   metadata: {spec.metadata_path.relative_to(REPO_ROOT)}")
        return 0

    if not spec.canonical_path.exists():
        print(f"FAIL: canonical snapshot missing at {spec.canonical_path}", file=sys.stderr)
        return 2

    canonical = spec.canonical_path.read_text(encoding="utf-8")
    canonical_bytes = _normalize_bytes(
        extract_ch1_prose(canonical) if spec.scope == "ch1" else canonical
    )
    expected_sha = meta.get("content_sha256") or hashlib.sha256(canonical_bytes).hexdigest()

    if from_file:
        if not from_file.exists():
            print(f"FAIL: --from-file missing: {from_file}", file=sys.stderr)
            return 3
        rebuilt_raw = from_file.read_text(encoding="utf-8")
    else:
        with tempfile.TemporaryDirectory(prefix=f"flagship_{spec.name}_parity_") as tmp:
            rebuilt_raw = _rebuild_book(meta, render_dir=Path(tmp))

    rebuilt_text = (
        extract_ch1_prose(rebuilt_raw) if spec.scope == "ch1" else rebuilt_raw
    )
    rebuilt_bytes = _normalize_bytes(rebuilt_text)
    rebuilt_sha = hashlib.sha256(rebuilt_bytes).hexdigest()

    label = "CH1" if spec.scope == "ch1" else "FULL BOOK"
    if rebuilt_bytes == canonical_bytes:
        print(f"✅ FLAGSHIP {label} GOLDEN PARITY — BYTE-IDENTICAL")
        print(f"   seed:      {meta.get('seed')}")
        print(f"   sha256:    {rebuilt_sha}")
        print(f"   words:     {len(rebuilt_text.split())}")
        if verbose:
            print(f"   invocation: {meta.get('invocation_shell', '')}")
        return 0

    print(f"❌ FLAGSHIP {label} GOLDEN PARITY — FAILED", file=sys.stderr)
    print(f"   expected sha256: {expected_sha} ({len(canonical_bytes):,} bytes)", file=sys.stderr)
    print(f"   rebuilt  sha256: {rebuilt_sha} ({len(rebuilt_bytes):,} bytes)", file=sys.stderr)
    print(f"   seed: {meta.get('seed')}", file=sys.stderr)
    print("\n  Restore reference — do NOT fresh-fix; golden recipe in metadata:", file=sys.stderr)
    print(f"    {spec.metadata_path.relative_to(REPO_ROOT)}", file=sys.stderr)
    print("    ratify via GOLDEN-UPDATE-RATIFIED: <OPD ref>", file=sys.stderr)
    if verbose:
        import difflib
        canon_lines = canonical if spec.scope == "full" else extract_ch1_prose(canonical)
        for line in difflib.unified_diff(
            canon_lines.splitlines(), rebuilt_text.splitlines(),
            fromfile="canonical", tofile="rebuilt", lineterm="",
        )[:60]:
            print(line, file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Flagship golden parity gate (multi-snapshot)")
    parser.add_argument("--snapshot", choices=["ch1", "full", "all"], default="ch1")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--ch1-from-file",
        type=Path,
        default=None,
        help="Read rebuilt CH1 from file instead of invoking run_pipeline.py",
    )
    parser.add_argument(
        "--full-from-file",
        type=Path,
        default=None,
        help="Read rebuilt full book from file instead of invoking run_pipeline.py",
    )
    args = parser.parse_args()

    targets = ["ch1", "full"] if args.snapshot == "all" else [args.snapshot]
    exit_code = 0
    for name in targets:
        spec = SNAPSHOTS[name]
        from_file = None
        if name == "ch1" and args.ch1_from_file:
            from_file = args.ch1_from_file
        if name == "full" and args.full_from_file:
            from_file = args.full_from_file
        rc = check_snapshot(spec, from_file=from_file, verbose=args.verbose)
        if rc != 0:
            exit_code = rc
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
