#!/usr/bin/env python3
"""Honesty gate: production enrichment_audit must not pretend research_fit fired.

Usage (CI / local):
  PYTHONPATH=. python3 scripts/ci/check_research_fit_honesty.py <render_dir> [...]
  PYTHONPATH=. python3 scripts/ci/check_research_fit_honesty.py --audit path/to/enrichment_audit.json

Exit 0 = honest. Exit 1 = claims/features inconsistent with research_fit payload.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


def _load_audit(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def check_audit(audit: dict[str, Any], *, label: str) -> list[str]:
    errors: list[str] = []
    rf = audit.get("research_fit")
    skip = str(audit.get("research_fit_skip_reason") or "").strip()
    if rf is None:
        errors.append(f"{label}: missing research_fit key")
        return errors
    if not isinstance(rf, dict):
        errors.append(f"{label}: research_fit must be a dict")
        return errors

    mode = str(rf.get("mode") or "").strip()
    skip_in_rf = str(rf.get("skip_reason") or "").strip()

    # Empty {} without skip is dishonest after this fix.
    if not rf and not skip:
        errors.append(
            f"{label}: research_fit empty with no research_fit_skip_reason "
            "(production must stamp skip or nonempty fit)"
        )

    if mode == "skipped" and not (skip or skip_in_rf):
        errors.append(f"{label}: research_fit.mode=skipped but no skip_reason")

    # Claiming spine pins while skipped is dishonest.
    if mode == "skipped" or skip_in_rf or (skip and "no_story_atoms" in skip):
        pins = rf.get("spine_pins") or []
        if pins:
            errors.append(f"{label}: skip mode but spine_pins nonempty")

    # Active modes must not look empty of structure.
    if mode in ("research_fit_v1", "twelve_shape_continuity"):
        if not rf.get("book_phases") and not rf.get("spine_pins") and not rf.get("motif_ledger"):
            # soft warn as error for honesty — at least one structure field
            errors.append(
                f"{label}: mode={mode} but missing book_phases/spine_pins/motif_ledger"
            )

    return errors


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", type=Path, help="Render dirs or enrichment_audit.json files")
    ap.add_argument("--audit", type=Path, default=None, help="Single enrichment_audit.json")
    ap.add_argument(
        "--base",
        default=None,
        help="git base ref — scan changed enrichment_audit.json (Drift detectors CI)",
    )
    ap.add_argument("--head", default="HEAD")
    ap.add_argument(
        "--advisory",
        action="store_true",
        help="Warn on findings but exit 0 (Lane 01 default for CI wiring; "
             "hard-block remains the default without this flag)",
    )
    args = ap.parse_args(argv)
    targets: list[Path] = []
    if args.audit:
        targets.append(args.audit)
    for p in args.paths:
        if p.is_dir():
            targets.append(p / "enrichment_audit.json")
        else:
            targets.append(p)
    if args.base:
        # Dependency-light: resolve repo root + changed paths without requiring
        # PYTHONPATH=scripts/ci when invoked as PYTHONPATH=.
        ci_dir = Path(__file__).resolve().parent
        if str(ci_dir) not in sys.path:
            sys.path.insert(0, str(ci_dir))
        from drift_detector_git import changed_paths, repo_root_from_script

        repo_root = repo_root_from_script(Path(__file__))
        for rel in changed_paths(args.base, args.head, repo_root):
            if rel.endswith("enrichment_audit.json"):
                targets.append(repo_root / rel)
    if not targets:
        if args.base:
            print("PASS research_fit honesty (0 changed enrichment_audit.json)")
            return 0
        print("No paths given", file=sys.stderr)
        return 2
    all_errs: list[str] = []
    for t in targets:
        if not t.is_file():
            all_errs.append(f"missing {t}")
            continue
        all_errs.extend(check_audit(_load_audit(t), label=str(t)))
    if all_errs:
        for e in all_errs:
            print(f"FAIL: {e}", file=sys.stderr)
        if args.advisory:
            print(
                f"WARN research_fit honesty ({len(all_errs)} finding(s) — advisory, not blocking)",
                file=sys.stderr,
            )
            return 0
        return 1
    print(f"PASS research_fit honesty ({len(targets)} audit(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
