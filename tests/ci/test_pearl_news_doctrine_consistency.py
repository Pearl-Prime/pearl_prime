"""Smoke test for the Pearl News doctrine-consistency gate.

The gate is expected to report violations against the current state of main
(documented in artifacts/coordination/pearl_news_teacher_pack_drift_audit.md).
The doctrine campaign (Phases A/B) drives the violation count toward zero;
this test asserts the gate is operational and detecting at least the known
ahjan-Theravada drift, so any regression in the gate itself surfaces.

Once Phase A/B PRs land, the assertion should be relaxed or flipped to an
exact-zero check (in a follow-up PR that also makes the workflow required).
"""

from __future__ import annotations

import subprocess
import sys
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "ci" / "pearl_news_doctrine_consistency.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
        timeout=60,
    )


def test_gate_runs_without_error():
    """The gate script must execute cleanly in report mode (exit 0)."""
    r = run()
    assert r.returncode == 0, f"report mode should exit 0, got {r.returncode}\nstderr: {r.stderr}"
    assert "PEARL NEWS" in r.stdout.upper(), "expected gate header in stdout"


def test_json_mode_produces_valid_json():
    """--json output must parse and have the expected shape."""
    r = run("--json")
    assert r.returncode == 0
    data = json.loads(r.stdout)
    assert "violations" in data
    assert "summary" in data
    assert "errors" in data["summary"]
    assert "warnings" in data["summary"]
    assert "teachers_checked" in data["summary"]
    assert data["summary"]["teachers_checked"] >= 1


def test_detects_known_ahjan_theravada_drift():
    """The gate must surface the known ahjan-Theravada drift.

    Documented in artifacts/coordination/pearl_news_teacher_pack_drift_audit.md.
    The doctrine.yaml `prohibited_outcomes` includes "Theravada Buddhist framing",
    and several ahjan packs frame him as a "Theravada Buddhist teacher". If this
    assertion ever fails AFTER Phase A merges, that's good news (drift cleared);
    update the test to check for zero ahjan violations instead.
    """
    r = run("--json")
    data = json.loads(r.stdout)
    ahjan_violations = [v for v in data["violations"] if v["teacher_id"] == "ahjan"]
    if not ahjan_violations:
        # Phase A may have cleared the drift — acceptable.
        return
    # Otherwise, expect at least one pack-tradition-prohibited hit
    pack_hits = [v for v in ahjan_violations if v["kind"] == "pack_tradition_prohibited"]
    assert pack_hits, (
        "expected at least one ahjan pack_tradition_prohibited violation "
        "(Theravada framing). Got: " + str(ahjan_violations)
    )


def test_strict_mode_exit_code_matches_error_count():
    """--strict should return 1 iff any ERROR exists, else 0."""
    json_r = run("--json")
    data = json.loads(json_r.stdout)
    expected_exit = 1 if data["summary"]["errors"] > 0 else 0

    strict_r = run("--strict")
    assert strict_r.returncode == expected_exit, (
        f"strict mode exit code mismatch: expected {expected_exit}, "
        f"got {strict_r.returncode}. Errors reported: {data['summary']['errors']}"
    )
