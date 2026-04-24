"""Tests for phoenix_v4.rendering.teacher_wrapper."""
from __future__ import annotations

import re

import pytest

from phoenix_v4.rendering import teacher_wrapper
from phoenix_v4.rendering.teacher_wrapper import (
    apply_wrapper,
    resolve_wrapper,
)


_UNRESOLVED_TOKEN_RE = re.compile(r"\{[A-Z_][A-Z0-9_]*\}")


def test_named_wrapper_resolves_for_teacher_with_display_name():
    """Happy path: teacher with display_name + tradition metadata → non-empty wrapper,
    no unresolved slots, deterministic under the seed."""
    # ahjan is in teacher_registry.yaml with display_name="Ahjan"
    spine_context = {
        "teacher_id": "ahjan",
        "topic": "anxiety",
        "persona_id": "midlife_women",
        "tradition": "Theravada forest",
        "tradition_short": "forest",
        "teaching_lineage": "contemplative forest",
    }
    prefix, suffix = resolve_wrapper(
        teacher_id="ahjan",
        section_type="HOOK",
        seed="tw_test_named",
        spine_context=spine_context,
    )
    combined = (prefix + " " + suffix).strip()
    assert combined, "expected a non-empty wrapper"
    assert not _UNRESOLVED_TOKEN_RE.search(combined), (
        f"wrapper contains unresolved slot: {combined!r}"
    )
    # Should be "Ahjan"-flavored (named mode took priority over generalized)
    assert "Ahjan" in combined

    # Deterministic with same seed
    p2, s2 = resolve_wrapper(
        teacher_id="ahjan",
        section_type="HOOK",
        seed="tw_test_named",
        spine_context=spine_context,
    )
    assert (p2, s2) == (prefix, suffix)


def test_no_teacher_id_noop():
    """No teacher_id → ("", "") and apply_wrapper returns content unchanged."""
    body = "This is the teacher atom content with many words in it here."
    prefix, suffix = resolve_wrapper(
        teacher_id=None,
        section_type="HOOK",
        seed="tw_test_notid",
        spine_context={},
    )
    assert (prefix, suffix) == ("", "")
    assert apply_wrapper(body, teacher_id=None, section_type="HOOK", seed="x") == body
    assert apply_wrapper(body, teacher_id="", section_type="HOOK", seed="x") == body


def test_unresolved_slot_falls_through_then_safe_default():
    """When no slot data is available for a given wrapper variant, the resolver
    must skip those variants. If none resolve under the current slot map, it
    returns ("", "") rather than emitting "{TEACHER_NAME}" into prose."""
    # Teacher with no registry entry and no spine overrides — no TEACHER_NAME
    # slot is available, so named-mode variants cannot resolve. The resolver
    # should fall through to generalized mode (TRADITION default fills in from
    # slot_defaults), producing a valid wrapper with no unresolved tokens.
    prefix, suffix = resolve_wrapper(
        teacher_id="__nonexistent_teacher__",
        section_type="EXERCISE",
        seed="tw_test_fallthrough",
        spine_context={},
    )
    combined = prefix + " " + suffix
    assert not _UNRESOLVED_TOKEN_RE.search(combined), (
        f"leaked unresolved token: {combined!r}"
    )
    # Either generalized resolved (preferred) or nothing did — both are safe.
    if combined.strip():
        # Must not contain TEACHER_NAME since named mode should have been skipped
        assert "Ahjan" not in combined
        assert "{" not in combined and "}" not in combined


def test_conclusion_wrapper_goes_to_suffix():
    """Conclusion section types produce suffix framing, not prefix."""
    spine_context = {
        "teacher_id": "ahjan",
        "tradition": "Theravada forest",
        "tradition_short": "forest",
        "teaching_lineage": "contemplative forest",
    }
    prefix, suffix = resolve_wrapper(
        teacher_id="ahjan",
        section_type="CONCLUSION",
        seed="tw_conclusion_seed",
        spine_context=spine_context,
    )
    combined = prefix + suffix
    assert not _UNRESOLVED_TOKEN_RE.search(combined)
    assert suffix and not prefix, (
        f"conclusion should produce suffix only, got prefix={prefix!r} suffix={suffix!r}"
    )
