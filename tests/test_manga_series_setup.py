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
