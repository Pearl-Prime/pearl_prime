#!/usr/bin/env python3
"""Metricool DRY-RUN payload for voice-bank craft pilot (never live-publishes).

Mirrors scripts/social/build_variant_metricool_dry_run.py safety flags:
draft=true, autoPublish=false, dryRun=true, media=UPLOAD_REQUIRED.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PILOT_DIR = REPO / "artifacts/social_media_voice_bank_2026-07-19/pilot_batch"
OUT = PILOT_DIR / "metricool_dry_run"


def main() -> int:
    receipt_path = PILOT_DIR / "anxiety_corporate_RECEIPT.json"
    mp4 = PILOT_DIR / "anxiety_corporate_short_9x16.mp4"
    if not receipt_path.is_file() or not mp4.is_file():
        print(f"missing pilot artifacts under {PILOT_DIR}")
        return 1
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    by_role = {b["role"]: b["speakable_text"] for b in receipt["beats"]}
    caption = "\n\n".join(
        by_role[r] for r in ("hook", "practice", "payoff") if r in by_role
    )
    payload = {
        "providers": ["tiktok_reels_shorts"],
        "publicationDate": "2026-07-26T09:00:00-04:00",
        "timezone": "America/New_York",
        "text": caption,
        "firstCommentText": 'Comment "GROUND" for the checklist.',
        "media": ["UPLOAD_REQUIRED"],
        "mediaAltText": [
            "Faceless vertical short on anxiety (broll + CosyVoice bank VO)"
        ],
        "videoCoverMilliseconds": 0,
        "autoPublish": False,
        "draft": True,
        "manualReviewRequired": True,
        "dryRun": True,
        "platformData": {
            "tiktok_reels_shortsData": {
                "surface": "tiktok_reels_shorts_vertical",
                "mediaKind": "video",
                "uploadMode": "UPLOAD_REQUIRED",
                "autoPublishAllowed": False,
                "livePublishingAuthorized": False,
            }
        },
        "localMediaPath": str(mp4.relative_to(REPO)),
        "pack_id": receipt["pack_id"],
        "style": "broll_montage",
        "topic": "anxiety",
        "persona": "corporate_managers",
        "calendar_primary": True,
        "voice_bank": True,
        "atom_ids": [b["atom_id"] for b in receipt["beats"]],
        "acceptance_layer": "system working — Metricool dry-run only (not live publish)",
        "brand_key": "waystream_sanctuary",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    out_json = OUT / "anxiety_corporate__tiktok_dry_run.json"
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    report = OUT / "publish_safety_report.md"
    report.write_text(
        "\n".join(
            [
                "# Publish safety report — voice-bank anxiety corporate pilot",
                "",
                "## Locked flags",
                "- `draft: true`",
                "- `autoPublish: false`",
                "- `dryRun: true`",
                "- `manualReviewRequired: true`",
                "- media: `UPLOAD_REQUIRED` (no live upload)",
                "",
                f"- payload: `{out_json.relative_to(REPO)}`",
                f"- local MP4: `{mp4.relative_to(REPO)}`",
                "",
                "## Not authorized",
                "- `autoPublish: true`",
                "- live Metricool API post",
                "",
                "Signal: `voice-bank-pilot-metricool-dry-run=PASS`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"OK dry-run → {out_json}")
    print(f"OK safety → {report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
