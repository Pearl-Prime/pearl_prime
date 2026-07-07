"""
OPD-116/117 Phase B — book-level angle journey coherence gate.

Runs only when angle_id is set and runtime is long-form (extended_book_2h+).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

from phoenix_v4.planning.angle_journey import (
    is_angle_journey_runtime,
    layer_for_chapter,
    merge_angle_journey,
)


@dataclass
class AngleJourneyCoherenceResult:
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)


def _named_object_for_topic(journey: dict[str, Any], topic_id: str) -> str:
    by_topic = journey.get("named_object_by_topic") or {}
    if not isinstance(by_topic, dict):
        return ""
    val = by_topic.get(topic_id)
    if val is None:
        return ""
    s = str(val).strip()
    if not s or s.upper() == "TODO" or s.startswith("TODO:"):
        return ""
    return s


def evaluate_angle_journey_coherence(
    *,
    angle_id: Optional[str],
    runtime_format: Optional[str],
    topic_id: str,
    chapter_proses: List[str],
    angle_layer_by_chapter: Optional[dict[int, int]] = None,
    enriched_chapters: Optional[List[Any]] = None,
) -> AngleJourneyCoherenceResult:
    """
    Validate angle journey threading across composed chapter bodies.

    Parameters
    ----------
    chapter_proses
        One composed chapter body per chapter (no headings required).
    angle_layer_by_chapter
        1-indexed chapter → layer N from chapter planner / beatmap patch.
    """
    aid = (angle_id or "").strip()
    errors: List[str] = []
    warnings: List[str] = []
    metrics: dict[str, Any] = {"angle_id": aid, "runtime_format": runtime_format}

    if not aid or not is_angle_journey_runtime(runtime_format):
        return AngleJourneyCoherenceResult(
            valid=True,
            warnings=["angle_journey_coherence: SKIPPED (no angle_id or not long-form runtime)"],
            metrics={**metrics, "skipped": True},
        )

    journey = merge_angle_journey(aid)
    layers = list(journey.get("layer_progression") or [])
    metrics["layer_progression"] = layers

    named = _named_object_for_topic(journey, topic_id)
    metrics["named_object"] = named

    n_ch = len(chapter_proses)
    if named:
        missing = [
            i + 1
            for i, prose in enumerate(chapter_proses)
            if named.lower() not in (prose or "").lower()
        ]
        metrics["chapters_missing_named_object"] = missing
        if missing:
            errors.append(
                f"angle_journey: named_object {named!r} absent in chapters {missing}"
            )
    else:
        warnings.append(
            "angle_journey: named_object not commissioned for topic; skipping per-chapter check"
        )

    layer_by_ch = dict(angle_layer_by_chapter or {})
    if not layer_by_ch and enriched_chapters:
        for ch in enriched_chapters:
            ch_num = int(getattr(ch, "number", 0))
            for slot in getattr(ch, "slots", []) or []:
                layer = (getattr(slot, "match_scores", None) or {}).get("angle_layer")
                if layer is not None:
                    layer_by_ch[ch_num] = int(layer)
                    break

    observed_layers: List[tuple[int, int]] = []
    for ch_num in sorted(layer_by_ch.keys()):
        layer = int(layer_by_ch[ch_num])
        observed_layers.append((ch_num, layer))
        expected = layer_for_chapter(ch_num, layers)
        if expected is not None and layer != expected:
            errors.append(
                f"angle_journey: chapter {ch_num} uses layer {layer} but registry maps to layer {expected}"
            )
        for row in layers:
            if not isinstance(row, dict):
                continue
            if int(row.get("layer") or 0) != layer:
                continue
            cr = row.get("chapter_range")
            if isinstance(cr, (list, tuple)) and len(cr) >= 2:
                lo, hi = int(cr[0]), int(cr[1])
                if ch_num < lo or ch_num > hi:
                    errors.append(
                        f"angle_journey: layer {layer} assigned to chapter {ch_num} outside range [{lo},{hi}]"
                    )

    metrics["observed_layers"] = observed_layers

    if observed_layers:
        layer_nums = [layer for _, layer in observed_layers]
        if layer_nums != sorted(layer_nums):
            errors.append(
                f"angle_journey: callback layers not monotonic: {layer_nums}"
            )
        # Final-phase timing derives from the progression itself (was hardcoded
        # layer>=5 / ch<11 for the 5-layer default; the flagship 11-level
        # ladder made that read every mid-book layer as premature). The final
        # layer must not fire before its own declared chapter_range floor —
        # identical behavior for legacy 5-layer angles (L5 range [11,12]).
        final_rows = [
            r for r in layers
            if isinstance(r, dict) and r.get("layer") is not None
        ]
        if final_rows:
            final_layer = max(int(r["layer"]) for r in final_rows)
            final_lo = None
            for r in final_rows:
                cr = r.get("chapter_range")
                if int(r["layer"]) == final_layer and isinstance(cr, (list, tuple)) and len(cr) >= 2:
                    final_lo = int(cr[0])
            if final_lo is not None:
                violations = [
                    (c, l) for c, l in observed_layers if l >= final_layer and c < final_lo
                ]
                if violations:
                    errors.append(
                        f"angle_journey: layer {final_layer} callback fired before chapter {final_lo} "
                        f"(violations: {violations})"
                    )

    angle_slot_chapters = sum(
        1
        for ch in (enriched_chapters or [])
        if any(
            str(getattr(s, "slot_type", "")).strip().upper()
            in ("ANGLE_DEFINITION", "ANGLE_CALLBACK")
            for s in (getattr(ch, "slots", []) or [])
        )
    )
    metrics["chapters_with_angle_slots"] = angle_slot_chapters
    if n_ch > 0:
        share = angle_slot_chapters / n_ch
        metrics["angle_slot_chapter_share"] = share
        if share < 0.8:
            errors.append(
                f"angle_journey: angle slots present in only {share:.0%} of chapters (< 80%)"
            )

    return AngleJourneyCoherenceResult(
        valid=not errors,
        errors=errors,
        warnings=warnings,
        metrics=metrics,
    )
