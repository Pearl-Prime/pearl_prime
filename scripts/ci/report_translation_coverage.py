#!/usr/bin/env python3
"""
Per-locale (persona, topic, engine) coverage.
Authority: PEARL_PRIME_100_PERCENT_DEV_PLAN §5.

Also reports atom coverage for CJK6: English sources under
atoms/{persona}/{topic}/{SLOT_OR_ENGINE}/CANONICAL.txt
(slots: PIVOT, TAKEAWAY, THREAD, PERMISSION, STORY;
 engines: comparison, false_alarm, grief, overwhelm, shame, spiral, watcher)
vs translations at atoms/.../{type}/locales/{locale}/CANONICAL.txt.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

CJK6_LOCALES = ("ja-JP", "ko-KR", "zh-CN", "zh-HK", "zh-SG", "zh-TW")
BESTSELLER_SLOTS = ("PIVOT", "TAKEAWAY", "THREAD", "PERMISSION", "STORY")
ENGINE_DIRS = ("comparison", "false_alarm", "grief", "overwhelm", "shame", "spiral", "watcher")
ALL_ATOM_TYPES = BESTSELLER_SLOTS + ENGINE_DIRS


def _count_canonical_under(root: Path) -> int:
    if not root.exists():
        return 0
    return sum(1 for _ in root.rglob("CANONICAL.txt"))


def _bestseller_english_sources(atoms_root: Path) -> list[Path]:
    """CANONICAL.txt under slot + engine dirs; excludes locales/ outputs."""
    out: list[Path] = []
    for atom_type in ALL_ATOM_TYPES:
        for path in atoms_root.rglob(f"{atom_type}/CANONICAL.txt"):
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
        "--output",
        type=Path,
        default=None,
        help="Write the same JSON as --json to this path (implies --json)",
    )
    ap.add_argument(
        "--locales",
        type=str,
        default=None,
        help="Comma-separated locales (default: en-US)",
    )
    args = ap.parse_args()
    emit_json = bool(args.json)

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

    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if emit_json:
        print(json.dumps(report, indent=2))
        return 0

    for loc, data in report["by_locale"].items():
        print(f"  {loc}: {data['persona_topic_count']} CANONICAL.txt")
    bs = report["bestseller"]
    print(
        f"\nAll atoms ({len(ALL_ATOM_TYPES)} types, CJK6): {bs['english_source_files']} English source files"
    )
    filter_locs: set[str] | None = None
    if args.locales:
        filter_locs = {x.strip() for x in args.locales.split(",") if x.strip()}
    for loc, row in bs["by_cjk_locale"].items():
        if filter_locs is not None and loc not in filter_locs:
            continue
        rem = int(row["expected_files"]) - int(row["translated_files"])
        print(
            f"  {loc}: {row['translated_files']}/{row['expected_files']} "
            f"({row['coverage_ratio']:.1%})  remaining={rem}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
