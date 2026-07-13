#!/usr/bin/env python3
"""Validate structural template registry and panel-type bridge coverage."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
TEMPLATES = REPO / "config" / "manga" / "structural_templates.yaml"
BRIDGE = REPO / "config" / "manga" / "panel_type_structural_bridge.yaml"
REQUIRED = {
    "standing_room_scene",
    "seated_table_scene",
    "closeup_subject_scene",
    "prop_insert_scene",
    "two_character_dialogue_scene",
    "action_impact_scene",
    "symbolic_metaphor_scene",
    "establishing_environment_scene",
}


def validate_coverage(template_path: Path = TEMPLATES, bridge_path: Path = BRIDGE) -> dict[str, Any]:
    templates_doc = yaml.safe_load(template_path.read_text(encoding="utf-8")) or {}
    bridge_doc = yaml.safe_load(bridge_path.read_text(encoding="utf-8")) or {}
    templates = templates_doc.get("templates") or {}
    mappings = bridge_doc.get("mappings") or {}
    failures: list[str] = []
    missing = sorted(REQUIRED - set(templates))
    if missing:
        failures.append(f"missing templates: {missing}")
    for template_id, row in templates.items():
        for key in (
            "story_purpose", "allowed_layers", "default_transform",
            "required_support_proof", "allowed_relations", "required_nodes", "fail_modes",
        ):
            if key not in row:
                failures.append(f"{template_id}: missing {key}")
    mapped_templates = {str(row.get("structural_template_id")) for row in mappings.values()}
    unmapped = sorted(REQUIRED - mapped_templates)
    if unmapped:
        failures.append(f"templates without panel-type bridge: {unmapped}")
    return {
        "passed": not failures,
        "manga-structural-template-count": len(templates),
        "manga-panel-type-coverage": "green" if not failures else "partial",
        "unsupported-panel-types": [],
        "failures": failures,
        "overall-manga-green": "NOT_PROVEN",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--templates", type=Path, default=TEMPLATES)
    parser.add_argument("--bridge", type=Path, default=BRIDGE)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    report = validate_coverage(args.templates, args.bridge)
    text = json.dumps(report, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if report["passed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
