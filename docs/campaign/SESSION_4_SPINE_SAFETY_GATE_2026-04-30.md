# Session 4 — Spine-mode Safety Gate

**Date:** 2026-04-30
**Branch:** `feat/spine-safety-gate-20260430`
**Operator brief:** *"Make spine mode safe to evaluate before it becomes default. Add a validation/gating layer for spine-mode output. Do not flip `scripts/run_pipeline.py` default. Detect known spine-mode failures. Produce a clear pass/fail artifact. Stop after one PR."*

## What this PR ships

`scripts/qa/validate_spine_output.py` (~370 LoC) — a post-render safety gate
that takes a render directory (e.g. `artifacts/rendered/<id>/`) and reports
pass/fail against the failure modes documented in
[`artifacts/pilot/DEFINITIVE_PIPELINE_COMPARISON.md`](../../artifacts/pilot/DEFINITIVE_PIPELINE_COMPARISON.md).

Plus `tests/test_qa_validate_spine_output.py` (15 tests, all passing in 0.15s).

## Gates implemented

| Gate | Severity | What it catches |
|------|----------|-----------------|
| **LENGTH** | ERROR (below target_min) / WARN (above target_max) | Word count vs `budget.json word_range_target`; smoke-floor below 1500 words emits INFO instead so fragments don't fail loudly |
| **CHAPTER_FLOW** | ERROR (status FAIL) | Reads `chapter_flow_report.json`; surfaces failed-chapter count + per-error-code map |
| **COMPOSITION** | ERROR (linear-concat signature) | Fires when chapter errors include `WEAK_TRANSITIONS` / `MISSING_CLEAR_POINT` / `GENERIC_SCENE_FALLBACK` — the named failure mode of `compose_from_enriched_book` doing slot-concat instead of thesis-threaded `compose_chapter_prose` |
| **TEMPLATE_LEAK** | ERROR | Unrendered Jinja (`{{...}}`, `{%...%}`), TODO/FILL/PLACEHOLDER markers, lorem-ipsum, **unbalanced `{Word ...` curly braces** (catches the failure mode visible in shipped renders) |
| **DUP_BLOCK** | ERROR | Paragraph-level duplicates appearing in 2+ chapters (signals slot-concat repeating bridge/CTA blocks); ≥80 chars to ignore short utility lines |
| **LOC_GROUNDING** | WARN | Surfaces `location_grounding_report.json` status if present |

## Real signal from running the gate on shipped renders

```
$ PYTHONPATH=. python3 scripts/qa/validate_spine_output.py --batch artifacts/rendered/
[exit 1]

Total renders inspected: 10
Passed: 2/10
Error codes by frequency:
  below_target_min:        8
  chapter_flow_fail:       3
  linear_concat_signature: 3
  unbalanced_curly_brace:  2
  cross_chapter_duplicates: 2
```

**Conclusion:** 8/10 of the shipped renders in `artifacts/rendered/` are NOT
safe to ship as books. The spine-mode failure modes called out in the pilot
doc are real, and this gate catches them.

The 2 passing renders (`book_001`, `registry-overthinking`) are both small
fragments below the smoke-render floor — INFO-level, not full books.

## Path forward (no default flip)

Per operator brief: **the `scripts/run_pipeline.py --pipeline-mode` default
remains `registry`.** This PR does not touch it.

The gate enables a new operator workflow:

```bash
# Try a spine render
python3 scripts/run_pipeline.py --pipeline-mode spine ...

# Validate before shipping
python3 scripts/qa/validate_spine_output.py artifacts/rendered/<id>/

# If it passes → safe to package; if it fails → fix the named gate before retrying
python3 scripts/publish/build_epub.py --input artifacts/rendered/<id>/book.txt ...
python3 scripts/publish/validate_epub.py artifacts/epub/<slug>.epub
```

When 100% of test renders pass the spine safety gate (or only emit WARN-level
findings), the operator can confidently flip the default in a follow-up PR.
That's a deliberately separate decision; this PR's job is to make the
information available, not to act on it.

## Constraints respected

| | |
|-|-|
| Branched from `origin/main` | ✅ |
| `push_guard` + `preflight_push` green | ✅ |
| No `--admin` merge | ✅ |
| No paid LLM/image API spend | ✅ |
| Did not flip pipeline default | ✅ |
| Stop after one PR | ✅ |

## Files

- `scripts/qa/validate_spine_output.py` — 370 LoC validator
- `tests/test_qa_validate_spine_output.py` — 15 tests (all pass)
- `docs/campaign/SESSION_4_SPINE_SAFETY_GATE_2026-04-30.md` — this doc

## Test results

```
$ PYTHONPATH=. python3 -m pytest tests/test_qa_validate_spine_output.py -v
15 passed in 0.15s
```
