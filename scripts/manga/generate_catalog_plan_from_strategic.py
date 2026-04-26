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

# Per spec D-18: 5 locales (added ko_KR for render+hold)
VALID_LOCALES = ("en_US", "ja_JP", "zh_TW", "zh_CN", "ko_KR")

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
    "thriller": "psychological_thriller",
    "romance": "romance_josei_drama",
    "romance / josei drama": "romance_josei_drama",
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


# ─── data model ─────────────────────────────────────────────────────────────


@dataclass
class BrandAllocation:
    """One brand's per-genre %-allocation row in GENRE_PORTFOLIO_PLAN."""

    brand_id: str
    tier: str  # "flagship" | "core" | "niche"
    target_series: int  # midpoint of tier range
    description: str  # one-line tagline
    genre_pct: dict[str, float] = field(default_factory=dict)  # slug → %

    def series_per_genre(self, genre_slug: str) -> int:
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
_RE_TABLE_ROW = re.compile(
    r"^\|\s*(?P<genre>[^|]+?)\s*\|\s*(?P<pct>\d+(?:\.\d+)?)\s*%\s*\|\s*(?P<count>\d+)?\s*(?:\(of\s+(?P<of>\d+)\))?\s*\|"
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

    if args.dry_run:
        print(f"dry-run: parsed {len(brands)} brands × {len(locales)} locales OK")
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
