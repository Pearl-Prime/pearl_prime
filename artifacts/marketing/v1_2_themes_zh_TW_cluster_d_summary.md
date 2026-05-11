# V1.2 themes summary — Cluster D × zh_TW (Relational/Connection/Family)

**File:** `artifacts/marketing/v1_2_themes_zh_TW_cluster_d.yaml`
**Locale:** zh_TW (Traditional Chinese, Taiwan-natural)
**Cluster:** D — Relational/Connection/Family
**Authoring date:** 2026-05-11
**Authority:** `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`

## Scope delivered

- 25 fully authored series (target: 25)
- 5 brands × 5 series each
- 100% Traditional Chinese, Taiwan-natural register
- 0 mainland phrasing in content body (header comment lists banned words as guidance)

## Brand distribution

| Brand | Series | Register |
|---|---|---|
| relational_calm_iyashikei | 5 | core · josei · 社交焦慮療癒 |
| confidence_core_romance (← inner_security) | 5 | core · shojo · 內在安全感 |
| bright_presence_tw_seinen | 5 | core · seinen · 亮系男性向 |
| heart_balance_shojo (← found_family_shojo) | 5 | core · josei/shojo · 非血緣家 |
| resilient_parent_social (← communal_warmth) | 5 | core · josei · 共同養育/社群 |

## Genre allocation (within constraint ranges)

| genre_family | Count | Target range | Status |
|---|---|---|---|
| healing | 6 | 6 (HARD floor) | meets floor |
| slice_of_life | 5 | 5 | meets target |
| supernatural_everyday | 5 | 4-5 | within range |
| mystery_cozy | 4 | 4 | meets target |
| fantasy_adventure | 3 | 3 | meets target |
| romance | 2 | 1-2 | at ceiling |
| **TOTAL** | **25** | **25** | OK |

## Serial engine distribution (STRICT enum)

- case_of_the_week: 9
- companion_roster: 5
- life_stage_rhythm: 5
- mystery_box: 3
- location_anthology: 2
- power_escalation_ladder: 1

All values in approved enum: `{mystery_box, power_escalation_ladder, companion_roster, location_anthology, case_of_the_week, life_stage_rhythm}`.

## Magical register distribution (STRICT enum)

- supernatural_everyday: 8
- magical_realism: 8
- none: 6
- soft_fantasy: 3

All values in approved enum: `{supernatural_everyday, magical_realism, soft_fantasy, isekai, occult_cosmic, none}`.

## Reading platform fit

- webtoon_vertical: 18 (72%)
- manga_traditional: 4 (16%)
- both: 3 (12%)

Effective webtoon-leaning ≈ 18/25 = 72% with 3 dual-platform — meets ~55% webtoon target with plenty of headroom.

## Volume runway target

- Min: 100 (a controlled-arc romance — 轉租一年, twelve-month structure)
- Max: 200
- Median: 175

## Persona distribution

- Gen Z (GZ-uni / GZ-firstjob): ~15 (60%)
- Gen Alpha (GA-mid): 2 (8%)
- Millennial (Mill-mid / Mill-careerist / Mill-parent): 8 (32%)

Skews Gen Z chosen-family + parental Mill — operator's "Heartstopper grew up" + "communal parenting" demographic.

## Taiwan-natural anchors used

夜市、媽祖廟、春節圍爐、中秋烤肉、冬至湯圓、寒暑假鄉下、雙北小巷、台南老街、花蓮玉里、雲林斗六、高雄苓雅、屏東鵝鑾鼻、陽明山、永康街、寧夏夜市、大稻埕、師大商圈、忠孝東路、新北永和/中和/板橋、台中北屯/南屯。

## Comp-title coverage

Heavy use of: 用九柑仔店, 葬送のフリーレン, 海街diary, 深夜食堂, 解憂雜貨店, 你的婚禮, 可不可以,你也剛好喜歡我, 我吃了那個男孩一整年的早餐, 神隱少女, 夏目友人帳, SPY×FAMILY, 千與千尋, MIU404, 蟲師, 千年女優, 孤獨的美食家, 媽媽,我可以這樣不一樣嗎.

All Taiwan-publication-native or major Japanese imports widely sold in TW. Zero China-mainland-only comp titles.

## Voice register

用九柑仔店 humanist + 神隱少女 magical + 海街diary family-warmth.

Tender, communal, specific. No greeting-card prose. Emotional engine across cluster: chosen family / family repair is built on small specific acts (a meal at a set time every week, a ritual no one else understands, a door always unlocked, a soup with the right one-sentence blessing).

## Compliance

- audit_llm_callers: 0 callers added (data file only).
- copyright: 0 (all original characters and series titles).
- deletions: 0 — file was new on this branch.
- file write_scope: 2 (YAML + this summary).
- 100% Traditional Chinese in content body.
- Mainland-phrasing scan: clean in body (banned terms appear only in the header guidance comment).

## Next actions

- Architect: ingest into V1.2 catalog plan.
- Manga ops: factor into zh_TW catalog batch (relational/family cluster slot).
- No follow-up edits expected; ready for downstream consumption.
