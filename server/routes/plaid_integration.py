"""
Plaid Integration — Bank connection + monthly ACH revenue collection.

Flow:
1. Admin clicks "Connect Bank" → create Plaid Link token
2. Plaid Link opens → admin authorizes bank (we never see credentials)
3. Exchange public_token for access_token → store encrypted
4. Monthly: calculate 4.8% of revenue → ACH to Pearl Prime + 48 Social

Requires: PLAID_CLIENT_ID, PLAID_SECRET env vars (or Keychain).
Plaid environments: sandbox → development → production.
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, Cookie, HTTPException
from pydantic import BaseModel

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import plaid
    from plaid.api import plaid_api
    from plaid.model.link_token_create_request import LinkTokenCreateRequest
    from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
    from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
    from plaid.model.products import Products
    from plaid.model.country_code import CountryCode
    PLAID_AVAILABLE = True
except ImportError:
    PLAID_AVAILABLE = False
    logger.warning("plaid-python not installed — Plaid integration unavailable")

try:
    import yaml
except ImportError:
    yaml = None

router = APIRouter(prefix="/api/v1/admin/plaid", tags=["plaid"])


def _get_plaid_config() -> dict:
    """Load Plaid config from brand_admin_users.yaml."""
    path = REPO_ROOT / "config" / "brand_management" / "brand_admin_users.yaml"
    if not path.exists() or yaml is None:
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("plaid") or {}


def _get_plaid_client() -> Any:
    """Create Plaid API client."""
    if not PLAID_AVAILABLE:
        raise HTTPException(status_code=503, detail="Plaid SDK not installed")

    client_id = os.environ.get("PLAID_CLIENT_ID", "")
    secret = os.environ.get("PLAID_SECRET", "")
    if not client_id or not secret:
        raise HTTPException(status_code=503, detail="PLAID_CLIENT_ID or PLAID_SECRET not configured")

    config = _get_plaid_config()
    env = config.get("environment", "sandbox")

    plaid_env = {
        "sandbox": plaid.Environment.Sandbox,
        "development": plaid.Environment.Development,
        "production": plaid.Environment.Production,
    }.get(env, plaid.Environment.Sandbox)

    configuration = plaid.Configuration(
        host=plaid_env,
        api_key={"clientId": client_id, "secret": secret},
    )
    api_client = plaid.ApiClient(configuration)
    return plaid_api.PlaidApi(api_client)


def _get_brand_from_session(brand_session: str) -> str:
    """Extract brand_id from session cookie."""
    from server.middleware.brand_auth import validate_session
    if not brand_session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    result = validate_session(brand_session)
    if not result:
        raise HTTPException(status_code=401, detail="Session expired")
    return result["brand_id"]


# ── Endpoints ─────────────────────────────────────────────────────

class PlaidExchangeRequest(BaseModel):
    public_token: str


@router.post("/link-token")
async def create_link_token(brand_session: str = Cookie(default="")):
    """Create a Plaid Link token for the brand admin to connect their bank.

    The admin's browser opens Plaid Link with this token.
    They authorize their bank account — we never see their bank credentials.
    """
    brand_id = _get_brand_from_session(brand_session)
    client = _get_plaid_client()

    request = LinkTokenCreateRequest(
        products=[Products("transfer")],
        client_name="Phoenix Protocol Books",
        country_codes=[CountryCode("US")],
        language="en",
        user=LinkTokenCreateRequestUser(client_user_id=brand_id),
    )

    response = client.link_token_create(request)
    return {"link_token": response.link_token, "brand_id": brand_id}


@router.post("/exchange")
async def exchange_public_token(req: PlaidExchangeRequest, brand_session: str = Cookie(default="")):
    """Exchange Plaid public_token for access_token.

    Called after admin completes Plaid Link.
    Access token is encrypted and stored — never exposed to frontend.
    """
    brand_id = _get_brand_from_session(brand_session)
    client = _get_plaid_client()

    exchange_request = ItemPublicTokenExchangeRequest(public_token=req.public_token)
    response = client.item_public_token_exchange(exchange_request)

    # Store encrypted
    from server.crypto import encrypt_credentials, decrypt_credentials
    existing = decrypt_credentials(brand_id) or {}
    existing["plaid"] = {
        "access_token": response.access_token,
        "item_id": response.item_id,
        "connected_at": datetime.utcnow().isoformat(),
    }
    encrypt_credentials(brand_id, existing)

    return {"message": "Bank connected successfully", "brand_id": brand_id}


@router.get("/status")
async def plaid_status(brand_session: str = Cookie(default="")):
    """Check if bank is connected for this brand."""
    brand_id = _get_brand_from_session(brand_session)

    from server.crypto import decrypt_credentials
    creds = decrypt_credentials(brand_id) or {}
    plaid_data = creds.get("plaid") or {}

    return {
        "brand_id": brand_id,
        "bank_connected": bool(plaid_data.get("access_token")),
        "connected_at": plaid_data.get("connected_at"),
    }
