"""Compile validated chapter_script (writer handoff) into panel_prompts.json artifact."""

from __future__ import annotations

from typing import Any, Mapping

from phoenix_v4.manga.visual_prompt_compiler import VisualPromptRequest, compile_visual_prompt

# Rough mood → engine mapping for kernel defaults (VISUAL_AGENT will refine).
_MOOD_TO_ENGINE: dict[str, str] = {
    "neutral": "shame",
    "tense": "overwhelm",
    "calm": "false_alarm",
    "dark": "grief",
    "high": "spiral",
}


def iter_panels_from_chapter_script(chapter_script: Mapping[str, Any]) -> list[dict[str, Any]]:
    """Flatten pages → panels in document order."""
    out: list[dict[str, Any]] = []
    for page in chapter_script.get("pages") or []:
        for panel in page.get("panels") or []:
            out.append(dict(panel))
    return out


def _panel_to_request(
    panel: Mapping[str, Any],
    *,
    style_id: str,
    teacher_id: str,
) -> VisualPromptRequest:
    action = str(panel.get("action") or "")
    dialogue = panel.get("dialogue")
    if isinstance(dialogue, list) and dialogue:
        atom_text = " ".join(str(x) for x in dialogue[:5])
    else:
        atom_text = action
    if not atom_text.strip():
        atom_text = "quiet beat"
    mood = str(panel.get("mood") or "neutral").lower()
    engine_type = _MOOD_TO_ENGINE.get(mood, "shame")
    pexpr = panel.get("panel_expression")
    if not isinstance(pexpr, str) and pexpr is not None:
        pexpr = str(pexpr)
    return VisualPromptRequest(
        atom_type="STORY",
        atom_text=atom_text[:4000],
        style_id=style_id,
        teacher_id=teacher_id,
        mechanism_depth="moderate",
        cost_intensity="medium",
        identity_stage="early",
        engine_type=engine_type,
        panel_expression=pexpr,
    )


def compile_panel_prompts_from_chapter_script(
    chapter_script: Mapping[str, Any],
    *,
    schema_version: str = "1.0.0",
    series_id: str | None = None,
    chapter_id: str | None = None,
    config_hash: str = "",
    style_id: str = "dark_psychological",
    teacher_id: str = "ahjan",
) -> dict[str, Any]:
    """Build a panel_prompts artifact dict (validate with schema stem ``panel_prompts``)."""
    panels_out: list[dict[str, Any]] = []
    for panel in iter_panels_from_chapter_script(chapter_script):
        pid = panel.get("panel_id")
        if not pid or not str(pid).strip():
            raise ValueError("Every panel must have a non-empty panel_id")
        req = _panel_to_request(panel, style_id=style_id, teacher_id=teacher_id)
        built = compile_visual_prompt(req)
        comp = built.get("composition_notes", "")
        if isinstance(comp, str):
            comp_notes: dict[str, Any] = {"summary": comp}
        elif isinstance(comp, dict):
            comp_notes = comp
        else:
            comp_notes = {"summary": str(comp)}
        panels_out.append(
            {
                "panel_id": str(pid),
                "prompt": built["positive"],
                "negative_prompt": built["negative"],
                "composition_notes": comp_notes,
                "prompt_token_count": int(built.get("prompt_token_count") or 0),
                "negative_token_count": int(built.get("negative_token_count") or 0),
                "continuity_tags": list(built.get("continuity_tags") or []),
                "silence_compliance": bool(built.get("silence_compliance")),
                "atom_type": built.get("atom_type"),
                "engine_type": built.get("engine_type"),
                "style_id": built.get("style_id"),
                "teacher_id": built.get("teacher_id"),
                "panel_function": built.get("panel_function"),
            }
        )

    out: dict[str, Any] = {
        "schema_version": schema_version,
        "artifact_type": "panel_prompts",
        "panels": panels_out,
    }
    if series_id is not None:
        out["series_id"] = series_id
    if chapter_id is not None:
        out["chapter_id"] = chapter_id
    if config_hash:
        out["config_hash"] = config_hash
    return out
