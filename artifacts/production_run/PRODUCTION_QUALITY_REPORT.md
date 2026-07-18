# Production Quality Report
*Generated: 2026-04-10 | Source: Deep Catalog Scoring (scripts/analysis/score_catalog_deep.py)*
*Full data: artifacts/analysis/catalog_deep_scores.json*

## Baseline (pre-enhancement)

| Metric | Score |
|--------|-------|
| Composite mean (45 books) | 0.4886 |
| Strongest topic | grief (0.6043) |
| Weakest topic | compassion_fatigue (0.4397) |
| Books above 0.60 | 3 of 45 (6.7%) |
| Books above 0.75 | 0 of 45 (0%) |

## Prior Rigorous Eval Baseline

From `artifacts/ei_v2/eval_rigorous_report.json` (3 books, gen_z_professionals):
- Overall composite: 0.5395
- Therapeutic value: 0.6322
- Emotional coherence: 0.9444
- Engagement: 0.2365
- Marketability: 0.2433
- Safety compliance: 0.9964

## Key Findings

See `artifacts/analysis/CATALOG_ENHANCEMENT_ROADMAP.md` for full analysis.

Top systemic weaknesses (heuristic-reported, some require calibration fix):
1. listen_experience (mean=0.016) — calibration issue, Phoenix short-sentence style
2. somatic_precision (mean=0.021) — calibration issue, density formula
3. content_uniqueness (mean=0.031) — calibration issue, Jaccard too harsh
4. exercise_quality (mean=0.182) — REAL content issue: no body/time anchors
5. opening_hook_strength (mean=0.270) — REAL content issue: no pattern-naming structure

## Enhancement Target

After calibration + P0 content fixes: 0.65-0.70 composite mean
After full enhancement roadmap: 0.75+ composite mean
