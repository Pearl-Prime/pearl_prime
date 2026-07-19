#!/usr/bin/env python3
"""Managed Metricool subsystem status — presence-only, never prints secrets.

Surfaces credential presence, brand wiring counts, pending blog_ids, config path,
network kill-switch, live-publish gate, and optional git tip.

Usage:
    eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
    python3 scripts/integrations/metricool/status.py
    python3 scripts/integrations/metricool/status.py --json
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
_PKG_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(_PKG_DIR))

from client import DEFAULT_BASE_URL, load_credentials  # noqa: E402
import post as metricool_post  # noqa: E402
import validate_config  # noqa: E402


def _git_tip() -> dict[str, str]:
    out: dict[str, str] = {"branch": "unknown", "sha": "unknown"}
    try:
        branch = subprocess.check_output(
            ["git", "branch", "--show-current"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        out["branch"] = branch or "DETACHED"
        out["sha"] = sha
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass
    return out


def network_env_allowed() -> bool:
    return os.environ.get("METRICOOL_ALLOW_NETWORK", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def collect_status(
    brands_map_path: Path = metricool_post.BRANDS_MAP_PATH,
) -> dict[str, Any]:
    creds = load_credentials()
    api_key_set = bool(creds.get("api_key"))
    user_id_set = bool(creds.get("user_id"))
    user_id_value = creds.get("user_id") or ""
    base_url = creds.get("base_url") or DEFAULT_BASE_URL

    validation: dict[str, Any]
    try:
        validation = validate_config.load_and_validate(brands_map_path)
    except Exception as exc:  # noqa: BLE001 — status must not crash
        validation = {"ok": False, "errors": [str(exc)], "warnings": []}

    brand_map = None
    pending: list[str] = []
    wired_real = 0
    try:
        brand_map = metricool_post.load_brand_map(brands_map_path)
        for key, row in (brand_map.get("brands") or {}).items():
            if not isinstance(row, dict):
                continue
            status = (row.get("status") or "").strip().lower()
            blog_id = "" if row.get("blog_id") is None else str(row.get("blog_id")).strip()
            if status == "wired":
                if metricool_post.is_placeholder_blog_id(blog_id):
                    pending.append(key)
                elif blog_id:
                    wired_real += 1
    except metricool_post.MetricoolConfigError as exc:
        validation.setdefault("errors", []).append(str(exc))

    tip = _git_tip()
    primary_blocker: str | None = None
    if not api_key_set or not user_id_set:
        primary_blocker = "Q-METRIC-CREDS"
    elif pending:
        primary_blocker = "Q-METRIC-02"
    elif not metricool_post.LIVE_PUBLISH_OPERATOR_APPROVED:
        # Not a pilot blocker — scale gate only
        pass

    return {
        "subsystem": "metricool",
        "managed": True,
        "credentials": {
            "METRICOOL_API_KEY": "set" if api_key_set else "MISSING",
            "METRICOOL_USER_ID": user_id_value if user_id_set else "MISSING",
            "METRICOOL_BASE_URL": base_url,
        },
        "brands_map_path": str(brands_map_path),
        "account": (brand_map or {}).get("account") if brand_map else None,
        "brand_count": validation.get("brand_count"),
        "wired_count": validation.get("wired_count"),
        "unwired_count": validation.get("unwired_count"),
        "wired_with_real_blog_id": wired_real,
        "blog_id_pending": pending,
        "config_ok": bool(validation.get("ok")),
        "config_errors": validation.get("errors") or [],
        "config_warnings": validation.get("warnings") or [],
        "network_kill_switch": {
            "METRICOOL_ALLOW_NETWORK": "ON" if network_env_allowed() else "OFF (default)",
            "note": "post.py refuses HTTP unless --dry-run or --network or METRICOOL_ALLOW_NETWORK=1",
        },
        "live_publish_approved": bool(metricool_post.LIVE_PUBLISH_OPERATOR_APPROVED),
        "q_metric_01": "OPEN" if not metricool_post.LIVE_PUBLISH_OPERATOR_APPROVED else "APPROVED",
        "git": tip,
        "primary_blocker": primary_blocker,
        "runbook": "docs/runbooks/METRICOOL_POSTING_RUNBOOK.md",
    }


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Metricool managed-system status (no secrets).")
    p.add_argument("--brands-map", type=Path, default=metricool_post.BRANDS_MAP_PATH)
    p.add_argument("--json", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = collect_status(args.brands_map)

    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("Metricool managed status")
        print(f"  API_KEY      {report['credentials']['METRICOOL_API_KEY']}")
        print(f"  USER_ID      {report['credentials']['METRICOOL_USER_ID']}")
        print(f"  BASE         {report['credentials']['METRICOOL_BASE_URL']}")
        print(f"  brands_map   {report['brands_map_path']}")
        print(
            f"  brands       count={report['brand_count']} "
            f"wired={report['wired_count']} unwired={report['unwired_count']} "
            f"real_blog_id={report['wired_with_real_blog_id']}"
        )
        if report["blog_id_pending"]:
            print(f"  pending      {', '.join(report['blog_id_pending'])}")
        print(f"  config       {'OK' if report['config_ok'] else 'FAIL'}")
        for e in report["config_errors"]:
            print(f"    ERROR: {e}")
        for w in report["config_warnings"]:
            print(f"    WARN: {w}")
        nk = report["network_kill_switch"]
        print(f"  network      {nk['METRICOOL_ALLOW_NETWORK']}")
        print(f"  live_gate    Q-METRIC-01={report['q_metric_01']}")
        print(f"  git          {report['git']['branch']} @ {report['git']['sha'][:12]}")
        print(f"  runbook      {report['runbook']}")
        if report["primary_blocker"]:
            print(f"PRIMARY_BLOCKER={report['primary_blocker']}")
        else:
            print("PRIMARY_BLOCKER=none (draft pilot may still need real blog_id check via preflight)")

    return 0 if report["config_ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
