#!/usr/bin/env python3
"""Run an episode-scale structural assembly lane with deterministic fixture support."""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Any, Callable

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

from integrate_real_v5_structural import integrate_workspace  # noqa: E402


def _story_beat_map(path: Path | None) -> dict[str, dict[str, Any]]:
    if not path:
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("panels") or data.get("beats") or []
    return {
        str(row.get("panel_id")): dict(row)
        for row in rows
        if isinstance(row, dict) and row.get("panel_id")
    }


def run_episode(
    *,
    episode_root: Path,
    out_dir: Path,
    story_plan: Path | None = None,
    fail_fast: bool = True,
    assembler: Callable[..., Any] | None = None,
) -> dict[str, Any]:
    structural_dir = out_dir / "structural_panels"
    index = integrate_workspace(
        workspace=episode_root,
        out_dir=structural_dir,
        fail_fast=fail_fast,
        assembler=assembler,
    )
    beat_map = _story_beat_map(story_plan)
    rows: list[dict[str, Any]] = []
    for panel in index["panels"]:
        beat = beat_map.get(panel["panel_id"], {})
        rows.append({
            "panel_id": panel["panel_id"],
            "story_beat": beat.get("beat_id") or beat.get("story_beat") or "",
            "raw_layer_status": "not-green",
            "selected_candidate": panel.get("selected_candidate", ""),
            "removed_px": panel.get("removed_px", ""),
            "support_mode": beat.get("support_mode", ""),
            "gate_status": panel["status"],
            "final_image_path": panel.get("final_image", ""),
            "error": panel.get("error", ""),
        })

    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "panel_status.tsv").open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]) if rows else ["panel_id"], delimiter="\t")
        writer.writeheader()
        writer.writerows(rows)
    episode_manifest = {
        "schema_version": "1.0.0",
        "episode_root": str(episode_root),
        "panel_count": len(rows),
        "panels": rows,
        "manga-batch-episode-lane": "green" if rows and all(r["gate_status"] == "green" for r in rows) else "partial",
        "live-gpu-required-for-ci": "no",
        "overall-manga-green": "NOT_PROVEN",
    }
    (out_dir / "episode_manifest.json").write_text(
        json.dumps(episode_manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    gate_summary = {
        "panel_count": len(rows),
        "passed": sum(r["gate_status"] == "green" for r in rows),
        "failed": sum(r["gate_status"] != "green" for r in rows),
    }
    (out_dir / "gate_summary.json").write_text(
        json.dumps(gate_summary, indent=2) + "\n",
        encoding="utf-8",
    )
    return episode_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--episode", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--story-plan", type=Path)
    parser.add_argument("--structural-assemble-real-v5", action="store_true")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fail-fast", action="store_true")
    group.add_argument("--continue-on-panel-fail", action="store_true")
    args = parser.parse_args()
    if not args.structural_assemble_real_v5:
        print("ERROR: --structural-assemble-real-v5 is required for this production lane", file=sys.stderr)
        return 2
    try:
        result = run_episode(
            episode_root=args.episode,
            out_dir=args.out_dir,
            story_plan=args.story_plan,
            fail_fast=not args.continue_on_panel_fail,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result["manga-batch-episode-lane"] == "green" else 2


if __name__ == "__main__":
    raise SystemExit(main())
