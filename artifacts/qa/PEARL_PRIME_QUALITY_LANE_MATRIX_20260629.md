# Pearl Prime — Duration × Topic Bestseller + Cohesion Matrix

Generated: 20260628T214202Z (local, production profile, persona `corporate_managers`)

## Step 1 — Matrix enumeration

### Durations (runtime_formats with word_range)

| format | word_range | chapter_count_default |
|---|---:|---:|
| micro_book_15 | 2500–4500 | 5 |
| micro_book_20 | 3000–5500 | 6 |
| compact_book_5ch_15min | 3000–4500 | 5 |
| compact_book_5ch_20min | 4000–5500 | 5 |
| short_book_30 | 4500–7500 | 8 |
| compact_book_8ch_30min | 5500–7500 | 8 |
| one_hour_book | 8000–10000 | 8 |
| standard_book_60min | 9000–12000 | 10 |
| standard_book | 9000–22000 | 10 |
| extended_book_2h | 17000–25000 | 14 |
| deep_book_4h | 20000–40000 | 16 |
| deep_book_6h | 50000–72000 | 20 |

### Topics (17 canonical)

`adhd_focus`, `anxiety`, `boundaries`, `burnout`, `compassion_fatigue`, `courage`, `depression`, `financial_anxiety`, `financial_stress`, `grief`, `imposter_syndrome`, `mindfulness`, `overthinking`, `self_worth`, `sleep_anxiety`, `social_anxiety`, `somatic_healing`

Arc coverage for `corporate_managers`: 15/17 topics

## Step 2 — One book per duration (QA EPUBs)

| duration | topic | words | chapter_flow | register | EI V2 | craft | book_pass | COHESION | VERDICT |
|---|---|---:|---|---|---|---|---|---|---|
| micro_book_15 | anxiety | 3449 | PASS | PASS | PASS (0.59) | PASS (0.47) | PASS | PASS | PASS |
| micro_book_20 | boundaries | 4100 | PASS | PASS | PASS (0.61) | PASS (0.51) | PASS | PASS | PASS |
| compact_book_5ch_15min | burnout | 3006 | PASS | PASS | PASS (0.61) | PASS (0.49) | PASS | PASS | PASS |
| compact_book_5ch_20min | compassion_fatigue | 4007 | PASS | PASS | PASS (0.62) | PASS (0.47) | PASS | PASS | PASS |
| short_book_30 | courage | 5816 | PASS | PASS | PASS (0.59) | PASS (0.48) | PASS | PASS | PASS |
| compact_book_8ch_30min | depression | 5507 | PASS | PASS | PASS (0.61) | PASS (0.48) | PASS | PASS | PASS |
| one_hour_book | financial_anxiety | 8004 | PASS | PASS | PASS (0.59) | WARN (0.38) | PASS | PASS | ADVISORY |
| standard_book_60min | financial_stress | 9024 | PASS | PASS | PASS (0.60) | PASS (0.44) | PASS | PASS | PASS |
| standard_book | grief | 15206 | PASS | PASS | PASS (0.63) | PASS (0.48) | PASS | PASS | PASS |
| extended_book_2h | imposter_syndrome | 17211 | PASS | PASS | PASS (0.64) | PASS (0.50) | PASS | PASS | PASS |
| deep_book_4h | overthinking | 20008 | PASS | PASS | PASS (0.62) | PASS (0.50) | PASS | PASS | PASS |
| deep_book_6h | self_worth | — | MISSING | MISSING | MISSING | MISSING | MISSING | MISSING | INCOMPLETE |

## Step 4 — Topic sweep at standard_book_60min

| duration | topic | words | chapter_flow | register | EI V2 | craft | book_pass | COHESION | VERDICT |
|---|---|---:|---|---|---|---|---|---|---|
| standard_book_60min | adhd_focus | — | NO_ARC | NO_ARC | NO_ARC | NO_ARC | NO_ARC | NO_ARC | NO_ARC |
| standard_book_60min | anxiety | 9631 | PASS | PASS | PASS (0.63) | PASS (0.50) | PASS | PASS | PASS |
| standard_book_60min | boundaries | 9013 | PASS | PASS | PASS (0.61) | PASS (0.51) | PASS | PASS | PASS |
| standard_book_60min | burnout | 9016 | PASS | PASS | PASS (0.58) | PASS (0.51) | PASS | PASS | PASS |
| standard_book_60min | compassion_fatigue | 9012 | PASS | PASS | PASS (0.62) | PASS (0.47) | PASS | PASS | PASS |
| standard_book_60min | courage | 9004 | PASS | PASS | PASS (0.61) | PASS (0.48) | PASS | PASS | PASS |
| standard_book_60min | depression | 9028 | PASS | PASS | PASS (0.60) | PASS (0.46) | PASS | PASS | PASS |
| standard_book_60min | financial_anxiety | 9003 | PASS | PASS | PASS (0.59) | WARN (0.39) | PASS | PASS | ADVISORY |
| standard_book_60min | financial_stress | 9024 | PASS | PASS | PASS (0.60) | PASS (0.44) | PASS | PASS | PASS |
| standard_book_60min | grief | 9419 | PASS | PASS | PASS (0.60) | PASS (0.48) | PASS | PASS | PASS |
| standard_book_60min | imposter_syndrome | 9090 | PASS | PASS | PASS (0.62) | PASS (0.50) | PASS | PASS | PASS |
| standard_book_60min | mindfulness | — | NO_ARC | NO_ARC | NO_ARC | NO_ARC | NO_ARC | NO_ARC | NO_ARC |
| standard_book_60min | overthinking | 9009 | PASS | PASS | PASS (0.60) | PASS (0.45) | PASS | PASS | PASS |
| standard_book_60min | self_worth | 9279 | PASS | PASS | PASS (0.62) | PASS (0.50) | PASS | PASS | PASS |
| standard_book_60min | sleep_anxiety | 9014 | PASS | PASS | PASS (0.58) | PASS (0.43) | PASS | PASS | PASS |
| standard_book_60min | social_anxiety | 9020 | PASS | PASS | PASS (0.58) | PASS (0.45) | PASS | PASS | PASS |
| standard_book_60min | somatic_healing | 9025 | PASS | PASS | PASS (0.61) | PASS (0.48) | PASS | PASS | PASS |

## Bottom line

**24/29 cells meet the full production bestseller + cohesive bar (VERDICT=PASS).**

This is expected to be **below 100%** while assembly-P0 (chapter_flow, register F1/F6, ARC_POSITION / BookStructurePlan) and cohesion lanes (F13 dwell-integration, adjacency atom selector) remain open per OPD-20260627-001.

### Systemic failure tally


### Cohesion detail (cells with issues)

- **standard_book_60min / adhd_focus**: NO_ARC — no corporate_managers master arc
- **standard_book_60min / mindfulness**: NO_ARC — no corporate_managers master arc
