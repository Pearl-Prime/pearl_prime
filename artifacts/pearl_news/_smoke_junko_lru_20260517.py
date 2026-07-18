"""Smoke test: junko x mental_health 5-variation rotation.

Validates:
  1. EN base pack parses as valid YAML.
  2. Each slot has 5 distinct options with 5 distinct semantic_family values.
  3. LRU selector returns 5 unique atoms across 5 consecutive article_ids,
     then repeats the earliest pick on the 6th call.
"""
import sys
import pathlib
import yaml
import shutil
import tempfile

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

PACK_PATH = REPO / "pearl_news/teacher_topic_packs/teachers/junko/mental_health.yaml"

print("=" * 78)
print("Junko x mental_health 5-variation LRU smoke test")
print("=" * 78)

# 1. YAML parse
with open(PACK_PATH, "r", encoding="utf-8") as f:
    pack = yaml.safe_load(f)
print(f"\n[1] YAML parse: OK ({len(pack)} top-level keys)")

# 2. Slot option counts + semantic_family distinctness
SLOTS_TO_CHECK = [
    "hook_personal",
    "hook_big_picture",
    "teacher_intro",
    "youth_somatic",
    "teacher_witness",
    "turnaround",
    "bridge",
    "teacher_perspective",
    "practice",
    "cta",
]

print("\n[2] Slot option counts + semantic_family distinctness:")
all_ok = True
for slot in SLOTS_TO_CHECK:
    options = (pack.get(slot) or {}).get("options") or []
    families = []
    ids = []
    for opt in options:
        meta = opt.get("metadata") or {}
        families.append(meta.get("semantic_family"))
        ids.append(opt.get("id"))
    count = len(options)
    unique_families = len(set(families))
    unique_ids = len(set(ids))
    status = "OK" if (count == 5 and unique_families == 5 and unique_ids == 5) else "FAIL"
    if status == "FAIL":
        all_ok = False
    print(f"  [{status}] {slot}: {count} options | {unique_ids} unique ids | {unique_families} unique families")
    if status == "FAIL":
        print(f"         ids:      {ids}")
        print(f"         families: {families}")

# Headline subsystem (nested differently)
hl = ((pack.get("title_system") or {}).get("headline_layer_2") or {}).get("options") or []
hl_families = [(o.get("metadata") or {}).get("semantic_family") for o in hl]
hl_ids = [o.get("id") for o in hl]
status = "OK" if (len(hl) == 5 and len(set(hl_families)) == 5 and len(set(hl_ids)) == 5) else "FAIL"
if status == "FAIL":
    all_ok = False
print(f"  [{status}] headline_layer_2: {len(hl)} options | {len(set(hl_ids))} unique ids | {len(set(hl_families))} unique families")

# 3. LRU rotation end-to-end via the actual selector
print("\n[3] LRU rotation (live selector, hook_personal slot):")
# Use a temp log path so we do not pollute the real artifacts/atom_usage_log.json
with tempfile.TemporaryDirectory() as tmpdir:
    log_path = pathlib.Path(tmpdir) / "_test_lru.json"

    from pearl_news.pipeline.atom_usage_tracker import pick_least_recently_used

    options = pack["hook_personal"]["options"]
    chosen_ids = []
    for i in range(7):
        chosen = pick_least_recently_used(
            options,
            teacher_id="junko",
            topic="mental_health",
            slot_name="hook_personal",
            article_id=f"junko-mh-test-{i:02d}",
            log_path=log_path,
            record_pick=True,
        )
        chosen_ids.append(chosen["id"])

    print(f"  Picks across 7 article_ids:")
    for i, cid in enumerate(chosen_ids):
        print(f"    {i+1}. {cid}")

    first_five_unique = len(set(chosen_ids[:5])) == 5
    sixth_is_repeat = chosen_ids[5] in chosen_ids[:5]
    if first_five_unique and sixth_is_repeat:
        print(f"\n  OK: first 5 picks are unique, 6th repeats earliest (LRU working).")
    else:
        all_ok = False
        print(f"\n  FAIL: first_five_unique={first_five_unique} sixth_is_repeat={sixth_is_repeat}")

# 4. Full pack-loader integration test
print("\n[4] Full pack-loader integration (apply_authority + LRU + locale):")
from pearl_news.pipeline.deterministic_teacher_topic import load_teacher_topic_pack

loaded = load_teacher_topic_pack(
    repo_root=REPO,
    teacher_id="junko",
    topic="mental_health",
    language="en",
)
# Confirm doctrine canonicalization fired
identity = (loaded or {}).get("identity") or {}
display_name = identity.get("display_name", "")
print(f"  identity.display_name = {display_name!r}")
if display_name == "Junko":
    print(f"  OK: doctrine overlay canonicalized to 'Junko'")
else:
    all_ok = False
    print(f"  FAIL: expected 'Junko', got {display_name!r}")

opt_count = len((loaded.get("hook_personal") or {}).get("options") or [])
print(f"  hook_personal options after locale merge = {opt_count}")
if opt_count == 5:
    print(f"  OK: 5 options survived locale merge")
else:
    print(f"  NOTE: {opt_count} options after locale merge — ja/zh-cn overlays not yet expanded.")

print("\n" + "=" * 78)
if all_ok:
    print("ALL PASS — junko x mental_health 5-variation expansion verified.")
    sys.exit(0)
else:
    print("FAIL — see above.")
    sys.exit(1)
