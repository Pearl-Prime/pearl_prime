<!-- AUTO-GENERATED — do not hand-edit. -->
<!-- Source: scripts/manga/generate_catalog_plan_from_strategic.py -->
<!-- Inputs: docs/GENRE_PORTFOLIO_PLAN.md + docs/CJK_CATALOG_PLAN.md + docs/US_CATALOG_PLAN.md -->
<!-- Per specs/MANGA_CATALOG_RECONCILIATION_SPEC.md §7.1 + D-17 -->

# Phoenix Omega — Manga Full Catalog Plan

Auto-generated from the strategic-tier plans. To update this file, edit the source
strategic docs and re-run the generator.

## Locales (per D-18, 5-locale matrix)

| Locale | Primary format | Platform(s) | Distribution status |
|---|---|---|---|
| en_US | Two paths — do NOT mix: (A) manga digest 5"×7.5" B&W for manga aisle OR (B) western doodle/cartoon for mainstream self-help shelf | Bookstores, Amazon, direct | distributed |
| ja_JP | Traditional B&W manga pages; tankobon + digital | LINE Manga, ComicWalker, Pixiv Comics | distributed |
| zh_TW | Hybrid: manga page layout, atmospheric rendering | LINE Comics TW, standalone print | distributed |
| zh_CN | Vertical-scroll tiáomàn (条漫), full color | Kuaikan Manhua, Bilibili Comics | gray_zone_disclosed |
| ko_KR | Vertical-scroll webtoon, full color | Naver Webtoon, LINE Global, Kakao | hold_pending_market_clearance |

## Brand portfolio (37 brands per `GENRE_PORTFOLIO_PLAN.md`)

| Brand | Tier | Series target | Genre mix |
|---|---|---|---|
| `cognitive_clarity` | flagship | 16 | psychological_thriller 35%, dark_fantasy 20%, sci_fi_cyberpunk 20%, supernatural_mystery 15%, workplace_drama 10% |
| `digital_ground` | flagship | 16 | sci_fi_cyberpunk 35%, workplace_drama 25%, psychological_horror 20%, isekai 15%, iyashikei 5% |
| `stillness_press` | flagship | 16 | iyashikei 30%, dark_fantasy 25%, psychological_horror 20%, supernatural_mystery 15%, isekai 10% |
| `body_memory_shojo` | core | 9 | dark_fantasy 20%, supernatural_mystery 20% |
| `career_lift_workplace` | core | 9 | workplace_drama 35%, supernatural_mystery 20%, iyashikei 15% |
| `executive_calm_workplace` | core | 9 | sci_fi_cyberpunk 25%, dark_fantasy 15% |
| `focus_sprint_workplace` | core | 9 | action_battle 25%, workplace_drama 20%, psychological_thriller 15% |
| `gentle_growth_healing` | core | 9 | iyashikei 25%, supernatural_mystery 20%, dark_fantasy 20% |
| `healing_ground_healing` | core | 9 | dark_fantasy 35%, iyashikei 25%, supernatural_mystery 25%, psychological_thriller 15% |
| `heart_balance_shojo` | core | 9 | iyashikei 25%, workplace_drama 20%, supernatural_mystery 15% |
| `high_performer_workplace` | core | 9 | psychological_thriller 25%, dark_fantasy 25%, historical_period 20% |
| `minimal_mind_healing` | core | 9 | iyashikei 40%, psychological_thriller 25%, sci_fi_cyberpunk 20%, supernatural_mystery 15% |
| `morning_momentum_workplace` | core | 9 | workplace_drama 25%, isekai 15% |
| `night_reset_healing` | core | 9 | iyashikei 40%, supernatural_mystery 20%, dark_fantasy 10% |
| `optimizer_workplace` | core | 9 | psychological_thriller 35%, workplace_drama 25%, sports_competition 10% |
| `relational_calm_iyashikei` | core | 9 | iyashikei 30%, supernatural_mystery 20%, psychological_thriller 15% |
| `sleep_restoration_iyashikei` | core | 9 | psychological_horror 30%, supernatural_mystery 20% |
| `somatic_wisdom_shojo` | core | 9 | iyashikei 30%, dark_fantasy 20% |
| `stabilizer_healing` | core | 9 | iyashikei 35%, workplace_drama 25%, sci_fi_cyberpunk 20%, dark_fantasy 20% |
| `adhd_forge_mystery` | niche | 5 | action_battle 30%, sports_competition 25%, isekai 20% |
| `bio_flow_healing` | niche | 5 | sci_fi_cyberpunk 35%, historical_period 20% |
| `bright_presence_tw_seinen` | niche | 5 | historical_period 25% |
| `calm_student_school` | niche | 5 | supernatural_mystery 25% |
| `confidence_core_romance` | niche | 5 | iyashikei 20% |
| `creative_unfold_social` | niche | 5 | supernatural_mystery 25%, action_battle 25%, school_coming_of_age 20% |
| `devotion_path_shonen` | niche | 5 | dark_fantasy 35%, action_battle 30% |
| `hormone_reset_healing` | niche | 5 | supernatural_mystery 30% |
| `legacy_builder_memoir` | niche | 5 | historical_period 40%, psychological_thriller 25%, iyashikei 15% |
| `longevity_lab_healing` | niche | 5 | sci_fi_cyberpunk 20%, supernatural_mystery 15% |
| `qi_foundation_cultivation` | niche | 5 | dark_fantasy 30%, action_battle 20% |
| `relationship_clarity_romance` | niche | 5 | psychological_thriller 20%, supernatural_mystery 15% |
| `resilient_parent_social` | niche | 5 | iyashikei 30%, dark_fantasy 20% |
| `solar_return_isekai` | niche | 5 | isekai 50%, dark_fantasy 25%, action_battle 25% |
| `spiritual_ground_supernatural` | niche | 5 | dark_fantasy 30%, iyashikei 20% |
| `stoic_edge_battle` | niche | 5 | action_battle 35%, historical_period 30% |
| `trauma_path_healing` | niche | 5 | dark_fantasy 35%, psychological_horror 30%, iyashikei 20%, historical_period 15% |
| `warrior_calm_cultivation` | niche | 5 | action_battle 30%, dark_fantasy 30%, iyashikei 15% |

## Catalog rows (brand × locale × genre)

Total brands parsed: **37**.
Total locales: **5** (per D-18).
Total genre slugs in allow-list: **15** (per §4.1).

Each row below represents one brand × locale slice. The series count is
the integer round of `target_series × genre_pct` for each genre slug.

### `adhd_forge_mystery` (niche — 5 series target)
> ADHD · Focus · Shonen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `bio_flow_healing` (niche — 5 series target)
> Body / Biology · Healing · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | sci_fi_cyberpunk | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | historical_period | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | sci_fi_cyberpunk | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | historical_period | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | sci_fi_cyberpunk | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | historical_period | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | sci_fi_cyberpunk | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | historical_period | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | sci_fi_cyberpunk | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | historical_period | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `body_memory_shojo` (core — 9 series target)
> Somatic Healing · Trauma · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `bright_presence_tw_seinen` (niche — 5 series target)
> Social Anxiety · TW market · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | historical_period | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | historical_period | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | historical_period | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | historical_period | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | historical_period | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `calm_student_school` (niche — 5 series target)
> Anxiety · Study · Shojo

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `career_lift_workplace` (core — 9 series target)
> Imposter Syndrome · Workplace · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `cognitive_clarity` (flagship — 16 series target)
> Overthinking · Psychology · CBT-adjacent · Seinen adult men

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | sci_fi_cyberpunk | 1 | distributed |
| en_US | psychological_thriller | 2 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | historical_period | 1 | distributed |
| en_US | cultivation_martial | 1 | distributed |
| en_US | school_coming_of_age | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | sci_fi_cyberpunk | 1 | distributed |
| ja_JP | psychological_thriller | 2 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | historical_period | 1 | distributed |
| ja_JP | cultivation_martial | 1 | distributed |
| ja_JP | school_coming_of_age | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | sci_fi_cyberpunk | 1 | distributed |
| zh_TW | psychological_thriller | 2 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | historical_period | 1 | distributed |
| zh_TW | cultivation_martial | 1 | distributed |
| zh_TW | school_coming_of_age | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | sci_fi_cyberpunk | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 2 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | historical_period | 1 | gray_zone_disclosed |
| zh_CN | cultivation_martial | 1 | gray_zone_disclosed |
| zh_CN | school_coming_of_age | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | sci_fi_cyberpunk | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 2 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | historical_period | 1 | hold_pending_market_clearance |
| ko_KR | cultivation_martial | 1 | hold_pending_market_clearance |
| ko_KR | school_coming_of_age | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `confidence_core_romance` (niche — 5 series target)
> Imposter Syndrome · Self-Worth · Shojo

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `creative_unfold_social` (niche — 5 series target)
> Social Anxiety · Creativity · Shojo

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | school_coming_of_age | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | school_coming_of_age | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | school_coming_of_age | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | school_coming_of_age | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | school_coming_of_age | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `devotion_path_shonen` (niche — 5 series target)
> Spiritual · Courage · Shonen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `digital_ground` (flagship — 16 series target)
> Burnout · Tech Worker · Digital Identity · Manhwa/Webtoon

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | sci_fi_cyberpunk | 2 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | historical_period | 1 | distributed |
| en_US | cultivation_martial | 1 | distributed |
| en_US | school_coming_of_age | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | sci_fi_cyberpunk | 2 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | historical_period | 1 | distributed |
| ja_JP | cultivation_martial | 1 | distributed |
| ja_JP | school_coming_of_age | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | sci_fi_cyberpunk | 2 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | historical_period | 1 | distributed |
| zh_TW | cultivation_martial | 1 | distributed |
| zh_TW | school_coming_of_age | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | sci_fi_cyberpunk | 2 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | historical_period | 1 | gray_zone_disclosed |
| zh_CN | cultivation_martial | 1 | gray_zone_disclosed |
| zh_CN | school_coming_of_age | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | sci_fi_cyberpunk | 2 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | historical_period | 1 | hold_pending_market_clearance |
| ko_KR | cultivation_martial | 1 | hold_pending_market_clearance |
| ko_KR | school_coming_of_age | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `executive_calm_workplace` (core — 9 series target)
> Burnout · Overthinking · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | sci_fi_cyberpunk | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | sci_fi_cyberpunk | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | sci_fi_cyberpunk | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | sci_fi_cyberpunk | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | sci_fi_cyberpunk | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `focus_sprint_workplace` (core — 9 series target)
> ADHD · Focus · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `gentle_growth_healing` (core — 9 series target)
> Self-Worth · Imposter Syndrome · Shojo

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `healing_ground_healing` (core — 9 series target)
> Grief · General Healing · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `heart_balance_shojo` (core — 9 series target)
> Social Anxiety · Relationships · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `high_performer_workplace` (core — 9 series target)
> Burnout · Financial Anxiety · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | historical_period | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | historical_period | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | historical_period | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | historical_period | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | historical_period | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `hormone_reset_healing` (niche — 5 series target)
> Somatic · Hormonal · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `legacy_builder_memoir` (niche — 5 series target)
> Self-Worth · Purpose · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | historical_period | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | historical_period | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | historical_period | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | historical_period | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | historical_period | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `longevity_lab_healing` (niche — 5 series target)
> Health · Aging · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | sci_fi_cyberpunk | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | sci_fi_cyberpunk | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | sci_fi_cyberpunk | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | sci_fi_cyberpunk | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | sci_fi_cyberpunk | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `minimal_mind_healing` (core — 9 series target)
> Overthinking · Mindfulness · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | sci_fi_cyberpunk | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | sci_fi_cyberpunk | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | sci_fi_cyberpunk | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | sci_fi_cyberpunk | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | sci_fi_cyberpunk | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `morning_momentum_workplace` (core — 9 series target)
> Burnout · Motivation · Shonen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `night_reset_healing` (core — 9 series target)
> Sleep · Rest · Night Routines · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `optimizer_workplace` (core — 9 series target)
> Overthinking · Productivity · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `qi_foundation_cultivation` (niche — 5 series target)
> Somatic (Eastern) · Cultivation · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `relational_calm_iyashikei` (core — 9 series target)
> Social Anxiety · Relationships · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `relationship_clarity_romance` (niche — 5 series target)
> Social Anxiety · Boundaries · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `resilient_parent_social` (niche — 5 series target)
> Burnout · Self-Worth · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `sleep_restoration_iyashikei` (core — 9 series target)
> Sleep · Night · Rest · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `solar_return_isekai` (niche — 5 series target)
> Self-Worth · Isekai framing · Shonen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `somatic_wisdom_shojo` (core — 9 series target)
> Somatic Healing · Body Memory · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `spiritual_ground_supernatural` (niche — 5 series target)
> Grief · Devotion · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `stabilizer_healing` (core — 9 series target)
> Burnout Recovery · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | sci_fi_cyberpunk | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | sci_fi_cyberpunk | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | sci_fi_cyberpunk | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | sci_fi_cyberpunk | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | sci_fi_cyberpunk | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `stillness_press` (flagship — 16 series target)
> Anxiety · Somatic · Sleep · Josei adult women

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 2 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | supernatural_mystery | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | sci_fi_cyberpunk | 1 | distributed |
| en_US | psychological_thriller | 1 | distributed |
| en_US | romance_josei_drama | 1 | distributed |
| en_US | workplace_drama | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | sports_competition | 1 | distributed |
| en_US | historical_period | 1 | distributed |
| en_US | cultivation_martial | 1 | distributed |
| en_US | school_coming_of_age | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 2 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | supernatural_mystery | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | sci_fi_cyberpunk | 1 | distributed |
| ja_JP | psychological_thriller | 1 | distributed |
| ja_JP | romance_josei_drama | 1 | distributed |
| ja_JP | workplace_drama | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | sports_competition | 1 | distributed |
| ja_JP | historical_period | 1 | distributed |
| ja_JP | cultivation_martial | 1 | distributed |
| ja_JP | school_coming_of_age | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 2 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | supernatural_mystery | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | sci_fi_cyberpunk | 1 | distributed |
| zh_TW | psychological_thriller | 1 | distributed |
| zh_TW | romance_josei_drama | 1 | distributed |
| zh_TW | workplace_drama | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | sports_competition | 1 | distributed |
| zh_TW | historical_period | 1 | distributed |
| zh_TW | cultivation_martial | 1 | distributed |
| zh_TW | school_coming_of_age | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 2 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | supernatural_mystery | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | sci_fi_cyberpunk | 1 | gray_zone_disclosed |
| zh_CN | psychological_thriller | 1 | gray_zone_disclosed |
| zh_CN | romance_josei_drama | 1 | gray_zone_disclosed |
| zh_CN | workplace_drama | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | sports_competition | 1 | gray_zone_disclosed |
| zh_CN | historical_period | 1 | gray_zone_disclosed |
| zh_CN | cultivation_martial | 1 | gray_zone_disclosed |
| zh_CN | school_coming_of_age | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 2 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | supernatural_mystery | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | sci_fi_cyberpunk | 1 | hold_pending_market_clearance |
| ko_KR | psychological_thriller | 1 | hold_pending_market_clearance |
| ko_KR | romance_josei_drama | 1 | hold_pending_market_clearance |
| ko_KR | workplace_drama | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | sports_competition | 1 | hold_pending_market_clearance |
| ko_KR | historical_period | 1 | hold_pending_market_clearance |
| ko_KR | cultivation_martial | 1 | hold_pending_market_clearance |
| ko_KR | school_coming_of_age | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `stoic_edge_battle` (niche — 5 series target)
> Courage · Resilience · Seinen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | historical_period | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | historical_period | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | historical_period | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | historical_period | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | historical_period | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `trauma_path_healing` (niche — 5 series target)
> Grief · Trauma · Josei

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | dark_fantasy | 1 | distributed |
| en_US | psychological_horror | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | psychological_horror | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | psychological_horror | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | psychological_horror | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | psychological_horror | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

### `warrior_calm_cultivation` (niche — 5 series target)
> Burnout · Inner Peace · Shonen

| Locale | Genre | Series count | Distribution status |
|---|---|---|---|
| en_US | iyashikei | 1 | distributed |
| en_US | dark_fantasy | 1 | distributed |
| en_US | isekai | 1 | distributed |
| en_US | action_battle | 1 | distributed |
| en_US | mecha | 1 | distributed |
| ja_JP | iyashikei | 1 | distributed |
| ja_JP | dark_fantasy | 1 | distributed |
| ja_JP | isekai | 1 | distributed |
| ja_JP | action_battle | 1 | distributed |
| ja_JP | mecha | 1 | distributed |
| zh_TW | iyashikei | 1 | distributed |
| zh_TW | dark_fantasy | 1 | distributed |
| zh_TW | isekai | 1 | distributed |
| zh_TW | action_battle | 1 | distributed |
| zh_TW | mecha | 1 | distributed |
| zh_CN | iyashikei | 1 | gray_zone_disclosed |
| zh_CN | dark_fantasy | 1 | gray_zone_disclosed |
| zh_CN | isekai | 1 | gray_zone_disclosed |
| zh_CN | action_battle | 1 | gray_zone_disclosed |
| zh_CN | mecha | 1 | gray_zone_disclosed |
| ko_KR | iyashikei | 1 | hold_pending_market_clearance |
| ko_KR | dark_fantasy | 1 | hold_pending_market_clearance |
| ko_KR | isekai | 1 | hold_pending_market_clearance |
| ko_KR | action_battle | 1 | hold_pending_market_clearance |
| ko_KR | mecha | 1 | hold_pending_market_clearance |

## Summary

- **Brands**: 37
- **Locales**: 5
- **Genres**: 15
- **Total localized series rows**: 1410
- **Estimated chapters at 14/series**: 19740

Per spec D-20, this catalog plan is materialized to disk by Phase 2X.4
atomic PR (schema flip + 132+716 stale YAML deletion + regenerate).

