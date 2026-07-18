#!/usr/bin/env python3
"""Upload one teacher example-reel MP4 to Cloudflare R2 (S3-compatible API).

Object key (stable): brand-admin/teachers/<slug>/example_reel_v1.mp4

Environment (same family as scripts/podcast/upload_podcast_to_r2.py):
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET
Optional:
  R2_PUBLIC_BASE_URL or PODCAST_PUBLIC_BASE_URL — printed with the object URL

Install: pip install boto3

Example:
  PYTHONPATH=. python3 scripts/brand_admin/upload_teacher_example_reel_r2.py \\
    --teacher-slug ahjan --file teacher_vid_package/ahjan.mp4
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    try:
        import boto3  # type: ignore
        from botocore.config import Config  # type: ignore
    except ImportError:
        print("Install boto3: pip install boto3", file=sys.stderr)
        return 1

    ap = argparse.ArgumentParser(description="Upload teacher example reel to R2")
    ap.add_argument("--teacher-slug", required=True, help="e.g. ahjan, adi_da")
    ap.add_argument("--file", type=Path, required=True, help="Local MP4 path")
    ap.add_argument("--bucket", default=os.environ.get("R2_BUCKET", "phoenix-podcast"))
    args = ap.parse_args()

    account = os.environ.get("R2_ACCOUNT_ID", "").strip()
    key_id = os.environ.get("R2_ACCESS_KEY_ID", "").strip()
    secret = os.environ.get("R2_SECRET_ACCESS_KEY", "").strip()
    if not all([account, key_id, secret, args.bucket]):
        print(
            "Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET",
            file=sys.stderr,
        )
        return 1

    local = args.file.resolve()
    if not local.is_file():
        print(f"Not a file: {local}", file=sys.stderr)
        return 1

    slug = args.teacher_slug.strip().lower().replace(" ", "_")
    key = f"brand-admin/teachers/{slug}/example_reel_v1.mp4"
    pub_base = (
        os.environ.get("R2_PUBLIC_BASE_URL") or os.environ.get("PODCAST_PUBLIC_BASE_URL") or ""
    ).rstrip("/")

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{account}.r2.cloudflarestorage.com",
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

    body = local.read_bytes()
    h = hashlib.sha256(body).hexdigest()
    client.put_object(
        Bucket=args.bucket,
        Key=key,
        Body=body,
        ContentType="video/mp4",
        CacheControl="public, max-age=31536000",
    )
    head = client.head_object(Bucket=args.bucket, Key=key)
    clen = head.get("ContentLength", len(body))
    https_url = f"{pub_base}/{key}" if pub_base else f"s3://{args.bucket}/{key}"
    print(f"key={key}")
    print(f"sha256={h}")
    print(f"content_length={clen}")
    print(f"public_url={https_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
