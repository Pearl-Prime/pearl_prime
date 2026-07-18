"""Mecha structural layer contract gates.

The mecha image bank needs stricter semantics than generic bank assembly:
background plates must stay environment/support-only, foreground L2 assets
must be one clean subject, and L3 assets must be isolated props.
"""
from __future__ import annotations

from typing import Any

CONTRACT_ID = "mecha_clean_structural_layer_v1"

MECHA_KEYS = {"mecha", "mecha_hangar", "mecha_cockpit"}
L0_FORBIDDEN_SUBJECTS = {
    "character",
    "characters",
    "pilot",
    "person",
    "people",
    "foreground_subject",
    "primary_subject",
    "mecha_subject",
}
L2_FORBIDDEN_CONTEXT = {
    "background",
    "cockpit",
    "hangar",
    "environment",
    "room",
    "scene",
    "console",
    "interior",
}
L3_FORBIDDEN_SUBJECTS = {
    "character",
    "pilot",
    "person",
    "people",
    "background",
    "environment",
    "scene",
}


def _contract(meta: dict[str, Any]) -> dict[str, Any]:
    contract = meta.get("structural_layer_contract") or {}
    return contract if isinstance(contract, dict) else {}


def is_mecha_structural_layer(meta: dict[str, Any] | None) -> bool:
    if not meta:
        return False
    contract = _contract(meta)
    if contract.get("id") == CONTRACT_ID:
        return True
    for key in ("genre", "genre_id", "style_register"):
        value = str(meta.get(key) or "").lower()
        if value in MECHA_KEYS or value.startswith("mecha_"):
            return True
    return False


def _as_bool(value: Any) -> bool:
    return bool(value) if isinstance(value, bool) else False


def _string_set(meta: dict[str, Any], *keys: str) -> set[str]:
    out: set[str] = set()
    for key in keys:
        value = meta.get(key)
        if isinstance(value, str):
            out.add(value.lower())
        elif isinstance(value, list):
            out.update(str(item).lower() for item in value)
    return out


def validate_mecha_layer_meta(
    meta: dict[str, Any] | None,
    *,
    layer_class: str,
) -> dict[str, Any] | None:
    """Return a pass report, or raise ValueError for a contract failure.

    Non-mecha layers return None so generic manga flows remain unchanged.
    """
    if not is_mecha_structural_layer(meta):
        return None
    meta = meta or {}
    contract = _contract(meta)
    failures: list[str] = []
    status = str(contract.get("status") or "missing")
    role = str(contract.get("role") or "").lower()
    subject = str(contract.get("subject") or "").lower()

    if contract.get("id") != CONTRACT_ID:
        failures.append("missing_mecha_clean_structural_layer_contract")
    if status != "clean":
        failures.append(f"contract_status_{status}")
    if meta.get("layer_class") and str(meta.get("layer_class")) != layer_class:
        failures.append("layer_class_mismatch")

    if layer_class == "L0":
        if role and role != "environment_support":
            failures.append("l0_role_must_be_environment_support")
        if _as_bool(contract.get("contains_primary_subject")):
            failures.append("l0_contains_primary_subject")
        if _as_bool(contract.get("contains_foreground_subject")):
            failures.append("l0_contains_foreground_subject")
        if _as_bool(contract.get("contains_pilot")):
            failures.append("l0_contains_pilot")
        subjects = _string_set(contract, "contains", "subjects")
        if subjects & L0_FORBIDDEN_SUBJECTS:
            failures.append("l0_subject_contamination")
        if not meta.get("support_zones"):
            failures.append("l0_missing_support_zones")
    elif layer_class == "L2":
        if role and role != "single_subject_cutout":
            failures.append("l2_role_must_be_single_subject_cutout")
        if subject not in {"pilot", "mecha"}:
            failures.append("l2_subject_must_be_pilot_or_mecha")
        if meta.get("scene_contamination") is not False:
            failures.append("l2_scene_contamination_not_false")
        if _as_bool(contract.get("contains_background")):
            failures.append("l2_contains_background")
        if _as_bool(contract.get("contains_environment")):
            failures.append("l2_contains_environment")
        context = _string_set(contract, "contains", "context", "background_context")
        if context & L2_FORBIDDEN_CONTEXT:
            failures.append("l2_context_contamination")
    elif layer_class == "L3":
        if role and role != "isolated_object":
            failures.append("l3_role_must_be_isolated_object")
        if subject not in {"object", "telemetry", "prop", "glove_pad"}:
            failures.append("l3_subject_must_be_object")
        subjects = _string_set(contract, "contains", "subjects")
        if subjects & L3_FORBIDDEN_SUBJECTS:
            failures.append("l3_subject_contamination")

    if failures:
        asset_id = str(meta.get("asset_id") or "<unknown>")
        raise ValueError(
            f"{layer_class} structural purity FAIL — "
            f"{','.join(failures)}; asset_id={asset_id} contract={CONTRACT_ID}"
        )
    return {
        "contract": CONTRACT_ID,
        "asset_id": str(meta.get("asset_id") or ""),
        "role": role,
        "subject": subject,
    }
