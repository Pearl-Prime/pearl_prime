"""Teacher-mode XOR music-mode validation for manga series plans.

Pure functions, no I/O, no pipeline coupling. `mode` unset = legacy series, always
valid (so this never changes existing behavior). When `mode` IS set it must be
exactly one of {teacher, music} and consistent with the author fields:
  - teacher-mode: requires teacher_id; must NOT carry a musician_id.
  - music-mode:   requires musician_id; must NOT carry a teacher_id.
"""
from __future__ import annotations

from typing import Any, Mapping, Optional

MODES = ("teacher", "music")


class ModeError(ValueError):
    """Raised when a series plan violates the teacher-XOR-music rule."""


def _truthy(v: Any) -> bool:
    return v is not None and str(v).strip() not in ("", "null", "None")


def resolve_mode(series_plan: Mapping[str, Any]) -> Optional[str]:
    """Return 'teacher' | 'music' | None (None = legacy, mode unset)."""
    mode = series_plan.get("mode")
    if not _truthy(mode):
        return None
    mode = str(mode).strip().lower()
    return mode


def assert_mode_xor(series_plan: Mapping[str, Any]) -> Optional[str]:
    """Validate the XOR rule for one series plan. Returns the resolved mode (or None).

    Raises ModeError on violation. A series with no `mode` is a no-op (legacy path).
    """
    mode = resolve_mode(series_plan)
    if mode is None:
        return None  # legacy series — untouched

    if mode not in MODES:
        raise ModeError(
            f"mode must be one of {MODES}, got {series_plan.get('mode')!r} "
            f"(series {series_plan.get('series_id', '?')})"
        )

    has_teacher = _truthy(series_plan.get("teacher_id"))
    has_musician = _truthy(series_plan.get("musician_id"))
    sid = series_plan.get("series_id", "?")

    if has_teacher and has_musician:
        raise ModeError(
            f"teacher-mode XOR music-mode: series {sid} sets BOTH teacher_id and "
            f"musician_id — a manga series is one archetype, never both."
        )
    if mode == "teacher" and not has_teacher:
        raise ModeError(f"teacher-mode series {sid} must set teacher_id.")
    if mode == "music" and not has_musician:
        raise ModeError(f"music-mode series {sid} must set musician_id.")
    return mode
