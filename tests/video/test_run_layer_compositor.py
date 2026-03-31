from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_run_layer_compositor_help():
    r = subprocess.run(
        [sys.executable, str(REPO_ROOT / "scripts" / "video" / "run_layer_compositor.py"), "--help"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    assert r.returncode == 0 and "Stage 12" in r.stdout
