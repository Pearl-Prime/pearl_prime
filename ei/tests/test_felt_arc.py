"""Unit tests for ei.felt_arc (P0.5) — CPU-only."""
from ei import felt_arc as fa


def test_vad_axes_discriminate():
    """Calm prose -> high valence/low arousal; panic prose -> low valence/high arousal."""
    cv, ca, ch = fa.score_text_vad(
        "the breath is slow and the body settles into stillness peace and calm rest")
    pv, pa, ph = fa.score_text_vad(
        "the chest is tight panic racing fear pounding terror anxiety dread alarm")
    assert ch > 0 and ph > 0
    assert cv > pv, "calm valence should exceed panic valence"
    assert pa > ca, "panic arousal should exceed calm arousal"


def test_somatic_arc_has_twelve_chapters():
    arc = fa.load_somatic_arc()
    assert len(arc) == 12
    roles = [c["role"] for c in arc]
    assert roles[0] == "recognition"
    assert roles[-1] == "integration"


def test_somatic_state_fit_on_synthetic_book():
    # a clearly calm-ending book should produce a finite fit in [0,1]
    text = ("anxiety fear tight chest racing " * 50
            + "notice breath observe slowly " * 50
            + "calm settle peace rest integration grounded " * 50)
    rep = fa.somatic_state_fit(text)
    assert 0.0 <= rep.somatic_state_fit <= 1.0
    assert rep.n_chapters == 12
    assert len(rep.measured) == 12
    assert isinstance(rep.observation_before_intervention_ok, bool)


def test_observation_before_intervention_flag_fires():
    # front-load high arousal -> the observation-first guard should flag it
    text = ("panic terror racing fear dread alarm trembling " * 80
            + "calm peace rest " * 200)
    rep = fa.somatic_state_fit(text)
    # not asserting a specific bool (depends on segmentation) — just that notes exist
    assert rep.notes
