#!/usr/bin/env python3
"""Buildable matrix: per active brand archetype, how many catalog cells are
arc-backed (plannable) — intersect each brand's primary_topics x primary_personas
with the master_arcs inventory (persona__topic__engine__format). This bounds the
real catalog size (arcs exist) vs the aspirational ~800/brand.

  PYTHONPATH=. python3 scripts/catalog/build_buildable_matrix.py
Out: artifacts/coordination/buildable_matrix.tsv
"""
from __future__ import annotations
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "config/brand_management/global_brand_registry_unified.yaml"
ARCS = ROOT / "config/source_of_truth/master_arcs"
OUT = ROOT / "artifacts/coordination/buildable_matrix.tsv"


def main():
    reg = yaml.safe_load(REG.read_text())
    brands = reg["brands"]
    n_lanes = len(reg.get("lanes", []))

    pairs = defaultdict(list)
    arc_personas, arc_topics, bad = set(), set(), 0
    for p in sorted(ARCS.glob("*.yaml")):
        parts = p.stem.split("__")
        if len(parts) != 4:
            bad += 1
            continue
        persona, topic, engine, fmt = parts
        pairs[(persona, topic)].append((engine, fmt))
        arc_personas.add(persona)
        arc_topics.add(topic)
    n_arcs = sum(len(v) for v in pairs.values())

    arche = {}
    for bid, rec in brands.items():
        arche.setdefault(rec.get("brand_archetype_id") or bid, rec)

    rows = []
    for a, rec in sorted(arche.items()):
        topics = rec.get("primary_topics") or []
        personas = rec.get("primary_personas") or []
        life = rec.get("lifecycle", "active")
        tm = rec.get("teacher_mode", False)
        series = books = 0
        for ps in personas:
            for tp in topics:
                cells = pairs.get((ps, tp))
                if cells:
                    series += 1
                    books += len(cells)
        rows.append((a, tm, life, len(topics), len(personas), series, books, books * n_lanes))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w") as f:
        f.write(f"archetype\tteacher_mode\tlifecycle\tn_topics\tn_personas\tbuildable_series\tbuildable_books\tbooks_x{n_lanes}lanes\n")
        for r in rows:
            f.write("\t".join(str(x) for x in r) + "\n")

    active = [r for r in rows if r[2] == "active"]
    tot_books = sum(r[6] for r in active)
    zero = [r[0] for r in active if r[6] == 0]
    print(f"arcs: {n_arcs} cells / {len(pairs)} (persona,topic) pairs; {bad} unparsed")
    print(f"archetypes: {len(rows)} ({len(active)} active)")
    print(f"buildable books/brand-locale (active): {tot_books}; x{n_lanes} lanes = {tot_books * n_lanes}")
    print(f"brands w/ 0 buildable (need arc seeding): {len(zero)} -> {zero}")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
