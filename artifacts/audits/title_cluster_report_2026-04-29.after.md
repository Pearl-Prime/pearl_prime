# Title Cluster + De-duplication Report

**Issue:** [#786 — B2 title cannibalization](https://github.com/Ahjan108/phoenix_omega_v4.8/issues/786)
**Generated:** by `scripts/catalog/cluster_and_dedupe_titles.py`

## Headline metrics

| Metric | Value | Threshold | Pass |
|---|---:|---:|:---:|
| Ready en_US rows | 1,478 | — | — |
| Ready en_US rows w/ title | 1,478 | — | — |
| Ready en_US blank-title | 0 | 0 | ✅ |
| Distinct titles | 698 | — | — |
| Distinct (title, subtitle) pairs | 1,478 | — | — |
| **Avg ready / distinct title** | **2.12** | **≤ 3.0** | ✅ |
| Avg ready / distinct (title,subtitle) | 1.00 | — | — |
| **Max exact (title,subtitle) repeat** | **1** | **≤ 3** | ✅ |
| Max title-only repeat | 8 | (informational) | — |
| Semantic cluster count | 698 | — | — |
| **Max semantic cluster size** | **6** | **≤ 6** | ✅ |
| Exact pairs over 3 (count) | 0 | 0 | ✅ |
| Semantic clusters over 6 (count) | 0 | 0 | ✅ |

### Verdict: **✅ B2 PASS**

## Delta vs baseline

| Metric | Before | After | Change |
|---|---:|---:|---:|
| ready_total | 1,478 | 1,478 | +0 |
| ready_titled | 1,277 | 1,478 | ++201 |
| ready_blank_title | 201 | 0 | -201 |
| distinct_titles | 42 | 698 | ++656 |
| distinct_pairs | 45 | 1,478 | ++1,433 |
| exact_pair_max | 47 | 1 | -46 |
| title_only_max | 47 | 8 | -39 |
| semantic_cluster_count | 40 | 698 | ++658 |
| semantic_cluster_max | 87 | 6 | -81 |
| avg_ready_per_distinct_title | 30.40 | 2.12 | -28.29 |

## Top exact (title, subtitle) duplicates

| n | title | subtitle |
|---:|---|---|
| 1 | Quiet From Scatter to Anchor | An Adhd Focus Companion for the Easily Distracted — for mid-level leaders |
| 1 | Quiet Brain on Your Side | A Adhd Focus Practice for Neurodivergent Adults — for millennial women professio |
| 1 | Quiet Permission to Drift | Working With Your ADHD Brain Instead of Against It — for tech and finance pros |
| 1 | Quiet Brain on Your Side | A Adhd Focus Practice for Neurodivergent Adults — for Gen Z professionals |
| 1 | Quiet The Loop That Frees You | Adhd Focus for Brains That Won't Sit Still — for frontline workers |
| 1 | Quiet Focus Without Force | A Soft Adhd Focus Guide for Restless Minds — for teachers and educators |
| 1 | Quiet The Loop That Frees You | Adhd Focus for Brains That Won't Sit Still — for working parents |
| 1 | Quiet Brain on Your Side | A Adhd Focus Practice for Neurodivergent Adults — for founders |
| 1 | Quiet Brain on Your Side | A Adhd Focus Practice for Neurodivergent Adults — for Gen Z students |
| 1 | Quiet Safe Enough | How to Calm Anxiety and Reclaim Your Nervous System — for mid-level leaders |

## Top semantic clusters (over 6 = violation)

| n | cluster |
|---:|---|
| 6 | `burnout::quiet::pre_collapse_warning` |
| 6 | `financial_stress::quiet::money_no_panic` |
| 6 | `anxiety::whole::safety_nervous_system` |
| 6 | `self_worth::together::without_proof` |
| 6 | `burnout::restful::long_way_back` |
| 6 | `mindfulness::bright::quiet_that_stays` |
| 6 | `mindfulness::devoted::land_in_moment` |
| 5 | `anxiety::quiet::safety_nervous_system` |
| 5 | `boundaries::quiet::stop_pouring` |
| 5 | `courage::quiet::fear_built_you` |

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

_No blank-title rows. ✅_
