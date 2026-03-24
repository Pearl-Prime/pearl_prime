"""Series setup: visual identity, genre, story architecture, validated artifacts."""

from phoenix_v4.manga.series.emit import (
    build_series_artifact_bundle,
    emit_series_setup,
    load_series_bundle_from_replay,
    validate_series_bundle,
    write_series_artifacts,
)
from phoenix_v4.manga.series.genre import build_genre_blueprint
from phoenix_v4.manga.series.series_asset_registry import build_asset_registry
from phoenix_v4.manga.series.story_architect import build_story_architecture_internal
from phoenix_v4.manga.series.visual_identity import (
    build_lettering_style_bible,
    build_style_bible,
)

__all__ = [
    "build_asset_registry",
    "build_genre_blueprint",
    "build_lettering_style_bible",
    "build_series_artifact_bundle",
    "build_story_architecture_internal",
    "build_style_bible",
    "emit_series_setup",
    "load_series_bundle_from_replay",
    "validate_series_bundle",
    "write_series_artifacts",
]
