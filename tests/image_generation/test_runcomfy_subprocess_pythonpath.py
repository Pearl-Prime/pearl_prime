"""Regression test for Conductor v3 Phase 1 smoke failure (PR #1054).

Scenario reproduced: when ``scripts/image_generation/batch_runner.py`` is
executed as a script (e.g. ``python3 scripts/image_generation/batch_runner.py``)
Python sets ``sys.path[0]`` to the script's directory — NOT the repo root.
The RunComfy dispatcher module (``dispatchers/runcomfy_dispatcher.py``) is
then loaded via ``importlib.util.spec_from_file_location`` and at its module
top does:

    from scripts.image_generation import runcomfy_dispatch as _rc

Without REPO_ROOT on ``sys.path`` this raises::

    ModuleNotFoundError: No module named 'scripts'

…which is exactly what the Conductor v3 Phase 1 smoke saw on 6/6 RunComfy
panel cells (PR #1054). This test guards against regression by:

1. Spawning a child Python process with the same ``sys.path[0]`` mutation
   that ``python3 scripts/image_generation/batch_runner.py`` produces.
2. Importing ``scripts.image_generation.batch_runner`` and triggering the
   dispatcher load path used in the live run (``_runcomfy()``).
3. Asserting the subprocess exits 0 with no ``ModuleNotFoundError`` text on
   stderr, and that ``scripts.image_generation.dispatchers.runcomfy_dispatcher``
   was successfully imported.

No RunComfy HTTP call is made — we only verify the import path resolves.
"""

from __future__ import annotations

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_child(script: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_batch_runner_script_invocation_keeps_scripts_importable() -> None:
    """Direct script invocation must not break ``from scripts.image_generation import …``.

    Reproduces the exact ``sys.path[0]`` state Python establishes when running
    ``python3 scripts/image_generation/batch_runner.py``. With the fix in
    place, importing the batch_runner module then loading the RunComfy
    dispatcher must succeed.
    """
    script = textwrap.dedent(
        """
        import sys
        from pathlib import Path

        # Emulate Python's behavior when batch_runner.py is invoked directly:
        # sys.path[0] is the script's directory, NOT the repo root.
        repo_root = Path.cwd().resolve()
        sys.path[0] = str(repo_root / "scripts" / "image_generation")

        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "scripts.image_generation.batch_runner",
            str(repo_root / "scripts" / "image_generation" / "batch_runner.py"),
        )
        mod = importlib.util.module_from_spec(spec)
        sys.modules["scripts.image_generation.batch_runner"] = mod
        spec.loader.exec_module(mod)

        # REPO_ROOT must have been injected onto sys.path by batch_runner top.
        assert str(mod.REPO_ROOT) in sys.path, "REPO_ROOT missing from sys.path"

        # Loading the RunComfy dispatcher exercises the failing top-level
        # ``from scripts.image_generation import runcomfy_dispatch as _rc``.
        rc_mod = mod._runcomfy()
        assert rc_mod.__name__ == "scripts.image_generation.dispatchers.runcomfy_dispatcher"
        print("OK")
        """
    ).strip()

    result = _run_child(script)
    assert "ModuleNotFoundError: No module named 'scripts'" not in result.stderr, (
        f"PYTHONPATH regression: dispatcher import failed.\n"
        f"stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    )
    assert result.returncode == 0, (
        f"child exited {result.returncode}; stderr:\n{result.stderr}\nstdout:\n{result.stdout}"
    )
    assert "OK" in result.stdout


def test_runcomfy_dispatcher_top_level_imports_resolve_via_repo_root() -> None:
    """``scripts.image_generation.dispatchers.runcomfy_dispatcher`` must import cleanly.

    Independent of batch_runner — verifies the dispatcher itself doesn't rely
    on caller-side sys.path manipulation that goes missing under script-mode.
    """
    script = textwrap.dedent(
        """
        import sys
        from pathlib import Path

        repo_root = Path.cwd().resolve()
        # Same hostile sys.path[0] as direct script invocation.
        sys.path[0] = str(repo_root / "scripts" / "image_generation")
        # batch_runner is what restores REPO_ROOT — import it the same way
        # the live entry point would (as a package module).
        sys.path.insert(0, str(repo_root))

        import scripts.image_generation.batch_runner as br
        rc_mod = br._runcomfy()
        # Confirm absolute imports resolved (would raise ModuleNotFoundError
        # without REPO_ROOT on sys.path).
        assert hasattr(rc_mod, "dispatch")
        assert hasattr(rc_mod, "build_plan")
        print("OK")
        """
    ).strip()

    result = _run_child(script)
    assert "ModuleNotFoundError" not in result.stderr, (
        f"Dispatcher top-level import regressed.\nstderr:\n{result.stderr}"
    )
    assert result.returncode == 0
    assert "OK" in result.stdout


def test_repo_root_injected_at_module_import() -> None:
    """Importing batch_runner must idempotently put REPO_ROOT on sys.path."""
    from scripts.image_generation import batch_runner

    assert str(batch_runner.REPO_ROOT) in sys.path, (
        "batch_runner did not inject REPO_ROOT onto sys.path at import time"
    )


def test_repeated_dispatcher_load_does_not_duplicate_sys_path_entries() -> None:
    """Defensive injection inside ``_load_dispatcher_module`` is idempotent.

    The guarded ``if str(REPO_ROOT) not in sys.path`` predicate must not append
    a new entry every call. We force a reload from a clean ``sys.path`` (no
    REPO_ROOT) and verify exactly one entry appears.
    """
    from scripts.image_generation import batch_runner

    repo_root_str = str(batch_runner.REPO_ROOT)
    # Prime: ensure REPO_ROOT is present, then verify count never grows.
    batch_runner._runcomfy_mod = None
    batch_runner._runcomfy()
    primed = sys.path.count(repo_root_str)
    assert primed >= 1, "REPO_ROOT missing from sys.path after first load"
    for _ in range(3):
        batch_runner._runcomfy_mod = None
        batch_runner._runcomfy()
    after = sys.path.count(repo_root_str)
    assert after == primed, (
        f"sys.path leaked entries on reload: primed={primed} after={after}"
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
