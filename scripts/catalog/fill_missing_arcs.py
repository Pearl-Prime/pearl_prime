#!/usr/bin/env python3
"""Materialize the missing en_US master_arcs from the authoring frontier.

Reads artifacts/coordination/authoring_frontier_en_US.json (see
gen_authoring_frontier.py) and runs tools/arc_generator.generate_arc for every
need_arc cell, writing config/source_of_truth/master_arcs/<cell>.yaml. Deterministic;
no paid LLM. Motif text comes from the per-template motif_bank (author those first).

chapter_count defaults to the corpus-dominant value per structural format
(F006 -> 20, matching the existing 594-arc corpus).

  PYTHONPATH=. python3 scripts/catalog/fill_missing_arcs.py --dry-run
  PYTHONPATH=. python3 scripts/catalog/fill_missing_arcs.py
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))
from tools.arc_generator import generate_arc  # noqa: E402

ARCS = REPO / "config/source_of_truth/master_arcs"
TEMPLATES = ARCS / "templates"
FRONTIER = REPO / "artifacts/coordination/authoring_frontier_en_US.json"

# Corpus-dominant chapter_count per structural format (see existing master_arcs).
CHAPTER_COUNT_BY_FMT = {"F006": 20}
DEFAULT_CHAPTER_COUNT = 20


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--frontier", type=Path, default=FRONTIER)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--overwrite", action="store_true", help="Regenerate even if arc file exists")
    args = ap.parse_args()

    frontier = json.loads(args.frontier.read_text())
    cells = frontier["need_arc"]
    wrote = skipped = errors = 0
    for c in cells:
        persona, topic, engine, fmt = c["persona"], c["topic"], c["engine"], c["fmt"]
        template = c.get("template", "standard_escalation")
        out_path = ARCS / c["arc_file"]
        if out_path.exists() and not args.overwrite:
            skipped += 1
            continue
        cc = CHAPTER_COUNT_BY_FMT.get(fmt, DEFAULT_CHAPTER_COUNT)
        if args.dry_run:
            print(f"would gen {out_path.name}  template={template} cc={cc}")
            continue
        try:
            generate_arc(
                template_path=TEMPLATES / f"{template}.yaml",
                persona=persona, topic=topic, format_id=fmt,
                chapter_count=cc, engine=engine, out_path=out_path,
            )
            wrote += 1
        except Exception as e:
            print(f"ERROR {out_path.name}: {e}", file=sys.stderr)
            errors += 1
    print(f"wrote={wrote} skipped={skipped} errors={errors} total_cells={len(cells)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
