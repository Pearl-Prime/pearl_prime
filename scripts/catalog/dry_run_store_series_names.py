#!/usr/bin/env python3
"""Dry-run store-series names for brand plans without catalog writes."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.naming.generator import (  # noqa: E402
    generate_store_series_candidates,
    is_generic_store_series_name,
)

DEFAULT_PLAN = REPO_ROOT / "config" / "catalog_planning" / "brand_series_plans.yaml"
DEFAULT_OUT = REPO_ROOT / "artifacts" / "qa" / "session_mining_specs_do_all_20260718" / "spec5_series_naming"


def _load_yaml(path: Path) -> dict[str, Any]:
    if yaml is None or not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def build_dry_run(
    *,
    plan_path: Path = DEFAULT_PLAN,
    limit: int | None = None,
    candidates_per_brand: int = 3,
) -> dict[str, Any]:
    data = _load_yaml(plan_path)
    brands = data.get("brands") or {}
    rows: list[dict[str, Any]] = []
    existing_titles: set[str] = set()
    generic_rejects = 0
    collision_rejects = 0
    for brand_id, cfg in sorted(brands.items()):
        if brand_id.startswith(("waystream", "way_stream")):
            continue
        if limit is not None and len(rows) >= limit:
            break
        topic = str((cfg or {}).get("primary_topic") or "anxiety")
        candidates = generate_store_series_candidates(
            brand_id=brand_id,
            topic_id=topic,
            persona_id="general_readers",
            seed="20260718",
            count=candidates_per_brand,
        )
        accepted = []
        rejects = []
        for cand in candidates:
            title = str(cand["series_title"])
            if is_generic_store_series_name(title, topic):
                generic_rejects += 1
                rejects.append({"title": title, "reason": "generic"})
                continue
            if title.lower() in existing_titles:
                collision_rejects += 1
                rejects.append({"title": title, "reason": "collision"})
                continue
            existing_titles.add(title.lower())
            accepted.append(cand)
        rows.append(
            {
                "brand_id": brand_id,
                "topic_id": topic,
                "accepted_candidates": accepted,
                "rejected_candidates": rejects,
            }
        )
    generated = sum(len(row["accepted_candidates"]) for row in rows)
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_plan": str(plan_path.relative_to(REPO_ROOT) if plan_path.is_relative_to(REPO_ROOT) else plan_path),
        "catalog_files_written": False,
        "production_public_release_authorized": False,
        "operator_review_required": True,
        "rows": rows,
        "stats": {
            "brands": len(rows),
            "series_names_generated": generated,
            "generic_rejects": generic_rejects,
            "collision_rejects": collision_rejects,
        },
    }


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Store Series Naming Dry Run",
        "",
        f"Generated: {report['generated_at']}",
        "Catalog files written: no",
        "Production public release authorized: no",
        "",
        "| Brand | Topic | Accepted | First Candidate |",
        "| --- | --- | ---: | --- |",
    ]
    for row in report["rows"]:
        accepted = row["accepted_candidates"]
        first = accepted[0]["series_title"] if accepted else ""
        lines.append(f"| `{row['brand_id']}` | {row['topic_id']} | {len(accepted)} | {first} |")
    return "\n".join(lines) + "\n"


def write_report(report: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "store_series_naming_dry_run.json"
    md_path = output_dir / "store_series_naming_dry_run.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run store series naming for brand plans")
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--candidates-per-brand", type=int, default=3)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    report = build_dry_run(
        plan_path=args.plan,
        limit=args.limit,
        candidates_per_brand=args.candidates_per_brand,
    )
    paths = write_report(report, args.output_dir)
    print(f"Dry-run report written: {paths['json']}")
    print(
        "Brands: {brands} Series names: {series_names_generated} Generic rejects: {generic_rejects}".format(
            **report["stats"]
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
