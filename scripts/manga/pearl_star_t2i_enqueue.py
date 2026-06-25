"""Enqueue manga panel render jobs onto Pearl Star Procrastinate queue."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

TaskName = Literal["t2i_flux_dev_h1a", "t2i_qwen_image", "t2i_flux_schnell"]

REPO_ROOT = Path(__file__).resolve().parents[2]


def queue_dsn_configured() -> bool:
    return bool(os.environ.get("PS_QUEUE_DSN", "").strip())


def pearl_star_dest_path(out_path: Path) -> str:
    """Map a local repo output path to the Pearl Star checkout path for queue workers."""
    repo = Path(os.environ.get("PS_PHOENIX_REPO", str(REPO_ROOT)))
    try:
        rel = out_path.resolve().relative_to(REPO_ROOT.resolve())
        return str((repo / rel).resolve())
    except ValueError:
        return str(out_path.resolve())


def enqueue_panel_job(
    *,
    task: TaskName,
    prompt: str,
    negative: str = "",
    width: int = 1080,
    height: int = 1920,
    seed: int = 42,
    panel_id: str = "",
    output_basename: str = "",
    dest_path: str = "",
    ssh_host: str = "pearl_star",
) -> dict[str, Any]:
    payload = {
        "prompt": prompt,
        "negative": negative,
        "width": width,
        "height": height,
        "seed": seed,
        "panel_id": panel_id,
        "output_basename": output_basename or panel_id,
        "dest_path": dest_path,
    }
    # Delegate to the canonical dispatch helper (RAP queue-first). This module
    # keeps its manga-specific signature + task picker + dest_path contract; the
    # local/SSH defer mechanic now lives once in scripts/pearl_star/dispatch.py.
    from scripts.pearl_star.dispatch import dispatch_gpu_job

    return dispatch_gpu_job("t2i", payload, task=task, ssh_host=ssh_host)


def pick_task_for_workflow(workflow_name: str) -> TaskName:
    low = workflow_name.lower()
    if "qwen" in low:
        return "t2i_qwen_image"
    if "schnell" in low:
        return "t2i_flux_schnell"
    return "t2i_flux_dev_h1a"
