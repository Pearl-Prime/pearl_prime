#!/usr/bin/env python3
"""
Generate brand URL routing manifest for Cloudflare Pages — $0 cost.

Using path-based routing on brand-admin-onboarding-bu2.pages.dev:
  - Landing pages: brand-admin-onboarding-bu2.pages.dev/{brand-slug}/
  - Freebie pages: brand-admin-onboarding-bu2.pages.dev/free/{freebie-slug}
  - Email sending: via GHL msgsndr.com infrastructure (no custom domain needed)

Requires: CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID env vars (or Keychain).

Usage:
    # Dry run (show what would be created)
    python scripts/brand_management/setup_brand_subdomains.py --dry-run

    # Create all subdomains
    python scripts/brand_management/setup_brand_subdomains.py --create

    # Create for one brand
    python scripts/brand_management/setup_brand_subdomains.py --create --brand inner_light_press_en_us

    # List existing subdomains
    python scripts/brand_management/setup_brand_subdomains.py --list
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

try:
    import requests
except ImportError:
    requests = None

# ── Cloudflare API ────────────────────────────────────────────────
CF_API_BASE = "https://api.cloudflare.com/client/v4"
ROOT_DOMAIN = "brand-admin-onboarding-bu2.pages.dev"

# GHL targets for CNAME records
GHL_FUNNEL_TARGET = "funnels.msgsndr.com"      # Landing pages / funnels
GHL_EMAIL_TARGET = "mailgun.org"                # Email sending (Mailgun via GHL)


def _get_cf_creds() -> tuple[str, str]:
    """Load Cloudflare API token and zone ID from env or Keychain."""
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    zone_id = os.environ.get("CLOUDFLARE_ZONE_ID", "")

    if not token:
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "phoenix-omega",
                 "-a", "CLOUDFLARE_API_TOKEN", "-w"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                token = result.stdout.strip()
        except Exception:
            pass

    if not zone_id:
        try:
            result = subprocess.run(
                ["security", "find-generic-password", "-s", "phoenix-omega",
                 "-a", "CLOUDFLARE_ZONE_ID", "-w"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                zone_id = result.stdout.strip()
        except Exception:
            pass

    return token, zone_id


def _cf_headers(token: str) -> dict:
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _brand_to_subdomain(brand_id: str) -> str:
    """Convert brand_id to a clean subdomain slug.

    inner_light_press_en_us → inner-light-press-en-us
    stabilizer_ja_jp → stabilizer-ja-jp
    """
    return brand_id.replace("_", "-")


def _load_brands() -> dict:
    if yaml is None:
        return {}
    path = REPO_ROOT / "config" / "brand_management" / "global_brand_registry.yaml"
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data.get("brands") or {}


def list_existing_subdomains(token: str, zone_id: str) -> list[str]:
    """List all existing DNS records for the zone."""
    if not requests:
        print("requests library required")
        return []

    records = []
    page = 1
    while True:
        resp = requests.get(
            f"{CF_API_BASE}/zones/{zone_id}/dns_records",
            headers=_cf_headers(token),
            params={"type": "CNAME", "per_page": 100, "page": page},
            timeout=30,
        )
        data = resp.json()
        if not data.get("success"):
            print(f"Error: {data.get('errors')}")
            break
        for r in data.get("result", []):
            records.append(r["name"])
        if page >= data.get("result_info", {}).get("total_pages", 1):
            break
        page += 1

    return records


def create_subdomain(
    token: str, zone_id: str, subdomain: str, target: str, record_type: str = "CNAME",
    proxied: bool = True, dry_run: bool = False,
) -> bool:
    """Create a single DNS record on Cloudflare."""
    full_name = f"{subdomain}.{ROOT_DOMAIN}"

    if dry_run:
        print(f"  [DRY-RUN] {record_type} {full_name} → {target}")
        return True

    if not requests:
        print("requests library required")
        return False

    resp = requests.post(
        f"{CF_API_BASE}/zones/{zone_id}/dns_records",
        headers=_cf_headers(token),
        json={
            "type": record_type,
            "name": full_name,
            "content": target,
            "proxied": proxied,
            "ttl": 1,  # auto
        },
        timeout=30,
    )
    data = resp.json()
    if data.get("success"):
        print(f"  ✅ {full_name} → {target}")
        return True
    else:
        errors = data.get("errors", [])
        # Check if already exists
        if any("already exists" in str(e).lower() for e in errors):
            print(f"  ⏭️  {full_name} already exists")
            return True
        print(f"  ❌ {full_name}: {errors}")
        return False


def setup_brand(
    token: str, zone_id: str, brand_id: str, dry_run: bool = False,
) -> dict:
    """Create landing page + email subdomains for one brand."""
    slug = _brand_to_subdomain(brand_id)

    results = {
        "brand_id": brand_id,
        "landing_page": f"{slug}.{ROOT_DOMAIN}",
        "email_sending": f"mail.{slug}.{ROOT_DOMAIN}",
    }

    # 1. Landing page subdomain → GHL funnels
    ok1 = create_subdomain(token, zone_id, slug, GHL_FUNNEL_TARGET, proxied=True, dry_run=dry_run)

    # 2. Email sending subdomain → Mailgun (GHL email)
    ok2 = create_subdomain(token, zone_id, f"mail.{slug}", GHL_EMAIL_TARGET, proxied=False, dry_run=dry_run)

    results["success"] = ok1 and ok2

    # Rate limit: Cloudflare allows 1200 requests/5min — be safe
    if not dry_run:
        time.sleep(0.1)  # 100ms between brands = ~3 seconds for 312 brands

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Setup brand subdomains on Cloudflare")
    parser.add_argument("--create", action="store_true", help="Create subdomains")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be created")
    parser.add_argument("--list", action="store_true", help="List existing CNAME records")
    parser.add_argument("--brand", help="Single brand ID")
    args = parser.parse_args()

    token, zone_id = _get_cf_creds()
    if not token or not zone_id:
        print("CLOUDFLARE_API_TOKEN and CLOUDFLARE_ZONE_ID required")
        print("Set env vars or add to macOS Keychain (service: phoenix-omega)")
        return 1

    if args.list:
        records = list_existing_subdomains(token, zone_id)
        print(f"Existing CNAME records: {len(records)}")
        for r in sorted(records):
            print(f"  {r}")
        return 0

    brands = _load_brands()
    if not brands:
        print("No brands found in global_brand_registry.yaml")
        return 1

    if args.brand:
        if args.brand not in brands:
            print(f"Brand not found: {args.brand}")
            return 1
        brands = {args.brand: brands[args.brand]}

    dry_run = args.dry_run or not args.create
    if dry_run and not args.dry_run:
        print("Specify --create to actually create subdomains, or --dry-run to preview")
        return 1

    print(f"{'DRY RUN' if dry_run else 'CREATING'}: {len(brands)} brands × 2 records = {len(brands) * 2} DNS records")
    print(f"Domain: {ROOT_DOMAIN}")
    print(f"GHL funnel target: {GHL_FUNNEL_TARGET}")
    print(f"GHL email target: {GHL_EMAIL_TARGET}")
    print()

    success = 0
    failed = 0
    for brand_id in sorted(brands.keys()):
        result = setup_brand(token, zone_id, brand_id, dry_run=dry_run)
        if result["success"]:
            success += 1
        else:
            failed += 1

    print(f"\nDone: {success} succeeded, {failed} failed out of {len(brands)} brands")

    # Write results manifest
    if not dry_run:
        manifest_path = REPO_ROOT / "artifacts" / "brand_subdomains" / "subdomain_manifest.json"
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest = {
            "root_domain": ROOT_DOMAIN,
            "total_brands": len(brands),
            "subdomains": {
                bid: {
                    "landing": f"{_brand_to_subdomain(bid)}.{ROOT_DOMAIN}",
                    "email": f"mail.{_brand_to_subdomain(bid)}.{ROOT_DOMAIN}",
                }
                for bid in sorted(brands.keys())
            },
        }
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"Manifest: {manifest_path}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
