"""Tests for golden-chapter sanitizer, furniture dedupe, and pilot report."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from phoenix_v4.rendering.golden_chapter_synthesis import (
    EnvironmentPhraseMemory,
    audit_artifact_leakage,
    collect_artifact_leakage_labels,
    dedupe_scene_furniture_book,
    evaluate_golden_chapter_readiness,
    post_compose_sanitize_chapter,
    write_golden_chapter_pilot_artifacts,
    _extract_single_body_from_depth_canonical_dump,
    _resolve_location_placeholders,
)
from phoenix_v4.planning.enrichment_select import EnrichedBook, EnrichedChapter, EnrichedSlot


def test_post_compose_strips_raw_markdown_dividers() -> None:
    raw = "First line.\n\n---\n\nSecond paragraph."
    out = post_compose_sanitize_chapter(raw, topic_id="anxiety")
    assert "---" not in out.splitlines()
    assert "First line" in out
    assert "Second paragraph" in out


def test_post_compose_strips_python_dict_like_lines() -> None:
    raw = "Good prose here.\n\n{'atom_id': 'x', 'body': 'y'}\n\nMore prose."
    out = post_compose_sanitize_chapter(raw, topic_id="anxiety")
    assert "atom_id" not in out
    assert "Good prose" in out
    assert "More prose" in out


def test_post_compose_fixes_double_the() -> None:
    out = post_compose_sanitize_chapter("The the train is late.", topic_id="")
    assert "The the" not in out


def test_post_compose_strips_buddhist_line_for_anxiety_topic() -> None:
    raw = "You feel wired before the meeting.\n\nBuddhist enlightenment is a journey.\n\nStay with the body."
    out = post_compose_sanitize_chapter(raw, topic_id="anxiety")
    assert "Buddhist" not in out
    assert "wired" in out.lower()


def test_dedupe_scene_furniture_book_caps_phrase() -> None:
    blob = (
        "One soft daylight along the sill. Two soft daylight along the sill. "
        "Three soft daylight along the sill."
    )
    out, notes = dedupe_scene_furniture_book(blob, max_each=1)
    assert out.count("soft daylight along the sill") == 1
    assert notes and "removed_extra" in notes[0]


def test_post_compose_strips_inline_triple_dash() -> None:
    raw = "First sentence. --- Second sentence after bad merge."
    out = post_compose_sanitize_chapter(raw, topic_id="")
    assert " ---" not in out
    assert "---" not in out


def test_artifact_audit_fails_on_inline_triple_dash() -> None:
    labels = collect_artifact_leakage_labels("One two three. --- Four.")
    assert "raw_markdown_dash_run" in labels


def test_artifact_audit_fails_on_python_dict_repr() -> None:
    labels = collect_artifact_leakage_labels("x\n\n{'atom_id': 'a', 'body': 'b'}\n\ny")
    assert "python_dict_repr" in labels


def test_artifact_audit_fails_on_repeated_canonical_headers() -> None:
    blob = "## HOOK v01 --- body --- ## HOOK v02 --- more"
    labels = collect_artifact_leakage_labels(blob)
    assert "repeated_canonical_variant_headers" in labels


def test_depth_canonical_dump_extracts_single_clean_body() -> None:
    bad = (
        "## HOOK v01 --- --- You did everything they said to do. Your chest has not gotten the memo. "
        "--- ## HOOK v02 --- --- The task is open. You have been looking at it for forty minutes."
    )
    got = _extract_single_body_from_depth_canonical_dump(bad)
    assert "##" not in got
    assert "---" not in got
    assert "memo" in got.lower() or "forty minutes" in got.lower()


def test_depth_story_canonical_dump_excerpt_from_report() -> None:
    bad = (
        "## SCENE v01 --- --- Your badge beeps at the door. The lobby smells like recycled air. "
        "{street_name} is visible through the glass. Your bag cuts into your left shoulder. "
        "--- ## SCENE v02 --- --- The {transit_line} lurches. Your coffee shifts in your hand. "
        "The person beside you types without stopping."
    )
    got = _extract_single_body_from_depth_canonical_dump(bad)
    assert "## SCENE" not in got
    assert "badge beeps" in got.lower()
    assert "{" not in got
    assert "coffee shifts" not in got.lower()


def test_resolve_location_placeholders_fixes_street_below_phrase() -> None:
    raw = "You look out. {street_name} is there below. The hum rises."
    out = _resolve_location_placeholders(raw)
    assert "{" not in out
    assert "there below" not in out.lower()


def test_resolve_location_placeholders_avoids_legacy_gray_phrase() -> None:
    memory = EnvironmentPhraseMemory()
    outputs = []
    for idx, raw in enumerate(
        (
            "Desk glow. {weather_detail} by the screen.",
            "Window edge. {weather_detail} near the glass.",
            "Office hush. {weather_detail} in the room.",
            "Hallway return. {weather_detail} over the frame.",
        )
    ):
        outputs.append(_resolve_location_placeholders(raw, phrase_memory=memory, chapter_index=idx))
    joined = " ".join(outputs).lower()
    assert "gray daylight filters in" not in joined


def test_artifact_audit_detects_section_header_leak() -> None:
    r = audit_artifact_leakage("## HOOK v01\n\nProse.")
    assert r["status"] == "FAIL"


def test_golden_chapter_report_writes_selected_fragments(tmp_path: Path) -> None:
    slots = [
        EnrichedSlot(
            slot_type="HOOK",
            content="Your chest tightens before you open the thread.",
            source="test",
            source_id="hook1",
            target_words=50,
            actual_words=10,
            enrichment_applied=[],
        ),
    ]
    ch = EnrichedChapter(
        number=1,
        role="open",
        working_title="Test Chapter",
        thesis="Anxiety is a false alarm on prediction.",
        slots=slots,
        total_words=10,
        source_breakdown={},
    )
    book = EnrichedBook(
        schema_version=1,
        stage="test",
        topic="anxiety",
        teacher_id=None,
        persona_id="gen_z_professionals",
        runtime_format="short_book_30",
        chapters=[ch],
        total_words=10,
        enrichment_audit={},
        spine_context={},
    )
    manuscript = "Chapter 1\nTest Chapter\n\nYour chest tightens before you open the thread.\n\n"
    path = write_golden_chapter_pilot_artifacts(
        manuscript_text=manuscript,
        enriched=book,
        chapter_number_1based=1,
        out_dir=tmp_path,
        topic_id="anxiety",
    )
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema_version"] == 1
    assert data["stage"] == "golden_chapter_pilot"
    assert len(data["selected_source_fragments"]) >= 1
    assert "golden_readiness" in data
    assert (tmp_path / "golden_chapter_1.txt").exists()


def test_evaluate_readiness_on_clean_minimal_prose() -> None:
    text = (
        "Your hands go cold on the walk. The point is not courage — it is that your body "
        "reads prediction as evidence.\n\n"
        "Try this for three minutes: name one sensation without fixing it.\n\n"
        "What happens tomorrow if you stop debating whether you are allowed to feel it?\n"
    )
    r = evaluate_golden_chapter_readiness(text, chapter_thesis="false alarm", working_title="t")
    assert r.automated_overall in ("PASS", "WARN", "FAIL")
    assert r.artifact_leakage.status == "PASS"
