"""
System information endpoints.

GET /api/v1/system/info      — repo metadata, config summary
GET /api/v1/system/registry  — governance system registry
GET /api/v1/system/docs      — list of canonical documentation files
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import yaml
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/system", tags=["system"])


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _git_info(repo_root: Path) -> dict:
    """Lightweight git metadata."""
    info: dict = {}
    try:
        info["branch"] = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=str(repo_root), text=True, timeout=5,
        ).strip()
    except Exception:
        info["branch"] = "unknown"
    try:
        info["commit"] = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=str(repo_root), text=True, timeout=5,
        ).strip()
    except Exception:
        info["commit"] = "unknown"
    return info


@router.get("/info")
async def system_info():
    """Repo metadata and server config summary."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    git = _git_info(repo_root)
    return {
        "project": "phoenix_omega",
        "repo_root": str(repo_root),
        "git": git,
        "server": {
            "host": cfg.host,
            "port": cfg.port,
            "log_level": cfg.log_level,
            "workers": cfg.workers,
        },
    }


@router.get("/registry")
async def system_registry():
    """Return the governance system registry."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    registry = _load_yaml(repo_root / "config" / "governance" / "system_registry.yaml")
    return {"registry": registry}


@router.get("/docs")
async def docs_list():
    """List canonical documentation files from docs/."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    docs_dir = repo_root / "docs"
    if not docs_dir.is_dir():
        return {"docs": []}
    files = sorted(
        str(p.relative_to(repo_root))
        for p in docs_dir.glob("*.md")
    )
    return {"docs": files, "count": len(files)}
