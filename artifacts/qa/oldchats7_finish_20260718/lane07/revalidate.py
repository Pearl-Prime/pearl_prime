#!/usr/bin/env python3
from pathlib import Path
import re
import yaml

LANE = Path(__file__).resolve().parent
ROOT = LANE.parents[3]
TEACHER = ("Sai Maa", "Ahjan", "Master Wu", "Master Sha", "Master Feung", "Junko", "Jagadguru")


def split_paras(text: str):
    return [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]


pass_n = fail_n = 0
details = []
for path in (ROOT / "SOURCE_OF_TRUTH/accent_banks/wisdom_essence").rglob("entries.yaml"):
    data = yaml.safe_load(path.read_text())
    for e in data.get("entries") or []:
        body = ((e.get("register_variants") or {}).get("secular") or {}).get("body") or ""
        n = len(split_paras(body))
        bleed = [t for t in TEACHER if t.lower() in body.lower()]
        ok = n == 3 and e.get("secular_safe") is True and not bleed
        pass_n += int(ok)
        fail_n += int(not ok)
        eid = e.get("essence_id")
        details.append(f"WISDOM {eid} paras={n} ok={ok}")

for rel in [
    "SOURCE_OF_TRUTH/accent_banks/encouragement/anxiety/entries.yaml",
    "SOURCE_OF_TRUTH/accent_banks/hook_story/anxiety/entries.yaml",
    "SOURCE_OF_TRUTH/accent_banks/metaphor/anxiety/entries.yaml",
    "SOURCE_OF_TRUTH/accent_banks/exercise_setup/anxiety/entries.yaml",
    "SOURCE_OF_TRUTH/accent_banks/reflection_questions/anxiety/entries.yaml",
    "SOURCE_OF_TRUTH/accent_banks/troubleshooting/anxiety/entries.yaml",
]:
    data = yaml.safe_load((ROOT / rel).read_text())
    for e in data.get("entries") or []:
        if e.get("deepened_by") != "lane07_source_authority_repair_20260718":
            continue
        body = e.get("body") or ""
        paras = len(split_paras(body))
        ok = bool(body.strip()) and bool(e.get("source_authority")) and bool(e.get("depth_pattern"))
        pass_n += int(ok)
        fail_n += int(not ok)
        details.append(f"{e.get('accent_id')} paras={paras} ok={ok}")

data = yaml.safe_load(
    (ROOT / "SOURCE_OF_TRUTH/accent_banks/external_stories/anxiety_entries.yaml").read_text()
)
for cluster in (data.get("clusters") or {}).values():
    for e in cluster or []:
        if e.get("deepened_by") == "lane07_source_authority_repair_20260718":
            ok = bool(e.get("story")) and bool(e.get("source_authority"))
            pass_n += int(ok)
            fail_n += int(not ok)
            details.append(f"{e.get('story_id')} alias={e.get('atom_type_alias')} ok={ok}")

(LANE / "VALIDATOR_REPORT.txt").write_text(
    f"PASS={pass_n} FAIL={fail_n}\n" + "\n".join(details) + "\n"
)
(LANE / "CHECKPOINT.md").write_text(
    f"""# Lane 07 checkpoint (final)

SOURCED=3
PARTIAL=7
NO_SOURCE=1
VALIDATOR_PASS={pass_n} VALIDATOR_FAIL={fail_n}
ROWS_DEEPENED=30
STILL_BLOCKED=MOTIF
FLAGSHIP_NOTE=ch1 parity FAIL on dirty shared tree; lane07 paths absent from CANONICAL_FLAGSHIP_CH1 atom_manifest (pre-existing drift)
"""
)
print(f"PASS={pass_n} FAIL={fail_n}")
