#!/usr/bin/env python3
"""
Bilibili Cookie Credential Setup — extract SESSDATA and bili_jct from browser.

Bilibili uses cookie-based authentication rather than OAuth. The two required
cookies are:

  SESSDATA   — session authentication token
  bili_jct   — CSRF token required for write operations (uploads, comments)

How to extract cookies manually:

  1. Open https://www.bilibili.com in your browser and log in.
  2. Open DevTools (F12 or Cmd+Shift+I / Ctrl+Shift+I).
  3. Go to Application (Chrome) or Storage (Firefox) -> Cookies -> bilibili.com
  4. Find and copy the values for:
       SESSDATA   (long alphanumeric string with possible URL-encoded chars)
       bili_jct    (32-character hex string)
  5. Paste them when prompted by this script.

NOTE: SESSDATA cookies expire (typically after ~30 days). You will need to
repeat this process when they expire. There is no automated refresh mechanism
for cookie-based auth.

Usage:
  # Interactive — opens browser, prompts for brand suffix:
  python scripts/video/credential_setup/bilibili_setup.py

  # Non-interactive — specify everything:
  python scripts/video/credential_setup/bilibili_setup.py \
    --sessdata <SESSDATA> --csrf <BILI_JCT> --brand-suffix _SP

  # Batch mode — process multiple brands from manifest:
  python scripts/video/credential_setup/bilibili_setup.py \
    --manifest credentials_manifest.yaml --output .env.bilibili

Output: prints credentials and optionally appends to a credentials file.
"""
from __future__ import annotations

import argparse
import os
import sys
import webbrowser
from pathlib import Path

BILIBILI_LOGIN_URL = "https://passport.bilibili.com/login"
BILIBILI_HOME_URL = "https://www.bilibili.com"


def prompt_cookie(name: str, description: str) -> str:
    """Prompt the user to paste a cookie value, with validation hints."""
    print(f"\n  Cookie: {name}")
    print(f"  ({description})")
    while True:
        value = input(f"  Paste {name}: ").strip()
        if not value:
            print(f"  ERROR: {name} cannot be empty. Try again.")
            continue
        return value


def open_browser_instructions() -> None:
    """Open Bilibili login page and print extraction instructions."""
    print("\nOpening Bilibili login page in your browser...")
    print(f"If the browser doesn't open, visit:\n{BILIBILI_LOGIN_URL}\n")
    webbrowser.open(BILIBILI_LOGIN_URL)

    print("After logging in, extract your cookies:")
    print("  1. Open DevTools (F12 or Cmd+Shift+I / Ctrl+Shift+I)")
    print("  2. Go to Application -> Cookies -> https://www.bilibili.com")
    print("  3. Copy the values for SESSDATA and bili_jct")
    print()


def validate_sessdata(value: str) -> bool:
    """Basic sanity check on SESSDATA format."""
    # SESSDATA is typically a long alphanumeric string, possibly URL-encoded
    if len(value) < 10:
        return False
    return True


def validate_csrf(value: str) -> bool:
    """Basic sanity check on bili_jct (CSRF token) format."""
    # bili_jct is a 32-character hex string
    if len(value) != 32:
        return False
    try:
        int(value, 16)
        return True
    except ValueError:
        return False


def process_brand(
    sessdata: str | None,
    csrf: str | None,
    brand_suffix: str,
    output_file: Path | None,
    open_browser: bool = True,
) -> dict:
    """Collect and store Bilibili credentials for one brand."""
    print(f"\n{'='*60}")
    print(f"  Bilibili credential setup for brand suffix: {brand_suffix}")
    print(f"{'='*60}")

    if open_browser and not (sessdata and csrf):
        open_browser_instructions()
        input("Press Enter after you have logged in and opened DevTools...")

    # --- SESSDATA ---
    if not sessdata:
        sessdata = prompt_cookie(
            "SESSDATA",
            "Long alphanumeric session token, may contain URL-encoded characters",
        )
    if not validate_sessdata(sessdata):
        print("WARNING: SESSDATA looks unusually short. Double-check the value.", file=sys.stderr)

    # --- bili_jct (CSRF) ---
    if not csrf:
        csrf = prompt_cookie(
            "bili_jct",
            "32-character hex CSRF token",
        )
    if not validate_csrf(csrf):
        print(
            "WARNING: bili_jct should be a 32-character hex string. "
            "The value you provided may be incorrect.",
            file=sys.stderr,
        )

    print(f"\nCredentials captured for {brand_suffix}")

    result = {
        f"BILI_SESSDATA{brand_suffix}": sessdata,
        f"BILI_CSRF{brand_suffix}": csrf,
    }

    if output_file:
        with open(output_file, "a") as f:
            for key, val in result.items():
                f.write(f"{key}={val}\n")
        print(f"Credentials appended to {output_file}")
    else:
        print("\nAdd these to your environment or .env file:")
        for key, val in result.items():
            print(f"  {key}={val}")

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Bilibili cookie credential setup (SESSDATA + bili_jct)",
    )
    parser.add_argument(
        "--sessdata",
        help="SESSDATA cookie value (or set BILI_SESSDATA env)",
    )
    parser.add_argument(
        "--csrf",
        help="bili_jct CSRF cookie value (or set BILI_CSRF env)",
    )
    parser.add_argument(
        "--brand-suffix",
        help="Brand credential suffix (e.g., _SP, _CC)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Append credentials to this file",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        help="YAML manifest with list of brands to process",
    )
    parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Skip opening the browser (assume user already has cookies)",
    )
    args = parser.parse_args()

    sessdata = args.sessdata or os.environ.get("BILI_SESSDATA", "") or None
    csrf = args.csrf or os.environ.get("BILI_CSRF", "") or None

    if args.manifest:
        try:
            import yaml  # type: ignore[import-untyped]

            manifest = yaml.safe_load(args.manifest.read_text())
        except ImportError:
            # Fallback: try json if the manifest is .json
            if args.manifest.suffix == ".json":
                import json

                manifest = json.loads(args.manifest.read_text())
            else:
                print("ERROR: PyYAML required for YAML manifest mode. pip install pyyaml")
                sys.exit(1)

        brands = manifest.get("brands", [])
        if not brands:
            print("ERROR: No brands found in manifest.", file=sys.stderr)
            sys.exit(1)

        print(f"Processing {len(brands)} brands from manifest...")
        for brand in brands:
            suffix = brand.get("suffix", "")
            if not suffix:
                continue
            input(f"\nPress Enter when ready to set up brand {suffix}...")
            process_brand(
                sessdata=None,  # Each brand needs its own cookies
                csrf=None,
                brand_suffix=suffix,
                output_file=args.output,
                open_browser=not args.no_browser,
            )
    else:
        suffix = args.brand_suffix
        if not suffix:
            suffix = input("Enter brand suffix (e.g., _SP, _CC): ").strip()
        process_brand(
            sessdata=sessdata,
            csrf=csrf,
            brand_suffix=suffix,
            output_file=args.output,
            open_browser=not args.no_browser,
        )


if __name__ == "__main__":
    main()
