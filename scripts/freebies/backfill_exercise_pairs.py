#!/usr/bin/env python3
"""Backfill exercise_pairs.yaml second_app from somatic_app_catalog.yaml."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load_yaml(p: Path) -> dict:
    import yaml
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _dump_yaml(p: Path, data: dict) -> None:
    import yaml
    p.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def _catalog_file_for_exercise(catalog: dict, exercise_id: str) -> str:
    apps = catalog.get("apps") or {}
    if exercise_id in apps:
        return str(apps[exercise_id].get("file") or "")
    # aliases: extended_exhale -> ex04, five_senses_grounding -> ex14, etc.
    aliases = {
        "478_breathing": "478_breathing",
        "extended_exhale": "extended_exhale",
        "five_senses_grounding": "grounding_54321",
        "body_scan": "body_scan",
        "box_breathing": "box_breathing",
        "cyclic_sighing": "cyclic_sighing",
        "sigh_of_relief": "physiological_sigh",
        "bee_breath": "bee_breath",
        "triangle_breathing": "triangle_breathing",
    }
    key = aliases.get(exercise_id, exercise_id)
    if key in apps:
        return str(apps[key].get("file") or "")
    for app_key, row in apps.items():
        if exercise_id.replace("_", "") in app_key.replace("_", ""):
            return str(row.get("file") or "")
    return ""


def main() -> int:
    pairs_path = REPO / "config/freebies/exercise_pairs.yaml"
    catalog_path = REPO / "config/freebies/somatic_app_catalog.yaml"
    pairs = _load_yaml(pairs_path)
    catalog = _load_yaml(catalog_path)
    updated = 0
    for ex_id, row in list(pairs.items()):
        if not isinstance(row, dict):
            continue
        second = row.get("second")
        if not second:
            continue
        if row.get("second_app"):
            continue
        app_file = _catalog_file_for_exercise(catalog, str(second))
        if app_file:
            row["second_app"] = app_file
            updated += 1
    _dump_yaml(pairs_path, pairs)
    print(f"backfilled second_app on {updated} exercise pairs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
