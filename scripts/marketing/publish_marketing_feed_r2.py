#!/usr/bin/env python3
"""Publish marketing_feed.json to pearl-prime-content R2 bucket."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _public_url(cdn_base: str, key: str) -> str:
    return f"{cdn_base.rstrip('/')}/{key}"


def _r2_key(brand_id: str, locale: str, week: str) -> str:
    return f"pearl-prime-content/{brand_id}/{locale}/{week}/marketing_feed.json"


def main() -> int:
    ap = argparse.ArgumentParser(description="Publish marketing feed to R2")
    ap.add_argument("--brand-id", required=True)
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--week", default=None)
    ap.add_argument("--feed", type=Path, default=None, help="Existing JSON (else build)")
    ap.add_argument("--bucket", default=os.environ.get("PEARL_PRIME_CONTENT_R2_BUCKET", "pearl-prime-content"))
    ap.add_argument(
        "--cdn-base",
        default=os.environ.get("PEARL_PRIME_CONTENT_CDN_URL", ""),
        help="Public CDN base, e.g. https://content.pearlprime.shop",
    )
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    feed_path = args.feed
    if not feed_path:
        cmd = [
            sys.executable,
            str(REPO_ROOT / "scripts/marketing/build_marketing_feed.py"),
            "--brand-id",
            args.brand_id,
            "--locale",
            args.locale,
        ]
        if args.week:
            cmd.extend(["--week", args.week])
        subprocess.check_call(cmd, cwd=REPO_ROOT)
        week = args.week
        if not week:
            import datetime as dt

            d = dt.date.today()
            week = f"{d.isocalendar().year}-W{d.isocalendar().week:02d}"
        feed_path = (
            REPO_ROOT
            / "artifacts"
            / "marketing_feed"
            / args.brand_id
            / args.locale
            / week
            / "marketing_feed.json"
        )

    feed_path = feed_path.resolve()
    if not feed_path.exists():
        print(f"feed not found: {feed_path}", file=sys.stderr)
        return 1

    feed = json.loads(feed_path.read_text(encoding="utf-8"))
    week = str(feed.get("week") or args.week or "")
    key = _r2_key(args.brand_id, args.locale, week)
    body = feed_path.read_bytes()
    sha = hashlib.sha256(body).hexdigest()

    manifest = {
        "brand_id": args.brand_id,
        "locale": args.locale,
        "week": week,
        "r2_key": key,
        "sha256": sha,
        "public_url": _public_url(args.cdn_base, key) if args.cdn_base else "",
        "item_count": len(feed.get("items") or []),
    }

    manifest_path = feed_path.parent / "publish_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    if args.dry_run:
        print(json.dumps(manifest, indent=2))
        return 0

    account = os.environ.get("R2_ACCOUNT_ID", "").strip()
    key_id = os.environ.get("R2_ACCESS_KEY_ID", "").strip()
    secret = os.environ.get("R2_SECRET_ACCESS_KEY", "").strip()
    if not all([account, key_id, secret]):
        print("Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY", file=sys.stderr)
        print(f"Dry-run manifest written: {manifest_path}", file=sys.stderr)
        return 2

    try:
        import boto3
        from botocore.config import Config
    except ImportError:
        print("Install boto3 for R2 upload", file=sys.stderr)
        return 1

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{account}.r2.cloudflarestorage.com",
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )
    client.put_object(
        Bucket=args.bucket,
        Key=key,
        Body=body,
        ContentType="application/json",
        CacheControl="public, max-age=300",
    )
    print(f"Published s3://{args.bucket}/{key}")
    if manifest["public_url"]:
        print(f"Public URL: {manifest['public_url']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
