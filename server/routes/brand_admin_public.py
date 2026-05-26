"""
Brand Admin public read-only API (no auth) — wired to the operations dashboard
at brand-wizard-app/public/brand_admin.html.

Prefix: /api/brand_admin (matches the existing brand_admin_download.py prefix the
dashboard already calls).

Endpoints:
  GET /api/brand_admin/brand_index
      Returns the live 3-axis brand inventory:
        book  — from config/brand_registry.yaml (locale-keyed)
        manga — from config/manga/canonical_brand_list.yaml (Path X canon, 37)
        music — from config/music/music_brand_registry.yaml (38+, may be template-only)
      Replaces the legacy 24-row inline ``const B={…}`` that the dashboard had.

  GET /api/brand_admin/brand/{brand_id}/books_by_platform
      For a single brand_id, returns the books × platforms grid the operator asked
      for ("clear and simple: for each brand a link to each books set for each
      platform"). Joins per-brand topic vocabulary to config/funnel/store_url_tracker.yaml
      rows. Empty rows return "No books published yet" framing in the UI.

Authority:
  - BR-CANON-01 Path X (docs/PEARL_ARCHITECT_STATE.md) — 3 axes intentionally distinct
  - MUSIC-MODE-BRAND-INTEGRATION-V1-01 — music registry SSOT location
  - DASH-02 — Pearl_Brand owns the dashboard subsystem

Read-only: this module never writes to repo state. Schema-strict YAML reads only.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:  # pragma: no cover — yaml is a hard dep elsewhere
    yaml = None  # type: ignore[assignment]

router = APIRouter(prefix="/api/brand_admin", tags=["brand-admin-public"])


# Canonical source files (read-only).
BOOK_REGISTRY = REPO_ROOT / "config" / "brand_registry.yaml"
MANGA_REGISTRY = REPO_ROOT / "config" / "manga" / "canonical_brand_list.yaml"
MUSIC_REGISTRY = REPO_ROOT / "config" / "music" / "music_brand_registry.yaml"
STORE_URL_TRACKER = REPO_ROOT / "config" / "funnel" / "store_url_tracker.yaml"

# Platform columns surfaced in the books × platforms grid. Driven by the columns
# already present in store_url_tracker.yaml so the UI doesn't ship empty headers
# for platforms we have no data wiring for yet.
PLATFORM_COLUMNS = ("kdp", "apple_books", "google_play", "kobo", "store_url_live")


def _load_yaml(path: Path) -> dict:
    """Read a YAML file or return {} if missing / parse-empty. Pure read."""
    if yaml is None or not path.is_file():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:  # pragma: no cover — caller surfaces 500
        logger.warning("YAML parse failed for %s: %s", path, exc)
        return {}


# ── Brand index across 3 axes ─────────────────────────────────────────────────

def _book_brand_rows() -> list[dict]:
    """Project config/brand_registry.yaml into the dashboard schema."""
    data = _load_yaml(BOOK_REGISTRY)
    brands = data.get("brands") or {}
    rows: list[dict] = []
    for brand_id, body in brands.items():
        if not isinstance(body, dict):
            continue
        rows.append(
            {
                "brand_id": brand_id,
                "name": brand_id.replace("_", " ").title(),
                "axis": "book",
                "tier": None,
                "locale": body.get("locale"),
                "catalog_id": body.get("catalog_id"),
                "status": body.get("lifecycle") or "active",
                "topics": body.get("family_allowlist") or [],
                "demographic": None,
                "primary_topic": None,
                "notes": None,
            }
        )
    return rows


def _manga_brand_rows() -> list[dict]:
    """Project config/manga/canonical_brand_list.yaml (Path X 37)."""
    data = _load_yaml(MANGA_REGISTRY)
    brands = data.get("brands") or {}
    rows: list[dict] = []
    for brand_id, body in brands.items():
        if not isinstance(body, dict):
            continue
        topics: list[str] = []
        primary = body.get("primary_topic")
        if primary:
            topics.append(primary)
        for sec in body.get("secondary_topics") or []:
            if sec and sec not in topics:
                topics.append(sec)
        rows.append(
            {
                "brand_id": brand_id,
                "name": brand_id.replace("_", " ").title(),
                "axis": "manga",
                "tier": body.get("tier"),
                "locale": None,
                "catalog_id": None,
                "status": "active",
                "topics": topics,
                "demographic": body.get("demographic"),
                "primary_topic": primary,
                "notes": body.get("notes"),
            }
        )
    return rows


def _music_brand_rows() -> list[dict]:
    """Project config/music/music_brand_registry.yaml (38+, may include template)."""
    data = _load_yaml(MUSIC_REGISTRY)
    brands = data.get("music_brands") or []
    rows: list[dict] = []
    for body in brands:
        if not isinstance(body, dict):
            continue
        brand_id = body.get("brand_id")
        if not brand_id:
            continue
        rows.append(
            {
                "brand_id": brand_id,
                "name": (body.get("musician_handle") or brand_id).replace("_", " ").title(),
                "axis": "music",
                "tier": None,
                "locale": None,
                "catalog_id": None,
                "status": body.get("status") or "inactive",
                "topics": [],
                "demographic": None,
                "primary_topic": None,
                "notes": body.get("notes"),
                "archetype": body.get("archetype"),
                "musician_handle": body.get("musician_handle"),
            }
        )
    return rows


@router.get("/brand_index")
async def brand_index() -> dict[str, Any]:
    """Return the live 3-axis brand inventory (replaces inline 24-row catalog)."""
    book = _book_brand_rows()
    manga = _manga_brand_rows()
    music = _music_brand_rows()
    return {
        "book": book,
        "manga": manga,
        "music": music,
        "counts": {
            "book": len(book),
            "manga": len(manga),
            "music": len(music),
            "total": len(book) + len(manga) + len(music),
        },
        "sources": {
            "book": BOOK_REGISTRY.relative_to(REPO_ROOT).as_posix(),
            "manga": MANGA_REGISTRY.relative_to(REPO_ROOT).as_posix(),
            "music": MUSIC_REGISTRY.relative_to(REPO_ROOT).as_posix(),
        },
        "axes_note": (
            "Path X (BR-CANON-01): book and manga axes are intentionally distinct; "
            "music is a third axis per MUSIC-MODE-BRAND-INTEGRATION-V1-01. brand_id "
            "may appear on more than one axis (e.g. stillness_press exists on both "
            "book and manga)."
        ),
    }


# ── Books × platforms grid per brand ──────────────────────────────────────────

def _topics_for_brand(brand_id: str) -> tuple[str | None, list[str], str | None]:
    """Resolve (axis, topics, notes) for a brand_id across all 3 axes.

    Returns the first match in axis-priority order: manga -> book -> music.
    Manga is checked first because its topic vocabulary aligns directly with
    store_url_tracker.yaml's topic keys (anxiety / burnout / etc.); book brand
    family_allowlist values are content-family labels (alarm_fear_systems / ...)
    that do NOT match store_url_tracker topics directly.
    """
    manga_data = _load_yaml(MANGA_REGISTRY).get("brands") or {}
    if brand_id in manga_data and isinstance(manga_data[brand_id], dict):
        body = manga_data[brand_id]
        topics = []
        primary = body.get("primary_topic")
        if primary:
            topics.append(primary)
        for sec in body.get("secondary_topics") or []:
            if sec and sec not in topics:
                topics.append(sec)
        return "manga", topics, body.get("notes")

    book_data = _load_yaml(BOOK_REGISTRY).get("brands") or {}
    if brand_id in book_data and isinstance(book_data[brand_id], dict):
        body = book_data[brand_id]
        # family_allowlist != store_url_tracker topic vocab; pass through anyway
        # so the UI can render rows and show the schema. Operator surfaces this
        # ontology gap as a separate ws.
        return "book", list(body.get("family_allowlist") or []), None

    music_brands = _load_yaml(MUSIC_REGISTRY).get("music_brands") or []
    for body in music_brands:
        if isinstance(body, dict) and body.get("brand_id") == brand_id:
            return "music", [], body.get("notes")

    return None, [], None


def _platform_row_for_topic(topic_body: dict[str, Any]) -> dict[str, str | None]:
    """Pull the canonical platform columns out of a store_url_tracker topic row."""
    return {col: topic_body.get(col) for col in PLATFORM_COLUMNS}


@router.get("/brand/{brand_id}/books_by_platform")
async def books_by_platform(brand_id: str) -> dict[str, Any]:
    """For one brand, return {topic -> platform -> url} rows + empty-state framing."""
    if not brand_id or "/" in brand_id or ".." in brand_id:
        raise HTTPException(status_code=400, detail="Invalid brand_id")

    axis, topics, notes = _topics_for_brand(brand_id)
    if axis is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Brand '{brand_id}' not found on any axis "
                f"(book / manga / music). Check /api/brand_admin/brand_index."
            ),
        )

    tracker = _load_yaml(STORE_URL_TRACKER).get("topics") or {}
    books: list[dict[str, Any]] = []
    unmatched: list[str] = []
    for topic in topics:
        body = tracker.get(topic)
        if not isinstance(body, dict):
            unmatched.append(topic)
            continue
        platforms = _platform_row_for_topic(body)
        any_live = any(v for v in platforms.values())
        books.append(
            {
                "title": topic.replace("_", " ").title(),
                "topic": topic,
                "catalog_id": body.get("catalog_id"),
                "series_id": body.get("series_id"),
                "status": body.get("status"),
                "platforms": platforms,
                "any_live": any_live,
            }
        )

    return {
        "brand_id": brand_id,
        "axis": axis,
        "notes": notes,
        "books": books,
        "platforms_header": list(PLATFORM_COLUMNS),
        "empty_state_message": (
            "No books published yet."
            if not books
            else None
        ),
        "ontology_gap": (
            f"{len(unmatched)} of the brand's topic labels are not present as "
            f"keys in store_url_tracker.yaml: {unmatched}. This is a known data "
            f"wiring gap for the book axis (family_allowlist vocabulary differs "
            f"from per-topic store URLs); follow-up under "
            f"ws_brand_admin_store_url_backfill_*. Manga axis topic vocabulary "
            f"matches store_url_tracker directly."
            if unmatched
            else None
        ),
        "source": STORE_URL_TRACKER.relative_to(REPO_ROOT).as_posix(),
    }
