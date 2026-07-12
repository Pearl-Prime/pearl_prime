"""Focused tests for spine-mode book_outline artifact writer."""
from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter, EnrichedSlot
from phoenix_v4.qa.book_outline import (
    build_book_outline_payload,
    render_book_outline_markdown,
    write_book_outline,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _slot(
    slot_type: str,
    *,
    source: str = "persona_atom",
    source_id: str = "atom_1",
    enrichment_applied: list[str] | None = None,
    journey_exercise_id: str | None = None,
) -> EnrichedSlot:
    return EnrichedSlot(
        slot_type=slot_type,
        content=f"{slot_type} body",
        source=source,
        source_id=source_id,
        target_words=40,
        actual_words=10,
        enrichment_applied=list(enrichment_applied or []),
        journey_exercise_id=journey_exercise_id,
    )


def _sample_book(*, with_optional_surfaces: bool = True) -> EnrichedBook:
    ch1 = EnrichedChapter(
        number=1,
        role="recognition",
        working_title="The Alarm",
        thesis="Notice the prediction before acting on it.",
        slots=[
            _slot("HOOK", enrichment_applied=["persona_alarm_behavior"]),
            _slot("SCENE"),
            _slot("STORY", enrichment_applied=["story_vividness"]),
            _slot("ANGLE_DEFINITION", source="angle_atom", source_id="angle_def:prediction"),
            _slot("REFLECTION"),
            _slot(
                "EXERCISE",
                enrichment_applied=["somatic_exercise"],
                journey_exercise_id="journey_ex_01",
            ),
            _slot("TAKEAWAY"),
            _slot("INTEGRATION"),
            _slot("THREAD"),
        ],
        total_words=120,
        source_breakdown={"persona_atom": 7, "angle_atom": 1},
    )
    ch2 = EnrichedChapter(
        number=2,
        role="reframe",
        working_title="Swap the evidence",
        thesis="Treat the alarm as a hypothesis.",
        slots=[
            _slot("HOOK"),
            _slot("ANGLE_CALLBACK", source="angle_atom", source_id="angle_cb:prediction"),
            _slot("PIVOT"),
            _slot("REFLECTION"),
            _slot("INTEGRATION"),
        ],
        total_words=80,
        source_breakdown={"persona_atom": 4, "angle_atom": 1},
    )
    spine: dict = {
        "book_idea": "prediction-as-evidence swap",
        "book_motif": "The Alarm (chest and phone)",
        "story_mix_profile": "recognition_before_action",
    }
    audit: dict = {}
    if with_optional_surfaces:
        spine["accent_assignments"] = [
            {
                "chapter": 1,
                "class": "ENCOURAGEMENT",
                "accent_id": "enc_alarm_01",
                "position": "after_EXERCISE",
                "supply_source": "authored_bank",
            },
            {
                "chapter": 1,
                "class": "EXTERNAL_STORY",
                "accent_id": "ext_story_01",
                "position": "after_HOOK",
                "supply_source": "authored_bank",
            },
            {
                "chapter": 2,
                "class": "WISDOM_ESSENCE",
                "accent_id": "wisdom_01",
                "position": "after_REFLECTION",
                "supply_source": "authored_bank",
            },
        ]
        audit = {
            "enrichment_strategy_report": {
                "book_idea": "prediction-as-evidence swap",
                "book_motif": "The Alarm (chest and phone)",
                "enrichment_strategy_profile": "recognition_before_action",
                "brand_accent_profile": "phoenix",
                "assignments": spine["accent_assignments"],
            },
            "section_packet_audit": [
                {
                    "chapter": 1,
                    "slot_type": "HOOK",
                    "source": "persona_atom",
                    "source_id": "atom_1",
                },
                {
                    "chapter": 1,
                    "slot_type": "EXERCISE",
                    "source": "persona_atom",
                    "source_id": "atom_1",
                },
                {
                    "chapter": 2,
                    "slot_type": "ANGLE_CALLBACK",
                    "source": "angle_atom",
                    "source_id": "angle_cb:prediction",
                },
            ],
        }
    return EnrichedBook(
        schema_version=1,
        stage="enrichment_select",
        topic="anxiety",
        teacher_id="ahjan",
        persona_id="gen_z_professionals",
        runtime_format="extended_book_2h",
        chapters=[ch1, ch2],
        total_words=200,
        enrichment_audit=audit,
        spine_context=spine,
        locale="en-US",
    )


def test_write_book_outline_emits_md_and_json(tmp_path: Path) -> None:
    book = _sample_book()
    paths = write_book_outline(
        enriched=book,
        render_dir=tmp_path,
        topic_id="anxiety",
        persona_id="gen_z_professionals",
        locale="en-US",
        runtime_format="extended_book_2h",
    )
    assert paths["markdown"].exists()
    assert paths["json"].exists()
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "# Book Outline" in md
    assert "prediction-as-evidence swap" in md
    assert "The Alarm (chest and phone)" in md
    assert "Chapter 1" in md
    assert "EXERCISE ✓" in md
    assert "ENCOURAGEMENT" in md
    assert "EXTERNAL_STORY" in md
    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["schema_version"] == 1
    assert payload["chapter_count"] == 2
    assert payload["book_idea"] == "prediction-as-evidence swap"


def test_chapter_rows_reflect_landed_slots_and_enrichments() -> None:
    book = _sample_book()
    payload = build_book_outline_payload(book)
    ch1 = payload["chapters"][0]
    assert ch1["core_slots"]["HOOK"] is True
    assert ch1["core_slots"]["EXERCISE"] is True
    assert ch1["core_slots"]["SCENE"] is True
    assert ch1["core_slots"]["PIVOT"] is False
    assert ch1["exercise"]["present"] is True
    assert "journey_ex_01" in ch1["exercise"]["journey_exercise_ids"]
    assert ch1["story"]["present"] is True
    assert ch1["enrichment_families"]["exercise"] is True
    assert ch1["enrichment_families"]["encouragement"] is True
    assert ch1["enrichment_families"]["parable_or_external_story"] is True
    assert ch1["enrichment_families"]["callback"] is False
    assert "somatic_exercise" in ch1["enrichment_hooks"]
    accent_classes = {a["class"] for a in ch1["accents"]}
    assert "ENCOURAGEMENT" in accent_classes
    assert "EXTERNAL_STORY" in accent_classes

    ch2 = payload["chapters"][1]
    assert ch2["angle"]["has_callback"] is True
    assert ch2["enrichment_families"]["callback"] is True
    assert ch2["enrichment_families"]["wisdom"] is True
    assert ch2["core_slots"]["EXERCISE"] is False


def test_missing_optional_surfaces_do_not_crash(tmp_path: Path) -> None:
    book = _sample_book(with_optional_surfaces=False)
    # Explicitly empty / None-like optional surfaces
    book.enrichment_audit = {}
    book.spine_context = {}
    paths = write_book_outline(enriched=book, render_dir=tmp_path)
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "# Book Outline" in md
    assert "Chapter 1" in md
    payload = build_book_outline_payload(book)
    assert payload["chapters"][0]["accents"] == []
    assert payload["book_idea"] == ""
    # Markdown still renders family presence from slots alone
    assert "exercise" in render_book_outline_markdown(payload)


def test_empty_book_does_not_crash(tmp_path: Path) -> None:
    book = EnrichedBook(
        schema_version=1,
        stage="enrichment_select",
        topic="anxiety",
        teacher_id=None,
        persona_id="gen_z_professionals",
        runtime_format="standard_book",
        chapters=[],
        total_words=0,
        enrichment_audit={},
        spine_context={},
    )
    paths = write_book_outline(enriched=book, render_dir=tmp_path)
    md = paths["markdown"].read_text(encoding="utf-8")
    assert "No chapters recorded" in md
    # None-like optional inputs via payload builder must also be safe
    book.enrichment_audit = None  # type: ignore[assignment]
    book.spine_context = None  # type: ignore[assignment]
    payload = build_book_outline_payload(book)
    assert payload["chapters"] == []
    assert "No chapters recorded" in render_book_outline_markdown(payload)


def test_spa_dict_shape_and_render_audit_merge() -> None:
    book = _sample_book(with_optional_surfaces=False)
    book.enrichment_audit = {
        "section_packet_audit": {
            "slots": [
                {"chapter": 1, "slot_type": "HOOK", "source": "persona_atom", "source_id": "h1"},
            ],
            "slot_count": 1,
        }
    }
    render_audit = [
        {
            "chapter": 1,
            "class": "QUOTE",
            "accent_id": "quote_01",
            "provenance": "authored_bank",
        }
    ]
    payload = build_book_outline_payload(book, accent_render_audit=render_audit)
    ch1 = payload["chapters"][0]
    assert ch1["section_packet_rows"][0]["slot_type"] == "HOOK"
    assert any(a["accent_id"] == "quote_01" for a in ch1["accents"])


def test_spine_pipeline_writes_book_outline_for_normal_render(tmp_path: Path) -> None:
    """Normal (non-contract) spine render emits book_outline.md/.json."""
    from types import SimpleNamespace

    import scripts.run_pipeline as rp

    ch = EnrichedChapter(
        1,
        "recognition",
        "t",
        "Notice the alarm.",
        [
            _slot("HOOK"),
            _slot("STORY"),
            _slot("EXERCISE", journey_exercise_id="ex1"),
            _slot("REFLECTION"),
            _slot("INTEGRATION"),
        ],
        50,
        {"persona_atom": 5},
    )
    enriched = EnrichedBook(
        1,
        "enrichment_select",
        "anxiety",
        "ahjan",
        "gen_z_professionals",
        "short_book_30",
        [ch],
        50,
        {
            "enrichment_strategy_report": {
                "book_idea": "prediction-as-evidence swap",
                "book_motif": "The Alarm",
                "enrichment_strategy_profile": "recognition_before_action",
            },
            "section_packet_audit": [
                {"chapter": 1, "slot_type": "HOOK", "source": "persona_atom", "source_id": "a"},
            ],
        },
        spine_context={
            "book_idea": "prediction-as-evidence swap",
            "book_motif": "The Alarm",
            "story_mix_profile": "recognition_before_action",
            "accent_assignments": [
                {
                    "chapter": 1,
                    "class": "ENCOURAGEMENT",
                    "accent_id": "enc_1",
                    "supply_source": "authored_bank",
                }
            ],
        },
        locale="en-US",
    )

    prose = "\n\n".join(f"Chapter {i}\n\nMinimal body {i}." for i in range(1, 7))
    render_dir = tmp_path / "normal_spine_render"
    ns = SimpleNamespace(
        seed="outline_emit_test",
        frame="somatic_first",
        runtime_format="short_book_30",
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
    }
    ws = tmp_path / "job_ws"
    ws.mkdir(parents=True, exist_ok=True)

    def _stub_select(req, repo_root=None):
        return enriched

    with patch("phoenix_v4.planning.enrichment_select.select_enrichment", side_effect=_stub_select):
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
                                            args=ns,
                                            book_spec_for_compiler=book_spec,
                                            quality_profile="draft",
                                            gates_run=False,
                                            gates_hard=False,
                                            ebook_job_ws=ws,
                                            repo_root=REPO_ROOT,
                                        )
    assert rc == 0
    # Must NOT be a contract-demo path suffix
    assert not str(render_dir).endswith("cli_demo_trace_run_composite_contract_v1")
    outline_md = render_dir / "book_outline.md"
    outline_json = render_dir / "book_outline.json"
    assert outline_md.exists(), "normal spine render must emit book_outline.md"
    assert outline_json.exists(), "normal spine render must emit book_outline.json"
    md = outline_md.read_text(encoding="utf-8")
    assert "Chapter 1" in md
    assert "prediction-as-evidence swap" in md
    data = json.loads(outline_json.read_text(encoding="utf-8"))
    assert data["chapters"][0]["core_slots"]["EXERCISE"] is True
    assert any(a["class"] == "ENCOURAGEMENT" for a in data["chapters"][0]["accents"])
