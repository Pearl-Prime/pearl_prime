#!/usr/bin/env python3
"""Build weekly marketing_feed.json for GHL (schema v3)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.marketing.brand_profile import get_brand_profile  # noqa: E402
from phoenix_v4.marketing.build_feed import build_marketing_feed, validate_feed  # noqa: E402


def _apply_brand_profile(args: argparse.Namespace) -> None:
    try:
        profile = get_brand_profile(args.brand_id)
    except KeyError:
        return
    if args.persona_id == "corporate_managers" and profile.get("default_persona"):
        args.persona_id = str(profile["default_persona"])
    if not args.landing_base and profile.get("landing_base"):
        args.landing_base = str(profile["landing_base"])
    if not args.shop_base or args.shop_base == "https://pearlprime.shop":
        if profile.get("shop_base"):
            args.shop_base = str(profile["shop_base"])
    prefix = profile.get("funnel_path_prefix")
    args.funnel_path_prefix = str(prefix) if prefix else None


def main() -> int:
    ap = argparse.ArgumentParser(description="Build marketing_feed.json for GHL")
    ap.add_argument("--brand-id", required=True, help="Brand id, e.g. stillness_press")
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--week", default=None, help="ISO week folder, e.g. 2026-W26")
    ap.add_argument("--persona-id", default="corporate_managers")
    ap.add_argument("--topic", action="append", dest="topics", help="Limit to topic(s)")
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Output path (default: artifacts/marketing_feed/{brand}/{locale}/{week}/marketing_feed.json)",
    )
    ap.add_argument("--shop-base", default="https://pearlprime.shop")
    ap.add_argument("--landing-base", default=None)
    ap.add_argument("--funnel-path-prefix", default=None, help="Override brand funnel URL prefix")
    ap.add_argument("--no-profile", action="store_true", help="Skip brand_marketing_registry.yaml")
    ap.add_argument("--validate-only", action="store_true", help="Validate existing --out file")
    args = ap.parse_args()
    args.funnel_path_prefix = args.funnel_path_prefix or None
    if not args.no_profile:
        _apply_brand_profile(args)

    if args.validate_only:
        out = args.out
        if not out or not out.exists():
            print("validate-only requires --out pointing to existing file", file=sys.stderr)
            return 1
        feed = json.loads(out.read_text(encoding="utf-8"))
        errors = validate_feed(feed)
        if errors:
            for e in errors:
                print(e, file=sys.stderr)
            return 1
        print(f"OK: {out} ({len(feed.get('items') or [])} items)")
        return 0

    feed = build_marketing_feed(
        brand_id=args.brand_id,
        locale=args.locale,
        week=args.week,
        topics=args.topics,
        shop_base=args.shop_base,
        persona_id=args.persona_id,
        landing_base=args.landing_base or "https://brand-admin-onboarding.pages.dev",
        funnel_path_prefix=args.funnel_path_prefix,
    )
    errors = validate_feed(feed)
    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    week = feed["week"]
    out = args.out or (
        REPO_ROOT
        / "artifacts"
        / "marketing_feed"
        / args.brand_id
        / args.locale
        / week
        / "marketing_feed.json"
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(feed, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {out} ({len(feed['items'])} items)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
