# V1.2 Cluster C × zh_TW — Authoring Summary

**Cluster:** C — Grief/Trauma/Healing
**Locale:** zh_TW (Traditional Chinese, Taiwan-natural)
**Deliverable:** `artifacts/marketing/v1_2_themes_zh_TW_cluster_c.yaml`
**Author:** Pearl_Writer (Claude subagent, Tier 1)
**Date:** 2026-05-11
**Total series:** 25 (5 brands × 5 series)

## Brand mapping (V1.1 → V1.2)

| V1.1 brand_id (cluster spec) | V1.2 brand_id (used in YAML) | Series count |
|---|---|---|
| grief_companion_iyashikei | `spiritual_ground_supernatural` | 5 |
| trauma_recovery_shojo | `trauma_path_healing` | 5 |
| healing_ground | `healing_ground_healing` | 5 |
| ash_and_steel_warrior_calm | `warrior_calm_cultivation` | 5 |
| surrender_form_warrior_calm | `stoic_edge_battle` | 5 |
| **Total** | | **25** |

Brand mapping follows the precedent established in PR #1061 (en_US Cluster C) and PR #1066 (ja_JP Cluster C).

## Genre allocation validation

Per `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`:

| genre_family | count | target (per cluster) | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 4 | 4–5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 3 | 3 | ✅ |
| romance | 1 | 1–2 | ✅ |
| horror | 1 | 1 | ✅ |
| other | 1 | 0–1 | ✅ |
| school | 0 | 0–1 | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

All 8 used genre families are within the binding range. STRICT enum compliance: only the V1.2-allowed genre families used (`healing | slice_of_life | supernatural_everyday | mystery_cozy | fantasy_adventure | romance | horror | other`).

## Structural enum distributions

### magical_register (V1.2 STRICT enum)

| value | count | share |
|---|---|---|
| supernatural_everyday | 9 | 36% |
| magical_realism | 8 | 32% |
| none | 4 | 16% |
| soft_fantasy | 3 | 12% |
| occult_cosmic | 1 | 4% |
| **TOTAL** | **25** | **100%** |

No `high_fantasy` (banned in V1.2). No `isekai` (Cluster C grief register does not invite isekai). Distribution aligns with the global advisory: supernatural_everyday + magical_realism dominate, with realist (`none`) at ~16% giving the Honey-Lemon-Soda-style portfolio balance for grief register.

### serial_engine (V1.2 STRICT enum)

| value | count |
|---|---|
| case_of_the_week | 15 |
| companion_roster | 3 |
| life_stage_rhythm | 3 |
| power_escalation_ladder | 3 |
| location_anthology | 1 |
| **TOTAL** | **25** |

`case_of_the_week` dominates (60%) because Cluster C's strongest engine is the customer/case-of-the-week iyashikei pattern (Mushishi, Natsume, Apothecary, Quick Stop, Bartender). `power_escalation_ladder` reserved for the two warrior_calm brands' battle-adjacent series + the modern dojo healing. No `mystery_box` (not a fit for Cluster C's open-emotional-stakes register).

## Reading platform fit

| value | count | share |
|---|---|---|
| webtoon_vertical | 13 | 52% |
| manga_traditional | 12 | 48% |
| **TOTAL** | **25** | **100%** |

Close to the locale target ~55% webtoon / ~45% manga. zh_TW slightly tilts webtoon vs the inverted ja_JP ratio (ja_JP Cluster C went 70% manga_traditional for older bereavement demographic).

## Persona allocation

| persona_archetype | count | share |
|---|---|---|
| GZ-firstjob | 8 | 32% |
| ML-bereaved | 8 | 32% |
| GZ-uni | 6 | 24% |
| GA-tween | 2 | 8% |
| GX-late | 1 | 4% |
| **TOTAL** | **25** | **100%** |

- **Gen Z (GZ-firstjob + GZ-uni):** 14/25 = 56% — matches the ~55% target.
- **Millennial (ML-bereaved):** 8/25 = 32% — matches the ~30% target.
- **Gen Alpha (GA-tween):** 2/25 = 8% — matches the ~10% target (limited bereavement fit for under-13 demographic, applied in healing_ground山羌 + 中藥房 stories with adult co-read).
- **Gen X (GX-late):** 1/25 = 4% — matches the ~5% target.

## Runway target

- Range: 120–200 volumes
- **Median: 140 volumes**
- Mean: ~144 volumes
- Distribution: 3×120 / 6×130 / 7×140 / 5×150 / 1×160 / 2×180 / 1×200

The two warrior_calm series (`shi_yong_de_xiao_yao` 180, `shan_de_shou_che_ren` 200) carry the longest runways — power_escalation_ladder engine + soft_fantasy register supports it. The healing_ground iyashikei spine sits at 130–150.

## zh_TW locale compliance (zero-mainland-phrasing audit)

All series authored in 100% Traditional Chinese, Taiwan-natural prose. Verified avoidance of mainland forms:
- ✅ No `视频` (used `影片` where applicable; no instances needed)
- ✅ No `软件` (no instances)
- ✅ No `智能手机` (no instances)
- ✅ No `互联网` (no instances)
- ✅ No `地铁` (used `MRT` / `捷運` where applicable)
- ✅ No `外卖` (used `外送` for `vol_2` brand-2 reference)
- ✅ No `打的` (used `搭客運` / `普悠瑪` / `機車`)

Cluster C TW-specific grief anchors actually used in the YAML prose:
- 中元 / 七月十五 / 庫銀 (B1 #1 七月的信箱; B1 #4 中元的紙錢店)
- 大稻埕迪化街、媽祖廟 (B1 #1)
- 燒王船祭、東港 (B1 #3 燒王船的小鎮)
- 鹿港老街 (B1 #4)
- 宜蘭壯圍海邊、清明 (B1 #5)
- 萬華、永和、內湖、新店、敦化南路 (B1 #2; B3 #2)
- 台南安平海堤 (B3 #1)
- 花蓮玉里 (B3 #3)
- 三義木雕 (B3 #4)
- 台東池上 (B3 #5)
- 信義鄉、玉山腳下、布農族 (B4 #4)
- 蘭嶼/綠島感的虛構黑潮諸島 (B5 #1)
- 礁溪到頭城濱海公路 (B5 #2)
- 桃園八德、二手書攤、退役士官長 (B5 #4)
- 逢甲夜市 (B5 #5)
- 排灣族口傳感、中央山脈虛構化的『靜山院』 (B4 #1, B4 #2)

Cultural references span north (台北/新北/桃園), central (彰化/南投/苗栗/台中/員林), south (台南/高雄/東港), east (宜蘭/花蓮/台東), and offshore (黑潮諸島虛構化) — wide TW geographic coverage rather than Taipei-only.

## Tone reference

`死神的精準度` (Schedule of Death) + `用九柑仔店` (Lin Family Store) + `神隱少女` (Spirited Away) — Ghost Festival realism with Ghibli soft-magic register. comp_titles cite: 用九柑仔店, 修羅之刻, 葬送的芙莉蓮, 海街日記, 送行者, 深夜食堂, 可不可以你也剛好喜歡我, 神隱少女, 螢火之森, 蟲師, 茶金, 幸福路上, BANANA FISH, 棋靈王, BECK, 四月是你的謊言, 82 年生的金智英, 孤味, 你的孩子不是你的孩子, 我吃了那個男孩一整年的早餐, 陽光普照, 返校, 湯道, 鋼之鍊金術師, Solo Leveling, 全知讀者視角, 魔法少女小圓, 黃金神威, 鬼太郎, 夏目友人帳, 天橋上的魔術師, 便利店人間, 前任行星, 海邊的卡夫卡 — all titles either internationally distributed or culturally well-known to TW readers.

## Files in this PR

1. `artifacts/marketing/v1_2_themes_zh_TW_cluster_c.yaml` — 25 series (NEW)
2. `artifacts/marketing/v1_2_themes_zh_TW_cluster_c_summary.md` — this file (NEW)

Total file write scope: 2 files (within ≤4 file limit). Zero deletions.
