#!/usr/bin/env python3
"""
Generate Global Brand Registry — 24 brands × 13 lanes = 312 brand instances.

Reads teacher_brand_map.yaml + locale_registry.yaml + brand_archetype_registry.yaml
and produces the full global_brand_registry.yaml.

Usage:
    python scripts/brand_management/generate_global_registry.py --all-lanes
    python scripts/brand_management/generate_global_registry.py --lane en_US
    python scripts/brand_management/generate_global_registry.py --verify
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    print("pyyaml required")
    sys.exit(1)


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


LANES = [
    "en_US", "zh_TW", "zh_HK", "zh_CN", "zh_SG",
    "ja_JP", "ko_KR", "es_US", "es_ES", "fr_FR",
    "de_DE", "it_IT", "hu_HU",
]


def generate_registry(lanes: list[str] | None = None) -> dict:
    """Generate the full global brand registry."""
    teacher_map = _load_yaml(REPO_ROOT / "config" / "brand_management" / "teacher_brand_map.yaml")
    corp_structure = _load_yaml(REPO_ROOT / "config" / "brand_management" / "corporate_structure.yaml")
    locale_reg = _load_yaml(REPO_ROOT / "config" / "localization" / "locale_registry.yaml")

    teacher_brands = teacher_map.get("teacher_brands") or {}
    non_teacher_brands = teacher_map.get("non_teacher_brands") or {}
    global_mission = teacher_map.get("global_mission", "")

    target_lanes = lanes or LANES
    brands = {}
    admin_counter = 0

    for lane_id in target_lanes:
        locale_key = lane_id.replace("_", "-")  # en_US → en-US for locale_registry
        locale_data = (locale_reg.get("locales") or {}).get(locale_key) or {}
        language = locale_data.get("language", lane_id.split("_")[0])
        region = locale_data.get("region", lane_id.split("_")[1] if "_" in lane_id else "")

        # Resolve corp info
        corp_info = {}
        if lane_id == "en_US":
            corp_info = {"model": "us_nonprofit", "entity_type": "501(c)(3)"}
        else:
            for group_key in ("asian_lanes", "european_lanes"):
                group = corp_structure.get(group_key) or {}
                if lane_id in group:
                    corp_info = group[lane_id]
                    break

        # ── Teacher brands (13 per lane) ──
        for brand_archetype_id, brand_data in teacher_brands.items():
            admin_counter += 1
            display_names = brand_data.get("display_names") or {}
            display_name = display_names.get(lane_id, brand_archetype_id.replace("_", " ").title())

            brand_id = f"{brand_archetype_id}_{lane_id.lower()}"
            brands[brand_id] = {
                "brand_id": brand_id,
                "brand_archetype_id": brand_archetype_id,
                "lane_id": lane_id,
                "locale": locale_key,
                "language": language,
                "region": region,
                "display_name": display_name,
                "teacher_id": brand_data.get("teacher_id"),
                "teacher_mode": True,
                "tradition": brand_data.get("tradition", ""),
                "brand_focus": brand_data.get("brand_focus", ""),
                "content_families": brand_data.get("content_families", []),
                "primary_topics": brand_data.get("primary_topics", []),
                "primary_personas": brand_data.get("primary_personas", []),
                "lifecycle": "active",
                "admin_id": f"admin_{admin_counter:04d}",
                "corp": _resolve_corp(lane_id, brand_archetype_id, brand_data, corp_info),
                "mission": global_mission,
            }

        # ── Non-teacher brands (11 per lane) ──
        for brand_archetype_id, brand_data in non_teacher_brands.items():
            admin_counter += 1
            # Generate localized display name (simple title case for now)
            display_name = brand_archetype_id.replace("_", " ").title()

            brand_id = f"{brand_archetype_id}_{lane_id.lower()}"
            brands[brand_id] = {
                "brand_id": brand_id,
                "brand_archetype_id": brand_archetype_id,
                "lane_id": lane_id,
                "locale": locale_key,
                "language": language,
                "region": region,
                "display_name": display_name,
                "teacher_id": None,
                "teacher_mode": False,
                "brand_focus": brand_data.get("brand_focus", ""),
                "content_families": brand_data.get("content_families", []),
                "primary_topics": brand_data.get("primary_topics", []),
                "primary_personas": brand_data.get("primary_personas", []),
                "lifecycle": "active",
                "admin_id": f"admin_{admin_counter:04d}",
                "corp": _resolve_corp(lane_id, brand_archetype_id, brand_data, corp_info),
                "mission": global_mission,
            }

    return {
        "schema_version": "1.0",
        "generated_by": "generate_global_registry.py",
        "total_brands": len(brands),
        "total_lanes": len(target_lanes),
        "brands_per_lane": 24,
        "teacher_brands_per_lane": 13,
        "non_teacher_brands_per_lane": 11,
        "brands": brands,
    }


def _resolve_corp(lane_id: str, brand_id: str, brand_data: dict, corp_info: dict) -> dict:
    """Resolve corporate entity for a brand."""
    if lane_id == "en_US":
        # US: each brand has its own non-profit church
        church_name = brand_data.get("church_name_us", f"{brand_id.replace('_', ' ').title()} Fellowship")
        return {
            "entity_type": "501(c)(3) non-profit church publication",
            "name": church_name,
            "alignment": brand_data.get("church_alignment", brand_data.get("brand_focus", "")),
        }
    else:
        # Non-US: shared corp per lane
        return {
            "entity_type": corp_info.get("entity_type", "LLC"),
            "name": corp_info.get("corp_name", f"Phoenix Omega {lane_id}"),
            "shared": True,
        }


def verify_registry(path: Path) -> dict:
    """Verify the generated registry."""
    data = _load_yaml(path)
    brands = data.get("brands") or {}
    lanes = set()
    teacher_count = {}
    non_teacher_count = {}

    for bid, bdata in brands.items():
        lane = bdata.get("lane_id", "?")
        lanes.add(lane)
        if bdata.get("teacher_mode"):
            teacher_count[lane] = teacher_count.get(lane, 0) + 1
        else:
            non_teacher_count[lane] = non_teacher_count.get(lane, 0) + 1

    return {
        "total_brands": len(brands),
        "total_lanes": len(lanes),
        "lanes": sorted(lanes),
        "teacher_per_lane": teacher_count,
        "non_teacher_per_lane": non_teacher_count,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate global brand registry")
    parser.add_argument("--all-lanes", action="store_true", help="Generate for all 13 lanes")
    parser.add_argument("--lane", help="Generate for a single lane")
    parser.add_argument("--verify", action="store_true", help="Verify existing registry")
    parser.add_argument("--output", default="config/brand_management/global_brand_registry.yaml")
    args = parser.parse_args()

    output_path = REPO_ROOT / args.output

    if args.verify:
        if not output_path.exists():
            print(f"Registry not found: {output_path}")
            return 1
        result = verify_registry(output_path)
        print(f"Total brands: {result['total_brands']}")
        print(f"Total lanes: {result['total_lanes']}")
        for lane in result["lanes"]:
            t = result["teacher_per_lane"].get(lane, 0)
            nt = result["non_teacher_per_lane"].get(lane, 0)
            print(f"  {lane}: {t} teacher + {nt} non-teacher = {t + nt}")
        return 0

    if args.all_lanes:
        lanes = None  # all
    elif args.lane:
        lanes = [args.lane]
    else:
        parser.error("Specify --all-lanes or --lane")
        return 1

    registry = generate_registry(lanes)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        yaml.dump(registry, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120),
        encoding="utf-8",
    )
    print(f"Generated: {output_path}")
    print(f"  Brands: {registry['total_brands']}")
    print(f"  Lanes: {registry['total_lanes']}")
    print(f"  Teacher brands/lane: {registry['teacher_brands_per_lane']}")
    print(f"  Non-teacher brands/lane: {registry['non_teacher_brands_per_lane']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
