#!/usr/bin/env python3
"""
Manga Asset Estimator
======================
Given brand / series / chapter counts, estimates:
  - Panel count (min/opt/max) per chapter
  - Background assets needed per chapter and per series
  - Character view sheets needed
  - Weekly/monthly art production hours
  - Approximate cost (GPU compute + human review)

Sources:
  config/manga/character_brand_registry.yaml   (backgrounds_per_chapter, character_views)
  config/manga/manga_brand_series_plan.yaml    (chapters_per_series_per_month, active_series)
  scripts/duration/plan_manga_pages.py         (GENRE_TABLE panel counts)

Usage:
    python3 scripts/manga/manga_asset_estimator.py --brand stillness_press
    python3 scripts/manga/manga_asset_estimator.py --all
    python3 scripts/manga/manga_asset_estimator.py --brand cognitive_clarity --weeks 12
    python3 scripts/manga/manga_asset_estimator.py --all --output artifacts/manga/asset_estimate.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

_WORKTREE = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_REPO_ROOT = _MAIN_REPO if _MAIN_REPO.exists() else _WORKTREE

sys.path.insert(0, str(_REPO_ROOT))

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# Panel count table (mirrors scripts/duration/plan_manga_pages.py GENRE_TABLE)
# ---------------------------------------------------------------------------
GENRE_PANELS: dict[str, tuple[int, int, int]] = {
    # (min_panels, opt_panels, max_panels) per chapter
    "iyashikei":          (20, 28, 40),
    "healing":            (20, 28, 40),
    "seinen":             (30, 40, 55),
    "shojo":              (18, 26, 38),
    "cultivation":        (30, 42, 60),
    "xianxia":            (30, 42, 60),
    "manhwa":             (35, 50, 70),
    "webtoon":            (35, 50, 70),
    "shonen":             (25, 36, 50),
    "isekai":             (28, 40, 58),
    "philosophical_dark": (22, 32, 48),
    "default":            (20, 30, 45),
}

# Background reuse rate — proportion of panels that need a NEW background
# (vs reusing an existing asset from the same chapter)
BG_REUSE_RATE: dict[str, float] = {
    "iyashikei": 0.35,     # rich backgrounds but many reused
    "seinen": 0.45,
    "shojo": 0.30,
    "cultivation": 0.40,
    "manhwa": 0.50,
    "shonen": 0.45,
    "isekai": 0.55,        # new world = more new backgrounds
    "philosophical_dark": 0.38,
    "default": 0.40,
}

# ---------------------------------------------------------------------------
# Cost model
# ---------------------------------------------------------------------------
# GPU compute cost per generated asset (USD, Pearl Star / RunComfy estimates)
COST_PER_PANEL_GPU = 0.04          # ComfyUI FLUX panel rough render
COST_PER_BACKGROUND_GPU = 0.12     # Higher-quality background render
COST_PER_CHARACTER_VIEW_GPU = 0.08 # IP-Adapter character view

# Human review time (minutes per asset type)
REVIEW_MINS_PER_PANEL = 0.5        # quick QA pass
REVIEW_MINS_PER_BG = 3.0           # background review + potential touch-up
REVIEW_MINS_PER_CHARACTER_VIEW = 5.0
REVIEW_MINS_PER_CHAPTER_PASS = 15.0  # full chapter narrative review

HUMAN_HOURLY_RATE_USD = 25.0       # for cost roll-up

# ---------------------------------------------------------------------------
# Loaders
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    if not _HAS_YAML:
        raise ImportError("PyYAML required: pip install pyyaml")
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _load_character_registry() -> dict:
    for base in [_WORKTREE, _REPO_ROOT]:
        p = base / "config/manga/character_brand_registry.yaml"
        if p.exists():
            return _load_yaml(p)
    return {}


def _load_series_plan() -> dict:
    for base in [_WORKTREE, _REPO_ROOT]:
        p = base / "config/manga/manga_brand_series_plan.yaml"
        if p.exists():
            return _load_yaml(p)
    return {}


# ---------------------------------------------------------------------------
# Estimator core
# ---------------------------------------------------------------------------

def estimate_brand(
    brand_id: str,
    brand_registry: dict,
    series_plan: dict,
    weeks: int = 4,
) -> dict:
    """Produce asset estimate for one brand over `weeks` weeks."""
    reg_entry = brand_registry.get("brands", {}).get(brand_id, {})
    plan_entry = series_plan.get("brands", {}).get(brand_id, {})
    global_defaults = series_plan.get("global_defaults", {})

    genre = reg_entry.get("genre") or plan_entry.get("genre", "default")
    panels = GENRE_PANELS.get(genre, GENRE_PANELS["default"])
    panels_min, panels_opt, panels_max = panels
    bg_rate = BG_REUSE_RATE.get(genre, BG_REUSE_RATE["default"])

    # Series/chapter cadence from plan
    chapters_per_month = plan_entry.get(
        "chapters_per_series_per_month",
        global_defaults.get("chapters_per_series_per_month", 2),
    )
    active_series = plan_entry.get(
        "active_series_target",
        global_defaults.get("active_series_target", 3),
    )
    chapters_per_month_total = chapters_per_month * active_series
    chapters_in_window = round(chapters_per_month_total * (weeks / 4.0))

    # Backgrounds from registry (per-chapter spec)
    bg_per_chapter_spec = reg_entry.get("asset_notes", {}).get("backgrounds_per_chapter")
    if bg_per_chapter_spec is None:
        bg_per_chapter_spec = round(panels_opt * bg_rate)

    # Character views (one-time setup cost, amortised over first run)
    char_views_list = reg_entry.get("asset_notes", {}).get("character_views_needed", [])
    char_views_count = sum(
        int(v.split("_")[-1]) if v.split("_")[-1].isdigit() else 1
        for v in char_views_list
    )
    supporting_cast_count = len(reg_entry.get("supporting_cast", []))
    total_char_views = char_views_count * (1 + supporting_cast_count)

    # Panel totals
    total_panels_opt = panels_opt * chapters_in_window
    total_panels_min = panels_min * chapters_in_window
    total_panels_max = panels_max * chapters_in_window

    # Background totals
    total_backgrounds = bg_per_chapter_spec * chapters_in_window

    # Cost estimates
    gpu_panels = total_panels_opt * COST_PER_PANEL_GPU
    gpu_backgrounds = total_backgrounds * COST_PER_BACKGROUND_GPU
    gpu_char_views = total_char_views * COST_PER_CHARACTER_VIEW_GPU
    gpu_total = gpu_panels + gpu_backgrounds + gpu_char_views

    human_mins = (
        total_panels_opt * REVIEW_MINS_PER_PANEL
        + total_backgrounds * REVIEW_MINS_PER_BG
        + total_char_views * REVIEW_MINS_PER_CHARACTER_VIEW
        + chapters_in_window * REVIEW_MINS_PER_CHAPTER_PASS
    )
    human_hours = human_mins / 60.0
    human_cost = human_hours * HUMAN_HOURLY_RATE_USD
    total_cost = gpu_total + human_cost

    return {
        "brand_id": brand_id,
        "genre": genre,
        "weeks": weeks,
        "active_series": active_series,
        "chapters_in_window": chapters_in_window,
        "panels": {
            "min": total_panels_min,
            "opt": total_panels_opt,
            "max": total_panels_max,
            "per_chapter_opt": panels_opt,
        },
        "backgrounds": {
            "total": total_backgrounds,
            "per_chapter": bg_per_chapter_spec,
        },
        "character_views": {
            "total": total_char_views,
            "view_types": char_views_list,
        },
        "cost_usd": {
            "gpu_panels": round(gpu_panels, 2),
            "gpu_backgrounds": round(gpu_backgrounds, 2),
            "gpu_character_views": round(gpu_char_views, 2),
            "gpu_total": round(gpu_total, 2),
            "human_hours": round(human_hours, 1),
            "human_cost": round(human_cost, 2),
            "total": round(total_cost, 2),
        },
    }


def estimate_all(weeks: int = 4) -> dict:
    """Estimate across all brands. Returns summary + per-brand breakdown."""
    brand_reg = _load_character_registry()
    series_plan = _load_series_plan()

    brand_ids = list(brand_reg.get("brands", {}).keys())
    results: list[dict] = []

    for bid in brand_ids:
        est = estimate_brand(bid, brand_reg, series_plan, weeks=weeks)
        results.append(est)

    total_chapters = sum(r["chapters_in_window"] for r in results)
    total_panels = sum(r["panels"]["opt"] for r in results)
    total_backgrounds = sum(r["backgrounds"]["total"] for r in results)
    total_char_views = sum(r["character_views"]["total"] for r in results)
    total_gpu = sum(r["cost_usd"]["gpu_total"] for r in results)
    total_human_hours = sum(r["cost_usd"]["human_hours"] for r in results)
    total_cost = sum(r["cost_usd"]["total"] for r in results)

    return {
        "weeks": weeks,
        "brand_count": len(results),
        "summary": {
            "total_chapters": total_chapters,
            "total_panels_opt": total_panels,
            "total_backgrounds": total_backgrounds,
            "total_character_views": total_char_views,
            "total_gpu_cost_usd": round(total_gpu, 2),
            "total_human_hours": round(total_human_hours, 1),
            "total_cost_usd": round(total_cost, 2),
            "cost_per_chapter_avg": round(total_cost / total_chapters, 2) if total_chapters else 0,
        },
        "brands": results,
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _print_estimate(est: dict) -> None:
    if "brands" in est:
        # All-brands summary
        s = est["summary"]
        print(f"Manga Asset Estimate — {est['brand_count']} brands, {est['weeks']}w window")
        print("=" * 55)
        print(f"  Chapters total    : {s['total_chapters']}")
        print(f"  Panels (opt)      : {s['total_panels_opt']:,}")
        print(f"  Backgrounds       : {s['total_backgrounds']:,}")
        print(f"  Character views   : {s['total_character_views']:,}")
        print(f"  GPU cost          : ${s['total_gpu_cost_usd']:,.2f}")
        print(f"  Human hours       : {s['total_human_hours']:,.1f}h")
        print(f"  Total cost        : ${s['total_cost_usd']:,.2f}")
        print(f"  Cost/chapter avg  : ${s['cost_per_chapter_avg']:.2f}")
        print()
        print(f"  {'Brand':<26} {'Chap':>5} {'Panels':>7} {'BGs':>5} {'GPU$':>8} {'Total$':>8}")
        print(f"  {'-'*26} {'-'*5} {'-'*7} {'-'*5} {'-'*8} {'-'*8}")
        for b in sorted(est["brands"], key=lambda x: -x["cost_usd"]["total"]):
            print(f"  {b['brand_id']:<26} {b['chapters_in_window']:>5} "
                  f"{b['panels']['opt']:>7,} {b['backgrounds']['total']:>5} "
                  f"${b['cost_usd']['gpu_total']:>7.2f} ${b['cost_usd']['total']:>7.2f}")
    else:
        # Single brand
        print(f"Manga Asset Estimate — {est['brand_id']} ({est['genre']}, {est['weeks']}w)")
        print("=" * 50)
        print(f"  Active series     : {est['active_series']}")
        print(f"  Chapters in window: {est['chapters_in_window']}")
        print(f"  Panels (opt)      : {est['panels']['opt']:,}  ({est['panels']['per_chapter_opt']}/chapter)")
        print(f"  Backgrounds       : {est['backgrounds']['total']}  ({est['backgrounds']['per_chapter']}/chapter)")
        print(f"  Character views   : {est['character_views']['total']}")
        print()
        c = est["cost_usd"]
        print(f"  GPU panels        : ${c['gpu_panels']:,.2f}")
        print(f"  GPU backgrounds   : ${c['gpu_backgrounds']:,.2f}")
        print(f"  GPU char views    : ${c['gpu_character_views']:,.2f}")
        print(f"  GPU total         : ${c['gpu_total']:,.2f}")
        print(f"  Human review      : {c['human_hours']:.1f}h  (${c['human_cost']:.2f})")
        print(f"  TOTAL             : ${c['total']:,.2f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manga Asset Estimator")
    scope = parser.add_mutually_exclusive_group(required=True)
    scope.add_argument("--brand", type=str, help="Single brand ID")
    scope.add_argument("--all", action="store_true", help="All brands")
    parser.add_argument("--weeks", type=int, default=4,
                        help="Planning window in weeks (default: 4)")
    parser.add_argument("--output", type=str, default=None,
                        help="Write JSON output to this path (relative to repo root)")
    args = parser.parse_args()

    if args.all:
        result = estimate_all(weeks=args.weeks)
    else:
        brand_reg = _load_character_registry()
        series_plan = _load_series_plan()
        result = estimate_brand(args.brand, brand_reg, series_plan, weeks=args.weeks)

    _print_estimate(result)

    if args.output:
        for base in [_WORKTREE, _REPO_ROOT]:
            out_path = base / args.output
            if out_path.parent.exists():
                break
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2)
        print(f"\nJSON written: {out_path}")


if __name__ == "__main__":
    main()
