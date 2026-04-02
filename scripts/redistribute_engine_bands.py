#!/usr/bin/env python3
"""
Redistribute BAND values across engine STORY atom roles for reader-experience-first alignment.

Reader experience principle: emotional temperature (BAND) should correlate with
narrative depth (mechanism_depth). Each role needs band diversity so the slot
resolver can always find atoms at the right depth for any arc shape.

Band spread per role (reader-aligned):
  RECOGNITION (depth=1):     [1, 2, 2, 3, 3] — safe recognition at low-to-mid intensity
  MECHANISM_PROOF (depth=2): [2, 3, 3, 4, 4] — understanding needs moderate warmth
  TURNING_POINT (depth=3):   [3, 3, 4, 4, 5] — frame shifts land with emotional heat
  EMBODIMENT (depth=4):      [2, 3, 4, 4, 5] — integration spans cool to breakthrough

Usage:
    python scripts/redistribute_engine_bands.py --dry-run
    python scripts/redistribute_engine_bands.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"

ENGINE_DIRS = {"comparison", "false_alarm", "grief", "overwhelm", "shame", "spiral", "watcher"}

# Reader-aligned band spreads per role (5 variants each)
ROLE_BANDS = {
    "RECOGNITION":     [1, 2, 2, 3, 3],
    "MECHANISM_PROOF": [2, 3, 3, 4, 4],
    "TURNING_POINT":   [3, 3, 4, 4, 5],
    "EMBODIMENT":      [2, 3, 4, 4, 5],
}

HEADER_RE = re.compile(r"^##\s+(\w+)\s+v(\d+)\s*$")


def redistribute_file(path: Path, dry_run: bool = False) -> dict:
    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    stats = {"file": str(path.relative_to(REPO_ROOT)), "fixed": 0, "already_ok": 0}
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        m = HEADER_RE.match(line.strip())
        if not m:
            new_lines.append(line)
            i += 1
            continue

        role = m.group(1).upper()
        vnum = int(m.group(2))
        new_lines.append(line)
        i += 1

        # Opening ---
        if i < len(lines) and lines[i].strip() == "---":
            new_lines.append(lines[i])
            i += 1
        else:
            continue

        # Collect metadata lines until closing ---
        meta_lines = []
        while i < len(lines) and lines[i].strip() != "---":
            meta_lines.append(lines[i])
            i += 1

        if role in ROLE_BANDS and 1 <= vnum <= 5:
            target_band = ROLE_BANDS[role][vnum - 1]
            new_meta = []
            changed = False
            for ml in meta_lines:
                stripped = ml.strip()
                if stripped.startswith("BAND:"):
                    current = stripped.split(":", 1)[1].strip()
                    if current != str(target_band):
                        new_meta.append(f"BAND: {target_band}")
                        changed = True
                    else:
                        new_meta.append(ml)
                else:
                    new_meta.append(ml)
            if changed:
                stats["fixed"] += 1
            else:
                stats["already_ok"] += 1
            new_lines.extend(new_meta)
        else:
            new_lines.extend(meta_lines)
            stats["already_ok"] += 1

        # Closing ---
        if i < len(lines) and lines[i].strip() == "---":
            new_lines.append(lines[i])
            i += 1

    if stats["fixed"] > 0 and not dry_run:
        path.write_text("\n".join(new_lines), encoding="utf-8")
    return stats


def find_engine_files(atoms_root: Path) -> list[Path]:
    files = []
    for persona_dir in sorted(atoms_root.iterdir()):
        if not persona_dir.is_dir():
            continue
        for topic_dir in sorted(persona_dir.iterdir()):
            if not topic_dir.is_dir():
                continue
            for engine_dir in sorted(topic_dir.iterdir()):
                if engine_dir.name in ENGINE_DIRS and engine_dir.is_dir():
                    canon = engine_dir / "CANONICAL.txt"
                    if canon.exists():
                        files.append(canon)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description="Redistribute engine atom BANDs for reader experience")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = find_engine_files(ATOMS_ROOT)
    total_fixed = 0
    total_ok = 0

    for f in files:
        stats = redistribute_file(f, args.dry_run)
        total_fixed += stats["fixed"]
        total_ok += stats["already_ok"]

    prefix = "[DRY-RUN] " if args.dry_run else ""
    print(f"{prefix}Summary:")
    print(f"  Files processed:  {len(files)}")
    print(f"  Bands reassigned: {total_fixed}")
    print(f"  Already correct:  {total_ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
