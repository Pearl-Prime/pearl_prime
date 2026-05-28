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

Matrix size: 37 brands x 4 locales x 3 surfaces = 444 cells.

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

    out_rows: list[list[str]] = []
    missing: list[str] = []
    cells_covered = 0
    total_cells = len(brands) * len(LAUNCH_LOCALES) * 3

    for brand in brands:
        for locale in LAUNCH_LOCALES:
            mc = manga.get((brand, locale), 0)
            bc = book.get((brand, locale), 0)
            pc = podcast.get((brand, locale), 0)
            m_ok, b_ok, p_ok = mc > 0, bc > 0, pc > 0
            cells_covered += int(m_ok) + int(b_ok) + int(p_ok)
            complete = m_ok and b_ok and p_ok
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
            if not complete:
                miss = [s for s, ok in (("manga", m_ok), ("book", b_ok), ("podcast", p_ok)) if not ok]
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
    print("\nPASS — all 37 brands x 4 locales have manga + book + podcast plans (444/444 cells).")
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
