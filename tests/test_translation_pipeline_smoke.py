"""Smoke tests: translation batch wiring (no Dashscope calls)."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def _run(args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    e = {**os.environ, "DASHSCOPE_API_KEY": "", **(env or {})}
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=e,
    )


def test_run_locale_batches_dry_run_core_one_topic():
    r = _run(
        [
            "scripts/localization/run_locale_batches.py",
            "--core-locales",
            "--topics",
            "climate",
            "--dry-run",
            "--translate-only",
            "--max-agents",
            "4",
            "--timeout-sec",
            "60",
        ]
    )
    assert r.returncode == 0, r.stderr + r.stdout
    assert "PASS" in r.stdout or "failures=0" in r.stdout


def test_translate_atoms_all_locales_help_lists_flags():
    r = _run(["scripts/localization/translate_atoms_all_locales.py", "--help"])
    assert r.returncode == 0, r.stderr + r.stdout
    out = r.stdout + r.stderr
    assert "--all-locales" in out and "--locale" in out


def test_validate_translations_help_lists_flags():
    r = _run(["scripts/localization/validate_translations.py", "--help"])
    assert r.returncode == 0, r.stderr + r.stdout
    out = r.stdout + r.stderr
    assert "--all-locales" in out or "--locale" in out


def test_locale_structural_gate_help_lists_locales():
    r = _run(["scripts/localization/locale_structural_gate.py", "--help"])
    assert r.returncode == 0, r.stderr + r.stdout
    out = r.stdout + r.stderr
    assert "--locales" in out
