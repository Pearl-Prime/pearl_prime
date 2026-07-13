#!/usr/bin/env python3
"""Panel planning legality for bank-assembly manifests (HR rules).

Single source for archetype → shot_type (MANGA_COMPOSITION_GRAMMAR_SPEC.md §6.3)
and fail-closed half-person / contamination / abstract-stage planning checks
(MANGA_HUMAN_READABILITY_ASSEMBLY_RULES_2026-07-09.md §2–§3, §9).

Consumed by:
  - generate_assembly_manifest.shot_type_for_archetype
  - assemble_from_bank.load_manifest → validate_manifest_composition_planning

Provenance: ARCHETYPE_SHOT_TYPE recovered from pre-#5428 generate_assembly_manifest
inline map (git show 206e6e8d^); planning checks authored from HR rules + G1_MATRIX.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from composition_grammar import G1_MATRIX, load_composition_meta

# Spec §6.3 + stillness HR-U16 repair archetype (shared_meal_table_medium → re_establish)
ARCHETYPE_SHOT_TYPE: dict[str, str] = {
    "sparse_establishing_wide": "establishing",
    "morning_routine_sequence": "re_establish",
    "walking_in_thought_medium": "re_establish",
    "character_quiet_face": "reaction_emotion",
    "character_face_micro_tension": "reaction_emotion",
    "chest_breath_micro": "dialogue_bust",
    "tea_beat_close_up": "insert_object",
    "hand_table_micro": "insert_object",
    "dappled_light_hand": "insert_object",
    "phone_notification_macro": "insert_object",
    "food_preparation_overhead": "insert_object",
    "kettle_steam_macro": "insert_object",
    "seasonal_anchor_object": "insert_object",
    "window_light_threshold": "diegetic_cu",
    "pet_companion_micro": "insert_object",
    "long_drop_decompression": "establishing",
    "miyazaki_ma_pause": "pillow_ma",
    "character_at_table_medium": "establishing",
    "shared_scene_medium": "establishing",
    "shared_meal_table_medium": "re_establish",
    "pendulation_pair_visual_rhyme": "closure_breath",
}

HALF_PERSON_CROPS = frozenset({"bust", "waist_up", "face_cu", "ecu_fragment", "hands"})
READABLE_ROOM_BG = frozenset({"full_render", "partial_motif"})
ABSTRACT_BG = frozenset({
    "defocus_derived",
    "tone_gradient",
    "manpu_emotion",
    "white_void",
    "black_void",
    "speedlines_focus",
})


def shot_type_for_archetype(archetype: str | None) -> str | None:
    if not archetype:
        return None
    return ARCHETYPE_SHOT_TYPE.get(archetype)


def _resolve(path_str: str, manifest_dir: Path, repo: Path) -> Path:
    p = Path(path_str)
    if p.is_absolute():
        return p
    cand = (manifest_dir / p).resolve()
    if cand.is_file():
        return cand
    cand = (repo / p).resolve()
    if cand.is_file():
        return cand
    return repo / p


def _effective_bg_class(l0_layer: dict[str, Any], l0_meta: dict[str, Any] | None) -> str:
    deriv = l0_layer.get("derivation") or {}
    dtype = (deriv.get("type") or deriv.get("op") or "").lower()
    if dtype in ("defocus", "defocus_derived"):
        return "defocus_derived"
    if dtype in ("tone_gradient", "tone_flat", "gradient", "tone"):
        return "tone_gradient"
    if dtype in ("manpu", "manpu_emotion"):
        return "manpu_emotion"
    if dtype in ("void", "white_void"):
        return "white_void"
    if dtype == "black_void":
        return "black_void"
    if l0_meta and l0_meta.get("bg_class"):
        return str(l0_meta["bg_class"])
    return "full_render"


def _l2_layers(panel: dict[str, Any]) -> list[dict[str, Any]]:
    return [ly for ly in (panel.get("layers") or []) if ly.get("layer_class") == "L2"]


def _l0_layer(panel: dict[str, Any]) -> dict[str, Any] | None:
    for ly in panel.get("layers") or []:
        if ly.get("layer_class") == "L0":
            return ly
    return None


def _half_person_exception(
    l2_meta: dict[str, Any],
    l0_meta: dict[str, Any] | None,
    layer: dict[str, Any],
    shot: str | None,
) -> bool:
    """Legal half-person-on-room exceptions (HR rules §3.1)."""
    if shot == "diegetic_cu":
        return True
    if l2_meta.get("diegetic_pair"):
        return True
    grounding = layer.get("grounding") or {}
    if grounding.get("occluder") is True and layer.get("anchor_slot"):
        if l0_meta:
            slots = l0_meta.get("anchor_slots") or []
            slot_id = layer.get("anchor_slot")
            for s in slots:
                if s.get("slot_id") == slot_id and s.get("occluder_crop_bbox_pct"):
                    return True
            if l2_meta.get("room_capable") and l2_meta.get("crop_class") in (
                "full_figure",
                "knees_up",
                "thigh_up",
            ):
                return True
        else:
            return True
    return False


def validate_manifest_composition_planning(
    manifest: dict[str, Any],
    manifest_dir: Path,
    repo: Path,
) -> list[str]:
    """Return planning error strings (empty = pass). Fail-closed for HR-F01 etc."""
    errors: list[str] = []
    for panel in manifest.get("panels") or []:
        pid = panel.get("panel_id", "<unknown>")
        shot = panel.get("shot_type")
        l0 = _l0_layer(panel)
        if not l0:
            continue
        l0_path = _resolve(str(l0.get("asset", "")), manifest_dir, repo)
        l0_meta = load_composition_meta(l0_path) if l0_path.is_file() else None
        bg = _effective_bg_class(l0, l0_meta)

        if shot == "pillow_ma" and _l2_layers(panel):
            errors.append(
                f"{pid}: HR-F11 pillow_ma must contain zero figure layers "
                f"(found L2 on shot_type=pillow_ma)"
            )

        if (
            shot == "insert_object"
            and bg in READABLE_ROOM_BG
            and not (l0.get("derivation"))
            and _l2_layers(panel)
        ):
            errors.append(
                f"{pid}: HR-U20 insert_object requires tone_gradient/void derivation "
                f"(or diegetic macro), not readable {bg}"
            )

        for layer in _l2_layers(panel):
            asset = str(layer.get("asset", ""))
            l2_path = _resolve(asset, manifest_dir, repo)
            l2_meta = load_composition_meta(l2_path) if l2_path.is_file() else None
            crop = (l2_meta or {}).get("crop_class") or ""

            if l2_meta and l2_meta.get("scene_contamination") and bg in ABSTRACT_BG:
                errors.append(
                    f"{pid}: contaminated L2 ({Path(asset).name}) illegal on abstract "
                    f"bg_class={bg}"
                )

            if (
                l2_meta
                and bg in ABSTRACT_BG
                and crop in ("bust", "face_cu", "waist_up")
                and l2_meta.get("abstract_stage_eligible") is False
            ):
                errors.append(
                    f"{pid}: L2 {Path(asset).name} crop={crop} not abstract_stage_eligible "
                    f"on bg_class={bg}"
                )

            if crop in HALF_PERSON_CROPS and bg in READABLE_ROOM_BG:
                if _half_person_exception(l2_meta or {}, l0_meta, layer, shot):
                    continue
                verdict = G1_MATRIX.get(crop, {}).get(bg, "ILLEGAL")
                if verdict == "ILLEGAL" or crop in HALF_PERSON_CROPS:
                    errors.append(
                        f"{pid}: HR-F01 floating half-person — crop={crop or '?'} on "
                        f"bg_class={bg} without diegetic_pair/occluder/diegetic_cu"
                    )
    return errors
