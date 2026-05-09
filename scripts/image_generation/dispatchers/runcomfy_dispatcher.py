"""RunComfy image dispatch with cost awareness (API + spend tracking).

Scaffold only: no RunComfy HTTP calls or spend in this module until wiring lands.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class RunComfyDispatchPlan:
    """Structured preview of what a live RunComfy job would do."""

    batch_id: str
    workflow_hint: str
    notes: str


def build_plan(batch: Mapping[str, Any]) -> RunComfyDispatchPlan:
    """Return a non-executing plan for logging and dry-run output."""
    batch_id = str(batch.get("batch_id", ""))
    workflow_hint = str(batch.get("runcomfy_workflow", "flux_txt2img_manga"))
    return RunComfyDispatchPlan(
        batch_id=batch_id,
        workflow_hint=workflow_hint,
        notes="stub: RunComfy API wiring + deployment id activation in follow-up",
    )


def dispatch(batch: Mapping[str, Any], *, dry_run: bool) -> dict[str, Any]:
    """Dispatch to RunComfy. When ``dry_run`` is True, never calls the API."""
    plan = build_plan(batch)
    result: dict[str, Any] = {
        "dispatch_path": "runcomfy",
        "dry_run": dry_run,
        "plan": {
            "batch_id": plan.batch_id,
            "workflow_hint": plan.workflow_hint,
            "notes": plan.notes,
        },
    }
    if dry_run:
        result["status"] = "dry_run"
        return result
    raise RuntimeError(
        "RunComfy live dispatch is disabled in this scaffold; "
        "enable after RunComfy wiring + cost gate verification."
    )
