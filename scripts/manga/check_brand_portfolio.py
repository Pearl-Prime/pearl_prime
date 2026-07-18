#!/usr/bin/env python3
"""Brand × genre portfolio allocation check — V2 manga pipeline Phase A.6.

Reads `config/manga/brand_genre_allocation.yaml` and validates that a
(brand_id, genre, locale) tuple is on-portfolio for the brand at that locale.

Per the cap entry MANGA-LAYERED-PIPELINE-V2-01 cross-cutting CC4: pre-render
check that prevents shipping mass-volume to a (brand, genre) the brand isn't
allocated to. Operator can still ship deliberately-off-portfolio ad-hoc
series (the `coexist` tentpole-divergence policy in the YAML) — this check
warns rather than hard-fails for low-allocation cells.

Thresholds (initial; Phase A baseline):
    allocation ≥ 10%  → ON_PORTFOLIO
    1% ≤ allocation < 10% → OFF_PORTFOLIO_WARN  (registered but de-prioritized)
    allocation == 0 / unregistered → OFF_PORTFOLIO_HARD (not in this brand's lane)

Usage:
    python3 scripts/manga/check_brand_portfolio.py \\
        --brand-id stillness_press \\
        --genre healing \\
        --locale en_US
"""
from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ALLOCATION_PATH = REPO_ROOT / "config" / "manga" / "brand_genre_allocation.yaml"

DEFAULT_ON_THRESHOLD = 10
DEFAULT_WARN_THRESHOLD = 1


class Verdict(str, Enum):
    ON = "ON_PORTFOLIO"
    WARN = "OFF_PORTFOLIO_WARN"
    HARD = "OFF_PORTFOLIO_HARD"


@dataclass
class PortfolioCheck:
    brand_id: str
    genre: str
    locale: str
    allocation_pct: float
    verdict: Verdict
    primary_genre: str | None = None
    tentpole_divergence: bool = False

    def to_dict(self) -> dict:
        return {
            "brand_id": self.brand_id,
            "genre": self.genre,
            "locale": self.locale,
            "allocation_pct": self.allocation_pct,
            "verdict": self.verdict.value,
            "primary_genre": self.primary_genre,
            "tentpole_divergence": self.tentpole_divergence,
        }

    def message(self) -> str:
        bits = [f"{self.verdict.value} {self.brand_id}/{self.genre}@{self.locale} ({self.allocation_pct}%)"]
        if self.primary_genre and self.primary_genre != self.genre:
            bits.append(f"brand primary: {self.primary_genre}")
        if self.tentpole_divergence:
            bits.append("tentpole_divergence registered")
        return "; ".join(bits)


def load_allocation_config(path: Path | None = None) -> dict:
    p = Path(path) if path else DEFAULT_ALLOCATION_PATH
    return yaml.safe_load(p.read_text())


def _allocation_pct(config: dict, brand_id: str, genre: str, locale: str) -> float:
    allocations = (config or {}).get("allocations") or {}
    locale_block = allocations.get(locale) or {}
    brand_block = locale_block.get(brand_id) or {}
    val = brand_block.get(genre)
    return float(val) if val is not None else 0.0


def _primary_genre(config: dict, brand_id: str, locale: str) -> str | None:
    allocations = (config or {}).get("allocations") or {}
    locale_block = allocations.get(locale) or {}
    brand_block = locale_block.get(brand_id) or {}
    if not brand_block:
        return None
    # Highest-weighted genre
    return max(brand_block.items(), key=lambda kv: kv[1])[0]


def _tentpole_divergence_registered(config: dict, brand_id: str, locale: str) -> bool:
    policy = (config or {}).get("tentpole_divergence_policy") or {}
    if not isinstance(policy, dict):
        return False
    entry = policy.get(brand_id) or policy.get(f"{brand_id}@{locale}")
    if isinstance(entry, dict):
        return (entry.get("decision") or "").lower() == "coexist"
    if isinstance(entry, str):
        return entry.lower() == "coexist"
    # Some configs nest by locale
    by_locale = entry if isinstance(entry, dict) else {}
    locale_entry = by_locale.get(locale) if isinstance(by_locale, dict) else None
    if isinstance(locale_entry, dict):
        return (locale_entry.get("decision") or "").lower() == "coexist"
    return False


def check_portfolio(
    brand_id: str,
    genre: str,
    locale: str,
    *,
    config: dict | None = None,
    on_threshold: float = DEFAULT_ON_THRESHOLD,
    warn_threshold: float = DEFAULT_WARN_THRESHOLD,
) -> PortfolioCheck:
    cfg = config if config is not None else load_allocation_config()
    pct = _allocation_pct(cfg, brand_id, genre, locale)
    primary = _primary_genre(cfg, brand_id, locale)
    divergence = _tentpole_divergence_registered(cfg, brand_id, locale)

    if pct >= on_threshold:
        verdict = Verdict.ON
    elif pct >= warn_threshold:
        verdict = Verdict.WARN
    else:
        verdict = Verdict.HARD

    return PortfolioCheck(
        brand_id=brand_id, genre=genre, locale=locale,
        allocation_pct=pct, verdict=verdict,
        primary_genre=primary, tentpole_divergence=divergence,
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand-id", required=True)
    ap.add_argument("--genre", required=True)
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--on-threshold", type=float, default=DEFAULT_ON_THRESHOLD)
    ap.add_argument("--warn-threshold", type=float, default=DEFAULT_WARN_THRESHOLD)
    ap.add_argument("--config", default=str(DEFAULT_ALLOCATION_PATH))
    args = ap.parse_args()

    cfg = load_allocation_config(Path(args.config))
    check = check_portfolio(
        args.brand_id, args.genre, args.locale,
        config=cfg,
        on_threshold=args.on_threshold,
        warn_threshold=args.warn_threshold,
    )
    print(check.message())
    return {Verdict.ON: 0, Verdict.WARN: 0, Verdict.HARD: 2}[check.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
