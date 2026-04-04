"""LINE video uploader — push video messages via LINE Messaging API.

LINE doesn't have a YouTube-style video upload API. Instead:
1. Video is hosted externally (Cloudflare R2 or other CDN)
2. LINE Messaging API sends a video message with the hosted URL
3. Followers see the video in their chat with the brand's LINE Official Account

Requires: LINE_CHANNEL_ACCESS_TOKEN_{SUFFIX} and LINE_TARGET_AUDIENCE_{SUFFIX}
          (group ID, user ID, or narrowcast audience)
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Optional

from .base import BaseUploader, UploadResult

logger = logging.getLogger(__name__)

try:
    import requests
except ImportError:
    requests = None  # type: ignore


LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_BROADCAST_URL = "https://api.line.me/v2/bot/message/broadcast"


class LINEUploader(BaseUploader):
    """Upload video to LINE followers via Messaging API push/broadcast."""

    platform = "line"

    def __init__(
        self,
        channel_id: str,
        brand_id: str,
        credential_suffix: str = "",
        dry_run: bool = True,
        video_host_url_base: str = "",
    ):
        super().__init__(channel_id=channel_id, brand_id=brand_id, dry_run=dry_run)
        self._suffix = credential_suffix.upper()
        self._access_token: str = ""
        self._target_id: str = ""  # group_id or user_id for push; empty = broadcast
        self._video_host_base = video_host_url_base

    def authenticate(self) -> bool:
        """Load LINE channel access token from env."""
        self._access_token = os.environ.get(f"LINE_CHANNEL_ACCESS_TOKEN{self._suffix}", "")
        self._target_id = os.environ.get(f"LINE_TARGET_AUDIENCE{self._suffix}", "")

        if not self._access_token:
            logger.error("LINE_CHANNEL_ACCESS_TOKEN%s not set", self._suffix)
            return False
        return True

    def _upload_video(
        self,
        video_path: Path,
        metadata: dict[str, Any],
    ) -> UploadResult:
        """Push video message to LINE followers.

        Since LINE doesn't host videos, we need a public URL.
        If video_host_url_base is set, construct URL from filename.
        Otherwise, return error asking for hosted URL.
        """
        if requests is None:
            return UploadResult(
                platform=self.platform,
                channel_id=self.channel_id,
                brand_id=self.brand_id,
                video_id=metadata.get("video_id", ""),
                success=False,
                error="requests library not installed",
            )

        # Construct video URL
        video_url = metadata.get("video_url") or ""
        if not video_url and self._video_host_base:
            video_url = f"{self._video_host_base.rstrip('/')}/{video_path.name}"

        if not video_url:
            return UploadResult(
                platform=self.platform,
                channel_id=self.channel_id,
                brand_id=self.brand_id,
                video_id=metadata.get("video_id", ""),
                success=False,
                error="No video_url provided and no video_host_url_base configured. LINE requires hosted video URL.",
            )

        # Build LINE message
        preview_url = metadata.get("thumbnail_url") or video_url  # fallback to video URL
        message = {
            "type": "video",
            "originalContentUrl": video_url,
            "previewImageUrl": preview_url,
        }

        # Add text message with CTA if provided
        messages = [message]
        cta_text = metadata.get("cta_text") or ""
        if cta_text:
            messages.append({"type": "text", "text": cta_text})

        # Push or broadcast
        if self._target_id:
            url = LINE_PUSH_URL
            body = {"to": self._target_id, "messages": messages}
        else:
            url = LINE_BROADCAST_URL
            body = {"messages": messages}

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        if self.dry_run:
            logger.info("[DRY-RUN] LINE %s: would send %d message(s) to %s",
                        "push" if self._target_id else "broadcast",
                        len(messages),
                        self._target_id or "all followers")
            return UploadResult(
                platform=self.platform,
                channel_id=self.channel_id,
                brand_id=self.brand_id,
                video_id=metadata.get("video_id", ""),
                success=True,
                platform_url=video_url,
                metadata={"dry_run": True, "message_count": len(messages)},
            )

        resp = requests.post(url, headers=headers, json=body, timeout=30)
        if resp.status_code == 200:
            return UploadResult(
                platform=self.platform,
                channel_id=self.channel_id,
                brand_id=self.brand_id,
                video_id=metadata.get("video_id", ""),
                success=True,
                platform_url=video_url,
                metadata={"line_response": resp.json() if resp.text else {}},
            )
        else:
            return UploadResult(
                platform=self.platform,
                channel_id=self.channel_id,
                brand_id=self.brand_id,
                video_id=metadata.get("video_id", ""),
                success=False,
                error=f"LINE API {resp.status_code}: {resp.text[:200]}",
            )

    def _set_metadata(self, platform_video_id: str, metadata: dict[str, Any]) -> bool:
        """LINE messages don't have editable metadata after sending."""
        return True
