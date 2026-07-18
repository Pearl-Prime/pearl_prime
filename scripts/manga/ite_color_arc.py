#!/usr/bin/env python3
"""ITE color temperature arc: per-panel targets + FFmpeg colorbalance hints (ITE §6).

  PYTHONPATH=. python3 scripts/manga/ite_color_arc.py chapter.json \\
    [--panel-paths paths.json] -o color_arc.json [--force]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.ite_pipeline import build_color_arc, load_ite_merged_config
from scripts.manga._config import should_skip_output, write_atomically


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE color arc prescription")
    ap.add_argument("chapter_json", type=Path)
    ap.add_argument("--panel-paths", type=Path, help='JSON object {"panel_id": "path/to.png"}')
    ap.add_argument("-o", "--out", required=True, type=Path)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workspace", type=Path, default=None)
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = (args.workspace or args.out.parent).resolve()
    if not args.no_job_check:
        require_stage("ite_color_arc", ws)

    if not args.chapter_json.is_file():
        if not args.no_job_check:
            mark_failed(ws, "ite_color_arc", error=f"missing {args.chapter_json}")
        print(f"Not found: {args.chapter_json}", file=sys.stderr)
        return 1

    if should_skip_output(args.out, ["artifact_type", "panels"], args.force):
        print(f"Skip (use --force): {args.out}")
        if not args.no_job_check:
            mark_complete(ws, "ite_color_arc", output=args.out.name)
        return 0

    chapter = json.loads(args.chapter_json.read_text(encoding="utf-8"))
    paths = None
    if args.panel_paths and args.panel_paths.is_file():
        paths = json.loads(args.panel_paths.read_text(encoding="utf-8"))
    cfg = load_ite_merged_config()
    out = build_color_arc(chapter, paths, cfg=cfg)
    write_atomically(args.out, out)
    print(f"Wrote color arc for {len(out.get('panels') or [])} panels to {args.out}")
    if not args.no_job_check:
        mark_complete(ws, "ite_color_arc", output=args.out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
