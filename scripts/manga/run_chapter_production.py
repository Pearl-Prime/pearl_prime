#!/usr/bin/env python3
"""Full chapter production path: prompts, manifest, lettering, optional page PNGs.

  PYTHONPATH=. python3 scripts/manga/run_chapter_production.py chapter_script.json \\
    --workspace /path/to/chapter_root \\
    [--backend noop|replay] [--replay-map map.json] [--compose-pages]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.chapter.chapter_production import produce_chapter_assets
from phoenix_v4.manga.image_backend import FixtureReplayImageBackend, NoopImageBackend
from phoenix_v4.manga.models import paths as manga_paths
from scripts.manga._config import config_snapshot_hash, write_atomically


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Chapter script → panel_prompts, manifest, lettering_spec, optional composites"
    )
    ap.add_argument("chapter_script", type=Path, help="chapter_script_writer_handoff JSON")
    ap.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="Chapter workspace root (writes canonical filenames here)",
    )
    ap.add_argument("--backend", choices=("noop", "replay"), default="noop")
    ap.add_argument("--replay-map", type=Path, help="panel_id → relative PNG path (replay backend)")
    ap.add_argument(
        "--compose-pages",
        action="store_true",
        help="Write final_page_composite/page_NNN.png (requires Pillow + ok panel paths)",
    )
    ap.add_argument("--style-id", default="dark_psychological")
    ap.add_argument("--teacher-id", default="ahjan")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = args.workspace.resolve()
    ws.mkdir(parents=True, exist_ok=True)
    if not args.no_job_check:
        require_stage("chapter_production", ws)

    path = args.chapter_script
    if not path.exists():
        if not args.no_job_check:
            mark_failed(ws, "chapter_production", error=f"missing {path}")
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1
    raw = json.loads(path.read_text(encoding="utf-8"))

    if args.backend == "noop":
        backend = NoopImageBackend()
    else:
        if not args.replay_map or not args.replay_map.exists():
            print("--replay-map required for replay backend", file=sys.stderr)
            return 1
        backend = FixtureReplayImageBackend.from_json_file(args.replay_map)
    snap = config_snapshot_hash()

    final_out = None
    if args.compose_pages:
        final_out = ws / manga_paths.FINAL_PAGE_COMPOSITE_DIR
        if args.backend == "noop":
            if not args.no_job_check:
                mark_failed(ws, "chapter_production", error="compose-pages needs replay backend")
            print("compose-pages needs replay backend with real PNG paths", file=sys.stderr)
            return 1

    try:
        bundle = produce_chapter_assets(
            raw,
            image_backend=backend,
            config_hash=snap,
            style_id=args.style_id,
            teacher_id=args.teacher_id,
            final_pages_out=final_out,
        )
    except Exception as e:
        if not args.no_job_check:
            mark_failed(ws, "chapter_production", error=str(e))
        print(f"Production failed: {e}", file=sys.stderr)
        return 1

    write_atomically(ws / manga_paths.PANEL_PROMPTS, bundle["panel_prompts"])
    write_atomically(ws / manga_paths.PANEL_IMAGES_MANIFEST, bundle["panel_images_manifest"])
    write_atomically(ws / manga_paths.LETTERING_SPEC, bundle["lettering_spec"])
    print(
        f"Wrote panel_prompts, panel_images_manifest, lettering_spec under {ws}"
    )
    if final_out and bundle.get("final_page_paths"):
        for p in bundle["final_page_paths"]:
            print(f"  page composite: {p}")
    if not args.no_job_check:
        mark_complete(ws, "chapter_production", output="panel_prompts.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
