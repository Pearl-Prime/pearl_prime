#!/usr/bin/env python3
"""Pipeline job enforcement — import require_stage() at top of every stage script."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.pipeline._job_io import (
    job_file,
    load_job,
    load_registry,
    normalize_job_stages,
    stage_index,
    stages_from_registry,
)
from scripts.pipeline._paths import REPO_ROOT


def _stage_line(st: dict, registry_stage: dict) -> str:
    name = st.get("name", "?")
    status = st.get("status")
    out = st.get("output") or ""
    req = registry_stage.get("required", True)
    mark = "✓" if status == "pass" else ("✗" if status == "fail" else "-")
    snip = f" → {out}" if out else ""
    rflag = "" if req else " (optional)"
    st_label = "pass" if status == "pass" else ("fail" if status == "fail" else "not run")
    return f"  {mark}  {name}{rflag}  [{st_label}]{snip}"


def require_stage(stage_name: str, workspace: Path | str) -> dict:
    """Validate job.json and stage order; exit 1 with actionable errors or return job dict."""
    ws = Path(workspace).resolve()
    jpath = job_file(ws)
    if not jpath.exists():
        print("=" * 64, file=sys.stderr)
        print("PIPELINE JOB: BLOCKED — no job.json", file=sys.stderr)
        print(f"Expected: {jpath}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Create a job first, then acknowledge the guide:", file=sys.stderr)
        print(
            f"  PYTHONPATH=. python3 scripts/pipeline/create_job.py --pipeline <video|ebook|manga|podcast|audiobook> \\",
            file=sys.stderr,
        )
        print(f"    ... required flags ... --workspace {ws}", file=sys.stderr)
        print(
            f"  PYTHONPATH=. python3 scripts/pipeline/acknowledge_guide.py --workspace {ws}",
            file=sys.stderr,
        )
        print("", file=sys.stderr)
        print("Registry (stage order): config/pipeline_registry.yaml", file=sys.stderr)
        print("=" * 64, file=sys.stderr)
        raise SystemExit(1)

    job = load_job(ws)
    pipeline = str(job.get("pipeline") or "")
    if not pipeline:
        print("job.json missing 'pipeline' field.", file=sys.stderr)
        raise SystemExit(1)

    reg = load_registry()
    pipe_cfg = (reg.get("pipelines") or {}).get(pipeline)
    if not pipe_cfg:
        print(f"Unknown pipeline in job.json: {pipeline}", file=sys.stderr)
        raise SystemExit(1)

    guide = str(job.get("guide_path") or pipe_cfg.get("guide") or "")
    if not job.get("guide_acknowledged"):
        print("=" * 64, file=sys.stderr)
        print("PIPELINE JOB: BLOCKED — guide not acknowledged", file=sys.stderr)
        print(f"Read: {REPO_ROOT / guide}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Then run:", file=sys.stderr)
        print(f"  PYTHONPATH=. python3 scripts/pipeline/acknowledge_guide.py --workspace {ws}", file=sys.stderr)
        print("=" * 64, file=sys.stderr)
        raise SystemExit(1)

    reg_stages = stages_from_registry(pipe_cfg)
    merged = normalize_job_stages(job, pipe_cfg)
    job["stages"] = merged

    try:
        idx = stage_index(merged, stage_name)
    except KeyError:
        print(f"Stage '{stage_name}' is not defined for pipeline '{pipeline}'.", file=sys.stderr)
        print(f"See config/pipeline_registry.yaml → pipelines.{pipeline}.stages", file=sys.stderr)
        raise SystemExit(1)

    # Prerequisites: all prior required stages must be pass
    blockers: list[str] = []
    for i in range(idx):
        prev = merged[i]
        rcfg = reg_stages[i] if i < len(reg_stages) else {}
        if not rcfg.get("required", True):
            continue
        st = prev.get("status")
        if st != "pass":
            nm = prev.get("name", "?")
            blockers.append(
                f"stage '{nm}' has not passed (status={st!r}; run earlier stages first)"
            )

    if blockers:
        print("=" * 64, file=sys.stderr)
        print(f"PIPELINE JOB: BLOCKED — cannot run stage {stage_name!r}", file=sys.stderr)
        print("", file=sys.stderr)
        for b in blockers:
            print(f"  • {b}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Current stages:", file=sys.stderr)
        for i, st in enumerate(merged):
            rc = reg_stages[i] if i < len(reg_stages) else {}
            print(_stage_line(st, rc), file=sys.stderr)
        print("", file=sys.stderr)
        print(f"GUIDE: {REPO_ROOT / guide}", file=sys.stderr)
        print("", file=sys.stderr)
        print("Human-readable status:", file=sys.stderr)
        print(f"  PYTHONPATH=. python3 scripts/pipeline/job_status.py {ws}", file=sys.stderr)
        print("=" * 64, file=sys.stderr)
        raise SystemExit(1)

    return job


def _cli() -> int:
    ap = argparse.ArgumentParser(description="Verify a pipeline stage is allowed for job.json")
    ap.add_argument("--stage", required=True)
    ap.add_argument("--workspace", type=Path, required=True)
    args = ap.parse_args()
    require_stage(args.stage, args.workspace)
    print("OK: stage allowed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(_cli())
