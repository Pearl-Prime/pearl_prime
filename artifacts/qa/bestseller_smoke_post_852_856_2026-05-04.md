# Bestseller Smoke Verification — post #852 + #856

**Date:** 2026-05-04
**Branch:** `agent/bestseller-smoke-verification-20260504`
**Base:** `origin/main` at `37edc4375c` (PR #856 squash) over `dcc5fad25a` (PR #852 squash)
**Iteration cap:** 0 (verification only — no production code touched)
**Outcome:** **REJECT**

## What this PR is

A single-shot smoke test against `production` quality profile using the largest
compact runtime format (`compact_book_8ch_30min`) for the `gen_z_professionals × anxiety`
matrix. The goal: prove that PR #852 (TEACHER_DOCTRINE atoms + chapter-flow atoms +
compact-format spec) and PR #856 (compact format declarations + per-section budget
+ runtime_policies) jointly close the bestseller-pass loop for the first compact
format.

This artifact PR does not change any production code. It records the verification
result and scopes the next-cycle work.

## Win-condition vs. observed

| Criterion | Target | Observed |
|---|---|---|
| Pipeline reaches `prose_render` | yes | **no** — failed at `quality_gate` (scene_anchor_density) |
| `book.txt` produced | yes | no |
| `word_count` in `[5500, 7500]` | yes | n/a (no render) |
| `chapter_flow` 0 FAIL | yes | n/a (no render) |
| `EI v2` composite ≥ 0.55 | yes | n/a (no render) |
| `memorable_lines` ≥ 6/8 chapters | yes | n/a (no render) |
| `bestseller_composite` Pass / non-blocking Hold | yes | n/a (no render) |

Pipeline exit code: `1`. Stage reached: planning + content selection (no `prose_render`).

## Failure modes (3, all upstream of bestseller-pass goal)

### 1. Auto-plan did not honor `chapter_count_default: 8`

`compact_book_8ch_30min` is declared in `config/format_selection/format_registry.yaml`
with `chapter_count_default: 8` and `word_range: [5500, 7500]` (PR #856).

But the smoke run produced a 13-chapter book (chapter ids `0`-`12` referenced in
the run log via `EXERCISE FALLBACK` entries and `Chapter contract: chapter 12`).

**Root cause:** the auto-plan generator at
[phoenix_v4/planning/book_structure_plan.py:18](phoenix_v4/planning/book_structure_plan.py:18)
holds a hardcoded `FORMAT_CHAPTER_COUNTS: dict[str, int]` that lists every legacy
runtime (`micro_book_15`, `pocket_guide`, `standard_book`, `deep_book_6h`, …) but
**none of the three new compact formats**:

```python
FORMAT_CHAPTER_COUNTS: dict[str, int] = {
    "micro_book_15": 5,
    "micro_book_20": 6,
    ...
    "deep_book_6h": 20,
}
# compact_book_5ch_15min, compact_book_5ch_20min,
# compact_book_8ch_30min — all missing.
```

At [phoenix_v4/planning/book_structure_plan.py:496](phoenix_v4/planning/book_structure_plan.py:496):

```python
n_chapters = chapter_count or FORMAT_CHAPTER_COUNTS.get(runtime_format, 10)
```

For an unknown format the fallback is `10`. The actual observed count of 13
suggests downstream logic (arc-driven? `assign_bestseller_structures` post-pad?)
adds further chapters. Either way, the format-registry declaration is not
authoritative for the auto-plan path.

**This is a wiring gap in #856** — the format was added to the registry but not
to the auto-plan generator's lookup table. Single-source-of-truth was not
reached.

### 2. EXERCISE coverage gap (every chapter fell back to `library_34`)

Every chapter in the auto-plan logged:

```
EXERCISE FALLBACK: Using library_34 for chapter <N> topic anxiety persona gen_z_professionals.
No registry or teacher exercise was available for this slot —
add EXERCISE coverage upstream if this is unexpected.
```

PR #852 backfilled `TEACHER_DOCTRINE` atoms and chapter-flow atoms. It did not
backfill `EXERCISE` slots for `gen_z_professionals × anxiety`. The `library_34`
fallback is the documented escape hatch, but the bestseller composite cannot
score on memorable, persona-specific exercises if every slot pulls a generic
library entry.

**This is a content gap, not a wiring gap.** The fix is another atom backfill PR
(EXERCISE slots for this matrix) — separate from #852's chapter-flow scope.

### 3. Scene anchor density cap FAIL on chapter 10

Hard quality-gate failure (the actual exit-1 cause):

```json
{
  "status": "FAIL",
  "book_plan_id": "generated_anxiety_gen_z_professionals_compact_book_8ch_30min",
  "scene_anchor_cap": 2,
  "violations": [
    {
      "chapter": 10,
      "cap": 2,
      "offenders": [
        {"phrase": "the nervous system is", "paragraph_count": 3}
      ]
    }
  ]
}
```

The phrase `the nervous system is` repeats in 3 paragraphs of chapter 10 (cap is 2).
This is the proximate gate failure, but it is **a downstream symptom of #1**:
the auto-plan ran with 13 chapters rather than 8, and the spine/atom selection
for the over-long auto-plan re-pulled the same scene anchor. With a correctly
scoped 8-chapter plan it is plausible (not certain) that no chapter would have
hit the cap.

**Recommend not chasing this directly until #1 lands.** Re-run the smoke after
the `FORMAT_CHAPTER_COUNTS` patch and see whether the anchor cap still trips.

## Dependency verification

| Check | Expected | Observed |
|---|---|---|
| PR #852 squash on main | yes | `dcc5fad25a` ✓ |
| PR #856 squash on main | yes | `37edc4375c` ✓ |
| Format `compact_book_8ch_30min` declared in registry | yes | yes ✓ |
| Format auto-plan chapter count = 8 | yes | **no — observed 13** |
| TEACHER_DOCTRINE atoms loaded | yes | yes (no `EnrichmentGap` raised) |
| EXERCISE atoms loaded for matrix | n/a | **no — every chapter fell back to `library_34`** |
| Word-budget clamp active | n/a (no render) | n/a |

## Files written by this PR

- `artifacts/qa/bestseller_smoke_post_852_856_2026-05-04.md` (this file — narrative)
- `artifacts/qa/bestseller_smoke_books/run.log` — full pipeline stdout/stderr
- `artifacts/qa/bestseller_smoke_books/scene_anchor_density_report.json` — gate report
- `artifacts/qa/bestseller_smoke_books/selected_content_variants.json` — what got selected

No `book.txt` (none rendered).
No `quality_summary.json` (pipeline did not reach quality summary stage).

## Smoke command (for reproducibility)

```bash
ws=/tmp/bestseller_smoke_post_merge
rm -rf "$ws" && mkdir -p "$ws"
PYTHONPATH=. python3 scripts/pipeline/create_job.py \
  --pipeline ebook --workspace "$ws" \
  --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__grief__F006.yaml
PYTHONPATH=. python3 scripts/pipeline/acknowledge_guide.py --workspace "$ws"
PYTHONPATH=. python3 scripts/run_pipeline.py \
  --topic anxiety --persona gen_z_professionals \
  --arc config/source_of_truth/master_arcs/gen_z_professionals__anxiety__grief__F006.yaml \
  --pipeline-mode spine \
  --runtime-format compact_book_8ch_30min \
  --render-book --render-dir "$ws" \
  --out "$ws/plan.json" \
  --quality-profile production \
  --seed 20260504 \
  --workspace "$ws"
```

## Next-cycle scope (not in this PR)

The bestseller-pass goal for compact formats is **two PRs away**, not one:

| PR | Type | Scope | Size |
|---|---|---|---|
| `eng/auto-plan-compact-format-counts` | wiring | add the three compact formats to `FORMAT_CHAPTER_COUNTS`; verify auto-plan honors `chapter_count_default` from format registry as the single source of truth (not the hardcoded dict); add unit test | small (~30 LOC + test) |
| `content/exercise-atoms-anxiety-gen-z-professionals` | content | backfill `EXERCISE` atom slots for the matrix so `library_34` is not the fallback; verify with the same smoke command | medium |

After both land, re-run **this exact smoke command** as the closing verification.
The scene-anchor-density failure may resolve on its own once chapter count is
correct; if it persists, treat as a third small wiring PR.

The V4 modular `output_format` mapping deferred from #856 closeout should not
proceed until this verification passes — there is no point wiring a modular
mapping onto an auto-plan layer that doesn't honor format-declared chapter counts.

## Gates

| Gate | Result |
|---|---|
| `push_guard` | PASS |
| `preflight_push` (run pre-PR) | pending — run before push |
| LLM audit | PASS (zero paid LLM calls; pipeline render is template/atom-driven) |
| No production code touched | PASS (only `artifacts/qa/` writes) |

## What this PR does NOT do

- Does not patch the auto-plan generator. That is a separate engineering PR.
- Does not backfill EXERCISE atoms. That is a separate content PR.
- Does not retry the smoke at the smaller compact formats (`compact_book_5ch_15min`,
  `compact_book_5ch_20min`). They share the same `FORMAT_CHAPTER_COUNTS` gap, so the
  same failure mode is expected — no information gained from re-running.
- Does not interleave with the cover stream (#855, #857) or the Pearl News stream
  (#850, #853). Those remain on their separate branch chains.
