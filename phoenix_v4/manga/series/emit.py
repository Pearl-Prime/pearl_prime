"""Assemble, validate, and write series workspace artifacts (Chunk B)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from phoenix_v4.manga.models import paths as manga_paths
from phoenix_v4.manga.models.validation import validate_instance
from phoenix_v4.manga.series.genre import build_genre_blueprint
from phoenix_v4.manga.series.series_asset_registry import build_asset_registry
from phoenix_v4.manga.series.story_architect import build_story_architecture_internal
from phoenix_v4.manga.series.visual_identity import (
    build_lettering_style_bible,
    build_style_bible,
)
from phoenix_v4.manga.transmission import story_architecture_internal_to_handoff


def build_series_artifact_bundle(
    *,
    series_id: str,
    arc_id: str,
    genre_id: str,
    schema_version: str = "1.0.0",
) -> dict[str, Any]:
    """Deterministic bundle: all series JSON artifacts, each schema-validated."""
    style = build_style_bible(schema_version=schema_version)
    letter = build_lettering_style_bible(schema_version=schema_version)
    genre = build_genre_blueprint(genre_id=genre_id, schema_version=schema_version)
    internal = build_story_architecture_internal(
        series_id=series_id, arc_id=arc_id, schema_version=schema_version
    )
    handoff = story_architecture_internal_to_handoff(internal)
    assets = build_asset_registry(schema_version=schema_version)

    bundle = {
        "style_bible": style,
        "lettering_style_bible": letter,
        "genre_blueprint": genre,
        "story_architecture_internal": internal,
        "story_architecture_handoff": handoff,
        "asset_registry": assets,
    }
    validate_series_bundle(bundle)
    return bundle


def validate_series_bundle(bundle: Mapping[str, Any]) -> None:
    """Validate each artifact in a bundle dict."""
    validate_instance(bundle["style_bible"], "style_bible")
    validate_instance(bundle["lettering_style_bible"], "lettering_style_bible")
    validate_instance(bundle["genre_blueprint"], "genre_blueprint")
    validate_instance(bundle["story_architecture_internal"], "story_architecture_internal")
    validate_instance(bundle["story_architecture_handoff"], "story_architecture_handoff")
    validate_instance(bundle["asset_registry"], "asset_registry")


def load_series_bundle_from_replay(path: Path) -> dict[str, Any]:
    """Load a full bundle JSON (replay fixture); validate every artifact."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TypeError(f"Expected object in {path}")
    required = {k for k, _ in _bundle_key_paths()}
    missing = required - raw.keys()
    if missing:
        raise ValueError(f"Replay bundle missing keys: {sorted(missing)}")
    validate_series_bundle(raw)
    return dict(raw)


def _bundle_key_paths() -> tuple[tuple[str, str], ...]:
    keys = (
        ("style_bible", manga_paths.STYLE_BIBLE),
        ("lettering_style_bible", manga_paths.LETTERING_STYLE_BIBLE),
        ("genre_blueprint", manga_paths.GENRE_BLUEPRINT),
        ("story_architecture_internal", manga_paths.STORY_ARCHITECTURE_INTERNAL),
        ("story_architecture_handoff", manga_paths.STORY_ARCHITECTURE_HANDOFF),
        ("asset_registry", manga_paths.ASSET_REGISTRY),
    )
    return keys


def write_series_artifacts(workspace_root: Path, bundle: Mapping[str, Any]) -> None:
    """Write bundle to ``workspace_root`` using canonical relative paths."""
    validate_series_bundle(bundle)
    key_to_path = dict(_bundle_key_paths())
    for key, rel in key_to_path.items():
        data = bundle[key]
        out = workspace_root / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def emit_series_setup(
    workspace_root: Path,
    *,
    series_id: str,
    arc_id: str,
    genre_id: str,
    schema_version: str = "1.0.0",
) -> dict[str, Any]:
    """Build deterministic bundle, validate, write under workspace_root."""
    bundle = build_series_artifact_bundle(
        series_id=series_id,
        arc_id=arc_id,
        genre_id=genre_id,
        schema_version=schema_version,
    )
    write_series_artifacts(workspace_root, bundle)
    return bundle
