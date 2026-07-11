#!/usr/bin/env python3
"""Emit validated series artifacts under a workspace root (deterministic, no LLM)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Write series/*.json artifacts (Chunk B — deterministic setup)."
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="Workspace root (will contain series/style_bible.json, etc.)",
    )
    parser.add_argument("--series-id", required=True)
    parser.add_argument("--arc-id", required=True)
    parser.add_argument("--genre-id", required=True)
    parser.add_argument("--schema-version", default="1.0.0")
    parser.add_argument(
        "--mode",
        default="",
        choices=("", "teacher", "music"),
        help="Optional mode vessel (teacher|music) for story architecture",
    )
    parser.add_argument("--brand-id", default="", help="Brand ID for manga author resolution")
    parser.add_argument("--locale", default="en_US", help="Locale for manga author")
    parser.add_argument("--topic", default="anxiety", help="Therapeutic topic")
    parser.add_argument("--demographic", default="anxious_millennials_urban", help="Target demographic")
    parser.add_argument("--auto-generate-author", action="store_true", help="Auto-generate manga author if none found")
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo))

    from phoenix_v4.manga.series.emit import emit_series_setup

    emit_series_setup(
        args.workspace.resolve(),
        series_id=args.series_id,
        arc_id=args.arc_id,
        genre_id=args.genre_id,
        schema_version=args.schema_version,
        brand_id=args.brand_id,
        locale=args.locale,
        topic=args.topic,
        demographic=args.demographic,
        auto_generate_author=args.auto_generate_author,
        mode=(args.mode or None),
    )
    print("OK wrote series artifacts under", args.workspace.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
