#!/usr/bin/env python3
"""Per-brand aggregates derived from the 37-brand manga series-plan SSOT.

SSOT: ``config/source_of_truth/manga_series_plans/<locale>/<brand>__<locale>__<genre>__<slug>.yaml``
Each file is one planned series. This is the single place that derives per-brand
facts from the SSOT so consumers don't re-implement the glob/group/validate dance.

Series counts are locale-invariant (verified across en_US/ja_JP/ko_KR/zh_CN/zh_TW),
so ``en_US`` is the reference locale for counts. ``teacher_id`` is consistent within
a brand and is ``None`` for the brands the strategic plan does not anchor to a
teacher (see specs/MANGA_CATALOG_RECONCILIATION_SPEC.md §"teacher_id: null").

Authority chain (per config/manga/canonical_brand_list.yaml header):
  GENRE_PORTFOLIO_PLAN.md -> MANGA_CATALOG_RECONCILIATION_SPEC.md ->
  canonical_brand_list.yaml -> manga_series_plans/ (this module reads the last two).
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
SSOT_ROOT = REPO / "config" / "source_of_truth" / "manga_series_plans"
CANON = REPO / "config" / "manga" / "canonical_brand_list.yaml"

LOCALES: tuple[str, ...] = ("en_US", "ja_JP", "ko_KR", "zh_CN", "zh_TW")
REFERENCE_LOCALE = "en_US"


def _load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def canonical_brand_ids() -> list[str]:
    """The canonical 37 manga brand ids, in canonical_brand_list order."""
    return list((_load(CANON).get("brands") or {}).keys())


def _brand_of(doc: dict[str, Any], path: Path) -> str:
    return str(doc.get("brand_id") or path.name.split("__", 1)[0])


def brand_aggregates(locale: str = REFERENCE_LOCALE) -> dict[str, dict[str, Any]]:
    """Map ``brand_id`` -> ``{series_count, teacher_id, primary_genre}`` for one locale.

    ``teacher_id`` is the single non-null teacher across the brand's series, else
    ``None``. ``primary_genre`` is the most common per-series genre (ties broken by
    sort order, so the result is deterministic).
    """
    locale_dir = SSOT_ROOT / locale
    out: dict[str, dict[str, Any]] = {}
    genres: dict[str, Counter] = {}
    teachers: dict[str, set[str]] = {}

    for path in sorted(locale_dir.glob("*.yaml")):
        doc = _load(path)
        brand = _brand_of(doc, path)
        agg = out.setdefault(brand, {"series_count": 0, "teacher_id": None, "primary_genre": None})
        agg["series_count"] += 1
        genres.setdefault(brand, Counter())
        teachers.setdefault(brand, set())
        if doc.get("genre"):
            genres[brand][str(doc["genre"])] += 1
        tid = doc.get("teacher_id")
        if tid:
            teachers[brand].add(str(tid))

    for brand, agg in out.items():
        tset = teachers.get(brand) or set()
        agg["teacher_id"] = sorted(tset)[0] if len(tset) == 1 else (sorted(tset)[0] if tset else None)
        gc = genres.get(brand) or Counter()
        if gc:
            # most_common is order-stable on first insertion; sort for determinism on ties.
            top = max(sorted(gc.items()), key=lambda kv: kv[1])
            agg["primary_genre"] = top[0]
    return out


def series_count_by_brand(locale: str = REFERENCE_LOCALE) -> dict[str, int]:
    """Map ``brand_id`` -> planned series count from the SSOT (one locale)."""
    return {b: a["series_count"] for b, a in brand_aggregates(locale).items()}


def verify_against_canonical() -> tuple[bool, list[str]]:
    """Check the SSOT brand set matches the canonical 37. Returns (ok, problems)."""
    canon = set(canonical_brand_ids())
    ssot = set(series_count_by_brand().keys())
    problems: list[str] = []
    if ssot - canon:
        problems.append(f"SSOT brands not in canonical list: {sorted(ssot - canon)}")
    if canon - ssot:
        problems.append(f"canonical brands missing from SSOT: {sorted(canon - ssot)}")
    return (not problems, problems)


if __name__ == "__main__":
    ok, problems = verify_against_canonical()
    aggs = brand_aggregates()
    print(f"SSOT brands: {len(aggs)} | canonical: {len(canonical_brand_ids())} | match: {ok}")
    for p in problems:
        print("  PROBLEM:", p)
    total = sum(a["series_count"] for a in aggs.values())
    print(f"total planned series (en_US): {total}")
    for brand in sorted(aggs):
        a = aggs[brand]
        print(f"  {brand:32s} count={a['series_count']:2d} teacher={a['teacher_id']} genre={a['primary_genre']}")
