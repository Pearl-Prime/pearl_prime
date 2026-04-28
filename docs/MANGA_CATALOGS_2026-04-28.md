# Manga Catalogs — en_US + ja_JP — 2026-04-28

**Status:** materialized.
**Authority:** [`docs/MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md`](MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md) §2.1, §2.2, §3, §5
**Generator:** [`scripts/catalog/generate_manga_catalog.py`](../scripts/catalog/generate_manga_catalog.py)
**Outputs:** [`artifacts/catalog/manga/`](../artifacts/catalog/manga/)

---

## TL;DR

Two manga catalogs materialized: **en_US (170 rows) + ja_JP (166 rows) = 336 series rows**, all `readiness_status=ready`. No ComfyUI runs, no LoRA training, no volume assembly, no LLM calls. Series titles are intentionally blank with `needs_title_synthesis_locale_native` per the same title-policy rule as the Pearl Prime book script catalogs.

zh_TW + zh_CN matrices exist in the plan (§2.3, §2.4) but are not materialized in this drop per task scope.

---

## Per-locale breakdown

| Locale | Brands | Series rows | Tentpole rows | Format split (print/web/vertical) | All ready? |
|--------|-------:|------------:|--------------:|-----------------------------------|-----------|
| en_US  |     12 |         170 |            40 | 0 / 40 / 130                       | ✅ 170/170 |
| ja_JP  |     12 |         166 |            39 | 41 / 45 / 80                       | ✅ 166/166 |
| **Total** |    |     **336** |        **79** | 41 / 85 / 210                      | ✅         |

Per-brand series counts cluster around 13–15 (each brand has ~12 non-zero genre cells whose percentages sum to 100%, producing `sum(round(pct/10))` ≈ 14 series per brand on average).

---

## Series count derivation

For each `(brand, genre)` cell with `allocation_pct > 0`:
`series_count = max(1, round(allocation_pct / 10))`.

Example — en_US `stillness_press` (12 cells, sum=100%):

| Genre | Allocation | Series rows |
|---|---:|---:|
| healing (tentpole) | 40% | 4 |
| essay | 12% | 1 |
| slice_of_life | 10% | 1 |
| memoir | 8% | 1 |
| supernatural_everyday | 5% | 1 |
| graphic_medicine | 5% | 1 |
| school | 4% | 0 → floored to 1 |
| family | 4% | 0 → floored to 1 |
| romance | 3% | 0 → floored to 1 |
| comedy | 3% | 0 → floored to 1 |
| mystery | 3% | 0 → floored to 1 |
| workplace | 3% | 0 → floored to 1 |
| **Total** | **100%** | **15** |

The `max(1, ...)` floor ensures every non-zero cell gets at least one series row; the bulk of the volume goes to the tentpole and high-allocation cells (40% → 4 series; 30% → 3 series; 15% → 2 series after rounding).

---

## Format-split bias per locale

Per plan §4:

| Locale | print_manga | web_manga | webtoon_vertical |
|--------|------------:|----------:|-----------------:|
| en_US  |           0 |        40 |              130 |
| ja_JP  |          41 |        45 |               80 |

- **en_US** — no print_manga (the en_US lane content mix is webtoon-primary + KDP graphic-novel EPUB; physical print-manga is not the primary surface).
- **ja_JP** — heavy print_manga share for tentpoles + ≥25% allocations (tankōbon route via `manga_app_partners` + `physical_doujin` per `market_catalog_registry.yaml::japan.business_tracks.manga_partnership`); web_manga for mid-allocation cells; webtoon_vertical for tertiary 1–8% cells.

The format assignment rule is encoded in [`scripts/catalog/generate_manga_catalog.py:series_format`](../scripts/catalog/generate_manga_catalog.py).

---

## Tentpole reconciliation (option C — Coexist)

Per plan §3, the mono-genre profile in `config/source_of_truth/manga_profiles/brands/{brand}_{genre}.yaml` is the brand's **tentpole / signature series**, while the matrix is the brand's **portfolio mix**. The catalog row's `is_tentpole=true` iff the row's genre matches the brand's mono-genre filename's genre.

### Tentpole mismatches (surface for owner)

| Locale | Brand        | Matrix Primary | Tentpole (mono-genre) | Affected rows | Recommended action |
|--------|--------------|----------------|-----------------------|---------------|--------------------|
| ja_JP  | warrior_calm | battle (25%)   | cultivation           | 2 series rows | Re-author mono-genre to `warrior_calm_battle.yaml` for ja_JP locale, OR rebalance ja_JP matrix so cultivation ≥ battle. |

This is a planning issue, not a render-readiness issue — both rows are emitted with `readiness_status=ready` and a `tentpole_mismatch` flag in `notes`.

---

## Data gaps surfaced + filled in this drop

The first generator pass produced **71 blocked rows** (en_US) due to two upstream data gaps. Both were closed inside `config/manga/canonical_genre_list.yaml` (no upstream taxonomy/pacing mutations):

1. **`family` genre had no pacing_proxy** → 7 rows blocked_pacing.
   Fix: added `pacing_proxy: social_issue` to the `family` row.
2. **9 pacing-only canonical genres + `cultivation` had no engine data** in `manga_taxonomy.yaml::genre_families`. The taxonomy is incomplete for: `mecha`, `dark_fantasy`, `sci_fi_cyberpunk`, `supernatural_everyday`, `school`, `memoir`, `social_issue`, `graphic_medicine`, `battle_internal`, plus `cultivation` (which has visual_grammars but no emotional_engines).
   Fix: added `taxonomy_fallback` block to `canonical_genre_list.yaml` with curated `default_visual_grammars` / `default_emotional_engines` / `default_serialization_engines` per genre. Generator consults taxonomy first, falls through to `taxonomy_fallback` for residual gaps.

After both fixes: **0 blocked rows** across both catalogs.

The fallback engine choices in `taxonomy_fallback` are derived from each pacing row's `reference_corpus` + canonical reader-promise framing per genre. They are intended as a working baseline; if `manga_taxonomy.yaml` is later extended to include these 10 genres natively, the generator will prefer the taxonomy entry and the fallback block can be retired.

---

## Genre coverage

| Locale | Distinct genres covered |
|--------|------------------------:|
| en_US  | 24 of 25 canonical genres |
| ja_JP  | 23 of 25 canonical genres |

Genres NOT covered in either locale: a small residual set (e.g. `procedural`, `food` may appear only in zh_TW/zh_CN matrices). All user-required genres are present in both locales: `mecha` (warrior_calm, solar_return, digital_ground × ja_JP), `horror` (digital_ground), `fantasy_adventure` (multiple brands), `dark_fantasy` (warrior_calm, solar_return, devotion_path), `sci_fi_cyberpunk` (digital_ground, solar_return).

---

## Pipeline route note

`pipeline_route` is set to `MANGA_PIPELINE_TBD — see docs/MANGA_CATALOG_PLAN_EN_US_JA_JP_ZH_TW_ZH_CN_2026-04-28.md §7` on every row.

The Pearl Prime spine pipeline (`scripts/run_pipeline.py --pipeline-mode spine`) handles **book scripts**, not manga. Manga rendering is a separate pipeline that does not exist yet — when it lands (covering panel composition, LoRA-conditioned generation, volume assembly), this column will be updated by re-running the generator.

This is the same shape as the rendering-out-of-scope rule for the Pearl Prime catalogs.

---

## What did NOT happen in this drop

Explicit per the task brief:

- ❌ ComfyUI runs (no images, no panels, no pages)
- ❌ LoRA training (refs only)
- ❌ Book / volume assembly (no manuscripts, no chapters)
- ❌ LLM calls (titles intentionally blank with `needs_title_synthesis_locale_native`)
- ❌ Manga rendering pipeline invocation (none exists yet)
- ❌ zh_TW / zh_CN catalogs (in the plan, not materialized)

What DID happen:

- ✅ 336 deterministic catalog rows produced from existing config authorities
- ✅ Two upstream data gaps closed inside `canonical_genre_list.yaml`
- ✅ All rows resolve to a complete `(visual_grammar, emotional_engine, serialization_engine, pacing_profile_ref, lora_plan_ref, character_pipeline_ref)` tuple
- ✅ One tentpole-mismatch surfaced for owner decision
- ✅ Schema matches plan §5 (23 columns, fixed order)

---

## Reproduction

```bash
python3 scripts/catalog/generate_manga_catalog.py \
  --locales en_US,ja_JP \
  --output-dir artifacts/catalog/manga/
```

Source SHA-256 fingerprints recorded in
[`artifacts/catalog/manga/manga_catalog_summary.json`](../artifacts/catalog/manga/manga_catalog_summary.json).

---

## Files added

| Path                                                    | Purpose                                          |
|---------------------------------------------------------|--------------------------------------------------|
| `config/manga/brand_genre_allocation.yaml`              | Materialized matrix (plan §2.1 + §2.2)           |
| `config/manga/canonical_genre_list.yaml`                | (modified) added family pacing_proxy + taxonomy_fallback |
| `scripts/catalog/generate_manga_catalog.py`             | Deterministic wrapper generator                   |
| `artifacts/catalog/manga/en_US_manga_catalog.csv`       | 170 series rows                                   |
| `artifacts/catalog/manga/ja_JP_manga_catalog.csv`       | 166 series rows                                   |
| `artifacts/catalog/manga/manga_catalog_summary.json`    | Aggregated totals + source SHA-256 fingerprints   |
| `artifacts/catalog/manga/README.md`                     | Schema reference                                  |
| `docs/MANGA_CATALOGS_2026-04-28.md`                     | This document                                     |

---

## Suggested next steps

1. **Owner sign-off on tentpole_mismatch** — decide whether `warrior_calm_battle_*` rows in ja_JP should keep cultivation as tentpole (rebalance matrix) or shift tentpole to battle (re-author mono-genre profile).
2. **Materialize zh_TW + zh_CN catalogs** — the matrices are already in plan §2.3 / §2.4; extending `brand_genre_allocation.yaml` with two more locale blocks reuses the same generator with no further code change.
3. **Locale-native title authoring** — author `series_title` synthesis files (no LLM) so series can become listing-ready.
4. **LoRA plan extension** — `brand_lora_plans.yaml` covers brand styles + character LoRAs, but does not yet have per-genre style overrides (e.g. mecha-specific prompt scaffolding for `bright_presence_tw`'s upcoming mecha tentpole). Owner decision Q-M3 from the plan still open.
5. **Manga rendering pipeline scoping** — `pipeline_route` is `MANGA_PIPELINE_TBD`. Defining the rendering route is its own scoping task and is required before any of these series can actually produce panels.
