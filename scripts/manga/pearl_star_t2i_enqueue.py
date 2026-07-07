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
    """Map panel output to a pearl-star-writable path on Pearl Star (PS_MANGA_OUT_ROOT)."""
    from scripts.pearl_star.manga_panel_paths import pearl_star_dest_path as _writable

    return _writable(out_path)


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
    out_path: str | Path = "",
    ssh_host: str = "pearl_star",
) -> dict[str, Any]:
    """Enqueue one t2i panel job (RAP queue-first).

  *out_path* — repo-relative or absolute panel PNG path; mapped to Pearl
  Star–writable *dest_path* via ``pearl_star_dest_path``.  RESUME_COMMANDS.sh
  and bank-contract snippets use this kwarg.  Explicit *dest_path* wins when both
  are set.
    """
    resolved_dest = dest_path
    if not resolved_dest and out_path:
        resolved_dest = pearl_star_dest_path(Path(out_path))
    payload = {
        "prompt": prompt,
        "negative": negative,
        "width": width,
        "height": height,
        "seed": seed,
        "panel_id": panel_id,
        "output_basename": output_basename or panel_id,
        "dest_path": resolved_dest,
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
