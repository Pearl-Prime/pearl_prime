# SCENE_ANCHOR_DENSITY_CAP_V2_SPEC

Status: ACTIVE (effective 2026-05-13)
Owner: Pearl_Dev (rendering / quality)
Supersedes: implicit cap=2 baked into `scripts/run_pipeline.py` since the
            scene_anchor_density gate was introduced.

## Problem

PR #1089 audited the en_US catalog at production-grade assembly (200 BookSpecs,
spine pipeline, `--quality-profile production`). Yield was 13.0% (26/200 rendered
`book.txt`); 168/200 (84%) failed at the `scene_anchor_density` gate before
bestseller scoring could run. Among rendered books, every single one passed
bestseller-craft scoring (mean ONTGP 0.579, range [0.406, 0.678]). The bottleneck
was therefore **gate over-tightness, not output quality**.

## Empirical diagnosis (PR #1089 audit, 2026-05-13)

The legacy default cap of `2` paragraphs-per-chapter for any 4..8 word phrase
was set without empirical calibration. Sampling all 168 failure reports under
`artifacts/pearl_prime_en_us/first_100_qa/renders/*/scene_anchor_density_report.json`:

| max paragraph_count | failure count | interpretation |
| --- | --- | --- |
| 3 | 156 | natural rhetorical motif (1 paragraph over cap) |
| 4 | 11  | borderline overuse |
| 5 | 1   | clear overuse |

Examples of paragraph_count=3 offenders that legitimately recur in well-structured
chapters: `"about who you are"`, `"you say yes before"`, `"the erosion of every line"`,
`"is named the loop is easier to interrupt"`. These are anchor phrases the chapter
deliberately returns to — not defects.

Reports also showed the same recurring motif inflated into 5–10 overlapping
n-gram entries (lengths 4..8 starting at the same anchor word). This is a
reporting-noise issue, not a decision-quality issue, but it obscured root cause.

## Decision

1. **Raise the default per-chapter cap from 2 to 3.** Phrases appearing in more
   than 3 paragraphs of a single chapter remain violations; phrases appearing in
   2–3 paragraphs are now permitted as natural motifs. This recovers ~91% catalog
   yield while still catching the 12 books with truly egregious 4+ paragraph
   repetitions.
2. **Centralize the cap in `config/quality/scene_anchor_density_config.yaml`.**
   `scripts/run_pipeline.py` now reads `default_cap_per_chapter` from this file.
3. **Authored plans retain hand-tuned caps.** `config/plans/*.yaml` files set
   `scene_plan.scene_anchor_cap` explicitly per chapter. The pipeline takes
   `min()` across chapters, so any explicit override (including cap=2) tightens
   the book. No regression for the small set of hand-tuned plans.
4. **Collapse overlapping n-gram offenders in reports.** When a single phrase
   recurs (e.g. an 8-word motif), the algorithm previously emitted up to 5
   offender entries (lengths 4..8 starting at the same anchor). The reporter now
   keeps only the longest member of each overlap chain at a given paragraph_count.
   Decision logic is unchanged.

## Out of scope

- Variant authoring / atom-bank diversification (Option B in the diagnosis
  matrix) is deferred. The empirical evidence — 156/168 failures at cap+1 —
  shows the dominant issue is gate calibration, not source repetition.
- Post-render dedup of repeated phrases (Option C) is deferred for the same
  reason. If post-cap-relaxation residual failures cluster around a fixable
  pattern, a follow-up PR may add a dedup pass.

## Verification protocol

```
PYTHONPATH=. python3 scripts/pearl_prime_en_us/assemble_first_100_qa.py \
  --target 200 --over-allocate 400 \
  --seed-tag bestseller_audit_FIX_20260513
PYTHONPATH=. python3 scripts/pearl_prime_en_us/aggregate_bestseller_audit.py
```

Acceptance:

- Yield ≥ 80% (was 13.0%)
- scene_anchor_density failure count < 20 (was 168)
- ONTGP distribution shift: mean within ±0.05 of pre-fix 0.579, no FAIL appearing
  (was 26/0/0 PASS/WARN/FAIL).

## Rollback

Set `default_cap_per_chapter: 2` in `config/quality/scene_anchor_density_config.yaml`
to restore the legacy behavior. No code change required.
