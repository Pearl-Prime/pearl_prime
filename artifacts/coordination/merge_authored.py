#!/usr/bin/env python3
"""Merge Pearl_Writer/Pearl_Editor structured authoring into skeleton plan YAMLs.

Input: a JSON file = list of series objects from author-brand-catalog-wf:
  [{series_id, series:{reader_promise_family, reader_avatar, series_voice_markers, comp_series},
    books:[{book_id, title, subtitle, cover_tagline, short_blurb, long_description,
            keywords:{primary,secondary}, comp_titles, bisac_codes}]}]

Writes the prose fields into the existing skeleton series_plan + book_plan YAMLs (preserving
ALL structural fields), sets _needs_authoring: false. Deterministic; never touches non-listed files.

  python3 artifacts/coordination/merge_authored.py /tmp/authored.json
"""
import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SDIR = ROOT / "config/source_of_truth/series_plans_en_us"
BDIR = ROOT / "config/source_of_truth/book_plans_en_us"


def main():
    data = json.load(open(sys.argv[1]))
    n_series = n_books = 0
    problems = []
    for s in data:
        sid = s["series_id"]
        sp_path = SDIR / f"{sid}.yaml"
        if not sp_path.exists():
            problems.append(f"missing series skeleton: {sid}")
            continue
        sp = yaml.safe_load(sp_path.read_text())
        sa = s["series"]
        sp["reader_promise_family"] = sa["reader_promise_family"]
        sp["reader_avatar"] = sa["reader_avatar"]
        sp["series_voice_markers"] = sa["series_voice_markers"]
        sp["comp_series"] = sa["comp_series"]
        sp["_needs_authoring"] = False
        sp_path.write_text(yaml.safe_dump(sp, sort_keys=False, allow_unicode=True))
        n_series += 1

        for b in s["books"]:
            bid = b["book_id"]
            bp_path = BDIR / f"{bid}.yaml"
            if not bp_path.exists():
                problems.append(f"missing book skeleton: {bid}")
                continue
            bp = yaml.safe_load(bp_path.read_text())
            bp["title"] = b["title"]
            bp["subtitle"] = b["subtitle"]
            bp["cover_tagline"] = b["cover_tagline"]
            bp["description"] = {"short_blurb": b["short_blurb"], "long_description": b["long_description"]}
            bp["keywords"] = {"primary": b["keywords"]["primary"], "secondary": b["keywords"]["secondary"]}
            bp["comp_titles"] = b["comp_titles"]
            bp["bisac_codes"] = b["bisac_codes"]
            bp["_needs_authoring"] = False
            bp_path.write_text(yaml.safe_dump(bp, sort_keys=False, allow_unicode=True))
            n_books += 1

    print(f"merged {n_series} series + {n_books} books")
    if problems:
        print("PROBLEMS:")
        for p in problems:
            print("  " + p)
        sys.exit(1)


if __name__ == "__main__":
    main()
