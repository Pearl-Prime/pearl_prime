#!/usr/bin/env python3
"""Validate a manga artifact JSON file against schemas/manga.

  PYTHONPATH=. python3 scripts/manga/validate_manga_json.py chapter_request path/to/file.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate manga JSON against schema stem.")
    parser.add_argument("schema_stem")
    parser.add_argument("json_path", type=Path)
    args = parser.parse_args()

    repo = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(repo))

    from phoenix_v4.manga.models.validation import load_and_validate

    try:
        load_and_validate(args.json_path.resolve(), args.schema_stem)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Validation failed: {e}", file=sys.stderr)
        return 1
    print("OK", args.schema_stem, args.json_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
