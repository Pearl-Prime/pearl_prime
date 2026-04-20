#!/usr/bin/env python3
"""ITE QC: gates T-01–T-20 + ITE_score (ITE §15).

  PYTHONPATH=. python3 scripts/manga/ite_qc.py \\
    --chapter chapter_gutter.json \\
    --color-arc color_arc.json \\
    --fractal fractal_report.json \\
    --breath chapter_breath.json \\
    [-o ite_qc_report.json] [--force]

Workspace shorthand (fills paths under ``<workspace>/debug/ite/``):

  PYTHONPATH=. python3 scripts/manga/ite_qc.py --workspace artifacts/manga/my_run/

Uses ``chapter_gutter.json``, ``color_arc.json``, ``fractal_report.json``,
``chapter_breath.json`` when present, writes ``ite_qc_report.json`` next to them.
If ``job.json`` is missing under the workspace, the pipeline job gate is skipped
with a note (same effect as ``--no-job-check`` for that case only).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.ite_pipeline import load_ite_merged_config, run_ite_qc
from scripts.manga._config import should_skip_output, write_atomically


def _load(p: Path | None) -> dict | None:
    if p is None or not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _apply_workspace_defaults(ws: Path, args: argparse.Namespace) -> None:
    """Resolve optional ITE artifact paths from a manga chapter workspace."""
    ite = (ws / "debug" / "ite").resolve()
    if args.chapter is None:
        args.chapter = ite / "chapter_gutter.json"
    if args.color_arc is None:
        p = ite / "color_arc.json"
        if p.is_file():
            args.color_arc = p
    if args.fractal is None:
        p = ite / "fractal_report.json"
        if p.is_file():
            args.fractal = p
    if args.breath is None:
        p = ite / "chapter_breath.json"
        if p.is_file():
            args.breath = p
    if args.soundtrack is None:
        p = ite / "soundtrack.json"
        if p.is_file():
            args.soundtrack = p
    if args.animation_plan is None:
        p = ite / "animation_plan.json"
        if p.is_file():
            args.animation_plan = p


def main() -> int:
    ap = argparse.ArgumentParser(description="ITE therapeutic QC gates")
    ap.add_argument(
        "--chapter",
        type=Path,
        default=None,
        help="Gutter-enriched chapter JSON (default: <workspace>/debug/ite/chapter_gutter.json when --workspace is set)",
    )
    ap.add_argument("--color-arc", type=Path, default=None)
    ap.add_argument("--fractal", type=Path, default=None)
    ap.add_argument("--breath", type=Path, default=None)
    ap.add_argument("--soundtrack", type=Path, default=None)
    ap.add_argument("--animation-plan", type=Path, default=None)
    ap.add_argument("--sabido", type=Path, help="Optional sabido_map JSON")
    ap.add_argument("-o", "--out", type=Path, default=None)
    ap.add_argument("--force", action="store_true")
    ap.add_argument(
        "--workspace",
        type=Path,
        default=None,
        help="Manga chapter workspace root; default ITE inputs from debug/ite/, default -o to debug/ite/ite_qc_report.json",
    )
    ap.add_argument(
        "--no-job-check",
        dest="no_job_check",
        action="store_true",
        help="Skip job.json enforcement (CI only)",
    )
    args = ap.parse_args()

    out_path = args.out
    if args.workspace is not None:
        ws_root = args.workspace.resolve()
        _apply_workspace_defaults(ws_root, args)
        if out_path is None:
            out_path = ws_root / "debug" / "ite" / "ite_qc_report.json"
    else:
        ws_root = None
        if out_path is None:
            out_path = Path("ite_qc_report.json")

    out_path = Path(out_path).resolve()
    ws = ws_root if ws_root is not None else out_path.parent

    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage
    from scripts.pipeline._job_io import job_file

    if not args.no_job_check and args.workspace is not None and not job_file(ws).is_file():
        print(
            "NOTE: ite_qc: no job.json under workspace; skipping pipeline job gate.",
            file=sys.stderr,
        )
        args.no_job_check = True

    if not args.no_job_check:
        require_stage("ite_qc", ws)

    if args.chapter is None or not args.chapter.is_file():
        if not args.no_job_check:
            mark_failed(ws, "ite_qc", error=f"missing {args.chapter}")
        print(
            "Not found: chapter gutter JSON. Pass --chapter or --workspace with "
            "debug/ite/chapter_gutter.json present.",
            file=sys.stderr,
        )
        return 1

    ch = _load(args.chapter)
    assert ch is not None

    if should_skip_output(
        out_path, ["gates", "ITE_score", "artifact_type"], args.force
    ):
        print(f"Skip (use --force): {out_path}")
        if not args.no_job_check:
            mark_complete(ws, "ite_qc", output=out_path.name)
        return 0

    cfg = load_ite_merged_config()
    sabido = _load(args.sabido)
    report = run_ite_qc(
        chapter_enriched=ch,
        color_arc=_load(args.color_arc),
        fractal_report=_load(args.fractal),
        breath_doc=_load(args.breath),
        soundtrack=_load(args.soundtrack),
        animation_plan=_load(args.animation_plan),
        sabido_map=sabido,
        cfg=cfg,
    )
    write_atomically(out_path, report)
    print(f"ITE_score={report.get('ITE_score')} passed={report.get('passed')}")
    ok = bool(report.get("passed"))
    if not args.no_job_check:
        if ok:
            mark_complete(ws, "ite_qc", output=out_path.name)
        else:
            mark_failed(ws, "ite_qc", error="QC gates failed")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
