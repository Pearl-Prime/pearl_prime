"""RunComfy image dispatch with cost awareness (API + spend tracking).

Dry-run uses ``runcomfy_dispatch.dispatch_workflow`` (no HTTP). Live dispatch
remains gated until operator activation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from scripts.image_generation import runcomfy_dispatch as _rc


@dataclass(frozen=True)
class RunComfyDispatchPlan:
    """Structured preview of what a live RunComfy job would do."""

    batch_id: str
    workflow_hint: str
    notes: str


def _workflow_json_path(batch: Mapping[str, Any]) -> Path:
    """Resolve workflow JSON under ``comfyui_workflows/`` from batch hints."""
    root = Path(__file__).resolve().parents[1] / "comfyui_workflows"
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


def dispatch(batch: Mapping[str, Any], *, dry_run: bool) -> dict[str, Any]:
    """Dispatch to RunComfy. When ``dry_run`` is True, never calls the API."""
    plan = build_plan(batch)
    wf_path = _workflow_json_path(batch)
    preview = _rc.dispatch_workflow(
        wf_path,
        dry_run=dry_run,
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
    raise RuntimeError(
        "RunComfy live dispatch is disabled in this scaffold; "
        "enable after RunComfy wiring + cost gate verification."
    )
