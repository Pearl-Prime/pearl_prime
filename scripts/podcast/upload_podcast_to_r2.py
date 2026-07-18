#!/usr/bin/env python3
"""Upload podcast MP3s, feed.xml, artwork to Cloudflare R2 (permanent objects)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


def main() -> int:
    try:
        import boto3  # type: ignore
        from botocore.config import Config  # type: ignore
    except ImportError:
        print("Install boto3: pip install boto3", file=sys.stderr)
        return 1

    ap = argparse.ArgumentParser(description="Upload podcast assets to R2")
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--brand-id", required=True)
    ap.add_argument("--series-id", required=True)
    ap.add_argument("--week", required=True)
    ap.add_argument("--bucket", default=os.environ.get("R2_BUCKET", "phoenix-podcast"))
    ap.add_argument("--workspace", type=Path, default=None, help="Directory containing job.json (default: --source-dir)")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = (args.workspace or args.source_dir).resolve()
    if not args.no_job_check:
        require_stage("upload", ws)

    account = os.environ.get("R2_ACCOUNT_ID", "").strip()
    key_id = os.environ.get("R2_ACCESS_KEY_ID", "").strip()
    secret = os.environ.get("R2_SECRET_ACCESS_KEY", "").strip()
    if not all([account, key_id, secret, args.bucket]):
        print("Set R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET", file=sys.stderr)
        if not args.no_job_check:
            mark_failed(ws, "upload", error="missing R2 credentials")
        return 1

    client = boto3.client(
        "s3",
        endpoint_url=f"https://{account}.r2.cloudflarestorage.com",
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )

    root = args.source_dir.resolve()
    prefix = f"{args.brand_id}/{args.series_id}/"
    pub_base = (os.environ.get("R2_PUBLIC_BASE_URL") or os.environ.get("PODCAST_PUBLIC_BASE_URL") or "").rstrip("/")

    manifest: dict = {"brand_id": args.brand_id, "series_id": args.series_id, "week": args.week, "objects": []}

    def upload(local: Path, key_suffix: str, cache: str, ctype: str) -> bool:
        key = prefix + key_suffix
        body = local.read_bytes()
        h = hashlib.sha256(body).hexdigest()
        client.put_object(
            Bucket=args.bucket,
            Key=key,
            Body=body,
            ContentType=ctype,
            CacheControl=cache,
        )
        head = client.head_object(Bucket=args.bucket, Key=key)
        clen = head.get("ContentLength", len(body))
        url = f"{pub_base}/{key}" if pub_base else f"s3://{args.bucket}/{key}"
        manifest["objects"].append({"key": key, "url": url, "sha256": h, "content_length": clen})
        return True

    for mp3 in sorted(root.glob("*.mp3")):
        upload(mp3, mp3.name, "public, max-age=31536000", "audio/mpeg")
    feed = root / "feed.xml"
    if feed.is_file():
        upload(feed, "feed.xml", "public, max-age=3600", "application/rss+xml")
    art = root / "artwork.jpg"
    if art.is_file():
        upload(art, "artwork.jpg", "public, max-age=31536000", "image/jpeg")

    out = root / "upload_manifest.json"
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(out)
    if not args.no_job_check:
        mark_complete(ws, "upload", output=out.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
