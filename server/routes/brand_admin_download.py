"""
Thin Brand Admin download API (OPD-120 / OPD-145 split-at-build).

Serves weekly admin ZIPs: monolithic per-week or per-platform subdirs.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse

from server.brand_admin_platform import (
    PLATFORM_SLUGS,
    monolithic_zip_path,
    platform_zip_path,
)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
COORD_DIR = REPO_ROOT / "artifacts" / "coordination"
PACKAGES_DIR = REPO_ROOT / "artifacts" / "weekly_packages"

router = APIRouter(prefix="/api/brand_admin", tags=["brand-admin-download"])


def iso_week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def _relative_phrase(when: datetime) -> str:
    delta = datetime.now(tz=timezone.utc) - when.astimezone(timezone.utc)
    secs = int(delta.total_seconds())
    if secs < 60:
        return "just now"
    if secs < 3600:
        return f"{secs // 60} min ago"
    if secs < 86400:
        return f"{secs // 3600} h ago"
    return f"{secs // 86400} d ago"


def coordination_build_status() -> dict:
    mon = iso_week_monday(datetime.now(tz=timezone.utc).date())
    path = COORD_DIR / f"weekly_packages_{mon.isoformat()}.tsv"
    if not path.is_file():
        candidates = sorted(
            COORD_DIR.glob("weekly_packages_*.tsv"),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        path = candidates[0] if candidates else None

    if path is None or not path.is_file():
        return {
            "status": "MISSING",
            "monday": mon.isoformat(),
            "mtime_iso": None,
            "relative": "never",
            "age_days": None,
            "path": None,
        }

    mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
    age_days = (datetime.now(tz=timezone.utc) - mtime).total_seconds() / 86400.0
    status = "CURRENT" if age_days <= 8.0 else "STALE"
    return {
        "status": status,
        "monday": path.stem.replace("weekly_packages_", ""),
        "mtime_iso": mtime.isoformat(),
        "relative": _relative_phrase(mtime),
        "age_days": round(age_days, 2),
        "path": path.relative_to(REPO_ROOT).as_posix(),
    }


@router.get("/coordination-status")
async def get_coordination_status() -> dict:
    """Last-built badge data from coordination TSV mtime."""
    return coordination_build_status()


def _stream_zip(zip_path: Path) -> FileResponse:
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=zip_path.name,
        headers={"Content-Disposition": f'attachment; filename="{zip_path.name}"'},
    )


@router.get("/download/{brand_id}/{week}")
async def download_admin_packet(
    brand_id: str,
    week: str,
    platform: Optional[str] = Query(None, description="Platform slug (OPD-145 split-at-build)"),
):
    """Stream monolithic ``<brand>_<week>.zip`` or per-platform ``<brand>_<week>_<platform>.zip``."""
    if not brand_id or ".." in brand_id or "/" in brand_id:
        raise HTTPException(status_code=400, detail="Invalid brand_id")
    if not week or ".." in week or "/" in week:
        raise HTTPException(status_code=400, detail="Invalid week")

    if platform is not None:
        plat = platform.strip()
        if not plat or ".." in plat or "/" in plat or "\\" in plat:
            raise HTTPException(status_code=400, detail="Invalid platform")
        if plat not in PLATFORM_SLUGS:
            raise HTTPException(status_code=400, detail=f"Unknown platform '{plat}'")
        zip_path = platform_zip_path(PACKAGES_DIR, brand_id, week, plat)
        if zip_path.is_file() and zip_path.stat().st_size > 0:
            return _stream_zip(zip_path)
        raise HTTPException(
            status_code=404,
            detail=f"No per-platform package for brand '{brand_id}' week '{week}' platform '{plat}'",
        )

    zip_path = monolithic_zip_path(PACKAGES_DIR, brand_id, week)
    if zip_path.is_file() and zip_path.stat().st_size > 0:
        return _stream_zip(zip_path)

    week_dir = PACKAGES_DIR / brand_id / week
    manifest = week_dir / "manifest.json"
    if manifest.is_file():
        raise HTTPException(
            status_code=500,
            detail="Build pipeline incomplete — run build_admin_packets.py or wait for Monday cron logs",
        )

    raise HTTPException(
        status_code=404,
        detail=f"No package for brand '{brand_id}' week '{week}'",
    )
