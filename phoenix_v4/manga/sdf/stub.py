"""Deterministic SDF conditioning placeholders for panel_prompts (Comfy export hook).

Full neural SDF training / sdf_projector live under ``config/manga/sdf/`` per spec §6.7.7.
This module only emits JSON-safe metadata so downstream batch/Comfy can branch when maps exist.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Mapping

SPEC_REF = "specs/MANGA_MODE_SYSTEM_SPEC.md §6.7"


def build_sdf_conditioning_stub(
    panel: Mapping[str, Any],
    *,
    pose_mod: str = "neutral",
    controlnet_strength: float = 0.6,
    map_kind: str = "disabled",
    model_ref: str | None = None,
    conditioning_map_path: str | None = None,
) -> dict[str, Any]:
    """Return ``sdf_conditioning`` object for one panel (no filesystem side effects)."""
    if map_kind not in ("disabled", "depth", "contour", "replay_fixture"):
        raise ValueError(f"Invalid map_kind: {map_kind!r}")
    out: dict[str, Any] = {
        "layer": "sdf_geometric_prior",
        "map_kind": map_kind,
        "pose_mod": pose_mod,
        "controlnet_strength": float(controlnet_strength),
        "spec_ref": SPEC_REF,
    }
    if model_ref:
        out["model_ref"] = model_ref
    if conditioning_map_path:
        out["conditioning_map_path"] = conditioning_map_path
    return out


def attach_sdf_stub_conditioning(
    panel_prompts: Mapping[str, Any],
    *,
    map_kind: str = "disabled",
    controlnet_strength: float = 0.6,
) -> dict[str, Any]:
    """Deep-copy ``panel_prompts`` and add ``sdf_conditioning`` to each panel entry."""
    doc = deepcopy(dict(panel_prompts))
    panels = doc.get("panels")
    if not isinstance(panels, list):
        return doc
    new_panels: list[dict[str, Any]] = []
    for p in panels:
        row = dict(p) if isinstance(p, dict) else {}
        mood = str(row.get("mood") or "neutral").lower()
        pose_mod = "neutral"
        if mood in ("tense", "dark", "high"):
            pose_mod = "dramatic"
        row["sdf_conditioning"] = build_sdf_conditioning_stub(
            row,
            pose_mod=pose_mod,
            controlnet_strength=controlnet_strength,
            map_kind=map_kind,
        )
        new_panels.append(row)
    doc["panels"] = new_panels
    return doc
