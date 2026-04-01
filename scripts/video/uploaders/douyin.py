"""Douyin uploader — Stage 18 platform integration for Douyin Open Platform API.

Auth: OAuth2 with client key/secret + access token.
Upload: Direct upload flow → create video → publish.

Note: Douyin is separate from TikTok (different API, different accounts, different content review).
ICP filing required for production use. Content review typically takes 24-72 hours.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from scripts.video.uploaders.base import BaseUploader, UploadResult

logger = logging.getLogger(__name__)

UPLOAD_URL = "https://open.douyin.com/api/media/video/upload/"
CREATE_URL = "https://open.douyin.com/api/douyin/v1/video/create_video/"


class DouyinUploader(BaseUploader):
    PLATFORM = "douyin"

    def __init__(self, platform_config: dict, brand_id: str, credential_suffix: str = "", dry_run: bool = True):
        super().__init__(platform_config, brand_id, credential_suffix, dry_run)
        self._access_token: str = ""

    def authenticate(self) -> bool:
        """Load Douyin access token from environment."""
        self._access_token = self._env("DOUYIN_ACCESS_TOKEN")
        if not self._access_token:
            logger.error("Douyin: missing access token for brand %s", self.brand_id)
            return False
        self._authenticated = True
        logger.info("Douyin: authenticated for brand %s", self.brand_id)
        return True

    def _upload_video(self, video_path: Path, metadata: dict[str, Any]) -> UploadResult:
        """Upload video via Douyin direct upload + create video flow."""
        title = metadata.get("title", "")[:55]
        hashtags = metadata.get("hashtags", [])[:20]

        file_size = video_path.stat().st_size

        # Step 1: Upload the video file
        with open(video_path, "rb") as f:
            video_data = f.read()

        req = Request(UPLOAD_URL, data=video_data, method="POST")
        req.add_header("Authorization", f"Bearer {self._access_token}")
        req.add_header("Content-Type", "video/mp4")
        req.add_header("Content-Length", str(file_size))

        try:
            with urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read())
        except HTTPError as exc:
            body = exc.read().decode(errors="replace")
            if exc.code == 429:
                return UploadResult(
                    platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                    video_id="", success=False, error="rate_limited",
                    retry_after_s=self.config.get("rate_limits", {}).get("retry_after_rate_limit_s", 300),
                )
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error=f"upload_failed_{exc.code}: {body[:200]}",
            )

        video_item_id = data.get("data", {}).get("video", {}).get("video_id", "")
        if not video_item_id:
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False, error="no_video_id_returned",
            )

        # Step 2: Create/publish the video with metadata
        caption_parts = [title]
        for ht in hashtags:
            tag = ht if ht.startswith("#") else f"#{ht}"
            caption_parts.append(tag)

        create_body = {
            "video_id": video_item_id,
            "text": " ".join(caption_parts)[:55],
        }

        req = Request(CREATE_URL, data=json.dumps(create_body).encode(), method="POST")
        req.add_header("Authorization", f"Bearer {self._access_token}")
        req.add_header("Content-Type", "application/json")

        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            item_id = data.get("data", {}).get("item_id", "")
            return UploadResult(
                platform=self.PLATFORM,
                channel_id="",
                brand_id=self.brand_id,
                video_id="",
                success=True,
                platform_video_id=item_id or video_item_id,
                platform_url=f"https://www.douyin.com/video/{item_id}" if item_id else "pending_review",
                uploaded_at=datetime.now(timezone.utc).isoformat(),
                metadata={
                    "title": title,
                    "status": "pending_review",
                    "review_lag_hours": self.config.get("rate_limits", {}).get("content_review_lag_hours", 24),
                },
            )
        except HTTPError as exc:
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error=f"create_failed_{exc.code}",
            )

    def _set_metadata(self, platform_video_id: str, metadata: dict[str, Any]) -> bool:
        """Douyin does not support post-publish metadata edits via open API."""
        logger.info("Douyin: post-publish metadata edits not supported via API")
        return True
