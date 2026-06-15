"""
Platform Setup Helper API — write-only credential capture for brand directors.

Powers brand-wizard-app/public/platform_setup_helper.html. REUSES the existing
encrypted vault (server/crypto.py: Fernet → artifacts/admin_credentials/<brand>.enc,
gitignored) — it does NOT introduce a new credential store.

Endpoints:
  POST /api/v1/setup-helper/credentials        — store a platform's login + WRITE-ONLY secret
  GET  /api/v1/setup-helper/credentials/status — which platforms are set (secret_set bool +
                                                  viewable login fields); NEVER returns secrets

Why a separate router from /api/v1/admin/credentials:
  The /admin route is gated behind the magic-link `brand_session` cookie (production portal).
  This helper is the operator-run LOCAL setup tool — it takes brand_id explicitly so a director
  can be walked through setup without the email-auth round-trip. Both write to the SAME vault.
  Decryption is server-side only (Pearl_Int upload); it is never exposed over HTTP here.

Key: ADMIN_CREDENTIAL_KEY (env or macOS Keychain `security … -s phoenix-omega -a ADMIN_CREDENTIAL_KEY`).
Generate: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
"""
from __future__ import annotations

import logging
import re
from typing import Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/setup-helper", tags=["setup-helper"])

_BRAND_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.\-]{0,127}$")
_PLATFORM_RE = re.compile(r"^[a-z0-9][a-z0-9_]{0,63}$")
_SECRET_KEY = "secret"  # the one encrypted, never-returned field within a platform entry


def _validate_brand(brand_id: str) -> str:
    b = (brand_id or "").strip()
    if not _BRAND_RE.fullmatch(b):
        raise HTTPException(status_code=422, detail="invalid brand_id")
    return b


def _validate_platform(platform: str) -> str:
    p = (platform or "").strip()
    if not _PLATFORM_RE.fullmatch(p):
        raise HTTPException(status_code=422, detail="invalid platform")
    return p


class SetupCredSubmission(BaseModel):
    brand_id: str
    platform: str
    username: Optional[Dict[str, str]] = None  # viewable login fields (email/id/url) — manageable
    secret: Optional[str] = None               # write-only secret (password / app-password / token)


@router.post("/credentials")
def store_setup_credentials(req: SetupCredSubmission) -> dict:
    """Merge a platform's viewable login fields and/or its write-only secret into the brand vault."""
    brand_id = _validate_brand(req.brand_id)
    platform = _validate_platform(req.platform)

    try:
        from server.crypto import encrypt_credentials, decrypt_credentials
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"crypto unavailable: {e}") from e

    existing = decrypt_credentials(brand_id) or {}
    entry = dict(existing.get(platform) or {})

    if req.username:
        for k, v in req.username.items():
            if k == _SECRET_KEY:
                continue  # never let a viewable field overwrite the secret slot
            if isinstance(v, str) and len(v) <= 4096:
                entry[k] = v

    # Write-only: only update the secret when a non-empty value is supplied; blank keeps the current one.
    if req.secret:
        if len(req.secret) > 8192:
            raise HTTPException(status_code=422, detail="secret too long")
        entry[_SECRET_KEY] = req.secret

    existing[platform] = entry
    try:
        encrypt_credentials(brand_id, existing)
    except RuntimeError as e:
        # ADMIN_CREDENTIAL_KEY missing / cryptography absent — surface clearly, never fall back to plaintext.
        raise HTTPException(status_code=503, detail=str(e)) from e

    return {
        "status": "saved",
        "brand_id": brand_id,
        "platform": platform,
        "secret_set": bool(entry.get(_SECRET_KEY)),
    }


@router.get("/credentials/status")
def setup_credential_status(brand_id: str = Query(...)) -> dict:
    """Return per-platform {secret_set, username(viewable)}. The secret value is NEVER returned."""
    bid = _validate_brand(brand_id)

    try:
        from server.crypto import decrypt_credentials
    except Exception as e:  # pragma: no cover
        raise HTTPException(status_code=500, detail=f"crypto unavailable: {e}") from e

    creds = decrypt_credentials(bid) or {}
    platforms = {}
    for plat, entry in creds.items():
        e = entry or {}
        viewable = {k: v for k, v in e.items() if k != _SECRET_KEY}
        platforms[plat] = {
            "secret_set": bool(e.get(_SECRET_KEY)),
            "username": viewable,
        }
    return {"brand_id": bid, "platforms": platforms}
