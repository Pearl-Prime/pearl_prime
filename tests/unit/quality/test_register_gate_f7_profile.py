"""F7 practice-density detector: precision + per-format threshold profile.

Two things under test:
  1. _is_prescribed_action precision (2026-07-07 fix): a prescribed action must
     (a) carry an imperative-set verb, (b) a whole-word timing/step cue, and
     (c) address the reader (you/your). Substring cue matches ("ten" in
     "attention") and third-person narrative ("Priya's laptop is open ...
     thirty minutes") no longer count. Real reader-directed prescriptions,
     including a genuinely over-prescribed chapter, still count — so the gate's
     ability to catch over-prescription is preserved, not weakened.
  2. The extended_book_2h threshold profile (WARN >= 10, FAIL >= 12); the
     default deep_book band (FAIL >= 4, WARN == 3) is unchanged.
"""
from __future__ import annotations

from phoenix_v4.quality.register_gate import (
    F7_FORMAT_THRESHOLDS,
    _detect_f7_practice_density,
    _is_prescribed_action,
)

# A genuine reader-directed prescription: imperative verb + timing cue + you/your.
_PRESCRIPTION = (
    "Notice your breath for ten seconds before the reply. "
    "Let your shoulders drop and hold the exhale after the count."
)
_FILLER = (
    "The office hums along without any urgency this afternoon. "
    "A quiet hour passes at the desk while the light shifts."
)


def _chapter(n: int) -> list[tuple[int, str]]:
    return [(1, "\n\n".join([_PRESCRIPTION] * n + [_FILLER]))]


# ── precision ────────────────────────────────────────────────────────────────
def test_reader_directed_prescription_counts() -> None:
    assert _is_prescribed_action(_PRESCRIPTION) is True


def test_substring_cue_false_positive_excluded() -> None:
    # "ten" ∈ "attention" / "tension"; "for" ∈ "forecast" — not timing cues.
    assert _is_prescribed_action(
        "Notice where your attention goes. Let it rest on the tension you carry, "
        "and name the forecast your mind is following."
    ) is False


def test_third_person_narrative_excluded() -> None:
    # Imperative-set verbs ("open", "start") used as narration + a real timing
    # word ("minutes"), but instructs no reader — must not count.
    assert _is_prescribed_action(
        "Priya's laptop is open to slide fourteen. The stakeholder review "
        "starts in thirty minutes, and she has not opened the deck."
    ) is False


def test_numbered_step_marker_still_matches() -> None:
    # "1."/"2."/"3." markers still count as timing/step cues (substring-matched).
    assert _is_prescribed_action(
        "Follow your breath through the count. 1. Breathe in. 2. Hold. 3. Release."
    ) is True


# ── over-prescription still detected ────────────────────────────────────────
def test_genuine_over_prescription_still_fails() -> None:
    # A chapter that really does drown the reader in timed instructions must
    # still hit FAIL — the precision fix removes noise, not signal.
    findings = _detect_f7_practice_density(_chapter(12), runtime_format="extended_book_2h")
    assert len(findings) == 1 and findings[0].severity == "FAIL"


# ── thresholds ───────────────────────────────────────────────────────────────
def test_default_thresholds_unchanged() -> None:
    findings = _detect_f7_practice_density(_chapter(4))
    assert len(findings) == 1 and findings[0].severity == "FAIL"
    findings = _detect_f7_practice_density(_chapter(3))
    assert len(findings) == 1 and findings[0].severity == "WARN"
    findings = _detect_f7_practice_density(_chapter(2))
    assert findings == []


def test_unknown_format_uses_default() -> None:
    findings = _detect_f7_practice_density(_chapter(4), runtime_format="standard_book")
    assert len(findings) == 1 and findings[0].severity == "FAIL"


def test_extended_book_2h_profile() -> None:
    assert F7_FORMAT_THRESHOLDS["extended_book_2h"] == {"fail_at": 12, "warn_at": 10}
    assert _detect_f7_practice_density(_chapter(9), runtime_format="extended_book_2h") == []
    findings = _detect_f7_practice_density(_chapter(10), runtime_format="extended_book_2h")
    assert len(findings) == 1 and findings[0].severity == "WARN"
    assert findings[0].evidence["runtime_format_profile"] == "extended_book_2h"
    findings = _detect_f7_practice_density(_chapter(12), runtime_format="extended_book_2h")
    assert len(findings) == 1 and findings[0].severity == "FAIL"
