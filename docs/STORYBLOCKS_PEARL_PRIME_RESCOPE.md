# Storyblocks-for-Pearl-Prime Re-Scope

**Status:** SPECCED (re-scope) — **not** EXECUTED-REAL  
**Date:** 2026-07-19  
**Signal:** `storyblocks-pearl-prime-rescope=<pending-SHA>`  
**Supersedes substrate assumption in:** `docs/STORYBLOCKS_EULA_COMPLIANCE.md`, `docs/STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md`, `artifacts/coordination/handoffs/storyblocks_eula_compliance_2026-07-19.md`  
**Does not void:** signed EULA clauses (license-on-download, MAU 104, no stockpiling, no AI training on stock)  
**Governing contract PDF:** `docs/Storyblocks API Agreement - 48 Social.pdf` (Licensee: **48 Social**, Doc Ref EUYIG-SF8TR-9LD23-TJ3AK)

---

## 1. Why the prior turn demanded 48social GitHub

Honest answer: the prior EXECUTE turn inferred substrate from **documents**, not from operator intent.

| Evidence used | What it implied |
|---------------|-----------------|
| Signed PDF title / Licensee = **48 Social** | Legal counterparty is the 48 Social product entity |
| `docs/storyblocks-integration.md` paths | Django: `backend/apps/brands/services/storyblocks/…`, `CampaignAssetDownload`, GCS campaign bank |
| MAU / `user_id` design | Per-**brand** anonymized identity (Q-SB-02), campaign confirm-first flow |
| Handoff blocker language | “Need writable clone of 48social Django backend” |

That assumption was **internally consistent with the design packet** and **may not match operator intent**.

Operator clarification (2026-07-19): goal is **Storyblocks in Pearl Prime**, which lives in **this repo** (`phoenix_omega`). Pearl Prime is not the 48social Django campaign product. Therefore **48social GitHub is not required** unless Pearl Prime will call a remote 48social Storyblocks service API (no such API client exists here today).

---

## 2. Discovery — what exists in phoenix_omega today

### Layer honesty

| Claim | Layer |
|-------|-------|
| EULA + Django design docs in phoenix_omega | **SPECCED** (for 48social substrate) |
| Pearl Prime Storyblocks integration | **ABSENT** → this re-scope moves it to **SPECCED** (Pearl Prime substrate) |
| Storyblocks download/search working in Pearl Prime | **not** EXECUTED-REAL (no code, no tests, no keys) |

### Storyblocks / stock hooks

| Probe | Result |
|-------|--------|
| `storyblocks` Python package / client in `scripts/` | **None** |
| `STOCK_PROVIDER` runtime flag in phoenix_omega | **None** (only in Django design docs) |
| `STORYBLOCKS_*` in `docs/INTEGRATION_CREDENTIALS_REGISTRY.md` | **Absent** |
| `STORYBLOCKS_*` in `scripts/ci/integration_env_registry.py` / Keychain tracked list | **Absent** |
| Signed Storyblocks PDF in `docs/` | **Present** (48 Social agreement) |
| Existing stock providers in-repo | **Pexels / Pixabay / Unsplash / Openverse** via `scripts/brand/build_stock_image_bank.py` |
| Local stock bank | `artifacts/stock_image_bank/{brand_id}/{collection_id}/` (+ optional R2 `brand_assets`) |
| Social b-roll consumers | `scripts/social/render_*_shorts.py`, `build_video_snippet_bank.py` ← **Pexels plates**, not Storyblocks |
| Cover pipeline | `scripts/publish/five_layer_cover_orchestrator.py`, `render_kdp_cover.py`, `config/catalog_planning/brand_cover_art_specs.yaml` — stock is a **curated source layer**, not a Storyblocks hook |
| Pearl Prime content R2 | `PEARL_PRIME_CONTENT_R2_BUCKET` — **marketing_feed.json** weekly feed, **not** a stock HD bank |

**Verdict:** Using Storyblocks in Pearl Prime is a **NEW phoenix_omega integration**. It does not reuse an existing Storyblocks service. The closest reuse surface is the **stock image bank** + cover/social consumers that already speak Pexels/Pixabay/Unsplash.

---

## 3. Correct substrate (Pearl Prime / phoenix_omega)

### 3.1 Where downloads should land

EULA §B forbids a shared HD stockpile. Map the 48social “per-campaign bank” idea to Pearl Prime **work units**:

| Element | Pearl Prime proposal |
|---------|----------------------|
| Catalog / preview metadata | `artifacts/stock_image_bank/storyblocks/{collection_id}/` (metadata + preview refs only) |
| Licensed HD bank | **Per work-unit prefix**, not a global pool: e.g. `artifacts/storyblocks_licensed/{work_unit_id}/{asset_id}.{ext}` **or** R2 `brand_assets/storyblocks_licensed/{work_unit_id}/…` |
| License proof record | Sidecar JSON +/or SQLite/JSONL ledger (phoenix equivalent of `CampaignAssetDownload`) |
| Lifecycle | Delete / expire HD when work unit is abandoned; no cross–work-unit hardlinks |

**Forbidden:** `artifacts/stock_image_bank/.../downloads/storyblocks/` as a bulk HD library warmed “for later.”

### 3.2 Metadata ties

Bind every licensed download to:

| Field | Purpose |
|-------|---------|
| `source_provider=storyblocks` | Attribution + AI wall-off |
| `storyblocks_stock_id` | Upstream id |
| `work_unit_type` + `work_unit_id` | What the license is for (see identity / unit below) |
| `brand_id` / `locale` | Pearl catalog brand context |
| `surface` | `cover` \| `social_broll` \| `interior` \| `manga` \| `pearl_news` \| … |
| `download_query_at` / `mau_user_id` | License-on-download audit |
| `model_released` / `property_released` | EULA identifiable people/property |
| `local_or_r2_uri` | Only URI render may read |

Optional link fields when known: `book_id`, `cell_id`, `atom_id`, `campaign_slug` — helpful for forensics, not a substitute for `work_unit_id`.

### 3.3 EULA constraints that still apply

Even if identity scope differs from 48social “per brand,” these remain non-negotiable:

1. **License-on-download** — preview ≠ license; render/publish must refuse Storyblocks bytes without a license proof row for that work unit.
2. **MAU ≤ 104** distinct anonymized User IDs on **Download** queries / UTC month; hard-block 105th (default Q-SB-01).
3. **No stockpiling** — no shared HD pool, no bulk prefetch, no scripted scrape.
4. **No AI training** on Stock Files / keywords / embeddings derived for training (selection-assist CLIP-from-thumbnail only if explicitly allowed and walled off).
5. **Attribution** + release-mark surfacing.
6. **Rate limits** — ≤600 search/min, ≤120 download/min aggregate.

Salt prefix for anonymization should change from `48social_user_` to a Pearl Prime prefix (e.g. `pearl_prime_user_`) once identity scope is locked — same stability rule: same logical identity → same 16-char hex for salt lifetime.

### 3.4 Identity scope — default proposal + open question

| Option | MAU burn rate | Fit |
|--------|---------------|-----|
| **A. Per locale brand** (e.g. `way_stream_sanctuary` × locale) | Low–medium | Closest to prior Q-SB-02 “per brand”; matches catalog brand_id |
| **B. Per Pearl Prime product line** (one id for all Pearl Prime) | Lowest (1 MAU) | Simplest ops; may be too coarse if Storyblocks expects end-user granularity |
| **C. Per book / cell** | High — can hit 104 fast | Over-fragmented; avoid unless Storyblocks requires it |
| **D. Per surface pipeline** (covers vs social vs news) | Medium | Useful if teams/billing differ by surface |

**Default proposal: A — per locale brand** (`anonymize_user_id(f"{brand_id}:{locale}")`), with work-unit bank = **per book cell** (or per social campaign slug) for HD isolation.

**OPEN QUESTION (operator):** Confirm A vs B (or other). Legal counterparty on the PDF is still “48 Social” — confirm Pearl Prime use is covered under that agreement / same API credentials.

---

## 4. In-repo EXECUTE plan (no 48social clone)

### 4.1 Files to add / extend

| Path | Role |
|------|------|
| `scripts/storyblocks/api_client.py` | HMAC search + download URL (port from design spec; phoenix-native) |
| `scripts/storyblocks/mau_ledger.py` | UTC-month distinct download identity ledger + hard 104 |
| `scripts/storyblocks/license_store.py` | License proof + work-unit bank bind |
| `scripts/storyblocks/confirm_download.py` | Sole HD download entry (confirm-first) |
| `scripts/brand/build_stock_image_bank.py` | Optional: add `storyblocks` provider for **preview/metadata only** |
| `scripts/ci/check_storyblocks_eula_guards.py` | CI: no alternate download paths; AI export wall |
| `scripts/ci/integration_env_registry.py` + credentials registry | Track `STORYBLOCKS_*` env names (keys later) |
| `tests/storyblocks/test_mau_and_license_guards.py` | MAU 104/105, search excluded, render guard |
| Consumers (phase 2, surface-gated) | Cover orchestrator / social broll / etc. — only after confirm path green |

### 4.2 What “100%” means for Pearl Prime

| Layer | Definition |
|-------|------------|
| **SPECCED** | This re-scope + EULA mechanism map adapted to phoenix paths |
| **CONFIG-EXISTS** | `STORYBLOCKS_*` in registry + Keychain; feature flag for provider |
| **CODE-WIRED** | Client + MAU + license store + one consumer call site |
| **EXECUTED-REAL** | Real Download query → HD in work-unit bank → license row → consumer reads only licensed URI; tests green |
| **“100%” for Pearl Prime Storyblocks** | EXECUTED-REAL on **operator-chosen surface** (default proposal: social b-roll **or** cover stock confirm path) + CI guards merged |

Docs alone ≠ 100%. Gate-PASS on unrelated checks ≠ Storyblocks works.

### 4.3 Surfaces — need operator pick

Priority candidates inside Pearl Prime / phoenix_omega:

1. **Social b-roll / shorts** — today Pexels; clearest Storyblocks video+image win  
2. **KDP / brand covers** — curated stock winners path  
3. **Pearl News / marketing feed imagery** — only if feed needs licensed stock  
4. **Manga panels** — **out of scope** by default (layered bank / generate path; do not conflate)

---

## 5. Credentials

| Item | State |
|------|-------|
| Storyblocks API keys in INTEGRATION_CREDENTIALS_REGISTRY | **Missing** — must add when wiring |
| Storyblocks in Keychain tracked list | **Missing** |
| Pexels/Pixabay/Unsplash | Used by stock bank scripts; **not** listed in INTEGRATION_CREDENTIALS_REGISTRY (gap); local `docs/stock_image_provider_keys.env` exists (do not commit secrets) |
| Pearl Prime content R2 | Documented for marketing JSON — separate from Storyblocks HD bank |

**ACCESS_REQUIRED:** Storyblocks public/private key pair (or whatever the signed API agreement issues), confirmation they apply to Pearl Prime use under the 48 Social agreement.

---

## 6. Relationship to prior 48social design docs

| Doc | Disposition |
|-----|-------------|
| `docs/storyblocks-integration.md` | Keep as **48social historical / alternate substrate** design; mark header “not Pearl Prime substrate” |
| `docs/STORYBLOCKS_EULA_COMPLIANCE.md` | Clause→guard map still valid; **call sites** retarget to phoenix scripts |
| `docs/STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md` | Pattern valid; replace GCS campaign paths with §3.1 work-unit bank |
| This doc | **Authoritative substrate for Pearl Prime EXECUTE** |

Do **not** block Pearl Prime work on cloning 48social.

---

## 7. NEXT_ACTION (operator)

1. **Surface pick:** covers / social b-roll / news / other  
2. **Identity scope ruling:** accept default **A (per locale brand)** or choose B/C/D  
3. **Legal/credential:** confirm Pearl Prime use under “48 Social” agreement + provide Storyblocks API keys to Keychain  
4. Then: EXECUTE in phoenix_omega per §4 (SPECCED → CODE-WIRED → EXECUTED-REAL on chosen surface)
