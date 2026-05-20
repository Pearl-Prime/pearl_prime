"""
Angle Integration Layer (V4.7). DEV SPEC: angle as structural narrative driver.

Schema:
  - v1: ``config/angles/angle_registry.yaml`` declares ``angles: {<id>: {...}}`` with
    structural fields (``arc_variant``, ``framing_mode``, ``chapter_1_role_bias``,
    ``integration_reinforcement_type``, optional ``arc_path``).
  - v2 (additive, this module supports both): topic-specific angles declare
    ``parent_universal: <UNIVERSAL_ID>`` and inherit structural + ``journey`` fields
    transitively. Legacy v1 angles may carry ``deprecated: true`` +
    ``successor_angle_id`` + ``deprecation_note``. The v2 SSOT is documented in
    ``docs/specs/ANGLE_REGISTRY_SSOT_V2_SPEC.md``.

Arc-First remains authoritative. Angle chooses variant (arc_path when set).
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

try:
    import yaml
except ImportError:
    yaml = None

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEFAULT_ANGLE_REGISTRY = REPO_ROOT / "config" / "angles" / "angle_registry.yaml"

_LOG = logging.getLogger(__name__)

# Structural fields that inherit downward through the parent_universal chain.
_INHERITED_STRUCTURAL_FIELDS = (
    "arc_variant",
    "framing_mode",
    "chapter_1_role_bias",
    "integration_reinforcement_type",
    "arc_path",
)

# Leaf-defined fields that do NOT inherit (per ANGLE_REGISTRY_SSOT_V2_SPEC §3.1).
_LEAF_ONLY_FIELDS = (
    "display_name",
    "core_frame",
    "use_when",
)


class DeprecatedAngleError(ValueError):
    """Raised when a deprecated angle is resolved without ``allow_legacy=True``."""


class AngleCycleError(ValueError):
    """Raised when ``parent_universal`` chains form a cycle."""


def load_angle_registry(registry_path: Optional[Path] = None) -> dict[str, Any]:
    """Load angle_registry.yaml. Returns full registry dict or empty dict on miss."""
    path = registry_path or DEFAULT_ANGLE_REGISTRY
    if not path.exists() or yaml is None:
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_angle_context(
    angle_id: Optional[str],
    registry_path: Optional[Path] = None,
    fail_fast: bool = False,
) -> Optional[dict[str, Any]]:
    """
    Return angle context dict for angle_id (chapter_1_role_bias, integration_reinforcement_type, framing_mode, etc.)
    or None if angle_id missing/not in registry. If fail_fast=True and angle_id is non-empty but not in registry, raise ValueError.

    For v2 topic-specific angles (those with parent_universal), this walks the inheritance chain so callers
    receive the merged structural + journey block. Deprecated angles still resolve (warning logged); to
    enforce strict v2 use ``resolve_angle_with_inheritance(allow_legacy=False)`` directly.
    """
    if not angle_id or not (angle_id := str(angle_id).strip()):
        return None
    reg = load_angle_registry(registry_path)
    angles_map = reg.get("angles") or {}
    angles = angles_map.get(angle_id)
    if not angles or not isinstance(angles, dict):
        if fail_fast:
            raise ValueError(
                f"angle_id {angle_id!r} not found in angle_registry (config/angles/angle_registry.yaml). "
                "Add it or omit angle_id."
            )
        return None
    # If the entry inherits, walk the chain. Allow legacy here because callers of the legacy
    # get_angle_context contract may pass deprecated angle_ids (back-compat path).
    if "parent_universal" in angles or angles.get("deprecated"):
        try:
            merged = resolve_angle_with_inheritance(angle_id, reg, allow_legacy=True)
        except (AngleCycleError, KeyError) as exc:
            _LOG.warning("angle inheritance failed for %r: %s — returning leaf only", angle_id, exc)
            return dict(angles)
        # Strip provenance from the returned dict to preserve v1 caller contract (flat structural fields).
        merged.pop("_resolution_provenance", None)
        return merged
    return dict(angles)


def resolve_arc_path(
    angle_id: Optional[str],
    default_arc_path: Path,
    repo_root: Optional[Path] = None,
    registry_path: Optional[Path] = None,
) -> Path:
    """
    If angle_id is in registry and has arc_path set (directly or via inheritance), return resolved
    path (repo_root / arc_path); else return default_arc_path. Arc variant is static; no runtime
    randomization.
    """
    path = default_arc_path
    root = repo_root or REPO_ROOT
    if not angle_id or not (angle_id := str(angle_id).strip()):
        return path
    ctx = get_angle_context(angle_id, registry_path)
    if not ctx:
        return path
    arc_path_str = ctx.get("arc_path")
    if not arc_path_str or not isinstance(arc_path_str, str):
        return path
    resolved = (root / arc_path_str.strip()).resolve()
    if resolved.exists():
        return resolved
    return path


def resolve_angle_with_inheritance(
    angle_id: str,
    registry: dict[str, Any],
    *,
    allow_legacy: bool = False,
) -> dict[str, Any]:
    """Merge structural + journey fields by walking the ``parent_universal`` chain.

    Per ``docs/specs/ANGLE_REGISTRY_SSOT_V2_SPEC.md`` §3:

    - Look up ``angle_id`` in ``registry['angles']``. Missing → ``KeyError``.
    - ``deprecated: true`` with ``allow_legacy=False`` → ``DeprecatedAngleError``.
    - Walk ``parent_universal`` transitively. Cycle → ``AngleCycleError``.
    - Merge root-down, leaf overrides. Structural fields and the ``journey`` block
      inherit; ``display_name``, ``core_frame``, ``use_when`` are leaf-only and do
      not inherit.
    - Attach ``_resolution_provenance`` to the returned dict for observability.

    Args:
        angle_id: angle_id to resolve.
        registry: full registry dict (e.g. from ``load_angle_registry()``).
        allow_legacy: if True, deprecated angles resolve normally with a warning;
            if False (default for new books), deprecated angles raise.

    Returns:
        Merged angle dict with ``_resolution_provenance`` metadata.

    Raises:
        KeyError: ``angle_id`` not declared in registry.
        DeprecatedAngleError: angle is deprecated and ``allow_legacy=False``.
        AngleCycleError: ``parent_universal`` chain forms a cycle.
    """
    angles_map = (registry or {}).get("angles") or {}
    if not angle_id or angle_id not in angles_map:
        raise KeyError(
            f"angle_id {angle_id!r} not declared in registry. "
            "Add it under angles: in config/angles/angle_registry.yaml."
        )

    leaf_entry = angles_map[angle_id]
    if not isinstance(leaf_entry, dict):
        raise KeyError(f"angle_id {angle_id!r} entry is not a mapping: {type(leaf_entry).__name__}")

    is_deprecated = bool(leaf_entry.get("deprecated"))
    successor_angle_id = leaf_entry.get("successor_angle_id") if is_deprecated else None
    if is_deprecated and not allow_legacy:
        note = leaf_entry.get("deprecation_note", "")
        raise DeprecatedAngleError(
            f"angle_id {angle_id!r} is deprecated. "
            f"successor_angle_id={successor_angle_id!r}. "
            f"Pass allow_legacy=True to resolve anyway. {note}".strip()
        )

    # Build chain leaf → root.
    chain: list[str] = []
    seen: set[str] = set()
    current_id: Optional[str] = angle_id
    while current_id is not None:
        if current_id in seen:
            cycle_path = " → ".join(chain + [current_id])
            raise AngleCycleError(
                f"parent_universal cycle detected for angle_id {angle_id!r}: {cycle_path}"
            )
        seen.add(current_id)
        entry = angles_map.get(current_id)
        if not isinstance(entry, dict):
            raise KeyError(
                f"parent_universal {current_id!r} (in chain for {angle_id!r}) not declared in registry."
            )
        chain.append(current_id)
        parent_id = entry.get("parent_universal")
        if parent_id is None:
            break
        current_id = str(parent_id).strip() or None

    # Merge root → leaf. Root (universal) values become the base; descendants override.
    merged: dict[str, Any] = {}
    inherited_fields: list[str] = []
    leaf_overrides: list[str] = []

    for idx, aid in enumerate(reversed(chain)):
        entry = angles_map[aid]
        is_root = idx == 0
        is_leaf = idx == len(chain) - 1
        for key, value in entry.items():
            if key == "parent_universal":
                # Preserve only on the leaf for downstream reference.
                if is_leaf:
                    merged["parent_universal"] = value
                continue
            if key in _LEAF_ONLY_FIELDS:
                # Display fields are leaf-only.
                if is_leaf:
                    merged[key] = value
                continue
            if key == "journey":
                # Merge journey block: leaf sub-fields override inherited sub-fields.
                if is_root:
                    merged["journey"] = _deep_copy_journey(value)
                    if not is_leaf and "journey" not in inherited_fields:
                        inherited_fields.append("journey")
                else:
                    if "journey" in merged and isinstance(merged["journey"], dict) and isinstance(value, dict):
                        for jk, jv in value.items():
                            merged["journey"][jk] = jv
                        if is_leaf and "journey" not in leaf_overrides:
                            leaf_overrides.append("journey")
                    else:
                        merged["journey"] = _deep_copy_journey(value)
                continue
            # Structural + miscellaneous (arc_variant, framing_mode, deprecation flags, etc.).
            merged[key] = value
            if is_leaf and key not in _LEAF_ONLY_FIELDS and key != "journey":
                # Track whether this is an override of an inherited value vs leaf-original.
                if len(chain) > 1 and key in _INHERITED_STRUCTURAL_FIELDS:
                    # Leaf restated something inheritable → counts as override.
                    if key not in leaf_overrides:
                        leaf_overrides.append(key)
            elif not is_leaf and key in _INHERITED_STRUCTURAL_FIELDS and key not in inherited_fields:
                inherited_fields.append(key)

    # Provenance.
    merged["_resolution_provenance"] = {
        "leaf_angle_id": angle_id,
        "parent_chain": list(chain),  # leaf → root
        "chain_depth": len(chain) - 1,
        "inherited_fields": [f for f in inherited_fields if f not in leaf_overrides],
        "leaf_overrides": leaf_overrides,
        "is_deprecated": is_deprecated,
        "successor_angle_id": successor_angle_id,
    }

    if is_deprecated and allow_legacy:
        _LOG.warning(
            "resolved deprecated angle_id %r (successor=%r); pass to legacy compat path only.",
            angle_id,
            successor_angle_id,
        )

    return merged


def _deep_copy_journey(journey: Any) -> Any:
    """Shallow-recursive copy of journey blocks so leaf overrides don't mutate parent."""
    if isinstance(journey, dict):
        return {k: _deep_copy_journey(v) for k, v in journey.items()}
    if isinstance(journey, list):
        return [_deep_copy_journey(item) for item in journey]
    return journey
