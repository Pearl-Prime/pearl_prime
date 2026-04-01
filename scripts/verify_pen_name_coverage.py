#!/usr/bin/env python3
"""Verify pen-name author system coverage and recovered counts."""
from __future__ import annotations

import json
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover - depends on environment
    raise SystemExit(f"PyYAML required: {exc}")


REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def main() -> int:
    brand_registry = _load_yaml(REPO_ROOT / "config" / "brand_registry.yaml")
    brand_archetypes = _load_yaml(REPO_ROOT / "config" / "catalog_planning" / "brand_archetype_registry.yaml")
    author_assignments = _load_yaml(REPO_ROOT / "config" / "brand_author_assignments.yaml")
    narrator_assignments = _load_yaml(REPO_ROOT / "config" / "brand_narrator_assignments.yaml")
    teacher_yaml = _load_yaml(REPO_ROOT / "config" / "authoring" / "pen_name_teacher_profiles.yaml")

    with open(REPO_ROOT / "config" / "authoring" / "pen_name_teacher_profiles_full.json", encoding="utf-8") as handle:
        teacher_json = json.load(handle)

    registry_brands = set((brand_registry.get("brands") or {}).keys())
    archetype_brands = {entry["brand_id"] for entry in (brand_archetypes.get("brand_archetypes") or [])}
    known_brands = registry_brands | archetype_brands

    author_rows = author_assignments.get("assignments") or []
    narrator_rows = narrator_assignments.get("assignments") or []
    teacher_map = teacher_yaml.get("teachers") or {}

    author_brands = {row.get("brand_id") for row in author_rows if row.get("brand_id")}
    narrator_brands = {row.get("brand_id") for row in narrator_rows if row.get("brand_id")}
    author_slots = [slot.get("author_id") for row in author_rows for slot in (row.get("author_pool") or []) if slot.get("author_id")]
    json_teacher_ids = [row.get("teacher_id") for row in teacher_json if row.get("teacher_id")]

    scenario_total = sum(
        len(values)
        for row in teacher_json
        for values in (row.get("scenario_seeds") or {}).values()
        if isinstance(values, list)
    )
    hook_total = sum(
        len(values)
        for row in teacher_json
        for values in (row.get("hook_atoms") or {}).values()
        if isinstance(values, list)
    )

    missing_author_brands = sorted(known_brands - author_brands)
    missing_narrator_brands = sorted(known_brands - narrator_brands)
    missing_yaml_ids = sorted(set(json_teacher_ids) - set(teacher_map))
    missing_json_ids = sorted(set(teacher_map) - set(json_teacher_ids))

    print("=== PEN-NAME COVERAGE VERIFICATION ===")
    print(f"Known brands: {len(known_brands)}")
    print(f"Author assignment brands: {len(author_brands)}")
    print(f"Narrator assignment brands: {len(narrator_brands)}")
    print(f"Author pool slots: {len(author_slots)}")
    print(f"Unique author ids: {len(set(author_slots))}")
    print(f"Teacher YAML entries: {len(teacher_map)}")
    print(f"Teacher JSON rows: {len(teacher_json)}")
    print(f"Teacher JSON unique ids: {len(set(json_teacher_ids))}")
    print(f"Duplicate JSON rows: {len(teacher_json) - len(set(json_teacher_ids))}")
    print(f"Scenario seeds: {scenario_total}")
    print(f"Hook atoms: {hook_total}")

    if missing_author_brands:
        print(f"MISSING author assignment brands: {missing_author_brands}")
    if missing_narrator_brands:
        print(f"MISSING narrator assignment brands: {missing_narrator_brands}")
    if missing_yaml_ids:
        print(f"MISSING teacher ids from YAML: {missing_yaml_ids[:20]}")
    if missing_json_ids:
        print(f"MISSING teacher ids from JSON: {missing_json_ids[:20]}")

    failures = []
    if missing_author_brands:
        failures.append("author assignment coverage")
    if missing_narrator_brands:
        failures.append("narrator assignment coverage")
    if missing_yaml_ids or missing_json_ids:
        failures.append("teacher registry alignment")
    if len(author_slots) != 480:
        failures.append("author slot count")
    if len(teacher_json) != 480:
        failures.append("teacher JSON row count")
    if len(teacher_map) != 452:
        failures.append("teacher YAML count")
    if scenario_total != 7113:
        failures.append("scenario seed total")
    if hook_total != 3506:
        failures.append("hook atom total")

    if failures:
        print(f"FAILURES: {', '.join(failures)}")
        return 1

    print("PASS: pen-name system coverage verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
