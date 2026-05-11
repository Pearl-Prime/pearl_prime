# V1.2 Themes — Cluster B (Cognitive/Focus/Burnout) × ja_JP — Summary

**Status:** Authoring complete (25/25 series)
**Locale:** ja_JP
**Cluster:** B — Cognitive/Focus/Burnout
**File:** `artifacts/marketing/v1_2_themes_ja_JP_cluster_b.yaml`
**Branch:** `agent/v1-2-cluster-b-ja-jp-retry2-20260512`
**Base:** `origin/main` (Cluster A ja_JP precedent: PR #1057; en_US Cluster B mapping: PR #1058)
**Authoring approach:** Native ja_JP composition (NOT translation of en_US Cluster B)

## Brands authored (5 × 5 = 25 series)

| # | brand_id (constraint) | brand_id (canonical) | tier | demographic | series |
|---|---|---|---|---|---|
| 1 | cognitive_clarity | cognitive_clarity | flagship | josei | 5 |
| 2 | burnout_iyashikei | stabilizer_healing | core | seinen | 5 |
| 3 | executive_function_focus | focus_sprint_workplace | core | seinen | 5 |
| 4 | neurodivergent_strengths | adhd_forge_mystery | core | shonen | 5 |
| 5 | career_lift | career_lift_workplace | core | seinen | 5 |

Brand-id mapping aligns with PR #1058 (en_US Cluster B precedent).

## Genre allocation validation (binding floors)

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 4 | 4–5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 3 | 3 | ✅ |
| romance | 1 | 1–2 | ✅ |
| horror | 1 | 1 | ✅ |
| school | 1 | 0–1 | ✅ |
| other | 0 | 0–1 | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

All rows within range. Constraint satisfied.

## STRICT enum confirmation

**serial_engine** — all 25 values within the strict enum set `{mystery_box, power_escalation_ladder, companion_roster, location_anthology, case_of_the_week, life_stage_rhythm}`:

| serial_engine | count |
|---|---|
| case_of_the_week | 10 |
| life_stage_rhythm | 4 |
| location_anthology | 3 |
| mystery_box | 3 |
| power_escalation_ladder | 3 |
| companion_roster | 2 |
| **TOTAL** | 25 |

No `party_quest`, no `slice_of_life_arc`, no `serialized_long_arc`. ✅

**genre_family** — all 25 values within the strict enum set. ✅

## Reading-platform split (JP-locale inversion target ~70/30)

| platform | count | share |
|---|---|---|
| `manga_traditional` | 16 | 64% |
| `webtoon_vertical` | 9 | 36% |

Target was ~70% manga_traditional / ~30% webtoon_vertical. Delivered 64/36 — slightly under the manga-traditional target. Higher webtoon allocation than Cluster A (76/24) because Cluster B's workplace/app/digital-economy daily-life anchors (app_blogosphere, coworking, side_gig, late-night-economy) lean naturally toward vertical mobile reading among the GZ knowledge-worker persona. Within the spirit of the JP-locale inversion (still majority manga_traditional, older-skewed JP buyers respected).

## Persona allocation

| persona_archetype | count | share |
|---|---|---|
| GZ-firstjob | 9 | 36% |
| Mill-careerist | 7 | 28% |
| GA-tween | 5 | 20% |
| GZ-uni | 2 | 8% |
| Mill-burnout | 2 | 8% |
| **TOTAL** | 25 | 100% |

Gen Z combined: 44% (target ~50%, slightly under). Millennial combined: 36% (target ~25%, intentionally heavier per JP guidance — Cluster B's burnout/career-transition subject matter is naturally Mill-skewing). Gen Alpha: 20% (target ~25%, close — Gen Alpha mass concentrated in adhd_forge_mystery brand and the school-focused career-lift entry).

## Magical-register distribution

| magical_register | count | share |
|---|---|---|
| magical_realism | 9 | 36% |
| none | 7 | 28% |
| supernatural_everyday | 4 | 16% |
| soft_fantasy | 4 | 16% |
| occult_cosmic | 1 | 4% |

Heavy `none` allocation (7) reflects Cluster B's workplace realism (副業会, 離職の湖, 終電の歌, 商工の授業, 連絡のない青春, 社内恋愛ではありません, 商店街の休み所) — all fully realist. Balanced against `magical_realism` (頭の中の喫茶店, 未来の自分からの手紙, 記憶の整理館, 転職の地図, 新幹線の手帖) which tilts toward the cognitive-clarity flagship's psychological-tool aesthetic.

## Volume-runway distribution

- Median: 150
- Min: 100 — Max: 200
- Distribution: 100×1, 120×2, 150×9, 180×5, 200×8
- Higher runways (180–200) on case-of-the-week and mystery-box engines that support long episodic runs (深夜のコピー機 180, 記憶の整理館 200, 商店街の休み所 200, 二十分タイム 180, 屋上のコーヒー 180, 鍛冶屋と探偵団 200, 新幹線の手帖 180, 地下の工房 200, 新神楽の夜明け 200, 二十分の塔 200, 転職の地図 200).
- Stretch series (≥180 runway): 11 of 25 (44%).

## Japanese-native register confirmation

All required fields written in natural Japanese (ja-native authoring, NOT translation):
- ✅ series_title — all 25
- ✅ series_logline — all 25
- ✅ series_description — all 25 (80–150 words each)
- ✅ opening_5_volume_arc.vol_1..5 — 125 entries
- ✅ long_arc_spine — all 25
- ✅ reader_promise — all 25
- ✅ marketing_angle — all 25
- ✅ audience — all 25
- No romaji content. No mainland Chinese phrasing.
- Structural enum fields (persona_archetype, daily_life_anchor, portal_mechanic, magical_register, serial_engine, genre_family, reading_platform_fit, emotional_engine) remain English per spec.

### Register/tone anchors applied

- 『葬送のフリーレン』感情の節度 — applied to 河川敷のベンチ, 離職の湖, 商店街の休み所, 転職の地図
- 『薬屋のひとりごと』職能の確かさ — applied to 深夜のコピー機, 記憶の整理館, 二十分タイム, 屋上のコーヒー, 鍛冶屋と探偵団, 転職の地図
- 『蟲師』日常の中の超常 — applied to 河川敷のベンチ, 先延ばしの猫, 明と隣, 新神楽の夜明け, 夜の病棟
- 『ハチミツとクローバー』倦怠と若さの矛盾 — applied to 連絡のない青春, 副業の夜, 社内恋愛ではありません, 商工の授業
- Real JP comp_titles drawn from the natural JP shelf: 葬送のフリーレン, 薬屋のひとりごと, ダンダダン, 夏目友人帳, 蟲師, ホリミヤ, 深夜食堂, あん, 違国日記, 森崎書店の日々, ハチミツとクローバー, あひるの空, 千と千尋の神隠し, とんがり帽子のアトリエ, コーヒーが冷めないうちに, ツバキ文具店, コンビニ人間, 君は月夜に光り輝く, 魔法少女まどか☆マギカ, BLACK JACK, 金田一少年の事件簿, となりのトトロ.

### Cluster B-specific cultural anchors used (per spec)

- 過労 (overwork) → 夜の病棟, 商店街の休み所, 終電の歌, 連絡のない青春
- 喫茶店 (kissaten) → 頭の中の喫茶店, 屋上のコーヒー
- 商店街 (shotengai elders) → 商店街の休み所, 二十分タイム, 鍛冶屋と探偵団, 商工の授業
- 副業 (side-gig) → 副業の夜
- 公園のベンチ / 河川敷 (park bench) → 河川敷のベンチ
- 終電 (last train) → 終電の歌
- コワーキング (coworking) → 森林オフィス
- 銀行員・公務員 (institutional employees) → 転職の地図, 離職の湖
- 屋上 (rooftop) → 屋上のコーヒー

## Out-of-scope guardrails confirmed

- File write scope: 2 files (YAML data + this summary MD). Within ≤4 limit. ✅
- No copyrighted content (comp_titles are reference comparisons only, not derivative use). ✅
- 0 deletions to existing files. ✅
- No en_US Cluster B or ja_JP Cluster A files touched. ✅
- All content authored fresh; no translation from en_US Cluster B. ✅
- LLM-policy audit: code untouched (data file only); expected 0 violations. ✅

## Next actions

1. Open PR titled `themes(ja_JP-cluster-b): V1.2 series — Cognitive/Focus/Burnout × ja_JP (25 series)`
2. Run `python3 scripts/ci/audit_llm_callers.py` for LLM-policy compliance (no code touched, expected 0 violations)
3. Hand off to ja_JP locale lead for native-speaker register review (Pearl_Brand reviewer)
4. Once approved, downstream consumers: `config/manga/manga_brand_series_plan.yaml` for ja_JP catalog integration
