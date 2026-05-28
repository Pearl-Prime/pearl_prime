#!/usr/bin/env python3
"""Generate manga-canon planned-volume config backfill (37 brands × ebook/podcast/audiobook).

The per-brand manga-series count (the dashboard's "manga series" tile) is the REAL
planned series count from the 37-brand SSOT at config/source_of_truth/manga_series_plans/
(via scripts/manga/manga_series_plan_ssot.py), so all 37 brands carry true counts
instead of flat tier-default placeholders. Ebook/podcast/audiobook stay on
Pearl_Marketing tier baselines (no per-series annual cadence exists in the SSOT),
preferring curated manga_brand_series_plan.yaml volume targets where present.

Run from repo root:
  PYTHONPATH=. python3 scripts/brand_admin/generate_manga_canon_planned_volumes.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
CANON = REPO / "config" / "manga" / "canonical_brand_list.yaml"
SERIES_PLAN = REPO / "config" / "manga" / "manga_brand_series_plan.yaml"

# Import the shared SSOT aggregator regardless of how the script is invoked.
sys.path.insert(0, str(REPO))
from scripts.manga.manga_series_plan_ssot import (  # noqa: E402
    REFERENCE_LOCALE,
    series_count_by_brand,
)

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


def _brand_row(brand_id: str, tier: str, series: dict, ssot_counts: dict[str, int]) -> dict:
    plan_key = SERIES_PLAN_ALIAS.get(brand_id, brand_id)
    body = series.get(plan_key) if isinstance(series.get(plan_key), dict) else {}
    tier_d = TIER_DEFAULTS.get(tier, TIER_DEFAULTS["core"])
    ebooks = body.get("volumes_per_year_target") or tier_d["volumes_per_year_target"]
    # manga_series = REAL planned series count from the 37-brand SSOT (all 37 brands
    # covered). active_series_target in THIS dashboard registry therefore means
    # "planned series total per the SSOT", not the legacy simultaneous-active band.
    # Fall back to the legacy/tier value only if a brand is unexpectedly absent
    # from the SSOT (verify_against_canonical() guards against that in main()).
    manga_series = ssot_counts.get(brand_id)
    if manga_series is None:
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

    ssot_counts = series_count_by_brand(REFERENCE_LOCALE)
    missing = sorted(set(canon.keys()) - set(ssot_counts.keys()))
    if missing:
        raise SystemExit(
            f"SSOT is missing {len(missing)} canonical brand(s); refusing to emit "
            f"placeholder counts: {missing}"
        )

    brands_out: dict[str, dict] = {}
    coverage_rows: list[str] = [
        "brand_id\ttier\tebooks_yr\tmanga_series\tssot_series_count\t"
        "podcast_eps_yr\taudiobook_titles_yr\tvolumes_source\tseries_plan_key"
    ]

    for brand_id in sorted(canon.keys()):
        body = canon[brand_id]
        tier = (body.get("tier") if isinstance(body, dict) else None) or "core"
        row = _brand_row(brand_id, tier, series, ssot_counts)
        key = row.pop("series_plan_key")
        brands_out[brand_id] = {k: v for k, v in row.items() if v is not None}
        if key:
            brands_out[brand_id]["series_plan_key"] = key
        legacy_body = series.get(key) if key else series.get(brand_id)
        volumes_source = (
            "curated_series_plan"
            if isinstance(legacy_body, dict) and legacy_body.get("volumes_per_year_target")
            else "tier_default"
        )
        coverage_rows.append(
            "\t".join(
                [
                    brand_id,
                    tier,
                    str(row["volumes_per_year_target"]),
                    str(row["active_series_target"]),
                    str(ssot_counts.get(brand_id, "")),
                    str(row["episodes_per_year_target"]),
                    str(row["titles_per_year_target"]),
                    volumes_source,
                    key or "",
                ]
            )
        )

    header = {
        "schema_version": 1,
        "registry_id": "manga_canon_planned_volumes",
        "owner": "pearl_brand",
        "status": "active",
        "source": "manga_series_plans SSOT (manga_series count); tier baselines Pearl_Marketing",
        "last_updated": "2026-05-28",
        "brand_list_source": "config/manga/canonical_brand_list.yaml",
        "series_count_source": f"config/source_of_truth/manga_series_plans/{REFERENCE_LOCALE}",
        "tier_defaults": TIER_DEFAULTS,
        "series_plan_alias": SERIES_PLAN_ALIAS,
        "notes": (
            "Brand-admin planned_volumes registry for 37 Path X manga-canon brands. "
            "active_series_target = REAL planned series count from the 37-brand SSOT "
            "(series counts are locale-invariant; en_US is the reference locale). "
            "volumes_per_year_target prefers curated manga_brand_series_plan.yaml via "
            "series_plan_key, else tier baseline; podcast/audiobook use tier baselines."
        ),
    }

    out_path = REPO / "config" / "brand_admin" / "manga_canon_planned_volumes.yaml"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    doc = {**header, "brands": brands_out}
    out_path.write_text(
        yaml.dump(doc, default_flow_style=False, sort_keys=False, allow_unicode=True),
        encoding="utf-8",
    )

    cov_path = REPO / "artifacts" / "brand_admin" / "planned_volumes_coverage_20260528.tsv"
    cov_path.parent.mkdir(parents=True, exist_ok=True)
    cov_path.write_text("\n".join(coverage_rows) + "\n", encoding="utf-8")
    print(f"Wrote {out_path} ({len(brands_out)} brands)")
    print(f"Wrote {cov_path}")


if __name__ == "__main__":
    main()
