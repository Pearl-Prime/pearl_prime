#!/usr/bin/env python3
"""Validate marketing feed schema config and optional feed JSON artifacts."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_yaml(path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML required")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def validate_schema_config(config_dir: Path) -> list[str]:
    errors: list[str] = []
    schema_path = config_dir / "marketing_feed_schema.yaml"
    slot_path = config_dir / "ghl_email_slot_rules.yaml"
    persona_path = config_dir / "ghl_persona_variant_map.yaml"

    for p in (schema_path, slot_path, persona_path):
        if not p.exists():
            errors.append(f"missing config: {p}")
    if errors:
        return errors

    schema = _load_yaml(schema_path)
    slots = _load_yaml(slot_path)
    personas = _load_yaml(persona_path)

    defaults = slots.get("defaults_by_content_type") or {}
    content_enum = set(schema.get("content_type_enum") or [])
    slot_enum = set(schema.get("email_slot_enum") or [])

    for ctype, slot in defaults.items():
        if ctype not in content_enum:
            errors.append(f"ghl_email_slot_rules unknown content_type: {ctype}")
        if slot not in slot_enum:
            errors.append(f"ghl_email_slot_rules invalid email_slot for {ctype}: {slot}")

    for key in ("default_variant",):
        if key not in personas:
            errors.append(f"ghl_persona_variant_map missing {key}")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-dir",
        type=Path,
        default=REPO_ROOT / "config" / "marketing",
    )
    parser.add_argument(
        "--sample-feed",
        action="store_true",
        help="Build stillness_press sample feed and validate",
    )
    args = parser.parse_args()

    errors = validate_schema_config(args.config_dir)
    if args.sample_feed:
        from phoenix_v4.marketing.build_feed import build_marketing_feed, validate_feed

        feed = build_marketing_feed(brand_id="stillness_press", topics=["anxiety", "compassion_fatigue"])
        errors.extend(validate_feed(feed))
        if not errors:
            sample = (
                REPO_ROOT
                / "artifacts"
                / "marketing_feed"
                / "stillness_press"
                / "en_US"
                / feed["week"]
                / "marketing_feed.sample.json"
            )
            sample.parent.mkdir(parents=True, exist_ok=True)
            sample.write_text(json.dumps(feed, indent=2) + "\n", encoding="utf-8")

    if errors:
        for e in errors:
            print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
