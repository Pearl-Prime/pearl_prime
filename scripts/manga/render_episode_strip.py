#!/usr/bin/env python3
"""Bridge: brand-2 chapter_script.yaml + panel renders → bubbled panels per
locale → manifest ready for webtoon_compose.

V1 baseline. Sensible heuristic defaults for bubble_style / intensity /
position_hint per the cognitive_clarity__/HANDOFF.md V1 spec. V2 layered
pipeline (LoRA + IP-Adapter + cookbook) replaces the heuristics with
genre-aware lettering per docs/MANGA_LAYERED_PIPELINE_V2_SCOPE.md.

Schema bridge:
    chapter_script.yaml has chapters → panels → narration{locale} +
    dialogue[].text{locale}. bubble_render expects per-line dict with
    ``text`` (string, already locale-resolved) plus intensity/bubble_style
    /position_hint metadata. This bridge resolves locale and applies
    defaults; no synthetic fields beyond what bubble_render documents.

Usage:
    python3 scripts/manga/render_episode_strip.py \\
      --chapter-script artifacts/manga/chapter_scripts/<series>/ep_001.yaml \\
      --panels-dir   artifacts/manga/panel_renders/<series>/ep_001/ \\
      --locale en-US \\
      --output-dir  artifacts/manga/episodes/<series>/ep_001_en-US_panels/

Locales accepted in either ``en-US`` (chapter_script convention) or
``en_US`` (bubble_render convention) form; converted internally.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from phoenix_v4.manga.chapter.bubble_render import render_bubbles_onto_panel  # noqa: E402


def _normalise_locale(loc: str) -> tuple[str, str]:
    """Return (chapter-script form 'en-US', bubble-render form 'en_US')."""
    dashed = loc.replace("_", "-")
    underscored = loc.replace("-", "_")
    return dashed, underscored


def _intensity_for(text: str, kind: str) -> str:
    if kind == "narration":
        return "whisper"
    if not text:
        return "normal"
    bangs = text.count("!")
    if bangs >= 2:
        return "screaming"
    if bangs == 1:
        return "excited"
    return "normal"


def _bubble_style_for(intensity: str, kind: str) -> str:
    if kind == "narration":
        return "square_narration"
    return {
        "screaming": "scream_ultra",
        "excited": "spiky_emphasis",
    }.get(intensity, "round_normal")


_DIALOGUE_POSITIONS = ["bottom_left", "bottom_right", "top_right", "center_left"]


def _build_dialogue_lines(panel: dict, locale_dashed: str) -> list[dict]:
    out: list[dict] = []
    for i, line in enumerate(panel.get("dialogue") or []):
        text_block = line.get("text") or {}
        if isinstance(text_block, dict):
            text = text_block.get(locale_dashed) or text_block.get("en-US") or ""
        else:
            text = str(text_block or "")
        text = text.strip()
        if not text:
            continue
        intensity = _intensity_for(text, "dialogue")
        out.append({
            "text": text,
            "intensity": intensity,
            "bubble_style": _bubble_style_for(intensity, "dialogue"),
            "position_hint": _DIALOGUE_POSITIONS[i % len(_DIALOGUE_POSITIONS)],
            "tail_style": "pointer",
            "speaker": line.get("speaker") or f"speaker_{i}",
        })
    return out


def _resolve_narration(panel: dict, locale_dashed: str) -> str | None:
    block = panel.get("narration") or {}
    if isinstance(block, dict):
        return (block.get(locale_dashed) or block.get("en-US") or "").strip() or None
    return str(block or "").strip() or None


def _resolve_sfx(panel: dict, locale_dashed: str) -> list[str]:
    """SFX in brand-2 schema is list of {placement, text:{locale}} dicts.
    bubble_render expects list[str] already locale-resolved. Strip dashes
    used as silent placeholders (operator convention)."""
    out: list[str] = []
    for s in panel.get("sfx") or []:
        if isinstance(s, str):
            txt = s.strip()
        elif isinstance(s, dict):
            block = s.get("text") or {}
            if isinstance(block, dict):
                txt = (block.get(locale_dashed) or block.get("en-US") or "").strip()
            else:
                txt = str(block or "").strip()
        else:
            txt = ""
        if txt and txt not in {"-", "—", "——"}:
            out.append(txt)
    return out


def _iter_panels(chapter_script: dict):
    chapters = chapter_script.get("chapters") or {}
    if isinstance(chapters, list):
        for ch in chapters:
            for p in ch.get("panels") or []:
                yield p
    else:
        for ch_id in sorted(chapters.keys()):
            for p in chapters[ch_id].get("panels") or []:
                yield p


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--chapter-script", required=True)
    ap.add_argument("--panels-dir", required=True, help="Directory of <panel_id>.png renders")
    ap.add_argument("--locale", required=True, help="e.g. en-US or ja-JP")
    ap.add_argument("--output-dir", required=True)
    ap.add_argument("--manifest-out", default=None, help="Optional manifest JSON path; defaults to <output-dir>/panel_images_manifest.json")
    args = ap.parse_args()

    locale_dashed, locale_underscored = _normalise_locale(args.locale)
    cs_path = Path(args.chapter_script).resolve()
    panels_dir = Path(args.panels_dir).resolve()
    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    chapter_script = yaml.safe_load(cs_path.read_text())

    manifest_panels: list[dict] = []
    n_done = 0
    n_silent = 0
    for panel in _iter_panels(chapter_script):
        pid = panel["panel_id"]
        src = panels_dir / f"{pid}.png"
        if not src.is_file():
            print(f"  SKIP {pid}: no render at {src}", file=sys.stderr)
            continue

        narration = _resolve_narration(panel, locale_dashed)
        dialogue_lines = _build_dialogue_lines(panel, locale_dashed)
        sfx = _resolve_sfx(panel, locale_dashed)

        out_path = out_dir / f"{pid}.png"

        if not narration and not dialogue_lines and not sfx:
            # Silent panel — copy through (bubble_render would no-op anyway).
            out_path.write_bytes(src.read_bytes())
            n_silent += 1
        else:
            render_bubbles_onto_panel(
                src,
                dialogue_lines,
                sfx,
                narration,
                out_path=out_path,
                locale=locale_underscored,
                default_locale="en_US",
            )
            n_done += 1

        manifest_panels.append({
            "panel_id": pid,
            "path": str(out_path),
            "status": "ok",
            "beat_type": panel.get("beat_type") or "spatial",
        })

    manifest = {
        "schema_version": "1.0.0",
        "locale": locale_underscored,
        "panels": manifest_panels,
    }
    manifest_path = Path(args.manifest_out) if args.manifest_out else out_dir / "panel_images_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"  bubbled: {n_done}, silent-pass: {n_silent}, total: {len(manifest_panels)}", file=sys.stderr)
    print(f"  manifest: {manifest_path}", file=sys.stderr)
    return 0 if manifest_panels else 1


if __name__ == "__main__":
    raise SystemExit(main())
