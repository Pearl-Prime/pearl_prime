#!/usr/bin/env python3
"""Install Metricool creds into macOS Keychain (durable, never prints secrets).

Reads the 64-char API token from the gitignored staging file
``docs/metricool_api.txt`` (or ``--from-file``), ignoring markdown/header lines.
Stores:
  service=phoenix-omega account=METRICOOL_API_KEY
  service=phoenix-omega account=METRICOOL_USER_ID (default 3564167)

Usage:
    python3 scripts/integrations/metricool/install_keychain_creds.py
    python3 scripts/integrations/metricool/install_keychain_creds.py --dry-run
"""

from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_KEY_FILE = REPO_ROOT / "docs" / "metricool_api.txt"
DEFAULT_USER_ID = "3564167"
SERVICE = "phoenix-omega"


def extract_api_key(text: str) -> str:
    """Prefer longest alnum token (Metricool keys are 64-char); never return markdown lines."""
    tokens: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith("**"):
            continue
        if "=" in s and re.search(r"KEY|TOKEN|AUTH", s, re.I):
            s = s.split("=", 1)[1].strip().strip('"').strip("'")
        if re.fullmatch(r"[A-Za-z0-9]{32,128}", s):
            tokens.append(s)
    if not tokens:
        raise ValueError("no token-shaped API key found in key file")
    return max(tokens, key=len)


def extract_user_id(text: str, default: str = DEFAULT_USER_ID) -> str:
    for line in text.splitlines():
        s = line.strip()
        if re.fullmatch(r"\d{5,}", s):
            return s
    return default


def store_keychain(account: str, value: str, *, dry_run: bool) -> None:
    if dry_run:
        digest = hashlib.sha256(value.encode()).hexdigest()[:12]
        print(f"DRY_RUN would store {account} len={len(value)} sha12={digest}")
        return
    subprocess.run(
        [
            "security",
            "add-generic-password",
            "-U",
            "-s",
            SERVICE,
            "-a",
            account,
            "-w",
            value,
        ],
        check=True,
    )
    print(f"STORED {account} (len={len(value)} sha12={hashlib.sha256(value.encode()).hexdigest()[:12]})")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Install Metricool Keychain creds (presence-safe).")
    p.add_argument("--from-file", type=Path, default=DEFAULT_KEY_FILE)
    p.add_argument("--user-id", default=DEFAULT_USER_ID)
    p.add_argument("--dry-run", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.from_file.is_file():
        print(f"ERROR: key file missing: {args.from_file}", file=sys.stderr)
        print("Create gitignored docs/metricool_api.txt or pass --from-file.", file=sys.stderr)
        return 2
    raw = args.from_file.read_text(encoding="utf-8", errors="replace")
    try:
        api_key = extract_api_key(raw)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    user_id = args.user_id if args.user_id != DEFAULT_USER_ID else extract_user_id(raw)
    store_keychain("METRICOOL_API_KEY", api_key, dry_run=args.dry_run)
    store_keychain("METRICOOL_USER_ID", user_id, dry_run=args.dry_run)
    print("NEXT: export METRICOOL_API_KEY/USER_ID from Keychain, then status.py / doctor.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
