#!/usr/bin/env python3
"""CI entry: secular + shape lint for composite_doctrine CANONICAL.txt files.

Full corpus scan (``--report-all``) lists every violation for Writer-lane triage.
PR/push gate (``--base`` … ``--head``) BLOCKs only when changed doctrine files
introduce or retain violations — legacy corpus debt does not block this gate landing.

Run:
    # Drift detectors (diff-only BLOCK):
    PYTHONPATH=. python3 scripts/quality/check_composite_doctrine_secular.py \\
        --base origin/main --head HEAD
    # Full corpus report (exit 0, for PR body / Writer queue):
    PYTHONPATH=. python3 scripts/quality/check_composite_doctrine_secular.py --report-all
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

sys.path.insert(0, str(REPO_ROOT / "scripts" / "ci"))
from drift_detector_git import changed_paths, repo_root_from_script  # noqa: E402

from phoenix_v4.quality.composite_doctrine_secular_lint import (  # noqa: E402
    lint_canonical_file,
    lint_composite_doctrine_tree,
)


def _doctrine_canonical_in_diff(base: str | None, head: str, repo_root: Path) -> list[Path]:
    prefix = "SOURCE_OF_TRUTH/composite_doctrine/"
    paths: list[Path] = []
    for rel in changed_paths(base, head, repo_root):
        if not rel.startswith(prefix):
            continue
        if not rel.endswith("CANONICAL.txt"):
            continue
        paths.append(repo_root / rel)
    return sorted(paths)


def _format_violation(v) -> str:
    atom = f" [{v.atom_id}]" if v.atom_id else ""
    loc = f"{v.path}:{v.line}" if v.line else v.path
    return f"{loc}{atom}: {v.matched_tell} — {v.excerpt}"


def _run_scan(paths: list[Path] | None = None):
    if paths is None:
        return lint_composite_doctrine_tree()
    violations = []
    for path in paths:
        violations.extend(lint_canonical_file(path))
    return violations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", default=None, help="Diff base ref (diff-only gate)")
    parser.add_argument("--head", default="HEAD", help="Diff head ref (default HEAD)")
    parser.add_argument(
        "--report-all",
        action="store_true",
        help="Scan full corpus; print violations; exit 0 (Writer triage)",
    )
    args = parser.parse_args()
    repo_root = repo_root_from_script(Path(__file__))

    if args.report_all:
        violations = _run_scan()
        if not violations:
            print("composite_doctrine lint report: PASS (0 violations)")
            return 0
        for v in violations:
            print(_format_violation(v))
        print(f"composite_doctrine lint report: {len(violations)} violation(s) (report-only)")
        return 0

    if args.base:
        paths = _doctrine_canonical_in_diff(args.base, args.head, repo_root)
        if not paths:
            print("composite_doctrine lint: SKIP (no composite_doctrine CANONICAL.txt in diff)")
            return 0
        violations = _run_scan(paths)
        scope = f"{len(paths)} changed file(s)"
    else:
        violations = _run_scan()
        scope = "full corpus"

    if not violations:
        print(f"composite_doctrine lint: PASS (0 violations; {scope})")
        return 0
    for v in violations:
        print(_format_violation(v))
    print(f"composite_doctrine lint: FAIL ({len(violations)} violation(s); {scope})")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
