#!/usr/bin/env python3
"""Print human-readable pipeline job status."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.pipeline._job_io import (
    job_file,
    load_job,
    load_registry,
    normalize_job_stages,
    stages_from_registry,
)
from scripts.pipeline._paths import REPO_ROOT


def _next_stage(stages: list[dict], reg_stages: list[dict]) -> tuple[str | None, dict | None]:
    for i, st in enumerate(stages):
        rc = reg_stages[i] if i < len(reg_stages) else {}
        need = rc.get("required", True)
        if st.get("status") == "pass":
            continue
        if not need and st.get("status") is None:
            # skip optional until required blocker cleared
            continue
        return str(st.get("name")), rc
    return None, None


def _cmd_hint(stage_name: str | None, pipe_cfg: dict, job: dict) -> str:
    if not stage_name:
        return "(none — all required stages pass)"
    stages = stages_from_registry(pipe_cfg)
    script = ""
    for s in stages:
        if s.get("name") == stage_name:
            script = str(s.get("script") or "")
            break
    params = job.get("params") or {}
    ws = Path(job.get("workspace") or ".")
    extra = ""
    if stage_name == "shot_plan":
        extra = f" {ws}/script_segments.json -o {ws}/shot_plan.json"
    elif stage_name == "render":
        extra = f" {ws}/timeline.json -o {ws} ..."
    if script and script not in ("inline", "null", ""):
        return f"python3 {script}{extra}".replace(f"{REPO_ROOT}/", "")
    return f"(see docs + config/pipeline_registry.yaml for stage {stage_name})"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("workspace", type=Path)
    args = ap.parse_args()
    ws = args.workspace.resolve()
    if not job_file(ws).exists():
        print(f"No job.json in {ws}", file=sys.stderr)
        return 1
    job = load_job(ws)
    job["workspace"] = str(ws)
    reg = load_registry()
    pipe = str(job.get("pipeline") or "")
    pipe_cfg = (reg.get("pipelines") or {}).get(pipe, {})
    guide = str(job.get("guide_path") or pipe_cfg.get("guide") or "")
    merged = normalize_job_stages(job, pipe_cfg)
    reg_stages = stages_from_registry(pipe_cfg)
    params = job.get("params") or {}

    ga = "✓ acknowledged" if job.get("guide_acknowledged") else "✗ NOT acknowledged — run acknowledge_guide.py"
    print("=" * 64)
    print(f"JOB: {job.get('job_id')}")
    print(f"PIPELINE: {pipe} | TEACHER: {params.get('teacher', '—')} | TOPIC: {params.get('topic', '—')} | BRAND: {params.get('brand') or params.get('brand_id', '—')}")
    print(f"GUIDE: {ga}")
    print("=" * 64)
    for i, st in enumerate(merged):
        name = st.get("name")
        stat = st.get("status")
        out = st.get("output") or ""
        rc = reg_stages[i] if i < len(reg_stages) else {}
        opt = "" if rc.get("required", True) else " (optional)"
        if stat == "pass":
            mark = "✓"
            label = f"pass  → {out}" if out else "pass"
        elif stat == "fail":
            mark = "✗"
            label = f"fail  → {out}" if out else "fail"
        else:
            mark = "-"
            label = "not run"
        print(f"  {mark}  {i + 1:>2}. {name}{opt}  [{label}]")
    nxt, _ = _next_stage(merged, reg_stages)
    print("=" * 64)
    print(f"NEXT: Run stage {nxt!r}" if nxt else "NEXT: (done or optional stages remain)")
    print(f"CMD:  {_cmd_hint(nxt, pipe_cfg, job)}")
    print(f"GUIDE: {REPO_ROOT / guide}")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
