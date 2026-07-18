# V1.2 Corrections Pass — 2026-05-12

**Branch:** `agent/v1-2-corrections-pass-20260512`
**Base:** `origin/main` @ `3da3088ef` (V1.2 tip, 500-series across 20 PRs merged)
**Scope:** Minimal surgical enum + brand_id remap across 4 cluster YAML files.
**Prose changes:** NONE (only enum values and brand_id / series_id metadata).
**Files touched:** 4 YAML + 1 audit MD = 5 total.

---

## Issue 1 — Non-canonical `serial_engine` values

Canonical 6 engines per PR #1051:
`mystery_box | power_escalation_ladder | companion_roster | location_anthology | case_of_the_week | life_stage_rhythm`

### 1a. `artifacts/marketing/v1_2_themes_en_US_cluster_b.yaml`

Drift value: `party_quest` (3 instances) → all remapped to **`companion_roster`**.

| Line | series_id | Rationale |
|------|-----------|-----------|
| 186 | `cognitive_clarity__en_US__guild_of_overthinkers` | "joins a guild of fellow-overthinkers… paladin/bard/healer" — recurring party is the engine. |
| 418 | `focus_sprint_workplace__en_US__hyperfocus_island` | "joins a small party… paladin from Working-Memory, bard from Time-Perception, healer from Emotional-Regulation" — same recurring roster. |
| 562 | `adhd_forge_mystery__en_US__interest_island` | "small party: paladin whose interest is mineral classification, bard whose interest is city pop, healer whose interest is dialect drift" — recurring roster. |

All three have an episodic location-of-the-week veneer (one island per arc), but the party is named, persistent, and central — `companion_roster` is the correct primary engine.

### 1b. `artifacts/marketing/v1_2_themes_zh_CN_cluster_a.yaml`

Drift values: `slice_of_life_arc` (8 instances), `serialized_long_arc` (2 instances).

| Line | series_id | Old enum | New enum | Rationale |
|------|-----------|----------|----------|-----------|
| 98  | `stillness_press__zh_CN__kou_dai_li_de_xiao_zhang_ben` | slice_of_life_arc | **life_stage_rhythm** | Uni → graduation arc; protagonist ages across volumes. |
| 126 | `stillness_press__zh_CN__neng_kan_jian_wo_jiao_lv_de_shi_you` | slice_of_life_arc | **life_stage_rhythm** | 23-yr-old learning to be seen across cohabitation arc. |
| 298 | `sleep_restoration_iyashikei__zh_CN__ye_chu_fang` | slice_of_life_arc | **case_of_the_week** | Different insomniac visitor through the kitchen window each volume. |
| 358 | `somatic_wisdom_shojo__zh_CN__pu_la_ti_si_jiao_lian_de_xiao_yao` | slice_of_life_arc | **case_of_the_week** | One client / one body-spirit per 50-min Pilates session per volume. |
| 414 | `somatic_wisdom_shojo__zh_CN__lin_li_an_mo_shi` | slice_of_life_arc | **case_of_the_week** | "一卷一位街坊" — different neighbor / body part per volume. |
| 442 | `somatic_wisdom_shojo__zh_CN__cheng_ji_huo_xi_shi_wai_lian_xi` | slice_of_life_arc | **case_of_the_week** | Each volume profiles one heavy-screen-user group member. |
| 470 | `somatic_wisdom_shojo__zh_CN__pan_yan_jian_shen_fang` | slice_of_life_arc | **case_of_the_week** | "一卷一位會員、一面墙" — different member + wall per volume. |
| 558 | `body_memory_shojo__zh_CN__shen_ti_zhi_tu_shi` | serialized_long_arc | **mystery_box** | Soft-fantasy register; gradual revelation of hidden twin sister at map's end — mystery-box payoff structure. |
| 614 | `body_memory_shojo__zh_CN__shou_de_ji_yi` | slice_of_life_arc | **case_of_the_week** | "一卷一位老人" — different elder per haircut per volume. |
| 758 | `stabilizer_healing__zh_CN__wen_xin_zhong_xue_xin_sheng_ji` | serialized_long_arc | **power_escalation_ladder** | School-year progression: girls + anxiety-creatures level up together each volume. |

---

## Issue 2 — Non-canonical `magical_register` value

Canonical 6 registers:
`supernatural_everyday | magical_realism | soft_fantasy | isekai | occult_cosmic | none`

### `artifacts/marketing/v1_2_themes_zh_TW_cluster_b.yaml`

Drift value: `high_fantasy` (3 instances) → all remapped to **`isekai`** (each series features a threshold crossing from real Taipei into a parallel fantasy realm).

| Line | series_id | Rationale |
|------|-----------|-----------|
| 431 | `focus_sprint_workplace__zh_TW__ban_dao_zhu_li_si_chu_zhang` | Office tea-room back door → "辦島" (Office Island) parallel realm — classic isekai threshold. |
| 519 | `adhd_forge_mystery__zh_TW__si_xiang_kuang_jia_de_jian_zao_zhe` | Library bookstack hidden door → parallel "腦島" (Brain Island) for neurodivergent only — isekai. |
| 635 | `career_lift_workplace__zh_TW__zhi_ye_zhuan_huan_qi_shi` | Front door of apartment → parallel fantasy Taipei with knights' guild — isekai. |

The `soft_fantasy` default in the operator brief would have undersold the threshold-crossing protagonist mechanic explicit in all three series descriptions; `isekai` is the precise canonical fit.

---

## Issue 3 — Cluster E ja_JP brand mapping mismatch

PR #1074 (`v1_2_themes_ja_JP_cluster_e.yaml`) used three brand_ids that diverged from the canonical en_US Cluster E mapping (PR #1073).

**Canonical Cluster E mapping (locked from en_US):**
- `gen_z_grounding` → `calm_student_school`
- `confidence_core` → `confidence_core_romance`
- `mecha_identity` → `solar_return_isekai`

**Before / after — ja_JP Cluster E brand_id swaps:**

| Cluster-role | ja_JP before | ja_JP after (canonical) |
|--------------|--------------|-------------------------|
| `digital_ground` | `digital_ground` | `digital_ground` (no change) |
| `gen_z_grounding` | `confidence_core_romance` | **`calm_student_school`** |
| `confidence_core` | `calm_student_school` | **`confidence_core_romance`** |
| `mecha_identity` | `focus_sprint_workplace` | **`solar_return_isekai`** |
| `queer_identity_growth` | `creative_unfold_social` | `creative_unfold_social` (no change) |

15 series affected (3 brands × 5 series). For each affected series:
- `brand_id:` field replaced with canonical brand.
- `series_id:` prefix re-slugged to match new brand (e.g. `confidence_core_romance__ja_JP__hoshou_shitsu_no_juu_gofun` → `calm_student_school__ja_JP__hoshou_shitsu_no_juu_gofun`).
- BRAND section comment headers (lines 199, 345, 491) and top-of-file mapping docstring (lines 16-18) updated to reflect the canonical mapping.
- **Prose unchanged.** Each series' narrative is brand-agnostic at the topic-register layer; the swap is mechanically safe. No conflicts surfaced during inspection of the 15 series descriptions.

**Verified post-state — ja_JP Cluster E brand_id distribution:**
```
digital_ground: 5
calm_student_school: 5
confidence_core_romance: 5
solar_return_isekai: 5
creative_unfold_social: 5
```
All 25 series have `series_id` prefixes matching their `brand_id`.

---

## Final canonical-enum state

Repo-wide sweep across all 20 V1.2 cluster YAMLs:

```bash
$ grep -rE "(party_quest|slice_of_life_arc|serialized_long_arc|high_fantasy)" \
      artifacts/marketing/v1_2_themes_*.yaml
# (no matches)
```

**Zero non-canonical enum values remain across the V1.2 corpus.**

## YAML parse verification

All 4 touched YAMLs parse with `yaml.safe_load` and report exactly 25 series each.

## Prose changes

NONE. Only enum values (`serial_engine`, `magical_register`), `brand_id`, `series_id` slugs, and structural / mapping comment lines were modified.

## Files in WRITE_SCOPE (5 total)

- `artifacts/marketing/v1_2_themes_en_US_cluster_b.yaml`
- `artifacts/marketing/v1_2_themes_zh_CN_cluster_a.yaml`
- `artifacts/marketing/v1_2_themes_zh_TW_cluster_b.yaml`
- `artifacts/marketing/v1_2_themes_ja_JP_cluster_e.yaml`
- `artifacts/qa/v1_2_corrections_pass_2026-05-12.md` (this file)
