"""Read/write validated ``stage_manifest`` under ``stages/<stage_id>/``."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from phoenix_v4.manga.models import paths as manga_paths
from phoenix_v4.manga.models.validation import validate_instance


def stage_manifest_path(workspace: Path, stage_id: str) -> Path:
    return Path(workspace).resolve() / manga_paths.STAGES_DIR / stage_id / "stage_manifest.json"


def stage_is_passed(workspace: Path, stage_id: str) -> bool:
    p = stage_manifest_path(workspace, stage_id)
    if not p.is_file():
        return False
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return d.get("status") == "passed"


def write_stage_manifest(
    workspace: Path,
    stage_id: str,
    *,
    stage_name: str,
    status: str,
    attempt: int = 1,
    inputs: Mapping[str, Any] | None = None,
    outputs: Mapping[str, Any] | None = None,
    error_summary: str | None = None,
    schema_version: str = "1.0.0",
) -> None:
    doc: dict[str, Any] = {
        "schema_version": schema_version,
        "artifact_type": "stage_manifest",
        "stage_id": stage_id,
        "stage_name": stage_name,
        "attempt": attempt,
        "status": status,
    }
    if inputs is not None:
        doc["inputs"] = dict(inputs)
    if outputs is not None:
        doc["outputs"] = dict(outputs)
    if error_summary:
        doc["error_summary"] = error_summary
    validate_instance(doc, "stage_manifest")
    p = stage_manifest_path(workspace, stage_id)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
