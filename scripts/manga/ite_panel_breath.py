#!/usr/bin/env python3
"""Panel Breath Engine: annotate chapter JSON with breath_sequence phases (ITE §5).

  PYTHONPATH=. python3 scripts/manga/ite_panel_breath.py chapter.json -o out.json [--force]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.ite_pipeline import annotate_panel_breath, load_ite_merged_config
from scripts.manga._config import should_skip_output, write_atomically


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE panel breath annotation")
    ap.add_argument("chapter_json", type=Path, help="Chapter or writer handoff JSON")
    ap.add_argument("-o", "--out", required=True, type=Path)
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    if not args.chapter_json.is_file():
        print(f"Not found: {args.chapter_json}", file=sys.stderr)
        return 1

    if should_skip_output(args.out, ["breath_sequences", "pages"], args.force):
        print(f"Skip (use --force): {args.out}")
        return 0

    chapter = json.loads(args.chapter_json.read_text(encoding="utf-8"))
    cfg = load_ite_merged_config()
    out = annotate_panel_breath(chapter, cfg=cfg)
    write_atomically(args.out, out)
    print(f"Wrote {len(out.get('breath_sequences') or [])} breath sequence(s) to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
