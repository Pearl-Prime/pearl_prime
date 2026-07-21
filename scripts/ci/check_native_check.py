#!/usr/bin/env python3
"""CI gate: native_check contract on translated production atoms.

Scans:
  - SOURCE_OF_TRUTH/teacher_banks/*/approved_atoms_localized/{locale}/**/*.yaml
    (inline native_check field)
  - atoms/**/locales/{locale}/ with native_check.yaml sidecar per locale dir

Modes:
  --bootstrap-mode   missing native_check → warn, exit 0 (transition)
  --production-only  fail on missing or n (ship gate; CI default when not bootstrap)

Run:
  PYTHONPATH=. python3 scripts/ci/check_native_check.py --bootstrap-mode
  PYTHONPATH=. python3 scripts/ci/check_native_check.py --production-only
  PYTHONPATH=. python3 scripts/ci/check_native_check.py --json-out artifacts/qa/native_check_coverage.json

Exit: 0 pass; 1 fail.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONTRACT_PATH = REPO_ROOT / "config" / "localization" / "native_check_contract.yaml"

# Production atom headers: "## HOOK v01" / "## PIVOT v01"
HEADER_VARIANT_RE = re.compile(r"^##\s+\S+\s+(v\d{2})\s*$", re.MULTILINE)
# Alternate / test format: "--- variant: v01"
ALT_VARIANT_RE = re.compile(r"^---\s+variant:\s+(v\d{2})\s*$", re.MULTILINE)
VARIANT_KEY_RE = re.compile(r"^v\d{2}$")
VALID_VALUES = frozenset({"y", "n"})


@dataclass
class ScanStats:
    teacher_atoms: int = 0
    atom_locale_dirs: int = 0
    atom_variants: int = 0
    native_y: int = 0
    native_n: int = 0
    missing: int = 0
    invalid: int = 0


@dataclass
class ScanResult:
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    stats: ScanStats = field(default_factory=ScanStats)
    # locale -> atom_class -> {y,n,missing,invalid,total}
    by_locale_class: dict[str, dict[str, dict[str, int]]] = field(
        default_factory=lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    )


def _load_contract(repo_root: Path) -> dict[str, Any]:
    path = repo_root / "config" / "localization" / "native_check_contract.yaml"
    if not path.is_file():
        raise FileNotFoundError(f"native_check contract missing: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    locales = list(data.get("non_baseline_locales") or [])
    baseline = data.get("baseline_locale", "en-US")
    if baseline in locales:
        locales = [loc for loc in locales if loc != baseline]
    return {
        "baseline_locale": baseline,
        "non_baseline_locales": locales,
        "production_ship_value": data.get("production_ship_value", "y"),
    }


def _parse_variants_from_canonical(path: Path) -> list[str]:
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8")
    found = HEADER_VARIANT_RE.findall(text)
    if not found:
        found = ALT_VARIANT_RE.findall(text)
    # Preserve order, dedupe
    seen: set[str] = set()
    out: list[str] = []
    for key in found:
        if key not in seen:
            seen.add(key)
            out.append(key)
    return out


def _bump(
    result: ScanResult,
    locale: str,
    atom_class: str,
    bucket: str,
) -> None:
    result.by_locale_class[locale][atom_class][bucket] += 1
    result.by_locale_class[locale][atom_class]["total"] += 1


def _record_value(
    result: ScanResult,
    value: str | None,
    label: str,
    *,
    locale: str,
    atom_class: str,
    bootstrap_mode: bool,
    production_only: bool,
) -> None:
    if value is None or (isinstance(value, str) and not str(value).strip()):
        result.stats.missing += 1
        _bump(result, locale, atom_class, "missing")
        msg = f"MISSING native_check: {label}"
        if bootstrap_mode:
            result.warnings.append(msg)
        else:
            result.violations.append(msg)
        return

    norm = str(value).strip().lower()
    if norm not in VALID_VALUES:
        result.stats.invalid += 1
        _bump(result, locale, atom_class, "invalid")
        result.violations.append(f"INVALID native_check={value!r}: {label}")
        return

    if norm == "y":
        result.stats.native_y += 1
        _bump(result, locale, atom_class, "y")
    else:
        result.stats.native_n += 1
        _bump(result, locale, atom_class, "n")
        if production_only and not bootstrap_mode:
            result.violations.append(f"native_check=n (not production-shippable): {label}")
        elif production_only and bootstrap_mode:
            # Transition: n is recorded but does not block bootstrap CI.
            # Ship gate (--production-only without --bootstrap-mode) still fails.
            result.warnings.append(f"native_check=n (bootstrap tolerates; ship gate will fail): {label}")
        else:
            result.warnings.append(f"native_check=n: {label}")


def _scan_teacher_banks(
    repo_root: Path,
    locales: list[str],
    result: ScanResult,
    *,
    bootstrap_mode: bool,
    production_only: bool,
) -> None:
    root = repo_root / "SOURCE_OF_TRUTH" / "teacher_banks"
    if not root.is_dir():
        return
    for teacher_dir in sorted(root.iterdir()):
        if not teacher_dir.is_dir():
            continue
        localized_root = teacher_dir / "approved_atoms_localized"
        if not localized_root.is_dir():
            continue
        for locale in locales:
            locale_dir = localized_root / locale
            if not locale_dir.is_dir():
                continue
            for yaml_path in sorted(locale_dir.rglob("*.yaml")):
                result.stats.teacher_atoms += 1
                # atom class = parent dir name (PIVOT, HOOK, …) when present
                atom_class = yaml_path.parent.name if yaml_path.parent != locale_dir else "teacher"
                try:
                    doc = yaml.safe_load(yaml_path.read_text(encoding="utf-8")) or {}
                except yaml.YAMLError as exc:
                    result.stats.invalid += 1
                    _bump(result, locale, atom_class, "invalid")
                    rel = yaml_path.relative_to(repo_root)
                    result.violations.append(f"YAML parse error {rel}: {exc}")
                    continue
                if not isinstance(doc, dict):
                    result.stats.invalid += 1
                    _bump(result, locale, atom_class, "invalid")
                    rel = yaml_path.relative_to(repo_root)
                    result.violations.append(f"expected mapping in {rel}")
                    continue
                rel = yaml_path.relative_to(repo_root)
                _record_value(
                    result,
                    doc.get("native_check"),
                    str(rel),
                    locale=locale,
                    atom_class=atom_class,
                    bootstrap_mode=bootstrap_mode,
                    production_only=production_only,
                )


def _scan_atoms_locales(
    repo_root: Path,
    locales: list[str],
    result: ScanResult,
    *,
    bootstrap_mode: bool,
    production_only: bool,
) -> None:
    atoms_root = repo_root / "atoms"
    if not atoms_root.is_dir():
        return
    for locale in locales:
        for locale_dir in sorted(atoms_root.rglob(f"locales/{locale}")):
            if not locale_dir.is_dir():
                continue
            canonical = locale_dir / "CANONICAL.txt"
            if not canonical.is_file():
                continue
            result.stats.atom_locale_dirs += 1
            rel_dir = locale_dir.relative_to(repo_root)
            # atoms/{persona}/{topic}/{slot}/locales/{locale}
            parts = locale_dir.parts
            try:
                loc_idx = parts.index("locales")
                atom_class = parts[loc_idx - 1] if loc_idx >= 1 else "unknown"
            except ValueError:
                atom_class = "unknown"
            variants = _parse_variants_from_canonical(canonical)
            sidecar_path = locale_dir / "native_check.yaml"
            if not sidecar_path.is_file():
                n_miss = max(len(variants), 1)
                result.stats.missing += n_miss
                for _ in range(n_miss):
                    _bump(result, locale, atom_class, "missing")
                msg = f"MISSING sidecar native_check.yaml: {rel_dir}"
                if bootstrap_mode:
                    result.warnings.append(msg)
                else:
                    result.violations.append(msg)
                continue

            try:
                sidecar = yaml.safe_load(sidecar_path.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError as exc:
                result.stats.invalid += 1
                _bump(result, locale, atom_class, "invalid")
                result.violations.append(f"YAML parse error {rel_dir}/native_check.yaml: {exc}")
                continue

            variant_map = sidecar.get("variants") if isinstance(sidecar, dict) else None
            if not isinstance(variant_map, dict):
                result.stats.invalid += 1
                _bump(result, locale, atom_class, "invalid")
                result.violations.append(f"native_check.yaml missing variants map: {rel_dir}")
                continue

            if not variants:
                result.stats.missing += 1
                _bump(result, locale, atom_class, "missing")
                msg = f"no variants parsed from CANONICAL.txt: {rel_dir}"
                if bootstrap_mode:
                    result.warnings.append(msg)
                else:
                    result.violations.append(msg)
                continue

            for variant_key in variants:
                result.stats.atom_variants += 1
                label = f"{rel_dir} variant {variant_key}"
                if variant_key not in variant_map:
                    _record_value(
                        result,
                        None,
                        label,
                        locale=locale,
                        atom_class=atom_class,
                        bootstrap_mode=bootstrap_mode,
                        production_only=production_only,
                    )
                    continue
                _record_value(
                    result,
                    variant_map[variant_key],
                    label,
                    locale=locale,
                    atom_class=atom_class,
                    bootstrap_mode=bootstrap_mode,
                    production_only=production_only,
                )

            for extra_key in sorted(variant_map):
                if extra_key not in variants and VARIANT_KEY_RE.match(str(extra_key)):
                    result.warnings.append(
                        f"extra variant key in sidecar (not in CANONICAL.txt): "
                        f"{rel_dir} {extra_key}"
                    )


def scan_native_check(
    repo_root: Path,
    *,
    bootstrap_mode: bool = False,
    production_only: bool = True,
) -> ScanResult:
    contract = _load_contract(repo_root)
    locales = contract["non_baseline_locales"]
    result = ScanResult()
    _scan_teacher_banks(
        repo_root,
        locales,
        result,
        bootstrap_mode=bootstrap_mode,
        production_only=production_only,
    )
    _scan_atoms_locales(
        repo_root,
        locales,
        result,
        bootstrap_mode=bootstrap_mode,
        production_only=production_only,
    )
    return result


def coverage_payload(result: ScanResult, *, bootstrap_mode: bool, production_only: bool) -> dict[str, Any]:
    s = result.stats
    by_locale: dict[str, Any] = {}
    for locale, classes in sorted(result.by_locale_class.items()):
        by_locale[locale] = {
            "by_class": {cls: dict(buckets) for cls, buckets in sorted(classes.items())},
            "totals": {
                "y": sum(b.get("y", 0) for b in classes.values()),
                "n": sum(b.get("n", 0) for b in classes.values()),
                "missing": sum(b.get("missing", 0) for b in classes.values()),
                "invalid": sum(b.get("invalid", 0) for b in classes.values()),
                "total": sum(b.get("total", 0) for b in classes.values()),
            },
        }
    total_checked = s.teacher_atoms + s.atom_variants
    return {
        "teacher_atoms": s.teacher_atoms,
        "atom_locale_dirs": s.atom_locale_dirs,
        "atom_variants": s.atom_variants,
        "total_checked": total_checked,
        "native_y": s.native_y,
        "native_n": s.native_n,
        "missing": s.missing,
        "invalid": s.invalid,
        "warnings": len(result.warnings),
        "violations": len(result.violations),
        "bootstrap_mode": bootstrap_mode,
        "production_only": production_only,
        "native_y_ratio": (s.native_y / total_checked) if total_checked else 0.0,
        "annotated_ratio": (
            (s.native_y + s.native_n) / total_checked if total_checked else 0.0
        ),
        "by_locale": by_locale,
    }


def _print_report(result: ScanResult, *, bootstrap_mode: bool) -> None:
    s = result.stats
    print(
        "native_check scan: "
        f"teacher_atoms={s.teacher_atoms} "
        f"atom_locale_dirs={s.atom_locale_dirs} "
        f"atom_variants={s.atom_variants} "
        f"y={s.native_y} n={s.native_n} missing={s.missing} invalid={s.invalid}"
    )
    for w in result.warnings[:50]:
        print(f"WARN: {w}")
    if len(result.warnings) > 50:
        print(f"WARN: ... and {len(result.warnings) - 50} more warnings")
    for v in result.violations[:50]:
        print(f"FAIL: {v}")
    if len(result.violations) > 50:
        print(f"FAIL: ... and {len(result.violations) - 50} more violations")
    if bootstrap_mode and result.warnings:
        print(f"bootstrap-mode: {len(result.warnings)} warning(s); missing tolerated")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Native-check contract gate for translated atoms")
    ap.add_argument(
        "--repo-root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root (default: auto-detect)",
    )
    ap.add_argument(
        "--bootstrap-mode",
        action="store_true",
        help="Warn only on missing native_check; exit 0 (transition)",
    )
    ap.add_argument(
        "--production-only",
        action="store_true",
        default=True,
        help="Fail on missing native_check or n when not in bootstrap (ship gate)",
    )
    ap.add_argument(
        "--no-production-only",
        action="store_false",
        dest="production_only",
        help="Allow n without failing (audit mode)",
    )
    ap.add_argument("--json", action="store_true", help="Emit JSON summary on stdout")
    ap.add_argument(
        "--json-out",
        type=Path,
        default=None,
        help="Write machine-readable coverage report (by locale + atom class)",
    )
    args = ap.parse_args(argv)

    repo_root = args.repo_root.resolve()
    try:
        result = scan_native_check(
            repo_root,
            bootstrap_mode=args.bootstrap_mode,
            production_only=args.production_only,
        )
    except FileNotFoundError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    payload = coverage_payload(
        result,
        bootstrap_mode=args.bootstrap_mode,
        production_only=args.production_only,
    )

    if args.json_out is not None:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"wrote coverage report: {args.json_out}")

    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        _print_report(result, bootstrap_mode=args.bootstrap_mode)

    if result.violations:
        print(f"native_check gate FAIL: {len(result.violations)} violation(s)")
        return 1
    print("native_check gate PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
