#!/usr/bin/env python3
"""Validate fonts/manga/FONT_REGISTRY.yaml — schema + locale coverage.

Per PR #631 Decision 3: every locale Phoenix Omega ships must have at
least one body font registered, or that locale's renders blow up with
missing-glyph boxes. This script fails CI if:

- Registry doesn't parse / required fields missing
- locale_coverage_required references font ids that don't exist
- A registered font's path collides with another font's path
- (Optional --strict) Any registered font is still status: pending

Usage:
    python3 scripts/manga/check_font_registry.py
    python3 scripts/manga/check_font_registry.py --strict   # fail on pending
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
REGISTRY = REPO / "fonts" / "manga" / "FONT_REGISTRY.yaml"


REQUIRED_FONT_FIELDS = ("id", "license", "path", "status")
VALID_STATUSES = ("pending", "installed", "verified", "blocked")
VALID_LOCALES = ("en_US", "ja_JP", "ko_KR", "zh_TW", "zh_CN")


def _load() -> dict[str, Any]:
    import yaml  # type: ignore

    if not REGISTRY.exists():
        raise FileNotFoundError(REGISTRY)
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}


def validate_registry(data: dict[str, Any], strict: bool = False) -> list[str]:
    errors: list[str] = []

    fonts = data.get("fonts") or []
    if not fonts:
        errors.append("registry has no fonts[]")
        return errors

    seen_ids: set[str] = set()
    seen_paths: set[str] = set()

    for f in fonts:
        if not isinstance(f, dict):
            errors.append(f"font entry not a mapping: {f}")
            continue
        for field in REQUIRED_FONT_FIELDS:
            if field not in f:
                errors.append(f"font {f.get('id', '?')}: missing required field '{field}'")

        fid = f.get("id")
        if fid in seen_ids:
            errors.append(f"duplicate font id: {fid}")
        else:
            seen_ids.add(fid)

        path = f.get("path")
        if path in seen_paths:
            errors.append(f"duplicate font path: {path}")
        else:
            seen_paths.add(path)

        status = f.get("status")
        if status not in VALID_STATUSES:
            errors.append(f"font {fid}: invalid status '{status}' (valid: {VALID_STATUSES})")
        if strict and status == "pending":
            errors.append(f"font {fid}: status=pending (strict mode requires installed/verified)")

        for locale in f.get("locale_targets") or []:
            if locale not in VALID_LOCALES:
                errors.append(f"font {fid}: unknown locale_target '{locale}'")

    # Coverage map cross-references
    coverage = data.get("locale_coverage_required") or {}
    for locale, roles in coverage.items():
        if locale not in VALID_LOCALES:
            errors.append(f"locale_coverage_required: unknown locale '{locale}'")
            continue
        if not isinstance(roles, dict):
            errors.append(f"locale_coverage_required[{locale}]: not a mapping")
            continue
        for role, font_id in roles.items():
            if font_id not in seen_ids:
                errors.append(
                    f"locale_coverage_required[{locale}].{role} references "
                    f"unknown font id '{font_id}'"
                )

    # Every catalog locale needs at least a body font
    catalog_locales = ("en_US", "ja_JP", "zh_TW", "zh_CN")
    for locale in catalog_locales:
        if locale not in coverage:
            errors.append(f"locale_coverage_required missing entry for {locale}")
            continue
        if "body" not in coverage[locale]:
            errors.append(f"locale_coverage_required[{locale}] has no 'body' role")

    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--strict", action="store_true",
                   help="Fail if any font is status=pending (default: warn only)")
    args = p.parse_args()

    try:
        data = _load()
    except Exception as e:
        sys.stderr.write(f"❌ failed to load registry: {e}\n")
        return 2

    errors = validate_registry(data, strict=args.strict)
    if errors:
        sys.stderr.write(f"❌ {len(errors)} validation errors:\n")
        for e in errors:
            sys.stderr.write(f"   - {e}\n")
        return 1

    fonts = data.get("fonts") or []
    coverage = data.get("locale_coverage_required") or {}
    pending = [f["id"] for f in fonts if f.get("status") == "pending"]

    print(f"✓ registry valid: {len(fonts)} fonts, {len(coverage)} locales covered")
    if pending:
        print(f"  {len(pending)} fonts still pending download:")
        for fid in pending:
            print(f"    - {fid}")
        print("  → run: bash scripts/manga/install_manga_fonts.sh")
    return 0


if __name__ == "__main__":
    sys.exit(main())
