"""RunComfy image dispatch with cost awareness (API + spend tracking).

Dry-run uses ``runcomfy_dispatch.dispatch_workflow`` (no HTTP). Live mode calls
``poll_billing(dry_run=False)`` before each job, respects the $10 cumulative
soft cap, then uses ``runcomfy_batch.submit_inference`` + poll/result/download
(``overrides`` pattern — deployment-native FLUX graph).

V1.2 PANEL HANG FIX (2026-05-13)
================================
RunComfy serverless cold-start single inference wall time was measured at
~292s (~5 min) on the FLUX deployment ``677edba8…`` — verified live on
2026-05-13. The prior ``max_wait=300`` left effectively zero headroom and any
upstream cell-guard set to 4 min was guaranteed to kill the dispatch before
RunComfy completed even a single render. The poll budget here is now
``RUNCOMFY_POLL_MAX_WAIT_S`` (default 600s, matching Pearl Star's history
poll budget). Upstream callers that enforce a per-cell wall guard MUST be
configured to >= 480s for RunComfy-dispatched panels — see
``docs/specs/CONDUCTOR_V3_DISPATCH_BRIDGE_V1_SPEC.md`` AMENDMENT-2026-05-13.
The dispatcher additionally returns ``poll_wait_s`` so observability can
detect drift back toward the cold-start ceiling.
"""

from __future__ import annotations

import hashlib
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from scripts.image_generation import runcomfy_dispatch as _rc
from scripts.image_generation import runcomfy_cost_tracker as _bill
from scripts.image_generation import batch_runner as _br
from scripts.image_generation import runcomfy_spend_ledger as _ledger
from scripts.image_generation.runcomfy_batch import (
    download_image,
    extract_image_url,
    get_result,
    poll_request,
    submit_inference,
)


@dataclass(frozen=True)
class RunComfyDispatchPlan:
    """Structured preview of what a live RunComfy job would do."""

    batch_id: str
    workflow_hint: str
    notes: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _workflow_json_path(batch: Mapping[str, Any]) -> Path:
    """Resolve workflow JSON under ``comfyui_workflows/`` from batch hints."""
    root = _repo_root() / "scripts" / "image_generation" / "comfyui_workflows"
    explicit = batch.get("runcomfy_workflow_path") or batch.get("workflow_path")
    if explicit:
        p = Path(str(explicit))
        return p if p.is_absolute() else root / p.name
    hint = str(batch.get("runcomfy_workflow", "flux_txt2img_manga")).strip()
    name = hint if hint.endswith(".json") else f"{hint}.json"
    return root / name


def build_plan(batch: Mapping[str, Any]) -> RunComfyDispatchPlan:
    """Return a non-executing plan for logging and dry-run output."""
    batch_id = str(batch.get("batch_id", ""))
    wf = _workflow_json_path(batch)
    workflow_hint = wf.stem
    return RunComfyDispatchPlan(
        batch_id=batch_id,
        workflow_hint=workflow_hint,
        notes=f"workflow_json={wf.name}",
    )


def _default_deployment_id() -> str:
    return (
        os.environ.get("RUNCOMFY_DEPLOYMENT_ID", "").strip()
        or "677edba8-ace0-4b2b-bad2-8e94b9959065"
    )


# V1.2 PANEL HANG FIX: cold-start P95 measured at ~292s on 2026-05-13.
# Set default to 600s and allow env override so ops can tune without redeploy.
_DEFAULT_POLL_MAX_WAIT_S: int = 600


def _poll_max_wait_s() -> int:
    raw = os.environ.get("RUNCOMFY_POLL_MAX_WAIT_S", "").strip()
    if not raw:
        return _DEFAULT_POLL_MAX_WAIT_S
    try:
        value = int(raw)
    except (TypeError, ValueError):
        return _DEFAULT_POLL_MAX_WAIT_S
    # Floor at 300 (legacy default) and ceil at 1800 (RunComfy hard timeout)
    # to keep configuration mistakes from bricking the dispatcher.
    return max(300, min(1800, value))


def _runcomfy_api_key() -> str:
    """Bearer material (RunComfy accepts token-shaped keys)."""
    return _rc.load_token(require=True)


def _validate_png(path: Path) -> None:
    if not path.is_file():
        raise RuntimeError(f"missing RunComfy download: {path}")
    if path.stat().st_size < 10_000:
        raise RuntimeError("downloaded image too small; likely corrupt")
    with path.open("rb") as handle:
        if handle.read(8) != b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("downloaded file is not a valid PNG")


def dispatch(
    batch: Mapping[str, Any],
    *,
    dry_run: bool,
    activation_output_dir: Path | None = None,
) -> dict[str, Any]:
    """Dispatch to RunComfy. ``activation_output_dir`` required when not dry_run."""
    plan = build_plan(batch)
    wf_path = _workflow_json_path(batch)
    # ``runcomfy_dispatch.dispatch_workflow`` remains dry-run-only upstream; always
    # query the preview path with ``dry_run=True`` for token/path validation.
    preview = _rc.dispatch_workflow(
        wf_path,
        dry_run=True,
        require_token=not dry_run,
    )
    result: dict[str, Any] = {
        "dispatch_path": "runcomfy",
        "dry_run": dry_run,
        "plan": {
            "batch_id": plan.batch_id,
            "workflow_hint": plan.workflow_hint,
            "notes": plan.notes,
        },
        "runcomfy_dispatch": preview,
    }
    if dry_run:
        result["status"] = "dry_run"
        return result

    if activation_output_dir is None:
        raise ValueError("activation_output_dir is required for RunComfy live dispatch")

    try:
        billing = _bill.poll_billing(dry_run=False)
        spend = float(billing.get("cumulative_month_spend_usd", 0.0))
    except Exception:
        spend = float(_br.runcomfy_cost_check().get("spend_to_date_usd", 0.0))
        billing = {"cumulative_month_spend_usd": spend, "billing_poll_error": True}

    result["billing_snapshot_usd"] = spend
    if spend >= 25.0:  # TEMPORARY: RunComfy deprecation burn — restore to 10.0 after closure
        result["status"] = "suppressed_cooldown"
        result["notes"] = "RunComfy cumulative_month_spend_usd >= $25; job not submitted (deprecation-burn cap)."
        return result

    api_key = _runcomfy_api_key()
    dep = _default_deployment_id()
    positive = str(batch.get("positive_prompt", "manga smoke render, clean lines"))
    try:
        seed = int(batch.get("seed", 42))
    except (TypeError, ValueError):
        seed = 42

    t0 = time.perf_counter()
    submit = submit_inference(
        api_key=api_key,
        deployment_id=dep,
        positive_prompt=positive,
        seed=seed,
    )
    status_url = str(submit.get("status_url") or "")
    result_url = str(submit.get("result_url") or "")
    request_id = str(submit.get("request_id") or submit.get("run_id") or "")
    api_base = "https://api.runcomfy.net/prod/v1"
    if not status_url and request_id:
        status_url = f"{api_base}/deployments/{dep}/requests/{request_id}/status"
    if not result_url and request_id:
        result_url = f"{api_base}/deployments/{dep}/requests/{request_id}/result"
    if not status_url:
        raise RuntimeError(f"RunComfy submit missing status URL: {submit!r}")

    poll_wait_s = _poll_max_wait_s()
    poll_t0 = time.perf_counter()
    poll_resp = poll_request(api_key, status_url, max_wait=poll_wait_s)
    poll_elapsed = round(time.perf_counter() - poll_t0, 2)
    poll_status = str(poll_resp.get("status", "unknown")) if isinstance(poll_resp, dict) else "unknown"
    if poll_status == "timeout":
        raise RuntimeError(
            f"RunComfy poll timed out after {poll_wait_s}s (status_url terminal status never reached). "
            f"Cold-start P95 is ~5 min; consider raising RUNCOMFY_POLL_MAX_WAIT_S."
        )
    if poll_status in ("failed", "error"):
        err = poll_resp.get("error") if isinstance(poll_resp, dict) else None
        raise RuntimeError(f"RunComfy poll terminal status={poll_status} error={err!r}")
    final = get_result(api_key, result_url) if result_url else {}
    image_url = extract_image_url(final)
    if not image_url:
        raise RuntimeError(f"No image URL in RunComfy result keys={list(final)[:12]}")

    out_dir = activation_output_dir / str(batch.get("batch_id", "batch"))
    out_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", str(batch.get("batch_id", "runcomfy"))) + ".png"
    dest = out_dir / safe
    download_image(image_url, dest)
    _validate_png(dest)
    wall = round(time.perf_counter() - t0, 2)
    sha = hashlib.sha256(dest.read_bytes()).hexdigest()
    result["status"] = "succeeded"
    try:
        result["output_path"] = str(dest.resolve().relative_to(_repo_root()))
    except ValueError:
        result["output_path"] = str(dest)
    result["sha256"] = sha
    result["wall_time_s"] = wall
    result["runcomfy_request_id"] = request_id
    # V1.2 PANEL HANG FIX: surface poll wall-time + budget so upstream cell
    # guards can be tuned against measured cold-start behaviour rather than
    # guesses. See AMENDMENT-2026-05-13 in CONDUCTOR_V3_DISPATCH_BRIDGE spec.
    result["poll_wait_s"] = poll_elapsed
    result["poll_budget_s"] = poll_wait_s

    # Append per-call spend ledger row (RUNCOMFY-SPEND-LEDGER-V1).
    # Wall-time GPU-seconds × published per-second rate; flagged ``estimated``
    # because vendor billing endpoint returns HTTP 403 in this env. See
    # docs/specs/RUNCOMFY_SPEND_LEDGER_V1_SPEC.md §3.
    try:
        ledger_row = _ledger.record_dispatch(
            batch_id=str(batch.get("batch_id", "")),
            workflow_id=plan.workflow_hint,
            gpu_seconds=float(wall),
            source="estimated",
            request_id=request_id,
        )
        result["spend_ledger"] = {
            "est_usd": ledger_row.est_usd,
            "cumulative_month_usd": ledger_row.cumulative_month_usd,
            "source": ledger_row.source,
            "rate_per_second_usd": ledger_row.rate_per_second_usd,
        }
    except Exception as ledger_err:  # noqa: BLE001 — never block dispatch on ledger
        result["spend_ledger_error"] = str(ledger_err)[:200]
    return result
