#!/usr/bin/env python3
"""
Manga asset estimator — planning rollups from brand_series_plans + brand_identity_system.

Reads:
  config/catalog_planning/brand_series_plans.yaml
  config/catalog_planning/brand_identity_system.yaml

Estimates per brand: panels/chapter (min/opt/max), backgrounds, character view count,
GPU USD, human labor USD, scaled by --weeks (default 4 = one planning month block).

Usage:
  python3 scripts/manga/manga_asset_estimator.py --all --weeks 4
  python3 scripts/manga/manga_asset_estimator.py --brand stillness_press --weeks 8
  python3 scripts/manga/manga_asset_estimator.py --all --dry-run
  python3 scripts/manga/manga_asset_estimator.py --all --output artifacts/manga/asset_estimate.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]

try:
    import yaml
except ImportError as e:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from e


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _merge_identity_maps(identity: dict[str, Any]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for key in ("teacher_brands", "standard_brands"):
        block = identity.get(key) or {}
        if isinstance(block, dict):
            for bid, meta in block.items():
                if isinstance(meta, dict):
                    out[str(bid)] = meta
    return out


def _is_series_entry(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    if "package" in obj and "title" not in obj:
        return False
    return "episode_count" in obj or "panel_estimate" in obj


def _iter_lane_series(brand_plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for lane_name in ("heavy_lanes", "medium_lanes"):
        lane = brand_plan.get(lane_name) or {}
        if not isinstance(lane, dict):
            continue
        for slot_key, series in lane.items():
            if not _is_series_entry(series):
                continue
            rows.append({"lane": lane_name, "slot": slot_key, **series})
    return rows


def _estimate_brand(
    brand_id: str,
    brand_plan: dict[str, Any],
    panel_defaults: dict[str, Any],
    identity: dict[str, dict[str, Any]],
    weeks: int,
) -> dict[str, Any]:
    std_ep = int(panel_defaults.get("standard_episode") or 46)
    short_ep = int(panel_defaults.get("short_episode") or 28)

    series_rows = _iter_lane_series(brand_plan)
    per_chapter: list[int] = []
    total_panels = 0
    total_episodes = 0
    topics: set[str] = set()

    for s in series_rows:
        ep = int(s.get("episode_count") or 0)
        pe = s.get("panel_estimate")
        if ep > 0 and pe is not None:
            p = int(pe)
            per_chapter.append(max(1, round(p / ep)))
            total_panels += p
            total_episodes += ep
        elif ep > 0:
            per_chapter.append(std_ep)
            total_panels += std_ep * ep
            total_episodes += ep
        t = s.get("topic") or s.get("angle_source")
        if t:
            topics.add(str(t))

    light = brand_plan.get("light_lanes") or {}
    light_panels = 0
    if isinstance(light, dict):
        covers = int(light.get("cover_count") or 0)
        kv = int(light.get("key_visual_count") or 0)
        # Treat each cover/KV as ~short_episode worth of illustration work
        light_panels = covers * short_ep + kv * max(short_ep // 2, 12)

    if not per_chapter:
        min_pc = short_ep
        opt_pc = std_ep
        max_pc = std_ep
    else:
        min_pc = min(per_chapter)
        max_pc = max(per_chapter)
        opt_pc = int(round(sum(per_chapter) / len(per_chapter)))

    # Backgrounds: distinct story topics + recurring sets per series
    backgrounds = max(6, len(topics) * 4 + len(series_rows) * 3)

    manga_mode = str(brand_plan.get("manga_mode") or "regular")
    teacher = brand_plan.get("teacher")
    if manga_mode == "teacher" and teacher:
        char_factor = 2.2  # teacher + student + recurring extras
        protagonist = str(teacher)
    else:
        char_factor = 1.6
        protagonist = "ensemble_cast"

    # Character "views" = rough shot count across slate (establishing + reverses)
    char_views = int(
        round(
            total_episodes * 10 * char_factor
            + len(series_rows) * 24
            + (light_panels / max(short_ep, 1)) * 4
        )
    )

    panels_with_light = total_panels + light_panels
    week_scale = max(weeks, 1) / 4.0

    # Heuristic economics (internal planning constants — not quotes)
    usd_per_panel_gpu = 0.012
    artist_hours_per_panel = 0.32
    hourly_usd = 78.0

    gpu_cost = round(panels_with_light * usd_per_panel_gpu * week_scale, 2)
    labor_hours = round(panels_with_light * artist_hours_per_panel * week_scale, 1)
    labor_usd = round(labor_hours * hourly_usd, 2)

    id_meta = identity.get(brand_id) or {}
    display_name = id_meta.get("display_name") or brand_id

    return {
        "brand_id": brand_id,
        "display_name": display_name,
        "manga_mode": manga_mode,
        "protagonist_anchor": protagonist,
        "weeks_horizon": weeks,
        "series_count": len(series_rows),
        "total_episodes": total_episodes,
        "panels_total_estimated": int(panels_with_light),
        "panels_heavy_medium": int(total_panels),
        "panels_light_lane_equiv": int(light_panels),
        "panels_per_chapter": {"min": min_pc, "opt": opt_pc, "max": max_pc},
        "backgrounds_estimated": backgrounds,
        "character_view_count_est": char_views,
        "gpu_cost_usd_est": gpu_cost,
        "human_labor_hours_est": labor_hours,
        "human_labor_cost_usd_est": labor_usd,
    }


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    headers = [
        "brand_id",
        "panels/ch (min)",
        "opt",
        "max",
        "bg",
        "char_views",
        "GPU $",
        "labor $",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join(["---"] * len(headers)) + "|",
    ]
    for r in rows:
        ppc = r["panels_per_chapter"]
        lines.append(
            "| "
            + " | ".join(
                [
                    r["brand_id"],
                    str(ppc["min"]),
                    str(ppc["opt"]),
                    str(ppc["max"]),
                    str(r["backgrounds_estimated"]),
                    str(r["character_view_count_est"]),
                    str(r["gpu_cost_usd_est"]),
                    str(r["human_labor_cost_usd_est"]),
                ]
            )
            + " |"
        )
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Estimate manga asset load per brand.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--brand", help="Single brand_id from brand_series_plans.yaml")
    g.add_argument("--all", action="store_true", help="All brands in series plans")
    ap.add_argument("--weeks", type=int, default=4, help="Planning horizon in weeks (default 4)")
    ap.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts/manga/asset_estimate.json",
        help="JSON output path (default: artifacts/manga/asset_estimate.json)",
    )
    ap.add_argument(
        "--dry-run",
        action="store_true",
        help="Print estimates but do not write --output",
    )
    args = ap.parse_args()

    plans_path = REPO_ROOT / "config/catalog_planning/brand_series_plans.yaml"
    identity_path = REPO_ROOT / "config/catalog_planning/brand_identity_system.yaml"
    plans = _load_yaml(plans_path)
    identity_raw = _load_yaml(identity_path)
    identity = _merge_identity_maps(identity_raw)

    panel_defaults = plans.get("panel_estimates") or {}
    brands_block = plans.get("brands") or {}
    if not isinstance(brands_block, dict):
        print("No brands block in brand_series_plans.yaml", file=sys.stderr)
        return 1

    brand_ids = sorted(
        k
        for k, v in brands_block.items()
        if isinstance(v, dict) and k not in ("schema_version", "last_updated")
    )
    if args.brand:
        if args.brand not in brand_ids:
            print(f"Unknown brand {args.brand!r}. Known: {', '.join(brand_ids[:8])}…", file=sys.stderr)
            return 1
        selected = [args.brand]
    else:
        selected = brand_ids

    estimates = [
        _estimate_brand(bid, brands_block[bid], panel_defaults, identity, args.weeks) for bid in selected
    ]

    payload = {
        "schema": "manga_asset_estimate_v1",
        "sources": {
            "brand_series_plans": str(plans_path.relative_to(REPO_ROOT)),
            "brand_identity_system": str(identity_path.relative_to(REPO_ROOT)),
        },
        "weeks": args.weeks,
        "brands": estimates,
        "totals": {
            "panels_total": sum(b["panels_total_estimated"] for b in estimates),
            "gpu_cost_usd": round(sum(b["gpu_cost_usd_est"] for b in estimates), 2),
            "human_labor_cost_usd": round(sum(b["human_labor_cost_usd_est"] for b in estimates), 2),
        },
    }

    print(json.dumps(payload, indent=2))
    print()
    print(_markdown_table(estimates))

    out_path: Path = args.output
    if not args.dry_run:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        print(f"\nWrote {out_path.relative_to(REPO_ROOT)}", file=sys.stderr)
    else:
        print("\n(dry-run: no JSON file written)", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
