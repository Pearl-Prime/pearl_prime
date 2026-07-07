from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_wrangler_config_points_to_pearl_prime_worker() -> None:
    config = json.loads((REPO_ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))

    assert config["name"] == "pearl-prime"
    assert config["main"] == "cloudflare/pearl_prime_worker.js"
    assert (REPO_ROOT / config["main"]).exists()


def test_root_package_json_pins_wrangler_for_workers_builds() -> None:
    manifest = json.loads((REPO_ROOT / "package.json").read_text(encoding="utf-8"))
    lockfile = REPO_ROOT / "package-lock.json"

    assert manifest.get("private") is True
    assert "wrangler" in manifest.get("devDependencies", {})
    assert lockfile.exists()
    assert "deploy" in manifest.get("scripts", {})


def test_worker_contract_exposes_health_shape() -> None:
    worker = (REPO_ROOT / "cloudflare" / "pearl_prime_worker.js").read_text(encoding="utf-8")

    assert 'url.pathname === "/"' in worker
    assert 'url.pathname === "/healthz"' in worker
    assert 'service: "pearl-prime"' in worker
    assert 'status: "ok"' in worker
