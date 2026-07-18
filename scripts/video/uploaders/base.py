"""Base uploader interface for Stage 18 — Upload/Publish."""
from __future__ import annotations

import logging
import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class UploadResult:
    """Result of a single video upload attempt."""

    platform: str
    channel_id: str
    brand_id: str
    video_id: str
    success: bool
    platform_video_id: str | None = None
    platform_url: str | None = None
    error: str | None = None
    retry_after_s: int | None = None
    quota_remaining: int | None = None
    uploaded_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {k: v for k, v in self.__dict__.items() if v is not None}


class BaseUploader(ABC):
    """Abstract base for all platform uploaders.

    Subclasses must implement:
      - authenticate()
      - _upload_video()
      - _set_metadata()

    The base class handles:
      - credential loading from env vars
      - dry-run mode
      - retry with exponential backoff
      - quota tracking
      - result formatting
    """

    PLATFORM: str = ""

    def __init__(
        self,
        platform_config: dict,
        brand_id: str,
        credential_suffix: str = "",
        dry_run: bool = True,
    ):
        self.config = platform_config
        self.brand_id = brand_id
        self.credential_suffix = credential_suffix
        self.dry_run = dry_run
        self._authenticated = False
        self._daily_upload_count = 0

    def _env(self, key: str) -> str:
        """Load credential from environment, applying brand suffix."""
        env_key = f"{key}{self.credential_suffix}"
        val = os.environ.get(env_key, "")
        if not val and not self.dry_run:
            raise EnvironmentError(f"Missing required credential: {env_key}")
        return val

    def _check_rate_limit(self) -> bool:
        """Return True if under daily rate limit."""
        limits = self.config.get("rate_limits", {})
        max_per_day = limits.get("max_uploads_per_day", 999)
        if self._daily_upload_count >= max_per_day:
            logger.warning(
                "%s: daily limit reached (%d/%d) for brand %s",
                self.PLATFORM,
                self._daily_upload_count,
                max_per_day,
                self.brand_id,
            )
            return False
        return True

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the platform API. Return True on success."""
        ...

    @abstractmethod
    def _upload_video(
        self,
        video_path: Path,
        metadata: dict[str, Any],
    ) -> UploadResult:
        """Platform-specific upload implementation."""
        ...

    @abstractmethod
    def _set_metadata(
        self,
        platform_video_id: str,
        metadata: dict[str, Any],
    ) -> bool:
        """Update metadata on an already-uploaded video. Return True on success."""
        ...

    def upload(
        self,
        video_path: Path,
        channel_id: str,
        video_id: str,
        variant: dict[str, Any],
        max_retries: int = 3,
        backoff_base_s: int = 60,
    ) -> UploadResult:
        """Upload a video with retry logic and dry-run support.

        Args:
            video_path: Path to the rendered video file.
            channel_id: Channel identifier from channel_registry.
            video_id: VCE video identifier.
            variant: Platform variant dict from platform_variants.json.
            max_retries: Maximum retry attempts.
            backoff_base_s: Base seconds for exponential backoff.
        """
        metadata = variant.get("metadata", {})
        metadata["channel_id"] = channel_id

        if not self._check_rate_limit():
            return UploadResult(
                platform=self.PLATFORM,
                channel_id=channel_id,
                brand_id=self.brand_id,
                video_id=video_id,
                success=False,
                error="daily_rate_limit_exceeded",
            )

        if self.dry_run:
            logger.info(
                "DRY RUN: would upload %s to %s (channel=%s, brand=%s)",
                video_path.name,
                self.PLATFORM,
                channel_id,
                self.brand_id,
            )
            return UploadResult(
                platform=self.PLATFORM,
                channel_id=channel_id,
                brand_id=self.brand_id,
                video_id=video_id,
                success=True,
                platform_video_id="dry-run-id",
                platform_url=f"https://{self.PLATFORM}.example.com/dry-run",
                metadata={"dry_run": True, "video_path": str(video_path)},
            )

        if not self._authenticated:
            if not self.authenticate():
                return UploadResult(
                    platform=self.PLATFORM,
                    channel_id=channel_id,
                    brand_id=self.brand_id,
                    video_id=video_id,
                    success=False,
                    error="authentication_failed",
                )

        last_error = ""
        for attempt in range(max_retries):
            try:
                result = self._upload_video(video_path, metadata)
                if result.success:
                    self._daily_upload_count += 1
                    result.channel_id = channel_id
                    result.brand_id = self.brand_id
                    result.video_id = video_id
                    return result
                last_error = result.error or "unknown"
                if result.retry_after_s:
                    wait = result.retry_after_s
                else:
                    wait = backoff_base_s * (2**attempt)
                logger.warning(
                    "%s upload attempt %d/%d failed: %s — retrying in %ds",
                    self.PLATFORM,
                    attempt + 1,
                    max_retries,
                    last_error,
                    wait,
                )
                time.sleep(wait)
            except Exception as exc:
                last_error = str(exc)
                wait = backoff_base_s * (2**attempt)
                logger.error(
                    "%s upload attempt %d/%d raised %s — retrying in %ds",
                    self.PLATFORM,
                    attempt + 1,
                    max_retries,
                    last_error,
                    wait,
                )
                time.sleep(wait)

        return UploadResult(
            platform=self.PLATFORM,
            channel_id=channel_id,
            brand_id=self.brand_id,
            video_id=video_id,
            success=False,
            error=f"max_retries_exceeded: {last_error}",
        )
