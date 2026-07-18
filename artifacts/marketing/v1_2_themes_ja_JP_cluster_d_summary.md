# V1.2 Themes — Cluster D (Relational/Connection/Family) × ja_JP — Summary

**Date:** 2026-05-11
**Author:** Pearl_Writer (Cluster D × ja_JP subagent)
**Deliverable:** `artifacts/marketing/v1_2_themes_ja_JP_cluster_d.yaml`
**Authority:**
- Constraint: `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`
- Structural template (en_US): `artifacts/marketing/v1_2_themes_en_US_cluster_d.yaml` (PR #1065)
- JP register reference: `artifacts/marketing/v1_2_themes_ja_JP_cluster_a.yaml` (PR #1057)

## Scope

- locale: `ja_JP`
- cluster: D — Relational/Connection/Family
- brands: 5 (`relational_calm_iyashikei`, `confidence_core_romance`, `bright_presence_tw_seinen`, `heart_balance_shojo`, `resilient_parent_social`)
- series per brand: 5
- total series: **25**

## Brand-id mapping (constraint doc → canonical_brand_list.yaml)

| Constraint doc | Canonical brand_id | Mapping note |
|---|---|---|
| `relational_calm_iyashikei` | `relational_calm_iyashikei` | exact |
| `inner_security` | `confidence_core_romance` | shojo inner-security/self-worth |
| `bright_presence` | `bright_presence_tw_seinen` | exact root: seinen bright-presence |
| `found_family_shojo` | `heart_balance_shojo` | josei relational shojo found-family |
| `communal_warmth` | `resilient_parent_social` | josei family-of-origin + chosen-family |

## Genre allocation validation

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 | OK |
| slice_of_life | 5 | 5 | OK |
| supernatural_everyday | 5 | 4-5 | OK |
| mystery_cozy | 4 | 4 | OK |
| fantasy_adventure | 3 | 3 | OK |
| romance | 2 | 1-2 (ceiling — Cluster D bumped per spec) | OK |
| **TOTAL** | **25** | **25** | OK |

All within binding ranges.

## Distributional checks

### Magical register (V1.2 strict enums)

| register | count |
|---|---|
| supernatural_everyday | 10 |
| magical_realism | 6 |
| none | 6 |
| soft_fantasy | 3 |

All 4 used registers are within the 6 canonical enum values. No `high_fantasy` used. No `isekai` (cluster fit), no `occult_cosmic` (cluster fit).

### Serial engine (V1.2 strict enums)

| engine | count |
|---|---|
| case_of_the_week | 15 |
| life_stage_rhythm | 4 |
| companion_roster | 3 |
| location_anthology | 3 |

All within the 6 canonical enum values.

### Reading platform fit

| platform | count | pct |
|---|---|---|
| manga_traditional | 17 | 68% |
| webtoon_vertical | 8 | 32% |

Within JP-guidance target (~70% manga_traditional / ~30% webtoon_vertical).

### Persona archetype

| persona | count | pct |
|---|---|---|
| GZ-firstjob | 5 | 20% |
| GZ-queer | 2 | 8% |
| GZ-uni | 3 | 12% |
| GA-tween | 3 | 12% |
| ML-mid | 12 | 48% |

Persona note: Brands 3 (bright_presence seinen) and 5 (resilient_parent communal_warmth) naturally skew ML-mid by register design (seinen + family-of-origin/parental). Gen Z total is 40% (10/25), Gen Alpha is 12% (3/25), Mill is 48% (12/25). Cluster D's family-of-origin focus and the seinen brand bias persona allocation toward Mill more than the 60/20/18/2 default; this is consistent with the en_US cluster D pattern (also Mill-heavy for the same brands) and reflects the inherently older register of inherited-house/diaspora-recovery/grandmother-shrine plotlines. JP register intensifies this (おばあちゃんち, 義実家, 同窓会 anchors are mostly Mill-resonant).

### Volume runway

- Min: 100
- Median: 175
- Max: 200

All series have a defined runway between 100-200 volumes. Median 175.

### Brand counts

| brand | count |
|---|---|
| relational_calm_iyashikei | 5 |
| confidence_core_romance | 5 |
| bright_presence_tw_seinen | 5 |
| heart_balance_shojo | 5 |
| resilient_parent_social | 5 |

Exactly 5 per brand.

## JP locale specifics applied

- 100% natural Japanese in: series_title, series_logline, series_description, opening_5_volume_arc, long_arc_spine, reader_promise, marketing_angle, audience.
- No romaji in content fields (series_id uses romaji as required by schema convention).
- Structural enums in English (per V1.2 schema spec).
- Cultural anchors used: 商店街, 町内会, おばあちゃんち, 縁側, 義実家, 三軒長屋, 駅前, 同窓会, ガレージ, 家族写真, 日曜の食卓, 那覇/沖縄, 博多, 横浜, 京都, 大阪, 川崎, 仙台, 長岡, 群馬, 鎌倉, 柏 (geographic JP rooting).
- comp_titles consist of real JP works: SPY×FAMILY, ホリミヤ, よつばと!, ハチミツとクローバー, フルーツバスケット, 君に届け, 海街diary, 違国日記, セトウツミ, 葬送のフリーレン, 蟲師, 夏目友人帳, コーヒーが冷めないうちに, 森崎書店の日々, ツバキ文具店, 薬屋のひとりごと, 旅猫リポート, 深夜食堂, BECK, のだめカンタービレ, とんがり帽子のアトリエ, 私の少年, サザエさん, 夜のクラゲは泳げない, サラリーマン金太郎, 君は月夜に光り輝く.
- Tone references: SPY×FAMILY (選びとる家族のあたたかさ) + ホリミヤ (関係性の機微) + よつばと! (家族のぬくもり) + 葬送のフリーレン (感情の節度).

## Validation gate

- 25/25 series ✓
- 5/5 brands ✓
- Genre allocation within binding ranges ✓
- Strict V1.2 enums (magical_register, serial_engine) ✓
- Platform 70/30 manga/webtoon (achieved 68/32) ✓
- All JP content in natural Japanese ✓
- All structural enums in English ✓
- 0 deletions ✓
- 4-file write_scope respected (1 yaml + 1 md) ✓
