#!/usr/bin/env python3
"""Generate pen-name author rosters for EVERY active brand archetype.

The author routing CODE (phoenix_v4/planning/author_brand_resolver.py) is already
correct (specificity-score); the gap is DATA — only stillness_press has a curated
pen-name pool. This emits a SUPERSET assignments file (curated rows kept verbatim +
generated rows for every other active archetype) so the resolver routes a distinct
byline author per (brand, topic). Curated brands are never overwritten.

Pen names are synthesized deterministically (stable per brand) from a name bank;
they can later be re-pointed to the 452-profile pool (config/authoring/
pen_name_teacher_profiles.yaml) for real bios/voices — that's an enrichment layer,
not needed for plan/cover/dashboard. sai_ma / sai_maa is NEVER used as a pen name.

Run:  PYTHONPATH=. python3 scripts/brand_management/gen_author_rosters.py
Out:  config/brand_author_assignments_generated.yaml
"""
from __future__ import annotations
import hashlib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "config/brand_management/global_brand_registry_unified.yaml"
CURATED = ROOT / "config/brand_author_assignments.yaml"
OUT = ROOT / "config/brand_author_assignments_generated.yaml"

FIRST = ["Lena", "Daniel", "Mira", "Kai", "Ruth", "Sam", "Noor", "Tara", "Rowan", "Mae",
         "Silas", "Iris", "Theo", "Ana", "Grace", "Hannah", "Jonah", "Marcus", "Oscar", "Priya",
         "Wren", "Cole", "Devon", "Elena", "Nina", "Ravi", "Sofia", "Tomas", "Adam", "Bea",
         "Caleb", "Dora", "Eli", "Faye", "Gideon", "Hana", "Ivo", "Juno", "Kira", "Liam",
         "Maya", "Nico", "Opal", "Pia", "Quinn", "Rhea", "Soren", "Talia", "Uma", "Vera",
         "Wade", "Yara", "Zane", "Brid", "Esme", "Otis", "Lior", "Suki"]
LAST = ["Frost", "Voss", "Santos", "Okafor", "Alder", "Meridian", "Ibrahim", "Woodfield", "Beck", "Rivers",
        "Grant", "Tam", "Castellan", "Reyes", "Adeyemi", "Stern", "Kim", "Reed", "Bello", "Raman",
        "Adler", "Bennett", "Hale", "Petrova", "Vazquez", "Chandra", "Marchetti", "Vidal", "Holt", "Crane",
        "Dunmore", "Ellison", "Fenwick", "Gable", "Harlow", "Iverson", "Janssen", "Keller", "Lowell", "Marsh",
        "Nolan", "Oakes", "Pryce", "Quill", "Rourke", "Sable", "Thorne", "Underhill", "Vance", "Whitlock",
        "Yardley", "Zhao", "Bramble", "Calder", "Devlin", "Estes", "Fairlie", "Gowan"]
BANNED = {"sai_ma", "sai_maa"}


def _h(s: str) -> int:
    return int(hashlib.sha1(s.encode()).hexdigest()[:8], 16)


def gen_pool(brand: str, n: int) -> list[str]:
    seed = _h(brand)
    out, used = [], set()
    i = 0
    while len(out) < n and i < n * 6:
        fn = FIRST[(seed + i * 13) % len(FIRST)]
        ln = LAST[(seed // 7 + i * 17) % len(LAST)]
        aid = f"{fn}_{ln}".lower()
        if aid not in used and aid not in BANNED:
            used.add(aid)
            out.append(aid)
        i += 1
    return out


def main() -> None:
    reg = yaml.safe_load(REG.read_text())
    curated = yaml.safe_load(CURATED.read_text()) or {}
    curated_rows = curated.get("assignments") or []
    have_pool = {r.get("brand_id") for r in curated_rows if r.get("author_pool")}

    # dedupe registry to active archetypes
    arche = {}
    for bid, rec in reg["brands"].items():
        a = rec.get("brand_archetype_id") or bid
        if rec.get("lifecycle", "active") == "active":
            arche.setdefault(a, rec)

    gen_rows, n_brands, n_authors = [], 0, 0
    for a, rec in sorted(arche.items()):
        if a in have_pool:
            continue  # curated wins (e.g. stillness_press)
        topics = rec.get("primary_topics") or []
        if not topics:
            continue  # thin brand: no topics -> no buildable cells yet, skip
        n = max(6, min(len(topics) + 1, 10))
        pool = gen_pool(a, n)
        gen_rows.append({"brand_id": a, "default_author": pool[0],
                         "author_pool": [{"author_id": p, "tier": 1 if i < 4 else 2}
                                         for i, p in enumerate(pool)]})
        for idx, topic in enumerate(sorted(topics)):
            gen_rows.append({"brand_id": a, "topic_ids": [topic], "default_author": pool[idx % len(pool)]})
        n_brands += 1
        n_authors += len(pool)

    merged = {
        "_generated_by": "scripts/brand_management/gen_author_rosters.py",
        "_note": "SUPERSET: curated brand_author_assignments.yaml rows + generated composite rosters. "
                 "Pen names are deterministic placeholders; re-point to pen_name_teacher_profiles.yaml for bios/voices.",
        "assignments": curated_rows + gen_rows,
    }
    OUT.write_text(yaml.safe_dump(merged, sort_keys=False, allow_unicode=True))
    print(f"curated brands with pool: {sorted(have_pool)}")
    print(f"generated rosters: {n_brands} brands, {n_authors} pen authors")
    print(f"total assignment rows: {len(merged['assignments'])} -> {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
