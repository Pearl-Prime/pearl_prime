"""
FastAPI surface for the brand wizard music survey save flow.

Run (repo root)::

    uvicorn music_survey_routes:app --app-dir brand-wizard-app/server --reload --port 8787

Vite dev server can proxy ``/wizard/music-survey/save`` to this port (same path).
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import FastAPI, HTTPException
from typing import Any

from pydantic import BaseModel, Field

# Resolve sibling handler when launched via uvicorn --app-dir or PYTHONPATH.
_server_dir = Path(__file__).resolve().parent
if str(_server_dir) not in sys.path:
    sys.path.insert(0, str(_server_dir))

from music_survey_save_handler import (  # noqa: E402
    MusicSurveySaveError,
    save_survey_to_brand_yaml,
)


def _brands_directory() -> Path:
    """``brand-wizard-app/brands`` (parent of ``server/``)."""
    return Path(__file__).resolve().parent.parent / "brands"


class MusicSurveySaveRequest(BaseModel):
    survey_responses: dict[str, Any]
    wizard_session_id: str = Field(..., min_length=1)


def create_music_survey_app() -> FastAPI:
    app = FastAPI(title="Brand Wizard — Music Survey Save", version="1.0.0")

    @app.post("/wizard/music-survey/save")
    def post_music_survey_save(body: MusicSurveySaveRequest) -> dict:
        try:
            return save_survey_to_brand_yaml(
                brands_dir=_brands_directory(),
                wizard_session_id=body.wizard_session_id,
                survey_responses=body.survey_responses,
            )
        except MusicSurveySaveError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    return app


app = create_music_survey_app()
