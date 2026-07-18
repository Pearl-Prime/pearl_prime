"""Guard: banned paid-LLM API keys must not be injected into GitHub Actions
workflow env blocks.

Closes the enforcement gap documented in CLAUDE.md ("ANTHROPIC_API_KEY /
CLAUDE_API_KEY reads in repo code" are BANNED, "enforced by
llm-policy-enforcement.yml") — previously audit_llm_callers.py only matched
Python SDK call sites (anthropic.Anthropic( / .messages.create(), so a stray
`CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}` in a workflow scored 0
violations. The `workflow_paid_key_injection` rule now flags that class.

Tier-2 Qwen/DashScope keys are sanctioned and must NOT be flagged.

Mirrors the monkeypatch-REPO_ROOT pattern in test_audit_llm_callers_roots.py.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import scripts.ci.audit_llm_callers as audit

# Test against the REAL shipped config so this guards the actual enforced rule.
REAL_BANNED = (
    Path(audit.__file__).resolve().parents[2]
    / "config"
    / "governance"
    / "banned_llm_patterns.yaml"
)
WF = ".github/workflows"
EXPR = "${{ " + "secrets.%s }}"  # split so this file never holds a literal injection


def _env_step(key: str) -> str:
    return (
        "name: t\non:\n  workflow_dispatch:\njobs:\n  j:\n"
        "    runs-on: ubuntu-latest\n    steps:\n      - name: s\n"
        "        env:\n"
        f"          {key}: {EXPR % key}\n"
        "        run: echo hi\n"
    )


def _seed(tmp: Path, files: dict[str, str]) -> None:
    (tmp / WF).mkdir(parents=True)
    for name, body in files.items():
        (tmp / WF / name).write_text(body, encoding="utf-8")


def _run(monkeypatch, tmp: Path) -> dict:
    monkeypatch.setattr(audit, "REPO_ROOT", tmp)
    out = tmp / "out.md"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit_llm_callers.py",
            "--banned-patterns-file",
            str(REAL_BANNED),
            "--output",
            str(out),
            "--roots",
            WF,
        ],
    )
    rc = audit.main()
    summary = json.loads((tmp / "llm_audit_summary.json").read_text(encoding="utf-8"))
    return rc, summary


def test_claude_api_key_injection_flagged(monkeypatch, tmp_path):
    _seed(tmp_path, {"bad.yml": _env_step("CLAUDE_API_KEY")})
    rc, summary = _run(monkeypatch, tmp_path)
    assert summary["violation_count"] == 1, summary
    v = summary["violations"][0]
    assert v["rule"] == "workflow_paid_key_injection"
    assert v["path"].endswith("bad.yml")
    assert rc == 0  # no --fail-on-violation passed


def test_anthropic_api_key_injection_flagged(monkeypatch, tmp_path):
    _seed(tmp_path, {"bad.yml": _env_step("ANTHROPIC_API_KEY")})
    _, summary = _run(monkeypatch, tmp_path)
    assert summary["violation_count"] == 1
    assert summary["violations"][0]["rule"] == "workflow_paid_key_injection"


def test_openai_api_key_injection_flagged(monkeypatch, tmp_path):
    _seed(tmp_path, {"bad.yml": _env_step("OPENAI_API_KEY")})
    _, summary = _run(monkeypatch, tmp_path)
    assert summary["violation_count"] == 1


def test_qwen_dashscope_tier2_key_not_flagged(monkeypatch, tmp_path):
    # Tier-2 CJK path (Qwen on Pearl Star) — sanctioned, must NOT be flagged.
    _seed(tmp_path, {"qwen.yml": _env_step("DASHSCOPE_API_KEY")})
    _, summary = _run(monkeypatch, tmp_path)
    assert summary["violation_count"] == 0, summary


def test_clean_workflow_not_flagged(monkeypatch, tmp_path):
    _seed(tmp_path, {"clean.yml": _env_step("R2_ACCESS_KEY_ID")})
    _, summary = _run(monkeypatch, tmp_path)
    assert summary["violation_count"] == 0
