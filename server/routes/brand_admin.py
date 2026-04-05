"""
Brand Admin Portal API Routes.

Endpoints:
  POST /api/v1/admin/auth/magic-link — send magic link email
  POST /api/v1/admin/auth/verify — verify token, create session
  POST /api/v1/admin/credentials — store encrypted platform credentials
  GET  /api/v1/admin/credentials/status — check which platforms have credentials
  GET  /api/v1/admin/catalog — list all titles for this brand
  GET  /api/v1/admin/weekly — list weekly packages
  GET  /api/v1/admin/weekly/{week}/{platform} — download platform ZIP
  GET  /api/v1/admin/performance — latest performance report
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Cookie, HTTPException, Response
from pydantic import BaseModel

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

router = APIRouter(prefix="/api/v1/admin", tags=["brand-admin"])


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _load_admin_users() -> dict:
    return _load_yaml(REPO_ROOT / "config" / "brand_management" / "brand_admin_users.yaml")


def _find_admin_by_email(email: str) -> dict | None:
    """Find admin entry by email. Returns {brand_id, admin_name, lane_id} or None."""
    users = _load_admin_users()
    admins = users.get("admins") or {}
    for brand_id, admin_data in admins.items():
        if isinstance(admin_data, dict) and admin_data.get("admin_email") == email:
            return {"brand_id": brand_id, **admin_data}
    return None


def _get_brand_from_session(brand_session: str = Cookie(default="")) -> str:
    """Extract and validate brand_id from session cookie."""
    from server.middleware.brand_auth import validate_session
    if not brand_session:
        raise HTTPException(status_code=401, detail="Not authenticated. Please log in.")
    result = validate_session(brand_session)
    if not result:
        raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
    return result["brand_id"]


# ── Auth endpoints ────────────────────────────────────────────────

class MagicLinkRequest(BaseModel):
    email: str

class VerifyRequest(BaseModel):
    token: str


@router.post("/auth/magic-link")
async def send_magic_link(req: MagicLinkRequest):
    """Send a magic link email to the brand admin."""
    admin = _find_admin_by_email(req.email)
    if not admin:
        # Don't reveal whether email exists
        return {"message": "If this email is registered, a login link has been sent."}

    from server.middleware.brand_auth import create_magic_link_token
    token = create_magic_link_token(req.email, admin["brand_id"])

    # Send email via Brevo SMTP (reuse funnel pattern)
    portal_domain = _load_admin_users().get("portal", {}).get("domain", "catalog.brand-admin-onboarding.pages.dev")
    link = f"https://{portal_domain}/verify?token={token}"

    # TODO: Wire to actual email sender (Brevo SMTP from funnel/)
    logger.info("Magic link for %s: %s", req.email, link)

    return {"message": "If this email is registered, a login link has been sent."}


@router.post("/auth/verify")
async def verify_magic_link(req: VerifyRequest, response: Response):
    """Verify magic link token and create session."""
    from server.middleware.brand_auth import verify_token, create_session
    result = verify_token(req.token)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid or expired token.")

    session_cookie = create_session(result["brand_id"], result["email"])
    response.set_cookie(
        key="brand_session",
        value=session_cookie,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=7 * 24 * 3600,  # 7 days
    )
    return {"brand_id": result["brand_id"], "email": result["email"]}


# ── Credential storage ────────────────────────────────────────────

class CredentialSubmission(BaseModel):
    platform: str
    credentials: dict[str, str]


@router.post("/credentials")
async def store_credentials(req: CredentialSubmission, brand_session: str = Cookie(default="")):
    """Store encrypted platform credentials for the brand."""
    brand_id = _get_brand_from_session(brand_session)

    from server.crypto import encrypt_credentials, decrypt_credentials
    # Load existing credentials and merge
    existing = decrypt_credentials(brand_id) or {}
    existing[req.platform] = req.credentials
    encrypt_credentials(brand_id, existing)

    return {"message": f"Credentials stored for {req.platform}", "brand_id": brand_id}


@router.get("/credentials/status")
async def credential_status(brand_session: str = Cookie(default="")):
    """Check which platforms have stored credentials."""
    brand_id = _get_brand_from_session(brand_session)

    from server.crypto import decrypt_credentials
    creds = decrypt_credentials(brand_id) or {}
    status = {platform: True for platform in creds}

    # Load all expected platforms for this brand's lane
    admin_users = _load_admin_users()
    admins = admin_users.get("admins") or {}
    admin_data = admins.get(brand_id) or {}
    lane_id = admin_data.get("lane_id", "en_US")

    portal = admin_users.get("portal") or {}
    expected_platforms = (portal.get("platforms_by_lane") or {}).get(lane_id, [])

    return {
        "brand_id": brand_id,
        "lane_id": lane_id,
        "platforms": {p: status.get(p, False) for p in expected_platforms},
    }


# ── Catalog endpoints ─────────────────────────────────────────────

@router.get("/catalog")
async def list_catalog(brand_session: str = Cookie(default="")):
    """List all titles for this brand (full catalog)."""
    brand_id = _get_brand_from_session(brand_session)

    catalog_dir = REPO_ROOT / "artifacts" / "weekly_packages" / brand_id
    if not catalog_dir.exists():
        return {"brand_id": brand_id, "titles": [], "total": 0}

    titles = []
    for week_dir in sorted(catalog_dir.iterdir(), reverse=True):
        if not week_dir.is_dir():
            continue
        manifest_path = week_dir / "upload_manifest.csv"
        if manifest_path.exists():
            import csv
            with open(manifest_path) as f:
                reader = csv.DictReader(f)
                for row in reader:
                    row["week"] = week_dir.name
                    titles.append(row)

    return {"brand_id": brand_id, "titles": titles, "total": len(titles)}


@router.get("/weekly")
async def list_weekly_packages(brand_session: str = Cookie(default="")):
    """List available weekly packages."""
    brand_id = _get_brand_from_session(brand_session)

    packages_dir = REPO_ROOT / "artifacts" / "weekly_packages" / brand_id
    if not packages_dir.exists():
        return {"brand_id": brand_id, "weeks": []}

    weeks = []
    for week_dir in sorted(packages_dir.iterdir(), reverse=True):
        if not week_dir.is_dir():
            continue
        manifest = week_dir / "upload_manifest.csv"
        readme = week_dir / "README.txt"
        platforms = [d.name for d in week_dir.iterdir() if d.is_dir()]

        weeks.append({
            "week": week_dir.name,
            "has_manifest": manifest.exists(),
            "has_readme": readme.exists(),
            "platforms": platforms,
            "file_count": sum(1 for _ in week_dir.rglob("*") if _.is_file()),
        })

    return {"brand_id": brand_id, "weeks": weeks}


@router.get("/weekly/{week}/{platform}")
async def download_platform_package(week: str, platform: str, brand_session: str = Cookie(default="")):
    """Download a platform-specific package as ZIP."""
    brand_id = _get_brand_from_session(brand_session)

    platform_dir = REPO_ROOT / "artifacts" / "weekly_packages" / brand_id / week / platform
    if not platform_dir.exists():
        raise HTTPException(status_code=404, detail=f"No {platform} package for week {week}")

    import io
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in platform_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(platform_dir)
                zf.write(file_path, arcname)

    buf.seek(0)
    filename = f"{brand_id}_{week}_{platform}.zip"
    return Response(
        content=buf.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


# ── Performance ───────────────────────────────────────────────────

@router.get("/performance")
async def get_performance(brand_session: str = Cookie(default="")):
    """Get latest performance checkup report."""
    brand_id = _get_brand_from_session(brand_session)

    perf_dir = REPO_ROOT / "artifacts" / "performance" / brand_id
    if not perf_dir.exists():
        return {"brand_id": brand_id, "reports": [], "latest": None}

    reports = sorted(perf_dir.glob("*.json"), reverse=True)
    latest = None
    if reports:
        latest = json.loads(reports[0].read_text(encoding="utf-8"))

    return {
        "brand_id": brand_id,
        "reports": [r.stem for r in reports[:10]],
        "latest": latest,
    }
