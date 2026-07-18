#!/usr/bin/env python3
"""Expand freebie_to_landing.yaml with somatic app catalog entries."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load_yaml(p: Path) -> dict:
    import yaml
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _dump_yaml(p: Path, data: dict) -> None:
    import yaml
    header = (
        "# Maps freebie_id / somatic app ids to landing paths.\n"
        "# somatic_apps: catalog id -> file (E1/E2 email link generation).\n"
        "# funnel_slug_routes: unchanged SEO slugs.\n\n"
    )
    p.write_text(header + yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def main() -> int:
    landing_path = REPO / "config/freebies/freebie_to_landing.yaml"
    catalog_path = REPO / "config/freebies/somatic_app_catalog.yaml"
    landing = _load_yaml(landing_path)
    catalog = _load_yaml(catalog_path)
    somatic_map = landing.get("somatic_apps") or {}
    for app_id, row in (catalog.get("apps") or {}).items():
        file_name = row.get("file")
        if not file_name:
            continue
        somatic_map[app_id] = {
            "file": file_name,
            "url": row.get("url") or f"/somatic_exercise_freebee_apps/{file_name}",
            "e1_eligible": bool(row.get("e1_eligible")),
            "e2_eligible": bool(row.get("e2_eligible")),
        }
    landing["somatic_apps"] = somatic_map
    _dump_yaml(landing_path, landing)
    print(f"somatic_apps: {len(somatic_map)} entries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
