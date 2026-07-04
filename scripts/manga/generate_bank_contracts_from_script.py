#!/usr/bin/env python3
"""Generate bank-contract inventory stubs from an M3 chapter_script ep_001.

Mechanical procedure for the remaining M3 flagship series (after the 3-pilot
M5-prep set). Reads panel `scene` text, emits minimal scene/object/pose
inventory YAMLs under artifacts/manga/<series_id>/bank_contracts/.

Does NOT invent art — only the contract. REAL layers require Pearl Star.

Usage:
    PYTHONPATH=. python3 scripts/manga/generate_bank_contracts_from_script.py \
        --chapter-script artifacts/manga/<series>/ep_001.yaml
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter-script", type=Path, required=True)
    args = ap.parse_args()
    data = yaml.safe_load(args.chapter_script.read_text())
    series_id = data["series_id"]
    brand_id = data.get("brand_id", series_id.split("__")[0])
    genre = data.get("genre", "iyashikei")
    # Crude scene buckets from first words of panel scenes
    scenes, objects, poses = [], [], []
    for page in data.get("pages") or []:
        for panel in page.get("panels") or []:
            scene = str(panel.get("scene") or "")
            words = re.findall(r"[A-Za-z]{4,}", scene)[:4]
            if words:
                sid = "_".join(w.lower() for w in words[:3])
                if sid and sid not in {s[0] for s in scenes}:
                    scenes.append((sid, scene[:200]))
            if "hand" in scene.lower() or "cup" in scene.lower() or "phone" in scene.lower():
                oid = "prop_" + str(len(objects))
                objects.append((oid, scene[:120]))
            if panel.get("dialogue_lines") or "face" in scene.lower():
                poses.append((f"pose_{len(poses)}", "Character pose derived from panel"))
    # Floor: at least 2 of each (Q-M5P-02 contract minimum)
    while len(scenes) < 2:
        scenes.append((f"scene_{len(scenes)}", "TODO: author from script"))
    while len(objects) < 2:
        objects.append((f"object_{len(objects)}", "TODO: author from script"))
    while len(poses) < 2:
        poses.append((f"pose_{len(poses)}", "TODO: author from script"))

    out = REPO / "artifacts" / "manga" / series_id / "bank_contracts"
    out.mkdir(parents=True, exist_ok=True)
    for kind, key, idk, items in (
        ("scene_inventory", "scenes", "scene_id", scenes[:8]),
        ("object_inventory", "objects", "object_id", objects[:8]),
        ("character_pose_inventory", "poses", "pose_id", poses[:8]),
    ):
        doc = {
            "schema_version": "1.0.0",
            "series_id": series_id,
            "brand_id": brand_id,
            "genre": genre,
            "m5_prep": True,
            "generated_from": str(args.chapter_script),
            key: [{idk: i, "description": d, "status": "specced_awaiting_gpu",
                   "render_resolution": [1080, 1920]} for i, d in items],
        }
        (out / f"{kind}.yaml").write_text(
            yaml.safe_dump(doc, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )
        print("wrote", out / f"{kind}.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
