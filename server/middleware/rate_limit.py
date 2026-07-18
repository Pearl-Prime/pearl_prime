"""
Simple in-memory per-IP rate limiter.

Not intended for production at scale (use a reverse proxy or Redis-backed
limiter). Sufficient for development and single-instance deployment.
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self._rpm = requests_per_minute
        self._window = 60.0  # seconds
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _client_ip(self, request: Request) -> str:
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    async def dispatch(self, request: Request, call_next: Callable):
        if self._rpm <= 0:
            return await call_next(request)

        ip = self._client_ip(request)
        now = time.monotonic()
        cutoff = now - self._window

        # Prune old entries
        self._hits[ip] = [t for t in self._hits[ip] if t > cutoff]

        if len(self._hits[ip]) >= self._rpm:
            return JSONResponse(
                {"error": "rate_limited", "detail": f"Rate limit exceeded ({self._rpm}/min)"},
                status_code=429,
            )

        self._hits[ip].append(now)
        return await call_next(request)
