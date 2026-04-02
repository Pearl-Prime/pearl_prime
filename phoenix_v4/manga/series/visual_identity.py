"""Series-level visual identity artifacts (style + lettering bibles)."""

from __future__ import annotations

from typing import Any


def build_style_bible(
    *,
    schema_version: str = "1.0.0",
    style_bible_version: str = "1",
    lexicons: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic minimal ``style_bible`` payload (validated by caller)."""
    return {
        "schema_version": schema_version,
        "artifact_type": "style_bible",
        "style_bible_version": style_bible_version,
        "lexicons": lexicons if lexicons is not None else {"palette": ["#0d0d0d", "#f5f5f5"]},
    }


def build_lettering_style_bible(
    *,
    schema_version: str = "1.0.0",
    fonts: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Deterministic minimal ``lettering_style_bible`` payload."""
    return {
        "schema_version": schema_version,
        "artifact_type": "lettering_style_bible",
        "fonts": fonts if fonts is not None else {"body": "NotoSans", "emphasis": "NotoSans-Bold"},
    }
