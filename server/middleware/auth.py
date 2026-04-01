"""
API-key authentication middleware.

When config.api_key is non-empty, every request (except /health and /ready)
must carry header  X-API-Key: <key>.
"""
from __future__ import annotations

import hmac
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

# Paths that never require auth
_PUBLIC_PATHS = frozenset({"/health", "/ready", "/docs", "/openapi.json", "/redoc"})


class APIKeyMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, api_key: str = ""):
        super().__init__(app)
        self._api_key = api_key

    async def dispatch(self, request: Request, call_next: Callable):
        # Skip auth if no key configured or path is public
        if not self._api_key or request.url.path in _PUBLIC_PATHS:
            return await call_next(request)

        provided = request.headers.get("X-API-Key", "")
        if not provided or not hmac.compare_digest(provided, self._api_key):
            return JSONResponse(
                {"error": "unauthorized", "detail": "Missing or invalid X-API-Key header"},
                status_code=401,
            )
        return await call_next(request)
