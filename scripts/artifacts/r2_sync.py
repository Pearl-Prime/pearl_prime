#!/usr/bin/env python3
"""Cloudflare R2 sync for Phoenix Omega binary artifacts.

Layer 2 of the cloud-native agents migration. Binary blobs (rendered manga
pages, character portraits, QA-run epubs) live in R2; the repo holds only
manifests with sha256 + R2 keys.

Usage:
    # Upload a directory of artifacts and write a manifest
    r2_sync.py push \\
        --namespace manga_rendered_books \\
        --src out/rendered/series_xyz/ep_001/ \\
        --series-id series_xyz \\
        --book-id ep_001 \\
        --manifest artifacts/manifests/manga_rendered_books/series_xyz/ep_001.yaml

    # Pull artifacts referenced by a manifest into local cache
    r2_sync.py pull --manifest artifacts/manifests/manga_rendered_books/series_xyz/ep_001.yaml

    # Verify a manifest matches what's actually in R2
    r2_sync.py verify --manifest artifacts/manifests/.../ep_001.yaml

    # List artifacts under a namespace prefix
    r2_sync.py ls --namespace manga_rendered_books

Auth: reads CLOUDFLARE_ACCOUNT_ID + R2_ACCESS_KEY_ID + R2_SECRET_ACCESS_KEY
from environment. Optional R2_ENDPOINT overrides the S3 endpoint URL — set
this for EU-jurisdiction or non-default-jurisdiction buckets where the host
is NOT https://<account_id>.r2.cloudflarestorage.com (Cloudflare prints the
correct URL on the R2 token result page). In Codespaces credentials come
from Codespaces secrets; in Pearl Star they come from the
integration_env_registry.py Keychain bridge; in Actions from repo secrets.

Refuses to run on a local laptop unless PHOENIX_OMEGA_REMOTE=local-override.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONFIG = REPO / "config" / "artifacts" / "r2_buckets.yaml"
SCHEMA = REPO / "schemas" / "artifacts" / "manifest.schema.json"
LOCAL_CACHE_DIR = REPO / "artifacts" / "r2_cache"


# ─── Errors ─────────────────────────────────────────────────────────────────


class R2SyncError(RuntimeError):
    pass


# ─── Lazy imports (boto3 only required at runtime, not at import time) ─────


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_config() -> dict[str, Any]:
    if not CONFIG.exists():
        raise R2SyncError(f"R2 config missing: {CONFIG}")
    return _load_yaml(CONFIG)


def _r2_client():
    """Return a boto3 client wired to R2's S3-compatible endpoint."""
    try:
        import boto3  # type: ignore
        from botocore.config import Config  # type: ignore
    except ImportError:
        raise R2SyncError(
            "boto3 not installed. In Codespaces this is in requirements.txt; "
            "if missing run: pip install boto3"
        )

    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    missing = [
        n
        for n, v in [
            ("CLOUDFLARE_ACCOUNT_ID", account_id),
            ("R2_ACCESS_KEY_ID", access_key),
            ("R2_SECRET_ACCESS_KEY", secret_key),
        ]
        if not v
    ]
    if missing:
        raise R2SyncError(
            f"Missing R2 credentials: {missing}. "
            "Add to Codespaces secrets at https://github.com/settings/codespaces "
            "or generate at https://dash.cloudflare.com → R2 → Manage R2 API Tokens."
        )

    endpoint = os.environ.get("R2_ENDPOINT") or f"https://{account_id}.r2.cloudflarestorage.com"
    return boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
        config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
    )


# ─── sha256 + manifest helpers ──────────────────────────────────────────────


def _sha256_file(path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def _content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".svg": "image/svg+xml",
        ".pdf": "application/pdf",
        ".epub": "application/epub+zip",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".wav": "audio/wav",
        ".json": "application/json",
        ".yaml": "application/yaml",
        ".yml": "application/yaml",
        ".txt": "text/plain",
        ".md": "text/markdown",
    }.get(suffix, "application/octet-stream")


def _validate_manifest(data: dict[str, Any]) -> list[str]:
    try:
        import jsonschema  # type: ignore

        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        return [
            f"{'.'.join(str(p) for p in err.absolute_path)}: {err.message}"
            for err in validator.iter_errors(data)
        ]
    except ImportError:
        # Soft check
        errors = []
        for req in ("manifest_schema", "manifest_id", "namespace", "bucket", "artifacts"):
            if req not in data:
                errors.append(f"missing required: {req}")
        return errors


def _write_manifest(path: Path, data: dict[str, Any]) -> None:
    import yaml  # type: ignore

    errors = _validate_manifest(data)
    if errors:
        raise R2SyncError(f"manifest invalid:\n  - " + "\n  - ".join(errors))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "# Auto-generated by scripts/artifacts/r2_sync.py — do not hand-edit.\n"
        + yaml.safe_dump(data, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


# ─── Operations ─────────────────────────────────────────────────────────────


def _resolve_namespace(cfg: dict[str, Any], namespace: str) -> dict[str, Any]:
    ns_cfg = (cfg.get("namespaces") or {}).get(namespace)
    if not ns_cfg:
        valid = list((cfg.get("namespaces") or {}).keys())
        raise R2SyncError(f"unknown namespace: {namespace}. valid: {valid}")
    return ns_cfg


def _bucket_name(cfg: dict[str, Any]) -> str:
    return ((cfg.get("buckets") or {}).get("artifacts") or {}).get("name") or "phoenix-omega-artifacts"


def cmd_push(args: argparse.Namespace) -> int:
    cfg = _load_config()
    ns_cfg = _resolve_namespace(cfg, args.namespace)
    bucket = _bucket_name(cfg)
    prefix = ns_cfg["prefix"]

    src = Path(args.src).resolve()
    if not src.exists() or not src.is_dir():
        raise R2SyncError(f"--src must be an existing directory: {src}")

    files = sorted(p for p in src.rglob("*") if p.is_file())
    if not files:
        raise R2SyncError(f"no files found under {src}")

    # Determine key prefix from optional series/book/run ids
    key_path_parts = [prefix.rstrip("/")]
    for opt in (args.series_id, args.book_id, args.run_id):
        if opt:
            key_path_parts.append(opt)
    key_prefix = "/".join(key_path_parts) + "/"

    client = _r2_client()
    artifacts = []
    total_bytes = 0

    for f in files:
        rel = f.relative_to(src)
        key = key_prefix + str(rel).replace(os.sep, "/")
        sha = _sha256_file(f)
        size = f.stat().st_size
        ctype = _content_type(f)

        if args.dry_run:
            print(f"would upload {f}  →  s3://{bucket}/{key}  ({size:,} B, {sha[:12]})")
        else:
            print(f"upload {rel}  ({size:,} B)")
            with f.open("rb") as fh:
                client.put_object(
                    Bucket=bucket,
                    Key=key,
                    Body=fh,
                    ContentType=ctype,
                    Metadata={"sha256": sha},
                )

        artifacts.append(
            {
                "key": key,
                "sha256": sha,
                "bytes": size,
                "content_type": ctype,
            }
        )
        total_bytes += size

    manifest_id = key_prefix.rstrip("/")
    manifest = {
        "manifest_schema": "1.0.0",
        "manifest_id": manifest_id,
        "namespace": args.namespace,
        "bucket": bucket,
        "produced_by": os.environ.get("PHOENIX_OMEGA_REMOTE", "unknown"),
        "produced_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "artifacts": artifacts,
        "total_bytes": total_bytes,
        "total_artifacts": len(artifacts),
    }
    if args.series_id:
        manifest["series_id"] = args.series_id
    if args.book_id:
        manifest["book_id"] = args.book_id
    if args.run_id:
        manifest["run_id"] = args.run_id

    manifest_path = Path(args.manifest) if args.manifest else (
        REPO / "artifacts" / "manifests" / args.namespace / f"{manifest_id.replace('/', '__')}.yaml"
    )
    _write_manifest(manifest_path, manifest)
    print(f"\n✓ pushed {len(artifacts)} artifacts ({total_bytes:,} B)")
    print(f"✓ manifest: {manifest_path.relative_to(REPO)}")
    return 0


def cmd_pull(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).resolve()
    manifest = _load_yaml(manifest_path)
    errors = _validate_manifest(manifest)
    if errors:
        raise R2SyncError(f"manifest invalid:\n  - " + "\n  - ".join(errors))

    client = _r2_client()
    bucket = manifest["bucket"]
    cache_dir = LOCAL_CACHE_DIR / manifest["manifest_id"]
    cache_dir.mkdir(parents=True, exist_ok=True)

    pulled = 0
    skipped = 0
    for art in manifest["artifacts"]:
        key = art["key"]
        sha = art["sha256"]
        local = cache_dir / Path(key).name
        if local.exists() and _sha256_file(local) == sha:
            skipped += 1
            continue
        if args.dry_run:
            print(f"would download s3://{bucket}/{key}  →  {local.relative_to(REPO)}")
        else:
            print(f"download {key}")
            client.download_file(bucket, key, str(local))
            actual = _sha256_file(local)
            if actual != sha:
                local.unlink()
                raise R2SyncError(f"sha256 mismatch on {key}: expected {sha}, got {actual}")
        pulled += 1

    print(f"\n✓ pulled {pulled}, cached-skip {skipped}")
    print(f"✓ cache: {cache_dir.relative_to(REPO)}")
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest).resolve()
    manifest = _load_yaml(manifest_path)
    errors = _validate_manifest(manifest)
    if errors:
        print("❌ manifest schema errors:")
        for e in errors:
            print(f"   - {e}")
        return 1

    client = _r2_client()
    bucket = manifest["bucket"]
    bad = []
    for art in manifest["artifacts"]:
        key = art["key"]
        try:
            head = client.head_object(Bucket=bucket, Key=key)
        except Exception as e:
            bad.append(f"{key}: missing in R2 ({e.__class__.__name__})")
            continue
        if head["ContentLength"] != art["bytes"]:
            bad.append(
                f"{key}: bytes mismatch (manifest={art['bytes']}, r2={head['ContentLength']})"
            )

    if bad:
        print(f"❌ {len(bad)} mismatches")
        for b in bad:
            print(f"   - {b}")
        return 1
    print(f"✓ all {len(manifest['artifacts'])} artifacts present in R2 with correct size")
    return 0


def cmd_ls(args: argparse.Namespace) -> int:
    cfg = _load_config()
    ns_cfg = _resolve_namespace(cfg, args.namespace)
    bucket = _bucket_name(cfg)
    prefix = ns_cfg["prefix"]
    if args.subprefix:
        prefix = prefix + args.subprefix

    client = _r2_client()
    paginator = client.get_paginator("list_objects_v2")
    n = 0
    total_bytes = 0
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents") or []:
            print(f"{obj['Size']:>12}  {obj['Key']}")
            n += 1
            total_bytes += obj["Size"]
            if args.head and n >= args.head:
                break
        if args.head and n >= args.head:
            break
    print(f"\n{n} objects, {total_bytes:,} bytes")
    return 0


# ─── CLI ────────────────────────────────────────────────────────────────────


def _main() -> int:
    # Hard guard: refuse local laptop unless override.
    # Add repo root to sys.path so the import works when run as a script.
    if str(REPO) not in sys.path:
        sys.path.insert(0, str(REPO))
    try:
        from scripts.agent.assert_remote import assert_remote  # type: ignore

        assert_remote(allow_override=True)
    except ImportError as e:
        sys.stderr.write(f"⚠️  assert_remote unavailable ({e}); proceeding without guard.\n")
    except Exception as e:
        sys.stderr.write(f"❌ assert_remote: {e}\n")
        return 2

    p = argparse.ArgumentParser(description="Phoenix Omega R2 artifact sync")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("push", help="upload directory + write manifest")
    sp.add_argument("--namespace", required=True)
    sp.add_argument("--src", required=True)
    sp.add_argument("--manifest", help="output manifest path (auto-derived if omitted)")
    sp.add_argument("--series-id")
    sp.add_argument("--book-id")
    sp.add_argument("--run-id")
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(fn=cmd_push)

    sp = sub.add_parser("pull", help="download artifacts referenced by manifest")
    sp.add_argument("--manifest", required=True)
    sp.add_argument("--dry-run", action="store_true")
    sp.set_defaults(fn=cmd_pull)

    sp = sub.add_parser("verify", help="check manifest against actual R2 state")
    sp.add_argument("--manifest", required=True)
    sp.set_defaults(fn=cmd_verify)

    sp = sub.add_parser("ls", help="list R2 objects under a namespace")
    sp.add_argument("--namespace", required=True)
    sp.add_argument("--subprefix", default="")
    sp.add_argument("--head", type=int, default=0, help="cap listing at N")
    sp.set_defaults(fn=cmd_ls)

    args = p.parse_args()
    try:
        return args.fn(args)
    except R2SyncError as e:
        sys.stderr.write(f"❌ {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(_main())
