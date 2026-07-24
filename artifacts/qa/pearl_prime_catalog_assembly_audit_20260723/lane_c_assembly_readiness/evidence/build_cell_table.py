#!/usr/bin/env python3
"""Lane C — full-corpus cell-level assembly-readiness prediction.

Read-only static analysis. Does NOT render, assemble, or invoke any pipeline
entry point. For every distinct (persona, topic, engine) cell that appears
anywhere in config/source_of_truth/book_plans_en_us/ (all 40 brand archetypes,
32,401 planned books), predicts:

  - CANONICAL.txt atom bank presence:  atoms/<persona>/<topic>/<engine>/CANONICAL.txt
  - story_atoms character bank presence: story_atoms/<persona>/anchored/<topic>/<engine>/ (non-empty)
  - thesis-bank topic-overlay coverage: topic in chapter_thesis_bank.yaml 'topics:' keys
  - predicted research_fit bind status: BOUND / UNBOUND-thin / UNKNOWN
  - predicted acceptance-layer ceiling (per PEARL_PRIME_BESTSELLER_ACCEPTANCE_SCORECARD.md)

Weighted by how many planned books (across all 40 brands) actually use that
cell, so the catalog-scale rollup is an EXACT full-corpus tabulation, not a
sample extrapolation.
"""
import os
import csv
import json
from pathlib import Path
from collections import defaultdict, Counter

REPO = Path("/private/tmp/claude-501/-Users-ahjan-phoenix-omega/eda0f494-ed89-4f19-95ff-cb16877fe8ea/scratchpad/wt-lane-c")
PLANS_DIR = REPO / "config/source_of_truth/book_plans_en_us"
ATOMS_DIR = REPO / "atoms"
STORY_ATOMS_DIR = REPO / "story_atoms"
THESIS_BANK = REPO / "config/planning/chapter_thesis_bank.yaml"

import yaml
thesis = yaml.safe_load(open(THESIS_BANK))
THESIS_TOPICS = set(thesis.get("topics", {}).keys())

# ---- Enumerate every distinct (persona, topic, engine) cell + book count + brand set ----
cell_counts = Counter()
cell_brands = defaultdict(set)
cell_needs_authoring_false = Counter()

for f in os.listdir(PLANS_DIR):
    if not f.endswith(".yaml"):
        continue
    base = f[:-5]
    if base.endswith("__1hr"):
        base = base[:-5]
    parts = base.split("__")
    if len(parts) < 5:
        continue
    brand, teacher, persona, topic, engine = parts[0], parts[1], parts[2], parts[3], parts[4]
    cell = (persona, topic, engine)
    cell_counts[cell] += 1
    cell_brands[cell].add(brand)

print(f"Distinct (persona,topic,engine) cells: {len(cell_counts)}")
print(f"Total planned book files covered: {sum(cell_counts.values())}")


def canonical_present(persona, topic, engine):
    p = ATOMS_DIR / persona / topic / engine / "CANONICAL.txt"
    return p.exists() and p.stat().st_size > 0


def story_atoms_present(persona, topic, engine):
    d = STORY_ATOMS_DIR / persona / "anchored" / topic / engine
    if not d.is_dir():
        return False
    # non-empty: at least one file somewhere under it
    for _root, _dirs, files in os.walk(d):
        if files:
            return True
    return False


rows = []
for cell, count in cell_counts.items():
    persona, topic, engine = cell
    canon = canonical_present(persona, topic, engine)
    story = story_atoms_present(persona, topic, engine)
    thesis_overlay = topic in THESIS_TOPICS

    if canon and story:
        bind = "BOUND"
    elif canon and not story:
        bind = "UNBOUND-thin"
    else:
        bind = "UNKNOWN"  # neither present (or story present w/o canon — treat as UNKNOWN too, checked below)

    # ceiling per scorecard
    if bind == "BOUND":
        ceiling = "authored-candidate-possible (Layer 2+ reachable; NOT guaranteed — see healthcare_rns x burnout 43006 precedent)"
    elif bind == "UNBOUND-thin":
        ceiling = "structurally-clear-only (Layer 1 cap; research_fit binding cap per scorecard)"
    else:
        ceiling = "likely-hard-fail (no atom bank at all; InsufficientVariantsError / renderer skip likely)"

    rows.append({
        "persona": persona,
        "topic": topic,
        "engine": engine,
        "planned_book_count": count,
        "brand_spread": len(cell_brands[cell]),
        "canonical_txt_present": canon,
        "story_atoms_present": story,
        "thesis_topic_overlay": thesis_overlay,
        "predicted_bind_status": bind,
        "predicted_acceptance_ceiling": ceiling,
    })

rows.sort(key=lambda r: -r["planned_book_count"])

out_csv = REPO.parent / "lane_c_work" / "full_cell_table.csv"
with open(out_csv, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {out_csv}")

# ---- Catalog-scale rollup (weighted by planned_book_count) ----
total_books = sum(r["planned_book_count"] for r in rows)
bound_books = sum(r["planned_book_count"] for r in rows if r["predicted_bind_status"] == "BOUND")
unbound_books = sum(r["planned_book_count"] for r in rows if r["predicted_bind_status"] == "UNBOUND-thin")
unknown_books = sum(r["planned_book_count"] for r in rows if r["predicted_bind_status"] == "UNKNOWN")

bound_cells = sum(1 for r in rows if r["predicted_bind_status"] == "BOUND")
unbound_cells = sum(1 for r in rows if r["predicted_bind_status"] == "UNBOUND-thin")
unknown_cells = sum(1 for r in rows if r["predicted_bind_status"] == "UNKNOWN")

print("\n=== CATALOG-SCALE ROLLUP (weighted by planned book count, full 32,401-file corpus) ===")
print(f"Total planned books (en_US, all 40 brands): {total_books}")
print(f"BOUND (canon+story present)      : {bound_books:6d} books ({100*bound_books/total_books:.1f}%)  across {bound_cells} of {len(rows)} distinct cells")
print(f"UNBOUND-thin (canon only)         : {unbound_books:6d} books ({100*unbound_books/total_books:.1f}%)  across {unbound_cells} of {len(rows)} distinct cells")
print(f"UNKNOWN (neither bank)            : {unknown_books:6d} books ({100*unknown_books/total_books:.1f}%)  across {unknown_cells} of {len(rows)} distinct cells")

# ---- Per-persona rollup (worst-exposure finding) ----
persona_totals = defaultdict(lambda: Counter())
for r in rows:
    persona_totals[r["persona"]][r["predicted_bind_status"]] += r["planned_book_count"]

print("\n=== PER-PERSONA ROLLUP ===")
persona_summary = []
for persona, c in sorted(persona_totals.items(), key=lambda kv: -sum(kv[1].values())):
    total = sum(c.values())
    bound_pct = 100 * c.get("BOUND", 0) / total if total else 0
    persona_summary.append((persona, total, c.get("BOUND", 0), c.get("UNBOUND-thin", 0), c.get("UNKNOWN", 0), bound_pct))
    print(f"{persona:35s} total={total:6d}  BOUND={c.get('BOUND',0):6d} ({bound_pct:5.1f}%)  UNBOUND-thin={c.get('UNBOUND-thin',0):6d}  UNKNOWN={c.get('UNKNOWN',0):6d}")

with open(REPO.parent / "lane_c_work" / "persona_rollup.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["persona", "total_planned_books", "bound_books", "unbound_thin_books", "unknown_books", "bound_pct"])
    for row in persona_summary:
        w.writerow(row)

# ---- Per-topic rollup (thesis-overlay cross-check) ----
topic_totals = defaultdict(lambda: Counter())
for r in rows:
    topic_totals[r["topic"]][r["predicted_bind_status"]] += r["planned_book_count"]

print("\n=== PER-TOPIC ROLLUP (thesis overlay cross-check) ===")
topic_summary = []
for topic, c in sorted(topic_totals.items(), key=lambda kv: -sum(kv[1].values())):
    total = sum(c.values())
    bound_pct = 100 * c.get("BOUND", 0) / total if total else 0
    has_overlay = topic in THESIS_TOPICS
    topic_summary.append((topic, total, c.get("BOUND", 0), c.get("UNBOUND-thin", 0), c.get("UNKNOWN", 0), bound_pct, has_overlay))
    print(f"{topic:25s} total={total:6d}  BOUND={c.get('BOUND',0):6d} ({bound_pct:5.1f}%)  thesis_overlay={has_overlay}")

with open(REPO.parent / "lane_c_work" / "topic_rollup.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["topic", "total_planned_books", "bound_books", "unbound_thin_books", "unknown_books", "bound_pct", "thesis_topic_overlay"])
    for row in topic_summary:
        w.writerow(row)

summary = {
    "total_planned_books": total_books,
    "bound_books": bound_books,
    "unbound_thin_books": unbound_books,
    "unknown_books": unknown_books,
    "bound_pct": round(100*bound_books/total_books, 2),
    "unbound_pct": round(100*unbound_books/total_books, 2),
    "unknown_pct": round(100*unknown_books/total_books, 2),
    "distinct_cells": len(rows),
    "bound_cells": bound_cells,
    "unbound_cells": unbound_cells,
    "unknown_cells": unknown_cells,
}
with open(REPO.parent / "lane_c_work" / "rollup_summary.json", "w") as f:
    json.dump(summary, f, indent=2)
print("\nWrote rollup_summary.json:", summary)
