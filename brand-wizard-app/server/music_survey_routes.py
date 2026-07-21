"""
FastAPI surface for the brand wizard music survey save flow.

Run (repo root)::

    uvicorn music_survey_routes:app --app-dir brand-wizard-app/server --reload --port 8787

Vite dev server can proxy ``/wizard/music-survey/save`` and ``/wizard/step/music-survey`` to this port (same paths).
"""
from __future__ import annotations

import html
import os
import re
import sys
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# Resolve sibling handler when launched via uvicorn --app-dir or PYTHONPATH.
_server_dir = Path(__file__).resolve().parent
if str(_server_dir) not in sys.path:
    sys.path.insert(0, str(_server_dir))

from music_survey_save_handler import (  # noqa: E402
    MusicBrandRegistryCollisionError,
    MusicSurveySaveError,
    default_canonical_brand_list_path,
    default_music_registry_path,
    save_survey_to_brand_yaml,
)

_ALLOWED_SURVEY_LOCALES = frozenset({"en", "ja", "zh-tw", "zh-cn"})

_CONTENT_LANGUAGE = {
    "en": "en",
    "ja": "ja",
    "zh-tw": "zh-Hant",
    "zh-cn": "zh-Hans",
}

_HTML_LANG = {
    "en": "en",
    "ja": "ja",
    "zh-tw": "zh-Hant",
    "zh-cn": "zh-Hans",
}

_DEGRADED_SURVEY_HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Survey unavailable</title></head>
<body style="font-family:system-ui,sans-serif;padding:2rem;background:#0f172a;color:#e2e8f0;">
<p>The musician reflections survey bundle is not installed on this host (expected under
<code style="color:#f59e0b">brand-wizard-app/dist/</code> or <code style="color:#f59e0b">brand-wizard-app/public/</code>).</p>
</body></html>"""


def _brands_directory() -> Path:
    """``brand-wizard-app/brands`` (parent of ``server/``)."""
    return Path(__file__).resolve().parent.parent / "brands"


def _music_registry_path() -> Path:
    """``config/music/music_brand_registry.yaml`` (repo root). Overridable via
    monkeypatch in tests so no test run ever writes the real registry file."""
    return default_music_registry_path()


def _canonical_brand_list_path() -> Path:
    """``config/manga/canonical_brand_list.yaml`` (Path X — read-only boundary).
    Overridable via monkeypatch in tests."""
    return default_canonical_brand_list_path()


def _brand_wizard_app_home() -> Path:
    return Path(__file__).resolve().parent.parent


def _survey_search_roots() -> list[Path]:
    roots: list[Path] = []
    extra = os.environ.get("BRAND_WIZARD_MUSIC_SURVEY_ROOT", "").strip()
    if extra:
        roots.append(Path(extra).resolve())
    if os.environ.get("BRAND_WIZARD_MUSIC_SURVEY_ROOT_EXCLUSIVE", "").strip() == "1":
        return roots
    home = _brand_wizard_app_home()
    roots.extend([home / "dist", home / "public"])
    return roots


def normalize_music_survey_locale(raw: Optional[str]) -> Optional[str]:
    """Return canonical locale key or None if unknown."""
    if raw is None or not str(raw).strip():
        return "en"
    s = str(raw).strip().lower().replace("_", "-")
    if s in _ALLOWED_SURVEY_LOCALES:
        return s
    return None


def _first_existing_file(rel_name: str) -> Optional[Path]:
    for base in _survey_search_roots():
        candidate = base / rel_name
        if candidate.is_file():
            return candidate
    return None


def _inject_locale_metadata(markup: str, locale: str) -> str:
    """Ensure routing metadata and html lang reflect the requested survey locale."""
    esc = html.escape(locale, quote=True)
    meta = f'    <meta name="pearl-music-survey-locale" content="{esc}">\n'
    out = markup
    if "pearl-music-survey-locale" not in out:
        if "<head>" in out:
            out = out.replace("<head>", "<head>\n" + meta, 1)
        else:
            out = meta + out
    lang = _HTML_LANG.get(locale, "en")
    if out.lstrip().lower().startswith("<!doctype") or "<html" in out[:500].lower():
        out = re.sub(
            r"<html\s+lang=\"[^\"]*\"",
            f'<html lang="{html.escape(lang, quote=True)}"',
            out,
            count=1,
            flags=re.IGNORECASE,
        )
    return out


def load_musician_reflections_survey_html(locale: str) -> Optional[str]:
    """
    Resolve static survey HTML for ``locale`` (en, ja, zh-tw, zh-cn).

    Preference order per search root: exact ``musician_reflections_survey-{locale}.html``,
    then (``en`` only) ``musician_reflections_survey.html``. If a per-locale file is absent,
    fall back to the canonical English ``musician_reflections_survey.html`` and annotate
    with ``<meta name="pearl-music-survey-locale">`` so every supported locale returns 200
    when the base bundle exists.
    """
    if locale not in _ALLOWED_SURVEY_LOCALES:
        return None

    exact = f"musician_reflections_survey-{locale}.html"
    p = _first_existing_file(exact)
    if p is not None:
        return _inject_locale_metadata(p.read_text(encoding="utf-8"), locale)

    if locale == "en":
        p2 = _first_existing_file("musician_reflections_survey.html")
        if p2 is not None:
            return _inject_locale_metadata(p2.read_text(encoding="utf-8"), "en")

    base = _first_existing_file("musician_reflections_survey.html")
    if base is not None:
        return _inject_locale_metadata(base.read_text(encoding="utf-8"), locale)
    return None


class MusicSurveySaveRequest(BaseModel):
    survey_responses: dict[str, Any]
    wizard_session_id: str = Field(..., min_length=1)


def create_music_survey_app() -> FastAPI:
    app = FastAPI(title="Brand Wizard — Music Survey Save", version="1.0.0")

    @app.get("/wizard/step/music-survey")
    def get_music_survey_step(
        locale: Optional[str] = Query(
            default=None,
            description="Survey locale: en, ja, zh-tw, zh-cn (default en).",
        ),
    ) -> HTMLResponse:
        loc = normalize_music_survey_locale(locale)
        if loc is None:
            raise HTTPException(status_code=404, detail="Unknown music survey locale")
        body = load_musician_reflections_survey_html(loc)
        if body is None:
            return HTMLResponse(content=_DEGRADED_SURVEY_HTML, status_code=503)
        return HTMLResponse(
            content=body,
            status_code=200,
            media_type="text/html; charset=utf-8",
            headers={"Content-Language": _CONTENT_LANGUAGE.get(loc, "en")},
        )

    @app.post("/wizard/music-survey/save")
    def post_music_survey_save(body: MusicSurveySaveRequest) -> dict:
        try:
            return save_survey_to_brand_yaml(
                brands_dir=_brands_directory(),
                wizard_session_id=body.wizard_session_id,
                survey_responses=body.survey_responses,
                music_registry_path=_music_registry_path(),
                canonical_brand_list_path=_canonical_brand_list_path(),
            )
        except MusicBrandRegistryCollisionError as e:
            # Path X (37) anti-drift hard reject — distinct from ordinary 422 validation
            # failures so callers can tell "your input was malformed" apart from "this
            # brand_id would contaminate the frozen manga canon."
            raise HTTPException(status_code=400, detail=str(e)) from e
        except MusicSurveySaveError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e

    return app


app = create_music_survey_app()
