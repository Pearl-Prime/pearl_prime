# V1.2 themes — Cluster E (Gen-Alpha/School/Identity) × zh_TW — Summary

**File:** `artifacts/marketing/v1_2_themes_zh_TW_cluster_e.yaml`
**Locale:** zh_TW (Traditional Chinese, Taiwan-natural)
**Cluster:** E — Gen-Alpha/School/Identity (the heaviest Gen Alpha cluster)
**Date:** 2026-05-11
**Author:** Pearl_Writer (Cluster E × zh_TW subagent)
**Constraint:** `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`

## Brand mapping (LOCKED from PR #1073 en_US — no invented mappings)

| constraint brand_id | canonical brand_id used here | series count |
|---|---|---|
| digital_ground | `digital_ground` | 5 |
| gen_z_grounding | `calm_student_school` | 5 |
| confidence_core | `confidence_core_romance` | 5 |
| mecha_identity | `solar_return_isekai` | 5 |
| queer_identity_growth | `creative_unfold_social` | 5 |
| **TOTAL** | — | **25** |

## Genre allocation validation

Target (per `v1_2_genre_allocation_constraint_2026-05-12.md`, Cluster E with school bumped to 2-3):

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 4 | 4-5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 2 | 2-3 | ✅ |
| romance | 2 | 1-2 | ✅ |
| school | 2 | 2-3 (bumped) | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

Mirrors the en_US Cluster E (PR #1073) distribution exactly for cross-locale comparability.

## Magical register distribution

| magical_register | count |
|---|---|
| supernatural_everyday | 7 |
| magical_realism | 6 |
| isekai | 3 |
| none | 9 |
| **TOTAL** | **25** |

`none` count is intentionally elevated for Cluster E because realist school slice-of-life + realist initial romance is the dominant register for the 那些年 + Heartstopper + Komi-san comp-space — Gen Alpha school stories often need no magic at all.

## Reading platform mix

| platform | count | share |
|---|---|---|
| webtoon_vertical | 14 | 56% |
| manga_traditional | 11 | 44% |

Target was ~55/45. Within tolerance.

## Persona allocation

| archetype | count | share |
|---|---|---|
| GA-quiet | 10 | 40% |
| GA-streamer | 8 | 32% |
| GA-coder | 3 | 12% |
| GA-queer | 1 | 4% |
| GZ-uni | 3 | 12% |

**Gen Alpha total: 22/25 = 88%.** Floor was ≥35%; Cluster E is the heaviest-GA cluster per the brief. This is consistent with the cluster's "Gen-Alpha/School/Identity" remit and mirrors en_US Cluster E's GA-heavy weighting. Gen Z is represented by 3 university-age series (digital_ground S3 `day_1247`, digital_ground S5 `禮拜天凌晨一點`, creative_unfold_social S5 `凌晨兩點的讀書會`) for portfolio coverage.

## Volume runway

- median: 175 volumes
- min: 145 volumes (creative_unfold_social S4 `三個粉絲也夠` — life_stage_rhythm with finite arc)
- max: 200 volumes (digital_ground S1 `覆蓋層看得見`, relational_calm parallel S1, solar_return_isekai S1 `誠實才會啟動的機甲` — flagship long-burns)

## Taiwan-natural register checks

- Banned mainland phrases (視頻 / 軟件 / 智能手機 / 互聯網 / 編程 / 學霸 / 學渣 / 信息 / 質量 / 服務器 / 數據 / 文件夾): zero in content body. Only appear in the YAML header comment listing them as forbidden.
- TW-specific anchors used across the 25 series: 校門口/通學路、社團活動、校慶、補習班、班導、福利社、中和、永和、板橋、永康街、大稻埕、迪化街、信義區、大安、松山、公館、捷運橘線、UBike、會考、學測、推甄.
- comp_titles: drawn from the operator's approved zh_TW Cluster E list — 那些年,我們一起追的女孩, Heartstopper, Komi-san は、コミュ症です, 葬送のフリーレン, SPY×FAMILY, 我的英雄學院, 排球少年, 鬼滅之刃, 海街diary, 你的婚禮, 我吃了那個男孩一整年的早餐, 藥師少女的獨語, 用九柑仔店, 解憂雜貨店, 深夜食堂, 便利店人間.
- Voice register: 那些年 + Heartstopper + Komi-san (earnest TW school romance + queer/identity warmth without TikTok-cringe), per brief.

## Five-brand series index

### Brand 01 — `digital_ground` (manhwa · 數位身分/倦怠/科技焦慮)
1. 覆蓋層看得見 — healing — 直播 overlay 標出快崩潰的觀眾
2. 置物櫃葉子 — healing — 國二 App 寫程式社的情緒儀表板
3. 第 1,247 天 — mystery_cozy — Z 世代 AI 陪伴推理
4. 服務分級 — mystery_cozy — 校園 IT 服務台 Wi-Fi 公平
5. 禮拜天凌晨一點 — slice_of_life — 資工系凌晨一點 Discord 共學

### Brand 02 — `calm_student_school` (← gen_z_grounding · shojo · 校園接地)
1. 第一節上課前的呼吸 — school — 校門口榕樹接地小儀式
2. 代課老師教的那一口氣 — school — 國三會考前 30 秒呼吸
3. 繞遠路回家 — slice_of_life — 國三放學共走中和
4. 圖書館的考試焦慮診所 — healing — 高二圖書館窗口小盒子
5. 上學路的小灰 — supernatural_everyday — 通學路上外婆派來的貓

### Brand 03 — `confidence_core_romance` (shojo · 自我價值/校園戀愛)
1. 傳錯的紙條 — romance — 高一同性安靜初戀
2. 筆友叫我勇敢的人 — romance — 東西部書信戀愛
3. 外婆的玉珮 — healing — 三代家族傳承療癒
4. 永康街古著店 — slice_of_life — 高二 42 件不敢穿
5. 候補日記 — mystery_cozy — 校慶話劇社候補預言日記

### Brand 04 — `solar_return_isekai` (← mecha_identity · shonen · isekai/身份)
1. 誠實才會啟動的機甲 — fantasy_adventure — 國三機甲只在誠實才動
2. 自插角色回信給我 — fantasy_adventure — 高二同人 isekai 反向
3. 鏡子裡真的稱呼 — supernatural_everyday — 國三性別認同探索
4. 存檔裡的爺爺 — mystery_cozy — 高三遺愛 RPG grief-work
5. K-pop 舞蹈教我重新認識身體 — supernatural_everyday — 國二飲食焦慮 K-pop 練舞

### Brand 05 — `creative_unfold_social` (← queer_identity_growth · shojo · 創意/社交焦慮/酷兒)
1. 圖書館的酷兒小誌 — healing — 高二酷兒匿名小誌
2. 美術教室午休的安靜 — slice_of_life — 四人不講話聯展
3. 夾克裡那封沒寄出的信 — supernatural_everyday — 二手店 1998 告白信追查
4. 三個粉絲也夠 — slice_of_life — 反流量每週三 9 點貼圖
5. 凌晨兩點的讀書會 — healing — 神經多樣性凌晨共學

## CLOSEOUT delta vs en_US Cluster E (PR #1073)

- Same 5 brand_ids in same order — locked.
- Same genre distribution (6/5/4/4/2/2/2 = 25).
- Localised settings: New Taipei 中和/永和/板橋, Taipei 大稻埕/永康街/松山/信義, Hualien 鳳林, Taichung. School realities: 會考/學測/推甄/補習班/班導.
- Localised comp_titles: 那些年/你的婚禮/我吃了那個男孩一整年的早餐/海街diary/用九柑仔店 alongside the shared global anchors.
- Heaviest Gen Alpha cluster sustained (88%).
