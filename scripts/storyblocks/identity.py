"""Anonymized Storyblocks user_id / project_id (EULA §2.1(iv)).

Q-SB-PP-02: identity scope = per locale brand.
Salt prefix is Pearl Prime (not 48social_user_).
"""

from __future__ import annotations

import hashlib

USER_SALT_PREFIX = "pearl_prime_user_"
PROJECT_SALT_PREFIX = "pearl_prime_project_"


def locale_brand_key(brand_id: str, locale: str) -> str:
    """Stable logical identity key for MAU + API user_id."""
    brand = (brand_id or "").strip()
    loc = (locale or "").strip()
    if not brand:
        raise ValueError("brand_id is required for Storyblocks identity")
    if not loc:
        raise ValueError("locale is required for Storyblocks identity")
    return f"{brand}:{loc}"


def anonymize_user_id(brand_id: str, locale: str) -> str:
    """SHA-256 hex truncated to 16 chars — stable for salt lifetime."""
    key = locale_brand_key(brand_id, locale)
    return hashlib.sha256(f"{USER_SALT_PREFIX}{key}".encode("utf-8")).hexdigest()[:16]


def anonymize_project_id(work_unit_id: str | int) -> str:
    """Anonymize work-unit / campaign id for Storyblocks project_id param."""
    wid = str(work_unit_id).strip()
    if not wid:
        raise ValueError("work_unit_id is required for Storyblocks project_id")
    return hashlib.sha256(f"{PROJECT_SALT_PREFIX}{wid}".encode("utf-8")).hexdigest()[:16]
