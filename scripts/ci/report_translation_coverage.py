#!/usr/bin/env python3
"""
Per-locale (persona, topic, engine) coverage.
Authority: PEARL_PRIME_100_PERCENT_DEV_PLAN §5.

Also reports bestseller atom coverage for CJK6: English sources under
atoms/{persona}/{topic}/{PIVOT|TAKEAWAY|THREAD|PERMISSION|STORY}/CANONICAL.txt
vs translations at atoms/.../{slot}/locales/{locale}/CANONICAL.txt.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CJK6_LOCALES = ("ja-JP", "ko-KR", "zh-CN", "zh-HK", "zh-SG", "zh-TW")
BESTSELLER_SLOTS = ("PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "STORY")


def _count_canonical_under(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for _ in root.rglob("CANONICAL.txt"))


def _bestseller_english_sources(atoms_root: Path) -> list[Path]:
    """CANONICAL.txt under slot dirs only; excludes locales/ outputs."""
    out: list[Path] = []
    for slot in BESTSELLER_SLOTS:
        for path in atoms_root.rglob(f"{slot}/CANONICAL.txt"):
            if "locales" in path.parts:
                continue
            rel = path.relative_to(atoms_root)
            if len(rel.parts) >= 4 and rel.parts[-1] == "CANONICAL.txt":
                out.append(path)
    return sorted(out)


def _bestseller_translated_count(
    sources: list[Path], atoms_root: Path, locale: str
) -> int:
    n = 0
    for src in sources:
        rel = src.relative_to(atoms_root)
        persona, topic, slot = rel.parts[0], rel.parts[1], rel.parts[2]
        tpath = atoms_root / persona / topic / slot / "locales" / locale / "CANONICAL.txt"
        if tpath.is_file():
            n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description="Translation coverage per locale")
    ap.add_argument("--json", action="store_true")
    ap.add_argument(
        "--locales",
        type=str,
        default=None,
        help="Comma-separated locales (default: en-US)",
    )
    args = ap.parse_args()

    locales = (args.locales or "en-US").split(",")
    report: dict = {"locales": locales, "by_locale": {}}

    atoms_en = REPO_ROOT / "atoms"
    bestseller_sources = _bestseller_english_sources(atoms_en)
    report["bestseller"] = {
        "slots": list(BESTSELLER_SLOTS),
        "cjk_locales": list(CJK6_LOCALES),
        "english_source_files": len(bestseller_sources),
        "by_cjk_locale": {},
    }
    for loc in CJK6_LOCALES:
        present = _bestseller_translated_count(bestseller_sources, atoms_en, loc)
        expected = len(bestseller_sources)
        report["bestseller"]["by_cjk_locale"][loc] = {
            "translated_files": present,
            "expected_files": expected,
            "coverage_ratio": (present / expected) if expected else 0.0,
        }

    for loc in locales:
        atoms_root = REPO_ROOT / "atoms" if loc == "en-US" else REPO_ROOT / "atoms" / loc
        if not atoms_root.exists():
            report["by_locale"][loc] = {
                "persona_topic_count": 0,
                "has_atoms": False,
            }
            continue
        count = _count_canonical_under(atoms_root)
        report["by_locale"][loc] = {
            "persona_topic_count": count,
            "has_atoms": count > 0,
        }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0
    for loc, data in report["by_locale"].items():
        print(f"  {loc}: {data['persona_topic_count']} CANONICAL.txt")
    bs = report["bestseller"]
    print(
        f"\nBestseller (5 slots, CJK6): {bs['english_source_files']} English source files"
    )
    for loc, row in bs["by_cjk_locale"].items():
        print(
            f"  {loc}: {row['translated_files']}/{row['expected_files']} "
            f"({row['coverage_ratio']:.1%})"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
