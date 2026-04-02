"""
Server configuration loader.

Reads config/server.yaml with env-var overrides.
Authority: docs/SERVER_INFRASTRUCTURE_SPEC.md
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List

import yaml


def _repo_root() -> Path:
    """Walk up from this file to find the repo root (contains config/)."""
    p = Path(__file__).resolve().parent.parent
    if (p / "config").is_dir():
        return p
    # Fallback: cwd
    return Path.cwd()


@dataclass
class HealthConfig:
    ci_stale_seconds: int = 7200
    required_files: List[str] = field(default_factory=lambda: [
        "config/governance/system_registry.yaml",
        "config/source_of_truth/master_arc_registry.yaml",
        "phoenix_v4/__init__.py",
    ])


@dataclass
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "info"
    workers: int = 1
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    api_key: str = ""
    rate_limit_rpm: int = 120
    repo_root: str = "."
    artifacts_dir: str = "artifacts"
    config_dir: str = "config"
    health: HealthConfig = field(default_factory=HealthConfig)

    @classmethod
    def load(cls, config_path: Path | None = None) -> "ServerConfig":
        root = _repo_root()
        if config_path is None:
            config_path = root / "config" / "server.yaml"

        raw: dict = {}
        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                raw = yaml.safe_load(f) or {}

        # Env-var overrides
        env_map = {
            "PHOENIX_HOST": "host",
            "PHOENIX_PORT": "port",
            "PHOENIX_LOG_LEVEL": "log_level",
            "PHOENIX_API_KEY": "api_key",
            "PHOENIX_CORS_ORIGINS": "cors_origins",
            "PHOENIX_WORKERS": "workers",
            "PHOENIX_RATE_LIMIT_RPM": "rate_limit_rpm",
        }
        for env_key, cfg_key in env_map.items():
            val = os.environ.get(env_key)
            if val is not None:
                raw[cfg_key] = val

        # Parse health sub-config
        health_raw = raw.pop("health", {})
        health = HealthConfig(
            ci_stale_seconds=int(health_raw.get("ci_stale_seconds", 7200)),
            required_files=health_raw.get("required_files", HealthConfig().required_files),
        )

        return cls(
            host=str(raw.get("host", "0.0.0.0")),
            port=int(raw.get("port", 8000)),
            log_level=str(raw.get("log_level", "info")),
            workers=int(raw.get("workers", 1)),
            cors_origins=str(raw.get("cors_origins", "http://localhost:3000")),
            api_key=str(raw.get("api_key", "")),
            rate_limit_rpm=int(raw.get("rate_limit_rpm", 120)),
            repo_root=str(raw.get("repo_root", ".")),
            artifacts_dir=str(raw.get("artifacts_dir", "artifacts")),
            config_dir=str(raw.get("config_dir", "config")),
            health=health,
        )

    def get_repo_root(self) -> Path:
        p = Path(self.repo_root)
        if not p.is_absolute():
            p = _repo_root() / p
        return p.resolve()

    def get_cors_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]
