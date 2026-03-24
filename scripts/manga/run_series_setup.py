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
    )
    print("OK wrote series artifacts under", args.workspace.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
