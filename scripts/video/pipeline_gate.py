#!/usr/bin/env python3
"""Video pipeline validation hook — prefer unified job enforcement (scripts/pipeline/check_job.py).

This module exists so config/pipeline_registry.yaml can reference a video gate script.
Full stage order and policies: docs/VIDEO_PIPELINE_COMPLETE_GUIDE.md + docs/VIDEO_PIPELINE_SPEC.md
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Video pipeline gate — delegates to unified job system when --workspace is set.",
    )
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument(
        "--stage",
        default="render",
        help="Stage name as in config/pipeline_registry.yaml (video pipeline)",
    )
    args = ap.parse_args()
    from scripts.pipeline.check_job import require_stage

    require_stage(args.stage, args.workspace)
    print("OK: video pipeline gate (job + stage order) satisfied for stage", args.stage)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
