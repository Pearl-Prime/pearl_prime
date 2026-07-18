#!/usr/bin/env python3
"""Image bank topic coverage helpers.

- Default **JSON** (legacy): Stillness canonical audit — topics with **zero** of 56 slots filled.
- **Slugs mode** (``--format slugs``): topics with fewer than ``--min-panels`` raw PNG files (space-separated, trailing newline only if non-empty).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from scripts.manga.stillness_press_image_bank import TOPICS_15, run_audit  # noqa: E402


def _count_raw_pngs(topic_dir: Path) -> int:
    if not topic_dir.is_dir():
        return 0
    return sum(1 for p in topic_dir.iterdir() if p.suffix.lower() == ".png" and p.is_file())


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brand", default="stillness_press")
    ap.add_argument(
        "--bank",
        type=Path,
        default=None,
        help="Image bank root (default image_bank/<brand>)",
    )
    ap.add_argument(
        "--format",
        choices=("json", "slugs"),
        default="json",
        help="json = zero canonical slots; slugs = raw PNG count vs --min-panels",
    )
    ap.add_argument(
        "--min-panels",
        type=int,
        default=60,
        help="Used with --format slugs: list topics with fewer PNG files",
    )
    args = ap.parse_args()
    bank = (args.bank or (REPO_ROOT / "image_bank" / args.brand)).resolve()

    if args.format == "json":
        data = run_audit(bank)
        per = data["per_topic"]  # type: ignore[index]
        zeros = [t for t in TOPICS_15 if int(per[t]["found"]) == 0]  # type: ignore[index]
        print(json.dumps({"zero_coverage_topics": zeros, "bank": str(bank)}, indent=2))
        return 0

    low: list[str] = []
    if bank.is_dir():
        for topic_dir in sorted(bank.iterdir()):
            if not topic_dir.is_dir():
                continue
            if _count_raw_pngs(topic_dir) < args.min_panels:
                low.append(topic_dir.name)
    sys.stdout.write(" ".join(low))
    if low:
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
