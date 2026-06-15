"""
Brand Admin public read-only API (no auth) — operations dashboard v2 + brand index.

Prefix: /api/brand_admin (shared with brand_admin_download.py).

Endpoints (PR #1296 base + v2 weekly-work):
  GET /api/brand_admin/brand_index
  GET /api/brand_admin/brand/{brand_id}/books_by_platform
  GET /api/brand_admin/brand/{brand_id}/planned_volumes
  GET /api/brand_admin/brand/{brand_id}/weekly?week=<YYYY-WW>
"""
from __future__ import annotations

import json
import logging
import re
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

from fastapi import APIRouter, HTTPException

from server.brand_admin_platform import (
    PLATFORM_SLUG_BY_DISPLAY,
    monolithic_zip_path,
    platform_zip_path,
)

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]

router = APIRouter(prefix="/api/brand_admin", tags=["brand-admin-public"])

BOOK_REGISTRY = REPO_ROOT / "config" / "brand_registry.yaml"
MANGA_REGISTRY = REPO_ROOT / "config" / "manga" / "canonical_brand_list.yaml"
MANGA_SERIES_PLAN = REPO_ROOT / "config" / "manga" / "manga_brand_series_plan.yaml"
MANGA_CANON_PLANNED = REPO_ROOT / "config" / "brand_admin" / "manga_canon_planned_volumes.yaml"
MUSIC_REGISTRY = REPO_ROOT / "config" / "music" / "music_brand_registry.yaml"
UNIFIED_REGISTRY = REPO_ROOT / "config" / "brand_management" / "global_brand_registry_unified.yaml"
STORE_URL_TRACKER = REPO_ROOT / "config" / "funnel" / "store_url_tracker.yaml"
PACKAGES_DIR = REPO_ROOT / "artifacts" / "weekly_packages"
COORD_DIR = REPO_ROOT / "artifacts" / "coordination"

PLATFORM_COLUMNS = ("kdp", "apple_books", "google_play", "kobo", "store_url_live")

DELIVERABLE_TYPES = ("books", "atoms", "manga_panels", "pearl_news", "podcast", "audiobook")

WEEK_ISO_RE = re.compile(r"^\d{4}-W(0[1-9]|[1-4]\d|5[0-3])$")
MONDAY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

# Operator-facing platform rows mapped from manifest deliverable keys (atoms omitted).
# Audible + Google Play Audiobooks added per AMENDMENT-2026-05-27 §3 (audiobook axis).
PLATFORM_ROW_DEFS: tuple[tuple[str, str, str], ...] = (
    ("Amazon KDP", "books", "books for KDP"),
    ("Google Play", "books", "books for Google Play"),
    ("Apple Books", "books", "books for Apple Books"),
    ("Kobo", "books", "books for Kobo"),
    ("WEBTOON", "manga_panels", "manga episodes"),
    ("LINE Manga", "manga_panels", "manga episodes"),
    ("Piccoma", "manga_panels", "manga episodes"),
    ("Spotify Podcast", "podcast", "podcast MP3s"),
    ("Apple Podcasts", "podcast", "podcast MP3s"),
    ("Audible", "audiobook", "audiobook M4B(s)"),
    ("Google Play Audiobooks", "audiobook", "audiobook M4B(s)"),
    ("Pearl News", "pearl_news", "Pearl News articles"),
)


def _load_yaml(path: Path) -> dict:
    if yaml is None or not path.is_file():
        return {}
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:  # pragma: no cover
        logger.warning("YAML parse failed for %s: %s", path, exc)
        return {}


def _validate_brand_id(brand_id: str) -> None:
    if not brand_id or "/" in brand_id or ".." in brand_id:
        raise HTTPException(status_code=400, detail="Invalid brand_id")


def _validate_week_token(week: str) -> None:
    if not week or "/" in week or ".." in week or "\\" in week:
        raise HTTPException(status_code=400, detail="Invalid week")


def week_iso_label(d: date) -> str:
    iso = d.isocalendar()
    return f"{iso.year}-W{iso.week:02d}"


def iso_week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def parse_week_param(week: Optional[str]) -> str:
    """Accept YYYY-Www or Monday YYYY-MM-DD; return YYYY-Www."""
    if week is None or not str(week).strip():
        return week_iso_label(datetime.now(tz=timezone.utc).date())
    token = str(week).strip()
    _validate_week_token(token)
    if WEEK_ISO_RE.match(token):
        return token
    if MONDAY_RE.match(token):
        try:
            d = date.fromisoformat(token)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid week date") from exc
        return week_iso_label(d)
    raise HTTPException(status_code=400, detail="Week must be YYYY-Www or YYYY-MM-DD (Monday)")


def _brand_exists(brand_id: str) -> bool:
    if brand_id in (_load_yaml(UNIFIED_REGISTRY).get("brands") or {}):
        return True  # unified 39×14 ids (e.g. somatic_wisdom_en_us) — what the wizard now assigns
    manga = (_load_yaml(MANGA_REGISTRY).get("brands") or {})
    if brand_id in manga:
        return True
    book = (_load_yaml(BOOK_REGISTRY).get("brands") or {})
    if brand_id in book:
        return True
    for body in _load_yaml(MUSIC_REGISTRY).get("music_brands") or []:
        if isinstance(body, dict) and body.get("brand_id") == brand_id:
            return True
    return False


def _axes_for_brand(brand_id: str) -> list[str]:
    axes: list[str] = []
    if brand_id in (_load_yaml(MANGA_REGISTRY).get("brands") or {}):
        axes.append("manga")
    if brand_id in (_load_yaml(BOOK_REGISTRY).get("brands") or {}):
        axes.append("book")
    for body in _load_yaml(MUSIC_REGISTRY).get("music_brands") or []:
        if isinstance(body, dict) and body.get("brand_id") == brand_id:
            axes.append("music")
            break
    return axes


def _unified_brand_rows() -> list[dict]:
    """The unified 39×14 registry (global_brand_registry_unified.yaml) — the canonical brand set
    the wizard matches/assigns to. Each brand carries its lane's manga% (manga not standalone)."""
    brands = _load_yaml(UNIFIED_REGISTRY).get("brands") or {}
    rows: list[dict] = []
    for brand_id, body in brands.items():
        if not isinstance(body, dict):
            continue
        pct = body.get("lane_manga_pct")
        axes = ["book"] + (["manga"] if isinstance(pct, (int, float)) and pct > 0 else [])
        rows.append({
            "brand_id": brand_id,
            "name": body.get("publication_corp") or body.get("display_name") or brand_id,
            "axis": "book",
            "axes_present": axes,
            "lane": body.get("lane_id"),
            "locale": body.get("locale"),
            "status": body.get("lifecycle") or "active",
            "topics": body.get("primary_topics") or [],
            "lane_manga_pct": pct,
            "publication_corp": body.get("publication_corp"),
            "teacher_id": body.get("teacher_id"),
        })
    return rows


def _book_brand_rows() -> list[dict]:
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
    unified = _unified_brand_rows()
    book = _book_brand_rows()
    manga = _manga_brand_rows()
    music = _music_brand_rows()
    return {
        "unified": unified,   # canonical 39×14 — the brand set the wizard matches/assigns to
        "book": book,
        "manga": manga,
        "music": music,
        "counts": {
            "unified": len(unified),
            "book": len(book),
            "manga": len(manga),
            "music": len(music),
            "total": len(book) + len(manga) + len(music),
        },
        "sources": {
            "unified": UNIFIED_REGISTRY.relative_to(REPO_ROOT).as_posix(),
            "book": BOOK_REGISTRY.relative_to(REPO_ROOT).as_posix(),
            "manga": MANGA_REGISTRY.relative_to(REPO_ROOT).as_posix(),
            "music": MUSIC_REGISTRY.relative_to(REPO_ROOT).as_posix(),
        },
        "operator_visible_canon": {
            "default": "manga",
            "count": len(manga),
            "note": "BR-CANON-02 pending: operator-visible 37 = manga canonical slots 1–37",
        },
        "axes_note": (
            "Path X (BR-CANON-01): book and manga axes are intentionally distinct; "
            "music is a third axis. brand_id may appear on more than one axis."
        ),
    }


def _topics_for_brand(brand_id: str) -> tuple[str | None, list[str], str | None]:
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
        return "book", list(body.get("family_allowlist") or []), None

    music_brands = _load_yaml(MUSIC_REGISTRY).get("music_brands") or []
    for body in music_brands:
        if isinstance(body, dict) and body.get("brand_id") == brand_id:
            return "music", [], body.get("notes")

    return None, [], None


def _platform_row_for_topic(topic_body: dict[str, Any]) -> dict[str, str | None]:
    return {col: topic_body.get(col) for col in PLATFORM_COLUMNS}


@router.get("/brand/{brand_id}/books_by_platform")
async def books_by_platform(brand_id: str) -> dict[str, Any]:
    _validate_brand_id(brand_id)
    axis, topics, notes = _topics_for_brand(brand_id)
    if axis is None:
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    tracker = _load_yaml(STORE_URL_TRACKER).get("topics") or {}
    books: list[dict[str, Any]] = []
    unmatched: list[str] = []
    for topic in topics:
        body = tracker.get(topic)
        if not isinstance(body, dict):
            unmatched.append(topic)
            continue
        platforms = _platform_row_for_topic(body)
        books.append(
            {
                "title": topic.replace("_", " ").title(),
                "topic": topic,
                "catalog_id": body.get("catalog_id"),
                "series_id": body.get("series_id"),
                "status": body.get("status"),
                "platforms": platforms,
                "any_live": any(v for v in platforms.values()),
            }
        )

    return {
        "brand_id": brand_id,
        "axis": axis,
        "notes": notes,
        "books": books,
        "platforms_header": list(PLATFORM_COLUMNS),
        "empty_state_message": "No books published yet." if not books else None,
        "ontology_gap": (
            f"{len(unmatched)} topic labels not in store_url_tracker.yaml: {unmatched}"
            if unmatched
            else None
        ),
        "source": STORE_URL_TRACKER.relative_to(REPO_ROOT).as_posix(),
    }


def _locales_for_brand(brand_id: str) -> list[str]:
    locales: list[str] = []
    book = (_load_yaml(BOOK_REGISTRY).get("brands") or {})
    for bid, body in book.items():
        if not isinstance(body, dict):
            continue
        if bid == brand_id or bid.startswith(f"{brand_id}_") or brand_id in bid:
            loc = body.get("locale")
            if loc and loc not in locales:
                locales.append(loc)
    if not locales and brand_id in (_load_yaml(MANGA_REGISTRY).get("brands") or {}):
        locales.append("en_US")
    return locales


def _manga_canon_planned_body(brand_id: str) -> dict[str, Any]:
    doc = _load_yaml(MANGA_CANON_PLANNED)
    body = (doc.get("brands") or {}).get(brand_id)
    return body if isinstance(body, dict) else {}


def _series_plan_body_for_brand(brand_id: str) -> dict[str, Any]:
    """Resolve manga_brand_series_plan row via canon alias or direct brand_id."""
    plan_doc = _load_yaml(MANGA_SERIES_PLAN)
    series = plan_doc.get("brands") or {}
    canon_row = _manga_canon_planned_body(brand_id)
    plan_key = canon_row.get("series_plan_key") or brand_id
    body = series.get(plan_key) if isinstance(series.get(plan_key), dict) else {}
    if not body:
        body = series.get(brand_id) if isinstance(series.get(brand_id), dict) else {}
    return body


@router.get("/brand/{brand_id}/planned_volumes")
async def planned_volumes(brand_id: str) -> dict[str, Any]:
    _validate_brand_id(brand_id)
    if not _brand_exists(brand_id):
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    gaps: list[str] = []
    manga_body = (_load_yaml(MANGA_REGISTRY).get("brands") or {}).get(brand_id) or {}
    canon_planned = _manga_canon_planned_body(brand_id)
    series_body = _series_plan_body_for_brand(brand_id)
    defaults = _load_yaml(MANGA_SERIES_PLAN).get("global_defaults") or {}
    tier_defaults = (_load_yaml(MANGA_CANON_PLANNED).get("tier_defaults") or {}).get(
        canon_planned.get("tier") or (manga_body.get("tier") if isinstance(manga_body, dict) else None)
        or "core",
        {},
    )

    ebooks = (
        canon_planned.get("volumes_per_year_target")
        or series_body.get("volumes_per_year_target")
        or tier_defaults.get("volumes_per_year_target")
        or defaults.get("volumes_per_year_target")
    )
    if ebooks is None:
        gaps.append("ebook plan absent")

    manga_series = (
        canon_planned.get("active_series_target")
        or series_body.get("active_series_target")
        or tier_defaults.get("active_series_target")
        or defaults.get("active_series_target")
    )
    if manga_series is None and brand_id not in (_load_yaml(MANGA_REGISTRY).get("brands") or {}):
        gaps.append("manga series plan absent")

    podcast = (
        canon_planned.get("episodes_per_year_target")
        or tier_defaults.get("episodes_per_year_target")
    )
    if podcast is None:
        gaps.append("podcast plan absent")

    audiobook = (
        canon_planned.get("titles_per_year_target")
        or tier_defaults.get("titles_per_year_target")
    )
    if audiobook is None:
        gaps.append("audiobook plan absent")

    parts: list[str] = []
    if ebooks is not None:
        parts.append(f"{ebooks} ebooks/yr")
    if manga_series is not None:
        parts.append(f"{manga_series} manga series")
    if podcast is not None:
        parts.append(f"{podcast} podcasts/yr")
    if audiobook is not None:
        parts.append(f"{audiobook} audiobooks/yr")
    locales = _locales_for_brand(brand_id)
    if locales:
        parts.append(f"{len(locales)} locale{'s' if len(locales) != 1 else ''}")

    name = brand_id.replace("_", " ").title()
    if isinstance(manga_body, dict) and manga_body.get("notes"):
        name = manga_body.get("notes", name)[:60]

    return {
        "brand_id": brand_id,
        "name": name,
        "planned": {
            "ebooks": ebooks,
            "manga_series": manga_series,
            "podcast": podcast,
            "audiobook": audiobook,
        },
        "locales_active": locales,
        "summary_line": " · ".join(parts) if parts else "No plan data yet",
        "gaps": gaps,
        "axes_present": _axes_for_brand(brand_id),
        "source": MANGA_CANON_PLANNED.relative_to(REPO_ROOT).as_posix()
        if canon_planned
        else MANGA_SERIES_PLAN.relative_to(REPO_ROOT).as_posix(),
    }


def _load_manifest(brand_id: str, week: str) -> Optional[dict[str, Any]]:
    path = PACKAGES_DIR / brand_id / week / "manifest.json"
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _deliverables_from_manifest(manifest: Optional[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    raw = (manifest or {}).get("deliverables") or {}
    for dtype in DELIVERABLE_TYPES:
        block = raw.get(dtype) if isinstance(raw, dict) else None
        if not isinstance(block, dict):
            out[dtype] = {"count": 0, "files": [], "status": "pending"}
            continue
        files = block.get("files") or []
        out[dtype] = {
            "count": len(files),
            "files": files,
            "status": block.get("status") or ("ready" if files else "pending"),
        }
    return out


def _package_zip_url(brand_id: str, week: str) -> Optional[str]:
    zip_path = monolithic_zip_path(PACKAGES_DIR, brand_id, week)
    if zip_path.is_file() and zip_path.stat().st_size > 0:
        return f"/api/brand_admin/download/{brand_id}/{week}"
    return None


def _platform_download_url(brand_id: str, week: str, platform_display: str, count: int) -> Optional[str]:
    if count <= 0:
        return None
    slug = PLATFORM_SLUG_BY_DISPLAY.get(platform_display)
    if not slug:
        return None
    zip_path = platform_zip_path(PACKAGES_DIR, brand_id, week, slug)
    if zip_path.is_file() and zip_path.stat().st_size > 0:
        return f"/api/brand_admin/download/{brand_id}/{week}?platform={slug}"
    return None


def _package_status(brand_id: str, week: str) -> str:
    zip_path = monolithic_zip_path(PACKAGES_DIR, brand_id, week)
    manifest = PACKAGES_DIR / brand_id / week / "manifest.json"
    if zip_path.is_file() and zip_path.stat().st_size > 0:
        return "current"
    if manifest.is_file():
        return "stale"
    return "missing"


def _history_weeks(brand_id: str, current_week: str, limit: int = 12) -> list[str]:
    brand_dir = PACKAGES_DIR / brand_id
    if not brand_dir.is_dir():
        return []
    weeks = []
    for child in brand_dir.iterdir():
        if child.is_dir() and WEEK_ISO_RE.match(child.name) and child.name != current_week:
            weeks.append(child.name)

    def sort_key(w: str) -> tuple[int, int]:
        y, ww = w.split("-W")
        return int(y), int(ww)

    weeks.sort(key=sort_key, reverse=True)
    return weeks[:limit]


def _platform_rows(
    brand_id: str,
    week: str,
    deliverables: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for platform, dtype, label in PLATFORM_ROW_DEFS:
        key = (platform, dtype)
        if key in seen:
            continue
        seen.add(key)
        block = deliverables.get(dtype, {"count": 0, "files": [], "status": "pending"})
        count = int(block.get("count") or 0)
        if count:
            blurb = f"{count} {label}"
        else:
            blurb = f"0 {label} this week"
        dl = _platform_download_url(brand_id, week, platform, count)
        rows.append(
            {
                "platform": platform,
                "platform_id": PLATFORM_SLUG_BY_DISPLAY.get(platform),
                "from_deliverable": dtype,
                "blurb": blurb,
                "download_url": dl,
                "deemphasized": dl is None,
            }
        )
    return rows


@router.get("/brand/{brand_id}/weekly")
async def brand_weekly(
    brand_id: str,
    week: Optional[str] = None,
) -> dict[str, Any]:
    _validate_brand_id(brand_id)
    if not _brand_exists(brand_id):
        raise HTTPException(status_code=404, detail=f"Brand '{brand_id}' not found")

    week_iso = parse_week_param(week)
    manifest = _load_manifest(brand_id, week_iso)
    deliverables = _deliverables_from_manifest(manifest)
    zip_url = _package_zip_url(brand_id, week_iso)

    return {
        "brand_id": brand_id,
        "week": week_iso,
        "package_zip_url": zip_url,
        "package_status": _package_status(brand_id, week_iso),
        "deliverables": deliverables,
        "platform_rows": _platform_rows(brand_id, week_iso, deliverables),
        "history_weeks": _history_weeks(brand_id, week_iso),
        "build_hint": (
            None
            if zip_url
            else f"python3 scripts/build_weekly_brand_package.py --brand {brand_id} --week {week_iso}"
        ),
    }
