#!/usr/bin/env python3
"""CI entry: secular-lint all composite_doctrine CANONICAL.txt files. Exit 1 on violations."""
from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.quality.composite_doctrine_secular_lint import lint_composite_doctrine_tree


def main() -> int:
    violations = lint_composite_doctrine_tree()
    if not violations:
        print("composite_doctrine secular lint: PASS (0 violations)")
        return 0
    for v in violations:
        print(f"{v.path}:{v.line}: {v.matched_tell} — {v.excerpt}")
    print(f"composite_doctrine secular lint: FAIL ({len(violations)} violation(s))")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
