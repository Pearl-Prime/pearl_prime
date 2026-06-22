"""Lettering spec from chapter_script."""

from __future__ import annotations

from phoenix_v4.manga.chapter.lettering_from_script import (
    build_lettering_spec_from_chapter_script,
)
from phoenix_v4.manga.models.validation import validate_instance


def test_lettering_spec_dialogue_vs_silence() -> None:
    script = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": "s",
        "chapter_id": "c",
        "pages": [
            {
                "page_number": 1,
                "page_type": "standard",
                "panels": [
                    {
                        "panel_id": "a",
                        "dialogue": ["Hello"],
                        "action": "x",
                        "camera": "wide",
                        "mood": "neutral",
                    },
                    {
                        "panel_id": "b",
                        "dialogue": [],
                        "action": "y",
                        "camera": "wide",
                        "mood": "neutral",
                    },
                ],
            }
        ],
    }
    spec = build_lettering_spec_from_chapter_script(script)
    validate_instance(spec, "lettering_spec")
    assert spec["lettering_panels"][0]["silence_confirmed"] is False
    assert spec["lettering_panels"][1]["silence_confirmed"] is True


def test_lettering_emits_head_bboxes_from_zones_for_tail_targeting() -> None:
    # Each speaker gets a fractional head box derived from their bubble zone so
    # the V2 renderer's tail points at the face, not the panel midline.
    script = {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": "s",
        "chapter_id": "c",
        "pages": [
            {
                "page_number": 1,
                "page_type": "standard",
                "panels": [
                    {
                        "panel_id": "p1",
                        "dialogue_lines": [
                            {"speaker": "Mira", "text": "Stay.", "position_hint": "top_right"},
                            {"speaker": "Ren", "text": "I can't.", "position_hint": "bottom_left"},
                        ],
                        "action": "x",
                        "camera": "two_shot",
                        "mood": "tense",
                    }
                ],
            }
        ],
    }
    spec = build_lettering_spec_from_chapter_script(script)
    validate_instance(spec, "lettering_spec")
    p1 = spec["lettering_panels"][0]
    boxes = p1["character_head_bboxes"]
    assert set(boxes) == {"Mira", "Ren"}
    # Mira (top_right) head box sits in the upper-right; mouth band is well above
    # the panel midline (the old fallback targeted y=0.55 — the torso).
    mira = boxes["Mira"]
    assert mira["x1"] >= 0.5 and mira["y2"] <= 0.55
    # An explicit author mouth_anchor on a line suppresses the derived box for
    # that speaker (the renderer reads the anchor directly).
    script["pages"][0]["panels"][0]["dialogue_lines"][0]["mouth_anchor"] = {"x": 0.7, "y": 0.25}
    spec2 = build_lettering_spec_from_chapter_script(script)
    p1b = spec2["lettering_panels"][0]
    assert p1b["dialogue_lines"][0]["mouth_anchor"] == {"x": 0.7, "y": 0.25}
    assert "Mira" not in p1b.get("character_head_bboxes", {})
