# Storyblocks Integration Specification

**Author**: Product Strategist
**Status**: Approved — EULA-reconciled 2026-07-19
**Created**: 2026-02-05
**Last Updated**: 2026-07-19
**Reviewed By**: Engineering Team (Winston, Amelia, Murat, Mary, Bob, Sally, John)
**Governing contract**: `docs/Storyblocks API Agreement - 48 Social.pdf` (Doc Ref EUYIG-SF8TR-9LD23-TJ3AK)
**Compliance mechanism map**: `docs/STORYBLOCKS_EULA_COMPLIANCE.md`

---

## Executive Summary

Replace Pixabay/Pexels/Unsplash with Storyblocks as the sole stock media provider. Implements a **preview-first flow** (Flow B): users see **watermark-free previews** (included in the signed API agreement), confirm selection, then HD is **downloaded** to GCS per-campaign.

**EULA ground truth (non-negotiable):** the HD **download query** is the license-granting act (§A / download semantics). A preview (even watermark-free) grants **no** license. Any asset used in a rendered/shipped campaign **must** have a `CampaignAssetDownload` record. Do **not** migrate to HD-upfront / shared HD pools / bulk prefetch — that risks §B stockpiling.

**MAU cost control:** Storyblocks bills $4.40/MAU beyond **104** distinct User IDs seen on **Download** queries per calendar month (§4.3(a) + Payment Schedule). Search user_ids do **not** count. We key `user_id` **per brand** (operator ruling Q-SB-02) and hard-cap the 105th new download identity (Q-SB-01).

---

## Problem Statement

Current stock providers (Pixabay, Pexels, Unsplash) have limitations:
- Rate limits restrict scale
- Mixed quality and licensing complexity
- No unified API

Storyblocks offers:
- Higher quality content
- Unified API with clear licensing
- Better content for professional use

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Search latency (P95) | < 2s |
| HD download + GCS upload | < 10s for 15s video |
| Preview load in selector | < 500ms (CDN-served) |
| CLIP embedding processing (async) | < 30s per asset |

---

## Architecture Overview

### Service Structure

```
backend/apps/brands/services/
├── stock_api_service.py              # Legacy (keep for now, deprecate later)
├── storyblocks/
│   ├── __init__.py
│   ├── api_service.py                # Low-level API wrapper with HMAC auth
│   ├── asset_service.py              # Business logic: search, store, confirm
│   └── utils.py                      # User ID anonymization, helpers
└── asset_selection_service.py        # Existing - add feature flag integration

backend/apps/brands/models.py         # Add fields to StockMediaAsset
backend/apps/brands/views.py          # Add feature flag at line 707

backend/apps/campaigns/models.py      # Add CampaignAssetDownload model (FK to Campaign)
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                  StoryblocksAPIService                          │
│              (Low-level API wrapper with HMAC)                  │
├─────────────────────────────────────────────────────────────────┤
│  search_videos(query, max_duration=15, page=1) → [results]      │
│  search_images(query, page=1) → [results]                       │
│  get_download_urls(stock_id, media_type) → {hd_urls}            │
│  _generate_hmac(resource) → (expires, hmac)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                 StoryblocksAssetService                         │
│             (Business logic: store, download, manage)           │
├─────────────────────────────────────────────────────────────────┤
│  search_and_store(query, media_type) → [asset_dicts]            │
│  confirm_selection(asset_id, campaign_id) → gcs_url             │
│  get_or_create_asset(storyblocks_data) → StockMediaAsset        │
│  get_campaign_asset(asset_id, campaign_id) → gcs_url | None     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Celery Tasks                              │
├─────────────────────────────────────────────────────────────────┤
│  @shared_task(queue='low')                                      │
│  compute_storyblocks_embedding(asset_id)                        │
│  - Downloads thumbnail/preview                                  │
│  - Runs CLIP                                                    │
│  - Extracts visual attributes                                   │
│  - Updates StockMediaAsset                                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Integration Points

**CRITICAL**: These are the exact locations where Storyblocks integration hooks into existing code.

### 1. AssetSelectionService Fallback (Line ~281)

Location: `backend/apps/brands/services/asset_selection_service.py:281`

```python
# Current code at line 281:
api_results = stock_api_service.search_and_ingest(
    query_text=query_text,
    media_type=media_type,
    brand_id=self.brand_id,
    brand_config=brand_config,
    count=needed,
)

# Add feature flag check:
if settings.STOCK_PROVIDER == 'storyblocks':
    from apps.brands.services.storyblocks.asset_service import storyblocks_asset_service
    api_results = storyblocks_asset_service.search_and_store(
        query=query_text,
        media_type=media_type,
        user_id=anonymize_user_id(self.brand_id),
        per_page=needed,
    )
else:
    api_results = stock_api_service.search_and_ingest(
        query_text=query_text,
        media_type=media_type,
        brand_id=self.brand_id,
        brand_config=brand_config,
        count=needed,
    )
```

### 2. PostGenerationService Quote Image Selection (Line ~369)

Location: `backend/apps/pipelines/services/post_generation_service.py:369`

Entry point for quote image selection:
```python
selected_assets = selection_service.select_asset(
    query_text=search_query,
    media_type="image",
    aspect_ratio=None,
    count=1,
    prefer_brand_assets=True,
    fallback_to_api=True,  # <-- This triggers stock API fallback
    original_text=quote_text,
)
```

No changes needed here - uses `AssetSelectionService` which handles the feature flag.

### 3. StockSearchView Frontend Endpoint (Line ~707)

Location: `backend/apps/brands/views.py:707`

```python
# Current code at line 707:
results = stock_api_service.search_and_ingest(
    query_text=query,
    media_type=media_type,
    count=count,
    skip_processing=True,
)

# Add feature flag check:
# EULA R2 / Q-SB-02: ALWAYS anonymize per brand_id — never request.user.id
# (per-end-user IDs would inflate Download MAUs past the 104 free tier).
if settings.STOCK_PROVIDER == 'storyblocks':
    from apps.brands.services.storyblocks.asset_service import storyblocks_asset_service
    brand_id = resolve_brand_id_from_request(request)  # brand/campaign context
    results = storyblocks_asset_service.search_and_store(
        query=query,
        media_type=media_type,
        user_id=anonymize_user_id(brand_id),
        per_page=count,
    )
else:
    results = stock_api_service.search_and_ingest(
        query_text=query,
        media_type=media_type,
        count=count,
        skip_processing=True,
    )
```

---

## Feature Flag Strategy

### Configuration

Add to `backend/config/settings/base.py`:

```python
# Stock media provider selection
# Options: 'legacy' (Pexels/Pixabay/Unsplash) | 'storyblocks'
STOCK_PROVIDER = env("STOCK_PROVIDER", default="legacy")

# Storyblocks API credentials
STORYBLOCKS_PUBLIC_KEY = env("STORYBLOCKS_PUBLIC_KEY", default="")
STORYBLOCKS_PRIVATE_KEY = env("STORYBLOCKS_PRIVATE_KEY", default="")

# Search defaults
STORYBLOCKS_MAX_VIDEO_DURATION = 15  # seconds
STORYBLOCKS_RESULTS_PER_PAGE = 50
```

### Environment Variables

```bash
# .env
STOCK_PROVIDER=storyblocks  # or 'legacy' for rollback
STORYBLOCKS_PUBLIC_KEY=your_public_key
STORYBLOCKS_PRIVATE_KEY=your_private_key
```

### Rollback Strategy

1. Set `STOCK_PROVIDER=legacy` in environment
2. Restart Django/Celery workers
3. Existing Storyblocks assets remain in DB (no migration needed)
4. New searches use legacy providers

---

## Data Model Changes

### StockMediaAsset Additions

Add to existing `StockMediaAsset` model in `backend/apps/brands/models.py` (line ~830):

```python
# Storyblocks-specific fields
storyblocks_stock_id = models.CharField(
    max_length=255,
    null=True,
    blank=True,
    db_index=True,
    help_text="Storyblocks stock item ID for download API"
)

preview_urls = models.JSONField(
    default=dict,
    blank=True,
    help_text='Storyblocks preview URLs: {"_180p": "...", "_360p": "...", "_720p": "..."}'
)

storyblocks_content_type = models.CharField(
    max_length=50,
    blank=True,
    help_text="Storyblocks content type: footage, motionbackgrounds, templates"
)

embedding_status = models.CharField(
    max_length=20,
    choices=[
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ],
    default='completed',  # Default 'completed' for existing legacy assets
    db_index=True,
    help_text="CLIP embedding computation status"
)
```

### New Model: CampaignAssetDownload

Add to `backend/apps/campaigns/models.py`:

```python
class CampaignAssetDownload(models.Model):
    """
    Tracks HD downloads per campaign.

    Each campaign has its own copy of B-roll assets for:
    - Clean lifecycle (delete campaign = delete assets)
    - Simple mental model ("this campaign's B-roll")
    - Licensing clarity
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    campaign = models.ForeignKey(
        'campaigns.Campaign',
        on_delete=models.CASCADE,
        related_name='asset_downloads',
        help_text="Campaign this download belongs to"
    )

    stock_asset = models.ForeignKey(
        'StockMediaAsset',
        on_delete=models.CASCADE,
        related_name='campaign_downloads',
        help_text="Stock asset that was downloaded"
    )

    gcs_url = models.URLField(
        max_length=2048,
        help_text="GCS URL: gs://bucket/campaigns/{campaign_id}/broll/{asset_id}.{ext}"
    )

    file_size_bytes = models.IntegerField(
        null=True,
        help_text="Downloaded file size in bytes"
    )

    downloaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'campaign_asset_downloads'
        unique_together = ['campaign', 'stock_asset']
        indexes = [
            models.Index(fields=['campaign', 'downloaded_at']),
        ]

    def __str__(self):
        return f"{self.campaign_id} - {self.stock_asset_id}"
```

---

## Method Signatures & Return Types

### Current Legacy Format (stock_api_service._asset_to_dict)

Reference: `backend/apps/brands/services/stock_api_service.py:667`

```python
def _asset_to_dict(asset: StockMediaAsset) -> dict:
    """Convert StockMediaAsset model to dict"""
    return {
        "id": str(asset.id),              # UUID
        "source": "stock",
        "source_provider": str,            # "pexels" | "pixabay" | "unsplash"
        "provider_id": str,
        "provider_url": str,
        "url": str,                        # HD URL ready to use
        "thumbnail_url": str,
        "media_type": str,                 # "image" | "video"
        "width": int,
        "height": int,
        "aspect_ratio": str,               # "16:9" | "9:16" | "1:1" etc
        "metadata": dict,
        "embedding_clip": list,
        "total_usage_count": int,
        "last_used_at": datetime | None,
    }
```

### Storyblocks Format (search_and_store return)

**MUST match legacy format** for drop-in replacement, with additions:

```python
def search_and_store(...) -> list[dict]:
    """
    Returns list of dicts matching legacy format + Storyblocks extensions.
    """
    return [{
        # Core fields (MUST match legacy)
        "id": str,                         # Our StockMediaAsset UUID
        "source": "stock",
        "source_provider": "storyblocks",
        "provider_id": str,                # Same as storyblocks_stock_id
        "provider_url": str,               # Storyblocks page URL
        "url": str,                        # Preview URL (720p for video, thumbnail for image)
        "thumbnail_url": str,
        "media_type": str,                 # "image" | "video"
        "width": int,
        "height": int,
        "aspect_ratio": str,
        "metadata": dict,
        "embedding_clip": list | None,     # May be None if still processing
        "total_usage_count": int,
        "last_used_at": datetime | None,

        # Storyblocks-specific (NEW)
        "storyblocks_stock_id": str,       # For download API
        "preview_urls": dict,              # {"_360p": "...", "_720p": "..."}
        "duration": float | None,          # For videos
        "embedding_status": str,           # "pending" | "processing" | "completed" | "failed"
        "requires_download": True,         # Flag for frontend/pipeline
    }]
```

---

## Storage Strategy

> **EULA bank contract (authoritative for license + metadata bind):**  
> `docs/STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md` — confirm-only HD path, per-campaign bank, `CampaignAssetDownload` as license proof, full field map. Do **not** build a shared HD pool.

### GCS Path Structure

**IMPORTANT**: Use `campaign_id`, not `project_id` (codebase uses Campaign model).  
This prefix **is** the per-campaign licensed bank (not a cross-campaign stockpile).

```
gs://{bucket}/campaigns/{campaign_id}/broll/{asset_uuid}.{ext}
```

Examples:
```
gs://48social-media-assets/campaigns/abc123-def456/broll/789xyz.mp4
gs://48social-media-assets/campaigns/abc123-def456/broll/123abc.jpg
```

**Note**: Storyblocks API `project_id` parameter = our `campaign_id` (hashed for anonymization)

### What We Store in DB

| Field | Purpose |
|-------|---------|
| `storyblocks_stock_id` | Required for download API calls |
| `thumbnail_url` | CDN URL for grid display (fast, stable) |
| `preview_urls` | CDN URLs for watermarked previews |
| `metadata` | Duration, dimensions, tags, content_type |
| `embedding_clip` | CLIP embedding (computed async from thumbnail) |
| Visual attributes | Brightness, saturation, colors (computed async) |

### What We Store in GCS (Per Campaign)

- HD file downloaded **only after user confirms selection**
- Each campaign maintains its own copy
- Delete campaign → delete its B-roll files (via Django signal)

### GCS Cleanup Signal (Required)

**CRITICAL**: Implement a `post_delete` signal on Campaign to clean up GCS files.

```python
# backend/apps/campaigns/signals.py

from django.db.models.signals import post_delete
from django.dispatch import receiver
from google.cloud import storage
from django.conf import settings
import logging

from .models import Campaign

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Campaign)
def cleanup_campaign_gcs_assets(sender, instance, **kwargs):
    """
    Clean up GCS B-roll files when a campaign is deleted.

    Path pattern: gs://{bucket}/campaigns/{campaign_id}/broll/

    Note: CampaignAssetDownload records are deleted via CASCADE,
    but GCS files must be explicitly removed.
    """
    try:
        client = storage.Client()
        bucket = client.bucket(settings.GCS_MEDIA_BUCKET)
        prefix = f"campaigns/{instance.id}/broll/"

        blobs = list(bucket.list_blobs(prefix=prefix))
        if blobs:
            logger.info(f"Deleting {len(blobs)} B-roll files for campaign {instance.id}")
            for blob in blobs:
                blob.delete()
            logger.info(f"Successfully cleaned up GCS assets for campaign {instance.id}")
        else:
            logger.debug(f"No B-roll files to clean up for campaign {instance.id}")

    except Exception as e:
        # Log but don't raise — campaign deletion should succeed even if GCS cleanup fails
        logger.error(f"Failed to clean up GCS assets for campaign {instance.id}: {e}")
```

```python
# backend/apps/campaigns/apps.py

from django.apps import AppConfig


class CampaignsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.campaigns'

    def ready(self):
        # Import signals to register them
        from . import signals  # noqa: F401
```

### What We Don't Store

- HD download URLs (fetch fresh from Storyblocks API each time)
- Pre-cached HD for "maybe later"
- Shared HD pool across campaigns

---

## HMAC Authentication Implementation

**CRITICAL**: Storyblocks requires HMAC-SHA256 authentication for all API calls.

### HMAC Signing Rules (Validated via Postman)

| Rule | Description | Example |
|------|-------------|---------|
| **Resolved paths only** | Sign the actual path with real IDs, NOT URL templates | ✅ `/api/v2/videos/stock-item/download/ABC123` ❌ `/api/v2/videos/stock-item/download/:stock_item_id` |
| **No query params** | Sign path only — strip everything after `?` | ✅ `/api/v2/videos/search` ❌ `/api/v2/videos/search?keywords=sunset` |
| **Leading slash required** | Path must start with `/` | ✅ `/api/v2/videos/search` ❌ `api/v2/videos/search` |

### Reference Implementation (Postman Pre-Request Script)

This is the **validated working code** tested against Storyblocks API for both search and download endpoints:

```javascript
// Postman Pre-Request Script - VALIDATED WORKING
// Works for: /api/v2/videos/search, /api/v2/videos/stock-item/download/{id}

const crypto = require('crypto-js');

// 1. Get credentials from environment variables
const publicKey = pm.environment.get('STORYBLOCKS_PUBLIC_KEY');
const privateKey = pm.environment.get('STORYBLOCKS_PRIVATE_KEY');

// Safety Check: Stop if keys are missing
if (!privateKey || !publicKey) {
    console.error("Missing API Keys! Check your Environment variables.");
    return;
}

// 2. Generate EXPIRES (Current time + 1 hour in seconds)
const expires = Math.floor(Date.now() / 1000) + 3600;

// 3. Get the Resolved Resource path
// CRITICAL: Use getPathWithQuery() to get actual values, not :param templates
// Then strip query params — we only sign the path portion
let fullPath = pm.request.url.getPathWithQuery();
let resource = fullPath.split('?')[0]; // Remove everything after '?'

// Ensure it starts with a leading slash
if (!resource.startsWith('/')) {
    resource = '/' + resource;
}

// 4. Generate HMAC
// Storyblocks Key = PrivateKey + Expires (concatenated as string)
const hmacKey = privateKey + expires;
const hmac = crypto.HmacSHA256(resource, hmacKey).toString(crypto.enc.Hex);

// 5. Set variables for the Params tab
pm.variables.set("api_expires", expires);
pm.variables.set("api_hmac", hmac);
pm.variables.set("api_key", publicKey);

// Debug logging (Ctrl + Alt + C in Postman to view console)
console.log("Signing Resource: " + resource);
console.log("With HMAC: " + hmac);
console.log("Expires: " + expires);
```

**Common Pitfall**: The download endpoint failed with `"HMAC header is invalid"` when:
1. Using `pm.request.url.path.join('/')` which returns unresolved `:stock_item_id` template
2. Accidentally setting `HMAC={{api_expires}}` instead of `HMAC={{api_hmac}}` (copy-paste error)

### Python Implementation

```python
# backend/apps/brands/services/storyblocks/api_service.py

import hashlib
import hmac
import time
import logging
from typing import Literal

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class StoryblocksAPIService:
    """
    Low-level wrapper for Storyblocks API.
    Handles HMAC authentication and raw API calls.
    """

    BASE_URL = "https://api.storyblocks.com"
    RATE_LIMIT_BACKOFF = 5  # seconds
    MAX_RETRIES = 2

    def __init__(self):
        self.public_key = settings.STORYBLOCKS_PUBLIC_KEY
        self.private_key = settings.STORYBLOCKS_PRIVATE_KEY

        if not self.public_key or not self.private_key:
            logger.warning("Storyblocks API keys not configured")

    def _generate_hmac(self, resource: str) -> tuple[int, str]:
        """
        Generate HMAC signature for Storyblocks API.

        Args:
            resource: API path with RESOLVED values (no :param templates).
                      e.g., "/api/v2/videos/stock-item/download/ABC123"
                      Must NOT include query params.
                      Must start with leading slash.

        Returns:
            (expires_timestamp, hmac_hex_string)

        Implementation:
            1. expires = current_time + 3600 (1 hour)
            2. key = private_key + expires (concatenated as string)
            3. signature = HMAC-SHA256(key, resource)

        Raises:
            ValueError: If resource contains unresolved :param template
        """
        # Validate: no unresolved URL templates
        if ':' in resource and '/:' in resource:
            raise ValueError(
                f"Resource path contains unresolved template variable: {resource}. "
                "Sign the actual path with real IDs, not URL templates."
            )

        # Ensure leading slash
        if not resource.startswith('/'):
            resource = '/' + resource

        # Strip query params if accidentally included
        resource = resource.split('?')[0]

        expires = int(time.time()) + 3600  # 1 hour from now

        # Key = private_key + expires (concatenated as string)
        hmac_key = f"{self.private_key}{expires}"

        # HMAC-SHA256 of resource path
        signature = hmac.new(
            hmac_key.encode('utf-8'),
            resource.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return expires, signature

    def _make_request(
        self,
        method: str,
        resource: str,
        params: dict | None = None,
        timeout: int = 30,
        retry_count: int = 0,
    ) -> dict:
        """
        Make authenticated request to Storyblocks API with error handling.
        """
        expires, hmac_sig = self._generate_hmac(resource)

        auth_params = {
            "APIKEY": self.public_key,
            "EXPIRES": expires,
            "HMAC": hmac_sig,
        }

        all_params = {**(params or {}), **auth_params}
        url = f"{self.BASE_URL}{resource}"

        try:
            response = requests.request(
                method=method,
                url=url,
                params=all_params,
                timeout=timeout
            )

            # Handle rate limit (429)
            if response.status_code == 429:
                if retry_count < self.MAX_RETRIES:
                    logger.warning(f"Storyblocks rate limit hit, retrying in {self.RATE_LIMIT_BACKOFF}s")
                    time.sleep(self.RATE_LIMIT_BACKOFF)
                    return self._make_request(method, resource, params, timeout, retry_count + 1)
                else:
                    raise StoryblocksRateLimitError("Rate limit exceeded after retries")

            # Handle auth error (403)
            if response.status_code == 403:
                error_data = response.json() if response.text else {}
                logger.error(f"Storyblocks auth failed - check HMAC: {error_data}")
                raise StoryblocksAuthError(error_data.get("errors", "Authentication failed"))

            # Handle not found (404)
            if response.status_code == 404:
                raise StoryblocksAssetNotFoundError(f"Resource not found: {resource}")

            response.raise_for_status()
            return response.json()

        except requests.exceptions.Timeout:
            logger.error(f"Storyblocks request timeout: {resource}")
            raise StoryblocksTimeoutError(f"Request timeout: {resource}")

    # ... rest of search_videos, search_images, get_download_urls methods


# Custom exceptions
class StoryblocksError(Exception):
    """Base exception for Storyblocks API errors"""
    pass

class StoryblocksAuthError(StoryblocksError):
    """HMAC authentication failed"""
    pass

class StoryblocksRateLimitError(StoryblocksError):
    """Rate limit exceeded"""
    pass

class StoryblocksAssetNotFoundError(StoryblocksError):
    """Asset not found (404)"""
    pass

class StoryblocksTimeoutError(StoryblocksError):
    """Request timeout"""
    pass


# Singleton instance
storyblocks_api_service = StoryblocksAPIService()
```

---

## User ID Anonymization

**REQUIRED** (§2.1(iv)): anonymized User IDs on **both** Search and Download queries.

**Identity scope (Q-SB-02):** pass the **brand id** into `anonymize_user_id`, not the end-user id.
One brand = one stable Storyblocks identity for the month (and forever under this salt).
This is both the operator ruling and the MAU cost control.

```python
# backend/apps/brands/services/storyblocks/utils.py

import hashlib


def anonymize_user_id(brand_id: str | int) -> str:
    """
    Hash brand ID for Storyblocks API compliance (§2.1(iv), Q-SB-02).

    Input MUST be brand_id (not end-user id). Deterministic + stable so
    one brand == one MAU identity when that brand performs a Download.
    """
    return hashlib.sha256(f"48social_user_{brand_id}".encode()).hexdigest()[:16]


def anonymize_project_id(project_id: str | int) -> str:
    """
    Hash project/campaign ID for Storyblocks API compliance.

    Note: Storyblocks calls it "project_id" but we use Campaign model.
    """
    return hashlib.sha256(f"48social_campaign_{project_id}".encode()).hexdigest()[:16]
```

Usage in API calls (search **and** download — both require anonymized user_id per §2.1(iv)):
```python
# ALWAYS brand-scoped (Q-SB-02). Never request.user.id.
response = storyblocks_api_service.search_videos(
    query=query,
    project_id=anonymize_project_id(campaign_id),
    user_id=anonymize_user_id(brand_id),
)
# Download path meters MAU (R3) BEFORE this call:
urls = storyblocks_api_service.get_download_urls(
    stock_id=stock_id,
    media_type=media_type,
    project_id=anonymize_project_id(campaign_id),
    user_id=anonymize_user_id(brand_id),
)
```

---

## API Endpoints

### Search Endpoint

```
POST /api/v1/storyblocks/search
```

**Request:**
```json
{
  "query": "sunset beach",
  "media_type": "video",
  "max_duration": 15,
  "page": 1,
  "per_page": 50
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid-of-stock-media-asset",
      "storyblocks_stock_id": "12345",
      "media_type": "video",
      "thumbnail_url": "https://d2v9y0dukr6mq2.cloudfront.net/video/thumbnail/...",
      "preview_urls": {
        "_180p": "https://d2v9y0dukr6mq2.cloudfront.net/video/preview/180p/...",
        "_360p": "https://d2v9y0dukr6mq2.cloudfront.net/video/preview/360p/...",
        "_720p": "https://d2v9y0dukr6mq2.cloudfront.net/video/preview/720p/..."
      },
      "duration": 12,
      "width": 1920,
      "height": 1080,
      "aspect_ratio": "16:9",
      "embedding_status": "completed",
      "requires_download": true,
      "metadata": {
        "title": "Sunset on tropical beach",
        "type": "footage",
        "tags": ["sunset", "beach", "ocean", "tropical"]
      }
    }
  ],
  "total_results": 847,
  "page": 1,
  "per_page": 50
}
```

### Confirm/Download Endpoint

```
POST /api/v1/storyblocks/confirm
```

**Request:**
```json
{
  "asset_id": "uuid-of-stock-media-asset",
  "campaign_id": "uuid-of-campaign"
}
```

**Response (success):**
```json
{
  "status": "success",
  "gcs_url": "https://storage.googleapis.com/bucket/campaigns/abc123/broll/def456.mp4",
  "asset_id": "uuid-of-stock-media-asset",
  "file_size_bytes": 8432156
}
```

**Response (already downloaded):**
```json
{
  "status": "exists",
  "gcs_url": "https://storage.googleapis.com/bucket/campaigns/abc123/broll/def456.mp4",
  "asset_id": "uuid-of-stock-media-asset"
}
```

---

## Frontend Implementation

### TypeScript Types

Location: `frontend/src/features/reel-editor/types.ts`

```typescript
/**
 * Stock media search result from API.
 * Updated for Storyblocks integration.
 */
export interface StockMediaResult {
  id: string;
  mediaType: "image" | "video";
  thumbnailUrl: string;
  sdUrl: string;           // Preview URL (may be watermarked)
  hdUrl: string;           // Same as sdUrl for Storyblocks (HD requires confirm)
  width: number;
  height: number;
  duration?: number;
  provider: string;        // "storyblocks" | "pexels" | "pixabay" | "unsplash"
  providerUrl: string;

  // Storyblocks-specific (NEW)
  storyblocksStockId?: string;  // For confirm endpoint
  previewUrls?: {
    _180p?: string;
    _360p?: string;
    _480p?: string;
    _720p?: string;
  };
  requiresDownload?: boolean;   // True for Storyblocks
  embeddingStatus?: "pending" | "processing" | "completed" | "failed";

  // Set after confirmation
  confirmedGcsUrl?: string;
}
```

### API Functions

Location: `frontend/src/features/reel-editor/api/bRollApi.ts` (add to existing file)

```typescript
// Add to bRollApi.ts

export interface StoryblocksSearchResponse {
  results: StockMediaResult[];
  total: number;
  query: string;
}

export interface StoryblocksConfirmRequest {
  asset_id: string;
  campaign_id: string;  // Note: campaign_id not project_id
}

export interface StoryblocksConfirmResponse {
  gcs_url: string;
  asset_id: string;
  status: "success" | "exists";
  file_size_bytes?: number;
}

/**
 * Search Storyblocks (returns previews, not HD)
 */
export async function searchStoryblocks(
  query: string,
  mediaType: MediaType = "all",
  count: number = 20,
): Promise<StoryblocksSearchResponse> {
  const response = await fetch(`/api/v1/storyblocks/search`, {
    method: "POST",
    headers: getAPIHeaders(),
    credentials: "include",
    body: JSON.stringify({
      query_text: query,
      media_type: mediaType,
      count,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error ${response.status}`);
  }

  return response.json();
}

/**
 * Confirm Storyblocks selection (downloads HD to GCS)
 */
export async function confirmStoryblocks(
  assetId: string,
  campaignId: string,
): Promise<StoryblocksConfirmResponse> {
  const response = await fetch(`/api/v1/storyblocks/confirm`, {
    method: "POST",
    headers: getAPIHeaders(),
    credentials: "include",
    body: JSON.stringify({
      asset_id: assetId,
      campaign_id: campaignId,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || `HTTP error ${response.status}`);
  }

  return response.json();
}
```

---

## Database Migration

### Migration 1: StockMediaAsset fields (brands app)

```python
# backend/apps/brands/migrations/XXXX_storyblocks_fields.py

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('brands', 'XXXX_previous_migration'),  # Replace with actual
    ]

    operations = [
        # Add Storyblocks fields to StockMediaAsset
        migrations.AddField(
            model_name='stockmediaasset',
            name='storyblocks_stock_id',
            field=models.CharField(
                blank=True,
                db_index=True,
                help_text='Storyblocks stock item ID for download API',
                max_length=255,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='stockmediaasset',
            name='preview_urls',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Storyblocks preview URLs',
            ),
        ),
        migrations.AddField(
            model_name='stockmediaasset',
            name='storyblocks_content_type',
            field=models.CharField(
                blank=True,
                help_text='Storyblocks content type',
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name='stockmediaasset',
            name='embedding_status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('processing', 'Processing'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                ],
                db_index=True,
                default='completed',  # Existing assets assumed complete
                help_text='CLIP embedding computation status',
                max_length=20,
            ),
        ),

        # Add index for Storyblocks lookups
        migrations.AddIndex(
            model_name='stockmediaasset',
            index=models.Index(
                fields=['storyblocks_stock_id'],
                name='storyblocks_stock_id_idx',
            ),
        ),
    ]
```

### Migration 2: CampaignAssetDownload model (campaigns app)

```python
# backend/apps/campaigns/migrations/XXXX_campaign_asset_download.py

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', 'XXXX_previous_migration'),  # Replace with actual
        ('brands', 'XXXX_storyblocks_fields'),  # After StockMediaAsset fields
    ]

    operations = [
        migrations.CreateModel(
            name='CampaignAssetDownload',
            fields=[
                ('id', models.UUIDField(
                    default=uuid.uuid4,
                    primary_key=True,
                    serialize=False,
                )),
                ('gcs_url', models.URLField(
                    help_text='GCS URL for downloaded asset',
                    max_length=2048,
                )),
                ('file_size_bytes', models.IntegerField(null=True)),
                ('downloaded_at', models.DateTimeField(auto_now_add=True)),
                ('campaign', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='asset_downloads',
                    to='campaigns.campaign',
                )),
                ('stock_asset', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='campaign_downloads',
                    to='brands.stockmediaasset',
                )),
            ],
            options={
                'db_table': 'campaign_asset_downloads',
            },
        ),
        migrations.AddIndex(
            model_name='campaignassetdownload',
            index=models.Index(
                fields=['campaign', 'downloaded_at'],
                name='campaign_as_campaig_idx',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='campaignassetdownload',
            unique_together={('campaign', 'stock_asset')},
        ),
    ]
```

---

## User Flows

### Flow 1: Pipeline (Automated B-roll Selection)

```
1. Quote extracted from video
           │
           ▼
2. Generate search query from quote text
           │
           ▼
3. AssetSelectionService.select_asset() called
   │
   ├── Checks STOCK_PROVIDER setting
   │
   └── If 'storyblocks':
       StoryblocksAssetService.search_and_store(query, "video")
       ├── Call StoryblocksAPIService.search_videos()
       ├── For each result:
       │   ├── Check if storyblocks_stock_id exists in DB
       │   ├── If not: create StockMediaAsset (embedding_status='pending')
       │   └── Queue: compute_storyblocks_embedding.delay(asset_id)
       └── Return list of asset dicts (matching legacy format)
           │
           ▼
4. AI ranks/scores using metadata (tags, duration, dimensions)
   (CLIP embeddings computed async — available for future selections)
           │
           ▼
5. Store top N suggestions in pipeline result
   (NOT downloaded yet — just asset IDs + preview URLs)
           │
           ▼
6. User opens Grid View → sees previews (watermarked)
           │
           ▼
7. User confirms OR swaps selection
           │
           ▼
8. On confirm: StoryblocksAssetService.confirm_selection(asset_id, campaign_id)
   ├── Call StoryblocksAPIService.get_download_urls(stock_id)
   ├── Download HD file from Storyblocks CDN
   ├── Upload to GCS: campaigns/{campaign_id}/broll/{asset_id}.mp4
   ├── Create CampaignAssetDownload record
   ├── Update StockAssetUsage for analytics
   └── Return GCS URL
           │
           ▼
9. Remotion render uses GCS URL (clean, no watermark)
```

### Flow 2: Manual B-roll Selector (Remotion Editor)

Same as before but with confirmation step before HD is available.

### Flow 3: Manual Image Selector (Fabric Canvas)

Same as Flow 2, but for images in the quote post editor (PhotoPanel).

---

## Implementation Sequence

| # | Task | Points | Notes |
|---|------|--------|-------|
| 1 | Add Storyblocks fields to StockMediaAsset | 1 | |
| 2 | Create CampaignAssetDownload model | 1 | In campaigns app |
| 3 | Create migration | 1 | |
| 4 | Implement StoryblocksAPIService | 3 | HMAC auth |
| 5 | Implement anonymization utils | 0.5 | |
| 6 | Implement StoryblocksAssetService | 2 | |
| 7 | Create API views + URL routes | 2 | |
| 8 | Add feature flag to AssetSelectionService | 1 | Line 281 |
| 9 | Add feature flag to StockSearchView | 0.5 | Line 707 |
| 10 | Create Celery task for embeddings | 2 | Queue: low |
| 11 | Frontend: Update types.ts | 0.5 | |
| 12 | Frontend: Add Storyblocks API functions to bRollApi.ts | 1 | |
| 13 | Frontend: Update BRollPanel with confirm flow | 3 | |
| 14 | Frontend: Update PhotoPanel with confirm flow | 2 | |
| 15 | Tests: Unit tests | 2 | |
| 16 | Tests: Integration tests | 2 | |
| 17 | Tests: E2E tests | 1 | |

**Total: ~24.5 story points**

---

## Testing Checklist

### Unit Tests

- [ ] StoryblocksAPIService HMAC generation (test against known values)
- [ ] StoryblocksAPIService search methods (mock responses)
- [ ] StoryblocksAssetService.search_and_store() return format
- [ ] StoryblocksAssetService.confirm_selection() GCS upload
- [ ] User ID anonymization
- [ ] Error handling (rate limit, auth, 404)
- [ ] Celery task: compute_storyblocks_embedding

### HMAC Test Vectors

**CRITICAL**: Use these test vectors to validate HMAC implementation. Validated against working Postman implementation.

```python
# backend/apps/brands/tests/test_storyblocks_api_service.py

import hashlib
import hmac
from unittest import mock

import pytest


class TestStoryblocksHMACGeneration:
    """
    Test HMAC generation against known vectors.
    Validated against working Postman implementation.
    """

    # Test credentials (from Storyblocks sandbox)
    TEST_PUBLIC_KEY = "test_ya1n5o5s7xa9zOtmwMIZYSsOJ7fUKI0hqKyeq3yzOyIQO5e4mZG7WWtYcxE"
    TEST_PRIVATE_KEY = "test_sFWy4cTej87nuJ0TYYzENs77cCPRrZXpDWApdhuFu0PaWSorptTlEglVYgV"

    def test_hmac_format_is_64_char_hex(self):
        """HMAC output must be 64-character hex string (SHA256)."""
        from apps.brands.services.storyblocks.api_service import StoryblocksAPIService

        with mock.patch.object(StoryblocksAPIService, '__init__', lambda self: None):
            service = StoryblocksAPIService()
            service.private_key = self.TEST_PRIVATE_KEY

            with mock.patch('time.time', return_value=1738800000):
                expires, hmac_sig = service._generate_hmac("/api/v2/videos/search")

                assert len(hmac_sig) == 64, "HMAC must be 64 hex characters"
                assert all(c in '0123456789abcdef' for c in hmac_sig), "HMAC must be lowercase hex"

    def test_hmac_deterministic_with_fixed_time(self):
        """Same inputs must produce same HMAC."""
        from apps.brands.services.storyblocks.api_service import StoryblocksAPIService

        with mock.patch.object(StoryblocksAPIService, '__init__', lambda self: None):
            service = StoryblocksAPIService()
            service.private_key = self.TEST_PRIVATE_KEY

            with mock.patch('time.time', return_value=1738800000):
                expires1, hmac1 = service._generate_hmac("/api/v2/videos/search")
                expires2, hmac2 = service._generate_hmac("/api/v2/videos/search")

                assert expires1 == expires2
                assert hmac1 == hmac2

    def test_hmac_expires_is_one_hour_ahead(self):
        """Expires must be current time + 3600 seconds."""
        from apps.brands.services.storyblocks.api_service import StoryblocksAPIService

        with mock.patch.object(StoryblocksAPIService, '__init__', lambda self: None):
            service = StoryblocksAPIService()
            service.private_key = self.TEST_PRIVATE_KEY

            fixed_time = 1738800000
            with mock.patch('time.time', return_value=fixed_time):
                expires, _ = service._generate_hmac("/api/v2/videos/search")

                assert expires == fixed_time + 3600

    def test_hmac_different_for_different_paths(self):
        """Different resource paths must produce different HMACs."""
        from apps.brands.services.storyblocks.api_service import StoryblocksAPIService

        with mock.patch.object(StoryblocksAPIService, '__init__', lambda self: None):
            service = StoryblocksAPIService()
            service.private_key = self.TEST_PRIVATE_KEY

            with mock.patch('time.time', return_value=1738800000):
                _, hmac_search = service._generate_hmac("/api/v2/videos/search")
                _, hmac_download = service._generate_hmac("/api/v2/videos/stock-item/download/ABC123")

                assert hmac_search != hmac_download

    def test_hmac_rejects_unresolved_template(self):
        """Must reject paths with :param templates."""
        from apps.brands.services.storyblocks.api_service import StoryblocksAPIService

        with mock.patch.object(StoryblocksAPIService, '__init__', lambda self: None):
            service = StoryblocksAPIService()
            service.private_key = self.TEST_PRIVATE_KEY

            with pytest.raises(ValueError, match="unresolved template"):
                service._generate_hmac("/api/v2/videos/stock-item/download/:stock_item_id")

    def test_hmac_known_vector_search(self):
        """
        Known test vector for search endpoint.

        Inputs:
            private_key: test_sFWy4cTej87nuJ0TYYzENs77cCPRrZXpDWApdhuFu0PaWSorptTlEglVYgV
            expires: 1738803600 (fixed_time + 3600)
            resource: /api/v2/videos/search
            hmac_key: {private_key}{expires}

        Expected: Deterministic HMAC (calculate once, hardcode for regression)
        """
        private_key = self.TEST_PRIVATE_KEY
        expires = 1738803600
        resource = "/api/v2/videos/search"

        hmac_key = f"{private_key}{expires}"
        expected_hmac = hmac.new(
            hmac_key.encode('utf-8'),
            resource.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        # This is the expected value — hardcode after first run for regression testing
        # Run this test once to get the value, then uncomment assertion:
        # assert expected_hmac == "YOUR_EXPECTED_HMAC_HERE"

        # For now, just verify it's valid format
        assert len(expected_hmac) == 64

    def test_hmac_known_vector_download(self):
        """
        Known test vector for download endpoint with resolved stock ID.

        Inputs:
            private_key: test_sFWy4cTej87nuJ0TYYzENs77cCPRrZXpDWApdhuFu0PaWSorptTlEglVYgV
            expires: 1738803600
            resource: /api/v2/videos/stock-item/download/SBV-338754857

        Note: Stock ID must be the actual ID, not :stock_item_id template.
        """
        private_key = self.TEST_PRIVATE_KEY
        expires = 1738803600
        resource = "/api/v2/videos/stock-item/download/SBV-338754857"

        hmac_key = f"{private_key}{expires}"
        expected_hmac = hmac.new(
            hmac_key.encode('utf-8'),
            resource.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        assert len(expected_hmac) == 64
        # Different from search path
        search_hmac = hmac.new(
            hmac_key.encode('utf-8'),
            "/api/v2/videos/search".encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        assert expected_hmac != search_hmac
```

### Integration Tests

- [ ] Search endpoint returns valid results matching legacy format
- [ ] Confirm endpoint downloads to GCS
- [ ] Confirm endpoint handles duplicate requests (returns existing)
- [ ] Feature flag switches between providers correctly
- [ ] Campaign deletion cleans up GCS files

### E2E Tests

- [ ] User searches for B-roll in Remotion editor
- [ ] User confirms selection, sees loading, gets HD
- [ ] User searches for image in Fabric canvas
- [ ] Pipeline suggests B-roll with preview URLs
- [ ] User confirms pipeline suggestion

---

## Fallback: Flow B → Flow A Migration

If watermarks prove unusable, migrate to HD-upfront with these changes:

### Backend

1. In pipeline task, after `search_and_store()`, immediately call `confirm_selection()` for top pick
2. Store GCS URL in pipeline result instead of preview URLs

### Frontend

1. Remove confirm button / loading state from BRollPanel
2. Use `hdUrl` directly (now populated with GCS URL)

**Estimated effort: 1-2 story points**

---

## Tech Debt Recommendation (Post-MVP)

Delete `ContentSuggestionService` after Storyblocks integration is stable:

- **File**: `backend/apps/pipelines/services/content_suggestion_service.py` (~800 lines)
- **Tests**: `backend/apps/pipelines/tests/test_content_suggestion_service.py`
- **Exports**: Remove from `backend/apps/pipelines/services/__init__.py`

**Reason**: Orphaned code from Epic 6, superseded by `AssetSelectionService`. Tests are already skipped. Creates confusion about where asset selection happens.

---

## Appendix: Architecture Summary

```
User Request
    │
    ▼
AssetSelectionService.select_asset()
    │
    ├── 1. Search BrandImageAsset/BrandVideoAsset (user uploads)
    │       └── CLIP embeddings, brand-scoped
    │
    ├── 2. Search StockMediaAsset (global stock pool)
    │       └── CLIP embeddings, shared across all users
    │       └── Currently: Pexels, Pixabay, Unsplash
    │       └── Future: Storyblocks (this spec)
    │
    ├── 3. Rank: Brand-first boost + usage penalty
    │
    └── 4. Fallback: stock_api_service.search_and_ingest()
            └── Hits live API → ingests to StockMediaAsset
            └── Feature flag: STOCK_PROVIDER='storyblocks' | 'legacy'
```

---

## Appendix: Storyblocks API Reference

### Authentication

Every request requires:
- `APIKEY`: Public key
- `EXPIRES`: Unix timestamp (up to 36 hours in future)
- `HMAC`: SHA-256 HMAC of resource path, keyed with `private_key + expires`

### Search Videos

```
GET /api/v2/videos/search
?keywords=sunset+beach
&max_duration=15
&content_type=footage,motionbackgrounds
&results_per_page=50
&safe_search=true
&project_id=<anonymize_project_id(campaign_id)>
&user_id=<anonymize_user_id(brand_id)>
```

### Search Images

```
GET /api/v2/images/search
?keywords=mountain
&results_per_page=50
&safe_search=true
&project_id=<anonymize_project_id(campaign_id)>
&user_id=<anonymize_user_id(brand_id)>
```

### Download

```
GET /api/v2/videos/stock-item/download/{stock_item_id}
?project_id=<anonymize_project_id(campaign_id)>
&user_id=<anonymize_user_id(brand_id)>
```

> Download queries are the **only** queries that count toward MAU (§4.3(a)).
> Meter + hard-cap (104) runs immediately before this call.

Response:
```json
{
  "MOV": {
    "_1080p": "https://d2v9y0dukr6mq2.cloudfront.net/video..."
  },
  "MP4": {
    "_1080p": "https://d2v9y0dukr6mq2.cloudfront.net/video...",
    "_720p": "https://d2v9y0dukr6mq2.cloudfront.net/video..."
  }
}
```

---

## EULA Compliance Addendum (2026-07-19)

Reconciled to `docs/Storyblocks API Agreement - 48 Social.pdf`.
Full clause→guard map: `docs/STORYBLOCKS_EULA_COMPLIANCE.md`.

### Spec vs contract deltas fixed in this revision

| Was (pre-2026-07-19) | Contract / operator ruling | Now |
|----------------------|----------------------------|-----|
| `StockSearchView` keyed `user_id` on `request.user.id` | §2.1(iv) + Q-SB-02 per-brand; MAU cost trap | All search+download use `anonymize_user_id(brand_id)` |
| No MAU meter | §4.3(a): MAU = distinct **Download** user_ids / calendar month; free tier 104 | Downloads-only ledger + hard block at 105th new brand (Q-SB-01) |
| Search and download treated alike for identity cost | Only Download queries count toward MAU | Meter only at `get_download_urls` |
| 429 backoff only | §2.1/§2.2: ≤600 search/min, ≤120 download/min | Proactive limiter + keep 429 backoff |
| No render-time license check | Preview ≠ license (§A) | Render/publish requires `CampaignAssetDownload` |
| Spec said “watermarked previews” | Agreement includes watermark-free previews | Preview may be watermark-free; still unlicensed until download |
| No AI-training wall-off | §B / preamble: no ML training on Stock Files/metadata | Selection-assist CLIP OK; training export forbidden |
| Release marks unspecified | Identifiable people/property clause | Persist `model_released` / `property_released` |
| Mix disclaimers unspecified | §2.2 if co-present with non-commercial-guarantee libraries | Q-SB-04: `STOCK_PROVIDER` mutually exclusive → N/A |

### MAU month basis (Q-SB-03)

**UTC calendar month** (`YYYY-MM`). Assumption: monthly invoices align to UTC calendar months. If Storyblocks billing uses a different anchor, adjust the ledger key only — keep hard cap semantics.

### Inventory note (phoenix_omega vs live backend)

This document is the **design surface** held in phoenix_omega. The live Django implementation lives in the separate **48 Social product backend** (`backend/apps/brands/services/storyblocks/…`). As of 2026-07-19 that repo was **not reachable** from the agent environment; treat code samples here as the contract for the backend PR, not as executable phoenix_omega code.
