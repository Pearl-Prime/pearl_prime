#!/usr/bin/env python3
"""Warn-only checker for the atom variation manifest."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.inventory.surface_inventory import build_surface_inventory  # noqa: E402
from scripts.qa.variation_manifest import build_variation_manifest  # noqa: E402


def check_manifest(manifest: dict, *, strict: bool = False) -> tuple[int, list[str]]:
    rows = manifest.get("rows") or manifest.get("cells") or []
    warnings: list[str] = []
    for row in rows:
        row_warnings = row.get("warnings") or []
        if row_warnings or row.get("status") == "WARN":
            warnings.append(f"{row.get('cell_id')}: {', '.join(row_warnings) or 'WARN'}")
    if warnings and strict:
        return 1, warnings
    return 0, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description="Check warn-only atom variation manifest")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--persona", action="append", dest="personas")
    parser.add_argument("--topic", action="append", dest="topics")
    parser.add_argument("--max-cells", type=int)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if args.manifest:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    else:
        surface = build_surface_inventory(
            repo_root=args.repo_root,
            personas=args.personas,
            topics=args.topics,
            max_cells=args.max_cells,
        )
        manifest = build_variation_manifest(surface)

    code, warnings = check_manifest(manifest, strict=args.strict)
    if warnings:
        print(f"WARN_ONLY variation findings: {len(warnings)}")
        for warning in warnings[:25]:
            print(f"WARN {warning}")
    else:
        print("PASS variation manifest")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
