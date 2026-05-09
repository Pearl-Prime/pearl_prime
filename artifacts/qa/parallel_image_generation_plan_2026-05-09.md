# Parallel Image Generation Plan — 2026-05-09

**Owner:** Pearl_Editor (this plan); Pearl_Dev + Pearl_Int (execution under `ws_image_batch_generation_orchestration_20260509`)
**Companion:** `image_asset_inventory_audit_2026-05-09.md`, `image_asset_inventory_2026-05-09.tsv`
**Status:** plan only — execution gated on **Pearl_Int Steps 3+4** (Animagine + Qwen-Image downloads)
**Hardware target:** Pearl Star (RTX 5070 Ti, 16 GB VRAM, single-GPU; sequential within-host parallel via wave batching)

---

## 1. Scope & non-goals

This document is the **operator-readable batch plan** that consumes the gap matrix from `image_asset_inventory_audit_2026-05-09.md` §4. Each row corresponds to one `(brand_id, locale, asset_type)` cell that is below target.

**This is a plan only.** No images generated in this session. Execution requires:

1. **Pearl_Int Step 3** complete: Animagine XL on Pearl Star (≈12 GB checkpoint on disk).
2. **Pearl_Int Step 4** complete: Qwen-Image on Pearl Star (≈8 GB checkpoint on disk).
3. Operator's parked **`HF_TOKEN_STAGED`** authorization activated for the download.
4. `ws_image_batch_generation_orchestration_20260509` has shipped a runner that:
   - Reads this MD's machine-section (§5)
   - Resolves LoRA chains per brand × series
   - Dispatches to the existing ComfyUI workflows
   - Writes outputs back to the canonical paths (`assets/manga_catalog/<brand>/<series>/...`, `brand-wizard-app/public/assets/...`)
   - Updates `image_asset_inventory_<DATE>.tsv` after each wave

---

## 2. Workflow template inventory (verified on disk)

| Asset purpose | Workflow template | Verified |
|---|---|---|
| Manga panel (FLUX text-to-image) | `scripts/image_generation/comfyui_workflows/flux_txt2img_manga.json` | ✅ |
| Manga panel (FLUX img2img) | `scripts/image_generation/comfyui_workflows/flux_img2img_manga.json` | ✅ |
| Manga panel (FLUX + IP-Adapter character lock) | `scripts/image_generation/comfyui_workflows/flux_ip_adapter_manga.json` | ✅ |
| Manga panel (FLUX + PuLID identity) | `scripts/image_generation/comfyui_workflows/flux_txt2img_manga_pulid.json` | ✅ |
| Anime style (Animagine XL) | `scripts/image_generation/comfyui_workflows/animagine_xl_txt2img_manga.json` | ✅ |
| Dark fantasy (Animagine XL) | `scripts/image_generation/comfyui_workflows/animagine_xl_dark_fantasy.json` | ✅ |
| Mecha (Animagine XL) | `scripts/image_generation/comfyui_workflows/animagine_xl_mecha.json` | ✅ |
| Manga panel (Qwen-Image) | `scripts/image_generation/comfyui_workflows/qwen_image_txt2img_manga.json` | ✅ (post‑#946) |
| Video b-roll | `scripts/image_generation/comfyui_workflows/flux_video_bank.json` | ✅ |

> **KDP / audiobook cover:** there is **no dedicated workflow JSON** today. The plan reuses `flux_txt2img_manga.json` with a KDP overlay variant (1600×2560 trim margins) — this is a **gap** flagged for `ws_image_batch_generation_orchestration_20260509` to add `flux_kdp_cover.json` and `flux_audiobook_cover.json`.

---

## 3. Targets per cell

Per the WORLDWIDE-CATALOG-GO-LIVE Q3 default and the manga catalog plan (`config/manga/manga_brand_series_plan.yaml`):

| asset_type | Target per `(brand × locale)` cell | Rationale |
|---|---:|---|
| `kdp_cover` | **800** | Q3 default catalog volume baseline. |
| `audiobook_cover` | **800** | 1:1 with KDP. |
| `manga_cover` | **8** per series × series count | 8 cover variants (front, profile, scene, symbolic, three_quarter, portrait, +2 topic-specific). |
| `manga_panel` | **100** per series | Phase-1 baseline (≈4 chapters × 25 panels). |
| `manga_protagonist` | **1** per series | `main_character.png`. |
| `manga_lora_ref` | **10** per series | Per `brand_lora_plans.yaml.character_loras.<teacher>.reference_views`. |
| `showcase_cover` | **3** | 1–3 brand showcase per locale. |
| `author_base` | **1** | Locale-agnostic teacher portrait. |
| `video_bank` | **3** | Brand-agnostic. |
| `onboarding_proof` | **5** | 5 wizard comparison images per locale. |

### 3.1 Series-count assumption per brand

- Flagship brands: 14 series each (per `canonical_brand_list.yaml` flagship target).
- Core brands: 8 series each (mid-band).
- Niche brands: 4 series each.

These multiply the per-series targets above.

---

## 4. Wave structure

Pearl Star has a **single GPU**. "Parallelization" here means **wave batching** with priority ordering. Each wave is sequential within itself; the wave boundary is a checkpoint.

### Wave 1 — Unblock the 19 zero-content brands (LoRA refs only)

Goal: emit **10 LoRA reference views per (brand × locale × series)** for the 19 brands with zero assets, so character-LoRA training can proceed in parallel on Pearl Star.

- 19 brands × 4 locales × 4 series (niche default) × 10 refs = **3,040 images**
- Workflow: `flux_txt2img_manga.json` (no LoRA chain yet — this IS the LoRA training input)
- Per-image wall time on RTX 5070 Ti: ≈ 12 s (FLUX-dev fp8, 1024×1024, 28 steps)
- Wave 1 wall time: 3,040 × 12 s = **36,480 s ≈ 10.1 h** at GPU saturation.

### Wave 2 — Unblock the 12 partial-content brands (LoRA refs to round out)

Goal: bring `manga_lora_ref` per (brand × locale × series) up to the 10-per-series target for brands that have `manga_protagonist` already but missing/incomplete LoRA refs.

- Estimate from §3.2 of audit: ~6 brands × 3 missing locales × 3 series × ~5 refs = **270 images**
- Wall time: 270 × 12 s = **3,240 s ≈ 0.9 h**

### Wave 3 — KDP + audiobook covers for active brands × non-US locales

Goal: 800 KDP + 800 audiobook per (active brand × {ja_JP, zh_TW, zh_CN}). For 12 active brands × 3 locales × 1,600 = **57,600 images**.

- Workflow: `flux_txt2img_manga.json` (with KDP overlay variant) + `flux_audiobook_cover.json` (TBD).
- LoRA chain: brand style LoRA (`style_<suffix>`) + (for teacher-bound brands) character LoRA `<teacher>_<suffix>`.
- Per-cover wall time: ≈ 18 s (FLUX-dev fp8, 1600×2560, 35 steps).
- Wave 3 wall time: 57,600 × 18 s = **1,036,800 s ≈ 288 h ≈ 12 days** at GPU saturation.

### Wave 4 — Manga panels for active series × all 4 locales

Goal: 100 panels × 4 locales × Σ(series across active brands).

- 12 active brands × {flagship 14 / core 8 / niche 4} series ≈ avg 8 series × 4 locales × 100 = **38,400 panels**.
- Workflow: `qwen_image_txt2img_manga.json` (Qwen-Image is the post‑#946 panel-render path) **OR** `animagine_xl_txt2img_manga.json` (style fallback).
- LoRA chain: brand style + protagonist LoRA per series + teacher character LoRA.
- Per-panel wall time: ≈ 15 s (Qwen-Image, 1024×1536, 30 steps).
- Wave 4 wall time: 38,400 × 15 s = **576,000 s ≈ 160 h ≈ 6.7 days**.

### Wave 5 — Showcase + video b-roll + onboarding proof completion

- Showcase: 37 brands × 4 locales × 3 = **444 images** at 12 s = 1.5 h
- Video bank: 37 brands × 3 = **111 video thumbs** at 12 s = 0.4 h
- Onboarding proof: 37 brands × 4 locales × 5 = **740 images** at 12 s = 2.5 h
- Wave 5 wall time: ≈ **4.4 h**

### Total wall time (single Pearl Star GPU, 24/7 unattended)

| Wave | Images | Hours | Days (24/7) |
|---|---:|---:|---:|
| W1 LoRA-ref unblock (zero brands) | 3,040 | 10 | 0.4 |
| W2 LoRA-ref completion (partial brands) | 270 | 1 | 0.04 |
| W3 KDP + audiobook (3 non-US locales) | 57,600 | 288 | 12.0 |
| W4 Manga panels (4 locales) | 38,400 | 160 | 6.7 |
| W5 Showcase + video + onboarding | 1,295 | 4 | 0.2 |
| **Total** | **100,605** | **~463 h** | **~19.3 days** |

> **At ~19 days of uninterrupted Pearl Star GPU utilization** (24/7 saturated), the worldwide catalog hits Phase-1 targets across all 4 locales for the 18 active brands. The 19 dormant brands need **prior LoRA training** before W3/W4 can include them.

---

## 5. Per-cell batch table (machine section)

Format: `brand_id | locale | asset_type | target_count | current_count | delta_count | workflow_template | LoRA_chain | estimated_minutes | batch_id`.

LoRA chain notation: `style_<brand_suffix> + <teacher>_<brand_suffix> + <protagonist>_<brand_suffix>_<locale>` (per `brand_lora_plans.yaml.brand_suffixes` + `character_loras` + `protagonist_loras`).

### 5.1 Wave 1 — Zero-content brands (LoRA refs)

(Excerpt; full enumeration is generated by `ws_image_batch_generation_orchestration_20260509`'s plan compiler from `image_asset_inventory_2026-05-09.tsv`.)

| brand_id | locale | asset_type | target | current | delta | workflow | LoRA_chain | est_min | batch_id |
|---|---|---|---:|---:|---:|---|---|---:|---|
| `healing_ground_healing` | en_US | manga_lora_ref | 40 | 0 | 40 | flux_txt2img_manga.json | `style_hg` (TBD) | 8 | W1.B01.L01 |
| `healing_ground_healing` | ja_JP | manga_lora_ref | 40 | 0 | 40 | flux_txt2img_manga.json | `style_hg` (TBD) | 8 | W1.B01.L02 |
| `healing_ground_healing` | zh_TW | manga_lora_ref | 40 | 0 | 40 | flux_txt2img_manga.json | `style_hg` (TBD) | 8 | W1.B01.L03 |
| `healing_ground_healing` | zh_CN | manga_lora_ref | 40 | 0 | 40 | flux_txt2img_manga.json | `style_hg` (TBD) | 8 | W1.B01.L04 |
| `minimal_mind_healing` | en_US | manga_lora_ref | 40 | 0 | 40 | flux_txt2img_manga.json | `style_min` (TBD) | 8 | W1.B02.L01 |
| `career_lift_workplace` | en_US | manga_lora_ref | 40 | 0 | 40 | flux_txt2img_manga.json | `style_cl` (TBD) | 8 | W1.B03.L01 |
| `high_performer_workplace` | en_US | manga_lora_ref | 40 | 0 | 40 | flux_txt2img_manga.json | `style_hp` (TBD) | 8 | W1.B04.L01 |
| `executive_calm_workplace` | en_US | manga_lora_ref | 40 | 0 | 40 | flux_txt2img_manga.json | `style_ec` (TBD) | 8 | W1.B05.L01 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Wave 1 totals:** 19 brands × 4 locales × 40 refs = **3,040 images / 608 batch-min ≈ 10.1 h**

### 5.2 Wave 3 — KDP + audiobook for active brands × non-US locales

| brand_id | locale | asset_type | target | current | delta | workflow | LoRA_chain | est_min | batch_id |
|---|---|---|---:|---:|---:|---|---|---:|---|
| `stillness_press` | ja_JP | kdp_cover | 800 | 0 | 800 | flux_txt2img_manga.json (KDP overlay) | `style_sp + ahjan_sp` | 240 | W3.B01.L02.K |
| `stillness_press` | ja_JP | audiobook_cover | 800 | 0 | 800 | flux_audiobook_cover.json (TBD) | `style_sp + ahjan_sp` | 240 | W3.B01.L02.A |
| `stillness_press` | zh_TW | kdp_cover | 800 | 0 | 800 | flux_txt2img_manga.json (KDP overlay) | `style_sp + ahjan_sp` | 240 | W3.B01.L03.K |
| `stillness_press` | zh_TW | audiobook_cover | 800 | 0 | 800 | flux_audiobook_cover.json (TBD) | `style_sp + ahjan_sp` | 240 | W3.B01.L03.A |
| `stillness_press` | zh_CN | kdp_cover | 800 | 0 | 800 | flux_txt2img_manga.json (KDP overlay) | `style_sp + ahjan_sp` | 240 | W3.B01.L04.K |
| `stillness_press` | zh_CN | audiobook_cover | 800 | 0 | 800 | flux_audiobook_cover.json (TBD) | `style_sp + ahjan_sp` | 240 | W3.B01.L04.A |
| `cognitive_clarity` | ja_JP | kdp_cover | 800 | 0 | 800 | flux_txt2img_manga.json (KDP overlay) | `style_cc + joshin_cc + (daisuke,sho,ren)_cc_jp` | 240 | W3.B02.L02.K |
| `cognitive_clarity` | ja_JP | audiobook_cover | 800 | 0 | 800 | flux_audiobook_cover.json (TBD) | `style_cc + joshin_cc` | 240 | W3.B02.L02.A |
| ... (12 active brands × 3 non-US locales × 2 cover types = **72 batch rows**) ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Wave 3 totals:** 12 brands × 3 locales × 1,600 covers = **57,600 images / ~17,280 batch-min ≈ 288 h**

### 5.3 Wave 4 — Manga panels per series × locale

(One row per (brand × series × locale).) Excerpt:

| brand_id | locale | asset_type | target | current | delta | workflow | LoRA_chain | est_min | batch_id |
|---|---|---|---:|---:|---:|---|---|---:|---|
| `stillness_press` | en_US | manga_panel | 1,400 | 94 | 1,306 | qwen_image_txt2img_manga.json | `style_sp + ahjan_sp + (saki,sensei,ken,honoka,ai,hana,yuki,mei)_sp_*` | 327 | W4.B01.L01.P |
| `stillness_press` | ja_JP | manga_panel | 1,400 | 56 | 1,344 | qwen_image_txt2img_manga.json | same | 336 | W4.B01.L02.P |
| `cognitive_clarity` | en_US | manga_panel | 800 | 4 | 796 | qwen_image_txt2img_manga.json | `style_cc + joshin_cc + (daisuke,sho,ren)_cc_jp` | 199 | W4.B02.L01.P |
| ... | ... | ... | ... | ... | ... | ... | ... | ... | ... |

**Wave 4 totals:** ≈ 38,400 panels / ≈ 9,600 batch-min ≈ 160 h

> The full 5.1/5.2/5.3 tables (~1,200 rows total) are not embedded here to keep this file readable; they are auto-generated by the future `scripts/image_batch/build_plan.py` (under `ws_image_batch_generation_orchestration_20260509`) from `image_asset_inventory_2026-05-09.tsv` against the canonical targets in §3.

---

## 6. Resume / restart contract

The runner under `ws_image_batch_generation_orchestration_20260509` MUST:

1. Persist a `state.json` per wave with: `{batch_id, started_at, completed_at, image_count, success, failure, sha256_per_output}`.
2. Idempotency: rerunning a `batch_id` skips images that already exist with matching seed.
3. Health check: every 100 images, write a line to `artifacts/qa/image_batch_runs/<DATE>_<wave>.log`.
4. Abort cleanly on disk-full (Pearl Star has ~2 TB free; W3+W4 = ~50 GB at PNG / ~5 GB at WebP — favor WebP for non-cover assets).
5. Re-run this audit's scan at the end of each wave so the dashboard refresh shows progress.

---

## 7. Cost / effort summary (operator-readable)

- **Operator effort:** zero during execution (autonomous Pearl Star run). Only Steps 3+4 download authorization is required.
- **Wall time at full GPU saturation:** ~19.3 days for full 4-locale parity across 18 active brands.
- **Realistic timeline assuming 12 h/day Pearl Star availability:** ~38.6 days.
- **Cost:** $0 LLM (Tier 2 unattended Pearl Star); $0 image API (local generation); electricity only.
- **Risk:** Pearl Star single-GPU is the bottleneck. Adding a second GPU (RTX 5090 — $2,500) halves the wall time. Documented but not requested.

---

## 8. Cross-references

- `image_asset_inventory_audit_2026-05-09.md` — source of gap matrix
- `image_asset_inventory_2026-05-09.tsv` — per-PNG row source
- `docs/specs/IMAGE_ASSET_INVENTORY_V1_SPEC.md` — schema + classification + dashboard contract
- `config/manga/brand_lora_plans.yaml` — LoRA chain source of truth
- `config/manga/canonical_brand_list.yaml` — 37-brand canon
- `scripts/image_generation/comfyui_workflows/*.json` — workflow templates
- `docs/PEARL_ARCHITECT_STATE.md` — `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01`
