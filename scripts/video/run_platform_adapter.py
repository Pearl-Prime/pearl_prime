#!/usr/bin/env python3
"""
Stage 15 — Platform Adapter: timeline + distribution_manifest + animation_plan -> platform_variants.json.
VCE §8: per-platform encode, thumbnails, metadata templates, compliance refs.
Usage: python scripts/video/run_platform_adapter.py <timeline.json> <distribution_manifest.json> <animation_plan.json> -o platform_variants.json [--platforms youtube,tiktok]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import config_snapshot_hash, load_json, load_yaml, should_skip_output, write_atomically
from scripts.video.vce_ffmpeg_builders import (
    caption_policy_for_platform,
    platform_duration_cap_argv,
    platform_video_audio_argv,
    quality_tuning,
    webp_panel_argv_template,
)

PLATFORM_ALIASES = {
    "youtube": "youtube",
    "youtube_shorts": "youtube_shorts",
    "tiktok": "tiktok",
    "instagram": "instagram_reels",
    "instagram_reels": "instagram_reels",
    "bilibili": "bilibili",
    "douyin": "douyin",
    "webtoon": "webtoon",
}


def _title_from_template(template_key: str, fields: dict, registry: dict) -> str:
    templates = registry.get("title_templates") or {}
    spec = templates.get(template_key) if isinstance(templates.get(template_key), dict) else None
    if not spec:
        for _k, v in templates.items():
            if isinstance(v, dict) and v.get("format"):
                spec = v
                break
    fmt = (spec or {}).get("format", "{topic}")
    defaults = {k: fields.get(k, "") for k in [
        "action", "struggle", "topic", "question", "number", "outcome",
        "persona_descriptor", "action_verb", "benefit",
    ]}
    try:
        return fmt.format(**defaults)
    except Exception:
        return fields.get("title", "Video title")


def run_platform_adapter(
    timeline: dict,
    dist: dict,
    animation_plan: dict,
    platform_keys: list[str],
) -> dict:
    compliance = load_yaml("config/video/platform_compliance.yaml")
    plat_specs = compliance.get("platforms") or {}
    thumb_specs = compliance.get("thumbnail_specs") or {}
    registry = load_yaml("config/video/channel_registry.yaml")
    brand = load_yaml("config/video/brand_style_tokens.yaml")
    caption_pol = load_yaml("config/video/caption_policies.yaml")

    video_id = dist.get("video_id", "video-unknown")
    plan_id = dist.get("plan_id") or timeline.get("plan_id")
    title = dist.get("title", "Untitled")
    description = dist.get("description", "")
    tags = dist.get("tags") or []

    hook_palette = ((brand.get("bands") or {}).get("hook") or (brand.get("palettes") or {}))
    _ = caption_pol

    variants = []
    for raw in platform_keys:
        key = PLATFORM_ALIASES.get(raw.strip().lower(), raw.strip().lower())
        pdef = plat_specs.get(key, {})
        enc = pdef.get("resolution") or timeline.get("resolution") or {"width": 1920, "height": 1080}
        thumb = thumb_specs.get(key.replace("youtube_shorts", "youtube").replace("instagram_reels", "tiktok"), {})

        ch_id = dist.get("channel_id", "ch_001")
        ch = (registry.get("channels") or {}).get(ch_id, {})
        tmpl_id = ch.get("title_template_id", "tmpl_heal")
        auto_title = _title_from_template(
            tmpl_id,
            {
                "title": title,
                "topic": title,
                "action": "breathe",
                "struggle": "stress",
                "question": "feel overwhelmed",
                "number": "3",
                "outcome": "calm",
                "persona_descriptor": "busy mind",
                "action_verb": "Calm",
                "benefit": "more ease",
            },
            registry,
        )

        meta = {
            "title": auto_title[:100] if key == "youtube" else auto_title[:150],
            "description": description,
            "tags": tags[:15] if key == "youtube" else tags[:5],
            "hashtags": tags[:5] if key in ("tiktok", "douyin", "instagram_reels") else [],
        }
        if key == "bilibili":
            meta["locale"] = "zh-CN"
        compliance_rules = pdef.get("compliance_rules") or {}
        base_crf = int(pdef.get("crf", 23))
        _, qual_preset = quality_tuning("standard")
        vid_argv, aud_argv = platform_video_audio_argv(key, base_crf, qual_preset)
        dur_cap = platform_duration_cap_argv(key)
        webp_tmpl = webp_panel_argv_template() if key == "webtoon" else None
        cap_del = caption_policy_for_platform(key)

        variants.append({
            "platform": key,
            "encode": {
                "width": enc.get("width"),
                "height": enc.get("height"),
                "codec": pdef.get("video_codec", "h264_high"),
                "crf": base_crf,
                "container": pdef.get("container", "mp4"),
                "caption_types": pdef.get("caption_types", []),
            },
            "ffmpeg": {
                "video_encode_argv": vid_argv,
                "audio_encode_argv": aud_argv,
                "duration_cap_argv": dur_cap,
                "encode_argv_tail": vid_argv + aud_argv + dur_cap,
                "webp_panel_argv_template": webp_tmpl,
            },
            "caption_delivery": cap_del,
            "thumbnail_spec": {
                "dimensions": [thumb.get("width", 1280), thumb.get("height", 720)],
                "hook_band_palette_ref": hook_palette,
                "variants": thumb.get("variants", 1),
            },
            "metadata": meta,
            "compliance": compliance_rules or {"notes": pdef.get("compliance_notes", [])},
            "animation_ref": {"shot_count": len(animation_plan.get("shots") or [])},
        })

    return {
        "plan_id": plan_id,
        "video_id": video_id,
        "config_hash": config_snapshot_hash(),
        "variants": variants,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="VCE Stage 15 — Platform adapter")
    ap.add_argument("timeline")
    ap.add_argument("distribution_manifest", help="May be a stub path if not yet written; use placeholder file for early runs")
    ap.add_argument("animation_plan")
    ap.add_argument("-o", "--out", required=True)
    ap.add_argument("--platforms", default="youtube,tiktok", help="Comma-separated platform keys")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--workspace", type=str, default=None, help="Directory containing job.json (default: parent of --out)")
    ap.add_argument("--no-job-check", dest="no_job_check", action="store_true", help="Skip job.json enforcement (CI only)")
    args = ap.parse_args()
    if args.no_job_check:
        print("WARNING: --no-job-check: pipeline job enforcement disabled (CI/testing only).", file=sys.stderr)
    from scripts.pipeline._video_workspace import resolve_video_workspace
    from scripts.pipeline.advance_stage import mark_complete, mark_failed
    from scripts.pipeline.check_job import require_stage

    ws = resolve_video_workspace(args, out_attr="out")
    if not args.no_job_check:
        require_stage("platform_adapt", ws)

    t_path, d_path, a_path = Path(args.timeline), Path(args.distribution_manifest), Path(args.animation_plan)
    if not t_path.exists() or not a_path.exists():
        if not args.no_job_check:
            mark_failed(ws, "platform_adapt", error="timeline or animation_plan not found")
        print("Error: timeline or animation_plan not found", file=sys.stderr)
        return 1

    timeline = load_json(t_path)
    animation_plan = load_json(a_path)
    if d_path.exists():
        dist = load_json(d_path)
    else:
        dist = {
            "video_id": f"video-{timeline.get('plan_id', 'unknown')}",
            "plan_id": timeline.get("plan_id"),
            "title": "Placeholder title",
            "description": "",
            "tags": [],
        }

    platforms = [p.strip() for p in args.platforms.split(",") if p.strip()]
    out = Path(args.out)
    h = config_snapshot_hash()
    if should_skip_output(out, ["plan_id", "variants", "config_hash"], args.force, h):
        print(f"Skip (exists): {out}")
        if not args.no_job_check:
            mark_complete(ws, "platform_adapt", output=out.name)
        return 0
    doc = run_platform_adapter(timeline, dist, animation_plan, platforms)
    write_atomically(out, doc)
    print(f"Wrote {len(doc['variants'])} platform variants to {out}")
    if not args.no_job_check:
        mark_complete(ws, "platform_adapt", output=out.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
