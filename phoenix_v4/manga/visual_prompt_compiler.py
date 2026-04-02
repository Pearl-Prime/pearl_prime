"""Deterministic visual prompt compiler for the manga kernel."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from phoenix_v4.manga.config import load_panel_layouts, load_seed_atoms, load_style_archetypes

DEFAULT_CHARACTER_BLOCKS = {
    "ahjan": "young woman, dark hair, contemplative expression, simple dark clothing",
    "maat": "elegant woman, warm brown skin, flowing robes, wise gentle expression",
    "sai_maa": "serene figure, light flowing garments, peaceful aura, soft features",
    "ra": "strong figure, commanding presence, golden accents, intense focused eyes",
    "master_wu": "elderly man, traditional robes, long beard, calm knowing expression",
}

DEFAULT_ENGINE_SCENES = {
    "shame": "confined interior space, dim lighting, shadows on walls",
    "grief": "open empty landscape, muted tones, vast sky",
    "spiral": "disorienting angles, tilted perspective, fragmented space",
    "overwhelm": "cluttered environment, too many objects, sensory overload",
    "false_alarm": "ordinary safe space with subtle tension, normal room with one wrong detail",
    "comparison": "split scene, two contrasting spaces side by side",
    "watcher": "observing from distance, window or doorway framing, voyeuristic angle",
}

DEFAULT_INTENSITY_MAP = {
    "low": "calm, subtle emotion, relaxed posture",
    "medium": "visible tension, guarded body language, uncertain expression",
    "high": "intense emotion, clenched hands, dramatic shadows, high contrast",
}

MECHANISM_DEPTH_TO_STORY_PANELS = {
    "shallow": 4,
    "moderate": 5,
    "deep": 6,
}


@dataclass(frozen=True)
class VisualPromptRequest:
    atom_type: str
    atom_text: str = ""
    style_id: str = "dark_psychological"
    teacher_id: str = "ahjan"
    mechanism_depth: str = "moderate"
    cost_intensity: str = "medium"
    identity_stage: str = "early"
    engine_type: str = "shame"
    atom_id: str | None = None
    panel_expression: str | None = None


def _token_count(text: str) -> int:
    return len([token for token in text.replace(",", " ").split() if token])


def resolve_panel_layout(atom_type: str, mechanism_depth: str = "moderate") -> dict[str, Any]:
    panel_map = load_panel_layouts()
    try:
        base = dict(panel_map[atom_type])
    except KeyError as exc:
        raise KeyError(f"Unknown manga atom_type: {atom_type}") from exc
    if atom_type == "STORY":
        try:
            base["panels"] = MECHANISM_DEPTH_TO_STORY_PANELS[mechanism_depth]
        except KeyError as exc:
            raise KeyError(f"Unknown mechanism_depth: {mechanism_depth}") from exc
    return base


def _resolve_seed_overrides(request: VisualPromptRequest) -> dict[str, Any]:
    if not request.atom_id:
        return {}
    atom = load_seed_atoms().get(request.atom_id)
    return dict(atom or {})


def compile_visual_prompt(request: VisualPromptRequest | dict[str, Any], **overrides: Any) -> dict[str, Any]:
    if isinstance(request, dict):
        request = VisualPromptRequest(**request)
    if overrides:
        request = VisualPromptRequest(**{**request.__dict__, **overrides})

    seed_overrides = _resolve_seed_overrides(request)
    request_values = {k: v for k, v in request.__dict__.items() if v not in (None, "")}
    effective = {
        **seed_overrides,
        **request_values,
    }
    style_id = effective["style_id"]
    atom_type = effective["atom_type"]
    teacher_id = effective["teacher_id"]
    engine_type = effective["engine_type"]
    cost_intensity = effective["cost_intensity"]

    style = load_style_archetypes().get(style_id)
    if not style:
        raise KeyError(f"Unknown manga style_id: {style_id}")

    panel = resolve_panel_layout(atom_type, effective["mechanism_depth"])
    char_block = DEFAULT_CHARACTER_BLOCKS.get(teacher_id, "mysterious figure, thoughtful expression")
    scene_block = DEFAULT_ENGINE_SCENES.get(engine_type, "neutral interior, soft lighting")
    emotion_block = DEFAULT_INTENSITY_MAP.get(cost_intensity, "neutral expression")
    panel_expression = effective.get("panel_expression") or ""

    extras = ["masterpiece", "best quality"]
    if panel_expression:
        extras.insert(0, panel_expression)

    positive = ", ".join(
        [
            char_block,
            style["prompt"],
            panel["camera"],
            scene_block,
            emotion_block,
            *extras,
        ]
    )
    negative = ", ".join(
        [
            "extra limbs",
            "deformed hands",
            "bad anatomy",
            "watermark",
            "text",
            "logo",
            style["negative"],
        ]
    )

    composition_notes = panel["composition"]
    if panel_expression:
        composition_notes = f"{composition_notes}; panel_expression={panel_expression}"

    return {
        "positive": positive,
        "negative": negative,
        "atom_id": effective.get("atom_id"),
        "atom_type": atom_type,
        "atom_text": effective.get("atom_text", ""),
        "style_id": style_id,
        "teacher_id": teacher_id,
        "engine_type": engine_type,
        "identity_stage": effective["identity_stage"],
        "cost_intensity": cost_intensity,
        "panel_function": panel["panel_function"],
        "panels": panel["panels"],
        "composition_notes": composition_notes,
        "continuity_tags": [
            f"teacher:{teacher_id}",
            f"style:{style_id}",
            f"engine:{engine_type}",
            f"identity_stage:{effective['identity_stage']}",
        ],
        "silence_compliance": "silent" in panel_expression.lower(),
        "prompt_token_count": _token_count(positive),
        "negative_token_count": _token_count(negative),
    }
