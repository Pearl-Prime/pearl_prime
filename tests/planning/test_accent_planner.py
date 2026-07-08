"""Tests for planner-owned accent intelligence v1."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning.accent_planner import (
    attach_accent_plan,
    compute_accent_signature,
    locale_to_cluster,
    resolve_accent_budget,
    validate_accent_plan,
)
from phoenix_v4.planning.beatmap_compile import compile_beatmap, load_format_spec, load_topic_engines
from phoenix_v4.planning.enrichment_select import EnrichmentRequest, select_enrichment
from phoenix_v4.planning.knob_apply import apply_knobs, load_knob_profile, load_spine
from phoenix_v4.rendering.accent_renderer import insert_accent_beats_into_streams

REPO_ROOT = Path(__file__).resolve().parents[2]


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
