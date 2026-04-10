from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from scripts.pipeline._paths import REPO_ROOT


def registry_path() -> Path:
    return REPO_ROOT / "config" / "pipeline_registry.yaml"


def load_registry() -> dict[str, Any]:
    try:
        import yaml
    except ImportError as e:
        raise SystemExit(
            "PyYAML is required for pipeline jobs. Install with: pip install pyyaml"
        ) from e
    p = registry_path()
    if not p.exists():
        raise FileNotFoundError(f"Missing pipeline registry: {p}")
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def job_file(workspace: Path) -> Path:
    return workspace.resolve() / "job.json"


def load_job(workspace: Path) -> dict[str, Any]:
    p = job_file(workspace)
    if not p.exists():
        raise FileNotFoundError(str(p))
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("job.json must be a JSON object")
    return data


def write_job_atomic(workspace: Path, job: dict[str, Any]) -> None:
    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)
    p = job_file(workspace)
    tmp = p.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(job, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(p)


def iso_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S%z")


def stages_from_registry(pipe_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    raw = pipe_cfg.get("stages") or []
    out: list[dict[str, Any]] = []
    for item in raw:
        if isinstance(item, dict) and item.get("name"):
            out.append(item)
    return out


def stage_index(stages: list[dict[str, Any]], name: str) -> int:
    for i, s in enumerate(stages):
        if s.get("name") == name:
            return i
    raise KeyError(name)


def normalize_job_stages(job: dict[str, Any], pipe_cfg: dict[str, Any]) -> list[dict[str, Any]]:
    """Ensure job['stages'] is a list of dicts aligned with registry order."""
    reg = stages_from_registry(pipe_cfg)
    by_name = {str(s.get("name")): s for s in job.get("stages") or [] if isinstance(s, dict)}
    merged: list[dict[str, Any]] = []
    for r in reg:
        n = str(r["name"])
        prev = by_name.get(n)
        if prev and isinstance(prev, dict):
            merged.append(
                {
                    "name": n,
                    "status": prev.get("status"),
                    "output": prev.get("output"),
                    "ts": prev.get("ts"),
                }
            )
        else:
            merged.append({"name": n, "status": None, "output": None, "ts": None})
    job["stages"] = merged
    return merged
