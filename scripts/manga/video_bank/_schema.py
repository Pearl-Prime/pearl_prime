"""Shared schema load + validate helpers for character_capture_manifest."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[3]
SCHEMA_PATH = REPO / "schemas" / "manga" / "character_capture_manifest.schema.json"


def load_schema(path: Path | None = None) -> dict[str, Any]:
    p = path or SCHEMA_PATH
    if not p.is_file():
        raise FileNotFoundError(
            f"capture manifest schema missing: {p} "
            "(requires manga-video-pose-bank-spec-merged on main)"
        )
    return json.loads(p.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict[str, Any], *, schema: dict[str, Any] | None = None) -> None:
    from jsonschema import Draft7Validator

    Draft7Validator(schema or load_schema()).validate(manifest)
