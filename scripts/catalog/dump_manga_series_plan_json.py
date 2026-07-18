#!/usr/bin/env python3
"""
Dump config/manga/manga_brand_series_plan.yaml as JSON for PhoenixControl.
Outputs a JSON array of brand plan objects to stdout.
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_CONFIG_ROOT = (
    _MAIN_REPO
    if not (REPO_ROOT / "config" / "brand_management").exists()
    and (_MAIN_REPO / "config" / "brand_management").exists()
    else REPO_ROOT
)


def find_plan_path() -> Path | None:
    for root in [REPO_ROOT, _CONFIG_ROOT]:
        p = root / "config/manga/manga_brand_series_plan.yaml"
        if p.exists():
            return p
    return None


def main() -> None:
    try:
        import yaml
    except ImportError:
        print(json.dumps({"error": "PyYAML required. pip install pyyaml"}))
        sys.exit(0)

    plan_path = find_plan_path()
    if not plan_path:
        print(json.dumps({"error": "manga_brand_series_plan.yaml not found"}))
        sys.exit(0)

    with open(plan_path, "r", encoding="utf-8") as fh:
        plan = yaml.safe_load(fh)

    brands = plan.get("brands", {})
    result = []
    for brand_id, data in brands.items():
        topic_alloc = {}
        for k, v in data.get("topic_allocation", {}).items():
            topic_alloc[k] = str(v)

        webtoon = data.get("webtoon_format", {})
        platform_cadence = webtoon.get("platform_cadence", {})

        rotation = data.get("series_rotation", {})

        result.append({
            "brand_id": brand_id,
            "teacher": data.get("teacher", ""),
            "genre": data.get("genre", ""),
            "primary_lane": data.get("primary_lane", "english_global"),
            "active_series_target": data.get("active_series_target", 3),
            "new_series_per_year": data.get("new_series_per_year", 4),
            "chapters_per_series_per_month": data.get("chapters_per_series_per_month", 2),
            "max_chapters_before_volume": data.get("max_chapters_before_volume", 10),
            "volumes_per_year_target": data.get("volumes_per_year_target", 6),
            "topic_allocation": topic_alloc,
            "webtoon_enabled": webtoon.get("enabled", True),
            "platform_cadence": {k: str(v) for k, v in platform_cadence.items()},
            "max_dormant_months": rotation.get("max_dormant_months", 3),
            "overlap_new_old_weeks": rotation.get("overlap_new_old_weeks", 2),
        })

    print(json.dumps(result))


if __name__ == "__main__":
    main()
