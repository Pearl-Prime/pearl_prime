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
