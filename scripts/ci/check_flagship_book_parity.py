#!/usr/bin/env python3
"""
Flagship CH1 golden parity CI gate.

Reads artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json, rebuilds
chapter 1 via the recorded seed/invocation, extracts CH1 prose from book.txt,
and byte-diff's against artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt.

Authority: artifacts/qa/ch1_12shape_preview_v4_20260705/manifest.json (atom manifest),
artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json (golden recipe).

Spawned by:
  - .github/workflows/drift-detectors.yml
  - scripts/run_production_readiness_gates.py (gate #28)
  - tests/test_flagship_book_parity.py (pytest wrapper)

Usage:
  python3 scripts/ci/check_flagship_book_parity.py
    → exit 0 if byte parity, non-zero with restoration protocol otherwise
  python3 scripts/ci/check_flagship_book_parity.py --verbose
  python3 scripts/ci/check_flagship_book_parity.py --ch1-from-file PATH
    → skip rebuild; diff PATH against snapshot (for testing the gate)

Exit codes:
  0 — CH1 prose byte-identical to canonical snapshot
  1 — parity drift (rebuilt CH1 differs from snapshot)
  2 — metadata or snapshot file missing / unparseable
  3 — pipeline rebuild failed
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
METADATA_PATH = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json"
CANONICAL_CH1_PATH = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt"
PIPELINE_SCRIPT = REPO_ROOT / "scripts/run_pipeline.py"


def _load_metadata() -> dict:
    if not METADATA_PATH.exists():
        print(f"FAIL: metadata missing at {METADATA_PATH}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: metadata unparseable: {exc}", file=sys.stderr)
        sys.exit(2)


def _load_canonical() -> str:
    if not CANONICAL_CH1_PATH.exists():
        print(f"FAIL: canonical snapshot missing at {CANONICAL_CH1_PATH}", file=sys.stderr)
        sys.exit(2)
    return CANONICAL_CH1_PATH.read_text(encoding="utf-8")


def _normalize_ch1_bytes(text: str) -> bytes:
    """Normalize CH1 prose for byte comparison (single UTF-8 payload, one trailing newline)."""
    return (text.rstrip() + "\n").encode("utf-8")


def extract_ch1_prose(book_text: str) -> str:
    """Extract CH1 body prose (no chapter title block)."""
    m = re.search(r"Chapter 1\b.*?\n\n(.*?)(?=\n\nChapter 2\b|\Z)", book_text, re.S)
    body = m.group(1).strip() if m else book_text.strip()
    if body.startswith("##"):
        body = body.split("\n\n", 1)[-1].strip()
    return body


def _rebuild_ch1(meta: dict, *, render_dir: Path) -> str:
    seed = meta.get("seed", "flagship_phase2_layer6")
    cmd = [
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
    env = {**dict(__import__("os").environ), "PYTHONPATH": str(REPO_ROOT)}
    try:
        result = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=600,
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
    return extract_ch1_prose(book_path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Flagship CH1 golden parity gate")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--ch1-from-file",
        type=Path,
        default=None,
        help="Read rebuilt CH1 from file instead of invoking run_pipeline.py",
    )
    args = parser.parse_args()

    meta = _load_metadata()
    canonical = _load_canonical()
    canonical_bytes = _normalize_ch1_bytes(canonical)
    expected_sha = meta.get("content_sha256") or hashlib.sha256(canonical_bytes).hexdigest()

    if args.ch1_from_file:
        if not args.ch1_from_file.exists():
            print(f"FAIL: --ch1-from-file missing: {args.ch1_from_file}", file=sys.stderr)
            return 3
        rebuilt = args.ch1_from_file.read_text(encoding="utf-8")
    else:
        with tempfile.TemporaryDirectory(prefix="flagship_ch1_parity_") as tmp:
            rebuilt = _rebuild_ch1(meta, render_dir=Path(tmp))

    rebuilt_bytes = _normalize_ch1_bytes(rebuilt)
    rebuilt_sha = hashlib.sha256(rebuilt_bytes).hexdigest()

    if rebuilt_bytes == canonical_bytes:
        print("✅ FLAGSHIP CH1 GOLDEN PARITY — BYTE-IDENTICAL")
        print(f"   seed:      {meta.get('seed')}")
        print(f"   sha256:    {rebuilt_sha}")
        print(f"   words:     {len(rebuilt.split())}")
        if args.verbose:
            print(f"   invocation: {meta.get('invocation_shell', '')}")
        return 0

    print("❌ FLAGSHIP CH1 GOLDEN PARITY — FAILED", file=sys.stderr)
    print(f"   expected sha256: {expected_sha} ({len(canonical_bytes):,} bytes)", file=sys.stderr)
    print(f"   rebuilt  sha256: {rebuilt_sha} ({len(rebuilt_bytes):,} bytes)", file=sys.stderr)
    print(f"   seed: {meta.get('seed')}", file=sys.stderr)
    print("\n  Restore reference — do NOT fresh-fix; golden recipe in metadata:", file=sys.stderr)
    print("    restore via `git checkout <sha> -- artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1.txt`", file=sys.stderr)
    print("    restore via `git checkout <sha> -- artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json`", file=sys.stderr)
    print("    golden recipe: artifacts/qa/snapshots/CANONICAL_FLAGSHIP_CH1_METADATA.json", file=sys.stderr)
    print("    atom manifest: artifacts/qa/ch1_12shape_preview_v4_20260705/manifest.json", file=sys.stderr)
    if args.verbose:
        import difflib
        for line in difflib.unified_diff(
            canonical.splitlines(), rebuilt.splitlines(),
            fromfile="canonical", tofile="rebuilt", lineterm="",
        )[:60]:
            print(line, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
