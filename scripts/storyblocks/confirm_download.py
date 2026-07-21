"""Sole HD download path for Pearl Prime Storyblocks (confirm-first).

Forbidden: pre-cache HD, shared pool, bulk prefetch, search-path downloads.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

import requests

from scripts.storyblocks.api_client import MediaType, StoryblocksAPIClient, pick_hd_url
from scripts.storyblocks.exceptions import StoryblocksConfigError, StoryblocksError
from scripts.storyblocks.identity import anonymize_user_id
from scripts.storyblocks.license_store import (
    LicenseRecord,
    LicenseStore,
    default_license_store,
    new_download_timestamp,
)
from scripts.storyblocks.mau_ledger import MauLedger, default_mau_ledger

logger = logging.getLogger(__name__)

# AI wall-off: HD bytes written here must never enter training/fine-tune datasets.
AI_TRAINING_WALL = (
    "Storyblocks Stock Files and metadata are excluded from AI/ML training export."
)


def confirm_selection(
    *,
    stock_id: str,
    media_type: MediaType,
    brand_id: str,
    locale: str,
    work_unit_id: str,
    work_unit_type: str = "social_campaign",
    surface: str = "social_broll",
    model_released: bool | None = None,
    property_released: bool | None = None,
    metadata: dict[str, Any] | None = None,
    client: StoryblocksAPIClient | None = None,
    mau_ledger: MauLedger | None = None,
    license_store: LicenseStore | None = None,
    http_get: Callable[..., Any] | None = None,
) -> LicenseRecord:
    """
    Confirm asset for a work unit: MAU → Download query → HD bank → license proof.

    This is the ONLY permitted HD download entry point.
    """
    store = license_store or default_license_store
    ledger = mau_ledger or default_mau_ledger
    existing = store.get(work_unit_id, stock_id)
    if existing and existing.local_uri and Path(existing.local_uri).exists():
        return existing

    api = client
    if api is None:
        try:
            api = StoryblocksAPIClient(require_keys=True)
        except StoryblocksConfigError:
            raise

    # R3 — downloads only
    mau = ledger.reserve_or_block(brand_id, locale)
    payload = api.get_download_urls(
        stock_id,
        media_type,
        brand_id=brand_id,
        locale=locale,
        work_unit_id=work_unit_id,
    )
    hd_url, ext = pick_hd_url(payload, media_type)
    dest = store.hd_path(work_unit_id, stock_id, ext)
    dest.parent.mkdir(parents=True, exist_ok=True)

    getter = http_get or requests.get
    resp = getter(hd_url, timeout=120)
    if getattr(resp, "status_code", 200) >= 400:
        raise StoryblocksError(f"HD fetch failed status={getattr(resp, 'status_code', '?')}")
    content = resp.content if hasattr(resp, "content") else resp.read()
    if not content:
        raise StoryblocksError("HD fetch returned empty body")
    dest.write_bytes(content)

    record = LicenseRecord(
        source_provider="storyblocks",
        storyblocks_stock_id=stock_id,
        work_unit_type=work_unit_type,
        work_unit_id=work_unit_id,
        brand_id=brand_id,
        locale=locale,
        surface=surface,
        media_type=media_type,
        mau_user_id=mau.user_id or anonymize_user_id(brand_id, locale),
        download_query_at=new_download_timestamp(),
        local_uri=str(dest.resolve()),
        model_released=model_released,
        property_released=property_released,
        metadata={
            **(metadata or {}),
            "ai_training_wall": AI_TRAINING_WALL,
            "attribution_label": "Stock media via Storyblocks",
        },
    )
    store.put(record)
    logger.info(
        "storyblocks.confirm_selection stock_id=%s work_unit=%s path=%s",
        stock_id,
        work_unit_id,
        dest,
    )
    return record
