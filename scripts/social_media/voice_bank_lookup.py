#!/usr/bin/env python3
"""Resolve social CosyVoice voice-bank rows by atom_id → MP3 path + speakable_text.

NEW-ARTIFACT-JUSTIFIED: single join surface for VCE + social shorts (no parallel
caption/audio systems). Fail-closed when status≠ok or speakable missing.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "artifacts" / "social_media_voice_bank_2026-07-19" / "MANIFEST.tsv"
DEFAULT_LOCAL_ROOT = REPO / "artifacts" / "social_media_voice_bank_2026-07-19"


@dataclass(frozen=True)
class VoiceBankHit:
    atom_id: str
    persona: str
    topic: str
    locale: str
    voice_id: str
    r2_key: str
    local_mp3: Path | None
    speakable_text: str
    status: str
    sha256: str
    bytes: int


class VoiceBankError(LookupError):
    pass


def _parse_manifest(path: Path) -> dict[str, dict[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines:
        raise VoiceBankError(f"empty manifest: {path}")
    cols = lines[0].split("\t")
    out: dict[str, dict[str, str]] = {}
    for line in lines[1:]:
        parts = line.split("\t")
        while len(parts) < len(cols):
            parts.append("")
        row = dict(zip(cols, parts[: len(cols)]))
        aid = row.get("atom_id") or ""
        if aid:
            out[aid] = row
    return out


class VoiceBankIndex:
    def __init__(
        self,
        manifest: Path | None = None,
        local_root: Path | None = None,
        *,
        allow_r2_download: bool = False,
    ) -> None:
        self.manifest_path = Path(manifest) if manifest else DEFAULT_MANIFEST
        self.local_root = Path(local_root) if local_root else DEFAULT_LOCAL_ROOT
        self.allow_r2_download = allow_r2_download
        if not self.manifest_path.is_file():
            raise VoiceBankError(f"manifest not found: {self.manifest_path}")
        self._by_id = _parse_manifest(self.manifest_path)

    def get_row(self, atom_id: str) -> dict[str, str] | None:
        return self._by_id.get(atom_id)

    def local_path_for_row(self, row: dict[str, str]) -> Path:
        locale = row.get("locale") or "en-US"
        persona = row.get("persona") or ""
        topic = row.get("topic") or ""
        aid = row.get("atom_id") or ""
        return self.local_root / "mp3" / locale / persona / topic / f"{aid}.mp3"

    def ensure_local_mp3(self, row: dict[str, str]) -> Path:
        local = self.local_path_for_row(row)
        if local.is_file() and local.stat().st_size >= 10_000:
            return local
        # also check pilot trees
        for alt_root in (
            self.local_root / "pilot_20260719b",
            self.local_root / "pilot_mp3_tree",
            self.local_root / "mp3",
        ):
            cand = (
                alt_root
                / (row.get("locale") or "en-US")
                / (row.get("persona") or "")
                / (row.get("topic") or "")
                / f"{row.get('atom_id')}.mp3"
            )
            if cand.is_file() and cand.stat().st_size >= 10_000:
                return cand
            # pilot_20260719b may nest under mp3/
            cand2 = (
                alt_root
                / "mp3"
                / (row.get("locale") or "en-US")
                / (row.get("persona") or "")
                / (row.get("topic") or "")
                / f"{row.get('atom_id')}.mp3"
            )
            if cand2.is_file() and cand2.stat().st_size >= 10_000:
                return cand2
        if not self.allow_r2_download:
            raise VoiceBankError(
                f"local MP3 missing for {row.get('atom_id')} (expected {local}); "
                "pass allow_r2_download=True or sync bank mp3 tree"
            )
        return self._download_r2(row, local)

    def _download_r2(self, row: dict[str, str], dest: Path) -> Path:
        import boto3
        from botocore.config import Config

        key = row.get("r2_key") or ""
        if not key:
            raise VoiceBankError(f"no r2_key for {row.get('atom_id')}")
        endpoint = (os.environ.get("R2_ENDPOINT") or "").strip()
        if not endpoint:
            account = os.environ.get("CLOUDFLARE_ACCOUNT_ID") or os.environ.get("R2_ACCOUNT_ID")
            if not account:
                raise VoiceBankError("missing R2_ENDPOINT / account id for download")
            endpoint = f"https://{account}.r2.cloudflarestorage.com"
        if not endpoint.startswith("http"):
            endpoint = "https://" + endpoint
        bucket = os.environ.get("R2_BUCKET") or "phoenix-omega-artifacts"
        client = boto3.client(
            "s3",
            endpoint_url=endpoint.rstrip("/"),
            aws_access_key_id=os.environ["R2_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["R2_SECRET_ACCESS_KEY"],
            region_name="auto",
            config=Config(signature_version="s3v4", retries={"max_attempts": 3}),
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        client.download_file(bucket, key, str(dest))
        if dest.stat().st_size < 10_000:
            raise VoiceBankError(f"downloaded MP3 too small: {dest}")
        return dest

    def resolve(self, atom_id: str, *, require_audio: bool = True) -> VoiceBankHit:
        row = self._by_id.get(atom_id)
        if not row:
            raise VoiceBankError(f"atom_id not in manifest: {atom_id}")
        status = row.get("status") or ""
        if status != "ok":
            raise VoiceBankError(f"atom_id {atom_id} status={status!r} (need ok)")
        speakable = (row.get("speakable_text") or "").strip()
        if not speakable:
            raise VoiceBankError(
                f"atom_id {atom_id} missing speakable_text — run backfill_speakable_text.py"
            )
        local: Path | None = None
        if require_audio:
            local = self.ensure_local_mp3(row)
        else:
            try:
                local = self.ensure_local_mp3(row)
            except VoiceBankError:
                local = None
        return VoiceBankHit(
            atom_id=atom_id,
            persona=row.get("persona") or "",
            topic=row.get("topic") or "",
            locale=row.get("locale") or "en-US",
            voice_id=row.get("voice_id") or "",
            r2_key=row.get("r2_key") or "",
            local_mp3=local,
            speakable_text=speakable,
            status=status,
            sha256=row.get("sha256") or "",
            bytes=int(row.get("bytes") or 0),
        )


def load_index(
    manifest: Path | str | None = None,
    local_root: Path | str | None = None,
    *,
    allow_r2_download: bool = False,
) -> VoiceBankIndex:
    return VoiceBankIndex(
        Path(manifest) if manifest else None,
        Path(local_root) if local_root else None,
        allow_r2_download=allow_r2_download,
    )


def resolve_atom(
    atom_id: str,
    *,
    manifest: Path | str | None = None,
    allow_r2_download: bool = False,
    require_audio: bool = True,
) -> VoiceBankHit:
    return load_index(manifest, allow_r2_download=allow_r2_download).resolve(
        atom_id, require_audio=require_audio
    )
