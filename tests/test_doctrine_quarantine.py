"""Tests for ACT-010: doctrine quarantine in enrichment_select.py (BSG-010).

Terms used come directly from _SOMATIC_QUARANTINE_TERMS (synced from
phoenix_v4/quality/frame_governor.py :: SPIRITUAL_LEXICON).
"""

from phoenix_v4.planning.enrichment_select import _is_doctrine_quarantined


def test_blocked_term_excluded_somatic_first():
    """Atom containing a quarantine term is blocked in somatic_first frame."""
    assert _is_doctrine_quarantined(
        "Your soul contract was written before birth.", "somatic_first"
    )


def test_blocked_term_chakra_excluded_somatic_first():
    """Another quarantine term (chakra) is blocked in somatic_first."""
    assert _is_doctrine_quarantined(
        "Balancing your chakra centres restores harmony.", "somatic_first"
    )


def test_blocked_term_vibration_excluded_somatic_first():
    """Term 'vibration' is blocked in somatic_first."""
    assert _is_doctrine_quarantined(
        "The vibration of love heals all wounds.", "somatic_first"
    )


def test_allowed_in_spiritual_first():
    """Quarantine terms are permitted when frame is spiritual_first."""
    assert not _is_doctrine_quarantined(
        "Your soul contract was written before birth.", "spiritual_first"
    )


def test_chakra_allowed_in_spiritual_first():
    assert not _is_doctrine_quarantined(
        "Balancing your chakra centres restores harmony.", "spiritual_first"
    )


def test_neutral_not_blocked():
    """Somatic/body-language prose is not blocked in any frame."""
    assert not _is_doctrine_quarantined(
        "Your nervous system responds to perceived threats before your thinking brain.",
        "somatic_first",
    )


def test_empty_not_blocked():
    """Empty string is never quarantined."""
    assert not _is_doctrine_quarantined("", "somatic_first")


def test_none_frame_blocks_spiritual_term():
    """Unset (empty) frame behaves like somatic_first — quarantine applies."""
    assert _is_doctrine_quarantined(
        "The akashic records hold your full history.", ""
    )


def test_case_insensitive():
    """Quarantine check is case-insensitive."""
    assert _is_doctrine_quarantined("CHAKRA ALIGNMENT IS ESSENTIAL.", "somatic_first")


def test_case_insensitive_mixed():
    """Mixed-case term is still caught."""
    assert _is_doctrine_quarantined("Dive into the Akashic records.", "somatic_first")


def test_partial_word_match_cosmic():
    """'cosmic' as a substring of a word is caught (term-in-text substring match)."""
    assert _is_doctrine_quarantined(
        "This is a cosmic reordering of your reality.", "somatic_first"
    )


def test_unrelated_frame_not_spiritual_first_blocks():
    """Any frame that is not 'spiritual_first' applies quarantine."""
    assert _is_doctrine_quarantined(
        "Past life memories shape present fears.", "somatic_first"
    )


def test_divine_timing_blocked():
    """Multi-word term 'divine timing' is blocked."""
    assert _is_doctrine_quarantined(
        "Trust in divine timing for your healing.", "somatic_first"
    )


def test_sacred_geometry_blocked():
    """Multi-word term 'sacred geometry' is blocked."""
    assert _is_doctrine_quarantined(
        "Sacred geometry underlies all biological structures.", "somatic_first"
    )


def test_light_body_blocked():
    """Multi-word term 'light body' is blocked."""
    assert _is_doctrine_quarantined(
        "Activate your light body for ascension.", "somatic_first"
    )


def test_energy_field_blocked():
    """Multi-word term 'energy field' is blocked."""
    assert _is_doctrine_quarantined(
        "The energy field around you shifts with emotion.", "somatic_first"
    )
