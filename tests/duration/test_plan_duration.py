from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration._config import load_duration_configs  # noqa: E402
from scripts.duration.plan_duration import plan  # noqa: E402


def test_plan_duration_scoring_in_range():
    cfgs = load_duration_configs()
    doc = plan(
        cfgs,
        brand_id="b",
        platform="youtube",
        locale="en-US",
        format_key="video_mid",
        persona="corporate_managers",
        intent="therapeutic",
        modality=None,
        micro_dose_protocol=False,
    )
    assert 0.0 <= doc["duration_fit_score"] <= 1.0
    assert doc["recommended_duration_sec"] > 0


def test_therapeutic_conflict_micro_dose():
    cfgs = load_duration_configs()
    doc = plan(
        cfgs,
        brand_id="b",
        platform="youtube_shorts",
        locale="en-US",
        format_key="video_short",
        persona="gen_z_professionals",
        intent="therapeutic",
        modality="breathing",
        micro_dose_protocol=False,
    )
    assert any("platform" in w.lower() or "therapeutic" in w.lower() for w in doc["warnings"]) or doc.get("blockers")


def test_persona_cap_ddiscovery():
    cfgs = load_duration_configs()
    doc = plan(
        cfgs,
        brand_id="b",
        platform="youtube",
        locale="en-US",
        format_key="video_long",
        persona="gen_alpha_students",
        intent="discovery",
        modality=None,
        micro_dose_protocol=False,
    )
    assert doc["recommended_duration_sec"] <= 86400


def test_plan_duration_cli(tmp_path):
    out = tmp_path / "plan.json"
    r = subprocess.run(
        [
            sys.executable,
            str(REPO_ROOT / "scripts" / "duration" / "plan_duration.py"),
            "--format",
            "ebook_standard",
            "--intent",
            "therapeutic",
            "--platform",
            "kdp",
            "-o",
            str(out),
            "--force",
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert r.returncode == 0, r.stderr
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data.get("recommended_page_count") is not None
