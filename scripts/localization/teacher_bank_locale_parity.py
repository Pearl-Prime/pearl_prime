#!/usr/bin/env python3
"""
Teacher Bank Locale Parity Report — teacher_bank_locale_parity.py

Reports localization coverage for SOURCE_OF_TRUTH/teacher_banks.
For each teacher bank, checks which locales have approved_atoms_localized/
and how many atoms are translated per slot type vs the en-US source count.

Outputs:
  - Human-readable parity table (stdout)
  - JSON report (--json-out PATH) for CI consumption
  - Exit code 0 = all checked teachers meet threshold
  - Exit code 1 = one or more teachers below threshold

Usage:
  python scripts/localization/teacher_bank_locale_parity.py
  python scripts/localization/teacher_bank_locale_parity.py --verbose
  python scripts/localization/teacher_bank_locale_parity.py --json-out artifacts/localization/teacher_parity.json
  python scripts/localization/teacher_bank_locale_parity.py --min-coverage 0.5
  python scripts/localization/teacher_bank_locale_parity.py --locales ja-JP ko-KR
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

# Locales from locale_registry.yaml (all non-baseline)
ALL_NON_BASELINE_LOCALES = [
    "ja-JP", "ko-KR",
    "zh-CN", "zh-TW", "zh-HK", "zh-SG",
    "es-US", "es-ES",
    "fr-FR", "de-DE", "it-IT", "hu-HU",
]

CJK6_LOCALES = ["ja-JP", "ko-KR", "zh-CN", "zh-TW", "zh-HK", "zh-SG"]
EU_LOCALES = ["es-US", "es-ES", "fr-FR", "de-DE", "it-IT", "hu-HU"]

TEACHER_BANKS_DIR = REPO_ROOT / "SOURCE_OF_TRUTH" / "teacher_banks"

SLOT_TYPES = [
    "COMPRESSION", "EXERCISE", "HOOK", "INTEGRATION", "PERMISSION",
    "PIVOT", "REFLECTION", "SCENE", "STORY", "TAKEAWAY", "THREAD",
]


def _count_atoms_in_dir(d: Path) -> dict[str, int]:
    """Count .yaml files per slot type subdirectory."""
    counts: dict[str, int] = {}
    if not d.is_dir():
        return counts
    for slot in SLOT_TYPES:
        slot_dir = d / slot
        if slot_dir.is_dir():
            counts[slot] = sum(1 for f in slot_dir.iterdir() if f.suffix == ".yaml")
    return counts


def analyze_teacher(teacher_dir: Path, locales: list[str]) -> dict[str, Any]:
    """Analyze one teacher bank for locale parity."""
    teacher_name = teacher_dir.name
    approved = teacher_dir / "approved_atoms"
    localized_root = teacher_dir / "approved_atoms_localized"

    # English source counts
    en_counts = _count_atoms_in_dir(approved)
    en_total = sum(en_counts.values())

    locale_data: dict[str, Any] = {}
    for locale in locales:
        locale_dir = localized_root / locale
        if not locale_dir.is_dir():
            locale_data[locale] = {
                "status": "missing",
                "total": 0,
                "by_slot": {},
                "pct": 0.0,
                "missing_slots": [s for s in SLOT_TYPES if en_counts.get(s, 0) > 0],
            }
            continue

        loc_counts = _count_atoms_in_dir(locale_dir)
        loc_total = sum(loc_counts.values())
        pct = (loc_total / en_total) if en_total > 0 else 0.0

        # Check slot-level gaps
        missing_slots = []
        for slot in SLOT_TYPES:
            en_n = en_counts.get(slot, 0)
            loc_n = loc_counts.get(slot, 0)
            if en_n > 0 and loc_n == 0:
                missing_slots.append(slot)

        status = "ok" if pct >= 1.0 else ("partial" if loc_total > 0 else "missing")
        locale_data[locale] = {
            "status": status,
            "total": loc_total,
            "by_slot": loc_counts,
            "pct": round(pct, 3),
            "missing_slots": missing_slots,
        }

    return {
        "teacher": teacher_name,
        "en_total": en_total,
        "en_by_slot": en_counts,
        "locales": locale_data,
    }


def run_parity_report(
    locales: list[str],
    min_coverage: float,
    verbose: bool,
    json_out: Path | None,
) -> int:
    """Run the parity report and return exit code."""
    if not TEACHER_BANKS_DIR.is_dir():
        print(f"ERROR: teacher banks dir not found: {TEACHER_BANKS_DIR}")
        return 2

    teachers = sorted(
        d for d in TEACHER_BANKS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )

    results: list[dict[str, Any]] = []
    for td in teachers:
        results.append(analyze_teacher(td, locales))

    # Print table header
    loc_cols = "  ".join(f"{l:>6}" for l in locales)
    print(f"\n{'Teacher':<18} {'en-US':>6}  {loc_cols}")
    print("-" * (26 + 8 * len(locales)))

    below_threshold: list[str] = []

    for r in results:
        teacher = r["teacher"]
        en_total = r["en_total"]
        cols: list[str] = []
        for loc in locales:
            ld = r["locales"][loc]
            if ld["status"] == "missing":
                cols.append(f"{'--':>6}")
            else:
                pct_str = f"{ld['pct']:.0%}"
                cols.append(f"{pct_str:>6}")
            if ld["pct"] < min_coverage and en_total > 0:
                below_threshold.append(f"{teacher}/{loc}")
        col_str = "  ".join(cols)
        print(f"{teacher:<18} {en_total:>6}  {col_str}")

        if verbose:
            for loc in locales:
                ld = r["locales"][loc]
                if ld["missing_slots"]:
                    print(f"  {loc}: missing slots: {', '.join(ld['missing_slots'])}")

    print("-" * (26 + 8 * len(locales)))

    # Summary
    total_teachers = len(results)
    fully_localized = 0
    partially_localized = 0
    not_localized = 0

    for r in results:
        has_any = False
        has_all = True
        for loc in locales:
            ld = r["locales"][loc]
            if ld["total"] > 0:
                has_any = True
            if ld["status"] != "ok":
                has_all = False
        if has_all and has_any:
            fully_localized += 1
        elif has_any:
            partially_localized += 1
        else:
            not_localized += 1

    print(f"\nTeachers: {total_teachers} total  |  "
          f"{fully_localized} fully localized  |  "
          f"{partially_localized} partial  |  "
          f"{not_localized} none")

    # CJK vs EU breakdown
    cjk_atoms = 0
    eu_atoms = 0
    for r in results:
        for loc in locales:
            ld = r["locales"][loc]
            if loc in CJK6_LOCALES:
                cjk_atoms += ld["total"]
            elif loc in EU_LOCALES:
                eu_atoms += ld["total"]

    print(f"CJK6 translated atoms: {cjk_atoms}  |  EU translated atoms: {eu_atoms}")

    # JSON output
    if json_out is not None:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "locales_checked": locales,
            "min_coverage_threshold": min_coverage,
            "total_teachers": total_teachers,
            "fully_localized": fully_localized,
            "partially_localized": partially_localized,
            "not_localized": not_localized,
            "gate_pass": len(below_threshold) == 0,
            "teachers": {r["teacher"]: r for r in results},
        }
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report: {json_out}")

    if below_threshold:
        print(f"\nBELOW {min_coverage:.0%} threshold: {len(below_threshold)} teacher/locale pairs")
        if verbose:
            for item in below_threshold[:20]:
                print(f"  - {item}")
        return 1

    print(f"\nGATE PASS — all teacher/locale pairs at or above {min_coverage:.0%}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Teacher bank locale parity report")
    ap.add_argument("--locales", nargs="+", default=None,
                    help="Locale codes to check (default: all 12 non-baseline)")
    ap.add_argument("--cjk-only", action="store_true",
                    help="Only check CJK6 locales")
    ap.add_argument("--eu-only", action="store_true",
                    help="Only check European locales")
    ap.add_argument("--min-coverage", type=float, default=0.0,
                    help="Minimum coverage ratio to pass (0.0-1.0, default 0.0 = advisory)")
    ap.add_argument("--verbose", "-v", action="store_true")
    ap.add_argument("--json-out", type=Path, default=None)
    ap.add_argument("--all-locales", action="store_true",
                    help="Alias for checking all non-baseline locales")
    args = ap.parse_args()

    if args.locales:
        locales = args.locales
    elif args.cjk_only:
        locales = CJK6_LOCALES
    elif args.eu_only:
        locales = EU_LOCALES
    else:
        locales = ALL_NON_BASELINE_LOCALES

    return run_parity_report(
        locales=locales,
        min_coverage=args.min_coverage,
        verbose=args.verbose,
        json_out=args.json_out,
    )


if __name__ == "__main__":
    sys.exit(main())
