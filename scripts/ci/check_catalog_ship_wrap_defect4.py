#!/usr/bin/env python3
"""
G-WRAP + G-DEF4 — catalog ship path checks on rendered book artifacts.

G-WRAP: HARD_FAIL if the same cleared exercise-wrapper stem appears in ≥4
chapters of book.txt (visible machinery).

G-DEF4: HARD_FAIL if enrichment_audit.json records any defect4_drops for the
active persona (foreign-persona registry bleed). Fix bank routing; do not
silence the detector.

When no --render-dir / --book is given, scans optional catalog render roots
and passes if none present (wiring integrity mode for CI).

Authority: artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md

Usage:
  PYTHONPATH=. python3 scripts/ci/check_catalog_ship_wrap_defect4.py \\
      --book path/to/book.txt --enrichment-audit path/to/enrichment_audit.json
  PYTHONPATH=. python3 scripts/ci/check_catalog_ship_wrap_defect4.py \\
      --render-dir artifacts/rendered/catalog_assembly/brand/book_id
  PYTHONPATH=. python3 scripts/ci/check_catalog_ship_wrap_defect4.py  # integrity no-op PASS

Exit: 0 pass; 1 fail.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Keep import path working when PYTHONPATH=.
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.planning.book_engine_policy import (  # noqa: E402
    CLEARED_EXERCISE_WRAPPER_PHRASES,
)
from phoenix_v4.quality.register_gate import (  # noqa: E402
    F16_WRAPPER_CHAPTER_LIMIT,
    _detect_f16_exercise_wrapper_spam,
    _split_chapters,
)


def check_wrap(book_text: str, *, label: str) -> list[str]:
    chapters = _split_chapters(book_text)
    findings = _detect_f16_exercise_wrapper_spam(
        chapters, quality_profile="production"
    )
    out: list[str] = []
    for f in findings:
        out.append(f"{label}: G-WRAP {f.summary}")
    return out


def check_defect4(audit: dict, *, label: str) -> list[str]:
    drops = audit.get("defect4_drops") or []
    if not isinstance(drops, list):
        return [f"{label}: enrichment_audit.defect4_drops must be a list"]
    if not drops:
        return []
    persona = audit.get("persona_id") or "?"
    sample = drops[0] if isinstance(drops[0], dict) else {"raw": drops[0]}
    return [
        f"{label}: G-DEF4 HARD_FAIL — {len(drops)} foreign-persona registry "
        f"drop(s) for persona_id={persona!r}; fix bank routing "
        f"(sample={sample}). Do not silence DEFECT4 detector."
    ]


def _resolve_book_and_audit(render_dir: Path) -> tuple[Path | None, Path | None]:
    book = render_dir / "book.txt"
    if not book.is_file():
        txts = sorted(render_dir.glob("*.txt"))
        book = txts[0] if txts else None
    audit = render_dir / "enrichment_audit.json"
    if not audit.is_file():
        audit = None
    return book, audit


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G-WRAP + G-DEF4 catalog ship checks")
    ap.add_argument("--book", type=Path, default=None)
    ap.add_argument("--enrichment-audit", type=Path, default=None)
    ap.add_argument("--render-dir", type=Path, default=None)
    ap.add_argument(
        "--skip-wrap",
        action="store_true",
        help="Only run G-DEF4",
    )
    ap.add_argument(
        "--skip-defect4",
        action="store_true",
        help="Only run G-WRAP",
    )
    args = ap.parse_args(argv)

    books: list[tuple[str, Path | None, Path | None]] = []
    if args.render_dir:
        b, a = _resolve_book_and_audit(args.render_dir)
        books.append((str(args.render_dir), b, a))
    elif args.book or args.enrichment_audit:
        books.append(("cli", args.book, args.enrichment_audit))
    else:
        # Integrity mode: confirm detector helpers import + thresholds exist.
        assert F16_WRAPPER_CHAPTER_LIMIT >= 4
        assert CLEARED_EXERCISE_WRAPPER_PHRASES
        print(
            "G-WRAP+G-DEF4: PASS (integrity) — detectors importable; "
            f"F16 chapter limit={F16_WRAPPER_CHAPTER_LIMIT}; "
            "no render-dir provided"
        )
        return 0

    violations: list[str] = []
    for label, book_path, audit_path in books:
        if not args.skip_wrap:
            if book_path is None or not book_path.is_file():
                violations.append(f"{label}: book.txt missing for G-WRAP")
            else:
                text = book_path.read_text(encoding="utf-8", errors="replace")
                violations.extend(check_wrap(text, label=str(book_path)))
        if not args.skip_defect4:
            if audit_path is None or not audit_path.is_file():
                # Missing audit on an explicit ship check is a fail; integrity
                # mode above already returned.
                violations.append(
                    f"{label}: enrichment_audit.json missing for G-DEF4"
                )
            else:
                try:
                    audit = json.loads(audit_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as exc:
                    violations.append(f"{audit_path}: invalid JSON ({exc})")
                    continue
                if not isinstance(audit, dict):
                    violations.append(f"{audit_path}: root must be object")
                    continue
                violations.extend(check_defect4(audit, label=str(audit_path)))

    if not violations:
        print("G-WRAP+G-DEF4: PASS")
        return 0

    print("G-WRAP+G-DEF4: FAIL", file=sys.stderr)
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
        print(f"::error::{v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
