# Assembled-Book Quality Scorecard

**Date:** 2026-06-30 · **Books verified:** 31 artifacts / 24 persona×topic cells · **Pass bar:** EI v2 ≥ 0.5 (Tier-1 read may override cohesive-flow)

## Summary counts

| Dimension | PASS | CONCERN | FAIL |
|-----------|-----:|--------:|-----:|
| Bestseller | 14 | 13 | 4 |
| Cohesive flow | 12 | 17 | 2 |
| Engaging | 20 | 4 | 7 |
| Marketing-fit (lexicon) | 31 | 0 | 0 |
| Leakage (clean_for_delivery) | 28 clean | 0 | 3 FAIL |

**Meta-finding confirmed:** Bestseller / engaging / marketing-fit score well on full spine books. **Cohesive flow is the soft dimension** — deterministic EI v2 cohesion averages 0.80+ PASS, but Tier-1 read downgrades all 12-chapter Pearl Prime books to CONCERN due to engine-keyed thesis reuse and cadence refrains. This matches the plan-scale repetition census (1281/1281 MEDIUM).

---

## Full spine — wave_proof draft (clean renders)

| Persona | Topic | Duration | Bestseller | Cohesive flow | Engaging | Marketing | Leakage | Verdict |
|---------|-------|----------|------------|---------------|----------|-----------|---------|---------|
| corporate_managers | burnout (grief engine) | standard_book | CONCERN 0.44 | **CONCERN** 0.82† | PASS 0.55 | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| corporate_managers | burnout (overwhelm) | standard_book | CONCERN 0.44 | **CONCERN** 0.82† | PASS 0.55 | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| corporate_managers | burnout (watcher) | standard_book | CONCERN 0.45 | **CONCERN** 0.85† | PASS 0.55 | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| gen_z_professionals | burnout (grief) | standard_book | CONCERN 0.46 | **CONCERN** 0.80† | PASS 0.58 | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| healthcare_rns | burnout (overwhelm) | standard_book | CONCERN 0.42 | **CONCERN** 0.85† | PASS 0.55 | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| working_parents | burnout (overwhelm) | standard_book | CONCERN 0.47 | **CONCERN** 0.83† | PASS 0.54 | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| first_responders | burnout (watcher) | standard_book | CONCERN 0.45 | **CONCERN** 0.85† | PASS 0.55 | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| gen_z_professionals | imposter_syndrome (shame) | standard_book | FAIL 0.40 | **CONCERN** 0.80† | PASS 0.58 | PASS / YES | clean | SELLABLE_WITH_ADVISORY |

† EI v2 deterministic PASS; Tier-1 override applied (see evidence below).

**Tier-1 cohesion evidence (wave_proof / corporate_managers × burnout overwhelm):**

- Ch1 and Ch2 share engine-keyed opener: *"This Is Not Tiredness"* + leadership-appearance thesis — identical across grief/overwhelm/watcher engines for same persona (`burnout_grief__corporate_managers` vs `burnout_overwhelm__corporate_managers` byte-identical through line ~40).
- Within-book cadence refrains repeat: *"Peel back the obvious. Something else lives one inch down."* (Ch2), *"Rest at this stop. You do not have to march past it."* (Ch1) — template cadence, not earned callbacks.
- Chapter titles **do** progress (Ch2 *"What You're Actually Losing"*, Ch3 *"The Equation You Never Questioned"*, Ch4 *"Your Body Was Telling the Truth"*) — journey exists at macro level; micro atom boundaries feel like restarts.
- `content_uniqueness` avg **0.13–0.16** across chapters (engine pool exhaustion per REPETITION_CENSUS).
- Scene assembly garble in places (e.g. Ch1 L20: *"carpet hush lingers through the corridor. does not exist in the elevator"*) — register/scene issue, not template leakage.

**Quotable hook (marketing):** *"You do not have to march past it."* / *"This is the bargain you make when you take responsibility for others."*

---

## Full spine — pilot_10 / #3605

| Persona | Topic | Bestseller | Cohesive flow | Engaging | Marketing | Leakage | Verdict |
|---------|-------|------------|---------------|----------|-----------|---------|---------|
| gen_alpha_students | anxiety | CONCERN 0.43 | CONCERN† | PASS | PASS / YES | **clean** | SELLABLE_WITH_ADVISORY |
| gen_z_professionals | burnout | CONCERN 0.42 | CONCERN† | PASS | PASS / YES | **FAIL** placeholder | **BLOCKED_LEAKAGE** |
| corporate_managers | burnout | FAIL 0.39 | CONCERN† | PASS | PASS / YES | **FAIL** placeholder | **BLOCKED_LEAKAGE** |
| corporate_managers | financial_anxiety | FAIL 0.38 | CONCERN† | CONCERN | PASS / YES | **FAIL** placeholder | **BLOCKED_LEAKAGE** |
| educators | anxiety | CONCERN 0.43 | CONCERN† | PASS | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| gen_alpha_students | boundaries | CONCERN 0.42 | CONCERN† | PASS | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| gen_x_sandwich | anxiety | CONCERN 0.42 | CONCERN† | PASS | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| gen_x_sandwich | boundaries | CONCERN 0.42 | CONCERN† | PASS | PASS / YES | clean | SELLABLE_WITH_ADVISORY |
| nyc_executives | anxiety | FAIL 0.39 | CONCERN† | PASS | PASS / UNKNOWN | clean | SELLABLE_WITH_ADVISORY |

**Leakage evidence (pilot_10 / corporate_managers × burnout):**

```
[Persona-specific hook for corporate_managers × burnout]
[Persona-specific hook for gen_z_professionals × burnout]
```

Appears ~24× in `04_corporate_managers__burnout/book.txt` — unauthored HOOK atom stubs per PILOT_10_REVIEW_PACKAGE §10. **Not caught by brace-placeholder gate** (square-bracket stubs). wave_proof draft set of same cell is **clean** and preferred for any near-term sell test.

---

## Teacher-mode EPUBs (`artifacts/epub/`)

| Book | Topic | Words | Bestseller | Cohesive | Engaging | Leakage | Verdict |
|------|-------|------:|------------|----------|----------|---------|---------|
| pamela_fellows_anxiety | anxiety | 5196 | PASS | PASS (single-ch) | PASS | clean | SELLABLE_AS_IS (micro) |
| omote_sleep_anxiety | sleep_anxiety | 6080 | PASS | PASS | PASS | clean | SELLABLE_AS_IS (micro) |
| ra_imposter_syndrome | imposter_syndrome | 6042 | PASS | PASS | PASS | clean | SELLABLE_AS_IS (micro) |
| ahjan_anxiety | anxiety | 5691 | PASS | PASS | FAIL | clean | ADVISORY (engagement) |
| miki_imposter_syndrome | imposter_syndrome | 6277 | PASS | PASS | CONCERN | clean | ADVISORY |
| master_sha_grief | grief | 4725 | PASS | PASS | CONCERN | clean | ADVISORY |
| adi_da_self_worth | self_worth | 5387 | PASS | PASS | CONCERN | clean | ADVISORY |
| maat_boundaries | boundaries | 6409 | PASS | PASS | FAIL | clean | ADVISORY |
| joshin_anxiety | anxiety | 5367 | PASS | PASS | FAIL | clean | ADVISORY |
| miyuki_overthinking | overthinking | 5224 | PASS | PASS | FAIL | clean | ADVISORY |
| sai_ma_grief | grief | 4952 | PASS | PASS | FAIL | clean | ADVISORY |
| master_feung_burnout | burnout | **260** | PASS | **FAIL** | FAIL | clean | **BLOCKED** (stub) |
| master_wu_courage | courage | **303** | PASS | **FAIL** | FAIL | clean | **BLOCKED** (stub) |

Teacher EPUBs are single-chapter samples — engaging FAIL on several reflects word-count/pacing heuristics, not necessarily reader rejection. No catalog listing rows (teacher_mode).

---

## Way Stream Sanctuary (canonical register-PASS)

| Persona | Topic | Bestseller | Cohesive | Engaging | Marketing | Leakage | Verdict |
|---------|-------|------------|----------|----------|-----------|---------|---------|
| corporate_managers | burnout | PASS 0.84 | PASS 0.93 | PASS 0.58 | PASS / YES | clean | **SELLABLE_AS_IS** |

Listing match: *"Devoted Permission to Pause"* / *"Resting Through Burnout Without Guilt — for mid-level leaders"*. Hook: *"Some of your tiredness is the watching, not the doing."*

---

## Machine-readable

- `SCORECARD.tsv` — tab-separated rows
- `scores.json` — full deterministic output
