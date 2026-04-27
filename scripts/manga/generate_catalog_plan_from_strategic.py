#!/usr/bin/env python3
"""
Generate the manga catalog plan from strategic-tier inputs.

Per specs/MANGA_CATALOG_RECONCILIATION_SPEC.md §7.1 and Phase 2X.1 (the catalog
plan generator). Reads:
  - docs/GENRE_PORTFOLIO_PLAN.md      (37 brands × 12+ genres, per-brand %-allocations)
  - docs/CJK_CATALOG_PLAN.md          (per-locale format mix for JP/TW/CN/KR)
  - docs/US_CATALOG_PLAN.md           (US-specific guidance)

Emits a structured Markdown catalog plan replacing the stale hand-edited
artifacts/manga/MANGA_FULL_CATALOG_PLAN.md (Apr 7-12, retired per D-3).

Per Phase 2X.1, this script does NOT auto-write the catalog plan to its target
path. The actual replacement happens atomically in Phase 2X.4 per D-20. This
script's default mode emits to stdout. Use --output PATH for explicit writes;
--dry-run validates parse without writing.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

REPO = Path(__file__).resolve().parents[2]

GENRE_PORTFOLIO_PATH = REPO / "docs" / "GENRE_PORTFOLIO_PLAN.md"
CJK_CATALOG_PATH = REPO / "docs" / "CJK_CATALOG_PLAN.md"
US_CATALOG_PATH = REPO / "docs" / "US_CATALOG_PLAN.md"

# Per spec §4.1 — must match scripts/manga/generate_series_plans_from_catalog.py
# VALID_GENRES exactly after Phase 2X.4 atomic flips the planner allow-list.
VALID_GENRES = (
    "iyashikei",
    "dark_fantasy",
    "psychological_horror",
    "supernatural_mystery",
    "isekai",
    "sci_fi_cyberpunk",
    "psychological_thriller",
    "romance_josei_drama",
    "workplace_drama",
    "action_battle",
    "sports_competition",
    "historical_period",
    "cultivation_martial",
    "school_coming_of_age",
    "mecha",
)

# Per spec D-18: 5 locales (added ko_KR for render+hold).
# Per operator 2026-04-27: extended to 8 markets — added es_LA (Latin America),
# hu_HU (Hungary), zh_HK (Hong Kong). Per-locale strategic plans are scaffolds
# until Pearl_Research deep-research authors fill the format-mix + revenue tables.
VALID_LOCALES = (
    "en_US", "ja_JP", "zh_TW", "zh_CN", "ko_KR",
    "es_LA", "hu_HU", "zh_HK",
)

# Mapping from GENRE_PORTFOLIO_PLAN's natural-language genre column headings to
# our 15-slug canonical allow-list. The strategic plan uses display names like
# "Iyashikei / Slice", "Dark Fantasy", "Psychological Horror", etc.
DISPLAY_TO_SLUG = {
    "iyashikei": "iyashikei",
    "iyashikei / slice": "iyashikei",
    "iyashikei / slice-of-life": "iyashikei",
    "slice of life": "iyashikei",
    "dark fantasy": "dark_fantasy",
    "psychological horror": "psychological_horror",
    "horror": "psychological_horror",
    "supernatural mystery": "supernatural_mystery",
    "isekai": "isekai",
    "sci-fi": "sci_fi_cyberpunk",
    "sci-fi / cyberpunk": "sci_fi_cyberpunk",
    "sci_fi / cyberpunk": "sci_fi_cyberpunk",
    "cyberpunk": "sci_fi_cyberpunk",
    "psychological thriller": "psychological_thriller",
    "psychological thriller / mystery": "psychological_thriller",
    "thriller": "psychological_thriller",
    "romance": "romance_josei_drama",
    "romance / josei drama": "romance_josei_drama",
    "romance / drama": "romance_josei_drama",
    "josei drama": "romance_josei_drama",
    "shojo": "romance_josei_drama",
    "workplace drama": "workplace_drama",
    "workplace drama / comedy": "workplace_drama",
    "workplace": "workplace_drama",
    "action / battle": "action_battle",
    "action": "action_battle",
    "battle": "action_battle",
    "sports": "sports_competition",
    "sports / competition": "sports_competition",
    "sports / competition (anchor)": "sports_competition",
    "historical": "historical_period",
    "historical / period drama": "historical_period",
    "historical / period": "historical_period",
    "cultivation": "cultivation_martial",
    "cultivation / martial arts": "cultivation_martial",
    "school": "school_coming_of_age",
    "school / coming-of-age": "school_coming_of_age",
    "coming of age": "school_coming_of_age",
    "mecha": "mecha",
}


# ─── brand-metadata → genre affinity ───────────────────────────────────────
#
# Per operator directive: every brand × every genre × every locale should
# produce ≥1 series_plan with a brand-metadata-weighted distribution.
# Strategic %-allocation from GENRE_PORTFOLIO_PLAN is the anchor; brand
# description tags add affinity adjustments; uniform baseline ensures every
# genre gets at least a small share.
#
# Tag → genre affinity weights derived from brand description keywords. Each
# brand's description (e.g. "Anxiety · Somatic · Sleep · Josei adult women")
# tokenizes into tags; tags map to genre boosts (additive). Used as the
# "metadata affinity" leg of distribute_genres() below.

# How much each strategy leg contributes to the final per-genre weight.
# Sum to 1.0. Per operator directive 2026-04-26 ("the spread of genres needs to
# be for all genres based on market %"): market_revenue is the DOMINANT leg
# (70%). Strategic anchor (20%) only colors brand identity at the margin;
# metadata (5%) and baseline (5%) are minor adjustments. Result: catalog
# totals approximate the documented per-genre market share.
DISTRIBUTION_WEIGHTS = {
    "flagship": {"strategic": 0.20, "metadata": 0.05, "market_revenue": 0.70, "baseline": 0.05},
    "core":     {"strategic": 0.20, "metadata": 0.05, "market_revenue": 0.70, "baseline": 0.05},
    "niche":    {"strategic": 0.20, "metadata": 0.05, "market_revenue": 0.70, "baseline": 0.05},
    "unknown":  {"strategic": 0.20, "metadata": 0.05, "market_revenue": 0.70, "baseline": 0.05},
}

# Per-genre market-revenue weights, derived from documented top-title sales:
#   - Mecha: Evangelion $16B franchise (unique tier — spec D-9 mega-example)
#   - Action/Battle: One Piece 530M + Naruto 250M + Dragon Ball 260M + Demon
#     Slayer 150M + MHA — ~1.2B combined sales tier
#   - Dark Fantasy: Berserk 70M + Frieren 30M (4.99M in 2024 alone) + Tokyo Ghoul
#     47M (overlapping psych_horror) — Mega tier per GENRE_PORTFOLIO_PLAN
#   - Isekai: Solo Leveling, Re:Zero, Slime, SAO — Mega (digital) per plan
#   - Psychological Horror: Tokyo Ghoul 47M; CAGR 18.74% (Large-growing)
#   - Supernatural Mystery: Mushishi 6M + Natsume 17M + xxxHOLiC 14M (Large)
#   - Romance/Josei Drama: broad-base ubiquitous (Large)
#   - Sports/Competition: Slam Dunk + Haikyuu + Ace of Diamond (Large)
#   - Sci-Fi/Cyberpunk: Akira + GitS (Mid; iconic, slower commercial pace)
#   - Psychological Thriller: Death Note 30M + Monster (Mid)
#   - Workplace Drama: Aggretsuko, Wotakoi (Mid; broad-but-not-mega)
#   - Historical/Period: Vinland Saga 7M, Vagabond, Bride's Story (Mid)
#   - Cultivation/Martial: huge in CN/TW; mid globally
#   - School/Coming-of-Age: broad-but-not-mega
#   - Iyashikei: Anchor tier (loyalty-builder; 3M ceiling without genre shell
#     per CJK_CATALOG_PLAN.md §1)
MARKET_REVENUE_WEIGHTS = {
    # Mega-of-mega tier — genres with single franchises ≥ $10B or aggregate sales ≥ 500M
    "action_battle":          1.50,  # One Piece 530M + Naruto 250M + Dragon Ball 260M + Demon Slayer 150M = 1.2B+ tier
    "mecha":                  1.40,  # Evangelion $16B franchise (single — spec D-9 mega-example)

    # Mega tier — multi-decade-bestseller franchises
    "dark_fantasy":           1.10,  # Mega per plan (Berserk 70M, Frieren 30M, Vinland 7M)
    "isekai":                 1.00,  # Mega (digital) per plan (Solo Leveling, Re:Zero, SAO, Slime)

    # Large-growing tier — high CAGR markets
    "psychological_horror":   0.85,  # Large-growing (Tokyo Ghoul 47M; CAGR 18.74%)

    # Large tier — broad-base or steady mid-millions sellers
    "supernatural_mystery":   0.65,  # Large (Mushishi 6M, Natsume 17M, xxxHOLiC 14M)
    "romance_josei_drama":    0.65,  # Large (broad-base; Heartstopper-tier ubiquity)
    "sports_competition":     0.65,  # Large (Slam Dunk, Haikyuu, Eyeshield)

    # Mid tier — iconic but slower commercial pace
    "sci_fi_cyberpunk":       0.50,  # Mid (Akira, Ghost in the Shell — classic prestige)
    "psychological_thriller": 0.50,  # Mid (Death Note 30M, Monster)
    "historical_period":      0.45,  # Mid (Vinland Saga, Vagabond, Bride's Story)
    "cultivation_martial":    0.45,  # Mid (huge in CN/TW; smaller global)
    "workplace_drama":        0.35,  # Mid (Aggretsuko, Wotakoi)
    "school_coming_of_age":   0.35,  # Mid (broad)

    # Anchor tier — loyalty-builder, not revenue
    "iyashikei":              0.25,  # Anchor (3M ceiling without genre shell per CJK_CATALOG_PLAN.md §1)
}

# Tag → per-genre affinity scores (0.0–1.0). Strict mapping from brand
# description keywords to genre relevance. Multiple tags per brand sum.
# Genres not listed for a tag get 0.0 contribution from that tag.
TAG_GENRE_AFFINITY = {
    # Wellness / topic tags
    "anxiety":            {"iyashikei": 0.7, "psychological_horror": 0.6, "supernatural_mystery": 0.4, "psychological_thriller": 0.3, "school_coming_of_age": 0.3},
    "somatic":            {"iyashikei": 0.7, "supernatural_mystery": 0.4, "dark_fantasy": 0.3, "romance_josei_drama": 0.2},
    "sleep":              {"iyashikei": 0.6, "supernatural_mystery": 0.5, "psychological_horror": 0.4, "psychological_thriller": 0.2},
    "burnout":            {"workplace_drama": 0.7, "sci_fi_cyberpunk": 0.5, "isekai": 0.5, "iyashikei": 0.3},
    "overthinking":       {"psychological_thriller": 0.8, "sci_fi_cyberpunk": 0.4, "psychological_horror": 0.3, "supernatural_mystery": 0.2},
    "psychology":         {"psychological_thriller": 0.7, "psychological_horror": 0.5, "supernatural_mystery": 0.3, "dark_fantasy": 0.3},
    "trauma":             {"dark_fantasy": 0.6, "psychological_horror": 0.5, "romance_josei_drama": 0.4, "historical_period": 0.3},
    "grief":              {"dark_fantasy": 0.6, "supernatural_mystery": 0.6, "iyashikei": 0.3, "historical_period": 0.4, "romance_josei_drama": 0.3},
    "social_anxiety":     {"romance_josei_drama": 0.5, "iyashikei": 0.4, "school_coming_of_age": 0.5, "supernatural_mystery": 0.3, "workplace_drama": 0.3},
    "relationships":      {"romance_josei_drama": 0.7, "iyashikei": 0.3, "workplace_drama": 0.3, "school_coming_of_age": 0.3},
    "boundaries":         {"romance_josei_drama": 0.5, "workplace_drama": 0.4, "psychological_thriller": 0.3, "iyashikei": 0.3},
    "self_worth":         {"romance_josei_drama": 0.4, "isekai": 0.5, "school_coming_of_age": 0.4, "action_battle": 0.4, "historical_period": 0.3},
    "imposter_syndrome":  {"workplace_drama": 0.6, "psychological_thriller": 0.5, "isekai": 0.5, "school_coming_of_age": 0.4, "sports_competition": 0.4},
    "courage":            {"action_battle": 0.7, "dark_fantasy": 0.5, "historical_period": 0.5, "sports_competition": 0.5, "isekai": 0.4},
    "purpose":            {"historical_period": 0.5, "action_battle": 0.4, "dark_fantasy": 0.4, "isekai": 0.3, "iyashikei": 0.3},
    "spiritual":          {"supernatural_mystery": 0.6, "cultivation_martial": 0.5, "iyashikei": 0.4, "historical_period": 0.3},
    "mindfulness":        {"iyashikei": 0.7, "supernatural_mystery": 0.3, "cultivation_martial": 0.3},
    "trauma_path":        {"dark_fantasy": 0.6, "psychological_horror": 0.5, "supernatural_mystery": 0.4, "iyashikei": 0.3},
    "performance":        {"sports_competition": 0.7, "workplace_drama": 0.5, "action_battle": 0.4, "psychological_thriller": 0.3},
    "adhd":               {"sports_competition": 0.6, "psychological_thriller": 0.4, "school_coming_of_age": 0.4, "supernatural_mystery": 0.3},
    "focus":              {"sports_competition": 0.5, "psychological_thriller": 0.4, "iyashikei": 0.4, "cultivation_martial": 0.4},
    "financial":          {"workplace_drama": 0.6, "sports_competition": 0.4, "historical_period": 0.3},
    "motivation":         {"sports_competition": 0.5, "action_battle": 0.5, "isekai": 0.4, "school_coming_of_age": 0.4},
    "memoir":             {"iyashikei": 0.4, "historical_period": 0.5, "romance_josei_drama": 0.4, "supernatural_mystery": 0.3},
    "legacy":             {"historical_period": 0.6, "dark_fantasy": 0.4, "action_battle": 0.4},
    "tech":               {"sci_fi_cyberpunk": 0.8, "workplace_drama": 0.5, "psychological_thriller": 0.4, "isekai": 0.3},
    "digital":            {"sci_fi_cyberpunk": 0.7, "workplace_drama": 0.4, "supernatural_mystery": 0.3},
    "warrior":            {"action_battle": 0.7, "cultivation_martial": 0.6, "historical_period": 0.5, "dark_fantasy": 0.4, "mecha": 0.3},
    "battle":             {"action_battle": 0.8, "dark_fantasy": 0.5, "cultivation_martial": 0.5, "mecha": 0.4, "historical_period": 0.3},
    "cultivation":        {"cultivation_martial": 0.9, "action_battle": 0.4, "historical_period": 0.4, "supernatural_mystery": 0.3},
    "qi":                 {"cultivation_martial": 0.8, "iyashikei": 0.3, "supernatural_mystery": 0.3},
    "stoic":              {"historical_period": 0.5, "dark_fantasy": 0.4, "action_battle": 0.4, "psychological_thriller": 0.3},
    "longevity":          {"iyashikei": 0.5, "historical_period": 0.4, "supernatural_mystery": 0.3, "romance_josei_drama": 0.3},
    "biology":            {"sci_fi_cyberpunk": 0.5, "iyashikei": 0.4, "supernatural_mystery": 0.3},
    "isekai":             {"isekai": 0.9, "dark_fantasy": 0.4, "action_battle": 0.3, "school_coming_of_age": 0.3},
    "supernatural":       {"supernatural_mystery": 0.8, "psychological_horror": 0.4, "dark_fantasy": 0.4, "cultivation_martial": 0.3},
    "devotion":           {"supernatural_mystery": 0.5, "cultivation_martial": 0.4, "iyashikei": 0.4, "historical_period": 0.3},
    "spiritual_grounding": {"supernatural_mystery": 0.6, "iyashikei": 0.4, "cultivation_martial": 0.4},
    # Demographic / register tags
    "josei":              {"romance_josei_drama": 0.4, "iyashikei": 0.4, "supernatural_mystery": 0.3, "psychological_thriller": 0.2, "workplace_drama": 0.3},
    "shojo":              {"romance_josei_drama": 0.5, "school_coming_of_age": 0.4, "supernatural_mystery": 0.3},
    "seinen":             {"psychological_thriller": 0.4, "dark_fantasy": 0.4, "sci_fi_cyberpunk": 0.3, "historical_period": 0.3, "workplace_drama": 0.3, "mecha": 0.3},
    "shonen":             {"action_battle": 0.5, "sports_competition": 0.4, "isekai": 0.4, "school_coming_of_age": 0.3, "cultivation_martial": 0.3},
    "manhwa":             {"sci_fi_cyberpunk": 0.4, "romance_josei_drama": 0.4, "isekai": 0.4, "action_battle": 0.4},
    "webtoon":            {"romance_josei_drama": 0.4, "isekai": 0.4, "action_battle": 0.4, "psychological_horror": 0.3},
    "tech_worker":        {"sci_fi_cyberpunk": 0.7, "workplace_drama": 0.6, "psychological_thriller": 0.4},
    "workplace":          {"workplace_drama": 0.8, "psychological_thriller": 0.3, "romance_josei_drama": 0.3, "sports_competition": 0.2},
}


def derive_brand_tags(brand_desc: str, brand_id: str = "") -> list[str]:
    """Tokenize a brand description + brand_id into matchable tag keys.

    Both description and brand_id are scanned so brands like
    `warrior_calm_cultivation` pick up "cultivation" + "warrior" tags from
    their slug even when the description only says "Burnout · Inner Peace · Shonen".

    Example: "Anxiety · Somatic · Sleep · Josei adult women" + "stillness_press"
      → ["anxiety", "somatic", "sleep", "josei"]
    """
    haystack = (brand_desc + " " + brand_id.replace("_", " ")).lower()
    # Split on common separators
    tokens: list[str] = []
    for sep in ["·", "•", ",", "/", "—", "-", "_"]:
        haystack = haystack.replace(sep, "|")
    seen = set()
    for chunk in haystack.split("|"):
        chunk = chunk.strip()
        if not chunk:
            continue
        # Match longest tag first
        for tag in sorted(TAG_GENRE_AFFINITY.keys(), key=len, reverse=True):
            if tag.replace("_", " ") in chunk or tag in chunk.replace(" ", "_"):
                if tag not in seen:
                    tokens.append(tag)
                    seen.add(tag)
                break
    # Also do a whole-haystack pass to catch tags that span chunk boundaries
    for tag in TAG_GENRE_AFFINITY.keys():
        if tag in seen:
            continue
        if tag in haystack or tag.replace("_", " ") in haystack:
            tokens.append(tag)
            seen.add(tag)
    return tokens


def compute_metadata_affinity(brand_desc: str, brand_id: str = "") -> dict[str, float]:
    """Compute per-genre affinity score from brand description + brand_id tags."""
    tags = derive_brand_tags(brand_desc, brand_id)
    raw = {g: 0.0 for g in VALID_GENRES}
    for tag in tags:
        for genre, score in TAG_GENRE_AFFINITY.get(tag, {}).items():
            if genre in raw:
                raw[genre] += score
    peak = max(raw.values()) if raw else 0
    if peak <= 0:
        return {g: 1.0 / len(VALID_GENRES) for g in VALID_GENRES}
    return {g: v / peak for g, v in raw.items()}




def distribute_strategic_strict(
    target_series: int,
    strategic_alloc: dict[str, float],
) -> dict[str, int]:
    """Spec-compliant per-genre series count for one brand.

    Distributes ``target_series`` across exactly the genres listed in
    ``strategic_alloc`` (which is the brand's per-genre %-allocation parsed
    from GENRE_PORTFOLIO_PLAN.md). Genres NOT in the spec table get 0
    series — no uniform fallback, no metadata bleed-through, no market
    revenue tilt.

    Uses the largest-remainder method (a.k.a. Hare quota) to ensure the
    integer counts sum to exactly ``target_series`` even when raw shares
    don't round cleanly. This gives every spec-listed genre a deterministic
    floor based on the documented %, and distributes any leftover seats to
    the genres with the largest fractional remainder.

    Special case: if a genre has %>0 in spec but rounds to 0 series at the
    given target, it still gets 1 series (so a "10%" line in the spec
    yields ≥1 series even if the brand has only 4 series total). The
    surplus is then trimmed from the largest-share genres.

    Args:
        target_series: total series count for this brand (e.g. 16 for
            stillness_press, 9 for sleep_restoration_iyashikei).
        strategic_alloc: dict mapping genre_slug → percentage (e.g.
            {"iyashikei": 30.0, "dark_fantasy": 25.0, ...}). Sum should be
            ~100. Genres not in this dict get 0 series.

    Returns:
        dict mapping genre_slug → integer series count. Sum equals
        ``target_series``. Only contains keys that are in
        ``strategic_alloc`` (no extra genres are introduced).

    Examples:
        >>> # stillness_press: 16 series, spec says 30/25/20/15/10
        >>> distribute_strategic_strict(16, {
        ...     "iyashikei": 30.0, "dark_fantasy": 25.0,
        ...     "psychological_horror": 20.0, "supernatural_mystery": 15.0,
        ...     "isekai": 10.0,
        ... })
        {'iyashikei': 5, 'dark_fantasy': 4, 'psychological_horror': 3,
         'supernatural_mystery': 2, 'isekai': 2}
    """
    if not strategic_alloc:
        return {}
    if target_series <= 0:
        return {g: 0 for g in strategic_alloc}

    # Normalize % so totals don't depend on whether spec sums to 100, 95, or 105
    total_pct = sum(strategic_alloc.values()) or 100.0

    # Step 1 — raw fractional share per genre
    raw_share: dict[str, float] = {
        g: target_series * (pct / total_pct) for g, pct in strategic_alloc.items()
    }

    # Step 2 — floors (integer part)
    floors: dict[str, int] = {g: int(s) for g, s in raw_share.items()}

    # Step 3 — promote any %>0 genre with floor 0 to 1 (every spec genre seats ≥1).
    # Track which were promoted so we can compensate by trimming.
    promoted = []
    for g, pct in strategic_alloc.items():
        if pct > 0 and floors[g] == 0:
            floors[g] = 1
            promoted.append(g)

    seated = sum(floors.values())

    # Step 4 — distribute remaining seats by largest fractional remainder
    if seated < target_series:
        remainders = sorted(
            ((g, raw_share[g] - int(raw_share[g])) for g in strategic_alloc if g not in promoted),
            key=lambda kv: -kv[1],
        )
        i = 0
        while seated < target_series and remainders:
            g = remainders[i % len(remainders)][0]
            floors[g] += 1
            seated += 1
            i += 1

    # Step 5 — if over-seated (because of promotions), trim from the genres with
    # the largest absolute count, but never below 1.
    while seated > target_series:
        # Trim from the genre with highest current count
        ranked = sorted(floors.items(), key=lambda kv: -kv[1])
        for g, cnt in ranked:
            if cnt > 1:
                floors[g] -= 1
                seated -= 1
                break
        else:
            break  # safety — every genre at 1; can't trim further

    return floors


def validate_brand_allocations(
    brands: list["BrandAllocation"],
    canonical_brand_ids: list[str] | None = None,
) -> tuple[bool, list[str]]:
    """Spec-compliance check before regen runs.

    Per operator directive: STOP and surface if any brand in the canonical
    list lacks a %-allocation table (or has one with <3 genres or sums
    outside 95-105%).

    Returns (ok, issues) where ``ok`` is True iff every canonical brand has
    a valid spec entry. ``issues`` is a human-readable list.
    """
    issues: list[str] = []
    parsed_ids = {b.brand_id for b in brands}

    if canonical_brand_ids:
        missing = [b for b in canonical_brand_ids if b not in parsed_ids]
        if missing:
            issues.append(
                f"BRANDS WITHOUT %-TABLES (need spec authoring): "
                f"{', '.join(sorted(missing))}"
            )

    for b in brands:
        s = sum(b.genre_pct.values())
        if s < 95 or s > 105:
            issues.append(
                f"{b.brand_id}: %-table sums to {s} (must be 95-105). "
                f"Genres: {list(b.genre_pct.keys())}"
            )
        if len(b.genre_pct) < 3:
            issues.append(
                f"{b.brand_id}: only {len(b.genre_pct)} genres parsed "
                f"(min 3 required). Got: {list(b.genre_pct.keys())}"
            )

    return (len(issues) == 0, issues)


def distribute_with_spread(
    target_series: int,
    strategic_alloc: dict[str, float],
    metadata_affinity: dict[str, float],
    tier: str,
) -> dict[str, int]:
    """Compute per-genre series count given strategic + metadata + baseline weights.

    Operator directive: every brand × every genre should produce ≥1 series
    where target_series ≥ 15. For smaller targets (core/niche), some genres
    will get 0 — distribution is concentrated by combined weight.
    """
    weights = DISTRIBUTION_WEIGHTS.get(tier, DISTRIBUTION_WEIGHTS["unknown"])

    # 1. Build combined weight per genre (sum ≈ 1.0 by construction)
    combined: dict[str, float] = {g: 0.0 for g in VALID_GENRES}

    # Strategic anchor — listed genres get their pct (sums to ≤1.0); rest get 0
    strat_total = sum(strategic_alloc.values()) or 100.0
    for g, pct in strategic_alloc.items():
        if g in combined:
            combined[g] += weights["strategic"] * (pct / strat_total)

    # Metadata affinity — already normalized to [0,1]; scale by sum so it's
    # comparable to strategic
    meta_total = sum(metadata_affinity.values()) or 1.0
    for g, score in metadata_affinity.items():
        combined[g] += weights["metadata"] * (score / meta_total)

    # Market revenue — weights derived from documented top-title sales tiers
    # (per GENRE_PORTFOLIO_PLAN.md tier table + manga_genre_writing_styles
    # corpus citations). Mega-tier mecha/action/dark_fantasy/isekai get
    # proportionally more share; iyashikei (anchor tier) gets less.
    revenue_total = sum(MARKET_REVENUE_WEIGHTS.values())
    for g in combined:
        combined[g] += weights["market_revenue"] * (MARKET_REVENUE_WEIGHTS.get(g, 0.5) / revenue_total)

    # Uniform baseline — every genre gets equal share of remaining budget
    baseline_per_genre = weights["baseline"] / len(VALID_GENRES)
    for g in combined:
        combined[g] += baseline_per_genre

    # 2. Convert to integer series counts via largest-remainder method
    n_genres = len(VALID_GENRES)

    # If target ≥ 15, force every genre to ≥1; the remainder distributes by weight.
    # If target < 15, top-N-by-weight genres get 1, rest get 0.
    if target_series >= n_genres:
        # Reserve 1 per genre as the floor (15 series), then distribute surplus
        floors = {g: 1 for g in VALID_GENRES}
        surplus = target_series - n_genres
        # Distribute surplus by weighted remainder
        weighted = sorted(combined.items(), key=lambda kv: -kv[1])
        # Each surplus point goes to the highest-weight genre, by ranked order
        for i in range(surplus):
            g = weighted[i % len(weighted)][0]
            # Cap at a reasonable max to prevent over-concentration
            if floors[g] < 6:
                floors[g] += 1
            else:
                # If a genre is at cap, find next genre that isn't capped
                for fallback_g, _ in weighted:
                    if floors[fallback_g] < 6:
                        floors[fallback_g] += 1
                        break
        return floors

    # target < 15: top-target genres get 1, rest 0
    weighted = sorted(combined.items(), key=lambda kv: -kv[1])
    floors = {g: 0 for g in VALID_GENRES}
    for g, _ in weighted[:target_series]:
        floors[g] = 1
    return floors


# ─── data model ─────────────────────────────────────────────────────────────


@dataclass
class BrandAllocation:
    """One brand's per-genre %-allocation row in GENRE_PORTFOLIO_PLAN."""

    brand_id: str
    tier: str  # "flagship" | "core" | "niche"
    target_series: int  # midpoint of tier range
    description: str  # one-line tagline
    genre_pct: dict[str, float] = field(default_factory=dict)  # slug → %
    spread_counts: dict[str, int] = field(default_factory=dict)  # slug → series-count after distribute_with_spread

    def series_per_genre(self, genre_slug: str) -> int:
        # Prefer spread distribution if computed; fall back to strategic %
        if self.spread_counts:
            return self.spread_counts.get(genre_slug, 0)
        return round(self.target_series * (self.genre_pct.get(genre_slug, 0.0) / 100.0))


@dataclass
class LocaleConfig:
    """Per-locale format mix and distribution stance."""

    locale: str
    format_mix: dict[str, str]  # format_slug → label
    primary_platforms: list[str]
    distribution_status: str  # "distributed" | "gray_zone_disclosed" | "hold_pending_market_clearance"


# ─── parsers ────────────────────────────────────────────────────────────────


_RE_BRAND_HEADING = re.compile(
    r"^####\s+`(?P<id>[a-z_0-9]+)`(?:\s*[—-]\s*(?P<desc>.+?))?\s*$"
)
_RE_TIER_HEADING = re.compile(
    r"^###\s+(?P<tier>Flagship|Core|Niche)(?:\s+/\s+\w+)?\s+Brands\b.*?\((?P<low>\d+)[–-](?P<high>\d+)\s+series.*\)?",
    re.IGNORECASE,
)
# Per-brand table header carries the authoritative target_series count, e.g.
#   "| Genre | % | Series (of 14) | Primary Wellness Embed |"
# This is more specific than the tier midpoint (e.g. flagship tier says
# 14–18, but `cognitive_clarity` is specifically "of 14"). Parser uses this
# when present; falls back to tier midpoint otherwise.
_RE_TABLE_HEADER_TARGET = re.compile(
    r"^\|\s*Genre\s*\|\s*%\s*\|\s*Series\s*\(of\s+(?P<target>\d+)\)\s*\|"
)
# Match a genre/% table row. The "count" column may be:
#   - integer ("5")
#   - integer range with em-dash, en-dash, or ASCII-dash ("3–4", "2-3", "1—2")
#   - placeholder dash for "0" ("—" / "-")
#   - empty
# We don't actually use the count value for distribution — the % is
# authoritative — but the regex must accept all forms or rows are silently
# dropped. Pre-fix the regex required a single integer, which silently dropped
# every range row in GENRE_PORTFOLIO_PLAN.md (~24 rows, ~20 brands affected).
_RE_TABLE_ROW = re.compile(
    r"^\|\s*(?P<genre>[^|]+?)\s*\|\s*(?P<pct>\d+(?:\.\d+)?)\s*%\s*\|"
    r"\s*(?P<count>(?:\d+(?:\s*[–—-]\s*\d+)?)|—|-)?"
    r"\s*(?:\(of\s+(?P<of>\d+)\))?\s*\|"
)


def parse_genre_portfolio(text: str) -> list[BrandAllocation]:
    """Extract brand allocations from GENRE_PORTFOLIO_PLAN.md.

    Strategy: walk the file line-by-line. Track the current tier (from H3
    headings like "### Flagship Brands (14–18 series target)"). Track current
    brand (from H4 like "#### `stillness_press` — Anxiety · Somatic · ..."). For
    each brand, parse the per-genre table that follows.
    """
    brands: list[BrandAllocation] = []
    cur_tier: str = "unknown"
    cur_target: int = 0
    cur_brand: BrandAllocation | None = None

    for line in text.splitlines():
        m_tier = _RE_TIER_HEADING.match(line)
        if m_tier:
            cur_tier = m_tier.group("tier").lower()
            low = int(m_tier.group("low"))
            high = int(m_tier.group("high"))
            cur_target = (low + high) // 2
            continue

        m_brand = _RE_BRAND_HEADING.match(line)
        if m_brand:
            if cur_brand and cur_brand.genre_pct:
                brands.append(cur_brand)
            cur_brand = BrandAllocation(
                brand_id=m_brand.group("id"),
                tier=cur_tier,
                target_series=cur_target or 6,
                description=(m_brand.group("desc") or "").strip(),
            )
            continue

        if cur_brand is None:
            continue

        # Per-brand table header overrides the tier-midpoint target.
        # Look for `| Genre | % | Series (of N) |` and use N.
        m_target = _RE_TABLE_HEADER_TARGET.match(line)
        if m_target:
            cur_brand.target_series = int(m_target.group("target"))
            continue

        m_row = _RE_TABLE_ROW.match(line)
        if m_row:
            display = m_row.group("genre").strip().lower()
            slug = DISPLAY_TO_SLUG.get(display)
            if not slug:
                # Genre not in our allow-list — skip silently. v1.1 spec allows
                # the strategic plan to reference future-genre rows that the
                # planner doesn't yet support.
                continue
            try:
                cur_brand.genre_pct[slug] = float(m_row.group("pct"))
            except (TypeError, ValueError):
                pass

    if cur_brand and cur_brand.genre_pct:
        brands.append(cur_brand)

    return brands


_RE_LOCALE_FORMAT_ROW = re.compile(
    r"^\|\s*\*\*(?P<locale>JP|US|TW|CN|KR)\*\*\s*\|\s*(?P<format>[^|]+)\|\s*(?P<style>[^|]+)\|\s*(?P<platform>[^|]+)\|"
)

_LOCALE_NORMALIZE = {
    "JP": "ja_JP",
    "US": "en_US",
    "TW": "zh_TW",
    "CN": "zh_CN",
    "KR": "ko_KR",
}


def parse_locale_formats(cjk_text: str) -> dict[str, LocaleConfig]:
    """Extract per-locale format and platform info from CJK_CATALOG_PLAN.md §2."""
    locales: dict[str, LocaleConfig] = {}
    for line in cjk_text.splitlines():
        m = _RE_LOCALE_FORMAT_ROW.match(line)
        if not m:
            continue
        locale = _LOCALE_NORMALIZE.get(m.group("locale"))
        if not locale:
            continue
        fmt = m.group("format").strip()
        platform = m.group("platform").strip()
        # Distribution status per spec D-18 + D-19
        if locale == "ko_KR":
            status = "hold_pending_market_clearance"
        elif locale == "zh_CN":
            status = "gray_zone_disclosed"
        else:
            status = "distributed"
        locales[locale] = LocaleConfig(
            locale=locale,
            format_mix={"primary": fmt},
            primary_platforms=[p.strip() for p in platform.split(",")],
            distribution_status=status,
        )
    # Ensure all 5 locales present even if the parsed table missed one (defensive)
    for lc in VALID_LOCALES:
        if lc not in locales:
            locales[lc] = LocaleConfig(
                locale=lc,
                format_mix={"primary": "color_vertical_webtoon"},
                primary_platforms=["TBD"],
                distribution_status=(
                    "hold_pending_market_clearance" if lc == "ko_KR"
                    else "gray_zone_disclosed" if lc == "zh_CN"
                    else "distributed"
                ),
            )
    return locales


# ─── catalog plan emitter ───────────────────────────────────────────────────


def emit_catalog_plan(brands: list[BrandAllocation], locales: dict[str, LocaleConfig]) -> str:
    """Generate the new MANGA_FULL_CATALOG_PLAN.md content."""
    lines: list[str] = []

    # Header
    lines.extend([
        "<!-- AUTO-GENERATED — do not hand-edit. -->",
        "<!-- Source: scripts/manga/generate_catalog_plan_from_strategic.py -->",
        "<!-- Inputs: docs/GENRE_PORTFOLIO_PLAN.md + docs/CJK_CATALOG_PLAN.md + docs/US_CATALOG_PLAN.md -->",
        "<!-- Per specs/MANGA_CATALOG_RECONCILIATION_SPEC.md §7.1 + D-17 -->",
        "",
        "# Phoenix Omega — Manga Full Catalog Plan",
        "",
        "Auto-generated from the strategic-tier plans. To update this file, edit the source",
        "strategic docs and re-run the generator.",
        "",
        "## Locales (per D-18, 5-locale matrix)",
        "",
        "| Locale | Primary format | Platform(s) | Distribution status |",
        "|---|---|---|---|",
    ])
    for lc_id in VALID_LOCALES:
        lc = locales[lc_id]
        platforms = ", ".join(lc.primary_platforms)
        fmt = lc.format_mix.get("primary", "n/a")
        lines.append(f"| {lc_id} | {fmt} | {platforms} | {lc.distribution_status} |")
    lines.append("")

    # Brand portfolio summary
    lines.extend([
        "## Brand portfolio (37 brands per `GENRE_PORTFOLIO_PLAN.md`)",
        "",
        "| Brand | Tier | Series target | Genre mix |",
        "|---|---|---|---|",
    ])
    for brand in sorted(brands, key=lambda b: (b.tier != "flagship", b.tier != "core", b.brand_id)):
        mix_summary = ", ".join(
            f"{slug} {pct:.0f}%"
            for slug, pct in sorted(brand.genre_pct.items(), key=lambda kv: -kv[1])
        )
        lines.append(
            f"| `{brand.brand_id}` | {brand.tier} | {brand.target_series} | {mix_summary} |"
        )
    lines.append("")

    # Series rows by brand × locale × genre
    lines.extend([
        "## Catalog rows (brand × locale × genre)",
        "",
        f"Total brands parsed: **{len(brands)}**.",
        f"Total locales: **{len(VALID_LOCALES)}** (per D-18).",
        f"Total genre slugs in allow-list: **{len(VALID_GENRES)}** (per §4.1).",
        "",
        "Each row below represents one brand × locale slice. The series count is",
        "the integer round of `target_series × genre_pct` for each genre slug.",
        "",
    ])

    total_series_count = 0
    for brand in sorted(brands, key=lambda b: b.brand_id):
        lines.append(f"### `{brand.brand_id}` ({brand.tier} — {brand.target_series} series target)")
        if brand.description:
            lines.append(f"> {brand.description}")
        lines.append("")
        lines.append("| Locale | Genre | Series count | Distribution status |")
        lines.append("|---|---|---|---|")
        for lc_id in VALID_LOCALES:
            lc = locales[lc_id]
            for genre in VALID_GENRES:
                count = brand.series_per_genre(genre)
                if count <= 0:
                    continue
                lines.append(
                    f"| {lc_id} | {genre} | {count} | {lc.distribution_status} |"
                )
                total_series_count += count
        lines.append("")

    # Summary
    lines.extend([
        "## Summary",
        "",
        f"- **Brands**: {len(brands)}",
        f"- **Locales**: {len(VALID_LOCALES)}",
        f"- **Genres**: {len(VALID_GENRES)}",
        f"- **Total localized series rows**: {total_series_count}",
        f"- **Estimated chapters at 14/series**: {total_series_count * 14}",
        "",
        "Per spec D-20, this catalog plan is materialized to disk by Phase 2X.4",
        "atomic PR (schema flip + 132+716 stale YAML deletion + regenerate).",
        "",
    ])

    return "\n".join(lines) + "\n"


# ─── CLI ────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n", 1)[0])
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Write generated catalog plan to PATH. Default: stdout.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate that all 3 strategic inputs parse cleanly. No output written.",
    )
    parser.add_argument(
        "--genre-portfolio",
        type=Path,
        default=GENRE_PORTFOLIO_PATH,
        help=f"Path to GENRE_PORTFOLIO_PLAN.md (default: {GENRE_PORTFOLIO_PATH.relative_to(REPO)})",
    )
    parser.add_argument(
        "--cjk-catalog",
        type=Path,
        default=CJK_CATALOG_PATH,
        help=f"Path to CJK_CATALOG_PLAN.md (default: {CJK_CATALOG_PATH.relative_to(REPO)})",
    )
    parser.add_argument(
        "--us-catalog",
        type=Path,
        default=US_CATALOG_PATH,
        help=f"Path to US_CATALOG_PLAN.md (default: {US_CATALOG_PATH.relative_to(REPO)})",
    )
    args = parser.parse_args(argv)

    for path in (args.genre_portfolio, args.cjk_catalog, args.us_catalog):
        if not path.exists():
            print(f"error: input file does not exist: {path}", file=sys.stderr)
            return 2

    portfolio_text = args.genre_portfolio.read_text(encoding="utf-8")
    cjk_text = args.cjk_catalog.read_text(encoding="utf-8")
    args.us_catalog.read_text(encoding="utf-8")  # validate readable; not used in v1

    brands = parse_genre_portfolio(portfolio_text)
    locales = parse_locale_formats(cjk_text)

    if not brands:
        print(
            "error: parsed 0 brands from GENRE_PORTFOLIO_PLAN.md — strategic doc"
            " structure may have changed; re-check parser regexes",
            file=sys.stderr,
        )
        return 3

    # Apply brand-metadata-weighted distribution: every brand gets a spread
    # across all 15 genres, biased by strategic %-allocation + description tags.
    # Per operator directive (2026-04-26): ALL brands get genre spread; some
    # get a little more, some a little less, based on metadata.
    for brand in brands:
        affinity = compute_metadata_affinity(brand.description, brand.brand_id)
        brand.spread_counts = distribute_with_spread(
            target_series=brand.target_series,
            strategic_alloc=brand.genre_pct,
            metadata_affinity=affinity,
            tier=brand.tier,
        )

    if args.dry_run:
        # Report distribution stats
        spread_total = sum(sum(b.spread_counts.values()) for b in brands)
        print(f"dry-run: parsed {len(brands)} brands × {len(locales)} locales OK")
        print(f"dry-run: spread distribution = {spread_total} series per locale × 5 locales = {spread_total * 5} localized rows")
        return 0

    output = emit_catalog_plan(brands, locales)

    if args.output:
        args.output.write_text(output, encoding="utf-8")
        print(f"wrote {args.output} ({len(output)} bytes)")
    else:
        sys.stdout.write(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
