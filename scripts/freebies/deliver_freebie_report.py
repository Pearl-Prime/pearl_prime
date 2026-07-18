#!/usr/bin/env python3
"""Dry-run or env-gated dispatch for Waystream freebie reports."""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from scripts.freebies.generate_freebie_report import build_report

CHANNELS = REPO / "config/freebies/report_delivery_channels.yaml"
TEMPLATES = REPO / "config/freebies/report_delivery_templates.yaml"


def _load(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _valid(channel: str, address: str, cfg: dict[str, Any]) -> bool:
    rule = ((cfg.get("validation") or {}).get(channel)) or ""
    if rule == "standard_email":
        return re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", address) is not None
    return bool(rule and re.match(rule, address))


def _required_env(channel: str, cfg: dict[str, Any]) -> list[str]:
    return list(((cfg.get("channels") or {}).get(channel) or {}).get("env_vars") or [])


def _render_template(channel: str, report: dict[str, Any]) -> dict[str, str]:
    templates = (_load(TEMPLATES).get("templates") or {})
    template = templates[channel]
    values = {
        "tool_name": report["source_page_slug"].replace("-", " "),
        "report_title": report["title"],
        "report_summary": report["summary"],
        "recommended_practice": report["sections"]["recommended_practice"],
    }
    return {key: value.format(**values) for key, value in template.items()}


def sanitized_payload(channel: str, address: str, report: dict[str, Any]) -> dict[str, Any]:
    redacted = address[:2] + "***" + address[-2:] if len(address) > 4 else "***"
    return {
        "channel": channel,
        "address_redacted": redacted,
        "report_id": report["report_id"],
        "source_page_slug": report["source_page_slug"],
        "message": _render_template(channel, report),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Dispatch a Waystream freebie report.")
    parser.add_argument("--channel", required=True, choices=["whatsapp", "telegram", "email", "line", "messenger"])
    parser.add_argument("--address", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    cfg = _load(CHANNELS)
    if not _valid(args.channel, args.address, cfg):
        raise SystemExit(f"invalid {args.channel} address")
    report = build_report(args.slug)
    payload = sanitized_payload(args.channel, args.address, report)
    if args.dry_run:
        print(json.dumps({"dry_run": True, "payload": payload}, indent=2, sort_keys=True))
        return 0
    missing = [name for name in _required_env(args.channel, cfg) if not os.environ.get(name)]
    if missing:
        raise SystemExit(f"missing required env for {args.channel}: {', '.join(missing)}")
    raise SystemExit("live delivery adapter intentionally env-gated; use provider implementation after credential setup")


if __name__ == "__main__":
    raise SystemExit(main())
