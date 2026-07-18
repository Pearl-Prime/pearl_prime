"""Smoke test: junko x economy_work + climate 5-variation expansion."""
import sys
import pathlib
import tempfile
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

TEACHER = "junko"
TOPICS = ["economy_work", "climate"]

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

all_ok = True

for topic in TOPICS:
    print(f"\n{'=' * 78}\n{TEACHER} x {topic}\n{'=' * 78}")

    pack_path = REPO / f"pearl_news/teacher_topic_packs/teachers/{TEACHER}/{topic}.yaml"
    with open(pack_path, "r", encoding="utf-8") as f:
        pack = yaml.safe_load(f)
    print(f"[1] YAML parse: OK ({len(pack)} top-level keys)")

    print(f"[2] 5 unique families per slot:")
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

    print(f"[3] LRU rotation (hook_personal):")
    with tempfile.TemporaryDirectory() as tmpdir:
        log_path = pathlib.Path(tmpdir) / "_test.json"
        from pearl_news.pipeline.atom_usage_tracker import pick_least_recently_used
        options = pack["hook_personal"]["options"]
        picks = []
        for i in range(7):
            chosen = pick_least_recently_used(
                options, teacher_id=TEACHER, topic=topic,
                slot_name="hook_personal",
                article_id=f"junko-{topic}-test-{i:02d}",
                log_path=log_path, record_pick=True,
            )
            picks.append(chosen["id"])
        for i, p in enumerate(picks):
            print(f"  {i+1}. {p}")
        if len(set(picks[:5])) == 5 and picks[5] in picks[:5]:
            print(f"  OK: 5 unique then earliest-repeat")
        else:
            all_ok = False
            print(f"  FAIL")

    print(f"[4] Locale verification:")
    from pearl_news.pipeline.deterministic_teacher_topic import load_teacher_topic_pack
    for lang, predicate in SCRIPT_CHECKS.items():
        p = load_teacher_topic_pack(repo_root=REPO, teacher_id=TEACHER,
                                    topic=topic, language=lang)
        if not p:
            print(f"  [{lang}] FAIL: pack not loaded")
            all_ok = False
            continue
        lang_ok = True
        for slot in SLOTS_TO_CHECK:
            opts = (p.get(slot) or {}).get("options") or []
            if len(opts) != 5:
                print(f"  [{lang}] {slot}: FAIL - {len(opts)} opts")
                lang_ok = False
                continue
            for opt in opts:
                text = opt.get("line") or opt.get("stat_line_2") or opt.get("announcement_line") or ""
                if isinstance(opt.get("paragraphs"), list):
                    text = " ".join(opt["paragraphs"])
                if not predicate(text):
                    print(f"  [{lang}] {slot}.{opt.get('id')}: NOT in target script")
                    lang_ok = False
                    break
            if not lang_ok:
                break
        if lang_ok:
            print(f"  [{lang}]: OK")
        else:
            all_ok = False

print("\n" + "=" * 78)
if all_ok:
    print("ALL PASS")
    sys.exit(0)
else:
    print("FAIL")
    sys.exit(1)
