#!/usr/bin/env python3
"""
Populate-only tool: freezes the operator-approved social visual set as the
CANONICAL_SOCIAL_VISUAL golden that scripts/ci/check_social_visual_parity.py
then defends forever (capture-once-defend-forever, mirroring the Pearl News
sidebar pattern).

DO NOT RUN THIS WITHOUT EXPLICIT OPERATOR APPROVAL of
artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md.
This script refuses to run without --confirm-operator-approved. Passing that
flag is an assertion by whoever runs it that the operator has actually looked
at and approved the packet -- this tool cannot verify that itself.

Usage:
  python3 scripts/social/freeze_social_visual_golden.py \\
    --approved-set pilot \\
    --confirm-operator-approved \\
    --approved-by "<operator name / handle>"

  --approved-set pilot   -> freezes the 3 pilot shortform MP4s (default)
  --approved-set all     -> also includes the 12 static + 3 carousel winners
  --dry-run              -> print what would be frozen without writing anything

After running, artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL/ contains the
byte-copied assets + CANONICAL_SOCIAL_VISUAL_METADATA.json, and the parity
gate flips from SKIP to PASS/FAIL (defending) on its next run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LANE05 = REPO_ROOT / "artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild"
LANE04 = REPO_ROOT / "artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane04_static_carousel_rebuild"
GOLDEN_DIR = REPO_ROOT / "artifacts/qa/snapshots/CANONICAL_SOCIAL_VISUAL"
METADATA_PATH = GOLDEN_DIR / "CANONICAL_SOCIAL_VISUAL_METADATA.json"

PILOT_MP4S = [
    "tt_anxiety_faceless",
    "tt_burnout_faceless",
    "yt_overthinking_faceless",
]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _probe_video(path: Path) -> dict:
    out = subprocess.run(
        [
            "/opt/homebrew/bin/ffprobe", "-v", "error", "-select_streams", "v:0",
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
        "duration_s": round(float(stream.get("duration", 0.0)), 3),
    }


def _collect_pilot_assets() -> list[dict]:
    assets = []
    for name in PILOT_MP4S:
        src = LANE05 / "shortform_mp4_rendered" / f"{name}.mp4"
        if not src.exists():
            print(f"WARN: expected pilot MP4 missing, skipping: {src}", file=sys.stderr)
            continue
        probe = _probe_video(src)
        assets.append({
            "example_id": name,
            "kind": "video",
            "source_path": str(src.relative_to(REPO_ROOT)),
            "path": str((GOLDEN_DIR / f"{name}.mp4").relative_to(REPO_ROOT)),
            "sha256": _sha256(src),
            "bytes": src.stat().st_size,
            **probe,
        })
    return assets


def _collect_static_carousel_assets() -> list[dict]:
    assets = []
    samples_dir = LANE04 / "static_carousel_render_samples"
    if not samples_dir.exists():
        return assets
    for img in sorted(samples_dir.rglob("*.jpg")):
        rel_id = str(img.relative_to(samples_dir))
        assets.append({
            "example_id": rel_id,
            "kind": "image",
            "source_path": str(img.relative_to(REPO_ROOT)),
            "path": str((GOLDEN_DIR / "static_carousel" / rel_id).relative_to(REPO_ROOT)),
            "sha256": _sha256(img),
            "bytes": img.stat().st_size,
        })
    return assets


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--approved-set", choices=["pilot", "all"], default="pilot")
    parser.add_argument("--confirm-operator-approved", action="store_true",
                        help="Required. Asserts the operator has approved LOOK_APPROVAL.md.")
    parser.add_argument("--approved-by", default="unspecified",
                        help="Operator name/handle who approved the look packet.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.confirm_operator_approved:
        print("REFUSED: this tool requires --confirm-operator-approved.", file=sys.stderr)
        print("Read artifacts/qa/social_visual_rebuild_publishable_quality_20260718/"
              "lane05_pearl_animator_rebuild/LOOK_APPROVAL.md and get the operator's actual "
              "sign-off before running this with that flag.", file=sys.stderr)
        return 2

    if METADATA_PATH.exists():
        print(f"REFUSED: golden already frozen at {METADATA_PATH}.", file=sys.stderr)
        print("This tool is populate-ONCE. To re-freeze after a new approved look, "
              "delete the existing golden deliberately with operator sign-off first.", file=sys.stderr)
        return 2

    assets = _collect_pilot_assets()
    if args.approved_set == "all":
        assets += _collect_static_carousel_assets()

    if not assets:
        print("REFUSED: no assets found to freeze.", file=sys.stderr)
        return 2

    print(f"About to freeze {len(assets)} asset(s) as CANONICAL_SOCIAL_VISUAL golden:")
    for a in assets:
        print(f"  - {a['example_id']} ({a['kind']}) <- {a['source_path']}")

    if args.dry_run:
        print("\n--dry-run: nothing written.")
        return 0

    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    for a in assets:
        dest = REPO_ROOT / a["path"]
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / a["source_path"], dest)

    metadata = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "operator_approved_by": args.approved_by,
        "approved_set": args.approved_set,
        "look_approval_packet": "artifacts/qa/social_visual_rebuild_publishable_quality_20260718/lane05_pearl_animator_rebuild/LOOK_APPROVAL.md",
        "pattern_mirrors": "scripts/ci/check_pearl_news_sidebar_parity.py",
        "assets": assets,
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2) + "\n")

    print(f"\nFROZEN: {METADATA_PATH}")
    print("The parity gate (scripts/ci/check_social_visual_parity.py) now defends this set.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
