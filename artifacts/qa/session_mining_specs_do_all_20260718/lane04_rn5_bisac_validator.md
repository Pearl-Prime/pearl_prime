# Lane 04 RN-5 BISAC Validator Only

## Smoke

Current generator maps are already corrected:

- `scripts/catalog/gen_plan_skeletons.py`
- `scripts/catalog/flip_authoring_skeletons.py`

Anxiety-family topics lead with `SEL036000`.

## Patch

- Added validator-only script: `scripts/ci/check_bisac_topic_map.py`.
- Added unit coverage: `tests/test_bisac_topic_map.py`.
- Existing sample plan validation checks that current catalog metadata leads with `SEL036000` without rewriting older secondary BISAC codes.

## Proof

- `PYTHONPATH=. python3 -m pytest tests/test_bisac_topic_map.py -q` -> 2 passed.
- `PYTHONPATH=. python3 scripts/ci/check_bisac_topic_map.py --sample-plan config/source_of_truth/book_plans_en_us/way_stream_sanctuary__default_teacher__gen_x_sandwich__anxiety__shame__1hr.yaml` -> PASS.

Catalog rewrite: no.
