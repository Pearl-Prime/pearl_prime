#!/usr/bin/env python3
"""Resolve compiled manga panel prompts against an asset bank before requesting new renders."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.asset_resolver import resolve_panel_assets
from scripts.manga._config import load_json, load_yaml, should_skip_output, write_atomically


def _load_bank(bank_path: Path) -> list[dict]:
    if not bank_path.exists():
        return []
    text = bank_path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    if text.startswith("["):
        return load_json(bank_path)
    assets = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        assets.append(json.loads(line))
    return assets


def main() -> int:
    ap = argparse.ArgumentParser(description="Resolve manga panel prompts against image bank assets")
    ap.add_argument("panel_prompts", help="Path to panel_prompts.json")
    ap.add_argument("-o", "--out", required=True, help="Output resolved_assets.json path")
    ap.add_argument("--bank", help="Optional path to image bank index (JSON array or JSONL)")
    ap.add_argument("--force", action="store_true", help="Overwrite output even if it already exists")
    args = ap.parse_args()

    prompt_path = Path(args.panel_prompts)
    if not prompt_path.exists():
        print(f"Error: not found: {prompt_path}", file=sys.stderr)
        return 1

    prompt_doc = load_json(prompt_path)
    bank_assets = _load_bank(Path(args.bank)) if args.bank else []
    priority = load_yaml("config/manga/asset_selection_priority.yaml")

    out_path = Path(args.out)
    if should_skip_output(out_path, ["chapter_id", "resolved"], args.force, prompt_doc.get("config_hash")):
        print(f"Skip (output exists, use --force to overwrite): {out_path}")
        return 0

    result = resolve_panel_assets(prompt_doc, bank_assets, priority=priority)
    write_atomically(out_path, result)
    print(
        f"Wrote resolved assets for {len(result['resolved'])} panels to {out_path} "
        f"({len(result['unresolved_panel_ids'])} need generation)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
