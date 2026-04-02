from __future__ import annotations

import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_wrangler_config_points_to_pearl_prime_worker() -> None:
    config = json.loads((REPO_ROOT / "wrangler.jsonc").read_text(encoding="utf-8"))

    assert config["name"] == "pearl-prime"
    assert config["main"] == "cloudflare/pearl_prime_worker.js"
    assert (REPO_ROOT / config["main"]).exists()


def test_worker_contract_exposes_health_shape() -> None:
    worker = (REPO_ROOT / "cloudflare" / "pearl_prime_worker.js").read_text(encoding="utf-8")

    assert 'url.pathname === "/"' in worker
    assert 'url.pathname === "/healthz"' in worker
    assert 'service: "pearl-prime"' in worker
    assert 'status: "ok"' in worker
