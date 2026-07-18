#!/usr/bin/env python3
"""Plan panel layout — resolved structural plan envelope writer.

Builds a verified plan envelope via structural_composition.build_plan_envelope.
Writes into candidate quarantine plans/ when --candidate-root is set.

Usage:
  PYTHONPATH=scripts/manga python3 scripts/manga/plan_panel_layout.py \\
    --bundle path/to/structural_bundle.json \\
    [--panel-type-id dialogue_seated_table] \\
    [--out path/to/plan_envelope.json] \\
    [--candidate-root artifacts/manga/<series>/structural_candidates/<id>]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "manga"))

from structural_composition import (  # noqa: E402
    StructuralHardFail,
    build_plan_envelope,
    emit_support_overlay,
)


def load_bundle(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        import yaml
        return yaml.safe_load(text)
    return json.loads(text)


def write_plan(
    bundle: dict,
    *,
    panel_type_id: str | None,
    out: Path,
    emit_overlay: bool,
) -> dict:
    envelope = build_plan_envelope(bundle, panel_type_id=panel_type_id)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(envelope, indent=2) + "\n", encoding="utf-8")
    if emit_overlay:
        overlay_path = out.with_name(out.stem + "_support_overlay.png")
        emit_support_overlay(envelope, out_path=overlay_path)
    return envelope


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--bundle", type=Path, required=True)
    ap.add_argument("--panel-type-id", default=None)
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument(
        "--candidate-root",
        type=Path,
        default=None,
        help="If set, write under <root>/plans/ (quarantine routing)",
    )
    ap.add_argument("--emit-overlay", action="store_true")
    args = ap.parse_args(argv)

    try:
        bundle = load_bundle(args.bundle)
        if args.candidate_root:
            plans_dir = args.candidate_root / "plans"
            plans_dir.mkdir(parents=True, exist_ok=True)
            # Ensure quarantine siblings exist (enforced routing scaffold)
            for sub in (
                "structural_validation",
                "candidates",
                "visual_validation",
                "accepted",
                "rejected",
                "promotion_records",
            ):
                (args.candidate_root / sub).mkdir(parents=True, exist_ok=True)
            out = args.out or plans_dir / f"{bundle.get('panel_id', bundle.get('bundle_id', 'panel'))}_plan.json"
        else:
            out = args.out or Path(f"{bundle.get('panel_id', 'panel')}_plan.json")
        env = write_plan(
            bundle,
            panel_type_id=args.panel_type_id or bundle.get("panel_type_id"),
            out=out,
            emit_overlay=args.emit_overlay,
        )
        print(json.dumps({
            "ok": True,
            "out": str(out),
            "plan_hash": env["plan_hash"],
            "structural_template_id": env["structural_template_id"],
            "panel_type_id": env.get("panel_type_id"),
        }, indent=2))
        return 0
    except StructuralHardFail as e:
        print(json.dumps({"ok": False, "code": e.code, "error": str(e)}, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
