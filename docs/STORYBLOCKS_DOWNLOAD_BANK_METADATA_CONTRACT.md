# Storyblocks Download → Bank → Metadata Contract

**Status:** SPECCED / implementation-ready (phoenix_omega design surface)  
**Not:** manga asset bank — this is the **48social per-campaign Storyblocks HD bank**  
**Governing EULA:** `docs/Storyblocks API Agreement - 48 Social.pdf` (EUYIG-SF8TR-9LD23-TJ3AK)  
**Companion:** `docs/STORYBLOCKS_EULA_COMPLIANCE.md` · `docs/storyblocks-integration.md`  
**Handoff:** `artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md`

---

## What “100%” means (acceptance layer — honest)

| Layer | Meaning for this workstream |
|-------|-----------------------------|
| **SPECCED** (this packet) | Download→bank→metadata contract + EULA guards + test matrix are complete and implementable |
| **CONFIG-EXISTS** | `STOCK_PROVIDER=storyblocks` + Storyblocks keys in backend env |
| **CODE-WIRED** | Guards exist in Django call sites listed in §C |
| **EXECUTED-REAL** | Confirm path downloads HD to campaign bank; MAU ledger/race tests green; render rejects preview-only |
| **PROVEN-AT-BAR / “100%” for this mission** | **All §C checklist items EXECUTED-REAL + test matrix green on the 48social Django backend**, merged with `storyblocks-eula-compliance=<full-SHA>` |

**100% ≠** phoenix_omega docs alone. Docs here are SPECCED. Claiming “100% done” without the backend merge is **G-CLAIM drift**.

---

## Interpretation lock

Operator ask: *“robust way to download into bank and tie to metadata … 100%.”*

| Candidate reading | Verdict |
|-------------------|---------|
| Manga layer bank / `assemble_from_bank.py` | **No** — wrong substrate; Storyblocks EULA is 48social Django |
| Shared catalog HD pool “bank” for reuse across campaigns | **Forbidden** — EULA §B stockpiling |
| **Per-campaign licensed HD bank + metadata bind** | **Yes** — confirm-first, license-on-download, CASCADE lifecycle |

---

## A. Download → Bank contract (EULA-safe)

### A.1 Sole HD download path

```
ONLY entry: StoryblocksAssetService.confirm_selection(asset_id, campaign_id, brand_id)
  → MauMeter.reserve_or_block(brand_id)          # R3 — downloads only
  → RateLimiter.acquire("download")              # ≤120/min
  → StoryblocksAPIService.get_download_urls(...) # license-granting query (§A)
  → HTTP GET HD bytes
  → GCS put  gs://{bucket}/campaigns/{campaign_id}/broll/{asset_uuid}.{ext}
  → CampaignAssetDownload.create(...)            # license proof + bank bind
  → return gcs_url                               # ONLY URL render may use
```

**Forbidden alternate paths (hard ban):**

- Pre-cache / warm HD for “likely” assets
- Shared HD pool under `gs://…/storyblocks/shared/…`
- Bulk prefetch / scripted scrape loops
- Render reading `preview_urls`, CDN preview, or Storyblocks CDN HD without `CampaignAssetDownload`
- Search path calling `get_download_urls`

Search may store **catalog metadata + preview URLs + optional CLIP-from-thumbnail** only. That is **not** the bank.

### A.2 Per-campaign bank location

| Element | Value |
|---------|--------|
| Bucket | `settings.GCS_MEDIA_BUCKET` (e.g. `48social-media-assets`) |
| Object key | `campaigns/{campaign_id}/broll/{stock_asset_uuid}.{ext}` |
| URI | `gs://{bucket}/{object_key}` |
| Ext | `mp4` / `mov` / `jpg` / `png` from download Content-Type / Storyblocks format |
| Isolation | One campaign prefix = one bank; no cross-campaign hardlinks |

Optional sidecar (same prefix, not required if DB is SSOT):

```
campaigns/{campaign_id}/broll/{stock_asset_uuid}.license.json
```

Sidecar mirrors `CampaignAssetDownload` fields for offline forensics; DB remains authoritative.

### A.3 Lifecycle (select → license → bank → bind → render → delete)

```mermaid
sequenceDiagram
  participant UI
  participant Search as search_and_store
  participant Confirm as confirm_selection
  participant SB as Storyblocks API
  participant Bank as GCS campaign bank
  participant CAD as CampaignAssetDownload
  participant Render as render/publish

  UI->>Search: query (preview only)
  Search->>SB: Search + anonymize_user_id(brand)
  Search-->>UI: preview URLs + metadata (requires_download=true)
  Note over Search: NO MAU meter; NO HD
  UI->>Confirm: select asset for campaign
  Confirm->>Confirm: MauMeter + rate limit
  Confirm->>SB: Download query (license grant)
  Confirm->>Bank: put HD object
  Confirm->>CAD: insert license proof + gcs_url + metadata bind
  Render->>CAD: assert exists for (campaign, asset)
  Render->>Bank: read gcs_url only
  Note over Render: preview URL → REJECT
  Note over Bank,CAD: campaign delete → CASCADE CAD + GCS prefix delete
```

### A.4 License proof = bank admission ticket

| Condition | Render allowed? |
|-----------|-----------------|
| `source_provider != "storyblocks"` | Yes (legacy path; out of this contract) |
| Storyblocks + `CampaignAssetDownload` row for `(campaign, stock_asset)` + `gcs_url` non-empty | **Yes** |
| Storyblocks + preview only / missing CAD | **No** — `UnlicensedStoryblocksAssetError` |

`CampaignAssetDownload` is the **license proof record**. No CAD ⇒ asset is not in the licensed bank for that campaign.

---

## B. Metadata binding (100% field map)

### B.1 Entity graph

```
Brand ──brand_id──► anonymize_user_id ──► Storyblocks API user_id
                      │
                      └──► StoryblocksMauLedger (year_month UTC, user_id)  [download only]

Campaign ──campaign_id──► anonymize_project_id ──► Storyblocks API project_id
    │
    ├── CampaignAssetDownload (license proof + bank bind) 1──1/stock per campaign
    │         │
    │         ├── gcs_url / object_key / file_size / downloaded_at
    │         ├── anonymized_user_id (snapshot at download)
    │         ├── mau_year_month (UTC YYYY-MM at download)
    │         └── stock_asset_id → StockMediaAsset
    │
    └── render reads ONLY gcs_url after assert_storyblocks_licensed

StockMediaAsset (catalog; may exist before license)
    ├── storyblocks_stock_id
    ├── source_provider = "storyblocks"
    ├── preview_urls / thumbnail_url   ← NOT for render
    ├── metadata.model_released / property_released
    ├── metadata.attribution / keywords (selection only)
    └── embedding_clip (thumbnail CLIP; selection-assist ONLY)
```

### B.2 Canonical schema

#### `StockMediaAsset` (catalog row — may be unlicensed)

| Field | Type | Bind purpose |
|-------|------|--------------|
| `id` | UUID PK | Internal asset id |
| `source_provider` | `"storyblocks"` | §3.2 attribution key |
| `storyblocks_stock_id` | str, indexed | Storyblocks stock item id for download API |
| `provider_id` | str | Same as stock id (legacy parity) |
| `preview_urls` | JSON | Selection UI only — **never render** |
| `thumbnail_url` | str | Grid + CLIP source |
| `media_type` | image\|video | |
| `width` / `height` / `duration` | | |
| `metadata.model_released` | bool\|null | EULA identifiable people |
| `metadata.property_released` | bool\|null | EULA identifiable property |
| `metadata.keywords` / tags | list | Selection only; **AI-training wall** |
| `metadata.attribution_label` | str | e.g. `"Stock media via Storyblocks"` |
| `embedding_clip` | vector\|null | Selection-assist only |
| `embedding_status` | enum | |
| `embedding_purpose` | const `"selection_assist"` | Wall-off marker |

#### `CampaignAssetDownload` (license proof + bank bind) — **extend**

| Field | Type | Bind purpose |
|-------|------|--------------|
| `id` | UUID PK | **license_proof_id** |
| `campaign_id` | FK CASCADE | Bank scope |
| `stock_asset_id` | FK | ↔ Storyblocks catalog asset |
| `gcs_url` | URL | Banked HD — **sole render URI** |
| `object_key` | str | `campaigns/{cid}/broll/{aid}.{ext}` |
| `file_size_bytes` | int\|null | Integrity |
| `content_sha256` | char64\|null | Optional byte verify |
| `downloaded_at` | datetime | License event time |
| `anonymized_user_id` | char16 | Brand identity used on Download query |
| `brand_id` | str | Operator identity scope (Q-SB-02) |
| `mau_year_month` | char7 | UTC `YYYY-MM` of license event |
| `storyblocks_stock_id` | str | Denormalized for audits |
| `source_provider` | const `"storyblocks"` | Attribution |
| `model_released` | bool\|null | Snapshot at download |
| `property_released` | bool\|null | Snapshot at download |
| `attribution_label` | str | Surfaced on credits |

**Uniqueness:** `unique_together = (campaign_id, stock_asset_id)`  
**Indexes:** `(campaign, downloaded_at)`, `(anonymized_user_id, mau_year_month)`, `storyblocks_stock_id`

#### `StoryblocksMauLedger` (R3)

| Field | Type |
|-------|------|
| `year_month` | UTC `YYYY-MM` |
| `user_id` | anonymized (16 hex) |
| `brand_id` | str |
| `first_download_at` | datetime |
| **unique** | `(year_month, user_id)` |

**Join point:** before `get_download_urls`, same `anonymized_user_id` written onto `CampaignAssetDownload` after success so audits can join CAD → ledger month.

### B.3 AI training wall (embeddings)

| Allowed | Forbidden |
|---------|-----------|
| CLIP on **thumbnail/preview** for ranking/selection | Export Storyblocks HD/preview/bytes into training sets |
| Store `embedding_purpose="selection_assist"` | Fine-tune / train on keywords, captions, biometric data |
| | Any dataset job with `source_provider="storyblocks"` without explicit deny |

Implement: module comment on `compute_storyblocks_embedding` + hard exclude in any training-export queryset.

### B.4 Race-safe MAU + bank write ordering

```
1. BEGIN SERIALIZABLE (or month-lock row FOR UPDATE)
2. MauMeter.reserve(brand) → insert ledger ON CONFLICT DO NOTHING; if new and count>104 → ROLLBACK + CapExceeded
3. get_download_urls + fetch HD
4. GCS put (idempotent overwrite same object_key)
5. CampaignAssetDownload upsert (unique campaign+asset)
6. COMMIT
```

If step 3–5 fail after ledger insert for a **new** brand: leave ledger row (brand already “activated” for the month — correct for MAU; retries free). Do **not** delete ledger on transient GCS failure.

---

## C. 100% compliance checklist → code touch points

### C.1 Checklist (every row must be EXECUTED-REAL for “100%”)

| ID | Guard | Django touch point (48social backend) | Done when |
|----|-------|----------------------------------------|-----------|
| **C-R1a** | Sole HD path = `confirm_selection` | `apps/brands/services/storyblocks/asset_service.py::confirm_selection` | No other caller of `get_download_urls` (rg gate in tests) |
| **C-R1b** | Render rejects non-CAD Storyblocks | `apps/pipelines/services/*` + shared `assert_storyblocks_licensed` in `storyblocks/license.py` | Unit + integration test |
| **C-R1c** | Preview URL never in render inputs | Same + frontend confirm uses bank URL | Test fixtures |
| **C-R2a** | Per-brand user_id on search | `apps/brands/views.py` StockSearchView + `asset_selection_service.py` | Same hash for same brand |
| **C-R2b** | Per-brand user_id on download | `confirm_selection` → API service | |
| **C-R3a** | MAU meter downloads only | `storyblocks/mau_meter.py` called only from confirm | Search does not touch ledger |
| **C-R3b** | Hard cap 104 | MauMeter | 104 pass / 105th block / repeat unlimited |
| **C-R3c** | 80/100 warnings | MauMeter telemetry | Log/metric asserted |
| **C-R3d** | Race-safe ledger | unique + transaction | Concurrent new brands at 103 |
| **C-RL** | Rate limit 600/120 | `storyblocks/rate_limiter.py` in `api_service.py` | Throttle tests |
| **C-AI** | Training wall | embedding task + export guard | Comment + deny test |
| **C-ATTR** | Attribution | CAD + credit surface | `source_provider` + label |
| **C-REL** | model/property released | `get_or_create_asset` metadata | Fields persisted |
| **C-MIX** | §2.2 N/A or disclaimers | settings docs / UI if mixed | Q-SB-04 |
| **C-LIFE** | Delete campaign → GCS + CAD | `campaigns/signals.py` post_delete | Integration |
| **C-BANK** | Object key layout | confirm_selection GCS put | Path contract test |

### C.2 Suggested new / touched modules

```
backend/apps/brands/services/storyblocks/
  api_service.py          # HMAC + rate limiter hook
  asset_service.py        # confirm_selection = sole HD path
  utils.py                # anonymize_user_id(brand_id)
  mau_meter.py            # NEW — R3
  rate_limiter.py         # NEW — 600/120
  license.py              # NEW — assert_storyblocks_licensed
  metadata.py             # NEW — bind CAD fields from asset + download event

backend/apps/brands/views.py
backend/apps/brands/services/asset_selection_service.py
backend/apps/brands/models.py          # StockMediaAsset fields if missing
backend/apps/campaigns/models.py       # CampaignAssetDownload extend + MauLedger
backend/apps/campaigns/signals.py      # GCS cleanup
backend/apps/pipelines/services/...    # call license.assert before render

backend/apps/brands/tests/test_storyblocks_mau_meter.py
backend/apps/brands/tests/test_storyblocks_license_guard.py
backend/apps/brands/tests/test_storyblocks_user_id.py
backend/apps/brands/tests/test_storyblocks_rate_limiter.py
backend/apps/brands/tests/test_storyblocks_bank_metadata_bind.py
backend/apps/campaigns/tests/test_campaign_gcs_cleanup.py
```

### C.3 Test matrix

| Test | Module | Assert |
|------|--------|--------|
| MAU 104th new brand download | `test_storyblocks_mau_meter.py` | allow |
| MAU 105th new brand | same | hard block, no API download call |
| Same brand 2nd+ download same month | same | allow; ledger count unchanged |
| Search does not create ledger row | same | after N searches, count=0 |
| Per-brand id stable | `test_storyblocks_user_id.py` | views + selection + confirm same hex |
| views.py ≠ user.id | same | different users, same brand → same id |
| Render without CAD | `test_storyblocks_license_guard.py` | raises |
| Render with CAD | same | uses `gcs_url` not preview |
| Rate limit search 601 | `test_storyblocks_rate_limiter.py` | blocks/queues |
| Rate limit download 121 | same | blocks |
| Bank bind fields complete | `test_storyblocks_bank_metadata_bind.py` | all §B.2 CAD fields set |
| Sole download caller | same or lint test | only `confirm_selection` calls `get_download_urls` |
| Campaign delete cleans GCS | `test_campaign_gcs_cleanup.py` | prefix empty |

---

## D. Operator paste-ready next commands

### D.1 When backend clone URL arrives

```bash
# 1) Clone private 48social Django backend
export SB_BACKEND_URL='git@github.com:48social/<PRIVATE_REPO>.git'  # OPERATOR FILLS
export SB_BACKEND_DIR="${HOME}/48social_backend"
git clone "$SB_BACKEND_URL" "$SB_BACKEND_DIR"
cd "$SB_BACKEND_DIR"
git fetch origin
git checkout -b agent/storyblocks-eula-bank-100pct origin/main

# 2) Pull design SSOT from pearlstar phoenix_omega tip (read-only reference)
ssh pearl_star 'cd ~/git/phoenix_omega_offline.git && git show agent/storyblocks-eula-compliance-20260719:docs/STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md' \
  > /tmp/STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md
ssh pearl_star 'cd ~/git/phoenix_omega_offline.git && git show agent/storyblocks-eula-compliance-20260719:docs/STORYBLOCKS_EULA_COMPLIANCE.md' \
  > /tmp/STORYBLOCKS_EULA_COMPLIANCE.md

# 3) Implement §C checklist against those docs; run §C.3 tests
# 4) Open PR, merge, emit:
#    storyblocks-eula-compliance=<full-SHA>
```

### D.2 Unblock phoenix_omega GitHub PR (optional; design already on pearlstar)

```bash
gh auth login -h github.com
cd /Users/ahjan/phoenix_omega
git push -u origin agent/storyblocks-eula-compliance-20260719
gh pr create --base main --head agent/storyblocks-eula-compliance-20260719 \
  --title "docs(storyblocks): EULA bank+metadata contract + compliance design" \
  --body "SPECCED only. See docs/STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md. Backend EXECUTED-REAL separate."
```

### D.3 Verify tip

```bash
git ls-remote pearlstar_offline refs/heads/agent/storyblocks-eula-compliance-20260719
# design files:
#   docs/STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md
#   docs/STORYBLOCKS_EULA_COMPLIANCE.md
#   docs/storyblocks-integration.md
```

---

## Anti-patterns (do not ship)

1. Shared HD bank across campaigns  
2. Download-on-search / HD-upfront “for speed”  
3. Counting search user_ids as MAU  
4. `anonymize_user_id(request.user.id)`  
5. Render from preview CDN  
6. Soft-allow 105th brand without operator override of Q-SB-01  
7. Exporting Storyblocks embeddings/keywords into ML training corpora  
8. Claiming “100%” on docs-only SPECCED layer  
