from __future__ import annotations

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent


def test_release_smoke_uses_fast_lane_rigorous_flags() -> None:
    script = (REPO_ROOT / "scripts" / "release" / "release_smoke.sh").read_text(
        encoding="utf-8"
    )

    rigorous_line = next(
        line for line in script.splitlines() if "run_rigorous_system_test.py" in line
    )

    assert "--skip-sim" in rigorous_line
    assert "--strict" in rigorous_line
    assert "--skip-atoms-coverage" in rigorous_line
    assert "--skip-systems-test" in rigorous_line


def test_rollback_smoke_uses_core_pytest_marker_lane() -> None:
    script = (REPO_ROOT / "scripts" / "release" / "rollback_smoke.sh").read_text(
        encoding="utf-8"
    )

    pytest_line = next(line for line in script.splitlines() if "-m pytest tests/" in line)

    assert '"not slow and not integration"' in pytest_line
