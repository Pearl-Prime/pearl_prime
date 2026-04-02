#!/usr/bin/env python3
"""
Validate translations against quality contracts and glossary.

Checks translated CANONICAL.txt files under atoms/**/locales/{locale}/
against:
  - config/localization/quality_contracts/glossary.yaml
  - config/localization/quality_contracts/golden_translation_regression.yaml
  - config/localization/quality_contracts/release_thresholds.yaml

Usage:
  python scripts/validate_translations.py --locale ja-JP
  python scripts/validate_translations.py --locale ja-JP --atoms-dir atoms/ --verbose
  python scripts/validate_translations.py --locale ja-JP --output report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent


# ── YAML loader ────────────────────────────────────────────────────────────

def _load_yaml(path: Path) -> dict:
    """Load YAML file, returning empty dict on failure."""
    try:
        import yaml  # type: ignore
    except ImportError:
        # Fallback: minimal YAML-subset parser for simple files
        return _load_yaml_fallback(path)
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _load_yaml_fallback(path: Path) -> dict:
    """Bare-bones YAML loader used when PyYAML is unavailable.

    Handles only the flat/list structures used by the quality-contract files.
    """
    import re

    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8")
    data: dict[str, Any] = {}
    current_key: str | None = None
    current_list: list | None = None
    current_item: dict | None = None

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # top-level scalar  key: value
        m = re.match(r"^(\w[\w_]*):\s*(.+)$", line)
        if m and not line[0].isspace():
            k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
            # try numeric
            try:
                v_parsed: Any = float(v)
                if v_parsed == int(v_parsed) and "." not in v:
                    v_parsed = int(v_parsed)
            except (ValueError, TypeError):
                v_parsed = v
            data[k] = v_parsed
            current_key = None
            current_list = None
            continue

        # top-level key opening a block (key:\n or key: [])
        m2 = re.match(r"^(\w[\w_]*):\s*(\[\])?\s*$", line)
        if m2 and not line[0].isspace():
            k = m2.group(1)
            data[k] = []
            current_key = k
            current_list = data[k]
            current_item = None
            continue

        # nested mapping key under top-level mapping
        m3 = re.match(r"^  (\w[\w_]*):\s*(.*)$", line)
        if m3 and current_key and isinstance(data.get(current_key), dict):
            k, v = m3.group(1), m3.group(2).strip().strip('"').strip("'")
            try:
                v_p: Any = float(v)
                if v_p == int(v_p) and "." not in v:
                    v_p = int(v_p)
            except (ValueError, TypeError):
                v_p = v
            data[current_key][k] = v_p
            continue

        # top-level key: with nested dict (like thresholds:)
        # detect indented block under a key that has no value
        if current_key and not isinstance(data.get(current_key), list):
            m4 = re.match(r"^  (\w[\w_]*):\s*(.+)$", line)
            if m4:
                if not isinstance(data[current_key], dict):
                    data[current_key] = {}
                k, v = m4.group(1), m4.group(2).strip().strip('"').strip("'")
                try:
                    v_p2: Any = float(v)
                    if v_p2 == int(v_p2) and "." not in v:
                        v_p2 = int(v_p2)
                except (ValueError, TypeError):
                    v_p2 = v
                data[current_key][k] = v_p2
                continue

        # list item start
        if stripped.startswith("- ") and current_list is not None:
            rest = stripped[2:].strip()
            # inline key: value
            m5 = re.match(r"^(\w[\w_]*):\s*(.+)$", rest)
            if m5:
                current_item = {m5.group(1): m5.group(2).strip().strip('"').strip("'")}
                current_list.append(current_item)
            else:
                current_list.append(rest)
                current_item = None
            continue

        # continuation of a list-item dict
        if current_item is not None and line.startswith("    "):
            m6 = re.match(r"^\s+(\w[\w_]*):\s*(.*)$", line)
            if m6:
                k, v = m6.group(1), m6.group(2).strip().strip('"').strip("'")
                if v == "[]":
                    v_final: Any = []
                else:
                    try:
                        v_final = float(v)
                        if v_final == int(v_final) and "." not in v:
                            v_final = int(v_final)
                    except (ValueError, TypeError):
                        v_final = v
                current_item[k] = v_final

    # Fixup: top-level keys that were set to empty string become dicts
    for k, v in list(data.items()):
        if v == "":
            data[k] = {}

    return data


# ── Quality contract loaders ───────────────────────────────────────────────

def load_glossary(repo_root: Path) -> list[dict]:
    """Return list of glossary term dicts."""
    data = _load_yaml(repo_root / "config" / "localization" / "quality_contracts" / "glossary.yaml")
    return data.get("terms", []) or []


def load_golden_segments(repo_root: Path) -> list[dict]:
    """Return list of golden translation segment dicts."""
    data = _load_yaml(repo_root / "config" / "localization" / "quality_contracts" / "golden_translation_regression.yaml")
    return data.get("segments", []) or []


def load_thresholds(repo_root: Path) -> dict:
    """Return thresholds dict."""
    data = _load_yaml(repo_root / "config" / "localization" / "quality_contracts" / "release_thresholds.yaml")
    return data.get("thresholds", {})


# ── Discovery ──────────────────────────────────────────────────────────────

def discover_translated_files(atoms_dir: Path, locale: str) -> list[Path]:
    """Find all translated CANONICAL.txt files for the given locale."""
    pattern = f"**/locales/{locale}/CANONICAL.txt"
    found = sorted(atoms_dir.glob(pattern))
    return found


# ── Glossary check ─────────────────────────────────────────────────────────

def check_glossary(text: str, terms: list[dict], locale: str) -> list[dict]:
    """Check that glossary terms use preferred translations.

    Returns a list of result dicts, one per applicable term.
    Each result has: term_id, en_term, expected, found, passed.
    """
    results = []
    text_lower = text.lower()

    for term in terms:
        term_id = term.get("id", "unknown")
        en_term = term.get("en_US", "")
        preferred = term.get(locale, "")
        forbidden = term.get(f"{locale}_forbidden", [])
        if isinstance(forbidden, str):
            forbidden = [forbidden]

        if not preferred:
            # No preferred translation defined for this locale; skip
            continue

        result: dict[str, Any] = {
            "term_id": term_id,
            "en_term": en_term,
            "expected": preferred,
            "found": None,
            "passed": True,
        }

        # Check if any forbidden alternative appears
        for fb in forbidden:
            if fb and fb.lower() in text_lower:
                result["found"] = fb
                result["passed"] = False
                break

        # If no forbidden term found, check if preferred term is present
        if result["passed"] and preferred.lower() not in text_lower:
            # The preferred term is absent — we don't fail for absence,
            # but it counts against coverage.
            result["found"] = None
            result["passed"] = True  # not a hard fail, just uncovered

        results.append(result)

    return results


def glossary_coverage(results: list[dict], text: str) -> float:
    """Fraction of applicable glossary terms whose preferred translation appears."""
    if not results:
        return 1.0  # No terms to check → 100 %
    text_lower = text.lower()
    covered = sum(
        1 for r in results
        if r["expected"] and r["expected"].lower() in text_lower
    )
    return covered / len(results)


# ── Golden regression check ────────────────────────────────────────────────

def fuzzy_match(actual: str, expected: str, threshold: float = 0.80) -> tuple[bool, float]:
    """Return (passed, similarity) using SequenceMatcher."""
    if not expected:
        return True, 1.0
    ratio = SequenceMatcher(None, actual.strip(), expected.strip()).ratio()
    return ratio >= threshold, round(ratio, 4)


def check_golden_segments(
    translated_files: list[Path],
    segments: list[dict],
    locale: str,
    fuzzy_threshold: float = 0.80,
) -> list[dict]:
    """Check golden segments against translated content.

    Each segment has a source (en_US) and expected translation for the locale.
    We search all translated files for content that should match.
    """
    # Build a single corpus from all translated files
    corpus_parts: list[str] = []
    for fp in translated_files:
        corpus_parts.append(fp.read_text(encoding="utf-8"))
    corpus = "\n".join(corpus_parts)

    results = []
    for seg in segments:
        seg_id = seg.get("id", "unknown")
        expected = seg.get(locale, "")
        source = seg.get("en_US", "")

        if not expected:
            # No expected translation for this locale
            continue

        # Try to find the best matching window in the corpus
        if not corpus.strip():
            results.append({
                "segment_id": seg_id,
                "source": source,
                "expected": expected,
                "best_match": "",
                "similarity": 0.0,
                "passed": False,
            })
            continue

        # Slide a window of similar length to expected over the corpus
        best_ratio = 0.0
        best_match = ""
        exp_len = len(expected)
        # Use line-by-line comparison for efficiency
        for line in corpus.splitlines():
            line_s = line.strip()
            if not line_s:
                continue
            ratio = SequenceMatcher(None, line_s, expected.strip()).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = line_s

        passed = best_ratio >= fuzzy_threshold
        results.append({
            "segment_id": seg_id,
            "source": source,
            "expected": expected,
            "best_match": best_match,
            "similarity": round(best_ratio, 4),
            "passed": passed,
        })

    return results


# ── Threshold check ────────────────────────────────────────────────────────

def check_thresholds(
    glossary_cov: float,
    golden_pass_rate: float,
    file_count: int,
    thresholds: dict,
) -> dict:
    """Compare metrics against release thresholds.  Returns a results dict."""
    min_glossary = thresholds.get("min_glossary_coverage", 0.0)
    min_golden = thresholds.get("min_golden_regression_pass", 1.0)
    min_segments = thresholds.get("min_segment_count_per_locale", 0)

    glossary_ok = glossary_cov >= min_glossary
    golden_ok = golden_pass_rate >= min_golden
    segment_ok = file_count >= min_segments

    return {
        "glossary_coverage": {"value": round(glossary_cov, 4), "threshold": min_glossary, "passed": glossary_ok},
        "golden_regression_pass": {"value": round(golden_pass_rate, 4), "threshold": min_golden, "passed": golden_ok},
        "segment_count": {"value": file_count, "threshold": min_segments, "passed": segment_ok},
        "all_passed": glossary_ok and golden_ok and segment_ok,
    }


# ── Main ───────────────────────────────────────────────────────────────────

def run_validation(
    locale: str,
    atoms_dir: Path,
    repo_root: Path,
    verbose: bool = False,
) -> dict:
    """Run all validation checks and return structured report."""

    # Load contracts
    glossary_terms = load_glossary(repo_root)
    golden_segments = load_golden_segments(repo_root)
    thresholds = load_thresholds(repo_root)

    # Discover translated files
    translated_files = discover_translated_files(atoms_dir, locale)

    if not translated_files:
        return {
            "locale": locale,
            "atoms_dir": str(atoms_dir),
            "file_count": 0,
            "error": f"No translated CANONICAL.txt files found for locale '{locale}'",
            "glossary_results": [],
            "golden_results": [],
            "threshold_check": check_thresholds(0.0, 0.0, 0, thresholds),
            "overall_passed": thresholds.get("min_segment_count_per_locale", 0) == 0
                              and thresholds.get("min_glossary_coverage", 0.0) == 0.0
                              and thresholds.get("min_golden_regression_pass", 1.0) <= 0.0,
        }

    # Per-file glossary checks
    all_glossary_results: list[dict] = []
    per_file: list[dict] = []
    total_coverage = 0.0

    for fp in translated_files:
        text = fp.read_text(encoding="utf-8")
        file_glossary = check_glossary(text, glossary_terms, locale)
        cov = glossary_coverage(file_glossary, text)
        total_coverage += cov

        forbidden_failures = [r for r in file_glossary if not r["passed"]]

        per_file.append({
            "file": str(fp.relative_to(atoms_dir)) if fp.is_relative_to(atoms_dir) else str(fp),
            "glossary_coverage": round(cov, 4),
            "glossary_failures": forbidden_failures,
        })
        all_glossary_results.extend(file_glossary)

    avg_glossary_coverage = total_coverage / len(translated_files) if translated_files else 0.0

    # Any forbidden-term failure is a hard fail on the glossary side
    has_forbidden = any(not r["passed"] for r in all_glossary_results)
    effective_glossary = 0.0 if has_forbidden else avg_glossary_coverage

    # Golden regression
    golden_results = check_golden_segments(translated_files, golden_segments, locale)
    golden_total = len(golden_results)
    golden_passed = sum(1 for r in golden_results if r["passed"])
    golden_pass_rate = golden_passed / golden_total if golden_total > 0 else 1.0

    # Threshold
    threshold_result = check_thresholds(
        effective_glossary, golden_pass_rate, len(translated_files), thresholds,
    )

    report = {
        "locale": locale,
        "atoms_dir": str(atoms_dir),
        "file_count": len(translated_files),
        "glossary_coverage": round(effective_glossary, 4),
        "has_forbidden_terms": has_forbidden,
        "golden_pass_rate": round(golden_pass_rate, 4),
        "per_file": per_file,
        "golden_results": golden_results,
        "threshold_check": threshold_result,
        "overall_passed": threshold_result["all_passed"],
    }

    if verbose:
        report["glossary_terms_loaded"] = len(glossary_terms)
        report["golden_segments_loaded"] = len(golden_segments)
        report["translated_files"] = [str(f) for f in translated_files]

    return report


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate translations against quality contracts and glossary.",
    )
    ap.add_argument("--locale", required=True, help="Target locale (e.g. ja-JP)")
    ap.add_argument("--atoms-dir", default="atoms/", help="Path to atoms directory (default: atoms/)")
    ap.add_argument("--verbose", action="store_true", help="Include extra detail in report")
    ap.add_argument("--output", "-o", help="Write JSON report to file (default: stdout)")
    args = ap.parse_args()

    repo_root = REPO_ROOT
    atoms_dir = Path(args.atoms_dir)
    if not atoms_dir.is_absolute():
        atoms_dir = repo_root / atoms_dir

    report = run_validation(
        locale=args.locale,
        atoms_dir=atoms_dir,
        repo_root=repo_root,
        verbose=args.verbose,
    )

    report_json = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report_json, encoding="utf-8")
        print(f"Report written to {out_path}", file=sys.stderr)
    else:
        print(report_json)

    return 0 if report["overall_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
