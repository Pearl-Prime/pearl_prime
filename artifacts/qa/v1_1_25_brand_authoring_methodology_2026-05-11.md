# V1.1 — 25 Path X brand series theme authoring methodology

**Date:** 2026-05-11  
**Owner:** Pearl_Marketing  
**Project:** PRJ-WORLDWIDE-CATALOG-GO-LIVE-V1 (Phase 2 V1.1)  
**Primary artifact:** `artifacts/marketing/v1_1_25_brand_series_themes_2026-05-11.yaml`  
**Inputs:** `config/manga/canonical_brand_list.yaml`; `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv` (V1.1_proposed rows); `config/manga/manga_brand_series_plan.yaml` (cadence/topic-allocation pattern for legacy 12 teacher brands); PR #1037 allocation lineage; PR #801 / `artifacts/research/japan_line_freebie_funnel_market_research_2026-04-29.md` (Japan LINE funnel cadence + rich-menu / step-message behavior for ja_JP tonal discipline).

## 1. Scope boundary

This session authors **topic anchors**, **per-locale series title concepts**, **arc_shape**, **emotional_throughline**, **surface_priority** (ebook vs manga emphasis per series concept), plus **locale tonal notes** and **surface split rationale** per brand. It does **not** author individual books, episodes, prompts, or LoRA plans (V1.1 generation phase; Pearl_Conductor v3).

## 2. Brand cohort derivation

The 25 brands are exactly the `priority_phase=V1.1_proposed` block in `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv` (healing_ground_healing through bright_presence_tw_seinen). Each row’s `brand_id` must match `canonical_brand_list.yaml` keys (Path X freeze).

## 3. How demographics steered the topic mix

For each `brand_id`, Pearl_Marketing read `tier`, `demographic`, `primary_topic`, `secondary_topics`, and `notes` from `canonical_brand_list.yaml` and enforced:

| Demographic | Series tilt |
|-------------|-------------|
| **josei** | Workplace dignity, grief seasons, relational repair, hormonal/sleep somatic arcs; indirect conflict and **face**-aware zh registers. |
| **seinen** | Systems, money, leadership ethics, biology/longevity literacy; blunt en_US allowed, **restrained** ja_JP melodrama. |
| **shojo** | Romance-of-self-worth, school anxiety, creativity-online ethics; consent-forward romance beats. |
| **shonen** | Motivation without grind glorification; ADHD mystery shells with **non-stigmatizing** antagonists. |
| **manhwa** | (Not in the 25 set) — pattern mirrored only where digital-native pacing informed workplace digital arcs indirectly. |

**Tier** informed default **surface_priority** skew: niche brands received more experimental manga_primary hooks where vertical-scroll emotional beats outperform long exposition; core healing brands leaned ebook_primary for ritual and psychoeducation spacing.

## 4. Pattern inheritance from the saturated 12

`manga_brand_series_plan.yaml` encodes **topic_allocation** and **webtoon_format.platform_cadence** per legacy teacher brand. For the 25 missing brands, we did **not** copy rows verbatim; we mirrored **structural intent**:

- **topic_allocation diversity** → each brand’s five series span distinct sub-topics drawn from `primary_topic` + `secondary_topics`.
- **platform_cadence discipline** → ja_JP notes cite LINE-adjacent **short open-rate half-life** and **step-message** friendliness (research §1.1–1.2), nudging shorter confession beats and micro-practices in manga_primary concepts.
- **series_rotation.max_dormant_months** ethos → arc_shape language favors **paced repair** over cliffhanger shame.

## 5. Locale register (en_US / ja_JP / zh_TW / zh_CN)

- **en_US:** Plain, direct wellness/prose acceptable; workplace money explicit where canonical notes include `financial_anxiety`.
- **ja_JP:** Honor **air-reading**, seasonal/gesture silence, tatemae/honne gradients, ringi-adjacent patience for executive arcs; **LINE Manga** vertical pacing referenced from PR #801 research lineage file cited in YAML `authority_refs`.
- **zh_TW:** Traditional Chinese; **面子**, family business, night-market, exam/cram culture where brand notes imply social or school pressure.
- **zh_CN:** Simplified Chinese; stability-forward grief framing, urban cost realism, **conservative** health claims for biology/longevity lanes; distinct from zh_TW where `bright_presence_tw_seinen` encodes Taiwan-forward texture per canonical `notes`.

## 6. Surface split (ebook vs manga)

`PEARL_PRIME_WORLDWIDE_CATALOG_PLAN_V1.md` anchors **222** regular cells (ebook + manga). V1.1 TSV uses **5×5** pilot depth for manga on these 25 brands. **`surface_priority`** per series concept is a **portfolio routing hint** for Conductor/generator: **ebook_primary** (long-form / scripts / footnotes), **manga_primary** (visual gesture / vertical pacing), or **balanced**. It is **not** a replacement for Phase-2 tier ladder counts on flagship/core/niche manga series depth.

## 7. QA checklist (human + machine)

1. **Count:** 25 `brand_id` keys under `brands:`; each of `en_US`, `ja_JP`, `zh_TW`, `zh_CN` has exactly **5** series objects.  
2. **Parse:** `python3 -c "import yaml; yaml.safe_load(open(...))"` passes.  
3. **Canon:** every `demographic_ref` cites `canonical_brand_list.yaml` path + tier/demographic/primary_topic/notes snapshot.  
4. **Drift:** No edits to `canonical_brand_list.yaml` / `brand_lora_plans.yaml` / `brand_genre_allocation.yaml` in this workstream.

## 8. Counts (SSOT for downstream dashboards)

| Metric | Value |
|--------|------:|
| Brands | 25 |
| Locales | 4 |
| Series concepts per locale | 125 |
| **Total series concepts** | **500** |
| Per-locale series concepts | en_US 125; ja_JP 125; zh_TW 125; zh_CN 125 |

## 9. Optional coordination note

`artifacts/coordination/ACTIVE_WORKSTREAMS.tsv` on this branch may lag `origin/main`; Pearl_PM should set `ws_catalog_generator_v1_1_25_brand_authoring_20260511` to **in_progress** / **completed** on the coordination branch that owns the 2026-05-11 worldwide amendment stack to avoid TSV fork drift.
