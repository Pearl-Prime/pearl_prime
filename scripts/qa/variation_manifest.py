#!/usr/bin/env python3
"""Build a warn-only variation manifest from atom surface inventory."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.inventory.surface_inventory import build_surface_inventory  # noqa: E402


def build_variation_manifest(surface_manifest: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for cell in surface_manifest.get("cells") or []:
        rows.append(
            {
                "cell_id": cell["cell_id"],
                "canonical_path": cell["canonical_path"],
                "surface_key": cell["surface_key"],
                "variant_count": cell["variant_count"],
                "min_variants_per_cell": cell["min_variants_per_cell"],
                "reader_state_entry": cell["reader_state_entry"],
                "reader_state_exit": cell["reader_state_exit"],
                "exercise_policy": cell["exercise_policy"],
                "story_policy": cell["story_policy"],
                "status": cell["status"],
                "warnings": cell["warnings"],
            }
        )
    warn = sum(1 for row in rows if row["status"] == "WARN")
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "warn_only": True,
        "source_inventory_generated_at": surface_manifest.get("generated_at"),
        "rows": rows,
        "stats": {"rows": len(rows), "pass": len(rows) - warn, "warn": warn},
    }


def _markdown(manifest: dict[str, Any]) -> str:
    lines = [
        "# Variation Manifest",
        "",
        f"Generated: {manifest['generated_at']}",
        "Mode: WARN only",
        "",
        "| Cell | Surface | Variants | Min | Status |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for row in manifest["rows"]:
        lines.append(
            f"| `{row['cell_id']}` | {row['surface_key']} | {row['variant_count']} | "
            f"{row['min_variants_per_cell']} | {row['status']} |"
        )
    return "\n".join(lines) + "\n"


def write_variation_manifest(manifest: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "variation_manifest.json"
    md_path = output_dir / "variation_manifest.md"
    json_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(manifest), encoding="utf-8")
    return {"json": json_path, "markdown": md_path}


def main() -> int:
    parser = argparse.ArgumentParser(description="Build warn-only atom variation manifest")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    parser.add_argument("--persona", action="append", dest="personas")
    parser.add_argument("--topic", action="append", dest="topics")
    parser.add_argument("--max-cells", type=int)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    surface = build_surface_inventory(
        repo_root=args.repo_root,
        personas=args.personas,
        topics=args.topics,
        max_cells=args.max_cells,
    )
    manifest = build_variation_manifest(surface)
    paths = write_variation_manifest(manifest, args.output_dir)
    print(f"Variation manifest written: {paths['json']}")
    print(f"Rows: {manifest['stats']['rows']} WARN: {manifest['stats']['warn']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
