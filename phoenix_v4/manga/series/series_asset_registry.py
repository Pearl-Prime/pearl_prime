"""Series ``asset_registry`` artifact builder (schema: asset_registry)."""

from __future__ import annotations

from typing import Any


def build_asset_registry(
    *,
    schema_version: str = "1.0.0",
    assets: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Minimal placeholder registry until real assets are registered."""
    if assets is None:
        assets = [{"asset_id": "series_placeholder"}]
    return {
        "schema_version": schema_version,
        "artifact_type": "asset_registry",
        "assets": assets,
    }
