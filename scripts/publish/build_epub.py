#!/usr/bin/env python3
"""scripts/publish/build_epub.py — operator-facing publishing entry point.

Thin wrapper around scripts/release/build_epub.py. Forwards all arguments
to the backend `main()` and returns its exit code unchanged.

WHY THIS WRAPPER EXISTS
-----------------------
The Phoenix Omega 100% production pathway doc
(docs/PHOENIX_OMEGA_PATHWAY_TO_100_2026-04-29.md, deliverable D-1.2) names
`scripts/publish/build_epub.py` as the EPUB packager command. The actual
builder predates that doc and lives at `scripts/release/build_epub.py`.

Rather than move the working backend (high blast radius — would break
every existing caller in artifacts/, tests, and operator scripts), this
wrapper exposes the publish-namespace path while preserving the backend
unchanged. Future PRs may consolidate one direction or the other; this
wrapper remains stable until then.

Companion validator: `scripts/publish/validate_epub.py`.

USAGE
-----
This wrapper accepts every flag the backend accepts. It forwards them
verbatim. Exit code = backend exit code.

  # Single-book build (preferred operator command surface)
  python3 scripts/publish/build_epub.py \\
      --input artifacts/pipeline_examples/ahjan/book_ahjan_anxiety_15min.txt \\
      --title "The Alarm Is Lying" \\
      --author "Lena Thorne" \\
      --teacher "Ahjan" \\
      --cover artifacts/pipeline_examples/ahjan/cover_ahjan_anxiety.png \\
      --output artifacts/epub/ahjan_anxiety.epub

  # NOTE: --author is a brand PEN-NAME; the teacher goes in --teacher and is
  # credited separately ("Teaching by <teacher>"). A teacher name is NEVER the
  # primary author (Q-TEACHERMODE-BYLINE-01 / OPD-20260701-001).

  # Batch build (all 13 teacher books)
  python3 scripts/publish/build_epub.py --batch

  # Dry-run
  python3 scripts/publish/build_epub.py --batch --dry-run

  # Help (shows the backend's flag set)
  python3 scripts/publish/build_epub.py --help

Then validate:

  python3 scripts/publish/validate_epub.py --batch artifacts/epub/

OPERATOR NOTE
-------------
A direct invocation of `python3 scripts/release/build_epub.py ...` still
works and produces identical output. This wrapper is the recommended
publish-namespace entry point per the pathway doc.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

# Re-export the backend's main(); call it as the entry point. We import
# lazily inside main() so that tests / callers that only want the module
# don't pay the ebooklib import cost when they don't need it.


def main() -> int:
    """Forward to scripts.release.build_epub.main(). Return its exit code."""
    from scripts.release import build_epub as _backend
    rc = _backend.main()
    # Backend's main() returns None on success; normalize to 0.
    return int(rc) if isinstance(rc, int) else 0


if __name__ == "__main__":
    sys.exit(main())
