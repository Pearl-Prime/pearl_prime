"""Derive ``lettering_spec`` (v2) from chapter_script writer handoff.

Schema version history
----------------------
v1.0.0 — silence_confirmed only (legacy)
v2.0.0 — adds dialogue_lines, sfx, narrator_caption, estimated_bubble_coverage

Bubble-tail targeting (V2 render): each lettering panel also carries
``character_head_bboxes`` — a fractional (0–1) head box per speaker derived
from that speaker's bubble zone — so ``tail_geometry.resolve_mouth_pixel``
points the tail at the speaker's face instead of the panel midline. A line the
author tagged with an explicit ``mouth_anchor`` (or ``character_position``) is
passed through verbatim and wins over the zone-derived box. Without this the
renderer fell through to the bare zone heuristic and tails landed on torsos.

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

# ── Bubble zone → fractional speaker head box (0–1) ─────────────────
# When a dialogue line's only positional signal is its bubble zone, assume the
# speaker is framed beneath/beside that bubble with their HEAD in the upper part
# of the zone's column. ``tail_geometry`` reads the mouth as the horizontal
# center, ~top 15% of this box — so the tail reaches a face, not a torso. These
# boxes are deliberately small and head-high (the prior midline fallback put the
# target at y≈0.55, i.e. the waist → "tail points at the knees"). Authors can
# override per-line with an explicit ``mouth_anchor`` / ``character_position``.
_ZONE_HEAD_BOX: dict[str, dict[str, float]] = {
    "top_left":      {"x1": 0.10, "y1": 0.26, "x2": 0.34, "y2": 0.50},
    "top_right":     {"x1": 0.66, "y1": 0.26, "x2": 0.90, "y2": 0.50},
    "top_center":    {"x1": 0.38, "y1": 0.28, "x2": 0.62, "y2": 0.52},
    "bottom_left":   {"x1": 0.10, "y1": 0.52, "x2": 0.34, "y2": 0.76},
    "bottom_right":  {"x1": 0.66, "y1": 0.52, "x2": 0.90, "y2": 0.76},
    "bottom_center": {"x1": 0.38, "y1": 0.54, "x2": 0.62, "y2": 0.78},
    "center_left":   {"x1": 0.08, "y1": 0.36, "x2": 0.32, "y2": 0.58},
    "center_right":  {"x1": 0.68, "y1": 0.36, "x2": 0.92, "y2": 0.58},
}


def _derive_character_head_bboxes(
    dialogue_lines: list[dict[str, Any]],
) -> dict[str, dict[str, float]]:
    """Build a per-speaker fractional head box from each line's bubble zone.

    One box per distinct speaker (first occurrence wins, so a speaker who
    appears twice keeps their first zone). Lines that already carry an explicit
    ``mouth_anchor`` are skipped here — the renderer reads that anchor directly
    and does not need a derived box. Returns ``{}`` when nothing is derivable,
    in which case the renderer keeps its in-built zone fallback.
    """
    boxes: dict[str, dict[str, float]] = {}
    for line in dialogue_lines:
        if line.get("mouth_anchor"):
            continue  # explicit anchor wins; no box needed
        speaker = str(line.get("speaker") or "").strip()
        if not speaker or speaker in boxes:
            continue
        hint = str(line.get("position_hint") or "").strip()
        box = _ZONE_HEAD_BOX.get(hint)
        if box is not None:
            boxes[speaker] = dict(box)
    return boxes


def _panel_has_dialogue_text(panel: Mapping[str, Any]) -> bool:
    """Return True when the panel contains at least one non-empty dialogue line.

    Handles three key conventions:
      - ``dialogue_lines`` (current chapter_script_writer_handoff v3 schema)
      - ``dialogue`` (legacy v1/v2 + tests)

    And two payload formats:
      - list[str] (legacy plain text)
      - list[dict] with either ``text`` (v2) or ``text_by_locale`` (v3)
    """
    dialogue = panel.get("dialogue_lines") or panel.get("dialogue")
    if not isinstance(dialogue, list):
        return False
    for x in dialogue:
        if isinstance(x, str):
            if x.strip():
                return True
        elif isinstance(x, dict):
            # v2: {"speaker": ..., "text": ..., ...}
            text = x.get("text")
            if text is not None and str(text).strip():
                return True
            # v3: {"speaker": ..., "text_by_locale": {"en_US": ..., "ja_JP": ...}, ...}
            tbl = x.get("text_by_locale")
            if isinstance(tbl, dict):
                for v in tbl.values():
                    if v is not None and str(v).strip():
                        return True
        elif x is not None:
            if str(x).strip():
                return True
    return False


def _extract_dialogue_lines(
    panel: Mapping[str, Any],
    panel_index: int,
) -> list[dict[str, Any]]:
    """Convert panel dialogue (str list OR dict list) to normalized dialogue_lines.

    Accepts either ``dialogue_lines`` (v3 chapter_script_writer_handoff schema)
    or ``dialogue`` (legacy v1/v2) — falls back to the older key for back-compat.
    """
    dialogue = panel.get("dialogue_lines") or panel.get("dialogue")
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
            # v2: item has "text"
            # v3: item has "text_by_locale": {en_US: ..., ja_JP: ...} (text optional)
            text = str(item.get("text") or "").strip()
            text_by_locale = item.get("text_by_locale")
            if not text and isinstance(text_by_locale, dict):
                # Prefer en_US (default_locale); else first non-empty value
                cand = text_by_locale.get("en_US")
                if not (cand and str(cand).strip()):
                    for v in text_by_locale.values():
                        if v and str(v).strip():
                            cand = v
                            break
                if cand:
                    text = str(cand).strip()
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
            # Preserve per-locale text + font overrides for v3 consumers
            if isinstance(text_by_locale, dict):
                line["text_by_locale"] = dict(text_by_locale)
            fol = item.get("font_override_by_locale")
            if isinstance(fol, dict):
                line["font_override_by_locale"] = dict(fol)
            # Pass author-supplied tail targeting through to the renderer. An
            # explicit normalized mouth_anchor {x,y} wins over any zone-derived
            # head box (tail_geometry checks mouth_anchor first).
            ma = item.get("mouth_anchor")
            if isinstance(ma, Mapping) and "x" in ma and "y" in ma:
                try:
                    line["mouth_anchor"] = {"x": float(ma["x"]), "y": float(ma["y"])}
                except (TypeError, ValueError):
                    pass
            lines.append(line)

    return lines


def _extract_sfx(panel: Mapping[str, Any]) -> list[str]:
    """Extract SFX list from panel.

    Accepts v2 ``sfx`` (list[str] | str) or v3 ``sfx_by_locale``
    (dict[locale, list[str] | str]). For v3 it prefers en_US then falls
    back to the first non-empty locale list.
    """
    sfx = panel.get("sfx")
    if isinstance(sfx, list):
        return [str(s) for s in sfx if s]
    if isinstance(sfx, str) and sfx.strip():
        return [sfx.strip()]
    # v3 schema
    sbl = panel.get("sfx_by_locale")
    if isinstance(sbl, dict):
        cand = sbl.get("en_US")
        if not cand:
            for v in sbl.values():
                if v:
                    cand = v
                    break
        if isinstance(cand, list):
            return [str(s) for s in cand if s]
        if isinstance(cand, str) and cand.strip():
            return [cand.strip()]
    return []


def _extract_narrator_caption(panel: Mapping[str, Any]) -> str | None:
    """Extract narrator caption text from panel.

    Accepts v2 ``narrator_caption`` / ``caption`` or v3
    ``narrator_caption_by_locale`` (prefers en_US, then any populated locale).
    """
    cap = panel.get("narrator_caption") or panel.get("caption")
    if cap and str(cap).strip():
        return str(cap).strip()
    # v3 schema
    cbl = panel.get("narrator_caption_by_locale")
    if isinstance(cbl, dict):
        cand = cbl.get("en_US")
        if not (cand and str(cand).strip()):
            for v in cbl.values():
                if v and str(v).strip():
                    cand = v
                    break
        if cand and str(cand).strip():
            return str(cand).strip()
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
            dlg_lines = _extract_dialogue_lines(panel, idx) if has_dlg else []
            entry["dialogue_lines"] = dlg_lines
            entry["sfx"] = sfx
            entry["narrator_caption"] = caption
            entry["estimated_bubble_coverage"] = None
            # Tail targeting: prefer author-supplied head boxes on the panel;
            # otherwise derive a per-speaker head box from each line's bubble
            # zone so V2 tails point at faces, not the panel midline.
            authored_boxes = panel.get("character_head_bboxes")
            if isinstance(authored_boxes, Mapping) and authored_boxes:
                entry["character_head_bboxes"] = dict(authored_boxes)
            else:
                derived = _derive_character_head_bboxes(dlg_lines)
                if derived:
                    entry["character_head_bboxes"] = derived

        lettering_panels.append(entry)

    return {
        "schema_version": schema_version,
        "artifact_type": "lettering_spec",
        "lettering_panels": lettering_panels,
    }
