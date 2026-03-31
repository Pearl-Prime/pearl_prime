#!/usr/bin/env python3
"""Validate config/onboarding JSON: structure and allowed enum values."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "config" / "onboarding" / "example_registry.json"
CONFIG_DIR = ROOT / "config" / "onboarding"

REQUIRED_KEYS = (
    "id",
    "lane",
    "market",
    "locale",
    "persona",
    "topic",
    "format",
    "status",
    "proof_intent",
    "production_fidelity",
    "product_family",
    "caption",
    "version",
    "created_at",
    "visual_category",
)
STATUSES = frozenset({"ready", "planned", "missing"})
PROOF_INTENTS = frozenset({"ships_product", "teaches_persona", "teaches_topic", "teaches_comparison"})
FIDELITY = frozenset({"production", "pipeline_demo", "supporting_visual"})


def main() -> int:
    errors: list[str] = []

    for path in sorted(CONFIG_DIR.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            errors.append(f"{path.name}: invalid JSON — {e}")
            continue

        if path.name == "example_registry.json":
            if not isinstance(data, list):
                errors.append("example_registry.json: root must be an array")
                continue
            ids: set[str] = set()
            for i, row in enumerate(data):
                p = f"{path.name}[{i}]"
                if not isinstance(row, dict):
                    errors.append(f"{p}: row must be object")
                    continue
                for k in REQUIRED_KEYS:
                    if k not in row:
                        errors.append(f"{p}: missing key {k!r}")
                rid = row.get("id")
                if isinstance(rid, str):
                    if rid in ids:
                        errors.append(f"{p}: duplicate id {rid!r}")
                    ids.add(rid)
                st = row.get("status")
                if st not in STATUSES:
                    errors.append(f"{p}: status must be one of {sorted(STATUSES)}, got {st!r}")
                pi = row.get("proof_intent")
                if pi not in PROOF_INTENTS:
                    errors.append(f"{p}: proof_intent must be one of {sorted(PROOF_INTENTS)}, got {pi!r}")
                fid = row.get("production_fidelity")
                if fid not in FIDELITY:
                    errors.append(
                        f"{p}: production_fidelity must be one of {sorted(FIDELITY)}, got {fid!r}"
                    )
                asset_path = row.get("asset_path")
                if st == "ready" and (not isinstance(asset_path, str) or not asset_path.strip()):
                    errors.append(f"{p}: ready rows must include non-empty asset_path")
                if st != "ready" and row.get("source") == "onboarding_seed_asset":
                    errors.append(f"{p}: non-ready rows cannot declare source onboarding_seed_asset")
                pr = row.get("placeholder_reason")
                if pr is not None and not isinstance(pr, str):
                    errors.append(f"{p}: placeholder_reason must be a string when present")
        else:
            if not isinstance(data, (dict, list)):
                errors.append(f"{path.name}: root must be object or array")

    if errors:
        print("validate_onboarding_registry.py: FAILED", file=sys.stderr)
        for e in errors:
            print(e, file=sys.stderr)
        return 1

    print("validate_onboarding_registry.py: OK —", REGISTRY.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
