# V1.2 themes — Cluster C (Grief/Trauma/Healing) × ja_JP — Summary

**Deliverable:** `artifacts/marketing/v1_2_themes_ja_JP_cluster_c.yaml`
**Branch:** `agent/v1-2-cluster-c-ja-jp-20260512`
**Base:** `origin/main` @ `d166ac96becd6d5f306cf07044a10f31d358c398`

## Scope

25 series = 5 brands × 5 series in natural Japanese (ja_JP, ja-native authoring).
Cluster C: Grief / Trauma / Healing. Structural enums in English.

## Brand mapping (from PR #1061 Cluster C en_US)

| ja_JP brand (canonical_brand_list.yaml) | en_US brand |
| --- | --- |
| spiritual_ground_supernatural | grief_companion_iyashikei |
| trauma_path_healing | trauma_recovery_shojo |
| healing_ground_healing | healing_ground_healing (exact) |
| warrior_calm_cultivation | ash_and_steel_warrior_calm |
| stoic_edge_battle | surrender_form_warrior_calm |

## Genre allocation — within binding floors

| genre_family | count | binding floor |
| --- | ---: | --- |
| healing | 6 | 6 (floor met) |
| slice_of_life | 5 | 5 (floor met) |
| supernatural_everyday | 5 | 4-5 (within range) |
| mystery_cozy | 4 | 4 (floor met) |
| fantasy_adventure | 3 | 3 (floor met) |
| romance | 1 | 1-2 (within range) |
| horror | 1 | 1 (floor met) |
| **TOTAL** | **25** | **25** |

## Distributions

**reading_platform_fit:** 18 manga_traditional (72%) / 7 webtoon_vertical (28%)
(Within target ~70/30; bereavement audience skews older, more page-based.)

**magical_register:** supernatural_everyday 11 | magical_realism 6 | soft_fantasy 4 | none 3 | occult_cosmic 1
(All STRICT enum — zero high_fantasy.)

**serial_engine:** case_of_the_week 12 | location_anthology 4 | companion_roster 3 | mystery_box 2 | life_stage_rhythm 2 | power_escalation_ladder 2
(All STRICT enum.)

**persona_archetype:** ML-bereaved 14 (56%) | GZ-firstjob 7 (28%) | GZ-uni 2 (8%) | GZ-queer 1 (4%) | GX-bereaved 1 (4%)
(Mill heavier for bereavement-cluster fit. ~36% Gen Z including queer; Gen Alpha intentionally absent — limited bereavement fit per brief.)

**volume_runway_target:** median 150, min 120, max 250

## JP-native register applied

- Tone: 葬送のフリーレン restraint + 蟲師 subtle supernatural + 死神の精度 / 君の膵臓をたべたい grief register
- Cultural anchors used: 仏壇, 法事, 墓参り, 形見, 遺品整理, 茶屋, 縁側, 線香, 四十九日, 縁側, 桐の箱, 三十三回忌, 居合, 弓道, 海女
- comp_titles drawn from real JP titles: 葬送のフリーレン, 蟲師, 死神の精度, 銀河鉄道の夜, リトル・フォレスト, ゴールデンカムイ, 海街diary, 違国日記, 深夜食堂, コーヒーが冷めないうちに, ツバキ文具店, ばらかもん, 鬼滅の刃, るろうに剣心, アンナチュラル, 風が強く吹いている
- 100% natural Japanese in: series_title, series_logline, series_description, opening_5_volume_arc, long_arc_spine, reader_promise, marketing_angle, audience
- Zero romaji in content fields; series_id uses Hepburn-style romaji per existing schema convention

## Authoring notes

- Loss is engine, not plot — restraint over preachy
- Each series gives喪 a competent specialist register (店主, 司書, 整理士, 道場継承者, 葬儀ドゥーラ, 走り手)
- Cluster C JP-specific anchors woven into vol arcs (四十九日 as a pivot point in 4 series; 仏壇 in 3; 墓参り in 2; 形見/遺品整理 in 11)
- Webtoon flipped to younger personas (GZ-uni, GZ-firstjob, GZ-queer) where format matches reader habit

## Compliance

- 0 deletions
- 2 files added (yaml + this summary md)
- audit_llm_callers expected 0 (no LLM code touched)
- No copyrighted content beyond comp_titles cited for genre positioning
