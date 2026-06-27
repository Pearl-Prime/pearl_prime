"""Locale → book/series plan directory helpers for catalog bridge scripts."""
from __future__ import annotations

from pathlib import Path

# Canonical lane_ids from global_brand_registry_unified.yaml (14 lanes).
SUPPORTED_LANE_IDS = frozenset({
    "en_US", "de_DE", "fr_FR", "es_ES", "es_US", "it_IT", "hu_HU", "pt_BR",
    "ja_JP", "ko_KR", "zh_TW", "zh_CN", "zh_HK", "zh_SG",
})

# CJK6: structural skeletons are bridge-safe; content authoring is translation/voice-gated.
CJK6_LANE_IDS = frozenset({"ja_JP", "ko_KR", "zh_CN", "zh_HK", "zh_SG", "zh_TW"})


def locale_slug(lane_id: str) -> str:
    """en_US → en_us (directory suffix under config/source_of_truth/)."""
    return lane_id.replace("-", "_").lower()


def plan_dirs(root: Path, lane_id: str) -> tuple[Path, Path]:
    slug = locale_slug(lane_id)
    base = root / "config/source_of_truth"
    return base / f"book_plans_{slug}", base / f"series_plans_{slug}"


def normalize_lane_id(raw: str) -> str:
    """Accept en_US, en-us, en_us → en_US."""
    if raw in SUPPORTED_LANE_IDS:
        return raw
    candidate = raw.replace("-", "_")
    for lane in SUPPORTED_LANE_IDS:
        if candidate.lower() == lane.lower():
            return lane
    supported = ", ".join(sorted(SUPPORTED_LANE_IDS))
    raise SystemExit(f"unsupported locale/lane_id {raw!r}; expected one of: {supported}")
