"""Deterministic visual prompt compiler for the manga kernel."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from phoenix_v4.manga.config import load_panel_layouts, load_seed_atoms, load_style_archetypes

DEFAULT_CHARACTER_BLOCKS = {
    "ahjan": "young woman, dark hair, contemplative expression, simple dark clothing",
    "maat": "elegant woman, warm brown skin, flowing robes, wise gentle expression",
    "sai_ma": "serene figure, light flowing garments, peaceful aura, soft features",
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

# Camera family -> shot-type phrase that leads the composed prompt. FLUX (and
# the other commercial-clean backends) weight leading tokens most, so the
# authored scene action + this shot phrase are emitted BEFORE the style tail.
# Mirrors scripts/manga/render_devotion_panels_gpu.py::_SHOT_PHRASE so the
# upstream compiler now produces what that renderer used to splice on per-panel.
CAMERA_TO_SHOT_PHRASE = {
    "establishing-wide": "wide establishing shot, full environment, scenery",
    "wide": "wide shot, full scene",
    "medium": "medium shot",
    "over-shoulder": "over-the-shoulder shot",
    "close-up": "close-up",
    "insert": "close insert detail",
    "environmental-insert": "environmental insert, scenery detail",
}
_DEFAULT_SHOT_PHRASE = "medium shot"

# Cameras the layout renders as pure scenery (no figure). When the authored
# camera is one of these we steer FLUX away from the default centred portrait.
_SCENERY_CAMERAS = {"environmental-insert"}
_SCENERY_POSITIVE = "no people, empty of figures"
_SCENERY_NEGATIVE = "person, people, face, portrait, character, human figure, crowd"

_ACTION_LIMIT = 340


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
    # Per-panel authored scene direction + camera (from the chapter_script /
    # writer handoff). When supplied these LEAD the positive prompt so each
    # panel renders its own beat instead of a scene-agnostic style portrait.
    action: str = ""
    camera: str = ""


def _token_count(text: str) -> int:
    return len([token for token in text.replace(",", " ").split() if token])


def _clean_action(action: str, limit: int = _ACTION_LIMIT) -> str:
    """Collapse whitespace + cap length of the authored scene direction.

    Drops the ``Final panel:`` production aside some beats carry so it does not
    become art, and trims at a word boundary when over ``limit``. Mirrors
    scripts/manga/render_devotion_panels_gpu.py::_clean_action.
    """
    a = " ".join(str(action or "").split()).strip()
    a = a.replace("Final panel:", "").strip()
    if len(a) > limit:
        a = a[:limit].rsplit(" ", 1)[0]
    return a


def _shot_phrase(camera: str) -> str:
    return CAMERA_TO_SHOT_PHRASE.get(str(camera or "").strip().lower(), _DEFAULT_SHOT_PHRASE)


def _scene_lead(action: str, camera: str) -> str:
    """Authored scene action + camera shot-type phrase — the FLUX-leading clause.

    Returns "" when there is no authored action AND no authored camera, so the
    legacy (atom/style-archetype) assembly is preserved byte-for-byte for callers
    that don't pass per-panel scene data.
    """
    cam = str(camera or "").strip().lower()
    scene = _clean_action(action)
    if not scene and not cam:
        return ""
    shot = _shot_phrase(cam)
    lead = f"{scene}, {shot}" if scene else shot
    if cam in _SCENERY_CAMERAS:
        lead = f"{lead}, {_SCENERY_POSITIVE}"
    return lead


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

    # Per-panel authored scene action + camera shot-type — this is what makes the
    # prompt scene-aware. When present it LEADS the positive prompt (FLUX weights
    # leading tokens most) so each panel renders its own beat; the existing
    # style-archetype tail (style/scene-mood/intensity) is appended after.
    camera = str(effective.get("camera") or "")
    scene_lead = _scene_lead(str(effective.get("action") or ""), camera)
    is_scenery = str(camera).strip().lower() in _SCENERY_CAMERAS

    extras = ["masterpiece", "best quality"]
    if panel_expression:
        extras.insert(0, panel_expression)

    # Camera the script authored beats the atom-layout default camera, so prefer
    # the authored shot phrase when we have one (avoids a contradictory framing).
    camera_token = _shot_phrase(camera) if scene_lead else panel["camera"]

    positive_parts: list[str] = []
    if scene_lead:
        positive_parts.append(scene_lead)
    # A scenery-only camera (environmental insert) should NOT inherit the human
    # character archetype — it is an empty-of-figures establishing detail.
    if not (scene_lead and is_scenery):
        positive_parts.append(char_block)
    positive_parts.extend(
        [
            style["prompt"],
            camera_token,
            scene_block,
            emotion_block,
            *extras,
        ]
    )
    positive = ", ".join(p for p in positive_parts if p and p.strip())

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
    # Steer an authored scenery insert away from the default centred portrait.
    if scene_lead and is_scenery:
        negative = f"{negative}, {_SCENERY_NEGATIVE}"

    composition_notes = panel["composition"]
    if scene_lead:
        composition_notes = f"{composition_notes}; scene_lead={scene_lead}"
    if panel_expression:
        composition_notes = f"{composition_notes}; panel_expression={panel_expression}"

    return {
        "positive": positive,
        "negative": negative,
        "atom_id": effective.get("atom_id"),
        "atom_type": atom_type,
        "atom_text": effective.get("atom_text", ""),
        "action": _clean_action(str(effective.get("action") or "")),
        "camera": camera,
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
