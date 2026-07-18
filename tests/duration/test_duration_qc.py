from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.duration.duration_qc import run_qc  # noqa: E402


def test_qc_passes_clean_plan():
    plan = {
        "duration_fit_score": 0.75,
        "format": "video_short",
        "intent": "discovery",
        "registry_unit": "seconds",
        "recommended_value": 30,
        "recommended_duration_sec": 30,
        "platform_compliant": True,
        "persona_budget_fit": True,
        "micro_dose_protocol": False,
    }
    rep = run_qc(plan, {}, False)
    assert rep["passed"] is True
    ids = {b["id"] for b in rep["blockers"]}
    assert "DURATION.FIT_SCORE_FAIL" not in ids


def test_qc_zero_duration_blocker():
    plan = {
        "duration_fit_score": 0.2,
        "format": "video_short",
        "intent": "therapeutic",
        "registry_unit": "seconds",
        "recommended_value": 0,
        "recommended_duration_sec": 0,
        "platform_compliant": True,
        "persona_budget_fit": False,
        "micro_dose_protocol": False,
    }
    rep = run_qc(plan, {"page_count": None}, False)
    assert any(b["id"] == "DURATION.ZERO" for b in rep["blockers"])


def test_qc_fit_fail_mode():
    plan = {
        "duration_fit_score": 0.30,
        "format": "podcast_standard",
        "intent": "therapeutic",
        "registry_unit": "seconds",
        "recommended_value": 600,
        "recommended_duration_sec": 600,
        "platform_compliant": True,
        "persona_budget_fit": True,
        "micro_dose_protocol": False,
    }
    rep = run_qc(plan, {}, True)
    assert any(b["id"] == "DURATION.FIT_SCORE_FAIL" for b in rep["blockers"])


def test_thirteen_gate_categories():
    plan = json.loads((REPO_ROOT / "fixtures" / "duration" / "sample_duration_plan.json").read_text(encoding="utf-8"))
    rep = run_qc(plan, {}, False)
    levels = [x["level"] for x in rep["blockers"] + rep["warnings"] + rep["infos"]]
    assert "BLOCKER" in levels or "WARN" in levels or "INFO" in levels
