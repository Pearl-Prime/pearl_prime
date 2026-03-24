"""Apply validated ``series_memory_update`` patches to ``series_memory``."""

from __future__ import annotations

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping


def load_or_init_series_memory(path: Path) -> dict[str, Any]:
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {
        "schema_version": "1.0.0",
        "artifact_type": "series_memory",
        "facts": [],
    }


def apply_series_memory_update(
    memory: Mapping[str, Any], update: Mapping[str, Any]
) -> dict[str, Any]:
    """Deepcopy memory and apply patches. Supported ops: ``append_fact``."""
    out = deepcopy(dict(memory))
    facts = out.setdefault("facts", [])
    if not isinstance(facts, list):
        facts = []
        out["facts"] = facts
    for patch in update.get("patches") or []:
        if not isinstance(patch, dict):
            continue
        if patch.get("op") == "append_fact" and isinstance(patch.get("fact"), dict):
            facts.append(dict(patch["fact"]))
    return out


def series_memory_content_sha256(memory: Mapping[str, Any]) -> str:
    body = json.dumps(memory, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(body).hexdigest()


def build_series_memory_snapshot(
    memory: Mapping[str, Any], *, schema_version: str = "1.0.0"
) -> dict[str, Any]:
    h = series_memory_content_sha256(memory)
    return {
        "schema_version": schema_version,
        "artifact_type": "series_memory_snapshot",
        "snapshot_of_series_memory_sha256": h,
        "facts": deepcopy(memory.get("facts") or []),
    }
