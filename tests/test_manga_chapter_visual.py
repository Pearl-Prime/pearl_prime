"""Chapter script → panel_prompts + image backends."""

from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.chapter.visual_from_script import compile_panel_prompts_from_chapter_script
from phoenix_v4.manga.chapter.writer_stub import build_chapter_script_pair_from_handoff
from phoenix_v4.manga.image_backend import (
    FixtureReplayImageBackend,
    NoopImageBackend,
    build_panel_images_manifest,
)
from phoenix_v4.manga.models.validation import validate_instance

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "manga" / "valid"


def test_compile_from_handoff_end_to_end() -> None:
    handoff = json.loads(
        (FIXTURES / "minimal_story_architecture_handoff.json").read_text(encoding="utf-8")
    )
    writer, _internal = build_chapter_script_pair_from_handoff(
        handoff,
        chapter_number=1,
        series_id="sample_series",
        chapter_id="ch01",
    )
    doc = compile_panel_prompts_from_chapter_script(
        writer,
        series_id="sample_series",
        chapter_id="ch01",
        config_hash="test",
    )
    validate_instance(doc, "panel_prompts")
    assert len(doc["panels"]) == 1
    assert "prompt" in doc["panels"][0]
    assert doc["panels"][0]["prompt_token_count"] >= 0


def test_noop_manifest_validates() -> None:
    handoff = json.loads(
        (FIXTURES / "minimal_story_architecture_handoff.json").read_text(encoding="utf-8")
    )
    writer, _ = build_chapter_script_pair_from_handoff(
        handoff, chapter_number=1, series_id="s", chapter_id="c1"
    )
    doc = compile_panel_prompts_from_chapter_script(writer, chapter_id="c1")
    gen = NoopImageBackend().generate(doc)
    manifest = build_panel_images_manifest(doc, gen)
    validate_instance(manifest, "panel_images_manifest")


def test_replay_backend_with_png(tmp_path: Path) -> None:
    # Minimal 1x1 PNG
    png = bytes(
        [
            0x89,
            0x50,
            0x4E,
            0x47,
            0x0D,
            0x0A,
            0x1A,
            0x0A,
            0x00,
            0x00,
            0x00,
            0x0D,
            0x49,
            0x48,
            0x44,
            0x52,
            0x00,
            0x00,
            0x00,
            0x01,
            0x00,
            0x00,
            0x00,
            0x01,
            0x08,
            0x06,
            0x00,
            0x00,
            0x00,
            0x1F,
            0x15,
            0xC4,
            0x89,
            0x00,
            0x00,
            0x00,
            0x0A,
            0x49,
            0x44,
            0x41,
            0x54,
            0x78,
            0x9C,
            0x63,
            0x00,
            0x01,
            0x00,
            0x00,
            0x05,
            0x00,
            0x01,
            0x0D,
            0x0A,
            0x2D,
            0xB4,
            0x00,
            0x00,
            0x00,
            0x00,
            0x49,
            0x45,
            0x4E,
            0x44,
            0xAE,
            0x42,
            0x60,
            0x82,
        ]
    )
    img = tmp_path / "a.png"
    img.write_bytes(png)
    handoff = json.loads(
        (FIXTURES / "minimal_story_architecture_handoff.json").read_text(encoding="utf-8")
    )
    writer, _ = build_chapter_script_pair_from_handoff(
        handoff, chapter_number=1, series_id="s", chapter_id="c1"
    )
    doc = compile_panel_prompts_from_chapter_script(writer, chapter_id="c1")
    pid = doc["panels"][0]["panel_id"]
    back = FixtureReplayImageBackend({pid: img})
    gen = back.generate(doc)
    manifest = build_panel_images_manifest(doc, gen)
    validate_instance(manifest, "panel_images_manifest")
    assert gen[0]["status"] == "ok"
    assert gen[0]["width"] == 1
