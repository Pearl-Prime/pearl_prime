from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts/ci/check_brand_admin_weekly_os_public_sync.py"


def test_weekly_os_public_matches_root_transform() -> None:
    proc = subprocess.run(
        [sys.executable, str(CHECK)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout
