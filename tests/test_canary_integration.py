"""
Integration tests for bestseller canary (scripts/canary/run_bestseller_canary.py).
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_canary_module():
    path = REPO_ROOT / "scripts" / "canary" / "run_bestseller_canary.py"
    spec = importlib.util.spec_from_file_location("run_bestseller_canary", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_bestseller_canary"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def canary_mod():
    mod = _load_canary_module()
    yield mod
    sys.modules.pop("run_bestseller_canary", None)


def test_canary_script_imports_without_error(canary_mod):
    assert canary_mod.run_bestseller_canary is not None
    assert canary_mod.load_merged_ei_config is not None
    assert canary_mod.deep_merge is not None


def test_config_loading_and_override_merging(canary_mod):
    merged = canary_mod.load_merged_ei_config(REPO_ROOT)
    assert merged["dimension_gates"]["fail_mode"] == "block"
    assert merged["dimension_gates"]["dimension_gate_phase"] == 3
    blocked = merged["dimension_gates"]["blocked_dimensions"]
    assert "engagement" in blocked
    assert "cohesion" in blocked
    assert "listen_experience" in blocked
    # Base keys preserved
    assert "enabled" in merged["dimension_gates"]
    assert merged["llm_quality"]["enabled"] is False


def test_deep_merge_nested(canary_mod):
    base = {"dimension_gates": {"enabled": True, "fail_mode": "warn", "nested": {"a": 1}}}
    over = {"dimension_gates": {"fail_mode": "block", "nested": {"b": 2}}}
    m = canary_mod.deep_merge(base, over)
    assert m["dimension_gates"]["enabled"] is True
    assert m["dimension_gates"]["fail_mode"] == "block"
    assert m["dimension_gates"]["nested"]["a"] == 1
    assert m["dimension_gates"]["nested"]["b"] == 2


def test_sentinel_tuple_finds_valid_engine_and_prose(canary_mod):
    merged = canary_mod.load_merged_ei_config(REPO_ROOT)
    persona, topic, engine, fmt, story_path, text = canary_mod.resolve_sentinel_tuple(REPO_ROOT, merged)
    assert persona == "gen_z_professionals"
    assert topic == "overthinking"
    assert engine  # reflection missing in atoms → fallback
    assert story_path.is_file()
    assert len(text.split()) >= 15


def test_evidence_directory_creation(canary_mod, tmp_path):
    ev = tmp_path / "ev1"
    d = canary_mod.ensure_evidence_dir(REPO_ROOT, ev)
    assert d.is_dir()
    d2 = canary_mod.ensure_evidence_dir(REPO_ROOT, None)
    assert "artifacts" in str(d2) and "canary" in str(d2)


def test_canary_summary_schema(canary_mod, tmp_path):
    ev = tmp_path / "canary_out"
    code, summary = canary_mod.run_bestseller_canary(repo_root=REPO_ROOT, evidence_dir=ev)
    assert isinstance(code, int)
    for key in (
        "canary_version",
        "pipeline_reference",
        "gates_passed",
        "gates_blocked",
        "gates_missing",
        "missing_modules",
        "overall_status",
        "evidence_dir",
        "sentinel",
        "errors",
    ):
        assert key in summary
    # safety_classifier present on successful gate path
    if summary["overall_status"] != "ERROR":
        assert "safety_classifier" in summary
    summary_path = Path(summary["evidence_dir"]) / "canary_summary.json"
    assert summary_path.is_file()
    data = json.loads(summary_path.read_text(encoding="utf-8"))
    assert data["canary_version"] == 1


def test_graceful_handling_when_gate_module_import_fails(canary_mod, tmp_path):
    ev = tmp_path / "canary_import_fail"
    with patch.object(canary_mod, "_import_dimension_gates", return_value=(None, "simulated ImportError")):
        code, summary = canary_mod.run_bestseller_canary(repo_root=REPO_ROOT, evidence_dir=ev)
    assert code == 2
    assert "phoenix_v4.quality.ei_v2.dimension_gates" in summary["missing_modules"]
    assert summary["overall_status"] == "ERROR"
    assert (Path(summary["evidence_dir"]) / "canary_summary.json").is_file()


def test_mock_single_chapter_pipeline_evidence_files(canary_mod, tmp_path):
    """End-to-end: one chapter slice produces full evidence bundle."""
    ev = tmp_path / "bundle"
    code, summary = canary_mod.run_bestseller_canary(repo_root=REPO_ROOT, evidence_dir=ev)
    base = Path(summary["evidence_dir"])
    assert (base / "canary_summary.json").is_file()
    assert (base / "chapter_gates_detail.json").is_file()
    assert (base / "safety_classifier_snapshot.json").is_file()
    assert (base / "canary_stdout.txt").is_file()
    detail = json.loads((base / "chapter_gates_detail.json").read_text(encoding="utf-8"))
    assert "gates" in detail
    assert detail["excerpt_word_count"] > 0
    assert summary["gates_missing"] == []
    assert code in (0, 1, 2)
