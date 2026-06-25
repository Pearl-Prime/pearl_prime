#!/usr/bin/env python3
"""Defer one manga panel t2i job onto Pearl Star Procrastinate queue.

Used by queue_panel_renders.py --via-queue (local DSN or SSH wrapper in
pearl_star_t2i_enqueue.py). Prints one JSON line: {"job_id": ..., "task": ..., "via": ...}

Run on Pearl Star with PS_QUEUE_DSN set, or locally when DSN points at the queue.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKER_DIR = REPO_ROOT / "scripts" / "pearl_star" / "worker"

TASK_NAMES = frozenset({"t2i_flux_dev_h1a", "t2i_qwen_image", "t2i_flux_schnell"})


def defer_task(task: str, payload: dict[str, Any]) -> int:
    if task not in TASK_NAMES:
        raise ValueError(f"unknown task {task!r}; expected one of {sorted(TASK_NAMES)}")
    if str(WORKER_DIR) not in sys.path:
        sys.path.insert(0, str(WORKER_DIR))
    os.environ.setdefault("PROCRASTINATE_APP", "app.app")
    from app import app  # noqa: WPS433

    with app.open():
        job_id = app.tasks[task].defer(**payload)
    out = {"job_id": job_id, "task": task, "via": "procrastinate"}
    print(json.dumps(out))
    return int(job_id)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--task", required=True, choices=sorted(TASK_NAMES))
    ap.add_argument("--payload", required=True, help="JSON object with task kwargs")
    args = ap.parse_args(argv)
    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as e:
        print(f"invalid --payload JSON: {e}", file=sys.stderr)
        return 2
    if not isinstance(payload, dict):
        print("--payload must be a JSON object", file=sys.stderr)
        return 2
    try:
        defer_task(args.task, payload)
    except Exception as e:
        print(f"defer failed: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
