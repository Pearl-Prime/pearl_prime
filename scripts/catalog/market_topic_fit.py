"""Load per-market topic fit / suppress lists from market_topic_fit.yaml."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

from scripts.catalog.locale_paths import normalize_lane_id

ROOT = Path(__file__).resolve().parents[2]
FIT_PATH = ROOT / "config/catalog_planning/market_topic_fit.yaml"


@lru_cache(maxsize=1)
def _registry() -> dict:
    return yaml.safe_load(FIT_PATH.read_text(encoding="utf-8")) or {}


def _market_for_lane(lane_id: str) -> dict | None:
    lane_id = normalize_lane_id(lane_id)
    for _market_id, rec in (_registry().get("markets") or {}).items():
        if rec.get("locale") == lane_id:
            return rec
    return None


def fit_topics_for_lane(lane_id: str) -> list[str] | None:
    """Return ordered fit topic ids for lane, or None if no market entry."""
    rec = _market_for_lane(lane_id)
    if not rec:
        return None
    fit = rec.get("fit") or {}
    return sorted(fit.keys())


def suppress_topics_for_lane(lane_id: str) -> set[str]:
    """Topics hard-suppressed for lane (empty if none)."""
    rec = _market_for_lane(lane_id)
    if not rec:
        return set()
    return set((rec.get("suppress") or {}).keys())


def topics_for_generation(lane_id: str, default_topics: list[str]) -> list[str]:
    """Fit-only topic list when market registry defines fit; else default."""
    fit = fit_topics_for_lane(lane_id)
    return fit if fit else list(default_topics)
