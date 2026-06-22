"""Freebie planner — workbook buyer-only gate and email slot enrichment."""
from __future__ import annotations

from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def registry_and_rules():
    import yaml

    reg = yaml.safe_load((REPO / "config/freebies/freebie_registry.yaml").read_text(encoding="utf-8"))
    rules = yaml.safe_load((REPO / "config/freebies/freebie_selection_rules.yaml").read_text(encoding="utf-8"))
    return reg.get("freebies") or {}, rules


def test_workbook_stripped_without_buyer(registry_and_rules):
    from phoenix_v4.planning.freebie_planner import _filter_workbooks_unless_buyer

    freebies_map, rules = registry_and_rules
    bundle = ["burnout_checklist_v1", "companion_core_v2"]
    filtered = _filter_workbooks_unless_buyer(bundle, freebies_map, rules, buyer=False)
    assert "companion_core_v2" not in filtered
    assert "burnout_checklist_v1" in filtered


def test_workbook_kept_with_buyer(registry_and_rules):
    from phoenix_v4.planning.freebie_planner import _filter_workbooks_unless_buyer

    freebies_map, rules = registry_and_rules
    bundle = ["companion_core_v2"]
    filtered = _filter_workbooks_unless_buyer(bundle, freebies_map, rules, buyer=True)
    assert "companion_core_v2" in filtered


def test_companion_rule_skipped_pre_purchase(registry_and_rules):
    from phoenix_v4.planning.freebie_planner import plan_freebies

    freebies_map, _ = registry_and_rules
    book_spec = {"topic_id": "topic_not_in_funnel_map", "persona_id": "gen_z_professionals"}
    format_plan = {"chapter_count": 20}
    compiled = {"chapter_slot_sequence": [["EXERCISE"]]}
    arc = {"engine": "burnout", "emotional_curve": [3, 4, 5]}
    bundle, _, _ = plan_freebies(
        book_spec,
        format_plan,
        compiled,
        arc,
        registry_path=REPO / "config/freebies/freebie_registry.yaml",
        rules_path=REPO / "config/freebies/freebie_selection_rules.yaml",
    )
    types = {freebies_map[fid].get("type") for fid in bundle if fid in freebies_map}
    assert "companion_workbook_pdf" not in types


def test_email_slot_enrichment():
    from phoenix_v4.planning.freebie_email_slots import enrich_bundle_with_slots, email_slot_for_type

    assert email_slot_for_type("checklist_pdf") == "bonus_pre_story"
    assert email_slot_for_type("companion_workbook_pdf") == "post_purchase"

    freebies_map = {
        "x1": {"type": "checklist_pdf", "output_formats": ["pdf"]},
        "x2": {"type": "companion_workbook_pdf", "output_formats": ["pdf"]},
    }
    rows = enrich_bundle_with_slots(
        [{"freebie_id": "x1", "formats": ["pdf"]}, {"freebie_id": "x2", "formats": ["pdf"]}],
        freebies_map,
        buyer=False,
    )
    by_id = {r["freebie_id"]: r for r in rows}
    assert by_id["x1"]["email_slot"] == "bonus_pre_story"
    assert by_id["x2"]["requires_buyer_tag"] is True


def test_archetype_resolver():
    from phoenix_v4.planning.freebie_archetype import resolve_archetype_for_topic

    row = resolve_archetype_for_topic("compassion_fatigue")
    assert row["primary_archetype_id"] == "capacity_assessment"
    assert row["e2_somatic_app"] == "app22_tonglen.html"
    assert row["funnel_slug"] == "compassion-fatigue-audit"
