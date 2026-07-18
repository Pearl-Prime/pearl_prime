"""Tests for EXERCISE-BANK-RESOLUTION-01 strict-canonical production gate.

The gate is `_check_exercise_strict_canonical_gate` in `scripts/run_pipeline.py`.
It raises SystemExit (matches the existing production-gate pattern) when
`quality_profile == "production"` AND the enrichment audit shows any EXERCISE
slot resolved via `practice_library` fall-through.
"""
from __future__ import annotations

import pytest

# Importing scripts.run_pipeline as a module so we can call the gate helper
# directly. The script is executable and uses argparse only inside main(),
# so import-time side effects are minimal.
import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RUN_PIPELINE_PATH = REPO_ROOT / "scripts" / "run_pipeline.py"

_spec = importlib.util.spec_from_file_location("_rp_module_under_test", RUN_PIPELINE_PATH)
_run_pipeline = importlib.util.module_from_spec(_spec)
sys.modules["_rp_module_under_test"] = _run_pipeline
_spec.loader.exec_module(_run_pipeline)
_check_gate = _run_pipeline._check_exercise_strict_canonical_gate


def test_strict_gate_raises_on_production_when_practice_library_fires():
    """Production + any practice_library EXERCISE → SystemExit."""
    audit = {"slots_from_practice_library": 3, "slots_from_teacher": 5}
    with pytest.raises(SystemExit) as exc_info:
        _check_gate("production", audit)
    msg = str(exc_info.value)
    assert "EXERCISE-BANK-RESOLUTION-01" in msg
    assert "3 EXERCISE slot(s)" in msg
    assert "practice_library" in msg


def test_strict_gate_allows_practice_library_on_draft_profile():
    """Draft + practice_library fires → no exit (backward compat)."""
    audit = {"slots_from_practice_library": 3, "slots_from_teacher": 5}
    # Should NOT raise.
    _check_gate("draft", audit)


def test_strict_gate_allows_practice_library_on_debug_profile():
    """Debug + practice_library fires → no exit."""
    audit = {"slots_from_practice_library": 3}
    _check_gate("debug", audit)


def test_strict_gate_allows_practice_library_on_flagship_profile():
    """Flagship + practice_library fires → no exit (flagship has its own gate logic)."""
    audit = {"slots_from_practice_library": 1}
    _check_gate("flagship", audit)


def test_strict_gate_passes_when_teacher_or_persona_atom_resolves():
    """Production but no practice_library fall-through → no exit."""
    audit = {"slots_from_practice_library": 0, "slots_from_teacher": 8}
    _check_gate("production", audit)


def test_strict_gate_passes_when_audit_is_none():
    """Production with no audit dict (edge case) → no exit (treated as 0)."""
    _check_gate("production", None)


def test_strict_gate_passes_when_audit_is_empty():
    """Production with empty audit dict → no exit."""
    _check_gate("production", {})
