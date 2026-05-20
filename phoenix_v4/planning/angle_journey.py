"""
OPD-116/117 Phase B — angle-as-journey planning helpers.

Injects ANGLE_DEFINITION / ANGLE_CALLBACK slots for long-form books with angle_id.
Atom content is resolved in enrichment_select; this module owns slot placement + layer map.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from phoenix_v4.planning.angle_resolver import DEFAULT_ANGLE_REGISTRY, load_angle_registry

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# extended_book_2h and deeper long-form runtimes (not micro/short/compact).
ANGLE_JOURNEY_RUNTIMES = frozenset({
    "standard_book",
    "extended_book_2h",
    "deep_book_4h",
    "deep_book_6h",
})

ANGLE_DEFINITION_SLOT = "ANGLE_DEFINITION"
ANGLE_CALLBACK_SLOT = "ANGLE_CALLBACK"

# Ch1 definition block target (paragraphs) for beatmap budgeting metadata.
ANGLE_DEFINITION_PARAGRAPH_WEIGHT = 15


def is_angle_journey_runtime(runtime_format: Optional[str]) -> bool:
    rf = (runtime_format or "").strip()
    if rf in ("micro_book_15", "micro_book_20"):
        return False
    return rf in ANGLE_JOURNEY_RUNTIMES


def merge_angle_journey(angle_id: str, registry: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Walk parent_universal and merge journey blocks (leaf overrides parent keys)."""
    reg = registry if registry is not None else load_angle_registry()
    angles_map = reg.get("angles") or {}
    merged: dict[str, Any] = {}
    chain: list[str] = []
    current: Optional[str] = angle_id
    seen: set[str] = set()
    while current and current not in seen:
        seen.add(current)
        chain.append(current)
        entry = angles_map.get(current)
        if not isinstance(entry, dict):
            break
        journey = entry.get("journey")
        if isinstance(journey, dict):
            for key, val in journey.items():
                if key not in merged or key == "layer_progression":
                    merged[key] = val
                elif key == "named_object_by_topic" and isinstance(val, dict):
                    base = dict(merged.get("named_object_by_topic") or {})
                    base.update(val)
                    merged["named_object_by_topic"] = base
                elif key == "core_mantras" and isinstance(val, list) and val:
                    merged["core_mantras"] = val
        current = entry.get("parent_universal")
        if current:
            current = str(current).strip() or None
    merged["_parent_chain"] = list(reversed(chain))
    return merged


def layer_for_chapter(chapter_1indexed: int, layer_progression: list[dict[str, Any]]) -> Optional[int]:
    """Return journey layer number (1..5) for a 1-indexed chapter, or None."""
    for row in layer_progression or []:
        if not isinstance(row, dict):
            continue
        layer = row.get("layer")
        cr = row.get("chapter_range")
        if layer is None or not isinstance(cr, (list, tuple)) or len(cr) < 2:
            continue
        try:
            lo, hi = int(cr[0]), int(cr[1])
        except (TypeError, ValueError):
            continue
        if lo <= chapter_1indexed <= hi:
            return int(layer)
    return None


def prior_layer_assertion(
    layer: int,
    layer_progression: list[dict[str, Any]],
) -> str:
    """Assertion text for layer-1 (memory-line source for layer N callback)."""
    if layer <= 1:
        return ""
    for row in layer_progression or []:
        if not isinstance(row, dict):
            continue
        if int(row.get("layer") or 0) == layer - 1:
            return str(row.get("assertion") or "").strip()
    return ""


def apply_angle_journey_slots(
    slot_definitions: list[list[str]],
    *,
    angle_id: Optional[str],
    runtime_format: Optional[str],
    registry_path: Optional[Path] = None,
) -> tuple[list[list[str]], dict[int, int], list[str]]:
    """
    Inject ANGLE_DEFINITION (Ch1) and ANGLE_CALLBACK (Ch2+, after HOOK).

    Returns (updated_slots, angle_layer_by_chapter_1indexed, warnings).
    """
    aid = (angle_id or "").strip()
    if not aid or not is_angle_journey_runtime(runtime_format):
        return slot_definitions, {}, []

    reg = load_angle_registry(registry_path or DEFAULT_ANGLE_REGISTRY)
    journey = merge_angle_journey(aid, reg)
    layers = list(journey.get("layer_progression") or [])
    if not layers:
        return slot_definitions, {}, [f"angle_journey: no layer_progression for {aid!r}; slots unchanged"]

    warnings: list[str] = []
    layer_by_ch: dict[int, int] = {}
    out: list[list[str]] = []

    for ch_idx, base_row in enumerate(slot_definitions):
        row = [str(s).strip().upper() for s in base_row]
        ch_num = ch_idx + 1

        if ch_idx == 0:
            if ANGLE_DEFINITION_SLOT not in row:
                ins = 1 if row and row[0] == "HOOK" else 0
                row.insert(ins, ANGLE_DEFINITION_SLOT)
        else:
            layer = layer_for_chapter(ch_num, layers)
            if layer is None:
                out.append(row)
                continue
            layer_by_ch[ch_num] = layer
            assertion = ""
            for lp in layers:
                if isinstance(lp, dict) and int(lp.get("layer") or 0) == layer:
                    assertion = str(lp.get("assertion") or "").strip()
                    break
            if assertion.upper() == "TODO":
                warnings.append(
                    f"angle_journey: ch{ch_num} layer {layer} assertion TODO; callback slot still injected"
                )
            if ANGLE_CALLBACK_SLOT not in row:
                if "HOOK" in row:
                    ins = row.index("HOOK") + 1
                else:
                    ins = min(1, len(row))
                row.insert(ins, ANGLE_CALLBACK_SLOT)

        out.append(row)

    return out, layer_by_ch, warnings


def analogy_lens_for_angle(angle_id: str, registry: Optional[dict[str, Any]] = None) -> str:
    journey = merge_angle_journey(angle_id, registry)
    return str(journey.get("analogy_lens") or "").strip()


def family_default_angle_id(
    analogy_lens: str,
    registry: Optional[dict[str, Any]] = None,
) -> Optional[str]:
    """First universal (no parent_universal) angle sharing analogy_lens."""
    if not analogy_lens:
        return None
    reg = registry if registry is not None else load_angle_registry()
    for aid, entry in (reg.get("angles") or {}).items():
        if not isinstance(entry, dict) or entry.get("parent_universal"):
            continue
        j = entry.get("journey") or {}
        if str(j.get("analogy_lens") or "").strip() == analogy_lens:
            return str(aid)
    return None


def patch_beatmap_angle_journey(beatmap: Any, angle_id: str) -> tuple[dict[int, int], list[str]]:
    """
    Mutate compiled Beatmap chapters in-place to add angle slots.
    Returns (angle_layer_by_chapter_1indexed, warnings).
    """
    from phoenix_v4.planning.beatmap_compile import BeatmapSlot

    rows = [list(ch.slot_definitions or [s.slot_type for s in ch.slots]) for ch in beatmap.chapters]
    updated, layer_by_ch, warns = apply_angle_journey_slots(
        rows,
        angle_id=angle_id,
        runtime_format=getattr(beatmap, "runtime_format", None),
    )
    for ch, new_types in zip(beatmap.chapters, updated):
        by_type = {s.slot_type.strip().upper(): s for s in ch.slots}
        hook_tw = by_type.get("HOOK", ch.slots[0] if ch.slots else None)
        base_tw = int(getattr(hook_tw, "target_words", 320) or 320)
        angle_def_tw = max(base_tw * 3, ANGLE_DEFINITION_PARAGRAPH_WEIGHT * 75)
        angle_cb_tw = max(base_tw, 280)
        new_slots: list[Any] = []
        sec_idx = 0
        for st in new_types:
            sec_idx += 1
            existing = by_type.get(st)
            if existing is not None:
                new_slots.append(existing)
                continue
            tw = angle_def_tw if st == ANGLE_DEFINITION_SLOT else angle_cb_tw
            crit = dict((hook_tw.atom_selection_criteria if hook_tw else {}) or {})
            crit["slot_type"] = st
            crit["angle_layer"] = layer_by_ch.get(ch.number)
            new_slots.append(
                BeatmapSlot(
                    slot_type=st,
                    weight=1.0,
                    target_words=tw,
                    somatic_section_index=sec_idx,
                    atom_selection_criteria=crit,
                    enrichment_hooks=[],
                    emotional_temperature=getattr(hook_tw, "emotional_temperature", "warm"),
                    is_required=True,
                )
            )
        ch.slots = new_slots
        ch.slot_definitions = [s.slot_type for s in new_slots]
    return layer_by_ch, warns
