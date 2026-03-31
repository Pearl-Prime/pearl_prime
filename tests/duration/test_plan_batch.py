from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def test_plan_batch_small_matrix(tmp_path):
    out = tmp_path / "batch.json"
    subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "duration" / "plan_batch.py"),
            "--brands",
            "stillness_press",
            "--platforms",
            "youtube",
            "--locales",
            "en-US",
            "-o",
            str(out),
            "--force",
        ],
        cwd=REPO_ROOT,
        check=True,
    )
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["count"] == 20
    assert data["items"][0]["format"] == sorted(
        __import__("yaml").safe_load(
            open(REPO_ROOT / "config" / "duration" / "duration_registry.yaml")
        )["formats"].keys()
    )[0]
