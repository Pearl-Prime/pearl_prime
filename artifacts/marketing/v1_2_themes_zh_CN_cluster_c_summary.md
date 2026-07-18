# V1.2 Themes Cluster C × zh_CN — Summary

**Date:** 2026-05-11
**Author:** Pearl_Writer (Cluster C × zh_CN subagent)
**Cluster:** C — Grief / Trauma / Healing
**Locale:** zh_CN (Simplified Chinese, mainland-natural)
**Deliverable:** `artifacts/marketing/v1_2_themes_zh_CN_cluster_c.yaml`
**Constraint anchor:** `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`
**Sister-locale anchor:** `artifacts/marketing/v1_2_themes_ja_JP_cluster_c.yaml` (PR #1066)
**Tally:** 25 series = 5 brands × 5 series

## Genre allocation — within all binding ranges

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 5 | 4-5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 3 | 3 | ✅ |
| romance | 1 | 1-2 | ✅ |
| horror | 1 | 1 | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

## Strict-enum compliance

- `serial_engine` values used: `case_of_the_week` (11), `companion_roster` (4), `location_anthology` (4), `mystery_box` (2), `life_stage_rhythm` (2), `power_escalation_ladder` (2) — **all in allowed enum**.
- `magical_register` values used: `supernatural_everyday` (11), `magical_realism` (6), `soft_fantasy` (4), `none` (3), `occult_cosmic` (1) — **all in allowed enum**.
- `genre_family` values used: 7 distinct values, all from allowed enum.

## Platform fit — mainland-tilted 70/30

- `webtoon_vertical`: 18 (72%)
- `manga_traditional`: 7 (28%)

INVERTED from ja_JP (which was 70/30 manga-heavy) — mainland reflects Kuaikan / Bilibili Comics dominance for Gen Z / Mill while keeping a respected page register for older bereavement readers (海葬, 中元节 老宅, 三代同堂 老破小, 老破小 family).

## Persona distribution

- ML-bereaved: 13 (52%) — Cluster C tilts older than other clusters; bereavement realism rewards Mill register
- GZ-firstjob: 8 (32%)
- GZ-uni: 2 (8%)
- GZ-queer: 1 (4%) — pet-grief and chosen-family register
- GX-bereaved: 1 (4%) — 老家乡下屋 (rural elder return) anchor

Combined Gen Z layer (GZ-firstjob + GZ-uni + GZ-queer) = 11 of 25 = 44%. Mill+GX = 14 of 25 = 56%. The Cluster C ja_JP sister file ran similar (55% Mill+older). This is appropriate for grief/bereavement — Gen Alpha intentionally absent for content-fit reasons (per constraint doc note).

## Magical-register distribution

- supernatural_everyday: 11 (44%) — operator's "Natsume-of-anxiety" anchor, here "Natsume-of-grief"
- magical_realism: 6 (24%)
- soft_fantasy: 4 (16%)
- none: 3 (12%) — full realism for 再婚清节记, 老家的乡下屋, 老破小的七夕十三天
- occult_cosmic: 1 (4%) — 中元节的老宅

## Serial-engine distribution

`case_of_the_week` dominates (11 of 25, 44%) — fits the per-volume customer/case framing the cluster needs. Plus 4 each of companion_roster and location_anthology, 2 each of mystery_box, life_stage_rhythm, power_escalation_ladder.

## Volume runway

Median: **150 volumes** | min 130 | max 200. The 200-vol top is 穿车人:第十代 (穿越当代东北/华北废弃公路 fantasy_adventure) — the most franchise-able power_escalation_ladder series.

## Mainland-locale guidance (applied)

- 100% Simplified Chinese throughout free-text fields.
- Zero Taiwan/HK phrasing — strict mainland register (视频/软件/智能手机/互联网/地铁/出租车/信息).
- Mainland grief anchors used across the 25 series: 清明 (Qingming) tomb-sweeping, 中元节 (Hungry Ghost Festival) joss-paper / lao zhai displays, 七夕 (Qixi memorial / 信箱), 牌位 / 灵堂, 烧纸钱, 头七, 老家 (ancestral hometown), 长辈遗物, 海葬 (modern sea burial), 微信遗信 / 网络祭祀 (Mid-Autumn delivery anchor).
- Cultural-place anchors: 上海老破小, 西安西郊小区, 苏州平江路, 重庆江北, 杭州 西湖区, 武汉, 厦门海域, 福建闽南 老宅, 安溪, 腾冲驿道, 大理苍山, 西塘古镇, 北京西二旗, 沈阳铁西区, 南京老门东 巷, 南京建邺.
- Comp titles used: 一人之下, 罗小黑战记, 镖人, 葬送的芙莉莲, 全知读者视角, 雏蜂, 深夜食堂, 解忧杂货店 (中文版), 你的名字 (中文版).

## Content compliance — clean

- No politics, no Tibet/Xinjiang.
- 远嫁台湾的姑姑 reference (1 series, 中元节的老宅) deliberately scopes only to 安溪米粉/铁观音/小巷, with explicit author-note: "不写她在台湾的政治环境". Compliant under wellness/family register.
- 退伍兵 太极陪练 (重新学呼吸) explicitly notes "不写部队具体场景、不涉政治". Compliant.
- 灾后心理援助 series (后期的心理咨询室) handles 唐山 1976 / 长江 1998 / 汶川 2008 / 北京 721 2012 / 矿难 strictly as 代际话语 (intergenerational speech), no state critique.
- 海葬 (modern burial), 网络祭祀, 代扫服务 are written as民政部门合规挂牌 / 民政部门批准 — explicitly aligned with state-led memorial framework.

## Brand × series tally

1. **spiritual_ground_supernatural** (← grief_companion_iyashikei) — 5 series — 灵堂前的第二张椅子, 奶奶的菜谱盒, 夜班宠物殡仪馆, 二次葬礼茶馆, 西郊小区的陪安人 — genres: healing×2, slice_of_life×2, mystery_cozy×1
2. **trauma_path_healing** (← trauma_recovery_shojo) — 5 series — 照片里的空白人, 楼下洗衣店的口袋信, 七夕夜的信箱, 雨林创伤康愈园, 再婚清节记 — genres: healing×1, slice_of_life×1, supernatural_everyday×1, fantasy_adventure×1, romance×1
3. **healing_ground_healing** (exact) — 5 series — 社区自强园的二楼, 清明无主墓档案, 老家的乡下屋, 中元节的老宅, 三代同堂的小阳台 — genres: healing×2, mystery_cozy×1, slice_of_life×1, horror×1
4. **warrior_calm_cultivation** (← ash_and_steel_warrior_calm) — 5 series — 灰与缘:古驿门, 老家的旧刀, 重新学呼吸, 一批旧折扇子的传, 后期的心理咨询室 — genres: fantasy_adventure×1, supernatural_everyday×1, healing×1, mystery_cozy×2
5. **stoic_edge_battle** (← surrender_form_warrior_calm) — 5 series — 老破小家庭的七夕十三天, 穿车人:第十代, 海葬船的七夕, 中元节的快递员, 纸钱折叠师的三月 — genres: slice_of_life×1, fantasy_adventure×1, supernatural_everyday×3

## Validation results

- `python3 scripts/ci/audit_llm_callers.py` → `violation_count: 0` ✅
- YAML parses cleanly via `yaml.safe_load` ✅
- 25/25 series ✅
- 5/5 brands × 5/5 per brand ✅
- 0 file deletions ✅
- 2 staged files (yaml + this MD) when PR opens ✅

## Out of scope

- Per-series persona-archetype lookup mapping (handled in canonical persona registry).
- Per-locale 125-target rollup (handled by Pearl_PM after all 5 clusters × 4 locales land).
- comp_titles regional licensing (handled by Pearl_Architect at portfolio level).
