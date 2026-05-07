#!/usr/bin/env python3
"""End-to-end V2 panel-prompt builder — Phase A.2 caller.

Reads:
    - chapter_script.yaml (the brand-2 schema: chapters[ch_id].panels[].scene
      + narration + dialogue + sfx; cognitive_clarity + future brands)
    - the series's character_design YAML (validated by the constraint solver
      from Phase A.1)

Emits:
    - panel_prompts.json compatible with queue_panel_renders.py (the V1
      brand-2 / cognitive_clarity schema: top-level brand/episode/model/
      render_target/prompts[])

Supersedes ad-hoc panel_prompts.json authoring. Brand-2 V1 ship at PR #923
used hand-authored panel prompts; this builder is the deterministic V2
replacement: same character_design + same drawing tradition + same
forbidden tokens → identical prompts every run.

Distinct from `scripts/manga/build_panel_prompts.py` which reads the older
v3 chapter_script_writer_handoff schema. The V2 builder reads the
brand-2/cognitive_clarity chapter_script schema and is the canonical
forward-looking path per cap entry MANGA-LAYERED-PIPELINE-V2-01 §A2.

Usage:
    python3 scripts/manga/build_panel_prompts_v2.py \\
        --chapter-script artifacts/manga/chapter_scripts/<series>/ep_001.yaml \\
        --character-design config/source_of_truth/manga_profiles/series/<series>.yaml \\
        --base-model flux_schnell \\
        --output artifacts/manga/panel_prompts/<series>/ep_001.panel_prompts.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.manga.character_individuation.prompt_builder import (  # noqa: E402
    build_prompt,
    load_builder_config,
)


def iter_panels(chapter_script: dict):
    """Brand-2 schema: chapters is a dict {ch01: {panels: [...]}}."""
    chapters = chapter_script.get("chapters") or {}
    if isinstance(chapters, dict):
        for ch_id in sorted(chapters.keys()):
            for p in chapters[ch_id].get("panels") or []:
                yield ch_id, p
    elif isinstance(chapters, list):
        for i, ch in enumerate(chapters):
            ch_id = ch.get("id") or f"ch{i+1:02d}"
            for p in ch.get("panels") or []:
                yield ch_id, p


def resolve_character_design(path: str | Path) -> dict:
    """Accept a series YAML carrying a character_design block, OR a raw
    character_design YAML."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"character_design source not found: {p}")
    data = yaml.safe_load(p.read_text()) or {}
    if "character_design" in data:
        cd = dict(data["character_design"])
        for fwd in ("market_demo", "genre_family", "secondary_genre", "brand_id", "series_id"):
            if fwd in data and fwd not in cd:
                cd[fwd] = data[fwd]
        return cd
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--chapter-script", required=True)
    ap.add_argument("--character-design", required=True,
                    help="Series YAML (with character_design block) OR raw character_design YAML")
    ap.add_argument("--base-model", default="flux_schnell",
                    choices=["flux_schnell", "qwen_image", "animagine_xl_4_0"])
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    cs_path = Path(args.chapter_script).resolve()
    chapter_script = yaml.safe_load(cs_path.read_text()) or {}

    character_design = resolve_character_design(args.character_design)

    primary_genre = (
        character_design.get("genre_family")
        or chapter_script.get("genre_family")
        or chapter_script.get("topic")
    )
    secondary_genre = (
        character_design.get("secondary_genre")
        or chapter_script.get("secondary_genre")
    )

    cfg = load_builder_config(
        base_model=args.base_model,
        width=args.width,
        height=args.height,
    )

    prompts: list[dict] = []
    for ch_id, panel in iter_panels(chapter_script):
        panel_id = panel.get("panel_id") or f"{ch_id}_p?"
        scene = panel.get("scene") or ""
        built = build_prompt(
            panel_id=panel_id,
            scene_description=scene,
            character_design=character_design,
            primary_genre=primary_genre,
            secondary_genre=secondary_genre,
            builder_config=cfg,
        )
        prompts.append(built.to_panel_prompt())

    output = {
        "schema_version": "1.0",
        "brand": chapter_script.get("brand"),
        "episode": Path(args.chapter_script).stem,
        "title": chapter_script.get("title"),
        "model": args.base_model,
        "render_target": f"{args.width}x{args.height} (webtoon vertical)",
        "locale_agnostic": True,
        "note": (
            "Generated by build_panel_prompts_v2.py (V2 Phase A.2). "
            "Imagery only — bubble_render composites locale-specific text."
        ),
        "prompts": prompts,
    }
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False))
    print(f"wrote {len(prompts)} panel prompts → {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
