"""Manga author resolver for series setup.

Resolves or generates a manga EI character-author for a series based on
brand_id, genre, locale, topic, and persona demographic.  Used by the
series setup pipeline to attach an author identity to every manga series.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


def _yaml_safe_load(path: Path) -> Any:
    if yaml is None:
        return {}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


MANGA_AUTHORS_DIR = REPO_ROOT / "config" / "authoring" / "manga_authors"


def load_manga_authors() -> list[dict[str, Any]]:
    """Load all manga author profiles from config."""
    authors: list[dict[str, Any]] = []
    if not MANGA_AUTHORS_DIR.exists():
        return authors
    for p in sorted(MANGA_AUTHORS_DIR.glob("*.yaml")):
        if p.name == "schema.yaml":
            continue
        data = _yaml_safe_load(p)
        if isinstance(data, dict) and "author_id" in data:
            authors.append(data)
    return authors


def find_matching_author(
    *,
    brand_id: str,
    genre_id: str,
    locale: Optional[str] = None,
    topic: Optional[str] = None,
) -> Optional[dict[str, Any]]:
    """Find an existing manga author matching brand + genre (+ optional locale/topic).

    Returns the best match or None.
    """
    authors = load_manga_authors()
    # Score candidates
    best: Optional[dict[str, Any]] = None
    best_score = -1
    for a in authors:
        if a.get("brand_id") != brand_id:
            continue
        if a.get("genre_tie_in") != genre_id:
            continue
        if a.get("status", "active") != "active":
            continue
        score = 2  # brand + genre match
        if locale and a.get("locale") == locale:
            score += 1
        if topic and a.get("therapeutic_topic") == topic:
            score += 1
        if score > best_score:
            best_score = score
            best = a
    return best


def resolve_manga_author(
    *,
    brand_id: str,
    genre_id: str,
    locale: str = "en_US",
    topic: str = "anxiety",
    demographic: str = "anxious_millennials_urban",
    auto_generate: bool = False,
) -> Optional[dict[str, Any]]:
    """Resolve a manga author for a series.

    1. Try to find an existing matching author from config.
    2. If auto_generate=True and no match found, generate one on-the-fly.
    3. Otherwise return None (caller should handle).
    """
    match = find_matching_author(
        brand_id=brand_id, genre_id=genre_id, locale=locale, topic=topic,
    )
    if match is not None:
        return match

    if auto_generate:
        try:
            from scripts.manga.generate_manga_author import (
                generate_manga_author_profile,
                validate_no_collision,
                write_manga_author_profile,
            )
        except ImportError:
            return None

        profile = generate_manga_author_profile(
            brand_id=brand_id,
            genre=genre_id,
            locale=locale,
            topic=topic,
            demographic=demographic,
        )
        collisions = validate_no_collision(profile["display_name"], brand_id)
        if collisions:
            return None
        write_manga_author_profile(profile)
        return profile

    return None


def build_author_identity_artifact(author: dict[str, Any]) -> dict[str, Any]:
    """Build a series-level author identity artifact from a manga author profile."""
    return {
        "artifact_type": "manga_author_identity",
        "schema_version": "1.0.0",
        "author_id": author.get("author_id", ""),
        "display_name": author.get("display_name", ""),
        "genre_tie_in": author.get("genre_tie_in", ""),
        "brand_id": author.get("brand_id", ""),
        "locale": author.get("locale", ""),
        "ei_disclosure_text": author.get("ei_disclosure_text", ""),
        "bio_blurb": author.get("bio_blurb", ""),
        "visual_style_notes": author.get("visual_style_notes", ""),
    }
