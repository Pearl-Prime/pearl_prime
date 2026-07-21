# Lane 05 RN-9 Docs Index Completeness Gate

## Smoke

Required docs were parsed from `docs/agent_brief.txt`:

- `docs/agent_brief.txt`
- `docs/PROGRAM_STATE.md`
- `docs/SESSION_UNITY_PROTOCOL.md`
- `docs/PEARL_ARCHITECT_STATE.md`
- `artifacts/coordination/ACTIVE_PROJECTS.tsv`
- `artifacts/coordination/ACTIVE_WORKSTREAMS.tsv`
- `artifacts/coordination/SUBSYSTEM_AUTHORITY_MAP.tsv`

Before the patch, only `PROGRAM_STATE` and `PEARL_ARCHITECT_STATE` were indexed as links.

## Patch

- Added a narrow required-read checker: `scripts/ci/check_required_docs_index.py`.
- Added a single `DOCS_INDEX.md` bootstrap line linking the required docs and coordination tables.
- Added parser test: `tests/test_required_docs_index.py`.

## Proof

- `PYTHONPATH=. python3 -m pytest tests/test_required_docs_index.py -q` -> 1 passed.
- `PYTHONPATH=. python3 scripts/ci/check_required_docs_index.py --repo-root .` -> PASS, `required_docs_scanned=7`.

Broad docs churn: no.
