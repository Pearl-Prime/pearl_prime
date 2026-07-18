"""Smoke test: junko x mental_health locale overlays land correctly.

After deep-merge, verify each slot has 5 options whose `line` (or `paragraphs`,
`stat_line_*`, etc.) is in the target locale's script.
"""
import sys
import pathlib
import yaml

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from pearl_news.pipeline.deterministic_teacher_topic import load_teacher_topic_pack

SLOTS_PROSE = [
    ("hook_personal", "line"),
    ("hook_big_picture", "line"),
    ("teacher_intro", "line"),
    ("youth_somatic", "line"),
    ("teacher_witness", "line"),
    ("bridge", "line"),
    ("cta", "line"),
]
SLOTS_TURN = [("turnaround", "stat_line_2")]
SLOTS_PARAS = [("teacher_perspective", "paragraphs")]
SLOTS_PRACTICE = [("practice", "announcement_line")]


def is_japanese(s: str) -> bool:
    return any("぀" <= c <= "ヿ" or "一" <= c <= "鿿" for c in s)


def is_chinese_simplified(s: str) -> bool:
    # zh-cn uses Han chars without hiragana/katakana
    has_han = any("一" <= c <= "鿿" for c in s)
    has_kana = any("぀" <= c <= "ヿ" for c in s)
    return has_han and not has_kana


def is_english(s: str) -> bool:
    return all(ord(c) < 0x4e00 for c in s) and len(s.strip()) > 0


CHECKS = {
    "en": is_english,
    "ja": is_japanese,
    "zh-cn": is_chinese_simplified,
}


print("=" * 78)
print("Junko x mental_health locale overlay smoke test")
print("=" * 78)

overall_ok = True
for lang, predicate in CHECKS.items():
    print(f"\n[{lang}]")
    pack = load_teacher_topic_pack(repo_root=REPO, teacher_id="junko",
                                    topic="mental_health", language=lang)
    if not pack:
        print(f"  FAIL: pack not loaded")
        overall_ok = False
        continue

    lang_ok = True
    for slot, field in SLOTS_PROSE + SLOTS_TURN + SLOTS_PRACTICE:
        options = (pack.get(slot) or {}).get("options") or []
        if len(options) != 5:
            print(f"  FAIL  {slot}: expected 5 options, got {len(options)}")
            lang_ok = False
            continue
        mismatches = []
        for opt in options:
            text = opt.get(field, "")
            if isinstance(text, list):
                text = " ".join(text)
            if not predicate(text):
                mismatches.append(opt.get("id"))
        if mismatches:
            print(f"  FAIL  {slot}.{field}: not in target script: {mismatches}")
            lang_ok = False
        else:
            print(f"  OK    {slot}.{field}: 5 options, all in target script")

    for slot, field in SLOTS_PARAS:
        options = (pack.get(slot) or {}).get("options") or []
        if len(options) != 5:
            print(f"  FAIL  {slot}: expected 5 options, got {len(options)}")
            lang_ok = False
            continue
        mismatches = []
        for opt in options:
            paragraphs = opt.get(field, [])
            joined = " ".join(paragraphs) if isinstance(paragraphs, list) else str(paragraphs)
            if not predicate(joined):
                mismatches.append(opt.get("id"))
        if mismatches:
            print(f"  FAIL  {slot}.{field}: not in target script: {mismatches}")
            lang_ok = False
        else:
            print(f"  OK    {slot}.{field}: 5 options, all in target script")

    # Headline subsystem
    hl_opts = (((pack.get("title_system") or {}).get("headline_layer_2") or {})
                .get("options") or [])
    if len(hl_opts) != 5:
        print(f"  FAIL  headline_layer_2: expected 5 options, got {len(hl_opts)}")
        lang_ok = False
    else:
        mismatches = [o.get("id") for o in hl_opts if not predicate(o.get("line", ""))]
        if mismatches:
            print(f"  FAIL  headline_layer_2.line: not in target script: {mismatches}")
            lang_ok = False
        else:
            print(f"  OK    headline_layer_2.line: 5 options, all in target script")

    if not lang_ok:
        overall_ok = False
    print(f"  {'PASS' if lang_ok else 'FAIL'} {lang}")

print("\n" + "=" * 78)
if overall_ok:
    print("ALL 3 LOCALES PASS — junko x mental_health overlays verified.")
    sys.exit(0)
else:
    print("FAIL — see above.")
    sys.exit(1)
