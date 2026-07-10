"""Tests for planner-owned accent intelligence v1."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning.accent_planner import (
    attach_accent_plan,
    compute_accent_signature,
    locale_to_cluster,
    plan_accent_beats_for_book,
    resolve_accent_budget,
    validate_accent_plan,
)
from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
from phoenix_v4.planning.enrichment_select import EnrichmentRequest, select_enrichment
from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine

REPO_ROOT = Path(__file__).resolve().parents[2]
ANXIETY_BOOK_IDEA = "prediction-as-evidence swap"
ANXIETY_BOOK_MOTIF = "The Alarm (chest and phone)"


def _enriched_burnout(seed: str = "4242"):
    fmt = load_format_spec("standard_book", REPO_ROOT)
    spine = load_spine("burnout", REPO_ROOT, runtime_format="standard_book")
    shaped = apply_knobs(
        spine,
        load_knob_profile("burnout", REPO_ROOT),
        runtime_format="standard_book",
    )
    beatmap = compile_beatmap(
        shaped,
        load_topic_engines("burnout", REPO_ROOT),
        fmt,
        repo_root=REPO_ROOT,
    )
    return select_enrichment(
        EnrichmentRequest(
            beatmap=beatmap,
            teacher_id=None,
            persona_id="corporate_managers",
            topic_id="burnout",
            seed=seed,
        ),
        repo_root=REPO_ROOT,
    )


def _enriched_anxiety(seed: str = "4242"):
    fmt = load_format_spec("standard_book", REPO_ROOT)
    spine = load_spine("anxiety", REPO_ROOT, runtime_format="standard_book")
    shaped = apply_knobs(
        spine,
        load_knob_profile("anxiety", REPO_ROOT),
        runtime_format="standard_book",
    )
    beatmap = compile_beatmap(
        shaped,
        load_topic_engines("anxiety", REPO_ROOT),
        fmt,
        repo_root=REPO_ROOT,
    )
    return select_enrichment(
        EnrichmentRequest(
            beatmap=beatmap,
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="anxiety",
            seed=seed,
            spine_context={
                "book_idea": ANXIETY_BOOK_IDEA,
                "book_motif": ANXIETY_BOOK_MOTIF,
                "enrichment_contract_v1": True,
            },
        ),
        repo_root=REPO_ROOT,
    )


def test_locale_to_cluster_en_us():
    assert locale_to_cluster("en-US") == "en_US"


def test_pilot_cell_accent_budget_nonzero():
    budget, profile, _ = resolve_accent_budget(
        "stillness_press",
        persona_id="corporate_managers",
        topic_id="burnout",
        repo_root=REPO_ROOT,
    )
    assert profile == "commercial_action"
    assert sum(budget.values()) >= 3


def test_anxiety_pilot_budget_includes_rq_and_ts():
    budget, profile, _ = resolve_accent_budget(
        "stillness_press",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        enrichment_contract_v1=True,
        repo_root=REPO_ROOT,
    )
    assert profile == "somatic_reflective"
    assert budget.get("REFLECTION_QUESTION", 0) >= 3
    assert budget.get("TROUBLESHOOTING", 0) >= 1


def test_accent_signature_stable():
    rows = [
        {"chapter": 2, "class": "EXTERNAL_STORY", "position": "after_REFLECTION"},
        {"chapter": 5, "class": "CITED_EVIDENCE", "position": "after_HOOK"},
    ]
    budget = {"EXTERNAL_STORY": 1, "CITED_EVIDENCE": 1}
    assert compute_accent_signature(rows, accent_budget=budget) == compute_accent_signature(
        rows, accent_budget=budget
    )


def test_insert_accent_beats_preserves_planner_only():
    from phoenix_v4.rendering.accent_renderer import insert_accent_beats_into_streams

    types_ = ["HOOK", "REFLECTION", "EXERCISE", "INTEGRATION"]
    proses = ["hook body", "reflection body", "exercise body", "integration body"]
    beats = [
        {
            "class": "CITED_EVIDENCE",
            "accent_id": "burn_who_occupational_burnout_2019",
            "position": "after_HOOK",
            "keys": {},
        }
    ]
    bodies = {"burn_who_occupational_burnout_2019": "Evidence paragraph with handoff to scene."}
    out_types, out_proses, rendered = insert_accent_beats_into_streams(types_, proses, beats, bodies)
    assert len(out_types) == 5
    assert rendered[0]["accent_id"] == "burn_who_occupational_burnout_2019"


@pytest.mark.slow
def test_attach_accent_plan_burnout_sparse_classes():
    planned = attach_accent_plan(
        _enriched_burnout(),
        brand_id="stillness_press",
        seed="4242",
        repo_root=REPO_ROOT,
    )
    ctx = planned.spine_context or {}
    assert ctx.get("accent_signature")
    classes = {r["class"] for r in (ctx.get("accent_assignments") or [])}
    assert {"EXTERNAL_STORY", "CITED_EVIDENCE", "ENCOURAGEMENT"}.issubset(classes)
    assert not validate_accent_plan(planned)


@pytest.mark.slow
def test_anxiety_pilot_authored_rq_ts_lands_without_fallback():
    enriched = _enriched_anxiety()
    plan = plan_accent_beats_for_book(
        enriched,
        brand_id="stillness_press",
        seed="4242",
        teacher_mode=False,
        repo_root=REPO_ROOT,
    )
    planned = attach_accent_plan(
        enriched,
        brand_id="stillness_press",
        seed="4242",
        teacher_mode=False,
        repo_root=REPO_ROOT,
    )
    strategy = (planned.enrichment_audit or {}).get("enrichment_strategy_report") or {}
    alignment = (planned.enrichment_audit or {}).get("bestseller_alignment_report") or {}

    rq_rows = [r for r in plan.flat_rows if r.get("class") == "REFLECTION_QUESTION"]
    ts_rows = [r for r in plan.flat_rows if r.get("class") == "TROUBLESHOOTING"]
    assert len(rq_rows) >= 3
    assert len(ts_rows) >= 1

    for row in rq_rows + ts_rows:
        assert str(row.get("accent_id", "")).startswith(("rq_anxiety_", "ts_anxiety_"))
        assert row.get("supply_source") == "authored_bank"

    provenance = strategy.get("supply_provenance_by_class") or {}
    assert provenance.get("REFLECTION_QUESTION") == "authored_bank"
    assert provenance.get("TROUBLESHOOTING") == "authored_bank"

    supported = alignment.get("supported_underfilled_budget_by_class") or {}
    assert int(supported.get("REFLECTION_QUESTION", 0)) == 0
    assert int(supported.get("TROUBLESHOOTING", 0)) == 0
    assert alignment.get("status") == "PASS"

    assert strategy.get("book_idea") == ANXIETY_BOOK_IDEA
    assert strategy.get("book_motif") == ANXIETY_BOOK_MOTIF
    assert not validate_accent_plan(planned)
