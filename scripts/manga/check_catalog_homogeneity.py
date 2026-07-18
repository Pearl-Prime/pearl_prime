#!/usr/bin/env python3
"""Detect manga catalog homogeneity problems.

Scans all manga_profile YAML files and reports:
1. Profiles that share (emotional_engine, chapter_hook_family) — collision risk
2. Profiles that share (market_demo, genre_family, visual_grammar) — lane overlap

Usage:
    python3 scripts/manga/check_catalog_homogeneity.py
    python3 scripts/manga/check_catalog_homogeneity.py --profiles-dir config/source_of_truth/manga_profiles

Exit code 0 = clean, 1 = warnings, 2 = collisions found.
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from phoenix_v4.manga.series.profile_loader import load_profile, MangaProfile


def scan_profiles(profiles_dir: Path) -> list[MangaProfile]:
    profiles = []
    for p in sorted(profiles_dir.glob("**/*.yaml")):
        if p.name.startswith("schema"):
            continue
        # Skip reference examples — they are per-series demonstration files,
        # not catalog lane templates, and should not be checked for collisions.
        if "examples" in p.parts:
            continue
        try:
            profiles.append(load_profile(p))
        except Exception as exc:
            print(f"  SKIP {p.name}: {exc}", file=sys.stderr)
    return profiles


def check_homogeneity(profiles: list[MangaProfile]) -> tuple[list[str], list[str]]:
    """Returns (warnings, collisions)."""
    warnings = []
    collisions = []

    # Check 1: emotional_engine + chapter_hook_family collision
    hook_key: dict[tuple, list[str]] = defaultdict(list)
    for p in profiles:
        key = (p.emotional_engine, p.chapter_hook_family)
        hook_key[key].append(p.title_id)
    for (engine, hook), titles in hook_key.items():
        if len(titles) > 1:
            collisions.append(
                f"COLLISION: emotional_engine={engine!r} + chapter_hook_family={hook!r} "
                f"shared by: {', '.join(titles)}"
            )

    # Check 2: market_demo + genre_family + visual_grammar lane overlap
    lane_key: dict[tuple, list[str]] = defaultdict(list)
    for p in profiles:
        key = (p.market_demo, p.genre_family, p.visual_grammar)
        lane_key[key].append(p.title_id)
    for (demo, genre, grammar), titles in lane_key.items():
        if len(titles) > 1:
            warnings.append(
                f"LANE OVERLAP: {demo}/{genre}/{grammar} "
                f"shared by: {', '.join(titles)}"
            )

    return warnings, collisions


def main() -> int:
    parser = argparse.ArgumentParser(description="Check manga catalog homogeneity")
    parser.add_argument("--profiles-dir", default="config/source_of_truth/manga_profiles")
    args = parser.parse_args()

    profiles_dir = Path(args.profiles_dir)
    if not profiles_dir.is_dir():
        print(f"ERROR: profiles directory not found: {profiles_dir}", file=sys.stderr)
        return 2

    profiles = scan_profiles(profiles_dir)
    print(f"Scanned {len(profiles)} profile(s).")

    if not profiles:
        print("No profiles found — nothing to check.")
        return 0

    warnings, collisions = check_homogeneity(profiles)

    for w in warnings:
        print(f"  WARNING: {w}")
    for c in collisions:
        print(f"  COLLISION: {c}")

    if collisions:
        print(f"\nResult: {len(collisions)} collision(s), {len(warnings)} warning(s). EXIT 2.")
        return 2
    if warnings:
        print(f"\nResult: {len(warnings)} warning(s), no collisions. EXIT 1.")
        return 1

    print("Result: catalog homogeneity OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
