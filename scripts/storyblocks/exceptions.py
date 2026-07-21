"""Storyblocks integration exceptions."""

from __future__ import annotations


class StoryblocksError(Exception):
    """Base exception for Storyblocks integration errors."""


class StoryblocksConfigError(StoryblocksError):
    """Missing or invalid Storyblocks configuration / credentials."""


class StoryblocksAuthError(StoryblocksError):
    """HMAC authentication failed (typically HTTP 403)."""


class StoryblocksRateLimitError(StoryblocksError):
    """Client or upstream rate limit exceeded."""


class StoryblocksMauCapError(StoryblocksError):
    """Hard block: 105th distinct download identity in UTC calendar month."""


class StoryblocksAssetNotFoundError(StoryblocksError):
    """Upstream asset not found (HTTP 404)."""


class StoryblocksTimeoutError(StoryblocksError):
    """Upstream request timed out."""
