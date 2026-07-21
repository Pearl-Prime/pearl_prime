"""CI wrapper for the anxiety accent flagship truth gate."""
from __future__ import annotations

from pathlib import Path

import pytest

from scripts.ci.check_accent_flagship_truth import check_artifacts

REPO_ROOT = Path(__file__).resolve().parents[2]
RENDER_DIR = REPO_ROOT / "artifacts" / "rendered" / "cli_demo_trace_run_composite_contract_v1"
PROOF_DIR = REPO_ROOT / "artifacts" / "qa" / "proprime_accent_flagship_proof_2026-07-11"


def _has_truth_bundle(path: Path) -> bool:
    return path.exists() and (
        (path / "enhancement_contract.json").exists()
        or ((path / "plan.json").exists() and (path / "rendered_accent_audit.json").exists())
    )


@pytest.mark.slow
def test_accent_flagship_truth_gate_artifacts_when_present():
    if _has_truth_bundle(PROOF_DIR):
        target = PROOF_DIR
    else:
        target = RENDER_DIR if _has_truth_bundle(RENDER_DIR) else (RENDER_DIR if RENDER_DIR.exists() else PROOF_DIR)
    if not target.exists():
        pytest.skip("flagship render artifacts not present; run canonical anxiety render first")
    errors: list[str] = []
    summary = check_artifacts(target, errors=errors)
    assert not errors, summary
