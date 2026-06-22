#!/usr/bin/env python3
"""Validate pre-purchase nurture PDF slot ratio against nurture_asset_mix.yaml."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    try:
        import yaml
    except ImportError:
        print("PyYAML required")
        return 1

    mix_path = REPO / "config/freebies/nurture_asset_mix.yaml"
    mix = yaml.safe_load(mix_path.read_text(encoding="utf-8"))
    pre = mix.get("pre_purchase") or {}
    target = float(pre.get("pdf_slot_target_ratio", 0.35))
    forbidden = set(pre.get("forbidden_pre_purchase_types") or [])

    slots_path = REPO / "config/freebies/archetype_assignments.yaml"
    slots = yaml.safe_load(slots_path.read_text(encoding="utf-8"))
    slot_map = slots.get("email_slot_by_type") or {}

    for ftype, slot in slot_map.items():
        if ftype in forbidden and slot != "post_purchase":
            print(f"FAIL: forbidden type {ftype} mapped to pre-purchase slot {slot}")
            return 1

    sequence = mix.get("reference_pre_purchase_sequence") or []
    total_slots = len(sequence)
    pdf_slots = sum(1 for row in sequence if row.get("format") == "pdf")
    ratio = pdf_slots / total_slots if total_slots else 0
    if ratio > target + 0.01:
        print(f"FAIL: PDF slot ratio {ratio:.2f} exceeds target {target}")
        return 1
    print(f"OK: pre-purchase PDF slot ratio {ratio:.2f} <= {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
