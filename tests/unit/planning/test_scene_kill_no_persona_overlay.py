"""SCENE-kill: persona SCENE banks are code-path dead; registry/Qwen owns SCENE."""
from __future__ import annotations

from phoenix_v4.planning.registry_resolver import _PERSONA_OVERLAY_TYPES, _TEACHER_OVERLAY_TYPES


def test_persona_overlay_excludes_scene():
    assert "SCENE" not in _PERSONA_OVERLAY_TYPES
    assert "HOOK" in _PERSONA_OVERLAY_TYPES
    assert "STORY" in _PERSONA_OVERLAY_TYPES


def test_teacher_overlay_still_excludes_scene():
    # Teacher mode already kept SCENE on the registry path.
    assert "SCENE" not in _TEACHER_OVERLAY_TYPES
