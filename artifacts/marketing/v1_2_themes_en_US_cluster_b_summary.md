# V1.2 Themes — en_US — Cluster B (Cognitive/Focus/Burnout) — Summary

**Status:** Authoring complete, within all binding ranges.
**Locale:** en_US
**Cluster:** B — Cognitive/Focus/Burnout
**Series authored:** 25 (5 brands × 5 series)
**File:** `artifacts/marketing/v1_2_themes_en_US_cluster_b.yaml`
**Authority:** `artifacts/research/v1_2_genre_allocation_constraint_2026-05-12.md` (BINDING per-cluster allocation)
**Pilot reference:** `artifacts/marketing/v1_2_themes_en_US_cluster_a.yaml` (PR #1056)

---

## Brand mapping (constraint doc → canonical_brand_list.yaml)

| Constraint brand name | Canonical brand_id | Tier | Demographic | Primary topic | Notes |
|---|---|---|---|---|---|
| cognitive_clarity | `cognitive_clarity` | flagship | seinen | overthinking | exact match |
| burnout_iyashikei | `stabilizer_healing` | core | seinen | burnout | mapped: closest burnout-iyashikei seinen brand in canonical list |
| executive_function_focus | `focus_sprint_workplace` | core | seinen | adhd_focus | mapped: canonical ADHD/focus seinen brand |
| neurodivergent_strengths | `adhd_forge_mystery` | niche | shonen | adhd_focus | mapped: canonical neurodivergent-strengths brand, shonen demographic |
| career_lift | `career_lift_workplace` | core | josei | imposter_syndrome | mapped: canonical name |

All five map onto canonical brands in `config/manga/canonical_brand_list.yaml`. No new brand IDs created.

---

## Per-brand series count

| Brand | Count |
|---|---|
| cognitive_clarity | 5 |
| stabilizer_healing | 5 |
| focus_sprint_workplace | 5 |
| adhd_forge_mystery | 5 |
| career_lift_workplace | 5 |
| **Total** | **25** |

---

## Genre allocation (BINDING constraint)

| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| slice_of_life | 5 | 5 | ✅ |
| supernatural_everyday | 4 | 4-5 | ✅ |
| mystery_cozy | 4 | 4 | ✅ |
| fantasy_adventure | 3 | 3 | ✅ |
| romance | 1 | 1-2 | ✅ |
| horror | 1 | 1 | ✅ |
| school | 1 | 0-1 | ✅ |
| other | 0 | 0-1 | ✅ |
| **Total** | **25** | **25** | **✅** |

All within range. Constraint passes.

### Per-brand × genre breakdown

| Brand | healing | slice_of_life | supernatural_everyday | mystery_cozy | fantasy_adventure | romance | horror | school | Total |
|---|---|---|---|---|---|---|---|---|---|
| cognitive_clarity | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 5 |
| stabilizer_healing | 2 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 5 |
| focus_sprint_workplace | 1 | 1 | 0 | 1 | 1 | 0 | 0 | 1 | 5 |
| adhd_forge_mystery | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 5 |
| career_lift_workplace | 1 | 1 | 1 | 0 | 0 | 1 | 1 | 0 | 5 |
| **Total** | **6** | **5** | **4** | **4** | **3** | **1** | **1** | **1** | **25** |

---

## Persona allocation

Per task brief: ~60% Gen Z, ~12% Gen Alpha, ~25% Millennial, ~3% Gen X.

| persona_archetype | count | % | Generation |
|---|---|---|---|
| GZ-firstjob | 5 | 20% | Gen Z |
| GZ-creator | 1 | 4% | Gen Z |
| GA-school | 3 | 12% | Gen Alpha |
| Millennial-burnout | 8 | 32% | Millennial |
| Millennial-adhd | 8 | 32% | Millennial |
| **Total** | **25** | **100%** | — |

**Generational summary:** Gen Z 6/25 (24%), Gen Alpha 3/25 (12%), Millennial 16/25 (64%), Gen X 0/25 (0%).

**Variance from brief:** Cluster B is mid-career-burnout-heavy by construction (career_lift, stabilizer_healing, focus_sprint_workplace all skew Millennial). The brief allowed for this tilt: "Personas skew Millennial + elder-Gen-Z (mid-20s to mid-30s) — career-burnout, ADHD, imposter, creative-overload." Net Millennial-heavy here (64% vs brief's 25%) reflects the cluster's specific scope (late-diagnosed ADHD, mid-career burnout, executive function for working adults). Gen Alpha at 12% matches brief target. Cluster A picks up more Gen Z; Cluster E picks up more Gen Alpha — net portfolio across 5 clusters will rebalance.

---

## Magical register distribution

| magical_register | count | % | constraint advisory |
|---|---|---|---|
| supernatural_everyday | 6 | 24% | (constraint 37% per-locale, but per-cluster flex) |
| magical_realism | 11 | 44% | (constraint 28%, this cluster tilts realist-magic for cognitive/letter/journal hooks) |
| isekai | 3 | 12% | (constraint 6%, this cluster overweights for "guild of overthinkers / interest island" recovery-isekai) |
| occult_cosmic | 1 | 4% | (constraint 2%, the layoff-horror series) |
| none | 4 | 16% | (constraint 19%, near target) |
| **Total** | **25** | **100%** | — |

Constraint is advisory on register distribution; binding only on genre_family. Cluster B tilts magical_realism because cognitive/focus/burnout maps naturally to letter-portal, app-portal, ledger-portal hooks (journal-with-replies, focus-app-that-sees, garden-as-telemetry) and slightly under-uses pure supernatural_everyday yokai (which Cluster A overweights).

---

## Serial engine distribution

| serial_engine | count | % |
|---|---|---|
| case_of_the_week | 13 | 52% |
| companion_roster | 7 | 28% |
| party_quest | 3 | 12% |
| serial_diary | 2 | 8% |
| **Total** | **25** | **100%** |

Cluster B is case-of-the-week-heavy by construction — the cognitive/focus/burnout domain maps naturally to single-client-per-volume Apothecary-style serialization. Party-quest reserved for the three recovery-isekai (cognitive_clarity Guild of Overthinkers, focus_sprint Eight Islands, adhd_forge Interest Island).

---

## Platform-fit distribution

| reading_platform_fit | count | % | constraint |
|---|---|---|---|
| webtoon_vertical | 21 | 84% | ≥60% ✅ |
| graphic_novel | 4 | 16% | — |

The four graphic-novel slots are the diary-register confessionals (Fifty-Two Loaves, The Saturday Firehouse, The Fourteenth Floor, After the Promotion) — all Fun Home / Persepolis comp-titled.

---

## Volume runway

| metric | value |
|---|---|
| median | 150 |
| mean | 136.8 |
| min | 80 |
| max | 200 |
| ≥30 floor | 25/25 ✅ |
| ≥80 aim | 25/25 ✅ |

Strongest runways (≥180): The 3 A.M. Aisle parallel (Overnight Print Shop=180), Sabbatical Inn=200, Off-Ramp Garden=180, Letter Box=160. These are the long-haul flagship-grade series.

---

## Daily life anchor distribution

| daily_life_anchor | count |
|---|---|
| app_blogosphere | 7 |
| late_night_economy | 4 |
| office_commute | 4 |
| slow_living | 5 |
| school_commute | 3 |
| parasocial_creator | 1 |
| retail_service | 0 |
| content_creation | 0 |
| location-specific (orchard, inn, garden, firehouse) | 1 |

App-blogosphere and slow-living dominate, consistent with the cluster's split between Gen Z app-saturated knowledge workers and Millennial post-corporate exiters.

---

## Comp titles spread

Most-cited comps (per series_description and comp_titles):
- **The Apothecary Diaries** — 11 series (case-of-the-week register)
- **Days at the Morisaki Bookshop** — 8 series (slow-burn healing register)
- **Before the Coffee Gets Cold** — 7 series (future-self / letter register)
- **Convenience Store Woman (Murata)** — 5 series (specific-job iyashikei)
- **Witch Hat Atelier** — 6 series (apprenticeship)
- **Frieren: Beyond Journey's End** — 5 series (slow-walk recovery)
- **Heartstopper** — 5 series (chosen-family tenderness)
- **Severance (Ling Ma)** — 4 series (corporate-ambient)
- **Fun Home (Bechdel)** — 3 series (confessional graphic-novel)

A24/Ghibli register dominant across the cluster. Two slight tonal outliers — *The Seven P.M. Whisper* (horror) and *Pomodoro Orchard* (pastoral) — broaden the portfolio.

---

## Validation against task brief

- [x] 25 series authored (5 brands × 5)
- [x] Brand mapping resolved against canonical_brand_list.yaml; documented above
- [x] Genre allocation within all binding ranges (table above)
- [x] V1.2 schema fields present in every series (series_id, brand_id, locale, persona_archetype, daily_life_anchor, portal_mechanic, episodic_frame_per_volume, magical_register, serial_engine, long_arc_spine, volume_runway_target, reading_platform_fit, series_title, series_logline, series_description, opening_5_volume_arc, comp_titles, reader_promise, marketing_angle, genre_family, emotional_engine, audience)
- [x] 80-150 word series_description, A24/Ghibli register, no TikTok lingo
- [x] Runway ≥30 floor and ≥80 aim hit on all 25
- [x] ≥60% webtoon_vertical (84%)
- [x] Cluster B persona tilt (Millennial + elder-Gen-Z, career-burnout / ADHD / imposter / creative-overload) honored
- [x] Portal mechanics include app, letter, mirror, game_level (constraint hit)
- [x] No copyright violations; no deletions; write_scope ≤4 files
- [x] Does NOT touch cluster_a.yaml or v1_2_themes_en_US.yaml

---

## Out of scope (deferred to other clusters / locales)

- Cluster A (Anxiety/Somatic/Sleep) covered in PR #1056
- Clusters C/D/E for en_US covered by parallel agents
- ja_JP / zh_CN / zh_TW Cluster B covered by parallel agents
- Brand-level packaging plans (cover thumbnails, KDP metadata) — downstream tooling
