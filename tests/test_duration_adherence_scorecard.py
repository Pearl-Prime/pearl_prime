"""Tests for duration adherence scorecard."""
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.ops.duration_adherence_scorecard import (
    _clamp01,
    generate_synthetic_outputs,
    grade_from_score,
    run,
    score_arc_fidelity,
    score_chapter_adherence,
    score_duration_adherence,
    score_slot_budget_adherence,
    score_word_adherence,
)

try:
    import yaml
except ImportError:
    yaml = None


def _load_config():
    p = REPO_ROOT / "config" / "duration_scorecard.yaml"
    if not p.exists() or yaml is None:
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


def _load_registry():
    p = REPO_ROOT / "config" / "format_selection" / "format_registry.yaml"
    if not p.exists() or yaml is None:
        return {}
    with open(p) as f:
        return yaml.safe_load(f) or {}


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


def test_config_file_exists():
    assert (REPO_ROOT / "config" / "duration_scorecard.yaml").exists()


def test_config_has_required_keys():
    cfg = _load_config()
    sc = cfg.get("duration_adherence_scorecard", {})
    assert "weights" in sc
    assert "grades" in sc
    assert "slot_word_ceilings" in sc
    assert "tts_wpm" in sc


def test_config_weights_sum_to_one():
    cfg = _load_config()
    weights = cfg.get("duration_adherence_scorecard", {}).get("weights", {})
    total = sum(weights.values())
    assert abs(total - 1.0) < 0.01, f"Weights sum to {total}, expected 1.0"


def test_config_grades_descending():
    cfg = _load_config()
    grades = cfg.get("duration_adherence_scorecard", {}).get("grades", {})
    assert grades.get("A", 0) > grades.get("B", 0)
    assert grades.get("B", 0) > grades.get("C", 0)
    assert grades.get("C", 0) > grades.get("D", 0)


# ---------------------------------------------------------------------------
# Synthetic data generation
# ---------------------------------------------------------------------------


def test_synthetic_generates_all_runtime_formats():
    registry = _load_registry()
    plans = generate_synthetic_outputs(registry, count_per_format=2)
    rt_ids = set(p["runtime_format"] for p in plans)
    expected = set((registry.get("runtime_formats") or {}).keys())
    assert rt_ids == expected, f"Missing formats: {expected - rt_ids}"


def test_synthetic_plans_have_chapters():
    registry = _load_registry()
    plans = generate_synthetic_outputs(registry, count_per_format=1)
    for p in plans:
        assert len(p["chapters"]) > 0, f"No chapters in {p['_source_path']}"
        for ch in p["chapters"]:
            assert len(ch["slots"]) > 0


def test_synthetic_plans_have_word_counts():
    registry = _load_registry()
    plans = generate_synthetic_outputs(registry, count_per_format=1)
    for p in plans:
        assert p["total_word_count"] > 0


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------


def test_word_adherence_perfect():
    """Plans exactly within range should score 1.0."""
    plans = [{"runtime_format": "standard_book", "total_word_count": 10000, "chapters": []}]
    rt = {"standard_book": {"word_range": [9000, 11000]}}
    score, detail = score_word_adherence(plans, rt)
    assert score == 1.0
    assert detail["within_range"] == 1


def test_word_adherence_outside():
    """Plans outside range should score 0."""
    plans = [{"runtime_format": "standard_book", "total_word_count": 5000, "chapters": []}]
    rt = {"standard_book": {"word_range": [9000, 11000]}}
    score, detail = score_word_adherence(plans, rt)
    assert score == 0.0
    assert detail["within_range"] == 0


def test_chapter_adherence_exact():
    plans = [{"runtime_format": "standard_book", "chapters": [{}] * 12}]
    registry = {"runtime_formats": {"standard_book": {"chapter_count_default": 12}}}
    score, detail = score_chapter_adherence(plans, registry)
    assert score == 1.0


def test_chapter_adherence_off_by_one():
    plans = [{"runtime_format": "standard_book", "chapters": [{}] * 11}]
    registry = {"runtime_formats": {"standard_book": {"chapter_count_default": 12}}}
    score, detail = score_chapter_adherence(plans, registry)
    # Off by 1: exact=0, close=1 → 0.70*0 + 0.30*1 = 0.30
    assert abs(score - 0.30) < 0.01


def test_duration_adherence_within_tolerance():
    cfg = {"duration_adherence_scorecard": {"tts_wpm": 150, "duration_tolerance_pct": 10}}
    # 55 min target × 150 WPM = 8250 words
    plans = [{"runtime_format": "standard_book", "total_word_count": 8250, "chapters": []}]
    rt = {"standard_book": {"duration_minutes": 55}}
    score, detail = score_duration_adherence(plans, rt, cfg)
    assert score == 1.0


def test_arc_fidelity_rising():
    """Perfect rising arc should score well."""
    chapters = [{"emotional_intensity": 0.3 + 0.5 * i / 9} for i in range(10)]
    plans = [{"chapters": chapters}]
    score, detail = score_arc_fidelity(plans)
    assert score > 0.9


def test_arc_fidelity_flat():
    """Flat arc should score ~0.5."""
    chapters = [{"emotional_intensity": 0.5} for _ in range(10)]
    plans = [{"chapters": chapters}]
    score, detail = score_arc_fidelity(plans)
    assert 0.4 <= score <= 0.6


# ---------------------------------------------------------------------------
# Grade assignment
# ---------------------------------------------------------------------------


def test_grade_a():
    assert grade_from_score(0.95, {"A": 0.90, "B": 0.80, "C": 0.70, "D": 0.60}) == "A"


def test_grade_f():
    assert grade_from_score(0.50, {"A": 0.90, "B": 0.80, "C": 0.70, "D": 0.60}) == "F"


# ---------------------------------------------------------------------------
# Full run (integration)
# ---------------------------------------------------------------------------


def test_full_run_synthetic():
    config = _load_config()
    registry = _load_registry()
    if not config or not registry:
        pytest.skip("Config or registry not available")
    plans = generate_synthetic_outputs(registry, count_per_format=2)
    result = run(config, registry, plans, "2026-03-31")
    assert "composite_score" in result
    assert "overall_grade" in result
    assert result["overall_grade"] in ("A", "B", "C", "D", "F")
    assert result["n_outputs_scored"] == len(plans)
    assert len(result["per_runtime_format"]) > 0
    assert len(result["per_structural_format"]) > 0
    assert "worst_offenders" in result


def test_full_run_empty():
    config = _load_config()
    registry = _load_registry()
    if not config or not registry:
        pytest.skip("Config or registry not available")
    result = run(config, registry, [], "2026-03-31")
    assert result["n_outputs_scored"] == 0
    assert result["overall_grade"] in ("A", "B", "C", "D", "F")


def test_clamp01():
    assert _clamp01(-0.5) == 0.0
    assert _clamp01(1.5) == 1.0
    assert _clamp01(0.5) == 0.5
