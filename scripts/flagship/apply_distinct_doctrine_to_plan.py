#!/usr/bin/env python3
"""Apply 12-distinct doctrine sequence to the flagship twelve-shape plan (final batch only).

Updates doctrine_id per chapter from gen_z_professionals_anxiety_distinct_doctrine_sequence.yaml.
ch1 v03 is never modified — parity golden lock.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLAN_PATH = (
    REPO_ROOT
    / "config/source_of_truth/twelve_shape_chapter_plans/gen_z_professionals_anxiety.yaml"
)
SEQUENCE_PATH = (
    REPO_ROOT
    / "config/source_of_truth/twelve_shape_chapter_plans"
    / "gen_z_professionals_anxiety_distinct_doctrine_sequence.yaml"
)
CH1_LOCKED = "COMPOSITE_DOCTRINE v03"


def _load_sequence(path: Path) -> dict[int, str]:
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    raw = data.get("doctrine_by_chapter") or {}
    out: dict[int, str] = {}
    for k, v in raw.items():
        out[int(k)] = str(v).strip()
    if out.get(1) != CH1_LOCKED:
        raise SystemExit(f"sequence ch1 must stay {CH1_LOCKED!r}, got {out.get(1)!r}")
    if len(set(out.values())) != 12:
        raise SystemExit(f"expected 12 distinct doctrine ids, got {len(set(out.values()))}")
    return out


def _apply(plan_text: str, sequence: dict[int, str]) -> str:
    lines = plan_text.splitlines()
    out: list[str] = []
    ch_num = 0
    ch1_before = ""
    for line in lines:
        m = re.match(r"^\s*-\s+chapter:\s+(\d+)\s*$", line)
        if m:
            ch_num = int(m.group(1))
        if ch_num == 1 and line.strip().startswith("doctrine_id:"):
            ch1_before = line
        if ch_num and line.strip().startswith("doctrine_id:") and ch_num in sequence:
            indent = line[: len(line) - len(line.lstrip())]
            if ch_num == 1:
                out.append(line)
                continue
            out.append(f'{indent}doctrine_id: "{sequence[ch_num]}"')
            continue
        out.append(line)
    if ch1_before and CH1_LOCKED not in ch1_before:
        raise SystemExit("refusing to apply: ch1 doctrine_id drift detected in plan")
    return "\n".join(out) + ("\n" if plan_text.endswith("\n") else "")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Print diff summary only")
    parser.add_argument("--plan", type=Path, default=PLAN_PATH)
    parser.add_argument("--sequence", type=Path, default=SEQUENCE_PATH)
    args = parser.parse_args()

    sequence = _load_sequence(args.sequence)
    plan_text = args.plan.read_text(encoding="utf-8")
    updated = _apply(plan_text, sequence)

    if updated == plan_text:
        print("no doctrine_id changes needed")
        return 0

    if args.dry_run:
        for ch in range(2, 13):
            print(f"ch{ch} -> {sequence[ch]}")
        return 0

    args.plan.write_text(updated, encoding="utf-8")
    print(f"applied 12-distinct doctrine sequence to {args.plan.name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
