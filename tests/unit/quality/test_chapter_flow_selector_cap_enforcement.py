"""ws_flow_glue_selector_cap_enforcement_20260517 / OPD-20260518-002 follow-up.

Background
----------
Junko + Miyuki standard_book smokes on 2026-05-19 showed identical chapter_flow
gate FAILs: MISSING_CLEAR_POINT and WEAK_TRANSITIONS on chapters 4, 8, 9, 12
even though the rendered prose contained valid clear-point and transitional
sentences. Root cause: ``_THESIS_CUES`` and ``_TRANSITION_CUES`` were narrow
phrase sets that only matched a handful of canonical teacher-voice formulations
("the point is", "what this means", "this is not", "principle:"). Bridge
families introduced by OPD-109 and modern teacher prose emit semantically
equivalent shapes — "Contradiction is not the problem here, it is the data.",
"What follows is not a test, it is an invitation.", "Watch how the same shape
lands in another life." — that the gate failed to recognize, producing
false-FAILs on otherwise well-formed chapters.

These tests pin:
  1. Specific expansion phrases now register as thesis_hits / transition_hits.
  2. Pre-existing thesis/transition cues continue to register (no regressions).
  3. Sentences that look thesis-like but are NOT in the expanded list still
     fail — i.e. the expansion is targeted, not a blanket relaxation.
"""
from __future__ import annotations

import pytest

from phoenix_v4.quality.chapter_flow_gate import (
    _THESIS_CUES,
    _TRANSITION_CUES,
    evaluate_chapter_flow,
)


# ---------------------------------------------------------------------------
# Cue-list pinning: the additions must be present
# ---------------------------------------------------------------------------

_EXPECTED_NEW_THESIS_CUES = (
    "is not the problem",
    "is the data",
    "is the practice",
    "is not a sign",
    "is meant to",
    "is the entry",
    "is not a test",
    "is not just",
    "what follows",
    "what remains",
    "the truth",
)

_EXPECTED_NEW_TRANSITION_CUES = (
    "watch how",
    "sit with",
    "underneath",
    "beneath",
    "one thread",
    "across",
    "step into",
    "the seeing",
    "in another",
)


@pytest.mark.parametrize("cue", _EXPECTED_NEW_THESIS_CUES)
def test_new_thesis_cue_present_in_module(cue: str) -> None:
    """Pin: each expansion cue lives in ``_THESIS_CUES``."""
    assert cue in _THESIS_CUES, (
        f"Expected new thesis cue {cue!r} missing from _THESIS_CUES. "
        "ws_flow_glue_selector_cap_enforcement expansion regressed."
    )


@pytest.mark.parametrize("cue", _EXPECTED_NEW_TRANSITION_CUES)
def test_new_transition_cue_present_in_module(cue: str) -> None:
    """Pin: each expansion cue lives in ``_TRANSITION_CUES``."""
    assert cue in _TRANSITION_CUES, (
        f"Expected new transition cue {cue!r} missing from _TRANSITION_CUES. "
        "ws_flow_glue_selector_cap_enforcement expansion regressed."
    )


# ---------------------------------------------------------------------------
# Pre-existing cues survive expansion (no regressions)
# ---------------------------------------------------------------------------

_LEGACY_THESIS_CUES = ("principle:", "the point is", "what this means", "this is not")
_LEGACY_TRANSITION_CUES = (
    "that moment", "which means", "so when", "this is why",
    "in practice", "for example", "here is", "because",
)


@pytest.mark.parametrize("cue", _LEGACY_THESIS_CUES)
def test_legacy_thesis_cue_preserved(cue: str) -> None:
    assert cue in _THESIS_CUES, f"Legacy thesis cue {cue!r} was lost during expansion."


@pytest.mark.parametrize("cue", _LEGACY_TRANSITION_CUES)
def test_legacy_transition_cue_preserved(cue: str) -> None:
    assert cue in _TRANSITION_CUES, f"Legacy transition cue {cue!r} was lost during expansion."


# ---------------------------------------------------------------------------
# Functional pinning: chapter prose that previously false-FAILed now passes
# ---------------------------------------------------------------------------

# This chapter is a stripped-down version of Junko Ch 4 from the 2026-05-19
# standard_book smoke. The old cue lists found 0 thesis hits and 2 transition
# hits (threshold 3), failing both MISSING_CLEAR_POINT and WEAK_TRANSITIONS.
# Every assertion below describes a real sentence shape from rendered prose.
JUNKO_CH4_LIKE_PROSE = """
The client is satisfied. He knows the client is satisfied.

Watch how the same shape lands in another life.

He puts his phone face-down on the counter. He looks at it. The demo was four days ago. The workaround held. The client is asking about onboarding. He picks the phone back up. He is still in it.

Sit with Junko's mindfulness and somatic long enough and one thread emerges.

What is given is given. The catching up is the rest of the life.

What follows is not a test. It is an invitation to feel the mechanism while it is still warm.

Start with the hand that hovered instead of moving. That freeze is the entry point.

Move your body once before you continue. Any movement counts.

Ancestor Greeting (Three-Generation Reach). Sit at the home altar or at a simple cleared surface. Light a single candle. Speak the names of three generations of women on your mother's side. After each name, pause for thirty seconds.

Now, observe the aftereffect of shaking. Small tremors can discharge excess adrenaline. If your body feels lighter or less pressurized, that indicates release occurred. Tremoring is a natural regulation mechanism in mammals. You allowed it deliberately.

There is no wrong response here.

Carry this forward: the sensations you experience when the alarm runs are not signs that something is going wrong. They are the alarm designed to do. Let your next small action prove whether it is true.

What remains is the moment after the alarm fires, when your body still wants to obey a prediction.

Contradiction is not the problem here. It is the data.
"""


def test_modern_teacher_prose_passes_thesis_check() -> None:
    """Junko Ch 4 prose: previously thesis_hits=0; now must be >=1."""
    result = evaluate_chapter_flow(JUNKO_CH4_LIKE_PROSE)
    assert result.metrics["thesis_hits"] >= 1, (
        f"Expected >=1 thesis hit in modern teacher prose; got "
        f"{result.metrics['thesis_hits']}. Errors: {result.errors}"
    )
    assert "MISSING_CLEAR_POINT" not in result.errors


def test_modern_teacher_prose_passes_transition_check() -> None:
    """Junko Ch 4 prose: previously transition_hits=2 (threshold 3); now must be >=3."""
    result = evaluate_chapter_flow(JUNKO_CH4_LIKE_PROSE)
    assert result.metrics["transition_hits"] >= 3, (
        f"Expected >=3 transition hits in modern teacher prose; got "
        f"{result.metrics['transition_hits']}. Errors: {result.errors}"
    )
    assert "WEAK_TRANSITIONS" not in result.errors


# ---------------------------------------------------------------------------
# Negative: the expansion is targeted, not a blanket relaxation
# ---------------------------------------------------------------------------

GENERIC_FLAT_PROSE = """
The room contains a chair, a table, and a window. The window faces north.

Outside there are clouds. Sometimes there are not clouds. The chair is wooden.

I sat in the chair for several minutes. Then I stood up. Then I sat back down.

The clouds did not change. The chair did not move. The table remained where it was.

I looked at the table for a while. Then I looked at the window. Then I closed my eyes.

When I opened them, nothing had shifted. The afternoon was long. The clouds returned.

I drank some water. I noticed the water was cold. The glass made a small sound on the table.

Eventually the room grew darker. I turned on a lamp. The lamp lit the chair from behind.

I sat in the chair until the room was fully dark, then I stood up and left the room.

Nothing remarkable happened that afternoon. The chair was not different than before.

I went into another room. There was another chair there. I did not sit in that chair.

I walked into the kitchen. The kettle was on the counter. I did not turn the kettle on.

After some time I went back to the first room. The first chair was still there.
"""


def test_generic_prose_without_thesis_signal_still_fails() -> None:
    """Targeted expansion: generic descriptive prose without ANY clear-point signal still FAILs."""
    result = evaluate_chapter_flow(GENERIC_FLAT_PROSE)
    # This prose has no thesis cues at all; the gate should still flag it.
    assert result.metrics["thesis_hits"] == 0, (
        f"Expected 0 thesis hits in generic flat prose, got {result.metrics['thesis_hits']}. "
        "Expansion may be too broad."
    )
    assert "MISSING_CLEAR_POINT" in result.errors


# ---------------------------------------------------------------------------
# Cue list size sanity
# ---------------------------------------------------------------------------

def test_thesis_cues_count_matches_expansion() -> None:
    """Sanity: 4 legacy + 11 expansion = 15 cues."""
    assert len(_THESIS_CUES) == 15, (
        f"Expected 15 thesis cues (4 legacy + 11 expansion); got {len(_THESIS_CUES)}. "
        "Update count or expansion list."
    )


def test_transition_cues_count_matches_expansion() -> None:
    """Sanity: 13 legacy + 9 expansion = 22 cues."""
    assert len(_TRANSITION_CUES) == 22, (
        f"Expected 22 transition cues (13 legacy + 9 expansion); got {len(_TRANSITION_CUES)}. "
        "Update count or expansion list."
    )
