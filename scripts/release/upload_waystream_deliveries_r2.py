#!/usr/bin/env python3
"""Upload Waystream delivery EPUBs to R2 and patch brand_deliveries JSON URLs.

EPUBs (~3.4 MB) exceed the repo no-binary-blobs cap (1 MB). They are served from
R2; the dashboard + storefront JSON feeds carry presigned download URLs.

Usage:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  PYTHONPATH=. python3 scripts/release/upload_waystream_deliveries_r2.py
  PYTHONPATH=. python3 scripts/release/upload_waystream_deliveries_r2.py --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BRAND = "way_stream_sanctuary"
PKG = REPO / "artifacts/weekly_packages" / BRAND
FEED_PATH = REPO / "brand-wizard-app/public/brand_deliveries" / f"{BRAND}.json"
MANIFEST = REPO / "artifacts/waystream/r2_delivery_manifest.json"
KEY_PREFIX = f"brand/{BRAND}/deliveries"
PRESIGN_SEC = int(os.environ.get("WAYSTREAM_R2_PRESIGN_SEC", str(60 * 60 * 24 * 30)))  # 30d


def _r2_client():
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:
        raise SystemExit("boto3 required: pip install boto3") from exc
    account = os.environ.get("R2_ACCOUNT_ID", "").strip()
    key_id = (os.environ.get("R2_ACCESS_KEY_ID") or os.environ.get("CF_R2_ACCESS_KEY") or "").strip()
    secret = (os.environ.get("R2_SECRET_ACCESS_KEY") or os.environ.get("CF_R2_SECRET_KEY") or "").strip()
    if not all([account, key_id, secret]):
        raise SystemExit("Missing R2_ACCOUNT_ID / R2_ACCESS_KEY_ID / R2_SECRET_ACCESS_KEY")
    endpoint = (os.environ.get("R2_ENDPOINT") or "").strip()
    if not endpoint:
        endpoint = f"https://{account}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def _bucket() -> str:
    b = (os.environ.get("R2_BUCKET") or os.environ.get("CF_R2_BUCKET") or "phoenix-omega-artifacts").strip()
    return b


def _scan_epubs() -> list[dict]:
    rows: list[dict] = []
    if not PKG.is_dir():
        return rows
    for week_dir in sorted(PKG.iterdir()):
        kdp = week_dir / "amazon_kdp"
        if not kdp.is_dir():
            continue
        for p in sorted(kdp.glob("*.epub")):
            body = p.read_bytes()
            rows.append(
                {
                    "book_id": p.stem,
                    "week": week_dir.name,
                    "platform": "amazon_kdp",
                    "file": p.name,
                    "path": str(p.resolve()),
                    "size": len(body),
                    "sha256": hashlib.sha256(body).hexdigest(),
                    "key": f"{KEY_PREFIX}/{week_dir.name}/amazon_kdp/{p.name}",
                }
            )
    return rows


def _patch_feed(url_by_file: dict[str, str]) -> int:
    if not FEED_PATH.is_file():
        return 0
    feed = json.loads(FEED_PATH.read_text(encoding="utf-8"))
    patched = 0
    for week, plats in (feed.get("weeks") or {}).items():
        for plat, files in plats.items():
            for entry in files or []:
                fname = entry.get("file") or ""
                if fname in url_by_file:
                    entry["url"] = url_by_file[fname]
                    entry["r2"] = True
                    patched += 1
    FEED_PATH.write_text(json.dumps(feed, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return patched


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    rows = _scan_epubs()
    if not rows:
        print("no EPUBs under weekly_packages — nothing to upload")
        return 0

    client = None if args.dry_run else _r2_client()
    bucket = _bucket()
    manifest: dict = {"brand": BRAND, "bucket": bucket, "prefix": KEY_PREFIX, "objects": []}
    url_by_file: dict[str, str] = {}

    for row in rows:
        if args.dry_run:
            url = f"PRESIGNED:{row['key']}"
        else:
            body = Path(row["path"]).read_bytes()
            client.put_object(  # type: ignore[union-attr]
                Bucket=bucket,
                Key=row["key"],
                Body=body,
                ContentType="application/epub+zip",
                CacheControl="public, max-age=31536000, immutable",
            )
            url = client.generate_presigned_url(  # type: ignore[union-attr]
                "get_object",
                Params={"Bucket": bucket, "Key": row["key"]},
                ExpiresIn=PRESIGN_SEC,
            )
        url_by_file[row["file"]] = url
        manifest["objects"].append({**row, "url": url})

    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    patched = _patch_feed(url_by_file)
    print(f"uploaded {len(rows)} EPUBs -> s3://{bucket}/{KEY_PREFIX}/")
    print(f"patched {patched} feed URLs in {FEED_PATH.relative_to(REPO)}")
    print(f"manifest -> {MANIFEST.relative_to(REPO)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
