#!/usr/bin/env python3
"""Generate artifacts/coordination/authoring_frontier_en_US.json.

Reconstructs the en_US authoring frontier deterministically from plans + arcs on
disk, reusing discover_assemble_campaign._arc_for_plan as the canonical
"arc-blocked" definition (a plan is arc-blocked iff it has no matching master_arc
file). Emits the unique (persona, topic, engine, fmt) cells that still need an arc,
plus topic/template distribution. No paid LLM; pure filesystem scan.

  PYTHONPATH=. python3 scripts/catalog/gen_authoring_frontier.py
  PYTHONPATH=. python3 scripts/catalog/gen_authoring_frontier.py --out artifacts/coordination/authoring_frontier_en_US.json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
PLANS = REPO / "config/source_of_truth/book_plans_en_us"
ARCS = REPO / "config/source_of_truth/master_arcs"
ATOMS = REPO / "atoms"
TEMPLATES = ARCS / "templates"
DEFAULT_OUT = REPO / "artifacts/coordination/authoring_frontier_en_US.json"

# compatible_formats per template (mirrors templates/*.yaml); first match wins in this order.
TEMPLATE_FORMATS = [
    ("standard_escalation", {"F001", "F002", "F003", "F006", "F007", "F010", "F011", "F014"}),
    ("slow_burn", {"F004", "F009", "F013"}),
    ("wave_cycle", {"F008"}),
]


def _load(p: Path) -> dict:
    try:
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}


def _import_dac():
    spec = importlib.util.spec_from_file_location(
        "dac", REPO / "scripts/catalog/discover_assemble_campaign.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _template_for(fmt: str) -> str:
    for name, fmts in TEMPLATE_FORMATS:
        if fmt in fmts:
            return name
    return "standard_escalation"


def _atoms_ok(persona: str, topic: str, engine: str) -> bool:
    p = ATOMS / persona / topic / engine / "CANONICAL.txt"
    return p.is_file() and p.stat().st_size > 100


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    dac = _import_dac()
    files = sorted(PLANS.glob("*.yaml"))
    cells: dict[tuple, list[str]] = defaultdict(list)
    blocked = 0
    needs_auth = 0
    for i, f in enumerate(files):
        if i % 5000 == 0:
            print(f"... {i}/{len(files)}", file=sys.stderr)
        plan = _load(f)
        if dac._arc_for_plan(plan):
            continue
        blocked += 1
        if plan.get("_needs_authoring") is True:
            needs_auth += 1
        bid = plan.get("book_id") or f.stem
        parts = bid.split("__")
        persona = parts[2] if len(parts) > 2 else ""
        topic = parts[3] if len(parts) > 3 else plan.get("topic", "")
        engine = plan.get("engine") or (parts[4].removesuffix("__1hr") if len(parts) > 4 else "")
        fmt = plan.get("structural_format_id") or "F006"
        cells[(persona, topic, engine, fmt)].append(bid)

    need_arc = []
    for (persona, topic, engine, fmt), bids in sorted(cells.items()):
        need_arc.append({
            "persona": persona, "topic": topic, "engine": engine, "fmt": fmt,
            "template": _template_for(fmt),
            "n_plans": len(bids),
            "atoms_ok": _atoms_ok(persona, topic, engine),
            "arc_file": f"{persona}__{topic}__{engine}__{fmt}.yaml",
            "sample_book_id": bids[0],
        })

    motif_banks = {tf.stem: set((_load(tf).get("motif_bank") or {}).keys())
                   for tf in TEMPLATES.glob("*.yaml")}
    topic_counts = Counter(c["topic"] for c in need_arc)
    payload = {
        "locale": "en_US",
        "generated_by": "scripts/catalog/gen_authoring_frontier.py",
        "total_plans": len(files),
        "arc_blocked_plans": blocked,
        "arc_blocked_needs_authoring": needs_auth,
        "unique_cells": len(need_arc),
        "topics": dict(topic_counts.most_common()),
        "motif_banks_present": {k: sorted(v) for k, v in motif_banks.items()},
        "need_arc": need_arc,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"Wrote {args.out}: {len(need_arc)} cells, "
          f"{blocked} arc-blocked plans ({needs_auth} needs_authoring), "
          f"{len(topic_counts)} topics")
    return 0


if __name__ == "__main__":
    sys.exit(main())
