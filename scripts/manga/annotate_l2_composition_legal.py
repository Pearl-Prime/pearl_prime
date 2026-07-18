#!/usr/bin/env python3
"""Annotate L2 composition.json legality extension fields (HR rules §10).

Writes/updates:
  abstract_stage_eligible, room_capable, scene_contamination,
  requires_occluder, pose_context (when missing)

Does not invent crop_class / camera / light — those must already exist or be
supplied via --infer-crop-from-name. Fail-closed when required base fields absent.

Usage:
  PYTHONPATH=scripts/manga python3 scripts/manga/annotate_l2_composition_legal.py \\
    --l2-dir artifacts/manga/<series>/v4_render_cache/ep_001/L2 \\
    [--dry-run] [--write]

Provenance: authored from HR rules §10 L2 legality extensions; module was GOVERNED
in rules artifact but never present in git history.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOM_CAPABLE_CROPS = frozenset({"full_figure", "knees_up", "thigh_up"})
ABSTRACT_STAGE_CROPS = frozenset({"bust", "waist_up", "face_cu"})
HANDS_CROPS = frozenset({"ecu_fragment", "hands"})

NAME_CROP_HINTS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"full_figure|standing", re.I), "full_figure"),
    (re.compile(r"knees_up|seated", re.I), "knees_up"),
    (re.compile(r"thigh", re.I), "thigh_up"),
    (re.compile(r"waist", re.I), "waist_up"),
    (re.compile(r"bust|clean_bust", re.I), "bust"),
    (re.compile(r"face|portrait", re.I), "face_cu"),
    (re.compile(r"hands|cup|insert", re.I), "hands"),
]


def infer_crop_from_name(name: str) -> str | None:
    for pat, crop in NAME_CROP_HINTS:
        if pat.search(name):
            return crop
    return None


def legality_fields(crop_class: str, *, asset_name: str = "") -> dict[str, Any]:
    room = crop_class in ROOM_CAPABLE_CROPS
    abstract = crop_class in ABSTRACT_STAGE_CROPS
    hands = crop_class in HANDS_CROPS or "hands" in asset_name.lower()
    return {
        "abstract_stage_eligible": bool(abstract or hands),
        "room_capable": bool(room),
        "scene_contamination": False,
        "requires_occluder": bool(crop_class in ("knees_up", "thigh_up") and room),
        "pose_context": (
            "hands_insert" if hands
            else "seated" if "seat" in asset_name.lower() or crop_class == "knees_up"
            else "standing" if crop_class == "full_figure"
            else "portrait" if abstract
            else "unknown"
        ),
    }


def annotate_file(
    png: Path,
    *,
    dry_run: bool,
    infer_crop: bool,
    force: bool,
) -> dict[str, Any]:
    side = Path(str(png).removesuffix(".png") + ".composition.json")
    report: dict[str, Any] = {"png": str(png), "sidecar": str(side), "action": "skip"}
    if not side.is_file():
        if not infer_crop:
            report["action"] = "missing_sidecar"
            report["error"] = "no composition.json and --infer-crop-from-name not set"
            return report
        crop = infer_crop_from_name(png.name)
        if not crop:
            report["action"] = "missing_sidecar"
            report["error"] = "cannot infer crop_class from name"
            return report
        meta: dict[str, Any] = {
            "schema_version": "1.0.0",
            "asset_id": png.stem.replace("_alpha", ""),
            "layer_class": "L2",
            "crop_class": crop,
        }
    else:
        meta = json.loads(side.read_text())
        crop = meta.get("crop_class")
        if not crop and infer_crop:
            crop = infer_crop_from_name(png.name)
            if crop:
                meta["crop_class"] = crop
        if not crop:
            report["action"] = "missing_crop_class"
            report["error"] = "crop_class required"
            return report

    fields = legality_fields(str(crop), asset_name=png.name)
    changed = False
    for k, v in fields.items():
        if force or k not in meta or meta.get(k) is None:
            if meta.get(k) != v:
                meta[k] = v
                changed = True
    report["fields"] = {k: meta.get(k) for k in fields}
    if not changed:
        report["action"] = "unchanged"
        return report
    report["action"] = "would_write" if dry_run else "wrote"
    if not dry_run:
        side.parent.mkdir(parents=True, exist_ok=True)
        side.write_text(json.dumps(meta, indent=2) + "\n")
    return report


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--l2-dir", type=Path, required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--write", action="store_true", help="persist sidecar updates")
    ap.add_argument("--infer-crop-from-name", action="store_true")
    ap.add_argument("--force", action="store_true", help="overwrite existing legality fields")
    ap.add_argument("--glob", default="*_alpha.png")
    args = ap.parse_args(argv)
    if not args.write:
        args.dry_run = True
    l2_dir = args.l2_dir
    if not l2_dir.is_dir():
        print(f"ERROR: not a directory: {l2_dir}", file=sys.stderr)
        return 2
    reports = []
    for png in sorted(l2_dir.glob(args.glob)):
        reports.append(
            annotate_file(
                png,
                dry_run=args.dry_run,
                infer_crop=args.infer_crop_from_name,
                force=args.force,
            )
        )
    wrote = sum(1 for r in reports if r["action"] in ("wrote", "would_write"))
    errors = [r for r in reports if r.get("error")]
    print(json.dumps({
        "scanned": len(reports),
        "changed": wrote,
        "errors": len(errors),
        "reports": reports,
    }, indent=2))
    return 1 if errors and not wrote else 0


if __name__ == "__main__":
    raise SystemExit(main())
