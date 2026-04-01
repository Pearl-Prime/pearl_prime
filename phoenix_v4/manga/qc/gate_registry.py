"""Load ``config/manga/gate_registry.yaml``."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from phoenix_v4.manga.models.validation import repo_root


@dataclass(frozen=True)
class GateSpec:
    gate_id: str
    stage_owner: str
    description: str
    severity: str = "BLOCKER"


def load_gate_registry(path: Path | None = None) -> list[GateSpec]:
    root = repo_root()
    p = path or (root / "config" / "manga" / "gate_registry.yaml")
    if not p.is_file():
        return []
    try:
        import yaml
    except ImportError as e:
        raise RuntimeError("PyYAML required to load gate_registry.yaml") from e
    raw = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    gates: list[GateSpec] = []
    for g in raw.get("gates") or []:
        if not isinstance(g, dict):
            continue
        gid = g.get("gate_id")
        if not gid:
            continue
        gates.append(
            GateSpec(
                gate_id=str(gid),
                stage_owner=str(g.get("stage_owner") or "unknown"),
                description=str(g.get("description") or ""),
                severity=str(g.get("severity") or "BLOCKER"),
            )
        )
    return gates


def gate_registry_json() -> str:
    """Stable JSON for debugging (not an artifact schema)."""
    return json.dumps(
        [{"gate_id": g.gate_id, "stage_owner": g.stage_owner} for g in load_gate_registry()],
        indent=2,
    )
