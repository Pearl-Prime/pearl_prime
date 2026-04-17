"""Upload manga release assets to Cloudflare R2 (Pearl_Prime / podcast-aligned env vars).

Uses the same credential names as scripts/podcast/upload_podcast_to_r2.py:
  R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET

Also accepts CF_R2_* aliases used in some operator environments.
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

try:
    import boto3  # type: ignore
    from botocore.config import Config  # type: ignore
    from botocore.exceptions import ClientError  # type: ignore
except ImportError:
    boto3 = None  # type: ignore
    Config = None  # type: ignore
    ClientError = Exception  # type: ignore


def r2_credentials() -> tuple[str, str, str, str]:
    account = (os.environ.get("R2_ACCOUNT_ID") or "").strip()
    key_id = (os.environ.get("R2_ACCESS_KEY_ID") or os.environ.get("CF_R2_ACCESS_KEY") or "").strip()
    secret = (os.environ.get("R2_SECRET_ACCESS_KEY") or os.environ.get("CF_R2_SECRET_KEY") or "").strip()
    bucket = (os.environ.get("R2_BUCKET") or os.environ.get("CF_R2_BUCKET") or "").strip()
    return account, key_id, secret, bucket


def r2_client():
    if boto3 is None or Config is None:
        raise RuntimeError("boto3 required for R2 upload")
    account, key_id, secret, _bucket = r2_credentials()
    if not all([account, key_id, secret]):
        raise RuntimeError("Missing R2_ACCOUNT_ID, R2_ACCESS_KEY_ID (or CF_R2_ACCESS_KEY), R2_SECRET_ACCESS_KEY (or CF_R2_SECRET_KEY)")
    return boto3.client(
        "s3",
        endpoint_url=f"https://{account}.r2.cloudflarestorage.com",
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def put_object_with_retries(
    client: Any,
    *,
    bucket: str,
    key: str,
    body: bytes,
    content_type: str,
    max_attempts: int = 3,
) -> None:
    delay = 2.0
    last_err: Exception | None = None
    for attempt in range(max_attempts):
        try:
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=body,
                ContentType=content_type,
            )
            return
        except ClientError as e:
            last_err = e
            if attempt + 1 >= max_attempts:
                break
            time.sleep(delay)
            delay *= 2.0
    assert last_err is not None
    raise last_err


def presigned_get_url(
    client: Any,
    *,
    bucket: str,
    key: str,
    expires_in: int = 604800,
) -> str:
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )


def upload_manga_release_dir(
    *,
    local_dir: Path,
    brand_id: str,
    date_slug: str,
    key_prefix: str | None = None,
    expires_in: int = 604800,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Upload PDF/CBZ/EPUB (+ optional logs) under ``{brand}/manga/{date}/``."""
    account, _k, _s, bucket = r2_credentials()
    prefix = (key_prefix or f"{brand_id}/manga/{date_slug}/").lstrip("/")
    out: dict[str, Any] = {
        "brand_id": brand_id,
        "date": date_slug,
        "prefix": prefix,
        "objects": [],
        "dry_run": dry_run,
    }
    if dry_run:
        for f in sorted(local_dir.glob("*")):
            if f.is_file():
                key = prefix + f.name
                out["objects"].append(
                    {
                        "key": key,
                        "local": str(f),
                        "presigned_url": f"SIGNED_URL_PLACEHOLDER:{key}",
                    }
                )
        return out

    if not bucket:
        raise RuntimeError("Missing R2_BUCKET (or CF_R2_BUCKET)")
    client = r2_client()
    for f in sorted(local_dir.glob("*")):
        if not f.is_file():
            continue
        suf = f.suffix.lower()
        ctype = "application/pdf" if suf == ".pdf" else "application/epub+zip" if suf == ".epub" else "application/x-cbz" if suf == ".cbz" else "application/octet-stream"
        key = prefix + f.name
        body = f.read_bytes()
        put_object_with_retries(client, bucket=bucket, key=key, body=body, content_type=ctype)
        url = presigned_get_url(client, bucket=bucket, key=key, expires_in=expires_in)
        out["objects"].append({"key": key, "local": str(f), "presigned_url": url})
    return out
