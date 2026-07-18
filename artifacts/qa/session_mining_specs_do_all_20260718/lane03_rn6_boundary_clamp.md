# Lane 03 RN-6 Boundary-Aware Word Clamp

## Smoke

Fresh fixture repro: a final paragraph slice with a very short first sentence could keep a longer unterminated second-sentence fragment because the prior boundary trim ignored sentence endings that occurred before the first third of the sliced text.

## Patch

- `scripts/run_pipeline.py` now trims sliced final paragraphs to the last complete sentence boundary whenever one exists.
- Plain token-stream fixtures with no sentence punctuation keep the existing word-slice behavior for accounting tests.
- Regression test added to `tests/test_run_pipeline_word_ceiling_clamp.py`.

## Proof

- `PYTHONPATH=. python3 -m pytest tests/test_run_pipeline_word_ceiling_clamp.py -q` -> 10 passed.
- Bounded single-cell render:
  - command used `--no-job-check` for CI/testing only, no publish/feed/queue writes.
  - output: `artifacts/qa/session_mining_specs_do_all_20260718/rn6_bounded_render/book.txt`
  - book words: 16,015
  - book quality: Pass in `artifacts/qa/session_mining_specs_do_all_20260718/rn6_bounded_render/book_quality_report.json`
  - boundary inspection: `ends_safe=True`, `has_partial_atom_trace=False`

No catalog-scale render was run.
