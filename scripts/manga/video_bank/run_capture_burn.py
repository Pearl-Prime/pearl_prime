#!/usr/bin/env python3
"""Run character-capture burns via the exempt DashScope free-media client.

IMPORTS ``scripts.social.dashscope_free_media`` only — this file must contain
ZERO DashScope native async headers or aigc service path literals.

Cloud engines only for this lane: ``wan2.7-t2v`` / ``wan2.7-i2v``. Self-hosted
engines are rejected. Honors:
  - PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1 + DASHSCOPE_FREE_QUOTA_API_KEY
  - --preflight-only (no burn)
  - --max-seconds hard cap
  - per-run quota ledger under the proof root
  - stub guard ≥50KB per clip

Usage:
  PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1 \\
  PYTHONPATH=. python3 scripts/manga/video_bank/run_capture_burn.py \\
    --manifest path/to/capture.json --proof-root artifacts/qa/... --preflight-only
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable, Optional

from scripts.manga.video_bank import ALLOWED_CLOUD_ENGINES, STUB_GUARD_BYTES
from scripts.manga.video_bank._schema import validate_manifest

# Import client symbols only — never re-declare DashScope endpoints here.
from scripts.social.dashscope_free_media import (  # noqa: E402
    DashScopeFreeMediaError,
    run_video,
)

REPO = Path(__file__).resolve().parents[3]


@dataclass
class QuotaLedger:
    planned_seconds: float = 0.0
    requested_seconds: float = 0.0
    spent_seconds: float = 0.0
    reserve_seconds: float = 0.0
    max_seconds_cap: float | None = None
    remaining_under_cap: float | None = None
    clips: list[dict[str, Any]] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def assert_allow_env(*, require_allow: bool = True) -> None:
    """Lane 01 contract: ALLOW=1 requires FREE key (no paid-key silent fallback)."""
    allow = (os.environ.get("PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW") or "").strip() == "1"
    free = (os.environ.get("DASHSCOPE_FREE_QUOTA_API_KEY") or "").strip()
    if require_allow and not allow:
        raise DashScopeFreeMediaError(
            "BLOCKER: set PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1 for capture burn "
            "(operator-present only; never cron)."
        )
    if allow and not free:
        raise DashScopeFreeMediaError(
            "BLOCKER: PHOENIX_DASHSCOPE_FREE_MEDIA_ALLOW=1 requires "
            "DASHSCOPE_FREE_QUOTA_API_KEY (no fallback to DASHSCOPE_API_KEY/QWEN_API_KEY)."
        )


def assert_cloud_engine(engine: str) -> None:
    if engine not in ALLOWED_CLOUD_ENGINES:
        raise ValueError(
            f"engine {engine!r} rejected — Lane 04 cloud-only engines are "
            f"{sorted(ALLOWED_CLOUD_ENGINES)}; self-hosted / r2v deferred"
        )


def compute_quota_plan(
    manifest: dict[str, Any],
    *,
    max_seconds: float | None,
    clip_filter: set[str] | None = None,
) -> QuotaLedger:
    budget = manifest.get("quota_budget") or {}
    planned = float(budget.get("planned_seconds") or 0)
    reserve = float(budget.get("reserve_seconds") or 0)
    ledger = QuotaLedger(
        planned_seconds=planned,
        reserve_seconds=reserve,
        max_seconds_cap=max_seconds,
    )
    requested = 0.0
    for cs in manifest.get("capture_sets") or []:
        clip_id = str(cs.get("clip_id") or "")
        if clip_filter is not None and clip_id not in clip_filter:
            continue
        engine = str(cs.get("engine") or "")
        assert_cloud_engine(engine)
        dur = float(cs.get("duration_s") or 0)
        requested += dur
        ledger.clips.append(
            {
                "clip_id": clip_id,
                "engine": engine,
                "duration_s": dur,
                "status": "planned",
            }
        )
    ledger.requested_seconds = requested
    if max_seconds is not None:
        if requested > max_seconds + 1e-9:
            raise ValueError(
                f"--max-seconds={max_seconds} refuses plan requesting {requested}s"
            )
        ledger.remaining_under_cap = max_seconds - requested
    # Reserve is a planning floor vs remaining free quota — recorded, not spent here.
    if reserve > 0:
        ledger.notes.append(
            f"reserve_seconds={reserve} must remain after burn (Lane 02 spend order)."
        )
    return ledger


def write_ledger(proof_root: Path, ledger: QuotaLedger) -> Path:
    proof_root.mkdir(parents=True, exist_ok=True)
    path = proof_root / "quota_ledger.json"
    path.write_text(json.dumps(ledger.to_dict(), indent=2) + "\n", encoding="utf-8")
    return path


def run_burn(
    manifest: dict[str, Any],
    *,
    proof_root: Path,
    max_seconds: float | None = None,
    preflight_only: bool = False,
    clip_ids: list[str] | None = None,
    video_runner: Optional[Callable[..., Any]] = None,
) -> QuotaLedger:
    validate_manifest(manifest)
    for cs in manifest.get("capture_sets") or []:
        assert_cloud_engine(str(cs.get("engine") or ""))

    filt = set(clip_ids) if clip_ids else None
    ledger = compute_quota_plan(manifest, max_seconds=max_seconds, clip_filter=filt)
    write_ledger(proof_root, ledger)

    if preflight_only:
        ledger.notes.append("preflight_only — no cloud submit")
        write_ledger(proof_root, ledger)
        return ledger

    assert_allow_env(require_allow=True)
    runner = video_runner or run_video
    clips_dir = proof_root / "clips"
    clips_dir.mkdir(parents=True, exist_ok=True)
    anchor = manifest.get("anchor") or {}
    image_url = anchor.get("public_url") or None
    spent = 0.0

    for row in ledger.clips:
        cs = next(
            c for c in manifest["capture_sets"] if c["clip_id"] == row["clip_id"]
        )
        engine = str(cs["engine"])
        dur = float(cs["duration_s"])
        if max_seconds is not None and spent + dur > max_seconds + 1e-9:
            row["status"] = "skipped_max_seconds"
            ledger.notes.append(f"refused {row['clip_id']}: would exceed --max-seconds")
            break
        if engine.endswith("-i2v") and not image_url:
            raise DashScopeFreeMediaError(
                f"clip {row['clip_id']}: wan2.7-i2v requires anchor.public_url"
            )
        result = runner(
            prompt=str(cs["prompt"]),
            out_dir=clips_dir,
            model=engine,
            duration_s=int(dur),
            image_url=image_url if engine.endswith("-i2v") else None,
            stem=row["clip_id"],
        )
        nbytes = int(getattr(result, "bytes", 0) or 0)
        local_path = Path(getattr(result, "local_path"))
        if nbytes < STUB_GUARD_BYTES:
            raise DashScopeFreeMediaError(
                f"stub guard fail: {local_path} bytes={nbytes} < {STUB_GUARD_BYTES}"
            )
        spent += dur
        row["status"] = "captured"
        row["bytes"] = nbytes
        row["local_path"] = str(local_path)
        row["task_id"] = getattr(result, "task_id", "")
        ledger.spent_seconds = spent
        if max_seconds is not None:
            ledger.remaining_under_cap = max_seconds - spent
        write_ledger(proof_root, ledger)

    write_ledger(proof_root, ledger)
    return ledger


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--proof-root", type=Path, required=True)
    ap.add_argument("--preflight-only", action="store_true")
    ap.add_argument("--max-seconds", type=float, default=None)
    ap.add_argument("--clip-id", action="append", default=None)
    return ap


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        ledger = run_burn(
            manifest,
            proof_root=args.proof_root,
            max_seconds=args.max_seconds,
            preflight_only=args.preflight_only,
            clip_ids=args.clip_id,
        )
    except (DashScopeFreeMediaError, ValueError, FileNotFoundError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(ledger.to_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
