#!/usr/bin/env python3
"""Install Storyblocks API keys into macOS Keychain (never prints secret values).

Reads a gitignored staging file (default ``docs/storyblocks_keys.env``) with:

    STORYBLOCKS_PUBLIC_KEY=...
    STORYBLOCKS_PRIVATE_KEY=...

Stores under Keychain service ``phoenix-omega`` (same as
``scripts/ci/load_integration_env_from_keychain.py``).

Usage:
    python3 scripts/storyblocks/install_keychain_creds.py
    python3 scripts/storyblocks/install_keychain_creds.py --from-file docs/storyblocks_keys.env
    python3 scripts/storyblocks/install_keychain_creds.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_KEY_FILE = REPO_ROOT / "docs" / "storyblocks_keys.env"
SERVICE = "phoenix-omega"
REQUIRED = ("STORYBLOCKS_PUBLIC_KEY", "STORYBLOCKS_PRIVATE_KEY")


def parse_env_file(text: str) -> dict[str, str]:
    """Parse KEY=val env, or labeled lines like ``API Public Key: <token>``."""
    out: dict[str, str] = {}
    bare: list[str] = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        lower = s.lower()
        if "=" in s and s.split("=", 1)[0].strip() in REQUIRED:
            k, v = s.split("=", 1)
            k = k.strip()
            v = v.strip().strip('"').strip("'")
            if k in REQUIRED and v and not v.lower().startswith("your_"):
                out[k] = v
            continue
        # Labeled dashboard paste: "API Public Key: …" / "API Private Key: …"
        if ":" in s and ("public" in lower or "private" in lower or lower.startswith("api")):
            val = s.split(":", 1)[1].strip().strip('"').strip("'")
            if "private" in lower:
                out["STORYBLOCKS_PRIVATE_KEY"] = val
            elif "public" in lower:
                out["STORYBLOCKS_PUBLIC_KEY"] = val
            else:
                bare.append(val)
            continue
        bare.append(s.strip('"').strip("'"))
    if "STORYBLOCKS_PUBLIC_KEY" not in out or "STORYBLOCKS_PRIVATE_KEY" not in out:
        if len(bare) >= 2:
            out.setdefault("STORYBLOCKS_PUBLIC_KEY", bare[0])
            out.setdefault("STORYBLOCKS_PRIVATE_KEY", bare[1])
    return out


def store_keychain(account: str, value: str, *, dry_run: bool) -> None:
    digest = hashlib.sha256(value.encode()).hexdigest()[:12]
    if dry_run:
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
    print(f"STORED {account} (len={len(value)} sha12={digest})")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--from-file", type=Path, default=DEFAULT_KEY_FILE)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if not args.from_file.is_file():
        print(f"ERROR: key file missing: {args.from_file}", file=sys.stderr)
        print(
            "Create gitignored docs/storyblocks_keys.env with STORYBLOCKS_PUBLIC_KEY= "
            "and STORYBLOCKS_PRIVATE_KEY= (from Storyblocks API dashboard), then re-run.",
            file=sys.stderr,
        )
        return 2

    raw = args.from_file.read_text(encoding="utf-8", errors="replace")
    parsed = parse_env_file(raw)
    missing = [k for k in REQUIRED if k not in parsed]
    if missing:
        print(f"ERROR: missing/invalid keys in {args.from_file}: {missing}", file=sys.stderr)
        return 2

    for name in REQUIRED:
        val = parsed[name]
        if not re.fullmatch(r"[A-Za-z0-9_\-]{16,256}", val):
            print(f"ERROR: {name} does not look like an API key token (len={len(val)})", file=sys.stderr)
            return 2
        store_keychain(name, val, dry_run=args.dry_run)

    print("OK — load with: eval \"$(python3 scripts/ci/load_integration_env_from_keychain.py)\"")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
