# Manga Catalog Plan — en_US / ja_JP / zh_TW / zh_CN — 2026-04-28

**Status:** PLAN ONLY — no manga catalog files generated.

> **Status note (2026-05-28):** The per-market format/genre matrices here remain the materialization source for `config/manga/brand_genre_allocation.yaml`. BUT the 12–13-brand roster predates the 37-brand canon — for **brands** use `config/manga/canonical_brand_list.yaml` (37) + the generated SSOT `config/source_of_truth/manga_series_plans/` (1,350 series, EXECUTED via Phase 2X). Genre %s are V1.2-era; the marketing-grounded V2 reweight target is `artifacts/research/marketing_grounded_per_genre_allocation_2026-05-13.md`.
**Authority for genre union:** [`config/manga/canonical_genre_list.yaml`](../config/manga/canonical_genre_list.yaml) (Precondition A output, 25 canonical genres)
**Authority for brand list:** [`config/catalog/market_catalog_registry.yaml`](../config/catalog/market_catalog_registry.yaml)
**Authority for archetype fit:** [`config/catalog_planning/teacher_brand_archetypes.yaml`](../config/catalog_planning/teacher_brand_archetypes.yaml), [`config/catalog_planning/brand_archetype_registry.yaml`](../config/catalog_planning/brand_archetype_registry.yaml)
**Companion catalogs (book scripts only):** [`docs/PEARL_PRIME_BOOK_SCRIPT_CATALOGS_2026-04-28.md`](PEARL_PRIME_BOOK_SCRIPT_CATALOGS_2026-04-28.md)

---

## §1 Scope

This is a **plan-only** artifact. No manga catalog files (`config/manga/manga_catalog_*.yaml`,
`artifacts/catalog/manga/*`) are generated in this drop. The deliverable is
the design contract for what the future manga catalog will contain when
later materialized.

What this doc defines:

1. The **brand × genre % allocation matrix** for each of the four target
   locales (en_US, ja_JP, zh_TW, zh_CN), with rows summing to 100% per brand.
2. The **reconciliation strategy** between this matrix and the existing 37
   mono-genre brand profiles in `config/source_of_truth/manga_profiles/brands/`.
3. The **locale strategy** — platform targets, genre-mix bias, adaptation
   destinations.
4. The **future catalog schema** the manga CSV will use when materialized.
5. **Dependencies and blockers** — what must land before manga catalog
   files can be safely generated.
6. The **execution sequence** for the future catalog creation task.

What this doc does NOT do:

- Generate any manga catalog YAML or CSV.
- Mutate any mono-genre brand profile.
- Change the canonical genre list (already produced as Precondition A).
- Call any LLM.
- Produce LoRA / character / panel artifacts.

---

## §2 Brand × genre % allocation matrix

### Genre column codes

For matrix readability the 25 canonical genres in
[`config/manga/canonical_genre_list.yaml`](../config/manga/canonical_genre_list.yaml)
are abbreviated below. The full table for each locale follows the legend.

| Code | Genre id              | Code | Genre id              | Code | Genre id              |
|------|-----------------------|------|-----------------------|------|-----------------------|
| BAT  | battle                | ROM  | romance               | SOL  | slice_of_life         |
| HOR  | horror                | MYS  | mystery               | SPO  | sports                |
| FAN  | fantasy_adventure     | WRK  | workplace             | FOO  | food                  |
| FAM  | family                | PRO  | procedural            | ESS  | essay                 |
| HEL  | healing               | HIS  | historical            | COM  | comedy                |
| CUL  | cultivation           | MEC  | mecha                 | DKF  | dark_fantasy          |
| SCY  | sci_fi_cyberpunk      | SUE  | supernatural_everyday | SCH  | school                |
| MEM  | memoir                | SOC  | social_issue          | GRM  | graphic_medicine      |
| BIN  | battle_internal       |      |                       |      |                       |

### Matrix design rule

For every brand row:

- **Primary genre** (tentpole, ~30–45%): the brand's existing mono-genre
  profile. This becomes the brand's "signature series" lane under
  reconciliation option C (see §3).
- **Secondary genres** (2–3 genres, ~30–40% combined): adjacent genres
  that the brand archetype + emotional engine support naturally.
- **Tertiary genres** (3–6 genres, ~15–25% combined): exploration lanes;
  one-shot or short-series cadence.
- **Excluded (0%)**: genres incompatible with the brand archetype
  (e.g. `sleep_restoration` does not produce mecha titles).

Rows sum to 100%. The matrix is **proposed**, not enforced — owner sign-off
required before materialization (see §6).

### §2.1 en_US matrix (12 teacher brands)

Locale bias: ebook-primary; manga is 10–15% of total mix per
`config/catalog/catalog_generation_config.yaml::lane_content_mix.en_US`.
Genre selections lean toward the universal-readability subset; lower
weighting on demo-bound genres (mecha, school) than ja_JP.

| Brand                | Primary (tentpole)         | Secondary                                             | Tertiary                                                                   | Excluded (0%)                                          |
|----------------------|----------------------------|-------------------------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------|
| stillness_press      | HEL 40%                    | ESS 12%, SOL 10%, MEM 8%                              | SUE 5%, GRM 5%, SCH 4%, FAM 4%, ROM 3%, COM 3%, MYS 3%, WRK 3%             | BAT, MEC, DKF, CUL, SPO, BIN, HOR, SCY, HIS, PRO, FOO  |
| cognitive_clarity    | ESS 35%                    | MYS 12%, BIN 10%, MEM 8%                              | WRK 7%, GRM 6%, SOL 5%, HEL 5%, SOC 4%, ROM 3%, COM 3%, SUE 2%             | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, FOO, FAM, SCH, PRO |
| somatic_wisdom       | ROM 30%                    | HEL 14%, ESS 10%, GRM 10%                             | SOL 8%, SCH 6%, FAM 5%, WRK 5%, MEM 4%, COM 4%, SUE 2%, BIN 2%             | BAT, MEC, DKF, CUL, SPO, HOR, SCY, HIS, FOO, PRO, MYS  |
| qi_foundation        | CUL 35%                    | HEL 15%, FAN 10%, BIN 8%                              | HIS 8%, ESS 7%, MEM 5%, SOL 4%, MYS 3%, SUE 3%, GRM 2%                     | ROM, MEC, DKF, SCY, SPO, HOR, COM, FOO, FAM, SCH, PRO, SOC |
| digital_ground       | SUE 30%                    | SOL 14%, SCH 10%, ESS 10%                             | ROM 8%, COM 7%, MYS 6%, FAN 5%, HOR 4%, MEM 3%, SCY 3%                     | BAT, MEC, DKF, CUL, SPO, HIS, FOO, FAM, PRO, GRM, BIN, SOC |
| heart_balance        | ROM 30%                    | SHJ-shadow→ESS 12%, FAM 10%, HEL 10%                  | MEM 8%, SOL 6%, GRM 6%, SOC 5%, SCH 5%, MYS 4%, COM 2%, SUE 2%             | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, FOO, PRO, BIN |
| relational_calm      | HEL 35%                    | SOL 14%, FAM 12%, ROM 8%                              | ESS 8%, SUE 6%, COM 5%, SCH 5%, GRM 3%, MEM 2%, FOO 2%                     | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, PRO, MYS, BIN, SOC |
| warrior_calm         | CUL 30%                    | BIN 15%, BAT 12%, FAN 10%                             | HIS 8%, MYS 6%, ESS 5%, MEC 4%, SPO 4%, DKF 3%, HEL 3%                     | ROM, SCY, COM, FOO, FAM, SCH, PRO, GRM, SUE, MEM, SOC, SOL |
| sleep_restoration    | HEL 45%                    | SOL 15%, SUE 10%, ESS 8%                              | MEM 5%, GRM 4%, FAM 4%, ROM 3%, SCH 3%, COM 2%, MYS 1%                     | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, PRO, FOO, BIN, SOC |
| body_memory          | ROM 28%                    | GRM 12%, MEM 10%, ESS 10%                             | HEL 8%, SOC 7%, FAM 6%, SOL 5%, SCH 5%, BIN 4%, MYS 3%, COM 2%             | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, FOO, PRO, SUE  |
| solar_return         | FAN 30%                    | DKF 12%, CUL 10%, BAT 10%                             | HIS 8%, ESS 7%, BIN 6%, ROM 5%, MYS 4%, SCY 4%, MEC 2%, SUE 2%             | SPO, COM, FOO, FAM, SCH, PRO, GRM, MEM, SOC, HEL, SOL    |
| devotion_path        | BAT 25%                    | FAN 13%, BIN 12%, CUL 10%                             | ESS 9%, ROM 7%, HIS 6%, DKF 5%, FAM 5%, MEM 3%, SUE 3%, MYS 2%             | MEC, SCY, SPO, HOR, COM, FOO, SCH, PRO, HEL, GRM, SOC, SOL |

#### en_US — top 3 deviations from uniform 1/25 (4%) baseline

- `sleep_restoration` bets heavy on **healing 45%** (≈11×) and avoids action genres entirely — its core promise is somatic recovery, not narrative tension.
- `qi_foundation` and `warrior_calm` both bet on **cultivation ≥30%** (≈8×) — only English-market brands allowed to carry the cultivation lane meaningfully.
- `solar_return` skews hard into **fantasy_adventure 30% + dark_fantasy 12%** — the only en_US brand with a meaningful DKF allocation, by virtue of its phoenix/cyclical-rebirth signature.

#### en_US — example 0% rationales

- `sleep_restoration` × `mecha` = 0%: machine-action register breaks the iyashikei contract.
- `cognitive_clarity` × `food` = 0%: zen-direct-pointing register has no surface for sensory cooking dramaturgy.
- `heart_balance` × `cultivation` = 0%: shojo+mythological brand voice is incompatible with progression-fantasy power scaling.

---

### §2.2 ja_JP matrix (12 teacher brands)

Same 12 brands as en_US. Locale bias: **manga-primary** (60% mix per
`market_catalog_registry.yaml::japan.content_mix`). Genre allocation lifts
demo-bound genres (school, supernatural_everyday, mecha, sports), suppresses
genres that are saturated in the JP market without local differentiator
(generic memoir/essay), and allocates more aggressively to the
mono-genre tentpole because the JP audience pays a premium for clear
genre identity.

| Brand                | Primary (tentpole)         | Secondary                                             | Tertiary                                                                   | Excluded (0%)                                          |
|----------------------|----------------------------|-------------------------------------------------------|----------------------------------------------------------------------------|--------------------------------------------------------|
| stillness_press      | HEL 45%                    | SOL 12%, SUE 10%, ESS 8%                              | SCH 6%, FAM 5%, MEM 4%, ROM 3%, COM 3%, GRM 2%, MYS 2%                     | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, FOO, PRO, BIN, SOC  |
| cognitive_clarity    | ESS 30%                    | MYS 14%, BIN 12%, GRM 10%                             | MEM 8%, WRK 6%, SOC 6%, SOL 5%, HEL 4%, SUE 3%, SCH 2%                     | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, FOO, ROM, COM, PRO, FAM |
| somatic_wisdom       | ROM 28%                    | SCH 14%, GRM 10%, ESS 10%                             | HEL 8%, SOC 7%, SOL 6%, FAM 5%, COM 4%, MEM 3%, BIN 3%, SUE 2%             | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, FOO, PRO, MYS, WRK, SOL |
| qi_foundation        | CUL 32%                    | HIS 14%, FAN 10%, BIN 10%                             | DKF 8%, HEL 8%, ESS 7%, MEM 4%, MYS 3%, SUE 3%, FOO 1%                     | ROM, MEC, SCY, SPO, HOR, COM, FAM, SCH, PRO, GRM, SOC, SOL  |
| digital_ground       | SUE 32%                    | SCH 14%, SOL 10%, ESS 8%                              | ROM 8%, COM 6%, MYS 6%, FAN 5%, MEC 4%, HOR 4%, SCY 3%                     | BAT, DKF, CUL, SPO, HIS, FOO, FAM, PRO, GRM, BIN, MEM, SOC, HEL |
| heart_balance        | ROM 32%                    | ESS 12%, FAM 10%, HEL 10%                             | SCH 7%, GRM 6%, MEM 5%, SOL 5%, SOC 5%, MYS 4%, COM 2%, SUE 2%             | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, FOO, PRO, BIN, WRK |
| relational_calm      | HEL 38%                    | SOL 14%, FAM 12%, SUE 8%                              | ROM 7%, SCH 6%, ESS 5%, COM 4%, MEM 3%, GRM 2%, FOO 1%                     | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, PRO, MYS, BIN, SOC, WRK |
| warrior_calm         | BAT 25%                    | CUL 15%, BIN 14%, FAN 10%                             | HIS 8%, MEC 8%, MYS 5%, ESS 5%, DKF 5%, SPO 4%, HEL 1%                     | ROM, SCY, COM, FOO, FAM, SCH, PRO, GRM, SUE, MEM, SOC, SOL, FOO  |
| sleep_restoration    | HEL 50%                    | SOL 15%, SUE 10%, ESS 6%                              | MEM 4%, GRM 4%, FAM 4%, ROM 3%, SCH 2%, COM 1%, MYS 1%                     | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, PRO, FOO, BIN, SOC |
| body_memory          | ROM 26%                    | GRM 14%, MEM 12%, ESS 10%                             | HEL 8%, SOC 7%, FAM 6%, SCH 5%, SOL 4%, BIN 4%, MYS 2%, COM 2%             | BAT, MEC, DKF, CUL, SPO, FAN, HOR, SCY, HIS, FOO, PRO, SUE  |
| solar_return         | FAN 32%                    | DKF 14%, BAT 10%, CUL 10%                             | HIS 8%, BIN 7%, MEC 5%, ESS 4%, ROM 4%, MYS 3%, SCY 2%, SUE 1%             | SPO, COM, FOO, FAM, SCH, PRO, GRM, MEM, SOC, HEL, SOL, HOR    |
| devotion_path        | BAT 30%                    | FAN 14%, BIN 12%, CUL 10%                             | HIS 8%, ROM 6%, DKF 5%, ESS 5%, FAM 4%, MEM 2%, SUE 2%, MYS 2%             | MEC, SCY, SPO, HOR, COM, FOO, SCH, PRO, HEL, GRM, SOC, SOL  |

#### ja_JP — top 3 deviations from uniform 1/25 baseline

- `sleep_restoration` ×  HEL 50% (≈12.5× baseline) — JP iyashikei market rewards single-genre saturation.
- `warrior_calm` ×  BAT 25% + MEC 8% — only brand carrying meaningful mecha allocation; JP-only register.
- `solar_return` × FAN 32% + DKF 14% — fantasy_adventure-as-tentpole skews hardest in JP where the isekai/dark-fantasy market is mature.

#### ja_JP — example 0% rationales

- `cognitive_clarity` × `comedy` = 0%: the zen direct-pointing tone is incompatible with comedic deformation pacing.
- `relational_calm` × `mecha` = 0%: wabi-sabi simplicity is structurally opposed to mechanical-detail-heavy panels.
- `body_memory` × `procedural` = 0%: somatic-memory grief register breaks under case-loop episodic structure.

---

### §2.3 zh_TW matrix (19 brands: 12 teacher + 6 zh-specific + bright_presence_tw)

The 12 teacher-brand rows use the same allocations as en_US with one
adjustment: cultivation and historical lift +5–8% (taking from essay/memoir)
to match the Taiwan market's stronger appetite for `cultivation_martial`
and historical-period content (per
`config/manga/canonical_genre_list.yaml` aliases). The 7 additional rows
appear below the teacher-brand block.

#### zh_TW — 12 teacher brands (same shape as en_US §2.1, with +CUL/+HIS bias)

| Brand                | Primary                  | Secondary                                       | Tertiary highlights              |
|----------------------|--------------------------|-------------------------------------------------|----------------------------------|
| stillness_press      | HEL 38%                  | ESS 12%, SOL 10%, HIS 6%                        | MEM, SUE, GRM, FAM, SCH          |
| cognitive_clarity    | ESS 32%                  | MYS 12%, BIN 10%, HIS 7%                        | MEM, WRK, GRM, SOL, HEL          |
| somatic_wisdom       | ROM 28%                  | HEL 13%, ESS 10%, GRM 9%                        | SOL, SCH, FAM, WRK, MEM          |
| qi_foundation        | CUL 40%                  | HIS 14%, FAN 10%, BIN 8%                        | HEL, ESS, MEM, SOL, MYS          |
| digital_ground       | SUE 28%                  | SOL 13%, SCH 10%, ESS 9%                        | ROM, COM, MYS, FAN, HOR          |
| heart_balance        | ROM 28%                  | ESS 12%, FAM 10%, HEL 9%, HIS 5%                | MEM, SOL, GRM, SOC, SCH          |
| relational_calm      | HEL 32%                  | SOL 14%, FAM 12%, ROM 7%                        | ESS, SUE, COM, SCH, GRM          |
| warrior_calm         | CUL 35%                  | BIN 14%, BAT 11%, HIS 10%, FAN 8%               | MYS, ESS, MEC, SPO, DKF          |
| sleep_restoration    | HEL 45%                  | SOL 15%, SUE 10%, ESS 7%                        | MEM, GRM, FAM, ROM, SCH          |
| body_memory          | ROM 26%                  | GRM 11%, MEM 10%, ESS 9%, HIS 5%                | HEL, SOC, FAM, SOL, SCH          |
| solar_return         | FAN 28%                  | DKF 12%, CUL 12%, HIS 10%, BAT 8%               | ESS, BIN, ROM, MYS, MEC          |
| devotion_path        | BAT 22%                  | FAN 13%, BIN 12%, CUL 12%, HIS 8%               | ESS, ROM, DKF, FAM, MEM          |

(Full 25-genre breakdown lives in the future-state CSV; rows sum to 100%
in implementation. The compact form above lists primary, secondary, and
tertiary highlights — see §5 for the full schema the materialized catalog
will use.)

#### zh_TW — 7 additional brands (6 zh-specific + Adi Da Taiwan-only)

| Brand                | Teacher mode | Primary       | Secondary                       | Notes                                                                  |
|----------------------|--------------|---------------|---------------------------------|------------------------------------------------------------------------|
| sleep_repair_tw      | false        | HEL 50%       | SOL 15%, SUE 10%, ESS 8%        | Standard brand; healing-iyashikei tentpole; same shape as `sleep_restoration` |
| stabilizer_tw        | false        | HEL 35%       | SOL 12%, ESS 10%, FAM 8%        | Nervous-system stabilization; broader emotional range than sleep_repair |
| panic_first_aid_tw   | false        | BIN 25%       | HOR 15%, HEL 12%, ESS 10%       | Acute-anxiety register; the only standard brand with meaningful HOR allocation |
| gen_z_grounding_tw   | false        | SCH 28%       | SOC 14%, SUE 10%, ROM 8%        | Generational/youth focus — heaviest school + social_issue allocation in zh_TW |
| grief_companion_tw   | false        | MEM 28%       | FAM 14%, GRM 12%, ESS 10%       | Memoir-tentpole — only brand whose primary is the memoir lane          |
| inner_security_tw    | false        | ESS 28%       | HEL 12%, MEM 10%, FAM 9%        | Attachment-adjacent reflective register                                |
| bright_presence_tw   | true         | MEC 30%       | SCY 14%, BIN 10%, ESS 10%, DKF 8% | **Only mecha-tentpole brand in any locale**; Adi Da philosophical mecha (Evangelion register). Excludes ROM, COM, FOO, SCH, FAM, SOL, SPO. |

#### zh_TW — top 3 deviations from baseline

- `bright_presence_tw` × MEC 30%: the only brand carrying a mecha
  tentpole anywhere in the four-locale plan. This is the design rationale
  for keeping it Taiwan-exclusive (Adi Da audience overlap with the TW
  philosophical-seinen reader).
- `qi_foundation` × CUL 40% (zh_TW lift from 35% en_US baseline): TW market
  matches the Chinese-origin cultivation lineage natively.
- `grief_companion_tw` × MEM 28%: TW catalog gets the only memoir-primary
  brand; pairs with Taiwan-strong adaptation channels for autobiographical
  manga.

---

### §2.4 zh_CN matrix (18 brands: 12 teacher + 6 zh-specific)

zh_CN catalog **omits** `bright_presence_tw` (Adi Da brand restricted to TW
per `config/manga/manga_brand_series_plan.yaml:13,381`). Manga is **0% mix**
on the zh_CN ebook lane per
`config/catalog/catalog_generation_config.yaml::lane_content_mix.zh_CN`
(market access constraint, not a genre-fit issue). The matrix below
documents the design intent for if/when manga becomes accessible.

#### zh_CN — 12 teacher brands

Same allocations as zh_TW §2.3, but with `cultivation` and `historical`
weights normalized back toward en_US baseline (zh_CN audience accesses
cultivation through web-novel / donghua channels rather than print/manga,
so the manga-genre mix is more conservative). Cell-level numbers identical
to en_US §2.1 except with HIS lifted +2% and CUL lifted +3% absorbed from
ESS.

#### zh_CN — 6 zh-specific brands

| Brand                | Teacher mode | Primary       | Secondary                       | Notes                                                                  |
|----------------------|--------------|---------------|---------------------------------|------------------------------------------------------------------------|
| sleep_repair_cn      | false        | HEL 50%       | SOL 15%, SUE 10%, ESS 8%        | Identical shape to sleep_repair_tw                                     |
| stabilizer_cn        | false        | HEL 35%       | SOL 12%, ESS 10%, FAM 8%        | Identical to stabilizer_tw                                             |
| panic_first_aid_cn   | false        | BIN 25%       | HOR 12%, HEL 14%, ESS 10%       | HOR slightly suppressed vs TW (regulatory sensitivity)                 |
| gen_z_grounding_cn   | false        | SCH 25%       | SOC 12%, SUE 10%, ROM 10%       | SOC slightly suppressed vs TW; school-romance lifts                    |
| grief_companion_cn   | false        | MEM 26%       | FAM 14%, ESS 12%, GRM 10%       | GRM slightly suppressed vs TW (graphic-medicine market is thinner)     |
| inner_security_cn    | false        | ESS 28%       | HEL 12%, MEM 10%, FAM 9%        | Identical to inner_security_tw                                         |

#### zh_CN — example 0% rationales (regulatory + market)

- All brands × `social_issue` ≤ 5%: regulatory review on contemporary
  Chinese social issue content is unpredictable; matrix conservatively
  caps the lane.
- All brands × `horror` ≤ 12%: same rationale; horror + body-horror
  expressionism is regulatory-sensitive.
- `panic_first_aid_cn` × `mecha` = 0%: panic-physiology register is
  incompatible with mecha-scale narrative.

---

## §3 Reconciliation with existing mono-genre brand profiles

There are **37** mono-genre profiles under
`config/source_of_truth/manga_profiles/brands/` (per `ls`). The dev brief
referenced "30" — the discrepancy is because some brands (e.g.
`bio_flow_healing`, `executive_calm_workplace`) are standard brands not in
the 12-teacher-brand set, but still carry mono-genre profiles. All 37
remain valid under the chosen reconciliation.

### Recommendation: option (C) — Coexist

The mono-genre profile is the brand's **tentpole / signature series**.
The portfolio matrix is the brand's full lane mix.

Concretely:

- The mono-genre filename (e.g. `solar_return_isekai.yaml`) names the
  tentpole — the long-running flagship that defines reader expectation.
- The matrix `Primary` column corresponds to the same genre as the
  tentpole (≥30% allocation guarantees the tentpole has enough volume to
  build series equity).
- Secondary and tertiary genres are the **portfolio releases** — one-shots,
  short series, format experiments, locale-specific spin-offs. They use
  the brand's voice and visual identity but explore adjacent genre lanes.

### Why option C over A or B

- **(A) Add `genre_allocation` field to mono-genre profile, keep
  primary_genre.** Rejected because it conflates two contracts in one
  file. The mono-genre profile is a **series-level** contract (one title's
  genre lane, pacing, page-cell rhythm); the matrix is a **brand-level
  portfolio** contract.
- **(B) Replace mono-genre with matrix; primary_genre = argmax.**
  Rejected because it discards the per-series specificity already
  encoded in pacing fields (`words_per_page_range`, `silent_panel_ratio_range`,
  etc.) that the renderer needs to decide visual budgets per title.
- **(C) Coexist with reconciliation rule.** ✅ Selected. Existing
  profiles remain authoritative for the tentpole; the matrix is materialized
  as a sibling artifact (`config/manga/brand_genre_allocation.yaml` —
  proposed name). Cross-link rule: matrix's `Primary` cell **must equal**
  the mono-genre file's `genre_family` (validation can be enforced by a
  small CI script when the matrix lands).

---

## §4 Locale strategy

### en_US

- Target platforms: WEBTOON Canvas (serial), Amazon KDP graphic novel EPUB
  (collected volumes), Apple Books, Google Play Books, Kobo.
- Genre mix bias: universal-readability genres lift (slice_of_life, healing,
  romance, essay, supernatural_everyday, fantasy_adventure); demo-bound JP
  genres (mecha, cultivation, school) suppress.
- Adaptation targets per `config/manga/manga_taxonomy.yaml::adaptation_targets`:
  primarily web-comic + ebook; light prose adaptation viable.
- Lane content mix: `manga_series 0.10 + manga_standalone 0.05 + micro_manga 0.05`
  (per `catalog_generation_config.yaml`).

### ja_JP

- Target platforms: `manga_app_partners` + `physical_doujin` + `booth.pm`
  (per `market_catalog_registry.yaml::japan.business_tracks.manga_partnership`),
  plus standard digital (Kindle JP, Rakuten Kobo JP).
- Genre mix bias: heaviest weighting on canonical demo lanes —
  shonen+seinen (battle, cultivation, sports, mystery), shojo+josei
  (romance, healing, slice_of_life), iyashikei suite (healing-as-tentpole).
- Cross-track strategy: dual track per `japan_dual_track_config.yaml`
  (manga partnership 60%, digital publishing 40%).
- This is the **highest-volume manga lane** in the plan; tentpole brands
  here drive the global series equity that en_US/zh_TW/zh_CN catalogs
  benefit from downstream.

### zh_TW

- Target platforms: BookWalker TW, LINE Webtoon TW, Pi Comic, Readmoo,
  Apple Books TW, Amazon TW.
- Genre mix bias: cultivation + historical-period lift (TW market matches
  the Chinese-tradition lineage); romance and shojo-adjacent genres at en_US
  baseline; supernatural_everyday slightly elevated (TW market has strong
  manhwa-style supernatural readership via webtoon).
- Carries the only mecha tentpole (`bright_presence_tw`) — see §2.3.
- Adaptation targets: webtoon-vertical primary; ebook secondary.

### zh_CN

- Target platforms (with regulatory caveat): Dangdang, Jingdong, WeRead,
  Ximalaya, Duokan. Manga lane is currently **0% mix** in the
  ebook-primary catalog config; this manga plan documents the design
  intent for if/when local-entity access is established.
- Genre mix bias: similar to zh_TW for cultivation + historical, but
  social_issue and horror lanes are conservatively suppressed (≤ 5% and
  ≤ 12% respectively) to reduce regulatory friction.
- Pipeline note: text content is on the Qwen / CJK6 lane per
  `CLAUDE.md` LLM Tier policy; manga visual generation pipeline is
  unaffected.

---

## §5 Future catalog field schema (planned, not implemented)

When the manga catalog CSV is materialized (separate task — see §7), the
proposed columns are:

| #  | Column                     | Type      | Notes                                                                      |
|----|----------------------------|-----------|----------------------------------------------------------------------------|
| 1  | `locale`                   | enum      | en_US / ja_JP / zh_TW / zh_CN                                              |
| 2  | `market`                   | string    | from `market_catalog_registry.yaml`                                        |
| 3  | `brand`                    | string    | brand id                                                                   |
| 4  | `brand_locale_name`        | string    | from `locale_brand_names.yaml`                                             |
| 5  | `series_id`                | string    | unique series identifier (planned: `{brand}_{genre}_{nn}`)                 |
| 6  | `series_title`             | string    | locale-localized                                                           |
| 7  | `genre`                    | enum      | from `config/manga/canonical_genre_list.yaml`                              |
| 8  | `is_tentpole`              | bool      | true iff this row's genre matches the brand's mono-genre tentpole          |
| 9  | `genre_allocation_pct`     | float     | per the matrix in §2 (rows must sum to 100% per brand)                     |
| 10 | `series_format`            | enum      | `print_manga` / `web_manga` / `webtoon_vertical` / `motion_comic`          |
| 11 | `chapters_per_volume`      | int       | typical 6–10 for tankōbon, 4–8 for webtoon collected                       |
| 12 | `cadence_weeks`            | int       | release cadence in weeks (1 = weekly serial, 4 = monthly volume)           |
| 13 | `visual_grammar`           | enum-list | from `manga_taxonomy.yaml::default_visual_grammars`                        |
| 14 | `emotional_engine`         | enum-list | from `manga_taxonomy.yaml::default_emotional_engines`                      |
| 15 | `serialization_engine`     | enum-list | from `manga_taxonomy.yaml::default_serialization_engines`                  |
| 16 | `pacing_profile_ref`       | string    | key into `config/manga/manga_pacing_by_genre.yaml`                         |
| 17 | `lora_plan_ref`            | string    | key into `config/manga/brand_lora_plans.yaml` (for visual generation)      |
| 18 | `character_pipeline_ref`   | string    | reference to character/protagonist LoRA spec                               |
| 19 | `pipeline_route`           | literal   | manga rendering route (TBD — separate from the book script spine pipeline) |
| 20 | `readiness_status`         | enum      | `ready` / `blocked_lora` / `blocked_pacing` / `blocked_archetype`          |
| 21 | `output_target_path`       | string    | `artifacts/manga/{locale}/{brand}/{series_id}/...`                         |
| 22 | `notes`                    | string    | free text                                                                  |
| 23 | `blockers`                 | string    | semicolon-separated blocker tags                                           |

This mirrors the Pearl Prime book script catalog schema where the lanes
overlap (locale/market/brand/readiness/output_target_path/notes/blockers)
and adds manga-specific columns (`series_format`, `cadence_weeks`,
`visual_grammar`, etc.).

---

## §6 Dependencies and blockers

Materializing the manga catalog requires, in order:

1. **Precondition A — genre reconciliation.** ✅ Complete in this drop:
   `config/manga/canonical_genre_list.yaml` (25 canonical genres, 20
   inbound aliases, must_include set covers user-required genres).
2. **§3 reconciliation strategy decision.** Owner-confirmed as option (C)
   in the dev brief decisions for this PR.
3. **Per-brand allocation sign-off.** Owner must approve the matrix in §2
   (the cells are proposed, not adopted). Sign-off can be partial
   (per-locale).
4. **LoRA + character pipeline coverage gap audit** —
   `config/manga/brand_lora_plans.yaml` must cover every (brand × genre)
   cell with allocation > 0% before that cell can move to
   `readiness_status=ready` in the materialized catalog. Genres not
   currently covered (e.g. mecha for `bright_presence_tw`) require new
   LoRA plans.
5. **Pacing contract coverage** — every cell's genre must resolve to a
   pacing row in `config/manga/manga_pacing_by_genre.yaml` (directly or
   via the alias map in `canonical_genre_list.yaml`). 25/25 currently
   resolve, so this is satisfied.

### Open questions for owner before §7 executes

- **Q-M1**: Should the materialized matrix file live at
  `config/manga/brand_genre_allocation.yaml` (proposed) or under
  `config/catalog_planning/`? The proposal places it under
  `config/manga/` because it's manga-format-specific. Owner to confirm.
- **Q-M2**: For zh_CN where lane content mix is 0% manga, should the
  matrix still be materialized (as design intent) or omitted until
  market access is established? The default below assumes
  *materialize but tag readiness as `blocked_market_access`*.
- **Q-M3**: bright_presence_tw mecha tentpole — should we proactively
  draft a LoRA plan now, or block on Adi Da audience research first?

---

## §7 Execution sequence (future task)

1. Owner sign-off on §2 matrices (per-locale acceptable).
2. Resolve Q-M1, Q-M2, Q-M3 from §6.
3. Write a small materializer script (proposal: `scripts/catalog/materialize_manga_genre_matrix.py`)
   that reads `config/manga/brand_genre_allocation.yaml` (the materialized
   matrix), enumerates `(brand, genre, locale)` rows, and emits per-locale
   manga catalog CSVs. Same wrapper pattern used by the Pearl Prime book
   script generator in this PR.
4. Apply LoRA plan coverage check for every cell with allocation > 0%.
   Cells without LoRA coverage are emitted as `readiness_status=blocked_lora`
   with `blockers=needs_lora_plan`.
5. Apply pacing contract resolution. Cells whose genre is unmapped → `blocked_pacing`.
6. Generate `artifacts/catalog/manga/{locale}_catalog.csv` for the four
   target locales, plus a `manga_catalog_summary.json` analogous to the
   Pearl Prime summary.
7. Generate a follow-up doc `docs/MANGA_CATALOG_<DATE>.md` reporting
   row counts, ready/blocked split, and top blockers — same shape as
   `docs/PEARL_PRIME_BOOK_SCRIPT_CATALOGS_2026-04-28.md`.

This sequence does **not** assemble manga panels, generate images, or
call any LLM. It is a catalog/queue task only.
