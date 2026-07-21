"""Low-level Storyblocks API client (HMAC auth).

Credentials (optional until live calls):
  STORYBLOCKS_PUBLIC_KEY
  STORYBLOCKS_PRIVATE_KEY

Load via:
  eval "$(python3 scripts/ci/load_integration_env_from_keychain.py)"
"""

from __future__ import annotations

import hashlib
import hmac
import logging
import os
import time
from typing import Any, Callable, Literal

import requests

from scripts.storyblocks.exceptions import (
    StoryblocksAssetNotFoundError,
    StoryblocksAuthError,
    StoryblocksConfigError,
    StoryblocksError,
    StoryblocksRateLimitError,
    StoryblocksTimeoutError,
)
from scripts.storyblocks.identity import anonymize_project_id, anonymize_user_id
from scripts.storyblocks.rate_limiter import SlidingWindowRateLimiter, default_rate_limiter

logger = logging.getLogger(__name__)

MediaType = Literal["video", "image", "audio"]


class StoryblocksAPIClient:
    """HMAC-authenticated Storyblocks API wrapper.

    Shared search/download surface for video, image, and audio (Lane 03/04).
    Lane 04 must extend this client — do not fork a second Storyblocks client.
    """

    BASE_URL = "https://api.storyblocks.com"
    RATE_LIMIT_BACKOFF = 5
    MAX_RETRIES = 2

    def __init__(
        self,
        public_key: str | None = None,
        private_key: str | None = None,
        rate_limiter: SlidingWindowRateLimiter | None = None,
        session: requests.Session | None = None,
        request_fn: Callable[..., Any] | None = None,
        require_keys: bool = True,
    ) -> None:
        self.public_key = public_key if public_key is not None else os.environ.get("STORYBLOCKS_PUBLIC_KEY", "")
        self.private_key = private_key if private_key is not None else os.environ.get("STORYBLOCKS_PRIVATE_KEY", "")
        self.rate_limiter = rate_limiter or default_rate_limiter
        self.session = session or requests.Session()
        self._request_fn = request_fn
        if require_keys and (not self.public_key or not self.private_key):
            raise StoryblocksConfigError(
                "Storyblocks API keys missing. Set STORYBLOCKS_PUBLIC_KEY and "
                "STORYBLOCKS_PRIVATE_KEY (Keychain via "
                "scripts/ci/load_integration_env_from_keychain.py). "
                "Do not invent fake successful live downloads."
            )

    def _generate_hmac(self, resource: str, *, now: float | None = None) -> tuple[int, str]:
        if "/:" in resource or resource.rstrip("/").endswith(":"):
            raise ValueError(
                f"Resource path contains unresolved template variable: {resource}. "
                "Sign the actual path with real IDs, not URL templates."
            )
        if not resource.startswith("/"):
            resource = "/" + resource
        resource = resource.split("?")[0]
        expires = int((time.time() if now is None else now) + 3600)
        hmac_key = f"{self.private_key}{expires}"
        signature = hmac.new(
            hmac_key.encode("utf-8"),
            resource.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return expires, signature

    def _make_request(
        self,
        method: str,
        resource: str,
        params: dict[str, Any] | None = None,
        *,
        rate_kind: str,
        timeout: int = 30,
        retry_count: int = 0,
    ) -> dict[str, Any]:
        if not self.public_key or not self.private_key:
            raise StoryblocksConfigError(
                "Storyblocks API keys missing; refusing live HTTP call."
            )
        self.rate_limiter.acquire(rate_kind)
        expires, hmac_sig = self._generate_hmac(resource)
        auth_params = {
            "APIKEY": self.public_key,
            "EXPIRES": expires,
            "HMAC": hmac_sig,
        }
        all_params = {**(params or {}), **auth_params}
        url = f"{self.BASE_URL}{resource}"
        try:
            if self._request_fn is not None:
                response = self._request_fn(method, url, params=all_params, timeout=timeout)
            else:
                response = self.session.request(method, url, params=all_params, timeout=timeout)
        except requests.exceptions.Timeout as exc:
            raise StoryblocksTimeoutError(f"Request timeout: {resource}") from exc

        if response.status_code == 429:
            if retry_count < self.MAX_RETRIES:
                logger.warning("Storyblocks 429; backoff %ss", self.RATE_LIMIT_BACKOFF)
                time.sleep(self.RATE_LIMIT_BACKOFF)
                return self._make_request(
                    method, resource, params, rate_kind=rate_kind, timeout=timeout, retry_count=retry_count + 1
                )
            raise StoryblocksRateLimitError("Rate limit exceeded after retries")

        if response.status_code == 403:
            try:
                error_data = response.json()
            except Exception:
                error_data = {"errors": response.text}
            raise StoryblocksAuthError(error_data.get("errors", "Authentication failed"))

        if response.status_code == 404:
            raise StoryblocksAssetNotFoundError(f"Resource not found: {resource}")

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            raise StoryblocksError(f"Storyblocks HTTP {response.status_code}: {response.text[:300]}") from exc
        data = response.json()
        if not isinstance(data, dict):
            raise StoryblocksError("Unexpected Storyblocks response type")
        return data

    def _identity_params(self, *, brand_id: str, locale: str, work_unit_id: str) -> dict[str, str]:
        return {
            "project_id": anonymize_project_id(work_unit_id),
            "user_id": anonymize_user_id(brand_id, locale),
        }

    @staticmethod
    def _drop_none(params: dict[str, Any]) -> dict[str, Any]:
        return {k: v for k, v in params.items() if v is not None and v != ""}

    def search_videos(
        self,
        query: str,
        *,
        brand_id: str,
        locale: str,
        work_unit_id: str,
        max_duration: int = 15,
        min_duration: int | None = None,
        page: int = 1,
        results_per_page: int = 50,
        required_keywords: str | None = None,
        filtered_keywords: str | None = None,
        content_type: str = "footage,motionbackgrounds",
        orientation: str | None = None,
        extended: str | None = None,
        has_talent_released: bool | None = None,
        safe_search: str = "true",
    ) -> dict[str, Any]:
        """Search — does NOT touch MAU ledger. CTQC kwargs from Lane 01."""
        params = self._drop_none(
            {
                "keywords": query,
                "min_duration": min_duration,
                "max_duration": max_duration,
                "content_type": content_type,
                "results_per_page": results_per_page,
                "page": page,
                "safe_search": safe_search,
                "required_keywords": required_keywords,
                "filtered_keywords": filtered_keywords,
                "orientation": orientation,
                "extended": extended,
                "has_talent_released": (
                    "true" if has_talent_released is True else "false" if has_talent_released is False else None
                ),
                **self._identity_params(brand_id=brand_id, locale=locale, work_unit_id=work_unit_id),
            }
        )
        return self._make_request("GET", "/api/v2/videos/search", params, rate_kind="search")

    def search_images(
        self,
        query: str,
        *,
        brand_id: str,
        locale: str,
        work_unit_id: str,
        page: int = 1,
        results_per_page: int = 50,
        required_keywords: str | None = None,
        filtered_keywords: str | None = None,
        orientation: str | None = None,
        extended: str | None = None,
        has_talent_released: bool | None = None,
        safe_search: str = "true",
    ) -> dict[str, Any]:
        """Search — does NOT touch MAU ledger."""
        params = self._drop_none(
            {
                "keywords": query,
                "results_per_page": results_per_page,
                "page": page,
                "safe_search": safe_search,
                "required_keywords": required_keywords,
                "filtered_keywords": filtered_keywords,
                "orientation": orientation,
                "extended": extended,
                "has_talent_released": (
                    "true" if has_talent_released is True else "false" if has_talent_released is False else None
                ),
                **self._identity_params(brand_id=brand_id, locale=locale, work_unit_id=work_unit_id),
            }
        )
        return self._make_request("GET", "/api/v2/images/search", params, rate_kind="search")

    def search_audio(
        self,
        query: str,
        *,
        brand_id: str,
        locale: str,
        work_unit_id: str,
        page: int = 1,
        results_per_page: int = 50,
        required_keywords: str | None = None,
        filtered_keywords: str | None = None,
        content_type: str = "music",
        min_bpm: int | None = None,
        max_bpm: int | None = None,
        has_vocals: bool | None = None,
        min_duration: int | None = None,
        max_duration: int | None = None,
        extended: str | None = None,
        safe_search: str = "true",
    ) -> dict[str, Any]:
        """Audio search (Lane 04 reuse). Does NOT touch MAU ledger."""
        params = self._drop_none(
            {
                "keywords": query,
                "content_type": content_type,
                "results_per_page": results_per_page,
                "page": page,
                "safe_search": safe_search,
                "required_keywords": required_keywords,
                "filtered_keywords": filtered_keywords,
                "min_bpm": min_bpm,
                "max_bpm": max_bpm,
                "has_vocals": (
                    "true" if has_vocals is True else "false" if has_vocals is False else None
                ),
                "min_duration": min_duration,
                "max_duration": max_duration,
                "extended": extended,
                **self._identity_params(brand_id=brand_id, locale=locale, work_unit_id=work_unit_id),
            }
        )
        return self._make_request("GET", "/api/v2/audio/search", params, rate_kind="search")

    def get_download_urls(
        self,
        stock_id: str,
        media_type: MediaType,
        *,
        brand_id: str,
        locale: str,
        work_unit_id: str,
    ) -> dict[str, Any]:
        """License-granting Download query (§A). Caller must MAU-meter first."""
        if media_type == "video":
            resource = f"/api/v2/videos/stock-item/download/{stock_id}"
        elif media_type == "image":
            resource = f"/api/v2/images/stock-item/download/{stock_id}"
        elif media_type == "audio":
            resource = f"/api/v2/audio/stock-item/download/{stock_id}"
        else:
            raise ValueError(f"unsupported media_type: {media_type}")
        params = self._identity_params(brand_id=brand_id, locale=locale, work_unit_id=work_unit_id)
        return self._make_request("GET", resource, params, rate_kind="download")


def pick_hd_url(download_payload: dict[str, Any], media_type: MediaType) -> tuple[str, str]:
    """Return (url, ext) preferring 1080p MP4 / largest image / WAV|MP3 audio."""
    if media_type == "video":
        for container, ext in (("MP4", "mp4"), ("MOV", "mov")):
            block = download_payload.get(container) or {}
            if isinstance(block, dict):
                for key in ("_1080p", "1080p", "_720p", "720p"):
                    url = block.get(key)
                    if url:
                        return str(url), ext
        raise StoryblocksError("No HD video URL in download payload")
    if media_type == "audio":
        for key, ext in (("WAV", "wav"), ("MP3", "mp3"), ("wav", "wav"), ("mp3", "mp3")):
            block = download_payload.get(key)
            if isinstance(block, str) and block.startswith("http"):
                return block, ext
            if isinstance(block, dict):
                for sub in ("_max", "max", "hq", "high", "url"):
                    url = block.get(sub)
                    if url:
                        return str(url), ext
        for key in ("url", "download_url", "preview_url"):
            if isinstance(download_payload.get(key), str):
                return str(download_payload[key]), "mp3"
        raise StoryblocksError("No HD audio URL in download payload")
    # images
    for key in ("JPG", "JPEG", "PNG", "jpg", "png"):
        block = download_payload.get(key)
        if isinstance(block, str) and block.startswith("http"):
            return block, "jpg" if "jp" in key.lower() else "png"
        if isinstance(block, dict):
            for sub in ("_max", "max", "large", "medium"):
                url = block.get(sub)
                if url:
                    return str(url), "jpg" if "jp" in key.lower() else "png"
    # common flat shapes
    for key in ("url", "download_url", "HD", "hd"):
        if isinstance(download_payload.get(key), str):
            return str(download_payload[key]), "jpg"
    raise StoryblocksError("No HD image URL in download payload")
