"""Bilibili uploader — Stage 18 platform integration for Bilibili Web Upload API.

Auth: Cookie-based (SESSDATA + bili_jct CSRF token).
Upload: Multipart chunk upload → submit with metadata.

Note: Bilibili requires zh-CN subtitles for all therapeutic content (platform policy).
The compliance flag in upload_config.yaml enforces this check before upload.
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

PREUPLOAD_URL = "https://member.bilibili.com/preupload"
SUBMIT_URL = "https://member.bilibili.com/x/vu/web/add"


class BilibiliUploader(BaseUploader):
    PLATFORM = "bilibili"

    def __init__(self, platform_config: dict, brand_id: str, credential_suffix: str = "", dry_run: bool = True):
        super().__init__(platform_config, brand_id, credential_suffix, dry_run)
        self._sessdata: str = ""
        self._csrf: str = ""

    def authenticate(self) -> bool:
        """Load SESSDATA and CSRF token from environment."""
        self._sessdata = self._env("BILI_SESSDATA")
        self._csrf = self._env("BILI_CSRF")
        if not self._sessdata or not self._csrf:
            logger.error("Bilibili: missing credentials for brand %s", self.brand_id)
            return False
        self._authenticated = True
        logger.info("Bilibili: authenticated for brand %s", self.brand_id)
        return True

    def _check_zh_subtitles(self, metadata: dict[str, Any]) -> bool:
        """Verify zh-CN subtitles are present (Bilibili compliance requirement)."""
        compliance = self.config.get("compliance", {})
        if compliance.get("requires_zh_subtitles"):
            subtitle_path = metadata.get("zh_subtitle_path", "")
            if not subtitle_path or not Path(subtitle_path).exists():
                logger.error("Bilibili: zh-CN subtitles required but not found at %s", subtitle_path)
                return False
        return True

    def _upload_video(self, video_path: Path, metadata: dict[str, Any]) -> UploadResult:
        """Upload video via Bilibili chunk upload flow."""
        if not self._check_zh_subtitles(metadata):
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error="zh_subtitles_required: Bilibili requires zh-CN subtitles",
            )

        title = metadata.get("title", "")[:80]
        description = metadata.get("description", "")[:2000]
        tags = metadata.get("tags", [])[:12]
        file_size = video_path.stat().st_size

        # Step 1: Get upload endpoint via preupload
        preupload_params = urlencode({
            "name": video_path.name,
            "size": file_size,
            "r": "upos",
            "profile": "ugcupos/bup",
        })
        pre_url = f"{PREUPLOAD_URL}?{preupload_params}"
        req = Request(pre_url)
        req.add_header("Cookie", f"SESSDATA={self._sessdata}")

        try:
            with urlopen(req, timeout=30) as resp:
                pre_data = json.loads(resp.read())
        except HTTPError as exc:
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error=f"preupload_failed_{exc.code}",
            )

        upos_uri = pre_data.get("upos_uri", "")
        upload_endpoint = pre_data.get("endpoint", "")
        auth_token = pre_data.get("auth", "")
        biz_id = pre_data.get("biz_id", 0)

        if not upos_uri or not upload_endpoint:
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False, error="preupload_missing_endpoint",
            )

        # Step 2: Upload file chunks
        chunk_size = self.config.get("upload", {}).get("chunk_size_bytes", 5 * 1024 * 1024)
        chunks_total = -(-file_size // chunk_size)

        with open(video_path, "rb") as f:
            for chunk_idx in range(chunks_total):
                chunk = f.read(chunk_size)
                chunk_url = (
                    f"https:{upload_endpoint}/{upos_uri.replace('upos://', '')}"
                    f"?partNumber={chunk_idx + 1}&uploadId={auth_token}"
                    f"&chunk={chunk_idx}&chunks={chunks_total}&size={len(chunk)}"
                    f"&start={chunk_idx * chunk_size}&end={chunk_idx * chunk_size + len(chunk)}"
                    f"&total={file_size}"
                )
                chunk_req = Request(chunk_url, data=chunk, method="PUT")
                chunk_req.add_header("Cookie", f"SESSDATA={self._sessdata}")
                try:
                    with urlopen(chunk_req, timeout=300):
                        pass
                except HTTPError as exc:
                    return UploadResult(
                        platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                        video_id="", success=False,
                        error=f"chunk_{chunk_idx}_failed_{exc.code}",
                    )

        # Step 3: Submit video with metadata
        submit_body = {
            "csrf": self._csrf,
            "videos": [{
                "filename": upos_uri.split("/")[-1].split(".")[0],
                "title": title,
                "desc": "",
                "cid": biz_id,
            }],
            "title": title,
            "desc": description,
            "tag": ",".join(tags),
            "tid": 122,  # 生活 → 日常 (Daily Life category, suitable for self-help)
            "copyright": 1,  # Original
            "no_reprint": 1,
            "subtitle": {"open": 1, "lan": "zh-CN"},
        }

        req = Request(SUBMIT_URL, data=json.dumps(submit_body).encode(), method="POST")
        req.add_header("Cookie", f"SESSDATA={self._sessdata}")
        req.add_header("Content-Type", "application/json")

        try:
            with urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read())
            if data.get("code") == 0:
                bili_bvid = data.get("data", {}).get("bvid", "")
                return UploadResult(
                    platform=self.PLATFORM,
                    channel_id="",
                    brand_id=self.brand_id,
                    video_id="",
                    success=True,
                    platform_video_id=bili_bvid,
                    platform_url=f"https://www.bilibili.com/video/{bili_bvid}",
                    uploaded_at=datetime.now(timezone.utc).isoformat(),
                    metadata={"title": title, "status": "pending_review"},
                )
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error=f"submit_error_{data.get('code')}: {data.get('message', '')}",
            )
        except HTTPError as exc:
            return UploadResult(
                platform=self.PLATFORM, channel_id="", brand_id=self.brand_id,
                video_id="", success=False,
                error=f"submit_failed_{exc.code}",
            )

    def _set_metadata(self, platform_video_id: str, metadata: dict[str, Any]) -> bool:
        """Bilibili supports limited metadata edits via web API."""
        logger.info("Bilibili: post-upload metadata edits require web session — skipping")
        return True
