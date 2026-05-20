"""
Phoenix Omega — FastAPI application factory.

Usage:
    # Dev
    python scripts/run_server.py
    # Or directly:
    uvicorn server.app:create_app --factory --reload

Authority: docs/SERVER_INFRASTRUCTURE_SPEC.md
"""
from __future__ import annotations

import logging
from functools import lru_cache

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from server.config import ServerConfig
from server.middleware.auth import APIKeyMiddleware
from server.middleware.rate_limit import RateLimitMiddleware
from server.routes import health, system, catalog, config_api, brand_admin_download

logger = logging.getLogger("phoenix.server")

_settings: ServerConfig | None = None


def get_settings() -> ServerConfig:
    """Return the active server config (set during create_app)."""
    global _settings
    if _settings is None:
        _settings = ServerConfig.load()
    return _settings


def create_app(config: ServerConfig | None = None) -> FastAPI:
    """Build and return the FastAPI application."""
    global _settings
    if config is None:
        config = ServerConfig.load()
    _settings = config

    app = FastAPI(
        title="Phoenix Omega API",
        description=(
            "REST API for the Phoenix therapeutic audio operating system. "
            "Provides catalog management, system health, configuration, "
            "and pipeline access endpoints."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Middleware (order matters: outermost first)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.get_cors_list(),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RateLimitMiddleware, requests_per_minute=config.rate_limit_rpm)
    app.add_middleware(APIKeyMiddleware, api_key=config.api_key)

    # Routes
    app.include_router(health.router)
    app.include_router(system.router)
    app.include_router(catalog.router)
    app.include_router(config_api.router)
    app.include_router(brand_admin_download.router)

    @app.on_event("startup")
    async def _startup():
        logger.info(
            "Phoenix Omega API starting — host=%s port=%s repo_root=%s",
            config.host, config.port, config.get_repo_root(),
        )

    return app
