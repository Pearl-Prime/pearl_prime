#!/usr/bin/env python3
"""
CaptionAdapter: timeline + script_segments + caption_policies -> caption content per segment (reflow/truncate).
Outputs a captions JSON keyed by segment_id with adapted text and truncation_flag if > threshold.
Usage: python scripts/video/run_caption_adapter.py <timeline.json> <script_segments.json> -o <captions.json> [--format 16:9] [--lang en]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import load_yaml, config_snapshot_hash, write_atomically, should_skip_output, REPO_ROOT


def _last_complete_clause_boundary(text: str, max_chars: int) -> int:
    if len(text) <= max_chars:
        return len(text)
    chunk = text[: max_chars + 1]
    for sep in [". ", "! ", "? ", "; ", ", "]:
        idx = chunk.rfind(sep)
        if idx != -1:
            return idx + len(sep)
    idx = chunk.rfind(" ")
    return idx + 1 if idx != -1 else max_chars


def adapt_caption(text: str, max_chars_per_line: int, max_lines: int, strategy: str, flag_threshold_pct: float) -> tuple[str, bool]:
    max_total = max_chars_per_line * max_lines
    if len(text) <= max_total:
        return text, False
    if strategy == "truncate" or strategy == "reflow_then_truncate":
        cut = _last_complete_clause_boundary(text, max_total)
        out = text[:cut].rstrip()
        if cut < len(text) and out and not out.endswith((".", "!", "?")):
            out += "…"
        truncated_pct = (1 - len(out) / len(text)) * 100 if text else 0
        return out, truncated_pct > flag_threshold_pct
    return text[:max_total], len(text) > max_total


def run_caption_adapter(
    timeline: dict,
    script_segments: dict,
    fmt: str,
    lang: str,
    *,
    voice_bank: Path | None = None,
) -> dict:
    policies = load_yaml("config/video/caption_policies.yaml")
    default = policies.get("default") or {}
    by_lang = (policies.get("by_language") or {}).get(lang) or default
    max_chars = by_lang.get("max_chars_per_line", default.get("max_chars_per_line", 42))
    max_lines = by_lang.get("max_lines", default.get("max_lines", 2))
    strategy = default.get("strategy", "reflow")
    flag_pct = default.get("truncation_flag_threshold_pct", 50)

    bank_index = None
    if voice_bank is not None:
        from scripts.social_media.voice_bank_lookup import load_index

        bank_index = load_index(voice_bank, allow_r2_download=False)

    segment_text = {}
    caption_source = {}
    for s in script_segments.get("segments", []):
        seg_id = s["segment_id"]
        text = (s.get("speakable_text") or s.get("text") or "").strip()
        src = "speakable_text" if s.get("speakable_text") else "script"
        atom_id = (s.get("primary_atom_id") or "").strip()
        if bank_index is not None and atom_id and not atom_id.startswith("html-"):
            try:
                hit = bank_index.resolve(atom_id, require_audio=False)
                text = hit.speakable_text
                src = "voice_bank_speakable"
                s["speakable_text"] = hit.speakable_text
            except Exception as e:
                print(
                    f"WARNING: caption voice-bank miss for {atom_id}: {e} "
                    f"(keeping {src} text; do not assume audio match)",
                    file=sys.stderr,
                )
        segment_text[seg_id] = text
        caption_source[seg_id] = src

    captions = {}
    for clip in timeline.get("clips", []):
        seg_id = clip.get("caption_ref", "")
        text = segment_text.get(seg_id, "")
        adapted, flag = adapt_caption(text, max_chars, max_lines, strategy, flag_pct)
        captions[seg_id] = {
            "text": adapted,
            "truncation_flagged": flag,
            "source": caption_source.get(seg_id, "script"),
        }
    return {
        "plan_id": timeline.get("plan_id", ""),
        "config_hash": config_snapshot_hash(),
        "format": fmt,
        "language": lang,
        "voice_bank_manifest": str(voice_bank) if voice_bank else None,
        "captions": captions,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Adapt captions per format/language from caption_policies")
    ap.add_argument("timeline", help="Path to timeline.json")
    ap.add_argument("script_segments", help="Path to script_segments.json")
    ap.add_argument("-o", "--out", required=True, help="Output captions.json path")
    ap.add_argument("--format", default="16:9", help="Aspect format for policy")
    ap.add_argument("--lang", default="en", help="Language code")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists")
    ap.add_argument("--workspace", type=str, default=None, help="Directory containing job.json (default: parent of --out)")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    _default_bank = REPO_ROOT / "artifacts" / "social_media_voice_bank_2026-07-19" / "MANIFEST.tsv"
    ap.add_argument(
        "--voice-bank",
        nargs="?",
        const=str(_default_bank),
        default=None,
        help="Caption from voice-bank speakable_text (join on primary_atom_id)",
    )
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline._video_workspace import resolve_video_workspace
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = resolve_video_workspace(args, out_attr="out")
    if not args.no_job_check:
        require_stage("caption", ws)

    tl_path = Path(args.timeline)
    seg_path = Path(args.script_segments)
    if not tl_path.exists() or not seg_path.exists():
        if not args.no_job_check:
            mark_failed(ws, "caption", error="timeline or script_segments not found")
        print("Error: timeline or script_segments not found", file=sys.stderr)
        return 1
    timeline = json.loads(tl_path.read_text(encoding="utf-8"))
    script_segments = json.loads(seg_path.read_text(encoding="utf-8"))

    out_path = Path(args.out)
    if should_skip_output(out_path, ["plan_id", "captions", "config_hash"], args.force, config_snapshot_hash()):
        print(f"Skip (output exists, use --force to overwrite): {out_path}")
        if not args.no_job_check:
            mark_complete(ws, "caption", output=out_path.name)
        return 0
    vb = Path(args.voice_bank) if args.voice_bank else None
    result = run_caption_adapter(
        timeline, script_segments, args.format, args.lang, voice_bank=vb
    )
    write_atomically(out_path, result)
    print(f"Wrote captions for {len(result['captions'])} segments to {out_path}")
    if not args.no_job_check:
        mark_complete(ws, "caption", output=out_path.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
