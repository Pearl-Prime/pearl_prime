#!/usr/bin/env python3
"""Upload music bank tree to Cloudflare R2 (S3-compatible API).

Environment (see docs/INTEGRATION_CREDENTIALS_REGISTRY.md — add rows if missing):
  R2_ACCOUNT_ID          — Cloudflare account id
  R2_ACCESS_KEY_ID       — R2 API token access key
  R2_SECRET_ACCESS_KEY   — R2 API token secret
  R2_BUCKET              — bucket name
  R2_PREFIX              — optional key prefix, e.g. music_bank/v1/

Install: pip install boto3

Usage (from repo root):
    python3 scripts/music/upload_music_bank_r2.py \\
        --local-dir assets/music_bank/by_brand

Dry run:
    python3 scripts/music/upload_music_bank_r2.py --local-dir assets/music_bank/base --dry-run
"""
from __future__ import annotations

import argparse
import mimetypes
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def main() -> int:
    try:
        import boto3  # type: ignore
        from botocore.config import Config  # type: ignore
    except ImportError:
        print("Install boto3: pip install boto3", file=sys.stderr)
        return 1

    ap = argparse.ArgumentParser(description="Upload directory to Cloudflare R2")
    ap.add_argument("--local-dir", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    account = os.environ.get("R2_ACCOUNT_ID", "").strip()
    key_id = os.environ.get("R2_ACCESS_KEY_ID", "").strip()
    secret = os.environ.get("R2_SECRET_ACCESS_KEY", "").strip()
    bucket = os.environ.get("R2_BUCKET", "").strip()
    prefix = os.environ.get("R2_PREFIX", "music_bank/").strip()
    if prefix and not prefix.endswith("/"):
        prefix += "/"

    if not all([account, key_id, secret, bucket]):
        print(
            "Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET",
            file=sys.stderr,
        )
        return 1

    root = args.local_dir.resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 1

    endpoint = f"https://{account}.r2.cloudflarestorage.com"
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

    files = [p for p in root.rglob("*") if p.is_file()]
    print(f"Uploading {len(files)} files from {root} → s3://{bucket}/{prefix}")

    for path in sorted(files):
        rel = path.relative_to(root).as_posix()
        key = f"{prefix}{rel}"
        ctype, _ = mimetypes.guess_type(path.name)
        extra = {"ContentType": ctype or "application/octet-stream"}
        if args.dry_run:
            print(f"  [dry-run] {key}")
            continue
        client.upload_file(str(path), bucket, key, ExtraArgs=extra)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
