"""Genre blueprint for series setup."""

from __future__ import annotations

from typing import Any


def build_genre_blueprint(
    *,
    genre_id: str,
    schema_version: str = "1.0.0",
    arc_structure: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic minimal ``genre_blueprint`` payload."""
    return {
        "schema_version": schema_version,
        "artifact_type": "genre_blueprint",
        "genre_id": genre_id,
        "arc_structure": arc_structure if arc_structure is not None else {"acts": 3},
    }
