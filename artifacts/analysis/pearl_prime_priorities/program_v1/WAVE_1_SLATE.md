# Wave 1 Slate — 25 books (§6-eligible, diversity-balanced)

**Governed by:** `docs/specs/PEARL_PRIME_100_TO_1000_BESTSELLER_BUILD_PROGRAM.md` §6 + `docs/specs/PEARL_PRIME_WAVE_1_EXECUTION_SPEC.md`.
**Source data:** `artifacts/analysis/pearl_prime_priorities/best_current_100_build_list.csv`.
**Machine-readable:** `wave_1_slate.csv` / `wave_1_slate.json` (this dir).

## Eligibility (§6, hard filter on the slate)

`readiness_band == build_now` AND `scene_blocks >= 30` (healthy SCENE) AND `sparse_unit_count == 0` (**no hard dependency on an unrepaired glue bank**). Healthy STORY depth (=20) holds across the eligible pool. Eligible pool = **45 of 100** slate rows.

## Diversity balance (cap ≤4/persona, ≤5/topic soft)

- **25 books · 8 personas · 8 topics · max persona share 4/25 (16%).**
- Persona: gen_alpha_students 4 · gen_z_professionals 4 · corporate_managers 4 · gen_x_sandwich 4 · tech_finance_burnout 4 · working_parents 3 · educators 1 · nyc_executives 1.
- Topic: burnout 5 · anxiety 4 · financial_anxiety 4 · imposter_syndrome 4 · boundaries 3 · social_anxiety 2 · compassion_fatigue 2 · overthinking 1.

## Correction vs the earlier draft roster

`gen_z_professionals / anxiety` carries `sparse_unit_count = 1` in `PERMISSION_GRANT` — a dependency on an unrepaired glue bank. Per §6 it is **excluded** from Wave 1 and the pilot, deferred until fix-first item #19. The draft roster also over-weighted gen_alpha_students (9) and gen_x_sandwich (6); the cap rebalances to ≤4/persona, preferring repeatable families over lucky one-offs.

## Roster

| # | Persona | Topic | Score | STORY | SCENE | sparse | locales | Pilot-10 |
|---:|---|---|---:|---:|---:|---:|---:|:--:|
| 1 | gen_alpha_students | anxiety | 451 | 20 | 30 | 0 | 37 | ● |
| 2 | gen_z_professionals | burnout | 261 | 20 | 30 | 0 | 33 | ● |
| 3 | gen_z_professionals | financial_anxiety | 261 | 20 | 30 | 0 | 33 | ● |
| 4 | gen_z_professionals | imposter_syndrome | 261 | 20 | 30 | 0 | 33 | |
| 5 | corporate_managers | burnout | 251 | 20 | 30 | 0 | 27 | ● |
| 6 | corporate_managers | financial_anxiety | 251 | 20 | 30 | 0 | 22 | ● |
| 7 | corporate_managers | imposter_syndrome | 251 | 20 | 30 | 0 | 22 | |
| 8 | corporate_managers | social_anxiety | 251 | 20 | 30 | 0 | 22 | |
| 9 | educators | anxiety | 251 | 20 | 30 | 0 | 42 | ● |
| 10 | gen_alpha_students | boundaries | 251 | 20 | 30 | 0 | 37 | ● |
| 11 | gen_alpha_students | burnout | 251 | 20 | 30 | 0 | 37 | |
| 12 | gen_alpha_students | compassion_fatigue | 251 | 20 | 30 | 0 | 37 | |
| 13 | gen_x_sandwich | anxiety | 251 | 20 | 30 | 0 | 22 | ● |
| 14 | gen_x_sandwich | boundaries | 251 | 20 | 30 | 0 | 22 | ● |
| 15 | gen_x_sandwich | burnout | 251 | 20 | 30 | 0 | 22 | |
| 16 | gen_x_sandwich | compassion_fatigue | 251 | 20 | 30 | 0 | 22 | |
| 17 | gen_z_professionals | boundaries | 251 | 20 | 30 | 0 | 32 | |
| 18 | nyc_executives | anxiety | 251 | 20 | 30 | 0 | 38 | ● |
| 19 | tech_finance_burnout | burnout | 251 | 20 | 30 | 0 | 45 | |
| 20 | tech_finance_burnout | financial_anxiety | 251 | 20 | 30 | 0 | 46 | |
| 21 | tech_finance_burnout | imposter_syndrome | 251 | 20 | 30 | 0 | 46 | |
| 22 | tech_finance_burnout | overthinking | 251 | 20 | 30 | 0 | 46 | |
| 23 | working_parents | financial_anxiety | 251 | 20 | 30 | 0 | 32 | |
| 24 | working_parents | imposter_syndrome | 251 | 20 | 30 | 0 | 33 | |
| 25 | working_parents | social_anxiety | 251 | 20 | 30 | 0 | 33 | |

The **Pilot-10** (●) is the strongest 10 under a tighter persona cap (2) — see `PILOT_10_AND_FAN_OUT.md`.
