#!/usr/bin/env python3
"""Set status: installed on FONT_REGISTRY entries whose font files exist on disk."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
REGISTRY = REPO_ROOT / "fonts" / "manga" / "FONT_REGISTRY.yaml"
BASE = REPO_ROOT / "fonts" / "manga"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--registry",
        type=Path,
        default=REGISTRY,
        help="Path to FONT_REGISTRY.yaml",
    )
    ap.add_argument(
        "--mark-installed",
        action="store_true",
        help="Update registry in place for existing font files",
    )
    args = ap.parse_args()
    data = yaml.safe_load(args.registry.read_text(encoding="utf-8")) or {}
    fonts = data.get("fonts") or []
    if not args.mark_installed:
        return 0
    changed = False
    for entry in fonts:
        if not isinstance(entry, dict):
            continue
        rel = entry.get("path")
        if not rel:
            continue
        p = (BASE / str(rel)).resolve()
        if p.is_file():
            if entry.get("status") != "installed":
                entry["status"] = "installed"
                changed = True
        else:
            if entry.get("status") == "installed":
                entry["status"] = "pending"
                changed = True
    if changed:
        args.registry.write_text(
            yaml.dump(data, sort_keys=False, allow_unicode=True) + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
