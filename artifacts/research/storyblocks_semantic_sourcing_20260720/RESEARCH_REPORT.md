# Storyblocks Capability + Semantic Stock-Sourcing Research

**Lane:** 01_storyblocks_capability_research  
**Agent:** Pearl_Research  
**Date:** 2026-07-20  
**Base SHA:** `9e9b9e606791590337cd7d0f2fb425def2e6f760` (`origin/main` local; GitHub HTTP 403)  
**Layer:** RESEARCHED (docs + public web; no live Storyblocks API keys)  
**Companion:** `RECOMMENDED_TAXONOMY.md`

---

## STARTUP / LIVE STATE

| Check | Result |
|-------|--------|
| `origin/main` SHA | `9e9b9e606791590337cd7d0f2fb425def2e6f760` |
| GitHub push/PR | **Blocked** (account suspended / HTTP 403) — land on `pearlstar_offline` |
| Prior taxonomy / caption-to-asset research | **None** under `docs/research/` or `artifacts/research/` (no Storyblocks keyword taxonomy / caption-to-asset docs) |
| `scripts/storyblocks/*` live download | **No keys path:** `StoryblocksAPIClient()` raises `StoryblocksConfigError` without `STORYBLOCKS_PUBLIC_KEY` / `STORYBLOCKS_PRIVATE_KEY` (`scripts/storyblocks/api_client.py:59-65,95-98`) |
| OPD-SB-PP-01b/02b/03b | **LOCKED** in `artifacts/coordination/operator_decisions_log.tsv` — surface = social_broll + media-bank + covers; identity = per locale brand; legal OK. Not re-opened. |
| Substrate authority | `docs/STORYBLOCKS_PEARL_PRIME_RESCOPE.md` (CODE-WIRED client; DOWNLOAD not EXECUTED-REAL without keys) |

### Open questions this report answers

1. How Storyblocks Content API search/tagging actually works (params, filters, metadata, keyword granularity).
2. Clip-length strategy vs beat roles (`hook`/`beat`/`value`/`endcard`).
3. Audio search → `mood_register` mapping.
4. Practical caption/atom → Storyblocks (or Pexels-bank) selection method buildable under Tier-1/Tier-2 LLM policy.
5. EULA constraints that shape design (MAU 104, no stockpile, no AI training; selection-assist CLIP status).

---

## 1. Search & keyword system

### 1.1 Auth + required IDs (compatible with existing client)

**Source (published docs):** Storyblocks API Reference (Postman public workspace), Authentication + Required Query Parameters.  
**Source (repo):** `scripts/storyblocks/api_client.py` — HMAC over resource path; `APIKEY` / `EXPIRES` / `HMAC`; base `https://api.storyblocks.com`.

| Param | Role |
|-------|------|
| `APIKEY`, `EXPIRES`, `HMAC` | Auth (HMAC-SHA256 of resource path with `private_key + expires`) |
| `user_id`, `project_id` | Required on search **and** download |
| Rate limits (contract) | ≤600 search/min, ≤120 download/min — PDF §2.1/§2.2; mirrored in `rate_limiter.py` |

Existing client search shape (do **not** redesign without cause):

- Video: `GET /api/v2/videos/search` with `keywords`, `max_duration`, `content_type=footage,motionbackgrounds`, `safe_search=true`, anonymized `user_id`/`project_id` (`api_client.py:144-166`).
- Image: `GET /api/v2/images/search` (`api_client.py:168-187`).
- Download: `GET /api/v2/{videos|images}/stock-item/download/{stock_id}` (`api_client.py:189-209`).
- **Gap vs API:** client has **no** `search_audio` yet; audio endpoint exists in published API (`GET /api/v2/audio/search`).

### 1.2 Video search parameters (published API)

**Source:** Postman Storyblocks API Reference — `GET /api/v2/videos/search`.

| Param | Behavior |
|-------|----------|
| `keywords` | Match these keywords; **comma-separated multiple values** |
| `required_keywords` | Must match **all** (AND) |
| `filtered_keywords` | Must match **none** (exclude) |
| `content_type` | `footage`, `motionbackgrounds`, `templates`, `all` |
| `quality` | `HD`, `4K`, `ALL` |
| `min_duration` / `max_duration` | Seconds |
| `orientation` | `horizontal`, `vertical`, `all` |
| `has_talent_released` / `has_property_released` | Model/property release filters |
| `has_alpha`, `is_editorial`, `is_vr_360` | Boolean filters |
| `categories` | Category IDs from Categories endpoint |
| `frame_rates` | e.g. 24, 25, 30, 50, 60 |
| `safe_search` | SFW only |
| `sort_by` | `most_relevant` (default), `most_downloaded`, `most_recent`, `trending_now`, `undiscovered` |
| `page` / `results_per_page` | Cap: ≤250/page; page×size ≤ 10,000 |
| `extended` | Opt-in metadata: `download_formats`, `keywords`, `isSensitiveContent`, `categories`, `description`, `isEditorial`, `isStereo`, `hasTalentReleased`, `hasPropertyReleased`, `hasAudio`, `hasAlpha`, `maxResolution`, `aspectRatio`, `dateAdded`, `durationMs` |

**Default search result fields (published example):** `id`, `title`, `type`, `contentClass`, `is_new`, `thumbnail_url`, `preview_urls` (`_180p`…`_720p`), `duration`, `durationMs`, `orientation`.  
Keywords/categories/releases are **not** in the default payload — request via `extended=keywords,categories,hasTalentReleased,hasPropertyReleased,hasAudio,durationMs,description`.

### 1.3 Keyword granularity in practice (grounded, not assumed)

**Source (public website search, not live API):**  
`https://www.storyblocks.com/video/search?keywords=person+nervous+in+crowd` → **34 results** for query labeled `person-nervous-in-crowd`.

Observed mix (per published docs: site filters ≈ API filters):

- **Usably close (top):** “Close-up of Nervous Student in Hoodie During Rehearsal”; “Focused person concentrates amid distractions… Nervous pupils…”
- **Broad / keyword collision:** concert crowds, festival dancers, rally crowds, anonymous street crowds — matches `crowd`/`person` more than `nervous`.

**Finding:** Storyblocks search is **keyword/tag retrieval**, not multimodal caption understanding. Multi-word phrases help but do **not** guarantee scene-level semantics. Practical implication for Lane 02:

1. Prefer **short concrete visual nouns + affect** (`nervous woman office`, `crowded subway tense`) over long prose captions.
2. Use `required_keywords` for hard visual anchors (e.g. `office` AND `woman`) and `filtered_keywords` to drop festivals/concerts for clinical-adjacent topics.
3. Always re-rank top-N with title/keyword overlap + optional local CLIP on **thumbnails** (see §4–§5).

**Example query constructions (per published docs — not live API):**

| Intent | Recommended params |
|--------|-------------------|
| Social anxiety crowd | `keywords=nervous,crowd,people` + `required_keywords=nervous` + `filtered_keywords=concert,festival,parade` + `orientation=vertical` + `max_duration=15` + `content_type=footage` + `extended=keywords,hasTalentReleased,durationMs,hasAudio` |
| Burnout desk | `keywords=exhausted,office,laptop,worker` + `required_keywords=office` + `has_talent_released=true` + `max_duration=12` |
| Boundaries conversation | `keywords=conversation,colleagues,meeting,serious` + `filtered_keywords=party,celebration` |

---

## 2. Clip-length strategy vs beat roles

**Source (repo):** `scripts/social/build_video_snippet_bank.py:75-80`

```text
BEAT_ROLE_DURATIONS = { hook: 3s, beat: 5s, value: 8s, endcard: 2s }
```

**Source (API):** `min_duration` / `max_duration` on video search; result `duration` / `durationMs`.

### Tradeoffs

| Approach | Pros | Cons |
|----------|------|------|
| **Short tagged clips** (~3–8s native, or trim from ≤15s) | Beat-aligned cuts; high keyword specificity; montage energy matches `broll_montage` | More downloads/MAU risk if identity fragmented (we use per-locale-brand — OK); continuity risk across cuts |
| **One longer continuous clip** (15–30s+) | Smooth motion; one license event | Harder to match four distinct semantic beats; waste on unused seconds; weaker keyword hit rate for long “story” clips |

### Recommendation (buildable)

| Beat role | Duration | Strategy |
|-----------|----------|----------|
| **hook** (3s) | Prefer **short native** clips with `max_duration=8`, trim to 3s from first high-motion second | Face/gesture/object punch; highest visual specificity |
| **beat** (5s) | Short tagged clip `max_duration=12`, trim to 5s | Recognition moment; same visual family as hook or soft cut |
| **value** (8s) | Prefer **slightly longer single clip** (`min_duration=6`, `max_duration=15`) over stitching 2×4s | Mechanism/calm explanation needs continuity; avoid jump-cuts during value |
| **endcard** (2s) | Shortest clip or freeze/hold from value tail; `max_duration=6` | Brand/CTA plate — kinetic_type often owns this; stock is secondary |

**Default bank policy:** Search with `max_duration=15` (already client default) for hook/beat/endcard; for value, allow up to 20s then trim. Prefer **one licensed clip per beat role cell** over multi-clip stitch inside a single beat. Across the four-beat montage, use **2–4 distinct short clips** (hook/beat short; value longer; endcard may reuse brand plate).

Do **not** bulk-prefetch a 30s library “for later” — EULA §B no stockpiling (PDF; see §5).

---

## 3. Music / audio licensing & mood mapping

### 3.1 Audio search API (published)

**Source:** Postman — `GET /api/v2/audio/search`.

| Param | Notes |
|-------|-------|
| `keywords` | Comma-separated |
| `content_type` | `music`, `sfx`, `all` |
| `min_duration` / `max_duration` | Seconds |
| `min_bpm` / `max_bpm` | Music only |
| `has_vocals` | Vocal filter |
| `required_keywords` / `filtered_keywords` | AND / NOT |
| `categories`, `safe_search`, `sort_by` | Same pattern as video |
| `extended` | `keywords`, `bpm`, `moods`, `genres`, `instruments`, `soundEffects`, `topTags`, `durationMs`, `hasTalentReleased`, `hasPropertyReleased`, `artists`, `pro`, `publisher`, … |

**Default result fields (published example):** `id`, `title`, `type`, `contentClass`, `thumbnail_url`, `waveform_url`, `preview_url`, `duration`, `durationMs`, `bpm`.

**Contributor tagging practice (Storyblocks Contributor FAQ):** 10–25 keywords; dropdown **moods** and **genres** — confirms API `extended=moods,genres` is the structured path, not free-text alone.  
URL: `https://contribute-faq.storyblocks.com/en/articles/4800758-how-can-i-write-better-keywords-on-my-audio-tracks`

**Legacy PDF (v1.8, 2018) mood enums (still useful vocabulary):** aggressive, epic-inspiring, happy-upbeat, … — treat as **historical enum hint**; verify against live Categories/`extended=moods` once keys exist. Source: Storyblocks API Documentation v1.8 PDF.

### 3.2 Map to Pearl `mood_register`

**Source (repo):** `config/social/media_bank_sizing_20260719.yaml:128-134`

| `mood_register` | Topic families | Storyblocks search recipe (recommended) |
|-----------------|----------------|------------------------------------------|
| `tense_anxious` | anxiety, financial_*, social_anxiety, sleep_anxiety, overthinking | `content_type=music`, `keywords=tense,anxious,suspense,pulse`, `min_bpm=90`, `max_bpm=130`, `has_vocals=false`, `extended=moods,genres,bpm,keywords` |
| `heavy_low` | depression, grief, burnout, compassion_fatigue | `keywords=melancholy,somber,slow,ambient`, `max_bpm=90`, `has_vocals=false` |
| `grounding_somatic` | somatic_healing, boundaries | `keywords=calm,ambient,peaceful,breath`, `max_bpm=100`, soft acoustic/`ambient` genre keywords |
| `empowering_courage` | courage, self_worth, imposter_syndrome | `keywords=uplifting,inspiring,hopeful,resolve`, `min_bpm=100`, `max_bpm=140`, filter out aggressive/horror via `filtered_keywords` |

**Audio EULA extras (PDF EULA bullet “Additional Restrictions on Use of Audio Stock Files”):** no upload of audio stock to Spotify/Apple Music/etc. as standalone; PRO marks may require reporting — persist `pro`/`publisher` from `extended` when downloading music beds.

**Client gap:** Lane 02 should extend `api_client.py` with `search_audio()` mirroring video HMAC + rate_kind=`search` — do not invent a second auth shape.

**Bank note:** `media_bank_sizing_20260719.yaml` currently lists audio `license_class_allowed: [musicgen_owned, owned_original]`. Storyblocks audio is a **future licensed class** under Pearl Prime surface lock (OPD-SB-PP-01b); taxonomy below still defines the mapping so Lane 02 can wire search before bank policy expands.

---

## 4. Core alignment method (caption/atom → asset)

### 4.1 Patterns from programmatic video systems (documented)

| Pattern | Source | Takeaway |
|---------|--------|----------|
| Script → scene keywords → Pexels/Pixabay search → Remotion assemble | GitHub `premkumarofficeoff/Automated-Video-Generator` README | Deterministic keyword extract → stock API → timeline; no vision API required |
| Schema-validated props → Remotion (deterministic render) | forgehouse “Programmatic Video” skill page | Keep assembly deterministic; separate AI cinematic layer |
| Context keyword table → asset class | `graphics-api-remotion` context keyword reference | Controlled vocabulary beats raw caption dump |

**Rejected for this program:** paid cloud vision/embedding APIs (OpenAI/Google) — CLAUDE.md LLM Tier Policy.  
**Allowed:** Tier-1 Claude for offline taxonomy authoring; Tier-2 local for unattended; **local CLIP on licensed/preview thumbnails** for selection-assist if EULA-ok (§5).

### 4.2 Recommended method (concrete, buildable) — **Controlled Taxonomy Query Compiler (CTQC)**

```text
atom {topic, persona, hook_family, tone, text}
        │
        ▼
[1] FIELD MAP  →  visual_intent + mood_register + beat_role
    (YAML tables in RECOMMENDED_TAXONOMY.md — no ML)
        │
        ▼
[2] QUERY COMPILE  →  Storyblocks params
    keywords, required_keywords, filtered_keywords,
    orientation, max_duration, content_type, has_talent_released,
    extended=keywords,hasTalentReleased,durationMs,hasAudio,description
        │
        ▼
[3] SEARCH  →  top N (N=20) via existing StoryblocksAPIClient.search_videos
    OR fallback Pexels-bank index (existing plates) if Storyblocks miss / MAU caution
        │
        ▼
[4] RANK (deterministic score)
    + title/keyword token overlap with compiled keyword set
    + duration proximity to BEAT_ROLE_DURATIONS[role]
    + release flags prefer model-released for people shots
    + optional: local CLIP cosine(thumbnail, short visual prompt)  # selection-assist only
        │
        ▼
[5] CONFIRM DOWNLOAD  →  confirm_download.py only (license-on-download, MAU ledger)
```

**Why this wins over caption-as-query:** §1.3 shows free-text phrases over-match crowds/festivals. Atom fields (`topic`/`hook_family`/`tone`) are stable keys; caption text contributes **optional** noun phrases via a small allowlisted extractor (concrete nouns only), never the full sentence as `keywords`.

**Pexels-bank coexistence:** Prefer curated local bank when a cell already has a winner (`config/social/curated_image_winners.yaml` pattern); use Storyblocks search for **video b-roll gaps** and new cells. Same ranking interface; different provider adapter.

### 4.3 Compatibility with `api_client.py`

Lane 02 should add optional params to `search_videos` (`required_keywords`, `filtered_keywords`, `orientation`, `min_duration`, `extended`, `has_talent_released`) as **kwargs into existing `params` dict** — keep HMAC/resource paths unchanged. Do not change MAU/download entrypoints.

---

## 5. EULA constraints that shape design

**Governing PDF:** `docs/Storyblocks API Agreement - 48 Social.pdf` (Doc Ref EUYIG-SF8TR-9LD23-TJ3AK; Licensee 48 Social; Effective 2026-02-24 → 2027-02-23).  
**Text extract:** `/tmp/sb_eula.txt` via `pdftotext` (research session).

| Constraint | PDF ground truth | Design impact |
|------------|------------------|---------------|
| **No AI training** | Preamble + EULA: may not use Stock Files (including caption info, keywords, other metadata) for ML/AI **to train AI systems**, or biometric ID tech. **Explicit carve-out:** “not meant to serve as a restriction on your ability to use AI to assist in your selection of Stock Files…” (PDF ~p.3–4 / extract lines 174–178) | **CTQC + local CLIP-from-thumbnail for ranking/selection is allowed.** Forbidden: exporting Storyblocks keywords/bytes/embeddings into training/fine-tune corpora. Aligns with `STORYBLOCKS_PEARL_PRIME_RESCOPE.md` §3.3 item 4 and `STORYBLOCKS_EULA_COMPLIANCE.md` AI wall-off. |
| **MAU 104** | Payment Schedule: MAU fee beyond **104** MAUs at $4.40; §4.3(a): MAU = distinct User IDs in **Download** queries per calendar month (extract lines 40–45, 363–367) | Hard-block 105th (`mau_ledger.py`); search does not burn MAU. Identity = per locale brand (OPD-SB-PP-02b). |
| **No stockpiling** | EULA: no standalone file use; no automation to download/scrape high volumes; no manual stockpile without a particular project (extract ~131–135) | Confirm-first per work unit only; no warm HD library for “later.” |
| **License-on-download** | License granted when End Users **download** via Application; watermark-free preview ≠ license (cover page + §A semantics in compliance map) | Rank/search on previews; render only after `confirm_download` / license_store. |
| **Rate limits** | 600 search / 120 download per minute (extract ~296, 309–310) | Existing `rate_limiter.py`. |
| **Anonymized user IDs** | API docs + PDF §2.1(iv) | Existing `identity.py` / `pearl_prime_user_` salt path. |

**CLIP reading confirmed against PDF (not only design paraphrase):** selection-assist AI is **explicitly allowed**; training on stock/keywords/metadata is **forbidden**. Wall-off: `embedding_purpose=selection_assist`; exclude `source_provider=storyblocks` from any training export (`STORYBLOCKS_DOWNLOAD_BANK_METADATA_CONTRACT.md` §B.3).

---

## Discovery summary

| Item | Status |
|------|--------|
| Duplicate research | None found — this lane is NEW |
| Client shape | Reuse HMAC client; extend params + add `search_audio` |
| Taxonomy deliverable | `RECOMMENDED_TAXONOMY.md` (Lane 02 input) |

## NEXT_ACTION

Hand `RECOMMENDED_TAXONOMY.md` to Lane 02 (query compiler + ranking YAML → code).
