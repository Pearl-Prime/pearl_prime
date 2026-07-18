"""
Magic link authentication for brand admin portal.

Flow:
1. Admin enters email → POST /auth/magic-link
2. Backend sends email with token link
3. Admin clicks link → POST /auth/verify with token
4. Backend sets HTTP-only session cookie (7 days)
5. All subsequent requests check cookie → resolve brand_id

Token storage: in-memory dict with 30-minute TTL.
Session storage: signed cookies (HMAC via SECRET_KEY).
"""
from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import time
import uuid
from typing import Optional

logger = logging.getLogger(__name__)

# In-memory token store: {token: {email, brand_id, created_at}}
_PENDING_TOKENS: dict[str, dict] = {}
TOKEN_TTL_S = 1800  # 30 minutes

# Session: {session_id: {brand_id, email, created_at}}
_SESSIONS: dict[str, dict] = {}
SESSION_TTL_S = 7 * 24 * 3600  # 7 days

SECRET_KEY = os.environ.get("PORTAL_SECRET_KEY", "dev-portal-secret-change-in-prod")


def _clean_expired() -> None:
    """Remove expired tokens and sessions."""
    now = time.time()
    expired_tokens = [k for k, v in _PENDING_TOKENS.items() if now - v["created_at"] > TOKEN_TTL_S]
    for k in expired_tokens:
        del _PENDING_TOKENS[k]
    expired_sessions = [k for k, v in _SESSIONS.items() if now - v["created_at"] > SESSION_TTL_S]
    for k in expired_sessions:
        del _SESSIONS[k]


def create_magic_link_token(email: str, brand_id: str) -> str:
    """Create a one-time magic link token for email verification."""
    _clean_expired()
    token = str(uuid.uuid4())
    _PENDING_TOKENS[token] = {
        "email": email,
        "brand_id": brand_id,
        "created_at": time.time(),
    }
    return token


def verify_token(token: str) -> Optional[dict]:
    """Verify a magic link token. Returns {email, brand_id} or None.

    Token is consumed (one-time use).
    """
    _clean_expired()
    entry = _PENDING_TOKENS.pop(token, None)
    if not entry:
        return None
    return {"email": entry["email"], "brand_id": entry["brand_id"]}


def create_session(brand_id: str, email: str) -> str:
    """Create a session and return the session_id (to be set as cookie)."""
    _clean_expired()
    session_id = str(uuid.uuid4())
    _SESSIONS[session_id] = {
        "brand_id": brand_id,
        "email": email,
        "created_at": time.time(),
    }
    # Sign the session_id so cookie can't be forged
    sig = hmac.new(SECRET_KEY.encode(), session_id.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{session_id}.{sig}"


def validate_session(signed_session: str) -> Optional[dict]:
    """Validate a signed session cookie. Returns {brand_id, email} or None."""
    _clean_expired()
    if "." not in signed_session:
        return None
    session_id, sig = signed_session.rsplit(".", 1)
    expected_sig = hmac.new(SECRET_KEY.encode(), session_id.encode(), hashlib.sha256).hexdigest()[:16]
    if not hmac.compare_digest(sig, expected_sig):
        return None
    entry = _SESSIONS.get(session_id)
    if not entry:
        return None
    return {"brand_id": entry["brand_id"], "email": entry["email"]}


def get_brand_id_from_request(cookies: dict) -> Optional[str]:
    """Extract brand_id from request cookies."""
    session_cookie = cookies.get("brand_session", "")
    if not session_cookie:
        return None
    result = validate_session(session_cookie)
    return result["brand_id"] if result else None
