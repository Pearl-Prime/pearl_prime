#!/usr/bin/env python3
"""Rebuild way_stream_sanctuary brand_deliveries feed from R2 delivery manifest.

The Brand Director dashboard reads brand-wizard-app/public/brand_deliveries/
way_stream_sanctuary.json (NOT storefront/public/...).

Default: proxy URLs (/download/<book_id>?week=...) — served by Cloudflare Pages
Function with R2 binding (no presigned URL expiry). Use --use-presign for legacy.

Usage:
  python3 scripts/marketing/rebuild_waystream_feed_from_r2.py \\
    --manifest artifacts/waystream/r2_delivery_manifest.json \\
    --output brand-wizard-app/public/brand_deliveries/way_stream_sanctuary.json

  # Legacy presigned URLs (7-day TTL, requires R2 creds):
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
  python3 scripts/marketing/rebuild_waystream_feed_from_r2.py --use-presign
"""
from __future__ import annotations

import argparse
import json
import os
import random
import sys
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "artifacts/waystream/r2_delivery_manifest.json"
DEFAULT_OUTPUT = REPO / "brand-wizard-app/public/brand_deliveries/way_stream_sanctuary.json"
DEFAULT_BRAND = "way_stream_sanctuary"
PRESERVE_PLATFORMS = frozenset({"kdp", "webtoon"})
# R2/S3 presigned GET expiry must be STRICTLY LESS than 7 days: R2 rejects an
# X-Amz-Expires >= 604800 with HTTP 400 "must be less than a week (in seconds)".
# Confirmed empirically 2026-07-01 (PR #4204). Cap one second under the ceiling.
MAX_PRESIGN_TTL = 604_799
OK_CONTENT_TYPES = frozenset(
    {"application/epub+zip", "application/octet-stream", "binary/octet-stream"}
)


def _r2_client():
    """S3 client for presign refresh (prefers R2_ENDPOINT for EU buckets)."""
    try:
        import boto3
        from botocore.config import Config
    except ImportError as exc:
        raise SystemExit("boto3 required for --refresh-presign: pip install boto3") from exc

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


def _bucket(manifest: dict[str, Any]) -> str:
    return (
        manifest.get("bucket")
        or os.environ.get("R2_BUCKET")
        or os.environ.get("CF_R2_BUCKET")
        or "phoenix-omega-artifacts"
    ).strip()


def _current_iso_week() -> str:
    iso = date.today().isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


def _parse_r2_key(key: str) -> dict[str, str]:
    """Fallback when manifest row lacks week/platform/file."""
    parts = key.split("/")
    if len(parts) < 6:
        raise ValueError(f"cannot parse R2 key: {key}")
    week = parts[3]
    platform = parts[4]
    file_name = parts[5]
    book_id = file_name.replace(".epub", "") if file_name.endswith(".epub") else file_name
    return {"week": week, "platform": platform, "file": file_name, "book_id": book_id}


def _load_existing(output: Path) -> dict[str, Any]:
    if not output.is_file():
        return {}
    try:
        data = json.loads(output.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


_MAX_TTL_WARNED = False


def _effective_presign_ttl(requested: int) -> int:
    global _MAX_TTL_WARNED
    if requested > MAX_PRESIGN_TTL:
        if not _MAX_TTL_WARNED:
            print(
                f"WARN: presigned-ttl {requested} exceeds R2 max {MAX_PRESIGN_TTL}; capping",
                file=sys.stderr,
            )
            _MAX_TTL_WARNED = True
        return MAX_PRESIGN_TTL
    return requested


def _presign_url(client: Any, bucket: str, key: str, ttl: int) -> str:
    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=_effective_presign_ttl(ttl),
    )


def _proxy_url(book_id: str, week: str, proxy_base: str) -> str:
    path = f"/download/{book_id}?week={week}"
    base = proxy_base.rstrip("/")
    return f"{base}{path}" if base else path


def _proxy_url_ok(url: str) -> bool:
    return url.startswith("/download/") and "?week=" in url and "way_stream_sanctuary__" in url


def _manifest_rows(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: dict[str, dict[str, Any]] = {}
    for obj in manifest.get("objects") or []:
        if not isinstance(obj, dict):
            continue
        file_name = str(obj.get("file") or "")
        if not file_name.endswith(".epub"):
            continue
        book_id = str(obj.get("book_id") or file_name.replace(".epub", ""))
        seen[book_id] = obj
    rows = list(seen.values())
    rows.sort(key=lambda o: (str(o.get("week") or ""), str(o.get("file") or "")))
    return rows


def _entry_from_obj(
    obj: dict[str, Any],
    *,
    bucket: str,
    client: Any | None,
    refresh_presign: bool,
    presigned_ttl: int,
    use_proxy: bool,
    proxy_base: str,
) -> dict[str, Any]:
    week = str(obj.get("week") or "")
    platform = str(obj.get("platform") or "amazon_kdp")
    file_name = str(obj.get("file") or "")
    key = str(obj.get("key") or "")
    if not week or not file_name:
        parsed = _parse_r2_key(key)
        week = week or parsed["week"]
        platform = platform or parsed["platform"]
        file_name = file_name or parsed["file"]

    book_id = str(obj.get("book_id") or file_name.replace(".epub", ""))

    if use_proxy:
        url = _proxy_url(book_id, week, proxy_base)
    elif refresh_presign:
        if not client:
            raise SystemExit("--refresh-presign requires R2 credentials")
        if not key:
            raise SystemExit(f"missing key for presign refresh: {file_name}")
        url = _presign_url(client, bucket, key, presigned_ttl)
    else:
        url = str(obj.get("url") or "")

    size = int(obj.get("size") or 0)
    return {
        "file": file_name,
        "url": url,
        "kb": round(size / 1024),
        "r2": True,
    }


def build_feed(
    manifest_path: Path,
    *,
    existing: dict[str, Any],
    refresh_presign: bool,
    presigned_ttl: int,
    use_proxy: bool,
    proxy_base: str,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    brand = str(manifest.get("brand") or existing.get("brand") or DEFAULT_BRAND)
    bucket = _bucket(manifest)
    client = _r2_client() if refresh_presign else None
    rows = _manifest_rows(manifest)

    weeks: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(dict)
    if isinstance(existing.get("weeks"), dict):
        for week, plats in existing["weeks"].items():
            if not isinstance(plats, dict):
                continue
            preserved = {
                plat: list(files)
                for plat, files in plats.items()
                if plat in PRESERVE_PLATFORMS and isinstance(files, list)
            }
            if preserved:
                weeks[str(week)] = preserved

    for obj in rows:
        entry = _entry_from_obj(
            obj,
            bucket=bucket,
            client=client,
            refresh_presign=refresh_presign,
            presigned_ttl=presigned_ttl,
            use_proxy=use_proxy,
            proxy_base=proxy_base,
        )
        week = str(obj.get("week") or _parse_r2_key(str(obj.get("key") or ""))["week"])
        platform = str(obj.get("platform") or "amazon_kdp")
        week_plats = weeks.setdefault(week, {})
        amazon = list(week_plats.get("amazon_kdp") or [])
        amazon = [e for e in amazon if e.get("file") != entry["file"]]
        amazon.append(entry)
        amazon.sort(key=lambda e: str(e.get("file") or ""))
        week_plats["amazon_kdp"] = amazon
        weeks[week] = week_plats

    weeks_sorted = sorted(weeks)
    cur_week = _current_iso_week()
    latest_week = cur_week if cur_week in weeks else (weeks_sorted[-1] if weeks_sorted else cur_week)

    feed = {
        "brand": brand,
        "weeks": {wk: weeks[wk] for wk in weeks_sorted},
        "latest_week": latest_week,
    }
    return feed, rows


def _collect_amazon_entries(feed: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for plats in (feed.get("weeks") or {}).values():
        if not isinstance(plats, dict):
            continue
        for entry in plats.get("amazon_kdp") or []:
            if isinstance(entry, dict):
                out.append(entry)
    return out


def _url_reachable(url: str) -> bool:
    """Check presigned R2 URL (HEAD often 400/405; GET Range is reliable)."""
    req = urllib.request.Request(url, method="GET")
    req.add_header("Range", "bytes=0-0")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            ctype = (resp.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return resp.status in (200, 206) and ctype in OK_CONTENT_TYPES
    except urllib.error.HTTPError as exc:
        if exc.code in (200, 206):
            ctype = (exc.headers.get("Content-Type") or "").split(";")[0].strip().lower()
            return ctype in OK_CONTENT_TYPES
        return False
    except Exception:
        return False


def _verify(
    feed: dict[str, Any],
    manifest_count: int,
    *,
    skip_sample: bool = False,
    use_proxy: bool = False,
    proxy_base: str = "",
) -> int:
    amazon = _collect_amazon_entries(feed)
    r2_true = sum(1 for e in amazon if e.get("r2") is True)
    weeks = feed.get("weeks") or {}
    sample_pool = [e["url"] for e in amazon if e.get("url")]
    sample_n = min(5, len(sample_pool))
    ok = 0
    if sample_pool and not skip_sample:
        if use_proxy:
            for url in random.sample(sample_pool, sample_n):
                if _proxy_url_ok(url):
                    ok += 1
        else:
            check_urls = sample_pool
            if proxy_base:
                check_urls = [f"{proxy_base.rstrip('/')}{u}" for u in sample_pool if u.startswith("/")]
            for url in random.sample(check_urls or sample_pool, sample_n):
                if _url_reachable(url):
                    ok += 1

    print(f"manifest_objects={manifest_count}")
    print(f"feed_amazon_kdp={len(amazon)}")
    print(f"r2_true={r2_true}")
    print(f"weeks={len(weeks)}")
    print(f"latest_week={feed.get('latest_week')}")
    if use_proxy:
        print(f"sample_url_proxy_format={ok}/{sample_n}")
    else:
        print(f"sample_url_http_200={ok}/{sample_n}")

    if len(amazon) != manifest_count:
        print(
            f"ERROR: feed amazon_kdp count {len(amazon)} != manifest {manifest_count}",
            file=sys.stderr,
        )
        return 1
    if r2_true != manifest_count:
        print(f"ERROR: r2_true {r2_true} != manifest {manifest_count}", file=sys.stderr)
        return 1
    if sample_n and ok < sample_n and not skip_sample:
        label = "sample_url_proxy_format" if use_proxy else "sample_url_http_200"
        print(f"ERROR: {label} {ok}/{sample_n} failed", file=sys.stderr)
        if not use_proxy:
            print("HINT: rerun with --refresh-presign (required when manifest URLs are stale)", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Rebuild way_stream_sanctuary feed from R2 manifest")
    ap.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument(
        "--presigned-ttl",
        type=int,
        default=604_799,
        help="Presign TTL seconds (must be < 604800 / 7d; R2 400s on >= a week)",
    )
    ap.add_argument(
        "--use-presign",
        action="store_true",
        help="Emit presigned R2 URLs instead of /download proxy paths",
    )
    ap.add_argument(
        "--proxy-base",
        default=os.environ.get("WAYSTREAM_PROXY_BASE", "").strip(),
        help="Optional absolute origin for proxy URLs (default: site-relative /download/...)",
    )
    ap.add_argument(
        "--refresh-presign",
        action="store_true",
        help="Regenerate presigned URLs via boto3 (requires R2 creds; implies --use-presign)",
    )
    ap.add_argument("--dry-run", action="store_true", help="Build + verify only; do not write output")
    args = ap.parse_args()

    if not args.manifest.is_file():
        print(f"manifest not found: {args.manifest}", file=sys.stderr)
        return 1

    existing = _load_existing(args.output)
    use_proxy = not args.use_presign and not args.refresh_presign
    refresh_presign = args.refresh_presign or (not args.dry_run and not use_proxy)
    feed, rows = build_feed(
        args.manifest,
        existing=existing,
        refresh_presign=refresh_presign,
        presigned_ttl=args.presigned_ttl,
        use_proxy=use_proxy,
        proxy_base=args.proxy_base,
    )

    rc = _verify(
        feed,
        len(rows),
        skip_sample=args.dry_run and not args.refresh_presign and not use_proxy,
        use_proxy=use_proxy,
        proxy_base=args.proxy_base,
    )
    if rc != 0:
        return rc

    if args.dry_run:
        print(f"dry-run: would write {args.output}")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(feed, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
