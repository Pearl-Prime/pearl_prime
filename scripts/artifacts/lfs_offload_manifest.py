#!/usr/bin/env python3
"""TSV manifest helpers for LFS→R2 offload (LFS_TO_R2_OFFLOAD_V1_SPEC).

Manifests live under artifacts/manifests/lfs_offload/<slug>.tsv with columns:
    repo_path, r2_key, bytes, sha256

Manifests store R2 keys only — never presigned URLs (presigns expire ≤1 week).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

MANIFEST_DIR = "artifacts/manifests/lfs_offload"
HEADER = ("repo_path", "r2_key", "bytes", "sha256")
META_PREFIX = "# "


@dataclass(frozen=True)
class OffloadEntry:
    repo_path: str
    r2_key: str
    bytes: int
    sha256: str


@dataclass(frozen=True)
class OffloadManifest:
    slug: str
    namespace: str
    bucket: str
    produced_at: str
    entries: tuple[OffloadEntry, ...]

    def by_repo_path(self) -> dict[str, OffloadEntry]:
        return {e.repo_path: e for e in self.entries}

    def by_basename(self) -> dict[str, OffloadEntry]:
        return {Path(e.repo_path).name: e for e in self.entries}


def sha256_file(path: Path, chunk_size: int = 65536) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()


def _parse_meta(line: str) -> tuple[str, str] | None:
    if not line.startswith(META_PREFIX):
        return None
    body = line[len(META_PREFIX) :].strip()
    if ":" not in body:
        return None
    key, val = body.split(":", 1)
    return key.strip(), val.strip()


def load_manifest_tsv(path: Path) -> OffloadManifest:
    slug = namespace = bucket = produced_at = ""
    entries: list[OffloadEntry] = []
    seen_header = False
    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw.strip():
            continue
        meta = _parse_meta(raw)
        if meta:
            key, val = meta
            if key == "slug":
                slug = val
            elif key == "namespace":
                namespace = val
            elif key == "bucket":
                bucket = val
            elif key == "produced_at":
                produced_at = val
            continue
        cols = raw.split("\t")
        if cols == list(HEADER):
            seen_header = True
            continue
        if not seen_header and cols[0] == "repo_path":
            seen_header = True
            continue
        if len(cols) < 4:
            continue
        repo_path, r2_key, nbytes, sha = cols[0], cols[1], int(cols[2]), cols[3]
        entries.append(OffloadEntry(repo_path, r2_key, nbytes, sha))
    if not slug:
        slug = path.stem
    if not produced_at:
        produced_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return OffloadManifest(slug, namespace, bucket, produced_at, tuple(entries))


def write_manifest_tsv(
    path: Path,
    *,
    slug: str,
    namespace: str,
    bucket: str,
    entries: list[OffloadEntry],
) -> None:
    produced_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"{META_PREFIX}slug: {slug}",
        f"{META_PREFIX}namespace: {namespace}",
        f"{META_PREFIX}bucket: {bucket}",
        f"{META_PREFIX}produced_at: {produced_at}",
        f"{META_PREFIX}generated_by: scripts/artifacts/lfs_offload_manifest.py",
        "\t".join(HEADER),
    ]
    for e in entries:
        lines.append(f"{e.repo_path}\t{e.r2_key}\t{e.bytes}\t{e.sha256}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def discover_manifests(repo_root: Path) -> Iterator[Path]:
    d = repo_root / MANIFEST_DIR
    if not d.is_dir():
        return
    yield from sorted(d.glob("*.tsv"))


def load_all_manifests(repo_root: Path) -> dict[str, OffloadEntry]:
    """Flat repo_path → entry index across every offload manifest."""
    index: dict[str, OffloadEntry] = {}
    for mf in discover_manifests(repo_root):
        for e in load_manifest_tsv(mf).entries:
            index[e.repo_path] = e
    return index
