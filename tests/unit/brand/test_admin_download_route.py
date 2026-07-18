"""Tests for server.routes.brand_admin_download (OPD-120)."""

from __future__ import annotations

import json
import zipfile
from datetime import datetime, timedelta, timezone
from io import BytesIO
from pathlib import Path

import pytest

pytest.importorskip("fastapi")
from fastapi.testclient import TestClient  # noqa: E402

from server.app import create_app  # noqa: E402
from server.config import ServerConfig  # noqa: E402


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    coord = tmp_path / "artifacts" / "coordination"
    coord.mkdir(parents=True, exist_ok=True)
    mon = (datetime.now(tz=timezone.utc).date() - timedelta(days=datetime.now().weekday()))
    tsv = coord / f"weekly_packages_{mon.isoformat()}.tsv"
    tsv.write_text("brand_id\tweek_iso\tdeliverable_type\tstatus\n", encoding="utf-8")

    monkeypatch.setattr("server.routes.brand_admin_download.REPO_ROOT", tmp_path)
    monkeypatch.setattr("server.routes.brand_admin_download.COORD_DIR", coord)
    monkeypatch.setattr("server.routes.brand_admin_download.PACKAGES_DIR", tmp_path / "artifacts" / "weekly_packages")

    cfg = ServerConfig.load()
    cfg.api_key = ""
    return TestClient(create_app(cfg))


def test_coordination_status_current(client: TestClient) -> None:
    r = client.get("/api/brand_admin/coordination-status")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] in ("CURRENT", "STALE", "MISSING")
    assert "relative" in data


def test_download_zip_200(client: TestClient, tmp_path: Path) -> None:
    brand, week = "alpha_brand", "2026-W20"
    pkg = tmp_path / "artifacts" / "weekly_packages" / brand / week
    pkg.mkdir(parents=True, exist_ok=True)
    zpath = pkg / f"{brand}_{week}.zip"
    buf = BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("manifest.json", json.dumps({"brand_id": brand}))
    zpath.write_bytes(buf.getvalue())

    r = client.get(f"/api/brand_admin/download/{brand}/{week}")
    assert r.status_code == 200
    assert r.headers["content-type"] == "application/zip"
    assert len(r.content) > 0


def test_download_404_missing(client: TestClient) -> None:
    r = client.get("/api/brand_admin/download/no_such_brand/2099-W99")
    assert r.status_code == 404
    assert "No package" in r.json()["detail"]


def test_download_500_manifest_only(client: TestClient, tmp_path: Path) -> None:
    brand, week = "beta_brand", "2026-W20"
    pkg = tmp_path / "artifacts" / "weekly_packages" / brand / week
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "manifest.json").write_text("{}", encoding="utf-8")

    r = client.get(f"/api/brand_admin/download/{brand}/{week}")
    assert r.status_code == 500
    assert "build_admin_packets" in r.json()["detail"].lower() or "pipeline" in r.json()["detail"].lower()
