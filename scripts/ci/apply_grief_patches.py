#!/usr/bin/env python3
"""Merge grief registry patch files into registry/grief.yaml.

Usage: python3 scripts/ci/apply_grief_patches.py
"""
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
GRIEF_YAML = REPO / "registry" / "grief.yaml"
PATCH_FILES = [
    REPO / "registry" / "grief_patch_ch1-3.yaml",
    REPO / "registry" / "grief_patch_ch4-6.yaml",
    REPO / "registry" / "grief_patch_ch7-9.yaml",
    REPO / "registry" / "grief_patch_ch10-12.yaml",
]


def apply_patches():
    with open(GRIEF_YAML) as f:
        data = yaml.safe_load(f)

    sections = data["sections"]
    total_added = 0

    for patch_file in PATCH_FILES:
        if not patch_file.exists():
            print(f"MISSING patch: {patch_file.name}", file=sys.stderr)
            continue
        with open(patch_file) as f:
            patch = yaml.safe_load(f)

        for ch_key, ch_patch in patch.items():
            if ch_key not in sections:
                print(f"WARN: chapter key {ch_key!r} not in grief.yaml", file=sys.stderr)
                continue
            ch_sections = sections[ch_key]["sections"]
            for sec_key, sec_patch in ch_patch.items():
                if sec_key not in ch_sections:
                    print(f"WARN: {ch_key}/{sec_key} not found", file=sys.stderr)
                    continue
                new_variants = sec_patch.get("new_variants") or []
                if not new_variants:
                    print(f"WARN: {ch_key}/{sec_key} has no new_variants", file=sys.stderr)
                    continue
                existing = ch_sections[sec_key].setdefault("variants", [])
                existing.extend(new_variants)
                total_added += len(new_variants)
                print(f"  {ch_key}/{sec_key}: +{len(new_variants)} → {len(existing)} total")

    with open(GRIEF_YAML, "w") as f:
        yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False, width=120)

    print(f"\nTotal variants added: {total_added}")
    print(f"Written: {GRIEF_YAML}")


if __name__ == "__main__":
    apply_patches()
