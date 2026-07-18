#!/usr/bin/env python3
"""
Locale Structural Gate — locale_structural_gate.py

Fast, LLM-free locale coverage check. Runs in GitHub Actions (PR gate) and
locally via Phoenix Command UI. Checks atom file coverage per locale — does
not evaluate translation quality (that's validate_translations.py + eval/fix loop).

Checks:
  1. Atom files exist for each locale / topic combination
  2. Atom translation_status is not 'stub' (i.e. actually translated)
  3. Atom counts match the en-US source count
  4. Word counts are within the 40-80 word contract range

Outputs:
  - Human-readable table (stdout)
  - JSON report (--json-out PATH) — consumed by PhoenixControl LocaleStatusView
  - Exit code 0 = all locales at or above threshold
  - Exit code 1 = one or more locales below threshold (CI fails)
  - Exit code 2 = no translated files found at all

Usage:
  # Quick status table
  python scripts/localization/locale_structural_gate.py

  # Full report with per-locale detail
  python scripts/localization/locale_structural_gate.py --verbose

  # JSON output for Phoenix Command UI
  python scripts/localization/locale_structural_gate.py --json-out artifacts/localization/locale_status.json

  # Only fail if below a minimum % threshold (default 0 — advisory mode)
  python scripts/localization/locale_structural_gate.py --min-coverage 0.8

  # Scope to specific locales
  python scripts/localization/locale_structural_gate.py --locales es-US es-ES de-DE it-IT
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

# ─── CONSTANTS ────────────────────────────────────────────────────────────────

PEARL_NEWS_TOPICS = [
    "climate", "economy_work", "education", "inequality",
    "mental_health", "partnerships", "peace_conflict",
]

# Canonical 14-locale set per config/localization/locale_registry.yaml locale_groups.all_locales
# (en-US is baseline; 13 non-en-US target locales here). pt-PT / ru-RU are not in the canon.
TARGET_LOCALES = [
    # CJK (Route 1)
    "ja-JP", "zh-CN", "zh-TW", "zh-HK", "zh-SG", "ko-KR",
    # European + Latin American (Route 2)
    "es-US", "es-ES", "fr-FR", "de-DE", "it-IT", "hu-HU",
    # Portuguese
    "pt-BR",
]

ATOMS_DIR = REPO_ROOT / "pearl_news" / "atoms" / "teacher_quotes_practices"
SOURCE_DIR = ATOMS_DIR
LOCALES_DIR = ATOMS_DIR / "locales"

MIN_ATOM_WORDS = 40
MAX_ATOM_WORDS = 80


# ─── HELPERS ──────────────────────────────────────────────────────────────────

def _load_yaml(path: Path) -> dict:
    if not path.exists() or yaml is None:
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _count_words(text: str) -> int:
    return len(str(text).split())


def _atom_texts_from_teacher(teacher_data: dict) -> list[str]:
    """Extract atom text strings from a teacher dict."""
    texts: list[str] = []
    atoms = teacher_data.get("atoms", [])
    if isinstance(atoms, list):
        for atom in atoms:
            if isinstance(atom, dict):
                texts.append(str(atom.get("text", atom.get("content", ""))))
            elif isinstance(atom, str):
                texts.append(atom)
    elif isinstance(atoms, dict):
        for v in atoms.values():
            if isinstance(v, str):
                texts.append(v)
            elif isinstance(v, dict):
                texts.append(str(v.get("text", v.get("content", ""))))
    return [t for t in texts if t.strip()]


# ─── SOURCE INVENTORY ─────────────────────────────────────────────────────────

def build_source_inventory() -> dict[str, dict[str, int]]:
    """
    Returns {topic: {teacher_id: atom_count}} for all en-US source files.
    """
    inventory: dict[str, dict[str, int]] = {}
    for topic in PEARL_NEWS_TOPICS:
        path = SOURCE_DIR / f"topic_{topic}.yaml"
        data = _load_yaml(path)
        teachers = data.get("teachers", {})
        if not isinstance(teachers, dict):
            inventory[topic] = {}
            continue
        inventory[topic] = {
            tid: len(_atom_texts_from_teacher(tdata))
            for tid, tdata in teachers.items()
            if isinstance(tdata, dict)
        }
    return inventory


# ─── LOCALE CHECKER ───────────────────────────────────────────────────────────

def check_locale(
    locale: str,
    source_inventory: dict[str, dict[str, int]],
    verbose: bool = False,
) -> dict[str, Any]:
    """
    Returns a per-locale status dict:
      {
        locale, status,         # "ok" | "partial" | "missing"
        pct_coverage,           # 0.0–1.0 of expected atoms translated
        topics_ok, topics_total,
        atoms_translated, atoms_expected,
        word_range_violations,  # count of atoms outside 40-80 words
        stub_count,             # atoms with translation_status == 'stub'
        issues: [str],          # list of human-readable issue strings
        per_topic: {topic: {...}}
      }
    """
    locale_dir = LOCALES_DIR / locale
    issues: list[str] = []
    per_topic: dict[str, Any] = {}

    total_atoms_expected = 0
    total_atoms_translated = 0
    total_word_violations = 0
    total_stubs = 0
    topics_ok = 0

    for topic in PEARL_NEWS_TOPICS:
        src_teachers = source_inventory.get(topic, {})
        src_atom_count = sum(src_teachers.values())
        total_atoms_expected += src_atom_count

        translated_path = locale_dir / f"topic_{topic}.yaml"
        if not translated_path.exists():
            per_topic[topic] = {
                "status": "missing",
                "atoms_translated": 0,
                "atoms_expected": src_atom_count,
                "pct": 0.0,
            }
            issues.append(f"{topic}: file missing ({locale_dir.name}/topic_{topic}.yaml)")
            continue

        data = _load_yaml(translated_path)
        teachers = data.get("teachers", {})
        if not isinstance(teachers, dict):
            per_topic[topic] = {"status": "invalid", "atoms_translated": 0, "atoms_expected": src_atom_count, "pct": 0.0}
            issues.append(f"{topic}: invalid YAML structure")
            continue

        topic_atoms_translated = 0
        topic_stubs = 0
        topic_word_violations = 0
        topic_issues: list[str] = []

        for teacher_id, teacher_data in teachers.items():
            if not isinstance(teacher_data, dict):
                continue
            atoms_raw = teacher_data.get("atoms", [])
            if isinstance(atoms_raw, list):
                atom_entries = atoms_raw
            elif isinstance(atoms_raw, dict):
                atom_entries = list(atoms_raw.values())
            else:
                atom_entries = []

            for atom in atom_entries:
                if isinstance(atom, dict):
                    status_val = atom.get("translation_status", atom.get("status", "translated"))
                    text = str(atom.get("text", atom.get("content", "")))
                else:
                    status_val = "translated"
                    text = str(atom)

                if str(status_val).lower() == "stub":
                    topic_stubs += 1
                    continue

                if text.strip():
                    topic_atoms_translated += 1
                    wc = _count_words(text)
                    if wc < MIN_ATOM_WORDS or wc > MAX_ATOM_WORDS:
                        topic_word_violations += 1
                        if verbose:
                            topic_issues.append(
                                f"  {teacher_id}: atom word count {wc} (expected {MIN_ATOM_WORDS}–{MAX_ATOM_WORDS})"
                            )

        total_atoms_translated += topic_atoms_translated
        total_stubs += topic_stubs
        total_word_violations += topic_word_violations

        topic_pct = (topic_atoms_translated / src_atom_count) if src_atom_count > 0 else 1.0
        topic_status = "ok" if topic_pct >= 1.0 and topic_stubs == 0 else (
            "partial" if topic_pct > 0 else "missing"
        )
        if topic_status == "ok":
            topics_ok += 1

        per_topic[topic] = {
            "status": topic_status,
            "atoms_translated": topic_atoms_translated,
            "atoms_expected": src_atom_count,
            "pct": round(topic_pct, 3),
            "stubs": topic_stubs,
            "word_violations": topic_word_violations,
        }
        if topic_stubs > 0:
            issues.append(f"{topic}: {topic_stubs} atom(s) still 'stub' status")
        if topic_word_violations > 0:
            issues.append(f"{topic}: {topic_word_violations} atom(s) outside {MIN_ATOM_WORDS}–{MAX_ATOM_WORDS} words")
        issues.extend(topic_issues)

    pct_coverage = (total_atoms_translated / total_atoms_expected) if total_atoms_expected > 0 else 0.0

    if pct_coverage >= 1.0 and total_stubs == 0:
        status = "ok"
    elif total_atoms_translated == 0:
        status = "missing"
    else:
        status = "partial"

    return {
        "locale": locale,
        "status": status,
        "pct_coverage": round(pct_coverage, 3),
        "topics_ok": topics_ok,
        "topics_total": len(PEARL_NEWS_TOPICS),
        "atoms_translated": total_atoms_translated,
        "atoms_expected": total_atoms_expected,
        "word_range_violations": total_word_violations,
        "stub_count": total_stubs,
        "issues": issues,
        "per_topic": per_topic,
    }


# ─── GATE RUNNER ─────────────────────────────────────────────────────────────

def run_gate(
    locales: list[str],
    min_coverage: float,
    verbose: bool,
    json_out: Path | None,
) -> int:
    """
    Run the structural gate for all requested locales.
    Returns exit code: 0 = pass, 1 = below threshold, 2 = no data at all.
    """
    source_inventory = build_source_inventory()
    total_source = sum(sum(t.values()) for t in source_inventory.values())

    if total_source == 0:
        print("ERROR: No en-US source atoms found. Check pearl_news/atoms/teacher_quotes_practices/")
        return 2

    results: list[dict] = []
    for locale in locales:
        result = check_locale(locale, source_inventory, verbose=verbose)
        results.append(result)

    # ── Print table ──────────────────────────────────────────────────────────
    # Header
    col_w = 10
    print(f"\n{'Locale':<10} {'Status':<10} {'Coverage':>10} {'Topics':>8} {'Atoms':>10} {'Issues':>7}")
    print("─" * 60)
    below_threshold: list[str] = []

    for r in results:
        locale = r["locale"]
        status = r["status"]
        pct = r["pct_coverage"]
        topics = f"{r['topics_ok']}/{r['topics_total']}"
        atoms = f"{r['atoms_translated']}/{r['atoms_expected']}"
        n_issues = len(r["issues"])

        # Emoji/indicator
        ind = "✓" if status == "ok" else ("~" if status == "partial" else "✗")

        print(f"{locale:<10} {ind} {status:<8} {pct:>9.0%} {topics:>8} {atoms:>10} {n_issues:>6} issues")

        if verbose and r["issues"]:
            for issue in r["issues"][:10]:
                print(f"           • {issue}")

        if pct < min_coverage:
            below_threshold.append(f"{locale} ({pct:.0%})")

    print("─" * 60)

    # Summary line
    ok_count = sum(1 for r in results if r["status"] == "ok")
    partial_count = sum(1 for r in results if r["status"] == "partial")
    missing_count = sum(1 for r in results if r["status"] == "missing")
    total_atoms_done = sum(r["atoms_translated"] for r in results)
    total_atoms_needed = sum(r["atoms_expected"] for r in results)
    overall_pct = (total_atoms_done / total_atoms_needed) if total_atoms_needed > 0 else 0.0

    print(f"\nSummary: {ok_count} OK  {partial_count} partial  {missing_count} missing  |  "
          f"Overall coverage: {overall_pct:.1%}  ({total_atoms_done}/{total_atoms_needed} atoms)")

    if below_threshold:
        print(f"\nBELOW {min_coverage:.0%} threshold: {', '.join(below_threshold)}")

    # ── JSON output ───────────────────────────────────────────────────────────
    if json_out is not None:
        json_out.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "source_atoms_total": total_source,
            "locales_checked": len(locales),
            "locales_ok": ok_count,
            "locales_partial": partial_count,
            "locales_missing": missing_count,
            "overall_pct_coverage": round(overall_pct, 4),
            "min_coverage_threshold": min_coverage,
            "gate_pass": len(below_threshold) == 0,
            "locales": {r["locale"]: r for r in results},
        }
        with open(json_out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report written to: {json_out}")

    # ── Exit code ─────────────────────────────────────────────────────────────
    if below_threshold:
        print(f"\nGATE FAIL — {len(below_threshold)} locale(s) below {min_coverage:.0%} threshold.")
        return 1

    print(f"\nGATE PASS — all {len(locales)} locale(s) at or above {min_coverage:.0%} threshold.")
    return 0


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description="Locale structural coverage gate (no LLM required)")
    ap.add_argument("--locales", nargs="+", default=None,
                    help="Locale codes to check (default: all 15)")
    ap.add_argument("--min-coverage", type=float, default=0.0,
                    help="Minimum atom coverage ratio to pass gate (0.0–1.0, default 0.0 = advisory)")
    ap.add_argument("--verbose", "-v", action="store_true",
                    help="Show per-topic detail and issue list")
    ap.add_argument("--json-out", type=Path, default=None,
                    help="Write JSON report to this path")
    args = ap.parse_args()

    locales = args.locales if args.locales else TARGET_LOCALES

    return run_gate(
        locales=locales,
        min_coverage=args.min_coverage,
        verbose=args.verbose,
        json_out=args.json_out,
    )


if __name__ == "__main__":
    sys.exit(main())
