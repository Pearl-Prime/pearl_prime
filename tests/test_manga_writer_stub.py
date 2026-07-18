"""Deterministic chapter script stub."""

from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.chapter.writer_stub import build_chapter_script_pair_from_handoff
from phoenix_v4.manga.models.validation import validate_instance

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "manga" / "valid"


def test_build_script_from_handoff_validates() -> None:
    handoff = json.loads(
        (FIXTURES / "minimal_story_architecture_handoff.json").read_text(encoding="utf-8")
    )
    w, i = build_chapter_script_pair_from_handoff(
        handoff,
        chapter_number=1,
        series_id="sample_series",
        chapter_id="ch01",
    )
    validate_instance(w, "chapter_script_writer_handoff")
    validate_instance(i, "chapter_script_internal_record")

