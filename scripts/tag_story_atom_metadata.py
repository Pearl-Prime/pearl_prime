#!/usr/bin/env python3
"""
Tag STORY atoms with narrative metadata (mechanism_depth, identity_stage, cost_type, cost_intensity).

Deterministic assignment by variant position (v01–v20). Idempotent — skips
atoms that already have metadata. Supports --dry-run and --persona/--topic filters.

Usage:
    python scripts/tag_story_atom_metadata.py --dry-run   # preview
    python scripts/tag_story_atom_metadata.py              # apply
    python scripts/tag_story_atom_metadata.py --persona gen_z_professionals --topic anxiety
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"

# Deterministic metadata mapping: variant number (1-20) -> metadata dict.
# Phase 1 (early/recognition):     v01-v05  depth=1, pre_awareness
# Phase 2 (mid/destabilization):   v06-v10  depth=2, destabilization
# Phase 3 (late/experimentation):  v11-v15  depth=3, experimentation
# Phase 4 (final/identity):        v16-v20  depth=4, self_claim
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

HEADER_RE = re.compile(r"^##\s+STORY\s+v(\d+)\s*$")
METADATA_KEY_RE = re.compile(r"^(MECHANISM_DEPTH|IDENTITY_STAGE|COST_TYPE|COST_INTENSITY)\s*:", re.IGNORECASE)


def _has_metadata(block_lines: list[str]) -> bool:
    """Check if a metadata block already has narrative fields."""
    return any(METADATA_KEY_RE.match(line.strip()) for line in block_lines)


def _format_metadata(meta: dict) -> str:
    """Format metadata dict as CANONICAL.txt metadata lines."""
    return (
        f"MECHANISM_DEPTH: {meta['mechanism_depth']}\n"
        f"IDENTITY_STAGE: {meta['identity_stage']}\n"
        f"COST_TYPE: {meta['cost_type']}\n"
        f"COST_INTENSITY: {meta['cost_intensity']}"
    )


def tag_file(path: Path, dry_run: bool = False) -> dict:
    """Tag a single STORY/CANONICAL.txt file. Returns stats."""
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    stats = {"file": str(path.relative_to(REPO_ROOT)), "tagged": 0, "skipped": 0, "errors": 0}

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = HEADER_RE.match(line.strip())
        if not m:
            new_lines.append(line)
            i += 1
            continue

        # Found ## STORY vNN header
        vnum = int(m.group(1))
        new_lines.append(line)
        i += 1

        # Expect opening ---
        if i < len(lines) and lines[i].strip() == "---":
            new_lines.append(lines[i])
            i += 1
        else:
            stats["errors"] += 1
            continue

        # Collect existing metadata lines until closing ---
        meta_lines = []
        while i < len(lines) and lines[i].strip() != "---":
            meta_lines.append(lines[i])
            i += 1

        if vnum not in VARIANT_METADATA:
            # Variant outside 1-20 range — preserve as-is
            new_lines.extend(meta_lines)
            stats["errors"] += 1
            continue

        if _has_metadata(meta_lines):
            # Already tagged — preserve existing
            new_lines.extend(meta_lines)
            stats["skipped"] += 1
        else:
            # Insert metadata
            meta = VARIANT_METADATA[vnum]
            new_lines.append(_format_metadata(meta))
            stats["tagged"] += 1

        # Closing --- (don't advance past it — main loop will add it)
        # Actually we need to add the closing --- line
        if i < len(lines) and lines[i].strip() == "---":
            new_lines.append(lines[i])
            i += 1

    if stats["tagged"] > 0 and not dry_run:
        path.write_text("\n".join(new_lines), encoding="utf-8")

    return stats


def find_story_files(
    atoms_root: Path,
    persona_filter: str | None = None,
    topic_filter: str | None = None,
) -> list[Path]:
    """Find all STORY/CANONICAL.txt files, optionally filtered."""
    files = sorted(atoms_root.rglob("STORY/CANONICAL.txt"))
    result = []
    for f in files:
        parts = f.relative_to(atoms_root).parts
        if len(parts) < 3:
            continue
        persona, topic = parts[0], parts[1]
        if persona_filter and persona != persona_filter:
            continue
        if topic_filter and topic != topic_filter:
            continue
        result.append(f)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Tag STORY atoms with narrative metadata")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--persona", help="Filter to specific persona")
    parser.add_argument("--topic", help="Filter to specific topic")
    parser.add_argument("--atoms-root", type=Path, default=ATOMS_ROOT)
    args = parser.parse_args()

    files = find_story_files(args.atoms_root, args.persona, args.topic)
    if not files:
        print("No STORY/CANONICAL.txt files found.")
        return 1

    total_tagged = 0
    total_skipped = 0
    total_errors = 0

    for f in files:
        stats = tag_file(f, dry_run=args.dry_run)
        total_tagged += stats["tagged"]
        total_skipped += stats["skipped"]
        total_errors += stats["errors"]
        if stats["tagged"] > 0:
            prefix = "[DRY-RUN] " if args.dry_run else ""
            print(f"  {prefix}{stats['file']}: tagged {stats['tagged']}, skipped {stats['skipped']}")

    print(f"\n{'[DRY-RUN] ' if args.dry_run else ''}Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Atoms tagged:    {total_tagged}")
    print(f"  Atoms skipped:   {total_skipped} (already have metadata)")
    print(f"  Errors:          {total_errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
