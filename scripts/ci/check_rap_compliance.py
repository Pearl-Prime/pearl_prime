#!/usr/bin/env python3
"""Warn when Pearl Star GPU/LLM work may be running outside the pscli queue (RAP).

Robust Agent Protocol (RAP) requires queue-first dispatch for tasks >10s on Pearl Star.
This check is best-effort: it cannot prove an agent followed RAP, only surface likely violations.

Run:
  PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py
  PYTHONPATH=. python3 scripts/ci/check_rap_compliance.py --strict   # exit 1 on violations

Exit: 0 by default (warnings only); 1 with --strict when violations found.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
_GH_WARN_PREFIX = "::warning::"

# Process command-line fragments that suggest direct GPU/LLM work bypassing pscli.
_DIRECT_GPU_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"queue_panel_renders\.py(?!.*--via-queue)"), "queue_panel_renders.py without --via-queue"),
    (re.compile(r"render_v5_episode\.py"), "render_v5_episode.py direct invocation"),
    (re.compile(r"comfyui.*--listen"), "ComfyUI server started outside pscli"),
    (re.compile(r"ollama run\b"), "ollama run direct (use pscli enqueue)"),
    (re.compile(r"curl .*/prompt\b"), "direct ComfyUI /prompt HTTP call"),
)

# Scripts that MUST pass --via-queue when not --dry-run (static scan targets).
_QUEUE_FIRST_SCRIPTS = (
    REPO_ROOT / "scripts" / "manga" / "queue_panel_renders.py",
)


def _warn(msg: str) -> None:
    print(f"{_GH_WARN_PREFIX}{msg}", file=sys.stderr)
    print(f"WARN: {msg}", file=sys.stderr)


def _pscli_available() -> bool:
    return shutil.which("pscli") is not None


def _pearl_star_context() -> bool:
    host = os.environ.get("PEARL_STAR_HOST", "").strip()
    dsn = os.environ.get("PS_QUEUE_DSN", "").strip()
    if host or dsn:
        return True
    try:
        hn = subprocess.check_output(["hostname"], text=True, timeout=5).strip().lower()
    except (subprocess.SubprocessError, OSError):
        return False
    return "pearl-star" in hn or hn == "pearlstar"


def _check_pscli_status() -> list[str]:
    violations: list[str] = []
    if not _pearl_star_context():
        return violations
    if not _pscli_available():
        violations.append("Pearl Star context detected but pscli not on PATH")
        return violations
    try:
        proc = subprocess.run(
            ["pscli", "status"],
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (subprocess.SubprocessError, OSError) as exc:
        violations.append(f"pscli status failed: {exc}")
        return violations
    out = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        violations.append(f"pscli status exit {proc.returncode}: {out.strip()[:200]}")
    elif "PAUSED" in out.upper():
        violations.append("pscli queue is PAUSED — do not enqueue until RUNNING")
    return violations


def _scan_process_table() -> list[str]:
    violations: list[str] = []
    try:
        proc = subprocess.run(["ps", "axww", "-o", "command="], capture_output=True, text=True, timeout=10)
    except (subprocess.SubprocessError, OSError):
        return violations
    for line in (proc.stdout or "").splitlines():
        cmd = line.strip()
        if not cmd or "check_rap_compliance" in cmd:
            continue
        for pattern, label in _DIRECT_GPU_PATTERNS:
            if pattern.search(cmd):
                violations.append(f"Running process matches RAP bypass: {label}")
                break
    return violations


def _scan_queue_first_script_help() -> list[str]:
    """Ensure canonical manga dispatch documents --via-queue (regression guard)."""
    violations: list[str] = []
    for path in _QUEUE_FIRST_SCRIPTS:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if "--via-queue" not in text:
            violations.append(f"{path.relative_to(REPO_ROOT)} missing --via-queue flag (RAP regression)")
    return violations


def main() -> int:
    ap = argparse.ArgumentParser(description="RAP compliance warnings for Pearl Star dispatch")
    ap.add_argument("--strict", action="store_true", help="Exit 1 when violations found")
    ap.add_argument("--skip-process-scan", action="store_true", help="Skip live process table scan")
    args = ap.parse_args()

    violations: list[str] = []
    violations.extend(_check_pscli_status())
    violations.extend(_scan_queue_first_script_help())
    if not args.skip_process_scan:
        violations.extend(_scan_process_table())

    if not violations:
        print("RAP compliance: OK (no violations detected)")
        return 0

    for v in violations:
        _warn(f"RAP: {v}")

    if args.strict:
        print(f"RAP compliance: FAIL ({len(violations)} violation(s))", file=sys.stderr)
        return 1
    print(f"RAP compliance: {len(violations)} warning(s) (non-blocking)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
