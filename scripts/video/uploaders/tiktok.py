"""TikTok uploader — Stage 18 platform integration for TikTok Content Posting API v2.

Auth: OAuth2 with client key/secret + access token.
Upload: Direct file upload via chunk upload, then publish.
"""
from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from scripts.video.uploaders.base import BaseUploader, UploadResult

logger = logging.getLogger(__name__)

INIT_URL = "https://open.tiktokapis.com/v2/post/publish/video/init/"
CHUNK_INIT_URL = "https://open.tiktokapis.com/v2/post/publish/inbox/video/init/"
STATUS_URL = "https://open.tiktokapis.com/v2/post/publish/status/fetch/"


class TikTokUploader(BaseUploader):
    PLATFORM = "tiktok"

    def __init__(self, platform_config: dict, brand_id: str, credential_suffix: str = "", dry_run: bool = True):
        super().__init__(platform_config, brand_id, credential_suffix, dry_run)
        self._access_token: str = ""

    def authenticate(self) -> bool:
        """Load access token from environment.

        TikTok OAuth2 flow requires user interaction for initial token grant.
        At runtime we use a pre-obtained access token (refreshed via CI secret rotation).
        """
        try:
            self._access_token = self._env("TIKTOK_ACCESS_TOKEN")
        except EnvironmentError as exc:
            logger.error("TikTok: %s", exc)
            return False
        if not self._access_token:
            logger.error("TikTok: missing access token for brand %s", self.brand_id)
            return False
        self._authenticated = True
        logger.info("TikTok: authenticated for brand %s", self.brand_id)
        return True

    def _upload_video(self, video_path: Path, metadata: dict[str, Any]) -> UploadResult:
        """Upload video via TikTok direct post API (chunk upload path)."""
        title = metadata.get("title", "")[:150]
        description = metadata.get("description", "")[:2200]
        hashtags = metadata.get("hashtags", [])[:30]

        # Build caption with hashtags
        caption_parts = [title]
        if description and description != title:
            caption_parts.append(description)
        for ht in hashtags:
            tag = ht if ht.startswith("#") else f"#{ht}"
            caption_parts.append(tag)
        caption = " ".join(caption_parts)[:2200]

        file_size = video_path.stat().st_size
        chunk_size = 10 * 1024 * 1024  # 10 MB

        # Step 1: Initialize upload
        init_body = {
            "post_info": {
                "title": title,
                "description": caption,
                "disable_duet": False,
                "disable_comment": False,
                "disable_stitch": False,
                "privacy_level": "PUBLIC_TO_EVERYONE",
            },
            "source_info": {
                "source": "FILE_UPLOAD",
                "video_size": file_size,
                "chunk_size": chunk_size,
                "total_chunk_count": -(-file_size // chunk_size),  # ceiling division
            },
        }

        req = Request(CHUNK_INIT_URL, data=json.dumps(init_body).encode(), method="POST")
        req.add_header("Authorization", f"Bearer {self._access_token}")
        req.add_header("Content-Type", "application/json; charset=UTF-8")

        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
        except HTTPError as exc:
            body = exc.read().decode(errors="replace")
            if exc.code == 429:
                return UploadResult(
                    platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                    video_id="", success=False, error="rate_limited",
                    retry_after_s=self.config.get("rate_limits", {}).get("retry_after_rate_limit_s", 60),
                )
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False, error=f"init_failed_{exc.code}: {body[:200]}",
            )

        error_data = data.get("error", {})
        if error_data.get("code") != "ok":
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error=f"init_error: {error_data.get('message', 'unknown')}",
            )

        upload_url = data.get("data", {}).get("upload_url", "")
        publish_id = data.get("data", {}).get("publish_id", "")

        if not upload_url:
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False, error="no_upload_url_returned",
            )

        # Step 2: Upload file chunks
        with open(video_path, "rb") as f:
            chunk_idx = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                chunk_req = Request(upload_url, data=chunk, method="PUT")
                chunk_req.add_header("Content-Type", "video/mp4")
                chunk_req.add_header("Content-Range",
                    f"bytes {chunk_idx * chunk_size}-{chunk_idx * chunk_size + len(chunk) - 1}/{file_size}")
                try:
                    with urlopen(chunk_req, timeout=300):
                        pass
                except HTTPError as exc:
                    return UploadResult(
                        platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                        video_id="", success=False,
                        error=f"chunk_{chunk_idx}_failed_{exc.code}",
                    )
                chunk_idx += 1

        # Step 3: Poll publish status
        tt_video_id = self._poll_publish_status(publish_id)
        if tt_video_id:
            return UploadResult(
                platform=self.PLATFORM,
                channel_id="",
                brand_id=self.brand_id,
                video_id="",
                success=True,
                platform_video_id=tt_video_id,
                platform_url=f"https://www.tiktok.com/@user/video/{tt_video_id}",
                uploaded_at=datetime.now(timezone.utc).isoformat(),
                metadata={"title": title, "caption": caption[:100]},
            )

        return UploadResult(
            platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
            video_id="", success=True,
            platform_video_id=publish_id,
            platform_url="pending_review",
            uploaded_at=datetime.now(timezone.utc).isoformat(),
            metadata={"title": title, "status": "processing"},
        )

    def _poll_publish_status(self, publish_id: str, max_polls: int = 10, interval_s: int = 5) -> str | None:
        """Poll TikTok for publish completion. Returns video_id or None."""
        for _ in range(max_polls):
            body = {"publish_id": publish_id}
            req = Request(STATUS_URL, data=json.dumps(body).encode(), method="POST")
            req.add_header("Authorization", f"Bearer {self._access_token}")
            req.add_header("Content-Type", "application/json")
            try:
                with urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read())
                status = data.get("data", {}).get("status", "")
                if status == "PUBLISH_COMPLETE":
                    return data.get("data", {}).get("publicaly_available_post_id", [{}])[0].get("id", "")
                if status in ("FAILED", "PUBLISH_FAILED"):
                    return None
            except (HTTPError, json.JSONDecodeError):
                pass
            time.sleep(interval_s)
        return None

    def _set_metadata(self, platform_video_id: str, metadata: dict[str, Any]) -> bool:
        """TikTok does not support post-upload metadata edits via API."""
        logger.info("TikTok: metadata updates not supported via API")
        return True
