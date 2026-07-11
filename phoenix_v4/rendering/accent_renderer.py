"""Materialize planner-assigned accent beats into chapter slot streams."""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Sequence, Tuple

ACCENT_SLOT_PREFIX = "_ACCENT:"


def _index_for_position(position: str, slot_types: Sequence[str]) -> int:
    st = [str(x).strip().upper() for x in slot_types]
    if position == "before_HOOK":
        return 0
    if position == "after_HOOK":
        return next((i + 1 for i, t in enumerate(st) if t == "HOOK"), 0)
    if position == "before_STORY":
        return next((i for i, t in enumerate(st) if t == "STORY"), len(st))
    if position == "after_EXERCISE":
        idx = max((i for i, t in enumerate(st) if t == "EXERCISE"), default=-1)
        return idx + 1 if idx >= 0 else len(st)
    if position == "after_REFLECTION":
        idx = max((i for i, t in enumerate(st) if t == "REFLECTION"), default=-1)
        return idx + 1 if idx >= 0 else len(st)
    if position == "before_THREAD":
        return next((i for i, t in enumerate(st) if t == "THREAD"), len(st))
    if position == "after_PIVOT":
        idx = max((i for i, t in enumerate(st) if t == "PIVOT"), default=-1)
        return idx + 1 if idx >= 0 else len(st)
    if position == "after_INTEGRATION":
        idx = max((i for i, t in enumerate(st) if t == "INTEGRATION"), default=-1)
        return idx + 1 if idx >= 0 else len(st)
    if position == "after_turning_point":
        story_idxs = [i for i, t in enumerate(st) if t == "STORY"]
        if len(story_idxs) >= 3:
            return story_idxs[2] + 1
        if story_idxs:
            return story_idxs[-1] + 1
        return len(st)
    return len(st)


def insert_accent_beats_into_streams(
    slot_types: List[str],
    slot_proses: List[str],
    accent_beats: Sequence[Mapping[str, Any]],
    accent_bodies: Mapping[str, str],
) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
    types_out = list(slot_types)
    proses_out = list(slot_proses)
    rendered: List[Dict[str, Any]] = []
    ordered = sorted(
        accent_beats,
        key=lambda b: (
            _index_for_position(str(b.get("position") or ""), types_out),
            str(b.get("class") or ""),
        ),
    )
    offset = 0
    for beat in ordered:
        accent_id = str(beat.get("accent_id") or "")
        body = (accent_bodies.get(accent_id) or "").strip()
        if not body:
            continue
        position = str(beat.get("position") or "")
        insert_at = _index_for_position(position, types_out) + offset
        insert_at = max(0, min(insert_at, len(types_out)))
        cls = str(beat.get("class") or "ACCENT")
        types_out.insert(insert_at, f"{ACCENT_SLOT_PREFIX}{cls}")
        proses_out.insert(insert_at, body)
        rendered.append(
            {
                "accent_id": accent_id,
                "class": cls,
                "position": position,
                "chapter_insert_index": insert_at,
                "body": body,
                "rendered_excerpt": body[:220].replace("\n", " ").strip(),
                "provenance": (beat.get("keys") or {}).get("supply_provenance")
                if isinstance(beat.get("keys"), dict)
                else beat.get("supply_provenance"),
            }
        )
        offset += 1
    return types_out, proses_out, rendered
