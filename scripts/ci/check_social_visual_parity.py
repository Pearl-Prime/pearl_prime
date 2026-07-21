#!/usr/bin/env python3
"""
Social visual golden parity CI gate — DORMANT until operator approval.

Mirrors scripts/ci/check_pearl_news_sidebar_parity.py's capture-once-defend-
forever pattern, applied to the social visual rebuild's shortform MP4s and
static/carousel winners instead of the Pearl News sidebar HTML.

Reads artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL/CANONICAL_SOCIAL_VISUAL_METADATA.json.
If that file does not exist, the golden has not been frozen yet (the operator
has not approved a look) — this gate SKIPS with exit 0. Once the operator
approves and scripts/social/freeze_social_visual_golden.py populates the
metadata + byte copies, this gate starts defending: every listed asset must
still exist at its recorded path with a matching sha256, and (for videos)
matching width/height/duration within tolerance.

Authority:
  artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md
  artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL/README.md
  scripts/ci/check_pearl_news_sidebar_parity.py (pattern this mirrors)

Usage:
  python3 scripts/ci/check_social_visual_parity.py
    -> exit 0 (SKIP, golden not frozen) OR exit 0 (PASS, parity held)
       OR exit 1 (FAIL, drift detected) with a per-asset failure list
  python3 scripts/ci/check_social_visual_parity.py --verbose
    -> also print per-asset sha256/dims/duration on PASS

Exit codes:
  0   -- SKIP (no golden yet) or PASS (parity held)
  1   -- one or more assets drifted (missing, hash mismatch, dims/duration mismatch)
  2   -- metadata file present but unparseable
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL"
METADATA_PATH = GOLDEN_DIR / "CANONICAL_SOCIAL_VISUAL_METADATA.json"

DURATION_TOLERANCE_S = 0.2


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _probe_video(path: Path) -> dict | None:
    """Best-effort ffprobe dims/duration; returns None if ffprobe unavailable."""
    import shutil
    import subprocess

    ffprobe = shutil.which("ffprobe") or "/opt/homebrew/bin/ffprobe"
    if not Path(ffprobe).exists():
        return None
    try:
        out = subprocess.run(
            [
                ffprobe, "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=width,height,duration",
                "-of", "json", str(path),
            ],
            capture_output=True, text=True, timeout=30, check=True,
        )
        data = json.loads(out.stdout)
        stream = (data.get("streams") or [{}])[0]
        return {
            "width": int(stream.get("width", 0)),
            "height": int(stream.get("height", 0)),
            "duration": float(stream.get("duration", 0.0)),
        }
    except Exception:  # noqa: BLE001 -- best-effort probe, never block on this
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Social visual golden parity gate (dormant until frozen)")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not METADATA_PATH.exists():
        print("SKIP: no CANONICAL_SOCIAL_VISUAL golden frozen yet — dormant gate, nothing to defend.")
        print(f"  metadata expected at: {METADATA_PATH}")
        print("  freeze after operator approval via scripts/social/freeze_social_visual_golden.py")
        return 0

    try:
        meta = json.loads(METADATA_PATH.read_text())
    except json.JSONDecodeError as e:
        print(f"FAIL: metadata unparseable: {e}", file=sys.stderr)
        return 2

    assets = meta.get("assets", [])
    if not assets:
        print("FAIL: metadata present but has no assets[] -- frozen golden is empty", file=sys.stderr)
        return 2

    overall_pass = True
    for asset in assets:
        rel_path = asset.get("path")
        expected_sha = asset.get("sha256")
        asset_path = REPO_ROOT / rel_path
        label = asset.get("example_id", rel_path)

        if not asset_path.exists():
            print(f"FAIL [{label}]: missing at {rel_path}", file=sys.stderr)
            overall_pass = False
            continue

        actual_sha = _sha256(asset_path)
        if actual_sha != expected_sha:
            print(f"FAIL [{label}]: sha256 drift — expected {expected_sha[:12]}… got {actual_sha[:12]}…", file=sys.stderr)
            overall_pass = False
            continue

        if asset.get("kind") == "video":
            probe = _probe_video(asset_path)
            if probe is not None:
                exp_w, exp_h = asset.get("width"), asset.get("height")
                exp_dur = asset.get("duration_s")
                if exp_w and probe["width"] != exp_w:
                    print(f"FAIL [{label}]: width drift — expected {exp_w} got {probe['width']}", file=sys.stderr)
                    overall_pass = False
                if exp_h and probe["height"] != exp_h:
                    print(f"FAIL [{label}]: height drift — expected {exp_h} got {probe['height']}", file=sys.stderr)
                    overall_pass = False
                if exp_dur and abs(probe["duration"] - exp_dur) > DURATION_TOLERANCE_S:
                    print(f"FAIL [{label}]: duration drift — expected {exp_dur}s got {probe['duration']}s", file=sys.stderr)
                    overall_pass = False

        if args.verbose and overall_pass:
            print(f"  PASS [{label}]: sha256={actual_sha[:12]}…")

    if overall_pass:
        print(f"PASS: CANONICAL_SOCIAL_VISUAL parity held for {len(assets)} asset(s).")
        print(f"  frozen at: {meta.get('frozen_at', 'unknown')}")
        print(f"  approved by: {meta.get('operator_approved_by', 'unknown')}")
        return 0

    print("\nRestore reference:", file=sys.stderr)
    print(f"  {METADATA_PATH}", file=sys.stderr)
    print("  artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
