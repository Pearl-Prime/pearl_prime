#!/usr/bin/env python3
"""V3.1 Phase F+G driver: bubble + compose all 10 episodes.

For each episode:
  Phase F (bubble): if chapter_script exists → build v3 lettering_spec, render
    bubbles onto panels via phoenix_v4.manga.chapter.bubble_render. If no
    chapter_script → mark all panels silent (no bubbles applied; manifest still
    points at the raw panel PNG).
  Phase G (compose): call webtoon_compose.compose_episode_strips() to stack
    panels vertically with beat-type gutters, downsample to 800px, slice into
    JPEG segments ≤ 1280px tall.

Output:
  artifacts/manga/<series>/lettering_v3_qwen/<ep>.lettering_spec.json
  artifacts/manga/<series>/bubbled_v3_qwen/<ep>/<panel_id>_bubbled.png  (where bubbles applied)
  artifacts/manga/<series>/composed_v3_qwen/<ep>_seg_NNN.jpg
"""
from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from phoenix_v4.manga.chapter.bubble_render import render_bubbles_on_panels  # noqa: E402
from phoenix_v4.manga.chapter.webtoon_compose import compose_episode_strips  # noqa: E402

sys.path.insert(0, str(REPO / "scripts" / "manga"))
import build_lettering_spec_v3 as lsv3  # noqa: E402


def _silent_lettering_spec(panel_ids: list[str]) -> dict[str, Any]:
    """When chapter_script is missing, mark all panels silent."""
    return {
        "schema_version": "3.0.0",
        "artifact_type": "lettering_spec",
        "default_locale": "en_US",
        "available_locales": ["en_US"],
        "lettering_panels": [
            {
                "panel_id": pid,
                "silence_confirmed": True,
                "dialogue_lines": [],
                "sfx_by_locale": {},
                "narrator_caption_by_locale": {},
                "estimated_bubble_coverage": None,
            }
            for pid in panel_ids
        ],
    }


def _stub_chapter_script(series_id: str, episode_id: str, panel_ids: list[str]) -> dict[str, Any]:
    """Minimal chapter_script when none exists; needed by render_bubbles_on_panels
    to know panel ordering + beat_types. Beat_types default to micro for silent
    panels (smallest gutter = 40px); standard for the first panel of an episode
    so compose_episode_strips treats it as scene-opener."""
    panels = []
    for i, pid in enumerate(panel_ids):
        panels.append({
            "panel_id": pid,
            "beat_type": "standard" if i == 0 else "micro",
            "silence_confirmed": True,
        })
    return {
        "schema_version": "1.0.0",
        "artifact_type": "chapter_script_writer_handoff",
        "series_id": series_id,
        "chapter_id": episode_id,
        "default_locale": "en_US",
        "available_locales": ["en_US"],
        "pages": [{"page_id": f"{episode_id}_p01", "panels": panels}],
    }


def _build_panel_images_manifest(
    series_id: str,
    episode_id: str,
    panels_dir: Path,
    panel_ids: list[str],
) -> dict[str, Any]:
    """Construct panel_images_manifest pointing at panels_v3_qwen/ep_X/*.png."""
    panels = []
    for pid in panel_ids:
        img_path = panels_dir / f"{pid}.png"
        if not img_path.is_file() or img_path.stat().st_size == 0:
            panels.append({"panel_id": pid, "status": "missing", "path": str(img_path)})
            continue
        panels.append({
            "panel_id": pid,
            "status": "ok",
            "path": str(img_path),
            "engine": "qwen_image_no_pulid",
        })
    return {
        "schema_version": "1.0.0",
        "artifact_type": "panel_images_manifest",
        "series_id": series_id,
        "chapter_id": episode_id,
        "panels": panels,
    }


def _panel_ids_for_episode(prompts_path: Path, panels_dir: Path) -> list[str]:
    """Source the panel_id list from panel_prompts_v3 (canonical ordering)."""
    if prompts_path.is_file():
        data = json.loads(prompts_path.read_text())
        return [p["panel_id"] for p in data.get("prompts", [])]
    # Fallback: sort PNGs by name
    return sorted(p.stem for p in panels_dir.glob("*.png") if p.stat().st_size > 0)


def run_episode(
    series_id: str,
    episode_id: str,
    chapter_script_path: Path,
    prompts_path: Path,
    panels_dir: Path,
    bubbled_out_dir: Path,
    composed_out_dir: Path,
    lettering_spec_path: Path,
    locale: str = "en_US",
) -> dict[str, Any]:
    """Build lettering_spec → bubble_render → compose_episode_strips for one episode."""
    panel_ids = _panel_ids_for_episode(prompts_path, panels_dir)
    if not panel_ids:
        return {"episode_id": episode_id, "status": "skip", "reason": "no panels"}

    # Phase F: lettering + bubble
    if chapter_script_path.is_file():
        chapter_script = yaml.safe_load(chapter_script_path.read_text())
        lettering_spec = lsv3.build_lettering_spec_v3(chapter_script)
        source = "chapter_script"
    else:
        chapter_script = _stub_chapter_script(series_id, episode_id, panel_ids)
        lettering_spec = _silent_lettering_spec(panel_ids)
        source = "silent_stub"

    lettering_spec_path.parent.mkdir(parents=True, exist_ok=True)
    lettering_spec_path.write_text(json.dumps(lettering_spec, indent=2, ensure_ascii=False))

    manifest = _build_panel_images_manifest(series_id, episode_id, panels_dir, panel_ids)

    bubbled_out_dir.mkdir(parents=True, exist_ok=True)
    updated_manifest = render_bubbles_on_panels(
        chapter_script=chapter_script,
        lettering_spec=lettering_spec,
        panel_images_manifest=manifest,
        bubble_style_config=None,
        out_dir=bubbled_out_dir,
        locale=locale,
    )
    n_bubbled = sum(
        1 for p in updated_manifest.get("panels", [])
        if "_bubbled" in str(p.get("path", ""))
    )

    # Phase G: compose
    composed_out_dir.mkdir(parents=True, exist_ok=True)
    payload = compose_episode_strips(
        chapter_script=chapter_script,
        panel_images_manifest=updated_manifest,
        out_dir=composed_out_dir,
        episode_id=episode_id,           # critical: defaults to "ep_001" else all episodes collide
    )

    n_segments = len(payload.get("segments", []))
    return {
        "episode_id": episode_id,
        "status": "ok",
        "lettering_source": source,
        "panels": len(panel_ids),
        "panels_bubbled": n_bubbled,
        "segments": n_segments,
        "total_bytes": payload.get("total_bytes"),
        "caps_check": payload.get("caps_check"),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series-id", default="stillness_press__ahjan__en_US__anxiety__the_alarm_is_lying")
    ap.add_argument("--prompts-base", type=Path,
                    default=REPO / "artifacts/manga/panel_prompts_v3")
    ap.add_argument("--chapter-scripts-base", type=Path,
                    default=REPO / "artifacts/manga/chapter_scripts")
    ap.add_argument("--panels-base", type=Path,
                    default=REPO / "artifacts/manga")
    ap.add_argument("--panels-subdir", default="panels_v3_qwen",
                    help="subdir under <panels-base>/<series_id>/ holding rendered panels")
    ap.add_argument("--out-lettering", type=Path,
                    default=REPO / "artifacts/manga")
    ap.add_argument("--out-bubbled", type=Path,
                    default=REPO / "artifacts/manga")
    ap.add_argument("--out-composed", type=Path,
                    default=REPO / "artifacts/manga")
    ap.add_argument("--locale", default="en_US")
    ap.add_argument("--episodes", nargs="*",
                    default=["ep_001", "ep_002", "ep_003", "ep_004", "ep_005",
                             "ep_006", "ep_007", "ep_008", "ep_009", "ep_010"])
    args = ap.parse_args(argv)

    results = []
    for ep in args.episodes:
        chapter_script_path = args.chapter_scripts_base / args.series_id / f"{ep}.yaml"
        prompts_path = args.prompts_base / args.series_id / f"{ep}.panel_prompts.json"
        panels_dir = args.panels_base / args.series_id / args.panels_subdir / ep
        lettering_spec_path = args.out_lettering / args.series_id / "lettering_v3_qwen" / f"{ep}.lettering_spec.json"
        bubbled_out_dir = args.out_bubbled / args.series_id / "bubbled_v3_qwen" / ep
        composed_out_dir = args.out_composed / args.series_id / "composed_v3_qwen"

        print(f"=== {ep} ===")
        try:
            result = run_episode(
                series_id=args.series_id,
                episode_id=ep,
                chapter_script_path=chapter_script_path,
                prompts_path=prompts_path,
                panels_dir=panels_dir,
                bubbled_out_dir=bubbled_out_dir,
                composed_out_dir=composed_out_dir,
                lettering_spec_path=lettering_spec_path,
                locale=args.locale,
            )
        except Exception as e:
            result = {"episode_id": ep, "status": "error", "error": str(e)}
            import traceback
            traceback.print_exc()
        results.append(result)
        print(f"  result: {result}")

    summary_path = args.out_composed / args.series_id / "composed_v3_qwen" / "_run_summary.json"
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nsummary: {summary_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
