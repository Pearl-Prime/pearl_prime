#!/usr/bin/env python3
"""
Fix engine atom metadata: upgrade EMBODIMENT role atoms to depth=4 and self_claim.

Engine CANONICAL.txt files have four story roles:
  RECOGNITION (v01-v05) → depth should be 1, pre_awareness
  MECHANISM_PROOF (v01-v05) → depth should be 2, destabilization
  TURNING_POINT (v01-v05) → depth should be 3, experimentation
  EMBODIMENT (v01-v05) → depth should be 4, self_claim  ← currently stuck at 3

This script:
1. Finds all engine CANONICAL.txt files
2. For each EMBODIMENT block, upgrades mechanism_depth to 4 and identity_stage to self_claim
3. Also ensures RECOGNITION=1/pre_awareness, MECHANISM_PROOF=2/destabilization,
   TURNING_POINT=3/experimentation for consistency

Usage:
    python scripts/fix_engine_atom_depth.py --dry-run
    python scripts/fix_engine_atom_depth.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ATOMS_ROOT = REPO_ROOT / "atoms"

ENGINE_DIRS = {"comparison", "false_alarm", "grief", "overwhelm", "shame", "spiral", "watcher"}

# Correct metadata per role
ROLE_METADATA = {
    "RECOGNITION":     {"mechanism_depth": 1, "identity_stage": "pre_awareness"},
    "MECHANISM_PROOF": {"mechanism_depth": 2, "identity_stage": "destabilization"},
    "TURNING_POINT":   {"mechanism_depth": 3, "identity_stage": "experimentation"},
    "EMBODIMENT":      {"mechanism_depth": 4, "identity_stage": "self_claim"},
}

HEADER_RE = re.compile(r"^##\s+(\w+)\s+v(\d+)\s*$")


def fix_file(path: Path, dry_run: bool = False) -> dict:
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
        new_lines.append(line)
        i += 1

        # Expect opening ---
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

        if role in ROLE_METADATA:
            target = ROLE_METADATA[role]
            new_meta = []
            changed = False
            for ml in meta_lines:
                stripped = ml.strip()
                if stripped.startswith("MECHANISM_DEPTH:"):
                    current = stripped.split(":", 1)[1].strip()
                    if current != str(target["mechanism_depth"]):
                        new_meta.append(f"MECHANISM_DEPTH: {target['mechanism_depth']}")
                        changed = True
                    else:
                        new_meta.append(ml)
                elif stripped.startswith("IDENTITY_STAGE:"):
                    current = stripped.split(":", 1)[1].strip()
                    if current != target["identity_stage"]:
                        new_meta.append(f"IDENTITY_STAGE: {target['identity_stage']}")
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
    parser = argparse.ArgumentParser(description="Fix engine atom depth/stage metadata")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = find_engine_files(ATOMS_ROOT)
    if not files:
        print("No engine CANONICAL.txt files found.")
        return 1

    total_fixed = 0
    total_ok = 0
    for f in files:
        stats = fix_file(f, args.dry_run)
        total_fixed += stats["fixed"]
        total_ok += stats["already_ok"]
        if stats["fixed"] > 0:
            prefix = "[DRY-RUN] " if args.dry_run else ""
            print(f"  {prefix}{stats['file']}: fixed {stats['fixed']} atoms")

    prefix = "[DRY-RUN] " if args.dry_run else ""
    print(f"\n{prefix}Summary:")
    print(f"  Files processed: {len(files)}")
    print(f"  Atoms fixed:     {total_fixed}")
    print(f"  Already correct: {total_ok}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
