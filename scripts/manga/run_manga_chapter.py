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
from phoenix_v4.manga.models.workspace_layout import resolve_chapter_workspace
from phoenix_v4.manga.runner.chapter_runner import (
    run_chapter_dag,
    run_chapter_dag_with_auto_revision,
)
from phoenix_v4.manga.runner.dag_order import RUN_ORDER
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
    ap.add_argument(
        "--chapter-id",
        help="Nested layout: workspace is series root; chapter at chapters/<id>/",
    )
    ap.add_argument(
        "--auto-revision",
        action="store_true",
        help="On QC hold, clear manifests from earliest implicated stage and retry",
    )
    ap.add_argument("--max-revision-rounds", type=int, default=3)
    ap.add_argument(
        "--no-sdf-stub",
        action="store_true",
        help="Omit sdf_conditioning placeholders on panel_prompts",
    )
    ap.add_argument("--style-id", default="dark_psychological")
    ap.add_argument("--teacher-id", default="ahjan")
    args = ap.parse_args()

    base = args.workspace.resolve()
    if not base.is_dir():
        print(f"Workspace not a directory: {base}", file=sys.stderr)
        return 1
    try:
        ws = resolve_chapter_workspace(base, chapter_id=args.chapter_id)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 1
    ws.mkdir(parents=True, exist_ok=True)

    if args.backend == "noop":
        backend = NoopImageBackend()
    else:
        if not args.replay_map or not args.replay_map.is_file():
            print("replay backend requires --replay-map", file=sys.stderr)
            return 1
        backend = FixtureReplayImageBackend.from_json_file(args.replay_map)

    snap = config_snapshot_hash()
    sdf_stub = not args.no_sdf_stub
    try:
        if args.auto_revision:
            ran, rounds = run_chapter_dag_with_auto_revision(
                ws,
                image_backend=backend,
                max_revision_rounds=args.max_revision_rounds,
                from_stage=args.from_stage,
                to_stage=args.to_stage,
                chapter_number=args.chapter_number,
                config_hash=snap,
                style_id=args.style_id,
                teacher_id=args.teacher_id,
                sdf_stub=sdf_stub,
            )
            print(f"Auto-revision rounds used: {rounds}")
        else:
            ran = run_chapter_dag(
                ws,
                image_backend=backend,
                from_stage=args.from_stage,
                to_stage=args.to_stage,
                chapter_number=args.chapter_number,
                config_hash=snap,
                style_id=args.style_id,
                teacher_id=args.teacher_id,
                sdf_stub=sdf_stub,
            )
    except Exception as e:
        print(f"DAG failed: {e}", file=sys.stderr)
        return 1

    print("Stages executed:", ", ".join(ran) or "(none — all skipped or empty range)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
