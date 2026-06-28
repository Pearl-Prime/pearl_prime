#!/usr/bin/env python3
"""Post-translation structural validator for CJK locale atoms.

Mirrors CI parse-sweep rules (assembly_compiler._parse_canonical_txt +
over-match signature scan). Use before writing or pulling locale atoms so
parse-failing translations never reach origin/main.

Usage:
    python3 scripts/localization/validate_cjk_atom.py path/to/locales/ja-JP/CANONICAL.txt
    python3 scripts/localization/validate_cjk_atom.py --paths-file /tmp/backlog.txt
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def validate_locale_atom(path: Path) -> tuple[bool, list[str]]:
    """Return (ok, failure_reasons). ok=True means safe to commit/pull."""
    sys.path.insert(0, str(REPO_ROOT))
    from phoenix_v4.planning.assembly_compiler import _parse_canonical_txt
    from scripts.ci.check_canonical_atom_parse_sweep import (
        is_baseline_parse_fail,
        is_english_story_pool,
        load_baseline,
        overmatch_signature_hits,
    )

    rel = str(path.resolve().relative_to(REPO_ROOT))
    baseline = load_baseline()
    reasons: list[str] = []

    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return False, [f"read error: {exc}"]

    parse_failed = False
    parse_exc = ""
    try:
        _parse_canonical_txt(path)
    except Exception as exc:
        parse_failed = True
        parse_exc = str(exc)

    om = overmatch_signature_hits(text)
    if om > 0 and rel not in baseline:
        reasons.append("overmatch_signature")
    if om > 0 and is_english_story_pool(path):
        reasons.append("story_pool_overmatch")

    if parse_failed and not is_baseline_parse_fail(rel, baseline):
        reasons.append(f"parse_fail: {parse_exc}")

    return not reasons, reasons


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("paths", nargs="*", help="Locale CANONICAL.txt paths")
    ap.add_argument("--paths-file", help="Newline-separated paths (repo-relative or absolute)")
    args = ap.parse_args(argv)

    paths: list[Path] = [Path(p) for p in args.paths]
    if args.paths_file:
        pf = Path(args.paths_file)
        for line in pf.read_text(encoding="utf-8").splitlines():
            line = line.strip().split("\t")[0]
            if line:
                p = Path(line)
                paths.append(p if p.is_absolute() else REPO_ROOT / line)

    if not paths:
        ap.error("provide paths or --paths-file")

    failed = 0
    for path in paths:
        ok, reasons = validate_locale_atom(path)
        if ok:
            print(f"OK  {path}")
        else:
            failed += 1
            print(f"FAIL {path}: {'; '.join(reasons)}")

    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
