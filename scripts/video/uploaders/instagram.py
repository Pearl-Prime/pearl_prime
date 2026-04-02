"""Instagram Reels uploader — Stage 18 platform integration for Instagram Graph API.

Auth: Meta OAuth2 long-lived access token + Instagram Business/Creator account user ID.
Upload: Container-based flow — create media container → poll until ready → publish.

The video must be hosted at a publicly accessible URL for Instagram to fetch.
In CI, we upload to a temporary storage (e.g., Cloudflare R2) first, then provide
the URL to Instagram's container creation endpoint.
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scripts.video.uploaders.base import BaseUploader, UploadResult

logger = logging.getLogger(__name__)

GRAPH_API_BASE = "https://graph.facebook.com/v18.0"


class InstagramReelsUploader(BaseUploader):
    PLATFORM = "instagram_reels"

    def __init__(self, platform_config: dict, brand_id: str, credential_suffix: str = "", dry_run: bool = True):
        super().__init__(platform_config, brand_id, credential_suffix, dry_run)
        self._access_token: str = ""
        self._ig_user_id: str = ""

    def authenticate(self) -> bool:
        """Load long-lived access token and IG user ID from environment."""
        self._access_token = self._env("IG_ACCESS_TOKEN")
        self._ig_user_id = self._env("IG_USER_ID")
        if not self._access_token or not self._ig_user_id:
            logger.error("Instagram: missing credentials for brand %s", self.brand_id)
            return False
        self._authenticated = True
        logger.info("Instagram: authenticated for brand %s (user_id=%s)", self.brand_id, self._ig_user_id)
        return True

    def _upload_video(self, video_path: Path, metadata: dict[str, Any]) -> UploadResult:
        """Upload Reel via Instagram container publish flow.

        Requires video_url in metadata — the video must be at a public URL.
        If not provided, returns error instructing caller to stage the file first.
        """
        video_url = metadata.get("video_url", "")
        if not video_url:
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error="video_url_required: Instagram requires a publicly accessible video URL. "
                      "Stage the file to Cloudflare R2 or similar first.",
            )

        caption_parts = []
        if metadata.get("title"):
            caption_parts.append(metadata["title"])
        if metadata.get("description") and metadata["description"] != metadata.get("title"):
            caption_parts.append(metadata["description"])
        for ht in metadata.get("hashtags", [])[:30]:
            tag = ht if ht.startswith("#") else f"#{ht}"
            caption_parts.append(tag)
        caption = "\n".join(caption_parts)[:2200]

        # Step 1: Create media container
        container_params = urlencode({
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
            "access_token": self._access_token,
        })
        container_url = f"{GRAPH_API_BASE}/{self._ig_user_id}/media?{container_params}"

        try:
            req = Request(container_url, method="POST")
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            container_id = data.get("id")
            if not container_id:
                return UploadResult(
                    platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                    video_id="", success=False, error="no_container_id_returned",
                )
        except HTTPError as exc:
            body = exc.read().decode(errors="replace")
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error=f"container_create_failed_{exc.code}: {body[:200]}",
            )

        # Step 2: Poll container status until FINISHED
        if not self._poll_container_status(container_id):
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error="container_processing_timeout",
            )

        # Step 3: Publish the container
        publish_params = urlencode({
            "creation_id": container_id,
            "access_token": self._access_token,
        })
        publish_url = f"{GRAPH_API_BASE}/{self._ig_user_id}/media_publish?{publish_params}"

        try:
            req = Request(publish_url, method="POST")
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            media_id = data.get("id", "")
            return UploadResult(
                platform=self.PLATFORM,
                channel_id="",
                brand_id=self.brand_id,
                video_id="",
                success=True,
                platform_video_id=media_id,
                platform_url=f"https://www.instagram.com/reel/{media_id}/",
                uploaded_at=datetime.now(timezone.utc).isoformat(),
                metadata={"caption": caption[:100]},
            )
        except HTTPError as exc:
            body = exc.read().decode(errors="replace")
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error=f"publish_failed_{exc.code}: {body[:200]}",
            )

    def _poll_container_status(self, container_id: str, max_polls: int = 30, interval_s: int = 10) -> bool:
        """Poll until container status is FINISHED. Return True on success."""
        for _ in range(max_polls):
            params = urlencode({
                "fields": "status_code",
                "access_token": self._access_token,
            })
            url = f"{GRAPH_API_BASE}/{container_id}?{params}"
            try:
                with urlopen(Request(url), timeout=15) as resp:
                    data = json.loads(resp.read())
                status = data.get("status_code", "")
                if status == "FINISHED":
                    return True
                if status == "ERROR":
                    logger.error("Instagram container %s failed processing", container_id)
                    return False
            except (HTTPError, json.JSONDecodeError):
                pass
            time.sleep(interval_s)
        return False

    def _set_metadata(self, platform_video_id: str, metadata: dict[str, Any]) -> bool:
        """Instagram does not support editing Reels metadata after publish."""
        logger.info("Instagram: post-publish metadata edits not supported")
        return True
