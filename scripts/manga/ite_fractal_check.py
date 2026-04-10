#!/usr/bin/env python3
"""ITE fractal regulation: box-counting FD estimates per panel image (ITE §7).

  PYTHONPATH=. python3 scripts/manga/ite_fractal_check.py --paths panel_paths.json \\
    [--chapter chapter.json] -o fractal_report.json [--force]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.ite_pipeline import load_ite_merged_config, run_fractal_check
from scripts.manga._config import should_skip_output, write_atomically


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE fractal dimension check")
    ap.add_argument("--paths", required=True, type=Path, help="JSON map panel_id -> image path")
    ap.add_argument("--chapter", type=Path, help="Optional chapter for categories / release gate")
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
        require_stage("ite_fractal", ws)

    if not args.paths.is_file():
        if not args.no_job_check:
            mark_failed(ws, "ite_fractal", error=f"missing {args.paths}")
        print(f"Not found: {args.paths}", file=sys.stderr)
        return 1

    if should_skip_output(args.out, ["artifact_type", "panels"], args.force):
        print(f"Skip (use --force): {args.out}")
        if not args.no_job_check:
            mark_complete(ws, "ite_fractal", output=args.out.name)
        return 0

    panel_paths = json.loads(args.paths.read_text(encoding="utf-8"))
    chapter = None
    if args.chapter and args.chapter.is_file():
        chapter = json.loads(args.chapter.read_text(encoding="utf-8"))
    cfg = load_ite_merged_config()
    out = run_fractal_check(panel_paths, chapter, cfg=cfg)
    write_atomically(args.out, out)
    print(f"Wrote fractal report ({len(out.get('panels') or [])} panels) to {args.out}")
    if out.get("stub_mode"):
        print("Note: stub mode (PIL/numpy unavailable)", file=sys.stderr)
    if not args.no_job_check:
        mark_complete(ws, "ite_fractal", output=args.out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
