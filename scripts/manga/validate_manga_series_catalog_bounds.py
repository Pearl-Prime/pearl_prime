#!/usr/bin/env python3
"""Validate manga_brand_series_plan.yaml against owner catalog bounds and pacing consistency.

Exits 0 on success, 1 on violation (for CI / pre-commit).
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

try:
    import yaml
except ImportError:
    print("PyYAML required", file=sys.stderr)
    sys.exit(1)


def main() -> int:
    path = REPO / "config/manga/manga_brand_series_plan.yaml"
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    gd = raw.get("global_defaults") or {}
    cmin = gd.get("target_series_catalog_min")
    cmax = gd.get("target_series_catalog_max")
    if cmin is None or cmax is None:
        print("global_defaults.target_series_catalog_min/max must be set", file=sys.stderr)
        return 1
    if cmin > cmax:
        print(f"catalog min {cmin} > max {cmax}", file=sys.stderr)
        return 1

    brands = raw.get("brands") or {}
    errors: list[str] = []

    for slug, block in brands.items():
        if not isinstance(block, dict):
            continue
        active = block.get("active_series_target", gd.get("active_series_target"))
        mx = block.get("max_active_series", gd.get("max_active_series"))
        nspy = block.get("new_series_per_year", gd.get("new_series_per_year"))
        if active is None or mx is None:
            errors.append(f"{slug}: missing active_series_target or max_active_series")
            continue
        if active > mx:
            errors.append(f"{slug}: active_series_target {active} > max_active_series {mx}")
        # Simultaneous active portfolio must stay within the long-run catalog ceiling.
        if mx > cmax:
            errors.append(f"{slug}: max_active_series {mx} > target_series_catalog_max {cmax}")
        if nspy is not None and nspy > cmax:
            errors.append(f"{slug}: new_series_per_year {nspy} > target_series_catalog_max {cmax}")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
