#!/usr/bin/env python3
"""
Build unified manga catalog CSV from market registry + brand series plans.

Reads:
  config/catalog/market_catalog_registry.yaml
  config/catalog_planning/brand_series_plans.yaml
  config/manga/manga_brand_series_plan.yaml (genre + cadence metadata)
  Optional extra rows: any YAML under config/catalog_planning/ whose document root
  contains a list field `manga_extra_catalog_rows` (list of dicts with CSV columns).

Output columns:
  brand_id, series_title, market, genre, protagonist, chapter_count, status,
  platform_primary, platform_secondary

Usage:
  python3 scripts/manga/build_manga_catalog.py --all
  python3 scripts/manga/build_manga_catalog.py --market us --dry-run
  python3 scripts/manga/build_manga_catalog.py --brand stillness_press
  python3 scripts/manga/build_manga_catalog.py --all --output artifacts/catalog/manga_catalog.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

FIELDNAMES = [
    "brand_id",
    "series_title",
    "market",
    "genre",
    "protagonist",
    "chapter_count",
    "status",
    "platform_primary",
    "platform_secondary",
]

try:
    import yaml
except ImportError as e:  # pragma: no cover
    raise SystemExit("PyYAML is required: pip install pyyaml") from e


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    return data if isinstance(data, dict) else {}


def _track_ids(tracks: Any) -> list[str]:
    out: list[str] = []
    if not isinstance(tracks, list):
        return out
    for t in tracks:
        if isinstance(t, str):
            out.append(t)
        elif isinstance(t, dict):
            tid = t.get("id")
            if tid:
                out.append(str(tid))
    return out


def _market_has_manga(tracks: Any) -> bool:
    ids = [x.lower() for x in _track_ids(tracks)]
    return any("manga" in x or "webtoon" in x for x in ids)


def _platform_pair(market: dict[str, Any]) -> tuple[str, str]:
    ps = market.get("platform_strategy") or []
    if not isinstance(ps, list) or not ps:
        return ("", "")
    primary = str(ps[0]) if ps else ""
    secondary = str(ps[1]) if len(ps) > 1 else ""
    return (primary, secondary)


def _is_series_entry(obj: Any) -> bool:
    if not isinstance(obj, dict):
        return False
    if "package" in obj and "title" not in obj:
        return False
    return bool(obj.get("title"))


def _iter_series(brand_plan: dict[str, Any]) -> Iterable[dict[str, Any]]:
    for lane_name in ("heavy_lanes", "medium_lanes"):
        lane = brand_plan.get(lane_name) or {}
        if not isinstance(lane, dict):
            continue
        for _slot, series in lane.items():
            if _is_series_entry(series):
                yield series


def _load_extra_rows(planning_dir: Path) -> list[dict[str, Any]]:
    extra: list[dict[str, Any]] = []
    if not planning_dir.is_dir():
        return extra
    for path in sorted(planning_dir.glob("*.yaml")):
        doc = _load_yaml(path)
        rows = doc.get("manga_extra_catalog_rows")
        if isinstance(rows, list):
            for row in rows:
                if isinstance(row, dict):
                    extra.append(row)
    return extra


def _row(
    *,
    brand_id: str,
    series_title: str,
    market_id: str,
    genre: str,
    protagonist: str,
    chapter_count: int,
    platform_primary: str,
    platform_secondary: str,
    status: str = "planned",
) -> dict[str, Any]:
    return {
        "brand_id": brand_id,
        "series_title": series_title,
        "market": market_id,
        "genre": genre,
        "protagonist": protagonist,
        "chapter_count": str(chapter_count),
        "status": status,
        "platform_primary": platform_primary,
        "platform_secondary": platform_secondary,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Build unified manga catalog CSV.")
    ap.add_argument("--all", action="store_true", help="Include all brands/markets (subject to filters)")
    ap.add_argument("--market", help="Filter to a single market_id (e.g. us, japan, korea)")
    ap.add_argument("--brand", help="Filter to a single brand_id")
    ap.add_argument(
        "--output",
        type=Path,
        default=REPO_ROOT / "artifacts/catalog/manga_catalog.csv",
        help="CSV path (default: artifacts/catalog/manga_catalog.csv)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Do not write CSV; print summary to stderr")
    args = ap.parse_args()

    if not args.all and not args.market and not args.brand:
        print("Specify --all and/or --market and/or --brand.", file=sys.stderr)
        return 2

    registry_path = REPO_ROOT / "config/catalog/market_catalog_registry.yaml"
    series_path = REPO_ROOT / "config/catalog_planning/brand_series_plans.yaml"
    manga_meta_path = REPO_ROOT / "config/manga/manga_brand_series_plan.yaml"
    planning_dir = REPO_ROOT / "config/catalog_planning"

    registry = _load_yaml(registry_path)
    series_plans = _load_yaml(series_path).get("brands") or {}
    manga_meta = (_load_yaml(manga_meta_path).get("brands") or {})

    if not isinstance(series_plans, dict):
        print("Invalid brand_series_plans.yaml", file=sys.stderr)
        return 1

    markets_block = registry.get("markets") or {}
    if not isinstance(markets_block, dict):
        print("Invalid market_catalog_registry.yaml", file=sys.stderr)
        return 1

    manga_markets: list[tuple[str, dict[str, Any]]] = []
    for mid, mdata in markets_block.items():
        if not isinstance(mdata, dict):
            continue
        if not _market_has_manga(mdata.get("business_tracks")):
            continue
        manga_markets.append((str(mid), mdata))

    if args.market:
        manga_markets = [(m, d) for m, d in manga_markets if m == args.market]
        if not manga_markets:
            print(f"No manga-enabled market matches {args.market!r}.", file=sys.stderr)
            return 1

    rows: list[dict[str, Any]] = []

    for market_id, mdata in manga_markets:
        brands_in_market = mdata.get("brands") or []
        if not isinstance(brands_in_market, list):
            continue
        p_pri, p_sec = _platform_pair(mdata)
        for brand_id in brands_in_market:
            bid = str(brand_id).strip()
            if args.brand and bid != args.brand:
                continue
            plan = series_plans.get(bid)
            if not isinstance(plan, dict):
                continue
            meta = manga_meta.get(bid) if isinstance(manga_meta, dict) else {}
            if not isinstance(meta, dict):
                meta = {}
            brand_genre = str(meta.get("genre") or plan.get("primary_topic") or "")
            manga_mode = str(plan.get("manga_mode") or "regular")
            teacher = plan.get("teacher")
            if manga_mode == "teacher" and teacher:
                protagonist = str(teacher)
            else:
                protagonist = "ensemble_cast"

            for series in _iter_series(plan):
                title = str(series.get("title") or "").strip()
                if not title:
                    continue
                topic = str(series.get("topic") or series.get("angle_source") or brand_genre)
                genre = brand_genre or topic
                ch = int(series.get("episode_count") or 0)
                rows.append(
                    _row(
                        brand_id=bid,
                        series_title=title,
                        market_id=market_id,
                        genre=genre,
                        protagonist=protagonist,
                        chapter_count=ch,
                        platform_primary=p_pri,
                        platform_secondary=p_sec,
                    )
                )

    need = set(FIELDNAMES)
    for extra in _load_extra_rows(planning_dir):
        if not need.issubset(extra.keys()):
            continue
        rows.append({k: str(extra[k]) for k in FIELDNAMES})

    if args.dry_run:
        print(f"rows={len(rows)} markets={[m for m, _ in manga_markets]}", file=sys.stderr)
        for i, r in enumerate(rows[:15]):
            print(f"  {i+1}: {r}", file=sys.stderr)
        if len(rows) > 15:
            print(f"  … ({len(rows) - 15} more)", file=sys.stderr)
        return 0

    out_path: Path = args.output
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        w.writeheader()
        for r in rows:
            w.writerow({k: r.get(k, "") for k in FIELDNAMES})

    print(f"Wrote {len(rows)} rows → {out_path.relative_to(REPO_ROOT)}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
