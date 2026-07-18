#!/usr/bin/env python3
"""Weekly deep-verify for LFS→R2 offloaded assets (LFS_TO_R2_OFFLOAD_V1_SPEC §4.3).

Fetches each manifest entry from R2 and verifies ContentLength + sha256.
Head-only mode (--head-only) checks sizes without downloading bodies.

Run:
    PYTHONPATH=. PHOENIX_OMEGA_REMOTE=local-override \\
        python3 scripts/ci/deep_verify_r2_offload.py

Exit: 0 pass; 1 any mismatch or missing object.
"""
from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.artifacts.lfs_offload_manifest import discover_manifests, load_manifest_tsv  # noqa: E402


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def _r2_client():
    from scripts.artifacts.r2_sync import _load_config, _r2_client as client_fn, _bucket_name  # noqa: E402

    return client_fn(), _bucket_name(_load_config())


def verify_manifest(mf_path: Path, *, head_only: bool) -> list[str]:
    manifest = load_manifest_tsv(mf_path)
    client, default_bucket = _r2_client()
    bucket = manifest.bucket or default_bucket
    errors: list[str] = []

    for entry in manifest.entries:
        try:
            head = client.head_object(Bucket=bucket, Key=entry.r2_key)
        except Exception as e:
            errors.append(f"{entry.repo_path}: missing in R2 ({e.__class__.__name__})")
            continue
        if head["ContentLength"] != entry.bytes:
            errors.append(
                f"{entry.repo_path}: bytes mismatch "
                f"(manifest={entry.bytes}, r2={head['ContentLength']})"
            )
            continue
        if head_only:
            continue
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp_path = Path(tmp.name)
        try:
            client.download_file(bucket, entry.r2_key, str(tmp_path))
            actual = _sha256_file(tmp_path)
            if actual != entry.sha256:
                errors.append(
                    f"{entry.repo_path}: sha256 mismatch "
                    f"(manifest={entry.sha256[:12]}…, r2={actual[:12]}…)"
                )
        finally:
            tmp_path.unlink(missing_ok=True)

    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Deep-verify R2 offload manifests")
    ap.add_argument("--repo-root", type=Path, default=REPO_ROOT)
    ap.add_argument("--manifest-dir", default="artifacts/manifests/lfs_offload")
    ap.add_argument("--head-only", action="store_true", help="skip sha256 body download")
    args = ap.parse_args(argv)

    manifests = list(discover_manifests(args.repo_root))
    if not manifests:
        print("R2-OFFLOAD DEEP-VERIFY: no manifests found (PASS vacuous)", file=sys.stderr)
        return 0

    all_errors: list[str] = []
    for mf in manifests:
        all_errors.extend(verify_manifest(mf, head_only=args.head_only))

    if not all_errors:
        print(f"R2-OFFLOAD DEEP-VERIFY: PASS ({len(manifests)} manifest(s))", file=sys.stderr)
        return 0
    for e in all_errors:
        print(f"FAIL: {e}", file=sys.stderr)
    print(f"R2-OFFLOAD DEEP-VERIFY: {len(all_errors)} error(s) — blocking", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
