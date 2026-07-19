#!/usr/bin/env python3
"""Resolve 5 broll plates for an evergreen topic (nearest stock folder fallback)."""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
STOCK = (
    REPO
    / "artifacts/stock_image_bank/way_stream_sanctuary/mental_health_editorial_100x"
    / "downloads/pexels"
)

# Evergreen topic → pexels editorial folder (or nearest)
TOPIC_STOCK_FOLDER = {
    "addiction": "healing",
    "adhd": "overthinking",
    "anxiety": "anxiety",
    "body_image": "self_worth",
    "boundaries": "boundaries",
    "burnout": "burnout",
    "compassion_fatigue": "healing",
    "courage": "hope",
    "depression": "depression",
    "divorce": "grief",
    "financial_anxiety": "anxiety",
    "grief": "grief",
    "imposter_syndrome": "self_worth",
    "money": "hope",
    "overthinking": "overthinking",
    "relationship_anxiety": "loneliness",
    "self_worth": "self_worth",
    "shame": "healing",
    "sleep_anxiety": "loneliness",
    "social_anxiety": "anxiety",
}

FALLBACK_FOLDERS = (
    "anxiety",
    "hope",
    "healing",
    "boundaries",
    "overthinking",
    "burnout",
    "depression",
    "grief",
    "self_worth",
    "loneliness",
)


def _list_images(folder: Path) -> list[Path]:
    if not folder.is_dir():
        return []
    out: list[Path] = []
    for pat in ("*.jpeg", "*.jpg", "*.png", "*.webp"):
        out.extend(sorted(folder.glob(pat)))
    return [p for p in out if p.is_file() and p.stat().st_size > 20_000]


def plates_for_topic(topic: str, n: int = 5) -> list[Path]:
    """Return n existing plate paths for topic (hard-fail if none)."""
    folder_name = TOPIC_STOCK_FOLDER.get(topic, "anxiety")
    images = _list_images(STOCK / folder_name)
    if len(images) < n:
        for fb in FALLBACK_FOLDERS:
            if fb == folder_name:
                continue
            extra = _list_images(STOCK / fb)
            for p in extra:
                if p not in images:
                    images.append(p)
                if len(images) >= n:
                    break
            if len(images) >= n:
                break
    if len(images) < n:
        raise FileNotFoundError(
            f"need {n} plates for topic={topic!r} (folder={folder_name}); found {len(images)}"
        )
    # Prefer spread across list
    if len(images) == n:
        return images
    step = max(1, len(images) // n)
    picked = [images[(i * step) % len(images)] for i in range(n)]
    # dedupe while preserving length
    seen: set[Path] = set()
    out: list[Path] = []
    for p in picked:
        if p not in seen:
            out.append(p)
            seen.add(p)
    for p in images:
        if len(out) >= n:
            break
        if p not in seen:
            out.append(p)
            seen.add(p)
    return out[:n]
