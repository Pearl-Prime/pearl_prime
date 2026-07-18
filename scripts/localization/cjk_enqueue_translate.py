#!/usr/bin/env python3
"""Enqueue one CJK translate batch via RAP queue-first dispatch (pscli/Procrastinate).

Never calls Ollama directly — routes through llm_translate_atoms_batch worker.

Usage:
  PYTHONPATH=. python3 scripts/localization/cjk_enqueue_translate.py \\
    --locale ja-JP --paths-file /tmp/batch.txt --wait
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.pearl_star.dispatch import DispatchError, dispatch_gpu_job


def _pscli(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run pscli locally if present on PATH, else over SSH to Pearl Star.

    Mac clients never have pscli on PATH (it is only installed on Pearl
    Star) — the dispatch itself already goes over SSH via dispatch.py, so
    status/inspect polling must follow the same route rather than assuming
    a local binary.
    """
    if shutil_which("pscli"):
        return subprocess.run(["pscli", *args], capture_output=True, text=True, timeout=timeout)
    ssh_host = os.environ.get("PS_QUEUE_SSH_HOST", "pearl_star")
    repo = os.environ.get("PS_PHOENIX_REPO", "/home/ahjan108/phoenix_omega")
    py = os.environ.get("PS_PY", "/opt/pearl-star/venv/bin/python")
    remote = (
        f"set -a; . /etc/pearl-star/queue.env 2>/dev/null; "
        f". {repo}/.pearl_star_queue.env 2>/dev/null; set +a; "
        f"{py} /usr/local/bin/pscli " + " ".join(args)
    )
    return subprocess.run(
        ["ssh", "-o", "BatchMode=yes", ssh_host, remote],
        capture_output=True,
        text=True,
        timeout=timeout + 15,
    )


def _pscli_status_ok() -> bool:
    proc = _pscli("status", timeout=15)
    if proc.returncode != 0:
        return False
    return "PAUSED" not in (proc.stdout or "")


def _wait_job(job_id: int, *, timeout_s: int = 7200) -> str:
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        proc = _pscli("inspect", str(job_id), timeout=30)
        out = proc.stdout or ""
        for line in out.splitlines():
            if line.strip().startswith("status:"):
                status = line.split(":", 1)[1].strip()
                if status == "succeeded":
                    return status
                if status in ("failed", "aborted", "cancelled"):
                    raise RuntimeError(f"job #{job_id} ended with status={status}\n{out}")
        time.sleep(10)
    raise TimeoutError(f"job #{job_id} did not succeed within {timeout_s}s")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--locale", required=True, help="BCP47 locale e.g. ja-JP")
    ap.add_argument("--paths-file", required=True, help="Paths file ON Pearl Star (absolute)")
    ap.add_argument("--model", default="qwen2.5:14b")
    ap.add_argument("--ollama-url", default="http://127.0.0.1:11434")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--wait", action="store_true", help="Poll until job succeeds")
    ap.add_argument("--timeout", type=int, default=7200)
    ap.add_argument("--gpu-acquire", action="store_true", help="pscli gpu-acquire cjk before enqueue")
    args = ap.parse_args(argv)

    if args.gpu_acquire:
        _pscli("gpu-acquire", "cjk", "--note", "cjk_enqueue_translate", timeout=15)

    if not _pscli_status_ok():
        print("WARN: pscli status reports PAUSED or unreachable", file=sys.stderr)

    payload = {
        "locale": args.locale,
        "paths_file": args.paths_file,
        "model": args.model,
        "ollama_url": args.ollama_url,
        "workers": args.workers,
        "force": args.force,
        "persona_atoms_only": True,
    }

    try:
        result = dispatch_gpu_job(
            job_class="llm",
            task="llm_translate_atoms_batch",
            payload=payload,
        )
    except DispatchError as exc:
        print(f"dispatch failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    job_id = int(result["job_id"])

    if args.wait:
        status = _wait_job(job_id, timeout_s=args.timeout)
        print(f"job #{job_id} {status}")
    return 0


def shutil_which(cmd: str) -> bool:
    from shutil import which
    return which(cmd) is not None


if __name__ == "__main__":
    raise SystemExit(main())
