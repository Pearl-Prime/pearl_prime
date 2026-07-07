#!/usr/bin/env python3
"""Build beats JSON for manga blind-10 Qwen2.5-VL pre-screen.

Output is consumed by scripts/video/run_frame_judge.py --beats (Tier 2 only).
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[4]

SLOTS = {
    "01": {
        "series_id": "stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying",
        "episode": "ep_001",
        "panel_dir": REPO
        / "artifacts/manga/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/composed_v3_qwen",
        "panel_glob": "ep_001_seg_*.jpg",
        "script": REPO
        / "artifacts/manga/chapter_scripts/stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying/ep_001.yaml",
    },
}


def _iter_panels(script: dict) -> list[dict]:
    panels: list[dict] = []
    if "panels" in script:
        panels.extend(script["panels"])
    for page in script.get("pages") or []:
        panels.extend(page.get("panels") or [])
    return panels


def _panel_scene_text(panel: dict) -> str:
    for key in ("scene", "scene_description", "visual_description", "description", "summary"):
        val = panel.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def build_beats(slot: str) -> list[dict]:
    cfg = SLOTS[slot]
    script = yaml.safe_load(cfg["script"].read_text(encoding="utf-8"))
    meta_panels = _iter_panels(script)

    beats: list[dict] = []
    for img in sorted(cfg["panel_dir"].glob(cfg["panel_glob"])):
        m = re.search(r"seg_(\d+)", img.name)
        if not m:
            continue
        seg = int(m.group(1))
        meta = meta_panels[seg - 1] if seg - 1 < len(meta_panels) else {}
        beats.append(
            {
                "id": f"slot{slot}_seg_{seg:03d}",
                "image": str(img),
                "scene_description": _panel_scene_text(meta) or f"Panel {seg} scene",
                "prompt": meta.get("render_prompt", "") or "",
                "segment": seg,
            }
        )
    return beats


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--slot", required=True, choices=sorted(SLOTS))
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    beats = build_beats(args.slot)
    if not beats:
        raise SystemExit(f"No beats built for slot {args.slot}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {"beats": beats, "slot": args.slot, "count": len(beats)}
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(beats)} beats → {args.output}")


if __name__ == "__main__":
    main()
