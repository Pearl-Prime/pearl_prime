# en_US Catalog Bestseller Audit — 2026-05-13

## TL;DR

- **200 BookSpecs assembled** from the canonical planner (en_US catalog ceiling).
- **26 books (13.0%) rendered to `book.txt`** and produced a bestseller (ONTGP) score; the remaining **174 (87.0%) failed at production quality gates pre-render**.
- **Dominant failure mode: `scene_anchor_density` (168 books, 84.0% of catalog)** — single largest blocker to bestseller-readiness today.
- Of the 26 rendered books: **26 PASS / 0 WARN / 0 FAIL** (bestseller verdict thresholds: ONTGP ≥ 0.40 PASS, ≥ 0.20 WARN).
- Among rendered books, ONTGP: mean **0.579**, median 0.587, range [0.406, 0.678]. Distribution is tight — every rendered book clears the PASS threshold.
- **Bottom line:** the bestseller-grade gap in the en_US catalog is NOT score quality — the rendered books all pass. The gap is **pipeline yield**. Until scene_anchor_density failures are addressed, ~87% of planner-allocated BookSpecs never reach the bestseller scoring stage.

---

**Total books assembled:** 200
**Books with ONTGP score:** 26
**Books missing score (assembly failed pre-render):** 174

**Score stats:** mean=0.579  median=0.587  min=0.406  max=0.678  stdev=0.061

## Verdict distribution

| Verdict | Count | % of total |
|---|---:|---:|
| PASS | 26 | 13.0% |
| WARN | 0 | 0.0% |
| FAIL | 0 | 0.0% |
| MISSING | 174 | 87.0% |

## Failure mode distribution (assembly gate failures)

| Failure mode | Count | % of total |
|---|---:|---:|
| scene_anchor_density | 168 | 84.0% |
| RENDERED | 26 | 13.0% |
| UNCATEGORIZED | 6 | 3.0% |

## ONTGP score histogram

| Bucket | Count | Bar |
|---|---:|---|
| 0.0-0.2 FAIL | 0 | `` |
| 0.2-0.3 | 0 | `` |
| 0.3-0.4 | 0 | `` |
| 0.4-0.5 PASS | 2 | `###` |
| 0.5-0.7 | 24 | `########################################` |
| 0.7-0.9 | 0 | `` |
| 0.9-1.0 | 0 | `` |

## Top 10 highest-scoring books

| Rank | book_id | topic | persona | teacher | ONTGP |
|---:|---|---|---|---|---:|
| 1 | book_0169_anxiety_entrepreneurs | anxiety | entrepreneurs | master_feung | 0.6778 |
| 2 | book_0122_boundaries_gen_alpha_students | boundaries | gen_alpha_students | ra | 0.6750 |
| 3 | book_0157_boundaries_tech_finance_burnout | boundaries | tech_finance_burnout | junko | 0.6610 |
| 4 | book_0142_sleep_anxiety_gen_alpha_students | sleep_anxiety | gen_alpha_students | joshin | 0.6332 |
| 5 | book_0194_boundaries_healthcare_rns | boundaries | healthcare_rns | joshin | 0.6264 |
| 6 | book_0140_overthinking_gen_z_professionals | overthinking | gen_z_professionals | ra | 0.6255 |
| 7 | book_0082_overthinking_first_responders | overthinking | first_responders | junko | 0.6157 |
| 8 | book_0087_compassion_fatigue_gen_x_sandwich | compassion_fatigue | gen_x_sandwich | junko | 0.6080 |
| 9 | book_0159_compassion_fatigue_working_parents | compassion_fatigue | working_parents | omote | 0.6075 |
| 10 | book_0133_anxiety_first_responders | anxiety | first_responders | master_wu | 0.5942 |

## Bottom 10 lowest-scoring books

| Rank | book_id | topic | persona | teacher | ONTGP |
|---:|---|---|---|---|---:|
| 1 | book_0000_anxiety_millennial_women_professionals | anxiety | millennial_women_professionals | ahjan | 0.4062 |
| 2 | book_0156_anxiety_millennial_women_professionals | anxiety | millennial_women_professionals | miki | 0.4311 |
| 3 | book_0099_burnout_corporate_managers | burnout | corporate_managers | master_feung | 0.5157 |
| 4 | book_0145_burnout_millennial_women_professionals | burnout | millennial_women_professionals | omote | 0.5315 |
| 5 | book_0059_sleep_anxiety_healthcare_rns | sleep_anxiety | healthcare_rns | ahjan | 0.5479 |
| 6 | book_0188_overthinking_tech_finance_burnout | overthinking | tech_finance_burnout | miki | 0.5513 |
| 7 | book_0094_sleep_anxiety_millennial_women_professionals | sleep_anxiety | millennial_women_professionals | master_wu | 0.5550 |
| 8 | book_0128_overthinking_gen_x_sandwich | overthinking | gen_x_sandwich | ahjan | 0.5587 |
| 9 | book_0116_overthinking_entrepreneurs | overthinking | entrepreneurs | joshin | 0.5634 |
| 10 | book_0002_burnout_entrepreneurs | burnout | entrepreneurs | master_feung | 0.5635 |

## Average score by topic

| Topic | n | avg ONTGP |
|---|---:|---:|
| burnout | 4 | 0.5486 |
| anxiety | 7 | 0.5490 |
| sleep_anxiety | 4 | 0.5816 |
| overthinking | 5 | 0.5829 |
| compassion_fatigue | 2 | 0.6078 |
| boundaries | 4 | 0.6384 |

## Average score by persona

| Persona | n | avg ONTGP |
|---|---:|---:|
| millennial_women_professionals | 4 | 0.4809 |
| corporate_managers | 2 | 0.5436 |
| gen_x_sandwich | 4 | 0.5855 |
| healthcare_rns | 2 | 0.5872 |
| working_parents | 2 | 0.5893 |
| tech_finance_burnout | 3 | 0.6009 |
| entrepreneurs | 3 | 0.6016 |
| first_responders | 2 | 0.6049 |
| gen_z_professionals | 1 | 0.6255 |
| gen_alpha_students | 3 | 0.6331 |

## Average score by teacher

| Teacher | n | avg ONTGP |
|---|---:|---:|
| miki | 2 | 0.4912 |
| ahjan | 4 | 0.5210 |
| master_wu | 2 | 0.5746 |
| omote | 3 | 0.5765 |
| master_feung | 3 | 0.5857 |
| joshin | 5 | 0.5996 |
| junko | 4 | 0.6190 |
| ra | 3 | 0.6240 |

## Recommendations: weak clusters (avg < 0.40, n ≥ 3)

_No weak clusters with sufficient sample size._

### Suggested remediation tracks

No cluster-scale ONTGP gaps identified among **rendered** books; all 26 rendered books clear PASS.

### Pipeline yield recommendations (the actual bottleneck)

The bestseller score is moot for 87% of the catalog because those books fail at production quality gates before scoring. Prioritized remediation:

1. **`scene_anchor_density` (168 books, 84.0%)** — single largest source of yield loss. This gate caps repeated >3-word phrases at 2 per book; investigate spine-mode prose duplication, then either (a) loosen cap (after impact analysis), (b) post-render dedup pass, or (c) source-atom variation backfill.
2. **`UNCATEGORIZED` (6 books, 3.0%)** — investigate root cause and decide whether to fix upstream or relax gate.

Re-running this audit after each remediation will quantify yield recovery.

