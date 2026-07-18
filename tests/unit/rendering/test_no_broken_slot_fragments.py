"""F2 register-gate fix — prose normalisation must not break wrapper lead-ins.

Defect ref:
    - OPD-20260518-002 — ``ws_flow_glue_selector_cap_enforcement_20260517``
    - phoenix_v4/rendering/golden_chapter_synthesis.py:_resolve_location_placeholders

Root cause:
    The trailing-punctuation collapse pass
    ``re.sub(r"([.!?])\\1+", r"\\1", t)`` collapsed every ``...`` to ``.``,
    destroying the legitimate ellipses on every wrapper variant defined in
    ``config/catalog_planning/teacher_wrapper_templates.yaml`` (every variant
    in that YAML ends with ``...``).

    Result: rendered books contained orphan lead-ins like
    ``"What Ahjan keeps pointing toward is."`` (no body completion on the
    same paragraph) which the F2 detector in
    ``phoenix_v4/quality/register_gate.py`` correctly HARD_FAILed under
    ``F2.B_sentence_end_preposition`` and ``F2.D_sub_4_word_paragraph``.

These tests cover:
    1. ``_resolve_location_placeholders`` preserves a three-dot ellipsis.
    2. Pathological ``....`` / ``.....`` (4+ dots) clamp back to a canonical
       ``...``.
    3. Accidentally duplicated terminators (``..``, ``!!``, ``??``) still
       collapse to one — the regression we are guarding against in the
       opposite direction.
    4. Every wrapper variant in
       ``config/catalog_planning/teacher_wrapper_templates.yaml`` that ends
       with ``...`` survives the pass intact.
    5. The full ``apply_wrapper`` → ``_resolve_location_placeholders``
       round-trip preserves the ellipsis for the exact templates that were
       producing the rendered ``is.`` / ``with.`` artifacts.
    6. The F2 detector still HARD_FAILs synthetic broken-fragment strings —
       the detector is not relaxed by this fix.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from phoenix_v4.quality.register_gate import evaluate_register
from phoenix_v4.rendering.golden_chapter_synthesis import (
    _resolve_location_placeholders,
)
from phoenix_v4.rendering.teacher_wrapper import (
    _reset_caches_for_tests,
    apply_wrapper,
    resolve_wrapper,
)


# Wrapper templates YAML — single source of truth for valid lead-ins.
_TEMPLATES_PATH = (
    Path(__file__).resolve().parents[3]
    / "config"
    / "catalog_planning"
    / "teacher_wrapper_templates.yaml"
)


# ---------------------------------------------------------------------------
# (1) Single-string preservation
# ---------------------------------------------------------------------------

def test_ellipsis_preserved_on_known_broken_prefix() -> None:
    """The specific Junko/Miyuki/Ahjan rendered artifact must survive intact."""
    s = "What Ahjan keeps pointing toward is..."
    assert _resolve_location_placeholders(s) == s


def test_ellipsis_preserved_in_path_begins_with_prefix() -> None:
    s = "In Ahjan's framework, the path begins with..."
    assert _resolve_location_placeholders(s) == s


def test_ellipsis_preserved_mid_string() -> None:
    """``Wait...what?`` keeps the ellipsis (a legitimate hesitation marker)."""
    s = "She paused. Wait...what was that?"
    assert _resolve_location_placeholders(s) == s


# ---------------------------------------------------------------------------
# (2) Over-long dot runs clamp to canonical ellipsis
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw",
    [
        "Done....",
        "Done.....",
        "Done........",
    ],
)
def test_over_long_dot_runs_clamp_to_ellipsis(raw: str) -> None:
    out = _resolve_location_placeholders(raw)
    assert out == "Done..."


# ---------------------------------------------------------------------------
# (3) Duplicated terminators still collapse (regression guard the OTHER way)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "raw,expected",
    [
        ("Foo!! Bar??", "Foo! Bar?"),
        ("Wait..ok", "Wait.ok"),
        ("Two periods..", "Two periods."),
        ("Quad bangs!!!!", "Quad bangs!"),
    ],
)
def test_duplicated_terminators_still_collapse(raw: str, expected: str) -> None:
    assert _resolve_location_placeholders(raw) == expected


# ---------------------------------------------------------------------------
# (4) Every wrapper variant ending in "..." survives the prose pass
# ---------------------------------------------------------------------------

def _load_wrapper_variants_ending_with_ellipsis() -> list[str]:
    """Pull every variant string ending with ``...`` from the wrapper YAML."""
    if not _TEMPLATES_PATH.exists():
        return []
    data = yaml.safe_load(_TEMPLATES_PATH.read_text(encoding="utf-8")) or {}
    out: list[str] = []
    for mode_block in data.values():
        if not isinstance(mode_block, dict):
            continue
        for wrapper_block in mode_block.values():
            if not isinstance(wrapper_block, dict):
                continue
            pat = wrapper_block.get("pattern")
            if isinstance(pat, str) and pat.strip().endswith("..."):
                out.append(pat.strip())
            for v in wrapper_block.get("variants") or []:
                if isinstance(v, str) and v.strip().endswith("..."):
                    out.append(v.strip())
    return out


def test_every_wrapper_variant_with_ellipsis_survives() -> None:
    # The wrapper YAML moved from trailing-ellipsis lead-ins to complete-sentence
    # lead-ins — the stronger fix for OPD-20260518-002: a lead-in like
    # "...the path begins with..." is now finished in the YAML itself
    # ("...begins with one honest look at what you keep avoiding."), so there is
    # no dangling "..." for the prose pass to collapse. Guard that the YAML still
    # exists (real breakage), but tolerate zero ellipsis variants; any present
    # must still survive the pass intact.
    assert _TEMPLATES_PATH.exists(), f"wrapper templates YAML missing: {_TEMPLATES_PATH}"
    for variant in _load_wrapper_variants_ending_with_ellipsis():
        # Slot tokens like {TEACHER_NAME} are present in the raw YAML — the
        # post-template prose is what matters, but the regex pass operates on
        # the substring after slot resolution. A neutral substitution proves
        # the ellipsis survives regardless of slot value.
        rendered = variant.replace("{TEACHER_NAME}", "Ahjan")
        rendered = rendered.replace("{TEACHING_LINEAGE}", "mindfulness and somatic")
        rendered = rendered.replace("{TRADITION}", "the contemplative tradition")
        rendered = rendered.replace("{TRADITION_SHORT}", "contemplative")
        rendered = rendered.replace("{PRACTICE_NAME}", "the practice")
        assert rendered.endswith("..."), f"sanity: {variant!r} no longer ends in ..."
        out = _resolve_location_placeholders(rendered)
        assert out.endswith("..."), (
            f"ellipsis stripped from wrapper variant {variant!r} → {out!r}"
        )
        # The "broken" F2 artifact is the lead-in ending with a preposition or
        # article plus a single period. The pass must not produce that shape.
        assert not out.endswith(" is."), f"F2 artifact reproduced: {out!r}"
        assert not out.endswith(" with."), f"F2 artifact reproduced: {out!r}"
        assert not out.endswith(" the."), f"F2 artifact reproduced: {out!r}"


# ---------------------------------------------------------------------------
# (5) Full apply_wrapper round-trip preserves ellipsis for the exact broken
#     variants identified in rendered books.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "section_type,seed",
    [
        ("REFLECTION", "inject:gen_z_professionals:anxiety:ahjan:inject:0:0"),
        ("REFLECTION", "depth:anxiety:1:reframe"),
    ],
)
def test_apply_wrapper_then_prose_pass_preserves_ellipsis(
    section_type: str, seed: str
) -> None:
    _reset_caches_for_tests()
    body = "When you work in the ordinary sense, you extract: hours for wage."
    spine_context = {"teacher_id": "ahjan"}
    # Resolve the lead-in independently so we can assert it survives the pass verbatim.
    prefix, _suffix = resolve_wrapper(
        teacher_id="ahjan",
        section_type=section_type,
        seed=seed,
        spine_context=spine_context,
    )
    wrapped = apply_wrapper(
        body,
        teacher_id="ahjan",
        section_type=section_type,
        seed=seed,
        spine_context=spine_context,
    )
    out = _resolve_location_placeholders(wrapped)
    # Inline-join model (PR #1508 follow-up, teacher_wrapper.join_wrapped): the ellipsis
    # lead-in now flows INLINE into the body's opening sentence, so it is no longer
    # paragraph-terminal. The invariant under test is unchanged in spirit — the
    # _resolve_location_placeholders collapse pass must NOT turn "...is..." into
    # "...is." (the F2 sentence-end-preposition artifact). Assert the resolved lead-in
    # survives the prose pass verbatim, ellipsis intact.
    # Lead-ins are now complete sentences (the YAML no longer uses trailing
    # ellipses), so require a proper sentence terminator rather than "..."
    # specifically. The real invariant is the next assertion: the resolved
    # lead-in survives the prose pass verbatim (no F2 collapse to "...is.").
    assert prefix and prefix.rstrip().endswith((".", "!", "?", "...", "…")), (
        f"expected a complete-sentence intro lead-in, got {prefix!r}"
    )
    assert prefix.rstrip() in out, (
        f"wrapper lead-in ellipsis not preserved through prose pass: {out!r}"
    )
    # Guard against the exact collapsed artifacts that motivated the original fix.
    assert "keeps pointing toward is. " not in out
    assert "the path begins with. " not in out


# ---------------------------------------------------------------------------
# (6) F2 detector is NOT relaxed — synthetic broken fragments still HARD_FAIL.
# ---------------------------------------------------------------------------

def test_f2_detector_still_catches_broken_preposition_endings() -> None:
    """``F2.B_sentence_end_preposition`` must still HARD_FAIL synthetic input.

    The ``In {TEACHER}'s framework, the path begins with...`` template
    collapses to ``... begins with.`` under the original regex bug, which
    F2.B catches via the trailing ``with.`` pattern.
    """
    book_text = (
        "Chapter 1\n\n"
        "Here is the mechanism. The system is real.\n\n"
        "In Ahjan's framework, the path begins with.\n\n"
        "The next paragraph that should have completed the thought.\n"
    )
    result = evaluate_register(book_text, teacher_id="ahjan")
    assert result.verdict == "HARD_FAIL", (
        f"expected HARD_FAIL but got {result.verdict} on synthetic broken-prefix book"
    )
    f2_findings = [f for f in result.findings if f.failure_id == "F2"]
    assert f2_findings, "F2 detector failed to fire on synthetic broken fragment"


def test_f2_detector_passes_when_ellipsis_preserved() -> None:
    """If the wrapper renders correctly with ``...`` the F2 detector should not fire."""
    book_text = (
        "Chapter 1\n\n"
        "Here is the mechanism. The system is real and stable underneath.\n\n"
        "In Ahjan's framework, the path begins with quiet observation of the body running its alarm.\n\n"
        "Love, in its many forms, mirrors the aspects of personality we embrace under load.\n"
    )
    result = evaluate_register(book_text, teacher_id="ahjan")
    f2_findings = [f for f in result.findings if f.failure_id == "F2"]
    assert not f2_findings, (
        f"F2 detector incorrectly fired on clean input: {f2_findings}"
    )


def test_register_gate_hard_fails_tradition_placeholder_leak() -> None:
    """Bare 'contemplative' as TRADITION substitute must HARD_FAIL the build."""
    body = "Chapter 1\n\nAccording to contemplative, the path begins.\n"
    result = evaluate_register(body)
    assert result.verdict == "HARD_FAIL"
    assert any(
        f.failure_id == "F2" and f.severity == "HARD_FAIL"
        for f in result.findings
    )
