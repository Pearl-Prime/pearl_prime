#!/usr/bin/env python3
"""Mark pipeline stages complete or failed (atomic job.json updates)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from scripts.pipeline._job_io import (
    iso_now,
    job_file,
    load_job,
    load_registry,
    normalize_job_stages,
    stage_index,
    write_job_atomic,
)


def mark_complete(
    workspace: Path | str,
    stage: str,
    *,
    output: str | None = None,
) -> None:
    ws = Path(workspace).resolve()
    job = load_job(ws)
    reg = load_registry()
    pipe = str(job.get("pipeline") or "")
    pipe_cfg = (reg.get("pipelines") or {}).get(pipe)
    if not pipe_cfg:
        raise ValueError(f"No registry entry for pipeline {pipe!r}")
    merged = normalize_job_stages(job, pipe_cfg)
    job["stages"] = merged
    i = stage_index(merged, stage)
    merged[i]["status"] = "pass"
    merged[i]["ts"] = iso_now()
    if output:
        merged[i]["output"] = output
    write_job_atomic(ws, job)


def mark_failed(
    workspace: Path | str,
    stage: str,
    *,
    error: str,
) -> None:
    ws = Path(workspace).resolve()
    if not job_file(ws).exists():
        return
    job = load_job(ws)
    reg = load_registry()
    pipe = str(job.get("pipeline") or "")
    pipe_cfg = (reg.get("pipelines") or {}).get(pipe)
    if not pipe_cfg:
        return
    merged = normalize_job_stages(job, pipe_cfg)
    job["stages"] = merged
    try:
        i = stage_index(merged, stage)
    except KeyError:
        return
    merged[i]["status"] = "fail"
    merged[i]["ts"] = iso_now()
    merged[i]["output"] = error[:500]
    write_job_atomic(ws, job)


def mark_pipeline_finished(workspace: Path | str, pipeline: str) -> None:
    """Mark every stage in the registry as pass (monolithic ebook/audiobook runs)."""
    ws = Path(workspace).resolve()
    job = load_job(ws)
    if str(job.get("pipeline")) != pipeline:
        return
    reg = load_registry()
    pipe_cfg = (reg.get("pipelines") or {}).get(pipeline)
    if not pipe_cfg:
        return
    merged = normalize_job_stages(job, pipe_cfg)
    now = iso_now()
    for st in merged:
        st["status"] = "pass"
        st["ts"] = now
    job["stages"] = merged
    write_job_atomic(ws, job)


def _cli() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    c1 = sub.add_parser("complete")
    c1.add_argument("--workspace", type=Path, required=True)
    c1.add_argument("--stage", required=True)
    c1.add_argument("--output", default=None)

    c2 = sub.add_parser("fail")
    c2.add_argument("--workspace", type=Path, required=True)
    c2.add_argument("--stage", required=True)
    c2.add_argument("--error", required=True)

    args = ap.parse_args()
    if args.cmd == "complete":
        mark_complete(args.workspace, args.stage, output=args.output)
        print("Marked pass:", args.stage)
        return 0
    if args.cmd == "fail":
        mark_failed(args.workspace, args.stage, error=args.error)
        print("Marked fail:", args.stage)
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(_cli())
