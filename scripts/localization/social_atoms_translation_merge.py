#!/usr/bin/env python3
"""Merge a {source_atom_id: translated_text} map onto EN social-media atoms
(SOURCE_OF_TRUTH/social_media_atoms/evergreen_en_us_atoms.jsonl) to produce a
locale JSONL, with schema fields (atom_id, locale, char_count, word_count,
translation_status, etc.) computed consistently.

Built for the CJK6 social-atom translation lane (2026-07-24,
docs/agent_prompt_packs/20260724_social_tts_en_plus_cjk6/03_Pearl_Localization_cjk6_translate.md).
Reuse for the remaining draft_operator_review_required extension wave rather
than forking a new script.

Usage:
  python3 scripts/localization/social_atoms_translation_merge.py \\
      <locale_us e.g. ja_JP> <translations.json> <out.jsonl> <source.json> [culture_risk_note]

translations.json format: {"EVG-ENUS-ANXI-CORP-B-01": "translated text", ...}
Must have exactly one entry per atom in source.json (KeyError raised otherwise).
Optional 5th arg overrides `culture_risk` uniformly for this locale's rows.
"""
import json
import sys
from datetime import date

LOCALE_TOKEN = {
    "ja_JP": "JAJP", "ko_KR": "KOKR", "zh_CN": "ZHCN",
    "zh_TW": "ZHTW", "zh_HK": "ZHHK", "zh_SG": "ZHSG",
}
LOCALE_HYPHEN = {
    "ja_JP": "ja-JP", "ko_KR": "ko-KR", "zh_CN": "zh-CN",
    "zh_TW": "zh-TW", "zh_HK": "zh-HK", "zh_SG": "zh-SG",
}
ENGINE = "claude_sonnet5_tier1_subagent"


def main():
    locale_us, trans_path, out_path, source_path = sys.argv[1:5]
    culture_risk_note = sys.argv[5] if len(sys.argv) > 5 else None
    token = LOCALE_TOKEN[locale_us]
    hyphen = LOCALE_HYPHEN[locale_us]

    with open(source_path, encoding="utf-8") as f:
        source = json.load(f)
    with open(trans_path, encoding="utf-8") as f:
        translations = json.load(f)

    missing = [a["atom_id"] for a in source if a["atom_id"] not in translations]
    if missing:
        print(f"ERROR: {len(missing)} atoms missing a translation, e.g. {missing[:5]}", file=sys.stderr)
        sys.exit(1)

    today = date.today().isoformat()
    out_rows = []
    for a in source:
        src_id = a["atom_id"]
        text = translations[src_id]
        row = dict(a)  # copy all source fields
        row["text"] = text
        row["locale"] = hyphen
        row["market_fit"] = hyphen
        row["atom_id"] = src_id.replace("ENUS", token)
        row["source_atom_id"] = src_id
        row["source_review_status"] = a.get("review_status")
        row["review_status"] = "translated_operator_review_required"
        row["translation_status"] = "machine_translated_unreviewed"
        row["translation_engine"] = ENGINE
        row["translation_date"] = today
        row["native_review_required"] = True
        row["acceptance_layer"] = "authored candidate (translated) — pending native review"
        if culture_risk_note:
            row["culture_risk"] = culture_risk_note
        row["char_count"] = len(text)
        row["word_count"] = len(text.split())
        row["first_fold_chars"] = len(text)
        out_rows.append(row)

    with open(out_path, "w", encoding="utf-8") as f:
        for row in out_rows:
            f.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")

    print(f"Wrote {len(out_rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
