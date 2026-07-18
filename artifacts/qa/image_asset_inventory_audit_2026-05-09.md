# Image Asset Inventory Audit — 2026-05-09

**Owner:** Pearl_Editor
**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (extends Phase 1 P1 surface 2 + P2 surface 3)
**Subsystem:** brand_admin (primary); manga_pipeline; pearl_prime
**Cap entry:** `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` (`docs/PEARL_ARCHITECT_STATE.md`)
**Status:** snapshot audit (no generation; gated on `Pearl_Int Steps 3+4` model downloads)
**Companion files:** `image_asset_inventory_2026-05-09.tsv`, `parallel_image_generation_plan_2026-05-09.md`, `docs/specs/IMAGE_ASSET_INVENTORY_V1_SPEC.md`

---

## 1. Executive summary

The Phoenix Omega catalog currently holds **6,528 PNG image assets** across **6 surfaces** but is **massively skewed** toward `en_US` (66 %) and three flagship brands. The post‑PR #977 dashboard surfaces only the active/inactive brand flag (`brand_wizard YAML` SSOT, Q4 default); it does **not** show image‑inventory depth. Operator visibility into per‑brand × per‑locale image counts is currently **zero**.

**Headline numbers (this snapshot):**

| Metric | Value |
|---|---:|
| Total PNGs scanned | **6,528** |
| Real images (≥1 KB) | **6,447** |
| LFS pointer files (<1 KB) | **81** (1.2 %) |
| Surfaces scanned | **6** (5 enumerated + `assets/manga_catalog` discovered) |
| Canonical manga brands (per `config/manga/canonical_brand_list.yaml`) | **37** |
| Cells in 37 × 4‑locale matrix | **148** |
| Cells with ≥1 asset | **59** (40 %) |
| Cells with 0 assets (red) | **89** (60 %) |
| Brands with ZERO images across all 4 target locales | **19 / 37** (51 %) |

**Critical gap:** `en_US` total = 4,337 vs. `ja_JP` 879 / `zh_TW` 607 / `zh_CN` 610. The non‑US locales together (~2,096) are still less than half the US figure, and 19 of 37 brands have **no asset of any kind** in any locale.

---

## 2. Surface‑level totals

| # | Surface | Path | Real PNGs | Notes |
|---|---|---|---:|---|
| 1 | Author cover bases | `assets/authors/cover_art/` | **17** | Locale‑agnostic teacher portrait; 7 are <50 KB stubs (book pen names: `ajahn_x`, `diane_reyes`, `kai_nakamura`, `luna_hart`, `marcus_cole`, `master_sha`, `omote`). |
| 2 | Brand wizard public assets | `brand-wizard-app/public/assets/` | **239** | Subdivided: `covers/kdp` 52, `covers/audiobook` 14, `covers/` (showcase) 13, `manga_covers/` 97, `manga_panels/` 60, `video_bank/` 3. |
| 3 | Pipeline examples | `artifacts/pipeline_examples/` | **34** | 13 per‑teacher demos + 12 `manga_book` + 9 `manga_covers` cross‑cut examples. |
| 4 | Manga rendered output | `artifacts/manga/` | **145** | 81 `anxiety_series` (Stillness Press EN), 61 `image_bank` (reusable BG/motif), 3 `stillness_press_qa_run`. |
| 5 | Onboarding proof media | `artifacts/onboarding_proof_media/images/` | **19** | Brand‑agnostic wizard comparison thumbnails (locale‑split: 1 jp, 1 tw, rest en). |
| 6 | **Manga catalog (discovered)** | `assets/manga_catalog/` | **6,074** | 25 brand directories, 4,610 LoRA refs + 1,228 protagonist `main_character.png` + 236 panels. **Not in dashboard's known SSOT** — must be picked up by ws_dashboard_image_inventory_consumer. |

> **Surface 6 caveat:** the operator prompt enumerated 5 surfaces; the audit revealed `assets/manga_catalog/` as the dominant surface (93 % of all PNGs). It is treated as a first‑class surface in the TSV and matrix; its discovery is itself a finding.

---

## 3. Asset‑type taxonomy

The user prompt's 8‑value asset_type vocabulary `{author_base, kdp_cover, audiobook_cover, manga_cover, manga_panel, pipeline_example, onboarding_proof, video_bank}` is extended with **6 manga_catalog‑specific types** to avoid information loss. The full taxonomy is normative in `docs/specs/IMAGE_ASSET_INVENTORY_V1_SPEC.md`.

| asset_type | Count | Surface | Definition |
|---|---:|---|---|
| `manga_lora_ref` | 4,610 | manga_catalog | Per‑series LoRA training reference views (`{front,three_quarter,profile}_view`, `expression_*`, `body_*`). |
| `manga_protagonist` | 1,228 | manga_catalog | `main_character.png` (1 per series — primary character portrait). |
| `manga_panel` | 296 | manga_catalog + brand_wizard | Story page panel (manga interior page). |
| `manga_cover` | 97 | brand_wizard | Manga cover variant (front / profile / scene / symbolic / three_quarter / portrait / topic). |
| `manga_render` | 81 | artifacts/manga | Anxiety‑series rendered output (Stillness Press EN). |
| `manga_image_bank` | 61 | artifacts/manga | Reusable BG / motif / character refs for the reuse‑before‑render pipeline. |
| `kdp_cover` | 52 | brand_wizard | KDP paperback / ebook front cover. |
| `pipeline_example` | 34 | artifacts/pipeline_examples | Cross‑cut pipeline demo images. |
| `onboarding_proof` | 19 | artifacts/onboarding_proof_media | Wizard comparison thumbnails. |
| `author_base` | 17 | assets/authors | Teacher identity portrait (locale‑agnostic). |
| `audiobook_cover` | 14 | brand_wizard | Audiobook square cover. |
| `showcase_cover` | 13 | brand_wizard | 1‑per‑teacher brand showcase cover. |
| `manga_qa_render` | 3 | artifacts/manga | QA‑run rendered output. |
| `video_bank` | 3 | brand_wizard | Brand‑agnostic video b‑roll thumbnail. |

---

## 4. Per‑brand × per‑locale matrix (compact)

Cells show **total PNG count** (real + LFS pointer). Color thresholds (informational): 🟢 ≥ 50, 🟡 1–49, 🔴 0.

> Full per‑asset‑type breakdown is in `image_asset_inventory_2026-05-09.tsv` (one row per file, 6,528 rows) and `image_asset_inventory_matrix_2026-05-09_aux.tsv` regeneration is documented under §7. The compact view below is the operator‑facing summary.

### 4.1 Flagship brands (3)

| brand_id | en_US | ja_JP | zh_TW | zh_CN | row total |
|---|---:|---:|---:|---:|---:|
| `stillness_press` | 🟢 1,144 | 🟢 551 | 🟢 192 | 🟢 204 | **2,091** |
| `cognitive_clarity` | 🟢 519 | 🟡 46 | 🟡 15 | 🟡 16 | **596** |
| `digital_ground` | 🟢 517 | 🟡 13 | 🟡 14 | 🟡 15 | **559** |

### 4.2 Core brands with content (8 / 16)

| brand_id | en_US | ja_JP | zh_TW | zh_CN | row total |
|---|---:|---:|---:|---:|---:|
| `sleep_restoration_iyashikei` | 🟢 275 | 🟡 16 | 🟡 16 | 🟡 17 | **324** |
| `somatic_wisdom_shojo` | 🟢 395 | 🟡 14 | 🟡 15 | 🟡 16 | **440** |
| `relational_calm_iyashikei` | 🟡 34 | 🟡 14 | 🟡 14 | 🟡 16 | **78** |
| `body_memory_shojo` | 🟡 32 | 🟡 14 | 🟡 15 | 🟡 16 | **77** |
| `night_reset_healing` | 🔴 0 | 🔴 0 | 🟡 15 | 🟡 15 | **30** |
| `gentle_growth_healing` | 🔴 0 | 🔴 0 | 🟡 14 | 🟡 13 | **27** |
| `stabilizer_healing` | 🔴 0 | 🔴 0 | 🟡 15 | 🟡 15 | **30** |
| `heart_balance_shojo` | 🟢 394 | 🟡 14 | 🟡 15 | 🟡 16 | **439** |

### 4.3 Niche brands with content (7 / 18)

| brand_id | en_US | ja_JP | zh_TW | zh_CN | row total |
|---|---:|---:|---:|---:|---:|
| `trauma_path_healing` | 🔴 0 | 🔴 0 | 🟡 28 | 🟡 27 | **55** |
| `devotion_path_shonen` | 🟢 396 | 🟡 14 | 🟡 14 | 🟡 13 | **437** |
| `warrior_calm_cultivation` | 🟢 201 | 🟢 156 | 🟢 168 | 🟢 168 | **693** |
| `solar_return_isekai` | 🟢 397 | 🟡 14 | 🟡 14 | 🟡 14 | **439** |
| `qi_foundation_cultivation` | 🟡 33 | 🟡 13 | 🟡 14 | 🟡 15 | **75** |
| `calm_student_school` | 🔴 0 | 🔴 0 | 🟡 14 | 🟡 14 | **28** |
| `bright_presence_tw_seinen` | 🔴 0 | 🔴 0 | 🟡 15 | 🔴 0 | **15** |

### 4.4 Brands with ZERO assets across all 4 locales (19 / 37) — 🔴 critical

| Tier | Brands |
|---|---|
| Core (8) | `healing_ground_healing`, `minimal_mind_healing`, `career_lift_workplace`, `high_performer_workplace`, `executive_calm_workplace`, `morning_momentum_workplace`, `optimizer_workplace`, `focus_sprint_workplace` |
| Niche (11) | `resilient_parent_social`, `confidence_core_romance`, `relationship_clarity_romance`, `adhd_forge_mystery`, `stoic_edge_battle`, `spiritual_ground_supernatural`, `legacy_builder_memoir`, `bio_flow_healing`, `longevity_lab_healing`, `hormone_reset_healing`, `creative_unfold_social` |

These 19 brands (51 % of the canonical set) have **no author base, no manga cover, no manga panel, no LoRA reference, and no pipeline example** in the repo. They are listed in `config/manga/canonical_brand_list.yaml` but have no concrete asset realization. **PR #972's `active_brand_classifier` already flags these as inactive** (0 active / 61 inactive at PR merge) — this audit corroborates that classification from the asset side.

### 4.5 Observed‑but‑non‑target locale: `ko_KR`

The TSV also contains **33 PNGs** in `ko_KR` (3 `digital_ground` series: `digground_kr_01/02/03`, mostly `manga_protagonist` + `manga_lora_ref`). `ko_KR` is **outside the Q3 4‑locale primary target** but is documented in `brand_lora_plans.protagonist_loras` (Korean characters Jieun, Junhyeok, Sumin). Treat as bonus inventory; do **not** include in the per‑locale 4‑column gap matrix.

---

## 5. Critical gap callouts

1. **🔴 19/37 brands are completely empty.** Cannot ship any worldwide catalog tile, manga preview, or wizard cover for these. Either: (a) downgrade them in `canonical_brand_list.yaml` (requires AMENDMENT), or (b) commit to LoRA training + asset generation per the parallel plan.
2. **🔴 `en_US`‑only depth across most brands.** Of the 18 brands with any content, 12 have full `en_US` set + only LoRA‑refs in other locales (no kdp/audiobook/manga_cover at JP/TW/CN). Localization parity requires **~14,400 covers** (12 brands × 4 locales × 800 covers Q3 baseline) once Pearl_Int Steps 3+4 unblock generation.
3. **🟡 `manga_lora_ref` saturation is uneven.** `stillness_press` has 1,570 LoRA refs (≈ 16 series × 10 refs × 4 locales rounded), while `relational_calm_iyashikei`, `body_memory_shojo`, `qi_foundation_cultivation` have **zero** in `en_US` (only `manga_protagonist`). LoRA training cannot complete on these brands without the reference pack.
4. **🟡 Author bases are stale and partial.** Only 10 of 17 author bases are >50 KB (real). The 7 stubs (`ajahn_x`, `diane_reyes`, `kai_nakamura`, `luna_hart`, `marcus_cole`, `master_sha`, `omote`) are placeholder pen names from the book pipeline; manga teachers `master_sha` and `omote` are real bindings but their bases need regeneration.
5. **🔴 No `audiobook_cover` outside `en_US`.** All 14 audiobook covers are en_US only. With CosyVoice2 audiobook expansion underway (per ACTIVE_WORKSTREAMS A2), JP/TW/CN audiobook covers are blocking the audio launch in non‑US markets.
6. **🔴 No `kdp_cover` outside `en_US`.** All 52 KDP covers are en_US. Same blocker as #5 for KDP localization.
7. **🟡 `bright_presence_tw_seinen` is asymmetric.** It has 15 PNGs in `zh_TW` (its native demographic) but **zero** in `zh_CN`, `ja_JP`, `en_US`. By design (TW market brand), but the dashboard should not flag this as a "gap" — it's intentional.

---

## 6. Per‑brand status (one row per active brand)

For brand × locale completeness percentages (vs. Q3 default targets), see `parallel_image_generation_plan_2026-05-09.md` §3.1. The completion percent is computed as: `Σ asset_count / Σ asset_target × 100` per cell.

**Headline:** even the most‑covered cell (`stillness_press × en_US`, 1,144 PNGs) is at **only ~17 % of target** (target ≈ 6,654: 800 kdp + 800 audiobook + 800×k manga panels + LoRA + showcase). Worldwide go‑live is **bottlenecked on Pearl_Int Steps 3+4**.

---

## 7. Re‑running this audit

This audit is reproducible without any state assumptions. To refresh:

```bash
# From repo root
python3 scripts/qa/scan_image_inventory.py \
  > artifacts/qa/image_asset_inventory_2026-05-09.tsv \
  2> artifacts/qa/image_asset_inventory_2026-05-09.summary.txt

python3 scripts/qa/build_image_matrix.py \
  --inventory artifacts/qa/image_asset_inventory_2026-05-09.tsv \
  --out artifacts/qa/image_asset_inventory_matrix_2026-05-09.tsv
```

> NOTE: The two scripts above are **proposed** to be added under `ws_image_inventory_audit_recurring_20260509`. This session generated the equivalent files via ad‑hoc Python (see `docs/specs/IMAGE_ASSET_INVENTORY_V1_SPEC.md` §6 for the canonical scanner pseudocode). Until the scripts land, this snapshot stands at audit date.

---

## 8. Findings → action items (named follow‑up workstreams)

| Workstream ID | Owner(s) | Summary | Depends on |
|---|---|---|---|
| `ws_image_inventory_audit_recurring_20260509` | Pearl_Editor | Weekly Monday cadence (matches WORLDWIDE-CATALOG-GO-LIVE Q5 weekly cadence). Re‑runs the scan + matrix + this MD. Output written to a dated copy under `artifacts/qa/`. Adds `scripts/qa/scan_image_inventory.py` + `scripts/qa/build_image_matrix.py`. | This audit landing on `main`. |
| `ws_dashboard_image_inventory_consumer_20260509` | Pearl_Brand | Implement the dashboard panel that reads `image_asset_inventory_<DATE>.tsv` + matrix and renders per‑active‑brand `locale × asset_type` cells with green/yellow/red status. Spec: `docs/specs/IMAGE_ASSET_INVENTORY_V1_SPEC.md` §5. | This audit on `main`; PR #977 `active_brand_panel` already shipped. |
| `ws_image_batch_generation_orchestration_20260509` | Pearl_Dev + Pearl_Int | Batch runner that consumes `parallel_image_generation_plan_2026-05-09.md` and dispatches to Pearl Star (Animagine + Qwen-Image). Wave‑based (W1→W4), single‑GPU sequential, stateful resume. | Pearl_Int Steps 3+4 (Animagine + Qwen-Image downloads, operator's parked `HF_TOKEN_STAGED` authorization). |
| **PREREQ** `Pearl_Int Steps 3+4` | Pearl_Int | Animagine + Qwen-Image model downloads on Pearl Star (RTX 5070 Ti) using parked `HF_TOKEN_STAGED`. Without this, all 19 zero‑content brands and all locale gaps remain blocked. | Operator authorization (parked, awaiting trigger). |

---

## 9. Out of scope (explicit)

- ❌ ANY image generation in this session (gated on Pearl_Int Steps 3+4).
- ❌ Modifying existing image files.
- ❌ Modifying `config/manga/canonical_brand_list.yaml` or `config/manga/brand_lora_plans.yaml` (cap drift).
- ❌ Implementing the dashboard inventory panel (named as `ws_dashboard_image_inventory_consumer_20260509`; separate session).
- ❌ Any change outside the 4 NEW files in this PR.

---

## 10. Cross‑references

- `docs/PEARL_ARCHITECT_STATE.md` — `WORLDWIDE-CATALOG-GO-LIVE-V1-PROGRAM-01` (Phase 1 P1 surface 2 + P2 surface 3); `TEACHER-MANGA-30S-VIDEO-V1-01` (12‑teacher binding ratified 2026‑05‑08).
- `BRAND_ADMIN_CANONICAL_PACKAGE.md` (lines 13–20) — Path X book vs. manga separation.
- `specs/AI_MANGA_PIPELINE_SUMMARY.md` — manga kernel reference.
- `docs/MANGA_IMPLEMENTATION_OUTLINE.md` — current implementation slice (kernel + retrieval‑first).
- `config/manga/canonical_brand_list.yaml` — 37‑brand canon.
- `config/manga/brand_lora_plans.yaml` — character + style + protagonist LoRA chains.
- `image_asset_inventory_2026-05-09.tsv` (companion file) — machine‑readable per‑PNG row.
- `parallel_image_generation_plan_2026-05-09.md` (companion file) — per‑gap‑cell generation plan.
- `docs/specs/IMAGE_ASSET_INVENTORY_V1_SPEC.md` (companion file) — schema + classification + dashboard contract.
