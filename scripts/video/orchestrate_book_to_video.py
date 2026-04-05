#!/usr/bin/env python3
"""
Video Orchestrator: Book/Manga Plan → 5 Platform Videos → Upload.

Takes a book plan JSON and produces platform-specific videos for:
  YouTube (10 min, 16:9), YouTube Shorts (60s, 9:16), TikTok (30-60s, 9:16),
  Instagram Reels (60s, 9:16), LINE (60-90s, 9:16).

Each video gets: brand-specific animation, ElevenLabs voice, freebie CTA, platform metadata.

Usage:
    # Produce all 5 formats (no upload)
    python scripts/video/orchestrate_book_to_video.py \\
        --plan artifacts/plan.json --brand-id stabilizer --channel-id ch_001

    # Produce + upload (dry-run by default)
    python scripts/video/orchestrate_book_to_video.py \\
        --plan artifacts/plan.json --brand-id stabilizer --channel-id ch_001 \\
        --upload

    # Produce + live upload
    python scripts/video/orchestrate_book_to_video.py \\
        --plan artifacts/plan.json --brand-id stabilizer --channel-id ch_001 \\
        --upload --no-dry-run
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:
    print("pyyaml required: pip install pyyaml")
    sys.exit(1)


def _load_yaml(p: Path) -> dict:
    if not p.exists():
        return {}
    return yaml.safe_load(p.read_text(encoding="utf-8")) or {}


# ── Platform → format mapping ────────────────────────────────────
PLATFORM_FORMAT_MAP = {
    "youtube": "mid",              # 16:9 cinematic, 2-10 min
    "youtube_shorts": "short",     # 9:16 portrait, 15-60s
    "tiktok": "short",             # 9:16 portrait, 30-60s
    "instagram": "short",          # 9:16 portrait, 30-60s
    "line": "short",               # 9:16 portrait, 60-90s
}

ALL_PLATFORMS = ["youtube", "youtube_shorts", "tiktok", "instagram", "line"]


def _resolve_freebie(plan: dict) -> dict:
    """Extract freebie info from plan JSON (already resolved by run_pipeline.py)."""
    freebie_bundle = plan.get("freebie_bundle") or []
    freebie_slug = plan.get("freebie_slug") or ""
    cta_template_id = plan.get("cta_template_id") or "workbook_forward"

    # Determine workbook label
    workbook_type = plan.get("companion_workbook_type") or "none"
    if workbook_type == "full":
        workbook_label = "workbook"
    elif workbook_type == "light_guide":
        workbook_label = "practice guide"
    elif freebie_bundle:
        workbook_label = "free guide"
    else:
        workbook_label = "free resource"

    return {
        "freebie_bundle": freebie_bundle,
        "freebie_slug": freebie_slug,
        "cta_template_id": cta_template_id,
        "workbook_label": workbook_label,
        "url": f"brand-admin-onboarding.pages.dev/free/{freebie_slug}" if freebie_slug else "",
    }


def _resolve_cta_text(cta_templates: dict, platform: str, freebie: dict, plan: dict) -> dict:
    """Resolve CTA text for a platform by substituting variables."""
    platform_ctas = cta_templates.get(platform) or {}
    brand_id = plan.get("brand_id") or plan.get("teacher_id") or "unknown"
    topic_id = plan.get("topic_id") or (plan.get("book_spec") or {}).get("topic_id") or ""
    topic_display = topic_id.replace("_", " ") if topic_id else "wellness"

    resolved = {}
    for cta_key, cta_spec in platform_ctas.items():
        if not isinstance(cta_spec, dict):
            continue
        template = cta_spec.get("template") or cta_spec.get("template_en") or ""
        text = template.replace("{workbook_label}", freebie["workbook_label"])
        text = text.replace("{slug}", freebie["freebie_slug"])
        text = text.replace("{brand_id}", brand_id)
        text = text.replace("{topic_display}", topic_display)
        text = text.replace("{url}", freebie["url"])
        resolved[cta_key] = {**cta_spec, "resolved_text": text}
    return resolved


def _extract_segments_from_plan(plan: dict, max_segments: int = 10) -> list[dict]:
    """Extract narration segments from plan for video script."""
    chapters = plan.get("chapter_slot_sequence") or []
    atom_ids = plan.get("atom_ids") or []
    topic_id = plan.get("topic_id") or ""
    topic_display = topic_id.replace("_", " ").title() if topic_id else "Wellness"

    segments = []
    idx = 0
    for ch_idx, slots in enumerate(chapters):
        if len(segments) >= max_segments:
            break
        for slot_type in slots:
            if idx >= len(atom_ids):
                break
            aid = atom_ids[idx]
            idx += 1
            # Use STORY, REFLECTION, INTEGRATION atoms as narration sources
            if slot_type in ("STORY", "REFLECTION", "INTEGRATION") and "placeholder" not in aid:
                segments.append({
                    "segment_id": f"seg_{len(segments):03d}",
                    "chapter": ch_idx + 1,
                    "slot_type": slot_type,
                    "atom_id": aid,
                    "text": f"Chapter {ch_idx + 1}: {topic_display} — {slot_type.lower()}",
                    "duration_s": 60 if slot_type == "STORY" else 30,
                })
    return segments[:max_segments]


def _write_render_manifest(segments: list[dict], output_path: Path) -> Path:
    """Write segments as render_manifest.json for the video pipeline."""
    manifest = {
        "schema_version": "1.0",
        "segments": segments,
    }
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


def produce_video(
    plan: dict,
    platform: str,
    channel_id: str,
    output_dir: Path,
    assets_dir: Optional[Path] = None,
    voice: bool = True,
    freebie_cta: bool = True,
    cta_config: Optional[dict] = None,
) -> dict:
    """Produce a single platform-format video from a book plan."""
    fmt = PLATFORM_FORMAT_MAP.get(platform, "short")
    plan_id = plan.get("plan_id") or plan.get("plan_hash") or "video"
    video_plan_id = f"{plan_id}-{platform}"

    video_dir = output_dir / platform
    video_dir.mkdir(parents=True, exist_ok=True)

    # Write render manifest
    max_segs = 10 if fmt == "mid" else 3  # long = more segments
    segments = _extract_segments_from_plan(plan, max_segments=max_segs)
    manifest_path = _write_render_manifest(segments, video_dir / "render_manifest.json")

    # Write CTA config for renderer
    if freebie_cta and cta_config:
        cta_path = video_dir / "cta_config.json"
        cta_path.write_text(json.dumps(cta_config, indent=2), encoding="utf-8")

    # Run video pipeline
    cmd = [
        sys.executable, str(REPO_ROOT / "scripts" / "video" / "run_pipeline.py"),
        "--plan-id", video_plan_id,
        "--format", fmt,
        "--channel-id", channel_id,
        "--render-manifest", str(manifest_path),
    ]
    if voice:
        cmd.append("--voice")
    if assets_dir and assets_dir.exists():
        cmd.extend(["--assets-dir", str(assets_dir)])
        cmd.append("--no-skip-render")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300, cwd=str(REPO_ROOT))

    video_file = None
    rendered_dir = REPO_ROOT / "artifacts" / "video" / video_plan_id / "rendered"
    if rendered_dir.exists():
        mp4s = list(rendered_dir.glob("*.mp4"))
        if mp4s:
            video_file = mp4s[0]

    return {
        "platform": platform,
        "format": fmt,
        "plan_id": video_plan_id,
        "video_file": str(video_file) if video_file else None,
        "success": result.returncode == 0,
        "error": result.stderr[-500:] if result.returncode != 0 else None,
    }


def upload_video(
    video_result: dict,
    channel_id: str,
    brand_id: str,
    cta_metadata: dict,
    dry_run: bool = True,
) -> dict:
    """Upload a produced video to its platform."""
    if not video_result.get("video_file"):
        return {"platform": video_result["platform"], "success": False, "error": "No video file"}

    platform = video_result["platform"]
    video_path = video_result["video_file"]

    # Build platform_variants.json for run_upload.py
    variants = {
        "video_id": video_result["plan_id"],
        "plan_id": video_result["plan_id"],
        "variants": [{
            "platform": platform,
            "title": cta_metadata.get("title", f"Wellness — {brand_id}"),
            "description": cta_metadata.get("description", ""),
            "tags": cta_metadata.get("tags", []),
        }],
    }
    variants_path = Path(video_path).parent / "platform_variants.json"
    variants_path.write_text(json.dumps(variants, indent=2), encoding="utf-8")

    cmd = [
        sys.executable, str(REPO_ROOT / "scripts" / "video" / "run_upload.py"),
        str(variants_path),
        "--channel-id", channel_id,
        "--video-dir", str(Path(video_path).parent),
    ]
    if not dry_run:
        cmd.append("--no-dry-run")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120, cwd=str(REPO_ROOT))

    return {
        "platform": platform,
        "success": result.returncode == 0,
        "dry_run": dry_run,
        "output": result.stdout[-300:] if result.returncode == 0 else None,
        "error": result.stderr[-300:] if result.returncode != 0 else None,
    }


def orchestrate(
    plan_path: Path,
    brand_id: str,
    channel_id: str,
    output_dir: Path,
    platforms: Optional[list[str]] = None,
    assets_dir: Optional[Path] = None,
    voice: bool = True,
    upload: bool = False,
    dry_run: bool = True,
) -> dict:
    """
    Full orchestration: book plan → 5 platform videos → optional upload.

    Returns manifest dict with results per platform.
    """
    platforms = platforms or ALL_PLATFORMS
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    plan["brand_id"] = brand_id

    # Resolve freebie
    freebie = _resolve_freebie(plan)

    # Load CTA templates
    cta_templates = _load_yaml(REPO_ROOT / "config" / "video" / "video_cta_templates.yaml")

    output_dir.mkdir(parents=True, exist_ok=True)
    results = {"plan_path": str(plan_path), "brand_id": brand_id, "freebie": freebie, "videos": {}}

    for platform in platforms:
        print(f"  [{platform}] Producing video...")
        cta_config = _resolve_cta_text(cta_templates, platform, freebie, plan)

        video_result = produce_video(
            plan, platform, channel_id, output_dir,
            assets_dir=assets_dir, voice=voice,
            freebie_cta=bool(freebie["freebie_slug"]),
            cta_config=cta_config,
        )
        results["videos"][platform] = video_result

        if video_result["success"]:
            print(f"  [{platform}] ✅ Video: {video_result.get('video_file', 'N/A')}")
        else:
            print(f"  [{platform}] ❌ Failed: {video_result.get('error', 'unknown')[:100]}")

        # Upload if requested
        if upload and video_result["success"]:
            print(f"  [{platform}] Uploading ({'dry-run' if dry_run else 'LIVE'})...")
            upload_result = upload_video(
                video_result, channel_id, brand_id,
                cta_metadata={"title": f"Wellness — {brand_id}", "tags": ["wellness", "selfhelp"]},
                dry_run=dry_run,
            )
            results["videos"][platform]["upload"] = upload_result

    # Write manifest
    manifest_path = output_dir / "video_manifest.json"
    manifest_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nManifest: {manifest_path}")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Orchestrate book plan → 5 platform videos → upload")
    parser.add_argument("--plan", required=True, help="Path to book plan JSON")
    parser.add_argument("--brand-id", required=True, help="Brand ID (e.g., stabilizer)")
    parser.add_argument("--channel-id", required=True, help="Channel ID (e.g., ch_001)")
    parser.add_argument("--output-dir", default="artifacts/video/orchestrated", help="Output directory")
    parser.add_argument("--platforms", default=",".join(ALL_PLATFORMS), help="Comma-separated platforms")
    parser.add_argument("--assets-dir", help="Image bank directory for rendering")
    parser.add_argument("--no-voice", action="store_true", help="Skip ElevenLabs voice synthesis")
    parser.add_argument("--upload", action="store_true", help="Upload after production")
    parser.add_argument("--no-dry-run", action="store_true", help="Live upload (not dry-run)")
    args = parser.parse_args()

    platforms = [p.strip() for p in args.platforms.split(",")]
    output_dir = Path(args.output_dir)
    assets_dir = Path(args.assets_dir) if args.assets_dir else None

    print(f"Orchestrating: {args.plan} → {len(platforms)} platforms")
    print(f"Brand: {args.brand_id} | Channel: {args.channel_id}")

    result = orchestrate(
        plan_path=Path(args.plan),
        brand_id=args.brand_id,
        channel_id=args.channel_id,
        output_dir=output_dir,
        platforms=platforms,
        assets_dir=assets_dir,
        voice=not args.no_voice,
        upload=args.upload,
        dry_run=not args.no_dry_run,
    )

    successes = sum(1 for v in result["videos"].values() if v.get("success"))
    print(f"\nResults: {successes}/{len(platforms)} videos produced")
    return 0 if successes == len(platforms) else 1


if __name__ == "__main__":
    sys.exit(main())
