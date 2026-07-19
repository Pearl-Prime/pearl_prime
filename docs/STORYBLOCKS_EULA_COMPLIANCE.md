# Storyblocks EULA Compliance — Mechanism Map

**Status:** DESIGN LANDED (phoenix_omega) — **backend implementation BLOCKED** (no access to 48social Django repo)  
**Governing contract:** `docs/Storyblocks API Agreement - 48 Social.pdf`  
**Doc Ref:** EUYIG-SF8TR-9LD23-TJ3AK  
**Effective:** 2026-02-24 → 2027-02-23  
**Licensee:** 48 Social  
**Design spec (reconciled):** `docs/storyblocks-integration.md`  
**Handoff:** `artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md`

---

## Acceptance language

This packet is **system-working design** (Layer: SPECCED / mechanism-ready). It is **not** EXECUTED-REAL on the product backend until the Django repo implements and merges the guards below. Do not claim “done / shippable / bestseller.”

---

## Clause → Guard mapping

| Clause | Requirement (contract ground truth) | Guard / mechanism | Call site (48social backend) |
|--------|-------------------------------------|-------------------|------------------------------|
| **§A + download semantics** | License to use Stock Files is granted when End Users **download** via the Application; watermark-free **preview is not a license** | **R1 License-on-download render guard:** refuse any Storyblocks-sourced asset in render/publish unless a `CampaignAssetDownload` row exists for `(campaign, stock_asset)` | `confirm_selection()` creates the record after HD fetch; render/publish path calls `assert_storyblocks_licensed(campaign_id, asset_id)` |
| **§B No stockpiling / no standalone / no scripted high-volume download** | No HD library outside projects; no bulk scrape | **Preserve** confirm-first → per-campaign GCS copy → CASCADE delete on campaign delete. **Forbidden:** pre-cache HD, shared HD pool, bulk prefetch | `StoryblocksAssetService.confirm_selection` only; no alternate download dispatchers |
| **§B / preamble AI/ML** | No training AI on Stock Files or metadata/keywords; selection-assist AI allowed | **AI wall-off:** CLIP-from-thumbnail for selection only; comment + export guard so Storyblocks bytes/tags never enter training/fine-tune datasets | `compute_storyblocks_embedding` + any dataset export pipeline |
| **§B Identifiable people/property** | Surface Model/Property Released marks; unreleased needs clearance awareness | Persist + return `model_released` / `property_released` on asset metadata; UI disclaimer when false | `get_or_create_asset` / search response dict |
| **§2.1(iv)** | Anonymized User IDs on **Search and Download** queries | SHA-256 `anonymize_user_id`; never send raw PII | All `StoryblocksAPIService` search + `get_download_urls` |
| **§2.1 / §2.2 rate limits** | ≤600 search/min and ≤120 download/min (aggregate) | Proactive client limiter + keep 429 backoff | `StoryblocksAPIService` before HTTP |
| **§2.2 content-mix** | If mixed with non-commercial-guarantee providers: conspicuous disclaimers | Default: `STOCK_PROVIDER` mutual exclusion → **N/A**; if mixed, show §2.2 strings | settings + frontend stock picker |
| **§3.2 Attribution** | Clearly attribute Content as from Storyblocks | `source_provider="storyblocks"` stored + surfaced in content-source credits | asset dict + credit surface |
| **§4.3(a) + Payment Schedule** | MAU = distinct User IDs in **Download** queries per calendar month; fee beyond **104** MAUs at $4.40 | **MAU meter + hard cap 104** on distinct download user_ids; search IDs do not count; 80/100 warnings | Before `get_download_urls` for a brand not yet in month ledger |

---

## Operator decisions (defaults — logged)

| ID | Decision | Default |
|----|----------|---------|
| **Q-SB-01** | 105th distinct download user_id in a month | **HARD BLOCK** (no silent overage) |
| **Q-SB-02** | user_id identity scope | **Per brand** (all end-users of one brand share one Storyblocks identity) |
| **Q-SB-03** | MAU month basis | **UTC calendar month** (invoice-month assumption; flag if Storyblocks uses another anchor) |
| **Q-SB-04** | Provider co-presence | **`STOCK_PROVIDER` mutually exclusive** → §2.2 mix disclaimers N/A |

Rows: `OPD-SB-01` … `OPD-SB-04` in `artifacts/coordination/operator_decisions_log.tsv`.

---

## R1 — License-on-download (render guard)

```python
# Conceptual — implement in 48social backend only
class UnlicensedStoryblocksAssetError(Exception):
    """Preview-only / never-downloaded Storyblocks asset cannot enter render."""


def assert_storyblocks_licensed(campaign_id, stock_asset) -> None:
    if stock_asset.source_provider != "storyblocks":
        return
    if not CampaignAssetDownload.objects.filter(
        campaign_id=campaign_id, stock_asset=stock_asset
    ).exists():
        raise UnlicensedStoryblocksAssetError(
            f"Storyblocks asset {stock_asset.id} has no CampaignAssetDownload "
            f"for campaign {campaign_id}; preview grants no license (EULA §A)."
        )
```

**Invariant:** `confirm_selection()` is the **only** path that (1) calls `get_download_urls`, (2) fetches HD, (3) writes GCS, (4) inserts `CampaignAssetDownload`. Preview URLs from search must never be passed to FFmpeg/render/publish.

---

## R2 — Per-brand anonymized user_id

**Bug in current design spec:** `AssetSelectionService` uses `anonymize_user_id(self.brand_id)` but `StockSearchView` uses `anonymize_user_id(request.user.id)`. That would inflate MAUs if downloads ever keyed the same way.

**Fix:** every Search **and** Download query uses:

```python
user_id = anonymize_user_id(brand_id)  # brand_id from request/campaign context
```

Resolve `brand_id` in `views.py` from the authenticated brand context / campaign ownership — never from `request.user.id` for Storyblocks API params.

Stability: same `brand_id` → same 16-char hex for the life of the salt prefix `48social_user_`.

---

## R3 — MAU meter (downloads only, hard 104)

### Semantics

- Ledger key: `(year_month_utc, anonymized_user_id)` where `year_month_utc = YYYY-MM` in **UTC**.
- Insert/check **only** immediately before a Download API call (`get_download_urls`).
- Search queries must **not** touch the ledger.
- If `anonymized_user_id` already in this month’s ledger → allow unlimited further downloads for that brand.
- If not in ledger and `count(distinct) >= 104` → **HARD BLOCK** (Q-SB-01); emit telemetry `storyblocks.mau.cap_blocked`.
- Warnings at distinct counts **80** and **100**: `storyblocks.mau.warning`.

### Race safety

```text
BEGIN;
  INSERT INTO storyblocks_mau_ledger (year_month, user_id, brand_id, first_download_at)
  VALUES (%YYYY-MM%, %uid%, %brand%, now())
  ON CONFLICT DO NOTHING;  -- unique(year_month, user_id)
  SELECT COUNT(*) FROM storyblocks_mau_ledger WHERE year_month = %YYYY-MM%;
  -- If insert was new AND count > 104: DELETE the just-inserted row; RAISE; ROLLBACK path
COMMIT;
```

Prefer: attempt insert → if new row, re-count under `SELECT … FOR UPDATE` on a month lock row, or use a serializable transaction so two new brands at 103 cannot both commit.

### Model sketch

```python
class StoryblocksMauLedger(models.Model):
    year_month = models.CharField(max_length=7)  # UTC YYYY-MM
    user_id = models.CharField(max_length=16)    # anonymized
    brand_id = models.CharField(max_length=64)
    first_download_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("year_month", "user_id")]
        indexes = [models.Index(fields=["year_month"])]
```

---

## Rate limiter (§2.1 / §2.2)

Proactive token bucket / sliding window **before** HTTP:

| Endpoint class | Cap |
|----------------|-----|
| Search | 600 / minute |
| Download | 120 / minute |

Keep existing 429 exponential backoff as safety net; do not rely on Storyblocks throttling alone.

---

## AI wall-off (§B)

Allowed: CLIP embeddings from **thumbnails/previews** to assist selection.  
Forbidden: exporting Storyblocks HD/preview bytes, tags, keywords, or embeddings into any model-training / fine-tuning corpus.

Add a module-level comment on the embedding task and a hard check in any dataset export job that excludes `source_provider="storyblocks"`.

---

## Attribution + release marks

- Store `source_provider="storyblocks"`.
- Persist `metadata.model_released` / `metadata.property_released` from API.
- Credit surface: “Stock media via Storyblocks” (or product-equivalent conspicuous attribution).
- When not model/property released: conspicuous disclaimer per §2.2 / EULA identifiable-people clause.

---

## Content-mix disclaimers (Q-SB-04)

With `STOCK_PROVIDER ∈ {storyblocks, legacy}` as a deploy-wide switch, providers are mutually exclusive → **§2.2 co-presence disclaimers are N/A**.  
If a future deploy shows both libraries in one UI, implement the exact disclaimer strings from §2.2 within 90 days of Effective Date (already elapsed as of 2026-07 — treat as immediate if mix ships).

---

## Required tests (backend repo)

1. MAU: 104 distinct brands download → pass; 105th new brand → block; repeat brand after counted → unlimited.
2. Search does not increment MAU ledger.
3. Per-brand anonymized id stable across a UTC month; views.py and AssetSelectionService produce identical ids for same brand.
4. Render guard rejects Storyblocks asset without `CampaignAssetDownload`.
5. Rate limiter blocks at 601st search / 121st download in a rolling minute.
6. Confirm-first path still sole HD download entry (no pre-cache).

---

## Backend repo required (BLOCKER)

Implement in the **48 Social Django product backend** (paths from design spec):

- `backend/apps/brands/services/storyblocks/`
- `backend/apps/brands/views.py` (StockSearchView)
- `backend/apps/brands/services/asset_selection_service.py`
- `backend/apps/campaigns/` (`CampaignAssetDownload` + MAU ledger)
- `backend/apps/pipelines/services/` (render/publish guard)

**Not found** in this environment (no sibling checkout; Pearl Star has no 48social clone; GitHub `Ahjan108` account suspended so org/repo search/clone failed). Operator must provide clone URL + push credentials.

---

## Resume command (when backend access exists)

```bash
# 1. Clone 48social Django backend; branch from its default main
# 2. Apply guards per this doc + reconciled docs/storyblocks-integration.md §EULA
# 3. Run the test list above
# 4. Open PR, merge, emit: storyblocks-eula-compliance=<full-SHA>
```
