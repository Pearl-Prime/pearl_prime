#!/usr/bin/env python3
"""
Stage 18 — Upload/Publish: platform_variants.json + rendered video → upload to target platforms.

VCE §Stage-18: Takes the output of Stage 15 (Platform Adapter) + rendered video files
and uploads them to the configured video platforms per channel/brand.

Usage:
  # Dry run (default — logs what would upload, no API calls):
  python scripts/video/run_upload.py <platform_variants.json> --channel-id ch_001

  # Live upload for a single channel:
  python scripts/video/run_upload.py <platform_variants.json> --channel-id ch_001 --no-dry-run --video-dir artifacts/video/plan-therapeutic-001/rendered/

  # Batch upload for all channels in a batch:
  python scripts/video/run_upload.py <platform_variants.json> --batch --video-dir artifacts/video/plan-therapeutic-001/rendered/

  # Specific platforms only:
  python scripts/video/run_upload.py <platform_variants.json> --channel-id ch_001 --platforms youtube,tiktok
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.video._config import config_snapshot_hash, load_json, load_yaml, write_atomically
from scripts.video.uploaders import UPLOADERS, UploadResult

logger = logging.getLogger(__name__)


def load_channel_registry() -> dict:
    """Load channel_registry.yaml and return channels dict keyed by channel_id."""
    reg = load_yaml("channel_registry.yaml")
    return reg.get("channels", {})


def load_upload_config() -> dict:
    """Load upload_config.yaml."""
    return load_yaml("upload_config.yaml")


def resolve_video_path(video_dir: Path, channel_id: str, platform: str) -> Path | None:
    """Find the rendered video file for a channel+platform combination.

    Convention: {video_dir}/{channel_id}_{platform}.mp4
    Fallback:   {video_dir}/{channel_id}.mp4 (single render for all platforms)
    """
    specific = video_dir / f"{channel_id}_{platform}.mp4"
    if specific.exists():
        return specific
    generic = video_dir / f"{channel_id}.mp4"
    if generic.exists():
        return generic
    # Try any mp4 in the directory
    mp4s = sorted(video_dir.glob("*.mp4"))
    if mp4s:
        return mp4s[0]
    return None


def get_brand_for_channel(channel_id: str, channels: dict) -> str:
    """Get brand_id for a channel from the registry."""
    ch = channels.get(channel_id, {})
    return ch.get("brand_id", "unknown")


def get_platforms_for_channel(
    channel_id: str,
    channels: dict,
    upload_config: dict,
    platform_filter: list[str] | None = None,
) -> list[str]:
    """Determine which platforms a channel should upload to.

    Uses brand_platform_map from upload_config to check enabled platforms per brand.
    If platform_filter is provided, intersect with enabled platforms.
    """
    brand_id = get_brand_for_channel(channel_id, channels)
    brand_map = upload_config.get("brand_platform_map", {}).get(brand_id, {})

    enabled = []
    for platform_key, is_enabled in brand_map.items():
        if isinstance(is_enabled, bool) and is_enabled:
            platform_cfg = upload_config.get("platforms", {}).get(platform_key, {})
            if platform_cfg.get("enabled", False) or platform_cfg.get("inherits"):
                enabled.append(platform_key)

    if platform_filter:
        enabled = [p for p in enabled if p in platform_filter]

    return enabled


def upload_single(
    variant: dict,
    video_path: Path,
    channel_id: str,
    video_id: str,
    brand_id: str,
    upload_config: dict,
    dry_run: bool,
) -> UploadResult:
    """Upload a single video to a single platform."""
    platform = variant.get("platform", "")
    platform_cfg = upload_config.get("platforms", {}).get(platform, {})

    # Handle inheritance (e.g., youtube_shorts inherits from youtube)
    if platform_cfg.get("inherits"):
        parent_key = platform_cfg["inherits"]
        parent_cfg = upload_config.get("platforms", {}).get(parent_key, {})
        merged = {**parent_cfg, **{k: v for k, v in platform_cfg.items() if k != "inherits"}}
        platform_cfg = merged

    if not platform_cfg:
        return UploadResult(
            platform=platform, channel_id=channel_id, brand_id=brand_id,
            video_id=video_id, success=False, error=f"no_config_for_platform_{platform}",
        )

    uploader_cls = UPLOADERS.get(platform)
    if not uploader_cls:
        return UploadResult(
            platform=platform, channel_id=channel_id, brand_id=brand_id,
            video_id=video_id, success=False, error=f"no_uploader_for_platform_{platform}",
        )

    # Determine credential suffix from brand map
    brand_map = upload_config.get("brand_platform_map", {}).get(brand_id, {})
    credential_suffix = brand_map.get("credential_suffix", "")

    scheduling = upload_config.get("scheduling", {})
    max_retries = scheduling.get("retry_max", 3)
    backoff = scheduling.get("retry_backoff_base_s", 60)

    uploader = uploader_cls(
        platform_config=platform_cfg,
        brand_id=brand_id,
        credential_suffix=credential_suffix,
        dry_run=dry_run,
    )

    # Handle Shorts mode for YouTube
    if platform == "youtube_shorts" and hasattr(uploader, "set_shorts_mode"):
        uploader.set_shorts_mode(True)

    return uploader.upload(
        video_path=video_path,
        channel_id=channel_id,
        video_id=video_id,
        variant=variant,
        max_retries=max_retries,
        backoff_base_s=backoff,
    )


def run_upload(
    variants_path: Path,
    channel_id: str | None,
    video_dir: Path,
    platforms_filter: list[str] | None,
    batch_mode: bool,
    dry_run: bool,
    output_path: Path | None,
) -> list[dict]:
    """Orchestrate uploads for one or more channels."""
    variants_data = load_json(variants_path)
    channels = load_channel_registry()
    upload_config = load_upload_config()
    config_hash = config_snapshot_hash()

    # Extract variants list
    if isinstance(variants_data, dict):
        variants_list = variants_data.get("variants", [])
        video_id = variants_data.get("video_id", "unknown")
    elif isinstance(variants_data, list):
        variants_list = variants_data
        video_id = "unknown"
    else:
        logger.error("Invalid platform_variants.json format")
        return []

    if not variants_list:
        logger.error("No platform variants found in %s", variants_path)
        return []

    # Determine which channels to process
    if batch_mode:
        channel_ids = list(channels.keys())
    elif channel_id:
        channel_ids = [channel_id]
    else:
        logger.error("Must specify --channel-id or --batch")
        return []

    results: list[dict] = []

    for ch_id in channel_ids:
        if ch_id not in channels:
            logger.warning("Channel %s not in registry, skipping", ch_id)
            continue

        brand_id = get_brand_for_channel(ch_id, channels)
        target_platforms = get_platforms_for_channel(ch_id, channels, upload_config, platforms_filter)

        if not target_platforms:
            logger.info("No enabled platforms for channel %s (brand=%s)", ch_id, brand_id)
            continue

        for platform_key in target_platforms:
            # Find matching variant
            variant = None
            for v in variants_list:
                if v.get("platform") == platform_key:
                    variant = v
                    break
            # Fallback: youtube_shorts uses youtube variant
            if not variant and platform_key == "youtube_shorts":
                for v in variants_list:
                    if v.get("platform") == "youtube":
                        variant = v
                        break

            if not variant:
                logger.warning("No variant for platform %s in variants file", platform_key)
                continue

            video_path = resolve_video_path(video_dir, ch_id, platform_key)
            if not video_path and not dry_run:
                logger.warning("No video file found for %s/%s in %s", ch_id, platform_key, video_dir)
                results.append(UploadResult(
                    platform=platform_key, channel_id=ch_id, brand_id=brand_id,
                    video_id=video_id, success=False, error="video_file_not_found",
                ).to_dict())
                continue

            # In dry-run, use a placeholder path
            if not video_path:
                video_path = video_dir / f"{ch_id}_{platform_key}.mp4"

            result = upload_single(
                variant=variant,
                video_path=video_path,
                channel_id=ch_id,
                video_id=video_id,
                brand_id=brand_id,
                upload_config=upload_config,
                dry_run=dry_run,
            )
            results.append(result.to_dict())
            logger.info(
                "%s %s → %s: %s%s",
                "DRY" if dry_run else "LIVE",
                ch_id,
                platform_key,
                "OK" if result.success else "FAIL",
                f" ({result.error})" if result.error else "",
            )

    # Write results
    output = {
        "upload_run_id": f"upload-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}",
        "config_hash": config_hash,
        "dry_run": dry_run,
        "channels_processed": len(channel_ids),
        "uploads_attempted": len(results),
        "uploads_succeeded": sum(1 for r in results if r.get("success")),
        "uploads_failed": sum(1 for r in results if not r.get("success")),
        "results": results,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    if output_path:
        write_atomically(output_path, output)
        logger.info("Upload results written to %s", output_path)
    else:
        print(json.dumps(output, indent=2))

    return results


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage 18 — Upload/Publish: upload rendered videos to target platforms.",
    )
    parser.add_argument("variants_json", type=Path, help="Path to platform_variants.json")
    parser.add_argument("--channel-id", type=str, help="Single channel to upload for")
    parser.add_argument("--batch", action="store_true", help="Upload for all channels in registry")
    parser.add_argument("--video-dir", type=Path, default=Path("artifacts/video/rendered"),
                        help="Directory containing rendered video files")
    parser.add_argument("--platforms", type=str, help="Comma-separated platform filter (e.g., youtube,tiktok)")
    parser.add_argument("--no-dry-run", action="store_true", help="Actually upload (default is dry-run)")
    parser.add_argument("-o", "--output", type=Path, help="Write results JSON to this path")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(name)s %(levelname)s %(message)s",
    )

    platforms_filter = args.platforms.split(",") if args.platforms else None
    dry_run = not args.no_dry_run

    if not args.channel_id and not args.batch:
        parser.error("Must specify --channel-id or --batch")

    results = run_upload(
        variants_path=args.variants_json,
        channel_id=args.channel_id,
        video_dir=args.video_dir,
        platforms_filter=platforms_filter,
        batch_mode=args.batch,
        dry_run=dry_run,
        output_path=args.output,
    )

    failed = sum(1 for r in results if not r.get("success"))
    if failed > 0 and not dry_run:
        logger.error("%d uploads failed", failed)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
