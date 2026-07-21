#!/usr/bin/env python3
"""Metricool durability doctor — one command for SAFE/SUPPORTED/MANAGED health.

Offline by default. Optional ``--network`` probes auth + pin blog (no publish).

Usage:
    python3 scripts/integrations/metricool/doctor.py
    python3 scripts/integrations/metricool/doctor.py --network
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
_PKG = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(_PKG))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "ci"))

import yaml  # noqa: E402

import status as metricool_status  # noqa: E402
import validate_config  # noqa: E402
from client import get_connected_platforms, load_credentials  # noqa: E402

PIN_PATH = REPO_ROOT / "config" / "integrations" / "metricool_waystream_pin.yaml"
BRANDS_MAP = REPO_ROOT / "config" / "integrations" / "metricool_brands.yaml"


def _run_ci_gate() -> dict[str, Any]:
    script = REPO_ROOT / "scripts" / "ci" / "check_metricool_managed.py"
    if not script.is_file():
        return {"ok": False, "detail": "check_metricool_managed.py missing"}
    r = subprocess.run(
        [sys.executable, str(script)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONPATH": f"scripts/ci:scripts/integrations/metricool:{REPO_ROOT}"},
    )
    out = (r.stdout or r.stderr or "").strip().splitlines()
    return {"ok": r.returncode == 0, "detail": out[-1] if out else f"exit={r.returncode}"}


def _load_pin() -> dict[str, Any]:
    data = yaml.safe_load(PIN_PATH.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def network_probe(pin: dict[str, Any]) -> dict[str, Any]:
    creds = load_credentials()
    if not creds.get("api_key") or not creds.get("user_id"):
        return {"ok": False, "detail": "creds missing for network probe"}
    blog_id = str(pin.get("blog_id") or "")
    try:
        resp = get_connected_platforms(
            blog_id=blog_id,
            user_id=creds["user_id"],
            api_key=creds["api_key"],
            base_url=creds.get("base_url") or "",
        )
    except Exception as exc:  # noqa: BLE001 — doctor must report
        return {"ok": False, "detail": f"{type(exc).__name__}: {exc}"}
    label = None
    data = resp.get("data") if isinstance(resp, dict) else None
    if isinstance(data, dict):
        label = data.get("label") or data.get("id")
    elif isinstance(resp, dict):
        label = resp.get("label") or resp.get("id")
    return {"ok": True, "detail": f"settings/brands/{blog_id} ok label={label!r}"}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Metricool durability doctor")
    p.add_argument("--network", action="store_true", help="Probe Metricool API for pin blog_id")
    p.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pin = _load_pin() if PIN_PATH.is_file() else {}
    status_report = metricool_status.collect_status(BRANDS_MAP)
    validation = validate_config.load_and_validate(BRANDS_MAP, strict_blog_ids=True)
    ci = _run_ci_gate()
    report: dict[str, Any] = {
        "subsystem": "metricool",
        "durable": True,
        "ci_gate": ci,
        "config_ok": bool(validation.get("ok")),
        "config_errors": validation.get("errors") or [],
        "pin": {
            "path": str(PIN_PATH),
            "blog_id": pin.get("blog_id"),
            "brand_key": pin.get("brand_key"),
            "proven_draft_post_id": pin.get("proven_draft_post_id"),
        },
        "credentials": status_report.get("credentials"),
        "primary_blocker": status_report.get("primary_blocker"),
        "network_probe": None,
    }
    ok = bool(ci.get("ok") and validation.get("ok"))
    if args.network:
        probe = network_probe(pin)
        report["network_probe"] = probe
        ok = ok and bool(probe.get("ok"))

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("Metricool doctor")
        print(f"  ci_gate     {'OK' if ci.get('ok') else 'FAIL'} — {ci.get('detail')}")
        print(f"  config      {'OK' if validation.get('ok') else 'FAIL'}")
        for e in validation.get("errors") or []:
            print(f"    ERROR: {e}")
        print(f"  pin         {pin.get('brand_key')} blog_id={pin.get('blog_id')}")
        print(f"  proven      postId={pin.get('proven_draft_post_id')}")
        creds = status_report.get("credentials") or {}
        print(f"  API_KEY     {creds.get('METRICOOL_API_KEY')}")
        print(f"  USER_ID     {creds.get('METRICOOL_USER_ID')}")
        if report["network_probe"] is not None:
            np = report["network_probe"]
            print(f"  network     {'OK' if np.get('ok') else 'FAIL'} — {np.get('detail')}")
        print(f"  blocker     {status_report.get('primary_blocker') or 'none'}")
        print("DURABLE=OK" if ok else "DURABLE=FAIL")
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
