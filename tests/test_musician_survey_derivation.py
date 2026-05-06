from pathlib import Path

from phoenix_v4.musician.survey_derivation import survey_to_profile_dict, write_bank_from_survey

REPO = Path(__file__).resolve().parents[1]


def test_survey_to_profile_dict():
    survey_path = REPO / "SOURCE_OF_TRUTH/musician_banks/test_artist_alpha/survey_responses/2026-05-06.yaml"
    from phoenix_v4.musician.survey_derivation import load_survey

    survey = load_survey(survey_path)
    prof = survey_to_profile_dict(survey, "test_artist_alpha")
    assert prof["display_name"] == "Test Artist Alpha"
    assert "recovery" in prof["themes"]


def test_write_bank_from_survey_roundtrip(tmp_path: Path):
    src = REPO / "SOURCE_OF_TRUTH/musician_banks/test_artist_alpha/survey_responses/2026-05-06.yaml"
    write_bank_from_survey(src, "test_artist_alpha", tmp_path)
    assert (tmp_path / "profile.yaml").exists()
