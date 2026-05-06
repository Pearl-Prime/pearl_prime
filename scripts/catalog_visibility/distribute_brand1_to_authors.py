#!/usr/bin/env python3
"""Distribute brand-1 (stillness_press) catalog rows across the 12 pen-name authors.

Inputs:
- artifacts/catalog/pearl_prime_book_script_catalogs/{en_US,ja_JP,zh_CN,zh_TW}_catalog.csv
- config/catalog_planning/teacher_brand_author_roster.yaml (§01 stillness_press authors)
- config/brand_author_assignments.yaml (topic→default_author affinity rules)

Allocation algorithm:
1. Read every brand=stillness_press row from the catalog.
2. For each row, look up topic in brand_author_assignments.yaml topic-affinity rules
   to find primary author + alternates.
3. Round-robin assign within (primary + alternates) so per-author load stays balanced
   (target ~16 books/author for en_US 192 titles).
4. Write distribution CSV to artifacts/catalog/brand1_author_distribution_<locale>.csv
   with columns: locale, brand, title, subtitle, topic, persona, author_id, author_pen_name,
   allocation_reason (primary | alternate | overflow).

Authority:
- docs/PEN_NAME_AUTHOR_SYSTEM.md (anti-spam: no voice >2× per brand within a locale)
- AUTHOR_ASSET_WORKBOOK.md §1 (author_id must exist in registry)
- TEACHER_MODE_AUTHORING_PLAYBOOK.md §8 (Teacher Mode interpreter voice)

Usage:
  python3 scripts/catalog_visibility/distribute_brand1_to_authors.py \
      --locale en_US [--dry-run] [--out artifacts/catalog/brand1_author_distribution_en_US.csv]
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG_DIR = REPO_ROOT / "artifacts/catalog/pearl_prime_book_script_catalogs"
ROSTER = REPO_ROOT / "config/catalog_planning/teacher_brand_author_roster.yaml"
ASSIGNMENTS = REPO_ROOT / "config/brand_author_assignments.yaml"
OUT_DIR = REPO_ROOT / "artifacts/catalog"

BRAND = "stillness_press"


def load_authors() -> list[str]:
    """Return ordered list of 12 stillness_press author_ids from the roster."""
    d = yaml.safe_load(ROSTER.read_text(encoding="utf-8"))
    return [a["author_id"] for a in d[BRAND]["authors"]]


def load_topic_affinity() -> dict[str, list[str]]:
    """Build topic → [primary_author, alternates...] from brand_author_assignments.yaml.

    Reads the topic-affinity rows (those with topic_ids set) and groups multiple rows
    on the same topic into a single ordered list (first row's default_author is primary).
    Adds in-line alternates parsed from comments (# also: <author_id>) where they exist.
    For robustness, this routine also walks the roster to find every author whose
    .topics include each topic and merges them as alternates — that way the comment
    annotations in the YAML are not load-bearing.
    """
    d = yaml.safe_load(ASSIGNMENTS.read_text(encoding="utf-8"))
    primary_by_topic: dict[str, str] = {}
    for row in d.get("assignments", []):
        if row.get("brand_id") != BRAND:
            continue
        topics = row.get("topic_ids") or []
        author = row.get("default_author")
        if not topics or not author:
            continue
        for t in topics:
            primary_by_topic.setdefault(t, author)

    # Build alternates from roster topic_ids
    roster = yaml.safe_load(ROSTER.read_text(encoding="utf-8"))
    alternates_by_topic: dict[str, list[str]] = defaultdict(list)
    for a in roster[BRAND]["authors"]:
        for t in a.get("topics") or []:
            if a["author_id"] not in alternates_by_topic[t]:
                alternates_by_topic[t].append(a["author_id"])

    # Compose ordered list per topic: primary first, then any roster alternates not already present
    out: dict[str, list[str]] = {}
    all_topics = set(primary_by_topic) | set(alternates_by_topic)
    for t in all_topics:
        primary = primary_by_topic.get(t)
        roster_alts = alternates_by_topic.get(t, [])
        ordered: list[str] = []
        if primary:
            ordered.append(primary)
        for a in roster_alts:
            if a not in ordered:
                ordered.append(a)
        out[t] = ordered
    return out


def load_positioning_pools() -> dict[str, list[str]]:
    """Return positioning_profile → [author_ids] from roster (load-balance fallback)."""
    roster = yaml.safe_load(ROSTER.read_text(encoding="utf-8"))
    pools: dict[str, list[str]] = defaultdict(list)
    for a in roster[BRAND]["authors"]:
        pools[a["positioning"]].append(a["author_id"])
    return dict(pools)


def author_positioning(author_id: str) -> str:
    roster = yaml.safe_load(ROSTER.read_text(encoding="utf-8"))
    for a in roster[BRAND]["authors"]:
        if a["author_id"] == author_id:
            return a["positioning"]
    return "somatic_companion"


def distribute(locale: str) -> tuple[list[dict[str, Any]], Counter, Counter]:
    """Walk catalog rows for the locale, assign each to an author. Returns (rows, per_author, per_topic).

    Algorithm:
    1. Topic affinity gives an ordered candidate list (primary + alternates).
    2. Pick least-loaded among candidates, preferring primary on ties.
    3. SOFT CAP: if least-loaded candidate is already at >= ceil(total/12 * 1.4), fall back
       to the least-loaded author in the SAME positioning_profile pool. This prevents any
       single author from dominating just because they're the only primary for 3+ topics
       (e.g. noor_ibrahim's courage + financial_anxiety + financial_stress = 34 books at v1).
    4. Reason is recorded: primary | alternate | overflow_balance | overflow_no_affinity.
    """
    csv_path = CATALOG_DIR / f"{locale}_catalog.csv"
    if not csv_path.exists():
        print(f"Catalog not found: {csv_path}", file=sys.stderr)
        sys.exit(2)

    # First pass: count total brand-1 rows so we can compute the soft cap
    total = 0
    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("brand") == BRAND:
                total += 1
    target_per_author = max(1, total // 12)
    soft_cap = int(target_per_author * 1.4)  # allow 40% over target before redirect

    affinity = load_topic_affinity()
    authors = load_authors()
    positioning_pools = load_positioning_pools()
    pen_names = {
        a["author_id"]: a["display_name"]
        for a in yaml.safe_load(ROSTER.read_text(encoding="utf-8"))[BRAND]["authors"]
    }

    per_author: Counter = Counter({a: 0 for a in authors})
    per_topic: Counter = Counter()
    out: list[dict[str, Any]] = []

    with csv_path.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            if row.get("brand") != BRAND:
                continue
            topic = row.get("topic", "").strip().strip('"').strip()
            per_topic[topic] += 1

            candidates = affinity.get(topic, [])
            chosen: str
            reason: str

            if not candidates:
                # No topic affinity — overflow to least-loaded author overall
                chosen = min(authors, key=lambda a: per_author[a])
                reason = "overflow_no_affinity"
            else:
                ranked = sorted(candidates, key=lambda a: (per_author[a], candidates.index(a)))
                pick = ranked[0]
                if per_author[pick] < soft_cap:
                    chosen = pick
                    reason = "primary" if pick == candidates[0] else "alternate"
                else:
                    # Cap hit on all candidates; widen to positioning_profile pool
                    profile = author_positioning(candidates[0])
                    pool = positioning_pools.get(profile, authors)
                    chosen = min(pool, key=lambda a: per_author[a])
                    reason = "overflow_balance"

            per_author[chosen] += 1
            out.append({
                "locale": row.get("locale", locale),
                "brand": BRAND,
                "title": row.get("title", "").strip(),
                "subtitle": row.get("subtitle", "").strip(),
                "topic": topic,
                "persona": row.get("persona", "").strip(),
                "teacher_id": row.get("teacher_id", "").strip(),
                "author_id": chosen,
                "author_pen_name": pen_names.get(chosen, chosen),
                "allocation_reason": reason,
            })
    return out, per_author, per_topic


def main() -> int:
    ap = argparse.ArgumentParser(description="Distribute brand-1 catalog rows across 12 pen-name authors.")
    ap.add_argument("--locale", default="en_US", choices=["en_US", "ja_JP", "zh_CN", "zh_TW"])
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    rows, per_author, per_topic = distribute(args.locale)
    out_path = args.out or (OUT_DIR / f"brand1_author_distribution_{args.locale}.csv")

    print(f"=== brand-1 ({BRAND}) distribution — locale={args.locale} ===\n")
    print(f"Total rows: {len(rows)}")
    print(f"\nTopic distribution ({len(per_topic)} unique):")
    for t, n in per_topic.most_common():
        print(f"  {n:3d}  {t}")
    print(f"\nPer-author allocation (target ~{len(rows) // 12 + 1} per author):")
    for a, n in per_author.most_common():
        print(f"  {n:3d}  {a}")
    print(f"\nAllocation reasons:")
    reason_count = Counter(r["allocation_reason"] for r in rows)
    for reason, n in reason_count.most_common():
        print(f"  {n:3d}  {reason}")

    if args.dry_run:
        print(f"\n[dry-run] would write {len(rows)} rows to {out_path.relative_to(REPO_ROOT)}")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nWrote {out_path.relative_to(REPO_ROOT)} ({len(rows)} rows)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
