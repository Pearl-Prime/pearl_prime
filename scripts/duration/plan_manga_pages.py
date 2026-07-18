#!/usr/bin/env python3
"""
CDIS §9 — Manga / webtoon panel and page recommendations.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration._config import config_snapshot_hash, load_yaml, should_skip_output, write_atomically  # noqa: E402

# §9.1 genre tables (panels)
GENRE_TABLE = {
    "webtoon_canvas": {
        "comedy": (12, 22, 30),
        "slice_of_life": (12, 22, 30),
        "iyashikei": (20, 28, 40),
        "healing": (20, 28, 40),
        "default": (15, 24, 35),
    },
    "webtoon_originals": {
        "horror": (40, 55, 80),
        "crime": (40, 55, 80),
        "drama": (40, 55, 80),
        "fantasy": (35, 50, 70),
        "action": (35, 50, 70),
        "default": (40, 50, 70),
    },
    "kakao": {"default": (40, 55, 80)},
    "bilibili_comics": {"default": (30, 60, 85)},
    "lezhin": {"default": (70, 80, 100)},
}


def plan_manga(
    platform: str,
    genre: str,
    therapeutic_intent: bool,
    locale: str,
    breath_sequences: int,
) -> dict:
    plat_key = platform.lower().replace(" ", "_")
    if plat_key in ("webtoon", "webtoon_canvas"):
        table = GENRE_TABLE["webtoon_canvas"]
    elif plat_key in ("webtoon_originals", "originals"):
        table = GENRE_TABLE["webtoon_originals"]
    elif "kakao" in plat_key:
        table = GENRE_TABLE["kakao"]
    elif "bilibili" in plat_key:
        table = GENRE_TABLE["bilibili_comics"]
    elif "lezhin" in plat_key:
        table = GENRE_TABLE["lezhin"]
    else:
        table = GENRE_TABLE["webtoon_canvas"]

    g = genre.lower().replace(" ", "_")
    tup = table.get(g) or table.get("default")
    pmin, popt, pmax = tup

    overhead = 0
    if therapeutic_intent:
        overhead += breath_sequences * 7
        if genre.lower() in ("iyashikei", "healing"):
            overhead += 5

    lo = min(pmax, pmin + overhead)
    opt = min(pmax, popt + overhead)
    hi = min(pmax + overhead, pmax + 15)

    pages = max(8, int(round(opt / 4.5)))
    chapters = 1

    iyashikei = genre.lower() in ("iyashikei", "healing")
    return {
        "platform": platform,
        "genre": genre,
        "locale": locale,
        "therapeutic_intent": therapeutic_intent,
        "breath_sequences": breath_sequences,
        "recommended_panel_count": int(opt),
        "panel_range": [int(lo), int(hi)],
        "recommended_page_count": pages,
        "chapter_count": chapters,
        "therapeutic_overhead_panels": overhead,
        "iyashikei_density": iyashikei,
        "config_hash": config_snapshot_hash(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="CDIS manga page / panel planner")
    ap.add_argument("--platform", default="webtoon")
    ap.add_argument("--genre", default="iyashikei")
    ap.add_argument("--therapeutic-intent", action="store_true")
    ap.add_argument("--locale", default="en-US")
    ap.add_argument("--breath-sequences", type=int, default=2, help="per chapter (ITE §9.2)")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()
    _ = load_yaml(REPO_ROOT / "config" / "duration" / "serialization_cadence.yaml")
    outp = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(outp, ["recommended_panel_count", "config_hash"], args.force, h):
        print(f"Skip: {outp}")
        return 0
    doc = plan_manga(
        args.platform,
        args.genre,
        args.therapeutic_intent,
        args.locale,
        args.breath_sequences,
    )
    write_atomically(outp, doc)
    print(f"Wrote {args.out} panels={doc['recommended_panel_count']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
