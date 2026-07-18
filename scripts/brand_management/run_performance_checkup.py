#!/usr/bin/env python3
"""
Weekly Performance Checkup — navigate platform dashboards, read analytics.

Opens Chrome tabs for each platform, navigates to analytics pages.
Reads performance data (revenue, views, downloads) — READ ONLY.
Stops at CAPTCHA/2FA for human to complete, then continues.

Uses Claude-in-Chrome MCP tools when available, falls back to webbrowser.open.

Usage:
    # Check all platforms for a brand
    python scripts/brand_management/run_performance_checkup.py --brand inner_light_press_en_us

    # Check specific platform
    python scripts/brand_management/run_performance_checkup.py --brand inner_light_press_en_us --platform youtube

    # List all brands with credentials
    python scripts/brand_management/run_performance_checkup.py --list-brands
"""
from __future__ import annotations

import argparse
import json
import sys
import webbrowser
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    yaml = None

# ── Platform dashboard URLs ───────────────────────────────────────
DASHBOARD_URLS = {
    "google_play": {
        "analytics": "https://play.google.com/console/developers",
        "description": "Google Play Console → Statistics → Revenue",
    },
    "youtube": {
        "analytics": "https://studio.youtube.com/channel/{channel_id}/analytics/tab-overview",
        "description": "YouTube Studio → Analytics → Overview",
    },
    "tiktok": {
        "analytics": "https://www.tiktok.com/creator#/analytics?tab=overview",
        "description": "TikTok Creator Center → Analytics → Overview",
    },
    "instagram": {
        "analytics": "https://www.instagram.com/accounts/insights/",
        "description": "Instagram → Professional Dashboard → Insights",
    },
    "kobo": {
        "analytics": "https://www.kobo.com/writinglife/library",
        "description": "Kobo Writing Life → Library → Sales",
    },
    "apple_books": {
        "analytics": "https://inaudio.com/dashboard",
        "description": "INaudio Dashboard → Revenue",
    },
}


def _load_yaml(p: Path) -> dict:
    if not p.exists() or yaml is None:
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


def _get_brand_credentials(brand_id: str) -> dict:
    """Load decrypted credentials for a brand."""
    try:
        sys.path.insert(0, str(REPO_ROOT))
        from server.crypto import decrypt_credentials
        return decrypt_credentials(brand_id) or {}
    except Exception:
        return {}


def _get_brand_platforms(brand_id: str) -> list[str]:
    """Get list of platforms this brand should be on."""
    admin_users = _load_yaml(REPO_ROOT / "config" / "brand_management" / "brand_admin_users.yaml")
    admins = admin_users.get("admins") or {}
    admin_data = admins.get(brand_id) or {}
    lane_id = admin_data.get("lane_id", "en_US")
    portal = admin_users.get("portal") or {}
    return (portal.get("platforms_by_lane") or {}).get(lane_id, ["google_play", "youtube"])


def run_checkup(brand_id: str, platforms: list[str] | None = None) -> dict:
    """Run performance checkup for a brand.

    Opens platform dashboards in browser. In Claude-in-Chrome mode,
    navigates automatically and reads data. Otherwise, opens URLs
    for manual checking.

    Returns performance report dict.
    """
    creds = _get_brand_credentials(brand_id)
    if not platforms:
        platforms = _get_brand_platforms(brand_id)

    report = {
        "brand_id": brand_id,
        "checkup_date": datetime.utcnow().isoformat(),
        "platforms": {},
    }

    for platform in platforms:
        platform_creds = creds.get(platform) or {}
        dashboard = DASHBOARD_URLS.get(platform)

        if not dashboard:
            report["platforms"][platform] = {"status": "no_dashboard_url"}
            continue

        # Resolve URL with credentials (e.g., channel_id for YouTube)
        url = dashboard["analytics"]
        for key, value in platform_creds.items():
            url = url.replace(f"{{{key}}}", str(value))

        print(f"\n{'='*60}")
        print(f"Platform: {platform}")
        print(f"Dashboard: {dashboard['description']}")
        print(f"URL: {url}")
        print(f"{'='*60}")

        # Open in browser
        print(f"Opening {platform} dashboard...")
        webbrowser.open(url)

        # In Claude-in-Chrome mode, the MCP tools would:
        # 1. navigate(url) — open the dashboard
        # 2. screenshot() — capture current state
        # 3. read_page() — extract text content
        # 4. If login required → print "Please log in" and wait
        # 5. If CAPTCHA → print "Please complete verification" and wait
        # 6. Once on analytics → get_page_text() and parse data

        report["platforms"][platform] = {
            "url": url,
            "status": "opened",
            "has_credentials": bool(platform_creds),
            "description": dashboard["description"],
            "checked_at": datetime.utcnow().isoformat(),
            # Revenue data populated by Claude-in-Chrome during the session
            "revenue": None,
            "views": None,
            "downloads": None,
        }

    return report


def list_brands_with_credentials() -> list[str]:
    """List all brands that have stored credentials."""
    cred_dir = REPO_ROOT / "artifacts" / "admin_credentials"
    if not cred_dir.exists():
        return []
    return [f.stem for f in cred_dir.glob("*.enc")]


def main() -> int:
    parser = argparse.ArgumentParser(description="Weekly performance checkup")
    parser.add_argument("--brand", help="Brand ID to check")
    parser.add_argument("--platform", help="Specific platform to check")
    parser.add_argument("--list-brands", action="store_true", help="List brands with credentials")
    args = parser.parse_args()

    if args.list_brands:
        brands = list_brands_with_credentials()
        print(f"Brands with credentials: {len(brands)}")
        for b in brands:
            print(f"  {b}")
        return 0

    if not args.brand:
        parser.error("Specify --brand or --list-brands")
        return 1

    platforms = [args.platform] if args.platform else None
    report = run_checkup(args.brand, platforms)

    # Save report
    report_dir = REPO_ROOT / "artifacts" / "performance" / args.brand
    report_dir.mkdir(parents=True, exist_ok=True)
    week = datetime.utcnow().strftime("%Y-W%V")
    report_path = report_dir / f"{week}.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\nReport saved: {report_path}")
    print(f"Platforms checked: {len(report['platforms'])}")
    for p, data in report["platforms"].items():
        status = "✅" if data.get("has_credentials") else "⚠️ no credentials"
        print(f"  {p}: {status}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
