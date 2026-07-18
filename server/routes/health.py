"""
Health and readiness endpoints.

GET /health  — always returns 200 with system health summary
GET /ready   — returns 200 when all required files exist, 503 otherwise
"""
from __future__ import annotations

import time
from pathlib import Path

from fastapi import APIRouter

router = APIRouter(tags=["health"])

_start_time = time.time()


def _check_health(repo_root: Path, required_files: list[str]) -> dict:
    """Run health checks against the repo root."""
    missing = []
    for rel in required_files:
        if not (repo_root / rel).exists():
            missing.append(rel)

    uptime = time.time() - _start_time
    return {
        "status": "healthy" if not missing else "degraded",
        "uptime_seconds": round(uptime, 1),
        "repo_root": str(repo_root),
        "missing_files": missing,
    }


@router.get("/health")
async def health():
    """Basic liveness probe. Always returns 200."""
    from server.app import get_settings
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    info = _check_health(repo_root, cfg.health.required_files)
    return info


@router.get("/ready")
async def ready():
    """Readiness probe. Returns 503 if critical files are missing."""
    from server.app import get_settings
    from starlette.responses import JSONResponse
    cfg = get_settings()
    repo_root = cfg.get_repo_root()
    info = _check_health(repo_root, cfg.health.required_files)
    if info["missing_files"]:
        return JSONResponse(info, status_code=503)
    return info
