#!/usr/bin/env python3
"""
Lean best-book golden parity / scale-bar CI gate.

Authority:
  artifacts/qa/snapshots/CANONICAL_LEAN_BEST_BOOK.txt
  artifacts/qa/snapshots/CANONICAL_LEAN_BEST_BOOK_METADATA.json

Doctrine (sidebar / flagship pattern):
  Operator reads once (Q-LEAN-BEST-01=A) → machine defends forever.
  - Default: lock golden snapshot bytes (sha256 integrity).
  - --from-file: byte-compare a candidate rebuild of the golden cell.
  - --wave-rendered-dir: hard-fail if any scaled lean book falls below the
    frozen machine-floor bar recorded in metadata (0/0/0 register floor).

Spawned by:
  - .github/workflows/drift-detectors.yml (integrity)
  - scripts/run_production_readiness_gates.py
  - tests/test_lean_best_book_parity.py
  - lean scale receipts (wave-bar mode)

Usage:
  python3 scripts/ci/check_lean_best_book_parity.py
  python3 scripts/ci/check_lean_best_book_parity.py --from-file path/to/book.txt
  python3 scripts/ci/check_lean_best_book_parity.py --wave-rendered-dir path/to/flat_rendered
  python3 scripts/ci/check_lean_best_book_parity.py --score-report path/to/intrabook_score.json

Exit codes:
  0 — pass
  1 — parity / scale-bar failure
  2 — metadata or snapshot missing / unparseable
  3 — input path missing
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT_PATH = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_LEAN_BEST_BOOK.txt"
METADATA_PATH = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_LEAN_BEST_BOOK_METADATA.json"

# Lean awkward-substitution residue patterns seen in read-selection repairs.
AWKWARD_PATTERNS = [
    re.compile(r"\bthe the\b", re.I),
    re.compile(r"\ba a\b", re.I),
    re.compile(r"\{\{[^{}]+\}\}"),
    re.compile(r"\bTODO\b"),
    re.compile(r"\bTBD\b"),
    re.compile(r"\bXXX\b"),
    re.compile(r"\[\[[^\]]+\]\]"),
    re.compile(r"\bco-?founder\s+co-?founder\b", re.I),
    re.compile(r"\bSUBST\b"),
]


def _load_metadata() -> dict:
    if not METADATA_PATH.exists():
        print(f"FAIL: metadata missing at {METADATA_PATH}", file=sys.stderr)
        sys.exit(2)
    try:
        return json.loads(METADATA_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: metadata unparseable: {exc}", file=sys.stderr)
        sys.exit(2)


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _sha256_file(path: Path) -> str:
    return _sha256_bytes(path.read_bytes())


def check_golden_integrity(meta: dict, *, verbose: bool = False) -> int:
    if meta.get("status") != "ratified":
        print("⏸️  LEAN BEST-BOOK GOLDEN — NOT RATIFIED")
        print(f"   metadata: {METADATA_PATH.relative_to(REPO_ROOT)}")
        return 0

    if not SNAPSHOT_PATH.exists():
        print(f"FAIL: canonical snapshot missing at {SNAPSHOT_PATH}", file=sys.stderr)
        return 2

    live = _sha256_file(SNAPSHOT_PATH)
    expected = meta.get("content_sha256")
    if not expected:
        print("FAIL: metadata missing content_sha256", file=sys.stderr)
        return 2

    if live != expected:
        print("❌ LEAN BEST-BOOK GOLDEN INTEGRITY — FAILED", file=sys.stderr)
        print(f"   expected sha256: {expected}", file=sys.stderr)
        print(f"   live     sha256: {live}", file=sys.stderr)
        print("   Restore — do NOT fresh-write:", file=sys.stderr)
        print(f"     {SNAPSHOT_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
        print(
            "     ratify via Q-LEAN-BEST-* = A after operator Layer-4 re-read",
            file=sys.stderr,
        )
        return 1

    print("✅ LEAN BEST-BOOK GOLDEN INTEGRITY — SHA256 LOCKED")
    print(f"   sha256:  {live}")
    print(f"   cell:    {meta.get('cell')}")
    print(f"   approval:{meta.get('operator_approval')}")
    if verbose:
        print(f"   bytes:   {SNAPSHOT_PATH.stat().st_size}")
        print(f"   gate:    {meta.get('parity_gate')}")
    return 0


def check_from_file(meta: dict, candidate: Path, *, verbose: bool = False) -> int:
    if not candidate.exists():
        print(f"FAIL: --from-file missing: {candidate}", file=sys.stderr)
        return 3
    integrity = check_golden_integrity(meta, verbose=verbose)
    if integrity != 0:
        return integrity

    canon = SNAPSHOT_PATH.read_bytes()
    rebuilt = candidate.read_bytes()
    if canon == rebuilt:
        print("✅ LEAN BEST-BOOK CELL PARITY — BYTE-IDENTICAL")
        print(f"   sha256: {_sha256_bytes(rebuilt)}")
        return 0

    print("❌ LEAN BEST-BOOK CELL PARITY — FAILED", file=sys.stderr)
    print(f"   canonical sha256: {_sha256_bytes(canon)}", file=sys.stderr)
    print(f"   candidate sha256: {_sha256_bytes(rebuilt)}", file=sys.stderr)
    print("   Golden cell rebuild must match frozen bytes.", file=sys.stderr)
    return 1


def _split_prose_paragraphs(text: str) -> list[str]:
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    out: list[str] = []
    for block in blocks:
        if re.fullmatch(r"#{1,6}\s+.+", block):
            continue
        if re.fullmatch(r"chapter\s+\d+(?:\s*[:.-].*)?", block, flags=re.I):
            continue
        # Skip short structural labels
        if len(block.split()) < 12:
            continue
        out.append(block)
    return out


def _score_book_text(text: str) -> dict:
    paras = _split_prose_paragraphs(text)
    counts = Counter(paras)
    repeated = sum(1 for _p, n in counts.items() if n > 1)
    repeated_extra = sum(n - 1 for _p, n in counts.items() if n > 1)
    awkward = 0
    for pat in AWKWARD_PATTERNS:
        awkward += len(pat.findall(text))
    return {
        "repeated_non_practice_paragraphs": repeated,
        "repeated_non_practice_extra_instances": repeated_extra,
        "awkward_hits": awkward,
        "words": len(text.split()),
    }


def _floors(meta: dict) -> dict:
    floor = meta.get("machine_floor") or {}
    return {
        "repeated_non_practice_paragraphs": int(floor.get("repeated_non_practice_paragraphs", 0)),
        "awkward_hits": int(floor.get("awkward_hits", 0)),
        "selected_atom_reuse_extra": int(floor.get("selected_atom_reuse_extra", 0)),
        "selected_body_reuse_extra": int(floor.get("selected_body_reuse_extra", 0)),
    }


def _row_exceeds_floor(row: dict, floors: dict) -> list[str]:
    fails: list[str] = []
    for key, limit in floors.items():
        if key not in row:
            continue
        val = int(row.get(key) or 0)
        if val > limit:
            fails.append(f"{key}={val}>{limit}")
    return fails


def check_score_report(meta: dict, report_path: Path, *, verbose: bool = False) -> int:
    integrity = check_golden_integrity(meta, verbose=verbose)
    if integrity != 0:
        return integrity
    if not report_path.exists():
        print(f"FAIL: --score-report missing: {report_path}", file=sys.stderr)
        return 3
    try:
        payload = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: score report unparseable: {exc}", file=sys.stderr)
        return 2

    rows = payload if isinstance(payload, list) else payload.get("books") or payload.get("rows") or []
    if not rows:
        print("FAIL: score report has no book rows", file=sys.stderr)
        return 2

    floors = _floors(meta)
    offenders: list[str] = []
    for row in rows:
        slug = row.get("slug") or row.get("cell") or "?"
        fails = _row_exceeds_floor(row, floors)
        if fails:
            offenders.append(f"{slug}: {', '.join(fails)}")

    if offenders:
        print("❌ LEAN SCALE BAR — BELOW FROZEN GOLDEN FLOOR", file=sys.stderr)
        for line in offenders[:40]:
            print(f"   {line}", file=sys.stderr)
        if len(offenders) > 40:
            print(f"   … +{len(offenders) - 40} more", file=sys.stderr)
        return 1

    print("✅ LEAN SCALE BAR — ALL BOOKS MEET GOLDEN MACHINE FLOOR")
    print(f"   books: {len(rows)}")
    print(f"   floor: {floors}")
    return 0


def check_wave_dir(meta: dict, wave_dir: Path, *, verbose: bool = False) -> int:
    integrity = check_golden_integrity(meta, verbose=verbose)
    if integrity != 0:
        return integrity
    if not wave_dir.exists():
        print(f"FAIL: --wave-rendered-dir missing: {wave_dir}", file=sys.stderr)
        return 3

    books = sorted(wave_dir.glob("*.txt"))
    if not books:
        # Also accept nested */book.txt
        books = sorted(wave_dir.glob("*/book.txt"))
    if not books:
        print(f"FAIL: no .txt books under {wave_dir}", file=sys.stderr)
        return 3

    floors = _floors(meta)
    offenders: list[str] = []
    rows: list[dict] = []
    for path in books:
        text = path.read_text(encoding="utf-8", errors="replace")
        score = _score_book_text(text)
        slug = path.stem if path.name != "book.txt" else path.parent.name
        row = {"slug": slug, **score}
        rows.append(row)
        fails = _row_exceeds_floor(score, floors)
        if fails:
            offenders.append(f"{slug}: {', '.join(fails)}")

    if offenders:
        print("❌ LEAN SCALE BAR — WAVE BELOW FROZEN GOLDEN FLOOR", file=sys.stderr)
        for line in offenders[:40]:
            print(f"   {line}", file=sys.stderr)
        if len(offenders) > 40:
            print(f"   … +{len(offenders) - 40} more", file=sys.stderr)
        return 1

    print("✅ LEAN SCALE BAR — WAVE MEETS GOLDEN MACHINE FLOOR")
    print(f"   books: {len(rows)}")
    print(f"   floor: repeated={floors['repeated_non_practice_paragraphs']} "
          f"awkward={floors['awkward_hits']}")
    if verbose:
        for row in rows[:5]:
            print(f"   sample {row['slug']}: words={row['words']} "
                  f"repeated={row['repeated_non_practice_paragraphs']} "
                  f"awkward={row['awkward_hits']}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Lean best-book golden parity / scale-bar gate")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument(
        "--from-file",
        type=Path,
        default=None,
        help="Byte-compare a golden-cell candidate against the frozen snapshot",
    )
    parser.add_argument(
        "--wave-rendered-dir",
        type=Path,
        default=None,
        help="Score every book under a flat_rendered (or */book.txt) directory against the golden floor",
    )
    parser.add_argument(
        "--score-report",
        type=Path,
        default=None,
        help="Validate a lean intrabook score JSON against the golden machine floor",
    )
    args = parser.parse_args()
    meta = _load_metadata()

    modes = sum(
        1
        for x in (args.from_file, args.wave_rendered_dir, args.score_report)
        if x is not None
    )
    if modes > 1:
        print("FAIL: use only one of --from-file / --wave-rendered-dir / --score-report", file=sys.stderr)
        return 2

    if args.from_file is not None:
        return check_from_file(meta, args.from_file, verbose=args.verbose)
    if args.wave_rendered_dir is not None:
        return check_wave_dir(meta, args.wave_rendered_dir, verbose=args.verbose)
    if args.score_report is not None:
        return check_score_report(meta, args.score_report, verbose=args.verbose)
    return check_golden_integrity(meta, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
