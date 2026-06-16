#!/usr/bin/env python3
"""Aggregate per-render score.json into SUMMARY.json + a markdown table."""
from __future__ import annotations

import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
TIERS = ["standard_book", "extended_book_2h", "deep_book_6h"]
LEVERB = {"standard_book": 61, "extended_book_2h": 67, "deep_book_6h": 224}
TIO = "HOOK v02 'The task is open'"

rows: dict = {}
for sj in OUT.glob("*/*/score.json"):
    d = json.loads(sj.read_text())
    rows[(d["format"], d["arm"])] = d

summary = {
    "cell": "gen_z_professionals x anxiety (ahjan), seed=leverB_baseline",
    "method": ("prefix = origin/main pre-fix enrichment_select via importlib shim; "
               "fixed = working-tree fix; composer/register_gate/atoms identical across arms"),
    "leverB_authority_baseline_F1": LEVERB,
    "tiers": [],
}
for t in TIERS:
    summary["tiers"].append({"format": t,
                             "prefix": rows.get((t, "prefix")),
                             "fixed": rows.get((t, "fixed"))})
(OUT / "SUMMARY.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

print("| tier | arm | words | F1 | F1_sizes | 'task is open' | verdict |")
print("|---|---|--:|--:|---|--:|---|")
for t in TIERS:
    for arm in ("prefix", "fixed"):
        d = rows.get((t, arm))
        if not d:
            print(f"| {t} | {arm} | — | MISSING | | | |")
            continue
        tio = d["cluster_phrase_counts"].get(TIO, "?")
        print(f"| {t} | {arm} | {d['words']} | {d['F1']} | {d['F1_sizes']} | {tio} | {d['verdict']} |")

print()
print("DELTA (prefix -> fixed):")
for t in TIERS:
    pre, fix = rows.get((t, "prefix")), rows.get((t, "fixed"))
    if pre and fix:
        ptio = pre["cluster_phrase_counts"][TIO]
        ftio = fix["cluster_phrase_counts"][TIO]
        print(f"  {t:18} F1 {pre['F1']:>3} -> {fix['F1']:>3} (delta {fix['F1']-pre['F1']:+d}); "
              f"'task is open' {ptio} -> {ftio}; words {pre['words']} -> {fix['words']}")
    else:
        print(f"  {t:18} incomplete (prefix={'ok' if pre else 'MISSING'}, fixed={'ok' if fix else 'MISSING'})")
