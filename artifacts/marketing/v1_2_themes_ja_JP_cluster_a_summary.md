# V1.2 Themes — Cluster A (Anxiety/Somatic/Sleep) × ja_JP — Summary

**Status:** Authoring complete (25/25 series)
**Locale:** ja_JP
**Cluster:** A — Anxiety/Somatic/Sleep
**File:** `artifacts/marketing/v1_2_themes_ja_JP_cluster_a.yaml`
**Branch:** `agent/v1-2-cluster-a-ja-jp-retry-20260512`
**Base:** `origin/main` @ `0ab722e26`
**Pilot reference:** PR #1056 (en_US Cluster A — same structural template)
**Authoring approach:** Native ja_JP composition (NOT translation of en_US)

## Brands authored (5 × 5 = 25 series)

| # | brand_id | tier | demographic | primary_topic | series |
|---|---|---|---|---|---|
| 1 | stillness_press | flagship | josei | anxiety | 5 |
| 2 | sleep_restoration_iyashikei | core | josei | sleep | 5 |
| 3 | somatic_wisdom_shojo | core | josei | somatic_healing | 5 |
| 4 | body_memory_shojo | core | josei | somatic_healing | 5 |
| 5 | stabilizer_healing | core | seinen | burnout/panic-first-aid | 5 |

Brand-id mapping from constraint doc to `config/manga/canonical_brand_list.yaml`:
- `body_memory_seinen` -> `body_memory_shojo` (canonical demographic = shojo/josei)
- `panic_first_aid_stabilizer` -> `stabilizer_healing` (canonical name)

## Genre allocation validation (binding floors)

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 5 | 4–5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 3 | 3 | ✅ |
| romance | 1 | 1–2 | ✅ |
| horror | 1 | 1 | ✅ |
| school | 0 | 0–1 | ✅ |
| other | 0 | 0–1 | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

All rows within range. Constraint satisfied.

## Reading-platform split (JP-locale inversion applied)

| platform | count | share | en_US-pilot share |
|---|---|---|---|
| `manga_traditional` | 19 | 76% | 0% |
| `webtoon_vertical` | 6 | 24% | 100% |

Target was ~70% manga_traditional / ~30% webtoon_vertical. Delivered 76/24 — within the spirit of the inversion (JP buyers older-skewed, page-format preference). Webtoon allocation concentrated on app-blogosphere and content-creation anchors where vertical format makes sense.

## Persona allocation

| persona_archetype | count | share |
|---|---|---|
| GZ-firstjob | 11 | 44% |
| GZ-uni | 5 | 20% |
| GZ-queer | 2 | 8% |
| Mill-careerist | 6 | 24% |
| GA-tween | 1 | 4% |
| **TOTAL** | 25 | 100% |

Gen Z combined: 72% (target ~50% + uni-extension). Millennial: 24% (target ~20%, slightly heavier as guided — JP works Mill-skewing more than en_US). Gen Alpha: 4% (target ~25% — under-allocated in this cluster because Anxiety/Somatic/Sleep tilts adult; Gen Alpha mass will land in Cluster E per the constraint doc allocation logic). Gen X: 0 (target ~5%, deferred).

**Persona-mix note for operator:** Cluster A's subject matter (panic, somatic trauma, sleep clinic,遺品整理) is naturally adult-skewed. The single Gen Alpha series (`furusato_no_engawa` — grandmother's `engawa` in summer) is the natural pediatric entry. Other locales' Cluster A may also under-deliver Gen Alpha; recommend constraint doc note that Gen-Alpha mass concentrates in Clusters D/E.

## Volume-runway distribution

- Median: 150
- Min: 100 — Max: 200
- Distribution: 6 series at 100, 11 series at 150, 8 series at 200
- Higher runways (200) concentrated on case-of-the-week serial_engine series (convenience-store, night-kitchen, panic-ER, ghost-tea-house) where episodic format supports long runs.

## Japanese-native register confirmation

All required fields written in natural Japanese (ja-native authoring, NOT translation):
- ✅ series_title — all 25
- ✅ series_logline — all 25
- ✅ series_description — all 25
- ✅ opening_5_volume_arc.vol_1..5 — 125 entries
- ✅ long_arc_spine — all 25
- ✅ reader_promise — all 25
- ✅ marketing_angle — all 25
- ✅ audience — all 25
- No romaji content. No mainland Chinese phrasing.
- Structural enum fields (persona_archetype, daily_life_anchor, portal_mechanic, magical_register, serial_engine, genre_family, etc.) remain English per spec ("Structural enum fields stay English").

### Register/tone anchors applied per series

- 『葬送のフリーレン』emotional restraint — applied to `tsuki_no_eki_no_nemuri_iin`, `yume_no_naka_no_byouin`
- 『薬屋のひとりごと』case-of-the-week competence — applied to `panic_no_kyukyu_shitsu`, `nichiyou_no_kogusuriya`, `mushi_to_karada`
- 『よつばと!』quiet wonder — applied to `furusato_no_engawa` (Gen Alpha entry)
- 『蟲師』supernatural-everyday subtle — applied to `shinya_podcast_no_chiisai_kami`, `hito_no_yume_wo_miru`, `mushi_to_karada`
- Real comp_titles drawn from the JP shelf: 葬送のフリーレン, 薬屋のひとりごと, ダンダダン (sparingly), 蟲師, よつばと!, ホリミヤ, 深夜食堂, あん, 違国日記, テルマエ・ロマエ, ツバキ文具店, BLACK JACK, コウノドリ, 千と千尋の神隠し, ジャンルmismatch避け.

### Cultural anchors used (per spec)

- 銭湯 (sento) — `sento_no_nukumori` (somatic-bathhouse healing)
- 神社 (jinja) — `yakei_no_jinja` (night-shrine work-study)
- 茶屋 (cha-ya) — `hatsuya_no_chairo` (panic-attack tea house)
- 商店街 (shotengai) — `shotengai_no_seitai_in`, `panic_no_kyukyu_shitsu`
- 喫茶店 (kissaten) — `kissaten_no_ato_sanjippun` (post-attack 30-min cafe)
- 駅 (eki) — `hitotsu_saki_no_eki` (one-stop-further station)
- 田舎 (inaka) + 縁側 (engawa) — `furusato_no_engawa` (Gen Alpha grandmother's house)
- 金継ぎ (kintsugi) — `hone_no_naka_no_kioku` (added value-add)
- 路地 (roji) — incidental in stillness_press setting

## Out-of-scope guardrails confirmed

- File write scope: 2 files (the YAML data file + this summary MD). Within ≤4 limit. ✅
- No copyrighted content (comp_titles are reference comparisons only, not derivative use). ✅
- 0 deletions to existing files. ✅
- No en_US Cluster A files touched. ✅
- All content authored fresh; no translation. ✅

## Next actions

1. Open PR titled `themes(ja_JP-cluster-a): V1.2 series — Anxiety/Somatic/Sleep × ja_JP (25 series)`
2. Run `python3 scripts/ci/audit_llm_callers.py` for LLM-policy compliance (no code touched, expected 0 violations)
3. Hand off to ja_JP locale lead for native-speaker register review (Pearl_Brand reviewer)
4. Once approved, downstream consumers: `config/manga/manga_brand_series_plan.yaml` for ja_JP catalog integration
