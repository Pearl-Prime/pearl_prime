# Catalog Planning Status Per Market — 2026-05-11

**Owner:** Pearl_PM
**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2)
**Subsystem:** pearl_pm coordination
**Mode:** read-only audit; this doc is the only file written.
**Audit base:** `origin/main` snapshot at branch creation (`agent/catalog-planning-status-2026-05-11`).

---

## 1. TL;DR (one line per market + parallel + podcast)

- **en_US (regular worldwide):** **PARTIAL** — book-script + manga catalog rows exist for 12/37 brands; weekly-volume SSOT is generic across all 37 (locale dimension deferred to V1.1).
- **ja_JP (regular worldwide):** **PARTIAL** — same 12/37 brand coverage as en_US in book + manga catalogs; Phoenix-cell worldwide plan TSV present.
- **zh_TW (regular worldwide):** **PARTIAL** — book + manga catalogs cover 19/37 brands (12 teacher + 6 zh-specific + `bright_presence_tw`); manga has 84 `blocked_lora` rows.
- **zh_CN (regular worldwide):** **PARTIAL** — book + manga catalogs cover 18/37 brands (12 teacher + 6 zh-specific); manga has 69 `blocked_lora` rows.
- **Japan-manga-only parallel catalog:** **NO** — cap is **active** (AMENDMENT-2026-05-11) and spec is binding, but **zero artifact rows exist**; generator branch + per-brand × series × episode plan are named workstreams not yet started.
- **Podcast (separate planning track, NOT a Phoenix cell):** **PARTIAL** — per-market planning configuration exists for 16 markets (incl. all 4 audited), but **no per-brand × series row catalog** has been generated; weekly-volume SSOT records `podcast: 0/week` for all 37 brands pending operator Table 6 ratification.

---

## 2. Status matrix

| Market | Brand coverage (X/37) | Book series per brand (book script catalog) | Manga series per brand (manga catalog) | Podcast plan | Status verdict |
|---|---|---|---|---|---|
| en_US | **12/37** ([catalog](../catalog/pearl_prime_book_script_catalogs/en_US_catalog.csv), [README](../catalog/pearl_prime_book_script_catalogs/README.md) §brand counts) | n/a — book pipeline is Pearl Prime 12×10×5 row-grain (`(brand, topic, persona)` triples). **1478 rows / 12 brands ≈ 123 rows/brand**, all `ready` ([summary](../catalog/pearl_prime_book_script_catalogs/catalog_summary.json)) | **13–15 series/brand** (170 rows / 12 brands; 0 blocked) ([summary](../catalog/manga/manga_catalog_summary.json), [README](../catalog/manga/README.md)) | Per-market podcast plan exists (`en_us` block in [config/podcast/brand_podcast_plans.yaml](../../config/podcast/brand_podcast_plans.yaml)); no per-brand catalog rows generated | **PARTIAL** |
| ja_JP | **12/37** ([catalog](../catalog/pearl_prime_book_script_catalogs/ja_JP_catalog.csv); [worldwide TSV](../catalog/worldwide_catalog_plan_ja_JP_2026-05-10.tsv) lists all 37 at the planning header level) | 1478 rows / 12 brands ≈ **123 rows/brand**, all `ready` | **13–16 series/brand** (166 rows / 12 brands; 0 blocked) | `ja_jp` plan in [brand_podcast_plans.yaml](../../config/podcast/brand_podcast_plans.yaml) (4 series/brand/yr × 8 ep = 32 ep/yr); no rows yet | **PARTIAL** |
| zh_TW | **19/37** (12 teacher + 6 zh-specific + `bright_presence_tw`) ([catalog](../catalog/pearl_prime_book_script_catalogs/zh_TW_catalog.csv), [README](../catalog/pearl_prime_book_script_catalogs/README.md) §brand counts) | 2818 rows / 19 brands ≈ **148 rows/brand**; **160 `blocked_score`** rows (needs scoring) | **13–16 series/brand** (275 rows / 19 brands; **84 `blocked_lora`**) | `zh_tw` plan in [brand_podcast_plans.yaml](../../config/podcast/brand_podcast_plans.yaml) (Tier 3); no rows yet | **PARTIAL** |
| zh_CN | **18/37** (12 teacher + 6 zh-specific) ([catalog](../catalog/pearl_prime_book_script_catalogs/zh_CN_catalog.csv), [README](../catalog/pearl_prime_book_script_catalogs/README.md) §brand counts) | 2630 rows / 18 brands ≈ **146 rows/brand**, all `ready` | **13–17 series/brand** (269 rows / 18 brands; **69 `blocked_lora`**) | `zh_cn` plan in [brand_podcast_plans.yaml](../../config/podcast/brand_podcast_plans.yaml) (Tier 3, 知识付费 monetization); no rows yet | **PARTIAL** |

**Cross-market notes**

- **Brand denominator (37/37):** authoritative source is [`config/manga/canonical_brand_list.yaml`](../../config/manga/canonical_brand_list.yaml) — confirmed `total_brands: 37` (3 flagship + 16 core + 18 niche). Path X canon, governing spec [`specs/MANGA_CATALOG_RECONCILIATION_SPEC.md`](../../specs/MANGA_CATALOG_RECONCILIATION_SPEC.md).
- **Book-pipeline brand denominator divergence:** the Pearl Prime book script catalog is intentionally narrower than Path X — it consumes the **12 teacher brand archetypes** ([`config/catalog_planning/teacher_brand_archetypes.yaml`](../../config/catalog_planning/teacher_brand_archetypes.yaml)), plus zh-specific extensions per [`brand_teacher_matrix_zh.yaml`](../../config/catalog_planning/brand_teacher_matrix_zh.yaml) and `bright_presence_tw`. Treat the X/37 ratio as the **manga-plane gap surface**, not as a book-pipeline regression.
- **Manga-catalog brand-coverage gap (25 brands missing):** the same 12-brand teacher subset feeds the manga catalog generator today; the remaining 25 of 37 Path X brands (e.g., `iyashikei` core brands beyond `sleep_restoration_iyashikei`, the workplace cluster, niche brands like `adhd_forge_mystery`, `legacy_builder_memoir`, `bio_flow_healing`, etc.) have **no manga rows in any locale**. Brand × genre allocation matrix ([`config/manga/brand_genre_allocation.yaml`](../../config/manga/brand_genre_allocation.yaml)) and per-brand cadence ([`config/manga/manga_brand_series_plan.yaml`](../../config/manga/manga_brand_series_plan.yaml)) need extension to drive the missing 25.
- **Worldwide planning TSVs (Phoenix-cell layer):** [`worldwide_catalog_plan_{en_US,ja_JP,zh}_2026-05-10.tsv`](../catalog/) cover all 37 brand_ids at the **planning header** grain (per-brand: `series_count`, `manga_episodes`, `podcast_episodes`, `parallel_japan_manga_only_cells`); the row-level book + manga catalogs above are the **execution-grain** subset (12 / 19 / 18 brands as actually generated).

---

## 3. Plain-English answer per market

### en_US (regular worldwide) — PARTIAL

The English-global lane has the cleanest catalog state of the four: 1,478 Pearl Prime book script rows (all `ready`, no scoring blockers, 12 teacher brands, ~123 rows/brand) plus 170 manga series rows (all `ready`, ~14 series/brand across 12 brands and 24 distinct genre lanes). What's missing is **Path X breadth** — 25 of the 37 manga canon brands have no rows in either catalog, because the generator currently consumes the 12-brand teacher archetypes and the brand × genre allocation matrix isn't materialized for the other brands. Marketing volume SSOT ([`config/marketing/weekly_volumes_per_brand.yaml`](../../config/marketing/weekly_volumes_per_brand.yaml)) is generic across all 37 brands and uniform (manga: 1/wk; ebook/audiobook/podcast/video/shorts: 0/wk), so en_US per-locale tuning is deferred to V1.1. Sources: [`pearl_prime_book_script_catalogs/catalog_summary.json`](../catalog/pearl_prime_book_script_catalogs/catalog_summary.json), [`manga/manga_catalog_summary.json`](../catalog/manga/manga_catalog_summary.json), [`README.md`](../catalog/pearl_prime_book_script_catalogs/README.md), [`README.md`](../catalog/manga/README.md).

### ja_JP (regular worldwide) — PARTIAL

ja_JP mirrors en_US at the row level (1,478 book rows / 12 brands, all `ready`; 166 manga series / 12 brands, all `ready`) and adds a Phoenix-cell **planning** TSV ([`worldwide_catalog_plan_ja_JP_2026-05-10.tsv`](../catalog/worldwide_catalog_plan_ja_JP_2026-05-10.tsv)) that enumerates all 37 brand_ids with `manga_series`, `manga_episodes`, `podcast_episodes`, and the `parallel_japan_manga_only_cells` annotation. The same 25-brand execution gap as en_US applies. There is **one outstanding tentpole reconciliation** flagged for `warrior_calm` (matrix Primary = `battle 25%` vs mono-genre tentpole = `cultivation`), 2 series rows tagged `tentpole_mismatch` per [`manga/README.md`](../catalog/manga/README.md) §Tentpole reconciliation. Podcast plan for `ja_jp` is configured (4 series/brand/yr × 8 ep, ambient music, ja-JP voice with teineigo register) but **no podcast catalog rows exist**. Japan also carries a parallel program — see §4 below.

### zh_TW (regular worldwide) — PARTIAL

zh_TW is the broadest at the brand-list level (**19/37**: 12 teacher + 6 zh-specific + `bright_presence_tw`) and the largest by row count (2,818 book rows; 275 manga series). It is also the **most blocked**: 160 `blocked_score` book rows (composite scoring data missing — preserved per "needs_score, do not invent confidence" rule) and **84 `blocked_lora` manga rows** (LoRA plans not yet authored for several zh_TW brand × genre cells in [`config/manga/brand_lora_plans.yaml`](../../config/manga/brand_lora_plans.yaml)). Marketing weekly-volume SSOT does not differentiate zh_TW from other locales (generic per-brand map). Podcast plan exists in Tier 3 (`zh_tw` block of [`brand_podcast_plans.yaml`](../../config/podcast/brand_podcast_plans.yaml), warm casual register, KKBox/SoundOn/Firstory distribution); no rows generated. Sources: [`catalog_summary.json`](../catalog/pearl_prime_book_script_catalogs/catalog_summary.json), [`manga_catalog_summary.json`](../catalog/manga/manga_catalog_summary.json).

### zh_CN (regular worldwide) — PARTIAL

zh_CN covers **18/37 brands** (12 teacher + 6 zh-specific; no `bright_presence_tw` Taiwan-only brand). Book script catalog: 2,630 rows, all `ready`, no scoring blockers (better than zh_TW's 160 `blocked_score`). Manga catalog: 269 series / 18 brands with **69 `blocked_lora`** rows — same root cause as zh_TW (LoRA plan coverage). Podcast plan in [`brand_podcast_plans.yaml`](../../config/podcast/brand_podcast_plans.yaml) (`zh_cn` Tier 3) carries China-specific constraints captured in config: Ximalaya direct upload (no RSS), 知识付费 model (RMB 99–199/series, 50–70% revenue share), formal credentials required for psychology content (Oct 2025 regulation), AI-audio labeling (March 2025 regulation), Findaway not available. **No podcast or audiobook catalog rows generated**; weekly-volume SSOT generic across locales.

---

## 4. Japan-manga-only parallel catalog — NO data; cap ACTIVE

**Cap status:** **active** per [`docs/PEARL_ARCHITECT_STATE.md`](../../docs/PEARL_ARCHITECT_STATE.md) §`JAPAN-MANGA-ONLY-CATALOG-V1-01` — `proposed → active` after AMENDMENT-2026-05-11 (operator Q1–Q4 ratified binding answers).

**Spec status:** binding — [`docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md`](../../docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md) AMENDMENT-2026-05-11.

**Implementation status:** **none yet.** Glob search for `artifacts/catalog/japan_manga*` and `artifacts/**/JAPAN_MANGA*` returns **only the spec doc** — there are no `.csv`, `.tsv`, `.yaml` row artifacts under `artifacts/catalog/`, `artifacts/manga/`, or `artifacts/qa/` for the parallel program.

**Operator decisions (binding):**

| Q | Answer | Implication |
|---|---|---|
| Q1 | **identical** | Same 37 brand_ids as regular Path X canon — no `canonical_brand_list.yaml` fork. |
| Q2 | **higher** | Default planning multiplier 2–3× regular `ja_JP` manga share per brand; cell envelope stays 37 (one per brand). |
| Q3 | **separate** | Distinct Japanese-only brand-admin wizard (manga fields only; Line Manga / JP platforms). |
| Q4 | **Phase-2-parallel** | Build alongside V1.1 worldwide; **not** gated on V1 worldwide ship. |

**Named (not yet executed) workstreams** — per spec §AMENDMENT-2026-05-11 and PEARL_ARCHITECT_STATE.md §JAPAN-MANGA-ONLY-CATALOG-V1-01 §5:

- `ws_japan_manga_only_catalog_scoping_20260510` (Pearl_PM + Pearl_Marketing) — **runnable**, not run.
- `ws_japan_manga_only_platform_contract_research_20260510` (Pearl_Research) — **runnable**, not run.
- `ws_japan_manga_only_brand_admin_separate_wizard_20260511` (Pearl_Brand) — **runnable**, not run.
- `ws_japan_manga_only_phase_2_parallel_kickoff_20260511` — **runnable**, not run.
- `ws_japan_manga_only_legal_entity_decision_20260510` — **operator_pending** (counsel).

**Verdict:** **NO** data exists yet for the Japan-manga-only parallel catalog. Cap, spec, and operator answers are in place; per-brand × series × episode plan and the catalog generator's `japan_manga_only` branch are named follow-ups (Pearl_PM + Pearl_Marketing for the plan; Pearl_Dev for the generator branch, modeled on `music_mode_branch.py` from #1008 per spec).

---

## 5. Podcast planning — PARTIAL (separate planning track, not a Phoenix cell)

Per [`docs/PEARL_ARCHITECT_STATE.md`](../../docs/PEARL_ARCHITECT_STATE.md) Phase 2 scope: *"Audiobook ships via Google Play brand admin (not a Phoenix cell). Podcast remains a **separate planning track**."*

**What exists:**

- [`config/podcast/brand_podcast_plans.yaml`](../../config/podcast/brand_podcast_plans.yaml) — per-market plans for 16 markets across Tier 1/2/3, including all four audited markets (`en_us`, `ja_jp`, `zh_cn`, `zh_tw`) plus `es_latam`, `pt_br`, `ko_kr`, `id_id`, `de_de`, `es_es`, `fr_fr`, `vi_vn`, `th_th`, `tl_ph`, `hi_in`, `ar_sa`. Each market block specifies platforms, episode length, cadence, content framing, voice strategy (provider/locale/gender), music style, monetization model, video variant flag, `series_per_brand_year`, `episodes_per_series`, `estimated_total_episodes_year`, `estimated_audio_hours_year`, and platform-specific special requirements (e.g., Podbbang for `ko_kr`, Ximalaya for `zh_cn`, Noice for `id_id`).
- [`config/podcast/podcast_format.yaml`](../../config/podcast/podcast_format.yaml) — render-format spec.
- Worldwide planning TSVs ([`worldwide_catalog_plan_{en_US,ja_JP,zh}_2026-05-10.tsv`](../catalog/)) include a `podcast_episodes` column per-brand (e.g., `stillness_press` ja_JP = 26 podcast_episodes).
- [`pearl_news/`](../../pearl_news/) (730+ teacher×topic pack files) — Pearl News is a separate scheduled pipeline (Tier 2 LLM), not a podcast planning surface.

**What does NOT exist:**

- Per-brand × series × episode podcast catalog rows analogous to `pearl_prime_book_script_catalogs/` or `artifacts/catalog/manga/`. No podcast `.csv` / `.tsv` row artifact under `artifacts/catalog/`.
- Operator-ratified weekly podcast volumes — [`config/marketing/weekly_volumes_per_brand.yaml`](../../config/marketing/weekly_volumes_per_brand.yaml) records `podcast: 0/week` for all 37 brands as a V1 baseline awaiting Table 6 ratification.

**Verdict:** **PARTIAL** — strong per-market planning configuration (16 markets, voice/platform/monetization/regulatory detail captured); no per-brand row catalog generated yet; weekly-volume SSOT zeroed pending operator commitments.

---

## 6. Audit anchors (citations)

- Brand canon (37): [`config/manga/canonical_brand_list.yaml`](../../config/manga/canonical_brand_list.yaml) (`total_brands: 37`, schema_version 1, last_updated 2026-04-27).
- Book script catalogs (4 markets): [`artifacts/catalog/pearl_prime_book_script_catalogs/`](../catalog/pearl_prime_book_script_catalogs/) — `en_US_catalog.csv`, `ja_JP_catalog.csv`, `zh_TW_catalog.csv`, `zh_CN_catalog.csv`, `catalog_summary.json`, `README.md`.
- Manga catalogs (4 markets): [`artifacts/catalog/manga/`](../catalog/manga/) — `en_US_manga_catalog.csv`, `ja_JP_manga_catalog.csv`, `zh_TW_manga_catalog.csv`, `zh_CN_manga_catalog.csv`, `manga_catalog_summary.json`, `README.md`.
- Worldwide planning TSVs (Phoenix-cell header grain, 37 brands × per-locale plan numbers): [`artifacts/catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv`](../catalog/worldwide_catalog_plan_en_US_2026-05-10.tsv), [`artifacts/catalog/worldwide_catalog_plan_ja_JP_2026-05-10.tsv`](../catalog/worldwide_catalog_plan_ja_JP_2026-05-10.tsv), [`artifacts/catalog/worldwide_catalog_plan_zh_2026-05-10.tsv`](../catalog/worldwide_catalog_plan_zh_2026-05-10.tsv).
- Marketing volume SSOT: [`config/marketing/weekly_volumes_per_brand.yaml`](../../config/marketing/weekly_volumes_per_brand.yaml) (status: draft; generic per-brand; awaits operator Table 6 ratification + V1.1 locale modeling).
- Spec: [`docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md`](../../docs/specs/PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md), [`docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md`](../../docs/specs/MARKETING_VOLUME_SSOT_V1_SPEC.md), [`docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md`](../../docs/specs/JAPAN_MANGA_ONLY_CATALOG_V1_SPEC.md).
- Architect state: [`docs/PEARL_ARCHITECT_STATE.md`](../../docs/PEARL_ARCHITECT_STATE.md) — Phase 2 scope (cell math = 222 + 37 = 259); cap entry `JAPAN-MANGA-ONLY-CATALOG-V1-01` (active).
- Podcast planning: [`config/podcast/brand_podcast_plans.yaml`](../../config/podcast/brand_podcast_plans.yaml), [`config/podcast/podcast_format.yaml`](../../config/podcast/podcast_format.yaml).

---

## 7. Recommended follow-ups (not actioned in this PR)

1. **Brand-coverage gap (25/37 unmapped to manga rows):** open a workstream to extend [`config/manga/brand_genre_allocation.yaml`](../../config/manga/brand_genre_allocation.yaml) and the manga catalog generator to cover the remaining 25 of 37 Path X brands across all 4 markets.
2. **`zh_TW` book scoring (160 `blocked_score`):** populate missing scoring data in [`config/catalog_planning/teacher_topic_persona_scores.yaml`](../../config/catalog_planning/teacher_topic_persona_scores.yaml) for the affected zh-specific brands; re-emit catalog.
3. **`zh_TW` + `zh_CN` manga LoRA blockers (84 + 69 rows):** author missing entries in [`config/manga/brand_lora_plans.yaml`](../../config/manga/brand_lora_plans.yaml) for zh-specific brands; re-emit manga catalog.
4. **Locale-aware marketing-volume SSOT (V1.1):** extend [`config/marketing/weekly_volumes_per_brand.yaml`](../../config/marketing/weekly_volumes_per_brand.yaml) schema to add a `locale` dimension so per-market commitments (en_US vs zh_CN, regular ja_JP vs Japan-manga-only) can be expressed.
5. **Japan-manga-only kickoff:** advance the four `runnable` workstreams (scoping, platform research, separate wizard, Phase-2 parallel kickoff) and open the Pearl_Dev workstream for the catalog generator's `japan_manga_only` branch (modeled on `music_mode_branch.py`).
6. **Podcast row catalog:** decide whether to materialize per-brand × series × episode podcast row artifacts under `artifacts/catalog/podcast/` analogous to the book-script and manga catalogs, or keep it at the current per-market plan + per-brand TSV header grain only.
