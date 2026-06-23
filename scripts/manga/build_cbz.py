#!/usr/bin/env python3
"""Build CBZ with ComicInfo.xml from composed manga pages."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path
from typing import Any

from phoenix_v4.manga.distribution.config_io import age_rating_for_market_demo
from scripts.manga._output_pipeline_xml import xml_escape


def _comicinfo_xml(profile: dict[str, Any]) -> str:
    title = str(profile.get("series_title") or profile.get("title_id") or "Manga")
    description = str(profile.get("series_description") or "").strip()
    logline = str(profile.get("series_logline") or "").strip()
    audience = str(profile.get("audience") or "").strip()
    positioning = str(profile.get("positioning") or "").strip()
    parts = [description]
    if logline:
        parts.append(logline)
    if audience:
        parts.append(f"Audience:\n{audience.strip()}")
    if positioning:
        parts.append(f"Positioning:\n{positioning.strip()}")
    summary = "\n\n".join(p for p in parts if p)

    genre_family = str(profile.get("genre_family") or "")
    subgenre = str(profile.get("subgenre") or "")
    genre = f"{genre_family} / {subgenre}".strip(" /")
    market_demo = str(profile.get("market_demo") or "")
    age = age_rating_for_market_demo(market_demo)
    reading = "RightToLeft"

    return (
        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
        "<ComicInfo>"
        f"<Title>{xml_escape(title)}</Title>"
        f"<Series>{xml_escape(title)}</Series>"
        "<Number>1</Number>"
        f"<Summary>{xml_escape(summary)}</Summary>"
        "<Manga>Yes</Manga>"
        f"<ReadingDirection>{reading}</ReadingDirection>"
        f"<Genre>{xml_escape(genre)}</Genre>"
        f"<AgeRating>{xml_escape(age)}</AgeRating>"
        "</ComicInfo>"
    )


def build_cbz(
    *,
    profile: dict[str, Any],
    pages: list[Path],
    out_path: Path,
) -> Path:
    title_id = str(profile.get("title_id") or "manga")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    comicinfo = _comicinfo_xml(profile)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("ComicInfo.xml", comicinfo)
        for idx, page in enumerate(pages, start=1):
            zf.write(page, arcname=f"{idx:03d}.png")

    sidecar = out_path.parent / f"{title_id}_cbz_metadata.json"
    sidecar.write_text(
        json.dumps(
            {
                "title_id": title_id,
                "comp_titles": profile.get("comp_titles") or [],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return out_path
