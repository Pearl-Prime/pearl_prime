"""
Tests for Phoenix Omega API server — health, system, catalog endpoints.

Run:  PYTHONPATH=. pytest tests/test_server_health.py -v
Requires: pip install httpx fastapi uvicorn
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure repo root on path
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))

try:
    from fastapi.testclient import TestClient
    from server.app import create_app
    from server.config import ServerConfig
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False

pytestmark = pytest.mark.skipif(not HAS_FASTAPI, reason="fastapi/httpx not installed")


@pytest.fixture
def client():
    """Create a test client with default config."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def auth_client():
    """Create a test client with API key auth enabled."""
    cfg = ServerConfig.load()
    cfg.api_key = "test-secret-key"
    app = create_app(cfg)
    return TestClient(app)


class TestHealth:
    def test_health_returns_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        data = r.json()
        assert "status" in data
        assert "uptime_seconds" in data

    def test_ready_returns_status(self, client):
        r = client.get("/ready")
        # May be 200 or 503 depending on repo state
        assert r.status_code in (200, 503)
        data = r.json()
        assert "status" in data


class TestAuth:
    def test_public_paths_no_auth(self, auth_client):
        """Health and docs should be accessible without API key."""
        for path in ["/health", "/ready", "/docs", "/openapi.json"]:
            r = auth_client.get(path)
            assert r.status_code != 401, f"{path} should not require auth"

    def test_api_requires_key(self, auth_client):
        """API endpoints should require X-API-Key when configured."""
        r = auth_client.get("/api/v1/system/info")
        assert r.status_code == 401

    def test_api_with_valid_key(self, auth_client):
        """API endpoints should work with correct key."""
        r = auth_client.get(
            "/api/v1/system/info",
            headers={"X-API-Key": "test-secret-key"},
        )
        assert r.status_code == 200

    def test_api_with_wrong_key(self, auth_client):
        """API endpoints should reject wrong key."""
        r = auth_client.get(
            "/api/v1/system/info",
            headers={"X-API-Key": "wrong-key"},
        )
        assert r.status_code == 401


class TestSystem:
    def test_system_info(self, client):
        r = client.get("/api/v1/system/info")
        assert r.status_code == 200
        data = r.json()
        assert data["project"] == "phoenix_omega"
        assert "git" in data

    def test_system_registry(self, client):
        r = client.get("/api/v1/system/registry")
        assert r.status_code == 200
        assert "registry" in r.json()

    def test_docs_list(self, client):
        r = client.get("/api/v1/system/docs")
        assert r.status_code == 200
        data = r.json()
        assert "docs" in data
        assert "count" in data


class TestCatalog:
    def test_list_brands(self, client):
        r = client.get("/api/v1/catalog/brands")
        assert r.status_code == 200
        assert "brands" in r.json()

    def test_list_topics(self, client):
        r = client.get("/api/v1/catalog/topics")
        assert r.status_code == 200
        assert "topics" in r.json()

    def test_list_arcs(self, client):
        r = client.get("/api/v1/catalog/arcs")
        assert r.status_code == 200
        data = r.json()
        assert "arcs" in data
        assert "count" in data

    def test_list_plans(self, client):
        r = client.get("/api/v1/catalog/plans")
        assert r.status_code == 200

    def test_validate_plan_missing_arc(self, client):
        r = client.post("/api/v1/catalog/validate", json={"topic": "burnout"})
        assert r.status_code == 422
        detail = r.json()["detail"]
        assert any("arc_id" in e for e in detail["validation_errors"])

    def test_validate_plan_valid(self, client):
        plan = {
            "arc_id": "arc_001",
            "persona": "gen_z_professional",
            "topic": "burnout",
            "engine": "shame",
            "chapters": [{"slot": "HOOK"}, {"slot": "STORY"}],
        }
        r = client.post("/api/v1/catalog/validate", json=plan)
        assert r.status_code == 200
        data = r.json()
        assert data["valid"] is True
        assert data["chapter_count"] == 2


class TestConfig:
    def test_quality_config(self, client):
        r = client.get("/api/v1/config/quality")
        assert r.status_code == 200
        assert "quality" in r.json()

    def test_governance_config(self, client):
        r = client.get("/api/v1/config/governance")
        assert r.status_code == 200
        assert "governance" in r.json()

    def test_teacher_config(self, client):
        r = client.get("/api/v1/config/teachers")
        assert r.status_code == 200
