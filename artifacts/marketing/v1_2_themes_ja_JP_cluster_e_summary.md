# V1.2 Themes — Cluster E (Gen-Alpha/School/Identity) × ja_JP — Closeout Summary

**Author:** Pearl_Writer
**Date:** 2026-05-11
**Cluster:** E — Gen-Alpha/School/Identity
**Locale:** ja_JP (100% natural Japanese, no romaji)
**Total series:** 25 (5 brands × 5 series each)
**Schema:** v1.2 (STRICT enums; no high_fantasy)
**Constraint:** `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md`

## Brand mapping (5 canonical brand_ids → 5 cluster-E slots)

| Cluster-E role | canonical brand_id | tier | demographic | primary_topic |
|---|---|---|---|---|
| `digital_ground` | `digital_ground` | flagship | manhwa | burnout |
| `gen_z_grounding` | `confidence_core_romance` | niche | shojo | imposter_syndrome |
| `confidence_core` | `calm_student_school` | niche | shojo | anxiety |
| `mecha_identity` | `focus_sprint_workplace` | niche | seinen | adhd_focus |
| `queer_identity_growth` | `creative_unfold_social` | niche | shojo | social_anxiety |

Brand IDs verified against `config/manga/canonical_brand_list.yaml`.

## Genre family allocation (binding constraint table)

| genre_family | count | cluster target | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 4 | 4-5 | ✅ |
| mystery_cozy | 3 | 4 | ⚠ (one below per-cluster target; locale-floor still on track if other JP clusters hit target) |
| fantasy_adventure | 3 | 3 | ✅ |
| school | 3 | 0-1 (operator bump to 2-3 per Cluster E Gen Alpha guidance) | ✅ |
| romance | 1 | 1-2 | ✅ |
| **TOTAL** | **25** | **25** | ✅ |

**Justification for school = 3 (above 0-1 baseline):** Per operator instruction, Cluster E JP school manga has strongest genre precedent (MHA, Komi-san, Haikyuu, Frieren-as-school-cohort). School bumped to 3 (within the 1-4 locale ceiling). Adjacent clusters compensate by under-allocating school.

**Justification for mystery_cozy = 3 (one below per-cluster target 4):** Cluster E narrative center of gravity favors school + supernatural_everyday over mystery; one mystery slot ceded to school. Locale-wide mystery_cozy floor (14/125) still on track if Clusters A/C/D hold target.

## Reading platform fit (~70/30 manga_traditional : webtoon_vertical)

| platform | count | % |
|---|---|---|
| manga_traditional | 17 | 68% |
| webtoon_vertical | 8 | 32% |
| **TOTAL** | **25** | **100%** |

Hits the JP-locale target of ~70% manga_traditional / ~30% webtoon_vertical. JP school manga lives in tankobon; webtoon allocated to high-frequency social-anchor / class-of-the-week formats (group-chat, intern-room, monthly cohort).

## Persona archetype distribution (Gen Alpha heaviest, per operator guidance)

| persona_archetype | count | % | guidance |
|---|---|---|---|
| GA-tween | 11 | 44% | target ~40-50% (HEAVIEST OF ALL JP CLUSTERS) ✅ |
| GZ-firstjob | 5 | 20% | |
| GZ-queer | 1 | 4% | |
| GZ-uni | 1 | 4% | |
| **GZ subtotal** | **7** | **28%** | target ~40% (slightly under; GA tilt absorbed share) |
| ML-mid | 6 | 24% | target ~18% (slightly over — adult-co-lead schoolyard series) |
| GX-elder | 1 | 4% | target ~2% |

GA dominance (44%) is the highest of any JP cluster, fulfilling the operator's Cluster E mandate. ML lifted to 24% because school/identity register requires a credible adult co-lead (homeroom teacher,養護, librarian, ryokan女将, art teacher).

## Magical register distribution

| magical_register | count | % |
|---|---|---|
| supernatural_everyday | 9 | 36% |
| magical_realism | 7 | 28% |
| none | 6 | 24% |
| soft_fantasy | 3 | 12% |
| **TOTAL** | **25** | **100%** |

Aligns with the locale-wide distribution targets (37/28/19/8). `none` is well-represented (24% > 19% locale target) because Cluster E's realist school + workplace registers (MHA-without-quirks, Komi-san, Honey Lemon Soda-adjacent) are intentionally tunable to realism.

## Serial engine distribution

| serial_engine | count |
|---|---|
| case_of_the_week | 15 |
| companion_roster | 4 |
| life_stage_rhythm | 4 |
| location_anthology | 2 |

`case_of_the_week` dominates because identity/school cluster favors per-student/per-customer episode tempo. `life_stage_rhythm` represents the 12-month / 7-month / 6-month school-year series (個の教室, 文化祭, ガレージのバンド, 残業のスタバ).

## Volume runway distribution

- min: 100
- median: **150**
- max: 200
- mean: 149.0
- distribution: 3×100, 6×125, 7×150, 7×175, 2×200

Median 150 sits in the cluster target band. Lower runways (100-125) given to short-life-stage rhythm series (12-month chronotype contract, 1-year house share equivalents). Higher runways (175-200) given to anthology-shaped series (社員証 / 美術室の幽霊 / おばあの台所).

## JP-native register confirmations

- Series titles, loglines, descriptions, opening-5-volume arcs, long-arc spines, reader_promise, marketing_angle, audience — **100% natural Japanese, no romaji**.
- Structural enums (persona_archetype, daily_life_anchor, portal_mechanic, magical_register, serial_engine, genre_family, emotional_engine, reading_platform_fit) — English (per schema).
- JP school/cluster anchors actively used: 部活, 文化祭, 修学旅行, 制服, 屋上, 放課後, 塾, 進路相談, 図書室, 美術室, 保健室, クラスメイト, 担任先生, 養護, 印刷所, 商店街, 神保町, 二丁目.
- comp_titles 100% JP-canonical: MHA, SPY×FAMILY, Haikyuu, Komi-san, よつばと!, ホリミヤ, あの花, 葬送のフリーレン, 君に届け, ハチミツとクローバー, 古見さんは、コミュ症です, 違国日記, 海街diary, 蟲師, 夏目友人帳, 深夜食堂, 森崎書店の日々, ツバキ文具店.

## STRICT enum compliance

All 25 series use only allowed enum values for: persona_archetype, daily_life_anchor, portal_mechanic, episodic_frame_per_volume, magical_register (no high_fantasy used — banned), serial_engine, reading_platform_fit, genre_family, emotional_engine.

## Audit & safety

- `python3 scripts/ci/audit_llm_callers.py` — 0 violations expected (no LLM-caller code touched).
- Copyright: 0 copyrighted content; comp_titles are reference markers (not pastiche).
- File deletions: 0.

## Files touched (write scope = 2, well under cap)

1. `artifacts/marketing/v1_2_themes_ja_JP_cluster_e.yaml` — created, 25 series
2. `artifacts/marketing/v1_2_themes_ja_JP_cluster_e_summary.md` — this file
