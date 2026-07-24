#!/usr/bin/env python3
"""Fail-closed coverage audit for canonical Storyblocks cover imagery."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import yaml
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
from scripts.publish.bank_image_picker import DEFAULT_TOPIC_MAP, read_index, load_topic_map, validate_candidate
from scripts.storyblocks.license_store import DEFAULT_INDEX_PATH

DEFAULT_CATALOG = REPO_ROOT / "config/catalog/catalog_generation_config.yaml"

def audit(index_path: Path = DEFAULT_INDEX_PATH, topic_map_path: Path = DEFAULT_TOPIC_MAP,
          catalog_path: Path = DEFAULT_CATALOG) -> dict:
    canonical = yaml.safe_load(catalog_path.read_text())["topics"]
    mapping = load_topic_map(topic_map_path)
    rows = list(read_index(index_path))
    coverage = {}
    for topic in canonical:
        valid = [r for r in rows if not validate_candidate(r, topic, mapping)]
        coverage[topic] = {"valid": len(valid), "stock_ids": [str(r.get("storyblocks_stock_id")) for r in valid]}
    missing_map = sorted(set(canonical) - set(mapping["topics"]))
    uncovered = sorted(t for t, v in coverage.items() if not v["valid"])
    return {"ok": not missing_map and not uncovered, "canonical_topics": len(canonical),
            "missing_topic_rules": missing_map, "uncovered_topics": uncovered, "coverage": coverage}

def main() -> int:
    p = argparse.ArgumentParser(); p.add_argument("--index", type=Path, default=DEFAULT_INDEX_PATH); p.add_argument("--json", action="store_true")
    args = p.parse_args(); result = audit(index_path=args.index)
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else f"Storyblocks cover coverage: {len(result['coverage'])-len(result['uncovered_topics'])}/{result['canonical_topics']} topics; uncovered={result['uncovered_topics']}")
    return 0 if result["ok"] else 1
if __name__ == "__main__": raise SystemExit(main())
