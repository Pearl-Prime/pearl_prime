"""Tests for planner-owned accent intelligence v1."""
from __future__ import annotations

from pathlib import Path

import pytest

from phoenix_v4.planning.accent_planner import (
    _load_author_disclosure,
    attach_accent_plan,
    build_enhancement_contract_v21_summary,
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


def _enriched_gen_z_sleep_anxiety(seed: str = "4242"):
    """AUTHOR_DISCLOSURE supply-extension cell (2026-07-14): gen_z_professionals x
    sleep_anxiety x ravi_chandra. Same author + persona as the anxiety pilot, a
    different topic he is already registered for (config/author_registry.yaml),
    chosen because it is the only one of the three extension topics with complete
    TEACHER_DOCTRINE atom coverage for gen_z_professionals today (overthinking and
    social_anxiety are missing that atom slot for this persona — a pre-existing,
    unrelated content gap, not an AUTHOR_DISCLOSURE issue)."""
    fmt = load_format_spec("standard_book", REPO_ROOT)
    spine = load_spine("sleep_anxiety", REPO_ROOT, runtime_format="standard_book")
    shaped = apply_knobs(
        spine,
        load_knob_profile("sleep_anxiety", REPO_ROOT),
        runtime_format="standard_book",
    )
    beatmap = compile_beatmap(
        shaped,
        load_topic_engines("sleep_anxiety", REPO_ROOT),
        fmt,
        repo_root=REPO_ROOT,
    )
    return select_enrichment(
        EnrichmentRequest(
            beatmap=beatmap,
            teacher_id=None,
            persona_id="gen_z_professionals",
            topic_id="sleep_anxiety",
            seed=seed,
            spine_context={
                "enrichment_contract_v1": True,
            },
        ),
        repo_root=REPO_ROOT,
    )


def test_locale_to_cluster_en_us():
    assert locale_to_cluster("en-US") == "en_US"


def test_optional_accent_underfill_blocks_when_budget_requests_accents():
    summary = build_enhancement_contract_v21_summary(
        accent_budget={"QUOTE": 2, "ENCOURAGEMENT": 1},
        flat_rows=[],
        chapter_count=12,
        story_mix_profile="minimal_accent",
        max_accents_per_chapter=2,
    )
    opt = summary["optional_accent_budget"]
    assert opt["zero_optional_accent_policy"]["authorized"] is False
    failures = summary["optional_accent_integrity"]["hard_failures"]
    codes = {row["code"] for row in failures}
    assert "supported_budget_underfill" in codes
    assert "optional_accent_chapter_under_target" in codes


def test_zero_optional_accent_budget_is_explicit_authorized_exception():
    summary = build_enhancement_contract_v21_summary(
        accent_budget={},
        flat_rows=[],
        chapter_count=12,
        story_mix_profile="minimal_accent",
        max_accents_per_chapter=2,
    )
    opt = summary["optional_accent_budget"]
    assert opt["zero_optional_accent_policy"]["authorized"] is True
    assert summary["optional_accent_integrity"]["status"] == "PASS"
    codes = {row["code"] for row in summary["optional_accent_integrity"]["warnings"]}
    assert "zero_optional_accent_exception" in codes


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
    assert budget.get("QUOTE", 0) >= 3
    assert budget.get("ENCOURAGEMENT", 0) >= 2
    assert budget.get("EXTERNAL_STORY", 0) >= 2


def test_flagship_frozen_golden_reconstruction_is_ravi_only():
    from phoenix_v4.planning.accent_planner import _author_commentary_and_disclosure_pools

    commentary, disclosure = _author_commentary_and_disclosure_pools(
        "gen_z_professionals",
        "anxiety",
        "lena_thorne",
        "en_US",
        REPO_ROOT,
    )

    assert len(commentary) == 10
    assert disclosure == []
    assert {row.get("commentary_id") for row in commentary} == {
        "ac_lena_anxiety_observed_charting_v01",
        "ac_lena_anxiety_observed_small_practice_v01",
        "ac_lena_anxiety_admission_panic_ended_it_v01",
        "ac_lena_anxiety_endorsement_helpers_v01",
        "ac_lena_anxiety_skeptic_monitor_v01",
        "ac_lena_anxiety_disclosure_ahjan_v01",
        "ac_lena_anxiety_observed_freeze_v01",
        "ac_lena_anxiety_admission_perform_steady_v01",
        "ac_lena_anxiety_endorsement_small_v01",
        "ac_lena_anxiety_skeptic_hand_on_chest_v01",
    }


def test_allowed_positions_rejects_illegal_placement():
    from phoenix_v4.planning.accent_planner import _position_fit_ok

    entry = {
        "commentary_id": "ac_ravi_anxiety_skeptic_standup_v01",
        "allowed_positions": ["after_EXERCISE"],
        "position_fit": None,
    }
    assert _position_fit_ok(entry, "after_EXERCISE") is True
    assert _position_fit_ok(entry, "after_REFLECTION") is False


def test_external_story_pivot_fit_rejects_cold_hook_and_reflection_stack():
    from phoenix_v4.planning.accent_planner import _position_fit_ok

    entry = {
        "story_id": "ext_anx_business_kodak_digital_v01",
        "position_fit": "supports PIVOT",
    }
    assert _position_fit_ok(entry, "after_HOOK") is False
    assert _position_fit_ok(entry, "after_REFLECTION") is False
    assert _position_fit_ok(entry, "before_STORY") is True


def test_external_story_wrapper_is_authorial_not_apparatus():
    from phoenix_v4.planning.accent_planner import _wrap_external_story

    body = _wrap_external_story(
        "Kodak protected its film business until the market moved without it.",
        "Kodak digital camera invention and bankruptcy arc",
        position="after_HOOK",
    )
    assert "This is not fiction from this book's cast" not in body
    assert "Source:" not in body
    assert body.startswith("The same alarm can scale")


def test_cited_evidence_wrapper_is_body_linked_not_generic_card():
    from phoenix_v4.planning.accent_planner import _wrap_cited_evidence

    body = _wrap_cited_evidence(
        "The brain constantly predicts what the body should feel next.",
        "Barrett LF (2017). How Emotions Are Made.",
        position="before_STORY",
        entry={"evidence_id": "anx_predictive_processing_barrett_2017"},
    )
    assert "A documented finding worth naming before we go further" not in body
    assert body.startswith("That replay has a nervous-system explanation.")
    assert "Carry that explanation back into the scene" in body


def test_story_mix_weights_prefer_intimate_over_mythic():
    from phoenix_v4.planning.accent_planner import _score_entry_for_chapter, _story_mix_profile_data

    intimate = _story_mix_profile_data("intimate_voice", REPO_ROOT)
    timeless = _story_mix_profile_data("timeless_wisdom", REPO_ROOT)
    film_entry = {
        "story_id": "ext_anx_film_inside_out_v01",
        "type": "film",
        "topic_keys": ["anxiety"],
        "body": "A film story about anxiety that is long enough to score.",
        "secular_safe": True,
    }
    mythic_entry = {
        "story_id": "ext_anx_mythic_icarus_v01",
        "type": "mythic",
        "topic_keys": ["anxiety"],
        "body": "A mythic story about anxiety that is long enough to score.",
        "secular_safe": True,
    }
    common = dict(
        accent_class="EXTERNAL_STORY",
        topic_id="anxiety",
        locale_cluster="en_US",
        composite_mode=True,
        chapter_number=3,
        chapter_count=12,
        position="after_REFLECTION",
        book_idea="prediction-as-evidence swap",
        book_motif="The Alarm (chest and phone)",
        seed="story-mix-test",
        persona_id="gen_z_professionals",
    )
    film_intimate = _score_entry_for_chapter(film_entry, story_mix_profile_data=intimate, **common)
    mythic_intimate = _score_entry_for_chapter(mythic_entry, story_mix_profile_data=intimate, **common)
    film_timeless = _score_entry_for_chapter(film_entry, story_mix_profile_data=timeless, **common)
    mythic_timeless = _score_entry_for_chapter(mythic_entry, story_mix_profile_data=timeless, **common)
    assert film_intimate > mythic_intimate
    assert mythic_timeless > film_timeless


@pytest.mark.slow
def test_main_pass_allows_multi_item_class_budget():
    """Budget >1 for a class must be satisfiable without relying only on refill."""
    enriched = _enriched_anxiety()
    plan = plan_accent_beats_for_book(
        enriched,
        brand_id="stillness_press",
        seed="4242",
        teacher_mode=False,
        repo_root=REPO_ROOT,
    )
    by_class = {}
    for row in plan.flat_rows:
        by_class.setdefault(row["class"], []).append(row["chapter"])
    # Multi-item classes should land on distinct chapters via the main spread path.
    for cls in ("REFLECTION_QUESTION", "ENCOURAGEMENT", "EXTERNAL_STORY", "QUOTE"):
        need = int(plan.accent_budget.get(cls, 0))
        if need > 1:
            assert len(by_class.get(cls, [])) >= min(need, 2), f"{cls} under-assigned: {by_class.get(cls)}"
            assert len(set(by_class.get(cls, []))) >= min(need, 2)


@pytest.mark.slow
def test_encouragement_provenance_stable_across_assignments():
    enriched = _enriched_anxiety()
    plan = plan_accent_beats_for_book(
        enriched,
        brand_id="stillness_press",
        seed="4242",
        teacher_mode=False,
        repo_root=REPO_ROOT,
    )
    enc = [r for r in plan.flat_rows if r.get("class") == "ENCOURAGEMENT"]
    assert enc
    provenances = {r.get("supply_source") for r in enc}
    assert provenances == {"atom_pool"}


def test_affirmation_not_in_live_accent_classes():
    from phoenix_v4.planning.accent_planner import ALL_ACCENT_CLASSES

    assert "AFFIRMATION" not in ALL_ACCENT_CLASSES



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
            "keys": {"surface_bucket": "proof_and_embodiment"},
        }
    ]
    bodies = {"burn_who_occupational_burnout_2019": "Evidence paragraph with handoff to scene."}
    out_types, out_proses, rendered = insert_accent_beats_into_streams(types_, proses, beats, bodies)
    assert len(out_types) == 5
    assert rendered[0]["accent_id"] == "burn_who_occupational_burnout_2019"


def test_insert_accent_beats_does_not_double_offset_later_positions():
    from phoenix_v4.rendering.accent_renderer import insert_accent_beats_into_streams

    types_ = ["HOOK", "REFLECTION", "THREAD"]
    proses = ["hook body", "reflection body", "thread body"]
    beats = [
        {
            "class": "QUOTE",
            "accent_id": "quote_01",
            "position": "after_HOOK",
            "keys": {"surface_bucket": "optional_accents"},
        },
        {
            "class": "ENCOURAGEMENT",
            "accent_id": "enc_01",
            "position": "before_THREAD",
            "keys": {"surface_bucket": "optional_accents"},
        },
    ]
    bodies = {
        "quote_01": "Quote body.",
        "enc_01": "Encouragement body.",
    }
    out_types, out_proses, rendered = insert_accent_beats_into_streams(types_, proses, beats, bodies)
    assert out_types == [
        "HOOK",
        "_ACCENT:QUOTE",
        "REFLECTION",
        "_ACCENT:ENCOURAGEMENT",
        "THREAD",
    ]
    assert out_proses[3] == "Encouragement body."
    assert [row["chapter_insert_index"] for row in rendered] == [1, 3]


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
    assert alignment.get("status") in ("PASS", "WARN")
    assert alignment.get("exemplar_config_present") is True

    quote_rows = [r for r in plan.flat_rows if r.get("class") == "QUOTE"]
    assert len(quote_rows) >= 3

    assert strategy.get("book_idea") == ANXIETY_BOOK_IDEA
    assert strategy.get("book_motif") == ANXIETY_BOOK_MOTIF
    v21 = (planned.spine_context or {}).get("enhancement_contract_v21") or {}
    tracked = {row["surface"]: row for row in (v21.get("tracked_surfaces") or [])}
    assert tracked["AUTHOR_DISCLOSURE"]["bucket"] == "proof_and_embodiment"

    # AUTHOR_DISCLOSURE is wired and selectable in general (ALL_ACCENT_CLASSES,
    # selection pools, ACCENT_SELECTION_ORDER all include it), but this exact
    # pilot cell (gen_z_professionals:anxiety) fully excludes it — see
    # _author_commentary_and_disclosure_pools() in accent_planner.py,
    # GOLDEN_5585_SCOPE_AWAY_2026-07-14. This cell is the flagship full-book
    # golden's plan_id (gen_z_professionals_anxiety_twelve_shape_v2, ratified
    # OPD-20260711-PROPRIME-ACCENT-PIPELINE-100PCT). Removing only the
    # guaranteed-minimum floor was NOT sufficient to restore byte parity:
    # splitting 3 entries out of AUTHOR_COMMENTARY (10 -> 7 candidates) changed
    # deterministic per-chapter ranking among the REMAINING commentary
    # candidates too, independent of whether AUTHOR_DISCLOSURE itself is
    # floored. The real fix merges those 3 entries back into the
    # AUTHOR_COMMENTARY candidate pool for THIS cell only (restoring the
    # original 10-candidate ranking universe byte-for-byte) and returns an
    # empty AUTHOR_DISCLOSURE pool here, so provenance is honestly "missing"
    # for this one cell, not "authored_bank" — every other persona/topic cell
    # still gets the real 7+3 split with AUTHOR_DISCLOSURE genuinely available.
    ad_rows = [r for r in plan.flat_rows if r.get("class") == "AUTHOR_DISCLOSURE"]
    assert not ad_rows, (
        "AUTHOR_DISCLOSURE must NOT be selected for gen_z_professionals:anxiety — "
        "this pilot cell is scoped away to protect the frozen flagship golden"
    )
    assert provenance.get("AUTHOR_DISCLOSURE") == "missing", (
        "for this one frozen cell, AUTHOR_DISCLOSURE's pool is genuinely empty "
        "(merged back into AUTHOR_COMMENTARY for ranking purposes) — provenance "
        "should say so honestly rather than claim authored_bank while selecting zero"
    )

    assert tracked["TROUBLESHOOTING"]["bucket"] == "chapter_engine"
    assert tracked["EXTERNAL_STORY"]["bucket"] == "proof_and_embodiment"
    ext_rows = [r for r in plan.flat_rows if r.get("class") == "EXTERNAL_STORY"]
    assert ext_rows
    for row in ext_rows:
        keys = row.get("keys") or {}
        assert keys.get("story_function")
        assert (keys.get("truth_metadata") or {}).get("citation")
        assert "after_HOOK" in (keys.get("preferred_positions") or []) or "before_STORY" in (
            keys.get("preferred_positions") or []
        )
    assert not validate_accent_plan(planned)
# --- AUTHOR_DISCLOSURE supply extension (2026-07-14) ------------------------
# Extends authored AUTHOR_DISCLOSURE supply beyond the single existing
# gen_z_professionals:anxiety pilot bank to other persona/topic cells where the
# SAME already-operator-approved author (ravi_chandra, assets/authors/ravi_chandra/bio.yaml,
# status: operator_approved) is already registered (config/author_registry.yaml
# topic_ids: anxiety, sleep_anxiety, overthinking, social_anxiety, courage). No new
# biographical claims are invented; the existing approved bio_license_refs
# vocabulary is reused and applied to each topic's specific mechanics. The
# gen_z_professionals:anxiety cell itself is untouched — it remains entangled
# with the open #5585/#5595 flagship-golden question.

_AUTHOR_DISCLOSURE_EXTENSION_TOPICS = ("overthinking", "sleep_anxiety", "social_anxiety")


def test_author_disclosure_extension_banks_load_with_valid_schema():
    """Each new AUTHOR_DISCLOSURE cell's authored bank loads real, schema-valid
    entries via the same _load_author_disclosure loader the planner uses —
    proving CODE-WIRED, not just CONFIG-EXISTS."""
    valid_functions = {
        "credibility",
        "vulnerability",
        "companionship",
        "failure_model",
        "turning_point",
        "limits_of_authority",
    }
    for topic in _AUTHOR_DISCLOSURE_EXTENSION_TOPICS:
        rows = _load_author_disclosure(topic, "ravi_chandra", "en_US", REPO_ROOT)
        assert len(rows) == 3, f"{topic}: expected 3 authored disclosures, got {len(rows)}"
        for row in rows:
            assert row.get("disclosure_id", "").startswith("ad_ravi_")
            assert row.get("disclosure_function") in valid_functions
            assert row.get("bio_license_refs"), f"{topic}: entry missing bio_license_refs"
            assert row.get("allowed_positions"), f"{topic}: entry missing allowed_positions"
            variants = row.get("position_variants") or {}
            assert variants, f"{topic}: entry missing position_variants"
            for position in row["allowed_positions"]:
                assert position in variants, f"{topic}: no variant body for allowed position {position}"


def test_author_disclosure_extension_does_not_touch_anxiety_pilot_cell():
    """Regression guard: the gen_z_professionals:anxiety cell (entangled with the
    #5585/#5595 flagship-golden question) must remain exactly as it is on
    origin/main — this extension added no bank file for it, and its pilot floor
    in _PILOT_ACCENT_MINIMUMS was not touched.

    Note: _load_author_disclosure("anxiety", ...) itself is NOT empty — that raw
    bank file already existed pre-extension (3 entries, split out of
    AUTHOR_COMMENTARY by PR #5585) and this extension correctly leaves it alone.
    The real invariant this pilot cell depends on is that
    _author_commentary_and_disclosure_pools() (GOLDEN_5585_SCOPE_AWAY_2026-07-14)
    still merges those 3 entries back into AUTHOR_COMMENTARY and reports an EMPTY
    disclosure pool for this exact cell, protecting the frozen flagship golden —
    checking the raw loader instead would be testing the wrong layer.
    """
    from phoenix_v4.planning.accent_planner import _author_commentary_and_disclosure_pools

    _, disclosure_pool = _author_commentary_and_disclosure_pools(
        "gen_z_professionals", "anxiety", "ravi_chandra", "en_US", REPO_ROOT
    )
    assert disclosure_pool == []

    budget, profile, _ = resolve_accent_budget(
        "stillness_press",
        persona_id="gen_z_professionals",
        topic_id="anxiety",
        enrichment_contract_v1=True,
        repo_root=REPO_ROOT,
    )
    assert profile == "somatic_reflective"
    # AUTHOR_DISCLOSURE was never part of the anxiety pilot's explicit floor
    # (QUOTE/ENCOURAGEMENT/REFLECTION_QUESTION/TROUBLESHOOTING/CITED_EVIDENCE/
    # EXTERNAL_STORY/WISDOM_ESSENCE/AUTHOR_COMMENTARY only) and still is not.
    assert budget.get("AUTHOR_DISCLOSURE", 0) == 0


@pytest.mark.slow
def test_gen_z_sleep_anxiety_author_disclosure_lands_without_fallback():
    """Full pipeline proof for one extension cell: gen_z_professionals x
    sleep_anxiety x ravi_chandra. AUTHOR_DISCLOSURE must be selected from the
    authored bank (not a fallback/no-op), with the correct id namespace and
    provenance, exactly like the anxiety pilot's REFLECTION_QUESTION/
    TROUBLESHOOTING regression above."""
    enriched = _enriched_gen_z_sleep_anxiety()
    plan = plan_accent_beats_for_book(
        enriched,
        brand_id="stillness_press",
        seed="4242",
        teacher_mode=False,
        repo_root=REPO_ROOT,
        author_id="ravi_chandra",
    )
    planned = attach_accent_plan(
        enriched,
        brand_id="stillness_press",
        seed="4242",
        teacher_mode=False,
        repo_root=REPO_ROOT,
        author_id="ravi_chandra",
    )

    ad_rows = [r for r in plan.flat_rows if r.get("class") == "AUTHOR_DISCLOSURE"]
    assert len(ad_rows) >= 1
    for row in ad_rows:
        assert str(row.get("accent_id", "")).startswith("ad_ravi_sleep_")
        assert row.get("supply_source") == "authored_bank"

    strategy = (planned.enrichment_audit or {}).get("enrichment_strategy_report") or {}
    provenance = strategy.get("supply_provenance_by_class") or {}
    assert provenance.get("AUTHOR_DISCLOSURE") == "authored_bank"

    v21 = (planned.spine_context or {}).get("enhancement_contract_v21") or {}
    tracked = {row["surface"]: row for row in (v21.get("tracked_surfaces") or [])}
    assert tracked["AUTHOR_DISCLOSURE"]["bucket"] == "proof_and_embodiment"
