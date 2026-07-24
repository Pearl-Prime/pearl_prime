#!/usr/bin/env python3
"""Ingest DashScope free-tier stills/clips into social media-bank manifests.

Fourth source alongside ffmpeg families — does NOT pretend Wan/qwen-image are
broll_montage / ken_burns / kinetic_type. Labels:

  family=wan_t2v | wan_i2v | qwen_image
  source_provider=dashscope_free
  content_provenance=INTERIM
  look_gate / review_status stay PENDING until operator PASS

Usage:
  PYTHONPATH=. python3 scripts/social/ingest_dashscope_free_media_bank.py \\
    --image artifacts/social_media_dashscope_free_2026-07-20/stills/foo.png \\
    --topic anxiety --design-family object_metaphor

  PYTHONPATH=. python3 scripts/social/ingest_dashscope_free_media_bank.py \\
    --video artifacts/.../clip.mp4 --topic anxiety --model wan2.7-t2v \\
    --duration-s 5
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
VIDEO_ROOT = REPO / "artifacts/social_media_video_bank_2026-07-19"
IMAGE_ROOT = REPO / "artifacts/social_media_image_bank_2026-07-19"
VIDEO_MANIFEST = VIDEO_ROOT / "MANIFEST.tsv"
IMAGE_MANIFEST = IMAGE_ROOT / "MANIFEST.tsv"
VIDEO_PILOTS = VIDEO_ROOT / "pilots"
IMAGE_PILOTS = IMAGE_ROOT / "pilots" / "dashscope_free"
STUB_GUARD = 50_000

VIDEO_COLUMNS = [
    "asset_id",
    "family",
    "topic_native_family",
    "beat_role",
    "k_index",
    "seed",
    "aspect_bucket",
    "width",
    "height",
    "fps",
    "duration_s_target",
    "duration_s_actual",
    "video_codec",
    "audio_codec",
    "has_audio",
    "bytes",
    "sha256_16",
    "mood_register",
    "source_stock_ref",
    "content_provenance",
    "license_status",
    "production_ready",
    "review_status",
    "render_status",
    "r2_key_planned",
    "r2_uploaded",
    "local_path",
    "generated_by",
    "generated_at",
]

IMAGE_COLUMNS = [
    "image_id",
    "topic",
    "design_family",
    "provider",
    "license_class",
    "license_status",
    "license_verified",
    "face_logo_safe",
    "safety_reviewed",
    "automated_status",
    "bytes",
    "width",
    "height",
    "aspect_native",
    "look_gate",
    "production_ready",
    "local_path",
    "source_url",
    "graduated_at",
]


def _sha16(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _read_tsv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def _write_tsv(path: Path, columns: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=columns, delimiter="\t", extrasaction="ignore")
        w.writeheader()
        for row in rows:
            w.writerow({c: row.get(c, "") for c in columns})
    tmp.replace(path)


def family_for_model(model: str) -> str:
    m = model.lower()
    if "i2v" in m:
        return "wan_i2v"
    if "t2v" in m or m.startswith("wan"):
        return "wan_t2v"
    return "qwen_image"


def ingest_video(
    src: Path,
    *,
    topic: str,
    model: str,
    duration_s: float,
    k_index: int = 0,
    width: int = 720,
    height: int = 1280,
) -> dict[str, Any]:
    if not src.is_file():
        raise FileNotFoundError(src)
    nbytes = src.stat().st_size
    if nbytes < STUB_GUARD:
        raise ValueError(f"stub-guard fail bytes={nbytes} < {STUB_GUARD}")
    family = family_for_model(model)
    asset_id = f"{family}__{topic}__beat__k{k_index:02d}__VERTICAL_9_16"
    VIDEO_PILOTS.mkdir(parents=True, exist_ok=True)
    dest = VIDEO_PILOTS / f"{asset_id}.mp4"
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    rel = str(dest.relative_to(REPO))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = {
        "asset_id": asset_id,
        "family": family,
        "topic_native_family": topic,
        "beat_role": "beat",
        "k_index": str(k_index),
        "seed": "0",
        "aspect_bucket": "VERTICAL_9_16",
        "width": str(width),
        "height": str(height),
        "fps": "24",
        "duration_s_target": str(duration_s),
        "duration_s_actual": str(duration_s),
        "video_codec": "h264",
        "audio_codec": "none",
        "has_audio": "False",
        "bytes": str(nbytes),
        "sha256_16": _sha16(dest),
        "mood_register": "interim_dashscope_free",
        "source_stock_ref": f"source_provider=dashscope_free;model={model}",
        "content_provenance": "INTERIM",
        "license_status": "modelstudio_trial_noncommercial",
        "production_ready": "False",
        "review_status": "unreviewed",
        "render_status": "ok",
        "r2_key_planned": (
            f"social-media-bank/v1/video/{topic}/{family}/9x16/{asset_id}.mp4"
        ),
        "r2_uploaded": "not_attempted",
        "local_path": rel,
        "generated_by": "scripts/social/ingest_dashscope_free_media_bank.py",
        "generated_at": now,
    }
    rows = _read_tsv(VIDEO_MANIFEST)
    rows = [r for r in rows if r.get("asset_id") != asset_id]
    rows.append(row)
    _write_tsv(VIDEO_MANIFEST, VIDEO_COLUMNS, rows)
    return row


def ingest_image(
    src: Path,
    *,
    topic: str,
    design_family: str,
    model: str = "qwen-image-2.0",
    width: int = 720,
    height: int = 1280,
) -> dict[str, Any]:
    if not src.is_file():
        raise FileNotFoundError(src)
    nbytes = src.stat().st_size
    if nbytes < 8_000:
        raise ValueError(f"image stub-sized bytes={nbytes}")
    IMAGE_PILOTS.mkdir(parents=True, exist_ok=True)
    stem = src.stem
    image_id = f"{topic}__dashscope_free__{stem}__{design_family}"[:160]
    dest = IMAGE_PILOTS / f"{image_id}{src.suffix.lower() or '.png'}"
    if src.resolve() != dest.resolve():
        shutil.copy2(src, dest)
    rel = str(dest.relative_to(REPO))
    now = datetime.now(timezone.utc).isoformat()
    row = {
        "image_id": image_id,
        "topic": topic,
        "design_family": design_family,
        "provider": "dashscope_free",
        "license_class": "modelstudio_trial",
        "license_status": "trial_noncommercial",
        "license_verified": "False",
        "face_logo_safe": "True",
        "safety_reviewed": "False",
        "automated_status": "pass_byte_guard",
        "bytes": str(nbytes),
        "width": str(width),
        "height": str(height),
        "aspect_native": "9:16",
        "look_gate": "PENDING",
        "production_ready": "False",
        "local_path": rel,
        "source_url": f"dashscope:{model}",
        "graduated_at": now,
    }
    rows = _read_tsv(IMAGE_MANIFEST)
    rows = [r for r in rows if r.get("image_id") != image_id]
    rows.append(row)
    _write_tsv(IMAGE_MANIFEST, IMAGE_COLUMNS, rows)
    # Also append a sidecar registry note for graduate_image_winners consumers.
    registry_note = IMAGE_ROOT / "dashscope_free_ingest_log.jsonl"
    with registry_note.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"content_provenance": "INTERIM", **row}, ensure_ascii=False) + "\n")
    return row


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--image", type=Path)
    g.add_argument("--video", type=Path)
    ap.add_argument("--topic", required=True)
    ap.add_argument("--design-family", default="object_metaphor")
    ap.add_argument("--model", default="")
    ap.add_argument("--duration-s", type=float, default=5.0)
    ap.add_argument("--k-index", type=int, default=0)
    args = ap.parse_args(argv)

    if args.image:
        model = args.model or "qwen-image-2.0"
        row = ingest_image(
            args.image,
            topic=args.topic,
            design_family=args.design_family,
            model=model,
        )
    else:
        model = args.model or "wan2.7-t2v"
        row = ingest_video(
            args.video,
            topic=args.topic,
            model=model,
            duration_s=args.duration_s,
            k_index=args.k_index,
        )
    print(json.dumps(row, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
