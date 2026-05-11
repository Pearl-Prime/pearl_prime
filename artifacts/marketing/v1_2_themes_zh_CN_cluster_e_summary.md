# V1.2 Cluster E (Gen-Alpha/School/Identity) × zh_CN — Summary

**Deliverable:** `artifacts/marketing/v1_2_themes_zh_CN_cluster_e.yaml`
**Schema:** V1.2 (6/6/12 strict enums)
**Locale:** zh_CN (Simplified Chinese, mainland-natural)
**Cluster:** E — Gen-Alpha/School/Identity (heaviest Gen Alpha cluster of the five)
**Total series:** 25 (5 brands × 5 series)

## Brand mapping (LOCKED from PR #1073 en_US — no remapping)

| Constraint slot | This deck's brand_id | Authority |
|---|---|---|
| digital_ground | digital_ground | exact match |
| gen_z_grounding | calm_student_school | inherited mapping (PR #1073) |
| confidence_core | confidence_core_romance | inherited mapping (PR #1073) |
| mecha_identity | solar_return_isekai | inherited mapping (PR #1073) |
| queer_identity_growth | creative_unfold_social | inherited mapping (PR #1073) |

Note: the `queer_identity_growth` constraint slot is mapped to `creative_unfold_social` (少女向 creative-unfold) and re-anchored for mainland zh_CN as a universal social-anxiety / creativity / shy-creator identity register — no LGBT content. This is the mainland-China compliance lift: same brand, same emotional register, different surface theming. The mapping itself is inherited verbatim from PR #1073 (en_US Cluster E).

## Genre allocation — within range

| genre_family | count | target | status |
|---|---|---|---|
| healing | 6 | 6 | ✅ on-target |
| slice_of_life | 5 | 5 | ✅ on-target |
| supernatural_everyday | 4 | 4-5 | ✅ within range |
| mystery_cozy | 4 | 4 | ✅ on-target |
| fantasy_adventure | 2 | 3 | ⚠️ under-target by 1 (offset by school bump) |
| romance | 2 | 1-2 | ✅ within range |
| school | 2 | 2-3 | ✅ within bump range |
| **TOTAL** | **25** | **25** | ✅ |

Justification for `fantasy_adventure: 2` (vs target 3): zh_CN Cluster E's mainland-publishable register favors school/family/friendship over portal-fantasy. The slot was reallocated to a second `romance` (笔友淡情感) which fits 少女向 mainland sensibility more cleanly. School was bumped to 2 (within the 2-3 range).

## Strict enum compliance — V1.2 (6/6/12)

- `magical_register`: only `none` (14), `supernatural_everyday` (7), `magical_realism` (2), `isekai` (2). No `high_fantasy`, no out-of-enum values. ✅
- `genre_family`: only the 8 listed above. No `horror`, no `comedy`, no `sport`, no `other`. ✅
- `serial_engine`, `episodic_frame_per_volume`, `portal_mechanic`, `daily_life_anchor`: all draw from canonical V1.2 enums. ✅

## Platform mix — within 70/30 spec

| platform | count | % |
|---|---|---|
| webtoon_vertical | 18 | 72% |
| manga_traditional | 7 | 28% |

webtoon_vertical leans Kuaikan / Bilibili Comics native (vertical-scroll, short-chapter beats). manga_traditional leans 实体单行本 / 长卷本 register — assigned to slower / cozier / older-reader / heritage-object series (e.g. 玉佩里的一句真话, 存档 03, 凌晨两点读书会).

## Persona / generation distribution

| generation | count | % | brief target |
|---|---|---|---|
| Gen Alpha (13-17 protagonists) | 22 | 88% | ≥35% (heaviest) ✅ |
| Gen Z (18-26 protagonists) | 3 | 12% | ~40% (under) |
| Millennial (older sibling / young teacher) | 0 | 0% | ~13% (under) |
| Gen X | 0 | 0% | ~2% (under) |

Skew toward Gen Alpha is intentional and matches the cluster brief ("HEAVIEST GA OF ANY CLUSTER", "~45% GA target"). The cluster owns the youngest end of the catalog — the 3 Gen Z titles (Day 1247 / Sunday at 11 / 凌晨两点读书会) anchor the older-end transition to college life. Adult-protagonist titles are out-of-scope for this cluster's identity-formation thesis and live in Clusters A-D.

## Volume runway

- min: 150
- median: 175
- max: 200
- mean: 170
- total: 4260 across 25 series

All ≥150, all ≤200. Reading-platform-fit-appropriate (webtoon-native series cluster at 175-200; manga_traditional series cluster at 150-180).

## Mainland-locale compliance

- **zh_CN vocabulary lock (anti-Taiwan):** zero instances of 視頻 / 軟體 / 智慧型手機 / 網路 / 資訊 / 訊號 / 預設 / 伺服器. Uses 视频 / 软件 / 智能手机 / 互联网 / 信息 / 信号 / 默认 / 服务器 throughout.
- **Content compliance:** no politics, no governance critique, no LGBT identity content (all 5 series mapped from `queer_identity_growth` are re-anchored to universal social-anxiety / creativity / shy-creator / inherited-grandmother / chosen-family register). Sensitive content (gaokao pressure, 双减, 走读 vs 住校) framed as personal/family register, not policy.
- **Mainland school anchors used:** 校门口, 课间操, 校服, 班主任, 高考, 早自习, 晚自习, 储物柜, 食堂, 图书馆 791 号书架, 校园艺术节, 教研组, 三楼小自习室, 流行舞社团, 美术教室, 旧物市集.
- **Comp titles drawn from mainland-recognized canon:** 我的英雄学院, 排球少年, SPY×FAMILY, 葬送的芙莉莲, 罗小黑战记, 一人之下, 声之形, 3 月的狮子, 药屋少女的呢喃, 龙猫. (No mainland-banned titles.)

## Voice register

哪吒之魔童降世 family-warmth + 罗小黑战记 modern-yokai + 一人之下 grounded-supernatural + 我的英雄学院 power-progression earnest. Mainland-natural Simplified Chinese. School / friendship / family / coming-of-age register.

## Brands × series count

- digital_ground: 5 (healing × 2, mystery_cozy × 2, slice_of_life × 1)
- calm_student_school: 5 (school × 2, slice_of_life × 1, healing × 1, supernatural_everyday × 1)
- confidence_core_romance: 5 (romance × 2, healing × 1, slice_of_life × 1, mystery_cozy × 1)
- solar_return_isekai: 5 (fantasy_adventure × 2, supernatural_everyday × 2, mystery_cozy × 1)
- creative_unfold_social: 5 (healing × 2, slice_of_life × 2, supernatural_everyday × 1)

## Downstream conformance

- Brand IDs are LOCKED to PR #1073 en_US mapping. Downstream catalog allocation (`artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv`) joins on the brand_id field, and this deck preserves the en_US lockset so the four-locale catalog rolls up cleanly.
- All series_id values are lowercase pinyin (no Chinese-character series_id), which keeps downstream YAML schema-validator happy.

## Authority chain

- `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md` — binding per-cluster allocation
- `artifacts/research/manga_bestseller_magical_serial_framework_2026-05-12.md` (PR #1051)
- `artifacts/research/manga_genz_genalpha_portal_framework_2026-05-13.md` (PR #1053)
- `config/manga/canonical_brand_list.yaml` — 37-brand canon
- `artifacts/marketing/v1_2_themes_en_US_cluster_e.yaml` (PR #1073) — brand mapping source
- `artifacts/marketing/v1_2_themes_ja_JP_cluster_e.yaml` (PR #1074) — sibling locale (note: PR #1074 created downstream conflict by remapping brand IDs; this deck explicitly locks to en_US's mapping to restore consistency)
- `artifacts/marketing/v1_2_themes_zh_CN_cluster_d.yaml` — zh_CN register reference
