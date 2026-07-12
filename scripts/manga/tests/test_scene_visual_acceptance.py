"""Candidate quarantine / acceptance routing tests."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

import structural_composition as sc  # noqa: E402
import validate_scene_assembly_visual as vsa  # noqa: E402


def _good_envelope():
    bundle = {
        "schema_version": "1.0.0",
        "bundle_id": "b1",
        "panel_id": "p_accept",
        "panel_type_id": "dialogue_seated_table",
        "structural_template_id": "seated_table_scene",
        "canvas": {"width": 1000, "height": 1000},
        "nodes": [
            {
                "node_id": "seat",
                "category": "support_surface",
                "role": "seat_or_table",
                "support_polygon_pct": [[30, 55], [70, 55], [72, 75], [28, 75]],
            },
            {
                "node_id": "char",
                "category": "character",
                "role": "primary_subject",
                "contact_point_pct": [0.0, 0.0],
            },
        ],
        "edges": [
            {"edge_id": "e1", "relation": "seated_on", "from_node": "char", "to_node": "seat"}
        ],
        "placements": [
            {
                "node_id": "char",
                "transform": {
                    "tx_pct": 50.0,
                    "ty_pct": 65.0,
                    "uniform_scale": 1.0,
                    "rotation_deg": 0.0,
                },
            }
        ],
    }
    return sc.build_plan_envelope(bundle)


def test_candidate_without_verdict_stays_quarantined(tmp_path: Path):
    root = tmp_path / "cand_root"
    vsa.ensure_quarantine_tree(root)
    env = _good_envelope()
    plan_path = root / "plans" / "p_accept_plan.json"
    plan_path.write_text(json.dumps(env, indent=2))
    report = vsa.run_structural_validation(plan_path, root)
    assert report["status"] == "pass"
    cand = vsa.stage_candidate(plan_path, root, report)
    status = json.loads((cand / "status.json").read_text())
    assert status["quarantined"] is True
    assert status["operator_verdict"] is None
    assert not (root / "accepted" / cand.name).exists()
    assert vsa.candidate_has_operator_verdict(cand) is False


def test_stale_verdict_cannot_promote_changed_candidate(tmp_path: Path):
    root = tmp_path / "cand_root"
    vsa.ensure_quarantine_tree(root)
    env = _good_envelope()
    plan_path = root / "plans" / "p_accept_plan.json"
    plan_path.write_text(json.dumps(env, indent=2))
    report = vsa.run_structural_validation(plan_path, root)
    cand = vsa.stage_candidate(plan_path, root, report)
    # Mutate candidate plan hash body
    mutated = json.loads((cand / "plan_envelope.json").read_text())
    mutated["plan_body"]["panel_id"] = "changed"
    mutated["plan_hash"] = sc.compute_plan_hash(mutated["plan_body"])
    (cand / "plan_envelope.json").write_text(json.dumps(mutated, indent=2))
    old_hash = env["plan_hash"]
    with pytest.raises(sc.StructuralHardFail) as ei:
        vsa.apply_operator_verdict(
            cand,
            verdict="pass",
            expected_plan_hash=old_hash,
        )
    assert ei.value.code == "STALE_VERDICT"
    assert not (root / "accepted" / cand.name).exists()


def test_accepted_only_mode_refuses_non_accepted(tmp_path: Path):
    root = tmp_path / "cand_root"
    vsa.ensure_quarantine_tree(root)
    env = _good_envelope()
    plan_path = root / "plans" / "p_accept_plan.json"
    plan_path.write_text(json.dumps(env, indent=2))
    with pytest.raises(sc.StructuralHardFail) as ei:
        vsa.assert_accepted_only(plan_path, root)
    assert ei.value.code == "ACCEPTED_ONLY_REFUSED"

    # After promote, accepted path is allowed
    report = vsa.run_structural_validation(plan_path, root)
    cand = vsa.stage_candidate(plan_path, root, report)
    vsa.apply_operator_verdict(cand, verdict="pass", expected_plan_hash=env["plan_hash"])
    accepted_plan = root / "accepted" / cand.name / "plan_envelope.json"
    vsa.assert_accepted_only(accepted_plan, root)  # no raise


def test_promote_pass_copies_to_accepted(tmp_path: Path):
    root = tmp_path / "cand_root"
    vsa.ensure_quarantine_tree(root)
    env = _good_envelope()
    plan_path = root / "plans" / "p_accept_plan.json"
    plan_path.write_text(json.dumps(env, indent=2))
    report = vsa.run_structural_validation(plan_path, root)
    cand = vsa.stage_candidate(plan_path, root, report)
    promo = vsa.apply_operator_verdict(
        cand, verdict="pass", expected_plan_hash=env["plan_hash"]
    )
    assert promo["result"] == "accepted"
    assert (root / "accepted" / cand.name / "plan_envelope.json").is_file()
    assert (root / "promotion_records" / f"{cand.name}_accepted.json").is_file()


def test_support_overlay_emitted_during_validation(tmp_path: Path):
    root = tmp_path / "cand_root"
    vsa.ensure_quarantine_tree(root)
    env = _good_envelope()
    plan_path = root / "plans" / "p_accept_plan.json"
    plan_path.write_text(json.dumps(env, indent=2))
    report = vsa.run_structural_validation(plan_path, root)
    assert report["support_overlay"]["same_resolved_transform_path"] is True
