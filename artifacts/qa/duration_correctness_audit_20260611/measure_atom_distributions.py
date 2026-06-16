#!/usr/bin/env python3
"""
Measure REAL atom per-variant word-count distributions from the live atoms/ library.

Atoms are stored as variant POOLS: atoms/<persona>/<topic>/<SLOT>/CANONICAL.txt
contains many variants delimited by '## SLOT vNN' headers. The pipeline selects
ONE variant per slot instance. We measure per-variant word counts (en-US baseline;
locales/ subdirs skipped — CJK is char-counted, analysed separately).

Output: atom_wordcount_distributions.json
  - by_slot_global[SLOT]              -> distribution of one-variant word counts
  - by_persona_topic_slot[p|t|SLOT]   -> same, scoped
  - persona_topics[p]                 -> coverage frame for sampling

Read-only. No generation.
"""
from __future__ import annotations
import json
import re
import statistics as st
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ATOMS = REPO / "atoms"
OUT = Path(__file__).resolve().parent / "atom_wordcount_distributions.json"

HEADER_RE = re.compile(r"^##\s+\S+.*$", re.MULTILINE)


def variant_wordcounts(text: str) -> list[int]:
    """Split a CANONICAL.txt variant pool into variants; return word count each."""
    segs = HEADER_RE.split(text)
    counts: list[int] = []
    for seg in segs:
        body_lines = [
            ln for ln in seg.splitlines()
            if ln.strip() and not set(ln.strip()) <= set("-")  # drop --- separators
        ]
        w = len(" ".join(body_lines).split())
        if w >= 5:
            counts.append(w)
    return counts


def summarize(vals: list[int]) -> dict:
    vals = sorted(vals)
    n = len(vals)
    if n == 0:
        return {"n": 0}
    return {
        "n": n,
        "mean": round(st.mean(vals), 1),
        "median": int(st.median(vals)),
        "p10": vals[max(0, int(0.10 * (n - 1)))],
        "p25": vals[max(0, int(0.25 * (n - 1)))],
        "p75": vals[min(n - 1, int(0.75 * (n - 1)))],
        "p90": vals[min(n - 1, int(0.90 * (n - 1)))],
        "min": vals[0],
        "max": vals[-1],
        "sd": round(st.pstdev(vals), 1) if n > 1 else 0.0,
    }


def main() -> None:
    by_pts: dict[tuple, list[int]] = defaultdict(list)
    by_slot: dict[str, list[int]] = defaultdict(list)
    persona_topics: dict[str, set] = defaultdict(set)
    n_pools = 0
    n_variants = 0

    for persona_dir in sorted(ATOMS.iterdir()):
        if not persona_dir.is_dir():
            continue
        persona = persona_dir.name
        for topic_dir in sorted(persona_dir.iterdir()):
            if not topic_dir.is_dir():
                continue
            topic = topic_dir.name
            persona_topics[persona].add(topic)
            for canon in topic_dir.rglob("CANONICAL.txt"):
                # en-US baseline only: skip localized copies under */locales/<loc>/
                if "locales" in canon.parts:
                    continue
                slot = canon.parent.name  # SLOT dir holds CANONICAL.txt
                try:
                    txt = canon.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                vcs = variant_wordcounts(txt)
                if not vcs:
                    continue
                n_pools += 1
                n_variants += len(vcs)
                by_pts[(persona, topic, slot)].extend(vcs)
                by_slot[slot].extend(vcs)

    out = {
        "_meta": {
            "atoms_root": str(ATOMS),
            "n_canonical_pools": n_pools,
            "n_variants_measured": n_variants,
            "note": "per-variant word counts from '## SLOT vNN' delimited CANONICAL.txt pools; en-US baseline",
        },
        "by_slot_global": {s: summarize(v) for s, v in sorted(by_slot.items())},
        "by_persona_topic_slot": {
            f"{p}|{t}|{s}": summarize(v) for (p, t, s), v in by_pts.items()
        },
        "persona_topics": {p: sorted(ts) for p, ts in sorted(persona_topics.items())},
    }
    OUT.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"Wrote {OUT}")
    print(f"Pools: {n_pools}   Variants: {n_variants}")
    print(f"{'SLOT':22s} {'n':>6} {'median':>7} {'mean':>7} {'p10':>6} {'p90':>6}")
    for s, d in sorted(out["by_slot_global"].items(), key=lambda kv: -kv[1].get("n", 0)):
        if d.get("n", 0) >= 20:
            print(f"{s:22s} {d['n']:6d} {d['median']:7d} {d['mean']:7.0f} {d['p10']:6d} {d['p90']:6d}")


if __name__ == "__main__":
    main()
