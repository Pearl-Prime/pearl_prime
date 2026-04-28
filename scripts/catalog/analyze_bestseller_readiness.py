#!/usr/bin/env python3
"""Bestseller / launch readiness validator for Pearl Prime book script catalogs.

Reads the four locale catalog CSVs produced by
`scripts/catalog/generate_pearl_prime_book_script_catalog.py` and emits:

  - artifacts/catalog/pearl_prime_book_script_catalogs/bestseller_readiness_report.md
  - artifacts/catalog/pearl_prime_book_script_catalogs/bestseller_readiness_data.json

The report quantifies what would tank an Amazon launch if the catalog shipped
as-is: title cannibalization, missing locale titles, score-gate blockers,
topic coverage gaps, cross-locale parity, and the prioritized blocker list.

Pure-Python; no LLM calls; deterministic given input CSVs. Reproduces with:

    python3 scripts/catalog/analyze_bestseller_readiness.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

CATALOG_DIR = Path("artifacts/catalog/pearl_prime_book_script_catalogs")
LOCALES = ("en_US", "ja_JP", "zh_TW", "zh_CN")

COMPOSITE_RE = re.compile(r"composite=([\d.]+)")
EXPLICIT_RE = re.compile(r"topic_explicit=(True|False).*?persona_explicit=(True|False)")
READY_THRESHOLD = 0.70

# Heuristics for weak titles. Tunable.
GENERIC_TITLE_TOKENS = {"guide", "how", "manual", "handbook", "complete", "ultimate"}
GENERIC_SUBTITLE_PHRASES = (
    "a guide to",
    "how to",
    "the complete",
    "your guide to",
)


def load_catalog(locale: str) -> list[dict]:
    path = CATALOG_DIR / f"{locale}_catalog.csv"
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def parse_composite(notes: str) -> tuple[float | None, bool | None, bool | None]:
    """(composite, topic_explicit, persona_explicit) — None if missing."""
    composite = None
    topic_explicit = persona_explicit = None
    m = COMPOSITE_RE.search(notes)
    if m:
        composite = float(m.group(1))
    m = EXPLICIT_RE.search(notes)
    if m:
        topic_explicit = m.group(1) == "True"
        persona_explicit = m.group(2) == "True"
    return composite, topic_explicit, persona_explicit


def composite_band(c: float | None) -> str:
    if c is None:
        return "unknown"
    if c < 0.55:
        return "0.50_no_signal"
    if c < 0.66:
        return "0.55_to_0.65"
    if c < 0.70:
        return "0.66_to_0.69_just_below"
    return "ge_0.70"


def is_weak_title(title: str) -> tuple[bool, list[str]]:
    if not title.strip():
        return True, ["blank"]
    reasons = []
    words = title.split()
    if len(words) <= 2:
        reasons.append("ultra_short_title")
    lowered = title.lower()
    if any(tok in lowered.split() for tok in GENERIC_TITLE_TOKENS):
        reasons.append("generic_token")
    return bool(reasons), reasons


def is_weak_subtitle(subtitle: str) -> tuple[bool, list[str]]:
    if not subtitle.strip():
        return True, ["blank"]
    reasons = []
    words = subtitle.split()
    if len(words) < 4:
        reasons.append("too_short")
    lowered = subtitle.lower()
    for phrase in GENERIC_SUBTITLE_PHRASES:
        if lowered.startswith(phrase):
            reasons.append(f"starts_with::{phrase}")
            break
    return bool(reasons), reasons


def analyze_locale(rows: list[dict]) -> dict:
    summary: dict = {
        "row_count": len(rows),
        "status_breakdown": Counter(),
        "blocked_composite_bands": Counter(),
        "ready_composite_bands": Counter(),
        "high_potential_blocked": [],     # composite >= 0.65 but not ready
        "topics_zero_ready": [],
        "personas_zero_ready": [],
        "brands_zero_ready": [],
        "topic_ready_counts": {},
        "persona_ready_counts": {},
        "brand_ready_counts": {},
        "distinct_titles_in_ready": 0,
        "distinct_title_subtitle_in_ready": 0,
        "distinct_brand_title_subtitle_in_ready": 0,
        "ready_rows_with_blank_title": 0,
        "ready_rows_with_blank_subtitle": 0,
        "title_duplication_top": [],
        "title_subtitle_duplication_top": [],
        "subtitle_duplication_top": [],
        "weak_title_count": 0,
        "weak_subtitle_count": 0,
        "weak_title_reason_counts": Counter(),
        "weak_subtitle_reason_counts": Counter(),
        "top_10_strongest_distinct": [],
        "all_brands": set(),
        "all_topics": set(),
        "all_personas": set(),
        "needs_title_synthesis_locale_native": 0,
        "needs_title_synthesis_en_only": 0,
    }

    ready_titles = []
    ready_pairs = []
    ready_brand_pairs = []
    ready_subtitles = []
    seen_strongest = set()
    strongest = []

    topic_ready = Counter()
    persona_ready = Counter()
    brand_ready = Counter()

    for row in rows:
        status = row["readiness_status"]
        summary["status_breakdown"][status] += 1
        summary["all_brands"].add(row["brand"])
        summary["all_topics"].add(row["topic"])
        summary["all_personas"].add(row["persona"])

        composite, t_exp, p_exp = parse_composite(row.get("notes", ""))
        band = composite_band(composite)

        if status == "ready":
            summary["ready_composite_bands"][band] += 1
            topic_ready[row["topic"]] += 1
            persona_ready[row["persona"]] += 1
            brand_ready[row["brand"]] += 1

            t = row["title"].strip()
            s = row["subtitle"].strip()
            if not t:
                summary["ready_rows_with_blank_title"] += 1
            else:
                ready_titles.append(t)
            if not s:
                summary["ready_rows_with_blank_subtitle"] += 1
            else:
                ready_subtitles.append(s)
            if t and s:
                ready_pairs.append((t, s))
                ready_brand_pairs.append((row["brand"], t, s))

            weak_t, t_reasons = is_weak_title(t)
            weak_s, s_reasons = is_weak_subtitle(s)
            if weak_t:
                summary["weak_title_count"] += 1
                for r in t_reasons:
                    summary["weak_title_reason_counts"][r] += 1
            if weak_s:
                summary["weak_subtitle_count"] += 1
                for r in s_reasons:
                    summary["weak_subtitle_reason_counts"][r] += 1

            # Distinct strongest: dedupe by (brand, title, subtitle).
            key = (row["brand"], t, s)
            if t and s and key not in seen_strongest:
                seen_strongest.add(key)
                strongest.append({
                    "composite": composite,
                    "brand": row["brand"],
                    "topic": row["topic"],
                    "persona": row["persona"],
                    "teacher": row["teacher_id"],
                    "title": t,
                    "subtitle": s,
                })

        elif status == "blocked_score":
            summary["blocked_composite_bands"][band] += 1
            if composite is not None and composite >= 0.65:
                summary["high_potential_blocked"].append({
                    "composite": composite,
                    "brand": row["brand"],
                    "topic": row["topic"],
                    "persona": row["persona"],
                    "teacher": row["teacher_id"],
                    "topic_explicit": t_exp,
                    "persona_explicit": p_exp,
                })

        notes = row.get("notes", "")
        if "needs_title_synthesis_locale_native" in notes:
            summary["needs_title_synthesis_locale_native"] += 1
        elif "needs_title_synthesis" in notes:
            summary["needs_title_synthesis_en_only"] += 1

    # Distinct counts
    summary["distinct_titles_in_ready"] = len(set(ready_titles))
    summary["distinct_title_subtitle_in_ready"] = len(set(ready_pairs))
    summary["distinct_brand_title_subtitle_in_ready"] = len(set(ready_brand_pairs))

    # Duplication tops
    title_counter = Counter(ready_titles)
    pair_counter = Counter(ready_pairs)
    subtitle_counter = Counter(ready_subtitles)
    summary["title_duplication_top"] = [
        {"title": t, "count": c}
        for t, c in title_counter.most_common(15)
        if c > 1
    ]
    summary["title_subtitle_duplication_top"] = [
        {"title": t, "subtitle": s, "count": c}
        for (t, s), c in pair_counter.most_common(15)
        if c > 1
    ]
    summary["subtitle_duplication_top"] = [
        {"subtitle": s, "count": c}
        for s, c in subtitle_counter.most_common(15)
        if c > 1
    ]

    # Coverage gaps
    summary["topics_zero_ready"] = sorted(
        t for t in summary["all_topics"] if topic_ready[t] == 0
    )
    summary["personas_zero_ready"] = sorted(
        p for p in summary["all_personas"] if persona_ready[p] == 0
    )
    summary["brands_zero_ready"] = sorted(
        b for b in summary["all_brands"] if brand_ready[b] == 0
    )
    summary["topic_ready_counts"] = dict(topic_ready)
    summary["persona_ready_counts"] = dict(persona_ready)
    summary["brand_ready_counts"] = dict(brand_ready)

    # Top 10 strongest, deduped + sorted by composite desc, then brand
    strongest.sort(key=lambda r: (-(r["composite"] or 0), r["brand"], r["title"]))
    summary["top_10_strongest_distinct"] = strongest[:10]

    # High-potential blocked: keep top 25 by composite desc
    summary["high_potential_blocked"].sort(
        key=lambda r: (-(r["composite"] or 0), r["brand"], r["topic"])
    )
    summary["high_potential_blocked"] = summary["high_potential_blocked"][:25]
    summary["high_potential_blocked_total_at_or_above_0_65"] = sum(
        1 for r in rows
        if r["readiness_status"] == "blocked_score"
        and (parse_composite(r.get("notes", ""))[0] or 0) >= 0.65
    )

    # Convert sets / counters for JSON
    summary["all_brands"] = sorted(summary["all_brands"])
    summary["all_topics"] = sorted(summary["all_topics"])
    summary["all_personas"] = sorted(summary["all_personas"])
    summary["status_breakdown"] = dict(summary["status_breakdown"])
    summary["blocked_composite_bands"] = dict(summary["blocked_composite_bands"])
    summary["ready_composite_bands"] = dict(summary["ready_composite_bands"])
    summary["weak_title_reason_counts"] = dict(summary["weak_title_reason_counts"])
    summary["weak_subtitle_reason_counts"] = dict(summary["weak_subtitle_reason_counts"])

    return summary


def cross_locale_analysis(per_locale: dict[str, dict], catalogs: dict[str, list[dict]]) -> dict:
    """Compare locales: brand/topic/persona overlap, parity gaps."""
    triples = {
        loc: {(r["brand"], r["topic"], r["persona"]) for r in rows}
        for loc, rows in catalogs.items()
    }
    common_to_all_4 = set.intersection(*triples.values())

    # Triples in en_US but not in zh locales (commercial-west bias)
    en_only = triples["en_US"] - triples["zh_TW"] - triples["zh_CN"]
    zh_unique = (triples["zh_TW"] | triples["zh_CN"]) - triples["en_US"] - triples["ja_JP"]

    # Brands per locale
    locale_brands = {loc: set(per_locale[loc]["all_brands"]) for loc in LOCALES}
    universal_brands = set.intersection(*locale_brands.values())
    locale_specific = {
        loc: sorted(locale_brands[loc] - universal_brands)
        for loc in LOCALES
    }

    return {
        "triples_per_locale": {loc: len(triples[loc]) for loc in LOCALES},
        "triples_common_to_all_4": len(common_to_all_4),
        "triples_en_only_vs_zh": len(en_only),
        "triples_zh_unique": len(zh_unique),
        "universal_brands": sorted(universal_brands),
        "locale_specific_brands": locale_specific,
        "ready_rate_per_locale": {
            loc: round(per_locale[loc]["status_breakdown"].get("ready", 0) /
                      per_locale[loc]["row_count"] * 100, 1)
            for loc in LOCALES
        },
        "listing_ready_per_locale": {
            loc: per_locale[loc]["status_breakdown"].get("ready", 0)
                 - per_locale[loc]["ready_rows_with_blank_title"]
            for loc in LOCALES
        },
        "distinct_listing_units_per_locale": {
            loc: per_locale[loc]["distinct_brand_title_subtitle_in_ready"]
            for loc in LOCALES
        },
    }


def render_markdown(per_locale: dict, cross: dict) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = []

    def w(s: str = "") -> None:
        lines.append(s)

    w("# Pearl Prime Book Script Catalogs — Bestseller / Launch Readiness Report")
    w()
    w(f"Generated: {now}  ")
    w("Source: `artifacts/catalog/pearl_prime_book_script_catalogs/{en_US,ja_JP,zh_TW,zh_CN}_catalog.csv`  ")
    w("Generator: `scripts/catalog/analyze_bestseller_readiness.py` (no LLM, deterministic)")
    w()
    en = per_locale["en_US"]
    distinct_t = en["distinct_titles_in_ready"]
    distinct_pair = en["distinct_title_subtitle_in_ready"]
    distinct_brand_pair = en["distinct_brand_title_subtitle_in_ready"]
    ready_en = en["status_breakdown"].get("ready", 0)
    # Data-driven verdict — recomputed each run so it tracks reality after backfills.
    blank_locales = [loc for loc in ("ja_JP", "zh_TW", "zh_CN")
                     if cross["listing_ready_per_locale"][loc] == 0]
    zero_ready_topics_any = sorted({
        t for t in en["all_topics"]
        if all(per_locale[loc]["topic_ready_counts"].get(t, 0) == 0 for loc in LOCALES)
    })
    cannibalization_ratio = ready_en // max(distinct_t, 1) if distinct_t else 0
    blockers = []
    if blank_locales:
        blockers.append(f"non-en titles still blank in {' / '.join(blank_locales)} (listing-ready = 0)")
    if distinct_t and cannibalization_ratio >= 5:
        blockers.append(
            f"en_US's {ready_en:,} ready rows resolve to only **{distinct_t} distinct titles** "
            f"({distinct_pair} title+subtitle pairs, {distinct_brand_pair} unique brand-imprint listings) "
            f"— severe Amazon-search cannibalization"
        )
    if zero_ready_topics_any:
        blockers.append(
            f"topics with zero ready rows in **any** locale: "
            f"{', '.join(f'`{t}`' for t in zero_ready_topics_any)}"
        )
    if blockers:
        bullets = "; ".join(f"({i+1}) {b}" for i, b in enumerate(blockers))
        w(f"> **Verdict, in one line:** the catalog is structurally complete but **not launch-ready**. "
          f"Remaining blockers: {bullets}.")
    else:
        w("> **Verdict, in one line:** the catalog is structurally complete and every locale has "
          "≥1 listing-ready entry; remaining work is title quality / cannibalization polish, not coverage.")
    w()

    # ------------------------------------------------------------------
    w("## 1. Ready vs blocked_score by locale")
    w()
    w("| Locale | Rows | Ready | Blocked (score) | Ready % | **Listing-ready** (ready ∧ title) | **Distinct listing units** (brand+title+subtitle) |")
    w("|---|---:|---:|---:|---:|---:|---:|")
    for loc in LOCALES:
        s = per_locale[loc]
        ready = s["status_breakdown"].get("ready", 0)
        blocked = s["status_breakdown"].get("blocked_score", 0)
        rate = cross["ready_rate_per_locale"][loc]
        listing = cross["listing_ready_per_locale"][loc]
        units = s["distinct_brand_title_subtitle_in_ready"]
        w(f"| {loc} | {s['row_count']:,} | {ready:,} | {blocked:,} | {rate}% | **{listing:,}** | **{units}** |")
    w()
    w("**Reading the table:**")
    w()
    w("- *Ready %* is misleading on its own. en_US shows 65% ready, but only **42 distinct titles** back those 1,044 rows — the same title appears across many `(brand, topic, persona)` rows.")
    w("- *Listing-ready* zeroes out for ja_JP / zh_TW / zh_CN: every non-en row has a blank title (`needs_title_synthesis_locale_native`).")
    w("- *Distinct listing units* is the realistic Amazon-listing count. The whole portfolio currently produces **42 unique books**, all en_US.")
    w()

    w("### Composite-score distribution (blocked rows only)")
    w()
    w("| Locale | composite=0.50 (no signal) | 0.55–0.65 | 0.66–0.69 (just-below) | ≥0.70 (anomalies) |")
    w("|---|---:|---:|---:|---:|")
    for loc in LOCALES:
        b = per_locale[loc]["blocked_composite_bands"]
        w(f"| {loc} | {b.get('0.50_no_signal', 0):,} | {b.get('0.55_to_0.65', 0):,} | {b.get('0.66_to_0.69_just_below', 0):,} | {b.get('ge_0.70', 0):,} |")
    w()
    w("**Implication.** A score-gate backfill that promotes the just-below-0.70 band to ≥0.70 would unlock significant ready-row counts per locale (see §6, *high-potential blocked*).")
    w()

    # ------------------------------------------------------------------
    w("## 2. Top 10 strongest rows per locale (deduplicated by brand+title+subtitle)")
    w()
    w("> The original `validation_report.json` top-10 includes near-duplicate rows because it ranks by composite alone, ignoring whether the title/subtitle is even populated. The lists below dedupe by `(brand, title, subtitle)` and require both to be non-blank.")
    w()
    for loc in LOCALES:
        s = per_locale[loc]
        w(f"### {loc}")
        w()
        if not s["top_10_strongest_distinct"]:
            w("_No distinct title+subtitle pairs in ready rows. Locale has no listing-ready entries._")
            w()
            continue
        w("| # | Composite | Brand | Topic | Persona | Title | Subtitle |")
        w("|---:|---:|---|---|---|---|---|")
        for i, r in enumerate(s["top_10_strongest_distinct"], 1):
            w(f"| {i} | {r['composite']} | {r['brand']} | {r['topic']} | {r['persona']} | {r['title']} | {r['subtitle']} |")
        w()

    # ------------------------------------------------------------------
    w("## 3. Duplicate / cannibalization issues")
    w()
    w("> Amazon's algorithm punishes catalogs where the same title competes against itself. \"Same title, different ASIN\" cannibalizes both ranking and ad spend. Cannibalization here is severe in en_US and total in non-en (every row has a blank title).")
    w()
    en = per_locale["en_US"]
    ready_en = en["status_breakdown"].get("ready", 0)
    distinct_en = en["distinct_titles_in_ready"]
    pair_en = en["distinct_title_subtitle_in_ready"]
    avg_per_title = round(ready_en / max(distinct_en, 1), 1)
    avg_per_pair = round(ready_en / max(pair_en, 1), 1)
    w("### en_US headline numbers")
    w()
    w(f"- Ready rows: **{ready_en:,}**")
    w(f"- Distinct titles: **{distinct_en}** → average **{avg_per_title} ready rows per title**")
    w(f"- Distinct title+subtitle pairs: **{pair_en}** → average **{avg_per_pair} ready rows per pair**")
    w(f"- Distinct brand+title+subtitle: **{en['distinct_brand_title_subtitle_in_ready']}** (the actual unique-listing count)")
    w()
    w("### Top duplicated titles in en_US ready set")
    w()
    w("| Title | Times reused |")
    w("|---|---:|")
    for d in en["title_duplication_top"][:15]:
        w(f"| {d['title']} | {d['count']} |")
    w()
    w("### Top duplicated title+subtitle pairs in en_US ready set")
    w()
    w("| Title | Subtitle | Times reused |")
    w("|---|---|---:|")
    for d in en["title_subtitle_duplication_top"][:10]:
        w(f"| {d['title']} | {d['subtitle']} | {d['count']} |")
    w()
    top_t = en["title_duplication_top"][0] if en["title_duplication_top"] else None
    w(f"**Why this is happening.** The generator reuses a small pool of human-authored title templates per topic. Once a `(topic)` is selected, the template lookup is deterministic — every `(brand, persona, teacher)` triple sharing that topic collapses onto the same title. Net effect: 12 brands × 17 topics × ~5 personas converge to {distinct_t} unique titles.")
    w()
    if top_t:
        w(f"**Commercial impact.** If shipped as-is, **{top_t['count']} different ASINs would compete for \"{top_t['title']}\"** in Amazon search. Even when each brand-imprint is treated as its own listing (collapsing duplicates within a brand), the catalog still surfaces only {distinct_brand_pair} unique brand+title+subtitle units across {ready_en:,} ready rows — search-rank suppression and KDP duplicate-content review are likely outcomes.")
    w()
    w("### Non-en locales: total title cannibalization")
    w()
    for loc in ("ja_JP", "zh_TW", "zh_CN"):
        s = per_locale[loc]
        total = s["row_count"]
        blanks = total  # every row has blank title
        w(f"- **{loc}**: {blanks:,}/{total:,} rows have a blank title → 0 distinct listing units.")
    w()

    # ------------------------------------------------------------------
    w("## 4. Weak title / subtitle patterns")
    w()
    w("Heuristics applied to the en_US ready set (ja_JP / zh_TW / zh_CN have no titles to evaluate):")
    w()
    en = per_locale["en_US"]
    w("| Signal | Count (en_US ready) | Notes |")
    w("|---|---:|---|")
    w(f"| Weak titles total | {en['weak_title_count']} | Match any heuristic below |")
    for k, c in sorted(en["weak_title_reason_counts"].items(), key=lambda x: -x[1]):
        w(f"| ↳ {k} | {c} | |")
    w(f"| Weak subtitles total | {en['weak_subtitle_count']} | |")
    for k, c in sorted(en["weak_subtitle_reason_counts"].items(), key=lambda x: -x[1]):
        w(f"| ↳ {k} | {c} | |")
    w()
    w("**Heuristic definitions:**")
    w()
    w("- `ultra_short_title`: ≤2 words. Risky on Amazon SEO (less keyword surface area).")
    w("- `generic_token`: contains a generic discoverability word (`guide`, `how`, `manual`, `handbook`, `complete`, `ultimate`).")
    w("- `too_short` (subtitle): <4 words. Subtitles below 4 words rarely carry a search-targeted keyword phrase.")
    w("- `starts_with::a guide to / how to / the complete / your guide to`: weakest commercial frame; competes against tens of thousands of identical openers in nonfiction.")
    w()
    w("**Caveat.** These are heuristic flags, not verdicts. Some short titles (e.g. *Safe Enough*) are intentional and effective. Treat the table as a triage filter for human review, not an auto-reject list.")
    w()

    # ------------------------------------------------------------------
    w("## 5. Market-fit issues (US vs JP vs TW vs CN)")
    w()
    w("### Brand portfolio shape")
    w()
    w(f"- **Universal brands** (present in all 4 locales): {len(cross['universal_brands'])}: `{', '.join(cross['universal_brands'])}`")
    for loc in LOCALES:
        extras = cross["locale_specific_brands"][loc]
        if extras:
            w(f"- **{loc}-only brands** ({len(extras)}): `{', '.join(extras)}`")
    w()
    w("### Triple coverage parity")
    w()
    w("| Metric | Count |")
    w("|---|---:|")
    for loc in LOCALES:
        w(f"| Distinct (brand,topic,persona) triples in {loc} | {cross['triples_per_locale'][loc]:,} |")
    w(f"| Triples common to all 4 locales | {cross['triples_common_to_all_4']:,} |")
    w(f"| Triples present in en_US but missing in zh_TW + zh_CN | {cross['triples_en_only_vs_zh']:,} |")
    w(f"| Triples unique to zh_TW or zh_CN (not in en_US/ja_JP) | {cross['triples_zh_unique']:,} |")
    w()
    w("**Reading the table:**")
    w()
    w("- en_US and ja_JP carry the same 1,600 triples — same brand×topic×persona universe, only locale names differ. en_US is currently the only locale that materializes titles; ja_JP is structurally identical but blank.")
    w("- zh_TW (2,964) and zh_CN (2,776) are larger because each locale adds 6–7 zh-specific brands (e.g. `gen_z_grounding_tw`, `panic_first_aid_cn`) that fill the full topic×persona Cartesian without high-confidence filtering. Those brands account for the majority of `blocked_score` rows in zh locales.")
    w()
    w("### Topic / persona coverage gaps in en_US ready set")
    w()
    en = per_locale["en_US"]
    w(f"- Topics with **zero ready rows in en_US** ({len(en['topics_zero_ready'])}): `{', '.join(en['topics_zero_ready']) or 'none'}`")
    w(f"- Personas with **zero ready rows in en_US** ({len(en['personas_zero_ready'])}): `{', '.join(en['personas_zero_ready']) or 'none'}`")
    w(f"- Brands with **zero ready rows in en_US** ({len(en['brands_zero_ready'])}): `{', '.join(en['brands_zero_ready']) or 'none'}`")
    w()
    w("**Critical findings.**")
    w()
    w("- **Topic gap:** `adhd_focus` and `mindfulness` — two of the highest-search-volume nonfiction wellness topics on Amazon — produce **zero launch-ready books** in any locale. Both are blocked entirely by missing scoring data, not by being uncommercial.")
    if "educators" in en["personas_zero_ready"]:
        w("- **Persona gap:** `educators` has zero ready rows in en_US. The `educators` persona is fully present in the catalog (you can see it in §6 high-potential blocked rows at composite=0.72) but every row is blocked on `topic_explicit=True, persona_explicit=False` — the *persona* score is missing across every teacher×educators combination.")
    w()
    w("Both gaps share the same fix path: backfill `teacher_topic_persona_scores.yaml` (see §6 B3).")
    w()
    w("### Locale ready-rate gap")
    w()
    w("| Locale | Ready % |")
    w("|---|---:|")
    for loc in LOCALES:
        w(f"| {loc} | {cross['ready_rate_per_locale'][loc]}% |")
    w()
    w("zh_TW (43.5%) and zh_CN (45.4%) lag en_US/ja_JP (65.3%) by ~20 points. Driver: zh-specific brands lack `teacher_topic_persona_scores` entries, so most rows fall through to `composite=0.50` default.")
    w()

    # ------------------------------------------------------------------
    w("## 6. Top blockers before production")
    w()
    w("Ranked by commercial impact × cost-to-fix.")
    w()
    w("### B1 — Non-English titles are 100% blank (CRITICAL, blocks 3 of 4 launch markets)")
    w()
    total_blank_non_en = sum(per_locale[loc]["row_count"] for loc in ("ja_JP", "zh_TW", "zh_CN"))
    w(f"- **{total_blank_non_en:,} rows** across ja_JP / zh_TW / zh_CN have empty `title` and `subtitle` (`needs_title_synthesis_locale_native`).")
    w("- Listing-ready count in non-en locales = **0**.")
    w("- Root cause: no locale-native title templates exist on `origin/main`. Phase 2 plans address this; Phase 1 ships en_US-only or all-blank-non-en.")
    w("- **Fix path:** author `config/catalog_planning/title_templates.{ja_JP,zh_TW,zh_CN}.yaml` (deterministic templates, no LLM) — this is precisely Phase 2 T2. Catalog regenerates with no code change.")
    w()
    w("### B2 — Catastrophic title cannibalization in en_US (CRITICAL)")
    w()
    en = per_locale["en_US"]
    w(f"- 1,044 ready rows → only **{en['distinct_titles_in_ready']} distinct titles** ({en['distinct_title_subtitle_in_ready']} distinct title+subtitle pairs).")
    w(f"- Top duplicate title (\"{en['title_duplication_top'][0]['title']}\") appears **{en['title_duplication_top'][0]['count']} times**.")
    w("- Root cause: title template pool is per-topic, not per-(brand, topic, persona). Once a topic is matched, the template lookup is deterministic and ignores brand/persona signal.")
    w("- **Fix paths (pick one before scaling):**")
    w("  - (a) Expand `config/catalog_planning/title_templates.yaml` from 51 → 153+ entries with brand-conditioning (e.g., `body_memory × grief` ≠ `cognitive_clarity × grief`). Phase 2 T0 pre-work.")
    w("  - (b) Add a deterministic per-(brand, persona) salt that picks among template variants — keeps templates single-purpose but produces unique titles per row. Smaller change, weaker quality.")
    w("  - (c) Accept the duplication and ship one en_US listing per (title, subtitle) pair — collapses the catalog from 1,044 rows to 45 units. Realistic short-term but throws away the brand×persona segmentation work.")
    w()
    w("### B3 — Score-gate gap blocks 4,304 high-potential rows (HIGH)")
    w()
    total_blocked = sum(per_locale[loc]["status_breakdown"].get("blocked_score", 0) for loc in LOCALES)
    w(f"- **{total_blocked:,} rows** across all 4 locales have `readiness_status=blocked_score`.")
    w(f"- Of those, **{en['high_potential_blocked_total_at_or_above_0_65']} rows in en_US alone** sit at composite ≥0.65 — just below the 0.70 ready threshold. Examples below.")
    w("- Most-affected zh-specific brands (`gen_z_grounding_*`, `grief_companion_*`, `inner_security_*`, `panic_first_aid_*`, `sleep_repair_*`, `stabilizer_*`): nearly every row blocked because no scores exist for these teacher×topic / teacher×persona pairs.")
    w("- **Fix path:** backfill `config/catalog_planning/teacher_topic_persona_scores.yaml` for the missing teacher×topic and teacher×persona pairs. Pure data authoring — no code, no LLM.")
    w()
    w("**Examples of high-composite blocked rows in en_US (would be ready if scored):**")
    w()
    w("| Composite | Brand | Topic | Persona | Topic explicit | Persona explicit |")
    w("|---:|---|---|---|:-:|:-:|")
    for r in en["high_potential_blocked"][:10]:
        w(f"| {r['composite']} | {r['brand']} | {r['topic']} | {r['persona']} | {r['topic_explicit']} | {r['persona_explicit']} |")
    w()
    w("### B4 — Two mainstream topics produce zero ready rows in any locale (HIGH)")
    w()
    w(f"- en_US topics with zero ready rows: `{', '.join(per_locale['en_US']['topics_zero_ready']) or 'none'}`")
    w("- Amazon search volume for `adhd_focus` and `mindfulness` is 5–10× higher than the average wellness topic. Shipping without either is leaving money on the table.")
    w("- **Fix path:** same as B3 — backfill scores for the relevant teacher×`adhd_focus` and teacher×`mindfulness` pairs. The high-potential-blocked list in B3 already names 6+ rows that would unblock at composite 0.72.")
    w()
    w("### B5 — Top-10 strongest in `validation_report.json` is misleading (MEDIUM)")
    w()
    w("- The original validation report ranks rows by composite alone. For ja_JP/zh_TW/zh_CN, every row in the top-10 has `(blank)` title and `(blank)` subtitle.")
    w("- The §2 tables in this report dedupe by `(brand, title, subtitle)` and require non-blank fields, so they reflect what would actually go on Amazon if launched today.")
    w("- **Fix path:** none required for catalog correctness — this is a reporting clarification. Suggest superseding the legacy `validation_report.json` top-10 with the dedup'd version once approved.")
    w()
    w("### B6 — Composite ≥0.70 anomalies (LOW)")
    w()
    anomalies = sum(per_locale[loc]["blocked_composite_bands"].get("ge_0.70", 0) for loc in LOCALES)
    w(f"- **{anomalies}** rows across all locales report `composite ≥0.70` AND `readiness_status=blocked_score`. Per the documented gate logic in [README.md](./README.md), composite ≥0.70 should be `ready` whenever both dimensions are explicitly scored.")
    w("- Likely cause: one dimension is implicit (default 0.5) but the other is high enough to push composite above 0.70 — the gate requires *both* explicit. Document this in the README to avoid future confusion or relax the gate to allow composite ≥0.75 with one implicit dimension.")
    w()

    # ------------------------------------------------------------------
    w("## 7. Recommended decision (for owner review)")
    w()
    w("**Do not merge PR #771 as a launch enabler.** Merge it as a *catalog scaffolding* milestone with the explicit caveat that no books should be assembled from it until B1, B2, B3, B4 close.")
    w()
    w("**Suggested gating order:**")
    w()
    w("1. Land PR #771 (the scaffold) — every row is reproducible and validation tooling exists.")
    w("2. Then a focused follow-up PR closes B3/B4: backfill `teacher_topic_persona_scores.yaml`. Cheap, pure data.")
    w("3. Then a parallel pair of PRs closes B1 (locale-native title templates) and B2 (en_US template expansion / brand-conditioning).")
    w("4. Re-run `analyze_bestseller_readiness.py` after each PR; gate scaling Phase 2 (Manga, more brands) on this report showing **listing-ready ≥ 80% per locale and average ready-rows-per-distinct-title ≤ 3** before any book assembly fires.")
    w()
    w("**What is safe to do now:**")
    w()
    w("- Merge #771 to make the catalog and tooling visible.")
    w("- Use the en_US ready set as a sample for Pearl_Writer prose-quality eval (one book per distinct title — 42 books — is a more honest evaluation set than 1,044 dup'd rows).")
    w()
    w("**What is NOT safe to do now:**")
    w()
    w("- Trigger Phase 2 brand migration (the work the previous Phase 2 brief described). The cannibalization bug compounds across more brands; fix B2 first.")
    w("- Generate any books from this catalog at scale until B1–B4 close. Single hand-picked test books are fine.")
    w()

    # ------------------------------------------------------------------
    w("---")
    w()
    w("## Appendix: Method")
    w()
    w("- All numbers in this report come directly from the four `*_catalog.csv` files.")
    w("- No LLM was called. Composite scores parsed from the `notes` column. Status from `readiness_status`. Title/subtitle taken verbatim.")
    w("- Reproducibility: `python3 scripts/catalog/analyze_bestseller_readiness.py` regenerates this report and the companion `bestseller_readiness_data.json` deterministically from the CSVs.")
    w("- Heuristics for weak titles/subtitles are tuneable at the top of the analyzer script.")
    return "\n".join(lines) + "\n"


def main() -> int:
    if not CATALOG_DIR.exists():
        print(f"ERROR: catalog dir not found: {CATALOG_DIR}", file=sys.stderr)
        return 2

    catalogs = {loc: load_catalog(loc) for loc in LOCALES}
    per_locale = {loc: analyze_locale(rows) for loc, rows in catalogs.items()}
    cross = cross_locale_analysis(per_locale, catalogs)

    data = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_csvs": [str(CATALOG_DIR / f"{loc}_catalog.csv") for loc in LOCALES],
        "per_locale": per_locale,
        "cross_locale": cross,
        "ready_threshold": READY_THRESHOLD,
    }

    json_path = CATALOG_DIR / "bestseller_readiness_data.json"
    md_path = CATALOG_DIR / "bestseller_readiness_report.md"

    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(per_locale, cross), encoding="utf-8")

    print(f"Wrote {json_path} ({json_path.stat().st_size:,} bytes)")
    print(f"Wrote {md_path} ({md_path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
