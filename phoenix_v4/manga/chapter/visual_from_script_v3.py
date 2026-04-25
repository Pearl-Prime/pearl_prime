"""Compile a v3 chapter_script_writer_handoff into panel_prompts ready for
FLUX-schnell-fp8 on Pearl Star.

Diverges from ``visual_from_script.py`` (v1/v2 path that uses atom-derived
prompts) because v3 chapter scripts (PR #651) carry hand-authored ``scene``
descriptions that ARE the FLUX prompt — they don't need atom-based
synthesis. This module instead:

1. Reads each panel's ``scene`` field (the visual description)
2. Prepends per-series style anchoring (palette + character lock-in + voice)
3. Appends composition cues + style tail (cozy_iyashikei, dappled light, etc.)
4. Builds a uniform negative prompt
5. Emits a panel_prompts artifact one entry per panel

Output is FLUX-schnell-fp8 ready: positive prompt ≤512 tokens, negative
prompt locked to anti-AI-look + anti-mismatched-character recipe per
PR #631 R-8 mitigation.

The same prompt set serves ALL locales — text is composed at compose-time
by bubble_render (PR #648), not baked into the render. Render is locale-
independent (PR #631 Decision 1).

Public API:
    compile_v3_panel_prompts(chapter_script: dict, *, style_overrides: dict | None = None)
        -> dict (artifact_type=panel_prompts)
"""
from __future__ import annotations

from typing import Any, Mapping

# ─── Style anchoring per visual style tag ──────────────────────────────────
# Drawn from PR #631 master reference + therapeutic-craft companion + the
# style column in MANGA_FULL_CATALOG_PLAN.md.

_STYLE_ANCHORS: dict[str, dict[str, str]] = {
    "cozy_iyashikei": {
        "palette": "muted earth tones, soft cream, warm dawn gold, jade green accent, dappled light",
        "tail": (
            "iyashikei manga, gentle linework, soft watercolor wash, "
            "low contrast, breathable negative space, contemplative mood, "
            "Studio Ghibli-influenced lighting, manga panel composition"
        ),
        "lighting": "warm morning light, dappled tree-leaf shadows, sRGB color space",
    },
    "dark_psychological": {
        "palette": "muted indigo + cool grey + accent crimson",
        "tail": (
            "seinen psychological manga, heavy linework, deep shadow, "
            "high contrast, claustrophobic framing, Inio Asano-influenced"
        ),
        "lighting": "low-key lighting, single window source, shadow-dominant",
    },
    "hyper_clean_cinematic": {
        "palette": "high-contrast black ink + selective color accents",
        "tail": (
            "premium webtoon, clean linework, cinematic framing, "
            "Solo Leveling-tier production, dynamic composition"
        ),
        "lighting": "dramatic backlight, color-keyed accents",
    },
    "power_progression": {
        "palette": "saturated primary colors, color-impact framing",
        "tail": (
            "shonen action webtoon, dynamic linework, motion lines, "
            "energy effects, Solo Leveling-style"
        ),
        "lighting": "high-contrast directional light, accent halos",
    },
    "webtoon_vertical_romance": {
        "palette": "soft pastels, warm pinks, golden hour",
        "tail": (
            "shojo webtoon, soft linework, sparkle accents, "
            "expressive eyes, Lore Olympus-influenced"
        ),
        "lighting": "warm golden-hour light, soft bloom",
    },
    "social_media_simulacra": {
        "palette": "screen-blue + warm interior + UI gradient accents",
        "tail": (
            "modern slice-of-life webtoon, mobile-native composition, "
            "phone-screen reflections, contemporary linework"
        ),
        "lighting": "screen-glow + ambient interior",
    },
}

# Universal negative prompt — anti-AI-look + anti-render-failures.
_BASE_NEGATIVE = (
    "extra fingers, extra limbs, malformed hands, distorted face, "
    "watermark, signature, text artifacts, low resolution, jpeg artifacts, "
    "blurry, lowres, bad anatomy, mismatched eyes, mismatched proportions, "
    "geometric grid, digital noise, repeating tile, AI gloss, plastic skin, "
    "uncanny valley face"
)


def _character_lock_in(chapter_script: Mapping[str, Any]) -> str:
    """Compose a character-consistency clause from main_characters[]."""
    chars = chapter_script.get("main_characters") or []
    parts: list[str] = []
    for c in chars:
        name = c.get("name", "")
        anchor = c.get("visual_anchor", "")
        if name and anchor:
            parts.append(f"{name}: {anchor}")
    if not parts:
        return ""
    return "consistent character: " + "; ".join(parts)


def _style_anchor(chapter_script: Mapping[str, Any], style_overrides: dict[str, str] | None = None) -> dict[str, str]:
    """Resolve style anchor for the chapter — uses style hint from script
    or overrides dict; defaults to cozy_iyashikei."""
    overrides = style_overrides or {}
    style_id = (
        overrides.get("style_id")
        or chapter_script.get("style")
        or "cozy_iyashikei"
    )
    return dict(_STYLE_ANCHORS.get(style_id, _STYLE_ANCHORS["cozy_iyashikei"]))


def _palette_clause(chapter_script: Mapping[str, Any], anchor: dict[str, str]) -> str:
    """Per-script palette overrides anchor defaults when set in scene_palette."""
    sp = chapter_script.get("scene_palette") or {}
    if sp:
        primary = sp.get("primary", "")
        secondary = sp.get("secondary", "")
        accent = sp.get("accent", "")
        bits = [b for b in (primary, secondary, accent) if b]
        if bits:
            return ", ".join(bits)
    return anchor.get("palette", "")


def _build_panel_prompt(
    panel: Mapping[str, Any],
    *,
    style_anchor: dict[str, str],
    palette_clause: str,
    character_lock_in: str,
    flashback_palette: str | None = None,
) -> tuple[str, str]:
    """Return (positive_prompt, negative_prompt) for one panel."""
    scene = str(panel.get("scene") or "").strip()
    if not scene:
        scene = "quiet panel, ambient establishing shot"

    # Detect flashback palette swap (panel.intent or palette field on panel)
    intent = str(panel.get("intent") or "").lower()
    if flashback_palette and ("flashback" in intent or "flashback palette" in scene.lower()):
        active_palette = flashback_palette
    else:
        active_palette = palette_clause

    # Beat-type to composition cue (per PR #631 §11)
    beat_to_composition = {
        "micro": "tight close-up, intimate framing",
        "spatial": "medium pull-back, contextual angle shift",
        "standard": "establishing wide, scene-transition framing",
        "long_drop": "wide establishing, deliberate negative space, decompression beat",
        "miyazaki_ma": "extreme wide, vast quiet space, awe-pullback composition",
    }
    composition = beat_to_composition.get(str(panel.get("beat_type") or ""), "")

    parts: list[str] = []
    if active_palette:
        parts.append(active_palette)
    parts.append(scene)
    if character_lock_in:
        parts.append(character_lock_in)
    if composition:
        parts.append(composition)
    parts.append(style_anchor.get("lighting", ""))
    parts.append(style_anchor.get("tail", ""))

    positive = ", ".join(p.strip() for p in parts if p and p.strip())
    return positive, _BASE_NEGATIVE


def compile_v3_panel_prompts(
    chapter_script: Mapping[str, Any],
    *,
    style_overrides: dict[str, str] | None = None,
    schema_version: str = "1.0.0",
) -> dict[str, Any]:
    """Build a panel_prompts artifact dict from a v3 chapter_script.

    Output:
        {
          "schema_version": "1.0.0",
          "artifact_type": "panel_prompts",
          "series_id": ..., "chapter_id": ...,
          "panels": [
            {
              "panel_id": "ep001_001",
              "prompt": "...positive prompt...",
              "negative_prompt": "...",
              "beat_type": "spatial",
              "silence_confirmed": false,
              "composition_notes": {"summary": "..."},
              "scene_excerpt": "...first 80 chars of scene..."
            },
            ...
          ]
        }
    """
    style_anchor = _style_anchor(chapter_script, style_overrides)
    palette_clause = _palette_clause(chapter_script, style_anchor)
    character_lock_in = _character_lock_in(chapter_script)

    sp = chapter_script.get("scene_palette") or {}
    flashback_palette = sp.get("flashback_palette")

    panels_out: list[dict[str, Any]] = []
    pages = chapter_script.get("pages") or []
    for page in pages:
        for panel in page.get("panels") or []:
            pid = panel.get("panel_id")
            if not pid:
                raise ValueError("every v3 panel must carry a non-empty panel_id")
            positive, negative = _build_panel_prompt(
                panel,
                style_anchor=style_anchor,
                palette_clause=palette_clause,
                character_lock_in=character_lock_in,
                flashback_palette=flashback_palette,
            )
            entry: dict[str, Any] = {
                "panel_id": str(pid),
                "prompt": positive,
                "negative_prompt": negative,
                "beat_type": panel.get("beat_type"),
                "silence_confirmed": bool(panel.get("silence_confirmed")),
                "composition_notes": {
                    "summary": str(panel.get("intent") or ""),
                    "scene_excerpt": (str(panel.get("scene") or "")[:120]),
                },
            }
            panels_out.append(entry)

    out: dict[str, Any] = {
        "schema_version": schema_version,
        "artifact_type": "panel_prompts",
        "panels": panels_out,
    }
    if "series_id" in chapter_script:
        out["series_id"] = chapter_script["series_id"]
    if "chapter_id" in chapter_script:
        out["chapter_id"] = chapter_script["chapter_id"]
    out["total_panels"] = len(panels_out)
    return out
