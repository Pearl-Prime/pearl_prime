#!/usr/bin/env python3
"""Validate manga author names for collisions.

CI-checkable script that:
1. Checks no manga author display_name collides with pen name authors.
2. Checks no two manga authors within the same brand share a display_name.
3. Checks all author_ids are globally unique.

Exit code 0 = all clear.  Exit code 1 = collisions found.

Usage:
    python scripts/manga/validate_manga_author_collisions.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.manga.generate_manga_author import (
    load_existing_manga_authors,
    load_pen_name_display_names,
)


def validate_all() -> list[str]:
    """Run all collision checks.  Returns list of error strings."""
    errors: list[str] = []
    pen_names = load_pen_name_display_names()
    manga_authors = load_existing_manga_authors()

    # 1. No manga author name matches a pen name author
    for a in manga_authors:
        dn = a.get("display_name", "")
        if dn in pen_names:
            errors.append(
                f"PEN_NAME_COLLISION: manga author '{dn}' "
                f"(id={a.get('author_id')}) collides with pen name author"
            )

    # 2. No duplicate display_name within the same brand
    brand_names: dict[str, list[str]] = {}
    for a in manga_authors:
        bid = a.get("brand_id", "")
        dn = a.get("display_name", "")
        brand_names.setdefault(bid, []).append(dn)
    for bid, names in brand_names.items():
        seen: set[str] = set()
        for n in names:
            if n in seen:
                errors.append(
                    f"BRAND_DUPLICATE: display_name '{n}' appears multiple "
                    f"times for brand '{bid}'"
                )
            seen.add(n)

    # 3. All author_ids globally unique
    ids_seen: set[str] = set()
    for a in manga_authors:
        aid = a.get("author_id", "")
        if aid in ids_seen:
            errors.append(f"ID_DUPLICATE: author_id '{aid}' is not unique")
        ids_seen.add(aid)

    return errors


def main() -> int:
    errors = validate_all()
    if errors:
        print(f"FAIL: {len(errors)} collision(s) found:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK: no manga author collisions detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
