"""ACT-014 — LLM policy compliance audit tests.

Verifies that audit_llm_callers.py finds 0 violations in the repo using
the canonical banned_llm_patterns.yaml + allowed_llm_patterns.yaml config.

The audit enforces the two-tier LLM policy:
  Tier 1: Claude Code subscription (operator-present) — no API spend
  Tier 2: Gemma/Qwen via Ollama on Pearl Star (unattended scheduled pipelines)
  BANNED: All paid LLM cloud APIs (Anthropic API key, OpenAI cloud, DashScope cloud)
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDIT_SCRIPT = REPO_ROOT / "scripts" / "ci" / "audit_llm_callers.py"
BANNED_PATTERNS = REPO_ROOT / "config" / "governance" / "banned_llm_patterns.yaml"
ALLOWED_PATTERNS = REPO_ROOT / "config" / "governance" / "allowed_llm_patterns.yaml"


def _run_audit(fail_on_violation: bool = False) -> dict:
    """Run the audit script and return parsed summary JSON."""
    cmd = [
        sys.executable,
        str(AUDIT_SCRIPT),
        "--banned-patterns-file", str(BANNED_PATTERNS),
        "--output", "/tmp/act014_llm_audit.md",
    ]
    if ALLOWED_PATTERNS.exists():
        cmd += ["--allowed-patterns-file", str(ALLOWED_PATTERNS)]
    if fail_on_violation:
        cmd.append("--fail-on-violation")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(REPO_ROOT))
    try:
        return json.loads(result.stdout.strip())
    except (json.JSONDecodeError, ValueError):
        return {"violation_count": -1, "stderr": result.stderr}


def test_audit_script_exists():
    assert AUDIT_SCRIPT.exists(), f"audit_llm_callers.py must exist at {AUDIT_SCRIPT}"


def test_banned_patterns_yaml_exists():
    assert BANNED_PATTERNS.exists(), f"banned_llm_patterns.yaml must exist at {BANNED_PATTERNS}"


def test_audit_zero_violations():
    """The repo must have zero banned LLM API usage violations."""
    result = _run_audit()
    count = result.get("violation_count", -1)
    assert count == 0, (
        f"LLM policy audit found {count} violation(s). "
        f"Run: python3 scripts/ci/audit_llm_callers.py "
        f"--banned-patterns-file config/governance/banned_llm_patterns.yaml "
        f"--output /tmp/llm_audit.md for details."
    )


def test_audit_returns_valid_json():
    result = _run_audit()
    assert "violation_count" in result, f"audit output must contain 'violation_count', got: {result}"


def test_audit_run_agent_refactor_deleted():
    """scripts/ci/run_agent_refactor.py (paid-API agent runner) must be deleted."""
    deleted = REPO_ROOT / "scripts" / "ci" / "run_agent_refactor.py"
    assert not deleted.exists(), "run_agent_refactor.py was not deleted as required by Phase 1"
