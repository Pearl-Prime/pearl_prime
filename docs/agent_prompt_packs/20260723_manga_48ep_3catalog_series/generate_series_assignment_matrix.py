#!/usr/bin/env python3
"""Deterministic brand x catalog -> genre + arc-shape assignment matrix.

Generates the planning matrix for the 48-episode / 4-arc manga series writing
program (docs/agent_prompt_packs/20260723_manga_48ep_3catalog_series/). Reuse
before authoring (docs/agent_brief.txt SS9): checks artifacts/manga/chapter_scripts/
for an EXISTING series directory per (brand, locale) before proposing a new one.

Inputs (read-only, canonical; priority order):
  artifacts/planning/world_14x37_books_manga_20260715/manga_genre_allocation_14x37.tsv
                                                -- AUTHORITATIVE brand-level genre DNA
                                                   (top-weighted genre per brand, same
                                                   across markets; ratified per
                                                   specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md).
                                                   Primary source -- reuse before authoring.
  config/manga/locale_genre_allocations.yaml   -- per-locale genre share table, used only
                                                   as a cross-check (does the brand's DNA
                                                   genre even appear in this market's mix?)
                                                   and as the fallback when a brand is
                                                   missing from the 14x37 file.
  config/manga/canonical_brand_list.yaml       -- 37 brands: tier/demographic/topic
  docs/research/manga_craft/index.md           -- 48-volume arc-shape summary table
  artifacts/manga/chapter_scripts/*/            -- existing series scaffolds (reuse check)

Output: TSV to stdout. Columns:
  catalog  brand_id  tier  demographic  primary_topic  secondary_topics
  genre_id  genre_source  locale_mix_check  craft_bible  arc_shape_hint
  existing_series_id  status  note

`status` in {REUSE_EXISTING, NEW_SERIES, EXCLUDED}.
`genre_source` in {14x37_dna, locale_affinity_fallback}.
`locale_mix_check` = OK if the DNA genre appears anywhere in this catalog's
locale_genre_allocations.yaml genre list, else FLAG_NOT_IN_LOCALE_MIX (surface
for PM/operator review -- do not silently drop; the two SSOTs encode different
things -- brand-level DNA vs market-level demand mix -- and can legitimately
disagree; a FLAG is not an error, it is a review pointer).
No randomness: brand order is fixed (tier then alpha).
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path("/Users/ahjan/phoenix_omega")
CATALOGS = ["en_US", "ja_JP", "zh_TW"]

# genre_id -> craft bible filename (docs/research/manga_craft/) and arc-shape hint
# (from index.md "Canonical 48-volume shapes summary" + per-lane SS7, condensed to a
# 4-arc-of-12-episode default unless the bible's native shape is materially different).
GENRE_META = {
    "iyashikei": ("iyashikei_minimalism.md", "12 x 4-episode seasonal cycles (atmospheric, not escalating stakes)"),
    "workplace_drama": ("workplace_drama.md", "4 arcs x 12 eps: onboarding shock -> burnout trough -> boundary stand -> role redefinition"),
    "psychological_thriller": ("psychological_thriller.md", "4 arcs x 12 eps: obsession seed -> spiral -> exposure -> reckoning"),
    "romance_josei_drama": ("shojo_romance.md", "4 arcs x 12 eps: proximity -> rupture -> repair -> commitment ladder"),
    "school_coming_of_age": ("school_coming_of_age.md", "4 arcs x 12 eps: entry -> status crisis -> alliance -> self-definition"),
    "supernatural_mystery": ("supernatural_mystery.md", "4 arcs x 12 eps: first case -> pattern -> origin/grief reveal -> boundary held"),
    "sports_competition": ("sports_competition.md", "4 arcs x 12 eps: recruit -> losing streak -> breakthrough -> championship arc"),
    "dark_fantasy": ("dark_fantasy.md", "4 arcs x 12 eps: loss -> grim world rules -> found-family -> meaning-made-from-grief"),
    "psychological_horror": ("psychological_horror.md", "4 arcs x 12 eps: intrusion -> escalating dread -> confrontation -> uneasy integration"),
    "isekai": ("isekai.md", "4 arcs x 12 eps: portal-with-cost -> adaptation -> stakes escalate -> choice to belong/return"),
    "cultivation_martial": ("cultivation_martial.md", "4 arcs x 12 eps: awakening -> tier climb -> rival/face stakes -> sect-level reckoning"),
    "mecha": ("mecha.md", "4 arcs x 12 eps: forced pilot -> identity-vs-machine -> scale/mortality -> chosen humanity"),
    "sci_fi_cyberpunk": ("sci_fi_cyberpunk.md", "4 arcs x 12 eps: system optimization -> body/identity cost -> resistance -> re-humanization"),
    "action_battle": ("action_battle.md", "4 arcs x 12 eps: inciting fight -> training/rival -> tournament/escalation -> reckoning"),
    "historical_period": ("historical_period.md", "4 arcs x 12 eps: displacement -> survival code -> legacy conflict -> honor resolved"),
    "seinen_psychological": ("seinen_psychological.md", "4 arcs x 12 eps: ordinary crack -> moral ambiguity -> withheld climax -> unresolved-but-earned close"),
    "josei_adult_memoir": ("josei_adult_memoir.md", "diaristic serial; retrospective beats at ep 12/24/36/48 (not stakes-escalation)"),
    "BL_slice_of_life": ("BL_slice_of_life.md", "4 arcs x 12 eps: recognition -> domestic intimacy -> external pressure -> chosen-family stability"),
    "graphic_novel_us_literary": ("graphic_novel_us_literary.md", "48 thematic-artifact vignettes grouped into 4 x 12 seasons"),
    "kodomomuke_educational": ("kodomomuke_educational.md", "age-band 4 x 12 eps, per-episode warm resolution"),
    "webtoon_vertical_romance": ("webtoon_vertical_romance.md", "4 seasons x 12 eps: meet -> rival/misread -> rupture -> proximity resolved"),
    "webtoon_vertical_drama": ("webtoon_vertical_drama.md", "4 floors/arcs x 12 eps: entry trial -> system rules -> alliance/betrayal -> floor-boss reckoning"),
}
# aliases seen in locale_genre_allocations.yaml but not literal bible filenames
GENRE_ALIAS = {}

# demographic -> ordered genre preference (first match in locale's available set wins)
DEMO_AFFINITY = {
    "manhwa": ["sci_fi_cyberpunk", "webtoon_vertical_drama", "workplace_drama", "action_battle", "isekai"],
    "shonen": ["action_battle", "sports_competition", "cultivation_martial", "isekai", "school_coming_of_age"],
    "shojo": ["romance_josei_drama", "school_coming_of_age", "supernatural_mystery", "iyashikei"],
    "seinen": ["seinen_psychological", "psychological_thriller", "workplace_drama", "dark_fantasy",
               "sci_fi_cyberpunk", "mecha", "historical_period", "cultivation_martial"],
    "josei": ["iyashikei", "romance_josei_drama", "supernatural_mystery", "workplace_drama",
              "josei_adult_memoir", "BL_slice_of_life", "psychological_horror"],
}
# primary_topic -> extra genre preference boost (prepended if present in locale set)
TOPIC_AFFINITY = {
    "anxiety": ["psychological_horror", "iyashikei", "supernatural_mystery"],
    "sleep": ["iyashikei", "psychological_horror"],
    "somatic_healing": ["iyashikei", "supernatural_mystery"],
    "grief": ["dark_fantasy", "historical_period", "supernatural_mystery"],
    "trauma_recovery": ["dark_fantasy", "psychological_horror"],
    "overthinking": ["psychological_thriller", "seinen_psychological"],
    "burnout": ["workplace_drama", "sci_fi_cyberpunk", "mecha"],
    "imposter_syndrome": ["psychological_thriller", "workplace_drama"],
    "financial_anxiety": ["workplace_drama"],
    "social_anxiety": ["romance_josei_drama", "school_coming_of_age"],
    "self_worth": ["romance_josei_drama", "isekai"],
    "boundaries": ["workplace_drama", "romance_josei_drama"],
    "shame": ["seinen_psychological", "dark_fantasy"],
    "courage": ["action_battle", "cultivation_martial"],
    "adhd_focus": ["sports_competition", "action_battle"],
    "compassion": ["iyashikei", "supernatural_mystery"],
}


def load_brands(path):
    doc = yaml.safe_load(path.read_text())
    brands = []
    for bid, b in doc["brands"].items():
        brands.append({
            "brand_id": bid,
            "tier": b.get("tier", "niche"),
            "demographic": b.get("demographic", ""),
            "primary_topic": b.get("primary_topic", ""),
            "secondary_topics": b.get("secondary_topics", []),
            "manga_locales": b.get("manga_locales"),
        })
    tier_rank = {"flagship": 0, "core": 1, "niche": 2}
    brands.sort(key=lambda b: (tier_rank.get(b["tier"], 9), b["brand_id"]))
    return brands


def load_locale_genres(path, catalog):
    doc = yaml.safe_load(path.read_text())
    entry = doc["locales"][catalog]
    genres = entry["genres"]
    tier_rank = {"primary": 0, "secondary": 1, "niche": 2}
    genres = sorted(genres, key=lambda g: (tier_rank.get(g["tier"], 9), -g["share_pct"]))
    return genres


def load_brand_dna_genres(path):
    """(market-with-hyphen, brand_id) -> ordered [(genre_id, weight), ...] desc by weight,
    from the ratified 2026-07-15 world_14x37 planning pack (specs/MANGA_BRAND_DNA_ANTI_SPAM_SPEC.md).
    """
    idx = {}
    if not path.is_file():
        return idx
    with path.open() as f:
        header = f.readline()
        for line in f:
            cols = line.rstrip("\n").split("\t")
            if len(cols) < 3:
                continue
            market, brand_id, weights_str = cols[0], cols[1], cols[2]
            pairs = []
            for tok in weights_str.split(","):
                tok = tok.strip()
                if ":" not in tok:
                    continue
                gid, w = tok.rsplit(":", 1)
                try:
                    pairs.append((gid.strip(), int(w)))
                except ValueError:
                    continue
            pairs.sort(key=lambda p: -p[1])
            idx[(market, brand_id)] = pairs
    return idx


def existing_series_index(chapter_scripts_dir):
    """Map (brand_id, locale) -> series_id for every existing chapter_scripts dir."""
    idx = {}
    if not chapter_scripts_dir.is_dir():
        return idx
    for d in chapter_scripts_dir.iterdir():
        if not d.is_dir():
            continue
        parts = d.name.split("__")
        for loc in CATALOGS:
            if loc in parts:
                # brand_id is always parts[0]; locale position varies (4 or 5 field names)
                idx.setdefault((parts[0], loc), []).append(d.name)
    return idx


def pick_genre_from_dna(brand, market_hyphen, dna_idx):
    pairs = dna_idx.get((market_hyphen, brand["brand_id"]))
    if not pairs:
        return None
    gid, weight = pairs[0]
    return gid, weight


def pick_genre(brand, locale_genres, cycle_pos):
    """Fallback only -- used when the brand has no 14x37 DNA row."""
    available_ids = [g["genre_id"] for g in locale_genres]
    pref = []
    for gid in TOPIC_AFFINITY.get(brand["primary_topic"], []):
        if gid in available_ids and gid not in pref:
            pref.append(gid)
    for gid in DEMO_AFFINITY.get(brand["demographic"], []):
        if gid in available_ids and gid not in pref:
            pref.append(gid)
    if pref:
        gid = pref[0]
        return gid, False
    g = locale_genres[cycle_pos % len(locale_genres)]
    return g["genre_id"], True


CATALOG_TO_MARKET_HYPHEN = {"en_US": "en-US", "ja_JP": "ja-JP", "zh_TW": "zh-TW"}


def main():
    brands = load_brands(ROOT / "config/manga/canonical_brand_list.yaml")
    existing = existing_series_index(ROOT / "artifacts/manga/chapter_scripts")
    dna_idx = load_brand_dna_genres(
        ROOT / "artifacts/planning/world_14x37_books_manga_20260715/manga_genre_allocation_14x37.tsv")

    print("\t".join([
        "catalog", "brand_id", "tier", "demographic", "primary_topic",
        "secondary_topics", "genre_id", "genre_source", "locale_mix_check",
        "craft_bible", "arc_shape_hint", "existing_series_id", "status", "note",
    ]))

    for catalog in CATALOGS:
        locale_genres = load_locale_genres(
            ROOT / "config/manga/locale_genre_allocations.yaml", catalog)
        locale_genre_ids = {g["genre_id"] for g in locale_genres}
        market_hyphen = CATALOG_TO_MARKET_HYPHEN[catalog]
        cycle_pos = 0
        for brand in brands:
            restrict = brand["manga_locales"]
            if restrict and catalog not in restrict:
                print("\t".join([
                    catalog, brand["brand_id"], brand["tier"], brand["demographic"],
                    brand["primary_topic"], ";".join(brand["secondary_topics"]),
                    "", "", "", "", "", "", "", "EXCLUDED",
                ]) + f"\tmanga_locales restricts this brand to {restrict}")
                continue

            existing_ids = existing.get((brand["brand_id"], catalog), [])
            dna_pick = pick_genre_from_dna(brand, market_hyphen, dna_idx)
            if dna_pick:
                genre_id, weight = dna_pick
                genre_source = "14x37_dna"
            else:
                genre_id, cycled = pick_genre(brand, locale_genres, cycle_pos)
                if cycled:
                    cycle_pos += 1
                genre_source = "locale_affinity_fallback"
            locale_mix_check = "OK" if genre_id in locale_genre_ids else "FLAG_NOT_IN_LOCALE_MIX"
            bible, arc_hint = GENRE_META.get(genre_id, ("(no bible mapped -- check docs/research/manga_craft/index.md manually)", ""))
            status = "REUSE_EXISTING" if existing_ids else "NEW_SERIES"
            note = ("existing chapter_scripts dir is a LISTING only (fails "
                    "check_manga_story_authored.py) -- author into it, do not "
                    "rename/duplicate") if existing_ids else "no existing series dir; create with proper author + title"
            print("\t".join([
                catalog, brand["brand_id"], brand["tier"], brand["demographic"],
                brand["primary_topic"], ";".join(brand["secondary_topics"]),
                genre_id, genre_source, locale_mix_check,
                f"docs/research/manga_craft/{bible}", arc_hint,
                ";".join(existing_ids), status, note,
            ]))


if __name__ == "__main__":
    sys.exit(main())
