#!/usr/bin/env python3
"""Set guide_acknowledged=true after printing a short summary of the pipeline guide."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scripts.pipeline._job_io import job_file, load_job, load_registry, write_job_atomic
from scripts.pipeline._paths import REPO_ROOT


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workspace", type=Path, required=True)
    args = ap.parse_args()
    ws = args.workspace.resolve()
    jf = job_file(ws)
    if not jf.exists():
        print(f"No job.json at {jf}", file=sys.stderr)
        return 1
    job = load_job(ws)
    pipeline = str(job.get("pipeline") or "")
    reg = load_registry()
    pipe_cfg = (reg.get("pipelines") or {}).get(pipeline, {})
    guide_rel = str(job.get("guide_path") or pipe_cfg.get("guide") or "")
    gpath = REPO_ROOT / guide_rel
    print("=" * 64)
    print(f"PIPELINE: {pipeline}")
    print(f"GUIDE: {gpath}")
    print("=" * 64)
    if gpath.is_file():
        lines = gpath.read_text(encoding="utf-8", errors="replace").splitlines()
        # Summary: before-you-start + first sections
        preview: list[str] = []
        for line in lines[:120]:
            preview.append(line)
        print("\n".join(preview))
        if len(lines) > 120:
            print(f"\n… ({len(lines) - 120} more lines in guide) …")
    else:
        print("(Guide file not found; acknowledge anyway for dev workspaces.)")
    print("=" * 64)
    print("KEY RULES:")
    print("  • Do not skip stages — follow config/pipeline_registry.yaml order.")
    print("  • Use repo scripts under scripts/ only; do not hand-roll FFmpeg/TTS for production.")
    print("  • Voice, pacing, and assets come from config/video/, config/tts/, and governed YAML.")
    print("=" * 64)

    job["guide_acknowledged"] = True
    if guide_rel and not job.get("guide_path"):
        job["guide_path"] = guide_rel
    write_job_atomic(ws, job)
    print("guide_acknowledged set to true in job.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
