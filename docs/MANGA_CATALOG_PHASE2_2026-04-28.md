# Manga Catalog Phase 2 — zh_TW + zh_CN Materialization — 2026-04-28

**Scope:** Option A only — extend manga catalogs to all 4 locales by materializing plan §2.3 (zh_TW) and §2.4 (zh_CN) into [`config/manga/brand_genre_allocation.yaml`](../config/manga/brand_genre_allocation.yaml). T2/T3/T4/T5 from the original Phase 2 brief deferred — preconditions for those tasks (locale-native title_templates files, generator locale-aware loaders, `stillness_press.yaml` brand_portfolio_allocation profile, 21 new genre series YAMLs) **do not exist** in the repo as of branch state `42a9c8f2655b`. See `STARTUP_RECEIPT` exchange on PR #771 for the precondition audit.

**Authority:** [`docs/MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md`](MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md) §2.3 + §2.4
**Generator:** [`scripts/catalog/generate_manga_catalog.py`](../scripts/catalog/generate_manga_catalog.py) (extended in this drop, no new script)
**Outputs:** [`artifacts/catalog/manga/`](../artifacts/catalog/manga/) (4 CSVs now, was 2)

---

## TL;DR

All 4 manga catalogs are materialized. **880 series rows total**, **727 ready (82.6%)**, **153 blocked_lora** (5 zh-specific brands per Chinese locale + 1 Adi Da Taiwan-only brand have no `brand_style_loras` entries — surfaced honestly, not fabricated).

| Locale | Brands | Rows | Ready | Blocked (reason) |
|---|---:|---:|---:|---|
| en_US | 12 | 170 | 170 | 0 |
| ja_JP | 12 | 166 | 166 | 0 |
| **zh_TW** | **19** | **275** | **191** | **84 blocked_lora** |
| **zh_CN** | **18** | **269** | **200** | **69 blocked_lora** |
| **Total** |  | **880** | **727** | **153** |

zh_TW + zh_CN matrices use the same generator and schema as PR #771 — no new script, no schema change. The generator was extended in-place to handle the two new locales, the zh-specific brand teacher map, and a locale-suffix-strip fallback for shared brand styles (e.g. `stabilizer_tw` resolves to `brand_lora_plans.brand_style_loras.stabilizer (shared via locale-suffix strip)`).

---

## What changed

### Modified

- **[`config/manga/brand_genre_allocation.yaml`](../config/manga/brand_genre_allocation.yaml)** — added two new locale blocks (`allocations.zh_TW`, `allocations.zh_CN`) plus a `zh_specific_brand_teacher` map. All 61 brand-rows across 4 locales sum to exactly 100% (validated with python before write). zh_TW totals 19 brands (12 teacher + 6 zh-specific + 1 Adi Da Taiwan-only); zh_CN totals 18 brands (12 teacher + 6 zh-specific).

- **[`scripts/catalog/generate_manga_catalog.py`](../scripts/catalog/generate_manga_catalog.py)** — extended in-place (does NOT mutate `generate_full_catalog.py`):
  - `LOCALE_TO_MARKET` and `LOCALE_TO_NAMES_KEY` now include `zh_TW` / `zh_CN`.
  - `series_format()` adds locale-biased rules for zh_TW (webtoon-vertical primary, web_manga for tentpoles) and zh_CN (web_manga primary if/when manga lane access lands).
  - `index_brand_teacher()` now consumes the `zh_specific_brand_teacher` block from `brand_genre_allocation.yaml`, returning `{teacher_id, teacher_mode}` per brand. This is how the 6 zh-specific standard brands (per locale) and `bright_presence_tw` get their teacher resolution.
  - `lora_refs()` adds a locale-suffix-strip fallback: `_tw` / `_cn` / `_hk` / `_sg` brand suffixes try the base brand for `brand_style_loras` lookup. This means `stabilizer_tw` correctly resolves to `stabilizer`'s style LoRA.
  - `blockers` logic now distinguishes `needs_lora_plan` (no brand style) from `needs_character_lora` (no character LoRA for the teacher). New `readiness_status` value `blocked_character_lora` if the gap is character-side only.

### Outputs (regenerated for all 4 locales)

- [`artifacts/catalog/manga/en_US_manga_catalog.csv`](../artifacts/catalog/manga/en_US_manga_catalog.csv) — 170 rows (unchanged shape from PR #771)
- [`artifacts/catalog/manga/ja_JP_manga_catalog.csv`](../artifacts/catalog/manga/ja_JP_manga_catalog.csv) — 166 rows (unchanged shape)
- [`artifacts/catalog/manga/zh_TW_manga_catalog.csv`](../artifacts/catalog/manga/zh_TW_manga_catalog.csv) — **275 rows (new)**
- [`artifacts/catalog/manga/zh_CN_manga_catalog.csv`](../artifacts/catalog/manga/zh_CN_manga_catalog.csv) — **269 rows (new)**
- [`artifacts/catalog/manga/manga_catalog_summary.json`](../artifacts/catalog/manga/manga_catalog_summary.json) — now covers all 4 locales

---

## blocked_lora rows are honest, not bugs

The 153 blocked_lora rows surface a real production gap. `config/manga/brand_lora_plans.yaml` covers:

- **`brand_style_loras`** — 36 brand styles, including the 12 global teacher brands (`stillness_press`, `cognitive_clarity`, …) and the standard brands' base names (`stabilizer`, `bio_flow`, `night_reset`, …). It does NOT include locale-suffixed variants like `sleep_repair_tw` or new entries like `bright_presence_tw`.
- **`character_loras`** — 12 teachers (ahjan, joshin, junko, maat, master_feung, master_sha, master_wu, miki, omote, pamela_fellows, ra, sai_ma). It does NOT include `adi_da`.

What this means per row:

| Brand | LoRA resolution | Status |
|---|---|---|
| 12 global teacher brands × 4 locales | direct match in `brand_style_loras` | ✅ ready |
| `stabilizer_{tw,cn}` | resolved via locale-suffix strip → `stabilizer` | ✅ ready |
| `sleep_repair_{tw,cn}`, `panic_first_aid_{tw,cn}`, `gen_z_grounding_{tw,cn}`, `grief_companion_{tw,cn}`, `inner_security_{tw,cn}` | base name not in `brand_style_loras` | ❌ blocked_lora |
| `bright_presence_tw` | base name not in `brand_style_loras` AND `adi_da` not in `character_loras` | ❌ blocked_lora (with `needs_lora_plan;needs_character_lora`) |

**These 153 rows are not bugs in the catalog — they are production gaps the catalog correctly surfaces.** Closing them requires authoring 5 new `brand_style_loras` entries (sleep_repair, panic_first_aid, gen_z_grounding, grief_companion, inner_security), 1 new entry for `bright_presence_tw`, and 1 new `character_loras` entry for `adi_da`. That is a separate task on the operator's RunComfy harness — not catalog work.

---

## Format-split bias per locale

Per plan §4 + the locale-biased `series_format()` rule:

| Locale | print_manga | web_manga | webtoon_vertical |
|--------|------------:|----------:|-----------------:|
| en_US  |           0 |        40 |              130 |
| ja_JP  |          41 |        45 |               80 |
| zh_TW  |           0 |       (varies) | (varies) |
| zh_CN  |           0 |       (varies) | (varies) |

zh_TW lane biases toward webtoon-vertical (LINE Webtoon TW primary platform per `market_catalog_registry.yaml::taiwan.platform_strategy`), with web_manga reserved for tentpoles + ≥25% allocations (BookWalker TW collected volumes). zh_CN matches the same shape; the catalog documents design intent even though `catalog_generation_config.yaml::lane_content_mix.zh_CN` keeps manga at 0% mix today (regulatory access constraint).

---

## Tentpole reconciliation (carry-forward from PR #771)

Tentpole rule (option C — Coexist): `is_tentpole=true` iff row's genre matches the brand's mono-genre profile filename. Tentpole counts:

- en_US: 40 tentpole rows (unchanged)
- ja_JP: 39 tentpole rows (unchanged) — including the `warrior_calm × battle` mismatch already surfaced in PR #771 (matrix Primary = battle 25%, mono-genre = `warrior_calm_cultivation.yaml`). **Owner decision D1 still pending.**
- zh_TW: ~40 tentpole rows (12 teacher brands × 1–4 tentpole-genre rows each)
- zh_CN: ~40 tentpole rows

`bright_presence_tw` is the **only mecha-tentpole brand in any locale**. Its mono-genre profile is `bright_presence_tw_seinen.yaml`; the matrix Primary is mecha. There is no `bright_presence_tw_mecha.yaml` mono-genre file yet — surface this for owner as a follow-up authoring task.

---

## What was deferred from the original Phase 2 brief

| Task | Reason for deferral |
|---|---|
| **T2** — regenerate Pearl Prime catalogs against locale-native `title_templates.{locale}.yaml` | Files do not exist. Brief assumed they had landed; precondition audit found they had not. No commit history references them. Authoring 459 native-language title rows by hand is a content-authoring sprint, not a catalog-generator change. |
| **T3** — migrate 11 brands to `brand_portfolio_allocation` mirror of `stillness_press.yaml` | The reference template `stillness_press.yaml` does not exist either. Only `stillness_press_iyashikei.yaml` (the mono-genre file) is present. Migration without a reference shape is undefined. |
| **T4** — regenerate manga catalog after T3 | Transitively blocked. |
| **T5** — top-50 launch-ready list per locale | Without T2 (locale-native titles), the non-en_US top lists would be either blank or saturated by the 47×-duplicated en_US title pool. Not useful until T2 lands. |
| **D1** — ja_JP `warrior_calm` tentpole mismatch decision | Owner has not chosen between A/B/C. Carries over from PR #771. |

---

## Reproduction

```bash
python3 scripts/catalog/generate_manga_catalog.py \
  --locales en_US,ja_JP,zh_TW,zh_CN \
  --output-dir artifacts/catalog/manga/
```

The generator is deterministic given identical input file contents. `manga_catalog_summary.json::source_files` records SHA-256 fingerprints of all eight inputs.

---

## Hard-rule compliance checklist (per dev brief)

- ✅ No paid LLM calls — series_title is blank with `needs_title_synthesis_locale_native`
- ✅ No book assembly, manga rendering, ComfyUI, LoRA training, images
- ✅ No `--admin` merge, no `--no-verify`
- ✅ Branch from `origin/main` (base `e2b4b3198b`)
- ✅ Used existing infrastructure — extended `generate_manga_catalog.py` in place; did NOT fork or duplicate
- ✅ Push-guard + preflight + governance + LLM audit run before push

---

## NEXT_ACTION (post-merge)

1. **Owner sign-off on tentpole_mismatch (D1, still pending from PR #771).**
2. **LoRA plan authoring** — 6 brand styles (sleep_repair, panic_first_aid, gen_z_grounding, grief_companion, inner_security, bright_presence_tw) + 1 character LoRA (adi_da). Closes 153 blocked_lora rows. RunComfy harness, not catalog CI.
3. **Mono-genre profile for `bright_presence_tw_mecha.yaml`** — current file is `bright_presence_tw_seinen.yaml` (seinen is a demo, not a genre); the brand's tentpole genre per the matrix is mecha.
4. **Phase 2 proper** — author the missing `title_templates.{en_US,ja_JP,zh_TW,zh_CN}.yaml` (153 entries each) before retrying T2/T3/T4/T5 from the original Phase 2 brief. The original brief's "✅ landed" status was incorrect; treat that work as not-yet-done.
