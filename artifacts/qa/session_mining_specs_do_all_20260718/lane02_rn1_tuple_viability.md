# Lane 02 RN-1 Tuple Viability Repro Fix

## Smoke

Fresh repro: a tuple with a valid binding and arc, no exact engine STORY bank, and a usable generic `atoms/<persona>/<topic>/STORY/CANONICAL.txt` previously produced `NO_STORY_POOL` because `check_tuple_viability.py` only loaded `atoms/<persona>/<topic>/<engine>/CANONICAL.txt`.

## Patch

- `phoenix_v4/gates/check_tuple_viability.py` now mirrors the registry resolver's STORY fallback rule before emitting `NO_STORY_POOL`.
- `repo_root` is threaded into `_get_gate_config` so temp-repo viability repros use the intended local gate config.
- Targeted repro test added: `tests/test_tuple_viability_story_fallback.py`.

## Proof

- `PYTHONPATH=. python3 -m pytest tests/test_tuple_viability_story_fallback.py -q` -> 1 passed.
- `PYTHONPATH=. python3 -m pytest tests/unit/planning/test_canonical_atom_parse_sweep_guard.py -q` -> 11 passed.
- `PYTHONPATH=. python3 -m pytest tests/test_catalog_ready_predicate.py -q` -> 9 passed.

No catalog-scale tuple sweep was run.
