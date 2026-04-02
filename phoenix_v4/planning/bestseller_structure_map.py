"""
Bestseller narrative structure → ordered slot sequence (docs/BESTSELLER_STRUCTURES.md).

BG-PR-09: compile-time check that chapter_slot_sequence matches the assigned
chapter_bestseller_structures beat order. Optional steps may be absent; steps
marked SCENE|STORY accept either slot at that position.

Authority: docs/BESTSELLER_STRUCTURES.md "Slot mapping" sections (12 structures).
"""
from __future__ import annotations

import logging
import re
from typing import Optional, Union

logger = logging.getLogger(__name__)

# (optional?, slot_or_alternatives) — alternatives = frozenset of allowed slot types
BeatStep = tuple[bool, Union[str, frozenset[str]]]

SCENE_OR_STORY = frozenset({"SCENE", "STORY"})

# Keys match phoenix_v4.planning.chapter_planner.BESTSELLER_STRUCTURES (snake_case).
BESTSELLER_BEAT_STEPS: dict[str, list[BeatStep]] = {
    "promise_engine": [
        (False, "HOOK"),
        (False, SCENE_OR_STORY),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "EXERCISE"),
        (False, "TAKEAWAY"),
        (False, "INTEGRATION"),
        (True, "PERMISSION"),
        (False, "THREAD"),
    ],
    "gladwell_spiral": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "THREAD"),
    ],
    "van_der_kolk": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "THREAD"),
    ],
    "atomic": [
        (False, "HOOK"),
        (False, SCENE_OR_STORY),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "EXERCISE"),
        (True, "PERMISSION"),
        (False, "THREAD"),
    ],
    "brene_brown": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "INTEGRATION"),
        (True, "PERMISSION"),
        (False, "THREAD"),
    ],
    "myth_killer": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "THREAD"),
    ],
    "case_file": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "THREAD"),
    ],
    "permission_slip": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "PERMISSION"),
        (False, "TAKEAWAY"),
        (False, "THREAD"),
    ],
    "zoom_lens": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "THREAD"),
    ],
    "contrast_engine": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "INTEGRATION"),
        (False, "THREAD"),
    ],
    "ancestor": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "PIVOT"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "INTEGRATION"),
        (False, "THREAD"),
    ],
    "letter": [
        (False, "HOOK"),
        (False, "SCENE"),
        (False, "STORY"),
        (False, "REFLECTION"),
        (False, "TAKEAWAY"),
        (False, "INTEGRATION"),
        (False, "THREAD"),
    ],
}


def normalize_structure_key(raw: str) -> str:
    s = (raw or "").strip().lower()
    s = re.sub(r"[\s\-]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    return s


def _step_label(spec: Union[str, frozenset[str]]) -> str:
    if isinstance(spec, frozenset):
        return "|".join(sorted(spec))
    return spec


def describe_expected_beat_order(structure_key: str) -> str:
    steps = BESTSELLER_BEAT_STEPS.get(structure_key, [])
    parts: list[str] = []
    for opt, spec in steps:
        label = _step_label(spec)
        parts.append(f"[{label}]?" if opt else label)
    return " → ".join(parts)


def _structure_vocab(steps: list[BeatStep]) -> frozenset[str]:
    names: set[str] = set()
    for _, spec in steps:
        if isinstance(spec, frozenset):
            names |= set(spec)
        else:
            names.add(spec)
    return frozenset(names)


def _matches(actual: str, spec: Union[str, frozenset[str]]) -> bool:
    if isinstance(spec, frozenset):
        return actual in spec
    return actual == spec


def validate_chapter_beat_order(structure_key: str, chapter_slots: list[str]) -> Optional[str]:
    """
    Return None if chapter slots satisfy the structure's beat order.

    Uses lockstep matching on slots that belong to this structure's vocabulary only
    (other slot types e.g. COMPRESSION are ignored). Optional steps may be omitted.
    """
    steps = BESTSELLER_BEAT_STEPS.get(structure_key)
    if not steps:
        return f"unknown bestseller structure key {structure_key!r}"

    vocab = _structure_vocab(steps)
    filtered: list[str] = []
    for s in chapter_slots:
        u = str(s).strip().upper()
        if not u:
            continue
        if u in vocab:
            filtered.append(u)

    fi = 0
    for optional, spec in steps:
        if optional:
            if fi < len(filtered) and _matches(filtered[fi], spec):
                fi += 1
            continue
        if fi >= len(filtered):
            want = _step_label(spec)
            return (
                f"missing required slot {want!r} (expected beat order: "
                f"{describe_expected_beat_order(structure_key)}; "
                f"structure-filtered slots: {filtered!r})"
            )
        if not _matches(filtered[fi], spec):
            want = _step_label(spec)
            return (
                f"at structure position expected {want!r}, got {filtered[fi]!r} "
                f"(expected: {describe_expected_beat_order(structure_key)}; "
                f"structure-filtered slots: {filtered!r})"
            )
        fi += 1

    if fi < len(filtered):
        return (
            f"extra slots after completed beat order: {filtered[fi:]!r} "
            f"(expected: {describe_expected_beat_order(structure_key)})"
        )
    return None


def collect_bestseller_beat_order_violations(
    *,
    chapter_slot_sequence: list[list[str]],
    chapter_bestseller_structures: Optional[list[str]],
    chapter_count: int,
) -> list[str]:
    """
    Deterministic messages for chapters where structure is assigned and beat order fails.
    Skips chapters with no/falsy structure name. Unknown structure keys yield a violation.
    """
    if not chapter_bestseller_structures:
        return []

    msgs: list[str] = []
    for ch in range(chapter_count):
        row = chapter_slot_sequence[ch] if ch < len(chapter_slot_sequence) else []
        raw = (
            chapter_bestseller_structures[ch]
            if ch < len(chapter_bestseller_structures)
            else None
        )
        if raw is None or not str(raw).strip():
            continue
        key = normalize_structure_key(str(raw))
        if key not in BESTSELLER_BEAT_STEPS:
            msgs.append(
                f"chapter {ch + 1}: unknown bestseller_structure {raw!r} "
                f"(normalized {key!r}); expected one of {sorted(BESTSELLER_BEAT_STEPS.keys())!r}"
            )
            continue
        err = validate_chapter_beat_order(key, row)
        if err:
            msgs.append(
                f"chapter {ch + 1} structure={raw!r}: {err} "
                f"(actual chapter_slot_sequence: {[str(x).strip().upper() for x in row]!r})"
            )
    return msgs


def apply_bestseller_beat_order_gate(
    *,
    chapter_slot_sequence: list[list[str]],
    chapter_bestseller_structures: Optional[list[str]],
    chapter_count: int,
    enforce: bool,
) -> None:
    """
    If enforce: raise ValueError on any violation.
    If not enforce: log WARNING per violation (deterministic messages).
    """
    violations = collect_bestseller_beat_order_violations(
        chapter_slot_sequence=chapter_slot_sequence,
        chapter_bestseller_structures=chapter_bestseller_structures,
        chapter_count=chapter_count,
    )
    if not violations:
        return
    text = "Bestseller beat order mismatch:\n" + "\n".join(violations)
    if enforce:
        raise ValueError(text)
    for line in violations:
        logger.warning("bestseller_beat_order: %s", line)
