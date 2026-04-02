#!/usr/bin/env python3
"""Compile a chapter request into panel_prompts.json for Colab or later render backends."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.panel_prompt_manifest import compile_panel_prompts
from scripts.manga._config import config_snapshot_hash, load_json_or_yaml, should_skip_output, write_atomically


def main() -> int:
    ap = argparse.ArgumentParser(description="Compile manga panel prompt manifest from chapter request JSON/YAML")
    ap.add_argument("chapter_request", help="Path to chapter request JSON/YAML")
    ap.add_argument("-o", "--out", required=True, help="Output panel_prompts.json path")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists")
    args = ap.parse_args()

    request_path = Path(args.chapter_request)
    if not request_path.exists():
        print(f"Error: not found: {request_path}", file=sys.stderr)
        return 1

    out_path = Path(args.out)
    snapshot = config_snapshot_hash()
    if should_skip_output(out_path, ["chapter_id", "panels", "config_hash"], args.force, snapshot):
        print(f"Skip (output exists, use --force to overwrite): {out_path}")
        return 0

    chapter_request = load_json_or_yaml(request_path)
    doc = compile_panel_prompts(chapter_request, config_hash=snapshot)
    write_atomically(out_path, doc)
    print(f"Wrote {len(doc['panels'])} panel prompts to {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
