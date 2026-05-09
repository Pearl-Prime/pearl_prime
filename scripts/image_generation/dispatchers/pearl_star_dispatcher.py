"""Pearl Star image dispatch (SSH + huggingface-cli or ComfyUI API).

Scaffold only: no network or SSH in this module until Pearl_Int Step 4 lands.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class PearlStarDispatchPlan:
    """Structured preview of what a live dispatch would do."""

    mode: str  # "ssh_hf_cli" | "comfyui_api" (activation-time choice)
    batch_id: str
    notes: str


def build_plan(batch: Mapping[str, Any]) -> PearlStarDispatchPlan:
    """Return a non-executing plan for logging and dry-run output."""
    batch_id = str(batch.get("batch_id", ""))
    mode = str(batch.get("pearl_star_mode", "ssh_hf_cli"))
    if mode not in ("ssh_hf_cli", "comfyui_api"):
        mode = "ssh_hf_cli"
    return PearlStarDispatchPlan(
        mode=mode,
        batch_id=batch_id,
        notes="stub: Pearl_Int Step 4 wiring replaces this path",
    )


def dispatch(batch: Mapping[str, Any], *, dry_run: bool) -> dict[str, Any]:
    """Dispatch to Pearl Star. When ``dry_run`` is True, never touches the network."""
    plan = build_plan(batch)
    result: dict[str, Any] = {
        "dispatch_path": "pearl_star",
        "dry_run": dry_run,
        "plan": {
            "mode": plan.mode,
            "batch_id": plan.batch_id,
            "notes": plan.notes,
        },
    }
    if dry_run:
        result["status"] = "dry_run"
        return result
    raise RuntimeError(
        "Pearl Star live dispatch is disabled in this scaffold; "
        "enable after Pearl_Int Step 4 + operator verification."
    )
