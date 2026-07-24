import csv, subprocess
from pathlib import Path

ATOMS = Path("atoms")
BACKLOG = Path("artifacts/qa/zh_tw_authoring_backlog_consolidated_20260723.tsv")
CORE_TYPES = ["HOOK","SCENE","STORY","REFLECTION","COMPRESSION","EXERCISE","INTEGRATION","PERMISSION","PIVOT","THREAD","TAKEAWAY"]

backlog_paths = set()
with open(BACKLOG) as f:
    r = csv.DictReader(f, delimiter="\t")
    for row in r:
        backlog_paths.add(row["path"])

personas = ["entrepreneurs","gen_x_sandwich","working_parents","gen_z_professionals",
    "healthcare_rns","corporate_managers","gen_alpha_students","first_responders",
    "millennial_women_professionals","tech_finance_burnout"]

candidates = []
for persona in personas:
    pdir = ATOMS / persona
    if not pdir.is_dir(): continue
    for topic_dir in sorted(pdir.iterdir()):
        if not topic_dir.is_dir(): continue
        topic = topic_dir.name
        scene = topic_dir / "SCENE" / "CANONICAL.txt"
        if not scene.exists(): continue
        try:
            if len(scene.read_text(encoding="utf-8",errors="ignore").strip()) < 200: continue
        except Exception: continue
        core_hits = [t for t in CORE_TYPES if f"atoms/{persona}/{topic}/{t}/locales/zh-TW/CANONICAL.txt" in backlog_paths]
        if core_hits: continue
        # find engine dirs = subdirs not in CORE_TYPES and not TEACHER_DOCTRINE
        engines = [d.name for d in topic_dir.iterdir() if d.is_dir() and d.name not in CORE_TYPES and d.name != "TEACHER_DOCTRINE" and d.name != "locales"]
        for eng in engines:
            eng_canonical = topic_dir / eng / "CANONICAL.txt"
            if not eng_canonical.exists(): continue
            try:
                if len(eng_canonical.read_text(encoding="utf-8",errors="ignore").strip()) < 100: continue
            except Exception: continue
            eng_path = f"atoms/{persona}/{topic}/{eng}/locales/zh-TW/CANONICAL.txt"
            if eng_path in backlog_paths: continue
            candidates.append((persona, topic, eng))

print(f"{len(candidates)} clean (persona,topic,engine) candidates before tuple-viability check")
for c in candidates:
    print(c)
