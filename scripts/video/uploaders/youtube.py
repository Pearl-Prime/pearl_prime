"""YouTube uploader — Stage 18 platform integration for YouTube Data API v3.

Handles both long-form YouTube and YouTube Shorts uploads via the same API.
Shorts are regular uploads with #Shorts in title/description and ≤60s duration.

Auth: OAuth2 with refresh token (no user interaction at runtime).
Upload: Resumable upload protocol for reliability on large files.
"""
from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from scripts.video.uploaders.base import BaseUploader, UploadResult

logger = logging.getLogger(__name__)

TOKEN_URL = "https://oauth2.googleapis.com/token"
UPLOAD_URL = "https://www.googleapis.com/upload/youtube/v3/videos"
VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


class YouTubeUploader(BaseUploader):
    PLATFORM = "youtube"

    def __init__(self, platform_config: dict, brand_id: str, credential_suffix: str = "", dry_run: bool = True):
        super().__init__(platform_config, brand_id, credential_suffix, dry_run)
        self._access_token: str = ""
        self._is_shorts = False

    def set_shorts_mode(self, enabled: bool = True) -> None:
        self._is_shorts = enabled

    def authenticate(self) -> bool:
        """Exchange refresh token for access token via OAuth2."""
        try:
            client_id = self._env("YT_CLIENT_ID")
            client_secret = self._env("YT_CLIENT_SECRET")
            refresh_token = self._env("YT_REFRESH_TOKEN")
        except EnvironmentError as exc:
            logger.error("YouTube: %s", exc)
            return False

        if not all([client_id, client_secret, refresh_token]):
            logger.error("YouTube: missing OAuth2 credentials for brand %s", self.brand_id)
            return False

        body = urlencode({
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }).encode()

        req = Request(TOKEN_URL, data=body, method="POST")
        req.add_header("Content-Type", "application/x-www-form-urlencoded")

        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            self._access_token = data["access_token"]
            self._authenticated = True
            logger.info("YouTube: authenticated for brand %s", self.brand_id)
            return True
        except (HTTPError, KeyError, json.JSONDecodeError) as exc:
            logger.error("YouTube: auth failed for brand %s: %s", self.brand_id, exc)
            return False

    def _upload_video(self, video_path: Path, metadata: dict[str, Any]) -> UploadResult:
        """Upload video using YouTube resumable upload protocol."""
        title = metadata.get("title", "Untitled")[:100]
        description = metadata.get("description", "")[:5000]
        tags = metadata.get("tags", [])[:30]
        hashtags = metadata.get("hashtags", [])

        if self._is_shorts and "#Shorts" not in title:
            title = f"{title} #Shorts"
        for ht in hashtags:
            tag = ht if ht.startswith("#") else f"#{ht}"
            if tag not in description:
                description = f"{description}\n{tag}"

        # Step 1: Initiate resumable upload
        video_meta = {
            "snippet": {
                "title": title,
                "description": description.strip(),
                "tags": tags,
                "categoryId": "22",  # People & Blogs (best for self-help)
                "defaultLanguage": "en",
            },
            "status": {
                "privacyStatus": "public",
                "selfDeclaredMadeForKids": False,
                "embeddable": True,
                "license": "youtube",
            },
        }

        params = urlencode({
            "uploadType": "resumable",
            "part": "snippet,status",
        })
        init_url = f"{UPLOAD_URL}?{params}"

        req = Request(init_url, data=json.dumps(video_meta).encode(), method="POST")
        req.add_header("Authorization", f"Bearer {self._access_token}")
        req.add_header("Content-Type", "application/json; charset=UTF-8")
        file_size = video_path.stat().st_size
        req.add_header("X-Upload-Content-Length", str(file_size))
        req.add_header("X-Upload-Content-Type", "video/mp4")

        try:
            with urlopen(req, timeout=30) as resp:
                upload_url = resp.headers.get("Location")
                if not upload_url:
                    return UploadResult(
                        platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                        video_id="", success=False, error="no_resumable_upload_url",
                    )
        except HTTPError as exc:
            body = exc.read().decode(errors="replace")
            if exc.code == 403 and "quotaExceeded" in body:
                return UploadResult(
                    platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                    video_id="", success=False, error="quota_exceeded",
                    retry_after_s=self.config.get("rate_limits", {}).get("retry_after_quota_s", 3600),
                )
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False, error=f"init_failed_{exc.code}: {body[:200]}",
            )

        # Step 2: Upload file in chunks
        chunk_size = self.config.get("upload", {}).get("chunk_size_bytes", 10 * 1024 * 1024)
        uploaded = 0

        with open(video_path, "rb") as f:
            while uploaded < file_size:
                chunk = f.read(chunk_size)
                end = uploaded + len(chunk) - 1

                chunk_req = Request(upload_url, data=chunk, method="PUT")
                chunk_req.add_header("Content-Type", "video/mp4")
                chunk_req.add_header("Content-Length", str(len(chunk)))
                chunk_req.add_header("Content-Range", f"bytes {uploaded}-{end}/{file_size}")

                try:
                    with urlopen(chunk_req, timeout=300) as resp:
                        if resp.status in (200, 201):
                            result_data = json.loads(resp.read())
                            yt_video_id = result_data.get("id", "")
                            return UploadResult(
                                platform="youtube_shorts" if self._is_shorts else "youtube",
                                channel_id="",
                                brand_id=self.brand_id,
                                video_id="",
                                success=True,
                                platform_video_id=yt_video_id,
                                platform_url=f"https://youtube.com/watch?v={yt_video_id}",
                                uploaded_at=datetime.now(timezone.utc).isoformat(),
                                metadata={"title": title, "privacy": "public"},
                            )
                except HTTPError as exc:
                    if exc.code == 308:
                        # Resume incomplete — continue uploading
                        uploaded = end + 1
                        continue
                    return UploadResult(
                        platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                        video_id="", success=False,
                        error=f"chunk_upload_failed_{exc.code}",
                    )
                uploaded = end + 1

        return UploadResult(
            platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
            video_id="", success=False, error="upload_completed_without_response",
        )

    def _set_metadata(self, platform_video_id: str, metadata: dict[str, Any]) -> bool:
        """Update video metadata after upload."""
        params = urlencode({"part": "snippet,status"})
        url = f"{VIDEOS_URL}?{params}"

        body = {
            "id": platform_video_id,
            "snippet": {
                "title": metadata.get("title", "")[:100],
                "description": metadata.get("description", "")[:5000],
                "tags": metadata.get("tags", [])[:30],
                "categoryId": "22",
            },
        }

        req = Request(url, data=json.dumps(body).encode(), method="PUT")
        req.add_header("Authorization", f"Bearer {self._access_token}")
        req.add_header("Content-Type", "application/json")

        try:
            with urlopen(req, timeout=30) as resp:
                return resp.status == 200
        except HTTPError as exc:
            logger.error("YouTube metadata update failed: %s", exc)
            return False
