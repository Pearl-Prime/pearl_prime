#!/usr/bin/env python3
"""
Build/refresh the en_US ebook assembly progress tracker.

RESUMABLE BY DESIGN: this script recomputes status from disk every run. It does
NOT hand-maintain state. Re-run it any time to get the truthful % assembled as
the Layer 3 fan-out grinds.

Plan basis (SSOT):
  - config/manga/canonical_brand_list.yaml         (37 brands: tier, demographic, topics)
  - artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv  (5 series x 5 books = 25/brand)

Status basis (scanned from disk):
  - artifacts/catalog/brand1_deep/<brand>/en_US/books/epub/*.epub   (the fan-out template dir)
  - artifacts/weekly_packages/<brand>/**/kdp/*.epub                  (MVP packaged path)

Row granularity: 37 brands x 5 series x 5 books = 925 rows.
Each brand's 5 series map to [primary_topic, *secondary_topics][:5].
A (brand, series_topic) with N real EPUBs marks the first N book-rows assembled.

Output:
  artifacts/catalog/assembly_progress_en_US.tsv   (925 data rows + header)
  + prints a summary (X/925 books, Y/37 brands) to stdout.

Usage:
  PYTHONPATH=. python3 scripts/catalog/build_assembly_progress_en_US.py
"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BRAND_LIST = REPO / "config/manga/canonical_brand_list.yaml"
EN_PLAN = REPO / "artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv"
OUT = REPO / "artifacts/catalog/assembly_progress_en_US.tsv"

COLUMNS = [
    "brand_id", "tier", "demographic", "series_index", "series_topic",
    "book_index", "status", "epub_path", "locale",
]


def load_brands() -> dict:
    """Parse canonical_brand_list.yaml -> {brand_id: {tier, demographic, primary_topic, secondary_topics[]}}."""
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(BRAND_LIST.read_text(encoding="utf-8"))
        out = {}
        for bid, row in (data.get("brands") or {}).items():
            out[bid] = {
                "tier": row.get("tier", ""),
                "demographic": row.get("demographic", ""),
                "primary_topic": row.get("primary_topic", ""),
                "secondary_topics": list(row.get("secondary_topics") or []),
            }
        return out
    except Exception:
        # Minimal fallback parser (no PyYAML): regex the block scalars.
        text = BRAND_LIST.read_text(encoding="utf-8")
        out = {}
        cur = None
        for line in text.splitlines():
            m = re.match(r"^  ([a-z][a-z0-9_]+):\s*$", line)
            if m:
                cur = m.group(1)
                out[cur] = {"tier": "", "demographic": "", "primary_topic": "", "secondary_topics": []}
                continue
            if cur:
                if (mm := re.match(r"^    tier:\s*(\S+)", line)):
                    out[cur]["tier"] = mm.group(1)
                elif (mm := re.match(r"^    demographic:\s*(\S+)", line)):
                    out[cur]["demographic"] = mm.group(1)
                elif (mm := re.match(r"^    primary_topic:\s*(\S+)", line)):
                    out[cur]["primary_topic"] = mm.group(1)
                elif (mm := re.match(r"^    secondary_topics:\s*\[(.*)\]", line)):
                    out[cur]["secondary_topics"] = [t.strip() for t in mm.group(1).split(",") if t.strip()]
        # drop any non-brand keys captured accidentally
        return {k: v for k, v in out.items() if v["primary_topic"]}


def load_plan() -> dict:
    """Parse the en_US allocation TSV -> {brand_id: (series_count, books_per_series)}."""
    out = {}
    lines = EN_PLAN.read_text(encoding="utf-8").splitlines()
    header = lines[0].split("\t")
    idx = {h: i for i, h in enumerate(header)}
    for line in lines[1:]:
        if not line.strip():
            continue
        c = line.split("\t")
        bid = c[idx["brand_id"]]
        try:
            sc = int(c[idx["series_count"]])
            bps = int(c[idx["books_per_series"]])
        except (ValueError, KeyError):
            sc, bps = 5, 5
        out[bid] = (sc, bps)
    return out


def topic_from_epub_name(name: str, topics: list[str]) -> str | None:
    """Match an EPUB filename (e.g. book_anxiety_gen_z_professionals.epub) to a series topic."""
    stem = name.lower()
    # longest topic first so multi-word topics win
    for t in sorted(topics, key=len, reverse=True):
        if t and t.lower() in stem:
            return t
    return None


def assembled_topics_for_brand(brand: str, topics: list[str]) -> dict:
    """Scan disk; return {series_topic: [epub_path,...]} of real assembled EPUBs."""
    found: dict[str, list[str]] = {t: [] for t in topics}
    patterns = [
        REPO / f"artifacts/catalog/brand1_deep/{brand}/en_US/books/epub/*.epub",
        REPO / f"artifacts/weekly_packages/{brand}/**/kdp/*.epub",
    ]
    seen = set()
    for pat in patterns:
        for p in glob.glob(str(pat), recursive=True):
            if p in seen:
                continue
            seen.add(p)
            name = Path(p).name
            if name.lower().endswith(".ja.epub"):
                continue  # en_US tracker only
            t = topic_from_epub_name(name, topics)
            if t is None:
                t = topics[0] if topics else "unknown"  # bucket unmatched into primary
            found.setdefault(t, []).append(str(Path(p).relative_to(REPO)))
    return found


def main() -> int:
    brands = load_brands()
    plan = load_plan()
    rows = []
    total = assembled = 0
    brands_started = set()

    for bid in sorted(brands):
        meta = brands[bid]
        sc, bps = plan.get(bid, (5, 5))
        series_topics = ([meta["primary_topic"]] + meta["secondary_topics"])[:sc]
        while len(series_topics) < sc:  # pad if a brand has < sc topics
            series_topics.append(meta["primary_topic"])
        disk = assembled_topics_for_brand(bid, series_topics)

        for s_i in range(sc):
            topic = series_topics[s_i]
            epubs = disk.get(topic, [])
            for b_i in range(bps):
                total += 1
                if b_i < len(epubs):
                    status, path = "assembled", epubs[b_i]
                    assembled += 1
                    brands_started.add(bid)
                else:
                    status, path = "planned", ""
                rows.append([
                    bid, meta["tier"], meta["demographic"], str(s_i + 1), topic,
                    str(b_i + 1), status, path, "en_US",
                ])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", encoding="utf-8") as f:
        f.write("\t".join(COLUMNS) + "\n")
        for r in rows:
            f.write("\t".join(r) + "\n")

    pct = (assembled / total * 100) if total else 0.0
    print(f"en_US ebook assembly: {assembled}/{total} books ({pct:.1f}%)")
    print(f"brands started: {len(brands_started)}/{len(brands)}")
    if brands_started:
        print("  " + ", ".join(sorted(brands_started)))
    print(f"tracker: {OUT.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
