#!/usr/bin/env python3
"""Per-brand finalize after authoring+merge: clean legacy remnants + ensure bylines,
then emit cross-series title-dedupe targets. Reusable across the grind.

  python3 artifacts/coordination/brand_finalize.py <brand>
Writes /tmp/<brand>_dedupe.json = {"retitle":[...], "avoid_titles":[...]} (empty retitle if no dupes).
"""
import glob, json, sys
from collections import defaultdict, Counter
from pathlib import Path
import yaml
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from phoenix_v4.planning.author_brand_resolver import resolve_author_from_brand

ROOT = Path(__file__).resolve().parents[2]
BDIR = ROOT / "config/source_of_truth/book_plans_en_us"
ASSIGN = ROOT / "config/brand_author_assignments_generated.yaml"
ASSIGN = ASSIGN if ASSIGN.exists() else None
LEG = ["created_at", "main_character_name", "main_character_lora_id", "confidence", "plan_source_path"]


def main():
    brand = sys.argv[1]
    books = {}
    for f in sorted(glob.glob(str(BDIR / f"{brand}__*.yaml"))):
        d = yaml.safe_load(open(f))
        if d.get("_needs_authoring") is not False:
            continue
        books[f] = d
    # clean legacy remnants + ensure bylines
    cleaned = 0
    for f, d in books.items():
        ch = False
        for k in LEG:
            if k in d:
                d.pop(k); ch = True
        ap = d.setdefault("author_positioning", {})
        if not ap.get("byline_author"):
            p = d["book_id"].split("__")
            ap["byline_author"] = resolve_author_from_brand(brand_id=brand, topic_id=p[3], persona_id=p[2], assignments_path=ASSIGN)
            ch = True
        if ch:
            open(f, "w").write(yaml.safe_dump(d, sort_keys=False, allow_unicode=True)); cleaned += 1
    # global title map (all brands) for the avoid-list + cross-brand collision detection
    global_titles = defaultdict(set)  # title -> {brands}
    for f in sorted(glob.glob(str(BDIR / "*.yaml"))):
        gd = yaml.safe_load(open(f))
        if gd.get("_needs_authoring") is not False:
            continue
        global_titles[gd["title"]].add(gd["book_id"].split("__")[0])

    # find within-brand exact dupes + cross-brand collisions + near-dupes (first-word clusters >=3)
    t2b = defaultdict(list)
    for d in books.values():
        t2b[d["title"]].append(d["book_id"])
    avoid = sorted(global_titles.keys())
    flagged = set()
    retitle = []

    def add(bid, reason):
        if bid in flagged:
            return
        flagged.add(bid)
        p = bid.split("__")
        retitle.append({"book_id": bid, "persona": p[2], "topic": p[3], "engine": p[4],
                        "current_title": next(d["title"] for d in books.values() if d["book_id"] == bid),
                        "subtitle": next(d.get("subtitle", "") for d in books.values() if d["book_id"] == bid),
                        "reason": reason})

    # exact dupes within brand: keep first, retitle rest
    for t, bids in t2b.items():
        if len(bids) > 1:
            for bid in sorted(bids)[1:]:
                add(bid, "exact_dup")

    # cross-brand collisions: a current-brand title also used by another (already-authored) brand
    for t, bids in t2b.items():
        if global_titles.get(t, set()) - {brand}:
            for bid in bids:
                add(bid, "cross_brand")

    # near-dupes: cluster by first significant word; keep 2, diversify the rest
    def fw(t):
        ws = t.split()
        if ws and ws[0].lower() in {"the", "a", "an"} and len(ws) > 1:
            return ws[1].lower().strip(".,:;'\"")
        return ws[0].lower().strip(".,:;'\"") if ws else ""
    clusters = defaultdict(list)
    for d in books.values():
        clusters[fw(d["title"])].append(d["book_id"])
    overused = []
    for word, bids in clusters.items():
        if len(bids) >= 3:
            overused.append(word)
            for bid in sorted(bids)[2:]:
                add(bid, f"near_dup:{word}")

    json.dump({"retitle": retitle, "avoid_titles": avoid, "overused_openers": overused},
              open(f"/tmp/{brand}_dedupe.json", "w"))
    print(f"{brand}: authored={len(books)} cleaned={cleaned} distinct={len(t2b)} retitle={len(retitle)} overused_openers={overused}")
    for r in retitle:
        print(f'  [{r["reason"]}] {r["persona"]}/{r["topic"]}/{r["engine"]}  was "{r["current_title"]}"')


def books_by_id(books, bid):
    for d in books.values():
        if d["book_id"] == bid:
            return d
    return {}


if __name__ == "__main__":
    main()
