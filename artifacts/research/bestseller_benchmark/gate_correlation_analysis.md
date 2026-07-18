# Gate correlation analysis — internal probe (N = 11)

## Data definition

- **N = 11** manuscript slices: `internal_deep6h_ch01` … `internal_deep6h_ch10` plus `_canary_standard_book_ch1`.  
- **Pearl_Editor aggregate** is the 9-dimension mean documented in `pearl_editor_markup.md`.  
- **Commercial Amazon ranks** are **not** used here: the scored text is **not** title-identified to the ten commercial targets in `book_corpus.yaml`. Any Spearman vs retailer rank would be **invalid** until legal samples are paired row-wise.

**Small-sample honesty:** With N = 11, two-sided p-values below ~0.05 should be treated as **hypothesis-generating**, not proof of production-world correlation.

## Numeric features extracted from `scores/*_scores.json`

| Gate / signal | Field used |
|---------------|------------|
| chapter_flow | `chapter_flow.score` (0–100 int) |
| bestseller_craft (ONTGP) | `bestseller_craft.ontgp_composite` (mean of move scores) |
| editorial | `editorial.total_score` (integer rubric total) |
| memorable_lines | PASS = 1.0 else 0.0 (binary helper; all PASS in this run) |
| book_quality_gate | PASS = 1.0 else 0.0 |
| museum block | `regression_museum.summary.blocked` as 1.0 / 0.0 |
| ei_v2 (proxy) | `ei_v2.tts_readability.composite` and `ei_v2.safety.risk_score` |

## Spearman rank correlations (scipy.stats.spearmanr)

### Top positive correlations

1. **editorial_total vs ONTGP composite — ρ ≈ 0.76, p ≈ 0.006**  
   Chapters the S13-ish editorial rubric likes also tend to score higher on ONTGP-style craft heuristics. This is **face-valid**: both reward structure and move coverage.

2. **Pearl_Editor aggregate vs chapter_flow.score — ρ ≈ 0.72, p ≈ 0.012**  
   Human-graded readability / hook quality aligns with flow-gate numeric score on this corpus.

3. **Pearl_Editor aggregate vs book_quality PASS binary — ρ ≈ 0.66, p ≈ 0.027**  
   Book-quality PASS correlates with higher Pearl marks here — mostly because repeated-phrase / flow failures track perceived draftiness.

### Top negative / weak correlations (still informative)

- **Pearl_Editor vs ONTGP composite — ρ ≈ 0.42, p ≈ 0.20 (not significant at α = 0.05)**  
  ONTGP can look “good” while Pearl still marks teacherly or repetitive passages — suggests **partial decoupling** between craft-zone math and reader-quality judgment.

- **chapter_flow.score vs ONTGP — ρ ≈ 0.10, p ≈ 0.77**  
  Nearly independent within this slice — flow gate is not a proxy for ONTGP.

## Per-gate verdict (for this branch, deterministic stack)

| Gate / bundle | Verdict | Notes |
|---------------|---------|-------|
| chapter_flow | **KEEP_AS_IS (monitor)** | Discriminates ch03/ch09/ch10 FAIL vs others PASS in this probe. |
| bestseller_craft | **NEEDS_MORE_DATA** | Needs title-identified commercial chapters to know if thresholds are miscalibrated vs market. |
| editorial (S13 generator) | **KEEP_AS_IS** | Behaves coherently with Pearl marks and ONTGP in this probe. |
| memorable_lines | **NEEDS_MORE_DATA** | All PASS here; no variance to validate failure usefulness. |
| transformation_arc | **NEEDS_MORE_DATA** | Single-chapter artifact always stresses “ending_weak” semantics — do not interpret literally in this benchmark shape. |
| book_quality_gate | **RECALIBRATE (threshold / policy review)** | FAIL dominates even on relatively strong internal chapters; repeated-phrase detector interacts badly with intentional anaphora in long drafts. |
| ei_v2 proxy | **KEEP_AS_IS** | Safety + TTS readability are informative and cheap; not used as merge gate here. |
| regression_museum | **RECALIBRATE** | **100% block rate** on all eleven slices — see `museum_calibration.md`. |

## Bestseller-passing-rate snapshot (internal probe)

If we naïvely treat **museum blocked == FAIL** for “shipping gate realism,” then **11 / 11** “books” fail — which would be an absurd conclusion for production deployment. This is the core calibration signal: **the museum is currently far too eager for long Phoenix chapters** until patterns are tightened or demoted.

## Self-consistency check

Pearl_Editor aggregates were scored **before** computing correlations; no iterative p-hacking beyond the stated pairs.
