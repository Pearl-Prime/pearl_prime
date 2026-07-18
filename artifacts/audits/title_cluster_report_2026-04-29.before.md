# Title Cluster + De-duplication Report

**Issue:** [#786 — B2 title cannibalization](https://github.com/Ahjan108/phoenix_omega_v4.8/issues/786)
**Generated:** by `scripts/catalog/cluster_and_dedupe_titles.py`

## Headline metrics

| Metric | Value | Threshold | Pass |
|---|---:|---:|:---:|
| Ready en_US rows | 1,478 | — | — |
| Ready en_US rows w/ title | 1,277 | — | — |
| Ready en_US blank-title | 201 | 0 | ❌ |
| Distinct titles | 42 | — | — |
| Distinct (title, subtitle) pairs | 45 | — | — |
| **Avg ready / distinct title** | **30.40** | **≤ 3.0** | ❌ |
| Avg ready / distinct (title,subtitle) | 28.38 | — | — |
| **Max exact (title,subtitle) repeat** | **47** | **≤ 3** | ❌ |
| Max title-only repeat | 47 | (informational) | — |
| Semantic cluster count | 40 | — | — |
| **Max semantic cluster size** | **87** | **≤ 6** | ❌ |
| Exact pairs over 3 (count) | 45 | 0 | ❌ |
| Semantic clusters over 6 (count) | 40 | 0 | ❌ |

### Verdict: **❌ B2 FAIL**

## Top exact (title, subtitle) duplicates

| n | title | subtitle |
|---:|---|---|
| 47 | Before You Break | Escaping Burnout and Rebuilding Your Energy |
| 46 | You Were Always Enough | Rebuilding Self-Esteem and Reclaiming Your Worth |
| 43 | Safe Enough | How to Calm Anxiety and Reclaim Your Nervous System |
| 42 | The Alarm Is Lying | A Nervous System Guide to Anxiety Recovery |
| 41 | Still Here Without You | Finding Your Way Through Grief and Heartbreak |
| 41 | Worthy Without Proof | How to Build Unshakable Self Worth and Confidence |
| 40 | Running on Fumes | A Recovery Guide for Burnout and Work Exhaustion |
| 39 | The No That Saved Me | A Practical Guide to Setting Boundaries and Finding Peace |
| 38 | The Collapse You Earned | Burnout Recovery for People Who Can't Stop |
| 37 | The Mirror Lied | A Self-Love Guide to Healing Low Self-Esteem |

## Top semantic clusters (over 6 = violation)

| n | cluster |
|---:|---|
| 87 ❌ | `burnout::pre_collapse_warning` |
| 70 ❌ | `anxiety::false_alarm_system` |
| 56 ❌ | `sleep_anxiety::permission_to_rest` |
| 54 ❌ | `compassion_fatigue::caring_until_empty` |
| 49 ❌ | `social_anxiety::room_not_watching` |
| 46 ❌ | `self_worth::always_were` |
| 43 ❌ | `anxiety::safety_nervous_system` |
| 41 ❌ | `grief::still_present` |
| 41 ❌ | `self_worth::without_proof` |
| 39 ❌ | `boundaries::saving_no` |

## Worst (brand, topic) collisions

| n | brand | topic |
|---:|---|---|
| 12 | stillness_press | anxiety |
| 12 | stillness_press | boundaries |
| 12 | stillness_press | courage |
| 12 | stillness_press | grief |
| 12 | stillness_press | imposter_syndrome |
| 12 | stillness_press | overthinking |
| 12 | stillness_press | self_worth |
| 12 | stillness_press | sleep_anxiety |
| 12 | stillness_press | social_anxiety |
| 12 | relational_calm | anxiety |

## Blank-title topic distribution

| topic | n blank |
|---|---:|
| mindfulness | 115 |
| adhd_focus | 86 |
