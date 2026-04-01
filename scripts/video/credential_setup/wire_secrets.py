#!/usr/bin/env python3
"""
Bulk GitHub Secrets wiring — reads credentials from a local env file and
sets them as GitHub repository secrets via `gh secret set`.

Usage:
  # Wire all credentials from the env file:
  python scripts/video/credential_setup/wire_secrets.py --env-file .credentials.env

  # Dry run — show what would be set without actually setting:
  python scripts/video/credential_setup/wire_secrets.py --env-file .credentials.env --dry-run

  # Wire only YouTube secrets:
  python scripts/video/credential_setup/wire_secrets.py --env-file .credentials.env --filter YT_

  # Verify existing secrets:
  python scripts/video/credential_setup/wire_secrets.py --verify

Expected .credentials.env format (one KEY=VALUE per line):
  YT_CLIENT_ID_SP=622695231606-xxxx.apps.googleusercontent.com
  YT_CLIENT_SECRET_SP=GOCSPX-xxxx
  YT_REFRESH_TOKEN_SP=1//04xxxx
  TIKTOK_CLIENT_KEY_SP=xxxx
  ...

SECURITY:
  - .credentials.env is LOCAL-ONLY — never commit it
  - Delete it after wiring secrets
  - The script never prints credential values
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def load_env_file(path: Path) -> dict[str, str]:
    """Parse a KEY=VALUE env file, skipping comments and blanks."""
    creds = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()
        if value.startswith('"') and value.endswith('"'):
            value = value[1:-1]
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        if key:
            creds[key] = value
    return creds


def set_secret(name: str, value: str, dry_run: bool = False) -> bool:
    """Set a single GitHub secret via gh CLI."""
    if dry_run:
        print(f"  [DRY RUN] Would set: {name} ({len(value)} chars)")
        return True

    try:
        result = subprocess.run(
            ["gh", "secret", "set", name],
            input=value,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            print(f"  OK: {name}")
            return True
        else:
            print(f"  FAIL: {name} — {result.stderr.strip()}")
            return False
    except FileNotFoundError:
        print("ERROR: 'gh' CLI not found. Install GitHub CLI: https://cli.github.com/")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {name}")
        return False


def list_existing_secrets() -> list[str]:
    """Get list of existing GitHub secret names."""
    try:
        result = subprocess.run(
            ["gh", "secret", "list", "--json", "name", "-q", ".[].name"],
            capture_output=True, text=True, timeout=15,
        )
        return result.stdout.strip().splitlines() if result.returncode == 0 else []
    except Exception:
        return []


def verify_secrets():
    """Check which video publishing secrets exist in GitHub."""
    existing = list_existing_secrets()
    if not existing:
        print("No secrets found (or gh not authenticated).")
        return

    prefixes = {
        "YT_CLIENT_ID": "YouTube Client ID",
        "YT_CLIENT_SECRET": "YouTube Client Secret",
        "YT_REFRESH_TOKEN": "YouTube Refresh Token",
        "TIKTOK_CLIENT_KEY": "TikTok Client Key",
        "TIKTOK_CLIENT_SECRET": "TikTok Client Secret",
        "TIKTOK_ACCESS_TOKEN": "TikTok Access Token",
        "IG_ACCESS_TOKEN": "Instagram Access Token",
        "IG_USER_ID": "Instagram User ID",
    }

    video_secrets = [s for s in existing if any(s.startswith(p) for p in prefixes)]
    other_secrets = [s for s in existing if s not in video_secrets]

    print(f"\nVideo Publishing Secrets ({len(video_secrets)} found):")
    print("-" * 50)

    # Group by brand suffix
    suffixes = set()
    for s in video_secrets:
        for prefix in prefixes:
            if s.startswith(prefix):
                suffix = s[len(prefix):]
                if suffix:
                    suffixes.add(suffix)

    for suffix in sorted(suffixes):
        print(f"\n  Brand: {suffix}")
        for prefix, label in prefixes.items():
            name = f"{prefix}{suffix}"
            status = "set" if name in video_secrets else "MISSING"
            marker = "  " if status == "set" else "!!"
            print(f"    {marker} {name}: {status}")

    if other_secrets:
        print(f"\n  Other secrets: {len(other_secrets)} (not shown)")


def main():
    parser = argparse.ArgumentParser(description="Bulk wire credentials to GitHub Secrets")
    parser.add_argument("--env-file", type=Path, help="Path to .credentials.env file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be set without setting")
    parser.add_argument("--filter", type=str, help="Only set secrets matching this prefix (e.g., YT_, TIKTOK_)")
    parser.add_argument("--verify", action="store_true", help="Check which video secrets already exist")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing secrets (default: skip)")
    args = parser.parse_args()

    if args.verify:
        verify_secrets()
        return

    if not args.env_file:
        parser.error("--env-file is required (or use --verify)")

    if not args.env_file.exists():
        print(f"ERROR: File not found: {args.env_file}")
        sys.exit(1)

    creds = load_env_file(args.env_file)
    if not creds:
        print("ERROR: No credentials found in file.")
        sys.exit(1)

    if args.filter:
        creds = {k: v for k, v in creds.items() if k.startswith(args.filter)}
        print(f"Filtered to {len(creds)} secrets matching '{args.filter}'")

    existing = list_existing_secrets() if not args.overwrite else []

    print(f"\nWiring {len(creds)} secrets to GitHub{'  [DRY RUN]' if args.dry_run else ''}:")
    print("-" * 50)

    ok = 0
    skipped = 0
    failed = 0

    for name, value in sorted(creds.items()):
        if not value:
            print(f"  SKIP: {name} (empty value)")
            skipped += 1
            continue
        if name in existing and not args.overwrite:
            print(f"  SKIP: {name} (already exists, use --overwrite)")
            skipped += 1
            continue
        if set_secret(name, value, args.dry_run):
            ok += 1
        else:
            failed += 1

    print(f"\nDone: {ok} set, {skipped} skipped, {failed} failed")

    if not args.dry_run and ok > 0:
        print(f"\nIMPORTANT: Delete {args.env_file} now that secrets are wired.")
        print(f"  rm {args.env_file}")


if __name__ == "__main__":
    main()
