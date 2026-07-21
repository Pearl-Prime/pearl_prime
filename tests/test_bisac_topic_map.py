from pathlib import Path

from scripts.ci.check_bisac_topic_map import (
    EXPECTED_TOPIC_BISAC,
    validate_generator_maps,
    validate_sample_plan,
)


def test_bisac_generator_maps_use_self_help_anxiety_first() -> None:
    assert validate_generator_maps() == []


def test_bisac_sample_plan_validator_rejects_wrong_first_code(tmp_path: Path) -> None:
    sample = tmp_path / "plan.yaml"
    sample.write_text(
        "book_id: brand__teacher__persona__anxiety__false_alarm\n"
        "bisac_codes:\n"
        "  - SEL045000\n",
        encoding="utf-8",
    )

    errors = validate_sample_plan(sample)

    assert errors
    assert EXPECTED_TOPIC_BISAC["anxiety"][0] in errors[0]
