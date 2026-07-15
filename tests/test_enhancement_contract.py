from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter, EnrichedSlot
from phoenix_v4.qa.enhancement_contract import (
    build_enhancement_contract_payload,
    write_enhancement_contract,
)
from phoenix_v4.rendering.accent_renderer import insert_accent_beats_into_streams

REPO_ROOT = Path(__file__).resolve().parent.parent


def _slot(
    slot_type: str,
    content: str,
    *,
    source_id: str,
    variant_id: str = "",
    atom_id: str = "",
) -> EnrichedSlot:
    return EnrichedSlot(
        slot_type=slot_type,
        content=content,
        source="persona_atom",
        source_id=source_id,
        target_words=40,
        actual_words=max(1, len(content.split())),
        enrichment_applied=[],
        variant_id=variant_id,
        atom_id=atom_id,
    )


def _sample_book() -> EnrichedBook:
    chapter = EnrichedChapter(
        number=1,
        role="recognition",
        working_title="The Alarm",
        thesis="Notice the prediction before obeying it.",
        slots=[
            _slot("HOOK", "Hook body.", source_id="hook_01", variant_id="hook_v1", atom_id="hook_atom_01"),
            _slot(
                "ANGLE_DEFINITION",
                "Angle definition body.",
                source_id="angle_def:prediction",
                variant_id="angle_def_v1",
            ),
            _slot("STORY", "Story body.", source_id="story_01", variant_id="story_v1"),
            _slot("REFLECTION", "Reflection body.", source_id="reflection_01"),
            _slot("EXERCISE", "Exercise body.", source_id="exercise_01", variant_id="exercise_v1"),
            _slot("ANGLE_CALLBACK", "Angle callback body.", source_id="angle_cb:prediction"),
            _slot("THREAD", "Thread body.", source_id="thread_01"),
        ],
        total_words=80,
        source_breakdown={"persona_atom": 7},
        accent_beats=[
            {
                "class": "QUOTE",
                "accent_id": "quote_01",
                "position": "after_HOOK",
                "keys": {"story_type": "film", "supply_provenance": "authored_bank"},
            },
            {
                "class": "ENCOURAGEMENT",
                "accent_id": "enc_01",
                "position": "before_THREAD",
                "keys": {"supply_provenance": "authored_bank"},
            },
        ],
        accent_bodies={
            "quote_01": "Quote body.",
            "enc_01": "Encouragement body.",
        },
    )
    return EnrichedBook(
        schema_version=1,
        stage="enrichment_select",
        topic="anxiety",
        teacher_id="ahjan",
        persona_id="gen_z_professionals",
        runtime_format="extended_book_2h",
        chapters=[chapter],
        total_words=80,
        enrichment_audit={
            "enrichment_strategy_report": {
                "book_idea": "prediction-as-evidence swap",
                "book_motif": "The Alarm (chest and phone)",
                "enrichment_strategy_profile": "intimate_voice",
                "assignments": [
                    {
                        "chapter": 1,
                        "class": "QUOTE",
                        "accent_id": "quote_01",
                        "position": "after_HOOK",
                        "supply_source": "authored_bank",
                        "keys": {"story_type": "film", "supply_provenance": "authored_bank"},
                    },
                    {
                        "chapter": 1,
                        "class": "ENCOURAGEMENT",
                        "accent_id": "enc_01",
                        "position": "before_THREAD",
                        "supply_source": "authored_bank",
                        "keys": {"supply_provenance": "authored_bank"},
                    },
                ],
            },
            "bestseller_alignment_report": {
                "supported_underfilled_budget_by_class": {},
            },
        },
        spine_context={
            "book_idea": "prediction-as-evidence swap",
            "book_motif": "The Alarm (chest and phone)",
            "accent_budget": {"QUOTE": 1, "ENCOURAGEMENT": 1},
            "accent_signature": "sig_123",
            "story_mix_profile": "intimate_voice",
            "accent_assignments": [
                {
                    "chapter": 1,
                    "class": "QUOTE",
                    "accent_id": "quote_01",
                    "position": "after_HOOK",
                    "supply_source": "authored_bank",
                    "keys": {"story_type": "film", "supply_provenance": "authored_bank"},
                },
                {
                    "chapter": 1,
                    "class": "ENCOURAGEMENT",
                    "accent_id": "enc_01",
                    "position": "before_THREAD",
                    "supply_source": "authored_bank",
                    "keys": {"supply_provenance": "authored_bank"},
                },
            ],
        },
        locale="en-US",
    )


def _sample_manuscript(book: EnrichedBook) -> str:
    chapter = book.chapters[0]
    slot_types = [str(slot.slot_type or "").strip().upper() for slot in chapter.slots]
    slot_proses = [str(slot.content or "").strip() for slot in chapter.slots]
    types_out, proses_out, _ = insert_accent_beats_into_streams(
        slot_types,
        slot_proses,
        chapter.accent_beats,
        chapter.accent_bodies,
    )
    body = "\n\n".join(proses_out)
    assert "THREAD" not in body  # sanity on prose content, not types
    return f"Chapter 1\n{chapter.working_title}\n\n{body}\n"


def test_build_enhancement_contract_payload_reconciles_final_manuscript() -> None:
    book = _sample_book()
    manuscript = _sample_manuscript(book)
    payload = build_enhancement_contract_payload(
        enriched=book,
        manuscript_text=manuscript,
        contract_id="enhancement_contract_v1",
        topic_id="anxiety",
        persona_id="gen_z_professionals",
        runtime_format="extended_book_2h",
    )
    assert payload["status"] == "PASS", payload["validation"]["errors"]
    assert payload["accent_rows"][0]["present_in_manuscript"] is True
    assert payload["accent_rows"][1]["final_order_matches_renderer"] is True
    assert payload["enhancement_contract_v21"]["optional_accent_budget"]["hard_max_total_accents"] >= 1
    tracked = {
        row["surface"]: row for row in payload["enhancement_contract_v21"]["tracked_surfaces"]
    }
    assert tracked["AUTHOR_DISCLOSURE"]["bucket"] == "proof_and_embodiment"
    proof_types = {row["slot_type"] for row in payload["core_surface_rows"]}
    assert {"STORY", "EXERCISE", "ANGLE_DEFINITION", "ANGLE_CALLBACK"} <= proof_types
    callback_rows = [row for row in payload["core_surface_rows"] if row.get("callback_role")]
    assert any(row["callback_role"] == "plant" for row in callback_rows)
    assert any(row["callback_role"] == "return" for row in callback_rows)
    assert payload["validation"]["unresolved_markers"] == []


def test_enhancement_contract_reconciles_uppercase_titled_chapter_heading() -> None:
    book = _sample_book()
    manuscript = _sample_manuscript(book).replace(
        "Chapter 1\n", "CHAPTER 1: The Alarm\n", 1
    )
    payload = build_enhancement_contract_payload(
        enriched=book,
        manuscript_text=manuscript,
        contract_id="enhancement_contract_v1",
        topic_id="anxiety",
        persona_id="gen_z_professionals",
        runtime_format="extended_book_2h",
    )
    assert payload["status"] == "PASS", payload["validation"]["errors"]
    assert all(row["present_in_manuscript"] for row in payload["core_surface_rows"])


def test_v21_analogy_metaphor_not_falsely_true_from_angle_definition_alone() -> None:
    """Regression: ANGLE_DEFINITION (a callback plant) must not, by itself, make
    ANALOGY/METAPHOR report present. _sample_book()'s chapter has an
    ANGLE_DEFINITION + ANGLE_CALLBACK pair but zero analogy/metaphor hooks on
    any slot — before the fix, both surfaces still lit up on the strength of
    the angle-definition slot alone (see artifacts/qa/
    enhancement_contract_v21_integration_2026-07-13/enhancement_contract.json
    chapter 1, where this exact false positive was observed in a real render).
    """
    book = _sample_book()
    manuscript = _sample_manuscript(book)
    payload = build_enhancement_contract_payload(
        enriched=book,
        manuscript_text=manuscript,
        contract_id="enhancement_contract_v1",
        topic_id="anxiety",
        persona_id="gen_z_professionals",
        runtime_format="extended_book_2h",
    )
    groups = payload["chapters"][0]["v21_surface_groups"]["cohesion_and_craft"]
    assert "CALLBACK_PLANT" in groups
    assert "CALLBACK_RETURN" in groups
    assert "ANALOGY" not in groups
    assert "METAPHOR" not in groups


def test_v21_analogy_metaphor_select_when_real_hook_present() -> None:
    """ANALOGY/METAPHOR must actually select into the rendered plan's surface
    report when their own real signal (an analogy/metaphor enrichment hook) is
    present — proving the class-specific detection path genuinely works, not
    just that the false-positive fallback was deleted.
    """
    book = _sample_book()
    reflection_slot = next(s for s in book.chapters[0].slots if s.slot_type == "REFLECTION")
    reflection_slot.enrichment_applied = ["analogy_bridge", "metaphor_thread"]
    manuscript = _sample_manuscript(book)
    payload = build_enhancement_contract_payload(
        enriched=book,
        manuscript_text=manuscript,
        contract_id="enhancement_contract_v1",
        topic_id="anxiety",
        persona_id="gen_z_professionals",
        runtime_format="extended_book_2h",
    )
    groups = payload["chapters"][0]["v21_surface_groups"]["cohesion_and_craft"]
    assert "ANALOGY" in groups
    assert "METAPHOR" in groups


def test_callback_layer_returns_reconcile_to_prior_base_plant() -> None:
    book = _sample_book()
    book.chapters[0].slots = [
        _slot("ANGLE_DEFINITION", "Angle definition body.", source_id="angle_def:PROTECTIVE_ALARM"),
        _slot("ANGLE_CALLBACK", "Angle callback body.", source_id="angle_cb:PROTECTIVE_ALARM:L3"),
        _slot("STORY", "Story body.", source_id="story_01", variant_id="story_v1"),
        _slot("EXERCISE", "Exercise body.", source_id="exercise_01", variant_id="exercise_v1"),
    ]
    book.chapters[0].accent_beats = []
    book.chapters[0].accent_bodies = {}
    book.spine_context["accent_assignments"] = []
    book.enrichment_audit["enrichment_strategy_report"]["assignments"] = []
    manuscript = "Chapter 1\nLayered Callback\n\nAngle definition body.\n\nAngle callback body.\n\nStory body.\n\nExercise body.\n"
    payload = build_enhancement_contract_payload(enriched=book, manuscript_text=manuscript)
    callback_rows = [row for row in payload["core_surface_rows"] if row.get("callback_role")]
    assert [row["plant_id"] for row in callback_rows] == ["PROTECTIVE_ALARM", "PROTECTIVE_ALARM"]
    assert not [
        err for err in payload["validation"]["errors"]
        if "callback_return_without_prior_plant" in err
    ]


def test_build_enhancement_contract_payload_flags_missing_and_orphan_rows() -> None:
    book = _sample_book()
    book.chapters[0].accent_bodies["orphan_01"] = "Orphan body."
    manuscript = "Chapter 1\nThe Alarm\n\nHook body.\n\nStory body.\n\nReflection body.\n\nExercise body.\n\nThread body.\n"
    payload = build_enhancement_contract_payload(
        enriched=book,
        manuscript_text=manuscript,
        contract_id="enhancement_contract_v1",
    )
    assert payload["status"] == "FAIL"
    assert payload["validation"]["missing_planned"]
    assert payload["validation"]["orphan_selected"]
    assert payload["validation"]["core_surface_failures"]


def test_write_enhancement_contract_emits_json_and_markdown(tmp_path: Path) -> None:
    book = _sample_book()
    paths = write_enhancement_contract(
        enriched=book,
        manuscript_text=_sample_manuscript(book),
        render_dir=tmp_path,
        contract_id="enhancement_contract_v1",
    )
    assert paths["json"].exists()
    assert paths["markdown"].exists()
    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["status"] == "PASS"
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "# Enhancement Contract" in md
    assert "Accent Proof" in md


def test_spine_pipeline_auto_writes_contract_for_flagship_chord(tmp_path: Path) -> None:
    from types import SimpleNamespace

    import scripts.run_pipeline as rp

    book = _sample_book()
    prose = _sample_manuscript(book)
    render_dir = tmp_path / "flagship_auto_contract"
    ws = tmp_path / "job_ws"
    ws.mkdir(parents=True, exist_ok=True)

    args = SimpleNamespace(
        seed="enhancement_contract_test",
        frame="somatic_first",
        runtime_format="extended_book_2h",
        render_dir=str(render_dir),
        render_book=True,
        out=None,
        enforce_scene_gate=False,
        scene_gate_mode="production",
        book_quality_override=False,
        generate_freebies=False,
        formats=None,
        publish_dir=None,
        asset_store=None,
        skip_audio=False,
        no_job_check=True,
        locale="en-US",
        golden_chapter_pilot=None,
        music_mode=None,
        musician_id=None,
        exercise_journeys=False,
        output_format=None,
    )
    book_spec = {
        "topic_id": "anxiety",
        "persona_id": "gen_z_professionals",
        "teacher_id": "ahjan",
        "locale": "en-US",
        "enrichment_contract_v1": True,
    }

    with patch("phoenix_v4.planning.enrichment_select.select_enrichment", side_effect=lambda *a, **k: book):
        with patch(
            "phoenix_v4.planning.enrichment_select.apply_depth_pass",
            lambda enriched_book, *a, **k: enriched_book,
        ):
            with patch(
                "phoenix_v4.planning.accent_planner.attach_accent_plan",
                side_effect=lambda enriched_book, **kw: enriched_book,
            ):
                with patch(
                    "phoenix_v4.planning.accent_planner.validate_accent_plan",
                    return_value=[],
                ):
                    with patch(
                        "phoenix_v4.rendering.chapter_composer.compose_from_enriched_book",
                        return_value=prose,
                    ):
                        with patch(
                            "phoenix_v4.rendering.book_renderer.clean_for_delivery",
                            side_effect=lambda p, **kw: p,
                        ):
                            with patch(
                                "phoenix_v4.rendering.book_renderer.strengthen_rendered_spine_manuscript",
                                side_effect=lambda p, **kw: p,
                            ):
                                with patch(
                                    "phoenix_v4.rendering.book_renderer.ensure_chapter_flow_cues",
                                    side_effect=lambda p, **kw: p,
                                ):
                                    with patch(
                                        "phoenix_v4.rendering.golden_chapter_synthesis.dedupe_scene_furniture_book",
                                        side_effect=lambda p, **kw: (p, []),
                                    ):
                                        rc = rp._run_spine_pipeline_mode(
                                            args=args,
                                            book_spec_for_compiler=book_spec,
                                            quality_profile="draft",
                                            gates_run=False,
                                            gates_hard=False,
                                            ebook_job_ws=ws,
                                            repo_root=REPO_ROOT,
                                        )
    assert rc == 0
    assert (render_dir / "enhancement_contract.json").exists()
    assert (render_dir / "enhancement_contract.md").exists()
    assert (render_dir / "plan.json").exists()
