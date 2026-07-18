"""Pearl Star Job Queue — llm translate_atoms batch worker (CJK lane).

One Procrastinate job = one atomic translate batch (paths-file slice). Uses the
shared gpu_heavy flock + respects pscli gpu_lane (cjk blocks manga t2i).

Tier policy: Ollama qwen2.5:14b on-box only. No paid LLM API (CLAUDE.md).
"""

from __future__ import annotations

import os
import socket
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app import app
from gpu_heavy_lock import gpu_heavy_lock

REPO_ROOT = Path(os.environ.get("PS_PHOENIX_REPO", Path.home() / "phoenix_omega"))
TRANSLATE_CLI = REPO_ROOT / "scripts" / "localization" / "translate_atoms_to_locale.py"
WORKLOAD = "llm_translate_atoms_batch"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _worker_id() -> str:
    return f"{socket.gethostname()}-llm-{os.getpid()}"


@app.task(name=WORKLOAD, queue="llm")
def llm_translate_atoms_batch(
    *,
    locale: str,
    paths_file: str,
    model: str = "qwen2.5:14b",
    ollama_url: str = "http://127.0.0.1:11434",
    workers: int = 1,
    force: bool = False,
    persona_atoms_only: bool = True,
) -> dict[str, Any]:
    """Run translate_atoms_to_locale.py for one paths-file batch under GPU lock."""
    pf = Path(paths_file)
    if not pf.is_file():
        raise FileNotFoundError(f"paths_file missing: {paths_file}")

    holder = f"{WORKLOAD}:{pf.name}"

    cmd = [
        sys.executable,
        str(TRANSLATE_CLI),
        "--locale",
        locale,
        "--paths-file",
        str(pf),
        "--model",
        model,
        "--ollama-url",
        ollama_url,
        "--workers",
        str(max(1, int(workers))),
    ]
    if force:
        cmd.append("--force")
    if persona_atoms_only:
        cmd.append("--persona-atoms-only")

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT)

    with gpu_heavy_lock(holder, worker_lane="cjk", note=f"locale={locale}"):
        proc = subprocess.run(
            cmd,
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=int(os.environ.get("PS_LLM_TRANSLATE_TIMEOUT_S", "7200")),
        )

    result = {
        "locale": locale,
        "paths_file": str(pf),
        "returncode": proc.returncode,
        "stdout_tail": (proc.stdout or "")[-4000:],
        "stderr_tail": (proc.stderr or "")[-2000:],
        "finished_at": _utc(),
        "worker_id": _worker_id(),
    }
    if proc.returncode != 0:
        raise RuntimeError(
            f"{WORKLOAD} failed rc={proc.returncode}: "
            f"{result['stderr_tail'] or result['stdout_tail']}"
        )
    return result
