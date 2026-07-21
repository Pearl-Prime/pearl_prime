"""Chunk B — series setup bundle, transmission handoff, replay fixture."""

from __future__ import annotations

import json
from pathlib import Path

from phoenix_v4.manga.models import paths as manga_paths
from phoenix_v4.manga.models.validation import load_and_validate
from phoenix_v4.manga.series.emit import (
    build_series_artifact_bundle,
    emit_series_setup,
    load_series_bundle_from_replay,
    write_series_artifacts,
)

FIXTURES = Path(__file__).resolve().parent / "fixtures" / "manga"
REPLAY_BUNDLE = FIXTURES / "series_replay" / "minimal_series_bundle.json"


def test_build_series_bundle_validates() -> None:
    b = build_series_artifact_bundle(
        series_id="t_series",
        arc_id="arc_t",
        genre_id="test_genre",
    )
    assert b["story_architecture_handoff"]["artifact_type"] == "story_architecture_handoff"
    assert "is_carrier_beat" not in json.dumps(b["story_architecture_handoff"])


def test_emit_series_setup_writes_expected_paths(tmp_path: Path) -> None:
    emit_series_setup(
        tmp_path,
        series_id="t_series",
        arc_id="arc_t",
        genre_id="g",
    )
    for rel, stem in (
        (manga_paths.STYLE_BIBLE, "style_bible"),
        (manga_paths.LETTERING_STYLE_BIBLE, "lettering_style_bible"),
        (manga_paths.GENRE_BLUEPRINT, "genre_blueprint"),
        (manga_paths.STORY_ARCHITECTURE_INTERNAL, "story_architecture_internal"),
        (manga_paths.STORY_ARCHITECTURE_HANDOFF, "story_architecture_handoff"),
        (manga_paths.ASSET_REGISTRY, "asset_registry"),
    ):
        p = tmp_path / rel
        assert p.is_file()
        load_and_validate(p, stem)


def test_replay_fixture_loads() -> None:
    b = load_series_bundle_from_replay(REPLAY_BUNDLE)
    assert b["genre_blueprint"]["genre_id"] == "urban_fantasy"


def test_write_series_artifacts_roundtrip(tmp_path: Path) -> None:
    b = build_series_artifact_bundle(
        series_id="t_series",
        arc_id="arc_t",
        genre_id="g",
    )
    write_series_artifacts(tmp_path, b)
    assert (tmp_path / manga_paths.STORY_ARCHITECTURE_HANDOFF).is_file()


def test_emit_series_setup_propagates_mode_and_genre(tmp_path: Path) -> None:
    """Real operator path: mode + genre_id land on architecture and chapter script."""
    from phoenix_v4.manga.chapter.writer_stub import build_chapter_script_pair_from_handoff

    for mode in ("teacher", "music"):
        ws = tmp_path / mode
        bundle = emit_series_setup(
            ws,
            series_id="mode_series",
            arc_id="mode_arc",
            genre_id="iyashikei",
            topic="anxiety",
            mode=mode,
        )
        internal = bundle["story_architecture_internal"]
        handoff = bundle["story_architecture_handoff"]
        assert internal.get("genre_id") == "iyashikei"
        assert handoff.get("genre_id") == "iyashikei"
        assert internal.get("mode") == mode
        assert handoff.get("mode") == mode
        assert isinstance(internal.get("mode_vessel"), dict)
        assert isinstance(handoff.get("mode_vessel"), dict)
        assert internal["mode_vessel"].get("mode") == mode

        writer, _ir = build_chapter_script_pair_from_handoff(
            handoff,
            chapter_number=1,
            series_id="mode_series",
            chapter_id="ch1",
        )
        declared = str(writer.get("genre") or writer.get("genre_id") or "")
        assert declared == "iyashikei"
        assert writer.get("mode") == mode


def test_emit_without_mode_still_declares_genre(tmp_path: Path) -> None:
    b = emit_series_setup(
        tmp_path,
        series_id="nog_mode",
        arc_id="a",
        genre_id="ci_smoke_genre",
    )
    assert b["story_architecture_internal"].get("genre_id") == "ci_smoke_genre"
    assert b["story_architecture_handoff"].get("genre_id") == "ci_smoke_genre"
    assert "mode" not in b["story_architecture_internal"]
    assert "mode_vessel" not in b["story_architecture_internal"]
