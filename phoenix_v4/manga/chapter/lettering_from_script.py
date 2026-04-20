"""Derive ``lettering_spec`` (v2) from chapter_script writer handoff.

Schema version history
----------------------
v1.0.0 — silence_confirmed only (legacy)
v2.0.0 — adds dialogue_lines, sfx, narrator_caption, estimated_bubble_coverage

Backward compatibility: v1 consumers only read ``silence_confirmed``, which
is present in both versions.  v2 consumers read the full dialogue_lines list.
"""

from __future__ import annotations

from typing import Any, Mapping

from phoenix_v4.manga.chapter.visual_from_script import iter_panels_from_chapter_script

# ── Intensity → bubble_style default mapping ────────────────────────
_INTENSITY_TO_BUBBLE: dict[str, str] = {
    "whisper": "whisper_dashed",
    "calm": "round_normal",
    "normal": "round_normal",
    "excited": "spiky_emphasis",
    "shouting": "spiky_emphasis",
    "screaming": "scream_ultra",
    "internal": "cloud_thought",
}

# ── Intensity → font_override default mapping ───────────────────────
_INTENSITY_TO_FONT: dict[str, str | None] = {
    "whisper": "light_whisper",
    "calm": None,
    "normal": None,
    "excited": "bold_action",
    "shouting": "bold_action",
    "screaming": "all_caps_scream",
    "internal": "italic_internal",
}

# ── Intensity → tail_style default ──────────────────────────────────
_INTENSITY_TO_TAIL: dict[str, str] = {
    "whisper": "pointer",
    "calm": "pointer",
    "normal": "pointer",
    "excited": "pointer",
    "shouting": "pointer",
    "screaming": "pointer",
    "internal": "dotless",
}

_VALID_INTENSITIES = frozenset(_INTENSITY_TO_BUBBLE)
_VALID_BUBBLE_STYLES = frozenset({
    "round_normal", "spiky_emphasis", "cloud_thought", "square_narration",
    "whisper_dashed", "scream_ultra", "electronic_sharp", "drip_horror", "shojo_soft",
})
_VALID_POSITIONS = frozenset({
    "top_left", "top_right", "top_center",
    "bottom_left", "bottom_right", "bottom_center",
    "center_left", "center_right",
})


def _panel_has_dialogue_text(panel: Mapping[str, Any]) -> bool:
    """Return True when the panel contains at least one non-empty dialogue line.

    Handles both legacy ``list[str]`` and v2 ``list[dict]`` dialogue formats.
    """
    dialogue = panel.get("dialogue")
    if not isinstance(dialogue, list):
        return False
    for x in dialogue:
        if isinstance(x, str):
            if x.strip():
                return True
        elif isinstance(x, dict):
            # v2 dict format: {"speaker": ..., "text": ..., ...}
            text = x.get("text")
            if text is not None and str(text).strip():
                return True
        elif x is not None:
            if str(x).strip():
                return True
    return False


def _extract_dialogue_lines(
    panel: Mapping[str, Any],
    panel_index: int,
) -> list[dict[str, Any]]:
    """Convert panel dialogue (str list OR dict list) to normalized dialogue_lines."""
    dialogue = panel.get("dialogue")
    if not isinstance(dialogue, list):
        return []

    lines: list[dict[str, Any]] = []
    # Position hints cycle through reading-order defaults
    _default_positions = ["top_right", "top_left", "bottom_right", "bottom_left"]

    for i, item in enumerate(dialogue):
        if isinstance(item, str):
            if not item.strip():
                continue
            text = item.strip()
            intensity = "normal"
            line: dict[str, Any] = {
                "speaker": f"speaker_{i + 1}",
                "text": text,
                "emotion": "neutral",
                "intensity": intensity,
                "bubble_style": _INTENSITY_TO_BUBBLE[intensity],
                "font_override": _INTENSITY_TO_FONT[intensity],
                "tail_style": _INTENSITY_TO_TAIL[intensity],
                "position_hint": _default_positions[i % len(_default_positions)],
                "speech_atom_id": None,
            }
            lines.append(line)

        elif isinstance(item, dict):
            text = str(item.get("text") or "").strip()
            if not text:
                continue

            intensity = str(item.get("intensity") or "normal").lower()
            if intensity not in _VALID_INTENSITIES:
                intensity = "normal"

            raw_bubble = item.get("bubble_style")
            if raw_bubble and str(raw_bubble) in _VALID_BUBBLE_STYLES:
                bubble_style = str(raw_bubble)
            else:
                bubble_style = _INTENSITY_TO_BUBBLE[intensity]

            raw_pos = item.get("position_hint")
            if raw_pos and str(raw_pos) in _VALID_POSITIONS:
                position_hint = str(raw_pos)
            else:
                position_hint = _default_positions[i % len(_default_positions)]

            tail = str(item.get("tail_style") or _INTENSITY_TO_TAIL[intensity])

            line = {
                "speaker": str(item.get("speaker") or f"speaker_{i + 1}"),
                "text": text,
                "emotion": str(item.get("emotion") or "neutral"),
                "intensity": intensity,
                "bubble_style": bubble_style,
                "font_override": item.get("font_override", _INTENSITY_TO_FONT[intensity]),
                "tail_style": tail,
                "position_hint": position_hint,
                "speech_atom_id": item.get("speech_atom_id"),
            }
            lines.append(line)

    return lines


def _extract_sfx(panel: Mapping[str, Any]) -> list[str]:
    """Extract SFX list from panel."""
    sfx = panel.get("sfx")
    if isinstance(sfx, list):
        return [str(s) for s in sfx if s]
    if isinstance(sfx, str) and sfx.strip():
        return [sfx.strip()]
    return []


def _extract_narrator_caption(panel: Mapping[str, Any]) -> str | None:
    """Extract narrator caption text from panel."""
    cap = panel.get("narrator_caption") or panel.get("caption")
    if cap and str(cap).strip():
        return str(cap).strip()
    return None


def build_lettering_spec_from_chapter_script(
    chapter_script: Mapping[str, Any],
    *,
    schema_version: str = "2.0.0",
) -> dict[str, Any]:
    """Build ``lettering_spec`` v2 from a chapter_script writer handoff.

    ``silence_confirmed`` is True when the panel has no dialogue lines with text
    AND no SFX AND no narrator caption.

    The v2 schema adds ``dialogue_lines``, ``sfx``, ``narrator_caption``, and
    ``estimated_bubble_coverage`` (None until the bubble renderer sets it).

    Setting ``schema_version="1.0.0"`` falls back to the legacy minimal output
    (silence_confirmed only) for any consumer that cannot handle v2.
    """
    lettering_panels: list[dict[str, Any]] = []
    for idx, panel in enumerate(iter_panels_from_chapter_script(chapter_script)):
        pid = panel.get("panel_id")
        if not pid or not str(pid).strip():
            raise ValueError("Every panel must have a non-empty panel_id")

        has_dlg = _panel_has_dialogue_text(panel)
        sfx = _extract_sfx(panel)
        caption = _extract_narrator_caption(panel)

        # silence_confirmed: True only if absolutely no spoken/written content
        silence = not has_dlg and not sfx and not caption

        entry: dict[str, Any] = {
            "panel_id": str(pid),
            "silence_confirmed": silence,
        }

        if schema_version != "1.0.0":
            # v2 fields
            entry["dialogue_lines"] = _extract_dialogue_lines(panel, idx) if has_dlg else []
            entry["sfx"] = sfx
            entry["narrator_caption"] = caption
            entry["estimated_bubble_coverage"] = None

        lettering_panels.append(entry)

    return {
        "schema_version": schema_version,
        "artifact_type": "lettering_spec",
        "lettering_panels": lettering_panels,
    }
