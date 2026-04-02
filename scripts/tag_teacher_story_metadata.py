#!/usr/bin/env python3
"""
Tag teacher bank STORY atoms (YAML format) with narrative metadata.

Teacher bank STORY atoms are individual YAML files (not CANONICAL.txt).
Uses the same deterministic assignment by atom number suffix (001-020).

Usage:
    python scripts/tag_teacher_story_metadata.py --dry-run
    python scripts/tag_teacher_story_metadata.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("pyyaml required: pip install pyyaml")
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
TEACHER_BANKS = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"

# Same mapping as tag_story_atom_metadata.py
VARIANT_METADATA = {
    1:  {"mechanism_depth": 1, "identity_stage": "pre_awareness",   "cost_type": "social",      "cost_intensity": 1},
    2:  {"mechanism_depth": 1, "identity_stage": "pre_awareness",   "cost_type": "social",      "cost_intensity": 2},
    3:  {"mechanism_depth": 1, "identity_stage": "pre_awareness",   "cost_type": "social",      "cost_intensity": 2},
    4:  {"mechanism_depth": 1, "identity_stage": "pre_awareness",   "cost_type": "social",      "cost_intensity": 2},
    5:  {"mechanism_depth": 1, "identity_stage": "pre_awareness",   "cost_type": "social",      "cost_intensity": 3},
    6:  {"mechanism_depth": 2, "identity_stage": "destabilization", "cost_type": "internal",    "cost_intensity": 2},
    7:  {"mechanism_depth": 2, "identity_stage": "destabilization", "cost_type": "internal",    "cost_intensity": 3},
    8:  {"mechanism_depth": 2, "identity_stage": "destabilization", "cost_type": "internal",    "cost_intensity": 3},
    9:  {"mechanism_depth": 2, "identity_stage": "destabilization", "cost_type": "internal",    "cost_intensity": 3},
    10: {"mechanism_depth": 2, "identity_stage": "destabilization", "cost_type": "internal",    "cost_intensity": 3},
    11: {"mechanism_depth": 3, "identity_stage": "experimentation", "cost_type": "opportunity", "cost_intensity": 3},
    12: {"mechanism_depth": 3, "identity_stage": "experimentation", "cost_type": "opportunity", "cost_intensity": 3},
    13: {"mechanism_depth": 3, "identity_stage": "experimentation", "cost_type": "opportunity", "cost_intensity": 4},
    14: {"mechanism_depth": 3, "identity_stage": "experimentation", "cost_type": "opportunity", "cost_intensity": 4},
    15: {"mechanism_depth": 3, "identity_stage": "experimentation", "cost_type": "opportunity", "cost_intensity": 4},
    16: {"mechanism_depth": 4, "identity_stage": "self_claim",      "cost_type": "identity",    "cost_intensity": 4},
    17: {"mechanism_depth": 4, "identity_stage": "self_claim",      "cost_type": "identity",    "cost_intensity": 4},
    18: {"mechanism_depth": 4, "identity_stage": "self_claim",      "cost_type": "identity",    "cost_intensity": 4},
    19: {"mechanism_depth": 4, "identity_stage": "self_claim",      "cost_type": "identity",    "cost_intensity": 5},
    20: {"mechanism_depth": 4, "identity_stage": "self_claim",      "cost_type": "identity",    "cost_intensity": 5},
}

NUM_RE = re.compile(r"_(\d{3})(?:_[a-z]{2}-[A-Z]{2})?\.yaml$")


def tag_yaml_file(path: Path, dry_run: bool = False) -> str | None:
    """Tag a single teacher STORY YAML. Returns action taken or None."""
    m = NUM_RE.search(path.name)
    if not m:
        return None
    vnum = int(m.group(1))
    if vnum not in VARIANT_METADATA:
        # Wrap around for atoms > 20
        vnum = ((vnum - 1) % 20) + 1

    meta = VARIANT_METADATA[vnum]
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}

    if "mechanism_depth" in data:
        return "skipped"

    data["mechanism_depth"] = meta["mechanism_depth"]
    data["identity_stage"] = meta["identity_stage"]
    data["cost_type"] = meta["cost_type"]
    data["cost_intensity"] = meta["cost_intensity"]

    if not dry_run:
        path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return "tagged"


def main() -> int:
    parser = argparse.ArgumentParser(description="Tag teacher bank STORY atoms with narrative metadata")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--teacher", help="Filter to specific teacher")
    args = parser.parse_args()

    if not TEACHER_BANKS.exists():
        print(f"Teacher banks not found at {TEACHER_BANKS}")
        return 1

    files = sorted(TEACHER_BANKS.rglob("STORY/*.yaml"))
    if args.teacher:
        files = [f for f in files if args.teacher in str(f)]

    tagged = skipped = errors = 0
    for f in files:
        result = tag_yaml_file(f, args.dry_run)
        if result == "tagged":
            tagged += 1
        elif result == "skipped":
            skipped += 1
        elif result is None:
            errors += 1

    prefix = "[DRY-RUN] " if args.dry_run else ""
    print(f"{prefix}Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Atoms tagged:    {tagged}")
    print(f"  Atoms skipped:   {skipped}")
    print(f"  Errors:          {errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
