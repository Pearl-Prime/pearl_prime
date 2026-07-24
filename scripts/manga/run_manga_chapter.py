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

import json

from phoenix_v4.manga.image_backend import (
    FixtureReplayImageBackend,
    NoopImageBackend,
    RunComfyImageBackend,
)
from phoenix_v4.manga.models.workspace_layout import resolve_chapter_workspace
from phoenix_v4.manga.runner.chapter_runner import (
    _resolve_chapter_genre,
    run_chapter_dag,
    run_chapter_dag_with_auto_revision,
)
from phoenix_v4.manga.runner.dag_order import RUN_ORDER
from phoenix_v4.manga.style_resolution import resolve_style_id
from scripts.manga._config import config_snapshot_hash


def _ensure_chapter_request(ws: Path, chapter_number: int) -> None:
    """Auto-create chapter_request.json from series handoff if missing."""
    cr_path = ws / "chapter_request.json"
    if cr_path.is_file():
        return
    handoff = ws / "series" / "story_architecture_handoff.json"
    if not handoff.is_file():
        # Try parent directory (flat workspace)
        handoff = ws.parent / "series" / "story_architecture_handoff.json"
    if not handoff.is_file():
        return
    data = json.loads(handoff.read_text(encoding="utf-8"))
    cr = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_request",
        "series_id": data.get("series_id", "unknown"),
        "chapter_id": f"ch_{chapter_number}",
        "arc_id": data.get("arc_id", "arc_1"),
    }
    cr_path.write_text(json.dumps(cr, indent=2) + "\n", encoding="utf-8")
    print(f"Auto-created {cr_path}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Run manga chapter pipeline stages (resumable).")
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--backend", choices=("noop", "replay", "runcomfy"), default="replay")
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
        "--runcomfy-deployment",
        default=None,
        help="RunComfy deployment ID (default: env RUNCOMFY_DEPLOYMENT_ID or 677edba8-ace0-4b2b-bad2-8e94b9959065)",
    )
    ap.add_argument(
        "--runcomfy-workflow",
        type=Path,
        default=None,
        help="Path to ComfyUI workflow JSON (default: bundled flux_video_bank.json)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Compile prompts only, skip API calls (runcomfy backend)")
    ap.add_argument(
        "--no-sdf-stub",
        action="store_true",
        help="Omit sdf_conditioning placeholders on panel_prompts",
    )
    ap.add_argument(
        "--style-id",
        default=None,
        help="Explicit style archetype id. Omit to resolve via the authority "
        "chain in phoenix_v4.manga.style_resolution (genre/teacher/format "
        "signal, falling back to grounded_realism).",
    )
    ap.add_argument("--teacher-id", default="ahjan")
    ap.add_argument("--export-pdf", action="store_true", help="Assemble page PNGs into a manga PDF after DAG completes")
    args = ap.parse_args()

    base = args.workspace.resolve()
    if not base.is_dir():
        print(f"Workspace not a directory: {base}", file=sys.stderr)
        return 1
    # Auto-create chapter_request.json if series setup exists but chapter request doesn't
    _ensure_chapter_request(base, args.chapter_number)
    try:
        ws = resolve_chapter_workspace(base, chapter_id=args.chapter_id)
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 1
    ws.mkdir(parents=True, exist_ok=True)

    if args.backend == "noop":
        backend = NoopImageBackend()
    elif args.backend == "runcomfy":
        backend = RunComfyImageBackend(
            deployment_id=args.runcomfy_deployment,
            workflow_path=args.runcomfy_workflow,
            output_dir=ws / "panel_images",
            dry_run=args.dry_run,
        )
    else:
        if not args.replay_map or not args.replay_map.is_file():
            print("replay backend requires --replay-map", file=sys.stderr)
            return 1
        backend = FixtureReplayImageBackend.from_json_file(args.replay_map)

    snap = config_snapshot_hash()
    sdf_stub = not args.no_sdf_stub

    resolved_style_id, style_source = resolve_style_id(
        explicit_override=args.style_id,
        teacher_id=args.teacher_id,
        genre_id=_resolve_chapter_genre(ws),
    )
    print(f"style_id={resolved_style_id} (source={style_source})", file=sys.stderr)

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
                style_id=resolved_style_id,
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
                style_id=resolved_style_id,
                teacher_id=args.teacher_id,
                sdf_stub=sdf_stub,
            )
    except Exception as e:
        print(f"DAG failed: {e}", file=sys.stderr)
        return 1

    print("Stages executed:", ", ".join(ran) or "(none — all skipped or empty range)")

    # ── PDF export ──
    if args.export_pdf:
        _export_pdf(ws)

    return 0


def _export_pdf(ws: Path) -> None:
    """Assemble final_page_composite PNGs into a single manga PDF."""
    composite_dir = ws / "final_page_composite"
    pages = sorted(composite_dir.glob("page_*.png"))
    if not pages:
        print("No page PNGs found for PDF export", file=sys.stderr)
        return
    try:
        from PIL import Image
    except ImportError:
        print("Pillow required for PDF export: pip install Pillow", file=sys.stderr)
        return
    images = [Image.open(p).convert("RGB") for p in pages]
    pdf_path = ws / "manga.pdf"
    if len(images) == 1:
        images[0].save(pdf_path, format="PDF")
    else:
        images[0].save(pdf_path, format="PDF", save_all=True, append_images=images[1:])
    for img in images:
        img.close()
    print(f"Exported manga PDF: {pdf_path} ({len(pages)} pages)")


if __name__ == "__main__":
    raise SystemExit(main())
