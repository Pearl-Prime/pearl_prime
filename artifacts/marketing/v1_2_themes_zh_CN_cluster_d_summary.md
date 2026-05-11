# V1.2 themes — Cluster D (Relational/Connection/Family) × zh_CN — summary

**Deliverable:** `artifacts/marketing/v1_2_themes_zh_CN_cluster_d.yaml`
**Series:** 25 (5 brands × 5)
**Locale:** zh_CN (Simplified Chinese, mainland-natural)
**Cluster:** D — Relational/Connection/Family
**Constraint anchor:** `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`

## Brand mapping

| Constraint-doc name | Canonical brand_id | Notes |
|---|---|---|
| relational_calm_iyashikei | relational_calm_iyashikei | exact |
| inner_security | confidence_core_romance | mapped (shojo self-worth ≈ inner-security) |
| bright_presence | bright_presence_tw_seinen | exact root |
| found_family_shojo | heart_balance_shojo | mapped (josei relational shojo) |
| communal_warmth | resilient_parent_social | mapped (josei communal/family) |

## Genre allocation (cluster D target range vs actual)

| genre_family | actual | target | range | within_range |
|---|---|---|---|---|
| healing | 6 | 6 | floor 6 | ✅ |
| slice_of_life | 5 | 5 | 4-6 | ✅ |
| supernatural_everyday | 5 | 4-5 | 4-5 | ✅ |
| mystery_cozy | 4 | 4 | 3-5 | ✅ |
| fantasy_adventure | 3 | 3 | 2-4 | ✅ |
| romance | 1 | 1-2 | 1-2 | ✅ |
| horror | 1 | 0-1 | 0-1 | ✅ |
| **TOTAL** | **25** | **25** | — | ✅ |

## Other distributions

- **magical_register** (V1.2 strict enum, 6 allowed): supernatural_everyday=10, magical_realism=6, none=6, soft_fantasy=2, occult_cosmic=1 (5 of 6 enums used; isekai unused — Cluster D family-themed doesn't lend itself to isekai).
- **reading_platform_fit:** webtoon_vertical=20 / manga_traditional=5 (80/20). Target was 70/30 — webtoon slightly over-tilted. Justification: Cluster D Gen Z + Gen Alpha persona skew + Kuaikan/Bilibili Comics mainland dominance. The 5 manga_traditional slots concentrated in `bright_presence_tw_seinen` (seinen pacing) and `resilient_parent_social` 中元节 series (page register for somber theme).
- **persona_archetype:** ML-mid=10 / GZ-firstjob=8 / GA-tween=5 / GZ-uni=2. Tilts older vs. en_US cluster-D guidance (~55% GZ, ~30% GA). **Deliberate authorial choice:** Cluster D zh_CN anchors (春节回家催婚, 重组家庭, 留守儿童, 中元节餐桌, 失独, 寻亲群) are intrinsically Mill-anchored on the mainland; the Gen Alpha slice (5/25 = 20%) concentrates in brand 02 (重组家庭周末桌, 老家小区奶奶, 视频通话, 表兄妹) and brand 04 (姐妹小仪式), exactly the sibling/cousin/intergenerational territory called out in the prompt's 'Gen Alpha sibling/cousin bonds are common in CN family unit'.
- **serial_engine:** case_of_the_week=15 / companion_roster=5 / life_stage_rhythm=5. case_of_the_week dominates because the Cluster D engine `客人/一卷一户人家` (one family per volume) maps natively to case_of_the_week.
- **volume_runway_target:** median 150, min 100, max 200. All within the V1.2 range. Median 150 sits at the V1.2 healthy-runway target.

## Mainland-locale phrasing compliance

- Zero Taiwan-phrasing detected: 視頻/軟體/智慧型/網路/臺灣/臺北/捷運 — all absent.
- Uses 视频, 软件, 智能手机, 互联网, 信息, 微信, 地铁, 公房, 老破小, 春节, 中元节, 清明, 表兄妹, 姑姑/舅舅, 留守儿童, 失独, 寻亲 throughout.
- City anchors used: 杭州, 成都, 武汉, 重庆, 上海, 北京, 西安, 苏州, 大理, 天津, 长沙, 济南, 贵州毕节, 山东曲阜, 广州花都, 河北沧州, 南京, 深圳. All mainland.
- comp_titles uniformly mainland-resonant IP family: 一人之下, 罗小黑战记, 葬送的芙莉莲, 深夜食堂, 镖人, 解忧杂货店 (中文版), Heartstopper, Honey Lemon Soda.

## Content-compliance scan

- ✅ No politics, no governance critique.
- ✅ No Taiwan/HK/Tibet/Xinjiang references.
- ✅ Family/intergenerational/blended-family/留守/失独/寻亲 themes framed as warmth, never as social critique. Magical register abstracts the more sensitive emotional content (失独 父亲, 中元节 餐桌, 寻亲 群里失踪人口) into supernatural_everyday / occult_cosmic / magical_realism tonalities.
- ✅ The single horror series (中元节的餐桌) is explicitly framed in description: "不血腥, 无恶灵, 只有家族里没说完的话" — 悲伤 not 惊吓.

## Tone reference (operator-specified)

- 一人之下 grounded-supernatural底色 (家族, 师徒, 市井)
- 罗小黑战记 modern-yokai 温度 (小孩眼睛, 小妖怪)
- 哪吒之魔童降世 family-warmth (家庭引擎, 不是 plot 装饰)
- All 25 series treat 家 as the engine, not the backdrop.

## Engineering notes

- Schema: V1.2 strict enums respected throughout (6 magical_registers, 12 genre_families, structural fields in English).
- File size: 740 lines, all under one file (within the ≤4 file write_scope).
- Zero deletions. Pure append per brand commit.
- audit_llm_callers expected clean (no LLM SDK calls added).
- Mass-deletion guard: only new files added, 0 deletions.
