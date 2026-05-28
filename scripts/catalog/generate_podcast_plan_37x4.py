#!/usr/bin/env python3
"""Generate the per-brand x per-locale podcast allocation plan (Layer 1 SSOT).

Closes the podcast gap in the worldwide catalog fan-out (Layer 1 of
docs/SYSTEMS_STATE_20260527.md §3). The 2026-05-11 allocation plan
(artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv,
PR #1037/#1038) is a *2-surface contract* (ebook + manga) enforced strict by
scripts/catalog/v1_1_brand_allocation_loader.py and
tests/catalog/test_v1_1_brand_allocation.py. The podcast surface is therefore
authored as a SEPARATE, additive plan with the same column schema so the
ebook+manga contract (296 rows, strict_surface) stays untouched.

Inputs (deterministic):
  - config/manga/canonical_brand_list.yaml      (the 37 canonical brands + tier)
  - config/podcast/brand_podcast_plans.yaml     (per-market podcast parameters)

Output:
  - artifacts/catalog/worldwide_catalog_37_brand_podcast_plan_2026-05-27.tsv
    columns: brand_id, locale, surface, series_count, episode_per_series_count,
             priority_phase  (identical schema to the 05-11 allocation TSV)

Allocation rule (per locale, podcast-native, derived from market config):
  - series_count          = markets[locale].series_per_brand_year  (seasons/yr)
  - episode_per_series_count = markets[locale].episodes_per_series
  - release cadence is weekly for all 4 launch locales (see market config).
Brand tier does not change the per-locale baseline (mirrors the ebook surface's
uniform 5/locale convention in the 05-11 TSV; tier depth is expressed at the
series-plan YAML layer, not the allocation layer).

Usage:
    python3 scripts/catalog/generate_podcast_plan_37x4.py            # write TSV
    python3 scripts/catalog/generate_podcast_plan_37x4.py --stdout   # print only
    python3 scripts/catalog/generate_podcast_plan_37x4.py --check    # verify up-to-date
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BRAND_LIST = REPO / "config" / "manga" / "canonical_brand_list.yaml"
PODCAST_PLANS = REPO / "config" / "podcast" / "brand_podcast_plans.yaml"
OUT_TSV = (
    REPO
    / "artifacts"
    / "catalog"
    / "worldwide_catalog_37_brand_podcast_plan_2026-05-27.tsv"
)

# The 4 launch locales for Layer 1 (per docs/SYSTEMS_STATE_20260527.md §3).
LAUNCH_LOCALES = ("en_US", "ja_JP", "zh_TW", "zh_CN")

# Canonical locale -> podcast market key in brand_podcast_plans.yaml.
LOCALE_TO_MARKET = {
    "en_US": "en_us",
    "ja_JP": "ja_jp",
    "zh_TW": "zh_tw",
    "zh_CN": "zh_cn",
}

SURFACE = "podcast"
PRIORITY_PHASE = "V1.1_podcast_proposed"
HEADER = (
    "brand_id\tlocale\tsurface\tseries_count\tepisode_per_series_count\tpriority_phase"
)


def _load_brands() -> list[str]:
    data = yaml.safe_load(BRAND_LIST.read_text(encoding="utf-8"))
    brands = list(data["brands"].keys())
    if len(brands) != data.get("total_brands", len(brands)):
        raise SystemExit(
            f"brand-count drift: {len(brands)} keys vs total_brands="
            f"{data.get('total_brands')}"
        )
    return brands


def _load_market_params() -> dict[str, dict[str, int]]:
    data = yaml.safe_load(PODCAST_PLANS.read_text(encoding="utf-8"))
    markets = data["markets"]
    defaults = data.get("defaults", {})
    params: dict[str, dict[str, int]] = {}
    for locale, mkey in LOCALE_TO_MARKET.items():
        if mkey not in markets:
            raise SystemExit(f"podcast market {mkey!r} missing for locale {locale}")
        m = markets[mkey]
        series = int(m.get("series_per_brand_year", defaults.get("series_per_brand_year", 4)))
        eps = int(m.get("episodes_per_series", defaults.get("episodes_per_series", 10)))
        params[locale] = {"series_count": series, "episodes_per_series": eps}
    return params


def build_rows() -> list[tuple[str, str, str, int, int, str]]:
    brands = _load_brands()
    params = _load_market_params()
    rows: list[tuple[str, str, str, int, int, str]] = []
    for brand in brands:
        for locale in LAUNCH_LOCALES:
            p = params[locale]
            rows.append(
                (
                    brand,
                    locale,
                    SURFACE,
                    p["series_count"],
                    p["episodes_per_series"],
                    PRIORITY_PHASE,
                )
            )
    return rows


def render(rows) -> str:
    lines = [HEADER]
    for r in rows:
        lines.append(f"{r[0]}\t{r[1]}\t{r[2]}\t{r[3]}\t{r[4]}\t{r[5]}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stdout", action="store_true", help="print TSV, do not write")
    ap.add_argument(
        "--check",
        action="store_true",
        help="exit 1 if the on-disk TSV differs from regenerated content",
    )
    args = ap.parse_args(argv)

    rows = build_rows()
    text = render(rows)
    expected_rows = len(_load_brands()) * len(LAUNCH_LOCALES)
    if len(rows) != expected_rows:
        print(
            f"FAIL: produced {len(rows)} rows, expected {expected_rows} "
            f"(37 brands x 4 locales)",
            file=sys.stderr,
        )
        return 2

    if args.stdout:
        sys.stdout.write(text)
        return 0

    if args.check:
        if not OUT_TSV.exists():
            print(f"FAIL: {OUT_TSV} missing; run without --check", file=sys.stderr)
            return 1
        if OUT_TSV.read_text(encoding="utf-8") != text:
            print(f"FAIL: {OUT_TSV} is stale; regenerate", file=sys.stderr)
            return 1
        print(f"OK: {OUT_TSV} up to date ({len(rows)} rows)")
        return 0

    OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
    OUT_TSV.write_text(text, encoding="utf-8")
    print(f"wrote {OUT_TSV} ({len(rows)} rows = 37 brands x 4 locales x podcast)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
