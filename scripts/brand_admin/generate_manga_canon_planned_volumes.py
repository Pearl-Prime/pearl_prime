#!/usr/bin/env python3
"""Generate manga-canon planned-volume config backfill (37 brands × ebook/podcast/audiobook).

Pearl_Editor + Pearl_Marketing tier baselines. Run from repo root:
  PYTHONPATH=. python3 scripts/brand_admin/generate_manga_canon_planned_volumes.py
"""
from __future__ import annotations

from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
CANON = REPO / "config" / "manga" / "canonical_brand_list.yaml"
SERIES_PLAN = REPO / "config" / "manga" / "manga_brand_series_plan.yaml"

# Canonical brand_id → manga_brand_series_plan.yaml key (teacher-lane legacy IDs).
SERIES_PLAN_ALIAS: dict[str, str] = {
    "sleep_restoration_iyashikei": "sleep_restoration",
    "somatic_wisdom_shojo": "somatic_wisdom",
    "relational_calm_iyashikei": "relational_calm",
    "body_memory_shojo": "body_memory",
    "heart_balance_shojo": "heart_balance",
    "devotion_path_shonen": "devotion_path",
    "solar_return_isekai": "solar_return",
    "warrior_calm_cultivation": "warrior_calm",
    "bright_presence_tw_seinen": "bright_presence_tw",
}

# Pearl_Marketing tier baselines (annual targets; podcast = episodes/yr).
TIER_DEFAULTS: dict[str, dict[str, int]] = {
    "flagship": {
        "volumes_per_year_target": 8,
        "active_series_target": 4,
        "episodes_per_year_target": 52,
        "titles_per_year_target": 8,
    },
    "core": {
        "volumes_per_year_target": 6,
        "active_series_target": 3,
        "episodes_per_year_target": 40,
        "titles_per_year_target": 6,
    },
    "niche": {
        "volumes_per_year_target": 4,
        "active_series_target": 2,
        "episodes_per_year_target": 26,
        "titles_per_year_target": 4,
    },
}


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _brand_row(brand_id: str, tier: str, series: dict, defaults: dict) -> dict:
    plan_key = SERIES_PLAN_ALIAS.get(brand_id, brand_id)
    body = series.get(plan_key) if isinstance(series.get(plan_key), dict) else {}
    tier_d = TIER_DEFAULTS.get(tier, TIER_DEFAULTS["core"])
    ebooks = body.get("volumes_per_year_target") or tier_d["volumes_per_year_target"]
    manga_series = body.get("active_series_target") or tier_d["active_series_target"]
    podcast = tier_d["episodes_per_year_target"]
    audiobook = tier_d["titles_per_year_target"]
    if body.get("volumes_per_year_target"):
        audiobook = body["volumes_per_year_target"]
    return {
        "tier": tier,
        "series_plan_key": plan_key if plan_key != brand_id else None,
        "volumes_per_year_target": int(ebooks),
        "active_series_target": int(manga_series),
        "episodes_per_year_target": int(podcast),
        "titles_per_year_target": int(audiobook),
    }


def main() -> None:
    canon = _load(CANON).get("brands") or {}
    plan = _load(SERIES_PLAN)
    series = plan.get("brands") or {}
    defaults = plan.get("global_defaults") or {}

    brands_out: dict[str, dict] = {}
    coverage_rows: list[str] = [
        "brand_id\ttier\tebooks_yr\tmanga_series\tpodcast_eps_yr\taudiobook_titles_yr\tseries_plan_key\tgaps"
    ]

    for brand_id in sorted(canon.keys()):
        body = canon[brand_id]
        tier = (body.get("tier") if isinstance(body, dict) else None) or "core"
        row = _brand_row(brand_id, tier, series, defaults)
        key = row.pop("series_plan_key")
        brands_out[brand_id] = {k: v for k, v in row.items() if v is not None}
        if key:
            brands_out[brand_id]["series_plan_key"] = key
        gaps = []
        if brand_id not in series and brand_id not in SERIES_PLAN_ALIAS.values():
            if not key or key not in series:
                gaps.append("manga_series_plan_inherited_tier")
        coverage_rows.append(
            "\t".join(
                [
                    brand_id,
                    tier,
                    str(row["volumes_per_year_target"]),
                    str(row["active_series_target"]),
                    str(row["episodes_per_year_target"]),
                    str(row["titles_per_year_target"]),
                    key or "",
                    ";".join(gaps) if gaps else "",
                ]
            )
        )

    header = {
        "schema_version": 1,
        "registry_id": "manga_canon_planned_volumes",
        "owner": "pearl_brand",
        "status": "active",
        "source": "ws_planned_volumes_per_brand_backfill_20260526; tier baselines Pearl_Marketing",
        "last_updated": "2026-05-27",
        "brand_list_source": "config/manga/canonical_brand_list.yaml",
        "tier_defaults": TIER_DEFAULTS,
        "series_plan_alias": SERIES_PLAN_ALIAS,
        "notes": (
            "Brand-admin planned_volumes SSOT for 37 Path X manga-canon brands. "
            "Ebook/manga_series values prefer manga_brand_series_plan.yaml via series_plan_key; "
            "podcast/audiobook use tier baselines unless overridden per brand."
        ),
    }

    out_path = REPO / "config" / "brand_admin" / "manga_canon_planned_volumes.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = {**header, "brands": brands_out}
    out_path.write_text(
        yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    cov_path = REPO / "artifacts" / "brand_admin" / "planned_volumes_coverage_20260527.tsv"
    cov_path.parent.mkdir(parents=True, exist_ok=True)
    cov_path.write_text("\n".join(coverage_rows) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(brands_out)} brands)")
    print(f"Wrote {cov_path}")


if __name__ == "__main__":
    main()
