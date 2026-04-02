"""EI v2 visual therapeutic dimensions."""
from __future__ import annotations

from phoenix_v4.quality.ei_v2.config import load_ei_v2_config, invalidate_ei_v2_config_cache
from phoenix_v4.quality.ei_v2.dimension_gates import gate_vt_stealth_text, run_visual_therapeutic_dimension_gates
from phoenix_v4.quality.ei_v2.visual_therapeutic import (
    compute_visual_therapeutic_scores,
    vt_stealth,
)


def test_vt_stealth_zero_on_forbidden_term():
    invalidate_ei_v2_config_cache()
    cfg = load_ei_v2_config()
    assert vt_stealth("This is about therapy today.", cfg=cfg) == 0.0
    assert vt_stealth("They walked by the river.", cfg=cfg) == 1.0


def test_gate_vt_stealth_text():
    invalidate_ei_v2_config_cache()
    g = gate_vt_stealth_text("mindfulness workshop")
    assert g.status == "FAIL"


def test_compute_visual_therapeutic_scores_composite():
    invalidate_ei_v2_config_cache()
    cfg = load_ei_v2_config()
    artifacts = {
        "breath": {"breath_sequences": [{"valid": True, "phases_present": ["inhale", "hold", "exhale", "pause"]}], "pages": []},
        "color_arc": {"panels": [{"color_temp_target": 5800 + i * 10} for i in range(10)]},
        "fractal": {"panels": [{"fd_estimate": 1.4, "compliant": True}]},
        "gutter": {"transitions": [{"gutter_class": "wide"}, {"gutter_class": "breath"}]},
        "chapter": {"pages": []},
    }
    scores = compute_visual_therapeutic_scores(artifacts, dialogue_text="safe dialogue", cfg=cfg)
    for k in ("vt_parasympathetic", "vt_processing", "vt_somatic", "vt_stealth", "ite_score"):
        assert k in scores
        assert 0.0 <= scores[k] <= 1.0


def test_run_visual_therapeutic_dimension_gates_enabled():
    invalidate_ei_v2_config_cache()
    cfg = load_ei_v2_config()
    if not (cfg.get("visual_therapeutic") or {}).get("enabled"):
        return
    artifacts = {
        "breath": {"breath_sequences": [{"valid": True}], "pages": []},
        "color_arc": {"panels": [{"color_temp_target": 6000}]},
        "fractal": {"panels": [{"compliant": True, "fd_estimate": 1.4}]},
        "gutter": {"transitions": [{"gutter_class": "standard"}]},
        "chapter": {"pages": []},
    }
    rep = run_visual_therapeutic_dimension_gates(artifacts, dialogue_text="ok", ei_cfg=cfg)
    assert rep.overall_status in ("PASS", "WARN", "FAIL")
    assert len(rep.gates) == 4
