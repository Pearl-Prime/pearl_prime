# V1.2 Genre Allocation Constraint — per-locale targets

**Status:** AUTHORING-CONSTRAINT (binding on Pearl_Writer V1.2 subagents)
**Author:** Pearl_Architect (operator-ratified)
**Date:** 2026-05-12
**Anchors:**
- `artifacts/research/popular_genre_ranking_2026-05-02.md` (genre rankings + Phoenix portfolio mass)
- `artifacts/research/manga_bestseller_magical_serial_framework_2026-05-12.md` (PR #1051 — magical+serial framework)
- `artifacts/research/manga_genz_genalpha_portal_framework_2026-05-13.md` (PR #1053 — Gen Z/Alpha portal-anchor framework)

## Why this constraint exists

The V1.2 themes framework adds `magical_register` and `serial_engine` fields per series. These are ORTHOGONAL to `genre_family` (e.g. Mushishi = `healing` + `supernatural_everyday`; Solo Leveling = `fantasy_adventure` + `isekai`).

If Pearl_Writer subagents author without an explicit `genre_family` distribution target, they may drift heavily toward `supernatural_everyday` or `fantasy_adventure` (because the magical-register prompt pulls them there) and inadvertently sink the **healing/iyashikei anchor — Phoenix's portfolio #1, 3.4× the next genre, intentionally defensible bet for the teacher-brand audience** per the marketing research.

This document fixes that drift risk by binding the per-locale 125-series allocation to a target distribution.

## Binding per-locale `genre_family` allocation (per 125 series)

| genre_family | Target count | Floor | Ceiling | Rationale |
|---|---|---|---|---|
| `healing` (incl. iyashikei) | **30** | 26 | 34 | **Phoenix #1 portfolio anchor; teacher-brand audience expects this; do NOT sink** |
| `slice_of_life` | **24** | 20 | 28 | High crossover with healing; ANN data: slice-of-life isekai 55% > standard iyashikei |
| `supernatural_everyday` | **22** | 18 | 28 | Mushishi / Natsume / Apothecary register — natural fit for magical-twist + healing therapeutic stake |
| `mystery_cozy` | **18** | 14 | 22 | Apothecary surge 2023→2024 (Oricon #4 2024); broad shallow allocation; blends with healing |
| `fantasy_adventure` (incl isekai) | **14** | 10 | 18 | UNDER-allocated in V1.1 (research finding); empirically global #2; isekai = "most read 2025" |
| `romance` | **8** | 6 | 12 | Webtoon dominance; honey-lemon-soda demographic; under-allocated in V1.1 |
| `horror` / `dark_fantasy` / `occult_cosmic` | **5** | 3 | 8 | Dandadan / JJK / Chainsaw Man cohort; underweighted in V1.1 |
| `school` | **2** | 1 | 4 | Gen Alpha bridge; ensemble-school engine (MHA-style) |
| `sport` / `comedy` / `other` | **2** | 0 | 4 | Scatter; reserves |
| **TOTAL** | **125** | — | — | — |

**Soft rules:**
- Floors are HARD: a locale with `healing < 26` fails the constraint
- Ceilings are SOFT but require justification in the summary MD (e.g. "ja_JP lifted mystery_cozy to 24 because Apothecary's strongest market is JP")
- Per-locale flex: ja_JP may tilt iyashikei (healing 32-34), zh_CN may tilt fantasy_adventure / mystery (cultural manhua weight), zh_TW balances both, en_US holds the canonical distribution

## Magical-register × genre_family orthogonality matrix (advisory, not binding)

Use to validate your authoring — these are FINE combinations:

| magical_register \ genre_family | healing | slice_of_life | supernatural_everyday | mystery_cozy | fantasy_adventure | romance | horror | school |
|---|---|---|---|---|---|---|---|---|
| `supernatural_everyday` | ✅ Mushishi | ✅ Natsume | ✅ canonical | ✅ Apothecary | ⚠️ blends | ✅ | ✅ | ✅ |
| `magical_realism` | ✅ Aria | ✅ canonical | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ✅ |
| `soft_fantasy` | ✅ Frieren-healing | ✅ | ⚠️ | ✅ Witch Hat | ✅ | ✅ | ⚠️ | ✅ |
| `isekai` | ⚠️ (recovery-isekai works) | ✅ slice-of-life isekai | ⚠️ | ⚠️ | ✅ canonical | ✅ Mushoku | ⚠️ | ⚠️ |
| `occult_cosmic` | ⚠️ | ⚠️ | ✅ | ✅ Mononoke | ✅ | ⚠️ | ✅ canonical | ⚠️ |
| `none` | ✅ Honey Lemon Soda | ✅ | (mismatch) | ✅ | ⚠️ rare | ✅ | ⚠️ | ✅ |

**Distribution rule for `magical_register`** (independent of genre_family):
- `supernatural_everyday`: ~46 of 125 (37%) — operator's "Natsume-of-anxiety" intuition; dominant register
- `magical_realism`: ~35 (28%)
- `soft_fantasy`: ~10 (8%)
- `isekai`: ~7 (6%)
- `occult_cosmic`: ~3 (2%)
- `none`: ~24 (19%) — yes, ~1 in 5 series can be fully realist for portfolio balance (Honey Lemon Soda / shojo-realist register)

## Brand-cluster assignment (5 clusters × 5 brands = 25 brands = 125 series at 5 series/brand)

Cluster the 25 V1.1 brands into 5 groups for the 20-subagent fan-out (5 clusters × 4 locales = 20 subagents, each authoring 25 series):

- **Cluster A — Anxiety/Somatic/Sleep (5 brands)**: stillness_press, sleep_restoration_iyashikei, somatic_wisdom_shojo, body_memory_seinen, panic_first_aid_stabilizer
- **Cluster B — Cognitive/Focus/Burnout (5 brands)**: cognitive_clarity, burnout_iyashikei, executive_function_focus, neurodivergent_strengths, career_lift
- **Cluster C — Grief/Trauma/Healing (5 brands)**: grief_companion_iyashikei, trauma_recovery_shojo, healing_ground, ash_and_steel_warrior_calm, surrender_form_warrior_calm
- **Cluster D — Relational/Connection/Family (5 brands)**: relational_calm_iyashikei, inner_security, bright_presence, found_family_shojo, communal_warmth
- **Cluster E — Gen-Alpha/School/Identity (5 brands)**: digital_ground, gen_z_grounding, confidence_core, mecha_identity, queer_identity_growth

(If actual brand IDs differ from above, the cluster owner must map their cluster's 5 brand_ids from `config/manga/canonical_brand_list.yaml` + `artifacts/qa/worldwide_catalog_37_brand_allocation_plan_2026-05-11.tsv` and document the mapping in the cluster summary MD.)

## Per-cluster genre_family allocation target (25 series each)

Apply the per-125-target divided by 5 (with rounding for floor compliance):

| genre_family | per cluster (25 series) |
|---|---|
| healing | 6 |
| slice_of_life | 5 |
| supernatural_everyday | 4-5 |
| mystery_cozy | 4 |
| fantasy_adventure | 3 |
| romance | 1-2 |
| horror/dark_fantasy/occult | 1 |
| school | 0-1 |
| other/sport/comedy | 0-1 |
| **TOTAL** | **25** |

(Sum over 5 clusters → 125, hits the per-locale target above.)

## Validation gate (for cluster CLOSEOUT_RECEIPTs)

Every cluster summary MD must include a table:
```
| genre_family | count | target | within_range |
|---|---|---|---|
| healing | 6 | 6 | ✅ |
| ... | ... | ... | ... |
```

If `within_range` is ❌ for any row, the cluster fails the constraint and must be re-authored.

## Out of scope

- This document is advisory on `magical_register` distribution but binding on `genre_family` distribution.
- Per-brand wellness topic stays governed by `config/manga/canonical_brand_list.yaml::primary_topic + secondary_topics` — not relaxed by this constraint.
- Persona allocation (Gen Z / Gen Alpha / Millennial mix) stays governed by PR #1053.
