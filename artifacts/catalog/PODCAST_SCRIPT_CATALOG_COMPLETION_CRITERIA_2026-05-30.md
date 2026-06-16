# Podcast Script Catalog — Completion Criteria

**Authority:** Pearl_Prime (planning artifact)  
**Date:** 2026-05-30  
**Companion data:** `artifacts/catalog/podcast_script_catalog_plan_2026-05-30.tsv`

---

## Definition: brand has full podcast script catalog planned

A brand (`brand_id` from `config/manga/canonical_brand_list.yaml`) is **catalog-planned** when **all** of the following hold for at least one in-scope locale (`en_US`, `ja_JP`, `ko_KR`, `zh_CN`, `zh_TW`):

| # | Requirement | Source / validation |
|---|-------------|---------------------|
| 1 | `brand_id` present in catalog plan TSV | Row exists in `podcast_script_catalog_plan_2026-05-30.tsv` |
| 2 | ≥1 script family enumerated | `script_family` ∈ {`narrative_arc`, `exercise_walkthrough`, `brand_story`, `sleep_narrative`, `interview_qa`} |
| 3 | Cadence declared per family | `cadence` column non-empty; default `weekly` unless family override |
| 4 | ≥1 locale with `en_US` baseline | Every brand has at least one `en_US` row |
| 5 | Narrator assignment present | `narrator` ≠ `pending_narrator_assignment` **or** explicit `pending_narrator_assignment` flagged in notes with owner |
| 6 | Format spec per family | `format_spec_ref` points to `config/podcast/podcast_format.yaml#<format_id>` |
| 7 | Localization mode declared | `localization_mode` ∈ {`native`, `translate_from_en_US`, `native_deep_template`} |
| 8 | Episode volume planned | `episode_count_planned` > 0 per family row |

### Per-family minimum format contract (length + segments)

| script_family | format_spec_ref | Target length | Segment contract |
|---------------|-----------------|---------------|------------------|
| `narrative_arc` | `#podcast_episode` | 15–25 min (locale-adjusted via market plan) | cold_open → theme_intro → scene → teaching → story → guided_practice → integration → thread → outro |
| `exercise_walkthrough` | `#podcast_short` | 2–5 min | micro_intro → practice (EXERCISE atom) → micro_outro |
| `brand_story` | `#podcast_trailer` | 3–5 min | teaser_hook → series_overview → episode_previews → cta |
| `sleep_narrative` | `#podcast_sleep` | 25–45 min | sleep soundscape → scene → plotless story → fade (inverse engagement curve) |
| `interview_qa` | `#podcast_episode` (bonus) | 15–25 min | optional post-season Q&A from persona pain_points |

---

## Wave-1 deep templates

| Template | brand_id | locale | readiness gate |
|----------|----------|--------|----------------|
| **US1** | `stillness_press` | `en_US` | `pipeline_validated` (PR #1347, 2026-W22 MVP) |
| **JP1** | `stillness_press` | `ja_JP` | `planned_deep_template` → operator approval before fan-out |

All other brand×locale cells remain `planned` until script generation lands.

---

## Localization handoff (Pearl_Localization)

| Mode | When | Pearl_Localization contract |
|------|------|----------------------------|
| `native` | `en_US` prose (non-deep-template brands) | `config/localization/quality_contracts/en-US/` |
| `native_deep_template` | US1 / JP1 stillness_press | Locale contract + operator review gate |
| `translate_from_en_US` | ja_JP, ko_KR, zh_CN, zh_TW fan-out | Per-locale `quality_contracts/<locale>/` + family-specific atom scope in TSV `notes` |

Translation must cover PIVOT, TAKEAWAY, THREAD, PERMISSION slot types per `config/localization/quality_contracts/README.md`.

---

## Cadence defaults and overrides

| Cadence | Applies to | Default schedule |
|---------|------------|------------------|
| `weekly` | `narrative_arc`, `sleep_narrative` | Monday 09:00 UTC (Tier-2 cron, PR #1348) |
| `daily_weekdays` | `exercise_walkthrough` | Mon–Fri micro-drops |
| `per_series_launch` | `brand_story` | Once per new season |
| `biweekly_optional` | `interview_qa` | Optional bonus; flagship/core only |

**Override list:** none in Wave-1 scope locales. (`es_latam` `twice_weekly` and `zh_hk` `biweekly` apply only to out-of-scope markets in `brand_podcast_plans.yaml`.)

---

## Script family assignment rules (summary)

1. **All brands, all locales:** `narrative_arc` + `brand_story`
2. **en_US / ja_JP / ko_KR:** add `exercise_walkthrough` (market plan `podcast_short`)
3. **Sleep-primary brands** (`sleep_restoration_iyashikei`, `night_reset_healing`): add `sleep_narrative`
4. **Flagship + core tiers:** add optional `interview_qa`

Episode counts derive from `artifacts/catalog/worldwide_catalog_37_brand_podcast_plan_2026-05-27.tsv` (4 locales) plus `ko_KR` extrapolation from `brand_podcast_plans.yaml` `ko_kr` market block.
