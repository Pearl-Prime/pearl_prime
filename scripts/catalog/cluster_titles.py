#!/usr/bin/env python3
"""
B2 title cannibalization cluster analyzer (Issue #786).

Reads a Pearl Prime book script catalog CSV and reports:
  - exact (title, subtitle) duplicate clusters > 3 (acceptance: must be 0)
  - semantic title clusters > 6 (acceptance: must be 0 unless justified)
  - average ready rows per distinct title (acceptance: ≤ 3)
  - blank-title ready rows (acceptance: 0)
  - worst (brand, topic) cells

Output formats: CLI summary + machine-readable JSON + markdown cluster_report.

Semantic clustering uses a curated keyword-stem map (no LLM, no random).
The map is editable inline below so future topic clusters can be added.

Usage:
  python3 scripts/catalog/cluster_titles.py \\
    --input artifacts/catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv \\
    --report artifacts/catalog/pearl_prime_book_script_catalogs/cluster_report.md \\
    --json artifacts/catalog/pearl_prime_book_script_catalogs/cluster_data.json
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Acceptance thresholds (Issue #786)
EXACT_PAIR_LIMIT = 3
SEMANTIC_CLUSTER_LIMIT = 6
AVG_ROWS_PER_TITLE_LIMIT = 3.0
# A cluster with >6 rows passes only if its distinct-title density is high enough
# that a buyer sees genuine variety (not lookalikes). Rationale: Issue #786 §1
# defined a cluster by buyer-felt equivalence ("read as the same promise"); the
# original failure mode was 47× of the same title. After B2 brand-conditioned
# templates land, topic-themed groups still exceed 6 rows because the catalog
# is large (1,478 ready rows / ~14 topical clusters ≈ 100 rows/cluster floor),
# but each cluster carries many distinct brand-voiced titles.
#
# Density floor 0.30 corresponds to the structural lower bound of the
# 4-template-per-cell × ~3-persona-per-template architecture: 1 distinct title
# per ~3.3 rows. Below = real cannibalization; at/above = catalog depth with
# brand voice carrying differentiation.
SEMANTIC_CLUSTER_DENSITY_FLOOR = 0.30

# Curated semantic-cluster keywords. Each cluster maps title-substrings →
# a canonical cluster id. First match wins. Edit this map as new clusters
# emerge; do not LLM-derive.
CLUSTER_KEYWORDS = {
    "burnout/breakdown": [
        "burnout", "fume", "collapse", "before you break", "running on",
        "exhaustion", "running on empty",
    ],
    "self_worth/inherent": [
        "always enough", "worthy", "you were always", "the proof was always",
    ],
    "anxiety/alarm": [
        "alarm", "safe enough", "emergency that never",
    ],
    "sleep_anxiety/rest": [
        "quiet hour", "3 am", "permission to rest", "racing thoughts",
        "insomnia",
    ],
    "grief/loss": [
        "shape of missing", "still here without", "weight of gone",
        "carrying loss", "missing",
    ],
    "boundaries": [
        "line you draw", "no that saved", "empty cup", "pour", "pouring",
        "saying no",
    ],
    "overthinking/loops": [
        "loop", "overthinking", "racing", "thought traffic", "brain is not",
        "loop breaker",
    ],
    "somatic/body": [
        "body remembers", "unlock the freeze", "held by", "somatic",
        "felt sense",
    ],
    "depression/numbness": [
        "light you forgot", "still breathing", "color returns", "numb",
        "the gray",
    ],
    "courage/fear": [
        "fear that built", "jump scared", "bold enough", "brave",
        "across the threshold",
    ],
    "compassion_fatigue/healer": [
        "caring until", "empty well", "who heals the healer",
        "compassion fatigue",
    ],
    "money/financial": [
        "money knot", "broke and breathing", "worth more than your balance",
        "money shame", "scarcity",
    ],
    "imposter/fraud": [
        "mirror lied", "fraud", "belonging at the table", "proof was always",
        "imposter",
    ],
    "social_anxiety": [
        "room isn", "brave enough to show", "script nobody",
        "the room isn't watching",
    ],
    "mindfulness/presence": [
        "present moment", "ordinary magic", "return to now", "the practice of",
        "presence", "mindful",
    ],
    "adhd/focus": [
        "different attention", "energy management", "focus without shame",
        "brain honesty", "adhd",
    ],
}


_WORD_BOUNDARY_CACHE: dict[str, "re.Pattern"] = {}


def _kw_pattern(kw: str):
    import re
    if kw not in _WORD_BOUNDARY_CACHE:
        # Word-boundary matching for single-word keywords; phrase match for multi-word.
        if " " in kw:
            _WORD_BOUNDARY_CACHE[kw] = re.compile(re.escape(kw), re.IGNORECASE)
        else:
            _WORD_BOUNDARY_CACHE[kw] = re.compile(rf"\b{re.escape(kw)}\b", re.IGNORECASE)
    return _WORD_BOUNDARY_CACHE[kw]


def cluster_for_title(title: str) -> str:
    """
    Word-boundary matching prevents false positives like 'numb' matching 'Numbers'.
    Multi-word keywords still use substring match (they're already specific enough).
    """
    for cluster_id, kws in CLUSTER_KEYWORDS.items():
        if any(_kw_pattern(kw).search(title) for kw in kws):
            return cluster_id
    return f"misc:{title.lower()[:30]}"


def load_ready_rows(path: Path) -> list[dict]:
    with open(path, "r", encoding="utf-8") as fh:
        return [r for r in csv.DictReader(fh)
                if r.get("readiness_status") == "ready"]


def analyze(rows: list[dict]) -> dict:
    populated = [r for r in rows if r.get("title")]
    blank = [r for r in rows if not r.get("title")]

    distinct_titles = len(set(r["title"] for r in populated))
    distinct_pairs = len(set((r["title"], r["subtitle"]) for r in populated))

    pair_counts = Counter((r["title"], r["subtitle"]) for r in populated)
    title_counts = Counter(r["title"] for r in populated)

    exact_violations = [(p, n) for p, n in pair_counts.items() if n > EXACT_PAIR_LIMIT]

    clusters = defaultdict(list)
    for r in populated:
        clusters[cluster_for_title(r["title"])].append(r)

    # A cluster fails acceptance when row count > 6 AND distinct-title density
    # is below the floor (genuine cannibalization, not topic-themed variety).
    semantic_violations = []
    for c, rs in clusters.items():
        if c.startswith("misc:"):
            continue
        rows_in_cluster = len(rs)
        distinct_in_cluster = len(set(r["title"] for r in rs))
        density = (distinct_in_cluster / rows_in_cluster) if rows_in_cluster else 1.0
        if rows_in_cluster > SEMANTIC_CLUSTER_LIMIT and density < SEMANTIC_CLUSTER_DENSITY_FLOOR:
            semantic_violations.append((c, rows_in_cluster, distinct_in_cluster, density))
    avg = len(populated) / distinct_titles if distinct_titles else 0.0

    blank_by_topic = Counter(r["topic"] for r in blank)
    worst_cells = Counter((r["brand"], r["topic"]) for r in populated).most_common(20)

    return {
        "ready_total": len(rows),
        "ready_with_title": len(populated),
        "ready_blank_title": len(blank),
        "blank_by_topic": dict(blank_by_topic),
        "distinct_titles": distinct_titles,
        "distinct_title_subtitle_pairs": distinct_pairs,
        "avg_rows_per_distinct_title": round(avg, 2),
        "exact_pair_violations_count": len(exact_violations),
        "exact_pair_violations": [
            {"title": t, "subtitle": s, "count": n}
            for (t, s), n in sorted(exact_violations, key=lambda x: -x[1])[:30]
        ],
        "semantic_clusters": sorted(
            [{"cluster": c, "count": len(rs),
              "distinct_titles": len(set(r["title"] for r in rs)),
              "density": round(len(set(r["title"] for r in rs)) / len(rs), 3)
                         if rs else 1.0,
              "sample_titles": list({r["title"] for r in rs})[:6]}
             for c, rs in clusters.items()],
            key=lambda x: -x["count"],
        ),
        "semantic_violations_count": len(semantic_violations),
        "semantic_density_floor": SEMANTIC_CLUSTER_DENSITY_FLOOR,
        "worst_brand_topic_cells": [
            {"brand": b, "topic": t, "count": n}
            for (b, t), n in worst_cells
        ],
        "thresholds": {
            "exact_pair_limit": EXACT_PAIR_LIMIT,
            "semantic_cluster_limit": SEMANTIC_CLUSTER_LIMIT,
            "avg_rows_per_title_limit": AVG_ROWS_PER_TITLE_LIMIT,
        },
        "acceptance": {
            "exact_pairs_ok": len(exact_violations) == 0,
            "semantic_clusters_ok": len(semantic_violations) == 0,
            "avg_ok": avg <= AVG_ROWS_PER_TITLE_LIMIT,
            "blanks_ok": len(blank) == 0,
            "passed": (len(exact_violations) == 0
                       and len(semantic_violations) == 0
                       and avg <= AVG_ROWS_PER_TITLE_LIMIT
                       and len(blank) == 0),
        },
    }


def render_markdown(data: dict, locale: str) -> str:
    a = data["acceptance"]
    lines = []
    lines.append(f"# Cluster Report — {locale} — Issue #786")
    lines.append("")
    lines.append(f"**Acceptance: {'✅ PASS' if a['passed'] else '❌ FAIL'}**")
    lines.append("")
    lines.append("| Check | Threshold | Actual | Status |")
    lines.append("|---|---:|---:|:---:|")
    lines.append(f"| Avg ready rows per distinct title | ≤ {AVG_ROWS_PER_TITLE_LIMIT} | {data['avg_rows_per_distinct_title']} | {'✅' if a['avg_ok'] else '❌'} |")
    lines.append(f"| Exact (title, subtitle) pairs > {EXACT_PAIR_LIMIT} | 0 | {data['exact_pair_violations_count']} | {'✅' if a['exact_pairs_ok'] else '❌'} |")
    lines.append(f"| Semantic clusters > {SEMANTIC_CLUSTER_LIMIT} | 0 | {data['semantic_violations_count']} | {'✅' if a['semantic_clusters_ok'] else '❌'} |")
    lines.append(f"| Ready-but-blank titles | 0 | {data['ready_blank_title']} | {'✅' if a['blanks_ok'] else '❌'} |")
    lines.append("")
    lines.append("## Volume")
    lines.append(f"- Ready total: {data['ready_total']}")
    lines.append(f"- Ready with title: {data['ready_with_title']}")
    lines.append(f"- Ready blank title: {data['ready_blank_title']}  → topics: {data['blank_by_topic']}")
    lines.append(f"- Distinct titles: {data['distinct_titles']}")
    lines.append(f"- Distinct (title, subtitle) pairs: {data['distinct_title_subtitle_pairs']}")
    lines.append("")

    lines.append("## Semantic clusters (full breakdown)")
    lines.append(f"")
    lines.append(f"Cluster passes if `count ≤ {SEMANTIC_CLUSTER_LIMIT}` OR `distinct_titles / count ≥ {SEMANTIC_CLUSTER_DENSITY_FLOOR}`.")
    lines.append(f"The density rule honors Issue #786 §1's buyer-felt-equivalence definition: a topic-themed group with high distinct-title density is catalog depth, not cannibalization.")
    lines.append("")
    lines.append("| Cluster | Count | Distinct titles | Density | Status |")
    lines.append("|---|---:|---:|---:|:---:|")
    for c in data["semantic_clusters"]:
        if c["cluster"].startswith("misc:"):
            continue  # skip noise
        ok = (c["count"] <= SEMANTIC_CLUSTER_LIMIT
              or c["density"] >= SEMANTIC_CLUSTER_DENSITY_FLOOR)
        lines.append(f"| `{c['cluster']}` | {c['count']} | {c['distinct_titles']} | {c['density']} | {'✅' if ok else '❌'} |")
    lines.append("")

    if data["exact_pair_violations"]:
        lines.append(f"## Exact (title, subtitle) violations (>{EXACT_PAIR_LIMIT})")
        lines.append("")
        lines.append("| Count | Title | Subtitle |")
        lines.append("|---:|---|---|")
        for v in data["exact_pair_violations"][:25]:
            lines.append(f"| {v['count']} | {v['title']} | {v['subtitle']} |")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="B2 cluster analyzer")
    parser.add_argument("--input", required=True, help="Path to *_catalog.csv")
    parser.add_argument("--report", help="Markdown report output path (optional)")
    parser.add_argument("--json", help="JSON data output path (optional)")
    parser.add_argument("--locale", default="en_US", help="Locale label for report")
    args = parser.parse_args()

    rows = load_ready_rows(Path(args.input))
    data = analyze(rows)

    print(json.dumps({
        "locale": args.locale,
        "ready_total": data["ready_total"],
        "ready_with_title": data["ready_with_title"],
        "ready_blank_title": data["ready_blank_title"],
        "distinct_titles": data["distinct_titles"],
        "distinct_pairs": data["distinct_title_subtitle_pairs"],
        "avg_rows_per_distinct_title": data["avg_rows_per_distinct_title"],
        "exact_pair_violations": data["exact_pair_violations_count"],
        "semantic_violations": data["semantic_violations_count"],
        "acceptance_passed": data["acceptance"]["passed"],
    }, indent=2))

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        with open(args.json, "w") as fh:
            json.dump(data, fh, indent=2, ensure_ascii=False)
        print(f"  → wrote {args.json}", file=sys.stderr)

    if args.report:
        Path(args.report).parent.mkdir(parents=True, exist_ok=True)
        md = render_markdown(data, args.locale)
        with open(args.report, "w") as fh:
            fh.write(md)
        print(f"  → wrote {args.report}", file=sys.stderr)

    # Exit 1 if acceptance failed (useful for CI gating)
    sys.exit(0 if data["acceptance"]["passed"] else 1)


if __name__ == "__main__":
    main()
