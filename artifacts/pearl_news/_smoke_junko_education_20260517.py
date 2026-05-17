"""Smoke test: junko x education 5-variation rotation + locale overlays."""
import sys
import pathlib
import tempfile
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

TEACHER = "junko"
TOPIC = "education"
PACK_PATH = REPO / f"pearl_news/teacher_topic_packs/teachers/{TEACHER}/{TOPIC}.yaml"

SLOTS_TO_CHECK = [
    "hook_personal", "hook_big_picture", "teacher_intro", "youth_somatic",
    "teacher_witness", "turnaround", "bridge", "teacher_perspective",
    "practice", "cta",
]


def is_japanese(s):
    return any("぀" <= c <= "ヿ" or "一" <= c <= "鿿" for c in s)


def is_chinese_simplified(s):
    has_han = any("一" <= c <= "鿿" for c in s)
    has_kana = any("぀" <= c <= "ヿ" for c in s)
    return has_han and not has_kana


def is_english(s):
    return all(ord(c) < 0x4e00 for c in s) and len(s.strip()) > 0


SCRIPT_CHECKS = {"en": is_english, "ja": is_japanese, "zh-cn": is_chinese_simplified}

print(f"=" * 78)
print(f"junko x {TOPIC} 5-variation + locale smoke test")
print(f"=" * 78)

# 1. YAML parse
with open(PACK_PATH, "r", encoding="utf-8") as f:
    pack = yaml.safe_load(f)
print(f"\n[1] YAML parse: OK ({len(pack)} top-level keys)")

# 2. Distinct ids + semantic_families
print(f"\n[2] Slot option counts + semantic_family distinctness:")
all_ok = True
for slot in SLOTS_TO_CHECK:
    options = (pack.get(slot) or {}).get("options") or []
    fams = [(o.get("metadata") or {}).get("semantic_family") for o in options]
    ids = [o.get("id") for o in options]
    ok = (len(options) == 5 and len(set(fams)) == 5 and len(set(ids)) == 5)
    print(f"  [{'OK' if ok else 'FAIL'}] {slot}: {len(options)} opts | {len(set(ids))} ids | {len(set(fams))} families")
    if not ok:
        all_ok = False
        print(f"         fams: {fams}")

hl = ((pack.get("title_system") or {}).get("headline_layer_2") or {}).get("options") or []
hl_fams = [(o.get("metadata") or {}).get("semantic_family") for o in hl]
ok = (len(hl) == 5 and len(set(hl_fams)) == 5)
print(f"  [{'OK' if ok else 'FAIL'}] headline_layer_2: {len(hl)} opts | {len(set(hl_fams))} families")
if not ok:
    all_ok = False

# 3. LRU rotation (live selector)
print(f"\n[3] LRU rotation (hook_personal):")
with tempfile.TemporaryDirectory() as tmpdir:
    log_path = pathlib.Path(tmpdir) / "_test.json"
    from pearl_news.pipeline.atom_usage_tracker import pick_least_recently_used
    options = pack["hook_personal"]["options"]
    picks = []
    for i in range(7):
        chosen = pick_least_recently_used(
            options, teacher_id=TEACHER, topic=TOPIC,
            slot_name="hook_personal",
            article_id=f"junko-edu-test-{i:02d}",
            log_path=log_path, record_pick=True,
        )
        picks.append(chosen["id"])
    for i, p in enumerate(picks):
        print(f"  {i+1}. {p}")
    if len(set(picks[:5])) == 5 and picks[5] in picks[:5]:
        print(f"  OK: 5 unique then earliest-repeat (LRU working)")
    else:
        all_ok = False
        print(f"  FAIL")

# 4. Locale overlays
print(f"\n[4] Locale overlay verification:")
from pearl_news.pipeline.deterministic_teacher_topic import load_teacher_topic_pack
for lang, predicate in SCRIPT_CHECKS.items():
    p = load_teacher_topic_pack(repo_root=REPO, teacher_id=TEACHER,
                                topic=TOPIC, language=lang)
    if not p:
        print(f"  [{lang}] FAIL: pack not loaded")
        all_ok = False
        continue
    lang_ok = True
    for slot in SLOTS_TO_CHECK:
        opts = (p.get(slot) or {}).get("options") or []
        if len(opts) != 5:
            print(f"  [{lang}] {slot}: FAIL — {len(opts)} opts")
            lang_ok = False
            continue
        mismatches = []
        for opt in opts:
            text = opt.get("line") or opt.get("stat_line_2") or opt.get("announcement_line") or ""
            if isinstance(opt.get("paragraphs"), list):
                text = " ".join(opt["paragraphs"])
            if not predicate(text):
                mismatches.append(opt.get("id"))
        if mismatches:
            print(f"  [{lang}] {slot}: FAIL — {mismatches}")
            lang_ok = False
    if lang_ok:
        print(f"  [{lang}]: OK")
    else:
        all_ok = False

# 5. Authority overlay
print(f"\n[5] Authority overlay:")
p = load_teacher_topic_pack(repo_root=REPO, teacher_id=TEACHER, topic=TOPIC, language="en")
dn = (p.get("identity") or {}).get("display_name", "")
if dn == "Junko":
    print(f"  identity.display_name = 'Junko' (canonicalized via doctrine overlay)")
else:
    print(f"  FAIL: got {dn!r}")
    all_ok = False

print("\n" + "=" * 78)
if all_ok:
    print(f"ALL PASS — junko x {TOPIC} verified.")
    sys.exit(0)
else:
    print(f"FAIL — see above.")
    sys.exit(1)
