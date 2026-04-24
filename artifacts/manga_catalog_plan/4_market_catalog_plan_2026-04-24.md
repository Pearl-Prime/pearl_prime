# Phoenix Omega Manga Catalog — 4-Market Plan
**Date:** 2026-04-24
**Agent:** Pearl_Publisher
**Scope:** en_US (USA English) · ja_JP (Japan) · zh_TW (Taiwan Traditional Chinese) · zh_CN (China Simplified Chinese)
**Authority:** `manga_brand_series_plan.yaml` · `genre_market_fit_matrix.yaml` · `brand_illustration_styles.yaml` · `brand_lora_plans.yaml`

---

## TL;DR — Catalog size per market

| Market | Primary brands | Secondary (rollout) brands | Volumes/year total |
|--------|----------------|----------------------------|---------------------|
| **en_US** | 10 english-global brands | — | **60 volumes/year** |
| **ja_JP** | 2 japan-native brands + 10 english-global rollouts | all others | **89 volumes/year** (13 native + 78 rollout ceiling; ~50 practical) |
| **zh_TW** | 1 taiwan-native brand | 10 english + 2 japan (TW rollout) | **5 native + rollout subset** |
| **zh_CN** | — (not declared primary) | Select brands with Kuaikan Manhua fit | **Character-only LoRA scope — no native catalog** |
| **TOTAL (full target)** | | | **~160 volumes/year at steady state** |

This is a 3-year steady-state target. Wave 1 launches a subset per market below.

---

## Market 1 — en_US (USA English)

**Platforms:** Amazon KDP, WEBTOON Canvas, Tapas, Audible, Spotify Audiobooks, Google Play Books, Apple Books
**Trim size:** 5.5×8.5″ graphic novel (en_US standard)
**Reading direction:** LTR (western standard)
**Color:** B&W for tankobon-style, color for digital/webtoon
**Launch priority lens:** KDP-first (70% royalty bracket), BookTok-drive-able

### Primary brands (10 english-global-lane)

| Brand | Teacher | Genre | Topics (4-engine × 4-persona grid) | Volumes/yr | Wave 1 books |
|-------|---------|-------|------------------------------------|------------|--------------|
| **stillness_press** | ahjan | iyashikei (contemplative ink wash) | anxiety / sleep_anxiety / somatic_healing | 6 | 6 P0 — stillness_press × Hana/Yuki/Mei seeds |
| **cognitive_clarity** | joshin | seinen (stark zen ink) | overthinking / imposter_syndrome / burnout / boundaries | 8 | 4 P0 |
| **somatic_wisdom** | pamela_fellows | josei (soft clinical) | somatic_healing / compassion_fatigue / self_worth | 5 | 3 P0 |
| **qi_foundation** | master_feung | cultivation (traditional Chinese brushwork) | burnout / anxiety / self_worth | 6 | **DEFER Wave 1** (Phase A decision 4 — thin en_US precedent) |
| **digital_ground** | miki | manhwa_webtoon (digital minimalism) | financial_anxiety / financial_stress / social_anxiety / imposter_syndrome | 8 | 4 P0 |
| **heart_balance** | maat | shojo+mythological (geometric Egyptian mysticism) | self_worth / boundaries / compassion_fatigue | 5 | 3 P0 |
| **warrior_calm** | master_wu | wuxia (martial ink) | courage / burnout / self_worth | 6 | **DEFER Wave 1** (Phase A decision 4) |
| **sleep_restoration** | master_sha | iyashikei (luminous night) | sleep_anxiety / somatic_healing | 4 | 2 P0 |
| **solar_return** | ra | isekai (ember abstraction) | courage / financial_anxiety / depression | 6 | 3 P1 (isekai has L-precedent in en_US) |
| **devotion_path** | sai_ma | shonen (flowing warmth) | courage / imposter_syndrome / burnout | 6 | 3 P1 (shonen has Y-precedent but wellness-shonen is niche) |

**en_US Wave 1 total: ~28 books** (exclude qi_foundation + warrior_calm = 17 books deferred)
**en_US steady-state: 60 volumes/year**

### Persona × topic matrix (en_US)
Top volume personas for en_US: `gen_z_professionals`, `tech_finance_burnout`, `millennial_women_professionals`, `corporate_managers`, `working_parents`, `healthcare_rns`, `entrepreneurs`, `first_responders`, `gen_x_sandwich`. Tier-1 has 11 personas with full 15-topic arc coverage each.

---

## Market 2 — ja_JP (Japan)

**Platforms:** Bookwalker, LINE Manga, Kindle JP, Kadokawa, Shueisha (licensed), Niconico
**Trim size:** B6 (128×182 mm) — Japanese standard
**Reading direction:** RTL
**Color:** B&W (tankobon standard), selective color for digital-first series
**Launch priority lens:** Digital-first (72.7% of JP manga market is digital); Bookwalker + LINE as primary channel

### Primary brands (2 japan-native-lane)

| Brand | Teacher | Genre | Topics | Volumes/yr | Wave 1 |
|-------|---------|-------|--------|------------|--------|
| **relational_calm** | junko | iyashikei (wabi-sabi simplicity) | anxiety / social_anxiety / burnout / sleep_anxiety | 8 | 4 P0 |
| **body_memory** | omote | josei (textured grief) | somatic_healing / self_worth / grief | 5 | 3 P0 |

### Secondary (english-global rollout into ja_JP)

All 10 english-global brands are candidates for JP rollout once they have 2+ volumes shipped in en_US. Priority rollout:
1. **stillness_press** (ahjan) — iyashikei is JP-native genre, localizes naturally
2. **cognitive_clarity** (joshin) — seinen has strongest JP commercial precedent (Vagabond, Honey & Clover)
3. **somatic_wisdom** (pamela_fellows) — josei market is active in JP
4. **heart_balance** (maat) — mythological themes fit JP shojo+

**ja_JP Wave 1 total: 7 books** (2 brands × ~3-4 series)
**ja_JP steady-state: ~50 volumes/year** (13 native + partial rollout, not full 78)

### Existing ja_JP series YAMLs
18 series already defined in `config/source_of_truth/manga_profiles/series/`:
- stillness_press ×11 (rollout): stillness_jp_01–16 (7 named chars, 4 unnamed)
- cognitive_clarity ×7 (rollout): cogclar_jp_01, 02, 04, 07, 10, 12, 13 (3 named chars, 4 unnamed)

**Gap:** 10 of 12 brands missing JP series YAMLs entirely (relational_calm, body_memory, somatic_wisdom, qi_foundation, digital_ground, heart_balance, warrior_calm, sleep_restoration, solar_return, devotion_path).

---

## Market 3 — zh_TW (Taiwan Traditional Chinese)

**Platforms:** Bookwalker TW, Tong Li Publishing, Eslite (bookstore), Kadokawa Taiwan
**Trim size:** B6 (128×182mm) — preserved from JP
**Reading direction:** RTL (preserved from JP convention)
**Color:** B&W primary (closer to JP publisher norms than en_US)
**Characters:** Traditional Chinese (繁體中文) + pinyin/Tongyong romanization
**Launch priority:** Single-brand launch, prove translation pipeline before broad rollout

### Primary brand (1 taiwan-native-lane)

| Brand | Teacher | Genre | Topics | Volumes/yr | Wave 1 |
|-------|---------|-------|--------|------------|--------|
| **bright_presence_tw** | adi_da | TW-native (localized style TBD) | depression / grief / courage | 5 | 3 P0 |

### Secondary (en_global + japan rollout to zh_TW)

Per genre_market_fit_matrix, `relational_calm` (junko) has a Taiwan rollout cell (verdict=L). Other brands are en_US primary with potential TW rollout after en_US ships.

**zh_TW Wave 1 total: 3 books** (bright_presence_tw only)
**zh_TW main character LoRA scope:** All protagonists across all brands that ship to zh_TW = ~20+ characters (for LoRA training — user's decision 4 from earlier was per-series unique characters).

### Existing zh_TW series YAMLs
**0 currently.** All need to be authored for zh_TW launch.

---

## Market 4 — zh_CN (China Simplified Chinese)

**Platforms:** Kuaikan Manhua (largest local platform), Tencent Manga
**Trim size:** Platform-dependent (webtoon-vertical for Kuaikan)
**Reading direction:** Platform-dependent (Kuaikan = vertical scroll LTR; print = RTL traditional)
**Characters:** Simplified Chinese (简体中文) + pinyin
**Launch priority:** NOT A PRIMARY LAUNCH MARKET. Character-LoRA-only scope for Wave 1.

### Regulatory constraints (per genre_market_fit_matrix)
- BL/GL content: BLOCKED
- Foreign manga import: RESTRICTED
- Political/religious content: HEAVY REVIEW

### Primary brand: NONE DECLARED
`manga_brand_series_plan.yaml` does not list zh_CN in `simultaneous_languages` or in any brand's `primary_lane`.

### zh_CN scope Wave 1

**Character LoRAs only** — per earlier master plan Phase 2 scope. For any brand that considers future zh_CN rollout, train the main character LoRAs using Simplified-Chinese character names now (alongside zh_TW Traditional Chinese versions). This future-proofs without committing to series production.

**zh_CN Wave 1: 0 series, ~20 character LoRAs** (shared scope with zh_TW character set).

---

## Master rollup — all 4 markets

### Volumes/year at steady state

| Market | Native | En-global rollout | Japan rollout | Total |
|--------|--------|-------------------|---------------|-------|
| en_US | — | 60 | — | **60** |
| ja_JP | 13 | 36 (partial rollout @ 60% of en-catalog) | — | **~49** |
| zh_TW | 5 | 12 (subset rollout @ 20%) | 5 (subset) | **~22** |
| zh_CN | 0 (series) | 0 (series) | 0 (series) | **0 (series); ~20 LoRAs** |
| **TOTAL** | 18 | 108 | 5 | **~131 volumes/year** |

### Wave 1 scope (ship-able first quarter)

| Market | Wave 1 volumes | P0 (ship first) | P1 (ship second) | Deferred |
|--------|---------------|------------------|-------------------|----------|
| en_US | ~34 | 28 (8 brands × 3-4 series) | 6 (solar_return + devotion_path) | 17 (qi_foundation + warrior_calm) |
| ja_JP | ~14 | 7 (relational_calm + body_memory) | 7 (stillness_press JP rollout) | — |
| zh_TW | 3 | 3 (bright_presence_tw only) | — | — |
| zh_CN | 0 series | — | — | — |
| **TOTAL Wave 1** | **~51 volumes** | **38** | **13** | **17** |

### Main-character LoRA scope

| Market | LoRAs needed (Wave 1) | LoRAs needed (steady-state) |
|--------|----------------------|-----------------------------|
| en_US | ~28 (one per Wave 1 book with unique protagonist) | ~60 |
| ja_JP | ~14 (existing named) + 10 for unnamed series | ~50 |
| zh_TW | ~3 (bright_presence_tw) + ~20 (all-brand TW localizations) | ~25 |
| zh_CN | ~20 (Simplified-Chinese versions of zh_TW characters) | ~25 |
| **TOTAL** | **~75 LoRAs Wave 1** | **~160 LoRAs steady-state** |

All LoRA training executes on **Pearl Star (free, local GPU)** — zero paid API spend for training. Owner-rule confirmed.

---

## Gaps that block execution

Listed in order of blocking severity:

### 🔴 BLOCKER 1: 0 series YAMLs for en_US full production
Only 3 en_US series YAMLs exist (Hana/Yuki/Mei stillness_press seeds). Phase B (Pearl Prime en_US book catalog) already generates these iteratively — in flight.

### 🔴 BLOCKER 2: 10 unnamed ja_JP series
Cannot train LoRAs for unnamed characters. Must cast + describe before LoRA pipeline.

### 🔴 BLOCKER 3: 0 series YAMLs for zh_TW + zh_CN
Both need full series authoring before books can ship.

### 🟡 BLOCKER 4: Brand style LoRAs
12 brand style LoRAs referenced in `brand_cover_art_specs.yaml` (style_sp, style_cc, etc.) but **0 have been trained**. Cover and interior art requires these.

### 🟡 BLOCKER 5: Disk space for render phase
Current free: 19 GB. Need 100+ GB for Phase D renders (reference images × 75 characters × 10 views = 750 images + ~75 LoRA weights × 250 MB = ~25 GB of artifacts).

---

## Recommended launch sequence (dependency-ordered)

```
1. Phase A.2 (IN FLIGHT): Teacher scoring expansion for 10 teachers
   — Blocks: Phase B series plan quality (weak signal without it)

2. Phase B1 (MERGED PILOT): Series plans for 3 en_US seed series
   — Done for stillness_press × {gen_z, healthcare_rns} × {anxiety, sleep_anxiety}

3. Phase B2 (NEXT): Scale series plans to all Wave 1 en_US series
   — ~28 series plans, one PR per brand

4. Phase B3 (PARALLEL): Author zh_TW bright_presence_tw series plans (3 series)

5. Phase B4 (PARALLEL): Complete ja_JP — name 10 unnamed characters, add 10 missing brand series

6. Phase C: Per-book plans (titles, metadata, keywords, descriptions) — batched per brand

7. Phase D: LoRA reference image generation — ALL 75 characters on Pearl Star (free)
   — Gated on: Blocker 5 (disk space — need +80 GB)

8. Phase E: LoRA training on Pearl Star
   — Each LoRA ~2 hours GPU time × 75 = ~150 GPU-hours (5-7 days serial)

9. Phase F: Final portrait render per book
   — Once LoRAs trained; fast

10. Phase G: Book body pipeline
    — Pearl Prime assembly per Wave 1 book, runs against corrected post-#614 pipeline

11. Phase H: Cover + interior art per book
    — Requires brand style LoRAs (Blocker 4) + protagonist LoRAs (Phase F)
```

### Time-to-first-ship estimate

- Phase A.2 + B2 + B3 + B4: **~2-3 weeks** (plan authoring)
- Phase C: **~1 week** (per-book metadata, mostly mechanical)
- Phase D-F (LoRA pipeline): **~1-2 weeks** (compute-bound on Pearl Star serial jobs)
- Phase G (book body): **~1 week** (pipeline runs + owner QA)
- Phase H (cover + interior art): **~2-3 weeks** (compute-bound)

**Total: ~8-11 weeks to first Wave 1 ship.** Aggressive but achievable given Pearl Star capacity is free and unlimited on time.

---

## What Pearl_Publisher did NOT do in this plan

- Did NOT write individual series plans (that's Phase B work — already in-flight PR #615 for pilot)
- Did NOT write per-book metadata (Phase C)
- Did NOT trigger any Pearl Star jobs (Phase D requires disk space unblock first)
- Did NOT modify any YAML beyond the `protagonist_loras` section committed earlier today
- Did NOT commit this plan to git yet — awaiting owner review

---

## Owner decisions needed on this plan

1. **Wave 1 scope: accept 51 volumes across 4 markets?** Or narrow (e.g. en_US only first, JP+TW Wave 2)?
2. **qi_foundation + warrior_calm deferral:** Already confirmed earlier. Confirms removes 17 en_US books from Wave 1 scope.
3. **zh_CN: accept character-only scope for Wave 1?** No series production until validated via zh_TW.
4. **Brand style LoRAs (Blocker 4): when to train?** These are separate from protagonist LoRAs — should Phase D cover both, or separate LoRA training wave?
5. **Disk space:** unblock Phase D by moving ~/Documents/Downloads (48 GB satsang archive) to external? Required before 75 character LoRAs can be trained.

Reply with decisions and Pearl_Publisher proceeds to Phase B2/B3/B4 scaling.
