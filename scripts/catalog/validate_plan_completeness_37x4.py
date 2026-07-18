#!/usr/bin/env python3
"""Plan-completeness validator — Layer 1 gate for worldwide catalog fan-out.

Asserts that every one of the 37 canonical manga brands has, for each of the 4
launch locales (en_US, ja_JP, zh_TW, zh_CN), a plan present on all 3 content
surfaces:

  - manga   : >=1 series_plan YAML in config/source_of_truth/manga_series_plans/<locale>/
              named <brand>__<locale>__<genre>__seriesNN.yaml
  - book    : an `ebook` surface row in
              artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv
              (the V1.1 allocation SSOT, PR #1037/#1038)
  - podcast : a `podcast` surface row in
              artifacts/catalog/worldwide_catalog_37_brand_podcast_plan_2026-05-27.tsv

This is the SSOT gate that unlocks Layers 2 + 3 per docs/SYSTEMS_STATE_20260527.md
§3. It is planning/data only — it does NOT inspect generated content (book text,
manga panels, audio), only that a PLAN exists for each cell.

Matrix size: 37 brands x 4 locales x 3 surfaces = 444 cells, MINUS any
market-exclusive manga lanes. A brand may declare `manga_locales` in
canonical_brand_list.yaml to lock its MANGA surface to a subset of launch
locales; the manga cells outside that subset are not expected and are excluded
from the matrix (book/podcast surfaces are unaffected). Today only
bright_presence_tw_seinen is locked (zh_TW-only, OPD-20260627-001), so the
expected matrix is 444 - 3 = 441 cells.

Emits artifacts/catalog/plan_completeness_37x4_20260527.tsv with one row per
(brand, locale) carrying manga/book/podcast booleans + per-surface counts.

Exit codes:
    0 — all 444 cells covered
    1 — at least one cell missing
    2 — input config / SSOT missing or malformed
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
BRAND_LIST = REPO / "config" / "manga" / "canonical_brand_list.yaml"
MANGA_SERIES_DIR = REPO / "config" / "source_of_truth" / "manga_series_plans"
EBOOK_TSV = (
    REPO / "artifacts" / "qa" / "worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv"
)
PODCAST_TSV = (
    REPO
    / "artifacts"
    / "catalog"
    / "worldwide_catalog_37_brand_podcast_plan_2026-05-27.tsv"
)
OUT_TSV = REPO / "artifacts" / "catalog" / "plan_completeness_37x4_20260527.tsv"

LAUNCH_LOCALES = ("en_US", "ja_JP", "zh_TW", "zh_CN")


def _load_brands() -> list[str]:
    if not BRAND_LIST.exists():
        raise SystemExit(f"[2] canonical brand list missing: {BRAND_LIST}")
    data = yaml.safe_load(BRAND_LIST.read_text(encoding="utf-8"))
    brands = list(data.get("brands", {}).keys())
    if not brands:
        raise SystemExit(f"[2] no brands in {BRAND_LIST}")
    return brands


def _manga_locale_locks() -> dict[str, set[str]]:
    """Per-brand manga-lane locale restriction from canonical_brand_list.yaml.

    A brand entry may declare an optional ``manga_locales`` list. When present,
    the brand's MANGA surface is expected ONLY in those launch locales; manga
    cells outside the set are not part of the matrix. Brands that omit the field
    default to all LAUNCH_LOCALES (the historical behaviour).

    Authority: brand profile header (e.g. bright_presence_tw_seinen is the
    Taiwan/zh_TW-exclusive Adi Da manga lane) ratified under OPD-20260627-001;
    PRs #2215 / #2217 removed the non-zh_TW manga plans.
    """
    if not BRAND_LIST.exists():
        raise SystemExit(f"[2] canonical brand list missing: {BRAND_LIST}")
    data = yaml.safe_load(BRAND_LIST.read_text(encoding="utf-8")) or {}
    locks: dict[str, set[str]] = {}
    for brand, attrs in (data.get("brands") or {}).items():
        locales = (attrs or {}).get("manga_locales")
        if locales:
            locks[brand] = {str(loc).strip() for loc in locales}
    return locks


def _manga_counts() -> dict[tuple[str, str], int]:
    """Count series_plan YAMLs per (brand, locale)."""
    counts: dict[tuple[str, str], int] = defaultdict(int)
    if not MANGA_SERIES_DIR.exists():
        raise SystemExit(f"[2] manga series-plan dir missing: {MANGA_SERIES_DIR}")
    for f in MANGA_SERIES_DIR.rglob("*.yaml"):
        if "_samples" in str(f):
            continue
        parts = f.stem.split("__")
        if len(parts) >= 2:
            counts[(parts[0], parts[1])] += 1
    return counts


def _surface_counts(tsv: Path, surface: str) -> dict[tuple[str, str], int]:
    """Count rows of the given surface per (brand, locale) in an allocation TSV."""
    counts: dict[tuple[str, str], int] = defaultdict(int)
    if not tsv.exists():
        raise SystemExit(f"[2] allocation TSV missing: {tsv}")
    with open(tsv, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        if reader.fieldnames is None:
            raise SystemExit(f"[2] empty TSV: {tsv}")
        norm = {h.strip().lower(): h for h in reader.fieldnames}
        for col in ("brand_id", "locale", "surface", "series_count"):
            if col not in norm:
                raise SystemExit(f"[2] {tsv} missing column {col!r}")
        for row in reader:
            if (row.get(norm["surface"]) or "").strip().lower() != surface:
                continue
            brand = (row.get(norm["brand_id"]) or "").strip()
            locale = (row.get(norm["locale"]) or "").strip()
            try:
                n = int((row.get(norm["series_count"]) or "0").strip())
            except ValueError:
                n = 0
            if brand and locale:
                counts[(brand, locale)] += max(n, 1)
    return counts


def validate(write: bool = True) -> int:
    brands = _load_brands()
    manga = _manga_counts()
    book = _surface_counts(EBOOK_TSV, "ebook")
    podcast = _surface_counts(PODCAST_TSV, "podcast")
    manga_locks = _manga_locale_locks()

    out_rows: list[list[str]] = []
    missing: list[str] = []
    cells_covered = 0
    total_cells = 0  # expected cells, net of market-exclusive manga lanes

    for brand in brands:
        lock = manga_locks.get(brand)
        for locale in LAUNCH_LOCALES:
            mc = manga.get((brand, locale), 0)
            bc = book.get((brand, locale), 0)
            pc = podcast.get((brand, locale), 0)
            m_ok, b_ok, p_ok = mc > 0, bc > 0, pc > 0
            # manga is only EXPECTED where the brand is not locale-locked out;
            # book + podcast are always expected for every (brand, locale).
            manga_expected = lock is None or locale in lock
            surfaces = (
                ("manga", manga_expected, m_ok),
                ("book", True, b_ok),
                ("podcast", True, p_ok),
            )
            miss = []
            for name, expected, ok in surfaces:
                if not expected:
                    continue
                total_cells += 1
                if ok:
                    cells_covered += 1
                else:
                    miss.append(name)
            complete = not miss
            out_rows.append(
                [
                    brand,
                    locale,
                    "1" if m_ok else "0",
                    str(mc),
                    "1" if b_ok else "0",
                    str(bc),
                    "1" if p_ok else "0",
                    str(pc),
                    "COMPLETE" if complete else "MISSING",
                ]
            )
            if miss:
                missing.append(f"{brand} / {locale}: missing {', '.join(miss)}")

    if write:
        OUT_TSV.parent.mkdir(parents=True, exist_ok=True)
        with open(OUT_TSV, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh, delimiter="\t")
            w.writerow(
                [
                    "brand_id",
                    "locale",
                    "manga_plan",
                    "manga_series_count",
                    "book_plan",
                    "book_series_count",
                    "podcast_plan",
                    "podcast_series_count",
                    "status",
                ]
            )
            w.writerows(out_rows)

    print(f"plan-completeness matrix: {cells_covered}/{total_cells} cells covered")
    print(f"  brands={len(brands)} locales={len(LAUNCH_LOCALES)} surfaces=3 (manga|book|podcast)")
    if write:
        print(f"  wrote {OUT_TSV}")
    if missing:
        print(f"\nFAIL — {len(missing)} incomplete (brand, locale) cells:", file=sys.stderr)
        for line in missing[:50]:
            print(f"  - {line}", file=sys.stderr)
        if len(missing) > 50:
            print(f"  ... and {len(missing) - 50} more", file=sys.stderr)
        return 1
    print(
        f"\nPASS — all 37 brands x 4 locales have their expected manga + book + "
        f"podcast plans ({cells_covered}/{total_cells} cells)."
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--no-write",
        action="store_true",
        help="validate only; do not (re)write the completeness TSV",
    )
    args = ap.parse_args(argv)
    return validate(write=not args.no_write)


if __name__ == "__main__":
    raise SystemExit(main())
