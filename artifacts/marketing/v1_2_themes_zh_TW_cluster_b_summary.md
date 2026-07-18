# V1.2 themes — Cluster B × zh_TW — Summary

**File**: `artifacts/marketing/v1_2_themes_zh_TW_cluster_b.yaml`
**Date**: 2026-05-11
**Author**: Pearl_Writer (Tier 1 Claude, operator-present)
**Branch**: `agent/v1-2-cluster-b-zh-tw-20260512`

## Scope
- **Locale**: zh_TW (Traditional Chinese, Taiwan-natural)
- **Cluster**: B — Cognitive / Focus / Burnout
- **Brands**: 5 × **Series per brand**: 5 = **25 series total**
- **Schema**: V1.2 (matching PR #1060 zh_TW Cluster A, PR #1062 ja_JP Cluster B)

## Per-brand counts

| # | Brand | Genres delivered | Series count |
|---|---|---|---|
| 01 | `cognitive_clarity` | healing×2, slice_of_life, supernatural_everyday, mystery_cozy | 5 |
| 02 | `stabilizer_healing` | healing×2, supernatural_everyday, slice_of_life, horror | 5 |
| 03 | `focus_sprint_workplace` | healing, mystery_cozy, supernatural_everyday, slice_of_life, fantasy_adventure | 5 |
| 04 | `adhd_forge_mystery` | mystery_cozy×2, fantasy_adventure, supernatural_everyday, slice_of_life | 5 |
| 05 | `career_lift_workplace` | healing, fantasy_adventure, romance, school, slice_of_life | 5 |
| **TOTAL** | | | **25** |

## Genre allocation — within constraint ranges

Constraint (from `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`):
- healing: 6, slice_of_life: 5, supernatural_everyday: 4–5, mystery_cozy: 4, fantasy_adventure: 3, romance: 1–2, horror: 1, school: 0–1, other: 0–1

| genre_family | Target | Delivered | within_range |
|---|---|---|---|
| healing | 6 | 6 | YES |
| slice_of_life | 5 | 5 | YES |
| supernatural_everyday | 4–5 | 4 | YES |
| mystery_cozy | 4 | 4 | YES |
| fantasy_adventure | 3 | 3 | YES |
| romance | 1–2 | 1 | YES |
| horror | 1 | 1 | YES |
| school | 0–1 | 1 | YES |
| other | 0–1 | 0 | YES |
| **TOTAL** | **25** | **25** | **ALL within_range** |

## STRICT enum confirmation

- `serial_engine` — all 25 in canon: `case_of_the_week`×9, `life_stage_rhythm`×4, `location_anthology`×3, `mystery_box`×3, `companion_roster`×3, `power_escalation_ladder`×3.
- `genre_family` — all 25 in canon (see table above).
- `magical_register` — `magical_realism`×9, `none`×8, `supernatural_everyday`×4, `high_fantasy`×3, `occult_cosmic`×1.

## Platform fit — 55/45 webtoon/manga

- `both`: 14 (56%)
- `webtoon_vertical`: 11 (44%)
- `manga_traditional` (exclusive): 0
- **Effective webtoon-readable**: 25/25 (`both`+`webtoon_vertical`)
- **Effective manga_traditional-readable**: 14/25 (`both`)
- Approximate 55/45 platform fit (slight webtoon-lean for zh_TW Gen Z heavy mix).

## Persona distribution (target ~60% GZ, ~25% GA, ~12% Mill, ~3% GX)

| persona | count | % | bucket |
|---|---|---|---|
| Mill-careerist | 12 | 48% | Millennial |
| GZ-firstjob | 6 | 24% | Gen Z |
| Mill-burnout | 3 | 12% | Millennial |
| GZ-uni | 3 | 12% | Gen Z |
| GA-elementary | 1 | 4% | Gen Alpha |

**Bucket totals**:
- Gen Z: 9 (36%)
- Gen Alpha: 1 (4%)
- Millennial: 15 (60%)
- Gen X: 0

**Note**: Cluster B (Cognitive/Focus/Burnout) skews older than Cluster A — burnout-recovery, career-pivot, ADHD late-diagnosis, exec-function, mid-career re-invention motifs naturally cluster Mill-heavy. Gen Z still represented across all 5 brands; Gen Alpha cross-generational entry via the neurodivergent_neighbors series. Operator-approved register flex per Cluster B target.

## Register / engine distributions

- **magical_register**: `magical_realism`×9 (36%), `none`×8 (32%), `supernatural_everyday`×4 (16%), `high_fantasy`×3 (12%), `occult_cosmic`×1 (4%) — heavy realism-magic continuum, restrained tone, Taiwan low-magic register.
- **serial_engine**: `case_of_the_week`×9 (36%) leads (workplace/clinic/cafe procedural-healing), then `life_stage_rhythm`×4, balanced across other engines.

## Runway

- **Median volume_runway_target**: 200
- **Min / Max**: 160 / 240
- All 25 series have runway ≥ 160 (V1.2 floor satisfied).

## Taiwan-locale conformance

- **Zero mainland Simplified phrasings detected**: 視頻/軟件/智能手機/互聯網/地鐵/外賣/視像 = 0 hits.
- **TW-natural forms used**: 影片×2, 軟體×3, 捷運×7 + MRT, 外送×2.
- **Cultural anchors deployed**: 永和樂華夜市, 大稻埕迪化街, 萬華舊商店街, 新店溪河堤, 信義區辦公樓, 南港園區, 內湖科學園區, 新竹園區, 雙和醫院, 台北捷運淡水信義線, 7-11/全家便利商店, 文青咖啡店, 補習街, 政大/中正大學, 客家話, 靈骨塔, 玉山/陽明山, 黑長尾雉/山羌/橘貓, 機車, KPI/廣告 AE/PM, ADHD/neurodivergent identity.
- **comp_titles**: 用九柑仔店, 解憂雜貨店, 深夜食堂, 可不可以你也剛好喜歡我, 千年女優, 蟲師, 夏目友人帳, 葬送のフリーレン, 神之塔, 小森食光, 半澤直樹, 心靈鑰匙, 送行者, 千與千尋, 便利店人間, 我是貓, 金田一少年事件簿, 東京愛情故事, 東大特訓班, 麵包超人 — TW-bookstore-recognizable.

## Hard-rules conformance

- `audit_llm_callers` — N/A (data file only, no LLM code touched).
- 0 file deletions; only `artifacts/marketing/v1_2_themes_zh_TW_cluster_b.yaml` + this summary touched (2 files, within 4 file write_scope).
- No copyright issues — all comp_titles are reference-only string mentions; no excerpted content.
- Tier-1 Claude (operator-present authoring).
