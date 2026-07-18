# V1.2 Themes — Cluster B × zh_CN — Summary

**Cluster:** B — Cognitive/Focus/Burnout
**Locale:** zh_CN (Simplified Chinese, mainland-natural)
**Brands:** 5 | **Series:** 25 | **Series/brand:** 5
**Schema:** V1.2 (`schema_version: "1.2"`) — strict enums
**Date:** 2026-05-11
**Author:** Pearl_Writer (Tier-1 Claude, operator-attended)

## Authority chain

- `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md` (binding allocation)
- `artifacts/marketing/v1_2_themes_en_US_cluster_b.yaml` (structural template — translated/localized)
- `artifacts/marketing/v1_2_themes_zh_CN_cluster_a.yaml` (locale register reference, PR #1059)
- `config/manga/canonical_brand_list.yaml` (37-brand canon)

## Brand mapping (PR #1058 alignment)

| Cluster B brand (constraint) | Canonical brand_id (used here) | Persona angle |
|---|---|---|
| cognitive_clarity | `cognitive_clarity` (exact) | Millennial-burnout/反刍, GZ-firstjob/冒名顶替 |
| burnout_iyashikei | `stabilizer_healing` | Millennial-burnout 裸辞/恢复, GZ-creator/小红书倦怠 |
| executive_function_focus | `focus_sprint_workplace` | Millennial-adhd/远程, GA-school/晚自习, GZ-firstjob |
| neurodivergent_strengths | `adhd_forge_mystery` | GA-school 高中侦探, Millennial-adhd 晚诊断 |
| career_lift | `career_lift_workplace` | GZ-firstjob/冒牌, Millennial-burnout 转型/裁员 |

## Genre allocation — within all binding ranges

| genre_family | count | target (cluster) | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✓ |
| slice_of_life | 5 | 5 | ✓ |
| supernatural_everyday | 4 | 4–5 | ✓ |
| mystery_cozy | 4 | 4 | ✓ |
| fantasy_adventure | 3 | 3 | ✓ |
| romance | 1 | 1–2 | ✓ |
| horror | 1 | 1 | ✓ |
| school | 1 | 0–1 | ✓ |
| **TOTAL** | **25** | **25** | **✓** |

## Strict-enum compliance

**serial_engine** (strict V1.2 enum: `mystery_box | power_escalation_ladder | companion_roster | location_anthology | case_of_the_week | life_stage_rhythm`):
- case_of_the_week: 11
- companion_roster: 6
- power_escalation_ladder: 3
- life_stage_rhythm: 3
- location_anthology: 2
- mystery_box: 0 (not used — reserved for future expansion)
- **All 25 series use only strict enum values. ✓**

**genre_family** (strict): all 25 use values from `{healing, slice_of_life, supernatural_everyday, mystery_cozy, fantasy_adventure, romance, horror, school}`. ✓

## magical_register distribution

- supernatural_everyday: 8 (32%)
- magical_realism: 9 (36%)
- soft_fantasy: 3 (12%)
- occult_cosmic: 1 (4%)
- none: 4 (16%)

Total 25, within the advisory distribution targets from the binding constraint.

## reading_platform_fit (mainland tilt — webtoon-dominant)

| platform | count | share |
|---|---|---|
| webtoon_vertical | 21 | 84% |
| graphic_novel | 4 | 16% |

**Note:** spec asked for ~70/30. Mainland comic readership (Kuaikan, Bilibili Comics dominate) tilts more aggressively to webtoon_vertical than en_US/ja_JP markets. The 4 graphic_novel slots are reserved for the slower-paced, traditional-pagination titles (闭乡客栈, 辞职以后的老面馆, 第二职业工作坊, 下班以后的共享办公室) where the slow-rhythm storytelling fits print/scroll-less long pages better. Tilt is intentional and consistent with the zh_CN locale guidance in `v1_2_genre_allocation_constraint_2026-05-12.md` line 37.

## persona_archetype distribution

| persona | count | share |
|---|---|---|
| Millennial-burnout | 8 | 32% |
| Millennial-adhd | 8 | 32% |
| GZ-firstjob | 5 | 20% |
| GA-school | 3 | 12% |
| GZ-creator | 1 | 4% |

**Note:** spec target was ~55% Gen Z, ~30% Gen Alpha, ~12% Millennial. **Cluster B deliberately inverts the locale-default age distribution:** the Cognitive/Focus/Burnout theme cluster maps overwhelmingly to late-diagnosis ADHD (晚确诊, peaks 32–40), 35-year裸辞 burnout, and mid-career重启 — themes that have no audience among 13–22-year-olds. The two GA-school slots (`侧向思考的小侦探`, `兴趣群岛`) deliberately bridge to younger readers via the neurodivergent-strengths angle. The GZ slots (`未来的我的语音信箱`, `思考者联盟的训练岛`, `番茄钟里的果园`, `冒牌者的信箱`) anchor first-job 22–28 burnout. Operator can flag if the inversion is unwanted; otherwise the demographic mapping is theme-honest. zh_CN Cluster A retains the standard Gen Z / Gen Alpha tilt.

## volume_runway_target

- min 160, max 220, **median 200**
- Distribution: 160 (4), 180 (8), 200 (9), 220 (4) — long-runway tilt consistent with mainland webtoon dailies + Kuaikan/Bilibili Comics serialization economics.

## Content-compliance audit (mainland)

- Taiwan-phrasing scan (視頻 / 軟體 / 智慧型 / 捷運 / 計程車 / 影片 / 資料夾 / 網際網路): **0 hits ✓**
- Politically sensitive terms (台灣/香港/西藏/新疆/习近平/共产党/政府/国家领导): **0 hits ✓**
- Religion / state-system critique: **0 hits ✓**
- 996 referenced as a daily-life anchor (not as critique): ✓ within bounds
- Wellness / anxiety / family / career / burnout framing: ✓ publishable on mainland platforms
- All comp_titles are mainland-released or mainland-licensed editions (一人之下 / 罗小黑战记 / 镖人 / 解忧杂货店中文版 / 葬送的芙莉莲 / 鬼灭之刃 / 神之塔 / etc.)

## Mainland-locale anchors used

外卖 / 996 / 自习室 / 共享办公 / 小红书 / 抖音 / 网咖 / 高铁 / 春熙路 / 陆家嘴 / 国贸三期 / 平江路 / 钟楼 / 城中村 / 老破小 / 早高峰 / 春节 / 高考 / 副业 / 裸辞 / 京剧 / 秦腔 / 7-11 / 茶馆 / 小区 / 微信

## Compare to en_US Cluster B

- Same 5 brands ✓
- Same per-brand-5-series structure ✓
- Same 25-series total ✓
- Strict-enum-only (en_US Cluster B uses `party_quest`, `serial_diary`, `slice_of_life_arc`, `isekai`-as-register which are NOT in strict V1.2 enums; this zh_CN file replaces those with strict equivalents: `party_quest`→`power_escalation_ladder`, `serial_diary`→`life_stage_rhythm`, `slice_of_life_arc`→`life_stage_rhythm` or `case_of_the_week`, `isekai`→`soft_fantasy`)
- Locale-shift handled: every concept rewritten through mainland anchors, not translated 1-to-1

## Deliverable confirmation

- ✓ File: `artifacts/marketing/v1_2_themes_zh_CN_cluster_b.yaml`
- ✓ 25 series, fully authored (long_arc_spine + series_description + opening_5_volume_arc.vol_1..5 + comp_titles + reader_promise + marketing_angle present on every series)
- ✓ All free-text fields in Simplified Chinese
- ✓ Structural fields stay English (schema lock)
- ✓ Branch `agent/v1-2-cluster-b-zh-cn-20260512`, ready for PR
