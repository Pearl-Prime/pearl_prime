# Scorer-truth closeout (2026-07-08)

**Lane:** uniqueness scorer truth-alignment (NOT thesis, NOT writer, NOT gate weakening)

## Verdict

Measurement-path false alarm **resolved**. Legacy `registry/{topic}.yaml` trigram scoring is now hard-labeled `legacy_registry_artifact` and cannot masquerade as shipped-book sellability truth. Shipped spine books are the default truth source.

## Burnout proof cells (trigram scorer)

| Cell | registry artifact | shipped spine |
|------|------------------:|--------------:|
| burnout_overwhelm__corporate_managers | 0.0 | 1.0 |
| burnout_watcher__corporate_managers | 0.0 | 1.0 |
| burnout_grief__corporate_managers | 0.0 | 1.0 |

## Production prose metrics

No book prose rewritten. No gates weakened. No score inflation — labels only plus explicit default truth source.

## Explicit non-claims

- This did **not** fix EI v2 semantic-dedup uniqueness (~0.16 on shipped burnout).
- That remains a separate shipped-book metric (adjacency/stub lane if it blocks ship).
- Thesis census work is parked; unrelated to this lane.

## Validation

```bash
PYTHONPATH=. python3 -m pytest tests/test_content_uniqueness_truth.py -v
PYTHONPATH=. python3 scripts/qa/score_uniqueness_truth_proof.py
```
