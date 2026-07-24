#!/usr/bin/env python3
"""Verify a translated locale JSONL file for the CJK6 social atom translation lane.

Checks (per locale):
  - row count matches source count
  - every row has non-empty `text`, correct `locale`, `atom_id` derived from
    `source_atom_id` with the ENUS token swapped for the locale token
  - CJK script presence (no bare-ASCII leftover English rows)
  - zh-TW / zh-HK: Traditional-purity via opencc s2t + Big5 non-encodability
    (same method as scripts/localization/check_title_language_conformance.py
    -- avoids the documented false-positive class on chars common to both
    scripts, memory: reference_zhtw_simplified_detection_big5)
  - zh-CN / zh-SG: Simplified-purity via opencc t2s + gb2312 non-encodability
  - ja-JP: Hiragana/Katakana/Kanji codepoint presence
  - ko-KR: Hangul codepoint presence

Reuse for the remaining draft_operator_review_required extension wave rather
than forking a new checker.

Usage:
  python3 scripts/localization/social_atoms_translation_verify.py \\
      <locale_code_underscore> <path_to_jsonl> <source_json>
"""
import json
import sys

HIRAGANA_KATAKANA = [(0x3040, 0x30FF), (0x31F0, 0x31FF)]
HANGUL = [(0xAC00, 0xD7A3), (0x1100, 0x11FF), (0x3130, 0x318F)]
CJK_IDEOGRAPH = [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF)]


def has_cp(text, ranges):
    for ch in text:
        cp = ord(ch)
        for lo, hi in ranges:
            if lo <= cp <= hi:
                return True
    return False


def is_ascii_only(text):
    return all(ord(ch) < 128 for ch in text)


def has_non_encodable(text, codec):
    for ch in text:
        if not ch.isalpha():
            continue
        try:
            ch.encode(codec)
        except UnicodeEncodeError:
            return True
    return False


_opencc_cache = {}


def opencc_conv(mode):
    if mode not in _opencc_cache:
        import opencc
        _opencc_cache[mode] = opencc.OpenCC(mode)
    return _opencc_cache[mode]


def wrong_script_traditional_required(text):
    if not text.strip():
        return False
    s2t = opencc_conv("s2t")
    if s2t.convert(text) == text:
        return False
    return has_non_encodable(text, "big5")


def wrong_script_simplified_required(text):
    if not text.strip():
        return False
    t2s = opencc_conv("t2s")
    if t2s.convert(text) == text:
        return False
    return has_non_encodable(text, "gb2312")


LOCALE_TOKEN = {
    "ja_JP": "JAJP", "ko_KR": "KOKR", "zh_CN": "ZHCN",
    "zh_TW": "ZHTW", "zh_HK": "ZHHK", "zh_SG": "ZHSG",
}
LOCALE_HYPHEN = {
    "ja_JP": "ja-JP", "ko_KR": "ko-KR", "zh_CN": "zh-CN",
    "zh_TW": "zh-TW", "zh_HK": "zh-HK", "zh_SG": "zh-SG",
}


def main():
    locale_us, path, source_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(source_path, encoding="utf-8") as f:
        source = json.load(f)
    source_ids = {a["atom_id"] for a in source}

    rows = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))

    problems = []
    token = LOCALE_TOKEN[locale_us]
    hyphen = LOCALE_HYPHEN[locale_us]

    if len(rows) != len(source):
        problems.append(f"ROW_COUNT_MISMATCH: got {len(rows)} want {len(source)}")

    ascii_leftover = 0
    script_wrong = 0
    bad_id_link = 0
    seen_source_ids = set()

    for r in rows:
        text = r.get("text", "")
        if r.get("locale") != hyphen:
            problems.append(f"BAD_LOCALE_FIELD atom_id={r.get('atom_id')} locale={r.get('locale')}")
        src_id = r.get("source_atom_id")
        if src_id not in source_ids:
            bad_id_link += 1
        else:
            seen_source_ids.add(src_id)
        expected_id = src_id.replace("ENUS", token) if src_id else None
        if r.get("atom_id") != expected_id:
            problems.append(f"ATOM_ID_MISMATCH got={r.get('atom_id')} want={expected_id}")

        if not text.strip():
            problems.append(f"EMPTY_TEXT atom_id={r.get('atom_id')}")
            continue

        if is_ascii_only(text):
            ascii_leftover += 1
            problems.append(f"ASCII_ONLY_LEFTOVER atom_id={r.get('atom_id')} text={text[:60]!r}")
            continue

        if locale_us == "ja_JP":
            if not has_cp(text, HIRAGANA_KATAKANA + CJK_IDEOGRAPH):
                script_wrong += 1
                problems.append(f"NO_JA_SCRIPT atom_id={r.get('atom_id')}")
        elif locale_us == "ko_KR":
            if not has_cp(text, HANGUL):
                script_wrong += 1
                problems.append(f"NO_KO_SCRIPT atom_id={r.get('atom_id')}")
        elif locale_us in ("zh_TW", "zh_HK"):
            if wrong_script_traditional_required(text):
                script_wrong += 1
                problems.append(f"SIMPLIFIED_IN_TRADITIONAL atom_id={r.get('atom_id')} text={text[:60]!r}")
        elif locale_us in ("zh_CN", "zh_SG"):
            if wrong_script_simplified_required(text):
                script_wrong += 1
                problems.append(f"TRADITIONAL_IN_SIMPLIFIED atom_id={r.get('atom_id')} text={text[:60]!r}")

    missing_ids = source_ids - seen_source_ids

    print(f"=== VERIFY {locale_us} ({path}) ===")
    print(f"rows: {len(rows)}  source: {len(source)}")
    print(f"ascii_leftover: {ascii_leftover}")
    print(f"script_wrong: {script_wrong}")
    print(f"bad_id_link: {bad_id_link}")
    print(f"missing_source_ids: {len(missing_ids)}")
    if problems:
        print(f"PROBLEMS ({len(problems)}):")
        for p in problems[:40]:
            print(" -", p)
        if len(problems) > 40:
            print(f"   ... and {len(problems)-40} more")
        print("RESULT: FAIL")
        sys.exit(1)
    else:
        print("RESULT: PASS")


if __name__ == "__main__":
    main()
