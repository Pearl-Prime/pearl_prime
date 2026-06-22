"""Enqueue manga panel render jobs onto Pearl Star Procrastinate queue."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Literal

TaskName = Literal["t2i_flux_dev_h1a", "t2i_qwen_image", "t2i_flux_schnell"]

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFER_CLI = REPO_ROOT / "scripts" / "manga" / "defer_panel_job_cli.py"


def queue_dsn_configured() -> bool:
    return bool(os.environ.get("PS_QUEUE_DSN", "").strip())


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
    }
    if queue_dsn_configured():
        return _run_defer_cli(task, payload, local=True)
    return _run_defer_cli(task, payload, local=False, ssh_host=ssh_host)


def _run_defer_cli(
    task: TaskName,
    payload: dict[str, Any],
    *,
    local: bool,
    ssh_host: str = "pearl_star",
) -> dict[str, Any]:
    payload_json = json.dumps(payload)
    repo = os.environ.get("PS_PHOENIX_REPO", str(REPO_ROOT))
    if local:
        cmd = ["python3", str(DEFER_CLI), "--task", task, "--payload", payload_json]
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=60, env=os.environ.copy())
    else:
        inner = json.dumps(payload_json)
        remote = (
            f"cd {repo} && set -a && . /etc/pearl-star/queue.env 2>/dev/null; set +a && "
            f"python3 scripts/manga/defer_panel_job_cli.py --task {task} --payload {inner}"
        )
        r = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", ssh_host, remote],
            capture_output=True,
            text=True,
            timeout=90,
        )
    if r.returncode != 0:
        raise RuntimeError(f"enqueue failed: {r.stderr.strip() or r.stdout}")
    line = r.stdout.strip().splitlines()[-1]
    result = json.loads(line)
    result["via"] = "local" if local else f"ssh:{ssh_host}"
    return result


def pick_task_for_workflow(workflow_name: str) -> TaskName:
    low = workflow_name.lower()
    if "qwen" in low:
        return "t2i_qwen_image"
    if "schnell" in low:
        return "t2i_flux_schnell"
    return "t2i_flux_dev_h1a"
