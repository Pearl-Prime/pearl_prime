#!/usr/bin/env python3
"""Optional live GHL inbound webhook push test for phoenix_lead capture payload."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load_yaml(p: Path) -> dict:
    import yaml
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def main() -> int:
    cfg = _load_yaml(REPO / "config/freebies/ghl_funnel_capture.yaml")
    env_name = cfg.get("webhook_env") or "PHOENIX_GHL_FUNNEL_WEBHOOK"
    webhook = os.environ.get(env_name, "").strip()
    if not webhook:
        print(f"SKIP: {env_name} unset — cannot live-push to GHL (operator must provision inbound webhook)")
        return 0

    payload = {
        "email": "freebie-smoke-test@example.com",
        "first_name": "Smoke",
        "quiz_id": "capacity_assessment",
        "topic": "compassion_fatigue",
        "funnel_slug": "compassion-fatigue-audit",
        "score": 12,
        "score_band": "medium",
        "tags": ["smoke_test", "freebie_capture"],
    }
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read(500).decode("utf-8", errors="replace")
            print(f"OK: GHL webhook responded {resp.status} — {body[:200]}")
            return 0
    except urllib.error.HTTPError as e:
        print(f"FAIL: GHL webhook HTTP {e.code} — {e.read(300).decode('utf-8', errors='replace')}")
        return 1
    except Exception as e:
        print(f"FAIL: GHL webhook error — {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
