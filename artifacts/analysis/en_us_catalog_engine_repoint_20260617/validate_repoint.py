#!/usr/bin/env python3
"""Validate re-pointed en_US plans per EN_US_CATALOG_ENGINE_REPOINT_V1_SPEC §7.

Checks, per brand, that 100% of written plans satisfy:
  1. parse (valid YAML)
  2. engine-legal (engine in allowed_engines[topic], not in forbidden)
  3. engine matches filename suffix AND series arc.installment.engine
  4. arc-backed (master_arc file exists)
  5. distinct (title, subtitle) within brand
  6. 0 "[Topic] Book" tails, 0 "Readers", persona-named where templated

Reports planned coverage % per brand.
"""
import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict

import yaml

BRANDS = ["stillness_press", "somatic_wisdom", "digital_ground", "cognitive_clarity",
          "sleep_restoration", "solar_return", "heart_balance"]


def load_yaml(p):
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_id(book_id):
    p = book_id.split("__")
    return p[0], p[1], p[2], p[3], p[4]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--arc-root", default=None, help="root holding master_arcs (default=root)")
    ap.add_argument("--bindings", required=True)
    ap.add_argument("--brand", default="ALL")
    args = ap.parse_args()

    bind = load_yaml(args.bindings)
    book_dir = os.path.join(args.root, "config/source_of_truth/book_plans_en_us")
    series_dir = os.path.join(args.root, "config/source_of_truth/series_plans_en_us")
    arc_dir = os.path.join(args.arc_root or args.root, "config/source_of_truth/master_arcs")
    brands = BRANDS if args.brand == "ALL" else [args.brand]

    overall_ok = True
    report = {}
    for brand in brands:
        files = sorted(glob.glob(os.path.join(book_dir, f"{brand}__*.yaml")))
        n = len(files)
        fails = defaultdict(list)
        seen_ts = {}
        # series engine map
        series_engines = {}
        for sp in sorted(glob.glob(os.path.join(series_dir, f"{brand}__*.yaml"))):
            d = load_yaml(sp)
            arc = d.get("arc") or {}
            for k, v in arc.items():
                series_engines[v.get("book_id")] = v.get("engine")
        topics_used = set()
        personas_used = set()
        for fp in files:
            fn = os.path.basename(fp)[:-5]
            try:
                d = load_yaml(fp)
            except Exception as e:
                fails["parse"].append(f"{fn}: {e}"); continue
            bid = d.get("book_id", "")
            _, _, persona, topic, eng_fn = parse_id(fn)
            topics_used.add(topic); personas_used.add(persona)
            engine = d.get("engine", "")
            allowed = set(bind.get(topic, {}).get("allowed_engines") or [])
            forbidden = set(bind.get(topic, {}).get("forbidden_engines") or [])
            # 2 engine-legal
            if engine not in allowed or engine in forbidden:
                fails["engine_illegal"].append(f"{fn}: engine={engine} not in allowed{allowed}")
            # 3 engine matches filename + book_id + series
            if engine != eng_fn:
                fails["engine_filename_mismatch"].append(f"{fn}: field={engine} fn={eng_fn}")
            if bid != fn:
                fails["book_id_filename_mismatch"].append(f"{fn}: book_id={bid}")
            if series_engines.get(bid) != engine:
                fails["series_engine_mismatch"].append(f"{fn}: series={series_engines.get(bid)}")
            # 4 arc-backed
            if not os.path.exists(os.path.join(arc_dir, f"{persona}__{topic}__{engine}__F006.yaml")):
                fails["no_arc"].append(fn)
            # 5 distinct (title, subtitle)
            t, s = d.get("title", ""), d.get("subtitle", "")
            key = (t, s)
            if key in seen_ts:
                fails["dup_title_subtitle"].append(f"{fn}: dup of {seen_ts[key]} -> {t!r}/{s!r}")
            else:
                seen_ts[key] = fn
            # 6 banned strings
            blob = f"{t} {s}"
            if re.search(r"\bReaders\b", blob):
                fails["readers"].append(f"{fn}: {blob!r}")
            if re.search(r"\bBook\b\s*$", t) or re.search(r"A [A-Z][a-z ]+ Book\b", t):
                # "[Topic] Book" tail (the old devotion defect)
                fails["topic_book_tail"].append(f"{fn}: title={t!r}")
            # empty title is a fail
            if not t:
                fails["empty_title"].append(fn)
            # dangling fill markers (unreplaced {X} or trailing 'for' with no persona)
            if "{" in blob or re.search(r"\bfor\s*$", blob) or re.search(r"\bfor\s*:", blob):
                fails["dangling_fill"].append(f"{fn}: {blob!r}")

        total_fail = sum(len(v) for v in fails.values())
        ok = total_fail == 0
        overall_ok = overall_ok and ok
        report[brand] = {
            "n_plans": n,
            "topics": sorted(topics_used),
            "n_personas": len(personas_used),
            "PASS": ok,
            "fail_counts": {k: len(v) for k, v in fails.items()},
            "sample_fails": {k: v[:3] for k, v in fails.items()},
        }

    print(json.dumps(report, indent=2))
    print("\n=== OVERALL:", "ALL PASS" if overall_ok else "FAILURES PRESENT", "===")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
