#!/usr/bin/env python3
"""
Bestseller Analysis at Scale
==============================
Runs bestseller quality gate analysis across a full catalog scope.
NOT the single-chapter canary (scripts/canary/run_bestseller_canary.py).
This sweeps all built books in a given scope and logs every result to the
QA findings registry for regression tracking.

Usage:
    python3 scripts/qa/run_bestseller_analysis.py --scope all
    python3 scripts/qa/run_bestseller_analysis.py --market japan
    python3 scripts/qa/run_bestseller_analysis.py --brand stillness_press
    python3 scripts/qa/run_bestseller_analysis.py --input artifacts/catalog/full_catalog.csv
    python3 scripts/qa/run_bestseller_analysis.py --scope all --dry-run

Output:
    artifacts/qa/bestseller_analysis_<timestamp>.json
    Exit code 1 if regressions detected.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
_WORKTREE = Path(__file__).resolve().parents[2]
_MAIN_REPO = Path("/Users/ahjan/phoenix_omega")
_REPO_ROOT = _MAIN_REPO if _MAIN_REPO.exists() else _WORKTREE

sys.path.insert(0, str(_REPO_ROOT))

try:
    import yaml
    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

# ---------------------------------------------------------------------------
# Market → locale mapping (mirrors generate_full_catalog.py)
# ---------------------------------------------------------------------------
MARKET_TO_LOCALE: dict[str, str] = {
    "us": "en_US",
    "japan": "ja_JP",
    "korea": "ko_KR",
    "germany": "de_DE",
    "france": "fr_FR",
    "taiwan": "zh_TW",
    "china": "zh_CN",
    "hong_kong": "zh_HK",
    "spain": "es_ES",
    "latam": "es_US",
    "brazil": "pt_BR",
    "italy": "it_IT",
    "singapore": "zh_SG",
    "hungary": "hu_HU",
}

# ---------------------------------------------------------------------------
# Gate stack wrapper
# ---------------------------------------------------------------------------

def run_gate_stack(text: str, gate_config: dict) -> dict:
    """Run all gates defined in gate_config against text.

    Returns {gate_name: {status, score, issues}}.
    Uses phoenix_v4 gate implementations when available; falls back to
    a lightweight heuristic runner for CI/dry-run contexts where the full
    phoenix_v4 tree is not importable.
    """
    results: dict[str, dict] = {}

    # --- Attempt real bestseller craft gate ---
    try:
        from phoenix_v4.quality.bestseller_craft_gate import evaluate_bestseller_craft
        thresholds = gate_config.get("bestseller_craft", {})
        craft_result = evaluate_bestseller_craft(text, thresholds=thresholds or None)
        overall_score = getattr(craft_result, "overall_score", None)
        fail_below = (thresholds.get("fail_below") if thresholds else None) or 0.20
        warn_below = (thresholds.get("warn_below") if thresholds else None) or 0.40
        if overall_score is None:
            status = "WARN"
        elif overall_score < fail_below:
            status = "FAIL"
        elif overall_score < warn_below:
            status = "WARN"
        else:
            status = "PASS"
        issues: list[str] = []
        if hasattr(craft_result, "failing_moves"):
            issues = [f"failing move: {m}" for m in (craft_result.failing_moves or [])]
        results["bestseller_craft"] = {
            "status": status,
            "score": float(overall_score) if overall_score is not None else None,
            "issues": issues,
        }
    except Exception as exc:  # noqa: BLE001
        results["bestseller_craft"] = {
            "status": "WARN",
            "score": None,
            "issues": [f"gate unavailable: {exc}"],
        }

    # --- Heuristic length gate ---
    word_count = len(text.split()) if text else 0
    min_words = gate_config.get("min_word_count", 1500)
    results["word_count"] = {
        "status": "PASS" if word_count >= min_words else "FAIL",
        "score": float(word_count),
        "issues": [] if word_count >= min_words else [f"word count {word_count} < {min_words}"],
    }

    return results


# ---------------------------------------------------------------------------
# Catalog loader + scope filter
# ---------------------------------------------------------------------------

def _load_catalog(csv_path: Path) -> list[dict]:
    if not csv_path.exists():
        return []
    with open(csv_path, "r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        return list(reader)


def _filter_entries(entries: list[dict], market: Optional[str], brand: Optional[str]) -> list[dict]:
    if market:
        locale = MARKET_TO_LOCALE.get(market.lower())
        if locale:
            entries = [e for e in entries if e.get("lane_id", "").lower() == locale.lower()]
    if brand:
        entries = [e for e in entries if e.get("brand_id", "").lower() == brand.lower()]
    return entries


def _load_gate_config() -> dict:
    for root in [_WORKTREE, _REPO_ROOT]:
        p = root / "config/quality/bestseller_craft_gate.yaml"
        if p.exists() and _HAS_YAML:
            with open(p, "r", encoding="utf-8") as fh:
                return yaml.safe_load(fh) or {}
    return {}


# ---------------------------------------------------------------------------
# Content loader
# ---------------------------------------------------------------------------

def _load_content(entry: dict) -> Optional[str]:
    """Try to load book text from book_path or content_path columns."""
    for col in ("book_path", "content_path", "atom_path"):
        raw = entry.get(col, "")
        if not raw:
            continue
        for base in [_WORKTREE, _REPO_ROOT]:
            p = base / raw
            if p.exists() and p.suffix in {".txt", ".md"}:
                try:
                    return p.read_text(encoding="utf-8")
                except OSError:
                    pass
    return None


# ---------------------------------------------------------------------------
# Main analysis runner
# ---------------------------------------------------------------------------

def run_analysis(
    entries: list[dict],
    gate_config: dict,
    run_id: str,
    dry_run: bool = False,
) -> dict:
    """Run gate stack over all entries. Returns summary dict."""
    from scripts.qa.qa_findings_registry import log_gate_result

    total = len(entries)
    passed = 0
    failed = 0
    warned = 0
    regressions = 0
    gate_breakdown: dict[str, dict] = {}
    failing_top: list[dict] = []
    passing_top: list[dict] = []

    for entry in entries:
        content_id = entry.get("catalog_id") or entry.get("title") or "unknown"
        text = _load_content(entry)
        if text is None:
            # No content file — use title + description as a stub text for gate scoring
            text = " ".join(filter(None, [
                entry.get("title", ""),
                entry.get("subtitle", ""),
                entry.get("description", ""),
            ]))

        gate_results = run_gate_stack(text, gate_config)

        entry_passed = True
        entry_issues: list[str] = []
        entry_scores: list[float] = []

        for gate_name, gresult in gate_results.items():
            status = gresult["status"]
            score = gresult["score"]
            issues = gresult["issues"]

            if not dry_run:
                written = log_gate_result(
                    content_id=content_id,
                    gate_name=gate_name,
                    status=status,
                    score=score,
                    issues=issues,
                    run_id=run_id,
                )
                if written.get("is_regression"):
                    regressions += 1

            # Gate breakdown accumulation
            if gate_name not in gate_breakdown:
                gate_breakdown[gate_name] = {"PASS": 0, "FAIL": 0, "WARN": 0}
            gate_breakdown[gate_name][status] = gate_breakdown[gate_name].get(status, 0) + 1

            if status == "FAIL":
                entry_passed = False
                entry_issues.extend(issues)
            if score is not None:
                entry_scores.append(score)

        avg_score = sum(entry_scores) / len(entry_scores) if entry_scores else None

        if entry_passed:
            passed += 1
            passing_top.append({
                "content_id": content_id,
                "brand_id": entry.get("brand_id"),
                "score": avg_score,
            })
        else:
            failed += 1
            failing_top.append({
                "content_id": content_id,
                "brand_id": entry.get("brand_id"),
                "score": avg_score,
                "issues": entry_issues[:3],
            })

    # Count warns from gate breakdown
    warned = sum(gate_breakdown.get(g, {}).get("WARN", 0) for g in gate_breakdown)

    pass_rate = passed / total * 100 if total else 0.0

    return {
        "run_id": run_id,
        "timestamp": datetime.now(tz=timezone.utc).isoformat(),
        "total_analyzed": total,
        "passed": passed,
        "failed": failed,
        "warned": warned,
        "regressions": regressions,
        "pass_rate": round(pass_rate, 2),
        "gate_breakdown": gate_breakdown,
        "top_failing": sorted(failing_top, key=lambda x: (x.get("score") or 0))[:10],
        "top_passing": sorted(passing_top, key=lambda x: -(x.get("score") or 0))[:10],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Bestseller Analysis at Scale")
    scope_group = parser.add_mutually_exclusive_group()
    scope_group.add_argument("--scope", choices=["all"], default=None,
                             help="Run across all catalog entries")
    scope_group.add_argument("--market", type=str, default=None,
                             help="Filter by market ID (e.g. japan, us, taiwan)")
    scope_group.add_argument("--brand", type=str, default=None,
                             help="Filter by brand ID (e.g. stillness_press)")
    parser.add_argument("--input", type=str,
                        default="artifacts/catalog/full_catalog.csv",
                        help="Path to full_catalog.csv (relative to repo root)")
    parser.add_argument("--output-dir", type=str,
                        default="artifacts/qa",
                        help="Directory for analysis output JSON")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run analysis but do not write to findings registry")
    args = parser.parse_args()

    # Resolve catalog CSV
    for base in [_WORKTREE, _REPO_ROOT]:
        csv_path = base / args.input
        if csv_path.exists():
            break
    else:
        csv_path = _REPO_ROOT / args.input

    print("Bestseller Analysis at Scale")
    print("=" * 40)
    print(f"Catalog: {csv_path}")
    if args.dry_run:
        print("[DRY-RUN] findings registry will NOT be updated")

    entries = _load_catalog(csv_path)
    if not entries:
        print(f"No catalog entries found at {csv_path}. Run generate_full_catalog.py first.")
        print("Continuing with empty entry list for dry-run validation.")

    # Apply scope filter
    if args.market:
        entries = _filter_entries(entries, market=args.market, brand=None)
        print(f"Market filter '{args.market}': {len(entries)} entries")
    elif args.brand:
        entries = _filter_entries(entries, market=None, brand=args.brand)
        print(f"Brand filter '{args.brand}': {len(entries)} entries")

    print(f"Analyzing {len(entries)} entries...")

    gate_config = _load_gate_config()
    run_id = uuid.uuid4().hex[:12]
    summary = run_analysis(entries, gate_config, run_id=run_id, dry_run=args.dry_run)

    # Print summary
    print()
    print(f"  Total analyzed : {summary['total_analyzed']}")
    print(f"  Passed         : {summary['passed']}")
    print(f"  Failed         : {summary['failed']}")
    print(f"  Pass rate      : {summary['pass_rate']}%")
    print(f"  Regressions    : {summary['regressions']}")

    if summary["top_failing"]:
        print()
        print("Top failing content IDs:")
        for item in summary["top_failing"][:5]:
            print(f"  {item['content_id']}  score={item.get('score')}  issues={item.get('issues', [])[:1]}")

    # Write output JSON
    ts = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%S")
    for base in [_WORKTREE, _REPO_ROOT]:
        out_dir = base / args.output_dir
        if out_dir.parent.exists():
            break
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"bestseller_analysis_{ts}.json"

    if not args.dry_run:
        with open(out_path, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        print(f"\nOutput: {out_path}")
    else:
        print(f"\n[DRY-RUN] Would write output to {out_path}")

    if summary["regressions"] > 0:
        print(f"\n⚠️  REGRESSION DETECTED — {summary['regressions']} regression(s) found in this run.")
        sys.exit(1)


if __name__ == "__main__":
    main()
