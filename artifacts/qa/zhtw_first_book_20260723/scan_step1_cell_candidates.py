import os, csv, subprocess, sys
from pathlib import Path

ROOT = Path(".")
ATOMS = ROOT / "atoms"
BACKLOG = ROOT / "artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv"

CORE_TYPES = ["HOOK","SCENE","STORY","REFLECTION","COMPRESSION","EXERCISE","INTEGRATION","PERMISSION","PIVOT","THREAD","TAKEAWAY"]

# load backlog paths -> set
backlog_paths = set()
with open(BACKLOG) as f:
    r = csv.DictReader(f, delimiter="\t")
    for row in r:
        backlog_paths.add(row["path"])

personas_priority = ["midlife_women","gen_z_student","nyc_executives","educators",
    "millennial_women_professionals","nyc_executives","entrepreneurs","gen_x_sandwich",
    "working_parents","gen_z_professionals","healthcare_rns","corporate_managers",
    "gen_alpha_students","tech_finance_burnout","first_responders"]
seen = set()
personas = []
for p in personas_priority:
    if p not in seen:
        personas.append(p); seen.add(p)

results = []
for persona in personas:
    pdir = ATOMS / persona
    if not pdir.is_dir(): continue
    for topic_dir in sorted(pdir.iterdir()):
        if not topic_dir.is_dir(): continue
        topic = topic_dir.name
        # check SCENE bank non-empty
        scene = topic_dir / "SCENE" / "CANONICAL.txt"
        if not scene.exists():
            continue
        try:
            content = scene.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if len(content.strip()) < 200:
            continue
        # check core body-prose zh-TW backlog hits (excluding engine-specific dirs which are lowercase)
        core_hits = 0
        core_hit_types = []
        for t in CORE_TYPES:
            path = f"atoms/{persona}/{topic}/{t}/locales/zh-TW/CANONICAL.txt"
            if path in backlog_paths:
                core_hits += 1
                core_hit_types.append(t)
        if core_hits > 0:
            continue  # skip dirty core cells
        results.append((persona, topic))

print(f"Found {len(results)} clean candidate (persona,topic) pairs with non-empty EN SCENE + 0 core-type zh-TW backlog hits")
for p,t in results:
    print(p,t)
