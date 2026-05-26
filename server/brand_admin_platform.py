"""Shared platform slug + weekly package path helpers (brand admin v2 / OPD-145)."""
from __future__ import annotations

from pathlib import Path

# (platform_slug, deliverable_type)
PLATFORM_SPECS: tuple[tuple[str, str], ...] = (
    ("kdp", "books"),
    ("google_play", "books"),
    ("apple_books", "books"),
    ("kobo", "books"),
    ("webtoon", "manga_panels"),
    ("line_manga", "manga_panels"),
    ("piccoma", "manga_panels"),
    ("spotify_podcast", "podcast"),
    ("apple_podcasts", "podcast"),
    ("pearl_news", "pearl_news"),
)

PLATFORM_SLUGS: frozenset[str] = frozenset(s[0] for s in PLATFORM_SPECS)

PLATFORM_SLUG_BY_DISPLAY: dict[str, str] = {
    "Amazon KDP": "kdp",
    "Google Play": "google_play",
    "Apple Books": "apple_books",
    "Kobo": "kobo",
    "WEBTOON": "webtoon",
    "LINE Manga": "line_manga",
    "Piccoma": "piccoma",
    "Spotify Podcast": "spotify_podcast",
    "Apple Podcasts": "apple_podcasts",
    "Pearl News": "pearl_news",
}

DELIVERABLE_BY_PLATFORM: dict[str, str] = dict(PLATFORM_SPECS)


def monolithic_zip_path(packages_dir: Path, brand_id: str, week: str) -> Path:
    return packages_dir / brand_id / week / f"{brand_id}_{week}.zip"


def platform_zip_path(packages_dir: Path, brand_id: str, week: str, platform: str) -> Path:
    return packages_dir / brand_id / week / platform / f"{brand_id}_{week}_{platform}.zip"


def validate_platform_slug(platform: str) -> None:
    if platform not in PLATFORM_SLUGS:
        raise ValueError(f"Unknown platform: {platform}")
