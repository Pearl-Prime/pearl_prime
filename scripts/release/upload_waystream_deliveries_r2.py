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

# Cloudflare R2 rejects presigned GETs with X-Amz-Expires >= 604800 (1 week) — HTTP 400
# InvalidArgument "X-Amz-Expires must be less than a week (in seconds)". Confirmed
# empirically 2026-07-01 (flip-assemble R2 pilot, PR #4204): a 30d presign 400'd, a 6d
# presign returned HTTP 200. Presigned URLs are inherently short-lived; the DURABLE public
# download path is the /download/<book>?week=... Cloudflare Pages Function, which re-signs
# the R2 object server-side on every request (brand-wizard-app/functions/download/[book_id].js,
# emitted by scripts/marketing/rebuild_waystream_feed_from_r2.py in default proxy mode).
R2_MAX_PRESIGN_SEC = 604_800  # exclusive ceiling; ExpiresIn must be strictly less
DEFAULT_PRESIGN_SEC = 60 * 60 * 24 * 6  # 6d — safely under the R2 1-week limit


def _resolve_presign_sec(env: dict[str, str] | None = None) -> int:
    """Resolve + validate the presign TTL from WAYSTREAM_R2_PRESIGN_SEC.

    Defaults to 6 days. Raises a clear error if a caller requests >= 1 week, since
    R2 would otherwise 400 every generated URL at fetch time.
    """
    src = os.environ if env is None else env
    raw = src.get("WAYSTREAM_R2_PRESIGN_SEC")
    sec = DEFAULT_PRESIGN_SEC if raw is None or not raw.strip() else int(raw)
    if sec >= R2_MAX_PRESIGN_SEC:
        raise SystemExit(
            f"WAYSTREAM_R2_PRESIGN_SEC={sec} is invalid: Cloudflare R2 rejects presigned "
            f"GETs with X-Amz-Expires >= {R2_MAX_PRESIGN_SEC} (1 week) with HTTP 400 "
            f'"X-Amz-Expires must be less than a week". Use a value < {R2_MAX_PRESIGN_SEC} '
            f"(default {DEFAULT_PRESIGN_SEC} = 6d), or rely on the durable /download proxy "
            "(scripts/marketing/rebuild_waystream_feed_from_r2.py, default proxy mode)."
        )
    if sec <= 0:
        raise SystemExit(f"WAYSTREAM_R2_PRESIGN_SEC={sec} must be a positive integer")
    return sec


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
    presign_sec = _resolve_presign_sec()  # fail fast on an out-of-range TTL
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
                ExpiresIn=presign_sec,
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
