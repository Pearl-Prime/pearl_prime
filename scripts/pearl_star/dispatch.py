"""Canonical Pearl Star GPU/LLM dispatch helper (RAP queue-first).

Single import point for any production caller that needs to run a >10 s job on
Pearl Star (Robust Agent Protocol — ``docs/ROBUST_AGENT_PROTOCOL.md``). Routes
every dispatch through the Procrastinate queue (spec
``docs/specs/PEARL_STAR_JOB_QUEUE_V1_SPEC.md`` §4.2/§4.7) instead of letting
callers hit the ComfyUI HTTP API directly or shell out to ``ollama run``.

Why this exists (NEW-ARTIFACT-JUSTIFIED): the proven local/SSH defer mechanic
lived only inside ``scripts/manga/pearl_star_t2i_enqueue.py`` (manga panels).
Five-plus call sites had copied the subprocess-to-``defer_panel_job_cli.py``
shape. This module dedupes that into one ``dispatch_gpu_job`` API keyed by the
four canonical workload queues (t2i / tts / llm / orch, spec §3) so new callers
import it instead of re-plumbing — and so the RAP compliance check has a single
sanctioned dispatch surface to recognize.

Usage (queue-first; never call ComfyUI/Ollama directly for >10 s work):

    from scripts.pearl_star.dispatch import dispatch_gpu_job

    job = dispatch_gpu_job(
        job_class="t2i",
        task="t2i_flux_dev_h1a",
        payload={"prompt": "...", "width": 1080, "height": 1920, "seed": 42},
    )
    print(job["job_id"])

Tier policy: stdlib + subprocess to the on-box ``defer_panel_job_cli.py``. No
paid LLM API (CLAUDE.md). When ``PS_QUEUE_DSN`` is set the defer runs locally;
otherwise it is shipped over SSH to ``PS_QUEUE_SSH_HOST`` (default ``pearl_star``).
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFER_CLI = REPO_ROOT / "scripts" / "manga" / "defer_panel_job_cli.py"
# Procrastinate is NOT installed on Pearl Star's system python3; the defer CLI
# must run under the on-box venv python (or an env override). System python3 is
# the fallback only when neither is present (e.g. local dev with DSN set).
DEFAULT_PS_PY = Path("/opt/pearl-star/venv/bin/python")


def queue_python() -> str:
    """Python interpreter that has procrastinate (Pearl Star venv, or env override)."""
    for key in ("PS_PY", "PS_QUEUE_PYTHON"):
        v = os.environ.get(key, "").strip()
        if v:
            return v
    if DEFAULT_PS_PY.is_file():
        return str(DEFAULT_PS_PY)
    return "python3"

# Canonical workload queues (spec §3 / §4.1). GPU-heavy queues run
# concurrency=1 to realize the shared GPU-lock (spec §4.7).
JOB_CLASSES: frozenset[str] = frozenset({"t2i", "tts", "llm", "orch"})

# Task names registered on the Procrastinate app today (worker/app.py). Kept in
# sync with the worker registry; a task not in this set is rejected before any
# subprocess fires so a typo never silently no-ops.
KNOWN_TASKS: dict[str, str] = {
    # task name -> job_class (queue)
    "t2i_flux_schnell": "t2i",
    "t2i_flux_dev_h1a": "t2i",
    "t2i_qwen_image": "t2i",
}


class DispatchError(RuntimeError):
    """Raised when a dispatch could not be enqueued onto the queue."""


def queue_dsn_configured() -> bool:
    """True when a local Procrastinate DSN is available (no SSH needed)."""
    return bool(os.environ.get("PS_QUEUE_DSN", "").strip())


def dispatch_gpu_job(
    job_class: str,
    payload: dict[str, Any],
    *,
    task: str | None = None,
    priority: int = 5,
    ssh_host: str | None = None,
) -> dict[str, Any]:
    """Enqueue one Pearl Star GPU/LLM job onto the Procrastinate queue.

    Parameters
    ----------
    job_class:
        One of the four canonical workload queues (``t2i``/``tts``/``llm``/``orch``).
    payload:
        JSON-serializable task kwargs (prompt, dims, seed, etc.).
    task:
        Procrastinate task name. Defaults to the sole task registered for the
        class when unambiguous (today: ``t2i`` -> ``t2i_flux_dev_h1a``).
    priority:
        Advisory priority (0-9, higher = sooner) carried in the payload for the
        worker/scheduler. Does not change queue concurrency caps.
    ssh_host:
        Override the SSH host used when ``PS_QUEUE_DSN`` is unset. Defaults to
        ``PS_QUEUE_SSH_HOST`` env or ``pearl_star``.

    Returns a dict ``{"job_id", "task", "via"}``.
    """
    if job_class not in JOB_CLASSES:
        raise ValueError(
            f"unknown job_class {job_class!r}; expected one of {sorted(JOB_CLASSES)}"
        )
    if not isinstance(payload, dict):
        raise TypeError("payload must be a dict of task kwargs")
    if not 0 <= int(priority) <= 9:
        raise ValueError("priority must be in 0..9")

    resolved = _resolve_task(job_class, task)
    full_payload = dict(payload)
    full_payload.setdefault("priority", int(priority))

    host = ssh_host or os.environ.get("PS_QUEUE_SSH_HOST", "pearl_star")
    if queue_dsn_configured():
        return _run_defer_cli(resolved, full_payload, local=True)
    return _run_defer_cli(resolved, full_payload, local=False, ssh_host=host)


def _resolve_task(job_class: str, task: str | None) -> str:
    if task is not None:
        expected = KNOWN_TASKS.get(task)
        if expected is None:
            raise ValueError(
                f"unknown task {task!r}; known tasks: {sorted(KNOWN_TASKS)}"
            )
        if expected != job_class:
            raise ValueError(
                f"task {task!r} belongs to job_class {expected!r}, not {job_class!r}"
            )
        return task
    candidates = [t for t, c in KNOWN_TASKS.items() if c == job_class]
    if len(candidates) == 1:
        return candidates[0]
    raise ValueError(
        f"job_class {job_class!r} has {len(candidates)} registered tasks "
        f"({sorted(candidates)}); pass task=... explicitly"
    )


def _run_defer_cli(
    task: str,
    payload: dict[str, Any],
    *,
    local: bool,
    ssh_host: str = "pearl_star",
) -> dict[str, Any]:
    payload_json = json.dumps(payload)
    repo = os.environ.get("PS_PHOENIX_REPO", str(REPO_ROOT))
    py = queue_python()
    if local:
        cmd = [py, str(DEFER_CLI), "--task", task, "--payload", payload_json]
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=60, env=os.environ.copy()
        )
    else:
        inner = json.dumps(payload_json)
        remote = (
            f"cd {repo} && set -a && . /etc/pearl-star/queue.env 2>/dev/null; set +a && "
            f"{py} scripts/manga/defer_panel_job_cli.py --task {task} --payload {inner}"
        )
        proc = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", ssh_host, remote],
            capture_output=True,
            text=True,
            timeout=90,
        )
    if proc.returncode != 0:
        raise DispatchError(
            f"dispatch failed (task={task}, local={local}): "
            f"{proc.stderr.strip() or proc.stdout.strip()}"
        )
    line = (proc.stdout or "").strip().splitlines()
    if not line:
        raise DispatchError(f"dispatch produced no output (task={task})")
    result = json.loads(line[-1])
    result["via"] = "local" if local else f"ssh:{ssh_host}"
    return result
