"""Tests for phoenix_v4.rendering.science_wrapper.

Mirrors tests/test_teacher_wrapper.py. The science wrapper has no teacher
registry — slot values come from spine_context + the YAML's slot_defaults —
and adds the anti-fabrication rule: named mode requires a real {RESEARCHER}
*and* {STUDY}, else it falls back to generalized.
"""
from __future__ import annotations

import re

import pytest

from phoenix_v4.rendering import science_wrapper
from phoenix_v4.rendering.science_wrapper import (
    apply_wrapper,
    join_wrapped,
    resolve_wrapper,
)


_UNRESOLVED_TOKEN_RE = re.compile(r"\{[A-Z_][A-Z0-9_]*\}")

# A real, citable researcher + study (named-mode provenance).
_NAMED_CTX = {
    "RESEARCHER": "Dr. Lisa Feldman Barrett",
    "STUDY": "How Emotions Are Made",
    "FIELD": "affective neuroscience",
    "FIELD_SHORT": "neuroscience",
    "FINDING": "naming a feeling reduces its physiological charge",
    "MECHANISM": "the brain's prediction-and-construction loop",
}


def test_named_wrapper_resolves_with_real_researcher_and_study():
    """Happy path: a real {RESEARCHER}+{STUDY} → non-empty named wrapper, no
    unresolved slots, deterministic under the seed, researcher actually cited."""
    prefix, suffix = resolve_wrapper(
        section_type="HOOK",
        seed="sw_test_named",
        spine_context=_NAMED_CTX,
    )
    combined = (prefix + " " + suffix).strip()
    assert combined, "expected a non-empty wrapper"
    assert not _UNRESOLVED_TOKEN_RE.search(combined), (
        f"wrapper contains unresolved slot: {combined!r}"
    )
    # Named mode took priority — the researcher is cited by name.
    assert "Barrett" in combined

    # Deterministic with same seed.
    p2, s2 = resolve_wrapper(
        section_type="HOOK",
        seed="sw_test_named",
        spine_context=_NAMED_CTX,
    )
    assert (p2, s2) == (prefix, suffix)


def test_generalized_wrapper_resolves_from_field_only():
    """No researcher/study, but a FIELD is supplied → generalized wrapper, no
    unresolved slots, and the researcher is NOT named."""
    prefix, suffix = resolve_wrapper(
        section_type="HOOK",
        seed="sw_test_generalized",
        spine_context={"FIELD": "stress physiology", "FIELD_SHORT": "stress-physiology"},
    )
    combined = (prefix + " " + suffix).strip()
    assert combined, "expected a non-empty generalized wrapper"
    assert not _UNRESOLVED_TOKEN_RE.search(combined)
    # Generalized mode: no named provenance leaked in.
    assert "Barrett" not in combined


def test_anti_fabrication_named_without_study_falls_back_to_generalized():
    """Anti-fabrication: a RESEARCHER without a STUDY must NOT produce a named
    citation. The resolver falls back to generalized (field-level) framing and
    never invents/uses the researcher's name as if a study existed."""
    prefix, suffix = resolve_wrapper(
        section_type="HOOK",
        seed="sw_test_no_study",
        spine_context={
            "RESEARCHER": "Dr. Solo Researcher",
            "FIELD": "affective neuroscience",
            "FIELD_SHORT": "neuroscience",
            "FINDING": "naming a feeling reduces its physiological charge",
        },
    )
    combined = (prefix + " " + suffix).strip()
    assert combined, "expected generalized fallback to resolve from FIELD"
    assert not _UNRESOLVED_TOKEN_RE.search(combined)
    # The researcher name must not appear — named mode was correctly skipped.
    assert "Solo Researcher" not in combined


def test_anti_fabrication_study_without_researcher_falls_back():
    """Symmetric anti-fabrication: a STUDY without a RESEARCHER also falls back
    to generalized rather than emitting a half-attributed named line."""
    prefix, suffix = resolve_wrapper(
        section_type="HOOK",
        seed="sw_test_no_researcher",
        spine_context={
            "STUDY": "An Anonymous Study",
            "FIELD": "stress physiology",
            "FIELD_SHORT": "stress-physiology",
        },
    )
    combined = (prefix + " " + suffix).strip()
    assert combined, "expected generalized fallback"
    assert not _UNRESOLVED_TOKEN_RE.search(combined)
    assert "Anonymous Study" not in combined


def test_no_context_uses_slot_defaults_safely():
    """Empty spine_context → the YAML slot_defaults (FIELD-level only) fill the
    generalized/composite wrapper. Never emits an unresolved token, and never a
    named researcher (RESEARCHER/STUDY are never defaulted)."""
    prefix, suffix = resolve_wrapper(
        section_type="EXERCISE",
        seed="sw_test_defaults",
        spine_context={},
    )
    combined = prefix + " " + suffix
    assert not _UNRESOLVED_TOKEN_RE.search(combined), (
        f"leaked unresolved token: {combined!r}"
    )
    if combined.strip():
        assert "{" not in combined and "}" not in combined


def test_composite_mode_resolves_with_no_slots():
    """Composite mode requires no slots — even with nothing useful in
    spine_context AND defaults stripped, composite variants resolve."""
    science_wrapper._reset_caches_for_tests()
    # Patch the loaded templates to drop slot_defaults and the FIELD slots from
    # context so named+generalized both fail their slot_requirements, forcing
    # composite (slot_requirements: []).
    real_loader = science_wrapper._load_templates
    templates = dict(real_loader())
    templates["slot_defaults"] = {}
    try:
        science_wrapper._templates_cache = templates
        prefix, suffix = resolve_wrapper(
            section_type="HOOK",
            seed="sw_test_composite",
            spine_context={},
        )
        combined = prefix + " " + suffix
        assert combined.strip(), "composite mode should resolve with no slots"
        assert not _UNRESOLVED_TOKEN_RE.search(combined)
    finally:
        science_wrapper._reset_caches_for_tests()


def test_conclusion_wrapper_goes_to_suffix():
    """Conclusion section types produce suffix framing, not prefix."""
    prefix, suffix = resolve_wrapper(
        section_type="CONCLUSION",
        seed="sw_conclusion_seed",
        spine_context=_NAMED_CTX,
    )
    combined = prefix + suffix
    assert not _UNRESOLVED_TOKEN_RE.search(combined)
    assert suffix and not prefix, (
        f"conclusion should produce suffix only, got prefix={prefix!r} suffix={suffix!r}"
    )


def test_apply_wrapper_returns_body_when_no_wrapper():
    """apply_wrapper with content but a missing templates file → body unchanged."""
    body = "This is the research-cited atom content with many words in it here."
    science_wrapper._reset_caches_for_tests()
    try:
        science_wrapper._templates_cache = {}  # simulate missing/empty templates
        out = apply_wrapper(body, section_type="HOOK", seed="x", spine_context=_NAMED_CTX)
        assert out == body
    finally:
        science_wrapper._reset_caches_for_tests()
    # Empty content → empty out regardless of templates.
    assert apply_wrapper("", section_type="HOOK", seed="x", spine_context=_NAMED_CTX) == ""


# ── join_wrapped: doctrine-intro stitch (mirrors teacher_wrapper) ────────────


def test_join_wrapped_inline_for_ellipsis_prefix():
    """A continuation lead-in (intro wrapper, ends in '...') flows INLINE into the
    body's opening sentence — no paragraph break orphaning the '...is...' lead-in."""
    out = join_wrapped(
        "Research in affective neuroscience consistently finds...",
        "Naming what you feel changes how your body holds it. The charge softens.",
        "",
    )
    assert out == (
        "Research in affective neuroscience consistently finds... "
        "Naming what you feel changes how your body holds it. The charge softens."
    )
    assert "\n\n" not in out
    # The defining regression: an ellipsis lead-in must NOT sit above a blank line.
    assert not re.search(r"\.\.\.\s*\n\n", out)


def test_join_wrapped_inline_for_unicode_ellipsis_prefix():
    """Unicode '…' lead-ins are treated the same as ASCII '...'."""
    out = join_wrapped("The neuroscience evidence points toward one thing…", "The body keeps the score.", "")
    assert out == "The neuroscience evidence points toward one thing… The body keeps the score."
    assert "\n\n" not in out


def test_join_wrapped_paragraph_for_label_prefix():
    """A label-style prefix (exercise wrapper, no trailing ellipsis) keeps its own
    paragraph — it should not run on into the body."""
    out = join_wrapped("A practice grounded in stress-physiology research", "Find a quiet place and sit.", "")
    assert out == "A practice grounded in stress-physiology research\n\nFind a quiet place and sit."


def test_join_wrapped_suffix_is_closing_paragraph():
    """Conclusion suffixes are appended as their own closing paragraph."""
    out = join_wrapped(
        "",
        "The doctrine body sits here.",
        "What the neuroscience research keeps returning to is the body's safety response...",
    )
    assert out == (
        "The doctrine body sits here.\n\n"
        "What the neuroscience research keeps returning to is the body's safety response..."
    )


def test_apply_wrapper_intro_does_not_dangle():
    """End-to-end: a resolved intro lead-in joins inline, never leaving a dangling
    '...' above a paragraph break (the doctrine-intro bleed)."""
    body = (
        "Naming what you feel changes how your body holds it. This is not willpower "
        "or suppression. The charge simply has somewhere to go."
    )
    prefix, suffix = resolve_wrapper(
        section_type="HOOK",
        seed="sw_inline_test",
        spine_context=_NAMED_CTX,
    )
    out = apply_wrapper(
        body,
        section_type="HOOK",
        seed="sw_inline_test",
        spine_context=_NAMED_CTX,
    )
    # HOOK → intro_wrapper → prefix only; every named intro variant ends in an ellipsis.
    assert prefix and not suffix
    if prefix.rstrip().endswith("...") or prefix.rstrip().endswith("…"):
        assert not re.search(r"\.\.\.\s*\n\n", out), "intro lead-in dangles above a paragraph break"
        assert f"{prefix.rstrip()} " in out, "intro lead-in should join inline with a single space"
    assert body.split(".")[0] in out  # doctrine body preserved verbatim
