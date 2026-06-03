#!/usr/bin/env python3
"""RunComfy API client wrapper (IMG-RENDER-DUAL-PATH-V1-01).

Loads ``RUNCOMFY_API_TOKEN`` from the environment or macOS Keychain
(service ``phoenix-omega``, account ``RUNCOMFY_API_TOKEN``). When
``dry_run=True``, ``dispatch_workflow`` never performs HTTP requests.

Live billing and job submission are gated by ``runcomfy_cost_tracker``.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_DEPLOYMENT_ID = "677edba8-ace0-4b2b-bad2-8e94b9959065"
_RUNCOMFY_JOB_BASE = "https://api.runcomfy.net/prod/v1"


class RunComfyAuthError(RuntimeError):
    """Missing or unreadable RunComfy credentials."""


def load_token(
    *,
    service: str = "phoenix-omega",
    require: bool = True,
) -> str:
    """Resolve Bearer token material from env, then Keychain (macOS)."""
    for name in ("RUNCOMFY_API_TOKEN", "RUNCOMFY_API_KEY", "RUNCOMFY_TOKEN"):
        v = os.environ.get(name, "").strip()
        if v:
            return v
    if sys.platform == "darwin":
        r = subprocess.run(
            [
                "security",
                "find-generic-password",
                "-s",
                service,
                "-a",
                "RUNCOMFY_API_TOKEN",
                "-w",
            ],
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            out = (r.stdout or "").strip()
            if out:
                return out
    if require:
        raise RunComfyAuthError(
            "RunComfy token not found: set RUNCOMFY_API_TOKEN (or RUNCOMFY_API_KEY) "
            f"in the environment, or add a Keychain generic password "
            f"(service={service!r}, account=RUNCOMFY_API_TOKEN)."
        )
    return ""


def _read_workflow(workflow_path: Path) -> dict[str, Any]:
    if not workflow_path.is_file():
        raise FileNotFoundError(f"workflow JSON not found: {workflow_path}")
    return json.loads(workflow_path.read_text(encoding="utf-8"))


def _cooldown_from_spend_file(spend_path: Path | None, cap_usd: float) -> bool:
    if spend_path is None or not spend_path.is_file():
        return False
    from scripts.image_generation import batch_runner

    info = batch_runner.runcomfy_cost_check(spend_path=spend_path, cooldown_usd=cap_usd)
    return bool(info.get("cooldown"))


def dispatch_workflow(
    workflow_path: str | Path,
    *,
    dry_run: bool = True,
    deployment_id: str | None = None,
    spend_tsv: Path | None = None,
    cooldown_usd: float = 25.0,  # TEMPORARY: RunComfy deprecation burn — restore to 10.0 after closure
    require_token: bool = True,
) -> dict[str, Any]:
    """Prepare or submit a RunComfy deployment job for the given workflow JSON.

    With ``dry_run=True`` (default for this wiring phase), validates paths and
    token visibility but performs **no** HTTP calls.
    """
    wf = Path(workflow_path).resolve()
    dep = (deployment_id or os.environ.get("RUNCOMFY_DEPLOYMENT_ID") or _DEFAULT_DEPLOYMENT_ID).strip()
    spend_path = spend_tsv
    if spend_path is None:
        spend_path = REPO_ROOT / "artifacts" / "qa" / "runcomfy_monthly_spend.tsv"

    token_loaded = False
    if require_token:
        try:
            load_token(require=True)
            token_loaded = True
        except RunComfyAuthError:
            raise
    else:
        token_loaded = bool(load_token(require=False))

    graph = _read_workflow(wf) if wf.is_file() else {}
    cooldown = _cooldown_from_spend_file(spend_path, cooldown_usd)

    base: dict[str, Any] = {
        "dry_run": dry_run,
        "workflow_path": str(wf),
        "deployment_id": dep,
        "workflow_node_count": len(graph) if isinstance(graph, dict) else 0,
        "api_base": _RUNCOMFY_JOB_BASE,
        "token_loaded": token_loaded,
        "cooldown": cooldown,
        "cooldown_threshold_usd": cooldown_usd,
        "spend_tsv": str(spend_path),
    }

    if dry_run:
        base["status"] = "dry_run"
        base["http_would_call"] = f"{_RUNCOMFY_JOB_BASE}/deployments/{dep}/requests"
        base["notes"] = "No HTTP request sent (dry_run=True)."
        return base

    if cooldown:
        base["status"] = "cooldown_blocked"
        base["notes"] = (
            f"cumulative_month_spend_usd >= {cooldown_usd}; suppress outbound job."
        )
        return base

    raise RuntimeError(
        "Live RunComfy dispatch is disabled until operator activation; "
        "use dry_run=True or complete the follow-up enablement PR."
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--workflow", type=Path, required=True, help="Path to ComfyUI workflow JSON")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not call RunComfy HTTP API (default when --live is omitted)",
    )
    p.add_argument(
        "--live",
        action="store_true",
        help="Attempt live dispatch (still blocked until activation PR)",
    )
    p.add_argument(
        "--no-require-token",
        action="store_true",
        help="Allow dry-run without a token (paths only)",
    )
    args = p.parse_args(argv)
    if args.live and args.dry_run:
        p.error("--live and --dry-run are mutually exclusive")
    dry_run = not args.live
    try:
        out = dispatch_workflow(
            args.workflow,
            dry_run=dry_run,
            require_token=not args.no_require_token,
        )
    except RunComfyAuthError as e:
        print(str(e), file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as e:
        print(str(e), file=sys.stderr)
        return 3
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
