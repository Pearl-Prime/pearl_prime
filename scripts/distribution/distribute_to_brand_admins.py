#!/usr/bin/env python3
"""Distribute a notification to every admin channel listed for a brand.

Usage:
    python3 scripts/distribution/distribute_to_brand_admins.py \
        --brand default --message "Build 42 is live"

    python3 scripts/distribution/distribute_to_brand_admins.py \
        --brand default --file artifacts/report.pdf --dry-run

Reads brand -> admin-channel mappings from
``config/messaging/brand_admin_channels.yaml`` and invokes the
``send_message.py`` handler for each entry.

Zero new pip dependencies -- reuses send_message internals.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError as exc:  # pragma: no cover
    raise SystemExit("PyYAML is required") from exc

REPO_ROOT = Path(__file__).resolve().parents[2]
BRAND_CONFIG = REPO_ROOT / "config" / "messaging" / "brand_admin_channels.yaml"

# Import the send_message module from our integrations directory.
sys.path.insert(0, str(REPO_ROOT / "scripts" / "integrations"))
import send_message as sm  # noqa: E402


def load_brand_admins(brand: str) -> list[dict]:
    """Return the list of admin channel entries for *brand*."""
    if not BRAND_CONFIG.exists():
        raise SystemExit(f"Missing brand admin config: {BRAND_CONFIG}")
    with BRAND_CONFIG.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    for entry in data.get("brands", []):
        if entry.get("brand") == brand:
            return entry.get("admins", [])
    raise SystemExit(f"Brand '{brand}' not found in {BRAND_CONFIG}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fan-out a message or file to all admin channels for a brand."
    )
    parser.add_argument("--brand", required=True, help="Brand slug to notify.")
    parser.add_argument("--message", default=None, help="Text to send.")
    parser.add_argument("--file", default=None, dest="file_path", help="File to upload.")
    parser.add_argument("--dry-run", action="store_true", help="Print payloads only.")
    args = parser.parse_args()

    if not args.message and not args.file_path:
        raise SystemExit("Either --message or --file is required.")

    admins = load_brand_admins(args.brand)
    channels = sm.load_config()
    results: list[dict] = []

    for admin in admins:
        ch = admin.get("channel")
        to = admin.get("to")
        if not ch or not to:
            print(f"[skip] incomplete admin entry: {admin}", file=sys.stderr)
            continue
        cfg = channels.get(ch, {})
        if not cfg.get("enabled"):
            print(f"[skip] channel '{ch}' not enabled locally", file=sys.stderr)
            continue

        try:
            if args.file_path:
                handler = sm.FILE_HANDLERS.get(ch)
                if not handler:
                    print(f"[skip] no file handler for '{ch}'", file=sys.stderr)
                    continue
                result = handler(cfg, to, args.file_path, args.dry_run)
            else:
                handler = sm.TEXT_HANDLERS.get(ch)
                if not handler:
                    print(f"[skip] no text handler for '{ch}'", file=sys.stderr)
                    continue
                result = handler(cfg, to, args.message, args.dry_run)
            results.append({"channel": ch, "to": to, "result": result})
        except SystemExit as exc:
            results.append({"channel": ch, "to": to, "error": str(exc)})

    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if all("error" not in r for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
