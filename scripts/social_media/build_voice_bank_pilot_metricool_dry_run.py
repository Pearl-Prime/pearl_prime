#!/usr/bin/env python3
"""Metricool DRY-RUN payloads for voice-bank craft packs (never live-publishes).

Reads ok receipts from pilot_batch and/or matrix_batch.
Safety: draft=true, autoPublish=false, dryRun=true, media=UPLOAD_REQUIRED.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_DIRS = [
    REPO / "artifacts/social_media_voice_bank_2026-07-19/matrix_batch",
    REPO / "artifacts/social_media_voice_bank_2026-07-19/pilot_batch",
]

FIRST_COMMENT = {
    "anxiety": 'Comment "GROUND" for the checklist.',
    "burnout": 'Comment "RESET" for the checklist.',
    "overthinking": 'Comment "FACT" for the checklist.',
}


def topic_persona_from_receipt(receipt: dict, pack_id: str) -> tuple[str, str]:
    if receipt.get("topic") and receipt.get("persona"):
        return str(receipt["topic"]), str(receipt["persona"])
    if "__" in pack_id:
        topic, persona = pack_id.split("__", 1)
        return topic, persona
    # legacy pilot ids
    if pack_id.startswith("anxiety"):
        return "anxiety", "corporate_managers"
    if pack_id.startswith("burnout"):
        return "burnout", "corporate_managers"
    if pack_id.startswith("overthinking"):
        return "overthinking", "gen_z_professionals"
    parts = pack_id.split("_", 1)
    return parts[0], parts[1] if len(parts) > 1 else "unknown"


def build_one(receipt_path: Path, out_dir: Path, day_offset: int) -> Path | None:
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("status") == "VO_BLOCKED":
        return None
    pack_id = receipt["pack_id"]
    mp4 = receipt_path.parent / f"{pack_id}_short_9x16.mp4"
    if not mp4.is_file():
        rel = receipt.get("mp4") or ""
        cand = Path(rel)
        mp4 = cand if cand.is_absolute() else (REPO / rel)
    if not mp4.is_file():
        raise FileNotFoundError(mp4)
    try:
        local_media = str(mp4.resolve().relative_to(REPO.resolve()))
    except ValueError:
        local_media = str(mp4)
    topic, persona = topic_persona_from_receipt(receipt, pack_id)
    by_role = {b["role"]: b["speakable_text"] for b in receipt.get("beats") or []}
    caption = "\n\n".join(
        by_role[r] for r in ("hook", "practice", "payoff") if r in by_role
    )
    pub = datetime(2026, 7, 26, 9, 0, 0) + timedelta(days=day_offset)
    payload = {
        "providers": ["tiktok_reels_shorts"],
        "publicationDate": pub.strftime("%Y-%m-%dT09:00:00-04:00"),
        "timezone": "America/New_York",
        "text": caption,
        "firstCommentText": FIRST_COMMENT.get(
            topic, 'Comment "GROUND" for the checklist.'
        ),
        "media": ["UPLOAD_REQUIRED"],
        "mediaAltText": [
            f"Faceless vertical short on {topic} (broll + CosyVoice bank VO)"
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
        "localMediaPath": local_media,
        "pack_id": pack_id,
        "style": "broll_montage",
        "topic": topic,
        "persona": persona,
        "calendar_primary": True,
        "voice_bank": True,
        "atom_ids": [b["atom_id"] for b in receipt.get("beats") or []],
        "acceptance_layer": "system working — Metricool dry-run only (not live publish)",
        "brand_key": "waystream_sanctuary",
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    out_json = out_dir / f"{pack_id}__tiktok_dry_run.json"
    out_json.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out_json


def write_safety_report(out_dir: Path, payloads: list[Path]) -> Path:
    lines = [
        "# Publish safety report — voice-bank matrix Metricool dry-runs",
        "",
        "## Locked flags (all payloads)",
        "- `draft: true`",
        "- `autoPublish: false`",
        "- `dryRun: true`",
        "- `manualReviewRequired: true`",
        "- media: `UPLOAD_REQUIRED` (no live upload)",
        "",
        f"## Payloads ({len(payloads)})",
    ]
    for p in payloads:
        try:
            shown = p.resolve().relative_to(REPO.resolve())
        except ValueError:
            shown = p
        lines.append(f"- `{shown}`")
    lines.extend(
        [
            "",
            "## Not authorized",
            "- `autoPublish: true`",
            "- live Metricool API post",
            "",
            "Signal: `voice-bank-matrix-metricool-dry-run=PASS`",
            "",
        ]
    )
    report = out_dir / "publish_safety_report.md"
    report.write_text("\n".join(lines), encoding="utf-8")
    return report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--receipt-dirs",
        default="",
        help="comma dirs with *_RECEIPT.json (default: matrix_batch then pilot_batch)",
    )
    ap.add_argument(
        "--out-dir",
        type=Path,
        default=REPO
        / "artifacts/social_media_voice_bank_2026-07-19/matrix_batch/metricool_dry_run",
    )
    args = ap.parse_args()
    dirs = (
        [Path(p.strip()) for p in args.receipt_dirs.split(",") if p.strip()]
        if args.receipt_dirs.strip()
        else DEFAULT_DIRS
    )
    receipts: list[Path] = []
    seen: set[str] = set()
    for d in dirs:
        if not d.is_dir():
            continue
        for rp in sorted(d.glob("*_RECEIPT.json")):
            try:
                rec = json.loads(rp.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            if rec.get("status") == "VO_BLOCKED":
                continue
            if rec.get("status") not in (None, "ok") and "beats" not in rec:
                continue
            # pilot receipts omit status but have beats
            if "beats" not in rec:
                continue
            pid = rec.get("pack_id") or rp.stem.replace("_RECEIPT", "")
            if pid in seen:
                continue
            seen.add(pid)
            receipts.append(rp)
    if not receipts:
        print("no ok receipts found")
        return 1
    outs: list[Path] = []
    for i, rp in enumerate(receipts):
        out = build_one(rp, args.out_dir, day_offset=i)
        if out is None:
            continue
        print(f"OK dry-run → {out}", flush=True)
        outs.append(out)
    report = write_safety_report(args.out_dir, outs)
    print(f"OK safety → {report} count={len(outs)}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
