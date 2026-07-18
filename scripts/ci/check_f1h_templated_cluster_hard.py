#!/usr/bin/env python3
"""
G-F1H — templated paragraph cluster HARD_FAIL escalation.

Per PEARL_PRIME_PERFECT_BOOKS_SPEC.md #3.B: register_gate's F1 detector already
FAILs a book when a templated-paragraph cluster reaches size >= 3 (see
phoenix_v4/quality/register_gate.py _detect_f1_templated_paragraphs). That
existing severity ladder (WARN at 2, FAIL at 3+) is untouched by this gate.

G-F1H is an *additive* catalog-ship escalation on top of it: when the same
templated paragraph spreads across >= G_F1H_CHAPTER_LIMIT distinct chapters,
that is visible cross-book machinery (a reader will notice a near-identical
paragraph parachuted into 6+ chapters), not just a local repeat — HARD_FAIL
for catalog ship, never advisory.

This script does NOT re-implement F1 similarity detection (no double-counting
of severities) — it re-uses register_gate's existing
_detect_f1_templated_paragraphs()/_split_chapters() findings and only adds the
>=6-distinct-chapters escalation rule that register_gate does not apply today.

Authority: artifacts/qa/pearl_prime_100book_analysis_20260718/PEARL_PRIME_PERFECT_BOOKS_SPEC.md #3.B (G-F1H row)

Usage:
  PYTHONPATH=. python3 scripts/ci/check_f1h_templated_cluster_hard.py  # integrity mode
  PYTHONPATH=. python3 scripts/ci/check_f1h_templated_cluster_hard.py --book path/to/book.txt
  PYTHONPATH=. python3 scripts/ci/check_f1h_templated_cluster_hard.py --render-dir artifacts/rendered/catalog_assembly/brand/book_id

Exit: 0 pass; 1 HARD_FAIL.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.register_gate import (  # noqa: E402
    _detect_f1_templated_paragraphs,
    _split_chapters,
)

# Spec #3.B G-F1H: "HARD_FAIL when any cluster size >= 6 chapters". F1 itself
# already FAILs at instance-cluster-size >= 3 (distinct paragraph instances,
# which may repeat within one chapter); G-F1H measures DISTINCT CHAPTER BREADTH
# of a cluster, escalating only when the templating has spread catalog-visibly.
G_F1H_CHAPTER_LIMIT = 6


def find_hard_fail_clusters(book_text: str) -> list[dict]:
    """Return G-F1H HARD_FAIL cluster records for a rendered book.txt."""
    chapters = _split_chapters(book_text)
    findings = _detect_f1_templated_paragraphs(chapters)
    hard: list[dict] = []
    for f in findings:
        instances = list(f.evidence.get("instances") or [])
        distinct_chapters = sorted({int(i["chapter"]) for i in instances})
        if len(distinct_chapters) >= G_F1H_CHAPTER_LIMIT:
            hard.append(
                {
                    "cluster_id": f.evidence.get("cluster_id"),
                    "distinct_chapters": distinct_chapters,
                    "chapter_count": len(distinct_chapters),
                    "instance_count": len(instances),
                    "excerpt": f.evidence.get("excerpt", ""),
                    "f1_severity": f.severity,
                }
            )
    return hard


def check_book(book_path: Path) -> list[str]:
    text = book_path.read_text(encoding="utf-8", errors="replace")
    hard = find_hard_fail_clusters(text)
    violations: list[str] = []
    for cluster in hard:
        violations.append(
            f"{book_path}: G-F1H HARD_FAIL — templated paragraph cluster "
            f"{cluster['cluster_id']} spans {cluster['chapter_count']} chapters "
            f"(>= {G_F1H_CHAPTER_LIMIT}) chapters={cluster['distinct_chapters']} "
            f"excerpt={cluster['excerpt']!r}"
        )
    return violations


def _resolve_book(render_dir: Path) -> Path | None:
    book = render_dir / "book.txt"
    if book.is_file():
        return book
    txts = sorted(render_dir.glob("*.txt"))
    return txts[0] if txts else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="G-F1H templated paragraph cluster HARD_FAIL escalation")
    ap.add_argument("--book", type=Path, default=None)
    ap.add_argument("--render-dir", type=Path, default=None)
    args = ap.parse_args(argv)

    book_path: Path | None = None
    if args.book:
        book_path = args.book
    elif args.render_dir:
        book_path = _resolve_book(args.render_dir)
        if book_path is None:
            print(f"G-F1H: FAIL — no book.txt found under {args.render_dir}", file=sys.stderr)
            return 1

    if book_path is None:
        # Integrity mode: confirm the detector import + threshold contract hold.
        assert G_F1H_CHAPTER_LIMIT >= 6
        assert callable(_detect_f1_templated_paragraphs)
        print(
            "G-F1H: PASS (integrity) — detector importable; "
            f"chapter limit={G_F1H_CHAPTER_LIMIT}; no --book/--render-dir provided"
        )
        return 0

    if not book_path.is_file():
        print(f"G-F1H: FAIL — book path missing: {book_path}", file=sys.stderr)
        return 1

    violations = check_book(book_path)
    if not violations:
        print(f"G-F1H: PASS — {book_path} has no cluster spanning >= {G_F1H_CHAPTER_LIMIT} chapters")
        return 0

    print("G-F1H: HARD_FAIL", file=sys.stderr)
    for v in violations:
        print(f"  - {v}", file=sys.stderr)
        print(f"::error::{v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
