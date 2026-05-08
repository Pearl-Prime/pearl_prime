"""Tests for audit_llm_callers --roots scoping and --max-runtime-seconds."""

from __future__ import annotations

import json
import sys
import pytest

import scripts.ci.audit_llm_callers as audit


MINIMAL_BANNED = """\
version: 1
global_exempt_prefixes:
  - "config/"
banned_patterns:
  z_ci_test_mark:
    regex: 'Z_CI_TEST_VIOLATION_MARK'
    reason: "test pattern for CI roots/max-runtime tests"
"""


def _write_minimal_repo(tmp: Path) -> None:
    (tmp / "config/governance").mkdir(parents=True)
    (tmp / "config/governance/banned_llm_patterns.yaml").write_text(MINIMAL_BANNED, encoding="utf-8")
    (tmp / "scripts/z_in_root").mkdir(parents=True)
    (tmp / "scripts/z_in_root/bad.py").write_text(
        "Z_CI_TEST_VIOLATION_MARK = 1\n",
        encoding="utf-8",
    )
    (tmp / "outside_scope").mkdir()
    (tmp / "outside_scope/bad.py").write_text(
        "Z_CI_TEST_VIOLATION_MARK = 2\n",
        encoding="utf-8",
    )


def test_roots_limits_violations_to_subtree(monkeypatch, tmp_path):
    _write_minimal_repo(tmp_path)
    out = tmp_path / "audit_out.md"
    monkeypatch.setattr(audit, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit_llm_callers.py",
            "--banned-patterns-file",
            str(tmp_path / "config/governance/banned_llm_patterns.yaml"),
            "--output",
            str(out),
            "--roots",
            "scripts",
        ],
    )
    rc = audit.main()
    assert rc == 0
    summary = json.loads(
        (out.parent / "llm_audit_summary.json").read_text(encoding="utf-8")
    )
    assert summary["violation_count"] == 1

    summary_path = tmp_path / "llm_audit_summary.json"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit_llm_callers.py",
            "--banned-patterns-file",
            str(tmp_path / "config/governance/banned_llm_patterns.yaml"),
            "--output",
            str(tmp_path / "audit_full.md"),
        ],
    )
    rc_full = audit.main()
    assert rc_full == 0
    full = json.loads(summary_path.read_text(encoding="utf-8"))
    assert full["violation_count"] == 2


def test_max_runtime_seconds_zero_exits_2(monkeypatch, tmp_path):
    _write_minimal_repo(tmp_path)
    monkeypatch.setattr(audit, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit_llm_callers.py",
            "--banned-patterns-file",
            str(tmp_path / "config/governance/banned_llm_patterns.yaml"),
            "--output",
            str(tmp_path / "out.md"),
            "--max-runtime-seconds",
            "0",
        ],
    )
    assert audit.main() == 2


def test_max_runtime_seconds_aborts_during_scan(monkeypatch, tmp_path):
    _write_minimal_repo(tmp_path)
    monkeypatch.setattr(audit, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "audit_llm_callers.py",
            "--banned-patterns-file",
            str(tmp_path / "config/governance/banned_llm_patterns.yaml"),
            "--output",
            str(tmp_path / "out.md"),
            "--max-runtime-seconds",
            "3600",
        ],
    )

    t = {"v": 1000.0}

    def boom_mono():
        t["v"] += 10**9
        return t["v"]

    monkeypatch.setattr(audit.time, "monotonic", boom_mono)
    assert audit.main() == 2
