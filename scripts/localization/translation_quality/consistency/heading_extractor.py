#!/usr/bin/env python3
"""Chapter-title/heading extractor.

Extracts every header ID (`## SHAPE vNN`) present across a locale's
localized CANONICAL.txt files, alongside the corresponding English
source's header set, and reports any set-difference per file --
deterministic comparison for Claude to scan for consistency issues (a
missing/renumbered heading is a strong signal something upstream went
wrong in the localization pass).

Usage:
    python3 scripts/localization/translation_quality/consistency/heading_extractor.py \\
        --locale zh-CN --atoms-root atoms --out artifacts/qa/headings_zh_cn.json
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]

HEADER_RE = re.compile(r"^##\s+([A-Za-z0-9_]+)\s+v(\d+)\s*$", re.MULTILINE)


def extract_headers(text: str) -> list[str]:
    return [f"{shape}_v{ver}" for shape, ver in HEADER_RE.findall(text)]


def scan_locale(atoms_root: Path, locale: str) -> dict[str, Any]:
    rows: dict[str, Any] = {}
    for localized_path in sorted(atoms_root.rglob(f"locales/{locale}/CANONICAL.txt")):
        source_path = localized_path.parents[2] / "CANONICAL.txt"
        try:
            localized_headers = extract_headers(localized_path.read_text(encoding="utf-8"))
        except OSError:
            continue
        source_headers: list[str] = []
        if source_path.is_file():
            try:
                source_headers = extract_headers(source_path.read_text(encoding="utf-8"))
            except OSError:
                pass

        missing = [h for h in source_headers if h not in localized_headers]
        extra = [h for h in localized_headers if h not in source_headers]
        duplicates = sorted({h for h in localized_headers if localized_headers.count(h) > 1})

        if missing or extra or duplicates:
            rel = str(localized_path.relative_to(REPO_ROOT))
            rows[rel] = {
                "source_header_count": len(source_headers),
                "localized_header_count": len(localized_headers),
                "missing": missing,
                "extra": extra,
                "duplicates": duplicates,
            }
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--locale", required=True)
    ap.add_argument("--atoms-root", type=Path, default=REPO_ROOT / "atoms")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args(argv)

    rows = scan_locale(args.atoms_root, args.locale)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(rows, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {args.out}: {len(rows)} files with a header set-difference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
