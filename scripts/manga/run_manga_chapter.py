#!/usr/bin/env python3
"""Resumable manga chapter DAG (replay/noop image backend, no live LLM).

  PYTHONPATH=. python3 scripts/manga/run_manga_chapter.py --workspace DIR \\
    [--backend replay --replay-map map.json] [--from-stage ID] [--to-stage ID]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.image_backend import FixtureReplayImageBackend, NoopImageBackend
from phoenix_v4.manga.runner.chapter_runner import RUN_ORDER, run_chapter_dag
from scripts.manga._config import config_snapshot_hash


def main() -> int:
    ap = argparse.ArgumentParser(description="Run manga chapter pipeline stages (resumable).")
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--backend", choices=("noop", "replay"), default="replay")
    ap.add_argument("--replay-map", type=Path, help="panel_id → relative PNG (replay backend)")
    ap.add_argument(
        "--from-stage",
        help=f"One of: {', '.join(RUN_ORDER)}",
    )
    ap.add_argument("--to-stage", help=f"One of: {', '.join(RUN_ORDER)}")
    ap.add_argument("--chapter-number", type=int, default=1)
    ap.add_argument("--style-id", default="dark_psychological")
    ap.add_argument("--teacher-id", default="ahjan")
    args = ap.parse_args()

    ws = args.workspace.resolve()
    if not ws.is_dir():
        print(f"Workspace not a directory: {ws}", file=sys.stderr)
        return 1

    if args.backend == "noop":
        backend = NoopImageBackend()
    else:
        if not args.replay_map or not args.replay_map.is_file():
            print("replay backend requires --replay-map", file=sys.stderr)
            return 1
        backend = FixtureReplayImageBackend.from_json_file(args.replay_map)

    snap = config_snapshot_hash()
    try:
        ran = run_chapter_dag(
            ws,
            image_backend=backend,
            from_stage=args.from_stage,
            to_stage=args.to_stage,
            chapter_number=args.chapter_number,
            config_hash=snap,
            style_id=args.style_id,
            teacher_id=args.teacher_id,
        )
    except Exception as e:
        print(f"DAG failed: {e}", file=sys.stderr)
        return 1

    print("Stages executed:", ", ".join(ran) or "(none — all skipped or empty range)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
