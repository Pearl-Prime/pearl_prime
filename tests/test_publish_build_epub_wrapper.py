"""Tests for scripts/publish/build_epub.py — thin wrapper for the
publish namespace around scripts/release/build_epub.py.

Verifies the wrapper:
  1. Imports without error.
  2. Exposes a main() callable.
  3. Forwards CLI flags to the backend (subprocess --help check).
  4. Normalises None return → exit 0.
  5. Preserves explicit int return codes from the backend.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))


def test_wrapper_imports() -> None:
    from scripts.publish import build_epub as wrapper
    assert callable(wrapper.main)


def test_wrapper_help_matches_backend_help() -> None:
    """Subprocess --help on the wrapper should produce the backend's argparse help.

    This proves args are forwarded verbatim without the wrapper rewriting them.
    """
    result = subprocess.run(
        [sys.executable, "scripts/publish/build_epub.py", "--help"],
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(REPO_ROOT), "PATH": "/usr/bin:/bin"},
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    out = result.stdout
    # Spot-check backend flags surface on the wrapper's --help.
    for flag in ("--input", "--title", "--cover", "--output", "--batch", "--dry-run", "--raw-cover"):
        assert flag in out, f"backend flag {flag!r} missing from wrapper --help: {out[:500]}"


def test_wrapper_returns_zero_when_backend_returns_none() -> None:
    """Backend main() returns None on success; wrapper normalises that to 0."""
    from scripts.publish import build_epub as wrapper
    with mock.patch("scripts.release.build_epub.main", return_value=None) as backend_main:
        rc = wrapper.main()
    assert rc == 0
    assert backend_main.called


def test_wrapper_preserves_int_return() -> None:
    """If a future backend version returns an int, the wrapper must pass it through."""
    from scripts.publish import build_epub as wrapper
    with mock.patch("scripts.release.build_epub.main", return_value=2):
        rc = wrapper.main()
    assert rc == 2


def test_wrapper_does_not_rewrite_argv() -> None:
    """Sanity: the wrapper must not pop/rewrite sys.argv before backend reads it."""
    from scripts.publish import build_epub as wrapper

    captured: dict = {}

    def fake_backend_main() -> None:
        captured["argv"] = list(sys.argv)
        return None

    with mock.patch.object(sys, "argv", ["scripts/publish/build_epub.py", "--batch", "--dry-run"]):
        with mock.patch("scripts.release.build_epub.main", side_effect=fake_backend_main):
            wrapper.main()
    assert captured["argv"] == ["scripts/publish/build_epub.py", "--batch", "--dry-run"]
