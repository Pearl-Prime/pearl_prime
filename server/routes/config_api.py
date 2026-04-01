"""
Configuration read endpoints (read-only).

GET /api/v1/config/quality       — quality gate thresholds
GET /api/v1/config/governance    — governance config summary
GET /api/v1/config/teachers      — teacher config listing
"""
from __future__ import annotations

from pathlib import Path

import yaml
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/config", tags=["config"])


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


@router.get("/quality")
async def quality_config():
    """Quality gate thresholds and EI v2 config."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    quality_dir = repo_root / "config" / "quality"
    result = {}
    if quality_dir.is_dir():
        for p in sorted(quality_dir.glob("*.yaml")):
            result[p.stem] = _load_yaml(p)
    return {"quality": result}


@router.get("/governance")
async def governance_config():
    """Governance configuration (system registry, required checks, branch registry)."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    gov_dir = repo_root / "config" / "governance"
    result = {}
    if gov_dir.is_dir():
        for p in sorted(gov_dir.glob("*.yaml")):
            result[p.stem] = _load_yaml(p)
        for p in sorted(gov_dir.glob("*.json")):
            import json
            if p.exists():
                with open(p, encoding="utf-8") as f:
                    result[p.stem] = json.load(f)
    return {"governance": result}


@router.get("/teachers")
async def teacher_config():
    """List available teacher configurations."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    teachers_dir = repo_root / "config" / "teachers"
    if not teachers_dir.is_dir():
        return {"teachers": [], "count": 0}
    teachers = sorted(
        p.stem for p in teachers_dir.glob("*.yaml")
    )
    return {"teachers": teachers, "count": len(teachers)}
