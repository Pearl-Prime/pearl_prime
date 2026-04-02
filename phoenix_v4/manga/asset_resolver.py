"""Retrieval-first asset resolver for manga panel prompts."""
from __future__ import annotations

from typing import Any

from phoenix_v4.manga.config import load_manga_gates

DEFAULT_ASSET_SELECTION_PRIORITY = {
    "composition_compat_threshold": 0.5,
    "weights": {
        "atom_type": 3.0,
        "style_id": 3.0,
        "teacher_id": 2.0,
        "engine_type": 1.5,
        "panel_function": 1.0,
        "continuity_tags_overlap": 0.5,
    },
}


def _overlap(left: list[str] | None, right: list[str] | None) -> int:
    return len(set(left or []) & set(right or []))


def _score_asset(panel_prompt: dict[str, Any], asset: dict[str, Any], priority: dict[str, Any]) -> float:
    weights = priority.get("weights", {})
    score = 0.0
    for key in ("atom_type", "style_id", "teacher_id", "engine_type", "panel_function"):
        prompt_value = panel_prompt.get(key)
        asset_value = asset.get(key)
        if prompt_value and asset_value and prompt_value == asset_value:
            score += float(weights.get(key, 0.0))
    score += _overlap(panel_prompt.get("continuity_tags"), asset.get("continuity_tags")) * float(
        weights.get("continuity_tags_overlap", 0.0)
    )
    return score


def resolve_panel_asset(
    panel_prompt: dict[str, Any],
    assets: list[dict[str, Any]],
    priority: dict[str, Any] | None = None,
    fallback_index: int = 0,
) -> dict[str, Any]:
    priority = priority or DEFAULT_ASSET_SELECTION_PRIORITY
    threshold = float(priority.get("composition_compat_threshold", 0.5))

    best_asset: dict[str, Any] | None = None
    best_score = float("-inf")
    for asset in assets:
        compat = float((asset.get("composition_compat") or {}).get("page", 1.0))
        if compat < threshold:
            continue
        score = _score_asset(panel_prompt, asset, priority)
        if score > best_score:
            best_score = score
            best_asset = asset

    if best_asset and best_score > 0:
        return {
            "panel_id": panel_prompt["panel_id"],
            "asset_id": best_asset["asset_id"],
            "source": "bank",
            "score": round(best_score, 3),
            "requires_generation": False,
        }

    atom_type = str(panel_prompt.get("atom_type", "panel")).lower()
    return {
        "panel_id": panel_prompt["panel_id"],
        "asset_id": f"placeholder-{atom_type}-{fallback_index:03d}",
        "source": "placeholder",
        "score": 0.0,
        "requires_generation": True,
    }


def resolve_panel_assets(
    prompt_doc: dict[str, Any],
    assets: list[dict[str, Any]],
    priority: dict[str, Any] | None = None,
) -> dict[str, Any]:
    priority = priority or DEFAULT_ASSET_SELECTION_PRIORITY
    resolved = [
        resolve_panel_asset(panel, assets, priority=priority, fallback_index=index + 1)
        for index, panel in enumerate(prompt_doc.get("panels", []))
    ]
    unresolved = [item["panel_id"] for item in resolved if item["requires_generation"]]
    return {
        "chapter_id": prompt_doc["chapter_id"],
        "variant_id": prompt_doc.get("variant_id", "default"),
        "config_hash": prompt_doc.get("config_hash"),
        "gates_snapshot": load_manga_gates().get("gates", []),
        "resolved": resolved,
        "unresolved_panel_ids": unresolved,
    }
