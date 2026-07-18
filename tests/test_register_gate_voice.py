"""
Tests for the voice-doctrine detectors added to phoenix_v4.quality.register_gate.

Covers the two Phase-2 voice-doctrine checks wired into the register gate:

  F12 — un-wrapped voice-shift lint (OVERLAY_SPEC §13 "Stage-6 voice-shift lint";
        cap BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01). FAIL on a raw teacher /
        science register that bypassed the wrapper; WARN on a thin wrapper.
        Shares the VoiceOutOfZoneError vocabulary with D12's voice_braid_gate.

  F13 — dwell-beat / integration-starvation check (OVERLAY_SPEC §7.3 dwell
        contract + §13 criterion #13). FAIL when 3+ consecutive named insights
        run with no dwell beat between them.

All detectors are deterministic (no LLM API — CLAUDE.md Tier policy). Synthetic
chapters are written to isolate the detector under test: F12/F13 example text is
constructed to avoid tripping the unrelated F1–F7 detectors (notably F2's
dangling-preposition rule), so each verdict reflects the new check alone.
"""
from __future__ import annotations

import pytest

from phoenix_v4.quality.register_gate import (
    _detect_f12_unwrapped_voice_shift,
    _detect_f13_dwell_starvation,
    _f13_is_dwell_beat,
    _f13_is_insight,
    _split_chapters,
    evaluate_register,
)


# ─────────────────────────────────────────────────────────────────────────────
# F12 — un-wrapped voice-shift lint
# ─────────────────────────────────────────────────────────────────────────────

def test_f12_fails_on_unwrapped_science_shift():
    """
    A raw 'Dr. X proved …' citation that bypassed the science wrapper must FAIL.

    This is the canonical un-wrapped science voice-shift: the register changes to
    science-citation prose with a named researcher and a proof verb, but no
    wrapper attribution ('Research in …', 'the … evidence', 'According to …')
    routed it. Per OVERLAY_SPEC §13 this is F12 FAIL.
    """
    body = (
        "Chapter 1\n\n"
        "You wake before the alarm again. The ceiling is the same gray.\n\n"
        "Dr. Caldwell proved that chronic stress shortens telomeres in every dividing cell.\n\n"
        "The body keeps a ledger nobody ever agreed to keep.\n"
    )
    result = evaluate_register(body)
    f12 = [f for f in result.findings if f.failure_id == "F12"]
    assert any(f.severity == "FAIL" for f in f12), "raw science citation must produce F12 FAIL"
    fail = next(f for f in f12 if f.severity == "FAIL")
    # Shared D12 vocabulary requirement.
    assert fail.evidence["error_class"] == "VoiceOutOfZoneError"
    assert fail.evidence["register"] == "science"
    assert fail.evidence["cap"] == "BESTSELLER-FIT-PLAN-VOICE-DOCTRINE-V1-01"
    # Un-wrapped shift drives the book verdict to FAIL.
    assert result.verdict == "FAIL"


def test_f12_fails_on_unwrapped_teacher_shift():
    """A raw 'Master X says …' (banned generalized-mode anti-pattern) must FAIL."""
    body = (
        "Chapter 1\n\n"
        "You sit with the breath because nothing else will hold still.\n\n"
        "Master Lin says the breath is the only honest teacher in the room.\n\n"
        "You already suspected as much.\n"
    )
    result = evaluate_register(body)
    f12_fail = [f for f in result.findings if f.failure_id == "F12" and f.severity == "FAIL"]
    assert f12_fail, "raw 'Master X says' must produce F12 FAIL"
    assert f12_fail[0].evidence["register"] == "teacher"
    assert f12_fail[0].evidence["error_class"] == "VoiceOutOfZoneError"


def test_f12_passes_on_wrapped_science_shift():
    """
    The SAME science claim, routed through the generalized science wrapper
    ('Research in … consistently finds …'), must NOT produce an F12 FAIL.
    """
    body = (
        "Chapter 1\n\n"
        "You wake before the alarm again.\n\n"
        "Research in psychophysiology consistently finds that chronic stress shortens telomeres.\n\n"
        "The body keeps a ledger.\n"
    )
    result = evaluate_register(body)
    f12_fail = [f for f in result.findings if f.failure_id == "F12" and f.severity == "FAIL"]
    assert not f12_fail, "wrapped science framing must not FAIL F12"


def test_f12_passes_on_wrapped_teacher_shift():
    """A named-mode teacher wrapper ('In X's framework, …') must NOT FAIL F12."""
    body = (
        "Chapter 1\n\n"
        "You sit with the breath because nothing else will hold still.\n\n"
        "In Ahjan's framework, the path begins with the breath and the body that carries it.\n\n"
        "You already suspected as much.\n"
    )
    result = evaluate_register(body)
    f12_fail = [f for f in result.findings if f.failure_id == "F12" and f.severity == "FAIL"]
    assert not f12_fail, "wrapped teacher framing must not FAIL F12"


def test_f12_warns_on_thin_wrapper():
    """
    A wrapper stem that resolved degenerately — a generalized 'According to <Named
    individual>,' with no real payload — is a thin wrapper: WARN, not FAIL.
    """
    body = (
        "Chapter 1\n\n"
        "You wake before the alarm again.\n\n"
        "According to Dr. Reyes, the body learns fear faster than it unlearns it.\n\n"
        "You feel that in the back of your neck.\n"
    )
    chapters = _split_chapters(body)
    findings = _detect_f12_unwrapped_voice_shift(chapters)
    f12_warn = [f for f in findings if f.failure_id == "F12" and f.severity == "WARN"]
    assert f12_warn, "a generalized stem naming an individual must WARN as a thin wrapper"
    assert all(f.evidence["error_class"] == "VoiceOutOfZoneError" for f in f12_warn)
    # A thin wrapper is a WARN, never a FAIL.
    assert not any(f.failure_id == "F12" and f.severity == "FAIL" for f in findings)


def test_f12_silent_on_clean_prose():
    """Ordinary authorial prose with no register shift must produce no F12."""
    body = (
        "Chapter 1\n\n"
        "You wake before the alarm. The ceiling is gray. Your shoulders drop a half inch.\n\n"
        "The kettle clicks and you let the cup warm your hands.\n"
    )
    findings = _detect_f12_unwrapped_voice_shift(_split_chapters(body))
    assert findings == [], "clean prose must not produce any F12 finding"


# ─────────────────────────────────────────────────────────────────────────────
# F13 — dwell-beat / integration starvation (criterion #13)
# ─────────────────────────────────────────────────────────────────────────────

def test_f13_warns_on_four_insight_run_with_no_dwell():
    """
    Four consecutive named insights with no dwell beat between them is integration
    starvation — advisory WARN only (injectors disabled 2026-07-01).
    """
    body = (
        "Chapter 1\n\n"
        "The mechanism is hypervigilance dressed as competence. "
        "Which means the calm you perform costs more than the panic you ever showed. "
        "The real cost is the relationships you ration to keep yourself safe. "
        "This is why the body never fully stands down at night.\n"
    )
    result = evaluate_register(body)
    f13 = [f for f in result.findings if f.failure_id == "F13"]
    warn = next(f for f in f13 if f.severity == "WARN")
    assert warn.evidence["criterion"] == 13
    assert warn.evidence["consecutive_insights"] >= 3
    assert result.verdict in ("WARN", "ADVISORY", "PASS")


def test_f13_passes_on_insight_dwell_insight():
    """
    Insight → dwell beat → insight → dwell beat → insight is correctly paced: each
    insight gets a beat to land. Must NOT trip F13.
    """
    body = (
        "Chapter 1\n\n"
        "The mechanism is hypervigilance dressed as competence. "
        "Your shoulders already know; they have been up near your ears since the first page. "
        "Which means the calm you perform costs more than the panic you hide. "
        "Read that again. Then stop reading for a moment. "
        "The real cost is the relationships you ration to stay safe.\n"
    )
    result = evaluate_register(body)
    f13 = [f for f in result.findings if f.failure_id == "F13"]
    assert not f13, "insight-dwell-insight pacing must not trip F13"


def test_f13_passes_on_two_consecutive_insights():
    """Two stacked insights are a §13 'warning'-band issue, not the FAIL band (3+)."""
    body = (
        "Chapter 1\n\n"
        "The mechanism is hypervigilance dressed as competence. "
        "Which means the calm you perform costs more than the panic you hide. "
        "You wake before the alarm again.\n"
    )
    findings = _detect_f13_dwell_starvation(_split_chapters(body))
    assert findings == [], "exactly two consecutive insights must not FAIL (threshold is 3)"


def test_f13_long_sensory_sentence_is_not_a_dwell_beat():
    """
    A sensory sentence longer than ~40 words is NOT a dwell beat (§7.3: 'a held
    breath, not a passage'), so it does not break a consecutive-insight run.
    """
    long_fake_dwell = (
        "Your shoulders and your jaw and your ribs and your chest and your throat and your "
        "hands and your heart and your belly and your spine and your neck and your feet all "
        "carry it, but this sentence runs far too long to be a held breath and so it is not "
        "a dwell beat at all under the contract."
    )
    assert not _f13_is_dwell_beat(long_fake_dwell)
    body = (
        "Chapter 1\n\n"
        "The mechanism is hypervigilance dressed as competence. "
        f"{long_fake_dwell} "
        "Which means the calm you perform costs more than the panic you hide. "
        "The real cost is the relationships you ration to stay safe.\n"
    )
    findings = _detect_f13_dwell_starvation(_split_chapters(body))
    assert any(f.severity == "WARN" for f in findings), (
        "a >40-word sensory passage is not a dwell beat; the insight run must still WARN"
    )


def test_f13_resets_run_per_chapter():
    """A well-paced chapter does not contaminate a later starved chapter's count."""
    body = (
        "Chapter 1\n\n"
        "The mechanism is hypervigilance. Your shoulders drop a half inch. You wake early again.\n\n"
        "Chapter 2\n\n"
        "The mechanism is shame. Which means you hide it. The real cost is connection lost. "
        "This is the pattern underneath all of it.\n"
    )
    findings = _detect_f13_dwell_starvation(_split_chapters(body))
    warns = [f for f in findings if f.severity == "WARN"]
    assert len(warns) == 1, "only the starved chapter should WARN"
    assert warns[0].chapter == 2


def test_f13_insight_and_dwell_classifiers():
    """Unit-level sanity on the two classifiers the detector composes."""
    assert _f13_is_insight("The mechanism is hypervigilance dressed as competence.")
    assert _f13_is_insight("Which means the calm you perform costs more than you think.")
    assert not _f13_is_insight("You wake before the alarm again and the ceiling is gray.")
    # Body landing, held silence, and single concrete consequence are dwell beats.
    assert _f13_is_dwell_beat("Your shoulders drop a half inch.")
    assert _f13_is_dwell_beat("Read that again. The next sentence can wait.")
    assert _f13_is_dwell_beat("Which means the next time their name lights up the phone, you already know.")


# ─────────────────────────────────────────────────────────────────────────────
# Routing — both detectors surface remediation lanes
# ─────────────────────────────────────────────────────────────────────────────

def test_voice_findings_route_to_lanes():
    """F12 and F13 each contribute a suggested remediation lane."""
    body = (
        "Chapter 1\n\n"
        "Dr. Caldwell proved that chronic stress shortens telomeres in every dividing cell.\n\n"
        "The mechanism is hypervigilance. Which means you never rest. The real cost is connection. "
        "This is the pattern underneath it.\n"
    )
    result = evaluate_register(body)
    lanes_blob = " || ".join(result.suggested_lanes)
    assert "wrapper" in lanes_blob or "VoiceOutOfZoneError" in lanes_blob, result.suggested_lanes
    assert "dwell" in lanes_blob or "§7.3" in lanes_blob, result.suggested_lanes


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-v"]))
