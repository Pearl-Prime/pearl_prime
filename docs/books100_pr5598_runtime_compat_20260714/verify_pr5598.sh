#!/usr/bin/env bash
set -euo pipefail
WORKTREE="${1:-/Users/ahjan/phoenix_omega_worktrees/books100-pr5598-runtime-compat-20260714}"
cd "$WORKTREE"

python3 -m py_compile \
  phoenix_v4/planning/canonical_atom_blocks.py \
  phoenix_v4/planning/pool_index.py \
  phoenix_v4/rendering/prose_resolver.py \
  phoenix_v4/planning/assembly_compiler.py \
  tests/planning/test_integration_canonical_parser.py

PYTHONPATH=. python3 -m pytest -q \
  tests/planning/test_integration_canonical_parser.py \
  tests/test_bestseller_editor_wiring.py::test_editor_report_fails_when_dimension_gates_block_delivery

PYTHONPATH=. python3 scripts/ci/check_canonical_atom_parse_sweep.py
PYTHONPATH=. python3 scripts/run_production_readiness_gates.py
