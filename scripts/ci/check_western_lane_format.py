#!/usr/bin/env python3
"""CI gate: western_intent_led en_US pilot must route to illustrated self-help format.

Blocks drift where en_US western-lane pilot cells are still assigned manga digest /
webtoon master_format (color_vertical_webtoon) instead of direct_self_help_illustrated.

Checks:
  1. format_routing.yaml western_lane_override.en_US.force_master
  2. western_cartoon_styles.yaml covers all 5 pilot brands
  3. us_illustrated_pilot_cells.yaml registry matches stub files on disk
  4. Each pilot series_plan stub has master_format=direct_self_help_illustrated,
     connector_lane=print_only, and no webtoon targets

Run:
    PYTHONPATH=scripts/ci:. python3 scripts/ci/check_western_lane_format.py

Exit: 0 PASS; 1 BLOCK.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

ROUTING = REPO_ROOT / "config" / "manga" / "format_routing.yaml"
PILOT_REGISTRY = REPO_ROOT / "config" / "manga" / "us_illustrated_pilot_cells.yaml"
STYLES = REPO_ROOT / "config" / "manga" / "western_cartoon_styles.yaml"
PLANS_ROOT = REPO_ROOT / "config" / "source_of_truth" / "manga_series_plans" / "en_US"
SCHEMA = REPO_ROOT / "schemas" / "manga" / "series_plan.schema.json"

ILLUSTRATED_MASTER = "direct_self_help_illustrated"
FORBIDDEN_WEBTOON_TARGETS = {"webtoon_canvas", "piccoma_smartoon", "line_manga_indies", "naver_webtoon"}


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise SystemExit("BLOCK: PyYAML required for check_western_lane_format.py")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def check_routing_override(routing: dict) -> list[str]:
    errors: list[str] = []
    wlo = routing.get("western_lane_override") or {}
    if wlo.get("lane") != "western_intent_led":
        errors.append("western_lane_override.lane must be western_intent_led")
    if wlo.get("product_shape") != "illustrated_self_help_picture_books":
        errors.append(
            "western_lane_override.product_shape must be illustrated_self_help_picture_books"
        )
    en_us = (wlo.get("locales") or {}).get("en_US") or {}
    if en_us.get("force_master") != ILLUSTRATED_MASTER:
        errors.append(
            f"western_lane_override.locales.en_US.force_master must be {ILLUSTRATED_MASTER}"
        )
    return errors


def check_style_registry(styles: dict, pilot_cells: list[dict]) -> list[str]:
    errors: list[str] = []
    brand_styles = (styles.get("brands") or {})
    for cell in pilot_cells:
        brand = cell["brand_id"]
        if brand not in brand_styles:
            errors.append(f"western_cartoon_styles.yaml missing brand: {brand}")
            continue
        entry = brand_styles[brand]
        prompt = (entry.get("prompt_template") or "").lower()
        if "manga" in prompt or "webtoon" in prompt:
            errors.append(f"{brand}: western_cartoon_styles prompt must not use manga/webtoon register")
    return errors


def check_pilot_stubs(pilot_cells: list[dict], schema: dict) -> list[str]:
    errors: list[str] = []
    try:
        import jsonschema  # type: ignore
    except ImportError:
        jsonschema = None  # type: ignore

    validator = jsonschema.Draft202012Validator(schema) if jsonschema else None

    for cell in pilot_cells:
        stub_name = cell["series_plan_stub"]
        path = PLANS_ROOT / stub_name
        if not path.is_file():
            errors.append(f"missing pilot series_plan stub: {stub_name}")
            continue

        plan = _load_yaml(path)
        if plan.get("master_format") != ILLUSTRATED_MASTER:
            errors.append(
                f"{stub_name}: master_format={plan.get('master_format')!r} "
                f"(expected {ILLUSTRATED_MASTER})"
            )
        if plan.get("format") != ILLUSTRATED_MASTER:
            errors.append(f"{stub_name}: format must equal master_format ({ILLUSTRATED_MASTER})")
        if plan.get("connector_lane") != "print_only":
            errors.append(
                f"{stub_name}: connector_lane={plan.get('connector_lane')!r} (expected print_only)"
            )
        targets = set(plan.get("target_platforms") or [])
        bad = targets & FORBIDDEN_WEBTOON_TARGETS
        if bad:
            errors.append(f"{stub_name}: webtoon/manga targets forbidden: {sorted(bad)}")
        if plan.get("brand_id") != cell["brand_id"]:
            errors.append(
                f"{stub_name}: brand_id={plan.get('brand_id')!r} != registry {cell['brand_id']!r}"
            )
        if plan.get("topic") != cell["topic"]:
            errors.append(
                f"{stub_name}: topic={plan.get('topic')!r} != registry {cell['topic']!r}"
            )
        if validator:
            for err in validator.iter_errors(plan):
                loc = ".".join(str(p) for p in err.absolute_path) or "(root)"
                errors.append(f"{stub_name}: schema {loc}: {err.message}")
                break

    return errors


def check_resolve_format_hook(routing: dict) -> list[str]:
    """Runtime routing must honor western_lane_override for en_US."""
    from scripts.manga.generate_series_plans_from_catalog import resolve_format  # type: ignore

    errors: list[str] = []
    # Any en_US genre/style combo should resolve to illustrated master under override.
    samples = [
        ("en_US", "iyashikei", "cozy_iyashikei"),
        ("en_US", "workplace_drama", "social_media_simulacra"),
        ("en_US", "psychological_thriller", "dark_psychological"),
    ]
    for locale, genre, style in samples:
        got = resolve_format(routing, locale, genre, style)
        if got != ILLUSTRATED_MASTER:
            errors.append(
                f"resolve_format({locale}, {genre}, {style}) -> {got!r} "
                f"(expected {ILLUSTRATED_MASTER})"
            )
    return errors


def run_checks() -> list[str]:
    errors: list[str] = []
    routing = _load_yaml(ROUTING)
    registry = _load_yaml(PILOT_REGISTRY)
    styles = _load_yaml(STYLES)
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))

    if registry.get("lane") != "western_intent_led":
        errors.append("us_illustrated_pilot_cells.yaml lane must be western_intent_led")
    if registry.get("master_format") != ILLUSTRATED_MASTER:
        errors.append("us_illustrated_pilot_cells.yaml master_format mismatch")

    pilot_cells = registry.get("pilot_cells") or []
    if len(pilot_cells) != 5:
        errors.append(f"expected 5 pilot cells, got {len(pilot_cells)}")

    errors.extend(check_routing_override(routing))
    errors.extend(check_style_registry(styles, pilot_cells))
    errors.extend(check_pilot_stubs(pilot_cells, schema))
    errors.extend(check_resolve_format_hook(routing))
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Western lane format correctness gate")
    parser.parse_args()
    errors = run_checks()
    if errors:
        print("BLOCK: western lane format check failed:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"PASS: western_intent_led en_US pilot ({ILLUSTRATED_MASTER}) — 5 cells OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
