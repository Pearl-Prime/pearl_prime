"""Integration tests for EI v2 dimension gates + hybrid production wiring in bestseller_editor."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.qa import bestseller_editor as be
from phoenix_v4.qa.bestseller_editor import (
    build_bestseller_editor_report,
    hybrid_select_slot_production,
)
from phoenix_v4.quality.ei_v2.hybrid_selector import HybridDecision


def _minimal_plan() -> dict:
    return {
        "plan_hash": "wiring_test",
        "atom_ids": [],
        "chapter_slot_sequence": [],
    }


def test_editor_report_fails_when_dimension_gates_block_delivery(tmp_path: Path) -> None:
    (tmp_path / "chapter_flow_report.json").write_text(
        json.dumps(
            {
                "chapter_count": 1,
                "status": "PASS",
                "chapters": [{"chapter": 1, "status": "PASS", "score": 100, "errors": []}],
                "dimension_gates_status": "FAIL",
                "dimension_gates_blocks_delivery": True,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "budget.json").write_text(json.dumps({}), encoding="utf-8")

    report = build_bestseller_editor_report(_minimal_plan(), tmp_path)
    assert report["dimension_gates_blocks_delivery"] is True
    assert report["dimension_gate_status"] == "FAIL"
    assert report["status"] == "FAIL"


def test_editor_report_pass_when_dimension_gates_skipped(tmp_path: Path) -> None:
    (tmp_path / "chapter_flow_report.json").write_text(
        json.dumps(
            {
                "chapter_count": 1,
                "status": "PASS",
                "chapters": [],
                "dimension_gates_status": "SKIP",
                "dimension_gates_blocks_delivery": False,
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "budget.json").write_text(json.dumps({}), encoding="utf-8")

    report = build_bestseller_editor_report(_minimal_plan(), tmp_path)
    assert report["dimension_gate_status"] == "PASS"
    assert report["dimension_gates_status"] == "SKIP"
    # Dimension gates are a no-op; overall status may be WARN if book_pass falls back in CI.
    assert report["status"] in ("PASS", "WARN")


def test_hybrid_select_slot_production_passes_v2_cfg_when_hybrid_enabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict = {}

    def fake_hybrid_select(**kwargs: object) -> HybridDecision:
        captured.update(kwargs)
        return HybridDecision(
            slot="HOOK",
            chapter_index=0,
            slot_index=0,
            final_chosen_id="a1",
            v1_chosen_id="a1",
            v2_chosen_id="a1",
            override_applied=False,
        )

    monkeypatch.setattr(
        "phoenix_v4.quality.ei_v2.hybrid_selector.hybrid_select",
        fake_hybrid_select,
    )

    cfg = {"hybrid": {"enabled": True}, "marker": 42}
    hybrid_select_slot_production(
        slot="HOOK",
        chapter_index=0,
        slot_index=0,
        candidates_raw=[{"atom_id": "a1"}],
        persona_id="p",
        topic_id="t",
        thesis="th",
        ei_v2_config=cfg,
    )
    assert captured.get("v2_cfg") == cfg


def test_hybrid_select_slot_production_omits_v2_cfg_when_hybrid_disabled(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict = {}

    def fake_hybrid_select(**kwargs: object) -> HybridDecision:
        captured.update(kwargs)
        return HybridDecision(
            slot="HOOK",
            chapter_index=0,
            slot_index=0,
            final_chosen_id="a1",
            v1_chosen_id="a1",
            v2_chosen_id="a1",
            override_applied=False,
        )

    monkeypatch.setattr(
        "phoenix_v4.quality.ei_v2.hybrid_selector.hybrid_select",
        fake_hybrid_select,
    )

    cfg = {"hybrid": {"enabled": False}}
    hybrid_select_slot_production(
        slot="HOOK",
        chapter_index=0,
        slot_index=0,
        candidates_raw=[{"atom_id": "a1"}],
        persona_id="p",
        topic_id="t",
        thesis="th",
        ei_v2_config=cfg,
    )
    assert captured.get("v2_cfg") is None


def test_dimension_gate_rollup_helpers() -> None:
    assert (
        be._dimension_gate_rollup_status(
            {"dimension_gates_blocks_delivery": True, "dimension_gates_status": "PASS"}
        )
        == "FAIL"
    )
    assert be._dimension_gate_rollup_status({"dimension_gates_status": "SKIP"}) == "PASS"


def test_chapter_flow_gate_report_skips_dimension_gates_when_disabled_in_config() -> None:
    from phoenix_v4.rendering.book_renderer import chapter_flow_gate_report

    long_body = " ".join(["breath"] * 40) + " " + " ".join(["shoulder"] * 10)
    plan = {"chapter_slot_sequence": [["HOOK"]], "atom_ids": ["placeholder:HOOK:ch0:slot0"]}
    prose = {"placeholder:HOOK:ch0:slot0": long_body}
    r = chapter_flow_gate_report(
        "",
        plan=plan,
        prose_map=prose,
        ei_v2_config={"dimension_gates": {"enabled": False}},
    )
    assert r["dimension_gates_status"] == "SKIP"
    assert r["dimension_gates_blocks_delivery"] is False
    assert "dimension_gates" not in r["chapters"][0]
