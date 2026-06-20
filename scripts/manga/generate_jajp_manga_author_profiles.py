#!/usr/bin/env python3
"""
Generate full EI manga-author profile YAMLs for the ja_JP catalog authors.
==========================================================================

Materializes one `config/authoring/manga_authors/*.yaml` profile per distinct
(brand_id, manga_author) pair referenced by the live ja_JP series plans — so
every author named in the catalog has a full EI-disclosure profile.

Faithful to the AS-BUILT data: display_names come straight from the series plans
(written by synthesize_manga_titles_jajp.py); this does NOT re-roll names. No LLM
— disclosure/bio/visual fields are templated in native Japanese.

Schema: config/authoring/manga_authors/schema.yaml (v1.0). Satisfies the enforced
collision rules (no pen-name clash · unique display_name per brand · unique
author_id). genre_tie_in is the reconciled genre (the schema's enum predates the
catalog reconciliation and is not CI-enforced; resolver matches on brand+genre).

Idempotent for a given catalog state. Usage:
  python3 scripts/manga/generate_jajp_manga_author_profiles.py
  python3 scripts/manga/generate_jajp_manga_author_profiles.py --dry-run
"""

from __future__ import annotations

import argparse
import glob
import hashlib
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))
from generate_manga_author import load_pen_name_display_names  # noqa: E402
from synthesize_manga_titles_jajp import GENRE_JP, TOPIC_JP  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
SERIES_DIR = REPO / "config" / "source_of_truth" / "manga_series_plans" / "ja_JP"
CANONICAL_BRANDS = REPO / "config" / "manga" / "canonical_brand_list.yaml"
OUT_DIR = REPO / "config" / "authoring" / "manga_authors"


def _author_id(brand: str, genre: str, name: str) -> str:
    h = hashlib.sha256(f"{brand}|{name}".encode("utf-8")).hexdigest()[:8]
    base = genre.lower().replace("-", "_")
    return f"{base}_{h}_ja_jp"  # ^[a-z][a-z0-9_]{3,63}$


def _disclosure(name: str) -> str:
    return (
        f"{name}は、AIによって生み出された覚醒知性（EI, Enlightened Intelligence）の"
        f"キャラクター作者です。物語はすべてAIが執筆しており、その事実を完全に開示しています"
        f"——これは制約ではなく、新しく透明な創作のかたちです。"
    )


def _bio(name: str, brand: str, genre_jp: str, topic_jp: str) -> str:
    return (
        f"{name}は、{brand}ブランドの{genre_jp}作品を手がけるEI漫画家。"
        f"{topic_jp}を物語の奥に静かに織り込みながら、{genre_jp}の様式で読者の心に届く一作を描く。"
    )


def _visual(brand: str, genre: str) -> str:
    return (
        f"{brand}のブランドビジュアルDNAに準拠。ジャンル: {genre}。"
        f"線画・スクリーントーン・配色・吹き出しの様式は config/brand_dna/ のパラメータに従う。"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Report counts; write nothing")
    args = ap.parse_args()

    brands = (yaml.safe_load(open(CANONICAL_BRANDS, encoding="utf-8")) or {}).get("brands", {})
    pen_names = load_pen_name_display_names()

    groups: dict[tuple[str, str], dict] = defaultdict(
        lambda: {"genres": [], "topics": [], "demographic": "general"}
    )
    for f in sorted(glob.glob(str(SERIES_DIR / "*.yaml"))):
        d = yaml.safe_load(open(f, encoding="utf-8")) or {}
        name = d.get("manga_author", "")
        if not name or name == "TBD":
            continue
        g = groups[(d["brand_id"], name)]
        g["genres"].append(d.get("genre", ""))
        g["topics"].append(d.get("topic", ""))
        g["demographic"] = d.get("demographic", "general")

    seen_ids: set[str] = set()
    written = 0
    pen_clash: list[str] = []
    for (brand, name), g in sorted(groups.items()):
        if name in pen_names:
            pen_clash.append(name)
            continue
        genre = Counter(g["genres"]).most_common(1)[0][0]
        topic = Counter(g["topics"]).most_common(1)[0][0]
        secondary = sorted(set(g["genres"]) - {genre})
        binfo = brands.get(brand, {})
        demo = binfo.get("demographic", g["demographic"])
        genre_jp = GENRE_JP.get(genre, genre)
        topic_jp = TOPIC_JP.get(topic, topic.replace("_", " "))

        aid = _author_id(brand, genre, name)
        while aid in seen_ids:
            aid += "x"
        seen_ids.add(aid)

        profile = {
            "author_id": aid,
            "display_name": name,
            "locale": "ja_JP",
            "genre_tie_in": genre,
            "brand_id": brand,
            "target_demographic": demo,
            "therapeutic_topic": topic,
            "ei_disclosure_text": _disclosure(name),
            "visual_style_notes": _visual(brand, genre),
            "bio_blurb": _bio(name, brand, genre_jp, topic_jp),
            "status": "active",
            "created_at": "2026-06-20T00:00:00Z",
        }
        if secondary:
            profile["secondary_genres"] = secondary
        if not args.dry_run:
            OUT_DIR.mkdir(parents=True, exist_ok=True)
            with open(OUT_DIR / f"{aid}.yaml", "w", encoding="utf-8") as fh:
                fh.write(f"# Manga Author Profile — {genre} (ja_JP) · brand {brand}\n")
                fh.write("# Auto-generated by scripts/manga/generate_jajp_manga_author_profiles.py\n\n")
                yaml.dump(profile, fh, allow_unicode=True, default_flow_style=False, sort_keys=False)
        written += 1

    print(f"profiles={'(dry) ' if args.dry_run else ''}{written}  "
          f"distinct_(brand,author)={len(groups)}  pen_name_clashes={len(pen_clash)} {pen_clash[:5]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
