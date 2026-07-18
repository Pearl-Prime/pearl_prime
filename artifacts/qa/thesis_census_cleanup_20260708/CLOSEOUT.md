# Thesis census cleanup — closeout (2026-07-08)

**Lane:** BOOKS / thesis census hygiene (NOT sellability, NOT `content_uniqueness`)

## Verdict

**thesis census improved** — cross-topic thesis reuse among the six authored topics dropped materially.

| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Multi-topic repeated thesis groups (≥2 topics, 77-cell fast census) | 70 (539-cell full) | **0** | **−70** |
| Top shared group cell span (comparison baseline) | 54 cells × 5 topics | **0** at 5-topic span | eliminated |
| Unique theses (77-cell fast census) | — | 70 | — |
| Cross-cell repeated (≥2 cells, fast census) | — | 50 | mostly within-topic duration dupes |

**Before oracle:** `CENSUS_BEFORE.json` (539-cell `score_cell` run, pre-overlay).  
**After oracle:** `CENSUS_AFTER.json` (77-cell `generate_book_plan` fast census, post-overlay).

Remaining cross-cell repeats are within-topic only (same thesis across durations/personas), not cross-topic baseline sharing.

## What changed

- `config/planning/chapter_thesis_bank.yaml` — topic overlays for **burnout, anxiety, boundaries, overthinking, self_worth, grief** (20 intents × primary engines per topic; comparison engine for 5 topics, plus secondary engines: overwhelm, shame, spiral, false_alarm, grief, watcher as bound).
- Engine-level `intents:` baseline **unchanged** — spiral / overwhelm / comparison columns intact; unauthored topics still fall through.
- `tests/test_chapter_thesis_bank_resolver.py` — 5 tests: topic override first, baseline fallback, same-engine/different-topic divergence, no regression on unauthored topics.
- `scripts/qa/thesis_census_fast.py` — fast census harness (avoids 10+ min full `score_cell` sweep).

## Resolver proof (same engine, different topic)

`comparison` + `expose_cost`:

| topic | thesis (leading fragment) |
|-------|---------------------------|
| burnout | Every comparison to harder-working peers quietly bills your body… |
| anxiety | Comparing your fear to others' composure is expensive… |
| boundaries | Every yardstick of who gives more quietly bills you… |

All differ; each matches `topics[topic][intent][engine]`, not `intents[intent][engine]`.

## Production prose metrics

**No production prose metric changed incidentally.** Thesis text is plan meta / exercise-hint only; it does not enter `content_uniqueness` trigram scoring or rendered body prose (confirmed in `artifacts/qa/thesis_detemplating_blocker_20260708/BLOCKER.md`).

## Explicit non-claims

- This did **NOT** fix sellability or `SELLABLE_AS_IS`.
- This did **NOT** fix `content_uniqueness`.
- Sellability / uniqueness still belong to the **adjacency + stub lane** unless separately proven.

## Validation

```
PYTHONPATH=. python3 -m pytest tests/test_chapter_thesis_bank_resolver.py -v   # 5 passed
PYTHONPATH=. python3 scripts/qa/thesis_census_fast.py --out artifacts/qa/thesis_census_cleanup_20260708/CENSUS_AFTER.json
```
