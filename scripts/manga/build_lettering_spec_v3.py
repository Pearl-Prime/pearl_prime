#!/usr/bin/env python3
"""Build a v3 lettering_spec directly from a v3 chapter_script.

The V2 ``build_lettering_spec_from_chapter_script`` in
``phoenix_v4.manga.chapter.lettering_from_script`` reads flat ``dialogue``,
``sfx``, ``narrator_caption`` fields. V3 chapter_scripts use ``dialogue_lines``
with ``text_by_locale`` + ``sfx_by_locale`` + ``narrator_caption_by_locale``.

This builder reads the V3 structure directly and emits a v3 lettering_spec
that the bubble renderer + locale_resolver understand natively.

Output schema (v3.0.0):
    {
      "schema_version": "3.0.0",
      "artifact_type": "lettering_spec",
      "default_locale": "en_US",
      "available_locales": [...],
      "lettering_panels": [
        {
          "panel_id": "...",
          "silence_confirmed": bool,
          "dialogue_lines": [
            {
              "speaker": "...",
              "text_by_locale": {...},
              "intensity": "...",
              "bubble_style": "...",
              "tail_style": "...",
              "position_hint": "...",
              "font_override_by_locale": {...},
              "emotion": "...",
              "speech_atom_id": ...
            }
          ],
          "sfx_by_locale": {...},
          "narrator_caption_by_locale": {...},
          "estimated_bubble_coverage": null
        }
      ]
    }
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml

# ── intensity → bubble + tail defaults (mirrors lettering_from_script v2) ──
_INTENSITY_TO_BUBBLE: dict[str, str] = {
    "whisper": "whisper_dashed",
    "calm": "round_normal",
    "normal": "round_normal",
    "excited": "spiky_emphasis",
    "shouting": "spiky_emphasis",
    "screaming": "scream_ultra",
    "internal": "cloud_thought",
}
_INTENSITY_TO_TAIL: dict[str, str] = {
    "whisper": "tapered",
    "calm": "standard",
    "normal": "standard",
    "excited": "spiked",
    "shouting": "spiked",
    "screaming": "burst",
    "internal": "none",
}
_DEFAULT_POSITIONS = ["top_right", "top_left", "bottom_right", "bottom_left"]


def _build_dialogue_line(item: Mapping[str, Any], idx: int) -> dict | None:
    """Convert one v3 dialogue_line entry to lettering_spec shape."""
    text_by_locale = item.get("text_by_locale") or {}
    if not isinstance(text_by_locale, dict):
        return None
    # Any non-empty text in ANY locale -> emit the line.
    if not any(str(v or "").strip() for v in text_by_locale.values()):
        return None

    intensity = str(item.get("intensity") or "normal").lower()
    if intensity not in _INTENSITY_TO_BUBBLE:
        intensity = "normal"

    return {
        "speaker": str(item.get("speaker") or f"speaker_{idx + 1}"),
        "text_by_locale": dict(text_by_locale),
        "emotion": str(item.get("emotion") or "neutral"),
        "intensity": intensity,
        "bubble_style": str(item.get("bubble_style") or _INTENSITY_TO_BUBBLE[intensity]),
        "tail_style": str(item.get("tail_style") or _INTENSITY_TO_TAIL[intensity]),
        "position_hint": str(item.get("position_hint") or _DEFAULT_POSITIONS[idx % 4]),
        "font_override_by_locale": item.get("font_override_by_locale") or {},
        "speech_atom_id": item.get("speech_atom_id"),
    }


def _iter_panels(chapter_script: Mapping[str, Any]):
    """Yield panel dicts in chapter order from a V3 chapter_script."""
    for page in chapter_script.get("pages") or []:
        for panel in page.get("panels") or []:
            yield panel


def build_lettering_spec_v3(chapter_script: Mapping[str, Any]) -> dict[str, Any]:
    """Produce a v3 lettering_spec from a v3 chapter_script."""
    default_locale = str(chapter_script.get("default_locale") or "en_US")
    available_locales = list(chapter_script.get("available_locales") or [default_locale])

    lettering_panels: list[dict[str, Any]] = []
    for idx, panel in enumerate(_iter_panels(chapter_script)):
        pid = str(panel.get("panel_id") or "").strip()
        if not pid:
            raise ValueError(f"panel #{idx} missing panel_id")

        # Dialogue lines (v3)
        v3_dialogue = panel.get("dialogue_lines") or []
        dlg_out: list[dict[str, Any]] = []
        for i, item in enumerate(v3_dialogue):
            if isinstance(item, Mapping):
                line = _build_dialogue_line(item, i)
                if line is not None:
                    dlg_out.append(line)

        # SFX (v3 by_locale; carry through)
        sfx_v3 = panel.get("sfx_by_locale") or {}
        if not isinstance(sfx_v3, dict):
            sfx_v3 = {}
        # Normalize each value to list[str]
        sfx_by_locale: dict[str, list[str]] = {}
        for loc, v in sfx_v3.items():
            if isinstance(v, list):
                sfx_by_locale[str(loc)] = [str(s) for s in v if s and str(s).strip()]
            elif isinstance(v, str) and v.strip():
                sfx_by_locale[str(loc)] = [v.strip()]

        # Narrator caption (v3 by_locale; carry through)
        cap_v3 = panel.get("narrator_caption_by_locale") or {}
        if not isinstance(cap_v3, dict):
            cap_v3 = {}
        narrator_caption_by_locale = {
            str(loc): str(v) for loc, v in cap_v3.items() if v and str(v).strip()
        }

        # Silence: True iff no dialogue text in any locale, no sfx in any locale,
        # no narrator caption in any locale, AND chapter_script doesn't explicitly
        # set silence_confirmed=false.
        has_dialogue = bool(dlg_out)
        has_sfx = any(sfx_by_locale.values())
        has_caption = bool(narrator_caption_by_locale)
        script_silent = panel.get("silence_confirmed")
        if script_silent is True and not (has_dialogue or has_sfx or has_caption):
            silence = True
        elif script_silent is False:
            silence = False
        else:
            silence = not (has_dialogue or has_sfx or has_caption)

        lettering_panels.append({
            "panel_id": pid,
            "silence_confirmed": silence,
            "dialogue_lines": dlg_out,
            "sfx_by_locale": sfx_by_locale,
            "narrator_caption_by_locale": narrator_caption_by_locale,
            "estimated_bubble_coverage": None,
        })

    return {
        "schema_version": "3.0.0",
        "artifact_type": "lettering_spec",
        "default_locale": default_locale,
        "available_locales": available_locales,
        "series_id": chapter_script.get("series_id"),
        "chapter_id": chapter_script.get("chapter_id"),
        "lettering_panels": lettering_panels,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Build v3 lettering_spec from v3 chapter_script.")
    ap.add_argument("--chapter-script", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args(argv)

    if not args.chapter_script.is_file():
        print(f"ERROR: chapter_script not found: {args.chapter_script}", file=sys.stderr)
        return 2

    chapter_script = yaml.safe_load(args.chapter_script.read_text())
    spec = build_lettering_spec_v3(chapter_script)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(spec, indent=2, ensure_ascii=False))
    n_panels = len(spec["lettering_panels"])
    n_silent = sum(1 for p in spec["lettering_panels"] if p["silence_confirmed"])
    n_with_dialogue = sum(1 for p in spec["lettering_panels"] if p["dialogue_lines"])
    print(f"wrote {args.output}")
    print(f"  panels={n_panels}, silent={n_silent}, with_dialogue={n_with_dialogue}, default_locale={spec['default_locale']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
