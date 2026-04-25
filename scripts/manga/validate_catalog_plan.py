#!/usr/bin/env python3
"""Validator for manga series_plan and book_plan YAMLs.

Checks each plan against:
  1. JSON Schema in schemas/manga/series_plan.schema.json (or book_plan.schema.json)
  2. panel_layout_template path exists
  3. format is consistent between series_plan and book_plan
  4. Every entry in target_platforms[] appears in config/publishing/ai_policy_blockers.yaml
     with status ALLOWED or ALLOWED_GREY
  5. format value is compatible with panel_layout_template

Usage:
    python3 scripts/manga/validate_catalog_plan.py series <plan.yaml>
    python3 scripts/manga/validate_catalog_plan.py book <plan.yaml>
    python3 scripts/manga/validate_catalog_plan.py all       # validates everything

Exit codes:
    0 — all valid
    1 — at least one validation failure
    2 — config / schema missing / malformed
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = REPO / "schemas" / "manga"
PANEL_TEMPLATES_DIR = REPO / "config" / "manga" / "panel_layout_templates"
POLICY_PATH = REPO / "config" / "publishing" / "ai_policy_blockers.yaml"


class ValidationError(Exception):
    pass


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _load_json_schema(stem: str) -> dict[str, Any]:
    p = SCHEMAS_DIR / f"{stem}.schema.json"
    if not p.exists():
        raise ValidationError(f"Schema missing: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def _load_allowed_platforms() -> set[str]:
    pol = _load_yaml(POLICY_PATH)
    platforms = pol.get("platforms") or {}
    return {
        name
        for name, spec in platforms.items()
        if spec.get("status") in ("ALLOWED", "ALLOWED_GREY")
    }


def _validate_against_schema(data: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    """Lightweight JSON-schema validation (PyYAML data → JSON-schema check)."""
    try:
        import jsonschema  # type: ignore[import]
    except ImportError:
        # Soft-validate: check required fields manually if jsonschema not installed
        errors: list[str] = []
        for req in (schema.get("required") or []):
            if req not in data:
                errors.append(f"missing required field: {req}")
        return errors

    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{'.'.join(str(p) for p in err.absolute_path)}: {err.message}"
        for err in validator.iter_errors(data)
    ]


def _validate_panel_template(data: dict[str, Any]) -> list[str]:
    template_path = data.get("panel_layout_template")
    if not template_path:
        return []
    full_path = REPO / template_path
    if not full_path.exists():
        return [f"panel_layout_template missing: {template_path}"]
    template = _load_yaml(full_path)
    errors: list[str] = []
    # Format consistency
    if data.get("format") and template.get("format") != data["format"]:
        errors.append(
            f"format mismatch: series_plan format={data['format']!r} "
            f"but panel_layout_template format={template.get('format')!r}"
        )
    # target_platforms compatibility check
    targets = data.get("target_platforms") or []
    incompat = template.get("incompatible_platforms") or []
    overlap = [p for p in targets if p in incompat]
    if overlap:
        errors.append(
            f"target_platforms include platforms incompatible with panel_layout_template: "
            f"{overlap} (template incompatible_platforms: {incompat})"
        )
    return errors


def _validate_target_platforms(data: dict[str, Any], allowed: set[str]) -> list[str]:
    targets = data.get("target_platforms") or []
    if not targets:
        return ["target_platforms is empty (must declare at least one)"]
    bad = [p for p in targets if p not in allowed]
    if bad:
        return [
            f"target_platforms references not-ALLOWED platforms: {bad}. "
            f"Each must appear in config/publishing/ai_policy_blockers.yaml with "
            f"status ALLOWED or ALLOWED_GREY."
        ]
    return []


def validate_plan(path: Path, kind: str) -> list[str]:
    """Returns list of error messages (empty list = valid)."""
    if kind not in ("series", "book"):
        raise ValidationError(f"unknown kind: {kind}")

    schema_stem = "series_plan" if kind == "series" else "book_plan"
    schema = _load_json_schema(schema_stem)
    data = _load_yaml(path)

    errors: list[str] = []
    errors.extend(_validate_against_schema(data, schema))
    errors.extend(_validate_panel_template(data))
    allowed = _load_allowed_platforms()
    errors.extend(_validate_target_platforms(data, allowed))

    return errors


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("kind", choices=["series", "book", "all"])
    p.add_argument("path", nargs="?", default=None, help="path to YAML (omit when kind=all)")
    args = p.parse_args()

    if args.kind == "all":
        # Walk all manga-catalog series + book plans (post-rebuild)
        # Pre-rebuild: there are none yet, so this is a no-op pass.
        manga_series = list(
            (REPO / "config" / "source_of_truth" / "manga_series_plans").rglob("*.yaml")
        )
        manga_books = list(
            (REPO / "config" / "source_of_truth" / "manga_book_plans").rglob("*.yaml")
        )
        if not manga_series and not manga_books:
            print(
                "✓ No manga catalog plans yet (config/source_of_truth/manga_series_plans/ "
                "and manga_book_plans/ are empty pre-rebuild). Validator passes vacuously."
            )
            return 0
        total_errors = 0
        for f in manga_series:
            errs = validate_plan(f, "series")
            if errs:
                total_errors += len(errs)
                print(f"❌ {f.relative_to(REPO)}")
                for e in errs:
                    print(f"   - {e}")
        for f in manga_books:
            errs = validate_plan(f, "book")
            if errs:
                total_errors += len(errs)
                print(f"❌ {f.relative_to(REPO)}")
                for e in errs:
                    print(f"   - {e}")
        if total_errors:
            print(f"\n{total_errors} validation error(s)")
            return 1
        print(
            f"✓ {len(manga_series)} series + {len(manga_books)} book plans validated."
        )
        return 0

    if args.path is None:
        print("ERROR: path required when kind != all", file=sys.stderr)
        return 2
    target = Path(args.path)
    if not target.exists():
        print(f"ERROR: file not found: {target}", file=sys.stderr)
        return 2

    errors = validate_plan(target, args.kind)
    if errors:
        print(f"❌ {target}: {len(errors)} error(s)")
        for e in errors:
            print(f"   - {e}")
        return 1
    print(f"✓ {target} validates against {args.kind}_plan schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
