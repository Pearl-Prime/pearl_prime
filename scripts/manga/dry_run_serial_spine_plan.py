#!/usr/bin/env python3
"""Dry-run a multivolume manga serial spine using existing serial loader."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.serial.spine_loader import (  # noqa: E402
    build_multivolume_dry_run_plan,
)

DEFAULT_OUT = REPO_ROOT / "artifacts" / "qa" / "session_mining_specs_do_all_20260718" / "spec7_manga_serial_spine"


def _markdown(plan: dict) -> str:
    lines = [
        "# Manga Serial Spine Dry Run",
        "",
        f"Series: `{plan['series_id']}`",
        "Parallel spine created: no",
        "Panel renders: 0",
        "",
        "| Volume | Title | Episodes | Status |",
        "| ---: | --- | ---: | --- |",
    ]
    for row in plan["volume_plans"]:
        lines.append(f"| {row['volume']} | {row['title']} | {len(row['episode_ids'])} | {row['status']} |")
    return "\n".join(lines) + "\n"


def write_plan(plan: dict, output_dir: Path) -> dict[str, Path]:
    if plan.get("validation_errors"):
        raise SystemExit("\n".join(plan["validation_errors"]))
    output_dir.mkdir(parents=True, exist_ok=True)
    safe = plan["series_id"].replace("/", "_")
    json_path = output_dir / f"{safe}.multivolume_spine_dry_run.json"
    md_path = output_dir / f"{safe}.multivolume_spine_dry_run.md"
    json_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(plan), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Dry-run manga multivolume serial spine")
    parser.add_argument("--series-id", required=True)
    parser.add_argument("--episodes-per-volume", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT)
    args = parser.parse_args()
    plan = build_multivolume_dry_run_plan(
        args.series_id,
        episodes_per_volume=args.episodes_per_volume,
        repo_root=REPO_ROOT,
    )
    paths = write_plan(plan, args.output_dir)
    print(f"Manga serial spine dry-run written: {paths['json']}")
    print(f"Volumes: {len(plan['volume_plans'])} Panel renders: {plan['panel_renders']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
